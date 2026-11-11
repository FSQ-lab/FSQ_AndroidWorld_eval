# FSQ-first stage proposal — no execution admission

**Offline preparation only. No live stage, device access, controller discovery or resource lease is authorized by these files.** Coordinator must read this stage proposal and the separate host-only resource-proof slice, obtain final independent approval, resolve current controller/non-conflict safety, then make one explicit admission decision. No code, documentation outside this requested plan, sealed inventory, original receipt or candidate was changed by this slice.

## Exact immutable bindings

- Candidate: `../candidate-final-manifest.json`; SHA256 `94a33fc3719cb2b289b274a415e78d91aeef5d9c34f8a63fedeac0e638e615f2`. Campaign `fsq-native-gpt61-r2-final-5554-20261110`.
- Accepted genuine native Responses receipt: `../native-model-success.json`; SHA256 `58d96868e5e4ccb139eb16e688178de0f2e9acbad40bc1f0035a293e0dd47323`. Accepted gate: `../model-gate.json`; SHA256 `b95002564fcbb0ca64d9ff116b561fe64c44ec508b11cf7dc7f141e40856869e`. These byte hashes were read locally during preparation; no new model call, authentication or sign-in was performed.
- Provider/configured/requested model is `github_copilot` / `gpt-6.1-sol`; actual returned `response.model` remains **unknown**, because native `ModelResult` does not expose it. The model receipt is not a live resource grant.
- Final independent closure is **approved offline** by w4:p2 for this exact revision-2 snapshot, R01–R08, R03 under clarified scope. `../independent-closure/report.json` SHA256 `5a941efe9bbe6d66f8a487c2995ea77946d7cccca898c0d422aef5fc02e612f6` is bound in the draft. It explicitly grants no live/resource permission; do not repeat review/tests/model gates.
- Formal scope is unchanged: exact frozen 116 tasks, seed 30, one combination/instance, identical frozen parameters, existing M/maxSteps/maxActions and B/B+610 allocation, one attempt per task, no automatic retry/resume. Smoke is a separate diagnostic attempt, not a calibration retry or added formal attempt.

## Exact target and current authority limits

Only the existing `emulator-5554`, AVD `AndroidWorldAvd`, console **5554**, ADB companion **5555**, gRPC **8554**, and frozen ADB path `/Users/qunmi/Library/Android/sdk/platform-tools/adb` are proposed. Preserve its existing lifecycle: no emulator or shared service restart/kill/reset; no new/replacement/cloned AVD, second target or alternative ports. The old 5560/5561/8560 proposal in `../environment-readonly-plan.json` is historical and not selected.

Native FSQ uses its original **uiautomator2** control and the official AndroidWorld **gRPC** evaluator, not Appium as an FSQ control path. Shared Appium `127.0.0.1:4723` still matters for conflicting sessions/controllers on the same target.

`../shared-resource-readonly.json` remains unchanged. Existing Appium log lines610980–610981 supplement the same failed GET `/sessions` with actual HTTP404 at `2026-11-10 06:00:13.505`. After a separate explicit permission, parent performed exactly one supported GET `/appium/sessions` at `2026-11-10T06:28:37Z`: **HTTP500**, WebDriver `unknown error`, server message `Potentially insecure feature 'session_discovery' has not been enabled`. `supported-session-discovery.json` and its error-detail supplement retain only necessary sanitized metadata. **Session count remains UNKNOWN**, not zero; no retry, feature enablement, restart, session mutation or device call followed.

Historical statements remain exactly limited: w6:p1 had “no retained exclusive window or in-flight real task”; w1:p1 and w2:p1 had “no reservation.” They are not current global-free proof, a target-controller handoff or a full-window lease. Human scheduling is explicitly **FSQ first; AMKernel waits until explicit release**. Priority alone grants no exclusive/disposable/mutation authority.

