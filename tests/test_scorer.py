import json
from pathlib import Path

import pytest

from fsq_androidworld_eval.action_budget import STEP_BUDGET_PROTOCOL
from fsq_androidworld_eval.lifecycle import TIME_BUDGET_PROTOCOL, episode_time_budget
from fsq_androidworld_eval.scorer import SCORING_POLICY, TERMINATION_POLICY, recalculate


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


@pytest.mark.parametrize("mutation", ["missing", "over_budget", "unproven_step", "valid_exhaustion"])
def test_declared_reference_budget_requires_consistent_execution_evidence(
    tmp_path: Path, mutation: str
) -> None:
    task = {"index": 0, "name": "A", "family": "android", "complexity": 0.2, "maxSteps": 2}
    manifest = {
        "campaignId": "reference-budget",
        "protocol": {"stepBudget": STEP_BUDGET_PROTOCOL},
        "tasks": [task],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    record = {
        "task": {"complexity": 0.2},
        "officialReward": 1.0,
        "error": None,
        "cleanup": _cleanup(),
        "stepBudget": {
            "protocol": STEP_BUDGET_PROTOCOL,
            "maxSteps": 2,
            "referenceStepsExecuted": 2,
            "executedActionCount": 2,
            "rejectedActionCount": 1,
            "actions": [{"kind": "back", "status": 200}, {"kind": "back", "status": 200}],
            "agentIndicatedDone": False,
            "exhausted": True,
        },
    }
    if mutation == "missing":
        del record["stepBudget"]
    elif mutation == "over_budget":
        record["stepBudget"]["executedActionCount"] = 3
    elif mutation == "unproven_step":
        record["stepBudget"]["referenceStepsExecuted"] = 1
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(manifest_path, tmp_path)

    if mutation == "valid_exhaustion":
        assert score["officialScore"] == 1.0
        assert score["invalidBreakdown"] == {}
    else:
        assert score["officialScore"] is None
        assert score["invalidBreakdown"] == {"invalid_protocol": 1}


@pytest.mark.parametrize("first_outcome", ["invalid_setup", "closed", "leaked"])
def test_unexecuted_tasks_do_not_create_cleanup_failures(
    tmp_path: Path, first_outcome: str
) -> None:
    from fsq_androidworld_eval.campaign import _write_summary

    manifest = {
        "campaignId": "partial-campaign", "kind": "calibration",
        "tasks": [
            {"index": 0, "name": "A", "family": "android"},
            {"index": 1, "name": "B", "family": "android"},
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    if first_outcome == "invalid_setup":
        record = {
            "error": {"type": "RuntimeError"}, "invalidReason": "invalid_setup",
            "officialReward": None,
            "cleanup": {
                "agentSession": {"status": "not_created"},
                "taskTearDown": "not_applicable", "environment": "closed",
            },
        }
    else:
        record = {"error": None, "officialReward": 1.0, "cleanup": _cleanup(first_outcome)}
    _write_result(tmp_path, 0, "A", record)
    _write_summary(tmp_path, manifest)

    result = recalculate(manifest_path, tmp_path)

    assert result["matchesSummary"] is True
    assert result["cleanupFailureCount"] == (1 if first_outcome == "leaked" else 0)
    assert result["episodes"][1]["classification"] == "incomplete"
    assert result["episodes"][1]["cleanupFailure"] is False
    assert result["qualified"] is False
    assert result["officialScore"] is None
    assert result["validEpisodeCount"] == (0 if first_outcome == "invalid_setup" else 1)


def _timed_attempt(reason: str = "completed", steps: int = 1) -> tuple[dict, dict]:
    task = {
        "index": 0, "name": "A", "family": "android", "complexity": 1.0,
        "maxSteps": 10, "timeBudget": episode_time_budget(10),
    }
    manifest = {
        "campaignId": "timed-attempt", "kind": "calibration",
        "protocol": {
            "timeBudget": TIME_BUDGET_PROTOCOL,
            "stepBudget": STEP_BUDGET_PROTOCOL,
            "terminationPolicy": TERMINATION_POLICY,
            "scoringPolicy": SCORING_POLICY,
        },
        "tasks": [task],
    }
    session_hash = "b" * 64
    record = {
        "protocol": {"timeBudget": TIME_BUDGET_PROTOCOL},
        "timeBudget": episode_time_budget(10),
        "task": {"complexity": 1.0},
        "agent": {
            "agentCompleted": reason == "completed",
            "termination": {"reason": reason},
            "normalized": {"toolCalls": [{"sessionCleanup": {
                "quitReturned": True, "sessionIdSha256": session_hash,
            }}]},
        },
        "appiumSessionAudit": {
            "createdSessionCount": 1, "deletedSessionCount": 1,
            "createdSessionHashes": [session_hash], "deletedSessionHashes": [session_hash],
            "errors": [],
        },
        "cleanup": {
            **_cleanup(), "agentSession": {"status": "closed", "sessionIdSha256": session_hash},
        },
        "evaluator": {"implementation": "android_world.task_eval.is_successful"},
        "officialReward": 1.0, "error": None,
        "stepBudget": {
            "protocol": STEP_BUDGET_PROTOCOL, "maxSteps": 10,
            "referenceStepsExecuted": steps, "executedActionCount": steps,
            "rejectedActionCount": 0,
            "actions": [{"kind": "back", "status": 200} for _ in range(steps)],
            "agentIndicatedDone": reason == "completed",
            "exhausted": steps == 10 and reason != "completed",
        },
    }
    return manifest, record


@pytest.mark.parametrize("reason,classification", [
    ("completed", "passed"),
    ("business_deadline", "passed"),
    ("omp_deadline", "passed"),
    ("unknown_termination", "invalid_agent"),
    ("forced_termination", "invalid_agent"),
])
def test_termination_classification_preserves_evaluated_reward(
    tmp_path: Path, reason: str, classification: str
) -> None:
    from fsq_androidworld_eval.campaign import _write_summary

    manifest, record = _timed_attempt(reason)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)
    summary = _write_summary(tmp_path, manifest)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] == 1.0
    assert summary["episodes"][0]["officialReward"] == 1.0
    assert score["episodes"][0]["classification"] == classification
    assert score["validEpisodeCount"] == (1 if classification == "passed" else 0)
    assert score["qualified"] is (classification == "passed")
    assert score["matchesSummary"] is True


@pytest.mark.parametrize("reason", ["business_deadline", "omp_deadline"])
@pytest.mark.parametrize("steps", [0, 3, 10])
def test_deadline_attempt_accepts_honest_partial_or_zero_reference_steps(
    tmp_path: Path, reason: str, steps: int
) -> None:
    manifest, record = _timed_attempt(reason, steps)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(path, tmp_path)

    assert score["officialScore"] == 1.0
    assert score["invalidBreakdown"] == {}


@pytest.mark.parametrize("evaluator", [None, {}])
def test_no_evaluator_cannot_supply_a_reward(tmp_path: Path, evaluator: dict | None) -> None:
    from fsq_androidworld_eval.campaign import _write_summary

    manifest, record = _timed_attempt()
    record["evaluator"] = evaluator
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)
    summary = _write_summary(tmp_path, manifest)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] is None
    assert summary["episodes"][0]["officialReward"] is None
    assert score["invalidBreakdown"] == {"invalid_evaluator": 1}
    assert score["matchesSummary"] is True


