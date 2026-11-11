# Native FSQ r4 formal run — complete coverage, NOT qualified

The original service ended naturally with exit **2**. Original report: `qualified=false`, `haltReason=null`. This is **not an all-116-valid score**. No task, evaluator, permission repair or campaign was rerun; original evidence is unchanged.

## Original evidence and time

- [Original formal report](../next-stage-plan/execution/run/report.json), byte SHA-256 `9bde5eb175cee2b6a9ac9a8d2827b7740b6d885c059caad5876a9dcfb1b59730`.
- Original report internal `identitySha256`: `ffe0e4175aa39c3975ef3bc307d7f1dd714cc21ebbd2d08144c1f75451c9b435` (distinct from the file-byte hash).
- [Original checkpoint](../next-stage-plan/execution/run/checkpoint.jsonl), [all-task locator/time/cleanup/usage index](task-index.json), [structured final handoff](report.json).
- Service `FSQFormalR4_20261110T154415Z`, leader PID58296. Original start `2026-11-10T15:44:44.771013Z`; end `2026-11-10T23:07:22.277957Z`; wall **26557.506944 seconds** (7h22m37.506944s). Its exit was observed through an owned-process kernel event, not device/status polling.

## Metrics from existing results only

| Scope | Attempted | Passed | Failed | Invalid evaluator | Valid official rewards | Reward sum | Valid-only mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 116 | 59 | 56 | 1 | 115 | 60 | 60/115 = 52.173913% |
| Android | 91 | 48 | 42 | 1 | 90 | 49 | 49/90 = 54.444444% |
| Information retrieval | 25 | 11 | 14 | 0 | 25 | 11 | 11/25 = 44% |

Coverage is 100%; indices0–115 were consumed in original order, one attempt and one official evaluator call each. Two recorded rewards are0.5. Family labels come directly from the frozen manifest. All reward means are **valid-official-reward-only diagnostics**, not leaderboard or fully qualified suite scores. Index101 remains null, never zero. Smoke/calibration rewards are excluded. Valid reward artifacts do not imply native protocol compliance: four of them have the summary-contract errors below.

## Four exact-main-summary contract errors — original classifications preserved

| Index | Task | Original classification | Official reward | Official reward artifact |
|---|---|---|---:|---|
| 13 | ExpenseAddMultipleFromGallery | passed | 1 | valid |
| 14 | ExpenseAddMultipleFromMarkor | failed | 0 | valid |
| 48 | RecipeAddMultipleRecipesFromMarkor2 | failed | 0 | valid |
| 49 | RecipeAddSingleRecipe | passed | 1 | valid |

Each original result records `mainAnswer.status=failed`, reason **`Main runner did not succeed`**, and native status `error`. The contract requires exactly one successful native `agent_runtime.runner` and its parsed `AgentFinalOutput` / `task_run_v1` summary verbatim; pre-plan, verifier or top-level text cannot substitute. The independent consumer therefore sees `proof.answer.status != valid` and adds `exact_main_summary` (`src/fsq_androidworld_eval/fsq_campaign.py:276–283`). This is failure to prove the native main-answer producer contract, **not** absence of an official numeric reward and not merely a string-comparison discrepancy.

All four official evaluations returned existing numeric rewards. Their passed/failed labels above are not rewritten. Their operational errors nevertheless fail the final `qualified` predicate. Thus this round is unqualified because of **four summary-contract episodes plus one evaluator-invalid episode**, not only index101. Original paths and per-case evidence are in `task-index.json` and `report.json`.

## Index101: evaluator invalid, not a scored failure

[Original result](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/result.json) and [original private evaluator diagnostic](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/evaluator-diagnostics.json).

The single official call after full native return/internal verification raised `RuntimeError`:

> Clipper app must be in the foreground to access clipboard. Additionally, app privileges must be granted manually by opening the clipper app and granting them.

The recorded stack is `SystemCopyToClipboard.is_successful:327 → get_clipboard_contents:1171 → _extract_clipper_output:1136`. The exact source branch means `extract_broadcast_data(raw_output)` returned `None`; launch-helper failure and non-OK adb-response errors are different earlier branches. Official clipboard comparison did not produce a reward.

