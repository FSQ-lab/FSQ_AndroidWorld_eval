"""Read frozen r12/r13 scores unchanged; r14 binds explicit coexistence evidence.

Revision 14 alone permits replacing the named accessibility-forwarder artifact;
all task specs, other environment assets and non-Harness runtime bytes stay frozen.
Request defaults never substitute for confirmed returned capability evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
from uuid import UUID

from fsq_androidworld_eval.action_budget import STEP_BUDGET_PROTOCOL
from fsq_androidworld_eval.appium_proxy import SESSION_ACCESSIBILITY_CONFIG, session_accessibility_audit_valid
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget
from fsq_androidworld_eval.omp_supervisor import termination_reason
from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission


TERMINATION_POLICY = {
    "completed": "evaluated_attempt",
    "step_budget": "evaluated_budget_limited_attempt",
    "business_deadline": "evaluated_budget_limited_attempt",
    "omp_deadline": "evaluated_budget_limited_attempt",
    "forced_termination": "invalid_agent",
    "unknown_termination": "invalid_agent",
}
SCORING_POLICY = {
    "officialReward": "preserve_evaluator_reward_independently_of_termination_and_cleanup",
    "missingEvaluator": "null",
    "validEpisodes": "evaluated_attempts_with_valid_protocol_and_agent_termination",
    "cleanupGate": "agent_proven_closed_or_pre_agent_not_created;_otherwise_halt",
}


def _uses_time_budget(record: dict[str, Any], protocol: dict[str, Any] | None = None) -> bool:
    return "timeBudget" in (protocol or record.get("protocol", {}))


def official_reward(record: dict[str, Any], protocol: dict[str, Any] | None = None) -> float | int | None:
    reward = record.get("officialReward")
    if type(reward) not in {int, float} or not math.isfinite(reward):
        return None
    evaluator = record.get("evaluator")
    if _uses_time_budget(record, protocol) and (
        not isinstance(evaluator, dict)
        or evaluator.get("implementation") != "android_world.task_eval.is_successful"
    ):
        return None
    return reward


def time_budget_valid(
    record: dict[str, Any], task: dict[str, Any], protocol: dict[str, Any]
) -> bool:
    maximum = task.get("maxSteps")
    if type(maximum) is not int or maximum <= 0:
        return False
    expected = episode_time_budget(maximum)
    observed = record.get("timeBudget")
    return (
        protocol.get("timeBudget") == TIME_BUDGET_PROTOCOL
        and protocol.get("terminationPolicy") == TERMINATION_POLICY
        and protocol.get("scoringPolicy") == SCORING_POLICY
        and record.get("protocol", {}).get("timeBudget") == TIME_BUDGET_PROTOCOL
        and task.get("timeBudget") == expected
        and isinstance(observed, dict)
        and all(observed.get(key) == value for key, value in expected.items())
    )


def _answer_submission_valid(record: dict[str, Any], protocol: dict[str, Any]) -> bool:
    """Revision 13 onward requires a bounded business receipt, never cleanup text."""
    if protocol.get("harnessRevision") not in {13, 14}:
        return "answerSubmission" not in protocol and "answerSubmission" not in record.get("protocol", {})
    agent = record.get("agent") or {}
    evidence = agent.get("answerSubmission")
    if not (
        protocol.get("answerSubmission") == ANSWER_SUBMISSION_PROTOCOL
        and record.get("protocol", {}).get("answerSubmission") == ANSWER_SUBMISSION_PROTOCOL
        and isinstance(evidence, dict) and evidence.get("protocol") == ANSWER_SUBMISSION_PROTOCOL
        and evidence.get("path") == "raw-private/business-submission.json"
        and isinstance(evidence.get("sha256"), str) and len(evidence["sha256"]) == 64
    ):
        return False
    def finite(value: Any) -> bool:
        return type(value) in {int, float} and math.isfinite(value) and value >= 0
    cutoff, business = evidence.get("cutoffSeconds"), evidence.get("businessDeadlineSeconds")
    if not finite(cutoff) or not finite(business) or cutoff > business:
        return False
    start, end = evidence.get("finalizationStartedAtSeconds"), evidence.get("finalizationDeadlineSeconds")
    if (start is None) != (end is None):
        return False
    if start is not None and not (
        finite(start) and finite(end) and start <= end
        and math.isclose(end, min(start + ANSWER_SUBMISSION_PROTOCOL["maximumFinalizationSeconds"], business), abs_tol=1e-6)
        and cutoff <= end
    ):
        return False
    cleanup = evidence.get("cleanupRequestedAtSeconds")
    if cleanup is not None and (not finite(cleanup) or cutoff > cleanup):
        return False
    receipt = evidence.get("receipt")
    if receipt is None:
        return record.get("agentAnswer", {}).get("reason") == "no_submission"
    if not isinstance(receipt, dict):
        return False
    received = receipt.get("receivedAtSeconds")
    phase = receipt.get("phase")
    return (
        type(receipt.get("eventSequence")) is int and receipt["eventSequence"] > 0
        and finite(received) and received <= cutoff
        and (phase == "business" and (start is None or received < start)
             or phase == "finalization" and start is not None and start <= received <= end)
    )


def _submission_artifacts_valid(record: dict[str, Any], result_path: Path) -> bool:
    """Bind the private typed submission to its actual business final event."""
    try:
        evidence = record["agent"]["answerSubmission"]
        raw_path = result_path.parent / "raw-private" / "business-submission.json"
        payload = raw_path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != evidence["sha256"]:
            return False
        archived = json.loads(payload)
        report = parse_submission(archived["rawText"])
        if report != archived:
            return False
        expected = {
            "validContract": report["validContract"], "reason": report["reason"],
            "taskOutcomeType": report["taskOutcomeType"], "sha256": report["sha256"],
            "rawSubmission": {"path": evidence["path"], "sha256": evidence["sha256"]},
        }
        if record.get("agentAnswer") != expected:
            return False
        receipt = evidence.get("receipt")
        if receipt is None:
            return report["rawText"] is None
        raw_events = result_path.parent / "raw-private" / "agent-events.jsonl"
        raw_bytes = raw_events.read_bytes()
        if hashlib.sha256(raw_bytes).hexdigest() != record["agent"]["rawEventsSha256"]:
            return False
        events = [json.loads(line) for line in raw_bytes.splitlines() if line.strip()]
        event = [event for event in events if isinstance(event, dict)][receipt["eventSequence"] - 1]
        message = event.get("message", {})
        text = "".join(item["text"] for item in message.get("content", [])
                       if isinstance(item, dict) and isinstance(item.get("text"), str))
        return (event.get("type") == "message_end" and message.get("role") == "assistant"
                and message.get("stopReason") == "stop" and text == report["rawText"])
    except (OSError, ValueError, TypeError, KeyError, IndexError):
        return False


def _session_accessibility_valid(record: dict[str, Any], protocol: dict[str, Any]) -> bool:
    if protocol.get("harnessRevision") != 14:
        return True
    return (
        protocol.get("sessionAccessibilityConfig") == SESSION_ACCESSIBILITY_CONFIG
        and record.get("protocol", {}).get("sessionAccessibilityConfig") == SESSION_ACCESSIBILITY_CONFIG
        and session_accessibility_audit_valid(record.get("appiumSessionAudit"), record.get("target", {}).get("serial"))
    )


def _inherited_environment_valid(source: Any, observed: Any) -> bool:
    """Only the explicitly named r14 helper pin may change, never app assets."""
    if not isinstance(source, dict) or not isinstance(observed, dict):
        return False
    if {key: value for key, value in source.items() if key != "artifacts"} != {
        key: value for key, value in observed.items() if key != "artifacts"
    }:
        return False
    old, new = source.get("artifacts"), observed.get("artifacts")
    if not isinstance(old, list) or not isinstance(new, list) or len(old) != len(new):
        return False
    helper_count = 0
    for before, after in zip(old, new):
        if not isinstance(before, dict) or not isinstance(after, dict):
            return False
        if before.get("name") in {SESSION_ACCESSIBILITY_CONFIG["inheritedForwarderArtifactName"],
                                  SESSION_ACCESSIBILITY_CONFIG["forwarderArtifactName"]}:
            helper_count += 1
            if after.get("name") != SESSION_ACCESSIBILITY_CONFIG["forwarderArtifactName"]:
                return False
            mutable = {"name", "url", "sha256", "sizeBytes"}
            if {key: value for key, value in before.items() if key not in mutable} != {
                key: value for key, value in after.items() if key not in mutable
            }:
                return False
            digest, size = after.get("sha256"), after.get("sizeBytes")
            if (not isinstance(digest, str) or len(digest) != 64
                    or any(char not in "0123456789abcdef" for char in digest)
                    or type(size) is not int or size <= 0 or not isinstance(after.get("url"), str)):
                return False
        elif before != after:
            return False
    return helper_count == 1


def record_classification(
    record: dict[str, Any],
    task: dict[str, Any] | None = None,
    protocol: dict[str, Any] | None = None,
) -> str:
    reward = official_reward(record, protocol)
    if record.get("invalidReason"):
        return record["invalidReason"]
    if record.get("error") is not None:
        return "invalid_infrastructure"
    if reward is None:
        return "invalid_evaluator"
    if protocol is not None and not _session_accessibility_valid(record, protocol):
        return "invalid_protocol"
    if _uses_time_budget(record, protocol):
        if task is not None and protocol is not None and not time_budget_valid(record, task, protocol):
            return "invalid_protocol"
        if protocol is not None and not _answer_submission_valid(record, protocol):
            return "invalid_protocol"
        agent = record.get("agent")
        termination = agent.get("termination") if isinstance(agent, dict) else None
        reason = termination.get("reason") if isinstance(termination, dict) else None
        if (
            reason not in {"completed", "step_budget", "business_deadline", "omp_deadline"}
            or agent.get("agentCompleted") is not (reason == "completed")
        ):
            return "invalid_agent"
        if reason == "step_budget" and termination_reason(
            agent.get("normalized") or {},
            business_expired=termination.get("businessDeadlineReached") is True,
            forced=termination.get("outerTermination") is True,
            budget_closure_reason=termination.get("actionBudgetClosureReason"),
        ) != "step_budget":
            return "invalid_agent"
    if protocol is not None and "stepBudget" in protocol and (
        protocol["stepBudget"] != STEP_BUDGET_PROTOCOL
        or task is None
        or not step_budget_valid(record, task)
    ):
        return "invalid_protocol"
    return "passed" if reward > 0.5 else "failed"


def step_budget_valid(record: dict[str, Any], task: dict[str, Any]) -> bool:
    """Check declared reference-step provenance without changing official reward."""
    budget = record.get("stepBudget")
    maximum = task.get("maxSteps")
    complexity = task.get("complexity")
    if (
        not isinstance(budget, dict)
        or type(maximum) is not int
        or maximum <= 0
        or type(complexity) not in {int, float}
        or not math.isfinite(complexity)
        or maximum != int(10 * complexity)
        or budget.get("protocol") != STEP_BUDGET_PROTOCOL
        or budget.get("maxSteps") != maximum
        or record.get("task", {}).get("complexity") != complexity
    ):
        return False
    steps = budget.get("referenceStepsExecuted")
    actions = budget.get("executedActionCount")
    rejected = budget.get("rejectedActionCount")
    entries = budget.get("actions")
    done = budget.get("agentIndicatedDone")
    exhausted = budget.get("exhausted")
    agent = record.get("agent")
    termination = agent.get("termination", {}) if isinstance(agent, dict) else {}
    deadline_limited = (
        record.get("protocol", {}).get("timeBudget") == TIME_BUDGET_PROTOCOL
        and termination.get("reason") in {"business_deadline", "omp_deadline"}
    )
    if termination.get("reason") == "step_budget" and not (
        steps == maximum and exhausted is True and done is False
        and budget.get("closureReason") == "step_budget"
    ):
        return False
    return (
        type(steps) is int
        and type(actions) is int
        and type(rejected) is int
        and 0 <= actions <= steps <= maximum
        and (steps > 0 or deadline_limited)
        and rejected >= 0
        and isinstance(entries, list)
        and len(entries) == actions
        and type(done) is bool
        and type(exhausted) is bool
        and ((exhausted is not done) or (deadline_limited and not done and not exhausted))
        and exhausted is (steps == maximum and not done)
    )

def _cleanup_failed(record: dict[str, Any]) -> bool:
    cleanup = record.get("cleanup")
    if not isinstance(cleanup, dict):
        return True
    session = cleanup.get("agentSession")
    if not isinstance(session, dict):
        return True
    task_teardown = cleanup.get("taskTearDown")
    environment = cleanup.get("environment")
    if _uses_time_budget(record) and session.get("status") == "closed":
        agent = record.get("agent")
        normalized = agent.get("normalized", {}) if isinstance(agent, dict) else {}
        calls = normalized.get("toolCalls", [])
        proofs = [call.get("sessionCleanup") for call in calls if isinstance(call, dict) and "sessionCleanup" in call] if isinstance(calls, list) else []
        audit = record.get("appiumSessionAudit", {})
        session_hash = session.get("sessionIdSha256")
        if not (
            isinstance(session_hash, str)
            and len(proofs) == 1
            and isinstance(proofs[0], dict)
            and proofs[0].get("quitReturned") is True
            and proofs[0].get("sessionIdSha256") == session_hash
            and audit.get("createdSessionCount") == 1
            and audit.get("deletedSessionCount") == 1
            and audit.get("createdSessionHashes") == [session_hash]
            and audit.get("deletedSessionHashes") == [session_hash]
            and audit.get("errors") == []
        ):
            return True
    if record.get("error") is None:
        return (
            session.get("status") != "closed"
            or task_teardown != "completed"
            or environment != "closed"
        )
    if _uses_time_budget(record) and session.get("status") == "not_created" and record.get("agent") is not None:
        return True
    return session.get("status") not in {"closed", "not_created"} or task_teardown not in {
        "completed",
        "not_applicable",
    } or environment not in {
        "closed",
        "not_created",
    }


def _calibration_gate_satisfied(manifest: dict[str, Any], campaign_dir: Path) -> bool:
    if manifest.get("kind") != "full":
        return manifest.get("kind") in {None, "calibration"}
    evidence_dir = campaign_dir / "calibration-evidence"
    manifest_path = evidence_dir / "manifest.json"
    try:
        calibration_manifest = json.loads(manifest_path.read_text())
        if (
            calibration_manifest.get("kind") != "calibration"
            or len(calibration_manifest.get("tasks", [])) != 12
            or calibration_manifest.get("protocol", {}) != manifest.get("protocol", {})
        ):
            return False
        recalculation = recalculate(manifest_path, evidence_dir)
        if recalculation.get("qualified") is not True or recalculation.get("matchesSummary") is not True:
            return False
        summary = json.loads((evidence_dir / "summary.json").read_text())
        payload = {key: value for key, value in summary.items() if key != "identitySha256"}
        identity = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if summary.get("identitySha256") != identity:
            return False
        paths = [manifest_path, evidence_dir / "summary.json"]
        for task in calibration_manifest["tasks"]:
            result_path = _latest_result(evidence_dir, task)
            if result_path is None:
                return False
            paths.append(result_path)
        if "campaignContinuation" in calibration_manifest.get("protocol", {}):
            paths.extend(evidence_dir / name for name in ("checkpoint.jsonl", "run-metadata.json", "device-readiness.json"))
            paths.extend((evidence_dir / "recoveries").glob("*.json"))
            paths.extend((evidence_dir / "episodes").glob("*/attempt-*/result.json"))
            if calibration_manifest.get("protocol", {}).get("harnessRevision") in {13, 14}:
                for name in ("business-submission.json", "agent-events.jsonl"):
                    paths.extend((evidence_dir / "episodes").glob(f"*/attempt-*/raw-private/{name}"))
            paths = list(set(paths))
        rows = [
            {
                "path": str(path.relative_to(evidence_dir)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(paths)
        ]
        evidence_identity = hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    observed_gate = {
        "campaignId": calibration_manifest["campaignId"],
        "manifestSha256": hashlib.sha256(
            json.dumps(calibration_manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "summaryIdentitySha256": identity,
        "evidenceSha256": evidence_identity,
    }
    return observed_gate == manifest.get("calibrationGate")

def _latest_result(campaign_dir: Path, task: dict[str, Any]) -> Path | None:
    episode_dir = campaign_dir / "episodes" / f"{task['index']:03d}-{task['name']}"
    results = sorted(episode_dir.glob("attempt-*/result.json"))
    return results[-1] if results else None


CONTINUATION_PROTOCOL = {"version": 2, "policy": "full_coverage_after_verified_recovery"}
INHERITED_MANIFEST_SHA256 = "2345c5af27c75f7c1a7c6e263b77963f426864a6486a51e845468430a50ea856"


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _attestation_valid(value: Any) -> bool:
    return (
        isinstance(value, dict) and value.get("qualified") is True and value.get("mismatches") == {}
        and value.get("identitySha256") == _canonical_sha256({key: item for key, item in value.items() if key != "identitySha256"})
    )


def _timezone_drift_only(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("qualified") is not False:
        return False
    mismatches = value.get("mismatches")
    if not isinstance(mismatches, dict) or set(mismatches) != {"timezone"}:
        return False
    drift = mismatches["timezone"]
    return (
        isinstance(drift, dict) and set(drift) == {"expected", "observed"}
        and drift.get("expected") == "UTC"
        and isinstance(drift.get("observed"), str) and bool(drift["observed"])
        and drift["observed"] != "UTC"
        and isinstance(value.get("device"), dict) and value["device"].get("timezone") == drift["observed"]
        and value.get("identitySha256") == _canonical_sha256({
            key: item for key, item in value.items() if key != "identitySha256"
        })
    )


def _ordered_times(*values: Any) -> bool:
    return all(type(value) in {int, float} and math.isfinite(value) for value in values) and all(
        left <= right for left, right in zip(values, values[1:])
    )


def _core_services_valid(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("adbState") != "device" or value.get("bootCompleted") != "1":
        return False
    if not all(value.get(field) is True for field in (
        "activityService", "packageService", "settingsService", "windowService",
        "appiumReady", "grpcReady", "qualified",
    )):
        return False
    for field in ("systemServerPids", "surfaceFlingerPids"):
        pids = value.get(field)
        if not isinstance(pids, list) or not pids or not all(
            isinstance(pid, str) and pid.isascii() and pid.isdecimal() and int(pid) > 0 for pid in pids
        ):
            return False
    boot_id = value.get("bootId")
    if not isinstance(boot_id, str):
        return False
    try:
        return str(UUID(boot_id)) == boot_id.lower()
    except ValueError:
        return False


def _known_recovery_cleanup(record: dict[str, Any], *, allow_agent_proof: bool = False) -> bool:
    """Recovery permits continuation, never substitutes for agent cleanup proof."""
    cleanup = record.get("cleanup")
    if not isinstance(cleanup, dict):
        return False
    session = cleanup.get("agentSession")
    if not isinstance(session, dict):
        return False
    if cleanup.get("taskTearDown") not in {"completed", "not_applicable"} or cleanup.get("environment") not in {"closed", "not_created"}:
        return False
    if session.get("status") == "not_created":
        if record.get("agent") is None:
            return True
        agent = record.get("agent")
        audit = record.get("appiumSessionAudit")
        return (
            allow_agent_proof and isinstance(agent, dict) and agent.get("processExited") is True
            and type(agent.get("exitCode")) is int
            and session.get("attribution") == "none" and session.get("verificationStatus") == "absent"
            and isinstance(audit, dict) and audit.get("errors") == []
            and all(type(audit.get(key)) is int and audit[key] == 0 for key in (
                "createdSessionCount", "deletedSessionCount", "activeSessionCount",
                "pendingRequestCount", "pendingCreateCount", "unknownCreationOutcomeCount",
            ))
            and audit.get("createdSessionHashes") == [] and audit.get("deletedSessionHashes") == []
        )
    if session.get("status") == "closed":
        return session.get("verificationStatus") == "absent" or (
            allow_agent_proof and isinstance(record.get("timeBudget"), dict) and not _cleanup_failed(record)
        )
    sessions = session.get("sessions")
    return (
        session.get("status") == "harness_reclaimed"
        and session.get("verificationStatus") == "absent"
        and session.get("attribution") == "harness"
        and all(type(session.get(key)) is int and session[key] == 0 for key in (
            "pendingRequestCount", "unknownCreationOutcomeCount", "activeSessionCount",
        ))
        and isinstance(sessions, list) and bool(sessions)
        and all(isinstance(item, dict) and item.get("quitReturned") is True
                and item.get("absentVerified") is True for item in sessions)
    )


def _continuation_needs_recovery(record: dict[str, Any], task: dict[str, Any], protocol: dict[str, Any]) -> bool:
    return (
        _cleanup_failed(record) or not _known_recovery_cleanup(
            record, allow_agent_proof=protocol.get("campaignContinuation", {}).get("version") == 2
        )
        or record_classification(record, task, protocol) != "passed"
        or record.get("error") is not None
        or (record.get("agent") or {}).get("termination", {}).get("reason") != "completed"
    )


def _result_provenance_valid(record: dict[str, Any], task: dict[str, Any], manifest: dict[str, Any], readiness_identity: Any) -> bool:
    protocol = manifest.get("protocol", {})
    observed = record.get("protocol") or {}
    recorded_task = record.get("task") or {}
    if not (
        record.get("schemaVersion") == 3
        and record.get("androidWorld", {}).get("revision") == protocol.get("androidWorldRevision")
        and record.get("amkernel", {}).get("version") == protocol.get("runtimeIdentity", {}).get("amkernelVersion")
        and record.get("target", {}).get("serial") == manifest.get("target", {}).get("serial")
        and recorded_task.get("name") == task.get("name")
        and observed.get("readinessIdentitySha256") == readiness_identity
        and all(observed.get(key) == protocol.get(key) for key in (
            "harnessRevision", "promptTemplateSha256", "mcpRequestTimeoutMs",
            "sessionCreationTimeoutSeconds", "pythonExecCallAdvisory", "stepBudget", "timeBudget",
        ))
        and (protocol.get("harnessRevision") != 14
             or observed.get("sessionAccessibilityConfig") == protocol.get("sessionAccessibilityConfig") == SESSION_ACCESSIBILITY_CONFIG)
    ):
        return False
    # A pre-agent initialization failure may have only the original name/seed.
    if record.get("agent") is None and record.get("error") is not None:
        return recorded_task.get("seed", task.get("instanceSeed")) == task.get("instanceSeed")
    agent = record.get("agent") or {}
    normalized = agent.get("normalized") or {}
    calls = normalized.get("toolCalls")
    model = protocol.get("model", "").split("/", 1)
    if len(model) != 2 or not isinstance(calls, list) or not all(isinstance(call, dict) for call in calls):
        return False
    allowed = protocol.get("agentToolPolicy", {})
    python_calls = sum(call.get("tool") == "write" and call.get("target") == "xd://mcp__amkernel_python_exec" for call in calls)
    budget = record.get("budget") or {}
    return (
        recorded_task.get("params") == task.get("params")
        and recorded_task.get("paramsSha256") == task.get("paramsSha256")
        and recorded_task.get("complexity") == task.get("complexity")
        and observed.get("environmentArtifacts") == protocol.get("environmentArtifacts")
        and normalized.get("provider") == model[0] and normalized.get("model") == model[1]
        and normalized.get("parseErrors") == 0
        and all(
            call.get("tool") in allowed.get("tools", [])
            and isinstance(call.get("target"), str)
            and (call["target"] in allowed.get("allowedTargets", []) or any(
                target.startswith("skill://") and call["target"].startswith(target + "/")
                for target in allowed.get("allowedTargets", [])
            ))
            and (call["tool"] != "write" or call["target"] in {"xd://mcp__amkernel_python_exec", "xd://report_issue"})
            for call in calls
        )
        and python_calls > 0 and budget.get("pythonExecCalls") == python_calls
        and budget.get("advisory") == protocol.get("pythonExecCallAdvisory")
        and budget.get("affectsOfficialReward") is False
    )


def continuation_audit(manifest: dict[str, Any], campaign_dir: Path) -> dict[str, Any]:
    """Read-only r12 provenance audit; an artifact row alone never proves a start.

    Recovery references retain the original result hash, classification and cleanup.
    A later clean device cannot repair a missing agent-close proof or null reward.
    Version 2 additionally binds a durable pre-action snapshot and permits only
    the official public datetime setup for sole UTC timezone drift, with verified
    prerequisites, strict controller close and ordered fresh post-action probes.
    Legacy version 1 keeps its original identity and evidence semantics.
    """
    protocol = manifest.get("protocol", {})
    if "campaignContinuation" not in protocol and protocol.get("harnessRevision") not in {12, 13, 14}:
        return {}
    errors: list[str] = []
    tasks = manifest.get("tasks", [])
    by_index = {task["index"]: task for task in tasks}
    manifest_identity = _canonical_sha256(manifest)

    def problem(message: str) -> None:
        errors.append(message)

    def load(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text())
            if not isinstance(value, dict):
                raise ValueError("expected object")
            return value
        except (OSError, ValueError):
            problem(f"unreadable_artifact:{path.name}")
            return {}

    def local_path(value: Any) -> Path | None:
        if not isinstance(value, str) or Path(value).is_absolute():
            problem("invalid_evidence_path")
            return None
        path = campaign_dir / value
        if not path.resolve().is_relative_to(campaign_dir.resolve()):
            problem("invalid_evidence_path")
            return None
        return path

    continuation_version = (protocol.get("campaignContinuation") or {}).get("version")
    expected_continuation = {"version": continuation_version, "policy": CONTINUATION_PROTOCOL["policy"]}
    if (type(continuation_version) is not int or continuation_version not in {1, 2}
            or protocol.get("campaignContinuation") != expected_continuation or protocol.get("harnessRevision") not in {12, 13, 14}):
        problem("continuation_protocol_mismatch")
    if protocol.get("harnessRevision") in {13, 14}:
        if continuation_version != 2 or protocol.get("answerSubmission") != ANSWER_SUBMISSION_PROTOCOL:
            problem("answer_submission_protocol_mismatch")
    elif "answerSubmission" in protocol:
        problem("answer_submission_protocol_mismatch")
    if protocol.get("harnessRevision") == 14 and protocol.get("sessionAccessibilityConfig") != SESSION_ACCESSIBILITY_CONFIG:
        problem("session_accessibility_config_mismatch")
    inherited = manifest.get("inheritedManifest") or {}
    source_path = Path(inherited.get("path", ""))
    source = load(source_path)
    try:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    except OSError:
        source_hash = None
    source_tasks = source.get("tasks", [])
    if not (
        source_hash == inherited.get("sha256") == INHERITED_MANIFEST_SHA256
        and inherited.get("tasksSha256") == _canonical_sha256(source_tasks)
        and inherited.get("campaignId") == source.get("campaignId")
        and inherited.get("taskCount") == len(source_tasks) == 116
        and source.get("schemaVersion") == 2
        and source.get("kind") == "full" and source.get("protocol", {}).get("harnessRevision") == 11
    ):
        problem("inherited_manifest_identity_mismatch")
    frozen = {task.get("name"): task for task in source_tasks}
    source_equality = True
    for index, task in enumerate(tasks):
        original = frozen.get(task.get("name"))
        expected = {**original, "index": index} if original is not None else None
        if type(task.get("index")) is not int or task != expected:
            source_equality = False
            problem(f"frozen_task_spec_mismatch:{index}")
    if len({task.get("name") for task in tasks}) != len(tasks):
        problem("duplicate_frozen_task")
    if manifest.get("kind") == "full" and tasks != source_tasks:
        source_equality = False
        problem("full_source_task_order_mismatch")
    if manifest.get("kind") not in {"full", "calibration"}:
        problem("invalid_continuation_campaign_kind")
    if manifest.get("kind") == "calibration" and len(tasks) != 12:
        problem("calibration_task_count_mismatch")
    permitted_changes = {"harnessRevision", "runtimeIdentity"}
    if protocol.get("harnessRevision") in {13, 14}:
        permitted_changes.add("promptTemplateSha256")
    if protocol.get("harnessRevision") == 14:
        permitted_changes.add("environmentArtifacts")
        if not _inherited_environment_valid(source.get("protocol", {}).get("environmentArtifacts"), protocol.get("environmentArtifacts")):
            problem("frozen_environment_artifacts_mismatch")
    for key, value in source.get("protocol", {}).items():
        if key not in permitted_changes and protocol.get(key) != value:
            problem(f"frozen_protocol_mismatch:{key}")
    frozen_runtime = {key: value for key, value in source.get("protocol", {}).get("runtimeIdentity", {}).items() if key != "harnessSourceSha256"}
    observed_runtime = {key: value for key, value in protocol.get("runtimeIdentity", {}).items() if key != "harnessSourceSha256"}
    if frozen_runtime != observed_runtime:
        problem("frozen_runtime_identity_mismatch")
    target = manifest.get("target", {})
    if {key: value for key, value in target.items() if key != "environmentMode"} != source.get("target"):
        problem("frozen_target_identity_mismatch")
    if "environmentMode" in target:
        mode = target["environmentMode"]
        mode_path = Path(mode.get("path", "")) if isinstance(mode, dict) else Path()
        mode_evidence = load(mode_path)
        try:
            mode_hash = hashlib.sha256(mode_path.read_bytes()).hexdigest()
        except OSError:
            mode_hash = None
        if not (isinstance(mode, dict) and mode_path.is_absolute()
                and mode_hash is not None and mode_hash == mode.get("sha256")
                and mode_evidence == mode.get("evidence")
                and mode_evidence.get("avd") == target.get("avd")
                and mode_evidence.get("serial") == target.get("serial")):
            problem("environment_mode_provenance_mismatch")
    metadata = load(campaign_dir / "run-metadata.json")
    readiness = load(campaign_dir / "device-readiness.json")
    readiness_identity = readiness.get("identitySha256")
    if not (
        metadata.get("manifestSha256") == manifest_identity
        and metadata.get("campaignId") == manifest.get("campaignId")
        and isinstance(readiness_identity, str)
        and metadata.get("readinessIdentitySha256") == readiness_identity
        and readiness_identity == _canonical_sha256({key: value for key, value in readiness.items() if key != "identitySha256"})
        and readiness.get("manifestSha256") == manifest_identity
        and readiness.get("target") == target
        and readiness.get("qualified") is True
        and readiness.get("environmentClose") == "closed"
        and readiness.get("environmentArtifacts") == protocol.get("environmentArtifacts")
        and (protocol.get("harnessRevision") != 14
             or readiness.get("sessionAccessibilityConfig") == protocol.get("sessionAccessibilityConfig") == SESSION_ACCESSIBILITY_CONFIG)
        and _attestation_valid(metadata.get("liveTargetAttestation"))
    ):
        problem("run_readiness_provenance_mismatch")
    initial_core_services = metadata.get("initialCoreServices")
    previous_core_services = initial_core_services if isinstance(initial_core_services, dict) else {}
    if not _core_services_valid(initial_core_services):
        problem("initial_core_services_unusable")
    starts: dict[tuple[int, int], dict[str, Any]] = {}
    terminals: dict[tuple[int, int], dict[str, Any]] = {}
    records: dict[tuple[int, int], dict[str, Any]] = {}
    recoveries: list[dict[str, Any]] = []
    terminal_rows: list[dict[str, Any]] = []
    recovery_befores: dict[tuple[int, int], tuple[dict[str, Any], dict[str, Any]]] = {}
    active: tuple[int, int] | None = None
    previous: tuple[int, int] | None = None
    recovered: set[tuple[int, int]] = set()
    paused = False
    pause_reason = None
    finished = False
    last_time = metadata.get("startedAtUnix", 0)
    if type(last_time) not in {int, float} or not math.isfinite(last_time):
        problem("invalid_run_start_time")
        last_time = 0
    try:
        checkpoint_bytes = (campaign_dir / "checkpoint.jsonl").read_bytes()
    except OSError:
        checkpoint_bytes = b""
        problem("missing_checkpoint")
    prefix = hashlib.sha256()
    start_event_count = 0
    terminal_event_count = 0
    for sequence, line in enumerate(checkpoint_bytes.splitlines(keepends=True), 1):
        prefix.update(line)
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("expected event object")
        except ValueError:
            problem(f"malformed_checkpoint_event:{sequence}")
            continue
        kind = event.get("event")
        start_event_count += kind == "attempt_started"
        terminal_event_count += kind == "attempt_terminal"
        if paused or finished:
            problem(f"event_after_stop:{sequence}")
        if kind in {"attempt_started", "attempt_terminal", "recovery", "recovery_before"}:
            index, attempt = event.get("taskIndex"), event.get("attempt")
            if type(index) is not int or index not in by_index or type(attempt) is not int or attempt < 1:
                problem(f"invalid_attempt_identity:{sequence}")
                continue
            key = (index, attempt)
            task = by_index[index]
            expected_result = f"episodes/{index:03d}-{task['name']}/attempt-{attempt}/result.json"
            if event.get("task") != task["name"]:
                problem(f"checkpoint_task_mismatch:{sequence}")
            if kind not in {"recovery", "recovery_before"} and any(event.get(field) != value for field, value in {
                "manifestSha256": manifest_identity, "readinessIdentitySha256": readiness_identity,
                "taskSpecSha256": _canonical_sha256(task), "result": expected_result,
            }.items()):
                problem(f"checkpoint_binding_mismatch:{sequence}")
        if kind == "attempt_started":
            if key in starts or active is not None:
                problem(f"duplicate_or_overlapping_start:{sequence}")
            expected_index = previous[0] + 1 if previous else 0
            if index == (previous[0] if previous else -1):
                prior = records.get(previous, {})
                if not (attempt == previous[1] + 1 <= protocol.get("invalidRetryLimit", 0) + 1
                        and record_classification(prior) == "invalid_infrastructure" and prior.get("agent") is None):
                    problem(f"nonretryable_replay:{sequence}")
            elif index != expected_index or attempt != 1:
                problem(f"unordered_start:{sequence}")
            if previous is not None:
                prior = records.get(previous, {})
                needs_recovery = _continuation_needs_recovery(prior, by_index[previous[0]], protocol)
                if needs_recovery and previous not in recovered:
                    problem(f"missing_verified_recovery:{sequence}")
            starts.setdefault(key, event)
            active = key
        elif kind == "attempt_terminal":
            if key not in starts or key in terminals or active != key:
                problem(f"unmatched_or_duplicate_terminal:{sequence}")
            result_path = local_path(event.get("result"))
            record = load(result_path) if result_path is not None else {}
            try:
                digest = hashlib.sha256(result_path.read_bytes()).hexdigest() if result_path is not None else None
            except OSError:
                digest = None
            if digest is None or digest != event.get("resultSha256"):
                problem(f"terminal_result_hash_mismatch:{sequence}")
            classification = record_classification(record, task, protocol)
            reward = official_reward(record, protocol)
            if event.get("classification") != classification or "officialReward" not in event or event.get("officialReward") != reward:
                problem(f"terminal_result_semantics_mismatch:{sequence}")
            if not _result_provenance_valid(record, task, manifest, readiness_identity):
                problem(f"result_provenance_mismatch:{sequence}")
            if (protocol.get("harnessRevision") in {13, 14} and record.get("agent") is not None
                    and (result_path is None or not _submission_artifacts_valid(record, result_path))):
                problem(f"answer_submission_artifact_mismatch:{sequence}")
            if record.get("agent") is not None:
                bounds = [starts.get(key, {}).get("startedAtUnix"), record.get("startedAtUnix"),
                          record.get("completedAtUnix"), event.get("completedAtUnix")]
                if not all(type(value) in {int, float} and math.isfinite(value) for value in bounds) or bounds != sorted(bounds):
                    problem(f"result_timestamp_provenance_mismatch:{sequence}")
            if key not in terminals:
                terminals[key] = event
                records[key] = record
                terminal_rows.append({"taskIndex": index, "attempt": attempt, "classification": classification,
                                      "officialReward": reward, "cleanupFailure": _cleanup_failed(record),
                                      "checkpointClassification": event.get("classification"),
                                      "checkpointOfficialReward": event.get("officialReward"),
                                      "result": event.get("result"), "resultSha256": digest})
            active = None
            previous = key
        elif kind == "recovery_before":
            evidence_path = local_path(event.get("evidence"))
            before = load(evidence_path) if evidence_path is not None else {}
            try:
                digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest() if evidence_path is not None else None
            except OSError:
                digest = None
            prior = records.get(key, {})
            terminal = terminals.get(key, {})
            before_bound = (
                continuation_version == 2 and key == previous and key in terminals and active is None
                and key not in recovery_befores and key not in recovered
                and digest is not None and digest == event.get("evidenceSha256")
                and before.get("identitySha256") == _canonical_sha256({
                    field: value for field, value in before.items() if field != "identitySha256"
                })
                and before.get("schemaVersion") == 2
                and all(before.get(field) == value for field, value in {
                    "manifestSha256": manifest_identity, "readinessIdentitySha256": readiness_identity,
                    "taskIndex": index, "task": task["name"], "attempt": attempt,
                    "taskSpecSha256": _canonical_sha256(task),
                    "result": terminal.get("result"), "resultSha256": terminal.get("resultSha256"),
                    "originalClassification": record_classification(prior, task, protocol),
                    "originalCleanup": prior.get("cleanup"),
                }.items())
                and _ordered_times(terminal.get("completedAtUnix"), before.get("recordedAtUnix"), event.get("completedAtUnix"))
            )
            if not before_bound:
                problem(f"recovery_before_boundary_mismatch:{sequence}")
            else:
                recovery_befores[key] = (event, before)
        elif kind == "recovery":
            evidence_path = local_path(event.get("evidence"))
            evidence = load(evidence_path) if evidence_path is not None else {}
            try:
                digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest() if evidence_path is not None else None
            except OSError:
                digest = None
            prior = records.get(key, {})
            terminal = terminals.get(key, {})
            identity = _canonical_sha256({field: value for field, value in evidence.items() if field != "identitySha256"})
            bound = (
                key == previous and key in terminals and active is None and key not in {(item["taskIndex"], item["attempt"]) for item in recoveries}
                and digest is not None and digest == event.get("evidenceSha256")
                and evidence.get("identitySha256") == identity
                and all(evidence.get(field) == value for field, value in {
                    "manifestSha256": manifest_identity, "readinessIdentitySha256": readiness_identity,
                    "taskIndex": index, "task": task["name"], "attempt": attempt,
                    "result": terminal.get("result"), "resultSha256": terminal.get("resultSha256"),
                    "originalClassification": record_classification(prior, task, protocol),
                    "originalCleanup": prior.get("cleanup"),
                }.items())
                and event.get("continuationAllowed") is evidence.get("continuationAllowed")
                and event.get("pauseReason") == evidence.get("pauseReason")
            )
            if not bound:
                problem(f"recovery_boundary_mismatch:{sequence}")
            services = evidence.get("coreServices") if isinstance(evidence.get("coreServices"), dict) else {}
            expected_campaign_identity = {"verified": True, "manifestSha256": manifest_identity}
            if continuation_version == 2:
                expected_campaign_identity["readinessIdentitySha256"] = readiness_identity
            allowed = (
                bound and _attestation_valid(evidence.get("attestation"))
                and evidence.get("campaignIdentity") == expected_campaign_identity
                and evidence.get("sessionAbsence") == {"sessionHashes": [], "verified": True}
                and _core_services_valid(services)
                and _known_recovery_cleanup(prior, allow_agent_proof=continuation_version == 2)
            )
            if continuation_version == 2:
                before_event, before = recovery_befores.get(key, ({}, {}))
                snapshot_bound = (
                    bool(before) and evidence.get("schemaVersion") == 2
                    and evidence.get("taskSpecSha256") == _canonical_sha256(task)
                    and evidence.get("beforeEvidence") == {
                        "path": before_event.get("evidence"), "sha256": before_event.get("evidenceSha256")
                    }
                    and all(evidence.get(field + "Before") == before.get(field) for field in (
                        "attestation", "campaignIdentity", "sessionAbsence", "coreServices"
                    ))
                    and _ordered_times(before_event.get("completedAtUnix"), evidence.get("recordedAtUnix"))
                )
                if not snapshot_bound:
                    problem(f"recovery_before_provenance_mismatch:{sequence}")
                before_ready = (
                    before.get("campaignIdentity") == expected_campaign_identity
                    and before.get("sessionAbsence") == {"sessionHashes": [], "verified": True}
                    and _core_services_valid(before.get("coreServices"))
                    and _known_recovery_cleanup(prior, allow_agent_proof=True)
                )
                if "remediation" in evidence:
                    remediation = evidence["remediation"]
                    repair_valid = (
                        isinstance(remediation, dict) and before_ready
                        and _timezone_drift_only(before.get("attestation"))
                        and remediation.get("name") == "android_world.utils.datetime_utils.setup_datetime"
                        and remediation.get("allowedScope") == ["auto_time", "auto_time_zone", "time_12_24", "timezone"]
                        and remediation.get("freezeDatetime") is False
                        and remediation.get("outcome") == "completed"
                        and remediation.get("environmentClose") == "closed"
                        and remediation.get("errors") == []
                        and _ordered_times(before_event.get("completedAtUnix"), remediation.get("startedAtUnix"),
                                           remediation.get("completedAtUnix"), evidence.get("recordedAtUnix"))
                        and isinstance(evidence.get("attestation"), dict)
                        and isinstance(evidence["attestation"].get("device"), dict)
                        and evidence["attestation"]["device"].get("timezone") == "UTC"
                        and all(services.get(field) == before.get("coreServices", {}).get(field) for field in (
                            "bootId", "systemServerPids", "surfaceFlingerPids"
                        ))
                    )
                    if not repair_valid:
                        problem(f"invalid_environment_remediation:{sequence}")
                    allowed = allowed and snapshot_bound and repair_valid
                else:
                    allowed = allowed and snapshot_bound and before_ready and _attestation_valid(before.get("attestation"))
                if allowed and not _ordered_times(last_time, evidence.get("recordedAtUnix")):
                    problem(f"unordered_recovery_timestamp:{sequence}")
                    allowed = False
                if allowed:
                    last_time = evidence["recordedAtUnix"]
            if event.get("continuationAllowed") is True:
                if not allowed:
                    problem(f"unproven_recovery_continuation:{sequence}")
                else:
                    recovered.add(key)
            recoveries.append({"taskIndex": index, "attempt": attempt, "evidence": event.get("evidence"),
                               "evidenceSha256": digest, "continuationAllowed": event.get("continuationAllowed"),
                               "pauseReason": event.get("pauseReason"), "checkpointSequence": sequence,
                               "originalClassification": evidence.get("originalClassification"),
                               "originalCleanup": evidence.get("originalCleanup"),
                               "originalResultSha256": evidence.get("resultSha256"),
                               **({"beforeEvidence": evidence.get("beforeEvidence"),
                                   "remediation": evidence.get("remediation")} if continuation_version == 2 else {}),
                               "coreServices": services,
                               "bootChanged": services.get("bootId") != previous_core_services.get("bootId"),
                               "systemServerChanged": services.get("systemServerPids") != previous_core_services.get("systemServerPids"),
                               "surfaceFlingerChanged": services.get("surfaceFlingerPids") != previous_core_services.get("surfaceFlingerPids"),
                               "checkpointPrefixSha256": prefix.hexdigest()})
            if bound and _core_services_valid(services):
                previous_core_services = services
        elif kind == "pause":
            paused, pause_reason = True, event.get("reason")
            if not isinstance(pause_reason, str) or not pause_reason or event.get("unstartedTaskIndexes") != [index for index in by_index if not any(key[0] == index for key in starts)]:
                problem(f"pause_evidence_mismatch:{sequence}")
        elif kind == "finished":
            finished = True
            if active is not None or len({key[0] for key in terminals}) != len(tasks):
                problem("premature_finished_event")
        else:
            problem(f"unknown_checkpoint_event:{sequence}")
        timestamp = event.get("startedAtUnix" if kind == "attempt_started" else "completedAtUnix")
        if kind in {"attempt_started", "attempt_terminal", "finished"}:
            if type(timestamp) not in {int, float} or not math.isfinite(timestamp) or timestamp < last_time:
                problem(f"unordered_checkpoint_timestamp:{sequence}")
            else:
                last_time = timestamp
    if finished:
        for key, record in records.items():
            if _continuation_needs_recovery(record, by_index[key[0]], protocol) and key not in recovered:
                problem(f"missing_verified_recovery_at_finish:{key[0]}:{key[1]}")
    expected_files = {event.get("result") for event in terminals.values()}
    actual_files = {str(path.relative_to(campaign_dir)) for path in (campaign_dir / "episodes").glob("*/attempt-*/result.json")}
    if actual_files != expected_files:
        problem("result_artifact_terminal_set_mismatch")
    started_indexes = sorted({key[0] for key in starts})
    unstarted = [index for index in by_index if index not in started_indexes]
    cleanup_count = sum(row["cleanupFailure"] for row in terminal_rows)
    complete = not unstarted and set(starts) == set(terminals) and finished and not paused and bool(tasks)
    valid = complete and not errors
    latest_rows = {row["taskIndex"]: row for row in terminal_rows}
    score_eligible = valid and cleanup_count == 0 and all(row["classification"] in {"passed", "failed"} for row in latest_rows.values())
    full_valid_score = None
    if manifest.get("kind") == "full" and len(tasks) == 116 and score_eligible and _calibration_gate_satisfied(manifest, campaign_dir):
        full_valid_score = sum(row["officialReward"] for row in latest_rows.values()) / 116
    return {
        "protocolIdentity": f"r{protocol.get('harnessRevision')}.full_coverage_after_verified_recovery.v{continuation_version}",
        "actualStartedEpisodeCount": len(started_indexes), "actualAttemptStartCount": len(starts),
        "unstartedTaskIndexes": unstarted, "recoveryReferences": recoveries,
        "paused": paused, "pauseReason": pause_reason,
        "legacyOfficialScore": None, "fullValidScore": full_valid_score,
        "coverageAudit": {
            "valid": valid, "complete": complete, "sourceTaskSpecsEqual": source_equality,
            "initialCoreServices": initial_core_services,
            "startedTaskIndexes": started_indexes, "terminalTaskIndexes": sorted({key[0] for key in terminals}),
            "terminalEpisodeCount": len({key[0] for key in terminals}), "terminalAttemptCount": len(terminals),
            "startEventCount": start_event_count, "terminalEventCount": terminal_event_count,
            "startedWithoutTerminal": [{"taskIndex": key[0], "attempt": key[1]} for key in starts if key not in terminals],
            "nullRewardCount": sum(row["officialReward"] is None for row in terminal_rows),
            "checkpointNullRewardCount": sum(row["checkpointOfficialReward"] is None for row in terminal_rows),
            "cleanupFailureCount": cleanup_count, "terminals": terminal_rows,
            "originalFailures": [row for row in terminal_rows if row["classification"].startswith("invalid_")
                                 or str(row["checkpointClassification"]).startswith("invalid_") or row["cleanupFailure"]],
            "checkpointSha256": hashlib.sha256(checkpoint_bytes).hexdigest(), "errors": errors,
        },
    }


def recalculate(manifest_path: Path, campaign_dir: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    rows = []
    family_rewards: dict[str, list[float]] = {}
    invalid_breakdown: dict[str, int] = {}
    for task in manifest["tasks"]:
        result_path = _latest_result(campaign_dir, task)
        if result_path is None:
            rows.append(
                {
                    "index": task["index"],
                    "task": task["name"],
                    "family": task["family"],
                    "officialReward": None,
                    "classification": "incomplete",
                    # No attempt exists to clean up. Missing results still block
                    # qualification through the valid/planned episode counts.
                    "cleanupFailure": False,
                }
            )
            continue
        record = json.loads(result_path.read_text())
        reward = official_reward(record, manifest.get("protocol"))
        cleanup_failure = _cleanup_failed(record)
        classification = record_classification(record, task, manifest.get("protocol"))
        if classification.startswith("invalid_"):
            invalid_breakdown[classification] = invalid_breakdown.get(classification, 0) + 1
        else:
            family_rewards.setdefault(task["family"], []).append(float(reward))
        rows.append(
            {
                "index": task["index"],
                "task": task["name"],
                "family": task["family"],
                "officialReward": reward,
                "classification": classification,
                "cleanupFailure": cleanup_failure,
                "result": str(result_path.relative_to(campaign_dir)),
            }
        )
    planned = len(manifest["tasks"])
    valid_rewards = [
        float(row["officialReward"])
        for row in rows
        if row["classification"] in {"passed", "failed"}
    ]
    valid = len(valid_rewards)
    reward_sum = sum(valid_rewards)
    cleanup_failure_count = sum(bool(row["cleanupFailure"]) for row in rows)
    continuation = continuation_audit(manifest, campaign_dir)
    if continuation:
        cleanup_failure_count = max(cleanup_failure_count, continuation["coverageAudit"]["cleanupFailureCount"])
    calibration_gate_satisfied = _calibration_gate_satisfied(manifest, campaign_dir)
    qualified = (
        valid == planned
        and len(rows) == planned
        and cleanup_failure_count == 0
        and calibration_gate_satisfied
        and (not continuation or continuation["coverageAudit"]["valid"])
    )
    family_scores = {
        family: {
            "validEpisodeCount": len(rewards),
            "officialRewardSum": sum(rewards),
            "scoreOnValidEpisodes": sum(rewards) / len(rewards) if rewards else None,
        }
        for family, rewards in sorted(family_rewards.items())
    }
    recalculation = {
        "schemaVersion": 1,
        "campaignId": manifest["campaignId"],
        "plannedEpisodeCount": planned,
        "validEpisodeCount": valid,
        "officialRewardSum": reward_sum,
        "officialScore": reward_sum / planned if qualified else None,
        "diagnosticScoreOnValidEpisodes": reward_sum / valid if valid else None,
        "lowerBoundScoreOnPlannedEpisodes": reward_sum / planned if planned else None,
        "qualified": qualified,
        "cleanupFailureCount": cleanup_failure_count,
        "invalidBreakdown": dict(sorted(invalid_breakdown.items())),
        "calibrationGateSatisfied": calibration_gate_satisfied,
        "family": family_scores,
        "episodes": rows,
    }
    if continuation:
        recalculation.update(continuation)
        if manifest.get("kind") == "full":
            recalculation["officialScore"] = None
    summary_path = campaign_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        recalculation["matchesSummary"] = all(
            recalculation[key] == summary.get(key)
            for key in (
                "plannedEpisodeCount",
                "validEpisodeCount",
                "officialRewardSum",
                "officialScore",
                "diagnosticScoreOnValidEpisodes",
                "lowerBoundScoreOnPlannedEpisodes",
                "qualified",
                "cleanupFailureCount",
                "invalidBreakdown",
                "calibrationGateSatisfied",
            )
        )
        if continuation:
            recalculation["matchesSummary"] = recalculation["matchesSummary"] and all(
                recalculation[key] == summary.get(key) for key in continuation
            )
    return recalculation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Independently recalculate one frozen campaign")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--campaign-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = recalculate(Path(args.manifest), Path(args.campaign_dir))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    raise SystemExit(0 if result.get("matchesSummary", True) else 1)


if __name__ == "__main__":
    main()
