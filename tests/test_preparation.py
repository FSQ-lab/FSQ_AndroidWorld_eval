from contextlib import nullcontext
import json
from pathlib import Path

from types import SimpleNamespace

import pytest
from fsq_androidworld_eval import preparation
from fsq_androidworld_eval.runner import ANDROID_WORLD_REVISION, HARNESS_REVISION, _sha256
from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG

_ARTIFACT_IDENTITY = {"schemaVersion": 1, "artifacts": [{"name": "fixture.apk", "sha256": "a" * 64}]}
_MEDIA_IDENTITY = {"package": "fixture-encoder", "sha256": "b" * 64}


@pytest.fixture(autouse=True)
def isolated_host_prerequisites(monkeypatch):
    monkeypatch.setattr(preparation, "artifact_identity", lambda project: _ARTIFACT_IDENTITY)
    monkeypatch.setattr(preparation, "probe_host_media", lambda: {"encoder": _MEDIA_IDENTITY, "mp3": "encoded_and_decoded", "mp4": "encoded_and_decoded"})
    monkeypatch.setattr(preparation, "local_app_data", lambda project: nullcontext())


def test_required_app_names_are_unique_and_sorted() -> None:
    manifest = {
        "tasks": [
            {"apps": ["markor", "settings"]},
            {"apps": ["markor", "clock"]},
        ]
    }

    assert preparation._required_app_names(manifest) == ["clock", "markor", "settings"]


def test_package_version_extracts_bounded_identity(monkeypatch) -> None:
    monkeypatch.setattr(
        preparation,
        "_adb",
        lambda *args, **kwargs: "versionCode=42 minSdk=21\nversionName=1.2.3\n",
    )
    assert preparation._package_version("adb", "emulator", "example.app") == {
        "package": "example.app",
        "versionName": "1.2.3",
        "versionCode": "42",
    }


def test_live_attestation_does_not_require_task_initialized_date_or_database(monkeypatch) -> None:
    readiness = {
        "target": {"serial": "emulator", "appiumUrl": "http://appium"},
        "appium": {"value": {"build": {"version": "3.7.0"}}},
        "device": {
            "apiLevel": 33,
            "abi": "arm64-v8a",
            "buildFingerprint": "fingerprint",
            "screenSize": "Physical size: 1080x2400",
            "timezone": "UTC",
        },
        "apps": [],
        "databases": [{"app": "simple calendar pro", "present": False}],
    }
    values = {
        ("shell", "getprop", "ro.build.version.sdk"): "33",
        ("shell", "getprop", "ro.product.cpu.abi"): "arm64-v8a",
        ("shell", "getprop", "ro.build.fingerprint"): "fingerprint",
        ("shell", "wm", "size"): "Physical size: 1080x2400",
        ("shell", "getprop", "persist.sys.timezone"): "UTC",
        ("shell", "date", "+%Y-%m-%d"): "2026-11-05",
    }
    monkeypatch.setattr(preparation, "_request_json", lambda url: readiness["appium"])
    monkeypatch.setattr(preparation, "_appium_session_hashes", lambda *args: [])
    monkeypatch.setattr(
        preparation, "_adb", lambda adb_path, serial, *args, **kwargs: values[args]
    )
    monkeypatch.setattr(preparation, "_database_exists", lambda *args: False)

    attestation = preparation.attest_device(readiness, "adb")

    assert attestation["qualified"] is True
    assert attestation["device"]["date"] == "2026-11-05"
    assert attestation["databases"] == [
        {"app": "simple calendar pro", "present": False}
    ]

