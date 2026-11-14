import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from fsq_androidworld_eval.fsq_evidence import EvidenceError, replay_dispatch_audit, validate_native_evidence
from fsq_androidworld_eval.fsq_native import (
    BudgetedAndroidHarness, NativeActionBudgetExceeded, NativeBoundaryError,
    NativeDeadlineExceeded, NativeDispatchBudget,
)


TASK_ID = "campaign-calibrate-003"
SERIAL = "emulator-5560"


def reference(path, payload):
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode()
    path.write_bytes(data)
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(data).hexdigest(),
            "sizeBytes": len(data), "visibility": "evaluator_private"}


def journal_reference(path):
    data = path.read_bytes()
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(data).hexdigest(),
            "sizeBytes": len(data), "visibility": "evaluator_private"}


def final_output(summary, status):
    return {"schema_version": "task_run_v1", "status": status, "summary": summary,
            "pre_plan": [], "plan_updates": [], "satisfied_criteria": [],
            "unmet_criteria": [], "evidence": [], "errors": []}


def native_step(output, *, status="success", tool="agent_runtime.runner", step_id=1):
    return {"step_id": step_id, "status": status, "actual_outcome": "Native runtime returned",
            "screenshot_path": None, "ui_tree_snapshot": None, "duration_ms": 1,
            "error": None, "tool_name": tool, "tool_output": output}


def return_receipt(budget, *, task_status="success", verification_status="success"):
    budget.receipt({"event": "native_execution_returned", "taskId": TASK_ID,
                    "nativeTaskId": TASK_ID, "taskStatus": task_status,
                    "verificationObserved": True, "verificationStatus": verification_status})


def episode(tmp_path, *, summary="exact parsed summary", business_status="success", kill="absent", runner_mode="valid"):
    """Real budget dispatches plus native model_dump-shaped artifacts, no SDK."""
    journal = tmp_path / "native-action-audit.jsonl"
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1, journal=journal)
    calls = []
    def forward(action, *, status="passed"):
        calls.append(action)
        return NS(status=status)
    if kill == "denied":
        budget.dispatch("tap_at", "action", lambda: forward("tap_at"))
        with pytest.raises(NativeActionBudgetExceeded):
            budget.dispatch("killApp", "teardown", lambda: forward("kill_app"))
    elif kill in {"succeeded", "failed"}:
        budget.dispatch("killApp", "teardown", lambda: forward("kill_app", status="passed" if kill == "succeeded" else "failed"))
    output = final_output(summary, business_status)
    steps = [native_step(output)]
    answer = {"status": "valid", "summary": summary, "businessStatus": business_status,
              "source": "agent_runtime.runner.tool_output.summary"}
    if runner_mode == "missing":
        steps = [native_step(output, tool="agent_runtime.verifier")]
    elif runner_mode == "failed":
        steps = [native_step({"failure_reason": "No final output"}, status="failed")]
    elif runner_mode == "ambiguous":
        steps.append(native_step(output, step_id=2))
    elif runner_mode == "invalid":
        steps[0]["tool_output"]["summary"] = 42
    if runner_mode != "valid":
        answer = {"status": runner_mode, "source": "agent_runtime.runner.tool_output.summary", "reason": "Explicit native outcome"}
    verification = {"status": business_status, "summary": "Native internal verification, not official reward",
                    "satisfied_criteria": [], "unmet_criteria": [], "diagnostics": []}
    task = {"task_id": TASK_ID, "status": business_status, "steps": steps,
            "verification": verification,
            "report": {"run_id": "native-run", "path": str(tmp_path / "execution-result.json"),
                       "format": "json", "evidence_manifest_path": None, "evidence_bundle_path": None,
                       "generated_at": "2026-11-10T00:00:00Z"}, "duration_ms": 5}
    return_receipt(budget, task_status=business_status, verification_status=business_status)
    result = {"schemaVersion": 1, "status": "completed", "taskId": TASK_ID,
              "nativeTarget": {"serial": SERIAL, "effectiveProvider": "github_copilot", "effectiveModel": "gpt-6.1-sol"},
              "mainAnswer": answer, "fsq": {"taskResult": reference(tmp_path / "task.json", task),
              "verification": reference(tmp_path / "verification.json", verification), "status": business_status,
              "completeDynamicExecutionReturned": True}, "actionBudget": budget.snapshot(),
              "actionAudit": journal_reference(journal), "cleanup": {"closeReceipts": []}}
    return {"process": {"terminated": False}, "result": result}, task, calls


