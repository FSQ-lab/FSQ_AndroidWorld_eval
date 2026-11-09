"""Qualify the target without running benchmark tasks or fabricating app state.

After official setup clears Audio Recorder data, complete Get started / Apply
through the locked official UI controller, wait for the idle main surface and
app-created recordings directory, then save the official app snapshot. Qualification
records that prerequisite and live attestation checks it again; neither path
creates the directory or records audio on the app's behalf.
Task-initialized database diagnostics remain separate from this startup gate.
Qualification also requires clean ADB capture and every official app snapshot
to restore successfully, before any benchmark task or Agent is started.
Revision 11 verifies frozen local environment artifacts before device mutation,
serves the helper APK locally, requires strict snapshot restoration, and propagates
controller close errors. Qualification is not a substitute for the separate
all-task non-scoring rehearsal required before a formal Agent campaign.
Revision 12 preserves installed applications and completes VLC onboarding through
the frozen AMKernel PythonExec/Appium seam before saving its official snapshot.
Live attestation rechecks onboarding and effective all-files permission.
"""

from __future__ import annotations

from contextlib import contextmanager
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from typing import Any

from android_world.env import adb_utils, device_constants, env_launcher, tools
from android_world.env.setup_device import setup as device_setup
from android_world.utils import app_snapshot

from fsq_androidworld_eval.environment import (
    artifact_identity, close_environment, load_environment, local_app_data, strict_snapshot_restores,
)
from fsq_androidworld_eval.host_prerequisites import probe_host_media
from fsq_androidworld_eval.mcp_runtime import RecoveryRuntime

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

