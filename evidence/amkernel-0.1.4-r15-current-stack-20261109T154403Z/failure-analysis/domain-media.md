# Media failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Scope: cases 001,036,115, original attempt1. Companion machine-readable records: `domain-media.json`; exact offline query code/output: `domain-media-queries.md`.

## Findings and confidence

|Case|Original outcome|Strongest supported finding|Cause confidence / boundary|
|---|---|---|---|
|001 AudioRecorderRecordAudioWithFileName|0.0, completed;9/20 accepted actions|Goal/params already end`.m4a`; reviewed oracle adds another`.m4a`. A six-second0.08Mb named recording is visible on a second screen.|**Confirmed source contract defect**, **probable episode-loss contribution**; actual full filesystem name/path not captured. Do not equate oracle zero with failure to record.|
|036 MarkorTranscribeVideo|0.0, step_budget;20/20 accepted actions|Agent deliberately creates transcription under Download, while oracle checks Documents/Markor. Saved UI string`Moria, Charlotte, Emilia` has a real typo but **passes current fuzzy content helper**(0.9130434782608695≥0.9).|**Probable path/existence failure**; persistent expected-path absence not logged. Output directory is implicit in oracle, not explicit in visible task. Visual source coverage incomplete.|
|115 VlcCreateTwoPlaylists|**0.5**, completed;46/48 accepted actions|Both 4 track playlist names visible; Adventure lasttwo visible tracks reversed. Two generic correction gestures denied **before** action admission; valid swipe left order unchanged. Agent's exhaustion explanation is false.|**Confirmed Agent ordering failure at UI layer**, **probable failed Adventure component**. Reward proves exactly one Boolean pass, not which. No DB snapshot.|

These are not blanket Runtime failures. All 69 actual Python executions in this slice returned a structured response with `kernelState=alive`. There are 10 failed cells:1 audio, 4 transcription, 5 VLC. Errors retain their actual layer: unavailable optional`lxml`, missing WebElement API, failed locators/waits, and explicit proxy gesture-policy denials. Successful continuation in the same Runtime is observed. No proposed mechanism/fix below is represented as approved or already implemented; AMKernel owner supplies a separate mechanism report.

## Method and provenance

Original `result.json`, `normalized-agent-events.json`, `raw-private/business-submission.json`, and `raw-private/agent-events.jsonl` were read only. Large JSONL was streamed using local Eval, never dumped. Actual `tool_execution_start.args.content` was parsed only for write calls targeting`xd://mcp__amkernel_python_exec`; each was paired by **full** toolCallId with `tool_execution_end`. `domain-media.json.timeline` retains original Python code, exact start/end/message line anchors, full IDs, response timestamp, duration, actual status/kernelState, bounded original semantic fields and errors. Removed generic tree wrappers or absent media bytes are not silently replaced with interpretation.

Campaign manifest/result pin AndroidWorld`55ddaf5edc6f6c25673aed343907d5b9dca66f84`. Official source below is the current checkout; individual task-file equality against frozen campaign bytes was not independently established in this slice. The parent-owned`shared-offline-checks.json` establishes current19-file **harness** digest equality to frozen manifest`861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`, not a per-task-source equality claim. All source-derived historical conclusions carry that task-source provenance limit.

No product/config/test changes; no live device, ADB, Appium, MCP, task/score rerun, build, lint, formatting or suite execution. Pure probes only call AST-extracted side-effect-free helpers over actual recorded strings or explicitly hypothetical UI-derived rows. Parent must perform any integration verification; no such check is claimed here.

## Common final-answer, clock and cleanup boundaries