def validate(outcome, root):
    return validate_native_evidence(outcome, episode_root=root, expected_task_id=TASK_ID, expected_serial=SERIAL, maximum=1)


def replace_task(outcome, task, tmp_path):
    outcome["result"]["fsq"]["taskResult"] = reference(tmp_path / "task.json", task)


def rewrite_journal(outcome):
    result = outcome["result"]
    path = Path(result["actionAudit"]["path"])
    path.write_text("".join(json.dumps(event, sort_keys=True, allow_nan=True) + "\n" for event in result["actionBudget"]["events"]))
    result["actionAudit"] = journal_reference(path)


@pytest.mark.parametrize("summary", ["", "  \n\t", "中文 🧭\n exact  "])
@pytest.mark.parametrize("status", ["success", "failed", "inconclusive"])
def test_exact_summary_and_business_failure_are_preserved(tmp_path, summary, status):
    outcome, task, calls = episode(tmp_path, summary=summary, business_status=status)
    evidence = validate(outcome, tmp_path)
    assert evidence["answer"]["summary"] == summary
    assert evidence["answer"]["businessStatus"] == status
    assert evidence["internalVerification"] == task["verification"]
    assert evidence["audit"]["admitted"] == 0
    assert calls == []


@pytest.mark.parametrize("kill,expected_calls", [("absent", []), ("failed", ["kill_app"]),
                                                   ("denied", ["tap_at"]), ("succeeded", ["kill_app"])])
def test_kill_outcomes_are_observations_not_admission_rules(tmp_path, kill, expected_calls):
    outcome, _, calls = episode(tmp_path, kill=kill)
    evidence = validate(outcome, tmp_path)
    observed = evidence["killEvidence"]
    assert observed["status"] == kill
    assert observed["relativeToMainFinal"] == "unknown"
    assert observed["relativeToNativeExecutionReturned"] == ("absent" if kill == "absent" else "before")
    assert observed["nativeExecutionReturnedSequence"] == len(outcome["result"]["actionBudget"]["events"])
    assert observed["attempted"] == int(kill != "absent")
    assert observed["admitted"] == int(kill in {"failed", "succeeded"})
    assert calls == expected_calls  # Validation must not execute a supplemental operation.


@pytest.mark.parametrize("mode", ["missing", "failed", "ambiguous", "invalid"])
def test_complete_native_return_preserves_explicit_nonvalid_answer(tmp_path, mode):
    outcome, _, _ = episode(tmp_path, runner_mode=mode)
    evidence = validate(outcome, tmp_path)
    assert evidence["answer"]["status"] == mode
    assert "summary" not in evidence["answer"]
    outcome["result"]["mainAnswer"].update(summary="invented verifier fallback")
    with pytest.raises(EvidenceError, match="fallback"):
        validate(outcome, tmp_path)


@pytest.mark.parametrize("field,value", [("summary", "different exact answer"), ("summary", " exact parsed summary"),
                                         ("businessStatus", "failed"), ("source", "agent_runtime.verifier")])
def test_rehashed_consumer_answer_contradictions_are_rejected(tmp_path, field, value):
    outcome, _, _ = episode(tmp_path)
    outcome["result"]["mainAnswer"][field] = value
    with pytest.raises(EvidenceError):
        validate(outcome, tmp_path)


@pytest.mark.parametrize("location", ["outcome", "task", "serial", "lifecycle"])
def test_rehashed_wrong_native_identity_is_rejected(tmp_path, location):
    outcome, task, _ = episode(tmp_path)
    if location == "outcome":
        outcome["result"]["taskId"] = "other-campaign-smoke-099"
    elif location == "task":
        task["task_id"] = "other-campaign-smoke-099"
        replace_task(outcome, task, tmp_path)
    elif location == "serial":
        outcome["result"]["nativeTarget"]["serial"] = "emulator-9998"
    else:
        outcome["result"]["actionBudget"]["events"][-1]["nativeTaskId"] = "other-campaign-smoke-099"
        rewrite_journal(outcome)
    with pytest.raises(EvidenceError, match="identity|serial"):
        validate(outcome, tmp_path)


def test_separately_rehashed_verification_cannot_override_native_result(tmp_path):
    outcome, _, _ = episode(tmp_path)
    outcome["result"]["fsq"]["verification"] = reference(tmp_path / "verification.json", {"status": "failed", "summary": "forged verification"})
    with pytest.raises(EvidenceError, match="differs from TaskResult"):
        validate(outcome, tmp_path)


