# System / SMS failure diagnosis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope: **085 SimpleSmsSendClipboardContent** and **098 SystemBrightnessMaxVerify**, attempt1 only. These are diagnosis documents, not product/configuration/test fixes. Original result, normalized event, business submission and raw event files were read only. No device, ADB, Appium, MCP execution, formal task/scoring rerun, build, formatter or test suite was invoked. Retained screenshots were decoded in memory; no new screenshot was captured.

## Findings at a glance

| Case | Proven outcome | Strongest causal finding | Root confidence |
|---|---|---|---|
| 085 | Official0; never got beyond recipient entry, no message-body/paste/send operation in trace; honest inability final | Six initial UI permits did not advance requested app flow; recipient presence was accepted without confirmed composer; all12 permits consumed. Appium clipboard helper failed independently, but is not a demonstrated Runtime cause. | **Confirmed behavior/planning failure**; underlying helper root unknown |
| 098 | Official0 despite success final; only3/10 permits used | Literal `root.iter('node')` hid native class-tag UI semantics; Agent unnecessarily dragged an already visually-max slider to x976 inside its own stated x1038 right bound, then accepted a screenshot as exact maximum. | **Probable endpoint regression**; exact final integer unknown. Parser/acceptance bug confirmed. |

Outcome confidence and root confidence are deliberately separate. Reward0 is not a substitute for provider rows, exact settings output, or component subscores. The companion JSON contains complete structured records, exact executed code, original structured Python response facts, full toolCall IDs, source anchors, timeline/ledger, proposed fixes, falsification conditions and unknowns.

## Paths and provenance

- `C = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`
- `A085 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1`
- `A098 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1`
- `A097 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/097-SystemBrightnessMax/attempt-1` (targeted same-campaign successful mechanism counterexample only).
- Shared Appium log: `evidence/screenshot-video-controls-20261106T231029Z/appium.log`. The campaign service receipt `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/service-receipt.json:13-17` identifies that service/log. Queries below are limited to owned sessions `fb607e05-8328-496b-b945-d7384303e186` and `d5ecafcc-25b3-4721-af53-e79c6bbdb9fc`; other campaigns in that shared file are out of scope.
- Both results record AndroidWorld0.1.0 at revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, AMKernel0.1.4. Device readiness records Android13/API33,1080x2400, UTC; no live readiness checks were performed here.
- Parent receipt `shared-offline-checks.json:1081-1088` proves current19-file Harness digest equals frozen manifest digest `861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`. Its per-case archive checks establish exact goal/reference clock/string contract and faithful first-final parsing. AndroidWorld task/helper code cited here is current checkout code; this domain did not independently hash every task file against a frozen snapshot. Installed UiAutomator2/Settings helper source is explanatory current local source, not a byte-attested historical snapshot.
- Raw `tool_execution_start.args.path` is `xd://mcp__amkernel_python_exec`; `args.content` holds actual code. Paired `tool_execution_end.result.content[type=text]` holds the returned structured Python result. The raw tool events have no timestamp; JSON labels the immediately preceding assistant-message timestamp as such. Appium log timestamps below have no encoded timezone and are not silently converted.

## Case 085

### Exact request, initialization and oracle

Visible goal (raw `A085/raw-private/agent-events.jsonl` message_end **line9**; `result.json:877-890`):

> Send a message to +15459061746 with the clipboard content in Simple SMS Messenger

Hidden task params: recipient `+15459061746`; expected clipboard body **`I think, therefore I am.`**; seed3566412234. The body is a report of task parameters, **not an Agent-observed clipboard read** and was not in the visible goal. Reference clock was explicitly visible:2023-10-15T15:34:00+00:00, timezoneUTC.

Source `android_world/android_world/task_evals/single/sms.py:158-170` specifies this goal and calls parent initialization followed by `adb_utils.set_clipboard_contents(params['message'])`. Parent `common_validators/sms_validators.py:176-180,234-253` turns airplane mode off, deletes SMS and thread rows in `/data/data/com.android.providers.telephony/databases/mmssms.db`, checks that the target message was not already sent, and waits5seconds. Base `task_eval.py:142-157` initializes clock/apps and seed. Initialization completed7.938seconds; **no actual initialized clipboard readback or SMS rows are archived**.