- Exact original goal appears in raw user message_end line 9 for each case. Reference clock is`2023-10-15T15:34:00+00:00`, timezoneUTC, supplied as initialization reference. No date-relative predicate exists in these three; missing-clock/timezone is not an evidenced cause.
- First business finals are raw lines 3539(audio),7345(transcription),8499(VLC). All are valid nonempty string`taskOutcome` envelopes. Parent shared receipt proves these are first assistant stops, exact rawText matches archives, receipt hashes match, and timestamps are before cutoff/business deadlines. Later cleanup finals are ignored, never precedence replacements.
- `src/fsq_androidworld_eval/submission.py:45-93` parses original JSON, requires string, and strips only outer whitespace. `runner.py:787-788` uses parsed answer for InformationRetrieval only. **These tasks grade state**, not their final prose. Wrong prose can expose reasoning but cannot directly produce these file/DB rewards.
- `runner.py:716-737` finishes business and session cleanup before evaluator790-796; **driver.quit precedes evaluation**. Task teardown822-827 follows evaluation. Original result stage timestamps support this order. The three dedicated cleanup cells only call`driver.quit()` and report returned ownership; no restore/delete/reset occurs. Post-quit persistence is not captured, so quit effects remain unmeasured, but later teardown cannot explain the earlier score.
- A reference loop completion iteration is distinct from an accepted UI action: `stepped_agent.py:113-125` increments reference count when returning done with`appiumAction=None`. Audio10 reference/9 accepted and VLC47 reference/46 accepted are not hidden mutations. Transcription20/20 has no completion-only iteration.

# Case 001 — AudioRecorderRecordAudioWithFileName

## Goal and exact oracle

Visible goal: **Record an audio clip and save it with name "presentation_fGwr.m4a" using Audio Recorder app.** Recorded params: `{"file_name":"presentation_fGwr.m4a","seed":170855541,"text":""}`.

Sources:

- `android_world/android_world/task_evals/single/audio_recorder.py:85-123`: constructor uses`CreateFile(params,AUDIORECORDER_DATA)`; initialize calls CreateFile initialization then clears recorder directory; evaluator checks`file_name + ".m4a"` and returns1iff exists.
- Same file125-159: generator explicitly starts from`random.choice(name) + ".m4a"`, then modifies filename; template91-92interpolates the resulting complete name.
- `env/device_constants.py:29`: recorder path`/storage/emulated/0/Android/data/com.dimowner.audiorecorder/files/Music/records`.
- `utils/file_utils.py:228-258`: if base exists, `find base -type f -o -type d`; target is exact converted`base/target` membership in the returned full paths. It is not “same basename anywhere”. It even includes directories; no audio decoder/size check.

Thus the reviewed oracle checks exactly:

```text
/storage/emulated/0/Android/data/com.dimowner.audiorecorder/files/Music/records/presentation_fGwr.m4a.m4a
```

This task does **not** call `CreateFile.is_successful`, does not check`text`, nonempty bytes, duration, or exactly one changed recording. Do not substitute neighboring `AudioRecorderRecordAudio`'s positive-size/new-file predicate. `CreateFile.initialize_task:191-194` clears common device storage; explicit recorder clear happens before execution; teardown clearing follows evaluation.

## Decisive timeline

|Python cell|Raw start/end lines; short toolCallId|Original returned fact / interpretation|
|---|---|---|
|2|747/748;`call_czDPwhYnxpaXyUjkLQelSz0Z`|`ModuleNotFoundError:lxml`, failed/alive. Agent recovers with stdlib ElementTree cell 3. No UI action lost.|
|7|2190/2191;`call_pkIzQbHCjPmq0MUroTW995Dq`|Record click; progress00:01, Recording…, M4a44.1kHz.|
|8|2467/2468;`call_gVpRBjyG0awtr7NaQq6QCl8v`|Stop click opens New name dialog, fieldRecord-1, Save available.|
|9|3074/3075;`call_ywIdmwOAiuSCSSLimghFDeI9`|Original code clears name, sends`presentation_fGwr`, saves. Returned`enteredBaseName` exact; visible title same,0.08MbM4a44.1kHz,00:06 duration.|
|10|3439/3440;`call_TwFo9hYNVtla8MrRdmIw4oNL`|RecordsActivity has list_item_name`presentation_fGwr`,0.08MbM4a44.1kHz,00:06. Cross-screen saved-list evidence, not physical filename bytes.|
|final|3539|Claims saved`presentation_fGwr.m4a`; valid first-business string.|
|11(cleanup)|3614/3615;`call_YwkP791CdGVmOk0cXZVdSrT2`|Only quit; completed/alive; quitReturnedtrue.|

