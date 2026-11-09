import hashlib
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
    if reason == "step_budget":
        record["agent"]["termination"]["actionBudgetClosureReason"] = "step_budget"
        record["agent"]["normalized"].update(
            agentCompleted=False, assistantStopReason="stop",
            terminalEvents=[{"type": "agent_end", "isTerminal": True}],
        )
        record["stepBudget"]["closureReason"] = "step_budget"
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


@pytest.mark.parametrize("reason", ["business_deadline", "step_budget"])
@pytest.mark.parametrize("status", ["harness_reclaimed", "idle_timeout", "unknown", "leaked"])
def test_non_agent_cleanup_retains_reward_but_never_qualifies(tmp_path: Path, status: str, reason: str) -> None:
    manifest, record = _timed_attempt(reason, 10 if reason == "step_budget" else 1)
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


@pytest.mark.parametrize("change,classification", [
    ("none", "failed"), ("partial_steps", "invalid_protocol"),
    ("missing_cause", "invalid_agent"), ("nonterminal", "invalid_agent"),
    ("aborted", "invalid_agent"), ("forced", "invalid_agent"),
    ("business_expired", "invalid_agent"), ("wrong_gate_reason", "invalid_protocol"),
    ("claimed_completion", "invalid_agent"),
])
def test_step_budget_attempt_preserves_zero_reward_without_fabricating_completion(
    tmp_path: Path, change: str, classification: str,
) -> None:
    manifest, record = _timed_attempt("step_budget", 10)
    record["officialReward"] = 0.0
    agent = record["agent"]
    if change == "partial_steps":
        record["stepBudget"].update(referenceStepsExecuted=9, executedActionCount=9, exhausted=False)
        record["stepBudget"]["actions"].pop()
    elif change == "missing_cause":
        del agent["termination"]["actionBudgetClosureReason"]
    elif change == "nonterminal":
        agent["normalized"]["terminalEvents"][-1]["isTerminal"] = False
    elif change == "aborted":
        agent["normalized"]["assistantStopReason"] = "aborted"
    elif change == "forced":
        agent["termination"]["outerTermination"] = True
    elif change == "business_expired":
        agent["termination"]["businessDeadlineReached"] = True
    elif change == "wrong_gate_reason":
        record["stepBudget"]["closureReason"] = "agent_terminated"
    elif change == "claimed_completion":
        agent["agentCompleted"] = True
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    score = recalculate(path, tmp_path)

    assert score["episodes"][0]["officialReward"] == 0.0
    assert score["episodes"][0]["classification"] == classification
    assert score["validEpisodeCount"] == int(change == "none")
    assert score["qualified"] is (change == "none")
    assert agent["agentCompleted"] is (change == "claimed_completion")


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _attestation() -> dict:
    value = {"qualified": True, "mismatches": {}}
    return {**value, "identitySha256": _digest(value)}


def _core_services() -> dict:
    return {
        "adbState": "device", "bootCompleted": "1", "activityService": True,
        "packageService": True, "settingsService": True, "windowService": True,
        "appiumReady": True, "grpcReady": True, "qualified": True,
        "systemServerPids": ["123"], "surfaceFlingerPids": ["456"],
        "bootId": "00000000-0000-4000-8000-000000000001",
    }


