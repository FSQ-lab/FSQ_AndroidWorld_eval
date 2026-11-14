import hashlib
import json
from pathlib import Path
import time

import pytest

from fsq_androidworld_eval import emulator_lifecycle as parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture
def grant(tmp_path, monkeypatch):
    adb = tmp_path / "owned-adb-fixture"
    adb.write_bytes(b"not executed in these admission tests")
    emulator = tmp_path / "owned-emulator-fixture"
    emulator.write_bytes(b"not executed in these admission tests")
    headless = tmp_path / "qemu/darwin-aarch64/qemu-system-aarch64-headless"
    headless.parent.mkdir(parents=True)
    headless.write_bytes(b"not executed in admission tests")
    witness = tmp_path / "witness.json"
    witness.write_text('{}')
    manifest_path = tmp_path / "manifest.json"
    manifest = {"target": {"serial": "emulator-5560", "consolePort": 5560, "grpcPort": 8556, "adbPath": str(adb)},
                "identities": {"nativeProviderMetadata": {"provider": "github_copilot", "model": "gpt-6.1-sol"}}}
    manifest_path.write_text(json.dumps(manifest))
    profile_path = tmp_path / "profile.json"
    profile = {"manifestPath": str(manifest_path), "authorizationPath": str(tmp_path / "authorization.json"),
               "profilePath": str(profile_path), "adbPort": 5561, "serverPort": 5037,
               "adbPath": str(adb), "adbSha256": digest(adb), "emulatorPath": str(emulator),
               "emulatorSha256": digest(emulator), "evaluatorPython": "/owned/venv/bin/python",
               "headlessPath": str(headless), "headlessSha256": digest(headless),
               "integrationOwner": {"pane": "w6:p1", "session": "isolated-fixture"},
               "executionOwner": {"pane": "w4:p1"},
               "failurePath": str(tmp_path / "resource-error.json"),
               "resourceReceiptPath": str(tmp_path / "resource.json"),
               "stopRequestedPath": str(tmp_path / "stop-requested.json"),
               "stopReceiptPath": str(tmp_path / "stop.json")}
    profile_path.write_text(json.dumps(profile))
    auth = {"schemaVersion": 1, "kind": "fsq_execution_authorization", "manifestSha256": digest(manifest_path),
            "approvedStages": ["prepare-apps"], "effectsGrant": {"ownedEmulatorLifecycle": True, "normalOwnedCleanup": True},
            "integrationOwner": profile["integrationOwner"], "executionOwner": profile["executionOwner"],
            "independentReview": {"status": "approved", "path": str(witness), "sha256": digest(witness)},
            "nativeModelCall": {"status": "passed_native_responses", "provider": "github_copilot", "requestedModel": "gpt-6.1-sol", "path": str(witness), "sha256": digest(witness)},
            "parentController": {"path": str(Path(parent.__file__).resolve()), "sha256": digest(parent.__file__),
                                 "profiles": {str(profile_path): digest(profile_path)}},
            "resource": {**manifest["target"], "exclusive": True, "disposable": True, "mutationsAllowed": True,
                         "notBeforeUnix": time.time() - 10, "validUntilUnix": time.time() + 300,
                         "authority": "isolated fixture only", "adbServerIdentity": {"pid": 123, "birthArgv": "fixture identity, not queried"}}}
    auth["resource"]["cleanupUntilUnix"] = auth["resource"]["validUntilUnix"] + 120
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    from fsq_androidworld_eval.adb_gateway import AdbGateway
    gate = AdbGateway(1, "emulator-5560", lambda kind: None)
    Path(profile["resourceReceiptPath"]).write_text(json.dumps({"gatewayPort": gate.port}))
    monkeypatch.setenv("FSQ_PARENT_ADB_GATEWAY", str(gate.port))
    try:
        yield profile_path, profile, auth
    finally:
        gate.close()


