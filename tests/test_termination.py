"""Termination evidence is independent of a process's successful exit status."""

import json
from pathlib import Path

import pytest

from fsq_androidworld_eval.runner import _normalize_agent_events
from fsq_androidworld_eval.omp_supervisor import termination_reason
from fsq_androidworld_eval.lifecycle import episode_time_budget


def normalized(tmp_path: Path, events):
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    return _normalize_agent_events(path)


def assistant(reason="stop", text="answer", **extra):
    return {"type": "message_end", "message": {
        "role": "assistant", "stopReason": reason,
        "content": [{"type": "text", "text": text}] if text else [], **extra,
    }}


def test_zero_exit_no_final_is_unknown_not_agent_completion(tmp_path):
    result = normalized(tmp_path, [{"type": "agent_end", "isTerminal": True}])
    assert result["agentCompleted"] is False
    assert result["finalText"] is None
    assert termination_reason(result, business_expired=False, forced=False, budget_closure_reason=None) == "unknown_termination"


def test_explicit_internal_deadline_survives_zero_exit_and_no_final(tmp_path):
    result = normalized(tmp_path, [
        assistant("aborted", None, errorMessage="Deadline exceeded"),
        {"type": "agent_end", "isTerminal": True},
    ])
    assert result["agentCompleted"] is False
    assert termination_reason(result, business_expired=False, forced=False, budget_closure_reason=None) == "omp_deadline"


def test_intermediate_text_is_not_final_and_nonterminal_end_is_not_completion(tmp_path):
    result = normalized(tmp_path, [assistant("toolUse", "working"),
                                   {"type": "agent_end", "isTerminal": False}])
    assert result["finalText"] is None
    assert result["agentCompleted"] is False


def test_abort_cannot_reuse_previous_final_text(tmp_path):
    result = normalized(tmp_path, [assistant(), assistant("aborted", None),
                                   {"type": "agent_end", "isTerminal": True}])
    assert result["finalText"] is None
    assert result["agentCompleted"] is False


def test_explicit_final_completion_and_forced_termination_remain_distinct(tmp_path):
    result = normalized(tmp_path, [assistant(), {"type": "agent_end", "isTerminal": True}])
    assert result["agentCompleted"] is True
    assert termination_reason(result, business_expired=False, forced=False, budget_closure_reason=None) == "completed"
    assert termination_reason(result, business_expired=True, forced=False, budget_closure_reason=None) == "business_deadline"
    assert termination_reason(result, business_expired=True, forced=True, budget_closure_reason=None) == "forced_termination"


@pytest.mark.parametrize("steps", [1, 10, 30, 100])
def test_task_independent_budget_orders_business_cleanup_and_force(steps):
    budget = episode_time_budget(steps)
    business = budget["businessSeconds"]
    assert business >= 120 + 60 * steps
    cleanup = business + budget["cleanupWindowSeconds"]
    assert business < cleanup < budget["forceSeconds"] < budget["episodeSeconds"]
    assert budget["episodeSeconds"] >= budget["forceSeconds"] + budget["recoveryWindowSeconds"]


def test_early_cleanup_cannot_consume_unused_business_time(monkeypatch):
    import fsq_androidworld_eval.lifecycle as lifecycle
    now = [100.0]
    monkeypatch.setattr(lifecycle, "monotonic", lambda: now[0])
    deadlines = lifecycle.EpisodeDeadlines(600, 180, 10)
    deadlines.start()
    now[0] = 110.0
    deadlines.begin_cleanup()
    assert deadlines.remaining("cleanup") == 180
    assert deadlines.remaining("force") == 190
    now[0] = 120.0
    deadlines.begin_cleanup()
    assert deadlines.remaining("cleanup") == 170
    assert deadlines.remaining("force") == 180
    now[0] = 290.0
    assert deadlines.expired("cleanup")
    assert not deadlines.expired("force")


@pytest.mark.parametrize("change,expected", [
    ("none", "step_budget"), ("no_controlled_stop", "unknown_termination"),
    ("nonterminal", "unknown_termination"), ("aborted", "unknown_termination"),
    ("later_error", "unknown_termination"), ("forced", "forced_termination"),
    ("business_expired", "business_deadline"), ("completed", "completed"),
])
def test_controlled_step_stop_requires_terminal_settlement(tmp_path, change, expected):
    result = normalized(tmp_path, [assistant(text="incomplete"), {"type": "agent_end", "isTerminal": True}])
    result["agentCompleted"] = change == "completed"
    closure = None if change == "no_controlled_stop" else "step_budget"
    if change == "nonterminal":
        result["terminalEvents"][-1]["isTerminal"] = False
    elif change == "aborted":
        result["assistantStopReason"] = "aborted"
    elif change == "later_error":
        result["terminalEvents"].append({"type": "error"})

    assert termination_reason(
        result, business_expired=change == "business_expired", forced=change == "forced",
        budget_closure_reason=closure,
    ) == expected
