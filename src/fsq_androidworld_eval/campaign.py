"""Freeze dependencies and qualify the Harness before any formal Agent run.

Revision 12 workflow (all commands use the same project and Runtime PATH):
  prepare-assets --project .
  prepare --kind rehearsal --inherit-manifest <frozen-r11-full> --environment-mode-report <mode-evidence> --campaign-id <id> --output <manifest>
  qualify --manifest <manifest> --output <readiness>
  rehearse --manifest <manifest> --readiness-report <readiness> --output-dir <new-dir>
Only a fully successful 116-task rehearsal can unlock a newly prepared calibration
or full campaign via run --rehearsal-report <new-dir>/report.json. Each new run
rejects prior execution evidence. Inherited preparation copies the exact frozen
task specs, never generates new suite parameters, and binds their source hashes.
Only the Harness source identity may change from the frozen Runtime; headless and
graphics-backend evidence is independently bound to the new target identity.
Abnormal terminals retain their classification and original cleanup, with fresh
global identity, readiness, session-absence and core-service evidence before the
next launch. Boot IDs and framework/SurfaceFlinger PIDs preserve recovery boundaries.
Unknown cleanup or unavailable services pauses with explicit unstarted tasks;
there is no automatic cold restart, old-protocol score claim, or resume.
Continuation v2 additionally restores an exact sole expected-UTC timezone drift
through official public datetime setup in a fresh owned environment, only after
proven original cleanup, identity, session absence and core health. Durable before
evidence precedes mutation; strict controller close and fresh probes gate the next
different task. No task initialization, reward rewrite, Agent retry or reset occurs.
Revision 14 binds explicit Appium accessibility coexistence and its capability
audit to manifests and qualification. Inheritance may replace only the named
forwarder APK pin; task specs and every other frozen asset remain unchanged.
"""

from __future__ import annotations

import argparse
import collections
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any

from android_world import registry, suite_utils

from fsq_androidworld_eval.action_budget import STEP_BUDGET_PROTOCOL
from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG
from fsq_androidworld_eval.continuation import (
    CAMPAIGN_CONTINUATION, cleanup_known, inherited_source, inherited_tasks,
    validate_inherited_runtime,
)
from fsq_androidworld_eval.preparation import attest_device, prepare_device
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget
from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL
from fsq_androidworld_eval.environment import artifact_identity, prepare_artifacts
from fsq_androidworld_eval.rehearsal import REHEARSAL_POLICY, run_rehearsal, validate_report
from fsq_androidworld_eval.host_prerequisites import media_encoder_identity, probe_host_media
from fsq_androidworld_eval.scorer import (
    SCORING_POLICY,
    TERMINATION_POLICY,
    _calibration_gate_satisfied,
    _cleanup_failed,
    continuation_audit,
    _inherited_environment_valid,
    official_reward,
    recalculate as recalculate_score,
    record_classification,
    step_budget_valid,
    time_budget_valid,
)
from fsq_androidworld_eval.runner import (
    ALLOWED_AGENT_TARGETS,
    ANDROID_WORLD_REVISION,
    DEFAULT_ADB,
    HARNESS_REVISION,
    MCP_REQUEST_TIMEOUT_MS,
    SESSION_CREATION_TIMEOUT_SECONDS,
    PYTHON_EXEC_CALL_ADVISORY,
    PROMPT_TEMPLATE_SHA256,
    _json_safe,
    _is_json_native,
    _sha256,
    _agent_protocol_violations,
    _appium_session_hashes,
    _request_json,
)

CALIBRATION_TASKS = [
    "SystemWifiTurnOff",
    "SystemBrightnessMax",
    "ClockStopWatchRunning",
    "ClockTimerEntry",
    "ContactsAddContact",
    "MarkorCreateNote",
    "MarkorEditNote",
    "FilesMoveFile",
    "SimpleCalendarAddOneEvent",
    "CameraTakePhoto",
    "TasksHighPriorityTasks",
    "SimpleCalendarEventsOnDate",
]
RETRYABLE_INVALID_REASONS = {"invalid_infrastructure"}


