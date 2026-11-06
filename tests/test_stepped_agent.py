"""Exercise the locked reference loop against the real concurrent action gate."""

from concurrent.futures import ThreadPoolExecutor
import subprocess
import threading
from typing import Any

from android_world import constants, episode_runner
import pytest

from fsq_androidworld_eval.action_budget import ActionGate, StepBudgetExceeded
import fsq_androidworld_eval.lifecycle as lifecycle
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines
from fsq_androidworld_eval.stepped_agent import AgentTerminated, AppiumSteppedAgent


class EpisodeEnvironment:
    """Only the environment reset/state surface used by the official runner."""

    def __init__(self) -> None:
        self.resets: list[bool] = []
        self.values: list[int] = []

    def reset(self, go_home: bool = False) -> None:
        self.resets.append(go_home)
        self.values.clear()


def _mutate(gate: ActionGate, env: EpisodeEnvironment, value: int) -> None:
    permit = gate.submit({"kind": "click", "path": "/session/:sessionId/element/:elementId/click"})
    try:
        env.values.append(value)
    finally:
        permit.complete(status=200)


@pytest.mark.parametrize("max_steps", [1, 3])
def test_official_episode_caps_continuous_worker_and_finishes_after_denial(
    max_steps: int,
) -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    started = threading.Event()
    denied = threading.Event()
    returned: dict[str, Any] = {"agentCompleted": True}

    def run_agent() -> dict[str, Any]:
        started.set()
        assert env.resets == [True]
        assert agent._max_steps == max_steps
        for value in range(max_steps + 2):
            try:
                _mutate(gate, env, value)
            except StepBudgetExceeded:
                denied.set()
                # Real post-budget reconciliation reads the state mutations
                # actually performed; it does not fabricate a task outcome.
                returned["observedValues"] = list(env.values)
                return returned
        raise AssertionError("Official step budget did not stop continuous execution")

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    assert not started.is_set()
    assert env.resets == []

    episode = episode_runner.run_episode(
        "perform actions",
        agent,
        max_n_steps=max_steps,
        start_on_home_screen=True,
        print_fn=lambda message: None,
    )

    assert episode.done is False
    assert env.values == list(range(max_steps))
    assert episode.step_data[constants.STEP_NUMBER] == list(range(max_steps))
    assert len(episode.step_data["appiumAction"]) == max_steps
    assert all(record["status"] == 200 for record in episode.step_data["appiumAction"])
    assert agent.finish() is returned
    assert returned == {
        "agentCompleted": True, "observedValues": list(range(max_steps)),
    }
    assert denied.is_set()
    assert agent.finish() is returned
    assert gate.snapshot()["executedActionCount"] == max_steps
    assert agent.reference_step_count == max_steps
    assert gate.snapshot()["rejectedActionCount"] == 1
    with pytest.raises(StepBudgetExceeded):
        _mutate(gate, env, 999)
    assert env.values == list(range(max_steps))
    assert env.resets == [True]
    with pytest.raises(RuntimeError, match="cannot reset"):
        agent.reset()
    assert env.resets == [True]


def test_official_episode_observes_completed_worker_without_fake_action() -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    result: dict[str, Any] = {"agentCompleted": True}

    def run_agent() -> dict[str, Any]:
        assert env.resets == [False]
        result["resetCount"] = len(env.resets)
        result["observedValues"] = list(env.values)
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    episode = episode_runner.run_episode(
        "observe only", agent, max_n_steps=4, print_fn=lambda message: None
    )

    assert episode.done is True
    assert episode.step_data == {
        "appiumAction": [None],
        constants.STEP_NUMBER: [0],
    }
    assert gate.snapshot()["executedActionCount"] == 0
    assert agent.finish() is result
    assert result == {"agentCompleted": True, "resetCount": 1, "observedValues": []}
    assert agent.reference_step_count == 1


def test_final_mutation_is_not_a_completion_declaration() -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()

    def run_agent() -> dict[str, Any]:
        _mutate(gate, env, 7)
        return {"agentCompleted": True, "observedValues": list(env.values)}

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    episode = episode_runner.run_episode(
        "one mutation", agent, max_n_steps=3, print_fn=lambda message: None
    )

    assert episode.done is True
    assert episode.step_data[constants.STEP_NUMBER] == [0, 1]
    assert episode.step_data["appiumAction"][0]["status"] == 200
    assert episode.step_data["appiumAction"][1] is None
    assert gate.snapshot()["executedActionCount"] == 1
    assert agent.finish() == {"agentCompleted": True, "observedValues": [7]}
    assert agent.reference_step_count == 2


