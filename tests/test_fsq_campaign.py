"""Offline consumer tests: collaborators never discover devices or invoke FSQ."""
import argparse
import copy
from contextlib import nullcontext
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from fsq_androidworld_eval import fsq_campaign as campaign
from fsq_androidworld_eval.fsq_native import NativeDispatchBudget
from fsq_androidworld_eval.fsq_evidence import validate_native_evidence
from fsq_androidworld_eval.fsq_runner import native_episode_id
from fsq_androidworld_eval.lifecycle import episode_time_budget


NOW = 1000.0


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(campaign._bytes(value) + b"\n")
    return path


def ref(root, path):
    return {"path": str(path.relative_to(root)), "sha256": campaign._hash(path), "bytes": path.stat().st_size}


def reseal(path, mutate):
    value = campaign._load(path)
    value.pop("identitySha256", None)
    mutate(value)
    put(path, campaign._sealed(value))


@pytest.fixture
def candidate(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign.time, "time", lambda: NOW)
    names = list(campaign.CALIBRATION_TASKS) + [f"OfficialTask{i:03d}" for i in range(104)]
    manifest = {
        "campaignId": "offline-fsq-campaign",
        "kind": "fsq_androidworld", "identities": {"nativeProviderMetadata": {"provider": "github_copilot", "model": "gpt-6.1-sol"}},
        "target": {"serial": "emulator-5560", "consolePort": 5560, "grpcPort": 8560, "adbPath": "/never-run/adb"},
        "paths": {"project": str(tmp_path), "evaluatorSite": str(tmp_path / "isolated-site")},
        "tasks": [{"index": i, "name": name, "paramsSha256": campaign._digest({"fixture": i}),
                   "apps": ["clock"], "maxActions": 10, "maxSteps": 10,
                   "timeBudget": episode_time_budget(10)} for i, name in enumerate(names)],
    }
    manifest_path = put(tmp_path / "manifest.json", manifest)
    review = put(tmp_path / "review.json", {"kind": "independent_native_adapter_review", "approved": True})
    model = put(tmp_path / "native-model.json", {"kind": "native_fsq_responses_receipt", "requestedModel": "gpt-6.1-sol"})
    authorization = {"schemaVersion": 1, "kind": "fsq_execution_authorization",
        "manifestSha256": campaign._hash(manifest_path), "approvedStages": ["qualify", "rehearse", "calibrate", "run"],
        "independentReview": {"status": "approved", "path": str(review), "sha256": campaign._hash(review)},
        "nativeModelCall": {"status": "passed_native_responses", "provider": "github_copilot", "requestedModel": "gpt-6.1-sol",
                            "path": str(model), "sha256": campaign._hash(model)},
        "resource": {**manifest["target"], "exclusive": True, "disposable": True, "mutationsAllowed": True,
                     "notBeforeUnix": 0, "validUntilUnix": 10**9, "authority": "explicit test coordinator"}}
    authorization_path = put(tmp_path / "authorization.json", authorization)
    readiness = {"schemaVersion": 1, "kind": campaign.READINESS_KIND,
        "binding": campaign._binding(manifest_path, manifest, authorization),
        "startedAtUnix": 900, "completedAtUnix": 950, "qualified": True, "error": None,
        "checks": {name: True for name in ("assets", "apps", "snapshots", "baseData", "utc", "coreEnvironment", "adbIsolation")},
        "apps": [{"name": "clock", "package": "fixture.clock", "versions": ["versionCode=1"], "apks": [{"sha256": "a" * 64}]}],
        "snapshotRestores": [{"app": "clock", "status": "restored"}],
        "cleanup": {"environment": "closed"}, "environmentArtifacts": {"fixturePinned": "sha256"},
        "device": {"fixture": "offline"}, "clock": dict(campaign.CLOCK_BASELINE)}
    readiness_path = put(tmp_path / "readiness.json", campaign._sealed(readiness))
    return SimpleNamespace(root=tmp_path, manifest=manifest, manifest_path=manifest_path,
                           auth=authorization, auth_path=authorization_path, readiness_path=readiness_path)


def consume_readiness(candidate, **kwargs):
    return campaign.validate_readiness(candidate.readiness_path, candidate.manifest_path,
                                       candidate.manifest, candidate.auth, now=NOW, **kwargs)


def rehearsal_record(candidate, spec):
    return {"schemaVersion": 1, "kind": "fsq_androidworld_rehearsal_task",
        "task": campaign._task_identity(spec), "manifestSha256": campaign._hash(candidate.manifest_path),
        "agentInvoked": False, "officialReward": None, "complete": True, "error": None,
        "stages": ["environment", "initialize_task", "is_successful", "tear_down", "close"],
        "evaluatorProbe": 0.0, "cleanup": {"taskTearDown": "completed", "environment": "closed"}}