def test_process_forcing_does_not_erase_complete_native_evidence(tmp_path):
    outcome, _, _ = episode(tmp_path)
    outcome["process"].update(terminated=True, killed=True, groupCleanup="unknown")
    outcome["result"]["status"] = "deadline"
    assert validate(outcome, tmp_path)["answer"]["status"] == "valid"


@pytest.mark.parametrize("change", ["missing", "wrong_state", "unobserved", "fake_main_final"])
def test_full_return_requires_real_known_lifecycle_receipt(tmp_path, change):
    outcome, _, _ = episode(tmp_path)
    events = outcome["result"]["actionBudget"]["events"]
    if change == "missing":
        events.pop()
    elif change == "wrong_state":
        events[-1]["verificationStatus"] = "failed"
    elif change == "unobserved":
        events[-1]["verificationObserved"] = False
    else:
        events[-1]["event"] = "native_main_final_without_kill"
    rewrite_journal(outcome)
    with pytest.raises(EvidenceError):
        validate(outcome, tmp_path)


@pytest.mark.parametrize("attack", ["hash", "size", "outside", "symlink", "directory", "traversal"])
def test_canonical_artifact_identity_is_enforced(tmp_path, attack):
    root = tmp_path / "episode"
    root.mkdir()
    outcome, task, _ = episode(root)
    ref = outcome["result"]["fsq"]["taskResult"]
    if attack == "hash":
        ref["sha256"] = "0" * 64
    elif attack == "size":
        ref["sizeBytes"] += 1
    elif attack == "outside":
        outcome["result"]["fsq"]["taskResult"] = reference(tmp_path / "outside.json", task)
    elif attack == "symlink":
        link = root / "link.json"
        link.symlink_to(root / "task.json")
        ref["path"] = str(link)
    elif attack == "directory":
        ref["path"] = str(root)
    else:
        ref["path"] = str(root / "unused" / ".." / "task.json")
    with pytest.raises(EvidenceError):
        validate(outcome, root)


def test_archived_references_are_valid_only_under_new_episode_root(tmp_path):
    import shutil
    original = tmp_path / "owned"
    original.mkdir()
    outcome, _, _ = episode(original)
    archived = tmp_path / "episode"
    shutil.copytree(original, archived)
    for ref in (outcome["result"]["fsq"]["taskResult"], outcome["result"]["fsq"]["verification"], outcome["result"]["actionAudit"]):
        ref["path"] = str(archived / Path(ref["path"]).relative_to(original))
    assert validate(outcome, archived)["answer"]["status"] == "valid"
    with pytest.raises(EvidenceError, match="escapes"):
        validate(outcome, original)


def test_journal_equality_is_not_substituted_for_semantic_replay(tmp_path):
    outcome, _, _ = episode(tmp_path, kill="succeeded")
    outcome["result"]["actionBudget"]["events"][0]["countedWrite"] = False
    rewrite_journal(outcome)
    with pytest.raises(EvidenceError, match="Mislabeled"):
        validate(outcome, tmp_path)


def test_hash_valid_but_different_embedded_and_journal_events_are_rejected(tmp_path):
    outcome, _, _ = episode(tmp_path, kill="succeeded")
    outcome["result"]["actionBudget"]["events"][0]["phase"] = "forged"
    with pytest.raises(EvidenceError, match="Embedded and journal"):
        validate(outcome, tmp_path)


def successful_budget(maximum=3):
    budget = NativeDispatchBudget(maximum, 100, clock=lambda: 1)
    budget.dispatch("tapAt", "action", lambda: NS(status="passed"), step_id="real-ticket")
    return budget


def replay(budget):
    snapshot = budget.snapshot()
    return replay_dispatch_audit(snapshot, snapshot["events"], maximum=budget.maximum)


def test_eleven_real_admissions_cannot_be_hidden_by_zero_counters():
    budget = NativeDispatchBudget(11, 100, clock=lambda: 1)
    for _ in range(11):
        budget.dispatch("tap_at", "action", lambda: NS(status="passed"))
    snapshot = budget.snapshot()
    snapshot.update(maximum=10, attempted=0, admitted=0, succeeded=0, failed=0, denied=0, inFlight=0, exhausted=False)
    with pytest.raises(EvidenceError, match="exceed maximum"):
        replay_dispatch_audit(snapshot, snapshot["events"], maximum=10)