def _command_version(command: str) -> str:
    completed = subprocess.run(
        [command, "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (completed.stdout or completed.stderr).strip()


def _file_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _paths_digest(paths: list[Path], root: Path) -> str:
    rows = [
        {"path": str(path.relative_to(root)), "sha256": _file_sha256(path)}
        for path in sorted(paths)
    ]
    return _sha256(rows)


def _git_revision(path: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.stdout.strip()


def _git_changes(path: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return sorted(line[3:] for line in completed.stdout.splitlines() if line)


def _runtime_identity(project: Path) -> dict[str, Any]:
    amkernel_command = shutil.which("amkernel")
    omp_command = shutil.which("omp")
    if amkernel_command is None or omp_command is None:
        raise RuntimeError("amkernel and omp must be available on PATH")
    skill_metadata = project / ".agents/skills/amkernel/.amkernel-metadata.json"
    official_manifest = project / ".agents/amkernel-official.json"
    if not skill_metadata.is_file() or not official_manifest.is_file():
        raise RuntimeError("installed AMKernel Skill identity files are missing")
    metadata = json.loads(skill_metadata.read_text())
    official = json.loads(official_manifest.read_text())
    android_world_checkout = project / "android_world"
    android_world_revision = _git_revision(android_world_checkout)
    generated_proto_paths = [
        "android_world/task_evals/information_retrieval/proto/state_pb2.py",
        "android_world/task_evals/information_retrieval/proto/state_pb2_grpc.py",
        "android_world/task_evals/information_retrieval/proto/task_pb2.py",
        "android_world/task_evals/information_retrieval/proto/task_pb2_grpc.py",
    ]
    unexpected_changes = sorted(
        set(_git_changes(android_world_checkout)) - set(generated_proto_paths)
    )
    if android_world_revision != ANDROID_WORLD_REVISION or unexpected_changes:
        raise RuntimeError(
            f"AndroidWorld checkout is not the frozen revision: {unexpected_changes}"
        )
    generated_proto_files = [
        android_world_checkout / path
        for path in generated_proto_paths
        if (android_world_checkout / path).is_file()
    ]
    harness_paths = list((project / "src/fsq_androidworld_eval").glob("*.py"))
    harness_paths.append(project / "pyproject.toml")
    agent_asset_paths = [
        path for path in (project / ".agents").rglob("*") if path.is_file()
    ]
    return {
        "amkernelVersion": _command_version(amkernel_command).removeprefix("amkernel "),
        "amkernelExecutableSha256": _file_sha256(Path(amkernel_command).resolve()),
        "ompVersion": _command_version(omp_command).removeprefix("omp "),
        "ompExecutableSha256": _file_sha256(Path(omp_command).resolve()),
        "pythonVersion": sys.version,
        "grpcForkSupport": os.environ["GRPC_ENABLE_FORK_SUPPORT"],
        "mediaEncoder": media_encoder_identity(),
        "harnessDependencies": sorted(
            [{"name": dist.metadata["Name"], "version": dist.version} for dist in importlib.metadata.distributions()],
            key=lambda row: row["name"].lower(),
        ),
        "harnessSourceSha256": _paths_digest(harness_paths, project),
        "installedAgentAssetsSha256": _paths_digest(agent_asset_paths, project),
        "androidWorldCheckoutRevision": android_world_revision,
        "skillMetadataSha256": _file_sha256(skill_metadata),
        "officialSkillManifestSha256": _file_sha256(official_manifest),
        "androidWorldGeneratedProtoSha256": _paths_digest(
            generated_proto_files, android_world_checkout
        ),
        "officialSkillArchiveSha256": official["archive"]["sha256"],
        "officialSkillSourceCommit": official["commit"],
        "skillRuntimeVersion": metadata["runtimeVersion"],
    }


def _calibration_evidence_paths(
    campaign_dir: Path, manifest: dict[str, Any]
) -> list[Path]:
    paths = [campaign_dir / "manifest.json", campaign_dir / "summary.json"]
    for task in manifest["tasks"]:
        episode_dir = campaign_dir / "episodes" / _episode_slug(task)
        results = sorted(episode_dir.glob("attempt-*/result.json"))
        if not results:
            raise ValueError(f"calibration result is missing for {task['name']}")
        paths.append(results[-1])
    if manifest.get("protocol", {}).get("campaignContinuation") == CAMPAIGN_CONTINUATION:
        extras = [campaign_dir / name for name in (
            "checkpoint.jsonl", "run-metadata.json", "device-readiness.json"
        )]
        extras.extend((campaign_dir / "recoveries").glob("*.json"))
        extras.extend((campaign_dir / "episodes").glob("*/attempt-*/result.json"))
        if manifest["protocol"].get("harnessRevision") in {13, 14}:
            for name in ("business-submission.json", "agent-events.jsonl"):
                extras.extend((campaign_dir / "episodes").glob(f"*/attempt-*/raw-private/{name}"))
        paths.extend(path for path in sorted(set(extras)) if path not in paths)
    return paths



def _calibration_result_has_provenance(
    record: dict[str, Any], task: dict[str, Any], manifest: dict[str, Any]
) -> bool:
    agent = record.get("agent")
    normalized = agent.get("normalized") if isinstance(agent, dict) else None
    audit = record.get("appiumSessionAudit")
    cleanup = record.get("cleanup")
    budget = record.get("budget")
    expected_provider, expected_model = manifest["protocol"]["model"].split("/", 1)
    tool_calls = normalized.get("toolCalls") if isinstance(normalized, dict) else None
    if not isinstance(tool_calls, list):
        return False
    python_exec_calls = [
        call
        for call in tool_calls
        if call.get("tool") == "write"
        and call.get("target") == "xd://mcp__amkernel_python_exec"
    ]
    cleanup_proofs = [
        call["sessionCleanup"] for call in tool_calls if "sessionCleanup" in call
    ]
    created_hashes = audit.get("createdSessionHashes") if isinstance(audit, dict) else None
    return (
        record.get("schemaVersion") == 3
        and record.get("androidWorld", {}).get("revision")
        == manifest["protocol"]["androidWorldRevision"]
        and record.get("amkernel", {}).get("version")
        == manifest["protocol"]["runtimeIdentity"]["amkernelVersion"]
        and record.get("target", {}).get("serial") == manifest["target"]["serial"]
        and record.get("task", {}).get("name") == task["name"]
        and record.get("task", {}).get("paramsSha256") == task["paramsSha256"]
        and record.get("protocol", {}).get("harnessRevision")
        == manifest["protocol"]["harnessRevision"]
        and record.get("protocol", {}).get("environmentArtifacts")
        == manifest["protocol"]["environmentArtifacts"]
        and record.get("protocol", {}).get("promptTemplateSha256")
        == manifest["protocol"]["promptTemplateSha256"]
        and record.get("protocol", {}).get("mcpRequestTimeoutMs")
        == manifest["protocol"]["mcpRequestTimeoutMs"]
        and record.get("protocol", {}).get("sessionCreationTimeoutSeconds")
        == manifest["protocol"]["sessionCreationTimeoutSeconds"]
        and normalized.get("provider") == expected_provider
        and normalized.get("model") == expected_model
        and normalized.get("parseErrors") == 0
        and _agent_protocol_violations(normalized) == []
        and step_budget_valid(record, task)
        and time_budget_valid(record, task, manifest["protocol"])
        and (manifest["protocol"].get("harnessRevision") != 14
             or record.get("protocol", {}).get("sessionAccessibilityConfig") == manifest["protocol"].get("sessionAccessibilityConfig") == SESSION_ACCESSIBILITY_CONFIG)
        and isinstance(budget, dict)
        and budget.get("pythonExecCalls") == len(python_exec_calls)
        and len(python_exec_calls) > 0
        and isinstance(audit, dict)
        and audit.get("createdSessionCount") == 1
        and audit.get("deletedSessionCount") == 1
        and created_hashes == audit.get("deletedSessionHashes")
        and isinstance(created_hashes, list)
        and len(created_hashes) == 1
        and audit.get("errors") == []
        and len(cleanup_proofs) == 1
        and cleanup_proofs[0].get("quitReturned") is True
        and cleanup_proofs[0].get("sessionIdSha256") == created_hashes[0]
        and record.get("evaluator", {}).get("implementation")
        == "android_world.task_eval.is_successful"
        and isinstance(cleanup, dict)
        and cleanup.get("agentSession", {}).get("status") == "closed"
        and cleanup.get("agentSession", {}).get("sessionIdSha256") == created_hashes[0]
        and cleanup.get("taskTearDown") == "completed"
        and cleanup.get("environment") == "closed"
    )
def _calibration_gate(campaign_dir: Path, project: Path) -> dict[str, str]:
    manifest_path = campaign_dir / "manifest.json"
    manifest = _load_manifest(manifest_path, project)
    if manifest.get("kind") != "calibration" or [
        task["name"] for task in manifest["tasks"]
    ] != CALIBRATION_TASKS:
        raise ValueError("calibration evidence does not use the frozen 12-task set")
    recalculation = recalculate_score(manifest_path, campaign_dir)
    if recalculation.get("qualified") is not True or recalculation.get("matchesSummary") is not True:
        raise ValueError("calibration evidence does not independently qualify")
    summary = json.loads((campaign_dir / "summary.json").read_text())
    payload = {key: value for key, value in summary.items() if key != "identitySha256"}
    identity = summary.get("identitySha256")
    if (
        not isinstance(identity, str)
        or identity != _sha256(payload)
        or summary.get("manifestSha256") != _sha256(manifest)
    ):
        raise ValueError("calibration summary identity is invalid")
    evidence_paths = _calibration_evidence_paths(campaign_dir, manifest)
    for task, result_path in zip(manifest["tasks"], evidence_paths[2:2 + len(manifest["tasks"])], strict=True):
        record = json.loads(result_path.read_text())
        if not _calibration_result_has_provenance(record, task, manifest):
            raise ValueError(f"calibration result lacks runner provenance for {task['name']}")
    return {
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "summaryIdentitySha256": identity,
        "evidenceSha256": _paths_digest(evidence_paths, campaign_dir),
    }


def _copy_calibration_evidence(source: Path, destination: Path) -> None:
    manifest = json.loads((source / "manifest.json").read_text())
    for source_path in _calibration_evidence_paths(source, manifest):
        target = destination / source_path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != source_path.read_bytes():
            raise ValueError("output directory contains different calibration evidence")
        if not target.exists():
            target.write_bytes(source_path.read_bytes())


def _environment_mode_report(path: Path, target: dict[str, Any]) -> dict[str, Any]:
    import hashlib

    path = path.resolve()
    payload = path.read_bytes()
    evidence = json.loads(payload)
    if not isinstance(evidence, dict) or any(evidence.get(key) != target.get(key) for key in ("avd", "serial")):
        raise ValueError("environment mode report belongs to a different target")
    return {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest(), "evidence": evidence}


def build_manifest(
    campaign_id: str,
    kind: str = "calibration",
    project: Path | None = None,
    calibration_campaign_dir: Path | None = None,
    inherit_manifest: Path | None = None,
    environment_mode_report: Path | None = None,
) -> dict[str, Any]:
    project = (project or Path.cwd()).resolve()
    if inherit_manifest is not None:
        source, provenance = inherited_source(inherit_manifest)
        mode = _environment_mode_report(environment_mode_report, source["target"]) if environment_mode_report is not None else None
        if campaign_id == source["campaignId"]:
            raise ValueError("inherited campaign requires a new campaign identity")
        if kind not in {"calibration", "full", "rehearsal"}:
            raise ValueError(f"unsupported campaign kind: {kind}")
        if kind == "full" and calibration_campaign_dir is None:
            raise ValueError("full campaign requires qualified calibration evidence")
        runtime_identity = _runtime_identity(project)
        validate_inherited_runtime(source, runtime_identity)
        current_artifacts = artifact_identity(project)
        if not _inherited_environment_valid(source["protocol"]["environmentArtifacts"], current_artifacts):
            raise ValueError("inherited environment may replace only the named accessibility forwarder")
        manifest = json.loads(json.dumps(source))
        manifest.update({
            "campaignId": campaign_id,
            "kind": kind,
            "calibrationGate": (
                _calibration_gate(calibration_campaign_dir.resolve(), project)
                if kind == "full" else None
            ),
            "inheritedManifest": provenance,
            "tasks": inherited_tasks(source, CALIBRATION_TASKS if kind == "calibration" else None),
        })
        if mode is not None:
            manifest["target"]["environmentMode"] = mode
        manifest["protocol"].update({
            "harnessRevision": HARNESS_REVISION,
            "runtimeIdentity": runtime_identity,
            "campaignContinuation": dict(CAMPAIGN_CONTINUATION),
            "answerSubmission": dict(ANSWER_SUBMISSION_PROTOCOL),
            "promptTemplateSha256": PROMPT_TEMPLATE_SHA256,
            "sessionAccessibilityConfig": dict(SESSION_ACCESSIBILITY_CONFIG),
            "environmentArtifacts": current_artifacts,
        })
        manifest["invalidRules"]["cleanupFailure"] = (
            "Preserve original cleanup and reward; continue only after verified recovery, "
            "otherwise pause for coordinated recovery without resuming this campaign."
        )
        manifest["invalidRules"]["invalid_protocol"] = (
            "Preserve episode protocol violations as invalid; continue only after verified recovery. "
            "Any global frozen identity mismatch pauses the campaign."
        )
        return manifest
    task_registry = registry.TaskRegistry()
    all_tasks = task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY)
    android_names = set(task_registry.get_registry(task_registry.ANDROID_FAMILY))
    information_retrieval_names = set(
        task_registry.get_registry(task_registry.INFORMATION_RETRIEVAL_FAMILY)
    )
    if kind == "calibration":
        task_names = CALIBRATION_TASKS
        calibration_gate = None
    elif kind in {"full", "rehearsal"}:
        if kind == "full" and calibration_campaign_dir is None:
            raise ValueError("full campaign requires qualified calibration evidence")
        task_names = sorted(all_tasks)
        calibration_gate = (
            _calibration_gate(calibration_campaign_dir.resolve(), project)
            if kind == "full" else None
        )
    else:
        raise ValueError(f"unsupported campaign kind: {kind}")
    metadata_path = Path(registry.__file__).with_name("task_metadata.json")
    metadata_rows = json.loads(metadata_path.read_text())
    metadata = {row["task_name"]: row for row in metadata_rows}
    suite = suite_utils.create_suite(
        all_tasks,
        n_task_combinations=1,
        seed=30,
        tasks=task_names,
        use_identical_params=True,
        env=None,
    )
    tasks = []
    for index, name in enumerate(task_names):
        instance = suite[name][0]
        params = instance.params
        row = metadata.get(name, {})
        family = (
            "android"
            if name in android_names
            else "information_retrieval"
            if name in information_retrieval_names
            else "unknown"
        )
        safe_params = _json_safe(params)
        params_transport = "seed"
        if _is_json_native(params):
            try:
                reconstructed = all_tasks[name](
                    json.loads(json.dumps(safe_params, separators=(",", ":")))
                )
            except Exception:
                pass
            else:
                if _sha256(reconstructed.params) == _sha256(params):
                    params_transport = "json"
        maximum = suite_utils._allocate_step_budget(instance.complexity)
        tasks.append(
            {
                "index": index,
                "name": name,
                "family": family,
                "apps": list(instance.app_names),
                "complexity": instance.complexity,
                "maxSteps": maximum,
                "timeBudget": episode_time_budget(maximum),
                "difficulty": row.get("difficulty", "unknown"),
                "tags": row.get("tags", []),
                "instanceSeed": params["seed"],
                "params": safe_params,
                "paramsSha256": _sha256(params),
                "paramsTransport": params_transport,
            }
        )
    return {
        "schemaVersion": 2,
        "campaignId": campaign_id,
        "kind": kind,
        "calibrationGate": calibration_gate,
        "protocol": {
            "androidWorldRevision": ANDROID_WORLD_REVISION,
            "androidWorldPackageVersion": importlib.metadata.version("android-world"),
            "taskMetadataSha256": _file_sha256(metadata_path),
            "harnessRevision": HARNESS_REVISION,
            "runtimeIdentity": _runtime_identity(project),
            "environmentArtifacts": artifact_identity(project),
            "sessionAccessibilityConfig": dict(SESSION_ACCESSIBILITY_CONFIG),
            "harnessRehearsal": REHEARSAL_POLICY,
            "campaignContinuation": dict(CAMPAIGN_CONTINUATION),
            "model": "github-copilot/gpt-5.6-sol",
            "taskRandomSeed": 30,
            "nTaskCombinations": 1,
            "useIdenticalParams": True,
            "promptTemplateSha256": PROMPT_TEMPLATE_SHA256,
            "timeBudget": TIME_BUDGET_PROTOCOL,
            "answerSubmission": ANSWER_SUBMISSION_PROTOCOL,
            "terminationPolicy": TERMINATION_POLICY,
            "scoringPolicy": SCORING_POLICY,
            "mcpRequestTimeoutMs": MCP_REQUEST_TIMEOUT_MS,
            "sessionCreationTimeoutSeconds": SESSION_CREATION_TIMEOUT_SECONDS,
            "pythonExecCallAdvisory": PYTHON_EXEC_CALL_ADVISORY,
            "maxAppiumSessionsPerEpisode": 1,
            "stepBudget": STEP_BUDGET_PROTOCOL,
            "fullTaskRetryLimit": 0,
            "invalidRetryLimit": 1,
            "scoreContract": "official_reward_only",
            "agentToolPolicy": {
                "tools": ["read", "write"],
                "allowedTargets": list(ALLOWED_AGENT_TARGETS),
            },
        },
        "target": {
            "avd": "AndroidWorldAvd",
            "deviceProfile": "Pixel 6",
            "apiLevel": 33,
            "abi": "arm64-v8a",
            "serial": "emulator-5554",
            "consolePort": 5554,
            "grpcPort": 8554,
            "appiumUrl": "http://127.0.0.1:4723",
            **({"environmentMode": _environment_mode_report(environment_mode_report, {
                "avd": "AndroidWorldAvd", "serial": "emulator-5554"
            })} if environment_mode_report is not None else {}),
        },
        "invalidRules": {
            "invalid_infrastructure": "Base environment failed before an Agent attempt; only this class may receive one frozen retry.",
            "invalid_setup": "Task initialization failed; do not retry inside a formal campaign.",
            "invalid_evaluator": "The official AndroidWorld evaluator did not return a reward; do not retry the Agent.",
            "invalid_protocol": "Preserve episode protocol violations as invalid; continue only after verified recovery. Any global frozen identity mismatch pauses the campaign.",
            "invalid_agent": "Unknown or forced Agent termination, or no valid Agent attempt; preserve any evaluator reward and do not retry.",
            "budget_limited": "Step exhaustion or business/OMP deadline is an evaluated budget-limited attempt, not Agent completion or a replacement reward.",
            "cleanupFailure": "Preserve original cleanup and reward; continue only after verified recovery, otherwise pause for coordinated recovery without resuming this campaign.",
        },
        "tasks": tasks,
    }


def write_manifest(
    path: Path,
    campaign_id: str,
    kind: str = "calibration",
    project: Path | None = None,
    calibration_campaign_dir: Path | None = None,
    inherit_manifest: Path | None = None,
    environment_mode_report: Path | None = None,
) -> None:
    manifest = build_manifest(campaign_id, kind, project, calibration_campaign_dir, inherit_manifest, environment_mode_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def _load_manifest(path: Path, project: Path | None = None) -> dict[str, Any]:
    project = (project or Path.cwd()).resolve()
    manifest = json.loads(path.read_text())
    if manifest.get("schemaVersion") != 2:
        raise ValueError("unsupported campaign manifest schema")
    kind = manifest.get("kind")
    tasks = manifest.get("tasks", [])
    mode = manifest.get("target", {}).get("environmentMode")
    if mode is not None:
        if not isinstance(mode, dict) or not isinstance(mode.get("path"), str):
            raise ValueError("environment mode identity is malformed")
        if mode != _environment_mode_report(Path(mode["path"]), manifest["target"]):
            raise ValueError("environment mode evidence digest mismatch")
    if kind == "calibration":
        if manifest.get("calibrationGate") is not None or len(tasks) != len(CALIBRATION_TASKS):
            raise ValueError("calibration manifest must contain the frozen 12-task set")
    elif kind == "full":
        gate = manifest.get("calibrationGate")
        if not isinstance(gate, dict) or set(gate) != {
            "campaignId",
            "manifestSha256",
            "summaryIdentitySha256",
            "evidenceSha256",
        }:
            raise ValueError("full campaign calibration gate is missing or malformed")
        if len(tasks) != 116:
            raise ValueError("full campaign must contain all 116 official tasks")
    elif kind == "rehearsal":
        if manifest.get("calibrationGate") is not None or len(tasks) != REHEARSAL_POLICY["requiredTaskCount"]:
            raise ValueError("rehearsal manifest must contain all 116 official tasks without a calibration gate")
    else:
        raise ValueError("campaign kind is invalid")
    protocol = manifest.get("protocol", {})
    metadata_path = Path(registry.__file__).with_name("task_metadata.json")
    expected = {
        "androidWorldRevision": ANDROID_WORLD_REVISION,
        "androidWorldPackageVersion": importlib.metadata.version("android-world"),
        "taskMetadataSha256": _file_sha256(metadata_path),
        "promptTemplateSha256": PROMPT_TEMPLATE_SHA256,
        "harnessRevision": HARNESS_REVISION,
        "sessionAccessibilityConfig": SESSION_ACCESSIBILITY_CONFIG,
        "stepBudget": STEP_BUDGET_PROTOCOL,
        "timeBudget": TIME_BUDGET_PROTOCOL,
        "answerSubmission": ANSWER_SUBMISSION_PROTOCOL,
        "terminationPolicy": TERMINATION_POLICY,
        "scoringPolicy": SCORING_POLICY,
        "mcpRequestTimeoutMs": MCP_REQUEST_TIMEOUT_MS,
        "sessionCreationTimeoutSeconds": SESSION_CREATION_TIMEOUT_SECONDS,
        "runtimeIdentity": _runtime_identity(project),
        "environmentArtifacts": artifact_identity(project),
        "harnessRehearsal": REHEARSAL_POLICY,
        "campaignContinuation": CAMPAIGN_CONTINUATION,
        "scoreContract": "official_reward_only",
        "model": "github-copilot/gpt-5.6-sol",
        "taskRandomSeed": 30,
        "nTaskCombinations": 1,
        "useIdenticalParams": True,
        "pythonExecCallAdvisory": PYTHON_EXEC_CALL_ADVISORY,
        "maxAppiumSessionsPerEpisode": 1,
        "fullTaskRetryLimit": 0,
        "invalidRetryLimit": 1,
        "agentToolPolicy": {
            "tools": ["read", "write"],
            "allowedTargets": list(ALLOWED_AGENT_TARGETS),
        },
    }
    mismatches = {
        key: {"manifest": protocol.get(key), "runtime": value}
        for key, value in expected.items()
        if protocol.get(key) != value
    }
    unexpected_keys = sorted(set(protocol) - set(expected))
    if unexpected_keys:
        mismatches["unexpectedKeys"] = {"manifest": unexpected_keys, "runtime": []}
    provenance = manifest.get("inheritedManifest")
    if provenance is not None:
        if not isinstance(provenance, dict) or not isinstance(provenance.get("path"), str):
            raise ValueError("inherited source provenance is malformed")
        source, expected_provenance = inherited_source(Path(provenance["path"]))
        expected_tasks = inherited_tasks(source, CALIBRATION_TASKS if kind == "calibration" else None)
        if provenance != expected_provenance or tasks != expected_tasks:
            raise ValueError("inherited source provenance or exact task specs mismatch")
        validate_inherited_runtime(source, protocol.get("runtimeIdentity", {}))
        frozen_protocol = {key: value for key, value in source["protocol"].items()
                           if key not in {"harnessRevision", "runtimeIdentity", "promptTemplateSha256", "environmentArtifacts"}}
        if any(protocol.get(key) != value for key, value in frozen_protocol.items()):
            raise ValueError("inherited source frozen episode protocol mismatch")
        if not _inherited_environment_valid(source["protocol"]["environmentArtifacts"], protocol.get("environmentArtifacts")):
            raise ValueError("inherited environment may replace only the named accessibility forwarder")
        if {key: value for key, value in manifest.get("target", {}).items() if key != "environmentMode"} != source["target"]:
            raise ValueError("inherited source target mismatch")
    elif kind == "calibration":
        expected_manifest = build_manifest(
            manifest["campaignId"], "calibration", project,
            environment_mode_report=Path(mode["path"]) if mode is not None else None,
        )
        if manifest != expected_manifest:
            raise ValueError("calibration manifest differs from the frozen campaign")
    if mismatches:
        raise ValueError(f"campaign protocol mismatch: {mismatches}")
    seen: set[str] = set()
    for expected_index, task in enumerate(manifest.get("tasks", [])):
        if task.get("index") != expected_index:
            raise ValueError("campaign task indexes must be contiguous and ordered")
        name = task.get("name")
        if not isinstance(name, str) or name in seen:
            raise ValueError("campaign task names must be unique strings")
        seen.add(name)
        if _sha256(task.get("params")) != task.get("paramsSha256"):
            raise ValueError(f"campaign parameter digest mismatch for {name}")
        if task.get("paramsTransport") not in {"json", "seed"}:
            raise ValueError(f"campaign parameter transport is invalid for {name}")
        maximum = task.get("maxSteps")
        if type(maximum) is not int or maximum <= 0 or task.get("timeBudget") != episode_time_budget(maximum):
            raise ValueError(f"campaign time budget mismatch for {name}")
    if not seen:
        raise ValueError("campaign has no tasks")
    if kind in {"full", "rehearsal"}:
        task_registry = registry.TaskRegistry()
        expected_names = sorted(task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY))
        if [task["name"] for task in tasks] != expected_names:
            raise ValueError("all-task manifest must contain the complete ordered official registry")
        if provenance is None:
            from fsq_androidworld_eval.runner import _task

            android_tasks = set(task_registry.get_registry(task_registry.ANDROID_FAMILY))
            for task in tasks:
                instance = _task(
                    task["name"],
                    json.dumps(task["params"]) if task["paramsTransport"] == "json" else None,
                    task["instanceSeed"] if task["paramsTransport"] == "seed" else None,
                )
                family = "android" if task["name"] in android_tasks else "information_retrieval"
                if (
                    _sha256(instance.params) != task["paramsSha256"]
                    or list(instance.app_names) != task["apps"]
                    or instance.complexity != task["complexity"]
                    or suite_utils._allocate_step_budget(instance.complexity) != task["maxSteps"]
                    or task["family"] != family
                ):
                    raise ValueError(f"frozen task cannot be reconstructed before device use: {task['name']}")
    return manifest


def _classification(
    record: dict[str, Any],
    task: dict[str, Any] | None = None,
    protocol: dict[str, Any] | None = None,
) -> str:
    return record_classification(record, task, protocol)


def _append_checkpoint(path: Path, event: dict[str, Any]) -> None:
    line = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())


def _episode_slug(task: dict[str, Any]) -> str:
    return f"{task['index']:03d}-{task['name']}"


def _workspace_digest(root: Path) -> str:
    rows = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        rows.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": _file_sha256(path),
            }
        )
    return _sha256(rows)