def native_record(candidate, spec, root, *, reward=0.0, business_status="failed", writes=0, stage="calibrate",
                  runner_failed=False, evaluator_exception=False, worker_exit=0,
                  runtime_status="completed", native_status=None):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    private = root / "raw-private"
    private.mkdir(exist_ok=True)
    task_id = native_episode_id(candidate.manifest["campaignId"], stage, spec["index"])
    task_status = native_status or ("error" if runner_failed else business_status)
    verification_value = {"status": business_status, "summary": "native verification"}
    task_path = put(private / "native-task.json", {"task_id": task_id, "status": task_status,
        "verification": verification_value, "steps": [
        {"tool_name": "agent_runtime.pre_plan", "status": "success", "tool_output": {"summary": "not the source"}},
        {"tool_name": "agent_runtime.runner", "status": "failed" if runner_failed else "success",
         "tool_output": {"failure_reason": "Agent exceeded the configured turn limit."} if runner_failed else {
            "schema_version": "task_run_v1", "status": business_status, "summary": "exact parsed summary"}}]})
    verification = put(private / "verification.json", verification_value)
    diagnostic = put(private / "evaluator.json", {"task": {"name": spec["name"], "paramsSha256": spec["paramsSha256"]},
                                                "officialReward": reward,
                                                "outcome": "exception" if evaluator_exception else "returned"})
    def native_ref(path):
        return {"path": str(path), "sha256": campaign._hash(path), "sizeBytes": path.stat().st_size,
                "visibility": "evaluator_private"}
    audit = private / "audit.jsonl"
    audit.write_text("")
    budget = NativeDispatchBudget(spec["maxActions"], 100, clock=lambda: 1, journal=audit)
    for i in range(writes):
        budget.dispatch("tap_at", "action", lambda: SimpleNamespace(status="failed"), step_id=str(i))
    budget.receipt({"event": "native_execution_returned", "taskId": task_id, "nativeTaskId": task_id,
                    "taskStatus": task_status, "verificationObserved": True, "verificationStatus": business_status})
    snapshot = budget.snapshot()
    result = {"schemaVersion": 1, "taskId": task_id, "status": runtime_status,
        "nativeTarget": {"effectiveProvider": "github_copilot", "effectiveModel": "gpt-6.1-sol",
                         "serial": candidate.manifest["target"]["serial"]},
        "fsq": {"completeDynamicExecutionReturned": True, "taskResult": native_ref(task_path),
                "verification": native_ref(verification), "status": task_status},
        "mainAnswer": {"status": "failed", "source": campaign.ANSWER_SOURCE} if runner_failed else {
            "status": "valid", "summary": "exact parsed summary", "businessStatus": business_status,
            "source": campaign.ANSWER_SOURCE},
        "actionBudget": snapshot, "actionAudit": native_ref(audit), "cleanup": {"closeReceipts": []}}
    process = {"spawnCount": 1, "workerExitObserved": True, "exitCode": worker_exit, "terminated": False, "killed": False,
               "groupCleanup": "settled", "businessDeadlineReached": False, "pgid": 999999}
    process_path = put(private / "worker-process.json", process)
    outcome = {"process": process, "result": result}
    proof = validate_native_evidence(outcome, episode_root=root, expected_task_id=task_id,
                                     expected_serial=candidate.manifest["target"]["serial"], maximum=spec["maxActions"])
    outcome_path = put(private / "outcome.json", outcome)
    classification = ("invalid_agent" if worker_exit or runtime_status != "completed" else
                      "invalid_evaluator" if evaluator_exception else "passed" if reward == 1 else "failed")
    record = {"schemaVersion": 1, "kind": "fsq_androidworld_episode", "attempt": 1,
        "stage": stage, "campaignId": candidate.manifest["campaignId"], "episodeId": task_id,
        "target": candidate.manifest["target"], "readinessSha256": campaign._hash(candidate.readiness_path),
        "authorizationSha256": campaign._digest(candidate.auth),
        "task": campaign._task_identity(spec), "manifestSha256": campaign._hash(candidate.manifest_path),
        "attemptStarted": True, "complete": True, "classification": classification, "officialReward": reward,
        "workerSpawnAttempted": True, "workerProcess": process, "workerProcessReference": ref(root, process_path),
        "evidenceFailure": None, "cleanup": {"taskTearDown": "completed", "environment": "closed", "workerProcessGroup": "settled"},
        "fsq": {"privateOutcome": ref(root, outcome_path), "killEvidence": proof["killEvidence"],
                "nativeStatus": task_status,
                "mainAnswer": {key: value for key, value in proof["answer"].items() if key != "summary"}}, "evaluatorCalls": 1,
        "evaluator": {"called": True, "afterFullFsq": True, "implementation": "android_world.task_eval.is_successful",
                      "ordering": "after_complete_native_FSQ_return_and_internal_verification", "diagnostics": ref(root, diagnostic)}}
    if evaluator_exception:
        record["error"] = {"type": "RuntimeError"}
    return record


def consume_episode(candidate, record, spec, root, *, stage="calibrate"):
    return campaign.operational_errors(record, spec, campaign._hash(candidate.manifest_path), episode_dir=root,
                                       stage=stage, manifest=candidate.manifest,
                                       readiness_sha=campaign._hash(candidate.readiness_path),
                                       authorization_sha=campaign._digest(candidate.auth))


def stage_report(candidate, stage, *, directory=None):
    directory = directory or candidate.root / stage
    directory.mkdir()
    attempts, records = [], []
    specs = campaign._selected(candidate.manifest, stage)
    for spec in specs:
        root = directory / "episodes" / f"{spec['index']:03d}-{spec['name']}"
        record = rehearsal_record(candidate, spec) if stage == "rehearse" else native_record(candidate, spec, root, stage=stage)
        put(root / "result.json", record)
        records.append(record)
        attempts.append({"attemptId": f"{stage}-{spec['index']}", "task": campaign._task_identity(spec),
                         "directory": str(root.relative_to(directory)), "artifacts": campaign._artifact_rows(root),
                         "outerProcess": {"forced": False}, "operationalErrors": []})
    report = {"schemaVersion": 1, "kind": campaign.REPORT_KINDS[stage],
        "binding": campaign._binding(candidate.manifest_path, candidate.manifest, candidate.auth),
        "readinessSha256": campaign._hash(candidate.readiness_path), "startedAtUnix": 900, "completedAtUnix": 950,
        "taskCount": len(specs), "taskSetSha256": campaign._digest([campaign._task_identity(spec) for spec in specs]),
        "attempts": attempts, "qualified": True, "haltReason": None,
        "summary": campaign._summary(stage, attempts, records, len(specs))}
    return put(directory / "report.json", campaign._sealed(report))


def consume_stage(candidate, path, stage):
    return campaign.validate_stage_report(path, stage, candidate.manifest_path, candidate.manifest,
                                          candidate.auth, readiness_path=candidate.readiness_path, now=NOW)


def args_for(candidate, stage, *, rehearsal=None, calibration=None):
    return argparse.Namespace(stage=stage, project=str(candidate.root), manifest=str(candidate.manifest_path),
        authorization=str(candidate.auth_path), output=str(candidate.root / f"execution-{stage}"),
        readiness=str(candidate.readiness_path), rehearsal=str(rehearsal) if rehearsal else None,
        calibration=str(calibration) if calibration else None)


def offline_execution(candidate, monkeypatch, *, first_cleanup=None, forced=False, drift_after=None, native_failure=None,
                      first_native_options=None, rewards=(0.0,), after_attempt=None, mutate_record=None, outer_exit=0):
    calls = []
    def load_candidate(*_):
        if drift_after is not None and len(calls) >= drift_after:
            raise ValueError("frozen global source drift")
        return copy.deepcopy(candidate.manifest)
    monkeypatch.setattr(campaign, "_load_candidate", load_candidate)
    monkeypatch.setattr(campaign, "_runner_api", lambda: SimpleNamespace(load_authorization=lambda *_: copy.deepcopy(candidate.auth)))
    def spawn(command, output, timeout):
        index = int(command[command.index("--task-index") + 1])
        root = Path(command[command.index("--output") + 1])
        stage = command[command.index("--stage") + 1]
        spec = candidate.manifest["tasks"][index]
        options = dict(first_native_options or {}) if not calls else {}
        options.setdefault("reward", rewards[len(calls) % len(rewards)])
        record = rehearsal_record(candidate, spec) if stage == "rehearse" else native_record(candidate, spec, root, stage=stage, **options)
        if first_cleanup and not calls:
            record["cleanup"]["environment"] = first_cleanup
        if native_failure and not calls:
            record["workerProcess"].update(terminated=True, exitCode=-15)
            process_path = root / record["workerProcessReference"]["path"]
            put(process_path, record["workerProcess"])
            record["workerProcessReference"] = ref(root, process_path)
            record.update(fsq=None, evidenceFailure=native_failure, classification="invalid_agent",
                          officialReward=None, evaluatorCalls=0, evaluator={"called": False})
        if mutate_record is not None:
            mutate_record(record)
        put(root / "result.json", record)
        (output / "process.log").write_text("offline collaborator\n")
        calls.append({"index": index, "timeout": timeout, "root": root, "resultBytes": (root / "result.json").read_bytes()})
        if after_attempt is not None:
            after_attempt(record)
        return {"forced": forced, "exitCode": -9 if forced else outer_exit, "spawnCount": 1, "timeoutSeconds": timeout}
    monkeypatch.setattr(campaign, "_spawn", spawn)
    return calls