@pytest.mark.parametrize("raises", [False, True])
def test_failure_consumes_admission_and_denial_has_no_ticket_or_forward(raises):
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    calls = []
    def fail():
        calls.append("one")
        if raises:
            raise OSError("private failure")
        return NS(status="failed")
    if raises:
        with pytest.raises(OSError):
            budget.dispatch("inputText", "action", fail)
    else:
        budget.dispatch("inputText", "action", fail)
    with pytest.raises(NativeActionBudgetExceeded):
        budget.dispatch("killApp", "teardown", lambda: calls.append("forbidden"))
    audit = replay(budget)
    assert (audit["attempted"], audit["admitted"], audit["failed"], audit["denied"]) == (2, 1, 1, 1)
    assert audit["killEvidence"]["status"] == "denied"
    assert calls == ["one"]
    assert "ticket" not in budget.snapshot()["events"][-1]


def test_read_tickets_and_nonwrite_denials_do_not_consume_write_units():
    now = [1]
    budget = NativeDispatchBudget(1, 100, clock=lambda: now[0])
    budget.dispatch("ui_snapshot", "observation", lambda: NS(status="passed"))
    for alias in ("perform_actions", "performActions"):
        with pytest.raises(NativeBoundaryError):
            budget.dispatch(alias, "action", lambda: pytest.fail("must not forward"))
    now[0] = 100
    with pytest.raises(NativeDeadlineExceeded):
        budget.dispatch("screenshot", "observation", lambda: pytest.fail("must not forward"))
    audit = replay(budget)
    assert all(audit[key] == 0 for key in ("attempted", "admitted", "succeeded", "failed", "denied", "inFlight"))
    assert audit["deadlineExceeded"] is True
    assert audit["eventCount"] == 5


def test_replay_handles_interleaved_read_and_write_completion_tickets():
    budget = NativeDispatchBudget(2, 100, clock=lambda: 1)
    def nested():
        budget.dispatch("screenshot", "observation", lambda: NS(status="passed"))
        budget.dispatch("killApp", "teardown", lambda: NS(status="failed"))
        return NS(status="passed")
    budget.dispatch("tap_at", "action", nested)
    audit = replay(budget)
    assert (audit["admitted"], audit["succeeded"], audit["failed"]) == (2, 1, 1)
    assert audit["killEvidence"]["relativeToNativeExecutionReturned"] == "unknown"


@pytest.mark.parametrize("counter", ["attempted", "admitted", "succeeded", "failed", "denied", "inFlight"])
def test_every_counter_is_reconciled_with_real_events(counter):
    snapshot = successful_budget().snapshot()
    snapshot[counter] += 1
    with pytest.raises(EvidenceError, match="counter mismatch"):
        replay_dispatch_audit(snapshot, snapshot["events"], maximum=3)


@pytest.mark.parametrize("attack", ["duplicate_attempt", "duplicate_completion", "unmatched", "mismatched_capability", "mismatched_phase",
                                     "write_flag", "alias", "nonfinite", "backwards", "sequence", "bool_counter", "premature_denial"])
def test_forged_event_transitions_are_rejected(attack):
    snapshot = successful_budget().snapshot()
    events = snapshot["events"]
    if attack == "duplicate_attempt":
        events.insert(1, copy.deepcopy(events[0]))
    elif attack == "duplicate_completion":
        events.append(copy.deepcopy(events[1]))
    elif attack == "unmatched":
        events[1]["ticket"] = 99
    elif attack == "mismatched_capability":
        events[1]["capability"] = "kill_app"
    elif attack == "mismatched_phase":
        events[1]["phase"] = "teardown"
    elif attack == "write_flag":
        events[0]["countedWrite"] = False
    elif attack == "alias":
        events[0]["capability"] = "tapAt"
    elif attack == "nonfinite":
        events[1]["monotonic"] = float("nan")
    elif attack == "backwards":
        events[1]["monotonic"] = 0
    elif attack == "sequence":
        events[1]["sequence"] = 17
    elif attack == "bool_counter":
        snapshot["succeeded"] = True
    else:
        events[0].update(event="denied", reason="action_budget")
        del events[0]["ticket"]
    if attack in {"duplicate_attempt", "duplicate_completion"}:
        for index, event in enumerate(events, 1):
            event["sequence"] = index
    with pytest.raises(EvidenceError):
        replay_dispatch_audit(snapshot, events, maximum=3)


