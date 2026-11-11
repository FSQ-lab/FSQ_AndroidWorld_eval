# FSQ / Android World native interface receipt

Scope: static source and actual local dependency/import identity; no Android access, business Agent execution, tests, or FSQ source edits. Model authentication remains pending; this is NOT a successful model-call receipt.

## Runtime identity (observed)

- Checkout: /Users/qunmi/Documents/FSQ_LAB/FSQ
- main commit: 7e3f0793f3962ef2d8cc92f06310326c9077ce0d; clean at scope check.
- Python: /Users/qunmi/Documents/FSQ_LAB/FSQ/.venv/bin/python; 3.11.16.
- Import origin: checkout/fsq_agent (editable install).
- pyproject version: 0.1.2; installed fsq-agent metadata: 0.1.0a1 (do not identify the evaluated build solely by this metadata).
- Installed: uiautomator2 3.5.2, openai 2.34.0, google-genai 2.21.0, pydantic 2.13.3, httpx 0.28.1.
- fsq / fsq-agent console entry: fsq_agent.adapters.cli:main.
- Native target: provider=github_copilot, request model=gpt-6.1-sol. Provider prefix github-copilot/ is not part of the native wire model id.
- Observed after the original native authentication process ended: provider remains deepseek/deepseek-flash, both FSQ-owned Copilot credential files are absent. Process fsq-copilot-auth-20261110 exited 4 with the generic message "GitHub Copilot configuration failed." Underlying cause and authenticated model-discovery outcome are unknown. No new authentication flow or target inference was started. Previous configuration is recoverable; private backup location/content intentionally excluded. Failure receipt: /tmp/fsq-copilot-model-receipt-20261110-7e3f079-a41d.json.

## Native per-episode composition (illustrative, not executed)

```python
from fsq_agent.agent import FsqAgent
from fsq_agent.adapters.coding_agent import create_coding_agent_runtime
from fsq_agent.ai_services import build_ai_assertion_evaluator
from fsq_agent.config import load_workspace_platform_settings
from fsq_agent.core import ArtifactStore, HarnessFactory
from fsq_agent.execution import DynamicExecutionRequest, DynamicExecutionService
from fsq_agent.models import Task

# workspace_root is the exact already-registered Android workspace root.
settings = load_workspace_platform_settings(workspace_root, "android")
settings.harness.android.serial = exact_serial

def make_episode_harness(run_id):
    native = HarnessFactory().create_harness(
        platform=settings.harness.platform,
        harness_settings=settings.harness,
        artifact_store=ArtifactStore(
            settings.output.runs_dir / run_id,
            secret_values=tuple(settings.runtime_secrets.private_values().values()),
        ),
        ai_assertion_evaluator=build_ai_assertion_evaluator(settings),
        runtime_secret_settings=settings.runtime_secrets,
        app_id=settings.harness.android.app_id,
        serial=exact_serial,
    )
    # Wrap native here with the evaluation-owned gate; delegate the complete
    # HarnessInterface, including action_space, evidence scope/capture,
    # context, error classification, and close. Do not hide/change tools.
    return wrap_native_harness(native)

agent = FsqAgent.from_settings(
    settings,
    runtime_factory=create_coding_agent_runtime,
    harness_factory=make_episode_harness,
)
task = Task(
    id=episode_id, name=goal, description=goal,
    planning_reference_kind="goal", planning_reference_text=goal,
)
execution = await DynamicExecutionService(agent=agent).execute(
    DynamicExecutionRequest(task=task, settings=settings, record=False)
)
result = execution.task_result
```

`wrap_native_harness` denotes the adapter owned by the evaluation project, not a supplied FSQ implementation. This composition must not be executed before model readiness and device ownership approval. `record=False` disables Case recording/publication, not planning, execution, independent verification, Run evidence, or reporting.

Sources: agent/_core.py:43-64; adapters/coding_agent/__init__.py:16-32; adapters/coding_agent/_runtime.py:922-932; harnesses/_factory.py:71-103; drivers/_factory.py:33-35; execution/dynamic.py:35-59,136-175 (all under fsq_agent/).

Serial: private runtime setting, not a persisted workspace field. Native DriverFactory uses explicit serial if supplied, otherwise settings.serial. Control Plane converts targetId to a deep-copied settings.harness.android.serial at adapters/control_plane/_execution.py:84-111; DynamicExecutionRequest has no targetId field.

## Answer mapping agreed with evaluation owner

For this AW profile, the formal business answer is the MAIN RUNNER summary, not verifier summary or a trajectory-derived guess.