## Cause, evidence limits and responsibility

**Confirmed:** reviewed source uses inconsistent complete-name/stem semantics. Plain goal requests single suffix; current oracle demands double suffix. The first divergence from the *oracle literal target* is cell 9's stem input, but this is not a demonstrated wrong-user-goal choice: the app shows codec separately and hides the extension in title/list.

**Probable:** missing double-extension path explains reward0. The evaluator returned0without error, but its actual `find` output is not archived. The UI record strongly supports a saved recording entry, not exact disk existence. We cannot prove that the correct single-suffix physical file existed, which directory the backend used, or whether quit changed persistence. Contract defect confidence must not be conflated with historical filesystem/score causation confidence.

Not budget-limited:9 accepted/20, no rejections/denials, normal completion;11 nominal slots remained before final. Not a recording-start/save error in the visible UI. Optional lxml failure is recovered and not a Runtime death. Receipt parsing does not change file predicates.

## Proposed fixes (not applied)

1. **Decision needed—AndroidWorld filename contract:** choose complete filename semantics (recommended: check recorded file_name verbatim) or stem semantics (then generate/display stem consistently). Update generator/template/oracle together in a separately versioned future benchmark; keep old score immutable. Do not teach the Agent a double-suffix workaround or silently accept arbitrary aliases.
2. **Proposed—Agent acceptance adherence:** existing amkernel-appium files guidance183-210already distinguishes title/stem/extension/full path and persisted read-back. Use available app file-info proof, or report unresolved physical name/path rather than assert it from title+codec. A Skill omission is not established by this trace. Added UI proof must fit existing budget and never bypass allowed interface.

Falsification: frozen task bytes differing materially, or original expected double-extension path actually present at evaluation, would defeat this mismatch as the sole score-loss explanation. No such persistent evidence was captured.

# Case 036 — MarkorTranscribeVideo

## Goal, source video and file predicates

Visible goal locates video`ZwUN_moment_70_.mp4` **in Download** and asks a comma-separated sequence in Markor file`ZwUN_moment_70__transcription.txt`. The goal does **not** explicitly name the output directory. Actual params: messages`["Maria","Charlotte","Emilia"]`, text`"Maria,Charlotte,Emilia"`, seed1222528574, plus seven exact noise filenames retained in JSON.

`markor.py:877-941` delegates success to`CreateFile(params,MARKOR_DATA)`. `Markor.initialize_task:60-62` clears notebook; `CreateFile.initialize_task` clears common storage; target generator902-908writes video underDOWNLOAD_DATA, each message8s. `user_data_generation.py:219-304` uses mp4v,320x240,30fps(default),240frames/message, yellow text at(50,120) on random per-frame RGBnoise. These are **source-intended generation properties**, not an historical ffprobe. Exact observed VLC target description in cell 6 is`Video: ZwUN_moment_70_, Duration:24seconds`; correct title and total duration are actually observed.

`file_validators.py:199-226` requires:

1. Full path`/storage/emulated/0/Documents/Markor/ZwUN_moment_70__transcription.txt` exists (`MARKOR_DATA` from`device_constants.py:32`). Missing path returns0 before content is read.
2. `cat` exactly that notebook path; decode, remove``, strip outer whitespace; compare to recorded text with`fuzzy_match`. `fuzzy_match_lib.py:20-51` uses case-insensitive SequenceMatcher ratio≥0.9—not exact CSV equality and not per-name scoring.

The observed UI string`Moria, Charlotte, Emilia` vs reference`Maria,Charlotte,Emilia` yields **0.9130434782608695, acceptedTrue** in the isolated current helper. This pure probe does not re-run the task, read any file or establish that evaluator ever reached content comparison. The Maria→Moria error is real relative to initialized params, but **not a sufficient zero-reward cause under the current content helper**.

## Actual rendered coverage, not a guessed transcript

