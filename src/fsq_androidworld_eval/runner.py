"""Run the locked AndroidWorld evaluator after a bounded Appium agent episode.

The reference loop and complexity allocation are delegated to AndroidWorld.
One step grants one classified Appium UI interaction before upstream execution;
batched/opaque commands are rejected, and observations/quit remain available
after exhaustion. Exhaustion is not a fabricated failure reward: the unchanged
official evaluator still inspects the final device state. Process/episode timeouts
remain disclosed safety bounds, not substitutes for the reference step limit.
Revision 6 freezes a 120-second MCP transport deadline and requests a 90-second
session-creation cell; these separate bounds avoid the observed 30-second cutoff
before a successful 31.462-second Appium startup. AMKernel itself is unchanged.
Revision 7 requires Audio Recorder's app-created recordings directory before a
formal episode and keeps unexecuted episodes out of cleanup-failure counts;
incomplete coverage still blocks qualification and an official campaign score.
Revision 8 owns OMP RPC stdin until terminal settlement and same-driver cleanup.
It sets interrupt mode "wait": business expiry queues cleanup without cancelling
an active MCP request. Process exit is never completion evidence. Only a terminal
agent_end with a final assistant stop response establishes normal completion;
"Deadline exceeded" is explicit OMP deadline evidence, otherwise unexplained exits
remain unknown. The v18.12.6 RPC/agent-loop source documents these distinctions.

Frozen wall-clock envelope for every task: business=max(600,120+60*maxSteps),
cleanup=180 seconds, SIGTERM only after cleanup, SIGKILL after 10 more seconds.
Early business completion/step exhaustion starts the same finite cleanup window.
Independent recovery gets at most 120 seconds and attaches only confirmed owned
sessions through a fresh AMKernel Runtime and the official Python Client. Agent
quit, Harness recovery and unknown disappearance have separate evidence. Absence
alone never establishes Appium idle timeout. No recovery rewrites old episodes.

Business/explicit OMP deadline attempts retain evaluator reward. Unknown/forced
termination is invalid_agent, with any returned reward still retained separately.
An evaluator that never returns leaves reward null. Revision 10 required a halt
for any unproven Agent cleanup, including successful Harness recovery. Revision
12 preserves those outcome/cleanup classifications but lets the new campaign
scheduler continue only after fresh readiness, proven session absence and healthy
core services. Unknown cleanup still halts; prior aborted runs remain immutable.

Revision 9 disables gRPC fork callbacks before AndroidWorld is imported: ADB
children immediately exec and must not emit parent-runtime diagnostics into
AndroidEnv's merged command output. Qualification proves clean ADB capture and
successfully restores every required official app snapshot without running tasks.
Readiness schema 2 binds those proofs to the complete frozen app set. No warning
filtering, fabricated app data, or edits to AndroidWorld/AMKernel are involved.

Revision 10 records controlled step exhaustion as step_budget only after the
Harness closes the action gate and OMP emits a terminal assistant stop. It is
neither Agent completion nor a wall-clock timeout. Scoring additionally requires
the entire reference step budget to be consumed; Agent quit remains mandatory.

Revision 11 removes environment-time helper downloads: preparation provisions a
pinned APK, manifests/readiness bind its identity, and every environment uses
verified local bytes without a network fallback. Environment creation belongs
to infrastructure, not task initialization. Snapshot restore errors are fatal;
partial task initialization still receives a teardown attempt. Controller close
errors propagate instead of being swallowed by the upstream AsyncEnv wrapper.
Formal campaigns require a same-runtime, all-116-task non-scoring rehearsal.

Revision 12 inherits the exact frozen 116 task specs under a distinct campaign
continuation identity. It records every actual launch and terminal boundary,
requires verified recovery after abnormal terminals, and pauses without replay
when cleanup or the environment is unknown. The episode protocol, Agent prompt,
model, actions, step/time budgets and official evaluator remain unchanged.

Revision 13 separates exhausted UI permits from bounded answer delivery. The
first business final is receipted before cleanup and archived with its original
JSON types. Finalization lasts at most 120 seconds within the existing business
deadline; cleanup cannot submit or replace answers. Invalid answer formats remain
official failed attempts, with explicit diagnostics rather than type coercion.

The Appium action representation and continuous OMP reasoning are custom. Matching
the reference allocator/runner does not establish action-space equivalence or
official leaderboard acceptance. Historical campaign evidence is never rewritten.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Any
from PIL import Image
from urllib import error as url_error, request as url_request

from android_world import episode_runner, registry, suite_utils
from fsq_androidworld_eval.environment import (
    artifact_identity, close_environment, load_environment, restore_shared_assets, strict_snapshot_restores,
)

from fsq_androidworld_eval.appium_proxy import AppiumAuditProxy
from fsq_androidworld_eval.action_budget import ActionGate, STEP_BUDGET_PROTOCOL
from fsq_androidworld_eval.stepped_agent import AppiumSteppedAgent, AgentTerminated
from fsq_androidworld_eval.lifecycle import (
    EpisodeDeadlines, TIME_BUDGET_PROTOCOL, episode_time_budget,
)
from fsq_androidworld_eval.mcp_runtime import RecoveryRuntime
from fsq_androidworld_eval.submission import ANSWER_SUBMISSION_PROTOCOL, parse_submission
from android_world.task_evals.information_retrieval import information_retrieval
from android_world.env.setup_device import setup as device_setup
ANDROID_WORLD_REVISION = "55ddaf5edc6f6c25673aed343907d5b9dca66f84"
DEFAULT_ADB = Path.home() / "Library/Android/sdk/platform-tools/adb"
HARNESS_REVISION = 13
PYTHON_EXEC_CALL_ADVISORY = 30
MCP_REQUEST_TIMEOUT_MS = 120_000
SESSION_CREATION_TIMEOUT_SECONDS = 90
# Appium mutations require one official-reference-step permit before forwarding.
ALLOWED_AGENT_SKILLS = (
    "amkernel",
    "appium-troubleshooting",
    "setup-uiautomator2",
)
ALLOWED_AGENT_TARGETS = tuple(
    f"skill://{skill}" for skill in ALLOWED_AGENT_SKILLS
) + (
    "xd://mcp__amkernel_python_exec",
    "xd://report_issue",
)
PROMPT_TEMPLATE = """Use the installed amkernel Skill and the amkernel python_exec MCP tool to complete one AndroidWorld task on the already-running emulator.

