from datetime import datetime, timedelta, timezone

import pytest

from fsq_androidworld_eval.task_time import (
    TASK_TIME_CONTEXT_PROTOCOL,
    task_time_context,
    task_time_provenance_valid,
)


def test_reference_clock_preserves_local_week_boundary_and_utc_offset():
    reference = datetime(2024, 1, 1, 0, 5, tzinfo=timezone(timedelta(hours=14)))

    context = task_time_context(reference)
    observed = datetime.fromisoformat(context["referenceTime"])

    assert observed.weekday() == 0
    assert observed.astimezone(timezone.utc).weekday() == 6
    assert observed.hour == 0
    assert observed.utcoffset() == timedelta(hours=14)
    assert context["timezone"] == "UTC+14:00"


def test_naive_task_clock_cannot_supply_a_relative_date_anchor():
    with pytest.raises(ValueError, match="timezone-aware"):
        task_time_context(datetime(2023, 10, 15, 15, 34))


@pytest.mark.parametrize("revision", [12, 13, 14])
def test_frozen_records_do_not_gain_a_task_clock_requirement(revision):
    assert task_time_provenance_valid({}, {"harnessRevision": revision}) is True


@pytest.mark.parametrize("context", [
    None,
    {},
    {"referenceTime": "2023-10-15T15:34:00", "timezone": "UTC"},
    {"referenceTime": "not a date", "timezone": "UTC"},
    {"referenceTime": "2023-10-15T15:34:00+00:00", "timezone": "UTC+01:00"},
    {"referenceTime": "2023-10-15T15:34:00+00:00", "timezone": "UTC", "liveClock": True},
])
def test_new_provenance_rejects_missing_or_contradictory_reference_clock(context):
    protocol = {"harnessRevision": 15, "taskTimeContext": TASK_TIME_CONTEXT_PROTOCOL}
    record = {"protocol": protocol, "agent": {}, "task": {"timeContext": context}}

    assert task_time_provenance_valid(record, protocol) is False


def test_pre_agent_failure_preserves_absent_reference_instead_of_inventing_time():
    protocol = {"harnessRevision": 15, "taskTimeContext": TASK_TIME_CONTEXT_PROTOCOL}
    record = {"protocol": protocol, "agent": None, "error": {"type": "InitializationFailed"}}

    assert task_time_provenance_valid(record, protocol) is True
    record["agent"] = {}
    assert task_time_provenance_valid(record, protocol) is False
