"""FSQ-only future qualification and single-attempt campaign gates.

No Android, FSQ, AMKernel or Appium module is imported by the offline consumers.
Live subcommands require independently reviewed, target-exclusive authorization.
Qualification consumes existing apps/snapshots: it never installs, repairs, saves a
replacement snapshot, or invents a first-launch UI recipe. Rehearsal is a separate
non-scoring official lifecycle check, not evidence that the FSQ policy succeeds.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any
import uuid
from fsq_androidworld_eval.fsq_evidence import EvidenceError, validate_native_evidence

CALIBRATION_TASKS = (
    "SystemWifiTurnOff", "SystemBrightnessMax", "ClockStopWatchRunning",
    "ClockTimerEntry", "ContactsAddContact", "MarkorCreateNote", "MarkorEditNote",
    "FilesMoveFile", "SimpleCalendarAddOneEvent", "CameraTakePhoto",
    "TasksHighPriorityTasks", "SimpleCalendarEventsOnDate",
)
READINESS_KIND = "fsq_androidworld_readiness"
CLOCK_BASELINE = {"timezone": "UTC", "autoTime": "0", "autoTimeZone": "0"}
REPORT_KINDS = {stage: f"fsq_androidworld_{stage}" for stage in ("rehearse", "calibrate", "run")}
OUTER_TIMEOUT_ALLOWANCE = 610
ANSWER_SOURCE = "agent_runtime.runner.tool_output.summary"


def _bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = child
    return value


def _load(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"evidence must not be a symlink: {path}")
    value = json.loads(path.read_bytes(), object_pairs_hook=_unique,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite evidence")))
    if not isinstance(value, dict):
        raise ValueError("evidence must be a JSON object")
    return value


def _save(path: Path, value: dict[str, Any]) -> None:
    """Publish once; never overwrite a terminal record, including failed records."""
    data = _bytes(value) + b"\n"
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("xb") as stream:
        os.chmod(temporary, 0o600)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()


def _sealed(value: dict[str, Any]) -> dict[str, Any]:
    return {**value, "identitySha256": _digest(value)}


def _check_seal(value: dict[str, Any]) -> None:
    payload = {key: child for key, child in value.items() if key != "identitySha256"}
    if value.get("identitySha256") != _digest(payload):
        raise ValueError("evidence identity hash mismatch")


def _binding(manifest_path: Path, manifest: dict[str, Any], authorization: dict[str, Any]) -> dict[str, Any]:
    return {"manifestSha256": _hash(manifest_path), "target": manifest["target"],
            "identitiesSha256": _digest(manifest["identities"]),
            "provider": "github_copilot", "model": "gpt-6.1-sol",
            "authorizationSha256": _digest(authorization)}


def _authorization_checks(manifest_path: Path, manifest: dict[str, Any], authorization: dict[str, Any], now: float) -> None:
    if (authorization.get("schemaVersion") != 1 or authorization.get("kind") != "fsq_execution_authorization"
            or authorization.get("manifestSha256") != _hash(manifest_path)):
        raise ValueError("missing exact FSQ execution authorization")
    _require_disposable(authorization)
    observed = manifest["identities"].get("nativeProviderMetadata", {})
    if observed.get("provider") != "github_copilot" or observed.get("model") != "gpt-6.1-sol":
        raise ValueError("frozen native provider/model readiness is still pending or changed")
    if "qualify" not in authorization.get("approvedStages", []):
        raise ValueError("FSQ qualification stage was not explicitly approved")
    review, model = authorization.get("independentReview", {}), authorization.get("nativeModelCall", {})
    if (review.get("status") != "approved" or model.get("status") != "passed_native_responses"
            or model.get("provider") != "github_copilot" or model.get("requestedModel") != "gpt-6.1-sol"):
        raise ValueError("FSQ independent review/native model-call approval missing")
    for receipt in (review, model):
        if not isinstance(receipt.get("path"), str) or receipt.get("sha256") != _hash(Path(receipt["path"])):
            raise ValueError("FSQ authorization receipt hash drift")
    resource = authorization["resource"]
    if any(resource.get(key) != manifest["target"][key] for key in ("serial", "consolePort", "grpcPort", "adbPath")):
        raise ValueError("FSQ exclusive resource target drift")
    start, end = resource.get("notBeforeUnix"), resource.get("validUntilUnix")
    if (type(start) not in (int, float) or type(end) not in (int, float)
            or not math.isfinite(start) or not math.isfinite(end) or not start <= now < end
            or not isinstance(resource.get("authority"), str) or not resource["authority"].strip()):
        raise ValueError("FSQ exclusive resource approval absent or expired")


def _fresh(report: dict[str, Any], now: float, authorization: dict[str, Any]) -> None:
    completed = report.get("completedAtUnix")
    started = report.get("startedAtUnix")
    if (type(completed) not in (int, float) or type(started) not in (int, float)
            or not math.isfinite(completed) or not math.isfinite(started)
            or not authorization["resource"]["notBeforeUnix"] <= started <= completed <= now):
        raise ValueError("gate report lies outside its explicit resource grant or has invalid timestamps")


def _apps(manifest: dict[str, Any]) -> list[str]:
    return sorted({app for spec in manifest["tasks"] for app in spec["apps"]})


def _task_identity(spec: dict[str, Any]) -> dict[str, Any]:
    return {key: spec[key] for key in ("index", "name", "paramsSha256")}


def _suite_specs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    specs = manifest.get("tasks", [])
    if (len(specs) != 116 or len({row["index"] for row in specs}) != 116
            or len({row["name"] for row in specs}) != 116):
        raise ValueError("FSQ gate requires all 116 unique frozen tasks")
    return specs


def validate_readiness(path: Path, manifest_path: Path, manifest: dict[str, Any],
                       authorization: dict[str, Any], *, now: float | None = None) -> dict[str, Any]:
    """Offline FSQ-only consumer; unrelated historical receipts cannot pass."""
    _authorization_checks(manifest_path, manifest, authorization, time.time() if now is None else now)
    report = _load(path)
    _check_seal(report)
    if report.get("kind") != READINESS_KIND or report.get("schemaVersion") != 1:
        raise ValueError("readiness must be an FSQ-only readiness report")
    if report.get("binding") != _binding(manifest_path, manifest, authorization):
        raise ValueError("readiness manifest/target/resource/model/review authorization drift")
    _fresh(report, time.time() if now is None else now, authorization)
    if report.get("qualified") is not True or report.get("error") is not None:
        raise ValueError("FSQ readiness qualification failed")
    checks = report.get("checks", {})
    for name in ("assets", "apps", "snapshots", "baseData", "utc", "coreEnvironment", "adbIsolation"):
        if checks.get(name) is not True:
            raise ValueError(f"FSQ readiness missing actual prerequisite: {name}")
    if report.get("clock") != CLOCK_BASELINE:
        raise ValueError("readiness lacks the official UTC clock baseline")
    if report.get("cleanup", {}).get("environment") != "closed":
        raise ValueError("readiness environment cleanup is unknown")
    if [row.get("name") for row in report.get("apps", [])] != _apps(manifest):
        raise ValueError("readiness app coverage mismatch")
    if ([row.get("app") for row in report.get("snapshotRestores", [])] != _apps(manifest)
            or any(row.get("status") != "restored" for row in report.get("snapshotRestores", []))):
        raise ValueError("readiness snapshot coverage mismatch")
    if not report.get("environmentArtifacts") or not report.get("device"):
        raise ValueError("readiness lacks pinned assets/device identity")
    return report


def _artifact_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("episode artifacts must not contain symlinks")
        if path.is_file():
            rows.append({"path": str(path.relative_to(root)), "sha256": _hash(path), "bytes": path.stat().st_size})
    return rows


def _check_artifacts(root: Path, rows: list[dict[str, Any]]) -> None:
    if not rows or rows != _artifact_rows(root):
        raise ValueError("episode artifact coverage/hash drift")


def _reward(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def halt_reason(record: dict[str, Any], *, errors: list[str] | None = None,
                outer_process: dict[str, Any] | None = None) -> str | None:
    """One native terminal decision, after owned cleanup and evidence consumption."""
    cleanup = record.get("cleanup", {})
    if (record.get("cleanupFailure") is True or cleanup.get("taskTearDown") != "completed"
            or cleanup.get("environment") != "closed"):
        return "unknown_or_failed_cleanup"
    process = record.get("workerProcess")
    if record.get("attemptStarted") is True:
        if not isinstance(process, dict) or process.get("groupCleanup") != "settled" or process.get("workerExitObserved") is not True:
            return "unknown_worker_cleanup"
        if process.get("terminated") or process.get("killed"):
            return "forced_worker"
    outer = outer_process if outer_process is not None else record.get("outerProcess", {})
    if outer.get("forced"):
        return "forced_worker"
    if record.get("evidenceFailure"):
        return "native_evidence_failure"
    if record.get("classification") in {"invalid_identity", "invalid_identity_drift", "invalid_authorization", "invalid_readiness"}:
        return "global_identity_drift"
    classification = record.get("classification")
    if isinstance(classification, str) and classification.startswith("invalid_"):
        return classification
    if record.get("error") is not None:
        return "episode_error"
    native = record.get("fsq") or {}
    answer = native.get("mainAnswer")
    if isinstance(answer, dict) and answer.get("status") != "valid":
        return "exact_main_summary"
    if native.get("nativeStatus") in {"error", "cancelled"}:
        return "native_runtime_error"
    if outer.get("errorType"):
        return "outer_process_error"
    if outer and outer.get("exitCode") != 0:
        return "outer_process_exit"
    if errors:
        return errors[0]
    return None


def _checked_reference(root: Path, reference: dict[str, Any]) -> Path:
    if not isinstance(reference, dict) or not isinstance(reference.get("path"), str):
        raise ValueError("required private artifact reference missing")
    candidate = Path(reference["path"])
    path = candidate if candidate.is_absolute() else root / candidate
    resolved_root, resolved = root.resolve(), path.resolve()
    if resolved_root not in resolved.parents or path.is_symlink():
        raise ValueError("private artifact escapes immutable episode directory")
    if reference.get("sha256") != _hash(path):
        raise ValueError("private artifact reference hash drift")
    return path


def operational_errors(record: dict[str, Any], spec: dict[str, Any], manifest_sha: str,
                       *, episode_dir: Path, stage: str, manifest: dict[str, Any],
                       readiness_sha: str, authorization_sha: str) -> list[str]:
    """Consume complete producer-shaped evidence, not internally rehashed claims."""
    from fsq_androidworld_eval.fsq_runner import native_episode_id
    errors = []
    expected_id = native_episode_id(manifest["campaignId"], stage, spec["index"])
    expected = {"kind": "fsq_androidworld_episode", "stage": stage,
                "campaignId": manifest["campaignId"], "episodeId": expected_id,
                "manifestSha256": manifest_sha, "readinessSha256": readiness_sha,
                "authorizationSha256": authorization_sha, "target": manifest["target"],
                "task": _task_identity(spec), "attempt": 1}
    if any(record.get(key) != value for key, value in expected.items()):
        errors.append("episode_identity_binding")
    if record.get("attemptStarted") is not True or record.get("complete") is not True:
        errors.append("incomplete_attempt")
    if record.get("classification") not in {"passed", "failed"} or not _reward(record.get("officialReward")):
        errors.append("invalid_official_evaluation")
    reason = halt_reason(record)
    if reason:
        errors.append(reason)
    try:
        trusted = _load(_checked_reference(episode_dir, record.get("workerProcessReference")))
        if trusted != record.get("workerProcess"):
            errors.append("worker_process_binding")
        outcome = _load(_checked_reference(episode_dir, (record.get("fsq") or {}).get("privateOutcome")))
    except (OSError, ValueError, TypeError):
        return errors + ["private_native_outcome"]
    process, result = outcome.get("process", {}), outcome.get("result") or {}
    if process != trusted:
        errors.append("worker_process_binding")
    if (process.get("spawnCount") != 1 or process.get("workerExitObserved") is not True
            or process.get("exitCode") != 0 or process.get("groupCleanup") != "settled"):
        errors.append("worker_exit")
    if result.get("status") != "completed":
        errors.append("full_native_execution")
    target = result.get("nativeTarget", {})
    if target.get("effectiveProvider") != "github_copilot" or target.get("effectiveModel") != "gpt-6.1-sol":
        errors.append("native_model_identity")
    try:
        proof = validate_native_evidence(outcome, episode_root=episode_dir, expected_task_id=expected_id,
                                         expected_serial=manifest["target"]["serial"], maximum=spec["maxActions"])
    except (EvidenceError, OSError, TypeError, KeyError):
        errors.append("native_evidence")
        proof = None
    if proof is not None:
        if proof["answer"].get("status") != "valid":
            errors.append("exact_main_summary")
        if (record.get("fsq") or {}).get("killEvidence") != proof["killEvidence"]:
            errors.append("kill_observation_binding")
    evaluator = record.get("evaluator", {})
    if (record.get("evaluatorCalls") != 1 or evaluator.get("called") is not True
            or evaluator.get("afterFullFsq") is not True
            or evaluator.get("ordering") != "after_complete_native_FSQ_return_and_internal_verification"
            or evaluator.get("implementation") != "android_world.task_eval.is_successful"):
        errors.append("official_evaluator_ordering")
    try:
        diagnostic = _load(_checked_reference(episode_dir, evaluator.get("diagnostics")))
        if diagnostic.get("task") != {"name": spec["name"], "paramsSha256": spec["paramsSha256"]}:
            errors.append("evaluator_artifact_identity")
        if diagnostic.get("officialReward") != record.get("officialReward") or diagnostic.get("outcome") != "returned":
            errors.append("evaluator_artifact_reward")
    except (OSError, ValueError, TypeError):
        errors.append("native_or_evaluator_artifacts")
    return errors


def _selected(manifest: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    specs = _suite_specs(manifest)
    if stage == "calibrate":
        by_name = {spec["name"]: spec for spec in specs}
        try:
            return [by_name[name] for name in CALIBRATION_TASKS]
        except KeyError as error:
            raise ValueError(f"frozen suite lacks original calibration task: {error}") from error
    return specs


def validate_stage_report(path: Path, stage: str, manifest_path: Path, manifest: dict[str, Any],
                          authorization: dict[str, Any], *, readiness_path: Path,
                          now: float | None = None) -> dict[str, Any]:
    validate_readiness(readiness_path, manifest_path, manifest, authorization, now=now)
    if stage not in authorization.get("approvedStages", []):
        raise ValueError("FSQ report stage was not explicitly approved")
    report = _load(path)
    _check_seal(report)
    if report.get("schemaVersion") != 1 or report.get("kind") != REPORT_KINDS[stage]:
        raise ValueError("wrong FSQ stage report kind")
    if report.get("binding") != _binding(manifest_path, manifest, authorization):
        raise ValueError("stage manifest/target/resource/model/review authorization drift")
    _fresh(report, time.time() if now is None else now, authorization)
    if report.get("readinessSha256") != _hash(readiness_path):
        raise ValueError("stage readiness bytes drift")
    specs = _selected(manifest, stage)
    attempts = report.get("attempts", [])
    if report.get("taskCount") != len(specs) or len(attempts) != len(specs):
        raise ValueError("stage task coverage mismatch")
    if len({row.get("attemptId") for row in attempts}) != len(attempts) or any(not row.get("attemptId") for row in attempts):
        raise ValueError("stage duplicate business attempt")
    if report.get("taskSetSha256") != _digest([_task_identity(spec) for spec in specs]):
        raise ValueError("stage task set hash mismatch")
    for row, spec in zip(attempts, specs, strict=True):
        if row.get("outerProcess", {}).get("forced") or row.get("operationalErrors"):
            raise ValueError("stage attempt has forced execution or operational errors")
        if row.get("task") != _task_identity(spec):
            raise ValueError("stage coverage/order/parameter drift")
        relative = Path(row.get("directory", ""))
        if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("episodes",):
            raise ValueError("invalid attempt artifact path")
        root = path.parent / relative
        if root.is_symlink() or root.parent.is_symlink():
            raise ValueError("stage attempt directories must not be symlinks")
        _check_artifacts(root, row.get("artifacts", []))
        record = _load(root / "result.json")
        if stage == "rehearse":
            if not _rehearsal_valid(record, spec, _hash(manifest_path)):
                raise ValueError("official rehearsal lifecycle failed")
        elif operational_errors(record, spec, _hash(manifest_path), episode_dir=root, stage=stage,
                                manifest=manifest, readiness_sha=_hash(readiness_path),
                                authorization_sha=_digest(authorization)):
            raise ValueError("native calibration/run operational protocol failed")
    if report.get("qualified") is not True or report.get("haltReason") is not None:
        raise ValueError("FSQ stage was not qualified")
    return report


def _runner_api() -> Any:
    from fsq_androidworld_eval import fsq_runner
    return fsq_runner


def _load_candidate(path: Path, project: Path) -> dict[str, Any]:
    from fsq_androidworld_eval.fsq_manifest import load_manifest
    return load_manifest(path, project)


def _adb(target: dict[str, Any], *arguments: str) -> str:
    from fsq_androidworld_eval.android_transport import scoped_adb_output
    return scoped_adb_output(target["adbPath"], target["serial"], *arguments, timeout=20)


def _clock_probe(target: dict[str, Any]) -> dict[str, str]:
    """Observe task-owned clock state without changing the target."""
    return {"timezone": _adb(target, "shell", "getprop", "persist.sys.timezone"),
            "autoTime": _adb(target, "shell", "settings", "get", "global", "auto_time"),
            "autoTimeZone": _adb(target, "shell", "settings", "get", "global", "auto_time_zone")}


def _device_probe(manifest: dict[str, Any]) -> dict[str, Any]:
    """Read-only stable app/device identity; no session, launch, install or repair."""
    from android_world.env.setup_device import setup
    target = manifest["target"]
    if target["serial"] != f"emulator-{target['consolePort']}":
        raise RuntimeError("official console-port controller cannot bind a different ADB serial")
    device = {name: _adb(target, "shell", "getprop", prop) for name, prop in (
        ("apiLevel", "ro.build.version.sdk"), ("abi", "ro.product.cpu.abi"),
        ("buildFingerprint", "ro.build.fingerprint"))}
    clock = _clock_probe(target)
    device["bootId"] = _adb(target, "shell", "cat", "/proc/sys/kernel/random/boot_id")
    uuid.UUID(device["bootId"])
    device["screenSize"] = _adb(target, "shell", "wm", "size")
    if device["apiLevel"] != "33":
        raise RuntimeError(f"existing official target must be API 33; observed apiLevel={device['apiLevel']!r}, clock={clock!r}; no automatic repair is authorized")
    if _adb(target, "get-state") != "device" or _adb(target, "shell", "getprop", "sys.boot_completed") != "1":
        raise RuntimeError("ADB target is not boot-complete")
    for service in ("activity", "package", "settings", "window"):
        if not _adb(target, "shell", "service", "check", service).endswith(": found"):
            raise RuntimeError(f"core Android service missing: {service}")
    for process in ("system_server", "surfaceflinger"):
        pids = _adb(target, "shell", "pidof", process).split()
        if not pids or any(not pid.isdigit() or int(pid) <= 0 for pid in pids):
            raise RuntimeError(f"core Android process missing: {process}")
    apps = []
    for name in _apps(manifest):
        app = setup.get_app_mapping(name)
        if app is None:
            raise RuntimeError(f"official app mapping unavailable: {name}")
        package = app.package_name()
        paths = _adb(target, "shell", "pm", "path", package).splitlines()
        if not paths or any(not path.startswith("package:") for path in paths):
            raise RuntimeError(f"required installed app missing: {name} ({package}); no install fallback")
        hashes = []
        for entry in paths:
            path = entry.removeprefix("package:")
            sha = _adb(target, "shell", "sha256sum", path).split()[0]
            if len(sha) != 64 or any(char not in "0123456789abcdef" for char in sha):
                raise RuntimeError(f"installed app checksum unavailable: {package}")
            hashes.append({"path": path, "sha256": sha})
        version_lines = _adb(target, "shell", "dumpsys", "package", package).splitlines()
        versions = sorted(line.strip() for line in version_lines if line.strip().startswith(("versionCode=", "versionName=")))
        if not versions:
            raise RuntimeError(f"installed app version unavailable: {package}")
        names = app.apk_names
        apk_names = ([names] if names else []) if isinstance(names, str) else list(names)
        apps.append({"name": name, "package": package, "versions": versions, "apks": hashes,
                     "officialApkNames": apk_names})
    return {"device": device, "apps": apps, "clock": clock}


def _check_installed_pins(apps: list[dict[str, Any]], artifacts: dict[str, Any]) -> None:
    pins = {row["name"]: row["sha256"] for row in artifacts.get("artifacts", [])}
    for app in apps:
        names = app.get("officialApkNames", [])
        if not names:
            continue  # System APKs are bound by OS fingerprint plus actual APK hashes.
        allowed = {pins[name] for name in names if name in pins}
        observed = {row["sha256"] for row in app["apks"]}
        if not allowed or not observed or not observed <= allowed:
            raise RuntimeError(f"installed official APK differs from source-pinned assets: {app['name']}; no reinstall fallback")


def _shared_assets_present(manifest: dict[str, Any], artifacts: dict[str, Any]) -> list[dict[str, Any]]:
    if "osmand" not in _apps(manifest):
        return []
    from android_world.env.setup_device import apps
    pins = {row["name"]: row["sha256"] for row in artifacts["artifacts"]}
    rows = []
    for name in apps.OsmAndApp.MAP_NAMES:
        destination = apps.OsmAndApp.DEVICE_MAPS_PATH.rstrip("/") + "/" + name
        observed = _adb(manifest["target"], "shell", "sha256sum", destination).split()
        if not observed or observed[0] != pins[name]:
            raise RuntimeError(f"required existing shared map missing or changed: {name}; no repair fallback")
        rows.append({"name": name, "sha256": pins[name], "status": "verified_existing"})
    return rows


def attest_readiness(manifest: dict[str, Any], readiness: dict[str, Any]) -> None:
    """Bind stable identity before mutation; official lifecycles own clock state."""
    observed = _device_probe(manifest)
    if observed["device"] != readiness["device"] or observed["apps"] != readiness["apps"]:
        raise RuntimeError("global device/app identity drift from FSQ qualification")


def _base_data(env: Any, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    from android_world.env import adb_utils, device_constants
    # These are actual app-created databases consumed by official task helpers.
    # Missing base state is a prerequisite failure, never an evaluator-made DB.
    databases = {
        "joplin": "/data/data/net.cozic.joplin/databases/joplin.sqlite",
        "open tracks sports tracker": "/data/data/de.dennisguse.opentracks/databases/database.db",
        "osmand": "/data/data/net.osmand/databases/map_markers_db",
        "pro expense": "/data/data/com.arduia.expense/databases/accounting.db",
        "simple calendar pro": "/data/data/com.simplemobiletools.calendar.pro/databases/events.db",
        "tasks": "/data/data/org.tasks/databases/database",
        "vlc": "/data/data/org.videolan.vlc/app_db/vlc_media.db",
    }
    rows = []
    for name in _apps(manifest):
        path = databases.get(name)
        directory = name == "audio recorder"
        if directory:
            path = device_constants.AUDIORECORDER_DATA
        if path is None:
            continue
        response = adb_utils.issue_generic_request(
            ["shell", "su", "0", "test", "-d" if directory else "-s", path], env.controller)
        adb_utils.check_ok(response, f"Required app-created base state missing for {name}: {path}; provision outside qualification")
        rows.append({"app": name, "pathSha256": hashlib.sha256(path.encode()).hexdigest(), "present": True})
    return rows


def _prepare_clock(manifest_path: Path, manifest: dict[str, Any], project: Path,
                   authorization: dict[str, Any]) -> dict[str, Any]:
    """Explicit authorized official clock restoration, never an admission fallback."""
    report: dict[str, Any] = {"schemaVersion": 1, "kind": "fsq_androidworld_clock_preparation",
        "binding": _binding(manifest_path, manifest, authorization), "startedAtUnix": time.time(),
        "prepared": False, "error": None, "cleanup": {"environment": "not_created"}}
    env = None
    creating = False
    try:
        from fsq_androidworld_eval.environment import artifact_identity, close_environment, load_environment
        _authorization_checks(manifest_path, manifest, authorization, time.time())
        if "prepare-clock" not in authorization.get("approvedStages", []):
            raise PermissionError("official clock preparation was not explicitly authorized")
        if time.time() + 600 + OUTER_TIMEOUT_ALLOWANCE > authorization["resource"]["validUntilUnix"]:
            raise ValueError("resource grant does not cover the clock preparation envelope")
        report["environmentArtifacts"] = artifact_identity(project)
        before = _device_probe(manifest)
        report["before"] = before
        _check_installed_pins(before["apps"], report["environmentArtifacts"])
        creating = True
        target = manifest["target"]
        env = load_environment(artifact_root=project, console_port=target["consolePort"],
                               adb_path=target["adbPath"], grpc_port=target["grpcPort"], freeze_datetime=True)
        report["after"] = _device_probe(manifest)
        if any(report["after"][key] != before[key] for key in ("device", "apps")):
            raise RuntimeError("global device/app identity drift during official clock preparation")
        if report["after"]["clock"] != CLOCK_BASELINE:
            raise RuntimeError(f"official clock preparation did not establish UTC baseline: {report['after']['clock']!r}")
        report["prepared"] = True
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)[:4096]}
    finally:
        if env is not None:
            try:
                close_environment(env)
                report["cleanup"]["environment"] = "closed"
            except Exception as error:
                report["cleanup"]["environment"] = "unknown"
                report["prepared"] = False
                report["error"] = {"type": type(error).__name__, "message": "official clock preparation cleanup failed"}
        elif creating:
            report["cleanup"]["environment"] = "unknown"
        report["completedAtUnix"] = time.time()
    return _sealed(report)


def _qualification(manifest_path: Path, manifest: dict[str, Any], project: Path,
                   authorization: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {"schemaVersion": 1, "kind": READINESS_KIND,
        "binding": _binding(manifest_path, manifest, authorization), "startedAtUnix": time.time(),
        "qualified": False, "error": None, "checks": {}, "apps": [], "snapshotRestores": [],
        "cleanup": {"environment": "not_created"}}
    env = None
    creating = False
    try:
        from fsq_androidworld_eval.environment import artifact_identity, close_environment, load_environment, strict_snapshot_restores
        from android_world.env import adb_utils
        from android_world.utils import app_snapshot
        # Authorization validation is owned by fsq_runner. Mutations below are
        # existing official snapshot restores, restricted to its disposable grant.
        _require_disposable(authorization)
        _authorization_checks(manifest_path, manifest, authorization, time.time())
        if time.time() + 600 + OUTER_TIMEOUT_ALLOWANCE > authorization["resource"]["validUntilUnix"]:
            raise ValueError("exclusive resource grant does not cover the qualification envelope")
        report["environmentArtifacts"] = artifact_identity(project)
        report["checks"]["assets"] = True
        report.update(_device_probe(manifest))
        if report["clock"] != CLOCK_BASELINE:
            raise RuntimeError(f"official UTC clock baseline absent: apiLevel={report['device'].get('apiLevel')!r}, clock={report['clock']!r}; explicit prepare-clock required, no automatic repair")
        _check_installed_pins(report["apps"], report["environmentArtifacts"])
        report["sharedAssets"] = _shared_assets_present(manifest, report["environmentArtifacts"])
        report["checks"].update({"apps": True, "utc": True})
        target = manifest["target"]
        creating = True
        env = load_environment(artifact_root=project, console_port=target["consolePort"],
                               adb_path=target["adbPath"], grpc_port=target["grpcPort"], freeze_datetime=False)
        marker = b"FSQ_NATIVE_ADB_CAPTURE"
        captured = adb_utils.issue_generic_request(["shell", "printf", marker.decode()], env.controller)
        adb_utils.check_ok(captured, "Official controller ADB capture failed")
        if captured.generic.output != marker:
            raise RuntimeError("official controller ADB output is not isolated")
        report["checks"]["adbIsolation"] = True
        # Exercise the actual gRPC-backed official core observation, not an
        # Appium/AMKernel receipt. This does not start a business/model session.
        state = env.get_state(wait_to_stabilize=False)
        if state is None or getattr(state, "pixels", None) is None:
            raise RuntimeError("official gRPC core environment produced no pixels")
        report["checks"]["coreEnvironment"] = True
        with strict_snapshot_restores():
            for app in _apps(manifest):
                app_snapshot.restore_snapshot(app, env.controller)
                report["snapshotRestores"].append({"app": app, "status": "restored"})
        report["checks"]["snapshots"] = True
        report["baseData"] = _base_data(env, manifest)
        report["checks"]["baseData"] = True
        attest_readiness(manifest, report)
        report["qualified"] = True
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)[:4096]}
    finally:
        if env is not None:
            try:
                close_environment(env)
                report["cleanup"]["environment"] = "closed"
            except Exception as error:
                report["cleanup"]["environment"] = "unknown"
                report["qualified"] = False
                report["error"] = {"type": type(error).__name__, "message": "official environment cleanup failed"}
        elif creating:
            report["cleanup"]["environment"] = "unknown"
        report["completedAtUnix"] = time.time()
    return _sealed(report)


def _require_disposable(authorization: dict[str, Any]) -> None:
    resource = authorization.get("resource", {})
    if (resource.get("exclusive") is not True or resource.get("disposable") is not True
            or resource.get("mutationsAllowed") is not True):
        raise ValueError("official staging requires an exclusive disposable resource with mutationsAllowed")


def _rehearsal_valid(record: dict[str, Any], spec: dict[str, Any], manifest_sha: str) -> bool:
    return (record.get("kind") == "fsq_androidworld_rehearsal_task"
            and record.get("manifestSha256") == manifest_sha and record.get("task") == _task_identity(spec)
            and record.get("agentInvoked") is False and record.get("officialReward") is None
            and record.get("complete") is True and record.get("error") is None
            and not record.get("cleanupErrors")
            and record.get("stages") == ["environment", "initialize_task", "is_successful", "tear_down", "close"]
            and _reward(record.get("evaluatorProbe"))
            and record.get("cleanup") == {"taskTearDown": "completed", "environment": "closed"})


def _rehearsal_task(manifest_path: Path, manifest: dict[str, Any], spec: dict[str, Any], project: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"schemaVersion": 1, "kind": "fsq_androidworld_rehearsal_task",
        "manifestSha256": _hash(manifest_path), "task": _task_identity(spec), "agentInvoked": False,
        "officialReward": None, "startedAtUnix": time.time(), "complete": False, "stages": [], "error": None,
        "cleanup": {"taskTearDown": "not_started", "environment": "not_created"}, "cleanupErrors": []}
    env = task = None
    initializing = creating = False
    try:
        from fsq_androidworld_eval.environment import close_environment, load_environment, restore_shared_assets, strict_snapshot_restores
        from fsq_androidworld_eval.fsq_manifest import task_from_spec
        target = manifest["target"]
        task = task_from_spec(spec)
        creating = True
        env = load_environment(artifact_root=project, console_port=target["consolePort"],
                               adb_path=target["adbPath"], grpc_port=target["grpcPort"], freeze_datetime=True)
        record["stages"].append("environment")
        env.reset(go_home=True)
        record["sharedAssets"] = restore_shared_assets(env, project, task.app_names)
        initializing = True
        with strict_snapshot_restores():
            task.initialize_task(env)
        record["stages"].append("initialize_task")
        value = task.is_successful(env)
        if not _reward(value):
            raise RuntimeError("official evaluator probe returned invalid reward")
        record["evaluatorProbe"] = value
        record["stages"].append("is_successful")
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)[:4096]}
    finally:
        if initializing and task is not None and env is not None:
            try:
                with strict_snapshot_restores():
                    task.tear_down(env)
                record["cleanup"]["taskTearDown"] = "completed"
                record["stages"].append("tear_down")
            except Exception as error:
                record["cleanup"]["taskTearDown"] = "unknown"
                record["cleanupErrors"].append({"phase": "tear_down", "type": type(error).__name__,
                                                "message": str(error)[:4096]})
        if env is not None:
            try:
                close_environment(env)
                record["cleanup"]["environment"] = "closed"
                record["stages"].append("close")
            except Exception as error:
                record["cleanup"]["environment"] = "unknown"
                record["cleanupErrors"].append({"phase": "close", "type": type(error).__name__,
                                                "message": str(error)[:4096]})
        elif creating:
            record["cleanup"]["environment"] = "unknown"
        record["complete"] = record["error"] is None and not record["cleanupErrors"]
        record["completedAtUnix"] = time.time()
    return record


def _checkpoint(output: Path, event: dict[str, Any]) -> None:
    line = _bytes(event) + b"\n"
    with (output / "checkpoint.jsonl").open("ab") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())
    print(line.decode().rstrip(), flush=True)


def _descendants(table: str, parent: int) -> list[int]:
    children: dict[int, list[int]] = collections.defaultdict(list)
    for line in table.splitlines():
        fields = line.split()
        if len(fields) == 2 and all(field.isdigit() for field in fields):
            pid, ppid = map(int, fields)
            children[ppid].append(pid)
    ordered, seen = [], {parent}
    frontier = [parent]
    while frontier:
        following = []
        for owner in frontier:
            for child in children[owner]:
                if child not in seen:
                    ordered.append(child)
                    seen.add(child)
                    following.append(child)
        frontier = following
    return list(reversed(ordered))


def _stop_process(process: subprocess.Popen) -> dict[str, Any]:
    # Native FSQ uses its own process group. Killing only the outer group can
    # leave that worker running against the device; include its owned tree.
    evidence: dict[str, Any] = {"descendantDiscovery": "unknown", "signalErrors": []}
    descendants = []
    try:
        table = subprocess.run(["/bin/ps", "-axo", "pid=,ppid="], capture_output=True,
                               text=True, timeout=5, check=True).stdout
        descendants = _descendants(table, process.pid)
        evidence["descendantDiscovery"] = "observed"
    except (OSError, subprocess.SubprocessError) as error:
        evidence["signalErrors"].append(type(error).__name__)
    for pid in [*descendants, process.pid]:
        for send in (os.killpg, os.kill):
            try:
                send(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError as error:
                evidence["signalErrors"].append(type(error).__name__)
    try:
        process.wait(timeout=10)
        evidence["outerExitObserved"] = True
    except (subprocess.TimeoutExpired, OSError) as error:
        evidence["outerExitObserved"] = False
        evidence["waitErrorType"] = type(error).__name__
    evidence["descendantCount"] = len(descendants)
    # No device restoration or descendant exit is inferred from sent signals.
    evidence["deviceCleanup"] = "unknown"
    return evidence


def _spawn(command: list[str], output: Path, timeout: int) -> dict[str, Any]:
    """One outer process, business budget + 610 seconds; no retry on timeout."""
    process = None
    forced = False
    termination = None
    try:
        with (output / "process.log").open("xb") as log:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                forced = True
                termination = _stop_process(process)
            except BaseException:
                forced = True
                termination = _stop_process(process)
                raise
    except OSError as error:
        return {"exitCode": process.returncode if process is not None else None,
                "forced": forced, "spawnCount": int(process is not None), "timeoutSeconds": timeout,
                "termination": termination, "errorType": type(error).__name__}
    return {"exitCode": process.returncode, "forced": forced, "spawnCount": 1,
            "timeoutSeconds": timeout, "termination": termination}


def _summary(stage: str, attempts: list[dict[str, Any]], records: list[dict[str, Any]], expected: int) -> dict[str, Any]:
    scores = [record["officialReward"] for record in records if _reward(record.get("officialReward"))]
    return {"attempted": len(attempts), "expected": expected, "coverage": len(attempts) / expected,
            "classifications": dict(collections.Counter(record.get("classification", "rehearsal") for record in records)),
            "reward": {"count": len(scores), "sum": sum(scores), "mean": sum(scores) / len(scores) if scores else None,
                       "denominator": "valid_official_rewards_only", "diagnosticOnly": True},
            "policyProven": False, "officialLeaderboardClaim": False,
            "purpose": "non_scoring_official_lifecycles" if stage == "rehearse" else "native_operational_protocol" if stage == "calibrate" else "single_attempt_frozen_suite"}


def run_stage(args: argparse.Namespace) -> int:
    stage = args.stage
    project, manifest_path = Path(args.project).absolute(), Path(args.manifest).absolute()
    authorization_path, output = Path(args.authorization).absolute(), Path(args.output).absolute()
    manifest = _load_candidate(manifest_path, project)
    api = _runner_api()
    authorization = api.load_authorization(manifest_path, manifest, stage, authorization_path)
    _require_disposable(authorization)
    readiness_path = Path(args.readiness).absolute() if args.readiness else None
    if stage not in {"prepare-clock", "qualify"}:
        if readiness_path is None:
            raise ValueError("FSQ-only readiness is required")
        validate_readiness(readiness_path, manifest_path, manifest, authorization)
    if stage in {"calibrate", "run"}:
        if not args.rehearsal:
            raise ValueError("fresh all-116 official rehearsal report is required")
        validate_stage_report(Path(args.rehearsal).absolute(), "rehearse", manifest_path, manifest,
                              authorization, readiness_path=readiness_path)
    if stage == "run":
        if not args.calibration:
            raise ValueError("fresh original-12 native calibration report is required")
        validate_stage_report(Path(args.calibration).absolute(), "calibrate", manifest_path, manifest,
                              authorization, readiness_path=readiness_path)
    prerequisites = {name: {"path": str(Path(value).absolute()), "sha256": _hash(Path(value).absolute())}
                     for name, value in (("readiness", args.readiness), ("rehearsal", args.rehearsal),
                                         ("calibration", args.calibration)) if value}
    if stage in {"prepare-clock", "qualify"} and time.time() + 600 + OUTER_TIMEOUT_ALLOWANCE > authorization["resource"]["validUntilUnix"]:
        raise ValueError("exclusive resource grant does not cover the preflight envelope")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    common = [sys.executable, "-B", "-m", "fsq_androidworld_eval.fsq_campaign", "_episode",
              "--stage", stage, "--project", str(project), "--manifest", str(manifest_path),
              "--authorization", str(authorization_path), "--result-root", str(output)]
    if readiness_path:
        common += ["--readiness", str(readiness_path)]
    for flag, value in (("--rehearsal", args.rehearsal), ("--calibration", args.calibration)):
        if value:
            common += [flag, str(Path(value).absolute())]
    started = time.time()
    _checkpoint(output, {"event": "stage_started", "stage": stage, "manifestSha256": _hash(manifest_path), "atUnix": started})
    if stage in {"prepare-clock", "qualify"}:
        success = "prepared" if stage == "prepare-clock" else "qualified"
        filename = "clock-preparation.json" if stage == "prepare-clock" else "readiness.json"
        kind = "fsq_androidworld_clock_preparation" if stage == "prepare-clock" else READINESS_KIND
        process = _spawn(common + ["--output", str(output / "qualification")], output, 600 + OUTER_TIMEOUT_ALLOWANCE)
        path = output / "qualification" / filename
        if not path.is_file():
            report = _sealed({"schemaVersion": 1, "kind": kind,
                "binding": _binding(manifest_path, manifest, authorization), "startedAtUnix": started,
                "completedAtUnix": time.time(), success: False, "error": {"type": "PreflightProcessFailure", "message": "No completed preflight report; prerequisites/cleanup unproven"},
                "checks": {}, "apps": [], "snapshotRestores": [], "cleanup": {"environment": "unknown"}, "outerProcess": process})
        else:
            report = _load(path)
            if process["forced"] or process["exitCode"] != 0:
                report = _sealed({**{key: value for key, value in report.items() if key != "identitySha256"}, success: False, "outerProcess": process})
        _save(output / filename, report)
        _checkpoint(output, {"event": "stage_completed", success: report[success], "reportSha256": _hash(output / filename)})
        return 0 if report[success] else 2
    specs = _selected(manifest, stage)
    episodes = output / "episodes"
    episodes.mkdir(mode=0o700)
    attempts, records = [], []
    halt = None
    stop_path = getattr(args, "stop_file", None)
    stop_file = Path(stop_path).absolute() if stop_path else None
    for spec in specs:
        if stop_file is not None and stop_file.exists():
            halt = "stop_requested"
            _checkpoint(output, {"event": "stage_halted", "reason": halt, "requestPath": str(stop_file)})
            break
        # Static drift checks do not touch the target; no retry/resume is possible.
        try:
            _load_candidate(manifest_path, project)
            current_auth = api.load_authorization(manifest_path, manifest, stage, authorization_path)
            if current_auth != authorization:
                raise ValueError("authorization identity changed")
            if time.time() + int(spec["timeBudget"]["businessSeconds"]) + OUTER_TIMEOUT_ALLOWANCE > authorization["resource"]["validUntilUnix"]:
                raise ValueError("exclusive resource grant does not cover the complete episode envelope")
        except Exception as error:
            halt = "global_identity_drift"
            _checkpoint(output, {"event": "stage_halted", "reason": halt, "errorType": type(error).__name__})
            break
        attempt_id = str(uuid.uuid4())
        directory = episodes / f"{spec['index']:03d}-{spec['name']}"
        launch = output / f"process-{spec['index']:03d}"
        launch.mkdir(mode=0o700)
        _checkpoint(output, {"event": "attempt_started", "attemptId": attempt_id, "task": _task_identity(spec)})
        process = _spawn(common + ["--task-index", str(spec["index"]), "--output", str(directory)],
                         launch, int(spec["timeBudget"]["businessSeconds"]) + OUTER_TIMEOUT_ALLOWANCE)
        result_path = directory / "result.json"
        if result_path.is_file():
            record = _load(result_path)
        else:
            directory.mkdir(exist_ok=True, mode=0o700)
            record = {"task": _task_identity(spec), "manifestSha256": _hash(manifest_path), "attemptStarted": True,
                      "complete": False, "classification": "invalid_outer_process", "officialReward": None,
                      "cleanup": {"taskTearDown": "unknown", "environment": "unknown"}, "outerProcess": process}
            _save(result_path, record)
        # Keep terminal worker/result bytes intact even if the outer process dies.
        errors = [] if stage == "rehearse" and _rehearsal_valid(record, spec, _hash(manifest_path)) else (
            ["official_rehearsal_lifecycle"] if stage == "rehearse" else operational_errors(
                record, spec, _hash(manifest_path), episode_dir=directory, stage=stage, manifest=manifest,
                readiness_sha=_hash(readiness_path), authorization_sha=_digest(authorization)))
        if process["forced"]:
            errors.append("forced_outer_process")
        elif process.get("errorType"):
            errors.append("outer_process_error")
        elif process.get("exitCode") != 0:
            errors.append("outer_process_exit")
        row = {"attemptId": attempt_id, "task": _task_identity(spec), "directory": str(directory.relative_to(output)),
               "outerProcess": process, "operationalErrors": errors, "artifacts": _artifact_rows(directory)}
        attempts.append(row)
        records.append(record)
        _checkpoint(output, {"event": "attempt_completed", **row, "classification": record.get("classification"), "officialReward": record.get("officialReward")})
        halt = halt_reason(record, errors=errors, outer_process=process)
        if halt:
            _checkpoint(output, {"event": "stage_halted", "reason": halt, "operationalErrors": errors})
            break
    report = _sealed({"schemaVersion": 1, "kind": REPORT_KINDS[stage],
        "binding": _binding(manifest_path, manifest, authorization), "readinessSha256": _hash(readiness_path),
        "prerequisites": prerequisites,
        "startedAtUnix": started, "completedAtUnix": time.time(), "taskCount": len(specs),
        "taskSetSha256": _digest([_task_identity(spec) for spec in specs]), "attempts": attempts,
        "qualified": len(attempts) == len(specs) and not halt and all(not row["operationalErrors"] for row in attempts),
        "haltReason": halt, "summary": _summary(stage, attempts, records, len(specs))})
    _save(output / "report.json", report)
    _checkpoint(output, {"event": "stage_completed", "qualified": report["qualified"], "summary": report["summary"], "reportSha256": _hash(output / "report.json")})
    return 0 if report["qualified"] else 2


def _episode(args: argparse.Namespace) -> int:
    project, manifest_path = Path(args.project).absolute(), Path(args.manifest).absolute()
    manifest = _load_candidate(manifest_path, project)
    sys.path.insert(0, manifest["paths"]["evaluatorSite"])
    api = _runner_api()
    authorization_path = Path(args.authorization).absolute()
    authorization = api.load_authorization(manifest_path, manifest, args.stage, authorization_path)
    _require_disposable(authorization)
    output = Path(args.output).absolute()
    if args.stage in {"prepare-clock", "qualify"}:
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
        if args.stage == "prepare-clock":
            report = _prepare_clock(manifest_path, manifest, project, authorization)
            _save(output / "clock-preparation.json", report)
            return 0 if report["prepared"] else 2
        report = _qualification(manifest_path, manifest, project, authorization)
        _save(output / "readiness.json", report)
        return 0 if report["qualified"] else 2
    readiness_path = Path(args.readiness).absolute()
    readiness = validate_readiness(readiness_path, manifest_path, manifest, authorization)
    if args.stage in {"calibrate", "run"}:
        if not args.rehearsal:
            raise ValueError("fresh all-116 official rehearsal report is required")
        validate_stage_report(Path(args.rehearsal).absolute(), "rehearse", manifest_path, manifest,
                              authorization, readiness_path=readiness_path)
    if args.stage == "run":
        if not args.calibration:
            raise ValueError("fresh original-12 native calibration report is required")
        validate_stage_report(Path(args.calibration).absolute(), "calibrate", manifest_path, manifest,
                              authorization, readiness_path=readiness_path)
    attest_readiness(manifest, readiness)
    spec = next(row for row in manifest["tasks"] if row["index"] == args.task_index)
    if args.stage == "rehearse":
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
        record = _rehearsal_task(manifest_path, manifest, spec, project)
        _save(output / "result.json", record)
        return 0 if _rehearsal_valid(record, spec, _hash(manifest_path)) else 2
    record = api.run_episode(manifest_path, project, args.task_index, output,
                             authorization_path, readiness_path, stage=args.stage,
                             rehearsal_path=Path(args.rehearsal).absolute() if args.rehearsal else None,
                             calibration_path=Path(args.calibration).absolute() if args.calibration else None,
                             oracle_result_roots=[Path(root) for root in args.result_root])
    return 0 if record.get("complete") and halt_reason(record) is None else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare-clock", "qualify", "rehearse", "calibrate", "run", "_episode"):
        child = sub.add_parser(name, help=argparse.SUPPRESS if name == "_episode" else None)
        child.add_argument("--manifest", required=True)
        child.add_argument("--project", default=str(Path.cwd()))
        child.add_argument("--authorization", required=True)
        child.add_argument("--output", required=True)
        child.add_argument("--readiness")
        child.add_argument("--rehearsal")
        child.add_argument("--calibration")
        child.add_argument("--result-root", action="append", default=[])
        if name == "_episode":
            child.add_argument("--stage", choices=("prepare-clock", "qualify", "rehearse", "calibrate", "run", "smoke"), required=True)
            child.add_argument("--task-index", type=int)
        else:
            child.set_defaults(stage=name)
            if name in {"rehearse", "calibrate", "run"}:
                child.add_argument("--stop-file", help="stop before the next episode when this path exists; never interrupt owned cleanup")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return _episode(args) if args.command == "_episode" else run_stage(args)


if __name__ == "__main__":
    raise SystemExit(main())