`adb_utils.py:1208-1238` sets clipboard via foreground **Clipper** package `ca.zgrs.clipper` (`adb_utils.py:126`), `clipper.set` broadcast and text; it parses returned broadcast data, then Back. The comment at1213-1215 warns emulator host clipboard synchronization can overwrite contents; this is a possible environment mechanism, **not observed here**. AndroidWorld's own getter at1143-1174 uses Clipper and `clipper.get`; it is not the getter the Agent attempted.

Exact official check (`sms_validators.py:93-152,211-217,255-276`):

1. Query `shell content query --uri content://sms/sent`.
2. A row must have address,body,date. Address has spaces/dashes removed and must equal `+15459061746`.
3. Body must fuzzy-match `I think, therefore I am.`. `fuzzy_match_lib.py:20-50` lowercases by default and requires `difflib.SequenceMatcher(...).ratio() >=0.9`.
4. Device-current time (`shell date +%s`, integer seconds*1000) minus SMS row date must be <=300000ms. There is no coded lower bound, but no future-date issue is evidenced in this attempt.
5. Current active package must be **`com.simplemobiletools.smsmessenger`**, regardless of app-agnostic sent-provider rows. Default Google Messages is not an equivalent app under this oracle.
6. Current UI text beginning `Sending` raises instead of returning0 (`:289-295`). No such exception was recorded.

Reward is the conjunction, no saved component subscores. This is a state task, not IR: the truthful inability final is a valid business envelope but does not itself produce reward0; the evaluator independently reads state.

### Constraints and first divergence

The initial prompt requires official Appium Python Client/UiAutomator2, one retained session, `noReset=True`, `autoLaunch=False`, `skipUnlock=True`, `newCommandTimeout=300`, session-creation execution timeout90, native interactions only, no shell/app-data APIs, exact12 UI-step limit, advisory30 Python calls, business840seconds, and no undo of requested final state. A forwarded failed UI action consumes a permit. Observations and quit remain available after closure; first business final wins; cleanup cannot replace it.

**First divergent action:** cell3 clicks launcher text `Messages` (raw731-732; Appium560179) and returns `com.google.android.apps.messaging/.ui.ConversationListActivity`. The Agent's raw assistant message_end730 explicitly wonders whether this could be Simple SMS. It was not. Cells4-8 then spend Back,drawer swipe,focus search,type search,and clicking the exact search text. Cell9 proves that exact text is the **search `android.widget.EditText`**, bounds`[214,156][886,301]`, not an application result. The correct app is finally activated in cell10, the seventh UI action.

### Complete executed-cell sequence

All19 returned executions have `kernelState=alive`:14completed,5failed. Failures are cells4,8,12,15,18, not loss of the Runtime. Full exact code and original response fields are in JSON.