- Cell 8(raw 2388-2390,`call_JKSYK2CVcXhGOWv4mtNGf9XK`) clicks exact target and samples38screenshots,1.43–24.88s since click, returning VideoPlayerActivity. Cell 9(raw 2636-2637) then reports **Video player tips**, Close, NEXT, Player controls. This first sample pass was not a demonstrated unobscured complete sequence.
- Cell 10(raw 2931-2934) dismisses tips and captures a screenshot. Original PNGpayload is RPC-elided; retained metadata is not pixels.
- Cell 11(raw 3397-3400,`call_4TBUNgLIGt9XVncAkaYRUCRS`) samples38more frames over0.34–23.24s after a new loop clock, cropping video y760..1640. It returns **MainActivity**, so playback ends during collection. No seek/replay/reset occurs. These times are loop elapsed times, not media positions.
- Cell 12(raw 3863-3865,`call_G4Ujy9Ssgwn0gsQGcxzH57em`) builds a JPEG from retained frames2indices16,18,...36. The intact338307-byte JPEG/SHA256`ccc6e9dbda2ce40d678c27f09b500bbd53eebff94573c1eb3b7bb0bc87e16782` visibly shows **Emilia** at indices 16/18(loop10.30/11.49s), then VLC library/noise thumbnails from index 20(loop12.89s) onward.
- Earlier PNG strings contain explicit`…[... chars elided for RPC frame]`; call11 has five display metadata entries but only two elided image payloads. Complete early Maria/Charlotte rendered evidence and original MP4 are not captured here. The expected full sequence comes from actual initialized params/source, **not an invented visual reading**. Noise thumbnails are not additional target messages. No repaired/recreated media or random-parameter transcript is substituted.

## Destination and save timeline

|Cell|Raw start/end; short toolCallId|What actually happened|
|---|---|---|
|13|4250/4251;`call_ew2Sq4FnVt7jclG37ZJJHTbe`|Home→drawer→Markor; parent row describes`/storage/emulated/0/Documents`, consistent with notebook underDocuments.|
|14|4574/4575;`call_VBGO5abteRcM8owu8NMd7sNx`|Clicks Folder.., moving toDocuments; waits for Download in wrong parent, TimeoutException. One accepted click only. **Earliest destination-binding deviation**.|
|15|4821/4822|Fresh title`> Documents`; parent path`/storage/emulated/0/Documents`.|
|16/17|4999/5000;5234/5235|Go to→Internal storage; root contains Documents and Download.|
|18|5466/5467;`call_tRn54xU7TNcjzfade6tezO20`|Clicks FolderDownload, then waits for absolute path string in page source and times out. Actual navigation succeeded.|
|19|5633/5634;`call_0LZxWN6WD4SMKPPi02p6BidL`|Fresh title`> Download`; targetMP4 visible. This is the current output-creation location.|
|20|5906/5907|Create-new dialog in Download; defaultsmy_note/.md.|
|21/22|6307/6308;6509/6510|`set_value` AttributeError before mutation; next read finds supportedclear/send_keys and unchangedmy_note/.md. This is client-API misuse, not AMKernel content corruption.|
|23|6873/6874;`call_i32XQdOmt9Iz80tnC55zg7gF`|clear/inputname,clear/input.txt,OK; exact filename fields returned; DocumentActivity editor open.|
|24|7301/7304;`call_pt4KuJaGoy7FFI10aEunxcFt`|Constructs`expected='Moria, Charlotte, Emilia'`; inputs it and clicksSave. Returned content same, Saveenabledfalse. Twentieth accepted action isSave.|
|final|7345|Claims saved`Download/ZwUN_moment_70__transcription.txt` withMoria,... . Valid first-business string.|
|25(cleanup)|7433/7434|Only quit; completed/alive.|

Cell 24readback verifies string input consistency and UI Save acknowledgement, **not persisted expected-path cat**. No reopen/document-info/full path snapshot is captured. Harness exhaustion steering at raw 7302 arrives during this admitted save call; its completed result still arrives. No action was denied/rejected; no saving cancellation is evidenced.

## Cause and proposals

