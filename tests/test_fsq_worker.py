import asyncio
import copy
import hashlib
import json
from types import SimpleNamespace as NS

import pytest

from fsq_androidworld_eval.fsq_native import BudgetedAndroidHarness, NativeActionBudgetExceeded
from fsq_androidworld_eval.fsq_worker import NativeBindings, execute_worker, main, select_main_answer, validate_request


def validate_fixture_output(value):
    """In-memory native-model collaborator; production uses AgentFinalOutput."""
    if value.get("schema_version") != "task_run_v1" or value.get("status") not in {"success", "failed", "inconclusive"} or not isinstance(value.get("summary"), str):
        raise ValueError("Invalid fixture output")
    return value


def runner(summary="answer", *, business_status="success", status="success"):
    return {"step_id": 1, "tool_name": "agent_runtime.runner", "status": status,
            "actual_outcome": "Native runtime result", "screenshot_path": None, "ui_tree_snapshot": None,
            "duration_ms": 1, "error": None,
            "tool_output": {"schema_version": "task_run_v1", "status": business_status, "summary": summary,
                            "pre_plan": [], "plan_updates": [], "satisfied_criteria": [],
                            "unmet_criteria": [], "evidence": [], "errors": []}}


def select(steps):
    return select_main_answer({"steps": steps}, validate_output=validate_fixture_output)


@pytest.mark.parametrize("summary", ["", "  \n\t", "42", "answer\nwith Unicode: 中文"])
@pytest.mark.parametrize("business_status", ["success", "failed", "inconclusive"])
def test_answer_is_exact_main_summary_not_business_status_or_verifier(summary, business_status):
    answer = select([
        {"tool_name": "agent_runtime.pre_plan", "status": "success", "tool_output": {"summary": "not the answer"}},
        runner(summary, business_status=business_status),
        {"tool_name": "agent_runtime.verifier", "status": "success", "tool_output": {"summary": "also not the answer"}},
    ])
    assert answer["status"] == "valid"
    assert answer["summary"] == summary
    assert answer["businessStatus"] == business_status
    assert answer["source"] == "agent_runtime.runner.tool_output.summary"


@pytest.mark.parametrize("steps,expected", [
    ([], "missing"),
    ([{"tool_name": "agent_runtime.runner.extra", "status": "success", "tool_output": {"summary": "no"}}], "missing"),
    ([runner(), runner("different")], "ambiguous"),
    ([runner(status="failed")], "failed"),
    ([{"tool_name": "agent_runtime.runner", "status": "failed", "tool_output": {"failure_reason": "no final"}}], "failed"),
    ([{"tool_name": "agent_runtime.runner", "status": "success", "tool_output": '{"schema_version":"task_run_v1","summary":"wire string"}'}], "invalid"),
    ([{"tool_name": "agent_runtime.runner", "status": "success", "tool_output": {"schema_version": "task_run_v1"}}], "invalid"),
    ([runner(None)], "invalid"),
    ([runner(42)], "invalid"),
    ([runner(business_status="invented")], "invalid"),
])
def test_exact_answer_contract_has_explicit_failures_without_fallback(steps, expected):
    answer = select(steps + [{"tool_name": "agent_runtime.verifier", "status": "success", "tool_output": {"summary": "tempting fallback"}}])
    assert answer["status"] == expected
    assert "summary" not in answer


def test_multiple_runners_are_ambiguous_even_if_one_failed():
    assert select([runner(status="failed"), runner()])["status"] == "ambiguous"




def request(tmp_path):
    workspace = tmp_path / "owned-workspace"
    return {"schemaVersion": 1, "settingsPath": str(workspace / ".fsq" / "config" / "config.android.yaml"),
            "workspace": str(workspace), "outputDir": str(tmp_path / "private-envelope"), "serial": "emulator-5554",
            "taskId": "fixture-task", "goal": "Exact initialized goal\nGeneric answer footer unchanged.", "appId": "fixture.app",
            "maxActions": 3, "businessDeadlineMonotonic": 100.0, "provider": "github_copilot", "model": "gpt-6.1-sol"}