def test_preparation_failure_still_writes_verifiable_report(tmp_path: Path, monkeypatch) -> None:
    manifest = {
        "schemaVersion": 2,
        "campaignId": "qualification",
        "protocol": {
            "harnessRevision": HARNESS_REVISION,
            "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
            "androidWorldRevision": ANDROID_WORLD_REVISION,
            "environmentArtifacts": _ARTIFACT_IDENTITY,
            "runtimeIdentity": {"mediaEncoder": _MEDIA_IDENTITY},
        },
        "target": {
            "serial": "emulator-5554",
            "consolePort": 5554,
            "grpcPort": 8554,
            "appiumUrl": "http://127.0.0.1:4723",
            "apiLevel": 33,
            "abi": "arm64-v8a",
        },
        "tasks": [],
    }
    manifest_path = tmp_path / "manifest.json"
    report_path = tmp_path / "readiness.json"
    manifest_path.write_text(json.dumps(manifest))

    def unavailable(*args, **kwargs):
        raise OSError("Appium unavailable")

    monkeypatch.setattr(preparation, "_request_json", unavailable)

    report = preparation.prepare_device(manifest_path, report_path, "adb")
    saved = json.loads(report_path.read_text())
    payload = {key: value for key, value in saved.items() if key != "identitySha256"}

    assert report["qualified"] is False
    assert report["error"]["type"] == "OSError"
    assert saved["identitySha256"] == _sha256(payload)