@pytest.mark.parametrize("command", [["kill-server"], ["start-server"], ["devices"], ["-s", "emulator-5554", "shell", "true"], ["-P", "5037", "shell", "true"]])
def test_emulator_cli_cannot_dispatch_global_or_wrong_target_commands(grant, monkeypatch, command):
    profile_path, profile, auth = grant
    from fsq_androidworld_eval import android_transport
    def forbidden(*args, **kwargs):
        raise AssertionError("No socket/process may be reached for denied SDK requests")
    real_connect = android_transport.socket.create_connection
    port = json.loads(Path(profile["resourceReceiptPath"]).read_text())["gatewayPort"]
    def own_control_only(address, **kwargs):
        if address != ("127.0.0.1", port):
            raise AssertionError("Only the owned failure-control socket is permitted")
        return real_connect(address, **kwargs)
    monkeypatch.setattr(android_transport.socket, "create_connection", own_control_only)
    monkeypatch.setattr(android_transport.subprocess, "run", forbidden)
    with pytest.raises((PermissionError, android_transport.AndroidTransportError)):
        parent.sdk_adb_cli(profile_path, command)
    assert json.loads(Path(profile["failurePath"]).read_text())["fatal"] is True
    with pytest.raises(PermissionError, match="latched failure"):
        parent.sdk_adb_cli(profile_path, ["shell", "true"])


def test_unknown_upstream_identity_prevents_emulator_creation(grant, monkeypatch):
    profile_path, profile, auth = grant
    auth["resource"]["adbServerIdentity"] = {}
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    def forbidden(*args, **kwargs):
        raise AssertionError("Emulator must not be spawned")
    monkeypatch.setattr(parent.subprocess, "Popen", forbidden)
    controller = parent.ParentResourceController(profile_path)
    with pytest.raises(PermissionError, match="identity is unknown"):
        controller.start()
    assert controller.process is None and controller.gateway is None
    with pytest.raises(AssertionError, match="one attempt"):
        controller.start()


def test_mutated_parent_profile_is_not_an_authorized_launch(grant, monkeypatch):
    profile_path, profile, auth = grant
    profile["adbPort"] = 5555
    profile_path.write_text(json.dumps(profile))
    with pytest.raises(PermissionError, match="not bound"):
        parent.ParentResourceController(profile_path).start()


def test_expired_parent_window_cannot_launch(grant):
    profile_path, profile, auth = grant
    auth["resource"]["validUntilUnix"] = time.time() - 1
    auth["resource"]["cleanupUntilUnix"] = auth["resource"]["validUntilUnix"] + 120
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    with pytest.raises(PermissionError, match="expired"):
        parent.ParentResourceController(profile_path).start()


def test_cleanup_window_does_not_reopen_preparation(grant):
    profile_path, profile, auth = grant
    auth["resource"]["validUntilUnix"] = time.time() - 1
    auth["resource"]["cleanupUntilUnix"] = auth["resource"]["validUntilUnix"] + 120
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    with pytest.raises(PermissionError, match="expired"):
        parent._authorize(profile_path)
    assert parent._authorize(profile_path, cleanup=True)[2]["effectsGrant"]["normalOwnedCleanup"] is True


def test_expired_business_grant_still_cleans_already_exited_owned_child(grant):
    from types import SimpleNamespace
    profile_path, profile, auth = grant
    auth["resource"]["validUntilUnix"] = time.time() - 1
    auth["resource"]["cleanupUntilUnix"] = auth["resource"]["validUntilUnix"] + 120
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    closed = []
    controller = parent.ParentResourceController(profile_path)
    controller.profile = profile
    controller.authorization_sha = digest(profile["authorizationPath"])
    controller.process = SimpleNamespace(pid=123, poll=lambda: 0, wait=lambda timeout: 0)
    controller.gateway = SimpleNamespace(latch=lambda: closed.append("fence"), close=lambda **kwargs: closed.append("gateway"))
    controller.log = SimpleNamespace(close=lambda: closed.append("log"))
    controller.stop()
    receipt = json.loads(Path(profile["stopReceiptPath"]).read_text())
    assert receipt["status"] == "closed" and receipt["shutdownRequested"] is False
    assert receipt["channel"] == "already_exited" and closed == ["fence", "gateway", "log"]


