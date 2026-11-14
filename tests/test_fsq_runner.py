from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from fsq_androidworld_eval import fsq_runner as runner
from fsq_androidworld_eval.lifecycle import episode_time_budget
from fsq_androidworld_eval.fsq_native import NativeDispatchBudget, NativeActionBudgetExceeded
from fsq_androidworld_eval.fsq_campaign import halt_reason


def _authorization(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("frozen")
    review = tmp_path / "review.txt"
    review.write_text("independent review receipt fixture")
    model = tmp_path / "model.txt"
    model.write_text("native Responses receipt fixture")
    target = {"serial": "emulator-5556", "consolePort": 5556, "grpcPort": 8556, "adbPath": "/sdk/adb"}
    manifest = {"target": target, "identities": {"nativeProviderMetadata": {
        "provider": "github_copilot", "model": "gpt-6.1-sol"}}}
    def ref(path):
        return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    payload = {"schemaVersion": 1, "kind": "fsq_execution_authorization",
               "manifestSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
               "approvedStages": ["smoke"], "independentReview": {"status": "approved", **ref(review)},
               "nativeModelCall": {"status": "passed_native_responses", "provider": "github_copilot",
                                   "requestedModel": "gpt-6.1-sol", **ref(model)},
               "resource": {"exclusive": True, "disposable": True, "mutationsAllowed": True,
                            **target, "notBeforeUnix": 10, "validUntilUnix": 20, "authority": "test coordinator"}}
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(payload))
    return manifest_path, manifest, path, payload


@pytest.mark.parametrize("mutation", ["target", "window", "review", "model", "stage", "provider", "mutation_grant"])
def test_live_admission_rejects_unproven_or_mismatched_facts_before_device(tmp_path, monkeypatch, mutation):
    manifest_path, manifest, path, payload = _authorization(tmp_path)
    monkeypatch.setattr(runner.time, "time", lambda: 15)
    if mutation == "target":
        payload["resource"]["serial"] = "emulator-5554"
    elif mutation == "window":
        payload["resource"]["validUntilUnix"] = 15
    elif mutation == "review":
        payload["independentReview"]["status"] = "pending"
    elif mutation == "model":
        payload["nativeModelCall"]["status"] = "pending_authentication"
    elif mutation == "stage":
        payload["approvedStages"] = []
    elif mutation == "provider":
        manifest["identities"]["nativeProviderMetadata"]["provider"] = "deepseek"
    else:
        payload["resource"]["mutationsAllowed"] = False
    path.write_text(json.dumps(payload))
    with pytest.raises((ValueError, PermissionError)):
        runner.load_authorization(manifest_path, manifest, "smoke", path)


def test_model_receipt_content_cannot_change_after_authorization(tmp_path, monkeypatch):
    manifest_path, manifest, path, payload = _authorization(tmp_path)
    monkeypatch.setattr(runner.time, "time", lambda: 15)
    Path(payload["nativeModelCall"]["path"]).write_text("different receipt")
    with pytest.raises(ValueError, match="bytes"):
        runner.load_authorization(manifest_path, manifest, "smoke", path)


