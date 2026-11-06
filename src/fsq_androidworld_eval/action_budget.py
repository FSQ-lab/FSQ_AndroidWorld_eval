"""One official reference step grants one attempted, classified Appium UI action.

The proxy submits only sanitized command descriptors. A grant is counted even when
upstream fails; rejection is not execution. No gate lock spans upstream I/O.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Condition
import time
from typing import Any

from fsq_androidworld_eval.lifecycle import EpisodeDeadlines


STEP_BUDGET_PROTOCOL = {
    "runner": "android_world.episode_runner.run_episode",
    "allocator": "android_world.suite_utils._allocate_step_budget",
    "stepUnit": "one gated Appium UI interaction",
    "version": 1,
}


class StepBudgetExceeded(RuntimeError):
    """The reference loop no longer authorizes another mutation."""


@dataclass
class _Ticket:
    record: dict[str, Any]
    granted: bool = False
    rejected: bool = False
    completed: bool = False


class ActionPermit:
    """A single-use grant whose completion must be reported in a finally block."""

    def __init__(self, gate: ActionGate, ticket: _Ticket):
        self._gate = gate
        self._ticket = ticket

    def complete(self, status: int | None = None) -> None:
        with self._gate._condition:
            if self._ticket.completed:
                return
            if status is not None:
                self._ticket.record["status"] = status
            self._ticket.completed = True
            self._gate._inflight -= 1
            self._gate._condition.notify_all()


class ActionGate:
    """FIFO rendezvous between HTTP workers and the official episode agent.

    ``submit`` takes trusted, already-templated ``kind``/``path`` strings, never
    request bodies. Extra fields are discarded. Shared business deadlines stop
    new grants without cancelling granted upstream I/O. ``advance_step`` may
    also use a shorter caller timeout; neither timeout invents an HTTP result.
    """

    def __init__(self) -> None:
        self._condition = Condition()
        self._advancing = False
        self._pending: deque[_Ticket] = deque()
        self._actions: list[dict[str, Any]] = []
        self._rejected = 0
        self._closed = False
        self._finished = False
        self._closure_reason: str | None = None
        self._inflight = 0
        self._deadlines: EpisodeDeadlines | None = None

    def bind_deadlines(self, deadlines: EpisodeDeadlines) -> None:
        with self._condition:
            self._deadlines = deadlines
            self._condition.notify_all()

    def _expire_business(self) -> None:
        if (
            not self._closed and not self._finished
            and self._deadlines is not None and self._deadlines.expired("business")
        ):
            self._stop(finished=False, reason="business_deadline")

    def submit(self, action: dict[str, Any]) -> ActionPermit:
        record = {key: action[key] for key in ("kind", "path")}
        if not all(isinstance(value, str) for value in record.values()):
            raise TypeError("Action descriptors require sanitized kind/path strings")
        ticket = _Ticket(record)
        with self._condition:
            self._expire_business()
            if self._closed or self._finished:
                self._rejected += 1
                raise StepBudgetExceeded("The official reference action budget is closed")
            self._pending.append(ticket)
            self._condition.notify_all()
            while not ticket.granted and not ticket.rejected:
                self._expire_business()
                if not ticket.rejected:
                    self._condition.wait(
                        None if self._deadlines is None
                        else self._deadlines.remaining("business")
                    )
            if ticket.rejected:
                raise StepBudgetExceeded("The official reference action budget is closed")
            return ActionPermit(self, ticket)

    def advance_step(self, timeout: float | None = None) -> dict[str, Any] | None:
        deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)

        def remaining(*, inflight: bool = False) -> float | None:
            value = None if deadline is None else deadline - time.monotonic()
            if self._deadlines is not None:
                business = self._deadlines.remaining("business")
                if business <= 0:
                    self._stop(finished=False, reason="business_deadline")
                    if inflight:
                        raise TimeoutError("The Appium business deadline expired")
                    return 0.0
                value = business if value is None else min(value, business)
            if value is not None and value <= 0:
                raise TimeoutError("Timed out waiting for an Appium action")
            return value

        # A condition-protected flag serializes consumers without holding any
        # mutex while the granted HTTP worker is doing upstream I/O.
        with self._condition:
            while self._advancing:
                self._expire_business()
                if self._closed or self._finished:
                    return None
                self._condition.wait(remaining())
            self._advancing = True
            try:
                while not self._pending:
                    self._expire_business()
                    if self._closed or self._finished:
                        return None
                    self._condition.wait(remaining())
                if self._closed or self._finished:
                    return None
                remaining()
                if self._closed or self._finished:
                    return None
                ticket = self._pending.popleft()
                ticket.granted = True
                self._actions.append(ticket.record)
                self._inflight += 1
                self._condition.notify_all()
                while not ticket.completed:
                    self._condition.wait(remaining(inflight=True))
                return dict(ticket.record)
            finally:
                self._advancing = False
                self._condition.notify_all()

    def _stop(self, *, finished: bool, reason: str) -> None:
        # Expiry checks may already hold this reentrant condition lock.
        with self._condition:
            if finished:
                self._finished = True
            else:
                self._closed = True
            if self._closure_reason is None:
                self._closure_reason = reason
            while self._pending:
                ticket = self._pending.popleft()
                ticket.rejected = True
                self._rejected += 1
            self._condition.notify_all()

    def close_budget(self, reason: str = "step_budget") -> None:
        self._stop(finished=False, reason=reason)

    def mark_agent_finished(self) -> None:
        self._stop(finished=True, reason="agent_finished")

    @property
    def executed_action_count(self) -> int:
        with self._condition:
            return len(self._actions)

    def snapshot(self) -> dict[str, Any]:
        with self._condition:
            self._expire_business()
            return {
                "executedActionCount": len(self._actions),
                "rejectedActionCount": self._rejected,
                "inflightActionCount": self._inflight,
                "closed": self._closed or self._finished,
                "closureReason": self._closure_reason,
                "agentFinished": self._finished,
                "actions": [dict(action) for action in self._actions],
            }