def test_readiness_consumes_only_new_exact_native_receipt(candidate):
    assert consume_readiness(candidate)["kind"] == campaign.READINESS_KIND
    reseal(candidate.readiness_path, lambda row: row.update(kind="amkernel_readiness"))
    with pytest.raises(ValueError, match="FSQ-only"):
        consume_readiness(candidate)


def test_missing_readiness_is_not_replaced_by_old_campaign_evidence(candidate):
    candidate.readiness_path.unlink()
    put(candidate.root / "old-amkernel-ready.json", {"qualified": True, "positiveCalls": 500})
    with pytest.raises(FileNotFoundError):
        consume_readiness(candidate)


@pytest.mark.parametrize("field,value", [("nativeModelCall", {}), ("independentReview", {}),
    ("nativeModelCall", {"status": "passed_amkernel", "provider": "github_copilot", "requestedModel": "gpt-6.1-sol"})])
def test_missing_or_unrelated_model_review_approval_fails(candidate, field, value):
    candidate.auth[field] = value
    with pytest.raises(ValueError, match="approval missing"):
        consume_readiness(candidate)


@pytest.mark.parametrize("field", ["serial", "consolePort", "grpcPort", "adbPath"])
def test_resource_and_target_identity_drift_fails(candidate, field):
    candidate.manifest["target"][field] = "drift" if field in {"serial", "adbPath"} else 9999
    with pytest.raises(ValueError, match="resource target drift"):
        consume_readiness(candidate)


def test_exact_manifest_bytes_and_receipt_hashes_are_bound(candidate):
    candidate.manifest_path.write_bytes(candidate.manifest_path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="exact FSQ"):
        consume_readiness(candidate)


def test_review_receipt_mutation_is_not_approval(candidate):
    Path(candidate.auth["independentReview"]["path"]).write_text("changed review")
    with pytest.raises(ValueError, match="receipt hash drift"):
        consume_readiness(candidate)


@pytest.mark.parametrize("prerequisite", ["assets", "apps", "snapshots", "baseData", "utc", "coreEnvironment", "adbIsolation"])
def test_every_actual_readiness_prerequisite_is_required(candidate, prerequisite):
    reseal(candidate.readiness_path, lambda row: row["checks"].pop(prerequisite))
    with pytest.raises(ValueError, match="actual prerequisite"):
        consume_readiness(candidate)


@pytest.mark.parametrize("change", [
    lambda row: row.update(startedAtUnix=-1),
    lambda row: row["apps"].clear(), lambda row: row["snapshotRestores"].clear(),
    lambda row: row["cleanup"].update(environment="unknown"),
])
def test_stale_incomplete_or_unclean_readiness_fails(candidate, change):
    reseal(candidate.readiness_path, change)
    with pytest.raises(ValueError):
        consume_readiness(candidate)


def test_all_116_official_lifecycles_are_a_separate_non_agent_gate(candidate):
    path = stage_report(candidate, "rehearse")
    report = consume_stage(candidate, path, "rehearse")
    assert report["taskCount"] == 116
    assert report["summary"]["policyProven"] is False
    assert report["summary"]["reward"]["count"] == 0
    assert report["summary"]["officialLeaderboardClaim"] is False


@pytest.mark.parametrize("change", [
    lambda row: row["attempts"].pop(), lambda row: row.update(taskCount=115),
    lambda row: row["attempts"][0]["task"].update(paramsSha256="drift"),
    lambda row: row.update(taskSetSha256="wrong"),
    lambda row: row["attempts"][1].update(attemptId=row["attempts"][0]["attemptId"]),
    lambda row: row["attempts"][0].update(outerProcess={"forced": True}),
])
def test_rehearsal_consumer_rejects_coverage_hash_unique_attempt_drift(candidate, change):
    path = stage_report(candidate, "rehearse")
    reseal(path, change)
    with pytest.raises(ValueError):
        consume_stage(candidate, path, "rehearse")


def test_rehearsal_artifact_tampering_is_not_hidden_by_qualified_boolean(candidate):
    path = stage_report(candidate, "rehearse")
    result = next((path.parent / "episodes").glob("*/result.json"))
    put(result, {"qualified": True, "kind": "harness_rehearsal_task"})
    with pytest.raises(ValueError, match="artifact coverage/hash drift"):
        consume_stage(candidate, path, "rehearse")


def test_original12_calibration_accepts_failed_rewards_and_zero_positive_calls(candidate):
    path = stage_report(candidate, "calibrate")
    report = consume_stage(candidate, path, "calibrate")
    assert [row["task"]["name"] for row in report["attempts"]] == list(campaign.CALIBRATION_TASKS)
    assert report["summary"]["reward"] == {"count": 12, "sum": 0.0, "mean": 0.0,
        "denominator": "valid_official_rewards_only", "diagnosticOnly": True}
    assert report["qualified"] is True


@pytest.mark.parametrize("business_status", ["success", "failed", "inconclusive"])
def test_payload_business_failure_is_not_protocol_call_failure(candidate, business_status):
    spec = candidate.manifest["tasks"][0]
    root = candidate.root / business_status
    record = native_record(candidate, spec, root, business_status=business_status, writes=1)
    assert consume_episode(candidate, record, spec, root) == []
    assert record["officialReward"] == 0




def test_calibration_rejects_private_source_or_evaluator_artifact_drift(candidate):
    spec = candidate.manifest["tasks"][0]
    root = candidate.root / "artifact-drift"
    record = native_record(candidate, spec, root)
    (root / "raw-private" / "native-task.json").write_text("changed native source")
    assert "native_evidence" in consume_episode(candidate, record, spec, root)


def test_full_requires_fresh_readiness_all116_and_original12_before_any_spawn(candidate, monkeypatch):
    calls = offline_execution(candidate, monkeypatch)
    args = args_for(candidate, "run")
    with pytest.raises(ValueError, match="all-116"):
        campaign.run_stage(args)
    assert calls == []
    assert not Path(args.output).exists()
    args.rehearsal = str(stage_report(candidate, "rehearse"))
    with pytest.raises(ValueError, match="original-12"):
        campaign.run_stage(args)
    assert calls == []