def _prepare_agent_workspace(source_project: Path, destination: Path) -> dict[str, Any]:
    source_agents = source_project / ".agents"
    if not source_agents.is_dir():
        raise RuntimeError("source project has no installed .agents directory")
    destination.mkdir(parents=True)
    shutil.copytree(source_agents, destination / ".agents")
    mcp_dir = destination / ".omp"
    mcp_dir.mkdir()
    amkernel_command = shutil.which("amkernel")
    if amkernel_command is None:
        raise RuntimeError("amkernel command is unavailable")
    mcp_config = {
        "$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json",
        "mcpServers": {
            "amkernel": {
                "command": str(Path(amkernel_command).resolve()),
                "cwd": ".",
                "type": "stdio",
                "timeout": MCP_REQUEST_TIMEOUT_MS,
            }
        },
    }
    (mcp_dir / "mcp.json").write_text(json.dumps(mcp_config, indent=2) + "\n")
    sandbox_profile = destination / ".sandbox.sb"
    # The agent may reach only the audited Appium proxy for Android control.
    # Keep model/MCP IPC available; block known direct device transports.
    direct_android_ports = (4723, 5037, 5554, 8554, *range(8200, 8300))
    transport_rules = "".join(
        f'(deny network-outbound (remote tcp "*:{port}"))\n'
        for port in direct_android_ports
    )
    sandbox_profile.write_text(
        "(version 1)\n"
        "(allow default)\n"
        + transport_rules
        + f"(deny file-read* file-write* (subpath {json.dumps(str(source_project))}))\n"
    )
    return {
        "digest": _workspace_digest(destination),
        "fileCount": sum(1 for path in destination.rglob("*") if path.is_file()),
        "sandboxProfileSha256": _file_sha256(sandbox_profile),
    }


