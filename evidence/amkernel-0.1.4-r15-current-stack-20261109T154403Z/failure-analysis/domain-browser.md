# Browser failure analysis — cases 003 and 004

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Full exact cell code, toolCall IDs, original structured PythonResponses, action ordinals/timestamps and evidence pointers: [domain-browser.json](domain-browser.json). Reproducible read-only probes and outputs: [domain-browser-queries.md](domain-browser-queries.md). Original evidence/source/configuration was not changed.

## Findings and confidence

| Case | Proven outcome / immediate cause | Root distinction |
|---|---|---|
|003 BrowserMaze | Zero reward; X stopped at (3,1), two Right moves short. Gate admitted20 UI actions and refused the next. Six native direction element clicks had no visible effect; coordinate touch did move X. | **Confirmed Agent behavior failure:** unverified six-action batch consumed recovery margin. **Unknown lower-level click mechanism**, not an AMKernel Runtime diagnosis. |
|004 BrowserMultiply | Zero reward; final81000, but page still displayed10/Click Me. No product input or Submit call; seven permits unused. Five immediate reads returned9,9,10,10,10, not established fresh generations. | **Confirmed Agent behavior failure:** collection freshness/phase and in-app completion were not established. **Unknown click/accessibility timing mechanism.** Native-only context denial is Harness policy, not Runtime bug. |

Both attempts have valid string submissions, no invalidReason, and clean session quit. Proposed fixes are not approved or implemented mechanisms. Loaded Skill already contains the required freshness, phase-aware wait, unverified-basis probe, and completion invariants.

## Shared oracle, initialization and dependency boundary

Official `android_world/android_world/task_evals/single/browser.py`:

* `BrowserTask.initialize_task:56–85` invokes base initialization, clears device storage and Chrome data, grants notification permission, substitutes `params.browser_task_seed` into inline HTML, and puts task.html in Downloads. Outer `params.seed` seeds Python initialization, **not** browser JavaScript. Chrome data clearing creates real cold-first-run overhead.
* `BrowserTask.initialize_device_time:49–54` enables automatic date/time. Both original prompts contain initialization reference2023-10-15T15:34:00+00:00, UTC; it is not live device time. Neither task is date-dependent.
* `BrowserTask.is_successful:98–109` obtains UI state and current package; reward0 unless package is com.android.chrome, then reward1 iff any UI element has exact text `Success!`. No partial credit, DB predicate, or chat-answer comparison.
* These classes inherit BrowserTask→TaskEval, **not MiniWoBTask**. The inline HTML has no external script/network requirement. MiniWoB uses another app and reward broadcasts (`task_evals/miniwob/miniwob_base.py:25–59,112–141`); that dependency is excluded. Chrome's No internet connection banner is not evidence the local puzzle is unavailable.

Harness `runner.py:716–737` finishes agent/owned-session cleanup **before** evaluator790–796; task teardown follows at821–826. Both agent `driver.quit()` calls return and audit has zero active sessions. Evaluator-time UI trees were not retained, so exact post-quit package/tree remains unknown. Both tasks are nevertheless unfinished **before** final/quit; no evidence supports successful task state erased solely by cleanup.

`submission.parse_submission:45–93` parses original JSON, requires nonempty string, strips whitespace, never coerces numbers. `omp_supervisor.py:211–234` selects first assistant stop before cleanup/cutoff. Maze first final raw line4067; Multiply line5205. Archived answers exactly match those first finals; later cleanup prose is ignored. For browser tasks even a correct numeric final cannot replace in-app solving.

Harness current19-input identity matches frozen hash861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66 (`shared-offline-checks.json#/sourceIdentity`). The same shared receipt covers prompt/parse/first-final precedence. AndroidWorld recorded revision55ddaf5edc6f6c25673aed343907d5b9dca66f84; inspected current browser.py SHA-2561f4befd3c069874861ac0144063b0d62e697dff418a82abd9801e25a350010cf. Assigned evidence lacks separately archived initialized HTML or a frozen per-file browser.py checksum. Source-derived state is labeled accordingly and checked against retained UI where available.

## 003 — BrowserMaze

### Exact request and randomized board