def test_full_runs_each_once_preserves_failed_rewards_and_streams_diagnostic_summary(candidate, monkeypatch, capsys):
    rehearsal = stage_report(candidate, "rehearse")
    calibration = stage_report(candidate, "calibrate")
    calls = offline_execution(candidate, monkeypatch)
    args = args_for(candidate, "run", rehearsal=rehearsal, calibration=calibration)
    assert campaign.run_stage(args) == 0
    report_path = Path(args.output) / "report.json"
    report = consume_stage(candidate, report_path, "run")
    assert [call["index"] for call in calls] == list(range(116))
    assert all(call["timeout"] == 720 + 610 for call in calls)
    assert report["summary"]["reward"]["count"] == 116
    assert report["summary"]["reward"]["mean"] == 0
    assert report["summary"]["classifications"] == {"failed": 116}
    assert len({row["attemptId"] for row in report["attempts"]}) == 116
    assert report["prerequisites"]["calibration"]["sha256"] == campaign._hash(calibration)
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert events[0]["event"] == "stage_started"
    assert sum(row["event"] == "attempt_started" for row in events) == 116
    assert events[-1]["event"] == "stage_completed"
    assert events[-1]["reportSha256"] == campaign._hash(report_path)
    with pytest.raises(FileExistsError):
        campaign.run_stage(args)
    assert len(calls) == 116


@pytest.mark.parametrize("cleanup,forced,reason", [("unknown", False, "unknown_or_failed_cleanup"),
    (None, True, "forced_worker"), ("failed:CloseError", True, "unknown_or_failed_cleanup")])
def test_unknown_cleanup_or_forced_worker_halts_without_retry_and_preserves_terminal(candidate, monkeypatch, cleanup, forced, reason):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, first_cleanup=cleanup, forced=forced)
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1
    assert report["haltReason"] == reason
    assert report["summary"]["reward"]["count"] == 1
    assert report["summary"]["reward"]["mean"] == 0
    assert (calls[0]["root"] / "result.json").read_bytes() == calls[0]["resultBytes"]
    assert report["qualified"] is False


def test_global_identity_drift_stops_before_next_attempt_and_keeps_coverage(candidate, monkeypatch):
    calls = offline_execution(candidate, monkeypatch, drift_after=1)
    args = args_for(candidate, "rehearse")
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1
    assert report["haltReason"] == "global_identity_drift"
    assert report["summary"]["attempted"] == 1
    assert report["summary"]["expected"] == 116

@pytest.mark.parametrize("options,reason,classification,reward", [
    ({"reward": 1.0, "runner_failed": True}, "exact_main_summary", "passed", 1.0),
    ({"reward": None, "evaluator_exception": True}, "invalid_evaluator", "invalid_evaluator", None),
    ({"reward": 1.0, "worker_exit": 7}, "invalid_agent", "invalid_agent", 1.0),
    ({"reward": 1.0, "runtime_status": "error"}, "invalid_agent", "invalid_agent", 1.0),
    ({"reward": 1.0, "native_status": "error"}, "native_runtime_error", "passed", 1.0),
])
def test_native_contract_failure_stops_dispatch_and_preserves_original_lines(
        candidate, monkeypatch, capsys, options, reason, classification, reward):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, first_native_options=options)
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert [call["index"] for call in calls] == [0]
    assert report["haltReason"] == reason and report["qualified"] is False
    assert report["summary"]["coverage"] == 1 / 12
    assert report["summary"]["classifications"] == {classification: 1}
    assert report["summary"]["reward"]["sum"] == (reward if reward is not None else 0)
    assert report["summary"]["reward"]["count"] == int(reward is not None)
    terminal = campaign._load(calls[0]["root"] / "result.json")
    assert terminal["classification"] == classification and terminal["officialReward"] == reward
    assert terminal["cleanup"]["taskTearDown"] == "completed" and terminal["cleanup"]["environment"] == "closed"
    assert (calls[0]["root"] / "result.json").read_bytes() == calls[0]["resultBytes"]
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [event["event"] for event in events] == [
        "stage_started", "attempt_started", "attempt_completed", "stage_halted", "stage_completed"]
    assert report["attempts"][0]["operationalErrors"]


def test_consumed_identity_error_stops_even_when_native_and_reward_succeed(candidate, monkeypatch):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, rewards=(1.0,),
                              mutate_record=lambda record: record.update(episodeId="wrong-episode"))
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1 and report["haltReason"] == "episode_identity_binding"
    assert "episode_identity_binding" in report["attempts"][0]["operationalErrors"]
    assert report["summary"]["reward"]["sum"] == 1.0


def test_nonzero_outer_exit_stops_after_clean_terminal_record(candidate, monkeypatch):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, rewards=(1.0,), outer_exit=7)
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1 and report["haltReason"] == "outer_process_exit"
    assert report["attempts"][0]["operationalErrors"] == ["outer_process_exit"]
    assert report["summary"]["classifications"] == {"passed": 1}
    assert report["summary"]["reward"]["sum"] == 1.0


def test_legal_zero_and_partial_rewards_continue_without_retry(candidate, monkeypatch):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, rewards=(0.0, 0.5))
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 0
    report = consume_stage(candidate, Path(args.output) / "report.json", "calibrate")
    assert [call["index"] for call in calls] == list(range(12))
    assert report["haltReason"] is None and report["qualified"] is True
    assert report["summary"]["reward"]["sum"] == 3.0
    assert report["summary"]["reward"]["count"] == 12


@pytest.mark.parametrize("before_first", [True, False])
def test_cli_stop_file_is_a_boundary_request_not_an_episode_failure(candidate, monkeypatch, before_first):
    rehearsal = stage_report(candidate, "rehearse")
    stop_file = candidate.root / "operator.stop"
    if before_first:
        stop_file.touch()
    calls = offline_execution(candidate, monkeypatch, rewards=(0.5,),
                              after_attempt=lambda record: stop_file.touch())
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    argv = ["calibrate", "--project", args.project, "--manifest", args.manifest,
            "--authorization", args.authorization, "--output", args.output,
            "--readiness", args.readiness, "--rehearsal", str(rehearsal), "--stop-file", str(stop_file)]
    assert campaign.main(argv) == 2
    report = campaign._load(Path(args.output) / "report.json")
    expected = 0 if before_first else 1
    assert len(calls) == expected and report["summary"]["attempted"] == expected
    assert report["summary"]["coverage"] == expected / 12
    assert report["haltReason"] == "stop_requested" and report["qualified"] is False
    assert report["summary"]["reward"]["sum"] == (0 if before_first else 0.5)
    assert stop_file.exists()
    if calls:
        assert campaign._load(calls[0]["root"] / "result.json")["cleanup"]["environment"] == "closed"