| Python cell | Raw start/end lines | Call ID prefix | Original status / kernel | Bounded fact |
|---:|---|---|---|---|
| 1 | 328/329 | `call_N4CeCJ3kmvfuPKv7Dp9ZVKP7` | completed / alive | One noReset, autoLaunch=False session; launcher package. |
| 2 | 553/554 | `call_sOwAPSgxkH1sN6rOYYHpo9x0` | completed / alive | Launcher text/description observation. |
| 3 | 731/732 | `call_mSnQGIFPNbDPb1B4qhXOenyi` | completed / alive | Messages click opened Google Messages. |
| 4 | 1022/1023 | `call_oNAtJweIEWP0lkkQgf328IKj` | failed / alive | Back + drawer swipe; exact app-name wait timed out. |
| 5 | 1166/1167 | `call_CfvokTyCsszlkO41ke3V7pGu` | completed / alive | Drawer contains Clipper/Messages; no exact app label observed. |
| 6 | 1514/1515 | `call_TsnCkqvTJRr7zAaNaHEWPZHX` | completed / alive | Search input got name; suggestions and exact input text returned. |
| 7 | 1687/1688 | `call_S6z3GP9uefthPujpnTUnFB1d` | completed / alive | Tuple-list inspection became bounded repr, not explicit attributes. |
| 8 | 1786/1787 | `call_ywjUXwNY2wZKW3ymPdCtAAnp` | failed / alive | Clicked search EditText; package transition timed out. |
| 9 | 1941/1942 | `call_tLgAEJHz8JkmOLiTONBiRQPB` | completed / alive | Exact name is android.widget.EditText at [214,156][886,301]. |
| 10 | 2048/2049 | `call_itEdpfwaR3g8WH8sWpsH2hB9` | completed / alive | Activated com.simplemobiletools.smsmessenger. |
| 11 | 2338/2339 | `call_IVx9O6QvKPwf4sgzZaXk59kl` | completed / alive | MainActivity, no stored conversations, Start a conversation. |
| 12 | 2662/2663 | `call_Zg79XfnNC7hHmrdahqeJYQ9x` | failed / alive | Clipboard getter failed first: Settings helper not running after5000ms. |
| 13 | 2982/2983 | `call_kkKlMjm4v7D3lWQbMfOFRnfv` | completed / alive | Start a conversation; NewConversationActivity and number EditText. |
| 14 | 3226/3227 | `call_z4g0WTPMGbcIFMre3mI06KxX` | completed / alive | Number+newline became number+space; same activity. |
| 15 | 3428/3429 | `call_mevVQxhWOMW6zigk5sHW2BgX` | failed / alive | KEYCODE_ENTER returned but page-transition wait timed out. |
| 16 | 3606/3607 | `call_AHWMXxE0AhPKxBXRSBAjVtPV` | completed / alive | Same recipient page/number+space; no composer. |
| 17 | 3800/3801 | `call_A0elllHAEZLLwSjFn0riK0XY` | completed / alive | KEYCODE_DEL removed trailing space; no composer. |
| 18 | 3899/3900 | `call_UNMJ0WhOX9gXg2rGpPV8heWQ` | failed / alive | Editor Done failed upstream500; consumed final permit. |
| 19 | 4054/4055 | `call_YwrKNSyJxoNZxHPXe87RThtl` | completed / alive | Dedicated driver.quit returned true. |

### Actual action ledger

`result.json:791-870` provides the sanitized12-action ledger. Locator/body attribution comes from raw code plus Appium requests, not guessing from sanitized kinds. **No budget-denied action exists**: rejectedActionCount0. The final admitted editor-action command returned upstream500 and spent step12.

| Step | Cell | Action | HTTP | Appium log line |
|---:|---:|---|---:|---:|
| 1 | 3 | Click launcher Messages; actual Google Messages, not requested app | 200 | 560179 |
| 2 | 4 | Back to launcher | 200 | 560189 |
| 3 | 4 | Swipe app drawer | 200 | 560197 |
| 4 | 6 | Focus launcher search field | 200 | 560539 |
| 5 | 6 | Type Simple SMS Messenger into launcher search | 200 | 560551 |
| 6 | 8 | Click exact-text search EditText, not app result | 200 | 560772 |
| 7 | 10 | Activate com.simplemobiletools.smsmessenger | 200 | 561098 |
| 8 | 13 | Click Start a conversation | 200 | 561274 |
| 9 | 14 | send_keys recipient plus newline | 200 | 561386 |
| 10 | 15 | KEYCODE_ENTER (66); no stage transition | 200 | 561483 |
| 11 | 17 | KEYCODE_DEL (67); remove trailing space | 200 | 561643 |
| 12 | 18 | mobile: performEditorAction done; upstream500 | 500 | 561705 |

Breakdown:6 wrong-app/launcher-search actions;1 correct activation;1 start-conversation;1 recipient input;3 recipient confirmation/correction key attempts; **0 message-body input,0paste,0send**. Cell12's getter is an observation in the gate ledger, not an accepted UI action, despite driver-internal helper startup effects. Native-driver hidden effects and reference-step semantics are a comparability caveat, not the cause of the six earlier route actions.

### Clipboard and recipient branches: what actually failed

**Clipboard:** cell12 fails at its **first** statement, `clipboard_text = driver.get_clipboard_text()`. The following click in that same cell never executes. Original structured error is `selenium.common.exceptions.WebDriverException: Appium Settings app is not running after 5000ms` (raw2663). Appium561269-561271 confirms `mobile: getClipboard` returned500 after5101ms. It is not a returned empty string and does not prove a copied value was absent or initialization failed.

Explanatory local source:

