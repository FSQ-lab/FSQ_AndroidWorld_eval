"""One native FSQ episode; complete FSQ first, official terminal oracle second.

This path never selects AMKernel/OMP/Appium and never rewrites an FSQ model loop.
All device access requires independent review/model/resource approval AND a fresh
FSQ-specific readiness receipt. Candidate preparation/inspection is separate.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import json
from pathlib import Path
import shutil
import sys
import time
from typing import Any

from fsq_androidworld_eval.fsq_manifest import (
    MODEL, PROVIDER, load_manifest, manifest_file_sha256, task_from_spec,
)
from fsq_androidworld_eval.fsq_supervisor import artifact_reference, private_json, run_fsq_worker
from fsq_androidworld_eval.lifecycle import episode_time_budget
from fsq_androidworld_eval.fsq_evidence import EvidenceError, validate_native_evidence


def _reference(receipt: dict[str, Any]) -> None:
    if not isinstance(receipt, dict) or not {"path", "sha256"} <= set(receipt):
        raise ValueError("a real receipt path and SHA256 are required")
    path = Path(receipt["path"])
    if path.is_symlink() or not path.is_file() or manifest_file_sha256(path) != receipt["sha256"]:
        raise ValueError("authorization receipt bytes do not match")


def load_authorization(
    manifest_path: Path, manifest: dict[str, Any], stage: str, authorization_path: Path, *, cleanup: bool = False,
) -> dict[str, Any]:
    """Validate coordinator assertions and receipt bindings, never infer approval.

    This is an experiment-admission record, not a cryptographic authorization
    system. Native model receipt identifies the requested model only: FSQ's
    ModelResult does not expose a server-returned response.model identity.
    """
    authorization = json.loads(authorization_path.read_text())
    if authorization.get("schemaVersion") != 1 or authorization.get("kind") != "fsq_execution_authorization":
        raise ValueError("not an FSQ execution authorization")
    if authorization.get("manifestSha256") != manifest_file_sha256(manifest_path):
        raise ValueError("authorization is for another frozen manifest")
    if stage not in authorization.get("approvedStages", []):
        raise PermissionError(f"stage {stage!r} has not been explicitly authorized")
    review = authorization.get("independentReview", {})
    if review.get("status") != "approved":
        raise PermissionError("independent adapter review is not approved")
    _reference(review)
    model = authorization.get("nativeModelCall", {})
    if (model.get("status") != "passed_native_responses"
            or model.get("provider") != PROVIDER or model.get("requestedModel") != MODEL):
        raise PermissionError("native FSQ model-call receipt is not ready")
    _reference(model)
    observed = manifest["identities"]["nativeProviderMetadata"]
    if observed.get("provider") != PROVIDER or observed.get("model") != MODEL:
        raise PermissionError("candidate was frozen before native provider/model readiness; prepare a new candidate")
    resource = authorization.get("resource", {})
    if (resource.get("exclusive") is not True or resource.get("disposable") is not True
            or resource.get("mutationsAllowed") is not True):
        raise PermissionError("exclusive disposable target ownership is unproven")
    for key in ("serial", "consolePort", "grpcPort", "adbPath"):
        if resource.get(key) != manifest["target"][key]:
            raise PermissionError("resource approval does not bind the exact target")
    now = time.time()
    deadline = resource.get("validUntilUnix")
    if cleanup or (stage == "prepare-apps" and authorization.get("effectsGrant", {}).get("ownedEmulatorLifecycle") is True):
        cleanup_deadline = resource.get("cleanupUntilUnix")
        if (stage != "prepare-apps" or authorization.get("effectsGrant", {}).get("normalOwnedCleanup") is not True
                or type(deadline) not in (int, float) or type(cleanup_deadline) not in (int, float)
                or not math.isfinite(deadline) or not math.isfinite(cleanup_deadline)
                or not deadline <= cleanup_deadline <= deadline + 120):
            raise PermissionError("bounded owned normal cleanup was not explicitly authorized")
        if cleanup:
            deadline = cleanup_deadline
    if not (type(resource.get("notBeforeUnix")) in (int, float)
            and type(deadline) in (int, float)
            and math.isfinite(resource["notBeforeUnix"]) and math.isfinite(deadline)
            and resource["notBeforeUnix"] <= now < deadline):
        raise PermissionError("exclusive resource window is absent or expired")
    if not isinstance(resource.get("authority"), str) or not resource["authority"].strip():
        raise PermissionError("resource holder/coordinator evidence is required")
    return authorization


def validate_readiness(path: Path, manifest_path: Path, manifest: dict[str, Any],
                       authorization: dict[str, Any]) -> dict[str, Any]:
    from fsq_androidworld_eval.fsq_campaign import validate_readiness as validate_native_readiness
    return validate_native_readiness(path, manifest_path, manifest, authorization)


def activate_evaluator_site(manifest: dict[str, Any]) -> None:
    """Reject an already imported shared evaluator rather than silently mixing it."""
    site = Path(manifest["paths"]["evaluatorSite"]).resolve()
    existing = sys.modules.get("android_world")
    if existing is not None:
        origin = Path(existing.__file__).resolve()
        if site not in origin.parents:
            raise RuntimeError("AndroidWorld was already imported from another installation")
    sys.path.insert(0, str(site))


def _primary_app_id(task: Any) -> str:
    from android_world.env.setup_device import setup as device_setup
    for app_name in task.app_names:
        app = device_setup.get_app_mapping(app_name)
        if app is not None:
            package = app.package_name()
            if package:
                return package
    raise ValueError("task has no explicit native Android app target")


def _episode_workspace(root: Path, *, episode_id: str, app_id: str) -> Path:
    workspace = root / "workspace"
    config = workspace / ".fsq" / "config" / "config.android.yaml"
    private_json(config, {"version": 2, "name": episode_id, "root_path": str(workspace),
                          "platform": "android", "target": {"app_id": app_id}})
    return workspace


def _stage_worker_modules(root: Path, expected_files: list[dict[str, Any]]) -> Path:
    """Only worker/native code is staged. No oracle, manifest or task data."""
    site = root / "worker-site"
    package = site / "fsq_androidworld_eval"
    package.mkdir(parents=True, exist_ok=False, mode=0o700)
    source = Path(__file__).parent
    expected = {entry["path"]: entry["sha256"] for entry in expected_files}
    for name in ("__init__.py", "fsq_native.py", "fsq_worker.py"):
        shutil.copyfile(source / name, package / name)
        if manifest_file_sha256(package / name) != expected.get(name):
            raise ValueError("staged worker code differs from frozen source")
    return site


def _archive_outcome(outcome: dict[str, Any], owned_root: Path, destination: Path) -> dict[str, Any]:
    """Keep exact native bytes; relocate only envelope artifact references."""
    for path in owned_root.rglob("*"):
        if path.is_symlink():
            raise ValueError("native artifact symlinks are not archived as trusted evidence")
    shutil.copytree(owned_root, destination)
    def relocate(value: Any) -> Any:
        if isinstance(value, dict):
            mapped = {key: relocate(child) for key, child in value.items()}
            if isinstance(mapped.get("path"), str):
                path = Path(mapped["path"])
                if path.is_absolute() and owned_root in path.parents:
                    mapped["path"] = str(destination / path.relative_to(owned_root))
            return mapped
        if isinstance(value, list):
            return [relocate(child) for child in value]
        return value
    return relocate(outcome)



def classification(record: dict[str, Any]) -> str:
    if record.get("invalidReason"):
        return record["invalidReason"]
    reward = record.get("officialReward")
    if type(reward) not in (int, float) or not math.isfinite(reward) or not 0 <= reward <= 1:
        return "invalid_evaluator"
    return "passed" if reward >= 1.0 else "failed"


def _require_window(authorization: dict[str, Any], seconds: float) -> None:
    if authorization["resource"]["validUntilUnix"] - time.time() < seconds:
        raise PermissionError("remaining exclusive resource grant cannot cover the full episode bound")


def native_episode_id(campaign_id: str, stage: str, index: int) -> str:
    return f"{campaign_id}-{stage}-{index:03d}"


def authorization_digest(authorization: dict[str, Any]) -> str:
    data = json.dumps(authorization, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def _admit_episode(manifest_path: Path, project: Path, task_index: int,
                   authorization_path: Path, readiness_path: Path, *, stage: str,
                   rehearsal_path: Path | None, calibration_path: Path | None) -> tuple[dict, dict, dict]:
    if stage not in {"smoke", "calibrate", "run"}:
        raise ValueError("unsupported native business stage")
    manifest = load_manifest(manifest_path, project)
    authorization = load_authorization(manifest_path, manifest, stage, authorization_path)
    validate_readiness(readiness_path, manifest_path, manifest, authorization)
    if stage in {"calibrate", "run"}:
        from fsq_androidworld_eval.fsq_campaign import validate_stage_report
        if rehearsal_path is None:
            raise PermissionError("native rehearsal proof is required before this stage")
        validate_stage_report(rehearsal_path, "rehearse", manifest_path, manifest, authorization,
                              readiness_path=readiness_path)
        if stage == "run":
            if calibration_path is None:
                raise PermissionError("native calibration proof is required before the formal stage")
            validate_stage_report(calibration_path, "calibrate", manifest_path, manifest, authorization,
                                  readiness_path=readiness_path)
    if type(task_index) is not int or not 0 <= task_index < len(manifest["tasks"]):
        raise ValueError("task index outside frozen suite")
    spec = manifest["tasks"][task_index]
    if episode_time_budget(spec["maxSteps"]) != spec["timeBudget"] or spec["maxActions"] != spec["maxSteps"]:
        raise ValueError("frozen native action/time allocator mismatch")
    _require_window(authorization, spec["timeBudget"]["episodeSeconds"])
    return manifest, authorization, spec


def _process_receipt(path: Path) -> dict[str, Any]:
    """Never turn absent/unreadable post-spawn evidence into a clean worker exit."""
    try:
        if path.is_symlink():
            raise ValueError("process evidence must not be a symlink")
        value = json.loads(path.read_bytes())
        if not isinstance(value, dict):
            raise ValueError("process evidence is not an object")
        return value
    except (OSError, ValueError):
        return {"groupCleanup": "unknown", "workerExitObserved": False, "receiptState": "unavailable"}


def run_episode(
    manifest_path: Path, project: Path, task_index: int, output_dir: Path,
    authorization_path: Path, readiness_path: Path, *, stage: str = "smoke",
    rehearsal_path: Path | None = None, calibration_path: Path | None = None,
    oracle_result_roots: list[Path] | None = None,
) -> dict[str, Any]:
    """No business retry; any actual failed attempt has its own durable record."""
    manifest, authorization, spec = _admit_episode(
        manifest_path, project, task_index, authorization_path, readiness_path,
        stage=stage, rehearsal_path=rehearsal_path, calibration_path=calibration_path)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    private = output_dir / "raw-private"
    private.mkdir(mode=0o700)
    process_receipt_path = private / "worker-process.json"
    episode_id = native_episode_id(manifest["campaignId"], stage, task_index)
    result_roots = [output_dir, readiness_path.resolve().parent,
                    *[path.resolve().parent for path in (rehearsal_path, calibration_path) if path is not None],
                    *[path.resolve() for path in (oracle_result_roots or [])]]
    record: dict[str, Any] = {
        "schemaVersion": 1, "kind": "fsq_androidworld_episode", "stage": stage,
        "campaignId": manifest["campaignId"], "manifestSha256": manifest_file_sha256(manifest_path),
        "readinessSha256": manifest_file_sha256(readiness_path),
        "authorizationSha256": authorization_digest(authorization),
        "episodeId": episode_id, "target": manifest["target"],
        "task": {"index": task_index, "name": spec["name"], "paramsSha256": spec["paramsSha256"]},
        "attempt": 1, "attemptStarted": False, "complete": False,
        "officialReward": None, "evaluatorCalls": 0, "fsq": None,
        "workerSpawnAttempted": False, "workerProcess": None, "evidenceFailure": None,
        "cleanup": {"taskTearDown": "not_started", "environment": "not_created",
                    "nativeDeviceRestoration": "not_provided_by_close", "workerProcessGroup": "not_started"},
        "startedAtUnix": time.time(),
    }
    env = None
    task = None
    initialization_started = False
    current_stage = "infrastructure"
    try:
        activate_evaluator_site(manifest)
        from fsq_androidworld_eval.environment import (
            load_environment, restore_shared_assets, strict_snapshot_restores, close_environment,
        )
        from fsq_androidworld_eval.evaluator_diagnostics import EvaluatorDiagnostics, bounded_type_name
        from fsq_androidworld_eval.task_time import task_time_context
        from android_world.task_evals.information_retrieval import information_retrieval
        task = task_from_spec(spec)
        allocated = episode_time_budget(spec["maxSteps"])
        if allocated != spec["timeBudget"] or spec["maxActions"] != spec["maxSteps"]:
            raise ValueError("frozen native action/time allocator mismatch")
        target = manifest["target"]
        env = load_environment(
            artifact_root=project, console_port=target["consolePort"],
            adb_path=target["adbPath"], grpc_port=target["grpcPort"], freeze_datetime=True,
        )
        env.reset(go_home=True)
        restore_shared_assets(env, project, task.app_names)
        current_stage = "task_initialization"
        initialization_started = True
        with strict_snapshot_restores():
            task.initialize_task(env)
        # Frozen params can be reworded by official initialization; preserve both
        # outside the Agent workspace, never forward evaluator params/expected.
        private_json(private / "task-initialization.json", {
            "frozenSpec": spec, "initializedGoal": task.goal,
            "initializationReferenceTime": task_time_context(task.device_time),
        })
        env.interaction_cache = ""
        current_stage = "agent"
        owned_root = Path(manifest["paths"]["settingsPath"]).parents[3] / "episodes" / episode_id
        owned_root.mkdir(parents=True, exist_ok=False, mode=0o700)
        workspace = _episode_workspace(owned_root, episode_id=episode_id, app_id=_primary_app_id(task))
        worker_site = _stage_worker_modules(owned_root, manifest["identities"]["evaluator"]["source"]["files"])
        _require_window(authorization, allocated["episodeSeconds"])
        deadline = time.monotonic() + allocated["businessSeconds"]
        request = {
            "schemaVersion": 1, "settingsPath": str(workspace / ".fsq/config/config.android.yaml"),
            "workspace": str(workspace), "outputDir": str(owned_root / "worker"),
            "serial": target["serial"], "taskId": episode_id, "goal": task.goal,
            "appId": _primary_app_id(task), "maxActions": spec["maxActions"],
            "businessDeadlineMonotonic": deadline, "provider": PROVIDER, "model": MODEL,
        }
        record["attemptStarted"] = True
        record["workerSpawnAttempted"] = True
        record["cleanup"]["workerProcessGroup"] = "unknown"
        record["agentStartedAtUnix"] = time.time()
        outcome = run_fsq_worker(
            request, python=Path(manifest["paths"]["fsqPython"]), worker_site=worker_site,
            private_dir=owned_root / "worker",
            oracle_roots=[project.resolve(), Path(manifest["paths"]["evaluatorSite"]).resolve(), *result_roots,
                          *[Path(root) for root in manifest["identities"]["androidWorld"]["oracleSourceRoots"]]],
            process_receipt_path=process_receipt_path,
            runtime_read_roots=[Path(manifest["identities"]["fsq"][key]) for key in ("prefix", "basePrefix")]
                               + [Path(manifest["identities"]["fsq"]["package"]["path"]),
                                  Path(manifest["target"]["adbPath"]).resolve().parent],
            cleanup_seconds=allocated["cleanupWindowSeconds"],
            grace_seconds=allocated["terminationGraceSeconds"],
        )
        # Trusted parent-owned process evidence is independent of parsing/archive.
        record["workerProcess"] = _process_receipt(process_receipt_path)
        record["cleanup"]["workerProcessGroup"] = ("settled" if (
            record["workerProcess"].get("groupCleanup") == "settled"
            and record["workerProcess"].get("workerExitObserved") is True) else "unknown")
        if record["workerProcess"] != outcome.get("process"):
            record["evidenceFailure"] = "process_receipt_mismatch"
            raise EvidenceError("trusted process receipt differs from worker envelope")
        if outcome.get("resultError"):
            record["evidenceFailure"] = "native_result_parse"
        record["fsq"] = {"unarchivedNativeRoot": str(owned_root),
                         "killEvidence": {"status": "unknown", "observation": "not_yet_validated"}}
        if record["cleanup"]["workerProcessGroup"] != "settled":
            record["evidenceFailure"] = "worker_group_cleanup_unproven"
            record["evaluatorNotCalled"] = "worker_group_cleanup_unproven"
            raise EvidenceError("worker group cleanup is unproven")
        result = outcome["result"]
        proof = None
        if result is not None and result.get("fsq", {}).get("completeDynamicExecutionReturned") is True:
            proof = validate_native_evidence(outcome, episode_root=owned_root, expected_task_id=episode_id,
                                             expected_serial=target["serial"], maximum=spec["maxActions"])
            record["fsq"]["killEvidence"] = proof["killEvidence"]
        try:
            outcome = _archive_outcome(outcome, owned_root, private / "fsq-native")
        except Exception:
            record["evidenceFailure"] = "native_archive"
            raise
        private_json(private / "fsq-worker-outcome.json", outcome)
        record["fsq"].update({
            "privateOutcome": artifact_reference(private / "fsq-worker-outcome.json", output_dir),
            "nativeArtifactsRoot": str(private / "fsq-native"),
            "restoration": outcome["restoration"],
        })
        if proof is None:
            record["invalidReason"] = "invalid_agent"
            record["evaluatorNotCalled"] = "complete_native_execution_unproven"
        else:
            answer = proof["answer"]
            record["fsq"]["mainAnswer"] = {key: value for key, value in answer.items() if key != "summary"}
            record["fsq"]["nativeStatus"] = result["fsq"]["status"]
            record["fsq"]["budget"] = result["actionBudget"]
            record["fsq"]["close"] = result.get("cleanup")
            record["fsq"]["killEvidence"] = proof["killEvidence"]
            record["fsq"]["internalVerification"] = {"status": proof["internalVerification"].get("status"),
                                                        "observation": "returned_in_complete_native_task_result"}
            if isinstance(task, information_retrieval.InformationRetrieval) and answer.get("status") == "valid":
                env.interaction_cache = answer["summary"]
            current_stage = "evaluator"
            diagnostics = EvaluatorDiagnostics(output_dir, task_name=task.name,
                                                params_sha256=spec["paramsSha256"])
            started = time.monotonic()
            try:
                with diagnostics:
                    record["evaluatorCalls"] += 1
                    record["officialReward"] = task.is_successful(env)
                    diagnostics.reward = record["officialReward"]
            finally:
                record["evaluator"] = {"durationSeconds": time.monotonic() - started,
                                       "called": record["evaluatorCalls"] == 1, "afterFullFsq": True,
                                       "implementation": "android_world.task_eval.is_successful",
                                       "diagnostics": diagnostics.reference,
                                       "ordering": "after_complete_native_FSQ_return_and_internal_verification"}
            if outcome["process"]["businessDeadlineReached"]:
                record["invalidReason"] = "invalid_agent"
                record["terminationReason"] = "business_deadline"
            elif (outcome["process"]["exitCode"] != 0 or result.get("status") != "completed"
                  or outcome["process"].get("terminated") or outcome["process"].get("killed")):
                # A settled but forcibly terminated group remains a forced attempt.
                record["invalidReason"] = "invalid_agent"
                record["terminationReason"] = "worker_nonzero_exit"
    except Exception as error:
        from fsq_androidworld_eval.evaluator_diagnostics import bounded_type_name
        if isinstance(error, EvidenceError):
            record["evidenceFailure"] = record["evidenceFailure"] or "native_evidence_invalid"
        record["error"] = {"type": bounded_type_name(error)[0]}
        record["invalidReason"] = {
            "infrastructure": "invalid_infrastructure", "task_initialization": "invalid_setup",
            "agent": "invalid_agent", "evaluator": "invalid_evaluator",
        }[current_stage]
        # Details may contain native expected state or provider secrets.
        private_json(private / "failure.json", {"stage": current_stage, "type": bounded_type_name(error)[0]})
    finally:
        if record["workerSpawnAttempted"]:
            record["workerProcess"] = _process_receipt(process_receipt_path)
            record["cleanup"]["workerProcessGroup"] = ("settled" if (
                record["workerProcess"].get("groupCleanup") == "settled"
                and record["workerProcess"].get("workerExitObserved") is True) else "unknown")
            if process_receipt_path.is_file() and not process_receipt_path.is_symlink():
                record["workerProcessReference"] = artifact_reference(process_receipt_path, output_dir)
        worker_settled = not record["workerSpawnAttempted"] or record["cleanup"]["workerProcessGroup"] == "settled"
        if task is not None and env is not None and initialization_started and worker_settled:
            try:
                from fsq_androidworld_eval.environment import strict_snapshot_restores
                with strict_snapshot_restores():
                    task.tear_down(env)
                record["cleanup"]["taskTearDown"] = "completed"
            except Exception as error:
                record["cleanup"]["taskTearDown"] = "failed:" + type(error).__name__
        elif initialization_started and not worker_settled:
            record["cleanup"]["taskTearDown"] = "unknown_due_to_worker_group"
        elif not initialization_started:
            record["cleanup"]["taskTearDown"] = "not_applicable"
        if env is not None:
            try:
                from fsq_androidworld_eval.environment import close_environment
                close_environment(env)
                record["cleanup"]["environment"] = "closed"
            except Exception as error:
                record["cleanup"]["environment"] = "failed:" + type(error).__name__
        record["cleanupFailure"] = (not worker_settled or any(
            str(record["cleanup"][key]).startswith(("failed:", "unknown"))
            for key in ("taskTearDown", "environment")))
        record["complete"] = True
        record["classification"] = classification(record)
        record["completedAtUnix"] = time.time()
        record["artifacts"] = [artifact_reference(path, output_dir)
                               for path in sorted(private.rglob("*")) if path.is_file()]
        private_json(output_dir / "result.json", record)
    return record


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="One complete native FSQ attempt; requires explicit live authorization")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--task-index", required=True, type=int)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--readiness", required=True, type=Path)
    parser.add_argument("--stage", choices=("smoke", "calibrate", "run"), default="smoke")
    parser.add_argument("--rehearsal-report", type=Path)
    parser.add_argument("--calibration-report", type=Path)
    args = parser.parse_args(argv)
    from fsq_androidworld_eval.fsq_campaign import _spawn, halt_reason
    manifest, authorization, spec = _admit_episode(
        args.manifest, args.project, args.task_index, args.authorization, args.readiness,
        stage=args.stage, rehearsal_path=args.rehearsal_report, calibration_path=args.calibration_report)
    output = args.output_dir.resolve()
    if output.exists():
        raise FileExistsError("standalone episode output already exists")
    outer = output.parent / (output.name + ".outer")
    outer.mkdir(parents=True, exist_ok=False, mode=0o700)
    command = [sys.executable, "-B", "-m", "fsq_androidworld_eval.fsq_campaign", "_episode",
               "--stage", args.stage, "--project", str(args.project.resolve()),
               "--manifest", str(args.manifest.resolve()), "--authorization", str(args.authorization.resolve()),
               "--readiness", str(args.readiness.resolve()), "--task-index", str(args.task_index),
               "--output", str(output), "--result-root", str(outer)]
    for flag, path in (("--rehearsal", args.rehearsal_report), ("--calibration", args.calibration_report)):
        if path is not None:
            command += [flag, str(path.resolve())]
    _require_window(authorization, spec["timeBudget"]["episodeSeconds"])
    process = _spawn(command, outer, spec["timeBudget"]["episodeSeconds"])
    private_json(outer / "outer-process.json", process)
    result_path = output / "result.json"
    result = None
    try:
        if not result_path.is_symlink():
            result = json.loads(result_path.read_bytes())
    except (OSError, ValueError):
        pass
    if process["forced"] or not isinstance(result, dict):
        terminal = {"kind": "fsq_standalone_outer_result", "stage": args.stage,
                    "campaignId": manifest["campaignId"], "outerProcess": process,
                    "classification": "invalid_outer_process", "officialReward": None,
                    "cleanupFailure": True, "cleanup": "unknown", "haltReason": "unknown_or_failed_cleanup",
                    "originalEpisodeResult": str(result_path) if result_path.exists() else None}
    else:
        terminal = {"kind": "fsq_standalone_outer_result", "outerProcess": process,
                    "classification": result["classification"], "officialReward": result.get("officialReward"),
                    "cleanupFailure": result["cleanupFailure"], "originalEpisodeResult": str(result_path),
                    "haltReason": halt_reason(result, outer_process=process)}
    private_json(outer / "standalone-result.json", terminal)
    print(json.dumps(terminal, sort_keys=True))
    raise SystemExit(1 if terminal["haltReason"] or terminal["cleanupFailure"] else 0)


if __name__ == "__main__":
    main()
