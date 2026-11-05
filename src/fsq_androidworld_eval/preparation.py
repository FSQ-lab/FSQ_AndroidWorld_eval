from __future__ import annotations

from contextlib import contextmanager
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any

from android_world.env import adb_utils, env_launcher
from android_world.env.setup_device import setup as device_setup

from fsq_androidworld_eval.runner import (
    ANDROID_WORLD_REVISION,
    HARNESS_REVISION,
    _appium_session_hashes,
    _request_json,
    _sha256,
)

_DATABASE_READINESS = {
    "joplin": "/data/data/net.cozic.joplin/databases/joplin.sqlite",
    "open tracks sports tracker": "/data/data/de.dennisguse.opentracks/databases/database.db",
    "osmand": "/data/data/net.osmand/databases/map_markers_db",
    "pro expense": "/data/data/com.arduia.expense/databases/accounting.db",
    "simple calendar pro": "/data/data/com.simplemobiletools.calendar.pro/databases/events.db",
    "tasks": "/data/data/org.tasks/databases/database",
    "vlc": "/data/data/org.videolan.vlc/app_db/vlc_media.db",
}


def _adb(adb_path: str, serial: str, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        [adb_path, "-s", serial, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if check and completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()[-2048:]
        raise RuntimeError(f"adb {' '.join(args)} failed: {message}")
    return completed.stdout.strip()


def _package_version(adb_path: str, serial: str, package: str) -> dict[str, str | None]:
    output = _adb(adb_path, serial, "shell", "dumpsys", "package", package)

    def value(pattern: str) -> str | None:
        match = re.search(pattern, output)
        return match.group(1) if match else None

    return {
        "package": package,
        "versionName": value(r"versionName=([^\s]+)"),
        "versionCode": value(r"versionCode=(\d+)"),
    }


def _database_exists(adb_path: str, serial: str, path: str) -> bool:
    output = _adb(
        adb_path,
        serial,
        "shell",
        "su",
        "0",
        "sh",
        "-c",
        f"test -e {path} && echo present || echo missing",
    )
    return output.splitlines()[-1:] == ["present"]


def _required_app_names(manifest: dict[str, Any]) -> list[str]:
    return sorted(
        {str(app) for task in manifest["tasks"] for app in task.get("apps", [])}
    )


@contextmanager
def _launcher_compatible_setup(activities: dict[str, str]):
    original = adb_utils.issue_generic_request
    replacements: list[str] = []

    def issue(args, env, timeout_sec=10):
        command = list(args) if not isinstance(args, str) else args.split()
        if command[:2] == ["shell", "monkey"] and "-p" in command:
            package = command[command.index("-p") + 1]
            replacements.append(package)
            command = [
                "shell",
                "am",
                "start",
                "-W",
                "-a",
                "android.intent.action.MAIN",
                "-c",
                "android.intent.category.LAUNCHER",
                "-n",
                activities[package],
            ]
        return original(command, env, timeout_sec)

    adb_utils.issue_generic_request = issue
    try:
        yield replacements
    finally:
        adb_utils.issue_generic_request = original


def attest_device(readiness: dict[str, Any], adb_path: str) -> dict[str, Any]:
    target = readiness["target"]
    serial = target["serial"]
    observed_appium = _request_json(target["appiumUrl"].rstrip("/") + "/status")
    sessions = _appium_session_hashes(target["appiumUrl"], adb_path, serial)
    device = {
        "apiLevel": int(_adb(adb_path, serial, "shell", "getprop", "ro.build.version.sdk")),
        "abi": _adb(adb_path, serial, "shell", "getprop", "ro.product.cpu.abi"),
        "buildFingerprint": _adb(
            adb_path, serial, "shell", "getprop", "ro.build.fingerprint"
        ),
        "screenSize": _adb(adb_path, serial, "shell", "wm", "size"),
        "timezone": _adb(
            adb_path, serial, "shell", "getprop", "persist.sys.timezone"
        ),
        "date": _adb(adb_path, serial, "shell", "date", "+%Y-%m-%d"),
    }
    expected_device = readiness["device"]
    stable_device_fields = ("apiLevel", "abi", "buildFingerprint", "screenSize", "timezone")
    mismatches = {
        field: {"expected": expected_device.get(field), "observed": device.get(field)}
        for field in stable_device_fields
        if expected_device.get(field) != device.get(field)
    }
    expected_build = readiness.get("appium", {}).get("value", {}).get("build")
    observed_build = observed_appium.get("value", {}).get("build")
    if expected_build != observed_build:
        mismatches["appiumBuild"] = {
            "expected": expected_build,
            "observed": observed_build,
        }
    if sessions:
        mismatches["appiumSessions"] = {"expected": [], "observed": sessions}

    apps = []
    for expected in readiness.get("apps", []):
        observed = _package_version(adb_path, serial, expected["package"])
        apps.append(observed)
        if observed != {
            "package": expected["package"],
            "versionName": expected["versionName"],
            "versionCode": expected["versionCode"],
        }:
            mismatches[f"app:{expected['name']}"] = {
                "expected": expected,
                "observed": observed,
            }
    databases = []
    for expected in readiness.get("databases", []):
        path = _DATABASE_READINESS[expected["app"]]
        present = _database_exists(adb_path, serial, path)
        databases.append({"app": expected["app"], "present": present})
    result = {
        "device": device,
        "appiumBuild": observed_build,
        "apps": apps,
        "databases": databases,
        "mismatches": mismatches,
        "qualified": not mismatches,
    }
    result["identitySha256"] = _sha256(result)
    return result

def prepare_device(manifest_path: Path, output_path: Path, adb_path: str) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    protocol = manifest.get("protocol", {})
    if manifest.get("schemaVersion") != 2:
        raise ValueError("device preparation requires campaign manifest schema 2")
    if protocol.get("harnessRevision") != HARNESS_REVISION:
        raise ValueError("device preparation harness revision mismatch")
    if protocol.get("androidWorldRevision") != ANDROID_WORLD_REVISION:
        raise ValueError("device preparation AndroidWorld revision mismatch")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    target = manifest["target"]
    serial = target["serial"]
    started = time.time()
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "startedAtUnix": started,
        "target": target,
        "appium": None,
        "device": None,
        "apps": [],
        "databases": [],
        "qualified": False,
        "error": None,
    }
    env = None
    try:
        report["appium"] = _request_json(target["appiumUrl"].rstrip("/") + "/status")
        appium_sessions = _appium_session_hashes(
            target["appiumUrl"], adb_path, serial
        )
        report["appiumSessionBaseline"] = appium_sessions
        if appium_sessions:
            raise RuntimeError("Appium has pre-existing sessions before device preparation")
        if _adb(adb_path, serial, "get-state") != "device":
            raise RuntimeError(f"ADB target {serial} is not ready")
        runtime_target = {
            "apiLevel": int(_adb(adb_path, serial, "shell", "getprop", "ro.build.version.sdk")),
            "abi": _adb(adb_path, serial, "shell", "getprop", "ro.product.cpu.abi"),
            "buildFingerprint": _adb(adb_path, serial, "shell", "getprop", "ro.build.fingerprint"),
            "screenSize": _adb(adb_path, serial, "shell", "wm", "size"),
            "timezone": _adb(adb_path, serial, "shell", "getprop", "persist.sys.timezone"),
        }
        if runtime_target["apiLevel"] != target["apiLevel"] or runtime_target["abi"] != target["abi"]:
            raise RuntimeError(f"runtime target mismatch: {runtime_target}")
        report["device"] = runtime_target

        app_names = _required_app_names(manifest)
        app_classes = []
        for app_name in app_names:
            app_class = device_setup.get_app_mapping(app_name)
            if app_class is None:
                raise RuntimeError(f"no AndroidWorld setup mapping for {app_name!r}")
            app_classes.append(app_class)
        launcher_activities = {
            adb_utils.extract_package_name(activity): activity
            for app_name in app_names
            if (activity := adb_utils.get_adb_activity(app_name))
        }

        env = env_launcher.load_and_setup_env(
            console_port=target["consolePort"],
            emulator_setup=False,
            freeze_datetime=False,
            adb_path=adb_path,
            grpc_port=target["grpcPort"],
        )
        with _launcher_compatible_setup(launcher_activities) as launcher_replacements:
            device_setup.setup_apps(env, tuple(app_classes))
        report["launcherCompatibility"] = {
            "mode": "main_launcher_intent_replaces_monkey",
            "packages": sorted(set(launcher_replacements)),
        }
        env_launcher.setup_env(env, emulator_setup=False, freeze_datetime=True)
        report["device"]["timezone"] = _adb(
            adb_path, serial, "shell", "getprop", "persist.sys.timezone"
        )
        report["device"]["datetime"] = _adb(
            adb_path, serial, "shell", "date", "+%Y-%m-%dT%H:%M:%S%z"
        )
        if report["device"]["timezone"] != "UTC":
            raise RuntimeError("AndroidWorld datetime setup did not set timezone to UTC")

        for app_name in app_names:
            activity = adb_utils.get_adb_activity(app_name)
            if not activity:
                raise RuntimeError(f"no deterministic launcher activity for {app_name!r}")
            package = adb_utils.extract_package_name(activity)
            launch_output = _adb(
                adb_path, serial, "shell", "am", "start", "-W", "-n", activity
            )
            if "Error:" in launch_output:
                raise RuntimeError(f"failed to launch {app_name}: {launch_output[-1024:]}")
            report["apps"].append(
                {
                    "name": app_name,
                    "activity": activity,
                    **_package_version(adb_path, serial, package),
                }
            )
            _adb(adb_path, serial, "shell", "am", "force-stop", package)

        for app_name, database_path in sorted(_DATABASE_READINESS.items()):
            if app_name not in app_names:
                continue
            present = _database_exists(adb_path, serial, database_path)
            report["databases"].append(
                {"app": app_name, "pathSha256": hashlib.sha256(database_path.encode()).hexdigest(), "present": present}
            )

        report["qualified"] = True
    except Exception as exc:
        report["error"] = {"type": type(exc).__name__, "message": str(exc)[:4096]}
    finally:
        if env is not None:
            try:
                env.close()
            except Exception as exc:
                report["environmentClose"] = f"failed:{type(exc).__name__}"
                report["qualified"] = False
                if report["error"] is None:
                    report["error"] = {
                        "type": type(exc).__name__,
                        "message": "AndroidWorld environment failed to close",
                    }
            else:
                report["environmentClose"] = "closed"
        else:
            report["environmentClose"] = "not_created"
        report["completedAtUnix"] = time.time()
        report["durationSeconds"] = round(report["completedAtUnix"] - started, 3)
        report["identitySha256"] = _sha256(report)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare and qualify one AndroidWorld campaign target")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--adb-path", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = prepare_device(Path(args.manifest), Path(args.output), args.adb_path)
    raise SystemExit(0 if report["qualified"] else 1)


if __name__ == "__main__":
    main()