@pytest.mark.parametrize("mutation", [False, True])
def test_zero_exit_without_final_response_terminates_without_done_or_extra_steps(
    mutation: bool,
) -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    result = {
        "exitCode": 0,
        "agentCompleted": False,
        "termination": {"reason": "unknown_termination"},
    }

    def run_agent() -> dict[str, Any]:
        if mutation:
            _mutate(gate, env, 7)
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    with pytest.raises(AgentTerminated) as caught:
        episode_runner.run_episode(
            "no final response", agent, max_n_steps=50, print_fn=lambda message: None
        )
    assert caught.value.reason == "unknown_termination"
    assert caught.value.result is result
    assert agent.reference_step_count == int(mutation)
    assert gate.snapshot()["executedActionCount"] == int(mutation)
    assert env.values == ([7] if mutation else [])
    assert agent._worker_finished.is_set()
    assert agent.finish() is result


@pytest.mark.parametrize("completion", [None, False, 1, "true"])
def test_completion_requires_literal_true(completion: Any) -> None:
    result = {"agentCompleted": completion}
    agent = AppiumSteppedAgent(
        EpisodeEnvironment(), lambda: result, ActionGate(), EpisodeDeadlines(5)
    )
    with pytest.raises(AgentTerminated) as caught:
        agent.step("no inferred completion")
    assert caught.value.reason == "unknown_termination"
    assert caught.value.result is result
    assert agent.reference_step_count == 0


@pytest.mark.parametrize(
    "failure",
    [RuntimeError("real worker failure"), subprocess.TimeoutExpired("omp", 2)],
)
def test_worker_exception_wakes_reference_loop_and_is_not_replaced(
    failure: BaseException,
) -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()

    def run_agent() -> dict[str, Any]:
        assert env.resets == [False]
        raise failure

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    with pytest.raises(type(failure)) as caught:
        episode_runner.run_episode(
            "worker fails", agent, max_n_steps=2, print_fn=lambda message: None
        )
    assert caught.value is failure
    with pytest.raises(type(failure)) as caught:
        agent.finish()
    assert caught.value is failure
    with pytest.raises(StepBudgetExceeded):
        _mutate(gate, env, 99)
    assert env.values == []
    assert gate.snapshot()["executedActionCount"] == 0


def test_finish_propagates_unhandled_worker_failure_after_budget_closes() -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    failures: list[BaseException] = []

    def run_agent() -> dict[str, Any]:
        _mutate(gate, env, 1)
        try:
            _mutate(gate, env, 2)
        except StepBudgetExceeded as failure:
            failures.append(failure)
            raise
        raise AssertionError("Second mutation must not run")

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    episode = episode_runner.run_episode(
        "no recovery from rejection", agent, max_n_steps=1, print_fn=lambda message: None
    )
    assert episode.done is False
    with pytest.raises(StepBudgetExceeded) as caught:
        agent.finish()
    assert failures == [caught.value]
    assert env.values == [1]
    assert gate.snapshot()["executedActionCount"] == 1
    assert gate.snapshot()["rejectedActionCount"] == 1


class ManualClock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


@pytest.mark.parametrize("waiting_method", ["step", "finish"])
def test_force_deadline_is_shared_and_never_invents_worker_shutdown(
    monkeypatch, waiting_method: str
) -> None:
    clock = ManualClock()
    monkeypatch.setattr(lifecycle, "monotonic", clock)
    env = EpisodeEnvironment()
    gate = ActionGate()
    release = threading.Event()
    waiting = threading.Event()
    result: dict[str, Any] = {"agentCompleted": True}
    deadlines = EpisodeDeadlines(10, cleanup_seconds=5, termination_grace_seconds=5)

    def run_agent() -> dict[str, Any]:
        _mutate(gate, env, 1)
        waiting.set()
        assert release.wait(timeout=5)
        result["observedValues"] = list(env.values)
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, deadlines)
    # Reset/setup time is outside the shared envelope until the first step.
    clock.now = 1000.0
    episode = episode_runner.run_episode(
        "bounded worker", agent, max_n_steps=1, print_fn=lambda message: None
    )
    assert episode.done is False
    assert waiting.wait(timeout=2)
    clock.now = 1021.0
    try:
        with pytest.raises(TimeoutError):
            if waiting_method == "step":
                agent.step("no fresh timeout")
            else:
                agent.finish()
        assert "observedValues" not in result
        with pytest.raises(StepBudgetExceeded):
            _mutate(gate, env, 2)
        assert env.values == [1]
        assert agent.reference_step_count == 1
    finally:
        release.set()
        assert agent._worker is not None
        agent._worker.join(timeout=2)
        assert not agent._worker.is_alive()
    assert agent.finish() is result
    assert result == {"agentCompleted": True, "observedValues": [1]}