Goal: “Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.” Actual raw original goal/control prompt is JSONL line9, fully reproduced in JSON. Params: browser_task_seed1364588068, outer seed3308742614. Complexity2 allocates20 interactions (`suite_utils._allocate_step_budget:491–502`).

`BrowserMaze.HTML:181–247` uses a32-bit LCG and randomized DFS-like stack ordering. Exact extracted JS with actual seed produces this board, matching **all16 visible cells** in retained screenshots (zero-based row/column):

```text
X . # #
# . . .
. . . .
. . . $   ($ is green goal)
```

Walls=(0,2),(0,3),(1,0); start=(0,0); goal=(3,3). Full topology is **known**, not extrapolated from incomplete accessibility. Shortest path R,D,D,D,R,R is six moves. Source-only exact JS probe reaches(3,3) and replaces body with `<h1>Success!</h1>`. Moves must stay in bounds and avoid walls (`browser.py:278–320`). The six-step attempted route was correct; no wall/path error explains no movement.

### Historical execution and complete action accounting

The raw JSONL is under `campaigns/.../episodes/003-BrowserMaze/attempt-1/raw-private/agent-events.jsonl`.

| UI ordinal | Execution / tool start–end lines | Action and evidence |
|---|---|---|
|1 |4 /1028–1029 | Touch swipe to drawer. |
|2 |5 /1168–1169 | Files; Downloads/task.html visible. |
|3 |6 /1342–1343 | task.html; subsequent observation fails StaleElementReference, but click already admitted. Call7 confirms resolver. |
|4 |8 /1642–1643 | Just once; Chrome Welcome/FirstRunActivity. |
|5 |9 /1832–1833 | Accept & continue; waiting for activity change times out. Call10 shows Turn on sync? in same activity. |
|6 |11 /2132–2133 | No thanks by negative_button; activity wait times out. Call12 still sync prompt. |
|7 |13 /2465–2466 | No thanks by observed text; returns to Files. |
|8 |14 /2739–2740 | Reopen task.html; resolver. |
|9 |15 /2915–2916 | Just once; Chrome search-engine promo. |
|10 |16 /3018–3019 | Keep Google; reaches maze. |
|11–16 |20 /3699–3701 | UiSelector text `.click()` R,D,D,D,R,R; completed/alive; six gate HTTP200 actions; screenshot **still X=(0,0)**. |
|17 |21 /3777–3779 | `driver.tap([(490,880)],100)` on observed Right center; screenshot **X=(0,1)**. |
|18–20 |22 /3961–3962 | Three coordinate Down taps admitted; next Right request refused by closed gate. Second planned Right never invoked. |
|rejected21 |22 /3961–3962 | Not an executed action. Rejection count1, executedActionCount20. |

24 python_exec cells,18 completed/6 failed, **all kernelState alive**, under advisory30. Call3's invalid appium.webdriver.common.actions import fails before UI request: zero permits. Corrected Selenium import call4 succeeds. Call17's WEBVIEW context selection fails before UI gate. Read-only call23/4018–4020 after refusal shows X=(3,1), goal=(3,3), no Success!, exactly two Right moves short. No further UI mutation is attempted. Final line4067 truthfully reports incomplete; call24/4135–4136 quits.

Budget sum:10 navigation/onboarding +6 unproductive direction element clicks +4 productive touches=20. Denied coordinate tap is not an accepted21st step. Policy denial is not the same counter as step-budget rejection. Two10-second activity waits are time cost, not extra UI actions.

### Locator, timing and policy distinctions

Call19/3498–3499 exposes native button labels/bounds: Up[8,842][115,918], Down[124,842][276,918], Left[283,842][409,918], Right[418,842][562,918]. Right touch(490,880) and Down(200,880) are inside observed controls. Six element clicks leave start unchanged; subsequent right touch visibly moves. Thus semantic click delivery was not established before widening. No per-click on-device dispatch trace distinguishes native accessibility click behavior, delayed dispatch, or other Appium/Chrome event effects. Coordinate success is page/geometry-specific evidence, not a universal fallback mandate.