def _readiness_identity(path: Path, manifest: dict[str, Any]) -> str:
    readiness = json.loads(path.read_text())
    if readiness.get("environmentClose") != "closed":
        raise ValueError("readiness report did not close the AndroidWorld environment")
    payload = {key: value for key, value in readiness.items() if key != "identitySha256"}
    identity = readiness.get("identitySha256")
    if identity != _sha256(payload):
        raise ValueError("readiness report identity is invalid")
    if not readiness.get("qualified"):
        raise ValueError("readiness report is not qualified")
    if readiness.get("manifestSha256") != _sha256(manifest):
        raise ValueError("readiness report belongs to a different manifest")
    if readiness.get("target") != manifest["target"]:
        raise ValueError("readiness target/environment mode identity differs from manifest")
    if readiness.get("environmentArtifacts") != manifest["protocol"]["environmentArtifacts"]:
        raise ValueError("readiness environment artifact identity differs from manifest")
    if readiness.get("sessionAccessibilityConfig") != manifest["protocol"].get("sessionAccessibilityConfig") or readiness.get("sessionAccessibilityConfig") != SESSION_ACCESSIBILITY_CONFIG:
        raise ValueError("readiness session accessibility configuration differs from manifest")
    expected_apps = sorted({app for task in manifest["tasks"] for app in task["apps"]})
    if (
        readiness.get("schemaVersion") != 2
        or readiness.get("adbOutputIsolated") is not True
        or readiness.get("snapshotRestores")
        != [{"app": app, "status": "restored"} for app in expected_apps]
    ):
        raise ValueError("readiness report lacks clean ADB capture or complete snapshot restore proof")
    if "vlc" in expected_apps and any(readiness.get("vlcStartup", {}).get(key) is not True for key in (
        "mainActivityObserved", "quitReturned", "onboardingCompleted", "allFilesAuthorized", "snapshotSavedAfterUi",
    )):
        raise ValueError("readiness report lacks completed VLC first-launch UI and snapshot evidence")
    return identity