- Python client `.venv/.../appium/webdriver/extensions/clipboard.py:70-95`: `get_clipboard_text()` -> `mobile: getClipboard` -> base64 decode.
- Installed `~/.appium/node_modules/appium-uiautomator2-driver/lib/commands/clipboard.ts:7-12`: API>=29 -> `settingsApp.getClipboard()`.
- `node_modules/io.appium.settings/lib/commands/clipboard.ts:16-30`: `requireRunning(shouldRestoreCurrentApp=True)` happens **before** clipboard broadcast and temporary IME context.
- `node_modules/io.appium.settings/lib/client.ts:78-133`: launches Settings helper, waits up to5000ms for service dumpsys output containing `isForeground=true`, then throws that error. This predicate proves the local failure class, not whether the service really failed to start, its permission/OS cause, or an erroneous detection predicate.

The Agent did not force-start shared services or create another session, which is correct. Cell13 succeeds in opening a conversation with the same live driver. No later clipboard read, Clipper UI inspection, native paste, or message body is captured. Getter failure is a real contributing blocker for that strategy, but **not a demonstrated AMKernel Runtime defect and not a sufficient explanation for earlier budget loss or missing recipient confirmation**.

**Recipient:** cell14 sends `'+15459061746\n'`. Returned text is `'+15459061746 '` with trailing **space**, still `.activities.NewConversationActivity`. Its wait is `activity_changed OR number_text_present`; the second condition becomes true from typing alone, so that wait does not validate recipient acceptance. Cell15 KEYCODE_ENTER returns but its activity-change wait times out. Cell16 shows the same recipient EditText and `No contacts found`; cell17 removes the trailing space but still shows only recipient entry. Observations filter for text or non-null contentDescription, potentially excluding a visually meaningful unlabeled confirmation control; **the full source/screenshot for this stage was not retained**, so no exact Next/arrow control is invented here. Cell18 `mobile: performEditorAction done` receives a sanitized500; underlying exception details are unknown.

### Submission, cleanup and persistence boundary

Finalization starts175.402140s after Agent start; first business final at180.648145s is raw event3936, before295.402140s finalization deadline. It says unable to send. Duplicate event3969 is ignored; cleanup prose4070 cannot replace it. The exact valid envelope and stripped answer are archived in `business-submission.json`; no type coercion/clock/first-final error is implicated.

Cell19 only retains ID,quits,and returns `quitReturned=True`. Appium561707-561711 returns DELETE200 and subsequent same-session GET404. There is **no agent Back/home/restore operation**. Harness `runner.py:716-737,790-826` and formal stage timestamps show quit/cleanup precedes evaluation; task teardown starts **after** reward. There is no post-quit package/DB readback in the domain evidence. Last observed package is correct; last page is recipient entry. Aggregate0 does not identify a particular missing provider row or package subcondition. No sent-provider rows are persisted in evidence, and no Sending exception occurred.

### Causal conclusion and proposed targets

**Confirmed behavior failure:** under the fixed budget, identity discovery and phase acceptance spent the task's mutations before any body/send. The newline-as-confirmation and number-present wait are concrete Agent-authored mistakes, not a Runtime locator translation failure. Outcome is confirmed; exact final database state remains unknown.

**Helper root unknown:** Settings foreground-service readiness failed. Missing historical service/logcat/error details prevent attributing its underlying cause. The structured failed response plus subsequent alive calls contradict a generic dead Runtime explanation.

**Proposed only, not approved fixes:** refine existing Android app-identity/stage examples and whole-outcome budgeting in `.agents/skills/amkernel/references/android-execution.md`; do not assume text equality proves app launch or recipient confirmation; retain contentless actionable controls before claiming no route. Existing **loaded** guidance already says similar icon/search echo is not target proof (raw tool-end55 embedded lines42-46), helper failure is symptom (embedded253-257), native shortcuts may be literal, and budget must include recipient/send/readback (embedded271-275); raw tool-end32 embedded170-173 and54 embedded344-352 cover acceptance/reservation. Thus a lack of core Skill guidance is **not established**. Helper/prequalification changes are **decision-needed** pending exact service evidence; do not force-start services, change capabilities, expand12steps, or leak hidden clipboard body into the prompt. No claim is made that saving the six wrong-route actions alone guarantees completion within12.