WEBVIEW_chrome appeared in driver.contexts; call17/3226–3227 failed `UnknownMethodException: Only native Android context is supported`. Exact string comes from `AppiumAuditProxy._authorize`, appium_proxy.py878–880. Prompt explicitly requires native interactions. This is **intentional Harness policy**, not kernel failure, broken Chromedriver readiness, or proof AMKernel lacks WebView support. No setup repair follows from that refusal.

FirstRunActivity hosts multiple pages: call9 timeout is reconciled by fresh Turn on sync? state. Call11 timeout followed by same prompt is real no-observed-progress, but does not prove why dismissal did not land. Phase predicates avoid invalid activity-only waits; that alone does not recover the six wasted maze permits.

### Cause and proposed fixes

**Confirmed proximate cause:** gate closure two moves short. **Confirmed behavior root:** six-action batch used unverified input and consumed recovery margin. Loaded amkernel-appium.md (raw read end96, embedded text114–150; current source113–149) already requires probing unverified basis, business change rather than HTTP success, reconciliation before retry, and stopping dependents on divergence. No missing Skill rule is established.

**Proposed adherence change, not implemented:** define X-position postcondition, use first intended move as small probe, inspect effect, widen only after delivery is reliable. If unchanged, distinguish pending from ineffective input using fresh bounded evidence before an evidence-backed touch. Count remaining actions. Ten startup +six effective moves fits20 with four permits spare; **counterfactual ledger, not rerun result**. Do not blanket-convert element clicks to taps or blindly retry late clicks.

**Decision-needed prompt clarity only:** runner.PROMPT_TEMPLATE could distinguish advertised WEBVIEW contexts from native-only permitted selection. This avoids a failed observation, not a consumed UI step, and does not diagnose no-effect clicks. Prompt changes affect future comparison identity.

## 004 — BrowserMultiply

### Exact request, state machine and collection boundary

Goal: “Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.” Original raw prompt line9 is fully retained in JSON. Params: browser_task_seed3143940091, outer seed1325351943. Complexity2.2 ->22 UI permits.

Conditional deterministic reconstruction from inspected current inline source and the recorded JS seed (`browser.py:393–439`), **not captured historical JavaScript state**:

```text
on load:       9
successful1: 10
successful2:  9
successful3:  5
successful4:  5
successful5: no new number; hide Click Me/number, reveal form
product:      20250
```

In that source-only reconstruction, LCG integer states are3646770462,4208185829,3727612416,2041316703,2056655666. Initial9 is actually captured at calls15/17. The remaining array and product20250 are conditional on initialized task.html matching the inspected current source; initialized HTML and historical live numbers[]/clickCount are unarchived, so the historical full generated array/product remain unknown independently of that assumption. Current source includes initial load in the collection and legitimately generates repeated final5 values, so a universal wait-until-value-differs is invalid. In the **offline current-source probe only**, checkAnswer accepts20250 and rejects81000. Confirmed historical noncompletion instead rests on observed reads9,9,10,10,10, persistent Click Me phase, and no input/Submit.

### Actual collection, phase and complete ledger

Raw path: `episodes/004-BrowserMultiply/attempt-1/raw-private/agent-events.jsonl` under same campaign.

| UI ordinal | Execution / raw tool lines | Action and evidence |
|---|---|---|
|1 |4 /979–980 | Drawer swipe. |
|2 |5 /1179–1180 | Files. |
|3 |6 /1395–1396 | task.html. Package resolver but immediate source still Files: cross-transition mismatch captured. Call7 fresh source confirms resolver. |
|4 |8 /1843–1844 | Just once; Chrome first-run. |
|5 |9 /2060–2061 | signin_fre_dismiss_button click; activity-change wait times out. Call10 still first-run. |
|6 |11 /2522–2523 | Observed displayed/enabled dismissal clicked again; returns to Files. |
|7 |12 /2836–2837 | Reopen task.html. |
|8 |13 /3047–3048 | Just once; search-engine promo. |
|9 |14 /3393–3394 | Keep Google; then context switch policy denial. Click counts, denial not UI action. |
|10–14 |18 /4538–4539 | Five UiSelector text Click Me clicks, each followed **immediately** by reading resourceId(number). Returns[9,9,10,10,10], product81000; controls still10/Click Me. |
|15 |20 /5016–5017 | Swipe upward looking for form; still10/Click Me. |