def _run_process(command: list[str], timeout: int) -> int:
    process = subprocess.Popen(command, start_new_session=os.name == "posix")
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=10)
        return 124


def _run_attempt(
    manifest: dict[str, Any],
    task: dict[str, Any],
    attempt_dir: Path,
    args: argparse.Namespace,
    agent_workspace: Path,
    readiness_path: Path,
    readiness_identity: str,
) -> dict[str, Any]:
    protocol = manifest["protocol"]
    target = manifest["target"]
    command = [
        sys.executable,
        "-m",
        "fsq_androidworld_eval.runner",
        "--project",
        str(agent_workspace),
        "--artifact-root",
        str(Path(args.project).resolve()),
        "--output-dir",
        str(attempt_dir),
        "--task",
        task["name"],
    ]
    if task["paramsTransport"] == "json":
        command.extend(["--params", json.dumps(task["params"], separators=(",", ":"))])
    else:
        command.extend(["--task-seed", str(task["instanceSeed"])])
    command.extend(
        [
            "--expected-params-sha256",
            task["paramsSha256"],
            "--expected-max-steps",
            str(task["maxSteps"]),
            "--model",
            protocol["model"],
            "--expected-amkernel-version",
            protocol["runtimeIdentity"]["amkernelVersion"],
            "--sandbox-profile",
            str(agent_workspace / ".sandbox.sb"),
            "--readiness-report",
            str(readiness_path),
            "--expected-readiness-sha256",
            readiness_identity,
            "--python-exec-call-advisory",
            str(protocol["pythonExecCallAdvisory"]),
            "--appium-url",
            target["appiumUrl"],
            "--device-serial",
            target["serial"],
            "--console-port",
            str(target["consolePort"]),
            "--grpc-port",
            str(target["grpcPort"]),
            "--adb-path",
            str(Path(args.adb_path).resolve()),
        ]
    )
    started_at = time.time()
    launch_error = None
    try:
        exit_code = _run_process(command, task["timeBudget"]["episodeSeconds"])
    except Exception as exc:
        exit_code = None
        launch_error = f"{type(exc).__name__}: {exc}"
    result_path = attempt_dir / "result.json"
    preserved_result = None
    if result_path.exists():
        try:
            result = json.loads(result_path.read_text())
            if not isinstance(result, dict):
                raise ValueError("runner result is not an object")
        except (OSError, ValueError) as exc:
            launch_error = f"{type(exc).__name__}: {exc}"
            preserved_path = attempt_dir / "unreadable-result.json"
            if preserved_path.exists():
                raise ValueError("unreadable terminal evidence path already exists")
            result_path.rename(preserved_path)
            preserved_result = str(preserved_path)
        else:
            return result
    if not result_path.exists():
        return {
            "schemaVersion": 3,
            "recordSource": "campaign_missing_runner_result",
            "startedAtUnix": started_at,
            "completedAtUnix": time.time(),
            "preservedRunnerResult": preserved_result,
            "task": {"name": task["name"], "seed": task["instanceSeed"]},
            "protocol": {"timeBudget": TIME_BUDGET_PROTOCOL},
            "timeBudget": task["timeBudget"],
            "agent": {
                "state": "unknown",
                "runnerExitCode": exit_code,
                "agentCompleted": False,
                "termination": {"reason": "unknown_termination"},
            },
            "officialReward": None,
            "invalidReason": "invalid_agent",
            "error": {
                "type": "MissingResult",
                "message": (
                    f"episode process exited {exit_code} without result.json; "
                    f"device mutation and cleanup state are unknown; {launch_error or ''}"
                ),
            },
            "cleanup": {
                "agentSession": {"status": "unknown"},
                "taskTearDown": "unknown",
                "environment": "unknown",
            },
        }