_DIRECTORY_READINESS = {
    "audio recorder": device_constants.AUDIORECORDER_DATA,
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


def _directory_readiness(
    adb_path: str, serial: str, app_names: set[str]
) -> list[dict[str, Any]]:
    rows = []
    for app_name, path in _DIRECTORY_READINESS.items():
        if app_name not in app_names:
            continue
        output = _adb(
            adb_path, serial, "shell",
            f"test -d {path} && echo present || echo missing",
        )
        rows.append({
            "app": app_name,
            "pathSha256": hashlib.sha256(path.encode()).hexdigest(),
            "present": output.splitlines()[-1:] == ["present"],
        })
    return rows


def _complete_audio_recorder_setup(env: Any, adb_path: str, serial: str) -> None:
    # Official AppSetup clears data. Complete its real UI before replacing the
    # snapshot, so later official restores do not return to the welcome screen.
    try:
        adb_utils.launch_app("audio recorder", env.controller)
        controller = tools.AndroidToolController(env=env.controller)
        controller.click_element("Get started")
        controller.click_element("Apply")
        deadline = time.monotonic() + 10
        while True:
            directory_ready = _directory_readiness(adb_path, serial, {"audio recorder"})[0]["present"]
            main_ready = any(element.text == "00:00" for element in env.controller.get_ui_elements())
            if directory_ready and main_ready:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("Audio Recorder did not finish its first-launch setup")
            time.sleep(0.2)
    finally:
        adb_utils.close_app("audio recorder", env.controller)
    app_snapshot.save_snapshot("audio recorder", env.controller)


def _vlc_startup_state(adb_path: str, serial: str) -> dict[str, bool]:
    preferences = _adb(adb_path, serial, "shell", "su", "0", "cat",
                       "/data/data/org.videolan.vlc/shared_prefs/org.videolan.vlc_preferences.xml")
    onboarding = any(node.get("name") == "app_onboarding_done" and node.get("value") == "true"
                     for node in ET.fromstring(preferences))
    permission = _adb(adb_path, serial, "shell", "appops", "get", "org.videolan.vlc", "MANAGE_EXTERNAL_STORAGE")
    return {"onboardingCompleted": onboarding, "allFilesAuthorized": "MANAGE_EXTERNAL_STORAGE: allow" in permission}


def _complete_vlc_setup(env: Any, project: Path, target: dict[str, Any], adb_path: str) -> dict[str, Any]:
    # The official setup may miss the uppercase SKIP control. Complete the real
    # UI through frozen AMKernel before saving the official application snapshot.
    with RecoveryRuntime(project, timeout_seconds=120) as runtime:
        creation = runtime.execute(
            "from appium import webdriver\n"
            "from appium.options.android import UiAutomator2Options\n"
            "from appium.webdriver.common.appiumby import AppiumBy\n"
            "from selenium.webdriver.support.ui import WebDriverWait\n"
            f"driver = webdriver.Remote({target['appiumUrl']!r}, options=UiAutomator2Options().load_capabilities("
            f"{{'platformName':'Android','appium:automationName':'UiAutomator2','appium:udid':{target['serial']!r},"
            "'appium:noReset':True,'appium:autoLaunch':False,'appium:skipUnlock':True,'appium:newCommandTimeout':300}))\n"
            "{'sessionId':driver.session_id,'newCommandTimeout':driver.capabilities.get('newCommandTimeout')}",
            timeout_seconds=90,
        )
        proof = runtime.execute('''
proof = {'sessionId': driver.session_id, 'mainActivityObserved': False, 'quitReturned': False}
try:
    driver.activate_app('org.videolan.vlc')
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_activity in {'.gui.MainActivity', '.gui.onboarding.OnboardingActivity'})
    if driver.current_activity == '.gui.onboarding.OnboardingActivity':
        wait.until(lambda d: d.find_element(AppiumBy.ID, 'org.videolan.vlc:id/skip_button')).click()
        wait.until(lambda d: d.current_activity == '.gui.MainActivity')
    buttons = driver.find_elements(AppiumBy.ID, 'org.videolan.vlc:id/grantPermissionButton')
    if buttons:
        buttons[0].click()
        wait.until(lambda d: d.find_element(AppiumBy.ID, 'android:id/button1')).click()
        wait.until(lambda d: d.current_package == 'com.android.settings')
        switch = wait.until(lambda d: d.find_element(AppiumBy.ID, 'android:id/switch_widget'))
        if switch.get_attribute('checked') == 'false':
            switch.click()
        wait.until(lambda d: d.find_element(AppiumBy.ID, 'android:id/switch_widget').get_attribute('checked') == 'true')
        driver.back()
    wait.until(lambda d: d.current_package == 'org.videolan.vlc' and d.current_activity == '.gui.MainActivity')
    proof['mainActivityObserved'] = True
except Exception as exc:
    proof['error'] = {'type': type(exc).__name__, 'message': str(exc)[:1000]}
finally:
    try:
        driver.terminate_app('org.videolan.vlc')
    finally:
        driver.quit()
        proof['quitReturned'] = True
proof
''', timeout_seconds=60)
    if creation.get("newCommandTimeout") != 300 or proof.get("sessionId") != creation.get("sessionId"):
        raise RuntimeError("VLC qualification session identity or negotiated timeout mismatch")
    if proof.get("mainActivityObserved") is not True or proof.get("quitReturned") is not True:
        raise RuntimeError(f"VLC first-launch UI qualification failed: {proof}")
    if _appium_session_hashes(target["appiumUrl"], adb_path, target["serial"]):
        raise RuntimeError("VLC qualification session absence is unproven")
    state = _vlc_startup_state(adb_path, target["serial"])
    if not all(state.values()):
        raise RuntimeError(f"VLC first-launch or file access is not ready: {state}")
    app_snapshot.save_snapshot("vlc", env.controller)
    return {**proof, **state, "snapshotSavedAfterUi": True}


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
    directories = _directory_readiness(
        adb_path, serial, {app["name"] for app in readiness.get("apps", [])}
    )
    expected_directories = {
        row["app"]: row for row in readiness.get("directories", [])
    }
    for observed in directories:
        expected = expected_directories.get(observed["app"])
        if observed != expected or observed["present"] is not True:
            mismatches[f"directory:{observed['app']}"] = {
                "expected": expected, "observed": observed,
            }
    if any(app["name"] == "vlc" for app in readiness.get("apps", [])):
        observed_vlc = _vlc_startup_state(adb_path, serial)
        expected_vlc = readiness.get("vlcStartup", {})
        if not all(observed_vlc.values()) or any(expected_vlc.get(key) is not True for key in observed_vlc):
            mismatches["startup:vlc"] = {"expected": expected_vlc, "observed": observed_vlc}
    result = {
        "device": device,
        "appiumBuild": observed_build,
        "apps": apps,
        "databases": databases,
        "directories": directories,
        "mismatches": mismatches,
        "qualified": not mismatches,
    }
    result["identitySha256"] = _sha256(result)
    return result

def prepare_device(
    manifest_path: Path, output_path: Path, adb_path: str, project: Path | None = None,
) -> dict[str, Any]:
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
        "schemaVersion": 2,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "startedAtUnix": started,
        "target": target,
        "appium": None,
        "device": None,
        "apps": [],
        "databases": [],
        "directories": [],
        "adbOutputIsolated": False,
        "snapshotRestores": [],
        "qualified": False,
        "error": None,
    }
    env = None
    environment_creation_started = False
    try:
        artifacts = artifact_identity((project or Path.cwd()).resolve())
        if artifacts != protocol.get("environmentArtifacts"):
            raise ValueError("local environment artifacts do not match manifest")
        report["environmentArtifacts"] = artifacts
        report["hostMedia"] = probe_host_media()
        if report["hostMedia"]["encoder"] != protocol["runtimeIdentity"]["mediaEncoder"]:
            raise ValueError("media encoder identity differs from frozen runtime")
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

        environment_creation_started = True
        env = load_environment(
            artifact_root=(project or Path.cwd()).resolve(),
            console_port=target["consolePort"],
            freeze_datetime=False,
            adb_path=adb_path,
            grpc_port=target["grpcPort"],
        )
        marker = b"FSQ_ADB_STDOUT_SENTINEL"
        captured = adb_utils.issue_generic_request(
            ["shell", "printf", marker.decode("ascii")], env.controller
        ).generic.output
        if captured != marker:
            raise RuntimeError(f"ADB capture contains non-command output: {captured[:1024]!r}")
        report["adbOutputIsolated"] = True
        with _launcher_compatible_setup(launcher_activities) as launcher_replacements:
            with local_app_data((project or Path.cwd()).resolve()):
                # Qualification resets official app state in the disposable
                # layer, but never reinstalls the frozen application artifacts.
                installed = device_setup.get_installed_packages(env)
                missing = [app.package_name() for app in app_classes if app.package_name() not in installed]
                if missing:
                    raise RuntimeError(f"Frozen installed apps are missing; installation is not authorized: {missing}")
                adb_utils.press_home_button(env.controller)
                adb_utils.set_root_if_needed(env.controller)
                for app in app_classes:
                    device_setup.setup_app(app, env)
                report["applicationInstallation"] = "preserved_existing_no_reinstall"
            if "audio recorder" in app_names:
                _complete_audio_recorder_setup(env, adb_path, serial)
            if "vlc" in app_names:
                report["vlcStartup"] = _complete_vlc_setup(
                    env, (project or Path.cwd()).resolve(), target, adb_path,
                )
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

        with strict_snapshot_restores():
            for app_name in app_names:
                app_snapshot.restore_snapshot(app_name, env.controller)
                report["snapshotRestores"].append({"app": app_name, "status": "restored"})
        if "vlc" in app_names and not all(_vlc_startup_state(adb_path, serial).values()):
            raise RuntimeError("Restored VLC snapshot lost first-launch readiness or authorized file access")

        report["directories"] = _directory_readiness(adb_path, serial, set(app_names))
        missing_directories = [row["app"] for row in report["directories"] if not row["present"]]
        if missing_directories:
            raise RuntimeError(
                "Complete first-launch setup through the app UI before qualification; "
                f"required app-created directories are missing: {missing_directories}"
            )

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
                close_environment(env)
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
            report["environmentClose"] = "unknown" if environment_creation_started else "not_created"
        report["completedAtUnix"] = time.time()
        report["durationSeconds"] = round(report["completedAtUnix"] - started, 3)
        report["identitySha256"] = _sha256(report)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare and qualify one AndroidWorld campaign target")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--project", default=".")
    parser.add_argument("--adb-path", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = prepare_device(Path(args.manifest), Path(args.output), args.adb_path, Path(args.project))
    raise SystemExit(0 if report["qualified"] else 1)


if __name__ == "__main__":
    main()