Foreground/permission/broadcast-data preconditions belong to the official clipboard acquisition helper. The original diagnostic does **not** retain the raw broadcast output, current foreground or privilege state, so missing permissions, foreground timing, empty/unparseable payload cannot be distinguished. The error wording is not proof of missing permission. No external network transient or particular model cause is established. Native worker exit0 and failed internal verification do not make the official evaluation valid. No replay, permission fix or re-scoring was performed.

Index101 cleanup records teardown completed, environment closed, owned worker group settled. Its native `kill_app` attempt was denied by the frozen action budget; this is not successful app kill or device restoration.

## Real instruction/driver discrepancy

The requested behavior was immediate stop on invalid. Frozen `halt_reason` (`fsq_campaign.py:204–220`) instead stops unknown/failed task/environment/worker cleanup, forced processes, native evidence failure, and global identity/authorization/readiness drift. It does **not** halt on `invalid_evaluator` or `exact_main_summary` alone.

The loop (`:867–888`) records `operationalErrors`, but breaks only for forced outer process or `halt_reason`; any operational error makes the **final** qualification false. Consequently these errors did not stop subsequent scheduling; indices102–115 were consumed after101. The earlier assistant statement that every invalid would immediately failclosed-stop was inaccurate. This is a real execution-contract deviation, not successful immediate-stop compliance. By the time the urgent interjection was handled,115 had already completed and the owned service had exited. Nothing was force-killed, hot-patched, retrospectively reclassified or repaired.

## Cleanup and target handoff

The116 original results and referenced raw worker-process receipts show:

- All task teardowns completed and environments closed; cleanupFailure=false throughout.
- All worker exits observed, all owned worker groups settled; all raw worker receipts match the corresponding result.
- No terminated/killed worker or forced outer process recorded. Per-task outer exit/cap and producer paths are in the index.
- Native device restoration is **`not_provided_by_close`** throughout. No whole-device/app rollback, unroot, global-clean or final map-presence claim is made. Historical R3 unknown cleanup stays unknown.

There is no known in-flight business or pending identified owned worker/group in this run's terminal evidence. No new OS/session/device sweep was made. Passive native workspaces/evidence remain retained; their deletion is not claimed. Shared Appium, emulator, ADB, unrelated sessions and timers were untouched.

**This assistant no longer holds the target.** The coordinator explicitly released exact5554/8554 to w6:p1 and reported the new hourly notifier stopped normally. No further device action, campaign or optimization follows this handoff. Whole-device end-state and historical/unrelated-session unknowns remain outside this run's cleanup proof.

## Frozen identity and measurement limits

- Candidate `a8550aee3e1b9438377d34b5cf48ff4adde732785afe40aae2249f6266773030`.
- Frozen evaluator source `92b8bc71f0b26b19aacb1b23cd0944c3a3f614dbd46c72ab93076629590e2625`; FSQ0.1.2 source `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`. These are existing manifest bindings, not a new source audit.
- Requested/configured `github_copilot/gpt-6.1-sol`; native `ModelResult` does not expose server-returned model or backend weight/build identity. Native-call receipt and original stage bindings are linked in the JSON report. No single-variable comparison to the old5.6-sol run or historical AMKernel83.1897 is justified; historical results remain unchanged.
- Existing native execution artifacts expose Harness AI-assertion `token_usage` in49 episodes:81 recorded phase entries, input266624/output8596/total275220. Only `harness_metadata.ai_assertion.token_usage` is summed; mirrored `harness_output` copies are excluded. These are scoped recorded fields, not proof of81 unique HTTP requests or whole-agent token/cost totals. Pre-plan/main-runner/verifier/other calls are not extrapolated. Original native `duration_ms` is available for all episodes; its sum is23431024ms, distinct from wall time.

Final work was artifact extraction and documentation only: no tests, new telemetry, scoring, source/SDK/model/Skill changes or device probes.