## Case 098

### Exact request and oracle

Visible goal (raw `A098/raw-private/agent-events.jsonl` message_end **line9**, `result.json:687-699`):

> Turn brightness to the max value.

Params `max_or_min='max'`,seed770927068. Reference clock/timezone exactly as above. The `Verify` subclass is an initialization distinction, **not** visible task text requiring needless mutation. It initializes maximum already: `system.py:74-86` calls `adb_utils.set_brightness('max')`; `adb_utils.py:971-1001` executes **`shell settings put system screen_brightness 255`**. The code shown does not set `screen_brightness_mode`; actual formal initial integer/mode readback is missing. Initialization completed0.478s. Earlier same-campaign harness rehearsal for this exact params hash returned initialStateReturn1.0 (`harness-rehearsal/tasks/098-SystemBrightnessMaxVerify/result.json:11-14,65-68`); this supports feasibility, not the formal attempt's precise initial state.

`_SystemBrightnessToggle.is_successful`, `system.py:41-52`, executes **`shell settings get system screen_brightness`**, decodes/strips, converts toint, returns1 iff the integer is **exactly255**. It does not read answer text, screenshot appearance, gamma-slider text, UI percentage, or automatic mode. There are no subscores. Under that cited normal-return code, reward0 implies comparator input was not255; the actual int was **not archived** and must not be reconstructed from a bar picture.

### Complete sequence and observed source mismatch

One session,8returned executions:7completed,1failed, allalive. Failure is a package-based wait, not failure to open shade. Business720s, UI budget10, advisory30calls; no deadline/exhaustion.

| Python cell | Raw start/end lines | Call ID prefix | Original status / kernel | Bounded fact |
|---:|---|---|---|---|
| 1 | 372/373 | `call_2IRGIsBUKVVzs9YHen6YRtBs` | completed / alive | Session created; launcher package. |
| 2 | 658/659 | `call_omANCz30h7PAIbugiMZYlnvP` | failed / alive | open_notifications succeeded; package-based wait timed out. |
| 3 | 940/941 | `call_ucQam18eqnF34lZfaFCtnmcu` | completed / alive | root.iter(node) produced items0 while /source was88838bytes. |
| 4 | 1088/1090 | `call_BYkwn2J7WwN1rqhxcrGgHynH` | completed / alive | Retained image proves notification shade; dict result bounded repr. |
| 5 | 1343/1345 | `call_TRdmiy2a3g7ZeaID62hBfZUp` | completed / alive | Expand shade; image appears already max/near max. |
| 6 | 1644/1645 | `call_4837cMLJuki8KqT3rpq0F8ha` | completed / alive | root.iter(node) again produced controls0, nodeCount0; source77170bytes. |
| 7 | 2138/2140 | `call_baV9f0v2QrsSLeEUCmIfTIgR` | completed / alive | Swipe x300->976 at y420; image appears full/near full, no numeric value. |
| 8 | 2330/2331 | `call_57gjZU69gBi7d7MEgAZ6APSU` | completed / alive | Dedicated quit returned true. |

Appium588620-588643 shows `mobile: openNotifications` returned200, followed by repeated `getCurrentPackage` with launcher identity. The later screenshot proves the notification shade was open; foreground app identity is not a reliable overlay-stage predicate.

Cells3,4,6 call `ET.fromstring(driver.page_source).iter('node')`; they return0items/0nodeCount. This is **not evidence of an empty page source or broken accessibility**: Appium588651 and588661 show88838-byte source responses;588673 shows77170bytes after expansion. Targeted neighbor097's retained native source prefix (raw3291) has tags `hierarchy`, `android.widget.FrameLayout`, not `<node>`; its actual slider tag is `<android.widget.SeekBar ... text='65535.0' ...>`. The exact-tag parser convention is wrong for the observed native serialization. Formal098 source bytes themselves were not archived, so the exact count/value of its slider cannot be retroactively recovered. The unobserved XML must not be called an empty driver tree.

### Screenshots, intent and actual mutation

Retained images were decoded from paired original tool-end `content[type=image]` in memory, no new capture:

| Cell/raw line | Original image SHA256 | Bounded observation and interpretation |
|---|---|---|
| 4/1090 | `1c3f34b6e4b96d8ceb2941cf108cdd27e7d0aa50c326aa6fa720dbad1de42ef1` | Notification shade visible; Internet/Bluetooth/notifications. This contradicts using launcher package alone to call shade opening unsuccessful. |
| 5/1345 | `ea75cdea7c5bc7c32ee2395daecd17b6d5f3769671288bb93f86393d66e8dffd` | Expanded quick settings; broad light-blue brightness bar near y420. Agent explicitly described it as already max. Numeric255 cannot be proven visually. |
| 7/2140 | `ba9fda334a27069e02d2a7abad90cd00a38980b08bdad3e1a711c24886347b0a` | Same expanded panel and gesture trace ending x976,y420 near sun/thumb graphic. Visually full/near full; no exact property readback. |

Agent message_end1643 says thumb centerx976 and fill across full bar indicates **already max**. Message_end2137 says no action might be necessary, but elects to drag from left to presumed maximum. Exact cell7 code comments track boundsx42..1038 and calls `driver.swipe(300,420,976,420,500)`. Ending atx976 is62pixels **inside** its own stated right bound1038. All returned auxiliary screenshot dicts contain a tuple imageSize and are represented as bounded repr; actual images were delivered. That serialization fact does not prove a Runtime cause for slider placement or predicate failure.

The first **consequential mutation divergence** is this unnecessary interior drag after observing already-max appearance. It was not caused by budget pressure and was not followed by a semantic value/range check. This can move an initialized exact endpoint to a visually similar near-endpoint state. That mechanism is **probable**, not a proved reconstruction of actual formal brightness.

### Actual action budget, not “inefficient” shorthand

`result.json:646-680`:3admitted HTTP200 interactions,0rejected, closure`agent_finished`,7unused permits. `referenceStepsExecuted=4` is not a fourth hidden action: `stepped_agent.py:113-124,131-156` counts3mutations plus terminal done=True reference step.

| Step | Cell | Action | HTTP | Appium log line |
|---:|---:|---|---:|---:|
| 1 | 2 | Open notifications | 200 | 588620 |
| 2 | 5 | Expand quick settings: swipe (540,250)->(540,1650) | 200 | 588662 |
| 3 | 7 | Drag brightness at y420 from x300 to x976 | 200 | 588678 |

The sole failed Python cell2 consumed only the opening-shade action; its package wait failed afterward. Observations did not spend mutations.8Python executions include dedicated cleanup. Agent finished211.595821s with a valid first business final; business deadline not reached.

### Targeted same-campaign successful counterexample 097

This was read narrowly for **native XML and exact slider endpoint mechanism**, not used to invent a benchmark answer.097 has same visible goal, same max predicate, but initialization starts atmin rather thanmax and its slider appears in a brightness dialog at another y-coordinate.

| Raw097 anchors | Actual control/operation | Actual returned fact |
|---|---|---|
| 3290-3291 | Native source prefix and SeekBar rect | Class-name XML tags; rectx42,y149,width996,height126, rightx1038 |
| 3761-3762 | Clickx1032,y212 | Native slider text`65140.0` |
| 3923-3924 | Swipe to1037,y212 | Native slider text`65469.0` |
| 4182-4183 | Swipe beyond right bound to1075,y212 | Native slider text`65535.0` |
| result.json:561 | Same state oracle after completion | officialReward1.0 |

This proves a near-right location can be **measurably below maximum** and a native numeric semantic value is available on this stack. It does **not** establish098's exact value, map every dialog/expanded-panel hitbox, or justify hardcoding gamma65535 everywhere. It also rules out the blanket explanation that all max tasks are impossible under this device/oracle.

### First final, cleanup and oracle distinction

First business final (event2238,211.595821s) is exact `{"taskOutcome":"Brightness set to maximum."}`; archive retains it as a valid string. It is not numerically interpreted by the oracle. Cleanup user message_end2248 follows; cell8 at2330-2331 calls only quit and returns true; Appium588682-588686 DELETE200,588687-588688 GET404. The Agent does **not** restore brightness or invoke Back/home in cleanup.