@pytest.fixture
def offline_episode(tmp_path, monkeypatch):
    from fsq_androidworld_eval import environment
    from android_world.task_evals.information_retrieval import information_retrieval
    events = []
    env = SimpleNamespace(interaction_cache="stale", reset=lambda **kwargs: events.append("reset"))
    class Task:
        name = "FixtureRetrieval"
        app_names = ("settings",)
        goal = "Return the requested fixture value."
        device_time = datetime(2023, 10, 15, tzinfo=timezone.utc)
        def initialize_task(self, current):
            events.append("initialize")
        def is_successful(self, current):
            events.append(("official", current.interaction_cache))
            return 0.5
        def tear_down(self, current):
            events.append("teardown")
    monkeypatch.setattr(information_retrieval, "InformationRetrieval", Task)
    monkeypatch.setattr(runner, "task_from_spec", lambda spec: Task())
    monkeypatch.setattr(runner, "activate_evaluator_site", lambda manifest: None)
    monkeypatch.setattr(runner, "_primary_app_id", lambda task: "com.android.settings")
    monkeypatch.setattr(environment, "load_environment", lambda **kwargs: env)
    monkeypatch.setattr(environment, "restore_shared_assets", lambda *args: [])
    monkeypatch.setattr(environment, "close_environment", lambda current: events.append("environment_close"))
    spec = {"index": 0, "name": "FixtureRetrieval", "paramsSha256": "fixture", "maxSteps": 10,
            "maxActions": 10, "timeBudget": episode_time_budget(10)}
    template = tmp_path / "runtime" / "template" / ".fsq" / "config" / "config.android.yaml"
    template.parent.mkdir(parents=True)
    template.write_text("template")
    manifest = {"campaignId": "offline", "tasks": [spec], "paths": {
        "settingsPath": str(template), "evaluatorSite": str(tmp_path / "isolated-site"),
        "fsqPython": "/fixture/python"}, "target": {"serial": "emulator-5556", "consolePort": 5556,
                                                    "grpcPort": 8556, "adbPath": "/fixture/adb"}}
    source = Path(runner.__file__).parent
    manifest["identities"] = {"evaluator": {"source": {"files": [
        {"path": name, "sha256": hashlib.sha256((source / name).read_bytes()).hexdigest()}
        for name in ("__init__.py", "fsq_worker.py", "fsq_native.py")
    ]}}, "androidWorld": {"oracleSourceRoots": [str(tmp_path / "retained-source")]},
        "fsq": {"prefix": "/fixture/venv", "basePrefix": "/fixture/base", "package": {"path": "/fixture/fsq_agent"}}}
    monkeypatch.setattr(runner, "load_manifest", lambda *args: manifest)
    monkeypatch.setattr(runner, "load_authorization", lambda *args: {
        "resource": {"validUntilUnix": runner.time.time() + 100_000}})
    monkeypatch.setattr(runner, "validate_readiness", lambda *args: {})
    manifest_path = tmp_path / "manifest.json"
    authorization = tmp_path / "authorization.json"
    readiness = tmp_path / "readiness.json"
    for path in (manifest_path, authorization, readiness):
        path.write_text("{}")
    def execute(*, complete=True, answer=True, deadline=False, kill="succeeded", forced=False,
                parse_error=False, archive_error=False, group_cleanup="settled"):
        def worker(request, **kwargs):
            assert request["goal"] == Task.goal
            assert "params" not in request and "expected" not in request
            assert env.interaction_cache == ""
            output = kwargs["private_dir"]
            output.mkdir(parents=True)
            (output / "native-log.txt").write_text("private model/answer fixture")
            audit = output / "native-action-audit.jsonl"
            budget = NativeDispatchBudget(request["maxActions"], 100, clock=lambda: 1, journal=audit)
            def forward_kill():
                events.append(("kill_forward", kill))
                return SimpleNamespace(status="passed" if kill == "succeeded" else "failed")
            if kill == "denied":
                for _ in range(request["maxActions"]):
                    budget.dispatch("tap_at", "action", lambda: SimpleNamespace(status="passed"))
                try:
                    budget.dispatch("kill_app", "action", forward_kill)
                except NativeActionBudgetExceeded:
                    pass
            elif kill != "absent":
                budget.dispatch("kill_app", "action", forward_kill)
            verification = {"status": "inconclusive", "summary": "private native verification"}
            native_task = {"task_id": request["taskId"], "status": "inconclusive", "verification": verification,
                           "steps": [{"tool_name": "agent_runtime.runner", "status": "success" if answer else "failed",
                                      "tool_output": {"schema_version": "task_run_v1", "status": "inconclusive",
                                                      "summary": "  exact value  "} if answer else {"failure_reason": "no parsed main output"}}]}
            def native_ref(path):
                return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "sizeBytes": path.stat().st_size, "visibility": "evaluator_private"}
            task_path = output / "native-task.json"
            verification_path = output / "verification.json"
            runner.private_json(task_path, native_task)
            runner.private_json(verification_path, verification)
            if complete:
                events.extend(["native_verification", "native_return"])
                budget.receipt({"event": "native_execution_returned", "taskId": request["taskId"],
                                "nativeTaskId": request["taskId"], "taskStatus": "inconclusive",
                                "verificationObserved": True, "verificationStatus": "inconclusive"})
            response = {"schemaVersion": 1, "taskId": request["taskId"], "status": "completed",
                        "nativeTarget": {"serial": request["serial"], "effectiveProvider": "github_copilot", "effectiveModel": "gpt-6.1-sol"},
                        "fsq": {"completeDynamicExecutionReturned": complete, "status": "inconclusive",
                                "taskResult": native_ref(task_path), "verification": native_ref(verification_path)},
                        "mainAnswer": {"status": "valid", "summary": "  exact value  ", "businessStatus": "inconclusive",
                                       "source": "agent_runtime.runner.tool_output.summary"} if answer else {
                                           "status": "failed", "source": "agent_runtime.runner.tool_output.summary"},
                        "actionBudget": budget.snapshot(), "actionAudit": native_ref(audit) if audit.exists() else None,
                        "cleanup": {"closeReceipts": [], "deviceRestored": False}}
            process = {"exitCode": -15 if forced else 0, "businessDeadlineReached": deadline,
                       "terminated": forced, "killed": False, "workerExitObserved": True, "spawnCount": 1,
                       "groupCleanup": group_cleanup, "pgid": 999999}
            runner.private_json(kwargs["process_receipt_path"], process)
            return {"process": process, "result": None if parse_error else response,
                    "resultError": {"type": "JSONDecodeError"} if parse_error else None,
                    "restoration": "not_provided_by_native_driver_close"}
        monkeypatch.setattr(runner, "run_fsq_worker", worker)
        if archive_error:
            def fail_archive(*args):
                raise OSError("controlled archive failure")
            monkeypatch.setattr(runner, "_archive_outcome", fail_archive)
        return runner.run_episode(manifest_path, tmp_path, 0, tmp_path / "episode", authorization, readiness)
    execute.fixture = SimpleNamespace(manifest=manifest, spec=spec, manifest_path=manifest_path,
                                      authorization=authorization, readiness=readiness, task_type=Task)
    return execute, events, tmp_path


