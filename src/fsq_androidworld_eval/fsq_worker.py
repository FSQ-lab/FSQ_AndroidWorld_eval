"""Private subprocess entry for a complete, unmodified FSQ dynamic execution.

Import this module safely without FSQ installed. The isolated worker interpreter
must have FSQ and its native dependencies installed (or its checkout on the
worker-only PYTHONPATH), plus this evaluator package. No discovery, adb, Appium,
provider fallback or model substitution is performed here.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .fsq_native import NativeDeadlineExceeded, NativeDispatchBudget, build_native_harness_factory

ANSWER_SOURCE = "agent_runtime.runner.tool_output.summary"
REQUIRED_FIELDS = frozenset({"schemaVersion", "settingsPath", "workspace", "outputDir", "serial", "taskId", "goal", "appId", "maxActions", "businessDeadlineMonotonic", "provider", "model"})
OPTIONAL_FIELDS = frozenset({"userConfigRoot", "runtimeProfile"})


def select_main_answer(task_result: dict[str, Any], *, validate_output: Callable[[Any], Any] | None = None) -> dict[str, Any]:
    """Only a single normal main runner's parsed task_run_v1 summary qualifies."""
    def reject(status: str, reason: str) -> dict[str, Any]:
        return {"status": status, "source": ANSWER_SOURCE, "reason": reason}
    if not isinstance(task_result, dict):
        return reject("invalid", "task_result is not an object")
    steps = task_result.get("steps")
    if not isinstance(steps, list):
        return reject("invalid", "task_result.steps is not a list")
    runners = [step for step in steps if isinstance(step, dict) and step.get("tool_name") == "agent_runtime.runner"]
    if not runners:
        return reject("missing", "No exact main runner step")
    if len(runners) != 1:
        return reject("ambiguous", "Multiple exact main runner steps")
    runner = runners[0]
    if runner.get("status") != "success":
        return reject("failed", "Main runner did not succeed")
    output = runner.get("tool_output")
    if not isinstance(output, dict) or output.get("schema_version") != "task_run_v1":
        return reject("invalid", "Main runner output is not a parsed task_run_v1 object")
    summary = output.get("summary")
    if not isinstance(summary, str):
        return reject("invalid", "Main runner summary is not a string")
    if validate_output is None:
        from fsq_agent.models import AgentFinalOutput
        validate_output = AgentFinalOutput.model_validate
    try:
        validate_output(output)
    except Exception:
        return reject("invalid", "Main runner output does not validate as AgentFinalOutput")
    return {"status": "valid", "summary": summary, "businessStatus": output["status"], "source": ANSWER_SOURCE, "reason": "One successful exact main runner with a validated task_run_v1 summary; redacted and reserialized, not wire text"}


def validate_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Worker request must be an object")
    if set(value) - REQUIRED_FIELDS - OPTIONAL_FIELDS or REQUIRED_FIELDS - set(value):
        raise ValueError("Worker request fields do not match schemaVersion 1")
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        raise ValueError("Unsupported worker request schema")
    for field in ("settingsPath", "workspace", "outputDir", "serial", "taskId", "goal", "provider", "model"):
        if not isinstance(value[field], str) or not value[field].strip() or "\x00" in value[field]:
            raise ValueError("Worker string field invalid: " + field)
    if value["serial"] != value["serial"].strip():
        raise ValueError("Serial must be exact, with no surrounding whitespace")
    if value["provider"] != "github_copilot" or value["model"] != "gpt-6.1-sol":
        raise ValueError("Unsupported requested native provider/model")
    if value["appId"] is not None and (not isinstance(value["appId"], str) or not value["appId"].strip()):
        raise ValueError("appId must be null or a nonempty string")
    NativeDispatchBudget(value["maxActions"], value["businessDeadlineMonotonic"])
    if "userConfigRoot" in value and (not isinstance(value["userConfigRoot"], str) or not value["userConfigRoot"].strip()):
        raise ValueError("userConfigRoot must be an explicit nonempty path")
    if "runtimeProfile" in value:
        profile = value["runtimeProfile"]
        if not isinstance(profile, dict) or set(profile) - {"maxTurns", "reasoningEffort", "tracingEnabled"}:
            raise ValueError("Unsupported explicit runtime profile")
        if "maxTurns" in profile and (type(profile["maxTurns"]) is not int or profile["maxTurns"] <= 0):
            raise ValueError("maxTurns must be positive")
        if "reasoningEffort" in profile and profile["reasoningEffort"] not in {"low", "mid", "high"}:
            raise ValueError("Invalid reasoningEffort")
        if "tracingEnabled" in profile and type(profile["tracingEnabled"]) is not bool:
            raise ValueError("tracingEnabled must be boolean")
    return dict(value)


