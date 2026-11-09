"""Behavioral coverage for private answer submission diagnostics."""

import hashlib
import json

import pytest

from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission


def test_protocol_is_json_native_and_describes_bounded_first_business_final():
    assert json.loads(json.dumps(ANSWER_SUBMISSION_PROTOCOL)) == ANSWER_SUBMISSION_PROTOCOL
    assert ANSWER_SUBMISSION_PROTOCOL == {
        "version": 1,
        "identity": "bounded_business_submission.v1",
        "maximumFinalizationSeconds": 120,
        "deadline": "min(action_gate_closed + maximumFinalizationSeconds, business_deadline)",
        "taskOutcomeType": "string",
        "selection": "first_business_final",
        "cleanupCanSubmit": False,
    }


@pytest.mark.parametrize("outcome,answer", [
    ("answer", "answer"),
    ("  answer\n\t", "answer"),
    ("\u2003café 世界\u2003", "café 世界"),
    ("0", "0"),
    ("false", "false"),
])
def test_accepts_only_trimmed_nonempty_strings(outcome, answer):
    raw = " \n" + json.dumps({"taskOutcome": outcome, "extra": [1, True]}) + "\t"
    result = parse_submission(raw)
    assert result == {
        "validContract": True,
        "reason": "valid",
        "rawText": raw,
        "parsedValue": {"taskOutcome": outcome, "extra": [1, True]},
        "taskOutcomeType": "string",
        "answer": answer,
        "sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
    }


def test_absent_submission_is_distinct_from_submitted_null_or_empty_text():
    result = parse_submission(None)
    assert result == {
        "validContract": False,
        "reason": "no_submission",
        "rawText": None,
        "parsedValue": None,
        "taskOutcomeType": None,
        "answer": None,
        "sha256": None,
    }
    assert parse_submission("null")["reason"] == "invalid_envelope"
    assert parse_submission("")["reason"] == "invalid_json"


@pytest.mark.parametrize("value,type_label", [
    (42, "number"),
    (4.25, "number"),
    ({"answer": "kept as an object"}, "object"),
    (["answer"], "array"),
    (True, "boolean"),
    (False, "boolean"),
    (None, "null"),
])
def test_rejects_nonstring_outcomes_without_coercion(value, type_label):
    raw = json.dumps({"taskOutcome": value})
    result = parse_submission(raw)
    assert result["reason"] == "invalid_task_outcome_type"
    assert result["validContract"] is False
    assert result["taskOutcomeType"] == type_label
    assert result["parsedValue"] == {"taskOutcome": value}
    assert type(result["parsedValue"]["taskOutcome"]) is type(value)
    assert result["rawText"] == raw
    assert result["answer"] is None
    assert result["sha256"] is None


@pytest.mark.parametrize("raw", [
    "", " \n\t", "not JSON", '{"taskOutcome":',
    '{"taskOutcome": "answer",}',
    '{"taskOutcome": "answer"} trailing',
    '{"taskOutcome": NaN}', '{"taskOutcome": Infinity}',
    '{"taskOutcome": -Infinity}',
    '{"taskOutcome": "answer", "extra": [NaN]}',
    "NaN", "Infinity", "-Infinity",
    "1e309", "-1e309", '{"taskOutcome": 1e309}',
    '{"taskOutcome": "answer", "extra": [{"value": -1e309}]}',
])
def test_malformed_and_nonfinite_tokens_are_invalid_json(raw):
    result = parse_submission(raw)
    assert result["reason"] == "invalid_json"
    assert result["validContract"] is False
    assert result["rawText"] == raw
    assert result["parsedValue"] is None
    assert result["taskOutcomeType"] is None
    assert result["answer"] is None
    assert result["sha256"] is None


@pytest.mark.parametrize("value", [None, True, False, 42, 4.25, "answer", [], [{"taskOutcome": "answer"}]])
def test_nonobject_envelopes_remain_original_json_values(value):
    raw = json.dumps(value)
    result = parse_submission(raw)
    assert result["reason"] == "invalid_envelope"
    assert result["validContract"] is False
    assert result["parsedValue"] == value
    assert type(result["parsedValue"]) is type(value)
    assert result["rawText"] == raw
    assert result["taskOutcomeType"] is None
    assert result["answer"] is None
    assert result["sha256"] is None


@pytest.mark.parametrize("value", [{}, {"answer": "not the contracted field"}, {"taskoutcome": "wrong case"}])
def test_missing_field_does_not_fall_back_to_other_keys(value):
    raw = json.dumps(value)
    result = parse_submission(raw)
    assert result["reason"] == "missing_task_outcome"
    assert result["validContract"] is False
    assert result["parsedValue"] == value
    assert result["rawText"] == raw
    assert result["taskOutcomeType"] is None
    assert result["answer"] is None
    assert result["sha256"] is None


@pytest.mark.parametrize("outcome", ["", " ", "\t\r\n", "\u2003\u00a0"])
def test_empty_or_whitespace_strings_are_not_answers(outcome):
    raw = json.dumps({"taskOutcome": outcome})
    result = parse_submission(raw)
    assert result["reason"] == "empty_task_outcome"
    assert result["validContract"] is False
    assert result["parsedValue"] == {"taskOutcome": outcome}
    assert result["rawText"] == raw
    assert result["taskOutcomeType"] == "string"
    assert result["answer"] is None
    assert result["sha256"] is None