@pytest.mark.parametrize("kill,forwarded", [("absent", 0), ("failed", 1), ("denied", 0), ("succeeded", 1)])
def test_complete_native_return_scores_once_without_kill_eligibility_gate(offline_episode, kill, forwarded):
    execute, events, root = offline_episode
    record = execute(kill=kill)
    assert len([event for event in events if isinstance(event, tuple) and event[0] == "kill_forward"]) == forwarded
    assert events.index("native_return") < next(i for i, event in enumerate(events) if isinstance(event, tuple) and event[0] == "official")
    assert record["evaluator"]["ordering"] == "after_complete_native_FSQ_return_and_internal_verification"
    assert record["fsq"]["killEvidence"]["relativeToMainFinal"] == "unknown"
    assert record["officialReward"] == 0.5
    assert record["classification"] == "failed"
    assert record["fsq"]["nativeStatus"] == "inconclusive"
    assert record["evaluatorCalls"] == 1
    assert "summary" not in record["fsq"]["mainAnswer"]
    public = (root / "episode/result.json").read_text()
    assert "exact value" not in public and "private model/answer fixture" not in public
    assert record["cleanup"]["taskTearDown"] == "completed"
    assert record["cleanup"]["environment"] == "closed"
    for ref in record["artifacts"]:
        assert hashlib.sha256((root / "episode" / ref["path"]).read_bytes()).hexdigest() == ref["sha256"]


def test_failed_runner_answer_never_reuses_cache_or_verifier(offline_episode):
    execute, events, _ = offline_episode
    record = execute(answer=False)
    assert ("official", "") in events
    assert record["officialReward"] == 0.5
    assert record["fsq"]["mainAnswer"]["status"] == "failed"
    assert record["evaluatorCalls"] == 1


def test_unproven_complete_native_execution_does_not_call_oracle(offline_episode):
    execute, events, _ = offline_episode
    record = execute(complete=False)
    assert not any(isinstance(event, tuple) and event[0] == "official" for event in events)
    assert record["officialReward"] is None
    assert record["evaluatorCalls"] == 0
    assert record["classification"] == "invalid_agent"
    assert events[-2:] == ["teardown", "environment_close"]


def test_deadline_keeps_reward_diagnostic_but_not_valid_success(offline_episode):
    execute, events, _ = offline_episode
    record = execute(deadline=True)
    assert record["officialReward"] == 0.5
    assert record["classification"] == "invalid_agent"
    assert record["terminationReason"] == "business_deadline"
    assert record["evaluatorCalls"] == 1


@pytest.mark.parametrize("reward", [True, None, float("nan"), float("inf"), -1, 1.01])
def test_invalid_official_rewards_are_not_success(reward):
    assert runner.classification({"officialReward": reward}) == "invalid_evaluator"