def _r12_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str = "calibration", *, version: int = 2, revision: int = 12) -> tuple[Path, dict, list[dict]]:
    """Synthetic frozen artifacts, not suite-generated benchmark parameters."""
    from fsq_androidworld_eval import scorer

    source_protocol = json.loads(json.dumps(_timed_attempt()[0]["protocol"]))
    source_protocol.update({
        "harnessRevision": 11, "androidWorldRevision": "frozen-android-world",
        "runtimeIdentity": {"amkernelVersion": "frozen-runtime"},
        "environmentArtifacts": {"identitySha256": "frozen-assets"},
        "promptTemplateSha256": "frozen-prompt", "mcpRequestTimeoutMs": 300000,
        "sessionCreationTimeoutSeconds": 300, "pythonExecCallAdvisory": 20,
        "invalidRetryLimit": 1, "model": "provider/model",
        "agentToolPolicy": {"tools": ["read", "write"], "allowedTargets": [
            "skill://amkernel", "xd://mcp__amkernel_python_exec", "xd://report_issue",
        ]},
    })
    tasks = [{
        **_timed_attempt()[0]["tasks"][0], "index": index, "name": f"Task{index:03d}",
        "instanceSeed": index, "params": {"fixture": index}, "paramsSha256": _digest({"fixture": index}),
        "paramsTransport": "json", "apps": ["fixture-app"], "tags": ["fixture"],
    } for index in range(116)]
    source = {"schemaVersion": 2, "campaignId": "frozen-source", "kind": "full", "protocol": source_protocol,
              "target": {"serial": "fixture-device"}, "tasks": tasks}
    source_path = tmp_path / "frozen-source.json"
    source_path.write_text(json.dumps(source))
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    monkeypatch.setattr(scorer, "INHERITED_MANIFEST_SHA256", source_hash)

    def emit(root: Path, campaign_kind: str) -> tuple[dict, list[dict]]:
        root.mkdir(parents=True)
        protocol = {**source_protocol, "harnessRevision": revision,
                    "campaignContinuation": {**scorer.CONTINUATION_PROTOCOL, "version": version}}
        if revision == 13:
            from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL
            protocol.update(answerSubmission=ANSWER_SUBMISSION_PROTOCOL, promptTemplateSha256="bounded-submission-prompt")
        manifest = {
            "campaignId": f"r12-{campaign_kind}", "kind": campaign_kind, "protocol": protocol,
            "target": {"serial": "fixture-device"},
            "inheritedManifest": {"path": str(source_path), "sha256": source_hash,
                "tasksSha256": _digest(tasks), "campaignId": source["campaignId"], "taskCount": 116},
            "tasks": tasks if campaign_kind == "full" else tasks[:12],
        }
        if campaign_kind == "full":
            calibration_dir = root / "calibration-evidence"
            calibration, _ = emit(calibration_dir, "calibration")
            summary = recalculate(calibration_dir / "manifest.json", calibration_dir)
            summary["identitySha256"] = _digest(summary)
            (calibration_dir / "summary.json").write_text(json.dumps(summary))
            paths = [path for path in calibration_dir.rglob("*") if path.is_file()]
            evidence_rows = [{"path": str(path.relative_to(calibration_dir)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(paths)]
            manifest["calibrationGate"] = {
                "campaignId": calibration["campaignId"], "manifestSha256": _digest(calibration),
                "summaryIdentitySha256": summary["identitySha256"], "evidenceSha256": _digest(evidence_rows),
            }
        identity = _digest(manifest)
        readiness = {"manifestSha256": identity, "qualified": True, "environmentClose": "closed",
                     "environmentArtifacts": protocol["environmentArtifacts"], "target": manifest["target"]}
        readiness["identitySha256"] = _digest(readiness)
        (root / "device-readiness.json").write_text(json.dumps(readiness))
        (root / "run-metadata.json").write_text(json.dumps({
            "campaignId": manifest["campaignId"], "manifestSha256": identity,
            "readinessIdentitySha256": readiness["identitySha256"],
            "liveTargetAttestation": _attestation(), "startedAtUnix": 1,
            "initialCoreServices": _core_services(),
        }))
        (root / "manifest.json").write_text(json.dumps(manifest))
        events = []
        for task in manifest["tasks"]:
            index, name = task["index"], task["name"]
            record = json.loads(json.dumps(_timed_attempt()[1]))
            record.update({
                "schemaVersion": 3, "androidWorld": {"revision": protocol["androidWorldRevision"]},
                "startedAtUnix": 2.1 + 2 * index, "completedAtUnix": 2.9 + 2 * index,
                "amkernel": {"version": "frozen-runtime"}, "target": manifest["target"],
                "task": {"name": name, "params": task["params"], "paramsSha256": task["paramsSha256"], "complexity": task["complexity"]},
                "protocol": {**protocol, "readinessIdentitySha256": readiness["identitySha256"]},
                "budget": {"pythonExecCalls": 1, "advisory": 20, "affectsOfficialReward": False},
            })
            record["cleanup"]["agentSession"]["verificationStatus"] = "absent"
            record["agent"]["normalized"].update(provider="provider", model="model", parseErrors=0)
            record["agent"]["normalized"]["toolCalls"][0].update(tool="write", target="xd://mcp__amkernel_python_exec")
            _write_result(root, index, name, record)
            if revision == 13:
                result_file = root / "episodes" / f"{index:03d}-{name}" / "attempt-1" / "result.json"
                _attach_submission(result_file, record, task["timeBudget"]["businessSeconds"])
            result = f"episodes/{index:03d}-{name}/attempt-1/result.json"
            binding = {"taskIndex": index, "task": name, "attempt": 1, "result": result,
                       "manifestSha256": identity, "readinessIdentitySha256": readiness["identitySha256"],
                       "taskSpecSha256": _digest(task)}
            events.extend([
                {**binding, "event": "attempt_started", "startedAtUnix": 2 + 2 * index},
                {**binding, "event": "attempt_terminal", "completedAtUnix": 3 + 2 * index,
                 "classification": "passed", "officialReward": 1.0,
                 "resultSha256": hashlib.sha256((root / result).read_bytes()).hexdigest()},
            ])
        events.append({"event": "finished", "completedAtUnix": 2 + 2 * len(manifest["tasks"])})
        _checkpoint(root, events)
        return manifest, events

    root = tmp_path / "campaign"
    manifest, events = emit(root, kind)
    return root, manifest, events


def _checkpoint(root: Path, events: list[dict]) -> None:
    serialized = []
    for event in events:
        if "_beforeEvent" in event:
            serialized.append(event["_beforeEvent"])
        serialized.append({key: value for key, value in event.items() if key != "_beforeEvent"})
    (root / "checkpoint.jsonl").write_text("".join(json.dumps(event) + "\n" for event in serialized))


def _change_terminal(root: Path, manifest: dict, events: list[dict], index: int, mutate) -> dict:
    from fsq_androidworld_eval.scorer import official_reward, record_classification

    terminal = next(event for event in events if event.get("event") == "attempt_terminal" and event["taskIndex"] == index)
    path = root / terminal["result"]
    record = json.loads(path.read_text())
    mutate(record)
    path.write_text(json.dumps(record))
    terminal.update(resultSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    classification=record_classification(record, manifest["tasks"][index], manifest["protocol"]),
                    officialReward=official_reward(record, manifest["protocol"]))
    return record


def _recovery(root: Path, manifest: dict, terminal: dict, record: dict, allowed: bool = True) -> dict:
    evidence = {
        "manifestSha256": terminal["manifestSha256"], "readinessIdentitySha256": terminal["readinessIdentitySha256"],
        "campaignIdentity": {"verified": True, "manifestSha256": _digest(manifest),
                             "readinessIdentitySha256": terminal["readinessIdentitySha256"]},
        "taskIndex": terminal["taskIndex"], "task": terminal["task"], "attempt": terminal["attempt"],
        "result": terminal["result"], "resultSha256": terminal["resultSha256"],
        "originalClassification": terminal["classification"], "originalCleanup": record["cleanup"],
        "attestation": _attestation(), "sessionAbsence": {"sessionHashes": [], "verified": True},
        "coreServices": _core_services(), "schemaVersion": 2,
        "taskSpecSha256": _digest(manifest["tasks"][terminal["taskIndex"]]),
        "recordedAtUnix": terminal["completedAtUnix"],
        "continuationAllowed": allowed, "pauseReason": None if allowed else "unknown_cleanup",
    }
    before = {key: value for key, value in evidence.items() if key not in {"continuationAllowed", "pauseReason"}}
    before["identitySha256"] = _digest(before)
    before_path = root / f"recoveries/{terminal['taskIndex']:03d}-attempt-1-before.json"
    before_path.parent.mkdir(exist_ok=True)
    before_path.write_text(json.dumps(before))
    before_event = {"event": "recovery_before", "taskIndex": terminal["taskIndex"], "task": terminal["task"],
                    "attempt": terminal["attempt"], "evidence": str(before_path.relative_to(root)),
                    "evidenceSha256": hashlib.sha256(before_path.read_bytes()).hexdigest(),
                    "completedAtUnix": before["recordedAtUnix"]}
    evidence["beforeEvidence"] = {"path": before_event["evidence"], "sha256": before_event["evidenceSha256"]}
    evidence.update({key + "Before": before[key] for key in (
        "attestation", "campaignIdentity", "sessionAbsence", "coreServices"
    )})
    evidence["identitySha256"] = _digest(evidence)
    path = root / f"recoveries/{terminal['taskIndex']:03d}-attempt-1.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(evidence))
    return {"event": "recovery", "taskIndex": terminal["taskIndex"], "task": terminal["task"], "attempt": 1,
            "evidence": str(path.relative_to(root)), "evidenceSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "continuationAllowed": allowed, "pauseReason": evidence["pauseReason"], "_beforeEvent": before_event}


@pytest.mark.parametrize("kind,count", [("calibration", 12), ("full", 116)])
def test_r12_complete_provenance_uses_separate_full_score(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str, count: int) -> None:
    root, _, _ = _r12_fixture(tmp_path, monkeypatch, kind)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is True
    assert result["officialScore"] == (1.0 if kind == "calibration" else None)
    assert result["fullValidScore"] == (1.0 if kind == "full" else None)
    assert result["legacyOfficialScore"] is None
    assert result["protocolIdentity"] == "r12.full_coverage_after_verified_recovery.v2"
    assert result["coverageAudit"]["valid"] is True
    assert result["coverageAudit"]["terminalAttemptCount"] == count
    assert result["actualStartedEpisodeCount"] == count
    assert result["unstartedTaskIndexes"] == []


def test_r12_116_result_rows_do_not_prove_any_episode_started(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _, _ = _r12_fixture(tmp_path, monkeypatch, "full")
    _checkpoint(root, [])

    result = recalculate(root / "manifest.json", root)

    assert result["validEpisodeCount"] == 116
    assert result["qualified"] is False
    assert result["fullValidScore"] is None
    assert result["actualStartedEpisodeCount"] == 0
    assert result["unstartedTaskIndexes"] == list(range(116))
    assert result["coverageAudit"]["terminalAttemptCount"] == 0


@pytest.mark.parametrize("mutation", ["duplicate_start", "duplicate_terminal", "terminal_before_start", "wrong_spec_binding", "wrong_result_hash", "missing_continuation", "frozen_runtime", "frozen_params"])
def test_r12_provenance_mutations_block_qualification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    if mutation == "duplicate_start":
        events.insert(1, dict(events[0]))
    elif mutation == "duplicate_terminal":
        events.insert(2, dict(events[1]))
    elif mutation == "terminal_before_start":
        events[0], events[1] = events[1], events[0]
    elif mutation == "wrong_spec_binding":
        events[0]["taskSpecSha256"] = "wrong"
    elif mutation == "wrong_result_hash":
        events[1]["resultSha256"] = "wrong"
    elif mutation == "missing_continuation":
        del manifest["protocol"]["campaignContinuation"]
        (root / "manifest.json").write_text(json.dumps(manifest))
    elif mutation == "frozen_runtime":
        manifest["protocol"]["runtimeIdentity"] = {"amkernelVersion": "changed"}
        (root / "manifest.json").write_text(json.dumps(manifest))
    else:
        manifest["tasks"][0]["params"]["fixture"] = "changed"
        (root / "manifest.json").write_text(json.dumps(manifest))
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is False
    assert result["coverageAudit"]["valid"] is False
    assert result["coverageAudit"]["errors"]


def test_r12_pause_reports_actual_starts_and_unstarted_nulls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _, events = _r12_fixture(tmp_path, monkeypatch)
    for event in events[2:]:
        if event.get("event") == "attempt_terminal":
            (root / event["result"]).unlink()
    events = events[:2] + [{"event": "pause", "reason": "unusable_environment", "unstartedTaskIndexes": list(range(1, 12))}]
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["actualStartedEpisodeCount"] == 1
    assert result["coverageAudit"]["terminalEpisodeCount"] == 1
    assert result["unstartedTaskIndexes"] == list(range(1, 12))
    assert result["paused"] is True
    assert result["pauseReason"] == "unusable_environment"
    assert result["coverageAudit"]["errors"] == []
    assert result["qualified"] is False
    assert all(row["officialReward"] is None for row in result["episodes"][1:])


@pytest.mark.parametrize("reason", ["forced_termination", "invalid_evaluator", "invalid_protocol"])
def test_r12_recovered_invalid_attempt_preserves_failure_and_null(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reason: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)

    def mutate(record: dict) -> None:
        if reason == "invalid_evaluator":
            record["evaluator"] = None
            record["officialReward"] = None
        elif reason == "invalid_protocol":
            record["invalidReason"] = "invalid_protocol"
        else:
            record["agent"]["agentCompleted"] = False
            record["agent"]["termination"]["reason"] = reason

    record = _change_terminal(root, manifest, events, 0, mutate)
    events.insert(2, _recovery(root, manifest, events[1], record))
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["valid"] is True
    assert result["actualStartedEpisodeCount"] == 12
    classification = "invalid_agent" if reason == "forced_termination" else reason
    assert result["invalidBreakdown"] == {classification: 1}
    assert result["coverageAudit"]["nullRewardCount"] == int(reason == "invalid_evaluator")
    assert result["episodes"][0]["officialReward"] == (None if reason == "invalid_evaluator" else 1.0)
    assert len(result["coverageAudit"]["originalFailures"]) == 1
    assert result["recoveryReferences"][0]["checkpointSequence"] == 4
    assert result["qualified"] is False


@pytest.mark.parametrize("cleanup", ["missing_proof", "harness_reclaimed", "unknown"])
def test_r12_recovery_never_repairs_original_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cleanup: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)

    def mutate(record: dict) -> None:
        if cleanup == "missing_proof":
            record["agent"]["normalized"]["toolCalls"][0].pop("sessionCleanup")
        elif cleanup == "harness_reclaimed":
            record["cleanup"]["agentSession"] = {
                "status": "harness_reclaimed", "pendingRequestCount": 0,
                "attribution": "harness", "verificationStatus": "absent",
                "unknownCreationOutcomeCount": 0, "activeSessionCount": 0,
                "sessions": [{"quitReturned": True, "absentVerified": True}],
            }
        else:
            record["cleanup"]["agentSession"]["status"] = "unknown"

    record = _change_terminal(root, manifest, events, 0, mutate)
    original = (root / events[1]["result"]).read_bytes()
    events.insert(2, _recovery(root, manifest, events[1], record))
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["episodes"][0]["officialReward"] == 1.0
    assert result["episodes"][0]["classification"] == "passed"
    assert result["cleanupFailureCount"] == 1
    assert result["qualified"] is False
    assert result["coverageAudit"]["valid"] is (cleanup != "unknown")
    assert (root / events[1]["result"]).read_bytes() == original


def test_r12_later_artifact_rewrite_breaks_recovery_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    record = _change_terminal(root, manifest, events, 0, lambda value: value.update(invalidReason="invalid_setup"))
    events.insert(2, _recovery(root, manifest, events[1], record))
    path = root / events[1]["result"]
    rewritten = json.loads(path.read_text())
    rewritten["invalidReason"] = None
    path.write_text(json.dumps(rewritten))
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is False
    assert any("terminal_result_hash_mismatch" in error for error in result["coverageAudit"]["errors"])
    assert any("recovery_boundary_mismatch" in error for error in result["coverageAudit"]["errors"])
    assert result["coverageAudit"]["originalFailures"][0]["checkpointClassification"] == "invalid_setup"
    assert result["recoveryReferences"][0]["originalClassification"] == "invalid_setup"


def test_r12_nonretryable_same_task_replay_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    record = _change_terminal(root, manifest, events, 0, lambda value: value.update(invalidReason="invalid_setup"))
    recovery = _recovery(root, manifest, events[1], record)
    replay = {**events[0], "attempt": 2, "startedAtUnix": 3, "result": "episodes/000-Task000/attempt-2/result.json"}
    events[2:2] = [recovery, replay]
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is False
    assert any("nonretryable_replay" in error for error in result["coverageAudit"]["errors"])
    assert result["actualAttemptStartCount"] == 13


def test_r11_retains_existing_formal_score_without_start_audit(tmp_path: Path) -> None:
    manifest, record = _timed_attempt()
    manifest["protocol"]["harnessRevision"] = 11
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    _write_result(tmp_path, 0, "A", record)

    result = recalculate(path, tmp_path)

    assert result["qualified"] is True
    assert result["officialScore"] == 1.0
    assert "coverageAudit" not in result
    assert "fullValidScore" not in result


@pytest.mark.parametrize("outcome", ["failed", "business_deadline", "invalid_evaluator"])
@pytest.mark.parametrize("index", [0, 11])
def test_r12_nonclean_outcomes_require_boundary_even_on_last_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, outcome: str, index: int) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)

    def mutate(record: dict) -> None:
        if outcome == "failed":
            record["officialReward"] = 0.0
        elif outcome == "business_deadline":
            record["agent"]["agentCompleted"] = False
            record["agent"]["termination"]["reason"] = outcome
            record["stepBudget"].update(agentIndicatedDone=False, exhausted=False)
        else:
            record["evaluator"] = None
            record["officialReward"] = None

    _change_terminal(root, manifest, events, index, mutate)
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["complete"] is True
    assert result["coverageAudit"]["valid"] is False
    assert any("missing_verified_recovery" in error for error in result["coverageAudit"]["errors"])
    assert result["qualified"] is False


def test_r12_full_requires_fresh_calibration_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _, _ = _r12_fixture(tmp_path, monkeypatch, "full")
    (root / "calibration-evidence/checkpoint.jsonl").write_text("")

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["valid"] is True
    assert result["validEpisodeCount"] == 116
    assert result["calibrationGateSatisfied"] is False
    assert result["qualified"] is False
    assert result["fullValidScore"] is None


def test_r12_preagent_retry_retains_original_failure_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    original = json.loads((root / events[1]["result"]).read_text())

    def mutate(record: dict) -> None:
        record.update(agent=None, error={"type": "RuntimeError"}, invalidReason="invalid_infrastructure",
                      officialReward=None, task={"name": "Task000", "seed": 0})
        record["cleanup"]["agentSession"] = {"status": "not_created"}

    record = _change_terminal(root, manifest, events, 0, mutate)
    recovery = _recovery(root, manifest, events[1], record)
    replay_path = root / "episodes/000-Task000/attempt-2/result.json"
    replay_path.parent.mkdir()
    original.update(startedAtUnix=3.1, completedAtUnix=3.9)
    replay_path.write_text(json.dumps(original))
    start = {**events[0], "attempt": 2, "startedAtUnix": 3, "result": str(replay_path.relative_to(root))}
    terminal = {**events[1], "attempt": 2, "completedAtUnix": 4, "result": start["result"],
                "classification": "passed", "officialReward": 1.0,
                "resultSha256": hashlib.sha256(replay_path.read_bytes()).hexdigest()}
    events[2:2] = [recovery, start, terminal]
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is True
    assert result["actualStartedEpisodeCount"] == 12
    assert result["actualAttemptStartCount"] == 13
    assert result["coverageAudit"]["terminalAttemptCount"] == 13
    assert result["coverageAudit"]["nullRewardCount"] == 1
    assert result["coverageAudit"]["originalFailures"][0]["classification"] == "invalid_infrastructure"


def test_r12_environment_mode_is_bound_to_original_target_and_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    report = {"avd": None, "serial": "fixture-device", "headless": True}
    report_path = tmp_path / "environment-mode.json"
    report_path.write_text(json.dumps(report))
    manifest["target"]["environmentMode"] = {"path": str(report_path),
        "sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(), "evidence": report}
    identity = _digest(manifest)
    readiness = json.loads((root / "device-readiness.json").read_text())
    readiness.update(manifestSha256=identity, target=manifest["target"])
    readiness["identitySha256"] = _digest({key: value for key, value in readiness.items() if key != "identitySha256"})
    metadata = json.loads((root / "run-metadata.json").read_text())
    metadata.update(manifestSha256=identity, readinessIdentitySha256=readiness["identitySha256"])
    (root / "manifest.json").write_text(json.dumps(manifest))
    (root / "device-readiness.json").write_text(json.dumps(readiness))
    (root / "run-metadata.json").write_text(json.dumps(metadata))
    for event in events:
        if event.get("event") in {"attempt_started", "attempt_terminal"}:
            event.update(manifestSha256=identity, readinessIdentitySha256=readiness["identitySha256"])
        if event.get("event") == "attempt_terminal":
            _change_terminal(root, manifest, events, event["taskIndex"], lambda record: record["protocol"].update(readinessIdentitySha256=readiness["identitySha256"]))
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)
    assert result["qualified"] is True

    report_path.write_text(json.dumps({**report, "headless": False}))
    result = recalculate(root / "manifest.json", root)
    assert result["qualified"] is False
    assert "environment_mode_provenance_mismatch" in result["coverageAudit"]["errors"]


@pytest.mark.parametrize("mutation", ["services", "session_absence", "attestation", "identity", "result_binding", "campaign_identity", "settings_service", "window_service", "system_server", "surface_flinger", "boot_id"])
def test_r12_recovery_requires_proof_not_only_allowed_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    record = _change_terminal(root, manifest, events, 0, lambda value: value.update(invalidReason="invalid_setup"))
    recovery = _recovery(root, manifest, events[1], record)
    path = root / recovery["evidence"]
    evidence = json.loads(path.read_text())
    if mutation == "services":
        evidence["coreServices"]["grpcReady"] = False
    elif mutation == "session_absence":
        evidence["sessionAbsence"]["sessionHashes"] = ["still-active"]
    elif mutation == "attestation":
        evidence["attestation"]["mismatches"] = {"device": "changed"}
        evidence["attestation"]["identitySha256"] = _digest({key: value for key, value in evidence["attestation"].items() if key != "identitySha256"})
    elif mutation == "result_binding":
        evidence["resultSha256"] = "unrelated-result"
    elif mutation == "campaign_identity":
        evidence["campaignIdentity"]["manifestSha256"] = "changed-campaign"
    elif mutation == "settings_service":
        evidence["coreServices"]["settingsService"] = False
    elif mutation == "window_service":
        evidence["coreServices"]["windowService"] = False
    elif mutation == "system_server":
        evidence["coreServices"]["systemServerPids"] = []
    elif mutation == "surface_flinger":
        evidence["coreServices"]["surfaceFlingerPids"] = ["unknown"]
    elif mutation == "boot_id":
        evidence["coreServices"]["bootId"] = "unknown"
    if mutation == "identity":
        evidence["identitySha256"] = "forged"
    else:
        evidence["identitySha256"] = _digest({key: value for key, value in evidence.items() if key != "identitySha256"})
    path.write_text(json.dumps(evidence))
    recovery["evidenceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    events.insert(2, recovery)
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is False
    assert result["coverageAudit"]["valid"] is False
    assert any("unproven_recovery_continuation" in error for error in result["coverageAudit"]["errors"])


def test_r12_initial_core_services_must_be_proven_before_starts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _, _ = _r12_fixture(tmp_path, monkeypatch)
    path = root / "run-metadata.json"
    metadata = json.loads(path.read_text())
    metadata["initialCoreServices"]["settingsService"] = False
    path.write_text(json.dumps(metadata))

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is False
    assert "initial_core_services_unusable" in result["coverageAudit"]["errors"]


def test_r12_core_identity_changes_are_diagnostic_not_pinned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)
    record = _change_terminal(root, manifest, events, 0, lambda value: value.update(invalidReason="invalid_protocol"))
    recovery = _recovery(root, manifest, events[1], record)
    path = root / recovery["evidence"]
    evidence = json.loads(path.read_text())
    evidence["coreServices"].update(bootId="00000000-0000-4000-8000-000000000002",
                                    systemServerPids=["789"], surfaceFlingerPids=["987"])
    evidence["identitySha256"] = _digest({key: value for key, value in evidence.items() if key != "identitySha256"})
    path.write_text(json.dumps(evidence))
    recovery["evidenceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    events.insert(2, recovery)
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["valid"] is True
    boundary = result["recoveryReferences"][0]
    assert boundary["bootChanged"] is True
    assert boundary["systemServerChanged"] is True
    assert boundary["surfaceFlingerChanged"] is True
    assert result["invalidBreakdown"] == {"invalid_protocol": 1}
    assert result["qualified"] is False


def _timezone_recovery(root: Path, manifest: dict, terminal: dict, record: dict) -> dict:
    recovery = _recovery(root, manifest, terminal, record)
    before_path = root / recovery["_beforeEvent"]["evidence"]
    before = json.loads(before_path.read_text())
    drift = {"qualified": False, "mismatches": {"timezone": {"expected": "UTC", "observed": "Asia/Shanghai"}},
             "device": {"timezone": "Asia/Shanghai"}}
    before["attestation"] = {**drift, "identitySha256": _digest(drift)}
    before["identitySha256"] = _digest({key: value for key, value in before.items() if key != "identitySha256"})
    before_path.write_text(json.dumps(before))
    recovery["_beforeEvent"]["evidenceSha256"] = hashlib.sha256(before_path.read_bytes()).hexdigest()
    path = root / recovery["evidence"]
    evidence = json.loads(path.read_text())
    evidence["beforeEvidence"]["sha256"] = recovery["_beforeEvent"]["evidenceSha256"]
    evidence["attestationBefore"] = before["attestation"]
    after = {"qualified": True, "mismatches": {}, "device": {"timezone": "UTC"}}
    evidence["attestation"] = {**after, "identitySha256": _digest(after)}
    evidence["remediation"] = {
        "name": "android_world.utils.datetime_utils.setup_datetime", "outcome": "completed",
        "environmentClose": "closed", "errors": [], "freezeDatetime": False,
        "allowedScope": ["auto_time", "auto_time_zone", "time_12_24", "timezone"],
        "startedAtUnix": terminal["completedAtUnix"], "completedAtUnix": terminal["completedAtUnix"],
    }
    _save_recovery(path, evidence, recovery)
    return recovery


def _save_recovery(path: Path, evidence: dict, recovery: dict) -> None:
    evidence["identitySha256"] = _digest({key: value for key, value in evidence.items() if key != "identitySha256"})
    path.write_text(json.dumps(evidence))
    recovery["evidenceSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("outcome", ["failed", "invalid_evaluator"])
def test_r12_v2_timezone_restoration_preserves_original_outcome(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, outcome: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch, "full")

    def mutate(record: dict) -> None:
        record["officialReward"] = 0.0 if outcome == "failed" else None
        if outcome == "invalid_evaluator":
            record["evaluator"] = None
        record["cleanup"]["agentSession"].pop("verificationStatus")

    record = _change_terminal(root, manifest, events, 0, mutate)
    original = (root / events[1]["result"]).read_bytes()
    recovery = _timezone_recovery(root, manifest, events[1], record)
    events.insert(2, recovery)
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["valid"] is True
    assert result["protocolIdentity"] == "r12.full_coverage_after_verified_recovery.v2"
    assert result["officialScore"] is None
    assert result["fullValidScore"] == (115 / 116 if outcome == "failed" else None)
    assert result["qualified"] is (outcome == "failed")
    assert result["episodes"][0]["classification"] == outcome
    assert result["episodes"][0]["officialReward"] == (0.0 if outcome == "failed" else None)
    assert result["coverageAudit"]["nullRewardCount"] == int(outcome == "invalid_evaluator")
    assert result["recoveryReferences"][0]["originalClassification"] == outcome
    assert result["recoveryReferences"][0]["originalCleanup"] == record["cleanup"]
    assert (root / events[1]["result"]).read_bytes() == original


@pytest.mark.parametrize("mutation", [
    "missing_before", "mutated_before", "missing_before_event", "before_copy", "before_binding",
    "before_identity", "before_sessions", "before_core", "unknown_cleanup", "other_drift", "wrong_expected",
    "action_name", "missing_action", "scope", "freeze", "action_failed", "action_errors", "close_unknown", "timestamps",
    "after_time", "after_identity", "after_readiness", "after_sessions", "after_core", "after_attestation", "reboot",
])
def test_r12_v2_remediation_requires_immutable_scoped_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str) -> None:
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)

    def mutate(record: dict) -> None:
        record["officialReward"] = 0.0
        if mutation == "unknown_cleanup":
            record["cleanup"]["environment"] = "unknown"

    record = _change_terminal(root, manifest, events, 0, mutate)
    recovery = _timezone_recovery(root, manifest, events[1], record)
    before_path = root / recovery["_beforeEvent"]["evidence"]
    before = json.loads(before_path.read_text())
    path = root / recovery["evidence"]
    evidence = json.loads(path.read_text())
    if mutation == "missing_before":
        before_path.unlink()
    elif mutation == "mutated_before":
        before["recordedAtUnix"] += 1
        before_path.write_text(json.dumps(before))
    elif mutation == "missing_before_event":
        del recovery["_beforeEvent"]
    elif mutation == "before_copy":
        evidence["attestationBefore"] = _attestation()
    elif mutation.startswith("before_") or mutation in {"other_drift", "wrong_expected"}:
        if mutation == "before_binding":
            before["resultSha256"] = "unrelated-result"
        elif mutation == "before_identity":
            before["campaignIdentity"]["verified"] = False
        elif mutation == "before_sessions":
            before["sessionAbsence"]["sessionHashes"] = ["live"]
        elif mutation == "before_core":
            before["coreServices"]["grpcReady"] = False
        elif mutation == "other_drift":
            before["attestation"]["mismatches"]["apiLevel"] = {"expected": 33, "observed": 34}
        else:
            before["attestation"]["mismatches"]["timezone"]["expected"] = "Europe/London"
        attestation = before["attestation"]
        attestation["identitySha256"] = _digest({key: value for key, value in attestation.items() if key != "identitySha256"})
        before["identitySha256"] = _digest({key: value for key, value in before.items() if key != "identitySha256"})
        before_path.write_text(json.dumps(before))
        recovery["_beforeEvent"]["evidenceSha256"] = hashlib.sha256(before_path.read_bytes()).hexdigest()
        evidence["beforeEvidence"]["sha256"] = recovery["_beforeEvent"]["evidenceSha256"]
        evidence.update({key + "Before": before[key] for key in (
            "attestation", "campaignIdentity", "sessionAbsence", "coreServices"
        )})
    elif mutation == "missing_action":
        del evidence["remediation"]
    elif mutation == "action_name":
        evidence["remediation"]["name"] = "shell.setprop"
    elif mutation == "scope":
        evidence["remediation"]["allowedScope"].append("clear_apps")
    elif mutation == "freeze":
        evidence["remediation"]["freezeDatetime"] = True
    elif mutation == "action_failed":
        evidence["remediation"]["outcome"] = "failed"
    elif mutation == "action_errors":
        evidence["remediation"]["errors"] = ["setup failed"]
    elif mutation == "close_unknown":
        evidence["remediation"]["environmentClose"] = "unknown"
    elif mutation == "timestamps":
        evidence["remediation"]["startedAtUnix"] = 1
    elif mutation == "after_time":
        evidence["recordedAtUnix"] = float("nan")
    elif mutation == "after_identity":
        evidence["campaignIdentity"]["manifestSha256"] = "another-manifest"
    elif mutation == "after_readiness":
        evidence["campaignIdentity"]["readinessIdentitySha256"] = "another-readiness"
    elif mutation == "after_sessions":
        evidence["sessionAbsence"]["sessionHashes"] = ["live"]
    elif mutation == "after_core":
        evidence["coreServices"] = []
    elif mutation == "after_attestation":
        evidence["attestation"] = []
    elif mutation == "reboot":
        evidence["coreServices"]["bootId"] = "00000000-0000-4000-8000-000000000002"
    _save_recovery(path, evidence, recovery)
    events.insert(2, recovery)
    _checkpoint(root, events)

    result = recalculate(root / "manifest.json", root)

    assert result["coverageAudit"]["valid"] is False
    assert result["qualified"] is False
    assert result["fullValidScore"] is None
    assert any("unproven_recovery_continuation" in error for error in result["coverageAudit"]["errors"])

def test_r12_v1_saved_protocol_identity_is_not_upgraded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _, _ = _r12_fixture(tmp_path, monkeypatch, version=1)

    result = recalculate(root / "manifest.json", root)

    assert result["qualified"] is True
    assert result["protocolIdentity"] == "r12.full_coverage_after_verified_recovery.v1"
    assert result["officialScore"] == 1.0

@pytest.mark.parametrize("unsafe", [None, "process", "pending", "unknown_creation"])
def test_v2_no_session_recovery_does_not_upgrade_invalid_agent_reward(tmp_path, monkeypatch, unsafe):
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch)

    def mutate(record):
        record["invalidReason"] = "invalid_agent"
        record["officialReward"] = None
        record["agent"].update({"processExited": unsafe != "process", "exitCode": 1, "agentCompleted": False})
        record["cleanup"]["agentSession"] = {"status": "not_created", "attribution": "none", "verificationStatus": "absent"}
        audit = {key: 0 for key in ("createdSessionCount", "deletedSessionCount", "activeSessionCount",
                                    "pendingRequestCount", "pendingCreateCount", "unknownCreationOutcomeCount")}
        audit.update({"errors": [], "createdSessionHashes": [], "deletedSessionHashes": []})
        if unsafe == "pending":
            audit["pendingRequestCount"] = 1
        elif unsafe == "unknown_creation":
            audit["unknownCreationOutcomeCount"] = 1
        record["appiumSessionAudit"] = audit

    record = _change_terminal(root, manifest, events, 0, mutate)
    events.insert(2, _recovery(root, manifest, events[1], record))
    _checkpoint(root, events)
    result = recalculate(root / "manifest.json", root)
    assert result["episodes"][0]["officialReward"] is None
    assert result["invalidBreakdown"] == {"invalid_agent": 1}
    assert result["qualified"] is False
    rejected = any("unproven_recovery_continuation" in error for error in result["coverageAudit"]["errors"])
    assert rejected is (unsafe is not None)