The official [Appium 3 migration guide](https://appium.io/docs/en/3.0/guides/migrating-2-to-3/#session-discovery-requires-feature-flag) establishes removal of GET `/sessions` and replacement by GET `/appium/sessions` with `*:session_discovery`. The one supported observation is now **consumed and refused**, not a future action to retry. Local installed routes are not proof of running byte identity. Existing retained master-list history reconciles to zero unmatched registrations, but lacks proven continuous coverage and cannot establish current session absence. The remaining non-conflict boundary requires an accountable current controller/target-authority handoff, not enabling the discovery flag or finding another registry-access path. Unknown current active session/controller means stop and report. Full host-only evidence is in `host-resource-evidence.json`.

## Proposed stages and proposed effects — none currently approved

| Order | Proposed stage | Scope and effects if later explicitly granted | Gate and bounded envelope |
| --- | --- | --- | --- |
| 1 | `qualify` | Fresh FSQ-specific installed-app/asset/UTC/device checks, ADB capture, actual gRPC core observation, restore existing official guest app snapshots/base state, then verify existing app-created base data. No business Agent/model call. Qualification itself does not install/repair assets or synthesize missing base data, save a replacement snapshot, or invent a first-launch recipe. This is **live and mutating**, not host-read-only. | Final independent/model/resource authorization, exact frozen identities; `600 + 610 = 1210s` remaining qualification envelope. Missing prerequisites fail, never silently repair. |
| 2 | `smoke` | Exactly one standalone native FSQ attempt of **index102 `SystemWifiTurnOff`**, with the original skill, observations, u2 connection, default `kill_app` semantics/internal verification, complete native return, terminal official evaluation and cleanup. It changes Wi-Fi and requires explicit mutation approval. | Successful fresh FSQ readiness bound to the same immutable authorization; **1330s** remaining full episode envelope. |
| 3 | `rehearse` | All 116 official initialize/is_successful/tear_down/close lifecycles, no business Agent, non-scoring. This still mutates official guest task/app state. | Only per explicit coordinator approval plus valid same-binding readiness; sum of existing per-task outer envelopes **225620s**, excluding stage overhead. |
| 4 | `calibrate` | Original 12 tasks in existing `CALIBRATION_TASKS` order, one genuine native attempt each, diagnostic operational evidence. | Only per explicit coordinator approval, same-binding readiness and valid all-116 rehearsal; summed frozen episode envelopes **18600s**, excluding overhead. |
| 5 | `run` | Full exact frozen 116-task formal single-attempt suite, unchanged scope/parameters/budgets. | Only per explicit coordinator approval plus valid same-binding readiness/rehearsal/calibration; summed frozen episode envelopes **225620s**, excluding overhead. |

**Native helper prerequisite is not established by this draft.** Future u2 connection may initialize support-server/instrumentation state; the unchanged native SDK may auto-provision helpers if absent. Coordinator must establish existing helper readiness or explicitly resolve whether native provisioning is permitted within the mutation grant before smoke. Do not promise that future live execution has no device mutation/install ever, do not assume helper presence, auto-repair, or patch the native lifecycle to suppress normal behavior. No helper/device query or installation was performed here. Original native business `kill_app` behavior is distinct from the forbidden ad hoc emulator/shared-service kill or supplementary app force-stop/kill.

### Why this one smoke and exactly what it budgets

`fsq_campaign.py:26-31,300-308` selects `SystemWifiTurnOff` first in the original-12 calibration order, although its frozen suite index is 102. Candidate declares easy/complexity1, maxSteps=maxActions=10, params SHA256 `ea520e5e870054de010df5f90dd92458decf8153b4798c9974a00186628a4d15`. Choosing that conservative existing task exercises the intended full native protocol without selecting a new task, changing the suite or claiming calibration/formal credit. Wi-Fi modification is a proposed effect, not presumed harmlessness or permission.

From `lifecycle.py:30-41` and the candidate:

- `B = max(600, 120 + 60 * 10) = 720s`.
- Cleanup window `180s`; termination grace `10s`; frozen force boundary `B + 190 = 910s`; recovery window `120s`.
- Full frozen episode/outer envelope is **B + 610 = 1330s**, not 720s or 910s. The remaining grant must cover this bound immediately before admission/spawn; existing entrypoints recheck it.
- Reserving both full configured envelopes consecutively gives a conservative planning sum **1210 + 1330 = 2540s**, plus actual overhead/hold/release work. This is **not a mandatory loader minimum or TTL**: admission requires 1210s remaining for qualification and 1330s remaining when the selected smoke is actually admitted; an early qualification return can leave that margin inside a shorter actual window. Coordinator chooses real finite endpoints from the actual schedule; none are invented here.
- The entire conditional sequence has a summed configured-envelope planning bound **472380s (131h13m)** before overhead, not a demanded lease duration: qualify + smoke + all-116 rehearsal + original-12 calibration + all-116 formal. Actual early returns can consume far less. The largest frozen single episode is **7930s**; each newly admitted episode still requires its own full remaining envelope. No automatic authorization extension, shortened task budget or smaller formal subset is implied.

## One coordinator decision: exact required fields

`authorization-draft.json` is intentionally **not loadable as admission**: wrong `kind`, no `approvedStages` member, resource booleans false, null window/authority. Accepted offline review and model evidence are already bound; they do not grant live resource use. Do not rename/copy the draft into approval.

With offline closure already accepted, coordinator must resolve the actual target/controller risk and issue one separate explicit resource/stage grant at:

`authorization-approved-qualify-smoke.json` in this directory (not created here).

The actual existing FSQ authorization namespace is:

1. `schemaVersion: 1`, `kind: "fsq_execution_authorization"`, exact `manifestSha256` above.
2. `approvedStages`: explicitly chosen stage strings. Initial proposal is **`["qualify", "smoke"]` only**, with exactly one standalone smoke as described. No later `rehearse`, `calibrate` or `run` is implied. If coordinator chooses to approve later conditional stages in that same once-issued grant, it must explicitly name them, approve their effects and cover their actual schedule before qualification; prerequisites and stop conditions still apply.
3. `independentReview`: `status: "approved"`, plus the actual approved final w4:p2 receipt `path` and byte `sha256` for this exact snapshot. Populate only after real approval.
4. `nativeModelCall`: `status: "passed_native_responses"`, `provider: "github_copilot"`, `requestedModel: "gpt-6.1-sol"`, actual `native-model-success.json` path and `58d96868e5e4ccb139eb16e688178de0f2e9acbad40bc1f0035a293e0dd47323`. Do not replace requested-model evidence with a fabricated server-model claim or repeat auth/model diagnostics.
5. `resource`: exact `serial`, `consolePort`, `grpcPort`, `adbPath`; `exclusive`, `disposable`, `mutationsAllowed` must be actual justified `true` assertions by the accountable coordinator/holder, **not inferred by the draft**; real numeric `notBeforeUnix` and `validUntilUnix` covering the plan; a nonempty `authority` identifying the accountable actual handoff/resource decision and evidence. Bind AVD/companion-port/lifecycle limits and current non-conflict/handoff proof in the real decision even though the loader's exact-target comparison directly checks only those four target keys. No fabricated controller signature/timestamp or process-ownership-as-permission.
6. Record no-restart/no-second-target limits, guest state disposability/snapshot/mutation scope, native helper prerequisite/provisioning decision, FSQ-first/AMKernel-wait policy, one-smoke scope, explicit release recipient w6:p1, and stop-on-unknown cleanup/controller conditions as coordinator policy/evidence. Extra JSON annotations are permitted but do not add loader enforcement: the loader validates coordinator assertions and receipt bindings, not live controller absence or cryptographic authority. In particular it does not enforce smoke count/task restrictions by itself; the prepared single-task command and coordinator/operator boundary must enforce them.

**Do not implicitly extend or edit an issued authorization.** `fsq_runner.authorization_digest` and campaign readiness/stage bindings cover the entire canonical authorization JSON, including window/stage/authority/annotation changes. Extending the window or later adding stages changes its identity; old readiness/rehearsal/calibration cannot be reused under that changed binding. Obtain explicit new approval and fresh matching qualification/prerequisite stage evidence if a new grant is actually necessary; do not merely rehash or relabel old receipts to imply execution. There is no invented receipt-age TTL or automatic renewal.

## Prepared command text, paths and guards

`prospective-commands.sh` contains exactly one real `qualify` command and exactly one real standalone `fsq_runner --stage smoke --task-index 102` command, in separate branches. **Neither was executed.** It does not contain later stage commands, a retry loop, discovery request, setup/reset/install command or alternate target.

Future guarded invocations are `bash prospective-commands.sh qualify` and, only after successful readiness and the admitted safety/helper conditions, `bash prospective-commands.sh smoke`. These are descriptions for the coordinator, not permission to run them now. The script uses the frozen evaluator `.venv/bin/python`, existing isolated evaluator-site and PyYAML parser overlay from the candidate; it performs no dependency setup. It requires the separate final authorization, exact candidate byte hash, new output root for qualification and absent smoke/outer paths. Smoke also requires a real fresh readiness path. Missing prerequisites fail closed. Existing public code performs real manifest/receipt/hash/stage/exact-target/window/readiness checks before device admission; file-existence guards alone are not authorization and cannot resolve unknown current controller safety.

New future output root, not created during this preparation:

`future-live-qualify-smoke-5554-7f139c2e/`

- Qualification: `qualify/`, including top-level `qualify/readiness.json`, `checkpoint.jsonl`, child `qualification/readiness.json` and owned process evidence/logs.
- Standalone smoke: `smoke-102-SystemWifiTurnOff/`, including `result.json`, private native evidence and parent-owned worker/process receipts.
- Separate outer supervisor: `smoke-102-SystemWifiTurnOff.outer/`, including `outer-process.json`, `standalone-result.json`, owned process evidence/logs. Parent/outer artifacts remain separate from worker-writable roots.

Preserve original terminal bytes, invalids and raw/private evidence with restrictive permissions; do not overwrite/delete failures, expose private goals/app contents/credentials, silently retry, recover, repair sources or rescore historical results. Present native dispatch/kill outcome, admitted action count, internal verification, complete native return, terminal official evaluation count/reward/classification and cleanup truthfully. Missing/failed/denied native kill is observed, **not** repaired by supplementary kill or a successful-kill eligibility gate. Only valid full native returns reach the one terminal official evaluation; do not invent rewards for invalid/forced attempts.

## Stop, cleanup and release

Qualification must actually report qualified checks and environment closed; smoke must preserve task teardown/environment close plus trusted observed owned-worker group settlement/exit and outer outcome. A zero shell exit is not proof of device cleanup; a non-perfect task reward is distinct from invalid evidence/cleanup. Forced/terminated/killed owned workers, failed/unobserved group settlement, invalid global identity/readiness/authorization, or unknown/failed task/environment cleanup **stop scheduling**. Existing owned-process supervision may terminate its own process tree under the admitted lifecycle; no new kill of shared emulator/Appium/service or unrelated process is permitted. Preserve forced/unknown terminals, report remaining uncertainty and ask only for the specific authority/prerequisite actually missing, never clear/repair the target.

After the approved scope completes, or coordinator explicitly decides it cannot continue, provide actual cleanup/remaining-owned-process and device-unknown evidence and **explicitly release the exact target to w6:p1**. State remaining unknowns even when release cannot assert a clean device. AMKernel remains waiting until that explicit release; FSQ priority, process exit, an expired window or historical holder statements are not release.

The draft-writing slice did not investigate host services or make endpoint/device/model calls. Parent independently completed the authorized host-only evidence and the single supported discovery refusal described above, then stopped further discovery. No code/original-evidence/dependency/Git/index change or live stage execution occurred. Offline review/model gates are complete. Remaining decision: accountable current target/control boundary and disposable guest-state risk, native helper initialization/provisioning effect scope if needed, exact chosen stages and finite window; coordinator can resolve these in one explicit grant without repeating completed gates.