def fixture_bindings(tmp_path, *, steps=None, business_status="success", service_failure=False, after_execution=None, close_failure=False, handle_budget_denials=False, actions=None, kill_status="passed"):
    events = []
    workspace = tmp_path / "owned-workspace"
    settings = NS(agent_runtime=NS(provider="github_copilot", model="gpt-6.1-sol", max_turns=100, reasoning_effort="mid", tracing_enabled=True),
                  harness=NS(platform="android", android=NS(backend="uiautomator2", serial=None, app_id="fixture.app")),
                  workspace=NS(root_dir=workspace), output=NS(root_dir=workspace / ".fsq" / "runs" / "android", runs_dir=workspace / ".fsq" / "runs" / "android"),
                  runtime_secrets=NS(private_values=lambda: {"fixture": "secret-value"}),
                  skills=object(), agent_context=object())
    original_skills = settings.skills
    original_context = settings.agent_context
    def load(workspace_path, platform, **kwargs):
        events.append(("load", workspace_path, platform, kwargs))
        return settings
    class NativeHarness:
        def invoke_action(self, step, context):
            events.append(("native_dispatch", step.action_name, step.kind))
            return NS(status=kill_status if step.action_name == "kill_app" else "passed")
        def close(self):
            events.append(("close",))
            if close_failure:
                raise OSError("private close detail")
    def factory_builder(actual_settings, budget):
        assert actual_settings is settings
        events.append(("harness_builder",))
        return lambda run_id: BudgetedAndroidHarness(NativeHarness(), budget)
    def runtime_factory(actual_settings, *, harness_factory):
        events.append(("native_runtime_factory",))
        return NS(harness_factory=harness_factory)
    class Agent:
        @classmethod
        def from_settings(cls, actual_settings, *, runtime_factory, harness_factory):
            events.append(("agent_from_settings",))
            return NS(runtime=runtime_factory(actual_settings, harness_factory=harness_factory))
    class Service:
        def __init__(self, *, agent):
            self.agent = agent
        async def execute(self, req):
            events.append(("execute", req))
            req.cancellation_check()
            assert req.record is False
            assert req.settings.skills is original_skills
            assert req.settings.agent_context is original_context
            assert req.settings.harness.android.serial == "emulator-5554"
            if service_failure:
                raise RuntimeError("credential=secret-value private goal")
            harness = self.agent.runtime.harness_factory("fixture-run")
            try:
                for name, kind in (actions if actions is not None else [("launch_app", "setup"), ("tap_at", "action"), ("kill_app", "teardown")]):
                    try:
                        harness.invoke_action(NS(action_name=name, kind=kind, step_id="fixture"), None)
                    except NativeActionBudgetExceeded:
                        if not handle_budget_denials:
                            raise
                        events.append(("handled_budget_denial", name))
            finally:
                harness.close()
            events.append(("internal_verification",))
            payload = {"task_id": req.task.id, "status": business_status, "steps": steps if steps is not None else [runner("  *** answer  ", business_status=business_status)],
                       "verification": {"status": business_status, "summary": "internal verifier, never answer",
                                        "satisfied_criteria": [], "unmet_criteria": [], "diagnostics": []},
                       "report": {"run_id": "fixture-run", "path": str(settings.output.runs_dir / "fixture-run" / "execution-result.json"),
                                  "format": "json", "evidence_manifest_path": None, "evidence_bundle_path": None,
                                  "generated_at": "2026-11-10T00:00:00Z"}, "duration_ms": 1}
            if after_execution:
                after_execution()
            return NS(task_result=NS(model_dump=lambda **kwargs: copy.deepcopy(payload)))
    bindings = NativeBindings(load, Agent, runtime_factory, Service, NS, NS, factory_builder, tmp_path / "readonly-fsq-source", validate_fixture_output)
    return bindings, settings, events


