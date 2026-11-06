from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock

import pytest

from fsq_androidworld_eval.action_budget import ActionGate, StepBudgetExceeded
import fsq_androidworld_eval.lifecycle as lifecycle
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines


ACTION = {"kind": "click", "path": "/session/:sessionId/element/:elementId/click"}


def _pending(gate: ActionGate, count: int = 1) -> None:
    with gate._condition:
        assert gate._condition.wait_for(lambda: len(gate._pending) >= count, timeout=2)


def test_concurrent_submitters_cannot_execute_more_than_granted_steps() -> None:
    gate = ActionGate()
    mutations: list[int] = []
    lock = Lock()

    def mutate(number: int) -> bool:
        try:
            permit = gate.submit(ACTION)
        except StepBudgetExceeded:
            return False
        try:
            with lock:
                mutations.append(number)
        finally:
            permit.complete(200)
        return True

    with ThreadPoolExecutor(max_workers=8) as workers:
        futures = [workers.submit(mutate, number) for number in range(8)]
        try:
            _pending(gate, 8)
            assert mutations == []
            assert gate.advance_step(timeout=2) == {**ACTION, "status": 200}
            assert gate.advance_step(timeout=2) == {**ACTION, "status": 200}
        finally:
            gate.close_budget()
        assert sum(future.result(timeout=2) for future in futures) == 2
    assert len(mutations) == 2
    assert gate.snapshot() == {
        "executedActionCount": 2,
        "rejectedActionCount": 6,
        "inflightActionCount": 0,
        "closed": True,
        "closureReason": "step_budget",
        "agentFinished": False,
        "actions": [{**ACTION, "status": 200}, {**ACTION, "status": 200}],
    }


def test_shutdown_rejects_queued_and_new_actions_and_wakes_step_waiter() -> None:
    for stop in ("close_budget", "mark_agent_finished"):
        gate = ActionGate()
        with ThreadPoolExecutor(max_workers=1) as workers:
            queued = workers.submit(gate.submit, ACTION)
            _pending(gate)
            getattr(gate, stop)()
            getattr(gate, stop)()
            with pytest.raises(StepBudgetExceeded):
                queued.result(timeout=2)
        with pytest.raises(StepBudgetExceeded):
            gate.submit(ACTION)
        assert gate.advance_step(timeout=0) is None
        assert gate.snapshot() == {
            "executedActionCount": 0,
            "rejectedActionCount": 2,
            "inflightActionCount": 0,
            "closed": True,
            "closureReason": "step_budget" if stop == "close_budget" else "agent_finished",
            "agentFinished": stop == "mark_agent_finished",
            "actions": [],
        }

        empty = ActionGate()
        waiting = Event()

        def advance() -> object:
            waiting.set()
            return empty.advance_step(timeout=2)

        with ThreadPoolExecutor(max_workers=1) as workers:
            future = workers.submit(advance)
            assert waiting.wait(2)
            getattr(empty, stop)()
            assert future.result(timeout=2) is None


def test_granted_attempt_waits_for_completion_even_when_agent_finishes() -> None:
    gate = ActionGate()
    granted = Event()
    release = Event()

    def request() -> None:
        permit = gate.submit({**ACTION, "payload": "must not be recorded"})
        granted.set()
        assert release.wait(2)
        permit.complete(500)
        permit.complete(200)

    with ThreadPoolExecutor(max_workers=2) as workers:
        request_future = workers.submit(request)
        step = workers.submit(gate.advance_step, 2)
        try:
            assert granted.wait(2)
            gate.mark_agent_finished()
            assert not step.done()
            assert gate.snapshot()["actions"] == [ACTION]
        finally:
            release.set()
        assert step.result(timeout=2) == {**ACTION, "status": 500}
        request_future.result(timeout=2)
    record = gate.snapshot()
    record["actions"][0]["kind"] = "tampered"
    assert gate.snapshot()["actions"] == [{**ACTION, "status": 500}]
    assert gate.advance_step(timeout=0) is None


def test_timeout_never_grants_a_pending_action_or_invents_a_status() -> None:
    gate = ActionGate()
    with pytest.raises(TimeoutError):
        gate.advance_step(timeout=0.01)
    with ThreadPoolExecutor(max_workers=1) as workers:
        future = workers.submit(gate.submit, ACTION)
        try:
            _pending(gate)
            with pytest.raises(TimeoutError):
                gate.advance_step(timeout=0)
            assert gate.snapshot()["executedActionCount"] == 0
        finally:
            gate.close_budget()
        with pytest.raises(StepBudgetExceeded):
            future.result(timeout=2)

    gate = ActionGate()
    with ThreadPoolExecutor(max_workers=1) as workers:
        permit_future = workers.submit(gate.submit, ACTION)
        _pending(gate)
        with pytest.raises(TimeoutError):
            gate.advance_step(timeout=0.01)
        permit = permit_future.result(timeout=2)
        gate.close_budget()
        assert gate.snapshot()["actions"] == [ACTION]
        permit.complete(503)
        assert gate.snapshot()["actions"] == [{**ACTION, "status": 503}]


