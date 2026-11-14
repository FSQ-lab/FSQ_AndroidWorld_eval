from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import json
import sys
from types import ModuleType, SimpleNamespace as NS

import pytest

from fsq_androidworld_eval.fsq_native import (
    BudgetedAndroidHarness, NativeActionBudgetExceeded, NativeBoundaryError,
    NativeDeadlineExceeded, NativeDispatchBudget, WRITE_CAPABILITIES, build_native_harness_factory,
)


class MemoryHarness:
    def __init__(self):
        self.calls = []
        self.close_calls = 0
        self.result = NS(status="passed")
        self.error = None
        self.close_error = None

    def invoke_action(self, step, context):
        self.calls.append((step.action_name, step.kind, context))
        if self.error:
            raise self.error
        return self.result

    def capture_scope(self, callback):
        self.calls.append(("scope", callback))
        return nullcontext()

    def get_context(self):
        return {"fixture": True}

    def action_space(self):
        return ["original fixture schemas"]

    def before_action(self, step, context):
        self.calls.append(("before", step, context))

    def after_action(self, step, context, result):
        self.calls.append(("after", step, context, result))

    def capture_artifact(self, *args):
        self.calls.append(("capture", *args))
        return "private fixture artifact"

    def classify_error(self, *args):
        self.calls.append(("classify", *args))
        return "harness_error"

    def close(self):
        self.close_calls += 1
        if self.close_error:
            raise self.close_error


def step(action="tap_at", phase="action"):
    return NS(action_name=action, kind=phase, step_id="fixture-step")


@pytest.mark.parametrize("action", list(WRITE_CAPABILITIES) + list(WRITE_CAPABILITIES.values()))
def test_all_eight_canonical_and_alias_writes_are_reserved_before_forward(action):
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    observed = []
    def forward():
        observed.append(budget.snapshot()["admitted"])
        return NS(status="passed")
    budget.dispatch(action, "action", forward)
    with pytest.raises(NativeActionBudgetExceeded):
        budget.dispatch(action, "action", forward)
    assert observed == [1]
    result = budget.snapshot()
    assert (result["attempted"], result["admitted"], result["succeeded"], result["denied"]) == (2, 1, 1, 1)


def test_shared_budget_is_atomic_across_concurrent_harnesses_and_same_turn_tools():
    budget = NativeDispatchBudget(7, 100, clock=lambda: 1)
    native = [MemoryHarness(), MemoryHarness()]
    harnesses = [BudgetedAndroidHarness(item, budget) for item in native]
    def invoke(index):
        try:
            harnesses[index % 2].invoke_action(step(), None)
            return True
        except NativeActionBudgetExceeded:
            return False
    with ThreadPoolExecutor(max_workers=16) as pool:
        admitted = list(pool.map(invoke, range(64)))
    receipt = budget.snapshot()
    assert sum(admitted) == sum(len(item.calls) for item in native) == 7
    assert receipt["attempted"] == 64
    assert receipt["denied"] == 57
    assert receipt["inFlight"] == 0
    assert receipt["admitted"] == receipt["succeeded"] + receipt["failed"]


def test_setup_teardown_and_composite_text_each_consume_one_unit():
    budget = NativeDispatchBudget(3, 100, clock=lambda: 1)
    native = MemoryHarness()
    harness = BudgetedAndroidHarness(native, budget)
    for action, phase in [("launch_app", "setup"), ("input_text", "action"), ("kill_app", "teardown")]:
        harness.invoke_action(step(action, phase), None)
    assert budget.snapshot()["admitted"] == 3
    assert [event["phase"] for event in budget.snapshot()["events"] if event["event"] == "attempted"] == ["setup", "action", "teardown"]
    assert budget.snapshot()["inputTextUnit"] == "composite_click_optional_clear_set_text"
    with pytest.raises(NativeActionBudgetExceeded):
        harness.invoke_action(step("kill_app", "teardown"), None)
    assert len(native.calls) == 3


@pytest.mark.parametrize("raises", [False, True])
def test_missing_target_or_partial_native_failure_never_refunds(raises):
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    native = MemoryHarness()
    native.result = NS(status="failed")
    if raises:
        native.error = OSError("private native error")
    harness = BudgetedAndroidHarness(native, budget)
    if raises:
        with pytest.raises(OSError):
            harness.invoke_action(step("input_text"), None)
    else:
        assert harness.invoke_action(step("input_text"), None).status == "failed"
    with pytest.raises(NativeActionBudgetExceeded):
        harness.invoke_action(step(), None)
    assert budget.snapshot()["admitted"] == budget.snapshot()["failed"] == 1
    assert "private native error" not in json.dumps(budget.snapshot())


def test_deadline_denies_before_forward_for_writes_and_reads():
    now = [5.0]
    budget = NativeDispatchBudget(5, 6, clock=lambda: now[0])
    native = MemoryHarness()
    harness = BudgetedAndroidHarness(native, budget)
    harness.invoke_action(step("ui_snapshot", "observation"), None)
    assert budget.snapshot()["admitted"] == 0
    now[0] = 6
    for action in ("tap_at", "ui_snapshot"):
        with pytest.raises(NativeDeadlineExceeded):
            harness.invoke_action(step(action), None)
    assert len(native.calls) == 1
    assert budget.snapshot()["deadlineExceeded"] is True
    assert budget.snapshot()["denied"] == 1


