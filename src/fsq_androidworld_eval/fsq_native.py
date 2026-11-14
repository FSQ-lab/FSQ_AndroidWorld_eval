"""FSQ-native dispatch accounting (no device imports at module import time).

One unit is an admitted Android Harness write-capability dispatch, not a u2 or
Appium primitive. input_text includes click/optional clear/set_text in one unit.
Construction, u2 service startup, observation and assertion side effects are not
units. Setup/teardown are units; failures consume their reservation. Native
perform_actions is unsupported, so no batching can bypass this boundary.
"""
from __future__ import annotations

import json
import math
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

WRITE_CAPABILITIES = {
    "launch_app": "launchApp", "kill_app": "killApp", "tap_on": "tapOn",
    "tap_at": "tapAt", "long_press_on": "longPressOn", "input_text": "inputText",
    "press_key": "pressKey", "swipe": "swipe",
}
WRITE_ALIASES = {alias: name for name, alias in WRITE_CAPABILITIES.items()}
READ_CAPABILITIES = frozenset({"assert_visible", "assert_not_visible", "assert_state", "assert_with_ai", "ui_snapshot", "screenshot", "read_element"})


class NativeBoundaryError(RuntimeError):
    """A dispatch was refused before forwarding to native FSQ."""


class NativeDeadlineExceeded(NativeBoundaryError):
    pass


class NativeActionBudgetExceeded(NativeBoundaryError):
    pass