def _group_metrics(
    tasks: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    episode_by_index = {episode["index"]: episode for episode in episodes}
    groups: dict[str, dict[str, Any]] = {}
    for task in tasks:
        raw_labels = task.get(field)
        labels = raw_labels if isinstance(raw_labels, list) else [raw_labels]
        labels = [str(label) for label in labels if label not in (None, "")]
        if not labels:
            labels = ["untagged" if field == "tags" else "none"]
        for label in labels:
            group = groups.setdefault(
                label,
                {
                    "plannedEpisodeCount": 0,
                    "completedEpisodeCount": 0,
                    "validEpisodeCount": 0,
                    "passedEpisodeCount": 0,
                    "failedEpisodeCount": 0,
                    "invalidEpisodeCount": 0,
                    "officialRewardSum": 0.0,
                    "scoreOnValidEpisodes": None,
                    "lowerBoundScoreOnPlannedEpisodes": 0.0,
                },
            )
            group["plannedEpisodeCount"] += 1
            episode = episode_by_index.get(task["index"])
            if episode is None:
                continue
            group["completedEpisodeCount"] += 1
            if episode["classification"].startswith("invalid_"):
                group["invalidEpisodeCount"] += 1
                continue
            reward = float(episode["officialReward"])
            group["validEpisodeCount"] += 1
            group["officialRewardSum"] += reward
            if reward > 0.5:
                group["passedEpisodeCount"] += 1
            else:
                group["failedEpisodeCount"] += 1
    for group in groups.values():
        valid = group["validEpisodeCount"]
        planned = group["plannedEpisodeCount"]
        if valid:
            group["scoreOnValidEpisodes"] = group["officialRewardSum"] / valid
        group["lowerBoundScoreOnPlannedEpisodes"] = (
            group["officialRewardSum"] / planned if planned else 0.0
        )
    return dict(sorted(groups.items()))


def _write_summary(output_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    classifications: collections.Counter[str] = collections.Counter()
    invalid_breakdown: collections.Counter[str] = collections.Counter()
    episodes = []
    valid_rewards: list[float] = []
    cleanup_failures = 0
    for task in manifest["tasks"]:
        episode_dir = output_dir / "episodes" / _episode_slug(task)
        attempts = sorted(episode_dir.glob("attempt-*/result.json"))
        if not attempts:
            continue
        result_path = attempts[-1]
        record = json.loads(result_path.read_text())
        classification = _classification(record, task, manifest.get("protocol"))
        classifications[classification] += 1
        if classification.startswith("invalid_"):
            invalid_breakdown[classification] += 1
        else:
            valid_rewards.append(float(record["officialReward"]))
        cleanup_failed = _cleanup_failed(record)
        cleanup_failures += int(cleanup_failed)
        agent = record.get("agent") if isinstance(record.get("agent"), dict) else {}
        budget = record.get("budget") if isinstance(record.get("budget"), dict) else {}
        episodes.append(
            {
                "index": task["index"],
                "task": task["name"],
                "attempts": len(attempts),
                "classification": classification,
                "officialReward": official_reward(record, manifest.get("protocol")),
                "durationSeconds": agent.get("durationSeconds"),
                "pythonExecCalls": budget.get("pythonExecCalls"),
                "exceededCallAdvisory": budget.get("exceededAdvisory"),
                "cleanupFailure": cleanup_failed,
                "result": str(result_path.relative_to(output_dir)),
            }
        )
    planned_count = len(manifest["tasks"])
    completed_count = len(episodes)
    valid_count = len(valid_rewards)
    calibration_gate_satisfied = _calibration_gate_satisfied(manifest, output_dir)
    reward_sum = sum(valid_rewards)
    continuation = continuation_audit(manifest, output_dir)
    if continuation:
        cleanup_failures = max(cleanup_failures, continuation["coverageAudit"]["cleanupFailureCount"])
    qualified = (
        completed_count == planned_count
        and valid_count == planned_count
        and cleanup_failures == 0
        and calibration_gate_satisfied
        and (not continuation or continuation["coverageAudit"]["valid"])
    )
    summary = {
        "schemaVersion": 2,
        "campaignId": manifest["campaignId"],
        "manifestSha256": _sha256(manifest),
        "plannedEpisodeCount": planned_count,
        "completedEpisodeCount": completed_count,
        "validEpisodeCount": valid_count,
        "validEpisodeCoverage": valid_count / planned_count if planned_count else 0.0,
        "officialRewardSum": reward_sum,
        "officialScore": reward_sum / planned_count if qualified else None,
        "diagnosticScoreOnValidEpisodes": reward_sum / valid_count if valid_count else None,
        "lowerBoundScoreOnPlannedEpisodes": reward_sum / planned_count if planned_count else None,
        "qualified": qualified,
        "classifications": dict(sorted(classifications.items())),
        "invalidBreakdown": dict(sorted(invalid_breakdown.items())),
        "cleanupFailureCount": cleanup_failures,
        "calibrationGateSatisfied": calibration_gate_satisfied,
        "metrics": {
            "family": _group_metrics(manifest["tasks"], episodes, "family"),
            "app": _group_metrics(manifest["tasks"], episodes, "apps"),
            "difficulty": _group_metrics(manifest["tasks"], episodes, "difficulty"),
            "tag": _group_metrics(manifest["tasks"], episodes, "tags"),
        },
        "episodes": episodes,
        "updatedAtUnix": time.time(),
    }
    summary.update(continuation)
    if continuation and manifest["kind"] == "full":
        summary["officialScore"] = None
    summary["identitySha256"] = _sha256(summary)
    temporary_path = output_dir / "summary.json.tmp"
    temporary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    os.replace(temporary_path, output_dir / "summary.json")
    return summary


def _retryable(record: dict[str, Any]) -> bool:
    return (
        _classification(record) in RETRYABLE_INVALID_REASONS
        and record.get("agent") is None
    )


def _core_service_health(readiness: dict[str, Any], adb_path: str) -> dict[str, Any]:
    """Bounded read-only readiness, never a session or an emulator restart."""
    import grpc
    from android_env.proto import emulator_controller_pb2_grpc
    from google.protobuf import empty_pb2
    import uuid

    target = readiness["target"]
    serial = target["serial"]

    def adb(*arguments: str) -> str:
        completed = subprocess.run(
            [adb_path, "-s", serial, *arguments], check=True,
            capture_output=True, text=True, timeout=10,
        )
        return completed.stdout.strip()

    result = {
        "adbState": adb("get-state"),
        "bootCompleted": adb("shell", "getprop", "sys.boot_completed"),
        "activityService": adb("shell", "service", "check", "activity").endswith(": found"),
        "packageService": adb("shell", "service", "check", "package").endswith(": found"),
        "settingsService": adb("shell", "service", "check", "settings").endswith(": found"),
        "windowService": adb("shell", "service", "check", "window").endswith(": found"),
        "systemServerPids": adb("shell", "pidof", "system_server").split(),
        "surfaceFlingerPids": adb("shell", "pidof", "surfaceflinger").split(),
        "bootId": adb("shell", "cat", "/proc/sys/kernel/random/boot_id"),
        "appiumReady": _request_json(target["appiumUrl"].rstrip("/") + "/status").get("value", {}).get("ready") is True,
        "grpcReady": False,
    }
    with grpc.secure_channel(f"localhost:{target['grpcPort']}", grpc.local_channel_credentials()) as channel:
        grpc.channel_ready_future(channel).result(timeout=10)
        status = emulator_controller_pb2_grpc.EmulatorControllerStub(channel).getStatus(empty_pb2.Empty(), timeout=10)
        result["grpcReady"] = status.booted is True
    try:
        uuid.UUID(result["bootId"])
        boot_id_valid = True
    except ValueError:
        boot_id_valid = False
    result["qualified"] = (
        result["adbState"] == "device" and result["bootCompleted"] == "1"
        and all(result[field] is True for field in (
            "activityService", "packageService", "settingsService", "windowService", "appiumReady", "grpcReady"
        ))
        and boot_id_valid
        and all(result[field] and all(pid.isdigit() and int(pid) > 0 for pid in result[field])
                for field in ("systemServerPids", "surfaceFlingerPids"))
    )
    return result


def restore_official_datetime(project: Path, target: dict[str, Any], adb_path: str) -> dict[str, Any]:
    """Official nonscoring setup; caller owns safety gates and durable evidence.

    Scheduling uses recover_campaign_environment to prove prerequisites and record
    immutable before-state before invoking this manifest-independent helper.
    """
    remediation = {
        "name": "android_world.utils.datetime_utils.setup_datetime",
        "allowedScope": ["auto_time", "auto_time_zone", "time_12_24", "timezone"],
        "freezeDatetime": False, "startedAtUnix": time.time(),
        "outcome": "failed", "environmentClose": "not_created", "errors": [],
    }
    env = None
    try:
        from android_world.utils import datetime_utils
        from fsq_androidworld_eval.environment import load_environment, close_environment

        env = load_environment(
            artifact_root=project, console_port=target["consolePort"],
            adb_path=adb_path, grpc_port=target["grpcPort"], freeze_datetime=False,
        )
        datetime_utils.setup_datetime(env.controller)
        remediation["outcome"] = "completed"
    except Exception as exc:
        remediation["errors"].append({"type": type(exc).__name__, "message": str(exc)})
    finally:
        if env is not None:
            try:
                close_environment(env)
                remediation["environmentClose"] = "closed"
            except Exception as exc:
                remediation["environmentClose"] = "failed"
                remediation["outcome"] = "failed"
                remediation["errors"].append({"type": type(exc).__name__, "message": str(exc)})
        remediation["completedAtUnix"] = time.time()
    return remediation


def recover_campaign_environment(
    output_dir: Path, manifest: dict[str, Any], task: dict[str, Any], attempt: int,
    record: dict[str, Any], result_path: Path, readiness: dict[str, Any],
    readiness_identity: str, adb_path: str, project: Path,
) -> dict[str, Any]:
    """Persist safety evidence, restore only UTC drift, and freshly requalify.

    The caller supplies a fresh evidence directory with frozen manifest/readiness
    files and an immutable terminal result; existing evidence is never overwritten.
    This is Harness environment setup after cleanup, never an episode retry.
    """
    recovery_prefix = output_dir / "recoveries" / f"{_episode_slug(task)}-attempt-{attempt}"
    if any(Path(str(recovery_prefix) + suffix).exists() for suffix in (".json", "-before.json")):
        raise ValueError("campaign recovery cannot overwrite or resume prior recovery evidence")
    evidence = {
        "schemaVersion": 2,
        "manifestSha256": _sha256(manifest),
        "readinessIdentitySha256": readiness_identity,
        "taskSpecSha256": _sha256(task),
        "taskIndex": task["index"], "task": task["name"], "attempt": attempt,
        "result": str(result_path.relative_to(output_dir)),
        "resultSha256": _file_sha256(result_path),
        "originalClassification": _classification(record, task, manifest["protocol"]),
        "originalCleanup": record.get("cleanup"),
        "recordedAtUnix": time.time(),
    }
    def identity_probe() -> dict[str, Any]:
        return {
            "verified": (
                _load_manifest(output_dir / "manifest.json", project) == manifest
                and _readiness_identity(output_dir / "device-readiness.json", manifest) == readiness_identity
                and json.loads((output_dir / "device-readiness.json").read_text()) == readiness
            ),
            "manifestSha256": _sha256(manifest),
            "readinessIdentitySha256": readiness_identity,
        }

    probes = (
        ("campaignIdentity", identity_probe),
        ("attestation", lambda: attest_device(readiness, adb_path)),
        ("sessionAbsence", lambda: {
            "sessionHashes": _appium_session_hashes(
                manifest["target"]["appiumUrl"], adb_path, manifest["target"]["serial"]
            ), "verified": True,
        }),
        ("coreServices", lambda: _core_service_health(readiness, adb_path)),
    )
    for field, probe in probes:
        try:
            evidence[field] = probe()
        except Exception as exc:
            evidence[field] = {"qualified": False, "verified": False,
                               "error": {"type": type(exc).__name__, "message": str(exc)}}
    mismatch = evidence["attestation"].get("mismatches", {})
    timezone_only = (
        evidence["attestation"].get("qualified") is False
        and isinstance(mismatch, dict) and set(mismatch) == {"timezone"}
        and isinstance(mismatch["timezone"], dict)
        and mismatch["timezone"].get("expected") == "UTC"
        and isinstance(mismatch["timezone"].get("observed"), str)
        and bool(mismatch["timezone"]["observed"])
        and mismatch["timezone"]["observed"] != "UTC"
    )
    safe_to_restore = (
        manifest["protocol"].get("campaignContinuation") == CAMPAIGN_CONTINUATION
        and evidence["campaignIdentity"].get("verified") is True
        and cleanup_known(record)
        and evidence["sessionAbsence"].get("verified") is True
        and evidence["sessionAbsence"].get("sessionHashes") == []
        and evidence["coreServices"].get("qualified") is True
    )
    recovery_dir = output_dir / "recoveries"
    recovery_dir.mkdir(exist_ok=True)
    before = dict(evidence)
    before["recordedAtUnix"] = time.time()
    before["identitySha256"] = _sha256(before)
    before_path = recovery_dir / f"{_episode_slug(task)}-attempt-{attempt}-before.json"
    with before_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(before, indent=2, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    # Directory durability and checkpoint binding precede the first mutation.
    directory_fd = os.open(recovery_dir, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    evidence["beforeEvidence"] = {
        "path": str(before_path.relative_to(output_dir)), "sha256": _file_sha256(before_path),
    }
    _append_checkpoint(output_dir / "checkpoint.jsonl", {
        "event": "recovery_before", "taskIndex": task["index"], "task": task["name"],
        "attempt": attempt, "evidence": evidence["beforeEvidence"]["path"],
        "evidenceSha256": evidence["beforeEvidence"]["sha256"], "completedAtUnix": time.time(),
    })
    for field, _probe in probes:
        evidence[field + "Before"] = before[field]
    if timezone_only and safe_to_restore:
        evidence["remediation"] = restore_official_datetime(project, manifest["target"], adb_path)
        for field, probe in probes:
            try:
                evidence[field] = probe()
            except Exception as exc:
                evidence[field] = {"qualified": False, "verified": False,
                                   "error": {"type": type(exc).__name__, "message": str(exc)}}
    reason = None
    if evidence["campaignIdentity"].get("verified") is not True:
        reason = "campaign_identity_changed_requires_new_campaign"
    elif not cleanup_known(record):
        reason = "cleanup_unknown_requires_coordinated_recovery"
    elif evidence.get("remediation", {}).get("outcome") == "failed":
        reason = "timezone_remediation_failed_requires_coordinated_recovery"
    elif "remediation" in evidence and any(
        evidence["coreServices"].get(field) != before["coreServices"].get(field)
        for field in ("bootId", "systemServerPids", "surfaceFlingerPids")
    ):
        reason = "core_process_changed_during_remediation_requires_coordinated_recovery"
    elif evidence["sessionAbsence"].get("verified") is not True or evidence["sessionAbsence"].get("sessionHashes") != []:
        reason = "session_absence_unproven_requires_coordinated_recovery"
    elif evidence["coreServices"].get("qualified") is not True:
        reason = "core_services_unavailable_requires_coordinated_recovery"
    elif evidence["attestation"].get("qualified") is not True:
        reason = "readiness_unavailable_requires_coordinated_recovery"
    evidence["continuationAllowed"] = reason is None
    evidence["pauseReason"] = reason
    evidence["recordedAtUnix"] = time.time()
    evidence["identitySha256"] = _sha256(evidence)
    path = recovery_dir / f"{_episode_slug(task)}-attempt-{attempt}.json"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    _append_checkpoint(output_dir / "checkpoint.jsonl", {
        "event": "recovery", "taskIndex": task["index"], "task": task["name"],
        "attempt": attempt, "evidence": str(path.relative_to(output_dir)),
        "evidenceSha256": _file_sha256(path),
        "continuationAllowed": evidence["continuationAllowed"], "pauseReason": reason,
        "completedAtUnix": time.time(),
    })
    return evidence


def _pause_campaign(output_dir: Path, manifest: dict[str, Any], reason: str) -> int:
    starts = [json.loads(line) for line in (output_dir / "checkpoint.jsonl").read_text().splitlines()]
    started = {event["taskIndex"] for event in starts if event.get("event") == "attempt_started"}
    _append_checkpoint(output_dir / "checkpoint.jsonl", {
        "event": "pause", "reason": reason,
        "unstartedTaskIndexes": [task["index"] for task in manifest["tasks"] if task["index"] not in started],
        "completedAtUnix": time.time(),
    })
    _write_summary(output_dir, manifest)
    return 2


def _reject_prior_execution(output_dir: Path) -> None:
    forbidden = ("checkpoint.jsonl", "run-metadata.json", "summary.json", "episodes", "recoveries")
    existing = [name for name in forbidden if (output_dir / name).exists()]
    if existing:
        raise ValueError(f"r12 campaign cannot resume or accept prior execution evidence: {existing}")


def run_campaign(args: argparse.Namespace) -> int:
    source_project = Path(args.project).resolve()
    manifest_path = Path(args.manifest).resolve()
    manifest = _load_manifest(manifest_path, source_project)
    if manifest["kind"] == "rehearsal":
        raise ValueError("non-scoring rehearsal manifests require the rehearse command, not run")
    output_dir = Path(args.output_dir).resolve()
    _reject_prior_execution(output_dir)
    rehearsal_source = Path(args.rehearsal_report).resolve()
    rehearsal_identity = validate_report(rehearsal_source, manifest, source_project)
    calibration_campaign_dir = None
    if manifest["kind"] == "full":
        calibration_arg = getattr(args, "calibration_campaign_dir", None)
        if calibration_arg is None:
            raise ValueError("full campaign run requires --calibration-campaign-dir")
        calibration_campaign_dir = Path(calibration_arg).resolve()
        if _calibration_gate(calibration_campaign_dir, source_project) != manifest["calibrationGate"]:
            raise ValueError("calibration evidence does not match the full campaign gate")
    readiness_source = Path(args.readiness_report).resolve()
    readiness_identity = _readiness_identity(readiness_source, manifest)
    readiness_document = json.loads(readiness_source.read_text())
    try:
        live_attestation = attest_device(readiness_document, str(Path(args.adb_path).resolve()))
    except Exception as exc:
        live_attestation = {"qualified": False, "mismatches": {
            "unavailable": {"type": type(exc).__name__, "message": str(exc)}
        }}
    try:
        initial_core_services = _core_service_health(readiness_document, str(Path(args.adb_path).resolve()))
    except Exception as exc:
        initial_core_services = {"qualified": False, "error": {
            "type": type(exc).__name__, "message": str(exc)
        }}
    output_dir.mkdir(parents=True, exist_ok=True)
    frozen_manifest = output_dir / "manifest.json"
    source_bytes = manifest_path.read_bytes()
    if frozen_manifest.exists() and frozen_manifest.read_bytes() != source_bytes:
        raise ValueError("output directory belongs to a different campaign manifest")
    if calibration_campaign_dir is not None:
        _copy_calibration_evidence(
            calibration_campaign_dir, output_dir / "calibration-evidence"
        )
    if not frozen_manifest.exists():
        frozen_manifest.write_bytes(source_bytes)
    rehearsal_destination = output_dir / "harness-rehearsal"
    if not rehearsal_destination.exists():
        shutil.copytree(rehearsal_source.parent, rehearsal_destination)
    if validate_report(rehearsal_destination / rehearsal_source.name, manifest, source_project) != rehearsal_identity:
        raise ValueError("copied rehearsal evidence differs from the frozen run gate")
    readiness_path = output_dir / "device-readiness.json"
    readiness_bytes = readiness_source.read_bytes()
    if readiness_path.exists() and readiness_path.read_bytes() != readiness_bytes:
        raise ValueError("output directory contains a different readiness report")
    if not readiness_path.exists():
        readiness_path.write_bytes(readiness_bytes)
    checkpoint = output_dir / "checkpoint.jsonl"
    checkpoint.touch(exist_ok=False)

    with tempfile.TemporaryDirectory(prefix=f"fsq-aw-{manifest['campaignId']}-") as temporary:
        agent_workspace = Path(temporary) / "agent-workspace"
        workspace_identity = _prepare_agent_workspace(source_project, agent_workspace)
        metadata_path = output_dir / "run-metadata.json"
        metadata = {
            "schemaVersion": 2,
            "campaignId": manifest["campaignId"],
            "manifestSha256": _sha256(manifest),
            "protocolIdentity": {
                "harnessRevision": HARNESS_REVISION,
                "sessionAccessibilityConfig": dict(SESSION_ACCESSIBILITY_CONFIG),
                "campaignContinuation": manifest["protocol"]["campaignContinuation"],
                "protocolSha256": _sha256(manifest["protocol"]),
            },
            "readinessIdentitySha256": readiness_identity,
            "liveTargetAttestation": live_attestation,
            "initialCoreServices": initial_core_services,
            "harnessRehearsalIdentitySha256": rehearsal_identity,
            "agentWorkspace": workspace_identity,
            "startedAtUnix": time.time(),
            "python": sys.version,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        if live_attestation.get("qualified") is not True:
            return _pause_campaign(output_dir, manifest, "initial_readiness_unavailable_requires_coordinated_recovery")
        if initial_core_services.get("qualified") is not True:
            return _pause_campaign(output_dir, manifest, "initial_core_services_unavailable_requires_coordinated_recovery")

        retry_limit = manifest["protocol"]["invalidRetryLimit"]
        for task in manifest["tasks"]:
            episode_dir = output_dir / "episodes" / _episode_slug(task)
            episode_dir.mkdir(parents=True, exist_ok=False)
            for attempt_number in range(1, retry_limit + 2):
                attempt_dir = episode_dir / f"attempt-{attempt_number}"
                result_path = attempt_dir / "result.json"
                binding = {
                    "taskIndex": task["index"], "task": task["name"], "attempt": attempt_number,
                    "manifestSha256": _sha256(manifest),
                    "readinessIdentitySha256": readiness_identity,
                    "taskSpecSha256": _sha256(task),
                    "result": str(result_path.relative_to(output_dir)),
                }
                _append_checkpoint(checkpoint, {
                    **binding, "event": "attempt_started", "startedAtUnix": time.time(),
                })
                record = _run_attempt(
                    manifest, task, attempt_dir, args, agent_workspace,
                    readiness_path, readiness_identity,
                )
                if not result_path.exists():
                    attempt_dir.mkdir(parents=True, exist_ok=True)
                    with result_path.open("x", encoding="utf-8") as stream:
                        stream.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
                classification = _classification(record, task, manifest["protocol"])
                _append_checkpoint(checkpoint, {
                    **binding, "event": "attempt_terminal", "classification": classification,
                    "officialReward": official_reward(record, manifest["protocol"]),
                    "resultSha256": _file_sha256(result_path), "completedAtUnix": time.time(),
                })
                agent = record.get("agent") if isinstance(record.get("agent"), dict) else {}
                abnormal = (
                    classification != "passed" or _cleanup_failed(record)
                    or record.get("error") is not None
                    or agent.get("termination", {}).get("reason") != "completed"
                )
                if abnormal:
                    recovery = recover_campaign_environment(
                        output_dir, manifest, task, attempt_number, record, result_path,
                        readiness_document, readiness_identity, str(Path(args.adb_path).resolve()),
                        source_project,
                    )
                    if not recovery["continuationAllowed"]:
                        return _pause_campaign(output_dir, manifest, recovery["pauseReason"])
                _write_summary(output_dir, manifest)
                if not (_retryable(record) and attempt_number <= retry_limit):
                    break
        _append_checkpoint(checkpoint, {"event": "finished", "completedAtUnix": time.time()})
        summary = _write_summary(output_dir, manifest)
    return 0 if summary["qualified"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare or run a frozen AndroidWorld campaign")
    subparsers = parser.add_subparsers(dest="command", required=True)
    assets = subparsers.add_parser("prepare-assets", help="explicitly acquire and verify pinned host assets")
    assets.add_argument("--project", default=".")
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--output", required=True)
    prepare.add_argument("--campaign-id", required=True)
    prepare.add_argument("--kind", choices=("calibration", "full", "rehearsal"), default="calibration")
    prepare.add_argument("--project", default=".")
    prepare.add_argument("--calibration-campaign-dir")
    prepare.add_argument("--inherit-manifest", help="copy exact specs from the authorized frozen r11 full manifest")
    prepare.add_argument("--environment-mode-report", help="bind fresh headless/backend evidence to the target identity")
    qualify = subparsers.add_parser("qualify")
    qualify.add_argument("--manifest", required=True)
    qualify.add_argument("--output", required=True)
    qualify.add_argument("--project", default=".")
    qualify.add_argument("--adb-path", default=str(DEFAULT_ADB))
    rehearse = subparsers.add_parser("rehearse", help="run all 116 real task lifecycles without an Agent or formal score")
    rehearse.add_argument("--manifest", required=True)
    rehearse.add_argument("--readiness-report", required=True)
    rehearse.add_argument("--output-dir", required=True)
    rehearse.add_argument("--project", default=".")
    rehearse.add_argument("--adb-path", default=str(DEFAULT_ADB))
    run = subparsers.add_parser("run")
    run.add_argument("--manifest", required=True)
    run.add_argument("--readiness-report", required=True)
    run.add_argument("--rehearsal-report", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--project", default=".")
    run.add_argument("--adb-path", default=str(DEFAULT_ADB))
    run.add_argument("--calibration-campaign-dir")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "prepare-assets":
        artifacts = prepare_artifacts(Path(args.project).resolve())
        print(json.dumps({"environmentArtifacts": artifacts, "hostMedia": probe_host_media()}, indent=2, sort_keys=True))
        return
    if args.command == "rehearse":
        raise SystemExit(run_rehearsal(args))
    if args.command == "prepare":
        write_manifest(
            Path(args.output),
            args.campaign_id,
            args.kind,
            Path(args.project),
            Path(args.calibration_campaign_dir).resolve()
            if args.calibration_campaign_dir
            else None,
            Path(args.inherit_manifest).resolve() if args.inherit_manifest else None,
            Path(args.environment_mode_report).resolve() if args.environment_mode_report else None,
        )
        return
    if args.command == "qualify":
        manifest_path = Path(args.manifest).resolve()
        _load_manifest(manifest_path, Path(args.project))
        report = prepare_device(manifest_path, Path(args.output), args.adb_path, Path(args.project))
        raise SystemExit(0 if report["qualified"] else 1)
    raise SystemExit(run_campaign(args))


if __name__ == "__main__":
    main()
