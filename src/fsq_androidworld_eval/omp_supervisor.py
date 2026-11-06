"""Own OMP's RPC process until task completion or a layered shutdown boundary.

A queued steer never aborts an in-flight MCP call. Business expiry denies new UI
permits; OMP and its MCP Runtime remain alive for the separate cleanup window.
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

CLEANUP_MESSAGE = (
    "HARNESS CONTROL: The business/action budget is closed. No more UI mutations or "
    "new sessions are permitted. Let any current python_exec finish without retrying "
    "its actions. Use the existing live driver to quit now. In a dedicated python_exec "
    "cell retain session_id=driver.session_id, call driver.quit(), and return exactly "
    "{'ownedSessionId':session_id,'quitReturned':True} only if quit returned. "
    "If no driver exists or the Kernel is dead report that honestly; do not create a "
    "replacement session. Preserve the requested final device state. Then finish."
)


def termination_reason(
    normalized: dict[str, Any], *, business_expired: bool, forced: bool,
) -> str:
    if forced:
        return "forced_termination"
    if normalized.get("ompDeadlineObserved"):
        return "omp_deadline"
    if business_expired:
        return "business_deadline"
    if normalized.get("agentCompleted"):
        return "completed"
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
    events: Queue[dict[str, Any] | None] = Queue()
    business_expired = False
    forced = False
    cleanup_requested = False
    cleanup_seen = False
    cleanup_prompt_sent = False
    task_final: str | None = None
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
            try:
                for line in process.stdout:
                    stdout.write(line)
                    stdout.flush()
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(event, dict):
                        events.put(event)
            finally:
                events.put(None)

        reader = Thread(target=read_events, name="omp-event-reader", daemon=True)
        reader.start()

        def send(command_type: str, **params: Any) -> None:
            assert process.stdin is not None
            process.stdin.write(json.dumps({"type": command_type, **params}) + "\n")
            process.stdin.flush()
            commands.append(command_type)

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
            while process.poll() is None:
                if not task_completed and not business_expired and deadlines.expired("business"):
                    business_expired = True
                    action_gate.close_budget(reason="business_deadline")
                if (business_expired or action_gate.snapshot().get("closed")) and not cleanup_requested:
                    deadlines.begin_cleanup()
                    send("steer", id="cleanup-steer", message=CLEANUP_MESSAGE)
                    cleanup_requested = True
                if deadlines.expired("cleanup"):
                    forced = True
                    terminate(signal.SIGTERM)
                    break
                try:
                    event = events.get(timeout=min(0.1, deadlines.remaining("cleanup")))
                except Empty:
                    continue
                if event is None:
                    break
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
                        if not cleanup_requested and last_stop == "stop":
                            task_final = "".join(
                                item["text"] for item in message.get("content", [])
                                if isinstance(item, dict) and isinstance(item.get("text"), str)
                            ) or None
                if event.get("type") == "agent_end":
                    if event.get("isTerminal") is not True:
                        continue
                    if not cleanup_requested:
                        task_completed = last_stop == "stop" and task_final is not None
                    observed = normalize(stdout_path)
                    has_quit = any("sessionCleanup" in call for call in observed["toolCalls"])
                    used_kernel = any(
                        call.get("target") == "xd://mcp__amkernel_python_exec"
                        for call in observed["toolCalls"]
                    )
                    if (cleanup_requested and not cleanup_seen or used_kernel and not has_quit) and not cleanup_prompt_sent:
                        action_gate.close_budget(reason="agent_finished")
                        deadlines.begin_cleanup()
                        send("prompt", id="cleanup", message=CLEANUP_MESSAGE)
                        cleanup_requested = True
                        cleanup_prompt_sent = True
                        continue
                    # Ignore intermediate run settles; only a terminal settle
                    # after cleanup opportunity permits Runtime disposal.
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
    if cleanup_requested:
        # Cleanup prose is not the task answer. Its tool results remain evidence.
        from fsq_androidworld_eval.runner import _scrub_final_text
        normalized["finalText"] = _scrub_final_text(task_final) if task_final else None
        normalized["agentCompleted"] = task_completed
    reason = termination_reason(normalized, business_expired=business_expired, forced=forced)
    normalized_path = output_dir / "normalized-agent-events.json"
    normalized_path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n")
    return {
        "command": ["sandbox-exec", "<sandbox-profile>", omp, "--mode", "rpc",
                    "--cwd", "<isolated-agent-project>"],
        "processExited": True, "exitCode": exit_code,
        "agentCompleted": bool(normalized["agentCompleted"]),
        "completedBeforeBusinessDeadline": task_completed and not business_expired,
        "timedOut": reason in {"omp_deadline", "business_deadline", "forced_termination"},
        "termination": {"reason": reason, "businessDeadlineReached": business_expired,
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