@pytest.fixture
def exec_child(grant, tmp_path, monkeypatch):
    """Real same-PID Darwin exec; no emulator, target port or shared daemon."""
    import select
    import shutil
    import subprocess
    from types import SimpleNamespace

    profile_path, profile, auth = grant
    source = tmp_path / "owned-exec.c"
    source.write_text(r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(int argc, char **argv) {
    char *leaf = strrchr(argv[0], '/');
    if (strcmp(leaf ? leaf + 1 : argv[0], "owned-emulator-fixture") == 0) {
        puts("launcher"); fflush(stdout);
        if (getchar() == EOF) return 2;
        argv[0] = getenv("FSQ_TEST_HEADLESS");
        execv(argv[0], argv);
        return 3;
    }
    puts("headless"); fflush(stdout);
    return getchar() == EOF ? 4 : 0;
}
''')
    subprocess.run(["/usr/bin/clang", str(source), "-o", profile["emulatorPath"]],
                   check=True, capture_output=True, timeout=30)
    shutil.copyfile(profile["emulatorPath"], profile["headlessPath"])
    Path(profile["headlessPath"]).chmod(0o700)
    profile.update({"emulatorSha256": digest(profile["emulatorPath"]),
                    "headlessSha256": digest(profile["headlessPath"])})
    profile_path.write_text(json.dumps(profile))
    auth["parentController"]["profiles"][str(profile_path)] = digest(profile_path)
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))
    controller = parent.ParentResourceController(profile_path)
    command, environment = parent.launch_spec(profile, {}, 1)
    environment["FSQ_TEST_HEADLESS"] = profile["headlessPath"]
    child = subprocess.Popen(command, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def line():
        assert select.select([child.stdout], [], [], 5)[0], "Fixture child did not reach its state"
        return child.stdout.readline().strip()

    assert line() == b"launcher"
    controller.process = controller._popen = child
    controller.profile = profile
    controller.command = command
    controller.identity = parent._pid_identity(child.pid)
    controller.authorization_sha = digest(profile["authorizationPath"])
    controller.gateway = SimpleNamespace(latch=lambda: None, close=lambda **kwargs: None)
    controller.log = (tmp_path / "controller-log").open("wb")
    monkeypatch.setattr(parent, "_listener_pids", lambda port: {child.pid})

    def advance():
        child.stdin.write(b"\n")
        child.stdin.flush()
        assert line() == b"headless"

    try:
        yield controller, advance
    finally:
        if child.poll() is None:
            child.stdin.write(b"\n")
            child.stdin.flush()
            child.wait(timeout=5)
        child.stdin.close()
        child.stdout.close()
        controller.log.close()


def test_real_launcher_exec_keeps_ownership_and_admits_only_pinned_headless(exec_child):
    controller, advance = exec_child
    before = controller.verify_identity()
    advance()
    after = controller.verify_identity(ready=True)
    assert {key: after[key] for key in ("pid", "parentPid", "birth")} == controller.identity
    assert before["executable"] == controller.profile["emulatorPath"]
    assert after["executable"] == controller.profile["headlessPath"]
    assert after["argv"] == [controller.profile["headlessPath"], *controller.command[1:]]


@pytest.mark.parametrize("mismatch", ["birth", "parent", "popen", "exe", "hash", "argv", "listener"])
def test_owned_exec_mismatch_blocks_normal_shutdown_without_rpc(exec_child, monkeypatch, mismatch):
    from types import SimpleNamespace
    from android_env.proto import emulator_controller_pb2_grpc as rpc

    controller, advance = exec_child
    advance()
    if mismatch in ("birth", "parent"):
        identity = dict(controller.identity)
        identity["birth" if mismatch == "birth" else "parentPid"] = "different epoch" if mismatch == "birth" else 1
        monkeypatch.setattr(parent, "_pid_identity", lambda pid: identity)
    elif mismatch == "popen":
        controller.process = SimpleNamespace(pid=controller._popen.pid, poll=lambda: None)
    elif mismatch in ("exe", "hash", "argv"):
        image = parent._process_image(controller.process.pid)
        if mismatch == "exe":
            image["executable"] = "/untrusted/qemu-system-aarch64-headless"
        elif mismatch == "hash":
            image["sha256"] = "0" * 64
        else:
            image["argv"][image["argv"].index("-avd") + 1] = "another-avd"
        monkeypatch.setattr(parent, "_process_image", lambda pid: image)
    else:
        monkeypatch.setattr(parent, "_listener_pids", lambda port: {1} if port == 5561 else {controller.process.pid})

    def forbidden(*args, **kwargs):
        raise AssertionError("Identity mismatch must prevent any shutdown dispatch")

    monkeypatch.setattr(rpc, "EmulatorControllerStub", forbidden)
    with pytest.raises(PermissionError):
        controller.stop()
    assert json.loads(Path(controller.profile["stopReceiptPath"]).read_text())["status"] == "unknown"
    assert controller._popen.poll() is None
    assert controller.stop_attempted is True


def test_missing_boot_listener_is_not_ready(exec_child, monkeypatch):
    controller, advance = exec_child
    advance()
    monkeypatch.setattr(parent, "_listener_pids", lambda port: set() if port == 5561 else {controller.process.pid})
    with pytest.raises(PermissionError, match="listener is absent"):
        controller.verify_identity(ready=True)


def test_real_exec_child_normal_stop_exits_zero_without_cleanup_exception(exec_child, monkeypatch):
    from types import SimpleNamespace
    from android_env.proto import emulator_controller_pb2_grpc as rpc

    controller, advance = exec_child
    controller.verify_identity()
    advance()

    def shutdown(request, *, timeout):
        controller.process.stdin.write(b"\n")
        controller.process.stdin.flush()

    monkeypatch.setattr(rpc, "EmulatorControllerStub", lambda channel: SimpleNamespace(
        setVmState=shutdown, getStatus=lambda request, timeout: SimpleNamespace(booted=True)))
    proof = controller.wait_until_booted(timeout=10)
    assert proof["executable"] == controller.profile["headlessPath"]
    assert json.loads(Path(controller.profile["resourceReceiptPath"]).read_text())["status"] == "owned_boot_qualified"
    controller.stop()
    receipt = json.loads(Path(controller.profile["stopReceiptPath"]).read_text())
    assert receipt["status"] == "closed" and receipt["exitCode"] == 0
    assert receipt["shutdownRequested"] is True and receipt["adbInvocations"] == 0
    assert receipt["bootQualified"] is True
    assert controller.process.returncode == 0
    assert controller.log.closed
    with pytest.raises(AssertionError, match="one normal stop"):
        controller.stop()


def test_backend_cannot_downgrade_to_launcher(exec_child, monkeypatch):
    controller, advance = exec_child
    advance()
    controller.verify_identity(ready=True)
    image = {"executable": controller.profile["emulatorPath"],
             "sha256": controller.profile["emulatorSha256"], "argv": controller.command}
    monkeypatch.setattr(parent, "_process_image", lambda pid: image)
    with pytest.raises(PermissionError, match="identity mismatch"):
        controller.verify_identity()


@pytest.mark.parametrize("smoke", [{"status": "unknown", "bootQualified": True},
                                  {"status": "closed", "bootQualified": False}])
def test_preparation_cannot_launch_after_unqualified_or_unknown_smoke(grant, monkeypatch, smoke):
    profile_path, profile, auth = grant
    smoke_path = profile_path.parent / "smoke-stop.json"
    smoke_path.write_text(json.dumps(smoke))
    profile["requiresSmokeReceipt"] = str(smoke_path)
    profile_path.write_text(json.dumps(profile))
    auth["parentController"]["profiles"][str(profile_path)] = digest(profile_path)
    Path(profile["authorizationPath"]).write_text(json.dumps(auth))

    def forbidden(*args, **kwargs):
        raise AssertionError("No emulator may be created after an unsuccessful smoke")

    monkeypatch.setattr(parent.subprocess, "Popen", forbidden)
    with pytest.raises(PermissionError, match="successful owned lifecycle smoke"):
        parent.ParentResourceController(profile_path).start()


def test_headless_file_drift_blocks_creation_before_any_gateway_or_child(grant, monkeypatch):
    profile_path, profile, auth = grant
    Path(profile["headlessPath"]).write_bytes(b"not the approved headless bytes")

    def forbidden(*args, **kwargs):
        raise AssertionError("An unpinned future exec must not start a child")

    monkeypatch.setattr(parent.subprocess, "Popen", forbidden)
    controller = parent.ParentResourceController(profile_path)
    with pytest.raises(PermissionError):
        controller.start()
    assert controller.process is None and controller.gateway is None


def test_missing_backend_cleanup_does_not_wait_through_unused_business_window(exec_child, monkeypatch):
    controller, advance = exec_child
    advance()
    epoch = time.time()
    clock = [epoch]
    monkeypatch.setattr(parent.time, "time", lambda: clock[0])
    monkeypatch.setattr(parent.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + max(60, seconds)))
    monkeypatch.setattr(parent, "_listener_pids", lambda port: set())
    with pytest.raises(PermissionError):
        controller.stop()
    assert clock[0] - epoch == 120
    assert controller.process.poll() is None
    assert json.loads(Path(controller.profile["stopReceiptPath"]).read_text())["status"] == "unknown"