@pytest.mark.parametrize("waiting_method", ["step", "finish"])
def test_cleanup_worker_can_settle_after_business_deadline_without_done(
    monkeypatch, waiting_method: str,
) -> None:
    clock = ManualClock()
    monkeypatch.setattr(lifecycle, "monotonic", clock)
    env = EpisodeEnvironment()
    gate = ActionGate()
    release = threading.Event()
    waiting = threading.Event()
    result = {"agentCompleted": True, "termination": {"reason": "completed"}}
    deadlines = EpisodeDeadlines(10, cleanup_seconds=5, termination_grace_seconds=5)

    def run_agent() -> dict[str, Any]:
        _mutate(gate, env, 1)
        waiting.set()
        assert release.wait(5)
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, deadlines)
    assert agent.step("one mutation").done is False
    assert waiting.wait(2)
    clock.now = 111.0
    with ThreadPoolExecutor(max_workers=1) as workers:
        pending = workers.submit(
            agent.step, "cleanup only"
        ) if waiting_method == "step" else workers.submit(agent.finish)
        try:
            with gate._condition:
                assert gate._condition.wait_for(lambda: gate._closed, timeout=2)
            assert not pending.done()
            with pytest.raises(StepBudgetExceeded):
                _mutate(gate, env, 2)
        finally:
            release.set()
        if waiting_method == "step":
            with pytest.raises(AgentTerminated) as caught:
                pending.result(timeout=2)
            assert caught.value.result is result
            assert caught.value.reason == "completed"
        else:
            assert pending.result(timeout=2) is result
    assert agent.reference_step_count == 1
    assert gate.snapshot()["closureReason"] == "business_deadline"
    assert agent.finish() is result


@pytest.mark.parametrize("failure", [None, RuntimeError("cleanup worker failure")])
def test_inflight_http_settles_in_cleanup_without_reporting_episode_done(
    monkeypatch, failure: BaseException | None,
) -> None:
    clock = ManualClock()
    monkeypatch.setattr(lifecycle, "monotonic", clock)
    env = EpisodeEnvironment()
    gate = ActionGate()
    granted = threading.Event()
    release = threading.Event()
    deadlines = EpisodeDeadlines(10, cleanup_seconds=5, termination_grace_seconds=5)
    result = {"agentCompleted": True, "termination": {"reason": "completed"}}

    def run_agent() -> dict[str, Any]:
        permit = gate.submit({"kind": "click", "path": "/session/:sessionId/click"})
        granted.set()
        try:
            assert release.wait(5)
            env.values.append(1)
        finally:
            permit.complete(200)
        if failure is not None:
            raise failure
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, deadlines)
    with ThreadPoolExecutor(max_workers=1) as workers:
        step = workers.submit(agent.step, "HTTP in flight")
        try:
            assert granted.wait(2)
            clock.now = 111.0
            with gate._condition:
                gate._condition.notify_all()
                assert gate._condition.wait_for(lambda: gate._closed, timeout=2)
            assert not step.done()
            snapshot = gate.snapshot()
            assert snapshot["inflightActionCount"] == 1
            assert snapshot["actions"] == [
                {"kind": "click", "path": "/session/:sessionId/click"}
            ]
            assert agent.reference_step_count == 1
            with pytest.raises(StepBudgetExceeded):
                _mutate(gate, env, 2)
        finally:
            release.set()
        if failure is None:
            with pytest.raises(AgentTerminated) as caught:
                step.result(timeout=2)
            assert caught.value.result is result
            assert agent.finish() is result
        else:
            with pytest.raises(type(failure)) as caught:
                step.result(timeout=2)
            assert caught.value is failure
            with pytest.raises(type(failure)) as caught:
                agent.finish()
            assert caught.value is failure
    assert env.values == [1]
    assert gate.snapshot()["inflightActionCount"] == 0
    assert gate.snapshot()["actions"][0]["status"] == 200


