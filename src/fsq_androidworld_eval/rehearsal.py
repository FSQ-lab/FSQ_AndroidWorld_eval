"""Exercise the complete frozen task lifecycle before spending Agent calls.

This is not a benchmark run: no Agent is invoked and officialReward is always
null. Each task gets a fresh official environment and its frozen parameters,
real initialization, initial-state evaluator probe, teardown and controller close.
Information-retrieval tasks additionally exercise the real answer checker with
its official expected answer; this oracle never enters an Agent workspace.
Workers run in a macOS loopback-only network sandbox, retaining ADB/gRPC/Appium
connectivity but forbidding remote acquisition. A failed task or unproven cleanup
halts the rehearsal. Evidence is immutable, hash-bound to runtime, parameters,
artifacts and readiness; formal runs require all 116 records, not a green flag.
This covers initialized-state paths, not all possible post-Agent application
states, model availability, host crashes or future device/hardware failures.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import time
import traceback
from typing import Any

from android_world import suite_utils
from android_world.task_evals.information_retrieval import (
    datetime_utils, information_retrieval, proto_utils,
)

from fsq_androidworld_eval.environment import (
    artifact_identity, close_environment, load_environment, restore_shared_assets, strict_snapshot_restores,
)
from fsq_androidworld_eval.host_prerequisites import probe_host_media
from fsq_androidworld_eval.preparation import attest_device
from fsq_androidworld_eval.runner import _appium_session_hashes, _json_safe, _sha256, _task

NETWORK_SANDBOX = (
    '(version 1)(allow default)(deny network-outbound)'
    '(allow network-outbound (remote ip "localhost:*"))'
)
REHEARSAL_POLICY = {
    "version": 1,
    "requiredTaskCount": 116,
    "agentInvoked": False,
    "officialReward": None,
    "environmentPerTask": "fresh_official_environment",
    "evaluator": "initial_state_and_information_retrieval_reference_answer",
    "network": "loopback_only_os_sandbox",
    "networkSandboxSha256": hashlib.sha256(NETWORK_SANDBOX.encode()).hexdigest(),
    "episodeTimeoutSeconds": 600,
    "failurePolicy": "halt_without_retry_or_resume",
    "requiredStages": [
        "infrastructure", "environment_creation", "task_initialization",
        "evaluator_probe", "task_teardown", "environment_close", "session_verification",
    ],
}


def _save(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(_json_safe(value), indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _reference_answer(task: information_retrieval.InformationRetrieval) -> str:
    def format_value(value: Any) -> str:
        if isinstance(value, datetime.datetime):
            return value.strftime(datetime_utils.DATE_FORMAT + " %H:%M")
        if isinstance(value, datetime.date):
            return value.strftime(datetime_utils.DATE_FORMAT)
        if isinstance(value, datetime.time):
            return value.strftime("%H:%M")
        return str(value)

    return ", ".join(format_value(value) for value in proto_utils.get_expected_answer(task.task))


def _probe_evaluator(task: Any, env: Any) -> dict[str, Any]:
    value = task.is_successful(env)
    if type(value) not in {int, float} or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"official evaluator returned an invalid reward: {value!r}")
    result = {"implementation": "android_world.task_eval.is_successful", "initialStateReturn": value}
    if isinstance(task, information_retrieval.InformationRetrieval):
        env.interaction_cache = _reference_answer(task)
        try:
            reference_value = task.is_successful(env)
            if type(reference_value) not in {int, float} or not math.isfinite(reference_value) or reference_value != 1.0:
                raise ValueError("official information-retrieval evaluator rejected its reference answer")
            result["referenceAnswerReturn"] = reference_value
        finally:
            env.interaction_cache = ""
    return result


def run_task(manifest: dict[str, Any], spec: dict[str, Any], project: Path, adb_path: str) -> dict[str, Any]:
    started = time.time()
    record: dict[str, Any] = {
        "schemaVersion": 1, "kind": "harness_rehearsal_task",
        "manifestSha256": _sha256(manifest),
        "task": {"name": spec["name"], "paramsSha256": spec["paramsSha256"]},
        "agentInvoked": False, "officialReward": None, "qualified": False,
        "startedAtUnix": started, "stages": [], "error": None,
        "cleanup": {"taskTearDown": "not_applicable", "environment": "not_created", "sessions": "unknown"},
    }
    env = None
    task = None
    initialization_started = False
    environment_creation_started = False
    target = manifest["target"]
    stage = None

    def enter(name: str) -> None:
        nonlocal stage
        if stage is not None and stage["status"] == "running":
            stage["status"] = "completed"
            stage["durationSeconds"] = round(time.time() - stage["startedAtUnix"], 3)
        stage = {"name": name, "status": "running", "startedAtUnix": time.time()}
        record["stages"].append(stage)

    try:
        enter("infrastructure")
        if artifact_identity(project) != manifest["protocol"]["environmentArtifacts"]:
            raise ValueError("environment artifacts do not match frozen manifest")
        if _appium_session_hashes(target["appiumUrl"], adb_path, target["serial"]):
            raise RuntimeError("rehearsal requires zero pre-existing Appium sessions")
        task = _task(
            spec["name"],
            json.dumps(spec["params"]) if spec["paramsTransport"] == "json" else None,
            spec["instanceSeed"] if spec["paramsTransport"] == "seed" else None,
        )
        if _sha256(task.params) != spec["paramsSha256"] or suite_utils._allocate_step_budget(task.complexity) != spec["maxSteps"]:
            raise ValueError("reconstructed task differs from frozen parameters or budget")
        enter("environment_creation")
        environment_creation_started = True
        env = load_environment(
            artifact_root=project, console_port=target["consolePort"],
            adb_path=adb_path, grpc_port=target["grpcPort"], freeze_datetime=True,
        )
        enter("task_initialization")
        env.reset(go_home=True)
        record["sharedAssets"] = restore_shared_assets(env, project, task.app_names)
        initialization_started = True
        with strict_snapshot_restores():
            task.initialize_task(env)
        enter("evaluator_probe")
        record["evaluatorProbe"] = _probe_evaluator(task, env)
    except Exception as exc:
        if stage is not None:
            stage["status"] = "failed"
        record["error"] = {
            "stage": stage["name"] if stage else None, "type": type(exc).__name__,
            "message": str(exc)[:4096], "traceback": "".join(traceback.format_exception(exc))[-8192:],
        }
    finally:
        enter("task_teardown")
        if initialization_started and task is not None and env is not None:
            try:
                with strict_snapshot_restores():
                    task.tear_down(env)
                record["cleanup"]["taskTearDown"] = "completed"
            except Exception as exc:
                stage["status"] = "failed"
                record["cleanup"]["taskTearDown"] = f"failed:{type(exc).__name__}"
                record["cleanup"]["taskTearDownError"] = str(exc)[:2048]
        enter("environment_close")
        if env is not None:
            try:
                close_environment(env)
                record["cleanup"]["environment"] = "closed"
            except Exception as exc:
                stage["status"] = "failed"
                record["cleanup"]["environment"] = f"failed:{type(exc).__name__}"
                record["cleanup"]["environmentError"] = str(exc)[:2048]
        elif environment_creation_started:
            record["cleanup"]["environment"] = "unknown"
        enter("session_verification")
        try:
            sessions = _appium_session_hashes(target["appiumUrl"], adb_path, target["serial"])
            record["cleanup"]["sessions"] = "absent" if sessions == [] else "leaked"
            if sessions:
                stage["status"] = "failed"
        except Exception as exc:
            stage["status"] = "failed"
            record["cleanup"]["sessionsError"] = str(exc)[:2048]
        if stage["status"] == "running":
            stage["status"] = "completed"
        record["completedAtUnix"] = time.time()
        record["durationSeconds"] = round(record["completedAtUnix"] - started, 3)
        record["qualified"] = _task_qualified(record, spec, _sha256(manifest))
    return record


def _task_qualified(record: dict[str, Any], spec: dict[str, Any], manifest_sha: str) -> bool:
    stages = record.get("stages", [])
    probe = record.get("evaluatorProbe", {})
    value = probe.get("initialStateReturn")
    reference = probe.get("referenceAnswerReturn")
    return (
        record.get("schemaVersion") == 1
        and record.get("kind") == "harness_rehearsal_task"
        and record.get("manifestSha256") == manifest_sha
        and record.get("task") == {"name": spec["name"], "paramsSha256": spec["paramsSha256"]}
        and record.get("agentInvoked") is False
        and record.get("officialReward") is None
        and record.get("error") is None
        and [row.get("name") for row in stages] == REHEARSAL_POLICY["requiredStages"]
        and all(row.get("status") == "completed" for row in stages)
        and probe.get("implementation") == "android_world.task_eval.is_successful"
        and type(value) in {int, float} and math.isfinite(value) and 0 <= value <= 1
        and (spec["family"] != "information_retrieval" or (type(reference) in {int, float} and math.isfinite(reference) and reference == 1.0))
        and record.get("cleanup") == {"taskTearDown": "completed", "environment": "closed", "sessions": "absent"}
    )


def validate_report(path: Path, manifest: dict[str, Any], project: Path) -> str:
    from fsq_androidworld_eval.campaign import _load_manifest

    report = json.loads(path.read_text())
    payload = {key: value for key, value in report.items() if key != "identitySha256"}
    if report.get("identitySha256") != _sha256(payload):
        raise ValueError("rehearsal report identity is invalid")
    if (
        report.get("schemaVersion") != 1 or report.get("kind") != "harness_rehearsal"
        or report.get("agentInvoked") is not False or report.get("officialReward") is not None
        or report.get("error") is not None
        or report.get("qualified") is not True or report.get("policy") != REHEARSAL_POLICY
    ):
        raise ValueError("all-task rehearsal is not qualified under the current non-scoring policy")
    saved = _load_manifest(path.parent / "manifest.json", project)
    if saved["kind"] != "rehearsal" or saved["protocol"] != manifest["protocol"] or saved["target"] != manifest["target"]:
        raise ValueError("rehearsal runtime, dependencies or target differ from campaign")
    if report.get("manifestSha256") != _sha256(saved):
        raise ValueError("rehearsal manifest identity is invalid")
    if report.get("hostMedia") != {
        "encoder": manifest["protocol"]["runtimeIdentity"]["mediaEncoder"],
        "mp3": "encoded_and_decoded", "mp4": "encoded_and_decoded",
    }:
        raise ValueError("rehearsal lacks matching real media-generation probes")
    by_name = {spec["name"]: spec for spec in saved["tasks"]}
    if any(by_name.get(spec["name"], {}).get("paramsSha256") != spec["paramsSha256"] for spec in manifest["tasks"]):
        raise ValueError("rehearsal did not cover the campaign parameters")
    rows = report.get("tasks", [])
    if len(rows) != len(saved["tasks"]) or len(rows) != REHEARSAL_POLICY["requiredTaskCount"]:
        raise ValueError("rehearsal lacks all 116 task records")
    for spec, row in zip(saved["tasks"], rows, strict=True):
        expected = f"tasks/{spec['index']:03d}-{spec['name']}/result.json"
        if row.get("result") != expected or row.get("task") != spec["name"] or row.get("qualified") is not True:
            raise ValueError("rehearsal task evidence order, status or path is invalid")
        result_path = path.parent / expected
        if hashlib.sha256(result_path.read_bytes()).hexdigest() != row.get("sha256"):
            raise ValueError(f"rehearsal task evidence changed: {spec['name']}")
        record = json.loads(result_path.read_text())
        if record.get("qualified") is not True or not _task_qualified(record, spec, _sha256(saved)):
            raise ValueError(f"rehearsal task lifecycle is not qualified: {spec['name']}")
    if report.get("finalAttestation", {}).get("qualified") is not True:
        raise ValueError("rehearsal final target attestation failed")
    return report["identitySha256"]


def run_rehearsal(args: argparse.Namespace) -> int:
    from fsq_androidworld_eval.campaign import _load_manifest, _readiness_identity, _run_process

    project = Path(args.project).resolve()
    manifest_path = Path(args.manifest).resolve()
    manifest = _load_manifest(manifest_path, project)
    if manifest["kind"] != "rehearsal":
        raise ValueError("rehearse requires a separate --kind rehearsal manifest, never a formal campaign")
    readiness_path = Path(args.readiness_report).resolve()
    readiness_identity = _readiness_identity(readiness_path, manifest)
    readiness = json.loads(readiness_path.read_text())
    attestation = attest_device(readiness, args.adb_path)
    if not attestation["qualified"]:
        raise ValueError(f"target no longer matches rehearsal readiness: {attestation['mismatches']}")
    sandbox = shutil.which("sandbox-exec")
    if sandbox is None:
        raise RuntimeError("loopback-only rehearsal requires macOS sandbox-exec")
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(manifest_path, output / "manifest.json")
    shutil.copyfile(readiness_path, output / "device-readiness.json")
    report: dict[str, Any] = {
        "schemaVersion": 1, "kind": "harness_rehearsal", "policy": REHEARSAL_POLICY,
        "manifestSha256": _sha256(manifest), "readinessIdentitySha256": readiness_identity,
        "startedAtUnix": time.time(), "qualified": False, "agentInvoked": False,
        "officialReward": None, "tasks": [], "error": None,
    }
    report_path = output / "report.json"
    _save(report_path, report)
    try:
        report["hostMedia"] = probe_host_media()
        if report["hostMedia"]["encoder"] != manifest["protocol"]["runtimeIdentity"]["mediaEncoder"]:
            raise ValueError("media encoder differs from the frozen runtime")
        for spec in manifest["tasks"]:
            result_path = output / "tasks" / f"{spec['index']:03d}-{spec['name']}" / "result.json"
            result_path.parent.mkdir(parents=True)
            command = [
                sandbox, "-p", NETWORK_SANDBOX, sys.executable, "-m", "fsq_androidworld_eval.rehearsal",
                "--manifest", str(output / "manifest.json"), "--project", str(project),
                "--task-index", str(spec["index"]), "--output", str(result_path), "--adb-path", args.adb_path,
            ]
            code = _run_process(command, REHEARSAL_POLICY["episodeTimeoutSeconds"])
            if not result_path.exists():
                raise RuntimeError(f"rehearsal worker exited {code} without cleanup evidence: {spec['name']}; halt and requalify")
            record = json.loads(result_path.read_text())
            qualified = code == 0 and _task_qualified(record, spec, _sha256(manifest))
            report["tasks"].append({
                "task": spec["name"], "result": str(result_path.relative_to(output)),
                "sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(), "qualified": qualified,
            })
            _save(report_path, report)
            print(f"Rehearsal {spec['index'] + 1}/{len(manifest['tasks'])}: {spec['name']} {'OK' if qualified else 'FAILED'}", flush=True)
            if not qualified:
                raise RuntimeError(f"rehearsal lifecycle failed: {spec['name']}; inspect task result; no next task started")
        report["finalAttestation"] = attest_device(readiness, args.adb_path)
        if not report["finalAttestation"]["qualified"]:
            raise RuntimeError("target prerequisites changed during rehearsal")
        report["qualified"] = len(report["tasks"]) == REHEARSAL_POLICY["requiredTaskCount"]
    except Exception as exc:
        report["error"] = {"type": type(exc).__name__, "message": str(exc)[:4096]}
    finally:
        report["completedAtUnix"] = time.time()
        report["durationSeconds"] = round(report["completedAtUnix"] - report["startedAtUnix"], 3)
        report["identitySha256"] = _sha256(report)
        _save(report_path, report)
    return 0 if report["qualified"] else 2


def main() -> None:
    parser = argparse.ArgumentParser(description="One isolated non-scoring rehearsal worker; use campaign rehearse for the full gate")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--task-index", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--adb-path", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    if manifest.get("kind") != "rehearsal":
        raise ValueError("worker refuses formal campaign manifests")
    spec = manifest["tasks"][args.task_index]
    record = run_task(manifest, spec, Path(args.project), args.adb_path)
    _save(Path(args.output), record)
    raise SystemExit(0 if record["qualified"] else 1)


if __name__ == "__main__":
    main()