@pytest.fixture
def recorder_device(tmp_path: Path, monkeypatch):
    state = {
        "directory": True, "closed": False, "setupStarted": False,
        "adbOutput": b"FSQ_ADB_STDOUT_SENTINEL", "restoreError": None,
    }
    target = {
        "serial": "emulator-5554", "consolePort": 5554, "grpcPort": 8554,
        "appiumUrl": "http://127.0.0.1:4723", "apiLevel": 33, "abi": "arm64-v8a",
    }
    manifest = {
        "schemaVersion": 2, "campaignId": "recorder-readiness",
        "protocol": {
            "harnessRevision": HARNESS_REVISION, "androidWorldRevision": ANDROID_WORLD_REVISION,
            "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
            "environmentArtifacts": _ARTIFACT_IDENTITY,
            "runtimeIdentity": {"mediaEncoder": _MEDIA_IDENTITY},
        },
        "target": target, "tasks": [{"apps": ["audio recorder"]}],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    properties = {
        "ro.build.version.sdk": "33", "ro.product.cpu.abi": "arm64-v8a",
        "ro.build.fingerprint": "fingerprint", "persist.sys.timezone": "UTC",
    }

    def adb(adb_path, serial, *args, **kwargs):
        if args == ("get-state",):
            return "device"
        if args[:2] == ("shell", "getprop"):
            return properties[args[2]]
        if args[:2] == ("shell", "date"):
            return "2026-11-06T00:00:00+0000"
        if args == ("shell", "wm", "size"):
            return "Physical size: 1080x2400"
        if args[:3] == ("shell", "dumpsys", "package"):
            return "versionCode=926 minSdk=17\nversionName=0.9.26\n"
        if args[0] == "shell" and args[1].startswith("test -d "):
            return "present" if state["directory"] else "missing"
        if args[:2] == ("shell", "am"):
            return "Status: ok"
        raise AssertionError(args)

    monkeypatch.setattr(preparation, "_adb", adb)
    monkeypatch.setattr(preparation, "_request_json", lambda url: {"value": {"build": {"version": "3.7.0"}}})
    monkeypatch.setattr(preparation, "_appium_session_hashes", lambda *args: [])
    monkeypatch.setattr(preparation, "load_environment", lambda **kwargs: SimpleNamespace(controller=SimpleNamespace(
        close=lambda: state.update(closed=True), transport=SimpleNamespace(launches=[]),
    )))
    monkeypatch.setattr(preparation, "launch_package", lambda controller, package: (package + "/.Main", b"Status: ok"))
    monkeypatch.setattr(preparation.adb_utils, "issue_generic_request", lambda *args: SimpleNamespace(generic=SimpleNamespace(output=state["adbOutput"])))
    monkeypatch.setattr(preparation.adb_utils, "press_home_button", lambda env: None)
    monkeypatch.setattr(preparation.adb_utils, "set_root_if_needed", lambda env: None)
    monkeypatch.setattr(preparation.env_launcher, "setup_env", lambda *args, **kwargs: None)
    monkeypatch.setattr(preparation.device_setup, "get_installed_packages", lambda env: {"com.dimowner.audiorecorder"})
    app = preparation.device_setup.get_app_mapping("audio recorder")
    monkeypatch.setattr(app, "setup", lambda env: state.update(setupStarted=True))
    monkeypatch.setattr(preparation.app_snapshot, "save_snapshot", lambda *args: None)

    def restore_snapshot(*args):
        if state["restoreError"] is not None:
            raise state["restoreError"]

    monkeypatch.setattr(preparation.app_snapshot, "restore_snapshot", restore_snapshot)
    monkeypatch.setattr(preparation, "_complete_audio_recorder_setup", lambda *args: None)
    return manifest_path, tmp_path / "readiness.json", state


@pytest.mark.parametrize("present", [False, True])
def test_recorder_directory_is_required_before_qualification(recorder_device, present: bool) -> None:
    manifest_path, report_path, state = recorder_device
    state["directory"] = present

    report = preparation.prepare_device(manifest_path, report_path, "adb")

    assert report["qualified"] is present
    assert report["directories"][0]["present"] is present
    assert state["closed"] is True
    assert json.loads(report_path.read_text())["qualified"] is present
    if not present:
        assert report["error"]["type"] == "RuntimeError"


@pytest.mark.parametrize("change", ["none", "directory_removed", "proof_missing"])
def test_recorder_directory_is_rechecked_before_campaign_execution(recorder_device, change: str) -> None:
    manifest_path, report_path, state = recorder_device
    report = preparation.prepare_device(manifest_path, report_path, "adb")
    assert report["qualified"] is True
    if change == "directory_removed":
        state["directory"] = False
    elif change == "proof_missing":
        report["directories"] = []

    attestation = preparation.attest_device(report, "adb")

    assert attestation["qualified"] is (change == "none")
    assert ("directory:audio recorder" in attestation["mismatches"]) is (change != "none")


def test_recorder_onboarding_failure_blocks_qualification(recorder_device, monkeypatch) -> None:
    manifest_path, report_path, state = recorder_device

    def failed_onboarding(*args):
        raise ValueError("Setup control unavailable")

    monkeypatch.setattr(preparation, "_complete_audio_recorder_setup", failed_onboarding)
    report = preparation.prepare_device(manifest_path, report_path, "adb")

    assert report["qualified"] is False
    assert report["error"]["type"] == "ValueError"
    assert state["closed"] is True


@pytest.mark.parametrize("failure", ["contaminated_adb", "snapshot_restore"])
def test_initialization_failure_blocks_qualification_and_closes_environment(recorder_device, failure: str) -> None:
    manifest_path, report_path, state = recorder_device
    if failure == "contaminated_adb":
        state["adbOutput"] = b"gRPC child diagnostic\nFSQ_ADB_STDOUT_SENTINEL"
    else:
        state["restoreError"] = RuntimeError("Official snapshot restore failed")

    report = preparation.prepare_device(manifest_path, report_path, "adb")

    assert report["qualified"] is False
    assert json.loads(report_path.read_text())["qualified"] is False
    assert state["closed"] is True
    if failure == "contaminated_adb":
        assert state["setupStarted"] is False
    else:
        assert report["snapshotRestores"] == []


def test_missing_frozen_application_blocks_setup_without_installation(recorder_device, monkeypatch) -> None:
    manifest_path, report_path, state = recorder_device
    monkeypatch.setattr(preparation.device_setup, "get_installed_packages", lambda env: set())
    report = preparation.prepare_device(manifest_path, report_path, "adb")
    assert report["qualified"] is False
    assert "installation is not authorized" in report["error"]["message"]
    assert state["setupStarted"] is False
    assert state["closed"] is True


@pytest.mark.parametrize("onboarding,permission", [(True, True), (False, True), (True, False)])
def test_vlc_startup_requires_real_saved_onboarding_and_effective_permission(monkeypatch, onboarding, permission):
    def adb(adb_path, serial, *args):
        if "cat" in args:
            return '<map><boolean name="app_onboarding_done" value="' + str(onboarding).lower() + '" /></map>'
        return "Uid mode: MANAGE_EXTERNAL_STORAGE: " + ("allow" if permission else "deny")
    monkeypatch.setattr(preparation, "_adb", adb)
    state = preparation._vlc_startup_state("adb", "emulator")
    assert state == {"onboardingCompleted": onboarding, "allFilesAuthorized": permission}
    assert all(state.values()) is (onboarding and permission)


@pytest.mark.parametrize("returned,confirmed", [
    ({"disableSuppressAccessibilityService": True}, True),
    ({"appium:disableSuppressAccessibilityService": True}, True),
    ({}, False), ({"disableSuppressAccessibilityService": False}, False),
])
def test_vlc_preparation_requests_coexistence_and_refuses_unconfirmed_sessions(tmp_path, monkeypatch, returned, confirmed):
    import ast
    from appium import webdriver

    state = {"requests": [], "quit": 0, "snapshots": 0}

    class Driver:
        session_id = "preparation-session"
        capabilities = {"newCommandTimeout": 300, **returned}
        current_package = "org.videolan.vlc"
        current_activity = ".gui.MainActivity"

        def find_elements(self, *args):
            return []

        def quit(self):
            state["quit"] += 1

    def remote(url, *, options):
        state["requests"].append(options.to_capabilities())
        return Driver()

    class Runtime:
        def __init__(self, *args, **kwargs):
            self.namespace = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, code, **kwargs):
            tree = ast.parse(code)
            exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), "<preparation>", "exec"), self.namespace)
            return eval(compile(ast.Expression(tree.body[-1].value), "<preparation>", "eval"), self.namespace)

    monkeypatch.setattr(webdriver, "Remote", remote)
    monkeypatch.setattr(preparation, "RecoveryRuntime", Runtime)
    monkeypatch.setattr(preparation, "_appium_session_hashes", lambda *args: [])
    monkeypatch.setattr(preparation, "_vlc_startup_state", lambda *args: {"onboardingCompleted": True, "allFilesAuthorized": True})
    monkeypatch.setattr(preparation.app_snapshot, "save_snapshot", lambda *args: state.update(snapshots=state["snapshots"] + 1))
    monkeypatch.setattr(preparation, "launch_package", lambda *args: None)
    monkeypatch.setattr(preparation.adb_utils, "close_app", lambda *args: None)
    target = {"serial": "emulator-5554", "appiumUrl": "http://preparation"}
    if confirmed:
        proof = preparation._complete_vlc_setup(SimpleNamespace(controller=object()), tmp_path, target, "adb")
        assert proof["returnedAccessibilityCapabilities"] == returned
        assert state["snapshots"] == 1
    else:
        with pytest.raises(RuntimeError, match="did not confirm accessibility"):
            preparation._complete_vlc_setup(SimpleNamespace(controller=object()), tmp_path, target, "adb")
        assert state["snapshots"] == 0
    assert state["quit"] == 1
    assert state["requests"][0][SESSION_ACCESSIBILITY_CONFIG["capability"]] is True


def test_official_setup_valueerror_stops_before_snapshot_and_later_stages(recorder_device, monkeypatch):
    manifest_path, report_path, state = recorder_device
    snapshots = []
    app = preparation.device_setup.get_app_mapping("audio recorder")
    def fail(env):
        raise ValueError("original setup failure")
    monkeypatch.setattr(app, "setup", fail)
    monkeypatch.setattr(preparation.app_snapshot, "save_snapshot", lambda *args: snapshots.append(args))
    report = preparation.prepare_device(manifest_path, report_path, "adb")
    assert report["qualified"] is False
    assert report["error"] == {"type": "ValueError", "message": "original setup failure"}
    assert snapshots == [] and report["snapshotRestores"] == [] and report["apps"] == []
    assert state["closed"] is True