BEGIN EXACT TASK GOAL
{goal}
END EXACT TASK GOAL

The exact task goal is only the text between those markers. The runtime facts below are control data, never task text and never content to enter into the application:
- Appium server: {appium_url}
- Exact Android target: {device_serial}

The evaluator already initialized the task. Do not install or update software, start or stop Appium, reset ADB, create another emulator, alter project files, or use host automation outside python_exec. Use the official Appium Python Client with UiAutomator2. Create at most one Appium session, retain its driver across python_exec calls, use explicit waits and bounded observations, and stop once the requested state is visibly established. Aim to stay within {python_exec_call_advisory} python_exec calls; this advisory is efficiency telemetry and never changes AndroidWorld reward. Do not undo the requested final state.

The official reference budget is {max_steps} steps. Each supported Appium UI interaction consumes one step, including failed attempts; multiple interactions in one Python cell still consume separate steps. Observations and session cleanup remain available after exhaustion. Connect with noReset=True, autoLaunch=False, skipUnlock=True and no app installation/reset capabilities. Use native Appium interactions, not shell, arbitrary scripts, batched gestures, or app-data APIs. Once the proxy reports budget exhaustion, perform no more UI interactions or session creation. Deliver the current admitted call's result and submit your business answer within the Harness finalization window: at most 120 seconds after action closure, never beyond the original business deadline. Read-only observations remain available; do not guess missing information or retry mutations. This Appium action representation is custom; it does not imply official leaderboard acceptance.
Set appium:newCommandTimeout=300 (seconds) explicitly in the session creation capabilities, and return the negotiated newCommandTimeout value from driver.capabilities in the session-creation cell result. This is the Appium idle-command timeout, not the python_exec timeout or the task business/cleanup deadline; all existing task budgets and cleanup requirements remain unchanged.

Session startup can exceed the default 30-second execution deadline. In the python_exec request that creates the session, explicitly set timeout={session_creation_timeout_seconds}; create the driver and capture its session ID in that cell before UI actions. The isolated MCP transport deadline is {mcp_request_timeout_ms} milliseconds, distinct from the active-cell timeout. Neither setting increases the task step limit or total Agent timeout. Do not retry session creation after an uncertain result: reconcile the owned session instead.