@pytest.mark.parametrize("business_status", ["success", "failed", "inconclusive"])
def test_full_worker_composition_waits_for_internal_verifier_and_persists_separate_private_results(tmp_path, business_status):
    bindings, settings, events = fixture_bindings(tmp_path, business_status=business_status)
    req = request(tmp_path)
    result = asyncio.run(execute_worker(req, bindings=bindings, clock=lambda: 1))
    assert result["status"] == "completed"
    assert result["fsq"]["status"] == business_status
    assert result["mainAnswer"]["summary"] == "  *** answer  "
    assert result["mainAnswer"]["businessStatus"] == business_status
    execution = next(event[1] for event in events if event[0] == "execute")
    assert execution.task.description == execution.task.name == execution.task.planning_reference_text == req["goal"]
    assert [event[0] for event in events][-2:] == ["close", "internal_verification"]
    assert result["actionBudget"]["admitted"] == 3
    assert result["cleanup"]["deviceRestored"] is False
    assert [event["event"] for event in result["cleanup"]["closeReceipts"]] == ["close_started", "close_succeeded"]
    from pathlib import Path
    for name in ("taskResult", "verification"):
        ref = result["fsq"][name]
        data = Path(ref["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == ref["sha256"]
        assert Path(ref["path"]).stat().st_mode & 0o777 == 0o600
        assert ref["visibility"] == "evaluator_private"
    assert result["fsq"]["taskResult"]["path"] != result["fsq"]["verification"]["path"]
    assert result["fsq"]["nativeRunsRoot"]["path"] == str(settings.output.runs_dir)
    assert result["nativeTarget"]["effectiveProvider"] == "github_copilot"
    audit = result["actionBudget"]["events"]
    assert audit[-1] == {"event": "native_execution_returned", "sequence": len(audit), "monotonic": 1,
                         "taskId": req["taskId"], "nativeTaskId": req["taskId"], "taskStatus": business_status,
                         "verificationObserved": True, "verificationStatus": business_status}
    persisted = json.loads(Path(result["fsq"]["taskResult"]["path"]).read_text())
    assert persisted["verification"] == json.loads(Path(result["fsq"]["verification"]["path"]).read_text())
    assert persisted["task_id"] == req["taskId"]
    assert [json.loads(line) for line in Path(result["actionAudit"]["path"]).read_text().splitlines()] == audit


@pytest.mark.parametrize("steps,answer_status", [([], "missing"), ([runner(status="failed")], "failed"), ([runner(), runner()], "ambiguous"), ([runner(None)], "invalid")])
def test_completed_native_result_is_preserved_when_main_answer_contract_fails(tmp_path, steps, answer_status):
    bindings, _, _ = fixture_bindings(tmp_path, steps=steps)
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: 1))
    assert result["status"] == "completed"
    assert result["fsq"]["completeDynamicExecutionReturned"] is True
    assert result["mainAnswer"]["status"] == answer_status
    assert "summary" not in result["mainAnswer"]


@pytest.mark.parametrize("field,value", [("provider", "deepseek"), ("model", "some-other-model")])
def test_effective_target_mismatch_fails_before_driver_runtime_or_harness_construction(tmp_path, field, value):
    bindings, settings, events = fixture_bindings(tmp_path)
    setattr(settings.agent_runtime, field, value)
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: 1))
    assert result["status"] == "failed"
    assert result["error"]["reason"] == "effective_provider_model_mismatch"
    assert result["nativeTarget"]["effective" + field.title()] == value
    assert [event[0] for event in events] == ["load"]
    assert result["actionBudget"]["admitted"] == 0
    assert result["cleanup"]["closeReceipts"] == []


def test_app_mismatch_and_noncanonical_config_fail_before_native_harness(tmp_path):
    for key, value in [("appId", "different.app"), ("settingsPath", str(tmp_path / "other.yaml"))]:
        bindings, _, events = fixture_bindings(tmp_path)
        req = request(tmp_path)
        req[key] = value
        result = asyncio.run(execute_worker(req, bindings=bindings, clock=lambda: 1))
        assert result["status"] == "failed"
        assert not any(event[0] == "harness_builder" for event in events)


def test_null_appid_retains_native_target_and_explicit_profile_is_applied(tmp_path):
    bindings, settings, events = fixture_bindings(tmp_path)
    req = request(tmp_path)
    req.update(appId=None, runtimeProfile={"maxTurns": 8, "reasoningEffort": "high", "tracingEnabled": False}, userConfigRoot=str(tmp_path / "private-auth"))
    result = asyncio.run(execute_worker(req, bindings=bindings, clock=lambda: 1))
    assert result["status"] == "completed"
    assert settings.harness.android.app_id == "fixture.app"
    assert (settings.agent_runtime.max_turns, settings.agent_runtime.reasoning_effort, settings.agent_runtime.tracing_enabled) == (8, "high", False)
    assert str(events[0][3]["user_config_root"]) == req["userConfigRoot"]


def test_initial_deadline_prevents_even_native_settings_load(tmp_path):
    bindings, _, events = fixture_bindings(tmp_path)
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: 100))
    assert result["status"] == "deadline"
    assert events == []
    assert result["actionBudget"]["deadlineExceeded"] is True


def test_deadline_after_full_native_return_preserves_result_but_reports_deadline(tmp_path):
    now = [1]
    bindings, _, _ = fixture_bindings(tmp_path, after_execution=lambda: now.__setitem__(0, 100))
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: now[0]))
    assert result["status"] == "deadline"
    assert result["fsq"]["completeDynamicExecutionReturned"] is True
    assert result["mainAnswer"]["summary"] == "  *** answer  "