def test_inflight_read_cannot_hide_behind_zero_write_inflight_counter():
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    def forward():
        snapshot = budget.snapshot()
        assert snapshot["inFlight"] == 0
        with pytest.raises(EvidenceError, match="outstanding"):
            replay_dispatch_audit(snapshot, snapshot["events"], maximum=1)
        return NS(status="passed")
    budget.dispatch("ui_snapshot", "observation", forward)
    assert replay(budget)["outstandingTickets"] == []


def test_harness_close_is_not_inferred_to_be_kill():
    class Native:
        def close(self):
            pass
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    BudgetedAndroidHarness(Native(), budget).close()
    assert replay(budget)["killEvidence"]["status"] == "absent"
    snapshot = budget.snapshot()
    snapshot["events"].pop(0)
    snapshot["events"][0]["sequence"] = 1
    with pytest.raises(EvidenceError, match="Unmatched"):
        replay_dispatch_audit(snapshot, snapshot["events"], maximum=1)


def test_complete_consumer_rejects_rehashed_eleven_writes_hidden_behind_ten_limit(tmp_path):
    outcome, _, _ = episode(tmp_path)
    journal = tmp_path / "eleven-writes.jsonl"
    budget = NativeDispatchBudget(11, 100, clock=lambda: 1, journal=journal)
    for _ in range(11):
        budget.dispatch("tap_at", "action", lambda: NS(status="passed"))
    return_receipt(budget)
    snapshot = budget.snapshot()
    snapshot.update(maximum=10, attempted=0, admitted=0, succeeded=0, failed=0, denied=0, inFlight=0, exhausted=False)
    outcome["result"].update(actionBudget=snapshot, actionAudit=journal_reference(journal))
    with pytest.raises(EvidenceError, match="exceed maximum"):
        validate_native_evidence(outcome, episode_root=tmp_path, expected_task_id=TASK_ID,
                                 expected_serial=SERIAL, maximum=10)


@pytest.mark.parametrize("artifact", ["task", "journal"])
def test_duplicate_json_keys_are_rejected_even_with_correct_hash(tmp_path, artifact):
    outcome, _, _ = episode(tmp_path)
    if artifact == "task":
        ref = outcome["result"]["fsq"]["taskResult"]
        path = Path(ref["path"])
        text = path.read_text().replace('"task_id":', '"task_id": "forged", "task_id":', 1)
    else:
        ref = outcome["result"]["actionAudit"]
        path = Path(ref["path"])
        text = path.read_text().replace('"sequence":', '"sequence": 999, "sequence":', 1)
    path.write_text(text)
    ref.update(journal_reference(path))
    with pytest.raises(EvidenceError, match="Invalid native JSON"):
        validate(outcome, tmp_path)


def test_post_return_dispatch_and_duplicate_lifecycle_are_rejected():
    for after_return in ("dispatch", "return"):
        budget = successful_budget()
        return_receipt(budget)
        if after_return == "dispatch":
            budget.dispatch("kill_app", "teardown", lambda: NS(status="passed"))
        else:
            return_receipt(budget)
        with pytest.raises(EvidenceError, match="after full native"):
            replay(budget)


def test_known_lifecycle_observation_cannot_hide_unsettled_ticket():
    budget = NativeDispatchBudget(1, 100, clock=lambda: 1)
    def forward():
        return_receipt(budget)
        with pytest.raises(EvidenceError, match="precedes dispatch"):
            replay(budget)
        return NS(status="passed")
    budget.dispatch("tap_at", "action", forward)


def test_snapshot_deadline_check_can_be_true_without_fabricated_denial_event():
    now = [1]
    budget = NativeDispatchBudget(1, 2, clock=lambda: now[0])
    budget.dispatch("tap_at", "action", lambda: NS(status="passed"))
    now[0] = 2
    with pytest.raises(NativeDeadlineExceeded):
        budget.check_deadline()
    assert replay(budget)["deadlineExceeded"] is True


def test_admission_timestamp_is_not_falsely_treated_as_check_timestamp():
    now = iter([1, 100, 100])
    budget = NativeDispatchBudget(1, 100, clock=lambda: next(now))
    budget.dispatch("tap_at", "action", lambda: NS(status="passed"))
    assert replay(budget)["admitted"] == 1


