import json
from pathlib import Path

from types import SimpleNamespace

import pytest
from fsq_androidworld_eval import preparation
from fsq_androidworld_eval.runner import ANDROID_WORLD_REVISION, HARNESS_REVISION, _sha256


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


def test_launcher_compatibility_replaces_monkey_with_main_intent(monkeypatch) -> None:
    observed = []

    def original(args, env, timeout_sec=10):
        observed.append(list(args))
        return "response"

    monkeypatch.setattr(preparation.adb_utils, "issue_generic_request", original)

    with preparation._launcher_compatible_setup(
        {"example.app": "example.app/.MainActivity"}
    ) as replacements:
        response = preparation.adb_utils.issue_generic_request(
            [
                "shell",
                "monkey",
                "-p",
                "example.app",
                "-candroid.intent.category.LAUNCHER",
                "1",
            ],
            object(),
        )

    assert response == "response"
    assert replacements == ["example.app"]
    assert observed == [
        [
            "shell",
            "am",
            "start",
            "-W",
            "-a",
            "android.intent.action.MAIN",
            "-c",
            "android.intent.category.LAUNCHER",
            "-n",
            "example.app/.MainActivity",
        ]
    ]




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
            "androidWorldRevision": ANDROID_WORLD_REVISION,
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
    state = {"directory": True, "closed": False}
    target = {
        "serial": "emulator-5554", "consolePort": 5554, "grpcPort": 8554,
        "appiumUrl": "http://127.0.0.1:4723", "apiLevel": 33, "abi": "arm64-v8a",
    }
    manifest = {
        "schemaVersion": 2, "campaignId": "recorder-readiness",
        "protocol": {"harnessRevision": HARNESS_REVISION, "androidWorldRevision": ANDROID_WORLD_REVISION},
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
    monkeypatch.setattr(preparation.env_launcher, "load_and_setup_env", lambda **kwargs: SimpleNamespace(close=lambda: state.update(closed=True)))
    monkeypatch.setattr(preparation.env_launcher, "setup_env", lambda *args, **kwargs: None)
    monkeypatch.setattr(preparation.device_setup, "setup_apps", lambda *args: None)
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