@dataclass(frozen=True)
class NativeBindings:
    """Data-only injection seam for offline tests; production loads native exports."""
    load_settings: Callable[..., Any]
    agent_type: Any
    runtime_factory: Callable[..., Any]
    execution_service_type: Any
    execution_request_type: Any
    task_type: Any
    harness_factory_builder: Callable[..., Any]
    source_root: Path | None = None
    validate_output: Callable[[Any], Any] | None = None


def load_native_bindings() -> NativeBindings:
    import fsq_agent
    from fsq_agent.adapters.coding_agent import create_coding_agent_runtime
    from fsq_agent.agent import FsqAgent
    from fsq_agent.config import load_workspace_platform_settings
    from fsq_agent.execution.dynamic import DynamicExecutionRequest, DynamicExecutionService
    from fsq_agent.models import AgentFinalOutput, Task
    return NativeBindings(load_workspace_platform_settings, FsqAgent, create_coding_agent_runtime, DynamicExecutionService,
                          DynamicExecutionRequest, Task, build_native_harness_factory,
                          Path(fsq_agent.__file__).resolve().parent.parent, AgentFinalOutput.model_validate)


def _private_json(path: Path, payload: Any) -> dict[str, Any]:
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
    finally:
        os.close(fd)
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(data).hexdigest(), "sizeBytes": len(data), "visibility": "evaluator_private"}


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _configure_settings(request: dict[str, Any], bindings: NativeBindings) -> Any:
    workspace = Path(request["workspace"]).expanduser().resolve()
    output = Path(request["outputDir"]).expanduser().resolve()
    if bindings.source_root is not None:
        source = bindings.source_root.resolve()
        if _inside(workspace, source) or _inside(source, workspace) or _inside(output, source) or _inside(source, output):
            raise ValueError("Worker-owned paths must not overlap the FSQ source checkout")
    config_path = (workspace / ".fsq" / "config" / "config.android.yaml").resolve()
    if Path(request["settingsPath"]).expanduser().resolve() != config_path:
        raise ValueError("settingsPath must identify the canonical owned Android workspace configuration")
    kwargs: dict[str, Any] = {}
    if "userConfigRoot" in request:
        kwargs["user_config_root"] = Path(request["userConfigRoot"]).expanduser().resolve()
    settings = bindings.load_settings(workspace, "android", **kwargs)
    if settings.harness.platform != "android" or settings.harness.android.backend != "uiautomator2":
        raise ValueError("Worker requires the native Android uiautomator2 Harness")
    settings.harness.android.serial = request["serial"]
    if request["appId"] is not None and settings.harness.android.app_id != request["appId"]:
        raise ValueError("Requested appId does not match the canonical native workspace target")
    # Preserve the official config's Skill, knowledge, prompt and secret objects.
    profile = request.get("runtimeProfile", {})
    if "maxTurns" in profile:
        settings.agent_runtime.max_turns = profile["maxTurns"]
    if "reasoningEffort" in profile:
        settings.agent_runtime.reasoning_effort = profile["reasoningEffort"]
    if "tracingEnabled" in profile:
        settings.agent_runtime.tracing_enabled = profile["tracingEnabled"]
    return settings