def test_mixed_kill_outcomes_preserve_each_real_dispatch_order():
    budget = NativeDispatchBudget(2, 100, clock=lambda: 1)
    budget.dispatch("killApp", "teardown", lambda: NS(status="failed"))
    budget.dispatch("kill_app", "teardown", lambda: NS(status="passed"))
    with pytest.raises(NativeActionBudgetExceeded):
        budget.dispatch("kill_app", "teardown", lambda: pytest.fail("must not forward"))
    return_receipt(budget)
    kill = replay(budget)["killEvidence"]
    assert kill["status"] == "mixed"
    assert [(event["attemptSequence"], event["outcomeSequence"], event["outcome"]) for event in kill["events"]] == [
        (1, 2, "failed"), (3, 4, "succeeded"), (5, 5, "denied")]
    assert (kill["succeeded"], kill["failed"], kill["denied"]) == (1, 1, 1)
    assert kill["relativeToMainFinal"] == "unknown"


def test_visually_equivalent_unicode_is_not_normalized_during_summary_comparison(tmp_path):
    outcome, _, _ = episode(tmp_path, summary="\u00e9")
    outcome["result"]["mainAnswer"]["summary"] = "e\u0301"
    with pytest.raises(EvidenceError, match="summary/business status"):
        validate(outcome, tmp_path)


@pytest.mark.parametrize("field,value", [("event", []), ("countedWrite", 1), ("ticket", True),
                                         ("sequence", 1.0), ("monotonic", float("inf"))])
def test_malformed_event_values_raise_evidence_error(field, value):
    snapshot = successful_budget().snapshot()
    snapshot["events"][0][field] = value
    with pytest.raises(EvidenceError):
        replay_dispatch_audit(snapshot, snapshot["events"], maximum=3)


def test_deadline_denial_flag_cannot_be_forged_to_false():
    budget = NativeDispatchBudget(1, 100, clock=lambda: 100)
    with pytest.raises(NativeDeadlineExceeded):
        budget.dispatch("kill_app", "teardown", lambda: pytest.fail("must not forward"))
    snapshot = budget.snapshot()
    snapshot["deadlineExceeded"] = False
    with pytest.raises(EvidenceError, match="contradicts snapshot"):
        replay_dispatch_audit(snapshot, snapshot["events"], maximum=1)


def retained_swipe_episode(tmp_path):
    fixture = json.loads((Path(__file__).parent / "fixtures" / "fsq_native_swipe.json").read_text())
    result = fixture["result"]
    result["fsq"].update(
        taskResult=reference(tmp_path / "task.json", fixture["task"]),
        verification=reference(tmp_path / "verification.json", fixture["verification"]),
    )
    journal = tmp_path / "native-action-audit.jsonl"
    journal.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in fixture["journal"]))
    result["actionAudit"] = journal_reference(journal)
    return {"result": result}


def validate_retained_swipe(outcome, root):
    result = outcome["result"]
    return validate_native_evidence(outcome, episode_root=root, expected_task_id=result["taskId"],
                                    expected_serial=result["nativeTarget"]["serial"], maximum=10)


def test_retained_native_swipe_preserves_full_consumer_accounting_and_answer(tmp_path):
    outcome = retained_swipe_episode(tmp_path)
    evidence = validate_retained_swipe(outcome, tmp_path)
    audit = evidence["audit"]
    assert (audit["attempted"], audit["admitted"], audit["succeeded"], audit["failed"]) == (5, 5, 5, 0)
    assert audit["outstandingTickets"] == []
    assert evidence["answer"]["summary"] == outcome["result"]["mainAnswer"]["summary"]
    assert evidence["answer"]["businessStatus"] == outcome["result"]["mainAnswer"]["businessStatus"]
    assert evidence["killEvidence"]["status"] == "succeeded"
    assert evidence["killEvidence"]["relativeToMainFinal"] == "unknown"


def test_retained_native_journal_still_rejects_rehashed_noncanonical_alias(tmp_path):
    outcome = retained_swipe_episode(tmp_path)
    for event in outcome["result"]["actionBudget"]["events"]:
        if event.get("capability") == "launch_app":
            event["capability"] = "launchApp"
    rewrite_journal(outcome)
    with pytest.raises(EvidenceError):
        validate_retained_swipe(outcome, tmp_path)


def test_retained_native_swipe_cannot_be_relabelled_as_an_uncounted_read(tmp_path):
    outcome = retained_swipe_episode(tmp_path)
    budget = outcome["result"]["actionBudget"]
    for event in budget["events"]:
        if event.get("capability") == "swipe":
            event["countedWrite"] = False
    for counter in ("attempted", "admitted", "succeeded"):
        budget[counter] -= 1
    rewrite_journal(outcome)
    with pytest.raises(EvidenceError):
        validate_retained_swipe(outcome, tmp_path)