@pytest.mark.parametrize("close_failure", [False, True])
def test_runtime_and_close_failures_never_become_zero_error_completion_or_leak_details(tmp_path, close_failure):
    bindings, _, _ = fixture_bindings(tmp_path, service_failure=not close_failure, close_failure=close_failure)
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: 1))
    assert result["status"] == "failed"
    assert result["mainAnswer"]["status"] == "missing"
    assert "secret-value" not in json.dumps(result)
    assert "private close detail" not in json.dumps(result)
    if close_failure:
        assert result["cleanup"]["closeReceipts"][-1]["event"] == "close_failed"


@pytest.mark.parametrize("key,value", [("schemaVersion", True), ("maxActions", False), ("maxActions", 0), ("businessDeadlineMonotonic", float("nan")), ("serial", " emulator-5554"), ("provider", "deepseek"), ("model", "github-copilot/gpt-6.1-sol"), ("oracleExpected", "hidden")])
def test_worker_rejects_bad_or_oracle_bearing_request_fields(tmp_path, key, value):
    req = request(tmp_path)
    req[key] = value
    with pytest.raises(ValueError):
        validate_request(req)


def test_cli_invalid_request_writes_honest_nonzero_private_failure_without_importing_fsq(tmp_path):
    source = tmp_path / "invalid-request.json"
    target = tmp_path / "result.json"
    source.write_text('{"schemaVersion": 99}')
    assert main(["--request", str(source), "--output", str(target)]) == 2
    result = json.loads(target.read_text())
    assert result["status"] == "failed"
    assert result["mainAnswer"]["status"] == "missing"
    assert target.stat().st_mode & 0o777 == 0o600


def test_exhausted_budget_stays_closed_even_if_native_loop_handles_denial_and_returns(tmp_path):
    bindings, _, events = fixture_bindings(tmp_path, handle_budget_denials=True)
    req = request(tmp_path)
    req["maxActions"] = 1
    result = asyncio.run(execute_worker(req, bindings=bindings, clock=lambda: 1))
    assert result["status"] == "completed"
    assert result["terminationReason"] == "action_budget"
    assert result["actionBudget"]["admitted"] == 1
    assert result["actionBudget"]["denied"] == 2
    assert result["actionBudget"]["exhausted"] is True
    assert [event[1] for event in events if event[0] == "native_dispatch"] == ["launch_app"]
    assert [event[1] for event in events if event[0] == "handled_budget_denial"] == ["tap_at", "kill_app"]


@pytest.mark.parametrize("value", [None, [], {"steps": None}, {"steps": {}}, {}])
def test_malformed_task_result_is_invalid_without_needing_native_import(value):
    assert select_main_answer(value)["status"] == "invalid"


@pytest.mark.parametrize("kill,actions,maximum,status,expected_calls", [
    ("absent", [], 3, "passed", []),
    ("failed", [("kill_app", "teardown")], 3, "failed", ["kill_app"]),
    ("denied", [("tap_at", "action"), ("kill_app", "teardown")], 1, "passed", ["tap_at"]),
    ("succeeded", [("kill_app", "teardown")], 3, "passed", ["kill_app"]),
])
def test_full_worker_reports_real_kill_outcomes_without_supplement_or_gate(tmp_path, kill, actions, maximum, status, expected_calls):
    from fsq_androidworld_eval.fsq_evidence import validate_native_evidence
    bindings, _, events = fixture_bindings(tmp_path, actions=actions, kill_status=status, handle_budget_denials=True)
    req = request(tmp_path)
    req["maxActions"] = maximum
    result = asyncio.run(execute_worker(req, bindings=bindings, clock=lambda: 1))
    assert result["status"] == "completed"
    evidence = validate_native_evidence({"result": result}, episode_root=tmp_path,
        expected_task_id=req["taskId"], expected_serial=req["serial"], maximum=maximum)
    assert evidence["killEvidence"]["status"] == kill
    assert evidence["killEvidence"]["relativeToMainFinal"] == "unknown"
    assert evidence["audit"]["nativeExecutionReturned"]["verificationObserved"] is True
    assert [event[1] for event in events if event[0] == "native_dispatch"] == expected_calls
    assert [event[0] for event in events][-2:] == ["close", "internal_verification"]


def test_service_failure_never_fabricates_full_return_boundary(tmp_path):
    bindings, _, _ = fixture_bindings(tmp_path, service_failure=True)
    result = asyncio.run(execute_worker(request(tmp_path), bindings=bindings, clock=lambda: 1))
    assert not any(event["event"] == "native_execution_returned" for event in result["actionBudget"]["events"])
    assert result["fsq"].get("completeDynamicExecutionReturned") is not True
