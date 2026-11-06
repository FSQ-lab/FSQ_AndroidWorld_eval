"""Frozen, task-independent wall-clock envelope for reference step budgets.

The business boundary closes mutation permits, not the MCP transport. The cleanup
window includes a complete 120-second MCP request plus 60 seconds for quit. Only
then may the supervisor terminate OMP; SIGKILL follows the termination grace.
"""

from __future__ import annotations

import math
from threading import Lock
from time import monotonic
from typing import Any

TIME_BUDGET_PROTOCOL = {
    "version": 1,
    "businessFormula": "max(600, 120 + 60 * maxSteps)",
    "startupSeconds": 120,
    "secondsPerStep": 60,
    "minimumBusinessSeconds": 600,
    "cleanupWindowSeconds": 180,
    "terminationGraceSeconds": 10,
    "episodeOverheadSeconds": 300,
    "mcpRequestTimeoutMs": 120_000,
    "cleanupPolicy": "agent_quit_required; harness_recovery_still_halts_campaign",
    "recoveryWindowSeconds": 120,
}


def episode_time_budget(max_steps: int) -> dict[str, int]:
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
        raise ValueError("max_steps must be a positive integer")
    business = max(600, 120 + 60 * max_steps)
    return {
        "businessSeconds": business,
        "cleanupWindowSeconds": 180,
        "terminationGraceSeconds": 10,
        "forceSeconds": business + 190,
        "recoveryWindowSeconds": 120,
        "episodeSeconds": business + 610,
    }


class EpisodeDeadlines:
    """One monotonic origin shared by supervisor, adapter, and HTTP gate."""

    def __init__(
        self, business_seconds: float, cleanup_seconds: float = 180,
        termination_grace_seconds: float = 10,
    ) -> None:
        values = (business_seconds, cleanup_seconds, termination_grace_seconds)
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError("Deadline intervals must be finite and positive")
        self._intervals = {
            "business": float(business_seconds),
            "cleanup": float(business_seconds + cleanup_seconds),
            "force": float(sum(values)),
        }
        self._lock = Lock()
        self._started: float | None = None
        self._cleanup_seconds = float(cleanup_seconds)
        self._termination_grace_seconds = float(termination_grace_seconds)

    def begin_cleanup(self) -> None:
        """Early completion/exhaustion gets a cleanup window, not unused work time."""
        with self._lock:
            if self._started is None:
                return
            elapsed = monotonic() - self._started
            self._intervals["cleanup"] = min(
                self._intervals["cleanup"], elapsed + self._cleanup_seconds,
            )
            self._intervals["force"] = min(
                self._intervals["force"],
                self._intervals["cleanup"] + self._termination_grace_seconds,
            )

    def start(self) -> None:
        with self._lock:
            if self._started is None:
                self._started = monotonic()

    def remaining(self, phase: str) -> float:
        with self._lock:
            if self._started is None:
                return self._intervals[phase]
            return max(0.0, self._started + self._intervals[phase] - monotonic())

    def expired(self, phase: str) -> bool:
        return self.remaining(phase) <= 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "started": self._started is not None,
            "remainingSeconds": {phase: self.remaining(phase) for phase in self._intervals},
        }