Only15/22 permits used; rejectedUI0. ReferenceStepsExecuted16 includes finish detection, not hidden extra mutation. Termination completed, **not exhaustion**.22 python cells (18 completed/4 failed), all alive. Missing lxml import call2 fails before observation; standard library XML parsing call3 succeeds. Call16 ID(button) lookup fails **before** click, zero permits; call17 confirms one native text control plus number9 via direct UiSelector. No form focus, input value, clear, send_keys, Submit, or achieved-success action exists in complete ledger.

Call18 original structured result includes Python numbers=[9,9,10,10,10], product81000, number TextView10, Click Me Button focused=true, and only EditText Chrome url_bar. Full original result in JSON includes bounds/flags/content URL. This is **Agent's Python list**, not a JS state dump: five reads do not prove five acknowledged generations. Multiplication is correct for that list; collection is unproven and source-inconsistent.

Fresh page source call19/4778–4779, post-swipe call20/5016–5017, screenshot call21/5186–5188 all continue to show10 and Click Me; no product edit/Submit. The only observed EditText is the Chrome address bar. Screenshot establishes unfinished pre-form state, not completion hidden behind an off-screen form. Agent nevertheless emits `{"taskOutcome":"81000"}` line5205, then cleanly quits call22/5287–5288. Format-valid chat output cannot satisfy in-app oracle.

### Locator/timing explanation and confidence limits

Source exposes bare HTML ids button/number through native accessibility. AppiumBy.ID(button) lookup failed, while UiSelector text Click Me and resourceId(number) succeeded. UiAutomator2 ID auto-qualification is **plausible, not proven**; actual lookup normalization/config was not retained. No AMKernel parser/kernel bug is established.

Five element-click requests HTTP200, reads9,9,10,10,10 never reach form. Ineffective/delayed native clicks and stale accessibility reads are alternatives; per-click browser events/source timestamps are missing. Under current source/no-reload assumptions, final10 is consistent with only one effective generation advance, but exact live clickCount is **unknown**. **Confirmed:** requested five clicks did not establish the five-click phase transition; fresh source and final screenshot retain old controls. **Not confirmed:** specific Runtime/Appium/Chrome/accessibility-cache defect.

WEBVIEW denial at call14 has the same exact native-only Harness-policy origin as Maze, after charged Keep Google. Native source stayed observable, kernel alive. No unrestricted WebDriver route, arbitrary script, or new session was authorized or needed to explain score.

### Cause and proposed fixes

**Confirmed immediate/behavior root:** agent substituted repeated immediate reads for acknowledged generation, omitted initial number in collector, then stopped without entering/submitting despite seven unused permits and visible pre-form state. Not budget shortage or pure multiplication error. Existing loaded Skill explicitly says reads do not prove freshness, values may legitimately repeat, retain initial disappearing task data, and verify phase—not stable label/activity.

**Proposed adherence change:** preserve initial visible value, establish interaction efficacy, acknowledge phase without requiring numeric difference, require fifth-click button/number disappearance plus input appearance. If freshness is unresolved retain uncertainty, not guesses/replays. Then input product, Submit, observe Success!. Do not hardcode diagnosis-derived20250 into future agents. Nine startup +five puzzle clicks +one input +Submit fits22, excluding extra focus/recovery; no future success claimed.

**Decision-needed wording:** BrowserMultiply.goal336–342 could say remember initially displayed number plus each subsequent generated number, then after five clicks enter product. Existing goal can be correctly interpreted from app flow; benchmark wording change affects comparability and does **not** repair ineffective clicks or missing submit. No oracle implementation bug demonstrated.

## Evidence gaps / hand-off

Maze topology is complete. Multiply expected source sequence uses actual seed, but runtime JS variables/initialized HTML not independently archived. Internal native-click delivery, per-click freshness and evaluator-time UI after quit remain unknown, not Runtime-fault conclusions. No device/API calls, formal task/score reruns, tests/builds/linters/formatters were run. Only recorded offline queries/probes exercised. No temporary scripts created. Proposed behavior/prompt changes are unimplemented/unapproved; independent amkernel-owner mechanism analysis remains separate. Parent may validate report JSON/schema/cross-case integration after all domain reports land.