def _attach_submission(result_file: Path, record: dict, business_seconds: int) -> None:
    from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission

    text = json.dumps({"taskOutcome": "fixture answer"})
    raw = result_file.parent / "raw-private"
    raw.mkdir()
    event = {"type": "message_end", "message": {"role": "assistant", "stopReason": "stop",
             "content": [{"type": "text", "text": text}]}}
    event_bytes = (json.dumps(event) + "\n").encode()
    (raw / "agent-events.jsonl").write_bytes(event_bytes)
    report = parse_submission(text)
    payload = json.dumps(report).encode()
    (raw / "business-submission.json").write_bytes(payload)
    evidence = {"protocol": ANSWER_SUBMISSION_PROTOCOL,
                "path": "raw-private/business-submission.json", "sha256": hashlib.sha256(payload).hexdigest(),
                "receipt": {"eventSequence": 1, "receivedAtSeconds": 0.1, "phase": "business"},
                "cutoffSeconds": 0.2, "businessDeadlineSeconds": business_seconds,
                "finalizationStartedAtSeconds": None, "finalizationDeadlineSeconds": None,
                "cleanupRequestedAtSeconds": 0.2, "ignoredFinalMessages": 0}
    record["agent"]["answerSubmission"] = evidence
    record["agent"]["rawEventsSha256"] = hashlib.sha256(event_bytes).hexdigest()
    record["agentAnswer"] = {key: report[key] for key in ("validContract", "reason", "taskOutcomeType", "sha256")}
    record["agentAnswer"]["rawSubmission"] = {"path": evidence["path"], "sha256": evidence["sha256"]}
    result_file.write_text(json.dumps(record))


