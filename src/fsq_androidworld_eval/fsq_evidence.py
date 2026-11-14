"""Offline native evidence validation; imports no FSQ, Android or model SDK.

Dispatch replay proves the producer's before-forward accounting, not device
restoration or official reward. Kill is an observation, never an admission gate.
"""
from __future__ import annotations

import hashlib
import json
import math
import stat
from pathlib import Path
from typing import Any

from .fsq_native import WRITE_ALIASES, WRITE_CAPABILITIES

ANSWER_SOURCE = "agent_runtime.runner.tool_output.summary"
UNIT = "admitted_android_harness_write_capability_dispatch"
VERIFICATION_STATUSES = ("success", "failed", "inconclusive")
TASK_STATUSES = VERIFICATION_STATUSES + ("cancelled", "error")
COUNTERS = ("attempted", "admitted", "succeeded", "failed", "denied", "inFlight")
EVENT_FIELDS = {
    "attempted": {"ticket", "capability", "phase", "stepId", "countedWrite"},
    "succeeded": {"ticket", "capability", "phase", "countedWrite", "errorType"},
    "failed": {"ticket", "capability", "phase", "countedWrite", "errorType"},
    "denied": {"capability", "phase", "stepId", "reason", "countedWrite"},
    "close_started": {"resource", "deviceRestored"},
    "close_succeeded": {"resource", "deviceRestored"},
    "close_failed": {"resource", "deviceRestored", "errorType"},
    "construction_failed": {"errorType", "cleanupOwner", "closeOutcome"},
    "native_execution_returned": {"taskId", "nativeTaskId", "taskStatus", "verificationObserved", "verificationStatus"},
}


