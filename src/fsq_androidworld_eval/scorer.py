from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _cleanup_failed(record: dict[str, Any]) -> bool:
    cleanup = record.get("cleanup")
    if not isinstance(cleanup, dict):
        return True
    session = cleanup.get("agentSession")
    if not isinstance(session, dict):
        return True
    task_teardown = cleanup.get("taskTearDown")
    environment = cleanup.get("environment")
    if record.get("error") is None:
        return (
            session.get("status") != "closed"
            or task_teardown != "completed"
            or environment != "closed"
        )
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
                    "cleanupFailure": True,
                }
            )
            continue
        record = json.loads(result_path.read_text())
        reward = record.get("officialReward")
        cleanup_failure = _cleanup_failed(record)
        if record.get("error") is not None or not isinstance(reward, (int, float)):
            classification = record.get("invalidReason") or "invalid_evaluator"
            invalid_breakdown[classification] = invalid_breakdown.get(classification, 0) + 1
            reward = None
        else:
            classification = "passed" if reward > 0.5 else "failed"
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
        if row["officialReward"] is not None
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