@pytest.mark.parametrize("transition", ["parse", "archive"])
def test_process_evidence_survives_result_and_archive_failures(offline_episode, transition):
    execute, events, root = offline_episode
    record = execute(forced=True, parse_error=transition == "parse", archive_error=transition == "archive")
    assert record["workerProcess"]["terminated"] is True
    assert record["workerProcess"]["groupCleanup"] == "settled"
    reference = record["workerProcessReference"]
    receipt = json.loads((root / "episode" / reference["path"]).read_bytes())
    assert receipt == record["workerProcess"]
    assert record["officialReward"] is None and record["evaluatorCalls"] == 0
    assert not any(isinstance(event, tuple) and event[0] == "official" for event in events)
    assert halt_reason(record) == "forced_worker"
    assert record["cleanup"]["taskTearDown"] == "completed"
    assert record["cleanup"]["environment"] == "closed"


def test_unknown_worker_group_never_scores_or_mutates_task_teardown(offline_episode):
    execute, events, _ = offline_episode
    record = execute(group_cleanup="unknown")
    assert record["evaluatorCalls"] == 0 and record["officialReward"] is None
    assert "teardown" not in events
    assert record["cleanupFailure"] is True
    assert record["cleanup"]["workerProcessGroup"] == "unknown"
    assert halt_reason(record) == "unknown_or_failed_cleanup"


@pytest.mark.parametrize("reward,answer,complete,fail_close,outer_exit,expected_exit,classification", [
    (0.0, True, True, False, 0, 0, "failed"),
    (0.5, True, True, False, 0, 0, "failed"),
    (1.0, True, True, False, 0, 0, "passed"),
    (1.0, False, True, False, 0, 1, "passed"),
    (None, True, True, False, 0, 1, "invalid_evaluator"),
    (None, True, False, False, 0, 1, "invalid_agent"),
    (1.0, False, True, True, 0, 1, "passed"),
    (1.0, True, True, False, 7, 1, "passed"),
])
def test_standalone_main_consumes_cleaned_episode_before_choosing_exit(
        offline_episode, monkeypatch, capsys, reward, answer, complete, fail_close,
        outer_exit, expected_exit, classification):
    from fsq_androidworld_eval import environment, fsq_campaign
    execute, events, root = offline_episode
    ctx = execute.fixture
    def oracle(self, current):
        events.append(("official", current.interaction_cache))
        if reward is None:
            raise RuntimeError("controlled evaluator exception")
        return reward
    monkeypatch.setattr(ctx.task_type, "is_successful", oracle)
    if fail_close:
        def close(current):
            events.append("environment_close")
            raise OSError("controlled close failure")
        monkeypatch.setattr(environment, "close_environment", close)
    produced = []
    def spawn(command, output, timeout):
        record = execute(answer=answer, complete=complete)
        produced.append((record, (root / "episode/result.json").read_bytes()))
        return {"forced": False, "exitCode": outer_exit, "spawnCount": 1, "timeoutSeconds": timeout}
    monkeypatch.setattr(fsq_campaign, "_spawn", spawn)
    with pytest.raises(SystemExit) as exited:
        runner.main(["--project", str(root), "--manifest", str(ctx.manifest_path), "--task-index", "0",
                     "--output-dir", str(root / "episode"), "--authorization", str(ctx.authorization),
                     "--readiness", str(ctx.readiness)])
    assert exited.value.code == expected_exit
    terminal = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert terminal == json.loads((root / "episode.outer/standalone-result.json").read_bytes())
    assert terminal["classification"] == classification
    assert (terminal["haltReason"] is None) is (expected_exit == 0)
    if fail_close:
        assert terminal["haltReason"] == "unknown_or_failed_cleanup"
    assert terminal["officialReward"] == (reward if complete else None)
    assert len(produced) == 1 and (root / "episode/result.json").read_bytes() == produced[0][1]
    record = produced[0][0]
    assert record["evaluatorCalls"] == int(complete)
    assert events[-2:] == ["teardown", "environment_close"]
    assert events.count("teardown") == 1 and events.count("environment_close") == 1
    assert record["cleanupFailure"] is fail_close
    if complete and not answer:
        assert record["fsq"]["mainAnswer"]["status"] == "failed"
        assert "summary" not in record["fsq"]["mainAnswer"]