def test_business_deadline_wakes_step_with_only_an_inflight_mcp_request() -> None:
    gate = ActionGate()
    waiting = threading.Event()
    release = threading.Event()
    result = {
        "agentCompleted": False, "termination": {"reason": "business_deadline"},
    }

    def run_agent() -> dict[str, Any]:
        waiting.set()
        assert release.wait(5)
        return result

    deadlines = EpisodeDeadlines(0.03, cleanup_seconds=1, termination_grace_seconds=1)
    agent = AppiumSteppedAgent(EpisodeEnvironment(), run_agent, gate, deadlines)
    with ThreadPoolExecutor(max_workers=1) as workers:
        step = workers.submit(agent.step, "MCP observation in flight")
        try:
            assert waiting.wait(2)
            with gate._condition:
                assert gate._condition.wait_for(lambda: gate._closed, timeout=2)
            assert not step.done()
            assert gate.snapshot()["executedActionCount"] == 0
        finally:
            release.set()
        with pytest.raises(AgentTerminated) as caught:
            step.result(timeout=2)
        assert caught.value.reason == "business_deadline"
        assert caught.value.result is result
    assert agent.reference_step_count == 0
    assert agent.finish() is result


def test_finish_closes_pending_mutations_before_waiting_for_worker() -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    denial_observed = threading.Event()

    def run_agent() -> dict[str, Any]:
        _mutate(gate, env, 3)
        try:
            _mutate(gate, env, 4)
        except StepBudgetExceeded:
            denial_observed.set()
            return {"observedValues": list(env.values)}
        raise AssertionError("Post-budget action was forwarded")

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    episode = episode_runner.run_episode(
        "one allowed action", agent, max_n_steps=1, print_fn=lambda message: None
    )
    assert episode.done is False
    assert agent.finish() == {"observedValues": [3]}
    assert denial_observed.is_set()
    assert gate.snapshot()["executedActionCount"] == 1
    assert gate.snapshot()["rejectedActionCount"] == 1


def test_zero_step_episode_never_resets_or_starts_worker() -> None:
    env = EpisodeEnvironment()
    gate = ActionGate()
    started = threading.Event()

    def run_agent() -> dict[str, Any]:
        started.set()
        raise AssertionError("Zero-step episode must not invoke OMP")

    agent = AppiumSteppedAgent(env, run_agent, gate, EpisodeDeadlines(5))
    episode = episode_runner.run_episode(
        "zero budget", agent, max_n_steps=0, print_fn=lambda message: None
    )
    assert episode.done is False
    assert episode.step_data == {}
    assert env.resets == []
    assert not started.is_set()
    with pytest.raises(RuntimeError, match="never started"):
        agent.finish()
    with pytest.raises(StepBudgetExceeded):
        _mutate(gate, env, 1)
    with pytest.raises(RuntimeError, match="budget is already closed"):
        agent.step("must remain unstarted")
    assert not started.is_set()
    assert env.values == []


def test_timely_explicit_completion_survives_later_cleanup_settlement(monkeypatch):
    clock = ManualClock()
    monkeypatch.setattr(lifecycle, "monotonic", clock)
    env = EpisodeEnvironment()
    gate = ActionGate()
    deadlines = EpisodeDeadlines(10, cleanup_seconds=5, termination_grace_seconds=5)
    completed = threading.Event()
    cleanup_release = threading.Event()

    def run_agent():
        _mutate(gate, env, 1)
        result = {
            "agentCompleted": True,
            "completedBeforeBusinessDeadline": not deadlines.expired("business"),
            "termination": {"reason": "completed"},
        }
        completed.set()
        assert cleanup_release.wait(5)
        return result

    agent = AppiumSteppedAgent(env, run_agent, gate, deadlines)
    assert agent.step("one mutation").done is False
    assert completed.wait(2)
    clock.now = 111.0
    cleanup_release.set()
    assert agent.step("observe settled cleanup").done is True
    assert env.values == [1]
    assert agent.finish()["completedBeforeBusinessDeadline"] is True