@pytest.mark.parametrize("mutation", [None, "late", "cleanup", "extended_window", "missing_policy", "wrong_type", "raw_changed", "event_changed"])
def test_new_submission_protocol_binds_business_receipt_and_original_bytes(tmp_path, monkeypatch, mutation):
    root, manifest, events = _r12_fixture(tmp_path, monkeypatch, revision=13)

    def mutate(record):
        evidence = record["agent"]["answerSubmission"]
        if mutation == "late":
            evidence["receipt"]["receivedAtSeconds"] = evidence["cutoffSeconds"] + 1
        elif mutation == "cleanup":
            evidence["receipt"]["phase"] = "cleanup"
        elif mutation == "extended_window":
            evidence.update(finalizationStartedAtSeconds=0, finalizationDeadlineSeconds=121)
        elif mutation == "missing_policy":
            record["protocol"].pop("answerSubmission")
        elif mutation == "wrong_type":
            record["agentAnswer"]["taskOutcomeType"] = "number"

    _change_terminal(root, manifest, events, 0, mutate)
    raw = root / "episodes/000-Task000/attempt-1/raw-private"
    if mutation == "raw_changed":
        (raw / "business-submission.json").write_text(json.dumps({"rawText": "changed"}))
    elif mutation == "event_changed":
        (raw / "agent-events.jsonl").write_text(json.dumps({"type": "agent_end"}))
    _checkpoint(root, events)
    result = recalculate(root / "manifest.json", root)
    assert result["protocolIdentity"] == "r13.full_coverage_after_verified_recovery.v2"
    assert result["qualified"] is (mutation is None)
    assert result["coverageAudit"]["valid"] is (mutation is None)

