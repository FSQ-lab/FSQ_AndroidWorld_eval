import json
from pathlib import Path

from fsq_androidworld_eval.scorer import recalculate


def _write_result(root: Path, index: int, name: str, record: dict) -> None:
    path = root / "episodes" / f"{index:03d}-{name}" / "attempt-1" / "result.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(record))


def _cleanup(status: str = "closed") -> dict:
    return {
        "agentSession": {"status": status},
        "taskTearDown": "completed",
        "environment": "closed",
    }


def test_recalculates_only_official_reward_and_matches_summary(tmp_path: Path) -> None:
    manifest = {
        "campaignId": "score-test",
        "tasks": [
            {"index": 0, "name": "A", "family": "android"},
            {"index": 1, "name": "B", "family": "information_retrieval"},
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    _write_result(
        tmp_path,
        0,
        "A",
        {
            "error": None,
            "officialReward": 1.0,
            "budget": {"exceededAdvisory": True},
            "cleanup": _cleanup(),
        },
    )
    _write_result(
        tmp_path,
        1,
        "B",
        {
            "error": None,
            "officialReward": 0.5,
            "budget": {"exceededAdvisory": False},
            "cleanup": _cleanup(),
        },
    )
    expected = {
        "plannedEpisodeCount": 2,
        "validEpisodeCount": 2,
        "officialRewardSum": 1.5,
        "officialScore": 0.75,
        "diagnosticScoreOnValidEpisodes": 0.75,
        "lowerBoundScoreOnPlannedEpisodes": 0.75,
        "qualified": True,
        "cleanupFailureCount": 0,
        "invalidBreakdown": {},
        "calibrationGateSatisfied": True,
    }
    (tmp_path / "summary.json").write_text(json.dumps(expected))

    result = recalculate(manifest_path, tmp_path)

    assert result["officialScore"] == 0.75
    assert result["episodes"][0]["officialReward"] == 1.0
    assert result["matchesSummary"] is True


def test_invalid_episode_blocks_official_score_but_preserves_lower_bound(tmp_path: Path) -> None:
    manifest = {
        "campaignId": "invalid-test",
        "tasks": [
            {"index": 0, "name": "A", "family": "android"},
            {"index": 1, "name": "B", "family": "android"},
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    _write_result(
        tmp_path,
        0,
        "A",
        {"error": None, "officialReward": 1.0, "cleanup": _cleanup()},
    )
    _write_result(
        tmp_path,
        1,
        "B",
        {
            "error": {"type": "SetupError"},
            "invalidReason": "invalid_setup",
            "officialReward": None,
            "cleanup": _cleanup("not_created"),
        },
    )

    result = recalculate(manifest_path, tmp_path)

    assert result["officialScore"] is None
    assert result["diagnosticScoreOnValidEpisodes"] == 1.0
    assert result["lowerBoundScoreOnPlannedEpisodes"] == 0.5
    assert result["invalidBreakdown"] == {"invalid_setup": 1}


def test_cleanup_failure_blocks_independent_qualification(tmp_path: Path) -> None:
    manifest = {
        "campaignId": "cleanup-test",
        "tasks": [{"index": 0, "name": "A", "family": "android"}],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    _write_result(
        tmp_path,
        0,
        "A",
        {"error": None, "officialReward": 1.0, "cleanup": _cleanup("leaked")},
    )

    result = recalculate(manifest_path, tmp_path)

    assert result["officialScore"] is None
    assert result["qualified"] is False
    assert result["cleanupFailureCount"] == 1



def test_missing_cleanup_fields_block_independent_qualification(tmp_path: Path) -> None:
    manifest = {
        "campaignId": "truncated-cleanup",
        "tasks": [{"index": 0, "name": "A", "family": "android"}],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    _write_result(
        tmp_path,
        0,
        "A",
        {
            "error": None,
            "officialReward": 1.0,
            "cleanup": {"agentSession": {"status": "closed"}},
        },
    )

    result = recalculate(manifest_path, tmp_path)

    assert result["qualified"] is False
    assert result["cleanupFailureCount"] == 1