**Probable zero cause:** the file was created underDownload while oracle requiresDocuments/Markor. Initial notebook clearing and no observed recreation there support this explanation, but persistent absence at evaluator time is unobserved. **Confirmed behavior:** Agent associated source-media folder with output folder and navigated away. **Comparability risk:** visible task omits the output directory that the oracle silently requires. Do not label this an explicit user-goal folder violation or a proven oracle-code bug.

Save exhausted the real20 action budget, leaving no accepted mutation capacity to move/correct/reopen. Budget did not prevent the final Save; it prevented later correction/verification. Early visual obstruction and typo are important behavior/evidence issues, but neither proves score cause. Four failed cells all retain kernelalive and are recovered; no Runtime crash is shown.

Proposals, all separate from cause:

1. **Agent adherence:** keep source and destination bindings separate. Retain observed app notebook for an unspecified output folder; compare extension/name/current folder independently before creating. Existing Skill files-and-notes and budgeting guidance already covers this; trace violation is not proof of missing guidance. Never hardcode hidden evaluator path as an Agent answer.
2. **Decision needed—future task contract:** expose Documents/Markor output directory, or explicitly define another accepted scope; version any changed benchmark. Original result remains0.
3. **Visual/API handling:** dismiss tips before timing capture; collect readable bounded source-message evidence with sequence boundaries; stop/report uncertainty rather than invent first-name reading. Use observedclear/send_keys instead of unavailable set_value. Fewer giant sheets reduce archival elision risk, but its exact owning mechanism needs separate review. Fixing Moria alone would not flip the current fuzzy comparison.

Falsification: actual file-info/persistent proof that the Download creation context saves toDocuments/Markor defeats path hypothesis; actual media showingMoria rather than initializedMaria would change visual error attribution. Neither was captured.

# Case 115 — VlcCreateTwoPlaylists

## Exact ordered goals and fractional oracle

**Ultimate Fails Series**, in order:

1. `2023_03_29_highlight_14_.mp4`
2. `scene_94_HD_MYI6.mp4`
3. `moment_1_HD_2023_07_27.mp4`
4. `recording_61_4K_final.mp4`

**Adventure Marathon**, in order:

1. `clip_12_HD_2023_02_25.mp4`
2. `8u3n_footage_29_HD.mp4`
3. `footage_46_raw_jZFR.mp4`
4. `D7B0_highlight_2_4K.mp4`

Full params/noise files/seed1076424442 are preserved in JSON. `vlc.py:215-218` initializes task 1(clear internal storage,VLCVideos,Playlist/Media/PlaylistMediaRelation), then task 2.setup_files only, deliberately not clearing database again. All requested and noise videos go to`/storage/emulated/0/VLCVideos`.

`vlc.py:29-71,144-150` pulls`/data/data/org.videolan.vlc/app_db/vlc_media.db`, joins PlaylistMediaRelation→Playlist→Media and supplies playlist_name,media_file_name,order_in_playlist. `sqlite_validators.py:30-70` is Boolean:

- count all joined rows whose playlist name fuzzy-matches candidate(case-insensitive ratio≥0.9); count must equal4;
- for each expected index 0..3, a matching playlist row must have **exact media filename** and **position==index**;
- any failure returnsFalse. Correct membership with reversed order still fails the whole component.

`VlcCreateTwoPlaylists.is_successful:224-226` averages the two componentBooleans. **Original reward is0.5, not0.0.** Therefore exactly one passed, assuming reviewed frozen semantics. Aggregate alone cannot distinguish`(1,0)` from`(0,1)`; there is no per-playlist oracle result or SQLite snapshot in this attempt.

## Construction and correction evidence