- Select result.steps where tool_name == "agent_runtime.runner"; normal default runtime emits exactly one runner step plus optional pre-plan steps. Require exactly one; 0 => missing, >1 => ambiguous, never choose an arbitrary last step.
- Require runner.status == "success" and a dictionary tool_output validating as AgentFinalOutput with schema_version == "task_run_v1". summary is a required str, but the schema has no nonempty constraint; empty/whitespace is an empty answer, not permission to infer one.
- Use tool_output["summary"] verbatim as the answer payload string, subject to FSQ's already-applied runtime-secret redaction. Preserve original string; do not strip/parse/extract a guessed answer.
- Preserve payload.status separately: runner StepResult success means successful call/parse, NOT business success. A valid payload may itself be failed/inconclusive; the profile owns whether to submit that actual summary, never fabricate a replacement.
- Failed runner steps carry failure metadata that need not contain summary. Treat as execution failure/missing answer; do not fall back to verifier, top-level Run summary, events, or pre-plan.
- There is no independent answer/final_answer field or answer-submission tool in task_run_v1. No FSQ source change is necessary to read summary; AW-specific action/answer submission must be implemented in the evaluation project according to its real API.
- This is a current-commit contract, not a future-version compatibility promise. Model wire original bytes are not retained by this field: output is parsed/re-serialized and runtime secrets may be replaced by ***.

Sources: models/_agent_io.py:39-50; adapters/coding_agent/_runtime.py:365-445,1044-1068; agent/_core.py:103-110; agent/_verifier.py:18-22,77-95; execution/dynamic.py:118-123. Verifier is a separate step, not an overwrite of the runner step.

## Android state-changing capability gate

Native method: harnesses/_android.py:90-112, AndroidHarness.invoke_action(step, context). Place evaluation gate BEFORE forwarding to native.invoke_action. Runner normalizes aliases, validates params and resolves runtime secrets before this call (core/runner/_runner.py:302-314).

Eight explicit mutating capabilities, defined in drivers/android/_uiautomator2.py:94-181:

- launch_app -> device.app_start
- kill_app -> device.app_stop
- tap_on -> selector.click
- tap_at -> device.click
- long_press_on -> selector.long_click
- input_text -> selector.click; optional selector.clear_text; selector.set_text
- press_key -> device.press
- swipe -> device.swipe

Reserve the episode-wide budget before each accepted mutation attempt; retain the debit on missing target, backend failure, or partial mutation. Count setup/teardown too, not only kind=action. One input_text call is one capability attempt, not one low-level u2 operation. Same-turn multiple tools each pass this gate; use one shared atomic reservation. Rejected malformed calls before invoke_action are outside this attempted-driver-call counting policy.

This gate is not an all-u2/network security boundary. Driver construction u2.connect(serial), backend implicit service startup, observation/context backend effects, external processes, or direct driver/device callers do not pass it. Constructor connection: drivers/android/_uiautomator2.py:72-78,341-349. Before-action evidence/context runs before invoke_action. Ordinary gate failure does not force loop exit: failure is returned to model; the exhausted gate must remain closed and the evaluation layer must separately record budget termination.

## Lifecycle and scoring

kill_app is a model-issued tool BEFORE the accepted main Agent final, not an after-final hook. Same response tool calls take priority over final text (agent_engine/_runner.py:155-174). Android Skill asks launch, collect final evidence, kill (resources/skills/android-harness.md:7-9). AndroidHarness.after_action is a no-op (:120-126); driver.close is a no-op (:77-78). Runtime closes harness before returning the runner step and before independent verification (_runtime.py:416-445,805-809; agent/_core.py:103-110).

A kill-before checkpoint is not a terminal score. The evaluation owner has now confirmed the profile policy: retain the original Skill, kill_app behavior, and independent internal verification, then perform official Android World scoring exactly once after FSQ returns. No kill suppression, fake success, deferred teardown, reflection, or monkeypatch is requested or supplied. This profile intentionally does not promise a pre-teardown final grade.

## Workspace fields

Canonical file: <workspace_root>/.fsq/config/config.android.yaml.
WorkspaceConfig fields: version=2, name, root_path, platform=android, target={app_id: <package>}, optional env={secret_name: value}. Do not expose env values.
Backend/policy are package-owned: config/config.android.yaml -> agent_runtime.max_turns=100, reasoning_effort=mid, tracing_enabled=true; harness.platform=android; harness.android.backend=uiautomator2; execution.post_action_delay_seconds.platform=1.0/common=0.0.
Provider/model/credentials are user-owned under ~/.fsq, not workspace/env inference overrides. Native Copilot uses fixed plan-dependent api[.business|.enterprise].githubcopilot.com endpoints and Responses protocol; exact runtime support still awaits live authentication/discovery/call.
Sources: models/_settings.py:91-112,358-369,471-479; config/_loader.py:133-169; config/config.android.yaml:1-14; providers/_github_copilot.py:32-51,126-140.

No FSQ development-file modifications are authorized in this round; repository /spec-driven gate remains in effect. Existing interfaces are sufficient for the currently agreed evaluation-owned thin adapter; no upstream implementation is supplied or required by that contract. Native authentication failed without activating Copilot; target live invocation remains blocked on new operator-authorized FSQ-owned authentication. Evaluation implementation and official scoring stay with the evaluation owner.