async def execute_worker(value: Any, *, bindings: NativeBindings | None = None, clock: Callable[[], float] = time.monotonic) -> dict[str, Any]:
    request = validate_request(value)
    # Import and configuration failures are reported without constructing a driver.
    output = Path(request["outputDir"]).expanduser().resolve()
    budget = NativeDispatchBudget(request["maxActions"], request["businessDeadlineMonotonic"], clock=clock)
    response: dict[str, Any] = {"schemaVersion": 1, "status": "failed", "taskId": request["taskId"],
        "mainAnswer": {"status": "missing", "source": ANSWER_SOURCE, "reason": "Complete FSQ execution has not returned"},
        "fsq": {"taskResult": None, "verification": None, "status": None},
        "nativeTarget": {"requestedProvider": request["provider"], "requestedModel": request["model"], "effectiveProvider": None,
                         "effectiveModel": None, "serial": request["serial"], "authentication": "native_provider_owned_not_asserted"}}
    try:
        budget.check_deadline()
        native = bindings if bindings is not None else load_native_bindings()
        settings = _configure_settings(request, native)
        response["nativeTarget"].update({"effectiveProvider": settings.agent_runtime.provider, "effectiveModel": settings.agent_runtime.model,
            "backend": settings.harness.android.backend, "appId": settings.harness.android.app_id,
            "maxTurns": settings.agent_runtime.max_turns, "reasoningEffort": settings.agent_runtime.reasoning_effort,
            "tracingEnabled": settings.agent_runtime.tracing_enabled})
        if settings.agent_runtime.provider != request["provider"] or settings.agent_runtime.model != request["model"]:
            response["error"] = {"type": "NativeTargetMismatch", "reason": "effective_provider_model_mismatch"}
            raise ValueError("Effective native provider/model mismatch")
        response["fsq"]["nativeRunsRoot"] = {"path": str(settings.output.runs_dir.resolve()), "visibility": "evaluator_private"}
        output.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(output, 0o700)
        workspace = Path(request["workspace"]).expanduser().resolve()
        workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(workspace, 0o700)
        budget.journal = output / "native-action-audit.jsonl"
        harness_factory = native.harness_factory_builder(settings, budget)
        agent = native.agent_type.from_settings(settings, runtime_factory=native.runtime_factory, harness_factory=harness_factory)
        task = native.task_type(id=request["taskId"], name=request["goal"], description=request["goal"],
                               planning_reference_kind="goal", planning_reference_text=request["goal"])
        service = native.execution_service_type(agent=agent)
        result = await service.execute(native.execution_request_type(task=task, settings=settings, record=False, cancellation_check=budget.check_deadline))
        task_result = result.task_result.model_dump(mode="json")
        # This is the observable full-service return, not a main-final timestamp.
        # Preserve native verification and all TaskResult fields verbatim.
        verification = task_result.get("verification")
        budget.receipt({"event": "native_execution_returned", "taskId": request["taskId"],
                        "nativeTaskId": task_result.get("task_id"), "taskStatus": task_result.get("status"),
                        "verificationObserved": isinstance(verification, dict),
                        "verificationStatus": verification.get("status") if isinstance(verification, dict) else None})
        response["fsq"] = {"taskResult": _private_json(output / "fsq-task-result.private.json", task_result),
                           "verification": _private_json(output / "fsq-verification.private.json", task_result["verification"]),
                           "status": task_result["status"], "completeDynamicExecutionReturned": True,
                           "nativeRunsRoot": {"path": str(settings.output.runs_dir.resolve()), "visibility": "evaluator_private"},
                           "nativeReport": {"path": task_result["report"]["path"], "visibility": "evaluator_private"}}
        response["mainAnswer"] = select_main_answer(task_result, validate_output=native.validate_output)
        budget.check_deadline()
        response["status"] = "completed"
    except BaseException as exc:
        # Do not publish arbitrary exception text: provider failures can contain
        # credentials, observations or private goals. Full native artifacts remain private.
        deadline = isinstance(exc, NativeDeadlineExceeded) or clock() >= budget.deadline
        response["status"] = "deadline" if deadline else "failed"
        response.setdefault("error", {"type": type(exc).__name__, "reason": "business_deadline" if deadline else "native_worker_failure"})
    snapshot = budget.snapshot()
    response["actionBudget"] = snapshot
    response["terminationReason"] = "deadline" if response["status"] == "deadline" else "action_budget" if any(event.get("reason") == "action_budget" for event in snapshot["events"]) else "native_execution_returned" if response["fsq"].get("completeDynamicExecutionReturned") else "native_worker_failure"
    response["cleanup"] = {"closeReceipts": [event for event in snapshot["events"] if event["event"].startswith("close_")],
                           "deviceRestored": False, "workerProcessExitRequiredBeforeOracle": True,
                           "note": "FSQ owns Harness disposal; native u2 driver close is a no-op and does not restore device state. In-flight synchronous calls/construction require supervisor process-group termination."}
    if budget.journal is not None and budget.journal.exists():
        data = budget.journal.read_bytes()
        response["actionAudit"] = {"path": str(budget.journal), "sha256": hashlib.sha256(data).hexdigest(), "sizeBytes": len(data), "visibility": "evaluator_private"}
    return response


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        response = asyncio.run(execute_worker(request))
    except BaseException as exc:
        response = {"schemaVersion": 1, "status": "failed", "mainAnswer": {"status": "missing", "source": ANSWER_SOURCE, "reason": "Worker request or startup failed"},
                    "error": {"type": type(exc).__name__, "reason": "invalid_request_or_startup"},
                    "fsq": {"taskResult": None, "verification": None, "status": None},
                    "actionBudget": None, "actionAudit": None, "nativeTarget": None,
                    "terminationReason": "invalid_request_or_startup",
                    "cleanup": {"closeReceipts": [], "deviceRestored": False, "workerProcessExitRequiredBeforeOracle": True}}
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _private_json(args.output, response)
    return 0 if response["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
