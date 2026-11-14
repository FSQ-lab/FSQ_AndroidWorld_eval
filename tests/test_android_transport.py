import os
import subprocess
from types import SimpleNamespace

import pytest
from android_env.components import config_classes
from android_env.proto import adb_pb2
from android_world.env import adb_utils
from android_world.env.setup_device import apps

from fsq_androidworld_eval import android_transport as transport


@pytest.fixture
def adb(monkeypatch):
    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    monkeypatch.setattr(transport.socket, "create_connection", lambda *a, **k: Connection())
    calls = []
    state = {"failure": None, "whoami": b"root\n", "launch": b"Status: ok\n", "resolution": b"com.dimowner.audiorecorder/.LauncherAlias\n"}

    def run(command, **kwargs):
        calls.append(command)
        args = command[7:]
        if state["failure"] is not None:
            if isinstance(state["failure"], BaseException):
                raise state["failure"]
            return subprocess.CompletedProcess(command, state["failure"], b"original output", b"original stderr")
        output = b""
        if args == ["shell", "whoami"]:
            output = state["whoami"]
        elif args == ["shell", "am", "get-current-user"]:
            output = b"12\n"
        elif args[:4] == ["shell", "cmd", "package", "resolve-activity"]:
            output = state["resolution"]
        elif args[:3] == ["shell", "am", "start"]:
            output = state["launch"]
        return subprocess.CompletedProcess(command, 0, output, b"")

    monkeypatch.setattr(transport.subprocess, "run", run)
    config = config_classes.AdbControllerConfig(adb_path="/owned/adb", device_name="emulator-5560", adb_server_port=5077)
    monkeypatch.setattr(transport.SingleAttemptAdb, "_prepare_client", lambda owner: owner.check())
    return transport.SingleAttemptAdb(config), calls, state


@pytest.mark.parametrize("failure,kind", [
    (251, "adb_nonzero"),
    (subprocess.TimeoutExpired("adb", 1, output=b"partial", stderr=b"timeout stderr"), "adb_timeout"),
    (OSError("spawn failed"), "adb_spawn_failed"),
])
def test_official_parser_failure_is_one_attempt_and_sticky(adb, failure, kind):
    controller, calls, state = adb
    state["failure"] = failure
    parser = transport.CheckedAdbParser(controller)
    request = adb_pb2.AdbRequest(generic=adb_pb2.AdbRequest.GenericRequest(args=["shell", "false"]))
    with pytest.raises(transport.AndroidTransportError) as first:
        parser.parse(request)
    with pytest.raises(transport.AndroidTransportError) as second:
        parser.parse(request)
    assert second.value is first.value
    assert first.value.kind == kind
    assert len(calls) == 1
    assert calls[0][:7] == ["/owned/adb", "-H", "127.0.0.1", "-P", "5077", "-s", "emulator-5560"]
    assert first.value.stdout == ("partial" if kind == "adb_timeout" else "original output" if kind == "adb_nonzero" else "")


