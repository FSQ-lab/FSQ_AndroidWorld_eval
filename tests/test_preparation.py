import json
from pathlib import Path

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