|Cell|Raw start/end; short toolCallId|Observed original code/result|
|---|---|---|
|11|2555/2556|Creates Adventure withclip12 first.|
|13|3262/3263|Adds8u3nsecond; opensD7B0More Actions→AddtoPlaylist beforefootage46.|
|14|3543/3544;`call_aPS9nsRWHjTYgQfXSv4pn5zf`|First click appendsD7B0 third; then opensfootagegroup. **Accepted action14 is earliest order deviation.**|
|15|3842/3843|Appendsfootage46 fourth.|
|17|4330/4331|Creates Ultimate withhighlight14 first.|
|20/21|5169/5170;5642/5643|Geometry helper throwsRuntimeErrorbeforeclick; corrected exactml_item_titlehelper appends scene94 second. No duplicate accepted append.|
|24|6288/6289|Appendsmoment1thenrecording61, in goal sequence.|
|26|6763/6764;`call_Ct5LrABBwcXZ8Iyaa6fKdd7b`|Overview shows Adventure4tracks8:17 and Ultimate4tracks7:23. Proves identities/cardinalities, not Ultimate detail order or exact DBnames.|
|27|7007/7008;`call_4V3GqVpHEuq7ZKgOkhCzaOTA`|Adventure detail sequence:clip12,8u3n,**D7B0,footage46**. Allfour visible titles extracted in order.|
|29|7442/7443;`call_CR8bPCN8PnfTuu5PPWPoSgbp`|`driver.drag_and_drop` failsUnknownMethodException:"Only a single native touch pointer is supported".|
|30|7651/7652;`call_vHVQBAEymlqiIACy69KW0L8D`|GenericActionChains failsUnknownMethodException:"Use one touch pointer and one contact cycle per step".|
|31|7889/7890|Third-track menu hasAppend,Insertnext,Information,Addtoplaylist,etc.; noMoveupoption in returned list.|
|32|8367/8368;`call_AWSc4dpDnDdWqmvdLZGFqAnb`|Closes menu; supported900msswipe fourth movehandle→third completes, but fresh readback remainsclip12,8u3n,D7B0,footage46. HTTP200 is not reorder success.|
|final|8499|Admits reversedlasttwo, asserts Ultimate correct, attributes Adventure failure toclosedinteractionbudget.|
|33(cleanup)|8578/8579|Onlyquit;completed/alive.|

### Which predicates are proved?

|Predicate|Evidence status|
|---|---|
|Both requested playlist identities exist in app;4tracks each|**Observed** overview26.|
|Adventure contains allfour requested visible stems|**Observed** detail27and32. Exact`.mp4` DBfilenames not read.|
|Adventure visible order lasttwo reversed|**Observed**, complete4-item list; construction chronology independently agrees.|
|Adventure exact SQLitepositions/filenames fail|**Probable**, not captured. Pure helper on explicitly UI-derived rows returnsFalse atpositions2/3.|
|Ultimate exact order correct|**Probable** from append chronology17→21→24, not detail readback/DB proof.|
|Ultimatecomponent=1,Adventurecomponent=0|**Probable** consistent with above and0.5, not directly archived.|
|ExactlyoneBooleancomponent=1|**Derived with certainty from0.5** under reviewed oracle aggregation.|

### Budget allegation is refuted

Original result: **46 accepted / 48 max**,47 reference iterations (includes completion),`exhausted=false`,`closureReason=agent_finished`,0ActionGate rejected;33 Python calls exceed30 **advisory**, which explicitly doesnotaffectreward. Two nominal accepted mutation slots remained at the last business mutation; after firstfinal, Agent-finishedcloses actionphase, not exhaustion.

The two errors29/30 are `appium_proxy._validate_actions:271-306` policy failures: exactlyone touch pointer source and one complete contactcycle. Handler`appium_proxy.py:494-502` calls authorization **before**`ActionGate.submit`, so these 2unsupported commands do not appear in accepted ledger and do not increment its rejectioncount. Audit records2deniedCommandCount withunsupportedoperation, while gate records0rejectedActionCount. No budget-exhaustion exception/steering occurs for VLC. Do not infer serialization specifics beyond reject class: original serializedW3Cpayloads are not retained, though exact helpers/errors are.

## Cause and proposals