def test_cleanup_failure_takes_precedence_over_pending_operator_stop_and_main_error(candidate, monkeypatch):
    rehearsal = stage_report(candidate, "rehearse")
    stop_file = candidate.root / "operator.stop"
    calls = offline_execution(candidate, monkeypatch, first_cleanup="failed:CloseError",
                              first_native_options={"reward": 1.0, "runner_failed": True},
                              after_attempt=lambda record: stop_file.touch())
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    args.stop_file = str(stop_file)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1 and report["haltReason"] == "unknown_or_failed_cleanup"
    assert report["summary"]["reward"]["sum"] == 1.0
    assert "exact_main_summary" in report["attempts"][0]["operationalErrors"]



def test_terminal_save_never_overwrites_previous_failure(tmp_path):
    path = tmp_path / "terminal.json"
    campaign._save(path, {"qualified": False, "failure": "preserve me"})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        campaign._save(path, {"qualified": True})
    assert path.read_bytes() == before


def test_parser_keeps_live_stages_explicit_and_requires_authorization():
    parser = campaign.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["qualify", "--manifest", "manifest.json", "--output", "new-stage"])
    args = parser.parse_args(["calibrate", "--manifest", "manifest.json", "--output", "new-stage", "--authorization", "grant.json"])
    assert args.stage == "calibrate"


def test_freshness_uses_explicit_resource_grant_not_an_arbitrary_day_limit(candidate):
    report = campaign.validate_readiness(candidate.readiness_path, candidate.manifest_path,
                                         candidate.manifest, candidate.auth, now=200000)
    assert report["qualified"] is True


@pytest.mark.parametrize("field,value", [("exclusive", False), ("disposable", False),
                                         ("mutationsAllowed", False), ("validUntilUnix", NOW)])
def test_no_mutating_stage_without_live_disposable_exclusive_grant(candidate, field, value):
    candidate.auth["resource"][field] = value
    with pytest.raises(ValueError):
        consume_readiness(candidate)


def qualification_collaborators(candidate, monkeypatch, *, missing_app=False, missing_base=False, close_failure=False):
    events = []
    def create(**kwargs):
        events.append(("environment", kwargs))
        return SimpleNamespace(controller=object(), get_state=lambda **_: SimpleNamespace(pixels=object()))
    def close(_):
        events.append(("close",))
        if close_failure:
            raise RuntimeError("unknown environment cleanup")
    environment = SimpleNamespace(artifact_identity=lambda _: {"fixturePinned": "sha256"},
        close_environment=close, load_environment=create, strict_snapshot_restores=nullcontext)
    adb = SimpleNamespace(issue_generic_request=lambda *_: SimpleNamespace(generic=SimpleNamespace(output=b"FSQ_NATIVE_ADB_CAPTURE")),
                          check_ok=lambda *_: None)
    snapshots = SimpleNamespace(restore_snapshot=lambda name, _: events.append(("restore", name)))
    monkeypatch.setitem(sys.modules, "fsq_androidworld_eval.environment", environment)
    monkeypatch.setitem(sys.modules, "android_world.env", SimpleNamespace(adb_utils=adb))
    monkeypatch.setitem(sys.modules, "android_world.utils", SimpleNamespace(app_snapshot=snapshots))
    def probe(_):
        events.append(("read_only_probe",))
        if missing_app:
            raise RuntimeError("required installed app missing: clock; no install fallback")
        ready = campaign._load(candidate.readiness_path)
        return {"device": ready["device"], "apps": ready["apps"], "clock": ready["clock"]}
    def base(*_):
        events.append(("base_data",))
        if missing_base:
            raise RuntimeError("required app-created database missing; provision outside qualification")
        return [{"app": "clock", "present": True}]
    monkeypatch.setattr(campaign, "_device_probe", probe)
    monkeypatch.setattr(campaign, "_base_data", base)
    return events


