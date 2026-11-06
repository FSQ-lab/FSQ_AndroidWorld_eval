"""Run continuous OMP execution through the official AndroidWorld step loop.

Each reference step grants one real Appium mutation through ``ActionGate``;
observations and session lifecycle requests remain the proxy's responsibility.
This adapter is single-episode: construction and reset never start OMP, and
``finish`` closes the budget before awaiting the worker's actual result.

``run_agent`` must itself bound and clean up its subprocess. Shared monotonic
deadlines close mutation permits at the business boundary, while already-granted
I/O, observations, and quit may settle until the force boundary. Returning from
the worker is not an agent completion declaration.
"""

from collections.abc import Callable
import threading
from typing import Any

from android_world.agents import base_agent
from android_world.env import interface

from fsq_androidworld_eval.action_budget import ActionGate
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines


class AgentTerminated(RuntimeError):
    """The worker settled without completing the reference episode."""

    def __init__(self, reason: str, result: dict[str, Any]) -> None:
        super().__init__(f"Continuous Appium agent terminated: {reason}")
        self.reason = reason
        self.result = result


class AppiumSteppedAgent(base_agent.EnvironmentInteractingAgent):
    """Adapt one bounded, continuous agent run to ``run_episode``."""

    def __init__(
        self,
        env: interface.AsyncEnv,
        run_agent: Callable[[], dict[str, Any]],
        action_gate: ActionGate,
        deadlines: EpisodeDeadlines,
    ) -> None:
        super().__init__(env, name="AppiumSteppedAgent")
        self._run_agent = run_agent
        self._action_gate = action_gate
        self._deadlines = deadlines
        self._action_gate.bind_deadlines(deadlines)
        self._reference_steps = 0
        self._worker: threading.Thread | None = None
        self._worker_finished = threading.Event()
        self._worker_result: dict[str, Any] | None = None
        self._worker_error: BaseException | None = None
        self._budget_closed = False

    def reset(self, go_home: bool = False) -> None:
        """Use the official reset, but never reset under a running episode."""
        if self._worker is not None:
            raise RuntimeError("AppiumSteppedAgent cannot reset after execution starts")
        super().reset(go_home=go_home)

    def _run_worker(self) -> None:
        try:
            self._worker_result = self._run_agent()
        except BaseException as error:
            self._worker_error = error
        finally:
            try:
                self._action_gate.mark_agent_finished()
            finally:
                self._worker_finished.set()

    def _start_worker(self) -> None:
        if self._worker is not None:
            return
        if self._budget_closed:
            raise RuntimeError("AppiumSteppedAgent budget is already closed")
        self._deadlines.start()
        self._worker = threading.Thread(
            target=self._run_worker,
            name="appium-stepped-agent",
            daemon=True,
        )
        self._worker.start()

    @property
    def reference_step_count(self) -> int:
        """Include a granted action even if its HTTP response outlives a step."""
        return max(self._reference_steps, self._action_gate.executed_action_count)

    def _close_budget(self, reason: str = "step_budget") -> None:
        self._budget_closed = True
        self._action_gate.close_budget(reason)

    def _raise_worker_error(self) -> None:
        if self._worker_finished.is_set() and self._worker_error is not None:
            raise self._worker_error

    def _wait_for_worker(self) -> None:
        assert self._worker is not None
        self._raise_worker_error()
        self._worker.join(timeout=self._deadlines.remaining("force"))
        if self._worker.is_alive():
            self._raise_worker_error()
            raise TimeoutError("Continuous Appium agent exceeded its force deadline")
        self._raise_worker_error()

    def _result(self) -> dict[str, Any]:
        if not isinstance(self._worker_result, dict):
            raise TypeError("Continuous Appium agent did not return a result dictionary")
        return self._worker_result

    def _completion(self, *, business_expired: bool) -> base_agent.AgentInteractionResult:
        result = self._result()
        termination = result.get("termination")
        completed_before_deadline = (
            isinstance(termination, dict)
            and termination.get("reason") == "completed"
            and result.get("completedBeforeBusinessDeadline") is True
        )
        if result.get("agentCompleted") is True and (not business_expired or completed_before_deadline):
            self._reference_steps += 1
            return base_agent.AgentInteractionResult(
                done=True, data={"appiumAction": None}
            )
        reason = termination.get("reason") if isinstance(termination, dict) else None
        if not isinstance(reason, str):
            reason = "business_deadline" if business_expired else "unknown_termination"
        raise AgentTerminated(reason, result)

    def step(self, goal: str) -> base_agent.AgentInteractionResult:
        """Grant exactly one attempted mutation, or report real worker completion."""
        del goal  # The existing OMP invocation already has the exact task goal.
        self._start_worker()
        try:
            try:
                action = self._action_gate.advance_step()
            except TimeoutError:
                if not self._deadlines.expired("business"):
                    raise
                action = None
            business_expired = self._deadlines.expired("business")
            if business_expired:
                self._close_budget("business_deadline")
            if action is None or business_expired:
                # Gate shutdown wakes the reference loop before the worker
                # returns. Retain the same force boundary while it settles.
                self._wait_for_worker()
                return self._completion(
                    business_expired=self._deadlines.expired("business")
                )
            self._raise_worker_error()
            self._reference_steps += 1
            # A mutation is an attempted step, never a completion declaration.
            return base_agent.AgentInteractionResult(
                done=False, data={"appiumAction": action}
            )
        except BaseException:
            self._close_budget(
                "business_deadline" if self._deadlines.expired("business")
                else "agent_terminated"
            )
            self._raise_worker_error()
            raise

    def finish(self) -> dict[str, Any]:
        """Close all future mutation permits, then return the real OMP result.

        A zero-step episode never starts OMP and therefore has no result. Reads
        and explicit session quit remain available through the proxy while a
        started worker reconciles the exhausted budget and completes shutdown.
        """
        self._close_budget(
            "business_deadline" if self._deadlines.expired("business")
            else "step_budget"
        )
        if self._worker is None:
            raise RuntimeError("AppiumSteppedAgent never started; no agent result exists")
        self._wait_for_worker()
        return self._result()
