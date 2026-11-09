"""Private diagnostics for the bounded business answer submission contract."""

import hashlib
import json
import math
from typing import Any


ANSWER_SUBMISSION_PROTOCOL: dict[str, Any] = {
    "version": 1,
    "identity": "bounded_business_submission.v1",
    "maximumFinalizationSeconds": 120,
    "deadline": "min(action_gate_closed + maximumFinalizationSeconds, business_deadline)",
    "taskOutcomeType": "string",
    "selection": "first_business_final",
    "cleanupCanSubmit": False,
}


def _reject_nonfinite(token: str) -> Any:
    raise ValueError(f"Non-JSON numeric token: {token}")


def _parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite JSON number: {token}")
    return value


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    return "object"


def parse_submission(raw_text: str | None) -> dict[str, Any]:
    """Return private diagnostics, retaining original input without coercion.

    ``parsedValue`` is the complete decoded envelope, including invalid field
    values. The report contains raw answer content and is not public metadata.
    Only an absent final submission (``None``) is ``no_submission``; an empty
    submitted string is malformed JSON.
    """
    report: dict[str, Any] = {
        "validContract": False,
        "reason": "no_submission",
        "rawText": raw_text,
        "parsedValue": None,
        "taskOutcomeType": None,
        "answer": None,
        "sha256": None,
    }
    if raw_text is None:
        return report
    try:
        value = json.loads(
            raw_text, parse_constant=_reject_nonfinite, parse_float=_parse_finite_float
        )
    except ValueError:
        report["reason"] = "invalid_json"
        return report
    report["parsedValue"] = value
    if not isinstance(value, dict):
        report["reason"] = "invalid_envelope"
        return report
    if "taskOutcome" not in value:
        report["reason"] = "missing_task_outcome"
        return report
    outcome = value["taskOutcome"]
    report["taskOutcomeType"] = _json_type(outcome)
    if not isinstance(outcome, str):
        report["reason"] = "invalid_task_outcome_type"
        return report
    answer = outcome.strip()
    if not answer:
        report["reason"] = "empty_task_outcome"
        return report
    report.update(
        validContract=True,
        reason="valid",
        answer=answer,
        sha256=hashlib.sha256(answer.encode("utf-8")).hexdigest(),
    )
    return report