def test_concurrent_reference_calls_serialize_grants_through_completion() -> None:
    gate = ActionGate()
    first_granted = Event()
    release = Event()
    second_granted = Event()

    def first_request() -> None:
        permit = gate.submit(ACTION)
        first_granted.set()
        assert release.wait(2)
        permit.complete(200)

    def second_request() -> None:
        permit = gate.submit(ACTION)
        second_granted.set()
        permit.complete(200)

    with ThreadPoolExecutor(max_workers=4) as workers:
        first = workers.submit(first_request)
        _pending(gate)
        step_one = workers.submit(gate.advance_step, 2)
        assert first_granted.wait(2)
        second = workers.submit(second_request)
        _pending(gate)
        step_two = workers.submit(gate.advance_step, 2)
        try:
            assert not second_granted.is_set()
            assert gate.snapshot()["executedActionCount"] == 1
        finally:
            release.set()
        assert step_one.result(timeout=2)["status"] == 200
        assert step_two.result(timeout=2)["status"] == 200
        first.result(timeout=2)
        second.result(timeout=2)
    gate.close_budget()
    assert second_granted.is_set()
    assert gate.snapshot()["executedActionCount"] == 2


def test_business_deadline_wakes_an_idle_reference_step_without_actions() -> None:
    gate = ActionGate()
    deadlines = EpisodeDeadlines(0.03, cleanup_seconds=1, termination_grace_seconds=1)
    gate.bind_deadlines(deadlines)
    deadlines.start()
    with ThreadPoolExecutor(max_workers=1) as workers:
        step = workers.submit(gate.advance_step)
        try:
            assert step.result(timeout=2) is None
        finally:
            gate.close_budget()
    snapshot = gate.snapshot()
    assert snapshot["closureReason"] == "business_deadline"
    assert snapshot["executedActionCount"] == 0
    assert snapshot["inflightActionCount"] == 0


def test_queued_mutation_expires_without_a_reference_step() -> None:
    gate = ActionGate()
    deadlines = EpisodeDeadlines(0.03, cleanup_seconds=1, termination_grace_seconds=1)
    gate.bind_deadlines(deadlines)
    deadlines.start()
    with ThreadPoolExecutor(max_workers=1) as workers:
        queued = workers.submit(gate.submit, ACTION)
        try:
            with pytest.raises(StepBudgetExceeded):
                queued.result(timeout=2)
        finally:
            gate.close_budget()
    assert gate.snapshot()["executedActionCount"] == 0
    assert gate.snapshot()["rejectedActionCount"] == 1
    assert gate.snapshot()["closureReason"] == "business_deadline"


def test_business_expiry_preserves_granted_io_but_rejects_all_later_mutations(
    monkeypatch,
) -> None:
    now = [100.0]
    monkeypatch.setattr(lifecycle, "monotonic", lambda: now[0])
    gate = ActionGate()
    deadlines = EpisodeDeadlines(10, cleanup_seconds=10, termination_grace_seconds=1)
    gate.bind_deadlines(deadlines)
    deadlines.start()
    granted = Event()
    release = Event()

    def request() -> None:
        permit = gate.submit(ACTION)
        granted.set()
        try:
            assert release.wait(2)
        finally:
            permit.complete(200)

    with ThreadPoolExecutor(max_workers=3) as workers:
        request_future = workers.submit(request)
        step = workers.submit(gate.advance_step)
        try:
            assert granted.wait(2)
            queued = workers.submit(gate.submit, ACTION)
            _pending(gate)
            now[0] = 111.0
            with gate._condition:
                gate._condition.notify_all()
            with pytest.raises(TimeoutError):
                step.result(timeout=2)
            with pytest.raises(StepBudgetExceeded):
                queued.result(timeout=2)
            with pytest.raises(StepBudgetExceeded):
                gate.submit(ACTION)
            snapshot = gate.snapshot()
            assert snapshot["actions"] == [ACTION]
            assert snapshot["executedActionCount"] == 1
            assert snapshot["inflightActionCount"] == 1
            assert snapshot["rejectedActionCount"] == 2
            assert snapshot["closureReason"] == "business_deadline"
            assert not snapshot["agentFinished"]
        finally:
            release.set()
        request_future.result(timeout=2)
    assert gate.snapshot()["inflightActionCount"] == 0
    assert gate.snapshot()["actions"] == [{**ACTION, "status": 200}]


def test_first_closure_reason_survives_worker_finish_and_repeated_shutdown() -> None:
    gate = ActionGate()
    gate.close_budget(reason="business_deadline")
    gate.mark_agent_finished()
    gate.close_budget()
    snapshot = gate.snapshot()
    assert snapshot["closureReason"] == "business_deadline"
    assert snapshot["closed"] is True
    assert snapshot["agentFinished"] is True