Current driver `lib/driver.ts:508-615` has conditional animation/IME and hidden-API-policy restoration, not brightness restoration. The historical log explicitly records only hidden API policy restoration in that quit section; it is not an exhaustive device settings audit. Therefore no explicit cleanup brightness mutation is observed, **but no setting value before/after quit exists**, so externally stable state across cleanup cannot be proved. Harness correctly matters here: evaluator1794265680.306703 occurs **after quit**, while task teardown starts1794265680.3549619, **after reward** (`result.json:614-629`; frozen `runner.py:716-737,790-826`). Post-reward task teardown cannot explain0. Earlier driver cleanup/asynchronous change remains logically possible but unsupported.

### Causal conclusion, oracle risk and proposed targets

- **Confirmed:** false confidence in completion; no exact maximum acceptance; Agent-authored `node` parser mismatch and package/overlay assumption. Three action returns succeeded, all kernelsalive.7permits remained. This is not a Runtime crash, deadline, budget exhaustion or malformed-answer failure.
- **Probable strongest score mechanism:** unnecessary drag to a graphic center/interior coordinate changed initialized255 to near-max while looking full; no numeric check caught it. Exact finalint/gamma/mode absent, so root confidence remainsprobable.
- **Not proved:** oracle source bug, a false negative despite actual255, actual brightness restoration by cleanup, or any particular numeric final value. Visual-vs-exact-state observability is a comparability risk, not evidence that the official predicate is wrong.
- **Proposed only:** improve native-source examples to inspect actual tags or prefer direct semantic class/resource locators; wait on overlay controls, not forced package switch; provide Android stop-if-already-satisfied and slider endpoint/range/readback examples. Loaded generic guidance already says package/activity cannot establish page/result, HTTP success is not outcome proof, controls-first semantic evidence and preserve requested state. Lack of the core invariants is not established; targeted examples are a proposal, not an approved coordinated fix.
- **Decision-needed diagnostics only:** for a separately authorized future isolated investigation, retain exact state-oracle component before/after cleanup and actual comparator input/mode, without exposing score hints to the Agent or modifying this campaign. Do not weaken255 comparison or move formal scoring timing to make this score pass. Falsification: historical proof of255 after drag and before evaluator would shift focus to intervening state changes/oracle execution rather than endpoint placement.

## Offline methods and output

The analysis used stdlib JSON/pathlib streaming of original JSONL, paired exact tool IDs, static source reads, and PIL/base64 only to **view already captured** images in memory. No AndroidWorld/Appium module was imported and no external command/device call was executed. Full original Python code and relevant original returned fields are preserved in JSON timeline; source/query interpretation is separate.

### Reproducible bounded event, action and helper query

This standalone Python query reads only the two assigned attempts plus same-campaign097's narrow endpoint/source observations and campaign-bound shared Appium session lines. It prints no base64, whole page source, full private tree or other-session log. It does not execute recorded code.

```python
import collections, json, pathlib, re
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
A = {85: C/"episodes/085-SimpleSmsSendClipboardContent/attempt-1",
     98: C/"episodes/098-SystemBrightnessMaxVerify/attempt-1"}
for index, p in A.items():
    r = json.loads((p/"result.json").read_text())
    starts = {}
    statuses, kernels = collections.Counter(), collections.Counter()
    with (p/"raw-private/agent-events.jsonl").open() as f:
        for line_no, line in enumerate(f, 1):
            e = json.loads(line)
            if e.get("type") == "tool_execution_start":
                starts[e["toolCallId"]] = (line_no, e)
            if e.get("type") != "tool_execution_end" or e.get("toolName") != "write":
                continue
            sn, start = starts[e["toolCallId"]]
            if start["args"].get("path") != "xd://mcp__amkernel_python_exec":
                continue
            texts = [x["text"] for x in e["result"].get("content", [])
                     if x.get("type") == "text"]
            if not texts:
                continue
            try:
                ret = json.loads(texts[0])
            except ValueError:
                continue
            if "executionCount" not in ret:
                continue
            statuses[ret["status"]] += 1
            kernels[ret["kernelState"]] += 1
            print(index, ret["executionCount"], sn, line_no,
                  e["toolCallId"].split("|")[0], ret["status"],
                  ret["kernelState"], ret.get("error", {}).get("message"))
    b = r["stepBudget"]
    print(index, dict(statuses), dict(kernels),
          {k: b[k] for k in ("maxSteps", "executedActionCount", "referenceStepsExecuted",
                              "rejectedActionCount", "closureReason")})
    print("receipt", r["agent"]["answerSubmission"]["receipt"])
log = pathlib.Path("evidence/screenshot-video-controls-20261106T231029Z/appium.log")
sids = {85: "fb607e05-8328-496b-b945-d7384303e186", 98: "d5ecafcc-25b3-4721-af53-e79c6bbdb9fc"}
with log.open(errors="replace") as f:
    for n, line in enumerate(f, 1):
        for index, sid in sids.items():
            if (sid in line or sid[:8] in line) and any(
                k in line for k in ("getClipboard", "performEditorAction", "DELETE /session",
                                   "Restoring hidden api", "/source 200")):
                print(index, n, line.rstrip()[:650])
```