**Confirmed root behavior:** out-of-order append created correction debt; two incompatible generic drag helpers were denied before admission, a valid swipe made no visible progress, and Agent stopped with an incorrect exhaustion explanation. **Probable score component:** Adventure fails ordering, Ultimate passes; exact DB/subscore pair is unknown. This is not a Runtime death, accepted-action cap, or proof of a proxy bug. Currentpolicy deliberately rejectsmouse/multisource/incompletegestureforms; the prompt does not spell out every serialized restriction, an interface clarity issue for decision rather than a proven implementation defect.

Proposals:

1. **Agent adherence:** append requested files in exact sequence rather than defer grouped earlier item. Keep the local intended sequence and compare all-item detail order, not a four-track summary. Existing Skill already requires independent order/persistence criteria; a Skill omission is not proven.
2. **Decision needed—gestureinterface:** clarify one-touch/source/contact-cycle contract and pre-admission vs budget refusal. Use a valid touch/hold/move only when needed and in budget; read back actual order. Do not relax the proxy blindly or map mouse automatically. A successful compliant reorder within the remaining two slots is **not observed or promised**.
3. **Proposed future diagnostic evidence:** bounded read-only join rows/component results before/after quit and at scoring would separate UI order from DB positions and prove which playlist passed. Preserve old campaign state/reward; do not capture a whole private DB or conflate such instrumentation with an Agent fix.

Falsification: archived serialized gesture satisfying all validator conditions would identify a proxy mechanism bug; DB positions differing from the visible list could change component attribution. Existing trace cannot settle either.

# Complete accepted-action ledgers

The tables below enumerate **every accepted mutation**; per-action paths/status/full IDs and corresponding original code/result are in JSON. All accepted statuses areHTTP200. Failures before mutation or policy admission are excluded and described separately. Counts are actual gated commands, not Python call counts.

## 001-AudioRecorderRecordAudioWithFileName

|Accepted#|Kind|Pythoncell(rawstart/end)|Meaning|
|---|---|---|---|
|1|`click`|4(1306/1307)|Open launcher search|
|2|`input`|5(1579/1580)|Search Audio Recorder|
|3|`click`|6(1852/1853)|Launch Audio Recorder|
|4|`click`|7(2190/2191)|Start recording|
|5|`click`|8(2467/2468)|Stop recording; New name dialog|
|6|`clear`|9(3074/3075)|Clear recording name|
|7|`input`|9(3074/3075)|Enter presentation_fGwr (without .m4a)|
|8|`click`|9(3074/3075)|Save recording|
|9|`click`|10(3439/3440)|Open records list|

Accepted9/20;reference10;gateclosure`agent_finished`;exhausted`False`;gaterejected0;proxydenied0.

## 036-MarkorTranscribeVideo

|Accepted#|Kind|Pythoncell(rawstart/end)|Meaning|
|---|---|---|---|
|1|`actions`|4(1005/1006)|Open app drawer swipe|
|2|`actions`|5(1263/1264)|Scroll app drawer to VLC|
|3|`click`|6(1503/1504)|Launch VLC|
|4|`click`|8(2388/2390)|Open target 24-second video|
|5|`click`|10(2931/2934)|Dismiss Video player tips|
|6|`mobile: pressKey`|13(4250/4251)|Home keycode 3|
|7|`actions`|13(4250/4251)|Open app drawer|
|8|`click`|13(4250/4251)|Launch Markor|
|9|`click`|14(4574/4575)|Folder .. from Markor notebook to Documents; subsequent Download wait times out|
|10|`click`|16(4999/5000)|Go to menu|
|11|`click`|17(5234/5235)|Internal storage|
|12|`click`|18(5466/5467)|Folder Download; subsequent absolute-path wait times out|
|13|`click`|20(5906/5907)|Create new file dialog within Download|
|14|`clear`|23(6873/6874)|Clear my_note name|
|15|`input`|23(6873/6874)|Enter ZwUN_moment_70__transcription|
|16|`clear`|23(6873/6874)|Clear .md extension|
|17|`input`|23(6873/6874)|Enter .txt extension|
|18|`click`|23(6873/6874)|Create .txt document|
|19|`input`|24(7301/7304)|Enter Moria, Charlotte, Emilia|
|20|`click`|24(7301/7304)|Save document; final accepted mutation|