class EvidenceError(ValueError):
    """Native evidence is incomplete, unsafe to read, or contradictory."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _finite(value: Any) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError) as error:
        raise EvidenceError("Evidence is not finite JSON") from error


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON object key")
        result[key] = value
    return result


def _load_json(data: str | bytes) -> Any:
    def reject_constant(value: str) -> Any:
        raise EvidenceError("Nonfinite JSON constant: " + value)
    try:
        return json.loads(data, object_pairs_hook=_unique_object, parse_constant=reject_constant)
    except (ValueError, UnicodeError) as error:
        raise EvidenceError("Invalid native JSON artifact") from error


def _artifact(reference: Any, root: Path) -> bytes:
    _require(isinstance(reference, dict), "Missing native artifact reference")
    name = reference.get("path")
    _require(isinstance(name, str) and bool(name) and "\x00" not in name, "Invalid native artifact path")
    path = Path(name)
    _require(name == str(path) and ".." not in path.parts, "Noncanonical native artifact path")
    candidate = path if path.is_absolute() else root / path
    try:
        resolved = candidate.resolve(strict=True)
        _require(candidate == resolved, "Native artifact path is an alias or symlink")
        _require(root in resolved.parents, "Native artifact escapes episode root")
        _require(stat.S_ISREG(resolved.stat().st_mode), "Native artifact is not a regular file")
        data = resolved.read_bytes()
    except (OSError, RuntimeError) as error:
        raise EvidenceError("Native artifact cannot be read") from error
    _require(type(reference.get("sizeBytes")) is int and reference["sizeBytes"] == len(data), "Native artifact size mismatch")
    _require(reference.get("sha256") == hashlib.sha256(data).hexdigest(), "Native artifact hash mismatch")
    _require(reference.get("visibility") == "evaluator_private", "Native artifact visibility mismatch")
    return data


def replay_dispatch_audit(snapshot: dict, events: list, *, maximum: int) -> dict:
    """Replay a terminal NativeDispatchBudget journal, including read tickets.

    Admissions consume the budget forever, including failures. Denials have no
    ticket and consume no admission. The clock may advance between the dispatch
    check and emission; emission timestamps are not admission-check timestamps.
    """
    _require(type(maximum) is int and maximum > 0, "Invalid expected maximum")
    _require(isinstance(snapshot, dict) and isinstance(events, list), "Invalid dispatch audit")
    _require(snapshot.get("unit") == UNIT, "Wrong dispatch accounting unit")
    _require(type(snapshot.get("maximum")) is int and snapshot["maximum"] == maximum, "Dispatch maximum mismatch")
    _require(snapshot.get("writeCapabilities") == list(WRITE_CAPABILITIES), "Dispatch capability inventory mismatch")
    _require(_finite(snapshot.get("deadlineMonotonic")), "Invalid dispatch deadline")
    _require(type(snapshot.get("deadlineExceeded")) is bool, "Invalid dispatch deadline flag")
    _require(_canonical(snapshot.get("events")) == _canonical(events), "Embedded and journal dispatch events differ")
    totals = {key: 0 for key in COUNTERS}
    pending: dict[int, dict] = {}
    next_ticket = 1
    last_time = -math.inf
    close_pending = 0
    close_receipts = []
    kills = []
    kill_by_ticket = {}
    returned = None
    saw_deadline = False
    for sequence, event in enumerate(events, 1):
        _require(isinstance(event, dict), "Dispatch event is not an object")
        _require(type(event.get("sequence")) is int and event["sequence"] == sequence, "Noncontiguous dispatch sequence")
        timestamp = event.get("monotonic")
        _require(_finite(timestamp) and timestamp >= last_time, "Nonfinite or nonmonotonic dispatch timestamp")
        last_time = timestamp
        kind = event.get("event")
        _require(isinstance(kind, str), "Invalid native audit event name")
        _require(kind in EVENT_FIELDS, "Unknown native audit event")
        _require(set(event) == EVENT_FIELDS[kind] | {"event", "sequence", "monotonic"}, "Native audit event fields mismatch")
        _require(returned is None, "Event occurs after full native execution returned")
        if kind in {"attempted", "succeeded", "failed", "denied"}:
            capability = event.get("capability")
            # Native swipe has the same spelling as its canonical capability.
            _require(isinstance(capability, str) and bool(capability)
                     and WRITE_ALIASES.get(capability, capability) == capability, "Noncanonical dispatch capability")
            write = capability in WRITE_CAPABILITIES
            _require(type(event.get("countedWrite")) is bool and event["countedWrite"] is write, "Mislabeled counted write")
            _require(isinstance(event.get("phase"), str) and bool(event["phase"]), "Invalid dispatch phase")
            if kind in {"attempted", "denied"}:
                _require(event.get("stepId") is None or isinstance(event.get("stepId"), str), "Invalid dispatch step ID")
                if write:
                    totals["attempted"] += 1
            if kind == "denied":
                _require("ticket" not in event, "Denied dispatch has a ticket")
                reason = event.get("reason")
                _require(isinstance(reason, str) and reason in {"deadline", "unsupported_batch", "action_budget"}, "Invalid dispatch denial")
                if reason == "deadline":
                    saw_deadline = True
                    _require(timestamp >= snapshot["deadlineMonotonic"], "Premature deadline denial")
                elif reason == "unsupported_batch":
                    _require(capability in {"perform_actions", "performActions"}, "Mislabeled unsupported batch")
                else:
                    _require(write and totals["admitted"] >= maximum, "Premature or nonwrite action-budget denial")
                if write:
                    totals["denied"] += 1
                if capability == "kill_app":
                    kills.append({"outcome": "denied", "reason": reason, "attemptSequence": sequence,
                                  "outcomeSequence": sequence, "monotonic": timestamp, "phase": event["phase"]})
                continue
            ticket = event.get("ticket")
            _require(type(ticket) is int and ticket > 0, "Invalid dispatch ticket")
            if kind == "attempted":
                _require(ticket == next_ticket, "Duplicate or noncontiguous dispatch ticket")
                _require(capability not in {"perform_actions", "performActions"}, "Unsupported batch was admitted")
                _require("reason" not in event, "Admitted dispatch has denial reason")
                next_ticket += 1
                pending[ticket] = event
                if write:
                    _require(totals["admitted"] < maximum, "Dispatch admissions exceed maximum")
                    totals["admitted"] += 1
                if capability == "kill_app":
                    observation = {"ticket": ticket, "outcome": "pending", "attemptSequence": sequence,
                                   "outcomeSequence": None, "monotonic": timestamp, "phase": event["phase"]}
                    kills.append(observation)
                    kill_by_ticket[ticket] = observation
            else:
                start = pending.pop(ticket, None)
                _require(start is not None, "Duplicate or unmatched dispatch completion")
                _require(all(event.get(key) == start.get(key) for key in ("capability", "phase", "countedWrite")), "Completion does not match admission")
                _require("reason" not in event, "Completion has denial reason")
                error_type = event.get("errorType")
                _require(error_type is None or isinstance(error_type, str), "Invalid dispatch error type")
                _require(kind != "succeeded" or error_type is None, "Successful dispatch claims an exception")
                if write:
                    totals[kind] += 1
                if capability == "kill_app":
                    kill_by_ticket[ticket].update(outcome=kind, outcomeSequence=sequence,
                                                  outcomeMonotonic=timestamp, errorType=error_type)
        elif kind in {"close_started", "close_succeeded", "close_failed"}:
            _require(event.get("resource") == "android_harness" and event.get("deviceRestored") is False, "Invalid Harness close receipt")
            if kind == "close_started":
                close_pending += 1
            else:
                _require(close_pending > 0, "Unmatched Harness close completion")
                close_pending -= 1
                if kind == "close_failed":
                    _require(isinstance(event.get("errorType"), str), "Missing Harness close failure type")
            close_receipts.append(dict(event))
        elif kind == "construction_failed":
            _require(isinstance(event.get("errorType"), str) and event.get("cleanupOwner") == "native_harness_factory"
                     and event.get("closeOutcome") == "not_observable", "Invalid native construction receipt")
        elif kind == "native_execution_returned":
            _require(not pending and close_pending == 0, "Native return precedes dispatch or close settlement")
            _require(isinstance(event.get("taskId"), str) and isinstance(event.get("nativeTaskId"), str), "Missing native return identity")
            _require(event.get("taskStatus") in TASK_STATUSES and event.get("verificationObserved") is True
                     and event.get("verificationStatus") in VERIFICATION_STATUSES, "Native return lacks observable verification")
            returned = dict(event)
        else:
            raise EvidenceError("Unknown native audit event")
    totals["inFlight"] = sum(event["countedWrite"] for event in pending.values())
    for key, value in totals.items():
        _require(type(snapshot.get(key)) is int and snapshot[key] == value, "Dispatch counter mismatch: " + key)
    _require(not pending and close_pending == 0, "Terminal dispatch audit has outstanding tickets or closes")
    _require(not saw_deadline or snapshot["deadlineExceeded"], "Deadline denial contradicts snapshot")
    _require(type(snapshot.get("exhausted")) is bool and snapshot["exhausted"] == (totals["admitted"] >= maximum), "Dispatch exhausted flag mismatch")
    outcomes = {item["outcome"] for item in kills}
    kill_evidence = {"observed": bool(kills), "status": "absent" if not kills else next(iter(outcomes)) if len(outcomes) == 1 else "mixed",
                     "attempted": len(kills), "admitted": sum(item["outcome"] != "denied" for item in kills),
                     "succeeded": sum(item["outcome"] == "succeeded" for item in kills),
                     "failed": sum(item["outcome"] == "failed" for item in kills),
                     "denied": sum(item["outcome"] == "denied" for item in kills), "events": kills,
                     "relativeToNativeExecutionReturned": "absent" if not kills else "before" if returned else "unknown",
                     "nativeExecutionReturnedSequence": returned["sequence"] if returned else None,
                     "relativeToMainFinal": "unknown", "mainFinalBoundary": "not_observed"}
    return {"unit": UNIT, "maximum": maximum, **totals, "outstandingTickets": [],
            "deadlineExceeded": snapshot["deadlineExceeded"], "exhausted": snapshot["exhausted"],
            "eventCount": len(events), "nativeExecutionReturned": returned,
            "closeReceipts": close_receipts, "killEvidence": kill_evidence}


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _valid_final_output(output: dict) -> bool:
    allowed = {"schema_version", "status", "summary", "pre_plan", "plan_updates", "satisfied_criteria", "unmet_criteria", "evidence", "errors"}
    if (set(output) - allowed or output.get("schema_version") != "task_run_v1"
            or output.get("status") not in VERIFICATION_STATUSES or not isinstance(output.get("summary"), str)):
        return False
    for key in ("plan_updates", "satisfied_criteria", "unmet_criteria", "evidence", "errors"):
        if key in output and not _string_list(output[key]):
            return False
    plan = output.get("pre_plan", [])
    if not isinstance(plan, list):
        return False
    for item in plan:
        if (not isinstance(item, dict) or set(item) - {"step_id", "action", "success_criteria", "status"}
                or type(item.get("step_id")) is not int or item["step_id"] < 1
                or not isinstance(item.get("action"), str) or item.get("status") not in ("success", "failed", "skipped", "adjusted")
                or not _string_list(item.get("success_criteria", []))):
            return False
    return True


def _main_answer(task: dict) -> dict:
    def reject(status: str, reason: str) -> dict:
        return {"status": status, "source": ANSWER_SOURCE, "reason": reason}
    steps = task.get("steps")
    _require(isinstance(steps, list), "Native TaskResult.steps is not a list")
    runners = [step for step in steps if isinstance(step, dict) and step.get("tool_name") == "agent_runtime.runner"]
    if not runners:
        return reject("missing", "No exact main runner step")
    if len(runners) != 1:
        return reject("ambiguous", "Multiple exact main runner steps")
    runner = runners[0]
    if runner.get("status") != "success":
        return reject("failed", "Main runner did not succeed")
    output = runner.get("tool_output")
    if not isinstance(output, dict) or not _valid_final_output(output):
        return reject("invalid", "Main runner output is not a validated task_run_v1 object")
    return {"status": "valid", "source": ANSWER_SOURCE, "summary": output["summary"], "businessStatus": output["status"]}


def validate_native_evidence(outcome: dict, *, episode_root: Path, expected_task_id: str,
                             expected_serial: str, maximum: int) -> dict:
    """Validate the supervisor result before or after artifact archival.

    ``episode_root`` is the original owned root before archival, or the canonical
    episode output directory afterwards. Process cleanup/exit is independent:
    callers must enforce the trusted supervisor receipt before invoking oracle.
    A complete native result can have a nonvalid answer or failed business status.
    """
    _require(isinstance(outcome, dict) and isinstance(outcome.get("result"), dict), "Missing native worker result")
    result = outcome["result"]
    _require(type(result.get("schemaVersion")) is int and result["schemaVersion"] == 1, "Invalid native outcome schema")
    _require(isinstance(expected_task_id, str) and bool(expected_task_id) and result.get("taskId") == expected_task_id, "Native outcome task identity mismatch")
    target = result.get("nativeTarget")
    _require(isinstance(expected_serial, str) and bool(expected_serial) and isinstance(target, dict)
             and target.get("serial") == expected_serial, "Native serial identity mismatch")
    fsq = result.get("fsq")
    _require(isinstance(fsq, dict) and fsq.get("completeDynamicExecutionReturned") is True, "Complete native execution is unproven")
    try:
        root = Path(episode_root).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise EvidenceError("Episode evidence root is unavailable") from error
    task = _load_json(_artifact(fsq.get("taskResult"), root))
    verification = _load_json(_artifact(fsq.get("verification"), root))
    _require(isinstance(task, dict) and task.get("task_id") == expected_task_id, "Native TaskResult task identity mismatch")
    _require(task.get("status") in TASK_STATUSES and fsq.get("status") == task["status"], "Native TaskResult status mismatch")
    _require(isinstance(verification, dict) and verification.get("status") in VERIFICATION_STATUSES
             and isinstance(verification.get("summary"), str), "Invalid native internal verification")
    _require(not set(verification) - {"status", "summary", "satisfied_criteria", "unmet_criteria", "diagnostics"}
             and all(_string_list(verification[key]) for key in ("satisfied_criteria", "unmet_criteria", "diagnostics") if key in verification), "Invalid native verification fields")
    _require(_canonical(task.get("verification")) == _canonical(verification), "Internal verification artifact differs from TaskResult")
    answer = _main_answer(task)
    selected = result.get("mainAnswer")
    _require(isinstance(selected, dict) and selected.get("status") == answer["status"]
             and selected.get("source") == ANSWER_SOURCE, "Selected main answer source/status mismatch")
    if answer["status"] == "valid":
        _require(selected.get("summary") == answer["summary"] and selected.get("businessStatus") == answer["businessStatus"], "Selected summary/business status differs from native runner")
    else:
        _require("summary" not in selected and "businessStatus" not in selected, "Nonvalid answer contains an invented fallback")
    budget = result.get("actionBudget")
    _require(isinstance(budget, dict) and isinstance(budget.get("events"), list), "Missing native dispatch snapshot")
    events = budget["events"]
    if result.get("actionAudit") is not None:
        journal = _artifact(result["actionAudit"], root)
        events = [_load_json(line) for line in journal.splitlines()]
    else:
        _require(not events, "Native dispatch journal is missing")
    audit = replay_dispatch_audit(budget, events, maximum=maximum)
    returned = audit["nativeExecutionReturned"]
    _require(isinstance(returned, dict), "Observed full native return boundary is missing")
    _require(returned["taskId"] == returned["nativeTaskId"] == expected_task_id
             and returned["taskStatus"] == task["status"] and returned["verificationStatus"] == verification["status"], "Native return boundary contradicts TaskResult identity/verification")
    cleanup = result.get("cleanup")
    _require(isinstance(cleanup, dict) and _canonical(cleanup.get("closeReceipts")) == _canonical(audit["closeReceipts"]), "Harness close receipts differ from dispatch journal")
    return {"answer": answer, "killEvidence": audit["killEvidence"], "internalVerification": verification, "audit": audit}
