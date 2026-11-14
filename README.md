# FSQ AndroidWorld evaluation

## Native FSQ AndroidWorld experiment

This is a separate `fsq_androidworld` experiment, not an AMKernel plugin or an
extension of an old AMKernel acceptance. Its independent evidence lives in
[`evidence/fsq-native-gpt61-corrected-20261110T043031Z`](evidence/fsq-native-gpt61-corrected-20261110T043031Z).
The original delivery and review counterexamples are retained, not execution
approval. The R01–R08 repair bundle is [`revision-2`](evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-2).
Its separately authorized qualification passed; its single index102 smoke remains
`invalid_agent/native_evidence_invalid`, with no official evaluator call or reward.
The canonical-swipe consumer repair belongs to
[`revision-3`](evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3).
Its distinct index97 smoke completed with official reward0; its later no-Agent
rehearsal stopped after four attempts at pre-task clock admission. Those outcomes
remain immutable. The subsequent clock-lifecycle repair belongs to
[`revision-4`](evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4),
with new source/candidate/review and explicit live authorization required.
No earlier qualification or partial rehearsal transfers to the new revision.

### repaired2 full-suite result — 2026-11-14

The separately authorized native FSQ 0.1.2 / `github_copilot` / `gpt-6.1-sol`
repaired2 run completed all 116 single attempts: **81 passed, 35 failed**,
116 valid official rewards, sum 81, **81/116 = 69.827586%**. Rehearsal,
calibration and formal-run reports all have `qualified=true`; their rewards
are not pooled. This is the frozen-suite measurement, not an official leaderboard
claim or a proof of the wider isolation policy (`officialLeaderboardClaim=false`,
`policyProven=false`).

The immutable local archive is
`~/.local/share/fsq-androidworld-eval/fsq-native-gpt61-repaired2-20261113T175540Z`.
Its `final-campaign-verification.json` binds the formal report SHA256
`3d5ce4006fc855dfeaeb597ddfd824e9ce43c7129f93884a19cffe87b35d6d27`.
Preserve this archive and the earlier baselines byte-for-byte; none of these
private results, runtime snapshots or credentials belong in the source commit.
Post-evaluation cleanup released owned processes and forwards, cleared the
clipboard and returned the device to Launcher without stopping shared services.
Changing Git state invalidates the old manifest's live-admission identity;
future execution requires a fresh candidate and authorization, never a rewrite
of the historical manifest.

### r4 formal run — completed, not qualified

The explicitly released r4 formal run completed all116 original single attempts
(91 Android +25 IR), then exited naturally with code2: `qualified=false`,
`haltReason=null`. Original classifications are59passed,56failed and1
`invalid_evaluator`. There are115 valid official reward artifacts, sum60;
`60/115 = 52.173913%` is a **valid-reward-only diagnostic**, not an all116-valid
score. Index101 remains null, never zero; smoke/calibration rewards are excluded.

Qualification fails for four `exact_main_summary` episodes (13/14/48/49) plus101's
evaluator error. Their original classifications/rewards are preserved:13 and49
passed/reward1;14 and48 failed/reward0. A failed native main-answer producer
contract is distinct from official reward validity. The frozen driver continued
these errors rather than implementing the requested immediate-invalid stop;
this instruction/driver discrepancy is recorded, not retrospectively repaired.

All116 recorded task/environment/owned-worker cleanups completed, but native
device restoration is not provided by close and historical R3 unknowns remain.
The assistant no longer holds the target; the coordinator released it to w6:p1.
See the [final handoff and original report hash](evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/final-handoff/report.md)
and [per-task original-evidence index](evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/final-handoff/task-index.json).
The historical AMKernel83.1897 result below is unchanged and is not a
single-variable comparison with this native FSQ experiment.

### Native execution and measurement contract

- Execute the complete native `FsqAgent.from_settings` through
  `DynamicExecutionService.execute(DynamicExecutionRequest(record=False))`, including
  pre-plan/main runner/internal verification. Preserve FSQ Skills, observations,
  native uiautomator2 and model-issued `kill_app`; do not replace the model loop,
  suppress kill, install a post-final hook, or score before full FSQ returns.
- Bind the exact manifest serial to the native Android settings. Target
  `github_copilot` / `gpt-6.1-sol`; reject effective provider/model mismatch and never
  fall back to another provider/model.
- Freeze all 116 corrected task definitions, ordering, seed 30 and one instance
  per task. JSON-compatible parameters are generated once and reconstructed from
  their frozen values, not regenerated from a clock-sensitive generator.
  The remaining seed-transport tasks must reconstruct to the exact frozen digest.
  Complete source/installed package and task-data maps must match.
- Budget `M = int(10 * complexity)` counts **admitted native Android Harness write
  capability dispatches**, not Appium requests or primitive uiautomator2 operations.
  Reserve atomically before forwarding; failed dispatches never refund. The eight
  writes include setup/teardown; `input_text` is one composite unit. Construction,
  implicit u2 startup and observation/assertion backend side effects are excluded.
  Multiple tools/harnesses share the gate; unsupported batching is rejected.
  The approved `read_element` observation crosses the same factory and deadline
  gate without consuming write units. The budget wrapper forwards Core's live
  observation-redactor hook to the native Harness, preserving its complete safe
  view before pagination and durable evidence serialization. Launch readiness
  parameters remain native-schema-owned and one launch remains one write.
  Unknown driver capabilities still fail closed; this does not add a reader,
  remaining-budget tool, turn allowance, oracle access or sandbox permission.
- Accept exactly one `agent_runtime.runner` step, with step status `success` and a
  parsed native `AgentFinalOutput` / `task_run_v1`. Use its `summary` string verbatim,
  after FSQ's own redaction; empty and whitespace strings remain empty answers.
  Preserve business status separately. Missing/failed/multiple/malformed runners
  never select pre-plan, verifier, top-level summary or a trajectory-derived answer.
- Give the worker only the initialized public goal, not evaluator parameters,
  task data or expected values. Stage only worker/native modules outside the
  evaluator tree; use narrow runtime read roots and a private worker `TMPDIR`.
  Pin and deny retained/direct-URL AndroidWorld source copies and all result roots,
  including outputs outside the checkout; deny unrelated OMP/Copilot credentials.
  This is a local filesystem boundary, not a general network/u2 security sandbox.
- Before the official evaluator, independently bind native TaskResult/verification,
  exact main summary, serial and episode identity, and replay dispatch admissions,
  tickets, outcomes and pending operations against the frozen maximum. A trusted
  parent-owned process receipt must prove worker exit and process-group settlement;
  parse/archive failures cannot erase that receipt or forced-worker attribution.
- After complete FSQ execution and settled dispatches, call the official terminal
  evaluator once. Observe native kill success/failure/denial/absence and internal
  verification without requiring successful kill, adding a main-final ordering
  gate, or issuing a replacement kill. Internal verification is not official reward.
  No oracle call for unproven full execution; no business retries or resume.