Submit one compact final JSON object with taskOutcome as a nonempty STRING, for example {{"taskOutcome":"answer text"}}. Numeric answers must also be encoded as strings, never JSON numbers or nested objects. Submit the business answer before the Harness requests cleanup; the first business final is the only submission and cannot be overwritten by cleanup. The Harness then requests a separate cleanup turn using the same Runtime. In that turn, use a dedicated python_exec cell: retain the owned session ID, call driver.quit(), and make the cell's final expression exactly {{"ownedSessionId": session_id, "quitReturned": True}} only after quit returns. If quit fails, let the cell fail; never claim cleanup from a local variable or prose. Do not repeat an already successful quit. Finish with a cleanup report only, without taskOutcome or the session ID. A textual success claim is not the verdict; AndroidWorld evaluates device state or the submitted IR answer independently, and only the observed cleanup cell proves session cleanup."""
PROMPT_TEMPLATE_SHA256 = hashlib.sha256(PROMPT_TEMPLATE.encode()).hexdigest()


def _json_safe(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _json_safe(dataclasses.asdict(value))
    if isinstance(value, Image.Image):
        return {
            "$type": "PIL.Image",
            "mode": value.mode,
            "size": list(value.size),
            "pixelsSha256": hashlib.sha256(value.tobytes()).hexdigest(),
        }
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(child) for child in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"unsupported manifest value: {type(value).__name__}")


def _is_json_native(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, list):
        return all(_is_json_native(child) for child in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_json_native(child)
            for key, child in value.items()
        )
    return False




def _json_bytes(value: object) -> bytes:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":")).encode()