Accepted20/20;reference20;gateclosure`step_budget`;exhausted`True`;gaterejected0;proxydenied0.

## 115-VlcCreateTwoPlaylists

|Accepted#|Kind|Pythoncell(rawstart/end)|Meaning|
|---|---|---|---|
|1|`actions`|4(1017/1018)|Open app drawer|
|2|`actions`|5(1246/1247)|Scroll app drawer|
|3|`click`|6(1428/1429)|Launch VLC|
|4|`click`|9(2121/2122)|Open clip_12_HD_2023_02_25 More Actions|
|5|`click`|10(2303/2304)|Add to playlist|
|6|`click`|11(2555/2556)|Focus playlist name|
|7|`input`|11(2555/2556)|Enter Adventure Marathon|
|8|`click`|11(2555/2556)|Save new playlist with clip_12|
|9|`click`|12(3001/3002)|8u3n_footage_29_HD More Actions|
|10|`click`|12(3001/3002)|Add to playlist|
|11|`click`|13(3262/3263)|Add 8u3n to Adventure|
|12|`click`|13(3262/3263)|D7B0_highlight_2_4K More Actions|
|13|`click`|13(3262/3263)|Add to playlist|
|14|`click`|14(3543/3544)|Add D7B0 third (first order deviation)|
|15|`click`|14(3543/3544)|Open footage_ group|
|16|`click`|15(3842/3843)|footage_46_raw_jZFR More Actions|
|17|`click`|15(3842/3843)|Add to playlist|
|18|`click`|15(3842/3843)|Append footage fourth|
|19|`click`|15(3842/3843)|Navigate up|
|20|`click`|16(4012/4013)|Open 2023_0 group|
|21|`click`|17(4330/4331)|2023_03_29_highlight_14_ More Actions|
|22|`click`|17(4330/4331)|Add to playlist|
|23|`click`|17(4330/4331)|Focus new playlist name|
|24|`input`|17(4330/4331)|Enter Ultimate Fails Series|
|25|`click`|17(4330/4331)|Save new playlist with highlight|
|26|`click`|17(4330/4331)|Navigate up|
|27|`click`|18(4634/4635)|Open search|
|28|`input`|19(4851/4852)|Search scene_94_HD_MYI6|
|29|`click`|21(5642/5643)|scene_94_HD_MYI6 More Actions|
|30|`click`|21(5642/5643)|Add to playlist|
|31|`click`|21(5642/5643)|Append scene to Ultimate|
|32|`back`|21(5642/5643)|Back hides keyboard/search state|
|33|`back`|22(5792/5793)|Back exits search|
|34|`click`|23(6022/6023)|Open moment_ group|
|35|`click`|24(6288/6289)|moment_1_HD_2023_07_27 More Actions|
|36|`click`|24(6288/6289)|Add to playlist|
|37|`click`|24(6288/6289)|Append moment to Ultimate|
|38|`click`|24(6288/6289)|Navigate up|
|39|`click`|24(6288/6289)|recording_61_4K_final More Actions|
|40|`click`|24(6288/6289)|Add to playlist|
|41|`click`|24(6288/6289)|Append recording to Ultimate|
|42|`click`|26(6763/6764)|Open Playlists overview|
|43|`click`|27(7007/7008)|Open Adventure to inspect all four tracks|
|44|`click`|31(7889/7890)|Open third-track D7B0 More Actions|
|45|`back`|32(8367/8368)|Close More Actions|
|46|`actions`|32(8367/8368)|Swipe fourth move handle toward third; order unchanged|

Accepted46/48;reference47;gateclosure`agent_finished`;exhausted`False`;gaterejected0;proxydenied2.

## Reproduction and missing state

Use `domain-media-queries.md` for exact standalone extraction, pure helper code and actual outputs, including retained JPEG decode. No reproducible query here fabricates filesystem/database snapshots or regenerated media. Stronger historical component proof would require original expected-path listing/cat or playlist join rows around quit/evaluation, plus unelided early target frames; these were not captured in assigned attempt files. They are **missing historical evidence**, not instructions to rerun these observed failures.