@pytest.mark.parametrize("mutation", ["manifest_protocol", "task_budget", "result_protocol", "result_budget", "termination_policy", "scoring_policy"])
def test_frozen_time_budget_and_policies_require_matching_evidence(
    tmp_path: Path, mutation: str
) -> None:
    from fsq_androidworld_eval.campaign import _write_summary

    manifest, record = json.loads(json.dumps(_timed_attempt()))
    if mutation == "manifest_protocol":
        manifest["protocol"]["timeBudget"]["cleanupWindowSeconds"] -= 1
    elif mutation == "task_budget":
        manifest["tasks"][0]["timeBudget"]["businessSeconds"] += 1
    elif mutation == "result_protocol":
        record["protocol"]["timeBudget"]["minimumBusinessSeconds"] -= 1
    elif mutation == "result_budget":
        record["timeBudget"]["episodeSeconds"] -= 1
    elif mutation == "termination_policy":
        manifest["protocol"]["terminationPolicy"]["forced_termination"] = "evaluated_attempt"
    else:
        manifest["protocol"]["scoringPolicy"]["cleanupGate"] = "allow_harness_reclaim"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)
    _write_summary(tmp_path, manifest)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] == 1.0
    assert score["officialScore"] is None
    assert score["invalidBreakdown"] == {"invalid_protocol": 1}
    assert score["matchesSummary"] is True


@pytest.mark.parametrize("cleanup_proven", [False, True])
def test_agent_close_requires_quit_and_deletion_evidence(
    tmp_path: Path, cleanup_proven: bool
) -> None:
    manifest, record = _timed_attempt()
    if not cleanup_proven:
        record["agent"]["normalized"]["toolCalls"] = []
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] == 1.0
    assert score["cleanupFailureCount"] == int(not cleanup_proven)
    assert score["qualified"] is cleanup_proven


def test_recalculation_never_rewrites_episode_artifacts(tmp_path: Path) -> None:
    manifest, record = _timed_attempt("forced_termination")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)
    episode = tmp_path / "episodes/000-A/attempt-1/result.json"
    original = episode.read_bytes()

    recalculate(path, tmp_path)

    assert episode.read_bytes() == original


@pytest.mark.parametrize("status", ["harness_reclaimed", "idle_timeout", "unknown", "leaked"])
def test_non_agent_cleanup_retains_reward_but_never_qualifies(tmp_path: Path, status: str) -> None:
    manifest, record = _timed_attempt("business_deadline")
    record["cleanup"]["agentSession"]["status"] = status
    record["cleanup"]["agentSession"]["harnessRecovery"] = {"status": "closed"}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] == 1.0
    assert score["episodes"][0]["classification"] == "passed"
    assert score["validEpisodeCount"] == 1
    assert score["cleanupFailureCount"] == 1
    assert score["qualified"] is False


@pytest.mark.parametrize("reason,steps,done,exhausted", [
    ("completed", 0, True, False),
    ("business_deadline", 3, False, True),
    ("business_deadline", 10, False, False),
])
def test_reference_exhaustion_is_only_a_consumed_step_budget(
    tmp_path: Path, reason: str, steps: int, done: bool, exhausted: bool
) -> None:
    manifest, record = _timed_attempt(reason, steps)
    record["stepBudget"].update(agentIndicatedDone=done, exhausted=exhausted)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(path, tmp_path)

    assert score["invalidBreakdown"] == {"invalid_protocol": 1}
    assert score["episodes"][0]["officialReward"] == 1.0