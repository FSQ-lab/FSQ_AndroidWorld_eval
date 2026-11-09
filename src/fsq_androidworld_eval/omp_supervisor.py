"""Own OMP's RPC process until task completion or a layered shutdown boundary.

A queued steer never aborts an in-flight MCP call. Action exhaustion permits a
bounded business final within the original business deadline; only afterward
does the separate cleanup window begin. Receipt time, not queue-consumer timing,
selects the first business final. Cleanup prose never supplies an IR answer.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from queue import Empty, Queue
import signal
import subprocess
from threading import Thread
import time
from typing import Any, Callable

from fsq_androidworld_eval.action_budget import ActionGate
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines
from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission

FINALIZATION_MESSAGE = (
    "HARNESS CONTROL: The UI action budget is exhausted. No more UI mutations or "
    "new sessions are permitted. Let the current admitted python_exec deliver its "
    "result without retrying actions. Read-only observations remain available, but "
    "stop gathering evidence as soon as the existing result suffices. Within at most "
    "120 seconds and never beyond the original business deadline, submit one final "
    "JSON object with taskOutcome as a nonempty STRING, for example "
    "{\"taskOutcome\":\"answer text\"}. Do not guess missing information. This is the business "
    "submission, not a cleanup report. The Harness will request cleanup separately."
)

CLEANUP_MESSAGE = (
    "HARNESS CONTROL: The business submission window is closed. No more UI "
    "mutations or new sessions are permitted. Let any current python_exec finish "
    "without retrying its actions. Use the existing live driver to quit now. In a "
    "dedicated python_exec cell retain session_id=driver.session_id, call driver.quit(), "
    "and return exactly {'ownedSessionId':session_id,'quitReturned':True} only if "
    "quit returned. Do not repeat an already successful quit. If no driver exists "
    "or the Kernel is dead report that honestly; do not create a replacement session. "
    "Preserve the requested final device state. Finish with a cleanup report only; "
    "do not submit taskOutcome. Cleanup text cannot replace the business submission."
)


def termination_reason(
    normalized: dict[str, Any], *, business_expired: bool, forced: bool,
    budget_closure_reason: str | None,
) -> str:
    if forced:
        return "forced_termination"
    if normalized.get("ompDeadlineObserved"):
        return "omp_deadline"
    if business_expired:
        return "business_deadline"
    if normalized.get("agentCompleted"):
        return "completed"
    events = normalized.get("terminalEvents")
    terminal = events[-1] if isinstance(events, list) and events else None
    if (
        budget_closure_reason == "step_budget"
        and normalized.get("assistantStopReason") == "stop"
        and isinstance(terminal, dict)
        and terminal.get("type") == "agent_end"
        and terminal.get("isTerminal") is True
    ):
        return "step_budget"
    return "unknown_termination"


def run_omp(
    *, project: Path, sandbox_profile: Path, output_dir: Path, prompt: str,
    omp: str, model: str, deadlines: EpisodeDeadlines, action_gate: ActionGate,
    normalize: Callable[[Path], dict[str, Any]], skills: tuple[str, ...],
) -> dict[str, Any]:
    raw_dir = output_dir / "raw-private"
    raw_dir.mkdir(mode=0o700)
    stdout_path = raw_dir / "agent-events.jsonl"
    stderr_path = raw_dir / "agent-stderr.txt"
    command = [
        "/usr/bin/sandbox-exec", "-f", str(sandbox_profile), omp,
        "--mode", "rpc", "--no-ui", "--no-session", "--auto-approve",
        "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,write",
        "--skills", ",".join(skills), "--model", model, "--cwd", str(project),
    ]
    started = time.monotonic()
    deadlines.start()
    business_end = time.monotonic() + deadlines.remaining("business")
    events: Queue[tuple[float, int, dict[str, Any]] | None] = Queue()
    business_expired = False
    forced = False
    cleanup_requested = False
    cleanup_seen = False
    cleanup_prompt_sent = False
    cleanup_at: float | None = None
    finalization_at: float | None = None
    finalization_end: float | None = None
    submission_cutoff = business_end
    submission_text: str | None = None
    submission_receipt: dict[str, Any] | None = None
    ignored_finals = 0
    task_completed = False
    last_stop: str | None = None
    commands: list[str] = []

    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w") as stderr:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=stderr,
            text=True, bufsize=1, start_new_session=os.name == "posix", cwd=project,
        )

        def read_events() -> None:
            assert process.stdout is not None
            sequence = 0
            try:
                for line in process.stdout:
                    received = time.monotonic()
                    stdout.write(line)
                    stdout.flush()
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(event, dict):
                        sequence += 1
                        events.put((received, sequence, event))
            finally:
                events.put(None)

        reader = Thread(target=read_events, name="omp-event-reader", daemon=True)
        reader.start()

        def send(command_type: str, **params: Any) -> None:
            assert process.stdin is not None
            process.stdin.write(json.dumps({"type": command_type, **params}) + "\n")
            process.stdin.flush()
            commands.append(command_type)

        def begin_cleanup(*, cutoff: float, terminal: bool = False) -> None:
            nonlocal cleanup_requested, cleanup_at, submission_cutoff, cleanup_prompt_sent
            submission_cutoff = min(submission_cutoff, cutoff)
            if not cleanup_requested:
                cleanup_at = time.monotonic()
                cleanup_requested = True
                action_gate.close_budget(reason="agent_finished")
                deadlines.begin_cleanup()
                if process.poll() is None:
                    send("prompt" if terminal else "steer", id="cleanup", message=CLEANUP_MESSAGE)
                    cleanup_prompt_sent = terminal

        def terminate(sig: int) -> None:
            try:
                if os.name == "posix":
                    os.killpg(process.pid, sig)
                elif sig == signal.SIGTERM:
                    process.terminate()
                else:
                    process.kill()
            except ProcessLookupError:
                pass

        try:
            send("set_interrupt_mode", id="interrupt-policy", mode="wait")
            send("prompt", id="episode", message=prompt)
            # Drain the reader through EOF even if the child has already exited.
            # Receipt timestamps, not consumer scheduling, define the answer cutoff.
            while True:
                now = time.monotonic()
                if not task_completed and not business_expired and now >= business_end:
                    business_expired = True
                    action_gate.close_budget(reason="business_deadline")
                gate = action_gate.snapshot()
                if (gate.get("closureReason") == "step_budget" and finalization_at is None
                        and not cleanup_requested and submission_receipt is None):
                    finalization_at = gate["closedAtMonotonic"]
                    finalization_end = min(
                        finalization_at + ANSWER_SUBMISSION_PROTOCOL["maximumFinalizationSeconds"],
                        business_end,
                    )
                    submission_cutoff = min(submission_cutoff, finalization_end)
                    if now < finalization_end and process.poll() is None:
                        send("steer", id="answer-finalization", message=FINALIZATION_MESSAGE)
                if not cleanup_requested:
                    if business_expired:
                        begin_cleanup(cutoff=business_end)
                    elif finalization_end is not None and now >= finalization_end:
                        begin_cleanup(cutoff=finalization_end)
                    elif gate.get("closed") and gate.get("closureReason") not in {
                        "step_budget", "agent_finished"
                    }:
                        begin_cleanup(cutoff=now)
                if deadlines.expired("cleanup"):
                    forced = True
                    terminate(signal.SIGTERM)
                    break
                try:
                    received_event = events.get(timeout=min(0.1, deadlines.remaining("cleanup")))
                except Empty:
                    if process.poll() is not None and not reader.is_alive():
                        break
                    continue
                if received_event is None:
                    break
                received, sequence, event = received_event
                if event.get("type") == "response" and event.get("success") is False:
                    raise RuntimeError("OMP rejected a Harness lifecycle RPC command")
                if event.get("type") == "message_end":
                    message = event.get("message", {})
                    if message.get("role") == "user" and any(
                        item.get("text") == CLEANUP_MESSAGE
                        for item in message.get("content", []) if isinstance(item, dict)
                    ):
                        cleanup_seen = True
                    if message.get("role") == "assistant":
                        last_stop = message.get("stopReason")
                        if last_stop == "stop":
                            if submission_receipt is None and not cleanup_seen and received <= submission_cutoff:
                                submission_text = "".join(
                                    item["text"] for item in message.get("content", [])
                                    if isinstance(item, dict) and isinstance(item.get("text"), str)
                                )
                                submission_receipt = {
                                    "eventSequence": sequence,
                                    "receivedAtSeconds": received - started,
                                    "phase": "finalization" if finalization_at is not None
                                    and received >= finalization_at else "business",
                                }
                                action_gate.close_budget(reason="agent_finished")
                            else:
                                ignored_finals += 1
                if event.get("type") == "agent_end" and event.get("isTerminal") is True:
                    observed = normalize(stdout_path)
                    has_quit = any("sessionCleanup" in call for call in observed["toolCalls"])
                    used_kernel = any(
                        call.get("target") == "xd://mcp__amkernel_python_exec"
                        for call in observed["toolCalls"]
                    )
                    if not cleanup_requested:
                        task_completed = (
                            submission_receipt is not None and last_stop == "stop"
                            and received <= business_end
                            and action_gate.snapshot().get("closureReason") != "step_budget"
                        )
                        if used_kernel and not has_quit:
                            begin_cleanup(cutoff=received, terminal=True)
                            continue
                        # No cleanup turn is needed when the existing dedicated
                        # quit proof already exists (or no Runtime was used).
                        submission_cutoff = min(submission_cutoff, received)
                        break
                    if ((not cleanup_seen or used_kernel and not has_quit)
                            and not cleanup_prompt_sent and process.poll() is None):
                        send("prompt", id="cleanup", message=CLEANUP_MESSAGE)
                        cleanup_prompt_sent = True
                        continue
                    break
        finally:
            if process.stdin is not None:
                process.stdin.close()
            if process.poll() is None:
                try:
                    process.wait(timeout=min(2, deadlines.remaining("cleanup")))
                except subprocess.TimeoutExpired:
                    terminate(signal.SIGTERM)
            if process.poll() is None:
                try:
                    process.wait(timeout=max(0.01, deadlines.remaining("force") - 0.1))
                except subprocess.TimeoutExpired:
                    forced = True
                    terminate(signal.SIGKILL)
            exit_code = process.wait(timeout=1)
            reader.join(timeout=1)

    normalized = normalize(stdout_path)
    from fsq_androidworld_eval.runner import _scrub_final_text
    normalized["finalText"] = _scrub_final_text(submission_text) if submission_text else None
    normalized["agentCompleted"] = task_completed
    submission = parse_submission(submission_text)
    submission_path = raw_dir / "business-submission.json"
    submission_path.write_text(json.dumps(submission, indent=2, sort_keys=True) + "\n")
    submission_evidence = {
        "protocol": ANSWER_SUBMISSION_PROTOCOL,
        "path": str(submission_path.relative_to(output_dir)),
        "sha256": hashlib.sha256(submission_path.read_bytes()).hexdigest(),
        "receipt": submission_receipt,
        "cutoffSeconds": submission_cutoff - started,
        "businessDeadlineSeconds": business_end - started,
        "finalizationStartedAtSeconds": finalization_at - started if finalization_at is not None else None,
        "finalizationDeadlineSeconds": finalization_end - started if finalization_end is not None else None,
        "cleanupRequestedAtSeconds": cleanup_at - started if cleanup_at is not None else None,
        "ignoredFinalMessages": ignored_finals,
    }
    reason = termination_reason(
        normalized, business_expired=business_expired, forced=forced,
        budget_closure_reason=action_gate.snapshot().get("closureReason"),
    )
    normalized_path = output_dir / "normalized-agent-events.json"
    normalized_path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n")
    return {
        "command": ["sandbox-exec", "<sandbox-profile>", omp, "--mode", "rpc",
                    "--cwd", "<isolated-agent-project>"],
        "processExited": True, "exitCode": exit_code,
        "agentCompleted": task_completed,
        "completedBeforeBusinessDeadline": task_completed,
        "answerSubmission": submission_evidence,
        "timedOut": reason in {"omp_deadline", "business_deadline", "forced_termination"},
        "termination": {"reason": reason, "businessDeadlineReached": business_expired,
                        "actionBudgetClosureReason": action_gate.snapshot().get("closureReason"),
                        "outerTermination": forced, "cleanupRequested": cleanup_requested,
                        "rpcCommands": commands, "deadlines": deadlines.snapshot()},
        "durationSeconds": round(time.monotonic() - started, 3),
        "rawEventsPath": str(stdout_path.relative_to(output_dir)),
        "rawStderrPath": str(stderr_path.relative_to(output_dir)),
        "normalizedEventsPath": normalized_path.name,
        "rawEventsSha256": hashlib.sha256(stdout_path.read_bytes()).hexdigest(),
        "rawStderrSha256": hashlib.sha256(stderr_path.read_bytes()).hexdigest(),
        "normalized": normalized,
    }