class NativeDispatchBudget:
    """Shared, thread-safe, before-forward admission and outcome journal.

    Audit contains identifiers only, never parameters, goal, observations or text.
    attempted includes denied attempts; admitted == succeeded + failed + inFlight.
    A deadline cannot interrupt an in-flight native call: supervisor must kill the
    worker/process group before its official evaluator is allowed to run.
    """

    def __init__(self, maximum: int, deadline: float, *, clock: Callable[[], float] = time.monotonic, journal: Path | None = None):
        if type(maximum) is not int or maximum <= 0:
            raise ValueError("maxActions must be a positive integer")
        if isinstance(deadline, bool) or not isinstance(deadline, (float, int)) or not math.isfinite(deadline):
            raise ValueError("businessDeadlineMonotonic must be finite")
        self.maximum = maximum
        self.deadline = float(deadline)
        self.clock = clock
        self.journal = journal
        self._lock = threading.RLock()
        self._events: list[dict[str, Any]] = []
        self._attempted = self._admitted = self._succeeded = self._failed = self._denied = 0
        self._next_id = 0
        self._pending: set[int] = set()
        self._deadline_exceeded = False

    def _emit(self, event: dict[str, Any]) -> None:
        event = {"sequence": len(self._events) + 1, "monotonic": self.clock(), **event}
        if self.journal is not None:
            fd = os.open(self.journal, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                data = (json.dumps(event, sort_keys=True) + "\n").encode()
                with os.fdopen(fd, "ab", closefd=False) as stream:
                    stream.write(data)
                    stream.flush()
            finally:
                os.close(fd)
        self._events.append(event)

    def check_deadline(self) -> None:
        with self._lock:
            if self.clock() >= self.deadline:
                self._deadline_exceeded = True
                raise NativeDeadlineExceeded("Business deadline reached")

    def dispatch(self, action: str, phase: str, forward: Callable[[], Any], *, step_id: str | None = None) -> Any:
        canonical = WRITE_ALIASES.get(action, action)
        write = canonical in WRITE_CAPABILITIES
        with self._lock:
            if write:
                self._attempted += 1
            reason = None
            if self.clock() >= self.deadline:
                self._deadline_exceeded = True
                reason = "deadline"
            elif canonical in {"perform_actions", "performActions"}:
                reason = "unsupported_batch"
            if write and reason is None and self._admitted >= self.maximum:
                reason = "action_budget"
            if reason:
                if write:
                    self._denied += 1
                self._emit({"event": "denied", "capability": canonical, "phase": phase, "stepId": step_id, "reason": reason, "countedWrite": write})
                error = NativeDeadlineExceeded if reason == "deadline" else NativeActionBudgetExceeded if reason == "action_budget" else NativeBoundaryError
                raise error(reason)
            self._next_id += 1
            ticket = self._next_id
            if write:
                self._admitted += 1
                self._pending.add(ticket)
            self._emit({"event": "attempted", "ticket": ticket, "capability": canonical, "phase": phase, "stepId": step_id, "countedWrite": write})
        try:
            result = forward()
        except BaseException as exc:
            self._finish(ticket, canonical, phase, write, False, type(exc).__name__)
            raise
        succeeded = getattr(result, "status", None) == "passed"
        self._finish(ticket, canonical, phase, write, succeeded, None)
        return result

    def _finish(self, ticket: int, action: str, phase: str, write: bool, success: bool, error: str | None) -> None:
        with self._lock:
            if write:
                self._pending.remove(ticket)
                if success:
                    self._succeeded += 1
                else:
                    self._failed += 1
            self._emit({"event": "succeeded" if success else "failed", "ticket": ticket, "capability": action, "phase": phase, "countedWrite": write, "errorType": error})

    def receipt(self, event: dict[str, Any]) -> None:
        with self._lock:
            self._emit(event)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {"unit": "admitted_android_harness_write_capability_dispatch", "writeCapabilities": list(WRITE_CAPABILITIES), "maximum": self.maximum,
                    "attempted": self._attempted, "admitted": self._admitted, "succeeded": self._succeeded, "failed": self._failed,
                    "denied": self._denied, "inFlight": len(self._pending), "deadlineMonotonic": self.deadline,
                    "deadlineExceeded": self._deadline_exceeded, "events": [dict(event) for event in self._events],
                    "exclusions": ["driver_construction", "uiautomator2_service_startup", "observation_and_assertion_side_effects", "external_processes_and_direct_driver_access"],
                    "securityBoundary": False, "exhausted": self._admitted >= self.maximum,
                    "inputTextUnit": "composite_click_optional_clear_set_text", "deviceRestoredByClose": False}


class BudgetedAndroidHarness:
    """Explicit complete HarnessInterface delegate; no reflection or private mutation."""

    def __init__(self, native: Any, budget: NativeDispatchBudget):
        self.native = native
        self.dispatch_budget = budget

    def configure_observation_redactor(self, redactor: Callable[[str], str]) -> None:
        self.native.configure_observation_redactor(redactor)

    def capture_scope(self, callback: Any) -> Any:
        return self.native.capture_scope(callback)

    def get_context(self) -> Any:
        return self.native.get_context()

    def action_space(self) -> Any:
        return self.native.action_space()

    def before_action(self, step: Any, context: Any) -> None:
        return self.native.before_action(step, context)

    def invoke_action(self, step: Any, context: Any) -> Any:
        return self.dispatch_budget.dispatch(step.action_name, step.kind,
            lambda: self.native.invoke_action(step, context), step_id=step.step_id)

    def after_action(self, step: Any, context: Any, action_result: Any) -> None:
        return self.native.after_action(step, context, action_result)

    def capture_artifact(self, kind: str, reason: str, context: Any, step_id: str, phase: str) -> Any:
        return self.native.capture_artifact(kind, reason, context, step_id, phase)

    def classify_error(self, error: BaseException, phase: str, step: Any) -> Any:
        return self.native.classify_error(error, phase, step)

    def close(self) -> None:
        self.dispatch_budget.receipt({"event": "close_started", "resource": "android_harness", "deviceRestored": False})
        try:
            self.native.close()
        except BaseException as exc:
            self.dispatch_budget.receipt({"event": "close_failed", "resource": "android_harness", "errorType": type(exc).__name__, "deviceRestored": False})
            raise
        self.dispatch_budget.receipt({"event": "close_succeeded", "resource": "android_harness", "deviceRestored": False})


def build_native_harness_factory(settings: Any, budget: NativeDispatchBudget) -> Callable[[str], Any]:
    """Match DefaultCodingAgentRuntime._build_harness default collaborators exactly."""
    from fsq_agent.ai_services import build_ai_assertion_evaluator
    from fsq_agent.core import ArtifactStore, HarnessFactory

    def factory(run_id: str) -> Any:
        budget.check_deadline()
        if not run_id or run_id in {".", ".."} or any(c in run_id for c in "/\\:\x00"):
            raise ValueError("Invalid native run ID")
        store = ArtifactStore(settings.output.runs_dir / run_id, secret_values=tuple(settings.runtime_secrets.private_values().values()))
        evaluator = build_ai_assertion_evaluator(settings)
        try:
            native = HarnessFactory().create_harness(platform=settings.harness.platform,
                harness_settings=settings.harness, artifact_store=store,
                ai_assertion_evaluator=evaluator, runtime_secret_settings=settings.runtime_secrets,
                app_id=settings.harness.android.app_id, serial=settings.harness.android.serial)
        except BaseException as exc:
            # Native factory owns construction-failure resource cleanup. It does
            # not expose per-resource close receipts, so do not invent them.
            budget.receipt({"event": "construction_failed", "errorType": type(exc).__name__,
                            "cleanupOwner": "native_harness_factory", "closeOutcome": "not_observable"})
            raise
        harness = BudgetedAndroidHarness(native, budget)
        try:
            for schema in harness.action_space():
                method = schema.driver_method
                if schema.metadata.get("executor_kind") == "driver" and method not in WRITE_CAPABILITIES and method not in READ_CAPABILITIES:
                    raise NativeBoundaryError("Unsupported native driver capability: " + method)
        except BaseException:
            try:
                harness.close()
            except BaseException:
                pass  # The close error is journaled; retain the primary failure.
            raise
        return harness
    return factory