def test_official_audio_recorder_setup_resolves_alias_for_current_user(adb, monkeypatch):
    controller, calls, state = adb
    parser = transport.CheckedAdbParser(controller)
    env = SimpleNamespace(controller=SimpleNamespace(execute_adb_call=parser.parse))
    monkeypatch.setattr(apps.time, "sleep", lambda seconds: None)
    apps.AudioRecorder.setup(env)
    launch = [c[7:] for c in calls if c[7:10] == ["shell", "am", "start"]]
    assert launch == [["shell", "am", "start", "-W", "--user", "12", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-n", "com.dimowner.audiorecorder/.LauncherAlias"]]
    assert all("monkey" not in command for command in calls)
    assert controller.launches == [{"package": "com.dimowner.audiorecorder", "user": 12, "component": "com.dimowner.audiorecorder/.LauncherAlias"}]


def test_mapped_and_unmapped_official_launches_use_same_resolver(adb):
    controller, calls, state = adb
    parser = transport.CheckedAdbParser(controller)
    owner = SimpleNamespace(execute_adb_call=parser.parse)
    adb_utils.launch_app("audio recorder", owner)
    state["resolution"] = b"com.example.newapp/.Alias\n"
    adb_utils.launch_app("com.example.newapp", owner)
    assert [row["package"] for row in controller.launches] == ["com.dimowner.audiorecorder", "com.example.newapp"]
    assert all("monkey" not in command for command in calls)


@pytest.mark.parametrize("output", [b"No activity found\n", b"com.other/.Activity\n", b"com.dimowner.audiorecorder/.A\ncom.dimowner.audiorecorder/.B\n"])
def test_unresolved_or_ambiguous_launcher_never_starts(adb, output):
    controller, calls, state = adb
    state["resolution"] = output
    with pytest.raises(transport.AndroidTransportError, match="launcher_resolution_failed"):
        controller.launch("com.dimowner.audiorecorder")
    assert len(calls) == 2
    assert not controller.launches


@pytest.mark.parametrize("output", [b"Error type 3\nError: Activity class does not exist\n", b"SecurityException: denied\n", b"Status: timeout\n", b"unrecognized output\n"])
def test_exit_zero_android_failure_is_fatal_without_fallback(adb, output):
    controller, calls, state = adb
    state["launch"] = output
    with pytest.raises(transport.AndroidTransportError, match="activity_launch_failed"):
        controller.launch("com.dimowner.audiorecorder")
    assert len(calls) == 3
    assert controller.launches == []


def test_existing_activity_warning_is_success(adb):
    controller, calls, state = adb
    state["launch"] = b"Warning: Activity not started, intent has been delivered to currently running top-most instance.\nStatus: ok\n"
    component, output = controller.launch("com.dimowner.audiorecorder")
    assert component == "com.dimowner.audiorecorder/.LauncherAlias"
    assert output == state["launch"]


@pytest.mark.parametrize("args", [["kill-server"], ["start-server"], ["devices"], ["-s", "emulator-5554", "shell", "true"]])
def test_shared_server_or_target_override_rejected_before_process(adb, args):
    controller, calls, _ = adb
    with pytest.raises(transport.AndroidTransportError):
        controller.execute_command(args)
    assert calls == []


def test_missing_server_is_not_started(adb, monkeypatch):
    controller, calls, _ = adb
    def absent(*args, **kwargs):
        raise ConnectionRefusedError("absent")
    monkeypatch.setattr(transport.socket, "create_connection", absent)
    with pytest.raises(transport.AndroidTransportError, match="adb_server_unavailable"):
        controller.execute_command(["shell", "true"])
    assert calls == []


def test_non_launch_monkey_is_not_rewritten_or_executed(adb):
    controller, calls, _ = adb
    request = adb_pb2.AdbRequest(generic=adb_pb2.AdbRequest.GenericRequest(args=["shell", "monkey", "-p", "com.example.app", "100"]))
    with pytest.raises(transport.AndroidTransportError, match="non_launch_monkey_forbidden"):
        transport.CheckedAdbParser(controller).parse(request)
    assert calls == []


def test_constructor_does_not_mutate_or_disclose_parent_environment(monkeypatch):
    monkeypatch.setenv("ANDROID_HOME", "/owned/sdk")
    monkeypatch.setenv("ANDROID_ADB_SERVER_PORT", "5077")
    before = dict(os.environ)
    transport.SingleAttemptAdb(config_classes.AdbControllerConfig())
    assert dict(os.environ) == before
    error = transport.AndroidTransportError("failure", ["shell", "token=SECRET"],
        b"password=SECRET ghp_PRIVATE\nAuthorization: Bearer SECRET\n\"api_key\": \"SECRET with spaces\"")
    assert "SECRET" not in str(error) and "PRIVATE" not in str(error)


def test_refresh_retains_failed_close_owner_and_closes_replacement(adb, monkeypatch):
    controller, _, _ = adb
    owners = []
    class Owner:
        def __init__(self):
            self.closed = False
            self.fail = False
        def close(self):
            self.closed = True
            if self.fail:
                raise ValueError("retired close failed")
    def build(*args):
        owner = Owner()
        owners.append(owner)
        return owner
    monkeypatch.setattr(transport, "_build_backend", build)
    config = config_classes.EmulatorConfig(adb_controller=controller._config)
    owner = transport.LocalAndroidWorldController(config, b"owned helper")
    owners[0].fail = True
    with pytest.raises(ValueError, match="retired close failed"):
        owner.refresh_env()
    with pytest.raises(ExceptionGroup):
        owner.close()
    assert all(row.closed for row in owners)
    assert owner._env is owners[1]


def test_partial_simulator_construction_closes_without_recovery(adb, monkeypatch):
    controller, calls, _ = adb
    closed = []
    original_close = transport.ExistingEmulator.close
    def close(owner):
        closed.append(owner)
        original_close(owner)
    def fail():
        controller._fail("construction_failure", [])
    monkeypatch.setattr(transport.ExistingEmulator, "close", close)
    monkeypatch.setattr(controller, "_require_server", fail)
    config = config_classes.EmulatorConfig(emulator_launcher=config_classes.EmulatorLauncherConfig(
        emulator_console_port=5560, adb_port=5561, grpc_port=8556,
    ), adb_controller=controller._config)
    with pytest.raises(transport.AndroidTransportError, match="construction_failure"):
        transport._build_backend(config, controller, b"helper")
    assert len(closed) == 1
    assert calls == []


@pytest.mark.parametrize("code", [None, 0, 251])
def test_logcat_cleanup_preserves_unexpected_exit_but_accepts_owned_stop(adb, code):
    import io
    controller, _, _ = adb
    class Process:
        stdout = io.StringIO("last log line")
        terminated = False
        def poll(self):
            return code
        def terminate(self):
            self.terminated = True
        def wait(self, timeout):
            return -15 if self.terminated else code
    process = Process()
    stream = transport.OwnedAdbLogStream(controller, False)
    stream._adb_subprocess = process
    controller._log_processes.add(process)
    if code is None:
        stream.stop_stream()
        assert process.terminated is True and controller.failure is None
    else:
        with pytest.raises(transport.AndroidTransportError) as failure:
            stream.stop_stream()
        assert failure.value.returncode == code
        assert controller.failure is failure.value and process.terminated is False
    assert process.stdout.closed and not controller._log_processes
    assert stream._adb_subprocess is None


def test_unlabelled_input_text_is_absent_from_failure_fields(adb):
    controller, calls, state = adb
    private = "a personal message with no credential label"
    state["failure"] = 251
    request = adb_pb2.AdbRequest()
    request.input_text.text = private
    with pytest.raises(transport.AndroidTransportError) as failure:
        transport.CheckedAdbParser(controller).parse(request)
    assert private not in str(failure.value)
    assert private not in failure.value.command
    assert calls[0][-1] == private
    echo = transport.AndroidTransportError("failure", calls[0], private, private)
    assert private not in echo.stdout and private not in echo.stderr


def test_audio_directory_probe_shares_environment_failure_latch(adb, monkeypatch):
    from fsq_androidworld_eval import preparation
    controller, calls, state = adb
    parser = transport.CheckedAdbParser(controller)
    owner = SimpleNamespace(transport=controller, execute_adb_call=parser.parse)
    def click(label):
        if label == "Apply":
            state["failure"] = 251
    monkeypatch.setattr(preparation.tools, "AndroidToolController", lambda **kwargs: SimpleNamespace(click_element=click))
    with pytest.raises(transport.AndroidTransportError) as failure:
        preparation._complete_audio_recorder_setup(SimpleNamespace(controller=owner), "/owned/adb", "emulator-5560")
    assert controller.failure is failure.value
    assert failure.value.kind == "adb_nonzero"
    assert len(calls) == 4
    assert all(call[7:10] != ["shell", "am", "force-stop"] for call in calls)


def test_helper_server_stop_failure_does_not_skip_raw_environment_close():
    closed = []
    wrapper = transport.LocalA11yWrapper.__new__(transport.LocalA11yWrapper)
    wrapper._env = SimpleNamespace(close=lambda: closed.append(True))
    wrapper._server = SimpleNamespace(stop=lambda grace: SimpleNamespace(wait=lambda timeout: False))
    with pytest.raises(ExceptionGroup, match="Accessibility wrapper cleanup failed"):
        wrapper.close()
    assert closed == [True]


def test_socket_refusal_survives_cached_parser_cleanup_and_first_receipt(tmp_path, monkeypatch):
    import json
    import socket
    from fsq_androidworld_eval import emulator_lifecycle
    from fsq_androidworld_eval.adb_gateway import AdbGateway

    owner = transport.SingleAttemptAdb(config_classes.AdbControllerConfig(
        adb_path="/not-executed/adb", device_name="emulator-5560", adb_server_port=1))
    gateway = AdbGateway(1, "emulator-5560", owner._gateway_failed)
    try:
        with socket.create_connection(("127.0.0.1", gateway.port), timeout=2) as client:
            AdbGateway._send_request(client, b"host:kill")
            assert AdbGateway._exact(client, 4) == b"FAIL"
        first = owner.failure
        refusal = first.gateway_failure
        assert first.__cause__ is refusal
        assert isinstance(refusal.original_cause, PermissionError)
        assert refusal.evidence["branch"] == "host_service_filter"
        assert refusal.evidence["request"]["value"] == "host:kill"
        assert refusal.evidence["gateway"]["port"] == gateway.port

        def forbidden(*args, **kwargs):
            raise AssertionError("Cached failure must prevent any subprocess or recovery")

        monkeypatch.setattr(transport.subprocess, "run", forbidden)
        parser = transport.CheckedAdbParser(owner)
        with pytest.raises(transport.AndroidTransportError) as later:
            parser.parse(adb_pb2.AdbRequest(generic=adb_pb2.AdbRequest.GenericRequest(args=["root"])))
        assert later.value is first and later.value.__cause__ is refusal
        path = tmp_path / "first.json"
        profile = {"failurePath": str(path)}
        emulator_lifecycle._record_failure(profile, first, gateway=gateway)
        original = path.read_bytes()
        with pytest.raises(transport.AndroidTransportError) as cleanup:
            owner._fail("adb_logcat_exited", ["logcat"], returncode=255)
        assert cleanup.value is first and cleanup.value.__cause__ is refusal
        emulator_lifecycle._record_failure(profile, RuntimeError("later cleanup"), gateway=gateway)
        assert path.read_bytes() == original
        assert json.loads(original)["gatewayFailure"] == refusal.evidence
        assert gateway.failure is refusal
    finally:
        gateway.close()


def test_refusal_trace_and_receipt_do_not_expose_input_or_credentials(tmp_path):
    import json
    import traceback
    from fsq_androidworld_eval import emulator_lifecycle
    from fsq_androidworld_eval.adb_gateway import AdbGatewayFailure

    private = b"shell,v2,raw:input text private-task-payload"
    cause = PermissionError("denied " + repr(private) + "\nauthorization: Bearer sk-privateCredential")
    scope = SimpleNamespace(port=9011, server_port=9012, serial="emulator-5560", version_admitted=True)
    refusal = AdbGatewayFailure(cause, "selected_service_filter", b"host:tport:serial:emulator-5560", private, scope)
    owner = transport.SingleAttemptAdb(config_classes.AdbControllerConfig(
        adb_path="/not-executed/adb", device_name="emulator-5560", adb_server_port=1))
    owner._gateway_failed(refusal)
    with pytest.raises(transport.AndroidTransportError) as failure:
        owner.check()
    path = tmp_path / "refusal.json"
    emulator_lifecycle._record_failure({"failurePath": str(path)}, failure.value,
                                      gateway=SimpleNamespace(latch=lambda: None))
    rendered = "".join(traceback.format_exception(failure.value)) + path.read_text()
    assert "private-task-payload" not in rendered
    assert "sk-privateCredential" not in rendered
    assert refusal.original_cause is cause
    evidence = json.loads(path.read_text())["gatewayFailure"]
    assert evidence["selectedService"]["redacted"] is True
    assert evidence["request"]["value"] == "host:tport:serial:emulator-5560"
    assert evidence["cause"]["type"] == "PermissionError"


@pytest.mark.parametrize("group_cause", [False, True])
def test_parent_group_receipt_preserves_first_explicit_refusal_and_other_errors(tmp_path, group_cause):
    import json
    from fsq_androidworld_eval import emulator_lifecycle
    from fsq_androidworld_eval.adb_gateway import AdbGatewayFailure

    scope = SimpleNamespace(port=9011, server_port=9012, serial="emulator-5560", version_admitted=True)
    first = AdbGatewayFailure(PermissionError("initialization refusal"), "host_service_filter", b"host:kill", None, scope)
    later = AdbGatewayFailure(PermissionError("cleanup refusal"), "latched_forward", b"host:version", None, scope)
    wrapped = RuntimeError("initialization wrapper")
    wrapped.__cause__ = first
    cleanup = RuntimeError("independent cleanup error")
    group = ExceptionGroup("construction and cleanup", [cleanup] if group_cause else [wrapped, ExceptionGroup("secondary", [cleanup, later])])
    if group_cause:
        group.__cause__ = first
    path = tmp_path / "first.json"
    gate = SimpleNamespace(latch=lambda: None)
    emulator_lifecycle._record_failure({"failurePath": str(path)}, group, gateway=gate)
    original = path.read_bytes()
    record = json.loads(original)
    assert record["type"] == "ExceptionGroup"
    assert record["gatewayFailure"] == first.evidence
    assert len(record["exceptions"]) == len(group.exceptions)
    assert "independent cleanup error" in json.dumps(record)
    emulator_lifecycle._record_failure({"failurePath": str(path)}, later, gateway=gate)
    assert path.read_bytes() == original


def test_root_exit_zero_without_root_identity_aborts_backend_creation(adb, monkeypatch):
    controller, calls, state = adb
    state["whoami"] = b"shell\n"
    def forbidden_backend(*args):
        raise AssertionError("An unrooted backend must not acquire helpers or logcat")
    monkeypatch.setattr(transport, "_build_backend", forbidden_backend)
    config = config_classes.EmulatorConfig(adb_controller=controller._config)
    with pytest.raises(transport.AndroidTransportError, match="adb_root_not_established"):
        transport.LocalAndroidWorldController(config, b"owned helper")
    assert sum(command[7:] == ["root"] for command in calls) == 1


@pytest.mark.parametrize("args", [
    ["push", "/owned/data.txt", "/sdcard/data.txt"],
    ["pull", "/sdcard/data.txt", "/owned/data.txt"],
    ["install", "-r", "-t", "-g", "/owned/application.apk"],
    ["root"],
    ["shell", "am", "start", "-a", "android.intent.action.CALL", "-d", "tel:15555550123"],
])
def test_official_device_lifecycle_commands_keep_fixed_gateway_prefix(adb, args):
    controller, calls, _ = adb
    controller.execute_command(args)
    assert calls == [["/owned/adb", "-H", "127.0.0.1", "-P", "5077", "-s", "emulator-5560"] + args]


@pytest.mark.parametrize("args", [
    ["emu", "kill"], ["emu", "avd", "snapshot", "load", "default"],
    ["emu", "geo", "fix", "1", "2"], ["emu", "gsm", "call", "+15555550123"],
    ["emu", "sms", "send", "+15555550123"],
    ["emu", "sms", "send", "+15555550123", "message", "kill"],
    ["emu", "sms", "send", "+15555550123", "message\nkill"],
    ["emu", "sms", "send", "+15555550123", "message\rkill"],
    ["emu", "sms", "send", "+15555550123", "message; kill"],
    ["emu", "sms", "send", "+15555550123", "message\x00kill"],
    ["emu", "sms", "send", "+1555;kill", "message"],
    ["emu", "sms", "send", "", "message"],
    ["emu", "sms", "send", "+15555550123", ""],
])
def test_console_management_injection_and_unselected_shapes_latch_before_io(adb, args):
    controller, calls, _ = adb
    with pytest.raises(transport.AndroidTransportError, match="emulator_command_forbidden") as first:
        controller.execute_command(args)
    with pytest.raises(transport.AndroidTransportError) as later:
        controller.execute_command(["shell", "true"])
    assert later.value is first.value
    assert calls == []


def test_official_sms_uses_framed_gateway_rpc_never_native_emu(adb, monkeypatch):
    import json
    import time

    controller, calls, _ = adb
    controller._gateway = SimpleNamespace(port=5078)
    monkeypatch.setattr(controller, "_require_server", controller.check)
    addresses = []
    writes = []
    responses = [b"OKAY00040029", b"OKAY0004OK\r\n"]

    class Connection:
        def __init__(self, response):
            self.response = response
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def settimeout(self, timeout):
            assert 0 < timeout <= 5
        def sendall(self, value):
            writes.append(value)
        def recv(self, count):
            result, self.response = self.response[:count], self.response[count:]
            return result

    def connect(address, timeout):
        addresses.append(address)
        return Connection(responses.pop(0))

    monkeypatch.setattr(transport.socket, "create_connection", connect)
    owner = SimpleNamespace(execute_adb_call=transport.CheckedAdbParser(controller).parse)
    before = time.time()
    response = adb_utils.text_emulator(owner, "+1 (555) 555-0123", "It's a bird, café.", timeout_sec=5)
    assert response.generic.output == b"OK\r\n"
    assert addresses == [("127.0.0.1", 5078), ("127.0.0.1", 5078)]
    assert writes[0] == b"000chost:version"
    prefix = b"fsq:emu:emulator-5560:"
    assert int(writes[1][:4], 16) == len(writes[1][4:])
    assert writes[1][4:].startswith(prefix)
    request = json.loads(writes[1][4 + len(prefix):])
    assert request["args"] == ["sms", "send", "+15555550123", "It's a bird, café."]
    assert before < request["deadline"] <= time.time() + 5
    assert calls == []


def test_sms_failure_fields_do_not_disclose_phone_or_message():
    number, message = "+15555550123", "It's a private lifecycle message"
    error = transport.AndroidTransportError("failure", ["emu", "sms", "send", number, message], message, number)
    assert number not in str(error)
    assert message not in str(error)


@pytest.mark.parametrize("status,kind", [(b"FAIL", "emulator_gateway_rejected"), (b"timeout", "adb_timeout")])
def test_sms_rpc_failures_are_sticky_without_cli_fallback(adb, monkeypatch, status, kind):
    controller, calls, _ = adb
    controller._gateway = SimpleNamespace(port=5078)
    monkeypatch.setattr(controller, "_require_server", controller.check)

    class Connection:
        response = b"FAIL0006denied"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def settimeout(self, timeout):
            pass
        def sendall(self, value):
            pass
        def recv(self, count):
            if status == b"timeout":
                raise TimeoutError("private timeout detail")
            value, self.response = self.response[:count], self.response[count:]
            return value

    monkeypatch.setattr(transport.socket, "create_connection", lambda *a, **k: Connection())
    with pytest.raises(transport.AndroidTransportError) as first:
        controller.execute_command(["emu", "sms", "send", "+15555550123", "private"], timeout=5)
    assert first.value.kind == kind
    with pytest.raises(transport.AndroidTransportError) as second:
        controller.execute_command(["root"])
    assert second.value is first.value and calls == []


@pytest.mark.parametrize("parent", [False, True])
def test_sdk_gateway_emulator_routing_uses_parent_when_present(monkeypatch, parent):
    monkeypatch.delenv("FSQ_PARENT_ADB_GATEWAY", raising=False)
    if parent:
        monkeypatch.setenv("FSQ_PARENT_ADB_GATEWAY", "5078")
    observed = []

    def gateway(*args, **kwargs):
        observed.append((args, kwargs))
        return SimpleNamespace(port=5079)

    monkeypatch.setattr(transport, "AdbGateway", gateway)
    monkeypatch.setattr(transport.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
        a[0], 0, b"Android Debug Bridge version 1.0.41\n", b""))
    controller = transport.SingleAttemptAdb(config_classes.AdbControllerConfig(
        adb_path="/owned/adb", device_name="emulator-5560", adb_server_port=5077))
    controller._prepare_client()
    assert observed[0][0][:2] == (5078 if parent else 5077, "emulator-5560")
    assert observed[0][1]["forward_emulator"] is parent