- Business deadline is `B = max(600, 120 + 60 * M)` seconds; native close allowance
  180 seconds, termination grace 10 seconds, outer bound `B + 610` seconds.
  Forced/unknown cleanup halts scheduling. Native `close()` is not a device-state
  restoration claim. Explicit exclusive/disposable resource approval must cover
  the full episode bound; no new arbitrary receipt-age TTL is imposed.

### Offline verification and future authorized commands

The shared `.venv` and its AndroidWorld installation were not replaced. Corrected
AndroidWorld plus complete source/data were installed into a new owned target.
The declared `PyYAML==6.0.3` dependency was installed only into the owned parser
prefix; its package/distribution identity is frozen too. Use the same overlay:

```bash
export PYTHONPATH="$HOME/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-dependencies"
.venv/bin/python -B -m fsq_androidworld_eval.fsq_manifest inspect \
  --project . \
  --manifest evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-2/candidate-final-manifest.json
.venv/bin/python -B -m pytest -q tests/test_fsq_manifest.py tests/test_fsq_native.py \
  tests/test_fsq_worker.py tests/test_fsq_supervisor.py tests/test_fsq_runner.py \
  tests/test_fsq_campaign.py tests/test_fsq_evidence.py tests/test_fsq_outer_entry.py
```

`fsq-native-androidworld-prepare`, `fsq-native-androidworld-episode` and
`fsq-native-androidworld-campaign` are declared package entry points; the exercised
commands use `python -m` without reinstalling the shared environment.

Only after independent review, a genuine native Responses-call receipt, exact
resource ownership and explicit coordinator stage authorization: prepare a **new**
manifest with the now-correct native provider metadata, then run `qualify`,
all-116-task non-scoring `rehearse`, original-12-task `calibrate`, and `run` through
`fsq_androidworld_eval.fsq_campaign`. Required flags are `--project`, `--manifest`,
`--authorization`, `--output`; later stages additionally bind `--readiness`,
`--rehearsal`, and finally `--calibration`. Each output directory is new and
immutable. The standalone smoke entry also requires authorization and readiness.
Exact prospective commands and receipt fields are in the dedicated handoff.

Native stages use one fail-closed terminal decision after owned worker, official
task teardown and environment cleanup. Unknown/failed cleanup wins over other
stop reasons; `invalid_*`, native/worker/outer-process failures and consumed
operational errors stop dispatch before the next task. A missing, failed or
noncanonical main answer stops even when the official reward is 1. The original
classification, official reward (including null), native verification and private
main-answer evidence remain separate and unchanged. Valid official 0 or partial
reward with a valid native return is a business outcome, not a stop or retry.
Standalone `fsq_runner.main` uses the same decision and cannot exit 0 for those
contract failures; neither entry scores, retries, repairs or resumes them again.

For `rehearse`, `calibrate` or `run`, optionally pass `--stop-file /absolute/path/native.stop`.
The operator creates that file to request a normal stop before the first or next
episode. An in-flight episode finishes its existing evaluation and owned cleanup
before the request is observed; no signal, forced termination or ownership claim
is implied. If an episode itself requires a stop, its terminal reason takes
precedence over the pending request. A boundary stop records `stop_requested`,
actual attempts/coverage and `qualified=false`, and exits nonzero (2), without
inventing an episode or turning unstarted tasks into failures. The request file
remains operator-owned. This is not a resume/checkpoint-repair protocol, and does
not change the separate frozen external AMKernel strict-stop implementation.

The coordinator accepted a genuine minimal native Responses receipt for configured
`github_copilot/gpt-6.1-sol`; server-returned model remains unknown because native
`ModelResult` does not expose it. FSQ has scheduling priority on the original
`emulator-5554` / console 5554 / gRPC 8554 target, but priority is not holder/readiness
proof or live authorization. Independent adapter closure and explicit stage/resource
grant remain required; release explicitly to the other AMKernel session afterwards.
Report complete coverage, invalids, original cleanup and denominator-labelled
reward diagnostics; no official leaderboard claim or single-variable comparison
to the historical AMKernel score is justified.

### Official environment transport boundary

`environment.load_environment` composes project-local AndroidEnv subclasses;
it does not patch the SDK, global loader, global launcher or native FSQ driver.
Each controller owns its helper bytes, refresh owners, logcat child and loopback
ADB gateway. Only the exact serial reaches the configured existing ADB daemon.
One command failure latches the environment; no SDK retry or shared daemon
restart is permitted. Close tears down owned host resources, not guest state.