Actual bounded outputs from the applied stream queries:

```text
085 returned Python cells:19 =14completed +5failed;19alive
085 budget:maxSteps12, executedActionCount12, referenceStepsExecuted12,
           rejectedActionCount0, closureReason step_budget
085 receipt:eventSequence3936,phase finalization,receivedAtSeconds180.64814508298878
085 Appium session-matched log lines:1947, first559766,last561713
085 getClipboard:request561269,HTTP500 response561271,5101ms
085 performEditorAction:request561705,HTTP500 response561706,66ms
085 DELETE:561707/561711 HTTP200; same-session GET561712/561713 HTTP404
098 returned Python cells:8 =7completed +1failed;8alive
098 budget:maxSteps10, executedActionCount3, referenceStepsExecuted4,
           rejectedActionCount0, closureReason agent_finished
098 receipt:eventSequence2238,phase business,receivedAtSeconds211.5958206669893
098 Appium session-matched log lines:97, first588591,last588688
098 /source responses:588651=88838bytes,588661=88838bytes,588673=77170bytes
098 native actions:588620 openNotifications,588662 expand swipe,588678 brightness swipe;
                   all HTTP200
098 DELETE:588682/588686 HTTP200; same-session GET588687/588688 HTTP404
```

Limits: API response byte lengths prove nonempty responses, not exact semantics. Shared logs record transport metadata, not oracle query output. Raw provider rows/current brightness int are unavailable. Token-stream partial `tool_execution_start` records can exist; only paired actual structured execution responses were counted. Original errors can be sanitized, notably085cell18; the missing server reason must remainunknown.

### Minimal pure causal probes (actual input from097, not fabricated UI)

Applied to `source` in original097 structured response at rawline3291:

```python
E97 = []
with (C/"episodes/097-SystemBrightnessMax/attempt-1/raw-private/agent-events.jsonl").open() as f:
    for n, line in enumerate(f, 1):
        E97.append((n, json.loads(line)))
r3291 = next(json.loads(c['text'])['result'] for n, e in E97 if n == 3291
             for c in e['result']['content'] if c['type'] == 'text')
source_prefix = r3291['source']
print({"sourcePrefixCharacters": len(source_prefix),
       "openingTagNames": re.findall(r'<([A-Za-z][A-Za-z0-9_.]*)\b', source_prefix),
       "literalNodeOpeners": len(re.findall(r'<node\b', source_prefix))})
print({"case98DragEndX": 976, "case98StatedRightBound": 1038,
       "shortfallPixels": 1038-976,
       "case97NearEdgeValue": 65469.0, "case97ObservedMaxValue": 65535.0,
       "remainingGammaUnits": 65535.0-65469.0})
```

Actual output:

```text
{'sourcePrefixCharacters':1200,
 'openingTagNames':['hierarchy','android.widget.FrameLayout','android.widget.FrameLayout'],
 'literalNodeOpeners':0}
{'case98DragEndX':976,'case98StatedRightBound':1038,'shortfallPixels':62,
 'case97NearEdgeValue':65469.0,'case97ObservedMaxValue':65535.0,'remainingGammaUnits':66.0}
```

Limits: source is a1200-character prefix from097, not a full098 document. Geometry subtraction does not model Android hitbox, gamma conversion or infer098int. It supports the parser-contract and near-edge-vs-exact-endpoint distinction only. Screenshot judgments remain visual interpretations. None of these probes reruns an observed failure or task.