def test_missing_installed_app_fails_before_staging_without_any_repair(candidate, monkeypatch):
    events = qualification_collaborators(candidate, monkeypatch, missing_app=True)
    report = campaign._qualification(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["qualified"] is False
    assert "installed app missing" in report["error"]["message"]
    assert events == [("read_only_probe",)]
    assert report["cleanup"]["environment"] == "not_created"


def test_missing_app_created_base_data_is_not_fabricated(candidate, monkeypatch):
    events = qualification_collaborators(candidate, monkeypatch, missing_base=True)
    report = campaign._qualification(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["qualified"] is False
    assert "app-created database missing" in report["error"]["message"]
    assert report["checks"].get("baseData") is not True
    assert ("restore", "clock") in events
    assert events[-1] == ("close",)
    assert report["cleanup"]["environment"] == "closed"


def test_real_qualification_checks_never_override_unknown_environment_cleanup(candidate, monkeypatch):
    qualification_collaborators(candidate, monkeypatch, close_failure=True)
    report = campaign._qualification(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["qualified"] is False
    assert report["cleanup"]["environment"] == "unknown"
    assert report["error"]["message"] == "official environment cleanup failed"


@pytest.mark.parametrize("primary_phase,cleanup_phases", [
    ("initialize_task", ("tear_down", "close")),
    ("is_successful", ("tear_down",)),
    (None, ("tear_down", "close")),
    (None, ("close",)),
    (None, ()),
])
def test_rehearsal_preserves_primary_error_and_independent_cleanup_errors(
        candidate, monkeypatch, primary_phase, cleanup_phases):
    events = []
    def operation(phase):
        events.append(phase)
        if phase == primary_phase:
            raise ValueError("primary:" + phase)
        if phase in cleanup_phases:
            raise RuntimeError("cleanup:" + phase)
        return 0.0
    task = SimpleNamespace(app_names=["clock"],
        initialize_task=lambda _: operation("initialize_task"),
        is_successful=lambda _: operation("is_successful"),
        tear_down=lambda _: operation("tear_down"))
    env = SimpleNamespace(reset=lambda **_: None)
    monkeypatch.setitem(sys.modules, "fsq_androidworld_eval.environment", SimpleNamespace(
        load_environment=lambda **_: env, close_environment=lambda _: operation("close"),
        restore_shared_assets=lambda *_: [], strict_snapshot_restores=nullcontext))
    monkeypatch.setitem(sys.modules, "fsq_androidworld_eval.fsq_manifest",
                        SimpleNamespace(task_from_spec=lambda _: task))
    record = campaign._rehearsal_task(candidate.manifest_path, candidate.manifest,
                                      candidate.manifest["tasks"][0], candidate.root)
    assert record["error"] == ({"type": "ValueError", "message": "primary:" + primary_phase}
                               if primary_phase else None)
    assert record["cleanupErrors"] == [{"phase": phase, "type": "RuntimeError",
                                        "message": "cleanup:" + phase} for phase in cleanup_phases]
    assert record["cleanup"] == {
        "taskTearDown": "unknown" if "tear_down" in cleanup_phases else "completed",
        "environment": "unknown" if "close" in cleanup_phases else "closed"}
    assert events == (["initialize_task"] if primary_phase == "initialize_task"
                      else ["initialize_task", "is_successful"]) + ["tear_down", "close"]
    assert record["complete"] is (primary_phase is None and not cleanup_phases)
    assert campaign._rehearsal_valid(record, candidate.manifest["tasks"][0],
                                     campaign._hash(candidate.manifest_path)) is record["complete"]


def test_forced_native_process_halts_even_with_an_official_failed_reward(candidate):
    spec = candidate.manifest["tasks"][0]
    record = native_record(candidate, spec, candidate.root / "native-forced", reward=0.25)
    record["workerProcess"]["terminated"] = True
    assert campaign.halt_reason(record) == "forced_worker"
    assert record["officialReward"] == 0.25


def test_internal_episode_cannot_attest_device_before_missing_full_gates(candidate, monkeypatch):
    offline_execution(candidate, monkeypatch)
    monkeypatch.setattr(campaign.sys, "path", list(sys.path))
    def forbidden(*_):
        raise AssertionError("device attestation before admission")
    monkeypatch.setattr(campaign, "attest_readiness", forbidden)
    args = campaign.build_parser().parse_args(["_episode", "--stage", "run", "--manifest", str(candidate.manifest_path),
        "--project", str(candidate.root), "--authorization", str(candidate.auth_path), "--readiness", str(candidate.readiness_path),
        "--output", str(candidate.root / "must-not-exist"), "--task-index", "0"])
    with pytest.raises(ValueError, match="all-116"):
        campaign._episode(args)
    assert not Path(args.output).exists()


def test_pinned_official_apk_mismatch_fails_without_install_fallback():
    apps = [{"name": "fixture", "officialApkNames": ["fixture.apk"], "apks": [{"sha256": "installed"}]}]
    with pytest.raises(RuntimeError, match="no reinstall fallback"):
        campaign._check_installed_pins(apps, {"artifacts": [{"name": "fixture.apk", "sha256": "frozen"}]})
    campaign._check_installed_pins(apps, {"artifacts": [{"name": "fixture.apk", "sha256": "installed"}]})


def test_outer_timeout_signals_only_observed_owned_descendants(candidate, monkeypatch):
    signals = []
    commands = []
    table = "100 1\n200 100\n201 200\n202 201\n999 1\n1000 999\n"
    def run(command, **kwargs):
        commands.append(command)
        assert kwargs["timeout"] == 5
        return SimpleNamespace(stdout=table)
    monkeypatch.setattr(campaign.subprocess, "run", run)
    monkeypatch.setattr(campaign.os, "killpg", lambda pid, sig: signals.append(("group", pid, sig)))
    monkeypatch.setattr(campaign.os, "kill", lambda pid, sig: signals.append(("pid", pid, sig)))
    waits = []
    owned = SimpleNamespace(pid=200, wait=lambda **kwargs: waits.append(kwargs))
    evidence = campaign._stop_process(owned)
    assert [pid for kind, pid, _ in signals if kind == "pid"] == [202, 201, 200]
    assert all(pid in {200, 201, 202} for _, pid, _ in signals)
    assert evidence["descendantCount"] == 2
    assert evidence["outerExitObserved"] is True
    assert evidence["deviceCleanup"] == "unknown"


def test_resource_grant_must_cover_the_whole_next_envelope(candidate, monkeypatch):
    candidate.auth["resource"]["validUntilUnix"] = NOW + 100
    ready = campaign._load(candidate.readiness_path)
    ready.pop("identitySha256")
    ready["binding"] = campaign._binding(candidate.manifest_path, candidate.manifest, candidate.auth)
    put(candidate.readiness_path, campaign._sealed(ready))
    calls = offline_execution(candidate, monkeypatch)
    args = args_for(candidate, "rehearse")
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert calls == []
    assert report["haltReason"] == "global_identity_drift"
    assert report["summary"]["attempted"] == 0


def test_missing_existing_shared_map_is_not_repaired(candidate, monkeypatch):
    candidate.manifest["tasks"][0]["apps"] = ["osmand"]
    mapping = SimpleNamespace(OsmAndApp=SimpleNamespace(MAP_NAMES=["official.obf"], DEVICE_MAPS_PATH="/fixture/maps"))
    monkeypatch.setitem(sys.modules, "android_world.env.setup_device", SimpleNamespace(apps=mapping))
    commands = []
    def adb(target, *arguments):
        commands.append(arguments)
        return "wrong-sha /fixture/maps/official.obf"
    monkeypatch.setattr(campaign, "_adb", adb)
    with pytest.raises(RuntimeError, match="no repair fallback"):
        campaign._shared_assets_present(candidate.manifest, {"artifacts": [{"name": "official.obf", "sha256": "expected"}]})
    assert commands == [("shell", "sha256sum", "/fixture/maps/official.obf")]


def test_requested_model_alone_does_not_make_frozen_native_configuration_ready(candidate):
    candidate.manifest["identities"]["nativeProviderMetadata"]["model"] = "deepseek-chat"
    with pytest.raises(ValueError, match="native provider/model readiness"):
        consume_readiness(candidate)


def rewrite_first_episode(candidate, report_path, mutate):
    report = campaign._load(report_path)
    row = report["attempts"][0]
    root = report_path.parent / row["directory"]
    record_path = root / "result.json"
    record = campaign._load(record_path)
    outcome_path = root / record["fsq"]["privateOutcome"]["path"]
    outcome = campaign._load(outcome_path)
    mutate(record, outcome, root)
    put(outcome_path, outcome)
    record["fsq"]["privateOutcome"] = ref(root, outcome_path)
    put(record_path, record)
    row["artifacts"] = campaign._artifact_rows(root)
    report.pop("identitySha256")
    put(report_path, campaign._sealed(report))


def test_rehashed_answer_not_equal_to_native_summary_is_rejected(candidate):
    path = stage_report(candidate, "calibrate")
    rewrite_first_episode(candidate, path, lambda record, outcome, root: outcome["result"]["mainAnswer"].update(summary="not emitted by native runner"))
    with pytest.raises(ValueError):
        consume_stage(candidate, path, "calibrate")


def test_rehashed_eleven_write_audit_cannot_hide_behind_zero_counters(candidate):
    path = stage_report(candidate, "calibrate")
    def forge(record, outcome, root):
        result = outcome["result"]
        budget = NativeDispatchBudget(11, 100, clock=lambda: 1)
        for i in range(11):
            budget.dispatch("tap_at", "action", lambda: SimpleNamespace(status="passed"), step_id=str(i))
        returned = {key: value for key, value in result["actionBudget"]["events"][-1].items()
                    if key not in {"sequence", "monotonic"}}
        budget.receipt(returned)
        snapshot = budget.snapshot()
        snapshot.update(maximum=10, attempted=0, admitted=0, succeeded=0, failed=0, denied=0, inFlight=0, exhausted=False)
        audit = Path(result["actionAudit"]["path"])
        audit.write_text("".join(json.dumps(event) + "\n" for event in snapshot["events"]))
        result["actionBudget"] = snapshot
        result["actionAudit"] = {"path": str(audit), "sha256": campaign._hash(audit), "sizeBytes": audit.stat().st_size}
    rewrite_first_episode(candidate, path, forge)
    with pytest.raises(ValueError):
        consume_stage(candidate, path, "calibrate")


@pytest.mark.parametrize("mutation", ["task", "serial", "readiness", "authorization", "campaign"])
def test_rehashed_wrong_native_or_episode_identity_is_rejected(candidate, mutation):
    path = stage_report(candidate, "calibrate")
    def change(record, outcome, root):
        if mutation == "serial":
            outcome["result"]["nativeTarget"]["serial"] = "emulator-9998"
        elif mutation == "task":
            result = outcome["result"]
            other_id = "other-campaign-smoke-099"
            result["taskId"] = other_id
            native_path = Path(result["fsq"]["taskResult"]["path"])
            native = campaign._load(native_path)
            native["task_id"] = other_id
            put(native_path, native)
            result["fsq"]["taskResult"] = {"path": str(native_path), "sha256": campaign._hash(native_path), "sizeBytes": native_path.stat().st_size}
            events = result["actionBudget"]["events"]
            events[-1].update(taskId=other_id, nativeTaskId=other_id)
            audit = Path(result["actionAudit"]["path"])
            audit.write_text("".join(json.dumps(event) + "\n" for event in events))
            result["actionAudit"] = {"path": str(audit), "sha256": campaign._hash(audit), "sizeBytes": audit.stat().st_size}
        else:
            record[{"readiness": "readinessSha256", "authorization": "authorizationSha256", "campaign": "campaignId"}[mutation]] = "another-binding"
    rewrite_first_episode(candidate, path, change)
    with pytest.raises(ValueError):
        consume_stage(candidate, path, "calibrate")


def test_coherent_smoke_episode_cannot_be_resealed_as_calibration(candidate):
    path = stage_report(candidate, "calibrate")
    report = campaign._load(path)
    row = report["attempts"][0]
    root = path.parent / row["directory"]
    smoke = native_record(candidate, candidate.manifest["tasks"][0], root, stage="smoke")
    put(root / "result.json", smoke)
    row["artifacts"] = campaign._artifact_rows(root)
    report.pop("identitySha256")
    put(path, campaign._sealed(report))
    with pytest.raises(ValueError):
        consume_stage(candidate, path, "calibrate")


@pytest.mark.parametrize("transition", ["native_result_parse", "native_archive"])
def test_native_forced_receipt_halts_before_next_task_despite_missing_native_envelope(candidate, monkeypatch, transition):
    rehearsal = stage_report(candidate, "rehearse")
    calls = offline_execution(candidate, monkeypatch, native_failure=transition)
    args = args_for(candidate, "calibrate", rehearsal=rehearsal)
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(calls) == 1
    assert report["haltReason"] == "forced_worker"
    assert report["summary"]["attempted"] == 1
    assert report["summary"]["expected"] == 12
    terminal = campaign._load(calls[0]["root"] / "result.json")
    assert terminal["fsq"] is None and terminal["evidenceFailure"] == transition
    assert terminal["workerProcess"]["terminated"] is True
    assert terminal["workerProcess"]["groupCleanup"] == "settled"
    assert terminal["cleanup"] == {"taskTearDown": "completed", "environment": "closed", "workerProcessGroup": "settled"}
    assert terminal["evaluatorCalls"] == 0 and terminal["officialReward"] is None
    assert (calls[0]["root"] / "result.json").read_bytes() == calls[0]["resultBytes"]


def clock_platform(candidate, monkeypatch, *, close_failure=False, restore_clock=True):
    """Offline property state: no real adb, environment, task, or model calls."""
    real_probe = campaign._device_probe
    events = qualification_collaborators(candidate, monkeypatch, close_failure=close_failure)
    state = {"api": "33", "abi": "x86_64", "build": "fixture-build", "timezone": "UTC",
             "auto_time": "0", "auto_time_zone": "0", "hash": "a" * 64,
             "boot": "00000000-0000-0000-0000-000000000001"}
    app = SimpleNamespace(package_name=lambda: "fixture.clock", apk_names=())
    monkeypatch.setitem(sys.modules, "android_world.env.setup_device",
                        SimpleNamespace(setup=SimpleNamespace(get_app_mapping=lambda _: app)))
    def adb(_, *args):
        if args[:2] == ("shell", "getprop"):
            key = {"ro.build.version.sdk": "api", "ro.product.cpu.abi": "abi",
                   "ro.build.fingerprint": "build", "persist.sys.timezone": "timezone"}.get(args[2])
            return state[key] if key else "1"
        if args == ("shell", "cat", "/proc/sys/kernel/random/boot_id"):
            return state["boot"]
        if args == ("shell", "wm", "size"):
            return "Physical size: 1080x2400"
        if args == ("get-state",):
            return "device"
        if args[:4] == ("shell", "settings", "get", "global"):
            return state[args[4]]
        if args[:3] == ("shell", "service", "check"):
            return f"Service {args[3]}: found"
        if args[:2] == ("shell", "pidof"):
            return "100"
        if args[:3] == ("shell", "pm", "path"):
            return "package:/fixture/base.apk"
        if args[:2] == ("shell", "sha256sum"):
            return state["hash"] + "  /fixture/base.apk"
        if args[:3] == ("shell", "dumpsys", "package"):
            return "versionCode=1"
        raise AssertionError(f"Unexpected device operation: {args!r}")
    monkeypatch.setattr(campaign, "_adb", adb)
    monkeypatch.setattr(campaign, "_device_probe", real_probe)
    readiness = campaign._load(candidate.readiness_path)
    readiness.update(real_probe(candidate.manifest))
    put(candidate.readiness_path, campaign._sealed({key: value for key, value in readiness.items() if key != "identitySha256"}))
    environment = sys.modules["fsq_androidworld_eval.environment"]
    create = environment.load_environment
    def official_setup(**kwargs):
        env = create(**kwargs)
        if kwargs["freeze_datetime"] and restore_clock:
            state.update(timezone="UTC", auto_time="0", auto_time_zone="0")
        return env
    environment.load_environment = official_setup
    return state, events


@pytest.mark.parametrize("field,value", [("api", "34"), ("build", "other-build"),
    ("boot", "00000000-0000-0000-0000-000000000002"), ("hash", "b" * 64)])
def test_task_clock_transition_does_not_hide_stable_identity_drift(candidate, monkeypatch, field, value):
    state, events = clock_platform(candidate, monkeypatch)
    readiness = campaign._load(candidate.readiness_path)
    state.update(timezone="Asia/Shanghai", auto_time="1", auto_time_zone="1")
    campaign.attest_readiness(candidate.manifest, readiness)
    state[field] = value
    with pytest.raises(RuntimeError):
        campaign.attest_readiness(candidate.manifest, readiness)
    assert state["timezone"] == "Asia/Shanghai"
    assert not any(event[0] == "environment" for event in events)


@pytest.mark.parametrize("changes", [{"timezone": "Asia/Shanghai"}, {"auto_time": "1"}, {"auto_time_zone": "1"}])
def test_qualification_requires_explicit_clock_baseline_without_repair(candidate, monkeypatch, changes):
    state, events = clock_platform(candidate, monkeypatch)
    state.update(changes)
    report = campaign._qualification(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["qualified"] is False
    assert report["clock"] == {"timezone": state["timezone"], "autoTime": state["auto_time"], "autoTimeZone": state["auto_time_zone"]}
    assert report["cleanup"]["environment"] == "not_created"
    assert not any(event[0] == "environment" for event in events)


def test_explicit_clock_preparation_allows_fresh_qualification_after_task_transition(candidate, monkeypatch):
    state, _ = clock_platform(candidate, monkeypatch)
    state.update(timezone="Asia/Shanghai", auto_time="1", auto_time_zone="1")
    candidate.auth["approvedStages"].append("prepare-clock")
    prepared = campaign._prepare_clock(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert prepared["prepared"] is True
    assert prepared["before"]["clock"]["timezone"] == "Asia/Shanghai"
    assert prepared["after"]["clock"] == {"timezone": "UTC", "autoTime": "0", "autoTimeZone": "0"}
    assert prepared["before"]["device"] == prepared["after"]["device"]
    assert prepared["cleanup"]["environment"] == "closed"
    report = campaign._qualification(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["qualified"] is True
    assert report["clock"] == prepared["after"]["clock"]
    assert report["checks"]["utc"] is True


@pytest.mark.parametrize("failure", ["not_restored", "close"])
def test_clock_preparation_failure_retains_effects_and_never_qualifies(candidate, monkeypatch, failure):
    state, _ = clock_platform(candidate, monkeypatch, close_failure=failure == "close", restore_clock=failure != "not_restored")
    state["timezone"] = "Asia/Shanghai"
    candidate.auth["approvedStages"].append("prepare-clock")
    report = campaign._prepare_clock(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["prepared"] is False
    assert report["after"]["clock"]["timezone"] == ("UTC" if failure == "close" else "Asia/Shanghai")
    assert report["cleanup"]["environment"] == ("unknown" if failure == "close" else "closed")


def test_clock_preparation_needs_its_own_stage_permission_before_mutation(candidate, monkeypatch):
    state, events = clock_platform(candidate, monkeypatch)
    state["timezone"] = "Asia/Shanghai"
    report = campaign._prepare_clock(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["prepared"] is False
    assert report["error"]["type"] == "PermissionError"
    assert state["timezone"] == "Asia/Shanghai"
    assert not any(event[0] == "environment" for event in events)


def test_readiness_utc_flag_cannot_replace_the_actual_clock_baseline(candidate):
    reseal(candidate.readiness_path, lambda row: row["clock"].update(autoTimeZone="1"))
    with pytest.raises(ValueError):
        consume_readiness(candidate)


@pytest.mark.parametrize("when,field,value", [("before", "api", "34"),
    ("during", "build", "other-build"), ("during", "hash", "b" * 64)])
def test_clock_preparation_never_repairs_or_accepts_stable_target_drift(candidate, monkeypatch, when, field, value):
    state, events = clock_platform(candidate, monkeypatch)
    state["timezone"] = "Asia/Shanghai"
    candidate.auth["approvedStages"].append("prepare-clock")
    if when == "before":
        state[field] = value
    else:
        environment = sys.modules["fsq_androidworld_eval.environment"]
        create = environment.load_environment
        def changed_target(**kwargs):
            env = create(**kwargs)
            state[field] = value
            return env
        environment.load_environment = changed_target
    report = campaign._prepare_clock(candidate.manifest_path, candidate.manifest, candidate.root, candidate.auth)
    assert report["prepared"] is False
    assert state[field] == value
    assert report["cleanup"]["environment"] == ("not_created" if when == "before" else "closed")
    if when == "before":
        assert state["timezone"] == "Asia/Shanghai"
        assert not any(event[0] == "environment" for event in events)


@pytest.mark.parametrize("failure", ["launch", "wait", "cleanup_wait"])
def test_stage_preserves_actual_spawn_and_owned_cleanup_evidence_on_oserror(candidate, monkeypatch, failure):
    monkeypatch.setattr(campaign, "_load_candidate", lambda *_: copy.deepcopy(candidate.manifest))
    launched, signals = [], []
    class Child:
        pid = 999999
        returncode = None
        waits = 0
        def wait(self, *, timeout):
            self.waits += 1
            if self.waits == 1 or failure == "cleanup_wait":
                raise OSError("controlled wait failure")
            self.returncode = -9
            return self.returncode
    child = Child()
    def popen(command, **kwargs):
        launched.append(command)
        if failure == "launch":
            raise OSError("controlled launch failure")
        return child
    monkeypatch.setattr(campaign.subprocess, "Popen", popen)
    monkeypatch.setattr(campaign.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout=""))
    monkeypatch.setattr(campaign.os, "killpg", lambda pid, sig: signals.append(("group", pid)))
    monkeypatch.setattr(campaign.os, "kill", lambda pid, sig: signals.append(("process", pid)))
    args = args_for(candidate, "rehearse")
    assert campaign.run_stage(args) == 2
    report = campaign._load(Path(args.output) / "report.json")
    assert len(launched) == 1 and report["summary"]["attempted"] == 1
    assert report["haltReason"] == "unknown_or_failed_cleanup" and report["qualified"] is False
    process = report["attempts"][0]["outerProcess"]
    assert process["spawnCount"] == int(failure != "launch")
    assert process["forced"] is (failure != "launch") and process["errorType"] == "OSError"
    if failure == "launch":
        assert signals == [] and process["termination"] is None
    else:
        assert signals == [("group", child.pid), ("process", child.pid)]
        assert process["termination"]["deviceCleanup"] == "unknown"
        assert process["termination"]["outerExitObserved"] is (failure != "cleanup_wait")
        if failure == "cleanup_wait":
            assert process["termination"]["waitErrorType"] == "OSError"