The gateway is necessary because [ADB's own client recovery](https://raw.githubusercontent.com/mirror/platform_packages_modules_adb/main/client/adb_client.cpp)
can send `host:kill` on protocol mismatch even without a `kill-server` argv.
It rejects global/other-target host services and returns failure before an
incompatible or absent upstream can trigger client recovery. Only locally
verified ADB protocol 1.0.41 is supported. No negative shared-daemon experiment
is needed or authorized to exercise this boundary.

Official lifecycle console commands are audited against the exact frozen 116-task
manifest, not every disabled task in the upstream package. Only `emu sms send`
is required (indices 081/082/083/086). Native `adb emu` ignores `-P` and connects
directly to the console, so it is never invoked by this bridge. A bounded private
framed RPC traverses owned SDK/parent gateways and authenticates only the exact
serial's loopback console, retaining version, epoch, deadline, close and first-error
admission. Only audited SMS argv are accepted; management commands, `gsm call`,
`geo fix`, foreign targets and control/semicolon injection remain denied. Quotes
and Unicode are permitted. Current frozen messages and all 40 noise sentences
satisfy this contract; enabling new tasks or expanding that corpus requires audit.
Existing device-scoped shell, sync push/pull, install and root paths are unchanged.

Non-scoring rehearsal retains the primary failure in `error` and ordered cleanup
failures in `cleanupErrors` with their phase, type and bounded original message.
Failed cleanup leaves the lifecycle incomplete; it never replaces the primary
initialization/probe error or clears a poisoned transport for business work.

Official launch-only Monkey forms and bare mapped activity launches resolve
the current Android user and installed MAIN/LAUNCHER component, including aliases.
Checked `am start -W` rejects process failures, timeouts and Android framework
errors even at exit zero; existing-activity warnings with `Status: ok` succeed.
Other Monkey programs fail closed; explicit intent arguments retain their
official semantics. Preparation's direct launch probes use the same resolver.
Native clock/device probes and Appium-404 process discovery use the same scoped
transport; discovery parses a successful process table rather than treating a
failed `pidof` command as an empty result.
An active Audio Recorder directory probe shares its controller's failure latch.
VLC UI preparation validates coexistence first, then uses the same checked native
launcher; owned Appium session cleanup never launches or force-stops the app.
Official setup ValueErrors propagate before snapshot creation. Preparation-only
execution may use native installation from existing hash-verified local APK cache
when its new limited grant permits it; no network/dependency download is implied.
Any change requires new source/candidate identity, independent review and a
limited stage/resource authorization; historical evidence/grants do not transfer.

Native controller construction checks `whoami`, performs native `adb root` at most
once when needed, and verifies root identity before acquiring backend/logcat owners.
The official later conditional root call then observes root without restarting an
owned stream. A zero root-command exit alone is not sufficient. Unexpected prior
logcat exits remain cleanup errors; no exit-code exemption clears the first failure.

Preparation control must not queue a Python completion-marker line behind a native
call on an interactive interpreter's stdin: an inherited subprocess stdin can
consume that line. The sealed Audio-first22 worker instead owns separate,
noninheritable control/reply descriptors and gives native children `/dev/null`
as stdin. Stage return/failure replies use the original reply descriptor; a
failure remains nonzero. After Audio's actual PNG/UI review, only explicit
acceptance permits the remaining21; after one normal cleanup, only control EOF
and actual worker/reader/log settlement are allowed. A missing four-byte passive
registration ACK event does not establish missing registration or override
successful native initialization.

Official Audio setup force-stops its first launch; the completion helper also
closes the configured app before saving its data snapshot. Launcher history and
snapshot success therefore do not prove foreground readiness. The Audio-first22
producer explicitly launches Recorder once after that snapshot, waits within a
bounded deadline for its visible main timer without onboarding or foreign
permission UI, then captures the actual PNG/UI for independent acceptance.
Report official setup-returned coverage separately from actual ready acceptance;
the other21 remain blocked on a rejected or ambiguous Audio surface.

Parent emulator lifecycle uses the same fail-closed boundary: a frozen `-adb-path`
executable and endpoint environment route SDK CLI/native registration through an
owned gateway. Only `host:emulator:5561` can register the isolated 5560 target;
registration requires successful protocol-41 admission against the pinned daemon
epoch before guest creation. Preparation, SDK CLI and registration share a first-error
fence, including when evidence writing fails. Every forwarded request rechecks the
original grant bytes, business deadline, daemon epoch and stop/error fences.
All automatic parent SDK-ADB commands hold one owned, cross-process file lock
through command execution and normal transport close. SDK initialization holds
the same lock from its initial whoami through any root/reconnect and final root
verification; backend construction is outside it. Thus later native broadcasts
cannot overlap root even when gRPC already reports booted. The old overlay-only
completion gate/receipt is removed rather than extending an opcode list.
Lock identity binds the original grant/profile and owned PID/parent/birth;
contention waits are bounded by the original command budget and business window.
Registration/reconnect still uses the gateway directly without taking this lock.
The SDK shim records/latches a command failure before attempting close; a
secondary close error remains separately visible after the original error.
Only a successful exact-serial `host:tport:serial` response can bind its returned
transport ID to that gateway. The fixed `wait-for-any-disconnect` opcode requires
such a learned ID and still passes the original per-forward epoch/deadline fence;
the reconnect wait must name the exact serial. Unknown IDs, foreign serials and
other transport-ID opcodes remain rejected. After an admitted service starts,
EOF ends only its read direction: forward FIN with `shutdown(SHUT_WR)` and drain
the opposite direction before closing the stream. This preserves shell response/
exit bytes after client FIN and late client control frames after upstream FIN.
Client reset remains normal cancellation; genuine upstream reset remains fatal.
Shell-v2 truncation/nonzero exit still fails through the pinned ADB consumer;
neither a command's exit zero nor an observational journal overrides the fence.
The first gateway refusal carries a bounded structured cause type/message, exact
rejecting branch, safe host request/selected-service descriptor and gateway/target
correlation. Raw shell/sync/app data and credentials are not diagnostic output.
The actual exception remains available in memory; printable causal chains use the
safe refusal object. Transport's first latch and the exclusive parent failure
receipt retain it across later cached checks and cleanup errors; the generic
external halt marker is not mistaken for the original rejecting request.
Malformed framing/version fields expose input-free parsing descriptions; their raw
parsing causes remain private. Ordered groups and explicit cause wrappers retain
the first gateway refusal alongside the other initialization/cleanup errors.
The original grant must separately permit owned normal cleanup, with an explicit
deadline no more than 120 seconds after the business deadline. Stop fences forwarding
under the send lock, retains the original start-grant hash, and bounds the sole
owned-PID gRPC `setVmState(SHUTDOWN)` dispatch, exit wait and gateway joins by that
cleanup deadline. No ADB stop, force-kill, renewal grant or success fallback exists.
After cleanup authorization, backend admission, RPC, exit wait and host joins share
a maximum 120-second deadline within the original grant; a missing backend cannot
consume the unused business window. Both SDK image pins are checked before creation.
Owned process identity separates the original Popen object, parent PID and stable
PID birth from executable/argv, which legitimately change during the launcher exec.
Only the exact frozen launcher and installed `qemu-system-aarch64-headless` paths
and hashes are admitted; Darwin kernel argv must retain every original argument.
Backend admission is monotonic. `start()`, `wait_until_booted()` and normal `stop()`
share this contract and reject foreign console/ADB/gRPC listeners. Boot admission
requires all three owned listeners before preparation consumes the resource.
Predeclared lifecycle slots use separately hashed profiles in
`parentController.profiles`, one original finite authorization, distinct receipts,
and a shared first-failure fence. A two-stage smoke/preparation grant requires its
new smoke's boot-qualified, normally closed receipt. Later grants may inherit that
accepted lifecycle proof without repeating smoke; they never inherit its resource
window. An evidence-only native-initialization diagnostic stops on either first
failure or initialization success and cannot advance to the 22-app loop.
An already attempted close may be skipped only with explicit matching closed/exit-zero
evidence; prior failed or unknown cleanup remains an error and is never retried.
Static/owned-peer verification does not prove a live SDK guest or shared daemon;
actual start/stop requires a new exact-candidate seal and resource authorization.

### Native change record

- 2026-11-14: audited all 116 inherited task lifecycles and 75 command shapes;
  replaced the four SMS tasks' blanket `emu` refusal with exact-target authenticated
  gateway RPC, without enabling disabled phone/geo tasks or console administration.
  Preserved rehearsal primary and cleanup errors independently. Related verification
  passed 537 tests with 1 skipped; directed real-device checks completed all 35
  lifecycles at indices 081–115 with 2918 command calls and known owned cleanup.
  These no-Agent, non-scoring checks are not a qualified all-116 rehearsal,
  calibration, formal score or execution authorization; old campaign records remain
  unchanged. The new isolated repaired2 candidate requires independent review.

- 2026-11-12: preserved both directions across service-stream FIN instead of
  closing both sockets at the first EOF. Actual pinned-ADB directory consumers
  retain late close-stdin frames; two-gateway regressions cover either first FIN.
  Upstream reset and truncated/nonzero shell exit remain fatal; retained live logs
  lack wire-close chronology and do not establish the historical reset cause.
- 2026-11-12: replaced the overlay-only bootstrap gate with a shared owned
  cross-process boundary covering parent automatic command/close and SDK
  root/reconnect/verify, including broadcasts arriving after boot qualification.
- 2026-11-12: replaced interactive preparation-marker waiting with an isolated
  fixed-worker control protocol; offline actual-process success/first-error
  consumers preserve timely settlement and nonzero errors without device calls.
- 2026-11-12: bound native root disconnect waits to exact-serial selected transport
  IDs under the unchanged daemon epoch, admitted only the exact-serial reconnect
  wait, established root before backend/logcat ownership, and distinguished native
  client stream cancellation from upstream failure. Historical Envclose failures
  remain unchanged; actual live preparation still requires a new sealed grant.
- 2026-11-12: retained structured first gateway refusal and safe causal propagation
  through transport and exclusive parent evidence, without expanding ADB admission
  or changing first-failure/retry policy. R2 historical missing-cause records remain unchanged.
- 2026-11-12: replaced mutable whole-command birth identity with stable owned-child
  identity plus exact pinned launcher-to-headless exec admission shared by startup,
  boot qualification and normal cleanup. Preserved historical incident receipts.
- 2026-11-12: added frozen parent lifecycle registration/version/epoch admission,
  a shared physical failure/stop fence and an original-grant-bounded normal cleanup
  lane. Historical daemon identities and grants are not current launch permission.
- 2026-11-12: replaced global environment construction/launcher hooks with owned
  transport, helper and request-boundary adapters. Isolated ADB host protocol
  recovery, retained failed logcat/partial-owner cleanup, and removed setup-error
  suppression. This source repair does not authorize or change historical runs.
- 2026-11-10: added the dedicated native worker, shared atomic dispatch gate,
  bounded subprocess supervision, corrected-task candidate freeze and independent
  qualification/rehearsal/calibration/full orchestration. Offline CLI execution
  exposed the missing parser dependency and clock-sensitive folder generation;
  preserved both failures and corrected them without changing official tasks,
  shared installations, native FSQ source, credentials or devices.
- 2026-11-10: implemented R01–R08 targeted-review repairs: narrow oracle boundary,
  durable parent process receipts, settled owned-group cleanup, public standalone
  outer watchdog, truthful non-gating kill observations, and independent native
  summary/audit/episode identity validation. Original review evidence is immutable;
  new verification and candidate identity belong to `revision-2`.
- 2026-11-10: corrected the native evidence consumer's rejection of the canonical
  `swipe` self-alias. Genuine camelCase aliases remain invalid journal values;
  canonical writes still consume the same budget. Added a desensitized real
  native-output fixture and full-consumer accounting/alias/write-label regressions.
  Path containment, symlink/hash checks, exact main summary, identity and audit
  checks are unchanged. The consumed index102 outcome and its null official reward
  remain immutable; this offline repair does not rerun or rescore that task.
- 2026-11-10: separated task-owned timezone/auto-time from stable target identity.
  Official BrowserTask may enable automatic timezone and does not restore UTC in
  teardown. API/boot/build/ABI/screen/APK identities remain fail-closed; qualification
  still requires an observed UTC/auto-time-off baseline. A separately authorized
  `prepare-clock` command uses official environment clock setup, records before/after
  state and cleanup, and never runs as an admission-error fallback. Each task retains
  its original clock semantics; no task-specific exception or score optimization.
  Old partial rehearsal and unknown cleanup stay unchanged; a new grant must authorize
  clock preparation, qualification and a full new no-Agent rehearsal, not resume.
- 2026-11-11: unified native stage and standalone terminal stops, including official-1/main-error divergence, any invalid episode and consumed operational failures; added cleanup-priority normal boundary stops via `--stop-file`. Preserve actual spawn count and termination uncertainty when an already-started outer process raises `OSError`. Original rewards/classifications, evaluator ordering, cleanup ownership and historical evidence are unchanged. Offline-only implementation; no launch authorization or live readiness is implied.
  Verification: focused native campaign, runner, evidence, outer-entry and supervisor checks passed **232 tests, 1 skipped**. Seven offline CLI scenarios exercised dispatch/exit behavior with fixture dependencies; separate owned-host-process smoke retained `spawnCount=1` and observed termination after an injected post-`Popen` wait error, while genuine exec failure retained `spawnCount=0`. No device/model run or live readiness is claimed.
- 2026-11-12: added the minimal native budget-wrapper bridge for the reviewed FSQ Android `read_element` capability and `configure_observation_redactor` callback. This is a new candidate integration, not a migration of r4 or AMKernel readiness/evidence; device smoke requires a separately confirmed exclusive handover, and no Agent/model run is authorized by this change.
  Verification and resource boundary: [new bridge evidence](evidence/fsq-budget-bridge-20261112T000630Z) records one isolated integration check (172 passed, 2 new fixture failures), followed only by the two affected consumers passing after adding synthetic screenshot support to the offline transport. Production bridge code was unchanged. A network-denied public-factory/Core/Recorder offline smoke reconstructed 6317 safe Unicode characters in nine pages, with zero read-side write admissions, one launch admission and fresh-process evidence recovery. Device smoke was **not run**: the AMKernel owner explicitly retained 5554/8554/4723 for its in-flight qualification/formal window; no replacement target was assigned. No device readiness, model ability or score improvement is claimed.

## Current-stack release evaluation

The approved comparison measures a newly published AMKernel release on **Harness
r15 and OMP 18.18.3**. It is not a single-variable AMKernel/Skills experiment.
The historical complete baseline used r12 continuation v2 and OMP 18.12.6.
Changes include bounded business-answer submission, accessibility coexistence and
the replacement forwarder, initialized task reference-clock context, and OMP.
Report these differences rather than attributing any score delta solely to Skills.
Historical manifests/results are never edited, resumed, or merged into a new run.

### Frozen experiment

- Exact source: `campaigns/amkernel-3388314-r11-timeout300-full-20261106T142607Z/manifest.json`.
- Source bytes SHA256: `2345c5af27c75f7c1a7c6e263b77963f426864a6486a51e845468430a50ea856`.
- Ordered 116-task specification SHA256: `f41b2dac8a427ddd22bbe4ea04b0104ae9feea8280c9295b2fe1dfbc6671d417`.
- Model: `github-copilot/gpt-5.6-sol`; seed 30; one identical-parameter instance and
  one business attempt per task. The only permitted retry remains one
  pre-Agent `invalid_infrastructure` retry.
- Step allocations, goals, instance seeds, parameters, ordering, time budgets,
  tool/action policy and official evaluators remain inherited, not regenerated.
- Qualification, all-116-task non-scoring rehearsal and 12-task calibration must
  be fresh under the exact new protocol, Runtime and target identities.
- For a complete valid full run, report `fullValidScore`, coverage, invalid/null
  rewards and original cleanup outcomes. `officialScore` remains null for the
  continuation full-run protocol; do not present it as an old-protocol score or
  an official AndroidWorld leaderboard result.

### Recorded result: AMKernel 0.1.4 (2026-11-10)

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.
The existing [campaign handoff](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/startup-handoff.json)
now records the final result (`finalResult`), all 20 failed tasks with their original
termination labels/rewards/result paths, and the release commit/wheel identity.
It retains the original startup evidence separately; the workflow is **completed**.

| Formal full-run field | Saved final value |
| --- | --- |
| Started / completed / planned | 116 / 116 / 116, unique complete coverage |
| Passed / failed / invalid | 96 / 20 / 0 |
| Cleanup failures / attempt retries | 0 / 0 |
| Official reward sum | 96.5 |
| `fullValidScore` | 0.8318965517241379 (83.1897%) |
| `officialScore` | `null` |

`fullValidScore = 96.5 / 116` includes partial credit (the final VLC task earned
0.5 despite classification `failed`); it is **not binary pass rate** or an official
AndroidWorld leaderboard score. Qualification, the 116-task non-scoring rehearsal
and 12/12 calibration passed; calibration is excluded from the formal totals.
AMKernel 0.1.4 / `github-copilot/gpt-5.6-sol` / Harness r15 / OMP 18.18.3 used
the inherited 116 tasks, seed 30, identical instance parameters, one business
attempt per task and unchanged task/action/time budgets.

The checkpoint `finished` event is 2026-11-10 **08:02:19 UTC+8**; summary was
finalized at 08:02:40, and full/supervisor exited **0** at **08:02:41 UTC+8**,
with no error or pause. The existing final read-only verification (08:03:01 UTC+8)
matched all 116 result hashes/rewards to checkpoint and all summary episodes to
their terminal records; coverage audit is complete with no errors.
Primary evidence: [summary](campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/summary.json),
[checkpoint](campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/checkpoint.jsonl),
[launch state](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/launch-state.json).

Failure analysis is recorded in the [module map](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/module-map.md) and [review resolutions](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/review-resolution.md).
Termination labels alone are not diagnoses. Historical r12 / OMP 18.12.6 differs
from this current stack: do not attribute any change solely to AMKernel/Skills. No historical-score
comparison or rescoring was added for this record.
Hourly reminders are stopped per the coordinator handoff; this documentation
operation did not alter their scheduler. Shared Appium/emulator were not stopped;
their current live state was not rechecked for this record. No restart is implied.

### Explicit identity migration

Existing `prepare --inherit-manifest` stays strict by default. To evaluate the
approved current stack, additionally supply `--runtime-migration /absolute/pins.json`.
This is a release-specific, immutable JSON approval, not an unrestricted upgrade
flag. It is copied into `protocol.runtimeMigration` with its original absolute
path and byte SHA256. Keep both that file and the exact wheel available for
subsequent loading and offline scoring. Changing either invalidates the run.

The approval has exactly these fields:

| Field | Required value/source |
| --- | --- |
| `schemaVersion` | Integer `1` |
| `comparison` | `current_stack` |
| `harnessRevision` | Integer `15` |
| `sourceManifestSha256` | Exact source-file digest above |
| `runtimeIdentity` | Complete observed `_runtime_identity(project)` dictionary after the approved release and matching Skills are installed; all keys, including final Harness source hash, are pinned |
| `release.version` | Exact newly published version, different from the frozen baseline; must equal both AMKernel and Skill Runtime versions |
| `release.artifactUrl` | Public HTTPS URL supplied by the release owner; no credentials or URL fragment |
| `release.artifactPath` | Absolute local path of that published `.whl`, not a rebuild from the development checkout |
| `release.artifactSha256` | Published/release-owner-verified wheel SHA256, checked against local bytes |
| `release.sourceCommit` | Full 40-character lowercase commit supplied by the release owner |
| `release.runtime.pythonVersion` | Exact `sys.version` from the launcher's own interpreter |
| `release.runtime.dependencies` | Complete installed distribution list in that interpreter, each `{name, version}`, sorted by lowercase name |

Only these original Runtime fields may change:

- AMKernel: `amkernelVersion`, `amkernelExecutableSha256`.
- OMP: `ompVersion`, `ompExecutableSha256`; version must be `omp/18.18.3`.
- Skills: `installedAgentAssetsSha256`, `skillMetadataSha256`,
  `skillRuntimeVersion`, `officialSkillManifestSha256`,
  `officialSkillArchiveSha256`, `officialSkillSourceCommit`.
- `harnessSourceSha256` already permits Harness evolution; the new value is still
  pinned exactly in the approval, so later code changes require new preparation.

Every other original Runtime field remains frozen even if a new approval tries
to change it: evaluator Python/dependencies, AndroidWorld revision/generated
protobuf, gRPC fork setting and media encoder. The existing named-forwarder-only
asset migration remains unchanged; no other APK/data asset may drift.

Preparation and every live manifest load also verify:

1. Project recovery/preparation MCP and campaign PATH resolve to the same stdio
   AMKernel launcher, without extra launcher arguments.
2. The launcher's absolute Python shebang identifies the actual Runtime. Its
   Python version and complete dependencies match `release.runtime` exactly.
3. All installed `amkernel/` package files match the pinned wheel; import origin
   is installed `site-packages`, not an editable development checkout.
4. Installed main Skill files match wheel bytes and their metadata. The
   wheel-matched packaged verifier checks official vendor/source and Skill copies.

The offline scorer checks the same migration allowlist, complete target pins,
original approval bytes, wheel hash/name/version and existing run provenance. It
never imports the measured package, repairs dependencies or contacts a device.
The URL and commit are release provenance assertions: local preparation does not
fetch the URL or independently prove that the claimed commit produced the wheel.
The coordinator must obtain that release evidence before accepting the pins.

### Preparation and launch boundary

Do not install/activate a release, run qualification, rehearsal, calibration or a
formal campaign until the coordinator provides the published version and permits
the corresponding changes/resource window. Never substitute a local development
build when the release is unavailable.

After approval and release installation, use the same pinned environment for all
stages. Keep the evaluator on its existing `.venv`; AMKernel uses its independent
managed Runtime. Do not upgrade unrelated dependencies to make a gate pass.

```bash
source .venv/androidworld-env.sh
export GRPC_ENABLE_FORK_SUPPORT=0
export PATH="$APPROVED_AMKERNEL_BIN:$APPROVED_OMP_BIN:$PATH"

.venv/bin/python -B -m fsq_androidworld_eval.campaign prepare \
  --project . --kind rehearsal --campaign-id "$REHEARSAL_ID" \
  --inherit-manifest "$FROZEN_SOURCE_MANIFEST" \
  --runtime-migration "$RELEASE_PINS" \
  --environment-mode-report "$ENVIRONMENT_MODE_REPORT" \
  --output "$REHEARSAL_MANIFEST"
```

`prepare` verifies only local identities/artifacts and writes a new manifest. It
neither operates the device nor runs an Agent. Invalid migration input fails
before creating the output directory. It requires existing pinned cache assets;
it never downloads them automatically. No release-independent real manifest can
be prepared because the release wheel, versions, Skills and Runtime must already
match their exact pins.

Use the same migration approval and environment evidence for calibration and
full preparation. Calibration selects the original 12 task specifications; full
preparation additionally requires `--calibration-campaign-dir` for the newly
qualified calibration. `qualify` and `rehearse` are device-mutating stages, not
read-only readiness probes. A full launch uses:

```bash
.venv/bin/python -B -m fsq_androidworld_eval.campaign run \
  --project . --manifest "$FULL_MANIFEST" \
  --readiness-report "$FULL_READINESS" \
  --rehearsal-report "$REHEARSAL_REPORT" \
  --calibration-campaign-dir "$CALIBRATION_DIR" \
  --output-dir "$FULL_RUN_DIR" \
  --adb-path "$HOME/Library/Android/sdk/platform-tools/adb"
```

Run IDs are explicit, not automatically assigned. Suggested convention:
`amkernel-<release>-r15-current-stack-<kind>-<UTC>`, under `campaigns/<id>/`.
Preserve `manifest.json`, `run-metadata.json`, readiness/rehearsal/calibration
artifacts, `checkpoint.jsonl`, per-attempt result/events/business submission,
recovery evidence and `summary.json`. Startup proof requires qualified initial
attestation/core health and an `attempt_started` event with real Agent/model/tool
activity; a PID or an output directory alone is not proof.

### Approved task-contract corrections (2026-11-10; new definition identity)

Scope: only **001 / 014 / 076**, from the completed [failure analysis](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/module-map.md) and [two-stage review resolutions](evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/review-resolution.md), followed by explicit implementation approval. The decisions below supersede the alternatives for future task definitions, not the historical evidence.

| Task | New contract | Compatibility boundary |
| --- | --- | --- |
| 001 `AudioRecorderRecordAudioWithFileName` | The generated/visible complete filename is checked verbatim, including its extension. | No appended `.m4a`, stem fallback or guessed alias. A different or double-suffixed file does not satisfy the requested name. |
| 014 `ExpenseAddMultipleFromMarkor` | Pipe-delimited, correctly quoted CSV has a separate `reimbursable=yes/no` selection column. The goal explicitly says select yes rows, exclude no rows and copy the original note unchanged. | Only this Markor task compares notes exactly; existing name fuzzy matching, thresholds and other expense tasks remain unchanged. Literal `Reimbursable.` inside an original note is ordinary note content, not a selection flag. |
| 076 `SimpleCalendarFirstEventAfterStartTime` | Strictly later start time, on the explicitly named date between 00:00 and 23:59. One existing-format hour draw derives query `{hour}:00` and relevant start `{hour}:30`; finite hours avoid rollover. All titles tied at the earliest qualifying start are requested. | Uses the existing IR formatter, IDENTITY expected-title rule and same-date exclusions, not a second generator. Old `time` parameters are not aliased to the new `hour` definition. |

The same-date start-only scope is the conservative choice: neighboring calendar IR tasks already bind `start_date`/`start_time`, and this generator excludes competing starts only on that date. The goal now states the scope rather than hiding a day-only interpretation. Strict `GREATER_THAN` exclusions remove same-date qualifying competitors/ties; the existing shared calendar helper also checks interval endpoints and can conservatively remove overlapping distractors. It was not changed; equality boundary fixtures use zero-duration point events. Future generated relevant state contains the unique earliest target; no hidden next-day search or threshold-equality answer is required.

**Identity and historical boundary:** these are new task definitions and generated instances. The frozen campaign, analysis receipts, manifests, parameters, original results and **83.1897%** are unchanged; no rescoring or device initialization was performed. A future evaluation requires a new manifest/task identity and fresh qualification under the normal launch policy. Do not treat the current modified checkout as the historical frozen oracle or reuse old076 params. Installed copies/build artifacts were not refreshed in this batch.

**First-batch parent/submodule ownership:** implementation and behavior tests are inside the `android_world` Git submodule (`android_world/task_evals/single/{audio_recorder,expense}.py` and their `_test.py` files; `android_world/task_evals/information_retrieval/proto/tasks.textproto` and `proto_utils_test.py`). Matching static descriptions in `android_world/task_metadata.json` and the existing [task guide](android_world/docs/tasks_guide.md) are synchronized. The first-batch parent change was this README only; third-batch parent implementation is described separately below. The submodule working tree is uncommitted; its Git commit/gitlink therefore does not yet identify these definitions. Subsequent integration requires separately authorized submodule commit/review, then parent gitlink update to that commit, and packaging/installation of that identity before qualification. No commit, push, staging, branch/protection change or dependency replacement was performed. Existing unrelated edits and generated protobuf files were preserved.

#### Narrow verification actually run once

```bash
env PYTHONPATH="$PWD/android_world" .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  android_world/android_world/task_evals/single/audio_recorder_test.py::AudioRecorderFileNameContractTest \
  android_world/android_world/task_evals/single/expense_test.py::ExpenseAddMultipleFromMarkorTest \
  android_world/android_world/task_evals/information_retrieval/proto_utils_test.py::CalendarFirstEventAfterStartTimeContractTest
```

Observed: **15 passed, 2 warnings in 0.35s**. Warnings were pydub `audioop` deprecation and missing ffmpeg discovery; no media encoder was needed or changed. The regression classes cover exact complete names versus aliases/missing files; CSV metadata/note separation and escaped/multiline notes; long polluted/stripped notes and wrong amount/category; every declared calendar date/hour, equality, strictly later, range and competing ties.

The same single command chain also ran a throwaway offline consumer script with `env PYTHONPATH="$PWD/android_world" .venv/bin/python -B <temporary-script>`. It imported this checkout, used real filename lookup against synthetic ADB response fixtures (no transport), actual CSV parsing/integrity validation, and actual IR formatting/exclusions/answer comparison. Observed:001 exact name1.0 versus doubled extension0.0;014 source102/selected2 with original notes accepted and metadata-polluted notes rejected;076 query21:00/target21:30, equality noise retained but not an answer, between-competitor excluded. The negative-note fixture emits the expected validator missing-row warning. The temporary script was removed after the successful smoke. This is offline contract proof, not shared-device/app validation, task initialization, a formal campaign, rehearsal, scoring or qualification.

Observed definition-source digests (not a substitute for a reviewed submodule commit or complete installed identity):

| Submodule-relative source | SHA256 |
| --- | --- |
| `android_world/task_evals/single/audio_recorder.py` | `f9a3a0143f711c9f111a372ce8ed27db93fe5d5788322f4f1425106ea529357f` |
| `android_world/task_evals/single/expense.py` | `2068db47b2e4681a6bf3adfaa639db431acf6a60c8b0523101f8eb6b7efabba9` |
| `android_world/task_evals/information_retrieval/proto/tasks.textproto` | `9442158ac415199aa6b6511e65626491c6dd325e601f572f9aa5012aa6ec15e4` |

030 metadata semantics,060 initialization and latent IR list matching remain separate work; no opportunistic fixes or experiments were included in the first batch. Private evaluator diagnostics and D01-D03 scoped closure are complete in source, as recorded below; deployment gates remain open.

### Post-evaluation implementation handoff — FSQ source portion complete

The [overall handoff](evidence/post-eval-fixes-20261110/handoff.md) and [machine-readable state](evidence/post-eval-fixes-20261110/handoff.json) separate source completion, independent external candidate work and deployment. **FSQportionComplete=true** for this evaluation repository's batches1 and3; neither installation/qualification nor all-three-batch completion is claimed. External AMKernel supplemental review does not block recording this source completion.

| Batch | Received evidence | Current acceptance boundary |
| --- | --- | --- |
| 1 — 001 / 014 / 076 contracts | Owner15passed plus offline consumer smoke; [independent contract review](evidence/post-eval-fixes-20261110/review.json) has no actionable source findings (P0/P1/P2 all zero). | Source work complete. G1/G2 future deployment gates remain open; no checks rerun by this update. |
| 2 — external AMKernel candidate | Original fixed OLD/NEW six-scene pair completed; candidate patch retained separately, not merged into the original tree. | Supplemental structured-recovery criterion review by w3:p3 pending, actualAttempts=0; no success-rate/cost-benefit or historical17case repair claim. |
| 3 — private evaluator diagnostics | Owner32passed (old26+new6), directed correction smoke; [independent closure](evidence/post-eval-fixes-20261110/review.json#/diagnosticsClosure) resolves D01/D02/D03. | Source work and targeted review complete. No new complete runtime/installed identity, manifest/readiness or fresh qualification is claimed. |

**Open P1 future-run gates, not contract-code findings:** G1: the first-batch review observed eight dirty tracked submodule files; submodule HEAD and parent gitlink both remain `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, and parent README is untracked. G2: the retained non-editable installed implementations, textproto and metadata differ from reviewed source. Source `PYTHONPATH` checks do not qualify installed consumers. Neither gate is fixed by this documentation integration: no staging/commit/gitlink update, package build/install or new manifest/qualification was performed. Any later authorized integration must capture the accepted source/package/import/task-data identities and use a new manifest with fresh qualification; old `time` params cannot be reused as new `hour` params. Review source-set digests describe the review-time bytes; this subsequent README-only integration changes README bytes without rewriting either independent review artifact.

#### Private evaluator receipt: source implemented and targeted review closed

The third-batch delivery changes `runner.py`, adds `evaluator_diagnostics.py` and adds `tests/test_evaluator_diagnostics.py`; this integration does not edit or rerun them. New-identity attempts default to an attempt-local `raw-private/evaluator-diagnostics.json`. It observes **existing** root/absl scoring-thread log records as bounded message templates/literal-argument projections, not newly rendered full log messages. It records evaluator exception type, bounded arguments and up to 16 frames without locals, the original scalar reward, task name/params hash, phase and start/end timestamps. It neither probes private task attributes nor queries a DB nor calls the evaluator again.

Capture begins only after the business Agent exits, adapter/session cleanup and protocol/submission checks (including any required `interaction_cache` setup). It spans the original single `task.is_successful(env)` call and ends on return or exception before task teardown. Filters are removed before sidecar writing. Initialization, Agent, recovery and teardown logs are outside this boundary. Only records reaching the existing root/absl filter points on that thread are visible; original logger levels, handlers and propagation are unchanged. Suppressed INFO/DEBUG, other threads/loggers, stdout/stderr and native output may be missing. Scoped privacy/source review is complete, but unchanged native sinks can still emit hidden values to their existing destinations; this is not an all-output confidentiality or OS/sandbox assurance.

The implementation reports a 0700 private directory and 0600 sidecar/temporary files, with atomic replacement. File size is bounded to65,536bytes; logs to49,152bytes/256records; each literal/type-name projection shares2,048characters/64nodes, depth3 and eight items per container. Type names are clipped to128characters before encoding; exceptions retain at most16frames without locals. Fixed schema labels and separately capped source/frame fields are outside that shared character count. Overflow, unsafe-object omission and capture failures are explicit. Trusted maintainers may read the private file offline; do not copy private contents into Agent prompts, tool responses, Skills, normalized events or public indexes.

The public result's `evaluator.diagnostics` contains only the receipt reference `{path, sha256, status, bytes}` for a persisted file. Status is `written`, `truncated` (including explicit argument omission) or `capture_error`. On write failure it contains `{status: write_failed, errorType}`, without a fictitious valid path/hash. Public evaluator exceptions retain only `{type}`, bounded to128characters through the hook-free helper; native details go to the private sidecar, with no public-detail fallback if writing fails. This reviewed output contract does not certify every existing log sink or OS/sandbox isolation.

`componentResults` explicitly says `not_provided` / `scalar_return_interface`; scalar rewards and native log text are not converted into invented Boolean/component scores. In particular VLC's 0.5 still does not identify which playlist subtask passed. Silent branches, final DB/device snapshots, full exception chains and historical unknowns (including 060/098/106 final-state gaps) remain unresolved. Historical attempts are not backfilled.

There is additional bounded projection/encoding work and local disk IO after scoring, before teardown. `evaluator.durationSeconds` excludes sidecar disk writing; the overall stage includes it. Byte bounds do not bound storage latency. **No zero-IO, zero-wall-clock-disturbance or performance-equivalence claim is made.** The delivery reports unchanged reward/terminal/cleanup behavior for the exercised offline paths; real runtime/device timing is unverified.

The original delivery recorded26passed/2warnings/0.44s after a fixture correction (initially7failed/19passed), plus five offline scenarios (`reject`, `pass`, `raise`, `silent`, `write_failure`). That evidence remains historical. After D01-D03 corrections, the same narrow command recorded **32passed/2warnings/0.51s, old26+new6**, once after corrections, plus directed root/absl-detach, pre-JSON long-type and hostile-metadata offline runner smoke. The later independent closure marks all three resolved; reviewer and this documentation owner did not rerun those checks. External device/process boundaries remain fixtures, not real-Agent/device proof.

#### Corrected source receipt and actual completion scope

Latest disposition: [review.json#/diagnosticsClosure](evidence/post-eval-fixes-20261110/review.json#/diagnosticsClosure); owner execution: [verification.json#/corrections/0](evidence/evaluator-private-diagnostics-20261110/verification.json#/corrections/0). The closure records matching corrected bytes below. It records verification.json file SHA256 `7e44cb90737500675277b7a837e0d7e2254a7bc1ece64cea749c1721e1ddf8bf` and implementation.md SHA256 `edb76403177d42154554ccb242a3d941c913385a658f32cc1f73b3790768b50a`; these are receipt-time values, not newly computed checks or a complete runtime identity. Old pending-review labels in the implementation receipt are superseded by the later closure, not rewritten.

| Reviewed corrected source | SHA256 from closure/corrections |
| --- | --- |
| `src/fsq_androidworld_eval/runner.py` | `a5864ca8edd0a00af6903ea27b4df84fb73630f6759de2105a9d463cb4fb766c` |
| `src/fsq_androidworld_eval/evaluator_diagnostics.py` | `d231b78432685fc61787a49a3a3cc3b0f31e7567498d90c33fce59192f80febc` |
| `tests/test_evaluator_diagnostics.py` | `95f091f2384889430aab4f00d839933f5fcd2946851ef98a7516f62b67d31977` |

D01 uses serialized copy-on-write filter lists so managed detach cannot skip another inflight capture. D02 bounds type names to128 characters and charges the shared projection budget before JSON encoding. D03 uses identity checks and builtin type-name access without user metadata hooks, including runner evaluator public error.type. Existing filters/handlers/order and native scoring/cleanup behavior are preserved within the reviewed boundaries; arbitrary third-party concurrent logger reconfiguration is not guaranteed safe.

`FSQportionComplete=true` means this **FSQ_AndroidWorld_eval repair source portion (batches1 and3)** is implemented, evidenced and independently reviewed; it does not mean the separate new FSQ task Agent has an AndroidWorld adapter or has been evaluated. Adoptable files are the eight first-batch submodule files described above and the three corrected parent files in this table. Documentation updates are confined to this README and the overall handoff. No further source change is requested by these scoped reviews. Deployment is incomplete and all-three-batch acceptance is not declared.

#### External AMKernel candidate — separate from FSQ source completion

Original delivery: [report](../amkernel/evidence/skill-boundary-ab-20261110T024711Z/report.md), [review-handoff.json](../amkernel/evidence/skill-boundary-ab-20261110T024711Z/review-handoff.json), [candidate.patch](../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate.patch), [candidate manifest](../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate-manifest.json). Candidate patch SHA256 as reported: `28a5506199f809e3315d95cddddbe844aac6a7c6bafd5b26d0dab7a49b4c1906`. Links point to the sibling repository; no patch is applied here or merged into the original amkernel tree.

| Original paired measure | OLD | NEW |
| --- | ---: | ---: |
| Business scenes passed | 6/6 | 6/6 |
| Python calls | 37 | 34 |
| Actions | 49 | 51 |
| Elapsed seconds | 293.626 | 349.422 |

All twelve original slots completed; this was synthetic loopback W3C UI via native Copilot CLI, not physical Android or formal OMP. There is no observed success-rate improvement or established overall cost benefit. Fewer calls are not assumed to outweigh more actions/time; tokens, monetary cost and actual provider model identity remain unknown. The candidate is retained only; it is not evidence that the historical17cases are fixed.

The independently registered structured-recovery supplement is awaiting `w3:p3` criterion review, **actualAttempts=0**. Original six-scene results do not qualify structured-result recovery. The coordinator will later append only actual supplemental evidence/conclusions; this external wait does not reopen or block completed FSQ repair source work.

#### Before any next enablement — separate authorization required

1. Obtain explicit deployment/resource authorization; choose accepted task definitions and protocol. Preserve historical manifests/results/83.1897%; scope completion alone is not launch permission.
2. Under separate Git authorization, review intended changes, commit the AndroidWorld submodule and advance the parent gitlink; include intended parent source/docs without sweeping unrelated/generated files. Capture actual commits and source hashes.
3. Build/install the accepted package identity separately; verify actual consumer imports and implementation/textproto/metadata bytes. Do not equate source PYTHONPATH proof with installed acceptance.
4. Capture the complete Harness/runtime/target/artifact identity, including corrected runner/helper. Check evaluator revision and migration admission policy; the old current_stack allowlist is not blanket approval of new AndroidWorld definitions. Any needed policy change requires separate authorization.
5. Prepare a distinct new manifest with approved definition/instance/protocol/runtime identities and fresh readiness/qualification in the authorized exclusive resource window; never rewrite or borrow old frozen evidence.
6. Run fresh non-scoring rehearsal and calibration required by the approved protocol, inspect actual identity/cleanup/evidence gates, and only then separately authorize a new campaign/output directory. No step is performed by this handoff.


All original formal results and evidence, including **83.1897%**, remain unchanged. No publish, commit, push, install, device/service operation, scoring, new campaign or qualification is part of this update. This FSQ repair source portion is complete now; only independent external supplemental conclusions and separately authorized deployment remain, not a pending internal D01-D03 review.

### Offline development checks

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_runtime_migration.py tests/test_campaign.py tests/test_scorer.py
```

These tests use temporary synthetic releases and no Android/Appium sessions.
They are not qualification, a rehearsal, a calibration, or evidence that the
forthcoming published AMKernel release works.

Inheritance tests use the checked-in, host-path-sanitized
`tests/fixtures/inherited_campaign.json`, not an ignored private campaign.
The fixture freezes the installed task metadata for each test and binds both
producer and independent-scorer source pins only inside that test process.
Production source/metadata drift checks and historical manifest bytes remain
unchanged.

Preparation verification (2026-11-09): the focused command above passed 300
tests with two existing pydub warnings. A real `prepare` CLI invocation against
a temporary synthetic release emitted and reloaded all 116 exact source specs
with r15, OMP 18.18.3 and the frozen model; same-version/different-byte OMP was
rejected before output creation. The first temporary CLI fixture lacked the
existing asset cache and failed closed; using a read-only reference to that cache
completed preparation without downloading or repairing assets. Temporary fixtures
were removed. An offline CLI recalculation of the historical complete baseline
matched its saved summary: 116 valid, reward sum 80, `fullValidScore=80/116`,
`officialScore=null`. No qualification, rehearsal, calibration or formal run was
started, and no new published-version readiness is claimed.

### Change record

- Added explicit `current_stack` release migration to existing inherited prepare,
  manifest reload and offline score audit. Strict legacy inheritance is unchanged.
- Added exact wheel/package/Skills and Runtime Python/dependency verification;
  retained original task/budget and named-forwarder-only environment constraints.
- 2026-11-10: implemented approved001/014/076 task-contract corrections in the AndroidWorld submodule; synchronized goal metadata, added behavior regressions and recorded one offline verification. New-definition identity only; historical83.1897% unchanged.
- 2026-11-10: integrated first-batch review and third-batch private-diagnostics implementation receipts into the working overall handoff. Preserve two open P1 future-run gates; second-batch real-Agent delivery and third-batch independent review remain pending. Documentation only; no tests rerun or launch authorization.
- 2026-11-10: superseded the earlier pending handoff with FSQportionComplete=true for reviewed batches1/3; recorded32passed and D01-D03 closure/latest hashes. External AMKernel paired delivery is recorded separately with structured supplement actualAttempts=0; deployment and all-three-batch acceptance remain unclaimed. Documentation/readback only; no checks rerun.
- 2026-11-14: recorded the repaired2 81/116 frozen-suite result and post-run resource release; isolated historical campaign tests from private files and stale SDK metadata. Full offline suite: 1196 passed, 1 skipped, two existing pydub warnings. Fresh offline native prepare/inspect and pinned official-Skill verification passed; no new live campaign was started.