def test_batching_is_explicitly_unsupported_without_forwarding():
    budget = NativeDispatchBudget(20, 100, clock=lambda: 1)
    native = MemoryHarness()
    harness = BudgetedAndroidHarness(native, budget)
    for action in ("perform_actions", "performActions"):
        with pytest.raises(NativeBoundaryError, match="unsupported_batch"):
            harness.invoke_action(step(action), None)
    assert native.calls == []
    assert budget.snapshot()["admitted"] == 0


def test_complete_harness_interface_and_close_receipts_preserve_native_calls(tmp_path):
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1, journal=tmp_path / "audit.jsonl")
    native = MemoryHarness()
    harness = BudgetedAndroidHarness(native, budget)
    item = step()
    context = harness.get_context()
    assert context == {"fixture": True}
    assert harness.action_space() == ["original fixture schemas"]
    callback = object()
    with harness.capture_scope(callback):
        harness.before_action(item, context)
        result = harness.invoke_action(item, context)
        harness.after_action(item, context, result)
    assert harness.capture_artifact("screenshot", "final", context, "fixture-step", "invoke") == "private fixture artifact"
    assert harness.classify_error(ValueError(), "invoke", item) == "harness_error"
    harness.close()
    native.close_error = OSError("do not leak")
    with pytest.raises(OSError):
        harness.close()
    assert native.close_calls == 2
    events = budget.snapshot()["events"]
    assert [event["event"] for event in events if event["event"].startswith("close_")] == ["close_started", "close_succeeded", "close_started", "close_failed"]
    assert all(event["deviceRestored"] is False for event in events if event["event"].startswith("close_"))
    persisted = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text().splitlines()]
    assert persisted == events
    assert (tmp_path / "audit.jsonl").stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("maximum,deadline", [(True, 1), (0, 1), (1, float("nan")), (1, float("inf")), (1, True)])
def test_invalid_budget_configuration_is_rejected(maximum, deadline):
    with pytest.raises(ValueError):
        NativeDispatchBudget(maximum, deadline)


def install_memory_factory_modules(monkeypatch, native, *, fail_construction=False):
    """Install only in-memory import collaborators, never a real FSQ runtime."""
    package = ModuleType("fsq_agent")
    package.__path__ = []
    core = ModuleType("fsq_agent.core")
    ai = ModuleType("fsq_agent.ai_services")
    calls = []
    evaluator = NS(close=lambda: calls.append(("evaluator_close",)))
    class Store:
        def __init__(self, path, *, secret_values):
            self.path = path
            self.secret_values = secret_values
    class Factory:
        def create_harness(self, **kwargs):
            calls.append(("create", kwargs))
            if fail_construction:
                # This fake public factory, like the real FSQ factory, owns its
                # construction cleanup; adapter must not invent close receipts.
                evaluator.close()
                raise OSError("private construction failure")
            return native
    def build_evaluator(settings):
        calls.append(("build_evaluator", settings))
        return evaluator
    core.ArtifactStore = Store
    core.HarnessFactory = Factory
    ai.build_ai_assertion_evaluator = build_evaluator
    monkeypatch.setitem(sys.modules, "fsq_agent", package)
    monkeypatch.setitem(sys.modules, "fsq_agent.core", core)
    monkeypatch.setitem(sys.modules, "fsq_agent.ai_services", ai)
    return calls, evaluator


def memory_settings(tmp_path):
    return NS(output=NS(runs_dir=tmp_path / "private-runs"),
              runtime_secrets=NS(private_values=lambda: {"fixture": "secret"}),
              harness=NS(platform="android", android=NS(app_id="fixture.app", serial="exact-serial")))




def test_new_native_write_surface_fails_closed_and_closes_created_harness(monkeypatch, tmp_path):
    native = MemoryHarness()
    native.action_space = lambda: [NS(driver_method="new_unbudgeted_write", metadata={"executor_kind": "driver"})]
    install_memory_factory_modules(monkeypatch, native)
    budget = NativeDispatchBudget(3, 100, clock=lambda: 1)
    with pytest.raises(NativeBoundaryError, match="Unsupported native driver capability"):
        build_native_harness_factory(memory_settings(tmp_path), budget)("run-1")
    assert native.close_calls == 1
    assert [event["event"] for event in budget.snapshot()["events"]] == ["close_started", "close_succeeded"]


def test_native_construction_failure_does_not_invent_observed_close_success(monkeypatch, tmp_path):
    native = MemoryHarness()
    calls, _ = install_memory_factory_modules(monkeypatch, native, fail_construction=True)
    budget = NativeDispatchBudget(3, 100, clock=lambda: 1)
    with pytest.raises(OSError):
        build_native_harness_factory(memory_settings(tmp_path), budget)("run-1")
    assert ("evaluator_close",) in calls
    assert native.close_calls == 0
    assert budget.snapshot()["events"][-1]["closeOutcome"] == "not_observable"
    assert not any(event["event"].startswith("close_") for event in budget.snapshot()["events"])


def test_deadline_and_bad_runid_prevent_factory_collaborator_construction(monkeypatch, tmp_path):
    native = MemoryHarness()
    calls, _ = install_memory_factory_modules(monkeypatch, native)
    budget = NativeDispatchBudget(3, 1, clock=lambda: 1)
    with pytest.raises(NativeDeadlineExceeded):
        build_native_harness_factory(memory_settings(tmp_path), budget)("run-1")
    assert calls == []
    budget = NativeDispatchBudget(3, 100, clock=lambda: 1)
    with pytest.raises(ValueError):
        build_native_harness_factory(memory_settings(tmp_path), budget)("../outside")
    assert calls == []