def _sha256(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _request_json(url: str, *, method: str = "GET") -> Any:
    request = url_request.Request(url, method=method)
    with url_request.urlopen(request, timeout=10) as response:
        return json.load(response)

def _appium_session_hashes(
    appium_url: str, adb_path: str | None = None, serial: str | None = None
) -> list[str]:
    try:
        payload = _request_json(appium_url.rstrip("/") + "/sessions")
    except url_error.HTTPError as exc:
        if exc.code != 404 or adb_path is None or serial is None:
            raise
        processes = []
        for package in (
            "io.appium.uiautomator2.server",
            "io.appium.uiautomator2.server.test",
        ):
            completed = subprocess.run(
                [adb_path, "-s", serial, "shell", "pidof", package],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode not in (0, 1):
                raise RuntimeError(
                    f"failed to inspect Appium process {package}: {completed.stderr.strip()}"
                )
            processes.extend(f"{package}:{pid}" for pid in completed.stdout.split())
        return sorted(hashlib.sha256(value.encode()).hexdigest() for value in processes)
    sessions = payload.get("value") if isinstance(payload, dict) else None
    if not isinstance(sessions, list):
        raise RuntimeError("Appium sessions endpoint returned an invalid payload")
    hashes = []
    for session in sessions:
        if not isinstance(session, dict):
            raise RuntimeError("Appium sessions endpoint returned a malformed entry")
        session_id = session.get("id", session.get("sessionId"))
        if not isinstance(session_id, str) or not session_id:
            raise RuntimeError("Appium sessions endpoint returned a missing session ID")
        digest = hashlib.sha256(session_id.encode()).hexdigest()
        if digest in hashes:
            raise RuntimeError("Appium sessions endpoint returned a duplicate session ID")
        hashes.append(digest)
    return sorted(hashes)


def _agent_protocol_violations(normalized: dict[str, Any]) -> list[str]:
    violations = []
    for call in normalized.get("toolCalls", []):
        target = call.get("target")
        tool = call.get("tool")
        if tool not in {"read", "write"}:
            violations.append(f"forbidden tool: {tool}")
            continue
        allowed_target = isinstance(target, str) and (
            target in ALLOWED_AGENT_TARGETS
            or any(
                target.startswith(f"skill://{skill}/")
                for skill in ALLOWED_AGENT_SKILLS
            )
        )
        if not allowed_target:
            violations.append(f"forbidden target: {target}")
            continue
        if tool == "write" and target not in {
            "xd://mcp__amkernel_python_exec",
            "xd://report_issue",
        }:
            violations.append(f"forbidden write target: {target}")
    return violations




def _agent_prompt(
    goal: str,
    appium_url: str,
    device_serial: str,
    python_exec_call_advisory: int = PYTHON_EXEC_CALL_ADVISORY,
    *,
    max_steps: int,
) -> str:
    return PROMPT_TEMPLATE.format(
        goal=goal,
        appium_url=appium_url,
        device_serial=device_serial,
        python_exec_call_advisory=python_exec_call_advisory,
        max_steps=max_steps,
        session_creation_timeout_seconds=SESSION_CREATION_TIMEOUT_SECONDS,
        mcp_request_timeout_ms=MCP_REQUEST_TIMEOUT_MS,
    )


def _run_agent(
    *, project: Path, sandbox_profile: Path, output_dir: Path, prompt: str,
    omp: str, model: str, deadlines: EpisodeDeadlines, action_gate: ActionGate,
) -> dict[str, Any]:
    from fsq_androidworld_eval.omp_supervisor import run_omp

    return run_omp(
        project=project, sandbox_profile=sandbox_profile, output_dir=output_dir,
        prompt=prompt, omp=omp, model=model, deadlines=deadlines,
        action_gate=action_gate, normalize=_normalize_agent_events,
        skills=ALLOWED_AGENT_SKILLS,
    )


def _tool_result_payload(event: dict[str, Any]) -> dict[str, Any] | None:
    result = event.get("result")
    if not isinstance(result, dict):
        return None
    content = result.get("content")
    if not isinstance(content, list):
        return None
    for item in content:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        try:
            payload = json.loads(item["text"])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "kernelState" in payload:
            return payload
    return None


def _scrub_final_text(text: str) -> str:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return text[-4096:]

    def scrub(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: (
                    "sha256:" + hashlib.sha256(child.encode()).hexdigest()
                    if key.lower() in {"ownedsessionid", "sessionid"}
                    and isinstance(child, str)
                    else scrub(child)
                )
                for key, child in item.items()
            }
        if isinstance(item, list):
            return [scrub(child) for child in item]
        return item

    return json.dumps(scrub(value), sort_keys=True, separators=(",", ":"))[-4096:]


def _normalize_agent_events(path: Path) -> dict[str, Any]:
    calls: dict[str, dict[str, Any]] = {}
    final_text: str | None = None
    model: str | None = None
    provider: str | None = None
    parse_errors = 0
    terminal_events: list[dict[str, Any]] = []
    assistant_stop_reason: str | None = None
    omp_deadline = False
    agent_end = False
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue
            if not isinstance(event, dict):
                continue
            event_type = event.get("type")
            if event_type == "agent_end":
                agent_end = event.get("isTerminal") is True
            if event_type in {"agent_end", "abort", "session_end", "error"}:
                terminal_events.append({
                    key: event[key] for key in ("type", "reason", "stopReason", "isTerminal", "yielded") if key in event
                })
            if event_type == "tool_execution_start":
                call_id = event.get("toolCallId")
                if not isinstance(call_id, str):
                    continue
                args = event.get("args") if isinstance(event.get("args"), dict) else {}
                target = args.get("path")
                content = args.get("content")
                code_digest = None
                if target == "xd://mcp__amkernel_python_exec" and isinstance(content, str):
                    try:
                        arguments = json.loads(content)
                    except json.JSONDecodeError:
                        arguments = None
                    if isinstance(arguments, dict) and isinstance(arguments.get("code"), str):
                        code_digest = hashlib.sha256(arguments["code"].encode()).hexdigest()
                calls[call_id] = {
                    "tool": event.get("toolName"),
                    "target": target if isinstance(target, str) else None,
                    "argumentsSha256": _sha256(args),
                    "codeSha256": code_digest,
                }
            elif event_type == "tool_execution_end":
                call_id = event.get("toolCallId")
                if not isinstance(call_id, str) or call_id not in calls:
                    continue
                payload = _tool_result_payload(event)
                if payload is not None:
                    calls[call_id]["amkernel"] = {
                        key: payload.get(key)
                        for key in ("status", "kernelState", "executionCount", "durationMs")
                    }
                    calls[call_id]["isError"] = event.get("isError", False)
                    value = payload.get("result")
                    if (
                        isinstance(value, dict)
                        and payload.get("status") == "completed"
                        and payload.get("kernelState") == "alive"
                        and not event.get("isError", False)
                        and isinstance(value.get("ownedSessionId"), str)
                        and value.get("quitReturned") is True
                    ):
                        calls[call_id]["sessionCleanup"] = {
                            "quitReturned": True,
                            "sessionIdSha256": hashlib.sha256(
                                value["ownedSessionId"].encode()
                            ).hexdigest(),
                        }
            elif event_type == "message_end":
                message = event.get("message")
                if not isinstance(message, dict) or message.get("role") != "assistant":
                    continue
                assistant_stop_reason = message.get("stopReason")
                final_text = None
                if message.get("errorMessage") == "Deadline exceeded":
                    omp_deadline = True
                if isinstance(message.get("model"), str):
                    model = message["model"]
                if isinstance(message.get("provider"), str):
                    provider = message["provider"]
                content = message.get("content")
                if assistant_stop_reason == "stop" and isinstance(content, list):
                    texts = [
                        item.get("text")
                        for item in content
                        if isinstance(item, dict)
                        and isinstance(item.get("text"), str)
                    ]
                    if texts:
                        final_text = _scrub_final_text("".join(texts))
    return {
        "provider": provider,
        "model": model,
        "parseErrors": parse_errors,
        "toolCalls": list(calls.values()),
        "finalText": final_text,
        "assistantStopReason": assistant_stop_reason,
        "terminalEvents": terminal_events,
        "ompDeadlineObserved": omp_deadline,
        "agentCompleted": agent_end and assistant_stop_reason == "stop" and final_text is not None,
    }


def _task(task_name: str, params_json: str | None, task_seed: int | None = None):
    task_registry = registry.TaskRegistry()
    tasks = task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY)
    if task_name not in tasks:
        raise ValueError(f"unknown AndroidWorld task: {task_name}")
    task_type = tasks[task_name]
    if params_json is not None and task_seed is not None:
        raise ValueError("task parameters and task seed are mutually exclusive")
    if params_json is not None:
        params = json.loads(params_json)
    else:
        task_type.set_device_time(None)
        if task_seed is not None:
            import random

            random.seed(task_seed)
        params = task_type.generate_random_params()
        if task_seed is not None:
            params["seed"] = task_seed
    if not isinstance(params, dict):
        raise ValueError("task parameters must be a JSON object")
    return task_type(params)

def _required_apps(task: Any) -> tuple[type, ...]:
    required = []
    for app_name in task.app_names:
        app = device_setup.get_app_mapping(app_name)
        if app is None:
            raise RuntimeError(f"no AndroidWorld app setup maps {app_name!r}")
        if app not in required:
            required.append(app)
    return tuple(required)


def _cleanup_owned_session(
    proxy: AppiumAuditProxy, normalized: dict[str, Any], project: Path,
    recovery_seconds: float,
) -> dict[str, Any]:
    """Agent proof and Harness recovery are separate, immutable outcomes."""
    recovery_end = time.monotonic() + recovery_seconds
    proxy.wait_for_idle(min(120.0, recovery_seconds))
    audit = proxy.audit()
    proofs = {
        call["sessionCleanup"]["sessionIdSha256"]
        for call in normalized.get("toolCalls", []) if "sessionCleanup" in call
    }
    created = set(audit["createdSessionHashes"])
    deleted = set(audit["deletedSessionHashes"])
    if not created and not audit.get("pendingRequestCount") and not audit.get("unknownCreationOutcomeCount"):
        return {"status": "not_created", "attribution": "none"}
    try:
        remaining = max(0.01, recovery_end - time.monotonic())
        with RecoveryRuntime(project, remaining) as runtime:
            recovery = proxy.reclaim_owned(
                runtime.execute, timeout_seconds=max(0.01, recovery_end - time.monotonic())
            )
    except Exception as exc:
        return {"status": "unknown", "attribution": "unknown",
                "error": type(exc).__name__, "createdSessionHashes": sorted(created)}
    sessions = recovery.get("sessions", [])
    if (
        len(created) == 1 and proofs == created == deleted
        and recovery.get("reclaimedSessionCount") == 0
        and recovery.get("pendingRequestCount") == 0
        and recovery.get("unknownCreationOutcomeCount") == 0
        and len(sessions) == 1
        and sessions[0].get("sessionHash") in created
        and sessions[0].get("alreadyAbsent") is True
        and sessions[0].get("absentVerified") is True
    ):
        return {"status": "closed", "sessionIdSha256": next(iter(created)),
                "attribution": "agent", "agentQuitReturned": True,
                "verification": recovery}
    return {**recovery, "attribution": (
        "harness" if recovery.get("status") == "harness_reclaimed" else "unknown"
    )}


def run(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    started_at = time.time()
    time_budget = episode_time_budget(args.expected_max_steps)
    record: dict[str, Any] = {
        "schemaVersion": 3,
        "startedAtUnix": started_at,
        "androidWorld": {
            "revision": ANDROID_WORLD_REVISION,
            "packageVersion": importlib.metadata.version("android-world"),
        },
        "amkernel": {"version": args.expected_amkernel_version, "tool": "python_exec"},
        "target": {
            "serial": args.device_serial,
            "consolePort": args.console_port,
            "grpcPort": args.grpc_port,
        },
        "task": {"name": args.task, "seed": args.task_seed},
        "protocol": {
            "promptTemplateSha256": PROMPT_TEMPLATE_SHA256,
            "timeBudget": TIME_BUDGET_PROTOCOL,
            "mcpRequestTimeoutMs": MCP_REQUEST_TIMEOUT_MS,
            "sessionCreationTimeoutSeconds": SESSION_CREATION_TIMEOUT_SECONDS,
            "pythonExecCallAdvisory": args.python_exec_call_advisory,
            "harnessRevision": HARNESS_REVISION,
            "maxAppiumSessions": 1,
            "readinessIdentitySha256": args.expected_readiness_sha256,
            "stepBudget": STEP_BUDGET_PROTOCOL,
            "answerSubmission": ANSWER_SUBMISSION_PROTOCOL,
        },
        "stages": [],
        "timeBudget": time_budget,
        "agent": None,
        "officialReward": None,
        "budget": None,
        "stepBudget": None,
        "invalidReason": None,
        "cleanup": {"agentSession": {"status": "not_created"}},
        "error": None,
    }
    env = None
    task = None
    task_initialization_started = False
    environment_creation_started = False
    appium_baseline: list[str] | None = None
    stage = "infrastructure"
    stage_entry: dict[str, Any] | None = None

    def enter_stage(name: str) -> None:
        nonlocal stage, stage_entry
        now = time.time()
        if stage_entry is not None and "completedAtUnix" not in stage_entry:
            stage_entry["completedAtUnix"] = now
            stage_entry["durationSeconds"] = round(now - stage_entry["startedAtUnix"], 3)
            if stage_entry["status"] == "running":
                stage_entry["status"] = "completed"
        stage = name
        stage_entry = {"name": name, "startedAtUnix": now, "status": "running"}
        record["stages"].append(stage_entry)

    try:
        enter_stage("infrastructure")
        readiness = json.loads(Path(args.readiness_report).read_text())
        readiness_payload = {
            key: value for key, value in readiness.items() if key != "identitySha256"
        }
        if not readiness.get("qualified"):
            raise RuntimeError("device readiness report is not qualified")
        if readiness.get("identitySha256") != _sha256(readiness_payload):
            raise ValueError("device readiness report identity is invalid")
        if readiness.get("identitySha256") != args.expected_readiness_sha256:
            raise ValueError("device readiness identity does not match campaign")
        artifacts = artifact_identity(Path(args.artifact_root))
        if artifacts != readiness.get("environmentArtifacts"):
            raise ValueError("local environment artifacts do not match readiness")
        record["protocol"]["environmentArtifacts"] = artifacts
        _request_json(args.appium_url.rstrip("/") + "/status")
        appium_baseline = _appium_session_hashes(
            args.appium_url, args.adb_path, args.device_serial
        )
        if appium_baseline:
            raise RuntimeError("Appium has pre-existing sessions")

        enter_stage("protocol")
        task = _task(args.task, args.params, args.task_seed)
        params_sha256 = _sha256(task.params)
        if args.expected_params_sha256 is not None and params_sha256 != args.expected_params_sha256:
            raise ValueError(f"generated task parameters do not match manifest: {params_sha256}")
        max_steps = suite_utils._allocate_step_budget(task.complexity)
        if max_steps <= 0 or max_steps != args.expected_max_steps:
            raise ValueError("task step budget does not match frozen manifest")
        # Official initialization can reword dates in task.params. Provenance
        # records the frozen input, while the live task keeps official semantics.
        frozen_params = _json_safe(task.params)
        required_apps = _required_apps(task)

        enter_stage("infrastructure")
        environment_creation_started = True
        env = load_environment(
            artifact_root=Path(args.artifact_root),
            console_port=args.console_port,
            freeze_datetime=True,
            adb_path=args.adb_path,
            grpc_port=args.grpc_port,
        )
        record["preparation"] = {
            "mode": "prequalified",
            "readinessIdentitySha256": args.expected_readiness_sha256,
            "apps": [app.app_name for app in required_apps],
        }
        env.reset(go_home=True)
        record["preparation"]["sharedAssets"] = restore_shared_assets(env, Path(args.artifact_root), task.app_names)
        enter_stage("task_initialization")
        task_initialization_started = True
        with strict_snapshot_restores():
            task.initialize_task(env)
        record["task"] = {
            "name": task.name,
            "params": frozen_params,
            "paramsSha256": params_sha256,
            "goal": task.goal,
            "complexity": task.complexity,
        }

        enter_stage("agent")
        action_gate = ActionGate()
        deadlines = EpisodeDeadlines(
            time_budget["businessSeconds"], time_budget["cleanupWindowSeconds"],
            time_budget["terminationGraceSeconds"],
        )
        with AppiumAuditProxy(
            args.appium_url, action_gate=action_gate, expected_udid=args.device_serial,
            deadlines=deadlines,
        ) as appium_proxy:
            adapter = AppiumSteppedAgent(
                env=env,
                run_agent=lambda: _run_agent(
                    project=project,
                    sandbox_profile=Path(args.sandbox_profile).resolve(),
                    output_dir=output_dir,
                    prompt=_agent_prompt(
                        task.goal,
                        appium_proxy.url,
                        args.device_serial,
                        args.python_exec_call_advisory,
                        max_steps=max_steps,
                    ),
                    omp=args.omp,
                    model=args.model,
                    deadlines=deadlines,
                    action_gate=action_gate,
                ),
                action_gate=action_gate,
                deadlines=deadlines,
            )
            reference_episode = None
            try:
                reference_episode = episode_runner.run_episode(
                    goal=task.goal,
                    agent=adapter,
                    max_n_steps=max_steps,
                    start_on_home_screen=task.start_on_home_screen,
                )
            except AgentTerminated:
                # Reference loop has no non-success termination result. Retain
                # the partial attempt without declaring Agent completion.
                pass
            finally:
                try:
                    record["agent"] = adapter.finish()
                finally:
                    try:
                        normalized = (record.get("agent") or {}).get("normalized", {})
                        record["cleanup"]["agentSession"] = _cleanup_owned_session(
                            appium_proxy, normalized, project,
                            time_budget["recoveryWindowSeconds"],
                        )
                    finally:
                        record["appiumSessionAudit"] = appium_proxy.audit()
                        steps = adapter.reference_step_count
                        done = reference_episode.done if reference_episode is not None else False
                        record["stepBudget"] = {
                            "protocol": STEP_BUDGET_PROTOCOL,
                            "maxSteps": max_steps,
                            "referenceStepsExecuted": steps,
                            "agentIndicatedDone": done,
                            "exhausted": steps == max_steps and not done,
                            **action_gate.snapshot(),
                        }
        if (
            record["agent"]["exitCode"] != 0
            and record["agent"]["normalized"]["provider"] is None
            and record["agent"]["normalized"]["toolCalls"] == []
        ):
            raise RuntimeError("Agent process exited before producing an event stream")

        enter_stage("agent_protocol")
        normalized = record["agent"]["normalized"]
        expected_provider, expected_model = args.model.split("/", 1)
        if normalized.get("provider") != expected_provider or normalized.get("model") != expected_model:
            raise ValueError("observed Agent provider/model does not match frozen protocol")
        if normalized.get("parseErrors") != 0:
            raise ValueError("Agent event stream contains parse errors")
        session_audit = record["appiumSessionAudit"]
        if session_audit["errors"]:
            raise ValueError(f"Appium session audit failed: {session_audit['errors']}")
        if session_audit["createdSessionCount"] > 1:
            raise ValueError("Agent created more than one Appium session")
        violations = _agent_protocol_violations(normalized)
        if violations:
            raise ValueError(f"Agent violated the frozen tool protocol: {violations}")
        python_exec_calls = sum(
            call.get("target") == "xd://mcp__amkernel_python_exec"
            and call.get("tool") == "write"
            for call in normalized["toolCalls"]
        )
        record["budget"] = {
            "pythonExecCalls": python_exec_calls,
            "advisory": args.python_exec_call_advisory,
            "exceededAdvisory": python_exec_calls > args.python_exec_call_advisory,
            "affectsOfficialReward": False,
        }
        submission_path = output_dir / "raw-private" / "business-submission.json"
        submission_evidence = record["agent"]["answerSubmission"]
        submission_bytes = submission_path.read_bytes()
        if hashlib.sha256(submission_bytes).hexdigest() != submission_evidence["sha256"]:
            raise ValueError("business submission evidence changed")
        archived_submission = json.loads(submission_bytes)
        submission = parse_submission(archived_submission["rawText"])
        if submission != archived_submission:
            raise ValueError("business submission diagnostics do not match raw input")
        record["agentAnswer"] = {
            "validContract": submission["validContract"],
            "reason": submission["reason"],
            "taskOutcomeType": submission["taskOutcomeType"],
            "sha256": submission["sha256"],
            "rawSubmission": {"path": submission_evidence["path"], "sha256": submission_evidence["sha256"]},
        }
        if isinstance(task, information_retrieval.InformationRetrieval) and submission["validContract"]:
            env.interaction_cache = submission["answer"]

        enter_stage("evaluator")
        evaluator_started = time.time()
        record["officialReward"] = task.is_successful(env)
        record["evaluator"] = {
            "implementation": "android_world.task_eval.is_successful",
            "durationSeconds": round(time.time() - evaluator_started, 3),
        }

        termination = record["agent"]["termination"]["reason"]
        if termination in {"unknown_termination", "forced_termination"}:
            record["invalidReason"] = "invalid_agent"
            record["error"] = {
                "type": "AgentTerminated",
                "message": termination,
            }
    except Exception as exc:
        if stage_entry is not None:
            stage_entry["status"] = "failed"
        record["error"] = {
            "type": type(exc).__name__,
            "message": str(exc)[:4096],
            "traceback": "".join(traceback.format_exception(exc))[-8192:],
        }
        record["invalidReason"] = {
            "protocol": "invalid_protocol",
            "infrastructure": "invalid_infrastructure",
            "task_initialization": "invalid_setup",
            "agent_protocol": "invalid_protocol",
            "evaluator": "invalid_evaluator",
            "session_cleanup_verification": "invalid_protocol",
        }.get(stage, "invalid_agent")
    finally:
        enter_stage("task_teardown")
        if task_initialization_started and task is not None and env is not None:
            try:
                with strict_snapshot_restores():
                    task.tear_down(env)
                record["cleanup"]["taskTearDown"] = "completed"
            except Exception as exc:
                record["cleanup"]["taskTearDown"] = f"failed:{type(exc).__name__}"
        else:
            record["cleanup"]["taskTearDown"] = "not_applicable"
        enter_stage("environment_close")
        if env is not None:
            try:
                close_environment(env)
                record["cleanup"]["environment"] = "closed"
            except Exception as exc:
                record["cleanup"]["environment"] = f"failed:{type(exc).__name__}"
        else:
            record["cleanup"]["environment"] = "unknown" if environment_creation_started else "not_created"
        if appium_baseline is not None:
            try:
                remaining_sessions = _appium_session_hashes(
                    args.appium_url, args.adb_path, args.device_serial
                )
            except Exception:
                cleanup = record["cleanup"]["agentSession"]
                cleanup["verificationStatus"] = "unknown"
                if cleanup["status"] == "closed":
                    cleanup["status"] = "unknown"
            else:
                if remaining_sessions != appium_baseline:
                    cleanup = record["cleanup"]["agentSession"]
                    cleanup["status"] = "leaked"
                    cleanup["remainingSessionHashes"] = remaining_sessions
                else:
                    record["cleanup"]["agentSession"]["verificationStatus"] = "absent"
        enter_stage("result_write")
        record["completedAtUnix"] = time.time()
        stage_entry["completedAtUnix"] = record["completedAtUnix"]
        stage_entry["durationSeconds"] = round(
            stage_entry["completedAtUnix"] - stage_entry["startedAtUnix"], 3
        )
        stage_entry["status"] = "completed"
        result_path = output_dir / "result.json"
        temporary_path = output_dir / "result.json.tmp"
        temporary_path.write_bytes(
            json.dumps(_json_safe(record), indent=2, sort_keys=True).encode() + b"\n"
        )
        os.replace(temporary_path, result_path)
    return 0 if record["error"] is None else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one AndroidWorld task through OMP and AMKernel")
    parser.add_argument("--project", required=True)
    parser.add_argument("--artifact-root", required=True, help="project containing verified frozen environment artifacts")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--params", help="fixed task parameter JSON")
    parser.add_argument("--model", required=True)
    parser.add_argument("--expected-amkernel-version", required=True)
    parser.add_argument("--sandbox-profile", required=True)
    parser.add_argument("--readiness-report", required=True)
    parser.add_argument("--expected-readiness-sha256", required=True)
    parser.add_argument("--omp", default="omp")
    parser.add_argument("--task-seed", type=int, help="fixed seed used to generate task parameters")
    parser.add_argument(
        "--python-exec-call-advisory",
        type=int,
        default=PYTHON_EXEC_CALL_ADVISORY,
    )
    parser.add_argument("--expected-params-sha256", help="manifest parameter digest")
    parser.add_argument("--expected-max-steps", type=int, required=True)
    parser.add_argument("--appium-url", default="http://127.0.0.1:4723")
    parser.add_argument("--device-serial", default="emulator-5554")
    parser.add_argument("--console-port", type=int, default=5554)
    parser.add_argument("--grpc-port", type=int, default=8554)
    parser.add_argument("--adb-path", default=str(DEFAULT_ADB))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
