from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from fsq_androidworld_eval.action_budget import STEP_BUDGET_PROTOCOL
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget


TERMINATION_POLICY = {
    "completed": "evaluated_attempt",
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
    if _uses_time_budget(record, protocol):
        if task is not None and protocol is not None and not time_budget_valid(record, task, protocol):
            return "invalid_protocol"
        agent = record.get("agent")
        termination = agent.get("termination") if isinstance(agent, dict) else None
        reason = termination.get("reason") if isinstance(termination, dict) else None
        if (
            reason not in {"completed", "business_deadline", "omp_deadline"}
            or agent.get("agentCompleted") is not (reason == "completed")
        ):
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
    calibration_gate_satisfied = _calibration_gate_satisfied(manifest, campaign_dir)
    qualified = (
        valid == planned
        and len(rows) == planned
        and cleanup_failure_count == 0
        and calibration_gate_satisfied
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
