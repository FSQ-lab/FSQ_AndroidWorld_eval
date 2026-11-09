"""Revision 15 publishes the initialized task clock, never a live or host clock.

Only public TaskEval.device_time is serialized. ISO wall time and its UTC offset
stay together; relative-date/week semantics remain those of the exact task goal.
Frozen revisions 12–14 do not acquire this new provenance requirement.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


TASK_TIME_CONTEXT_PROTOCOL = {
    "version": 1,
    "source": "initialized_task.device_time",
    "clock": "initialization_reference_not_live",
}


def task_time_context(reference_time: datetime) -> dict[str, str]:
    offset = reference_time.utcoffset()
    if offset is None:
        raise ValueError("Initialized task reference time must be timezone-aware")
    return {
        "referenceTime": reference_time.isoformat(),
        "timezone": str(timezone(offset)),
    }


def task_time_provenance_valid(record: dict[str, Any], protocol: dict[str, Any]) -> bool:
    if protocol.get("harnessRevision") != 15:
        return True
    if not (
        protocol.get("taskTimeContext") == TASK_TIME_CONTEXT_PROTOCOL
        and record.get("protocol", {}).get("taskTimeContext") == TASK_TIME_CONTEXT_PROTOCOL
    ):
        return False
    if record.get("agent") is None and record.get("error") is not None:
        return True
    context = record.get("task", {}).get("timeContext")
    if not isinstance(context, dict) or not isinstance(context.get("referenceTime"), str):
        return False
    try:
        return task_time_context(datetime.fromisoformat(context["referenceTime"])) == context
    except (ValueError, TypeError, OverflowError):
        return False
