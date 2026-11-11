# 本轮20项失败：逐案证据与因果分析（跨项目整合／两阶段独立复核）

唯一campaign：`amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`。

20项失败全部覆盖；以下索引按原taskIndex排序，正文按领域组织并保留完整独立取证章节。每案区分goal/初始化/oracle、历史实际调用和输出、动作账本、首次可证偏离、近因与root cause、备选解释和证据缺口，以及独立的未实施fix方案。结构化完整参数/工具原文/响应与锚点见[cases.json](cases.json)，公共提交/时钟/清理/源码身份探针见[shared-offline-checks.json](shared-offline-checks.json)。

**状态：跨项目调查与两阶段独立复核整合完成；MA01–MA13全部接受/采用，最终owner纠偏JSON/MD已锁。** 无外部等待或剩余报告争议；44eval/37owner按既有7组去重，不相加；不宣称20项历史根因均已证。

原正式成绩不变：116完成，96passed/20failed/0invalid，reward96.5，fullValidScore83.1897%，officialScore=null。115保留0.5；不能把20案都写成reward0。

## 独立review修订与规范置信

R02：引用[review.json](review.json)中`independentOfflineQueries.sourceIdentity`的31-file历史blob/hash与复现代码，全部与所引revision内容一致；本修订不重跑。剩余源码身份缺口收窄为历史import路径/安装包bytes未归档。历史生成HTML、DB、proto、helper依赖等具体状态缺口仍按案例保留。

MA01补充：owner17个current retained installed文件与旧31-file blob digest一致，另有13个发布Runtime模块收据。执行归属owner/原review；范围不同不相加，不是本批探针/核验，也不关闭完整历史import/helper/DB字节缺口。

R03：44fix均有具体`project/module/file/symbol`、确切Skill section或原Agent cell，登记见[module-map.md](module-map.md#review-fix-location-register)。分为behavioral/proposed-product/diagnostic/protocol-decision；行为失误不等于缺Skill，更不等于Runtime实现bug。

R04：以下三种置信独立；source defect的unknown表示未建立该案产品/任务源码缺陷，不否认已证Agent行为。episode维度是历史失分归因，不是对已记录reward的怀疑。原领域叙述中局部confirmed不能替代此表或抹掉unknown。

| case | source-defect | observed-behavior | episode-failure-cause | 必须保留的unknown |
|---|---|---|---|---|
| 001 | confirmed | confirmed | probable | physical recording filename/path and pre/post-quit existence |
| 003 | unknown | confirmed | probable | native-click delivery/timing；post-quit oracle UI |
| 004 | unknown | confirmed | probable | historical JS numbers/clickCount and initialized task.html；native dispatch versus stale observations |
| 014 | confirmed | confirmed | probable | final accounting.db note/category/cents and predicate branch |
| 023 | unknown | confirmed | probable | post-quit exact file paths/content；unopened rename dialog feasibility |
| 024 | unknown | confirmed | probable | post-quit file content/identity；actual feasibility of remaining route |
| 030 | confirmed | confirmed | unknown | whether any file was deleted；initial/final metadata, survivor scope and mount atime policy |
| 033 | unknown | confirmed | probable | exact evaluator-time file/cat and short-circuit branch |
| 036 | unknown | confirmed | probable | expected/actual output disk path and bytes；early frame content omitted by RPC |
| 049 | unknown | confirmed | probable | input transformation layer (IME/driver/app)；final broccoli DB fields |
| 052 | unknown | confirmed | probable | counterpart UI occurrence identity and full finalDB；universal budget feasibility |
| 058 | unknown | confirmed | probable | actual clicked-menu element IDs；post-quit playlist DB/order |
| 060 | confirmed | confirmed | unknown | complete actual song set/per-song durations；post-quit playlist DB and precise failure predicate |
| 076 | confirmed | confirmed | probable | complete strict-after/date-scoped first-event inventory；natural-language correctness of next-day title |
| 085 | unknown | confirmed | probable | historical Node/Appium/helper package lock/hash/imported bytes；contemporaneous helper foreground-service evidence and original clipboard/provider rows |
| 091 | unknown | confirmed | probable | second activity full category/date/distance and original proto/DB total |
| 098 | unknown | confirmed | unknown | formal098完整XML、active geometry、初末/evaluator整数、swipe是否改变状态；097不替代098 |
| 106 | confirmed | confirmed | confirmed（仅2vs3长度拒绝） | third title、实际filter、group存在与可达性、10步全覆盖可行性 |
| 107 | unknown | confirmed | probable | DB rowIDs and absolute due timestamps of noise rows |
| 115 | unknown | confirmed | probable | individual historical validator results and joined DB order；post-quit persistent winner component |

R05：085历史helper依赖lock/hash/实际安装bytes未归档，原readiness报错不证明当前解释性helper源码就是历史加载实现；098实际完整XML、slider读值与亮度整数unknown，097只能支撑机制推断。R01/R06是认可并保留的反证/结论边界，未被登记为新报告错误。

逐finding及MA01–MA13处理见[review-resolution.md](review-resolution.md)与[review-resolution.json](review-resolution.json)。旧review hash/override是历史读取边界；owner最终纠偏收据已读取并锁定新hash，不把本次identity绑定写成重做13项审计。下方关系表为原锁定版具体claim的历史关系，最终均接受纠偏；unknown/语义待决不等于剩余报告分歧。

## 模块实际对齐与裁定

<a id="module-alignment"></a>

7组去重优先级/具体责任/最小方案与未执行验收见[module-map](module-map.md#cross-project-priority)。每案`moduleAlignment`含owner mechanism/fix指针、agree/disagree/different-scope、强证据与采用裁定；每项44fix有反向关系，完整37来源映射在`cases.json.moduleAlignment.proposalMapping`。MA13不把这些主owner新改文伪装成第二review已重审。

| case | 关系（仅具体claim） | 最终采用与证据优势 |
|---|---|---|
| 001 | compatible-but-different-scope | Filename contract mismatch plausibly explains zero; exact existence-helper input/result not retained. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 003 | disagree | 十个导航动作后，六个element.click批量结束截图仍X=(0,0)；一次Right坐标tap后X=(0,1)，随后获准三个Down后末X=(3,1)，下一个Right预算拒绝。四次恢复touch有效，不是四次撞墙；不能将四次恢复进展归给之前六click。底层dispatch/快照时序unknown。 控制裁定：MA03 |
| 004 | agree_on_scoped_observations | No entry/Submit and persistent pre-form state support noncompletion; historical JS variables and evaluator UI unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 014 | compatible-but-different-scope | Marker-bearing saved UI notes fail reviewed comparator; final accounting.db/category/cents unavailable. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 023 | agree_on_scoped_observations | Rename was never executed; evaluator-time original/new paths are not independently captured. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 024 | agree_on_scoped_observations | No rename recorded; exact post-quit disk contents/path remain unavailable. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 030 | agree_on_scoped_observations | Physical deletion, survivor set and exact failing filesystem predicate cannot be established. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 033 | compatible-but-different-scope | Exact-name/default extension and line shape diverge; actual evaluator short-circuit branch not captured. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 036 | compatible-but-different-scope | 捕获UI字串按真实fuzzy规则的条件关系>=0.9，不代表文件存在或evaluator已比较/通过内容。可见创建breadcrumb为Download，oracle限定Documents/Markor；物理文件路径/短路分支未捕获，因此目录失分probable。视觉采样不足可改进，但不能以Moria为本次已证失分原因。 控制裁定：MA05 |
| 049 | agree_on_scoped_observations | Wrong saved servings UI and unverified repair explain a probable mismatch; DB and text-changing layer unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 052 | compatible-but-different-scope | 原params共32occurrences/31完整内容类、恰一个二重对；特定title出现10次不等于10个重复。生成器至少8个同title/description贡献是通用下界，不是完整UI group；42视窗观测非42独立记录。未完成Delete confirmed，完整真实DB/行身份/合法34步可行性unknown。 控制裁定：MA04 |
| 058 | agree_on_scoped_observations | Wrong visible membership confirmed; actual clicked-menu IDs, DB insert/dedup/order mechanism unobserved. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 060 | disagree | 已见Select all14首/68:25与移除未commit是业务观测。evaluator读playlist.db joined duration_ms；并无历史最终行集/分支。RetroPlaylistDuration未调用基类初始化/存储隔离是独立源码风险，影响实际集合/seed范围unknown。只知道该次投影未显示per-song数值，不知道所有合法Details/原生路线都不存在。 控制裁定：MA06 |
| 076 | compatible-but-different-scope | 源码期望Grocery Shopping恰17:20却问after，契约冲突confirmed；Agent提交次日title与原oracle不符confirmed。它是否符合strict-after、该日限定/跨日范围及全局first未知；既不认定Agent正确，也不凭解释偏好认定跨日必违规。 控制裁定：MA07 |
| 085 | agree_on_scoped_observations | Wrong route/missing recipient/body/send directly explain noncompletion; historical helper root and evaluator provider rows unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 091 | compatible-but-different-scope | Answer is one observed contribution; second membership/6502m total source-linked probable, no original proto/DB total. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 098 | compatible-but-different-scope | 已见匹配literal node为0、未做semantic/numeric验收、一次swipe候选动作和reward0。正式初始整数、实际XML标签、active geometry、是否改变数值及精确末值未独立留证。若历史实际加载的谓词成功读int，则0逻辑含义为!=255；不是独立读值。无证据排除所有授权native Settings读回路线，也无证据证明初始255被该drag破坏。 控制裁定：MA09 |
| 106 | disagree | 固定proto三title与最终两title必长度拒绝confirmed；第三身份/在UI何处/是否可达/10步内能否完整遍历unknown。Show completed操作后两candidate离开当前viewport是观测，不由menu词/checkbox或排序配置标签证明真实group已存在/可进入，更不据此排除app/visibility问题。 控制裁定：MA10 |
| 107 | disagree | 提交20而oracleCOUNT6及采用label-membership谓词confirmed。各噪声具体绝对日期/formatter语义仅source-linked或probable。四个变化窗口拼接报告26行且保留同窗重复occurrences；被省略的窗口经原回包证为未变，不能认定丢数据或独立merge根因。稳定DB/row IDs仍缺，不据fingerprint声称任意情况下覆盖必正确。 控制裁定：MA08 |
| 115 | disagree | 可见Adventure最后两项反序及追加顺序confirmed；持久DB与UI映射、哪份Boolean通过仍unknown/probable。原分0.5且46/48主动结束，不是budget耗尽；gate结束时closed(agent_finished)。两次policy拒绝不计UI步骤。确已打开行菜单，未发现Move up/down；不等于所有合法reorder/repair不可能。 控制裁定：MA11 |



## 20案完整索引

| 索引/任务 | reward；终止；实际动作 | 可证发现与根因边界 | 置信范围 |
|---|---|---|---|
| [001 AudioRecorderRecordAudioWithFileName](#case-001) | 0；completed；9/20 | 源码文件名契约不一致；实际物理路径未留证 | 源码问题 confirmed；失分因果 probable |
| [003 BrowserMaze](#case-003) | 0；step_budget；20/20 | 6次未经效果验证的原生点击未移动；触摸有效后仅完成4步 | 行为链 confirmed；click底层机制 unknown |
| [004 BrowserMultiply](#case-004) | 0；completed；15/22 | 把即时读数当新生成值；未输入或Submit，尚余7步 | 未完成／验收错误 confirmed；新鲜度机制 unknown |
| [014 ExpenseAddMultipleFromMarkor](#case-014) | 0；completed；33/60 | 可见备注被加Reimbursable标记，oracle却比较未加标记的参考值 | 源码分裂 confirmed；DB失分因果 probable |
| [023 MarkorAddNoteHeader](#case-023) | 0；step_budget；12/12 | 正文已改；重命名走错界面，12/12才暴露Rename | 行为 confirmed；最终文件状态 probable/unknown |
| [024 MarkorChangeNoteContent](#case-024) | 0；completed；11/12 | 仅改正文，未执行重命名；11/12主动停止 | 行为 confirmed；最终磁盘内容 unknown |
| [030 MarkorDeleteNewestNote](#case-030) | 0；step_budget；10/10 | 未验证swipe删除，空集合误当目标缺席；实际删除 unknown | 策略／验收 confirmed；文件谓词 unknown |
| [033 MarkorMergeNotes](#case-033) | 0；completed；17/78 | 创建默认.md且少额外空行；自构expected不等于请求 | 已保存UI差异 confirmed；oracle短路 probable |
| [036 MarkorTranscribeVideo](#case-036) | 0；step_budget；20/20 | 在Download创建而oracle查Markor目录；Moria差异通过fuzzy | 路径行为 confirmed；失分路径 probable |
| [049 RecipeAddSingleRecipe](#case-049) | 0；step_budget；24/24 | servings变形后未验证修复即Save；文本变形层 unknown | 保存验收缺口 confirmed；DB因果 probable |
| [052 RecipeDeleteDuplicateRecipes3](#case-052) | 0；step_budget；34/34 | 32输入/31等价类；未完成真重复对确认，无Delete | 未删除 confirmed；策略根因 probable |
| [058 RetroCreatePlaylist](#case-058) | 0；completed；23/24 | 3次添加后只有1首；宽祖先XPath可能重复命中同一行 | 1首UI confirmed；定位别名 probable |
| [060 RetroPlaylistDuration](#case-060) | 0；step_budget；30/30 | 未测时长Select all后14首/68:25；移除未提交 | 聚合规划 confirmed；初始化风险独立 |
| [076 SimpleCalendarFirstEventAfterStartTime](#case-076) | 0；completed；3/10 | after阈值与恰在阈值的期望事件冲突；次日答案未获证明 | oracle契约 confirmed；自然语言正确答案 unknown |
| [085 SimpleSmsSendClipboardContent](#case-085) | 0；step_budget；12/12 | 前6步未推进目标应用；收件人未确认，无正文/发送 | 行为 confirmed；clipboard helper底层原因 unknown |
| [091 SportsTrackerTotalDistanceForCategoryOverInterval](#case-091) | 0；completed；12/20 | 1996m只是单项；第二候选未核实，6502m仅probable重建 | 缺聚合覆盖 confirmed；完整数值 probable |
| [098 SystemBrightnessMaxVerify](#case-098) | 0；completed；3/10 | 未做exact-state验收；实际XML/active geometry/初末整数与swipe效果未证 | 行为缺口confirmed；episode状态因果unknown |
| [106 TasksCompletedTasksForDate](#case-106) | 0；step_budget；10/10 | 2个标题对3个期望槽，第三标题未捕获；10步耗尽 | 基数拒绝 confirmed；过滤状态 probable/unknown |
| [107 TasksDueNextWeek](#case-107) | 0；completed；8/10 | label谓词计20、oracle6；原merge保留occurrences，未证冗余窗丢数据 | 日期谓词错误confirmed；formatter/具体日期仍probable |
| [115 VlcCreateTwoPlaylists](#case-115) | 0.5；completed；46/48 | 第二列表末两项反序；46/48非耗尽，保留reward0.5 | 顺序行为 confirmed；获胜持久分项 unknown |

## 公共因果边界

20案首个业务final均正确保留、合法string解析精确、goal和初始化时钟均可见；不能套用旧版missing-final、cleanup覆盖或number外层强转解释。391个结构化Python响应全部报告kernel alive，328completed/63failed；失败cell可能已有成功动作前缀，不等于回滚。352个实际获准UI动作，9案step_budget、11案completed；终止分类不替代动作耗费根因。原生-only和单动作代理策略拒绝不应误归为Runtime崩溃；策略可比性另列[module-map.md](module-map.md)。

**重要裁定**：001/014/076源码契约问题与历史失分分支分开；036的Moria拼写差异通过当前fuzzy，不能当独立失分解释；033的三行文本通过通用fuzzy却失败严格五行形状；115的46/48与closure=agent_finished反驳“耗尽”；091的6502m和004的20250只能按各自注明的源/假设范围引用。106第三标题、060完整歌曲时长集、状态类task的post-quit持久状态等保持unknown。

## 领域：media

原领域报告：[domain-media.md](domain-media.md)；结构化取证：[domain-media.json](domain-media.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Media failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Scope: cases 001,036,115, original attempt1. Companion machine-readable records: `domain-media.json`; exact offline query code/output: `domain-media-queries.md`.

#### Findings and confidence

|Case|Original outcome|Strongest supported finding|Cause confidence / boundary|
|---|---|---|---|
|001 AudioRecorderRecordAudioWithFileName|0.0, completed;9/20 accepted actions|Goal/params already end`.m4a`; reviewed oracle adds another`.m4a`. A six-second0.08Mb named recording is visible on a second screen.|**Confirmed source contract defect**, **probable episode-loss contribution**; actual full filesystem name/path not captured. Do not equate oracle zero with failure to record.|
|036 MarkorTranscribeVideo|0.0, step_budget;20/20 accepted actions|Agent deliberately creates transcription under Download, while oracle checks Documents/Markor. Saved UI string`Moria, Charlotte, Emilia` has a real typo but **passes current fuzzy content helper**(0.9130434782608695≥0.9).|**Probable path/existence failure**; persistent expected-path absence not logged. Output directory is implicit in oracle, not explicit in visible task. Visual source coverage incomplete.|
|115 VlcCreateTwoPlaylists|**0.5**, completed;46/48 accepted actions|Both 4 track playlist names visible; Adventure lasttwo visible tracks reversed. Two generic correction gestures denied **before** action admission; valid swipe left order unchanged. Agent's exhaustion explanation is false.|**Confirmed Agent ordering failure at UI layer**, **probable failed Adventure component**. Reward proves exactly one Boolean pass, not which. No DB snapshot.|

These are not blanket Runtime failures. All 69 actual Python executions in this slice returned a structured response with `kernelState=alive`. There are 10 failed cells:1 audio, 4 transcription, 5 VLC. Errors retain their actual layer: unavailable optional`lxml`, missing WebElement API, failed locators/waits, and explicit proxy gesture-policy denials. Successful continuation in the same Runtime is observed. No proposed mechanism/fix below is represented as approved or already implemented; AMKernel owner supplies a separate mechanism report.

#### Method and provenance

Original `result.json`, `normalized-agent-events.json`, `raw-private/business-submission.json`, and `raw-private/agent-events.jsonl` were read only. Large JSONL was streamed using local Eval, never dumped. Actual `tool_execution_start.args.content` was parsed only for write calls targeting`xd://mcp__amkernel_python_exec`; each was paired by **full** toolCallId with `tool_execution_end`. `domain-media.json.timeline` retains original Python code, exact start/end/message line anchors, full IDs, response timestamp, duration, actual status/kernelState, bounded original semantic fields and errors. Removed generic tree wrappers or absent media bytes are not silently replaced with interpretation.

Campaign records revision`55ddaf5edc6f6c25673aed343907d5b9dca66f84`。独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。 原共享19-file Harness身份收据保持原样；源码推导仍不等于实际文件/DB/媒体状态。

No product/config/test changes; no live device, ADB, Appium, MCP, task/score rerun, build, lint, formatting or suite execution. Pure probes only call AST-extracted side-effect-free helpers over actual recorded strings or explicitly hypothetical UI-derived rows. Parent must perform any integration verification; no such check is claimed here.

#### Common final-answer, clock and cleanup boundaries

- Exact original goal appears in raw user message_end line 9 for each case. Reference clock is`2023-10-15T15:34:00+00:00`, timezoneUTC, supplied as initialization reference. No date-relative predicate exists in these three; missing-clock/timezone is not an evidenced cause.
- First business finals are raw lines 3539(audio),7345(transcription),8499(VLC). All are valid nonempty string`taskOutcome` envelopes. Parent shared receipt proves these are first assistant stops, exact rawText matches archives, receipt hashes match, and timestamps are before cutoff/business deadlines. Later cleanup finals are ignored, never precedence replacements.
- `src/fsq_androidworld_eval/submission.py:45-93` parses original JSON, requires string, and strips only outer whitespace. `runner.py:787-788` uses parsed answer for InformationRetrieval only. **These tasks grade state**, not their final prose. Wrong prose can expose reasoning but cannot directly produce these file/DB rewards.
- `runner.py:716-737` finishes business and session cleanup before evaluator790-796; **driver.quit precedes evaluation**. Task teardown822-827 follows evaluation. Original result stage timestamps support this order. The three dedicated cleanup cells only call`driver.quit()` and report returned ownership; no restore/delete/reset occurs. Post-quit persistence is not captured, so quit effects remain unmeasured, but later teardown cannot explain the earlier score.
- A reference loop completion iteration is distinct from an accepted UI action: `stepped_agent.py:113-125` increments reference count when returning done with`appiumAction=None`. Audio10 reference/9 accepted and VLC47 reference/46 accepted are not hidden mutations. Transcription20/20 has no completion-only iteration.

<a id="case-001"></a>

### Case 001 — AudioRecorderRecordAudioWithFileName

#### Goal and exact oracle

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

#### Decisive timeline

|Python cell|Raw start/end lines; short toolCallId|Original returned fact / interpretation|
|---|---|---|
|2|747/748;`call_czDPwhYnxpaXyUjkLQelSz0Z`|`ModuleNotFoundError:lxml`, failed/alive. Agent recovers with stdlib ElementTree cell 3. No UI action lost.|
|7|2190/2191;`call_pkIzQbHCjPmq0MUroTW995Dq`|Record click; progress00:01, Recording…, M4a44.1kHz.|
|8|2467/2468;`call_gVpRBjyG0awtr7NaQq6QCl8v`|Stop click opens New name dialog, fieldRecord-1, Save available.|
|9|3074/3075;`call_ywIdmwOAiuSCSSLimghFDeI9`|Original code clears name, sends`presentation_fGwr`, saves. Returned`enteredBaseName` exact; visible title same,0.08MbM4a44.1kHz,00:06 duration.|
|10|3439/3440;`call_TwFo9hYNVtla8MrRdmIw4oNL`|RecordsActivity has list_item_name`presentation_fGwr`,0.08MbM4a44.1kHz,00:06. Cross-screen saved-list evidence, not physical filename bytes.|
|final|3539|Claims saved`presentation_fGwr.m4a`; valid first-business string.|
|11(cleanup)|3614/3615;`call_YwkP791CdGVmOk0cXZVdSrT2`|Only quit; completed/alive; quitReturnedtrue.|

#### Cause, evidence limits and responsibility

**Confirmed:** reviewed source uses inconsistent complete-name/stem semantics. Plain goal requests single suffix; current oracle demands double suffix. The first divergence from the *oracle literal target* is cell 9's stem input, but this is not a demonstrated wrong-user-goal choice: the app shows codec separately and hides the extension in title/list.

**Probable:** missing double-extension path explains reward0. The evaluator returned0without error, but its actual `find` output is not archived. The UI record strongly supports a saved recording entry, not exact disk existence. We cannot prove that the correct single-suffix physical file existed, which directory the backend used, or whether quit changed persistence. Contract defect confidence must not be conflated with historical filesystem/score causation confidence.

Not budget-limited:9 accepted/20, no rejections/denials, normal completion;11 nominal slots remained before final. Not a recording-start/save error in the visible UI. Optional lxml failure is recovered and not a Runtime death. Receipt parsing does not change file predicates.

#### Proposed fixes (not applied)

1. **Decision needed—AndroidWorld filename contract:** choose complete filename semantics (recommended: check recorded file_name verbatim) or stem semantics (then generate/display stem consistently). Update generator/template/oracle together in a separately versioned future benchmark; keep old score immutable. Do not teach the Agent a double-suffix workaround or silently accept arbitrary aliases.
2. **Proposed—Agent acceptance adherence:** existing amkernel-appium files guidance183-210already distinguishes title/stem/extension/full path and persisted read-back. Use available app file-info proof, or report unresolved physical name/path rather than assert it from title+codec. A Skill omission is not established by this trace. Added UI proof must fit existing budget and never bypass allowed interface.

Falsification: frozen task bytes differing materially, or original expected double-extension path actually present at evaluation, would defeat this mismatch as the sole score-loss explanation. No such persistent evidence was captured.

<a id="case-036"></a>

### Case 036 — MarkorTranscribeVideo

#### Goal, source video and file predicates

Visible goal locates video`ZwUN_moment_70_.mp4` **in Download** and asks a comma-separated sequence in Markor file`ZwUN_moment_70__transcription.txt`. The goal does **not** explicitly name the output directory. Actual params: messages`["Maria","Charlotte","Emilia"]`, text`"Maria,Charlotte,Emilia"`, seed1222528574, plus seven exact noise filenames retained in JSON.

`markor.py:877-941` delegates success to`CreateFile(params,MARKOR_DATA)`. `Markor.initialize_task:60-62` clears notebook; `CreateFile.initialize_task` clears common storage; target generator902-908writes video underDOWNLOAD_DATA, each message8s. `user_data_generation.py:219-304` uses mp4v,320x240,30fps(default),240frames/message, yellow text at(50,120) on random per-frame RGBnoise. These are **source-intended generation properties**, not an historical ffprobe. Exact observed VLC target description in cell 6 is`Video: ZwUN_moment_70_, Duration:24seconds`; correct title and total duration are actually observed.

`file_validators.py:199-226` requires:

1. Full path`/storage/emulated/0/Documents/Markor/ZwUN_moment_70__transcription.txt` exists (`MARKOR_DATA` from`device_constants.py:32`). Missing path returns0 before content is read.
2. `cat` exactly that notebook path; decode, remove`
`, strip outer whitespace; compare to recorded text with`fuzzy_match`. `fuzzy_match_lib.py:20-51` uses case-insensitive SequenceMatcher ratio≥0.9—not exact CSV equality and not per-name scoring.

The observed UI string`Moria, Charlotte, Emilia` vs reference`Maria,Charlotte,Emilia` yields **0.9130434782608695, acceptedTrue** in the isolated current helper. This pure probe does not re-run the task, read any file or establish that evaluator ever reached content comparison. The Maria→Moria error is real relative to initialized params, but **not a sufficient zero-reward cause under the current content helper**.

#### Actual rendered coverage, not a guessed transcript

- Cell 8(raw 2388-2390,`call_JKSYK2CVcXhGOWv4mtNGf9XK`) clicks exact target and samples38screenshots,1.43–24.88s since click, returning VideoPlayerActivity. Cell 9(raw 2636-2637) then reports **Video player tips**, Close, NEXT, Player controls. This first sample pass was not a demonstrated unobscured complete sequence.
- Cell 10(raw 2931-2934) dismisses tips and captures a screenshot. Original PNGpayload is RPC-elided; retained metadata is not pixels.
- Cell 11(raw 3397-3400,`call_4TBUNgLIGt9XVncAkaYRUCRS`) samples38more frames over0.34–23.24s after a new loop clock, cropping video y760..1640. It returns **MainActivity**, so playback ends during collection. No seek/replay/reset occurs. These times are loop elapsed times, not media positions.
- Cell 12(raw 3863-3865,`call_G4Ujy9Ssgwn0gsQGcxzH57em`) builds a JPEG from retained frames2indices16,18,...36. The intact338307-byte JPEG/SHA256`ccc6e9dbda2ce40d678c27f09b500bbd53eebff94573c1eb3b7bb0bc87e16782` visibly shows **Emilia** at indices 16/18(loop10.30/11.49s), then VLC library/noise thumbnails from index 20(loop12.89s) onward.
- Earlier PNG strings contain explicit`…[... chars elided for RPC frame]`; call11 has five display metadata entries but only two elided image payloads. Complete early Maria/Charlotte rendered evidence and original MP4 are not captured here. The expected full sequence comes from actual initialized params/source, **not an invented visual reading**. Noise thumbnails are not additional target messages. No repaired/recreated media or random-parameter transcript is substituted.

#### Destination and save timeline

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

#### Cause and proposals

**Probable zero cause:** the file was created underDownload while oracle requiresDocuments/Markor. Initial notebook clearing and no observed recreation there support this explanation, but persistent absence at evaluator time is unobserved. **Confirmed behavior:** Agent associated source-media folder with output folder and navigated away. **Comparability risk:** visible task omits the output directory that the oracle silently requires. Do not label this an explicit user-goal folder violation or a proven oracle-code bug.

Save exhausted the real20 action budget, leaving no accepted mutation capacity to move/correct/reopen. Budget did not prevent the final Save; it prevented later correction/verification. Early visual obstruction and typo are important behavior/evidence issues, but neither proves score cause. Four failed cells all retain kernelalive and are recovered; no Runtime crash is shown.

Proposals, all separate from cause:

1. **Agent adherence:** keep source and destination bindings separate. Retain observed app notebook for an unspecified output folder; compare extension/name/current folder independently before creating. Existing Skill files-and-notes and budgeting guidance already covers this; trace violation is not proof of missing guidance. Never hardcode hidden evaluator path as an Agent answer.
2. **Decision needed—future task contract:** expose Documents/Markor output directory, or explicitly define another accepted scope; version any changed benchmark. Original result remains0.
3. **Visual/API handling:** dismiss tips before timing capture; collect readable bounded source-message evidence with sequence boundaries; stop/report uncertainty rather than invent first-name reading. Use observedclear/send_keys instead of unavailable set_value. Fewer giant sheets reduce archival elision risk, but its exact owning mechanism needs separate review. Fixing Moria alone would not flip the current fuzzy comparison.

Falsification: actual file-info/persistent proof that the Download creation context saves toDocuments/Markor defeats path hypothesis; actual media showingMoria rather than initializedMaria would change visual error attribution. Neither was captured.

<a id="case-115"></a>

### Case 115 — VlcCreateTwoPlaylists

#### Exact ordered goals and fractional oracle

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

#### Construction and correction evidence

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

##### Which predicates are proved?

|Predicate|Evidence status|
|---|---|
|Both requested playlist identities exist in app;4tracks each|**Observed** overview26.|
|Adventure contains allfour requested visible stems|**Observed** detail27and32. Exact`.mp4` DBfilenames not read.|
|Adventure visible order lasttwo reversed|**Observed**, complete4-item list; construction chronology independently agrees.|
|Adventure exact SQLitepositions/filenames fail|**Probable**, not captured. Pure helper on explicitly UI-derived rows returnsFalse atpositions2/3.|
|Ultimate exact order correct|**Probable** from append chronology17→21→24, not detail readback/DB proof.|
|Ultimatecomponent=1,Adventurecomponent=0|**Probable** consistent with above and0.5, not directly archived.|
|ExactlyoneBooleancomponent=1|**Derived with certainty from0.5** under reviewed oracle aggregation.|

##### Budget allegation is refuted

Original result: **46 accepted / 48 max**,47 reference iterations (includes completion),`exhausted=false`,`closureReason=agent_finished`,0ActionGate rejected;33 Python calls exceed30 **advisory**, which explicitly doesnotaffectreward. Two nominal accepted mutation slots remained at the last business mutation; after firstfinal, Agent-finishedcloses actionphase, not exhaustion.

The two errors29/30 are `appium_proxy._validate_actions:271-306` policy failures: exactlyone touch pointer source and one complete contactcycle. Handler`appium_proxy.py:494-502` calls authorization **before**`ActionGate.submit`, so these 2unsupported commands do not appear in accepted ledger and do not increment its rejectioncount. Audit records2deniedCommandCount withunsupportedoperation, while gate records0rejectedActionCount. No budget-exhaustion exception/steering occurs for VLC. Do not infer serialization specifics beyond reject class: original serializedW3Cpayloads are not retained, though exact helpers/errors are.

#### Cause and proposals

**Confirmed root behavior:** out-of-order append created correction debt; two incompatible generic drag helpers were denied before admission, a valid swipe made no visible progress, and Agent stopped with an incorrect exhaustion explanation. **Probable score component:** Adventure fails ordering, Ultimate passes; exact DB/subscore pair is unknown. This is not a Runtime death, accepted-action cap, or proof of a proxy bug. Currentpolicy deliberately rejectsmouse/multisource/incompletegestureforms; the prompt does not spell out every serialized restriction, an interface clarity issue for decision rather than a proven implementation defect.

Proposals:

1. **Agent adherence:** append requested files in exact sequence rather than defer grouped earlier item. Keep the local intended sequence and compare all-item detail order, not a four-track summary. Existing Skill already requires independent order/persistence criteria; a Skill omission is not proven.
2. **Decision needed—gestureinterface:** clarify one-touch/source/contact-cycle contract and pre-admission vs budget refusal. Use a valid touch/hold/move only when needed and in budget; read back actual order. Do not relax the proxy blindly or map mouse automatically. A successful compliant reorder within the remaining two slots is **not observed or promised**.
3. **Proposed future diagnostic evidence:** bounded read-only join rows/component results before/after quit and at scoring would separate UI order from DB positions and prove which playlist passed. Preserve old campaign state/reward; do not capture a whole private DB or conflate such instrumentation with an Agent fix.

Falsification: archived serialized gesture satisfying all validator conditions would identify a proxy mechanism bug; DB positions differing from the visible list could change component attribution. Existing trace cannot settle either.

### Complete accepted-action ledgers

The tables below enumerate **every accepted mutation**; per-action paths/status/full IDs and corresponding original code/result are in JSON. All accepted statuses areHTTP200. Failures before mutation or policy admission are excluded and described separately. Counts are actual gated commands, not Python call counts.

#### 001-AudioRecorderRecordAudioWithFileName

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

#### 036-MarkorTranscribeVideo

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

#### 115-VlcCreateTwoPlaylists

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

#### Reproduction and missing state

Use `domain-media-queries.md` for exact standalone extraction, pure helper code and actual outputs, including retained JPEG decode. No reproducible query here fabricates filesystem/database snapshots or regenerated media. Stronger historical component proof would require original expected-path listing/cat or playlist join rows around quit/evaluation, plus unelided early target frames; these were not captured in assigned attempt files. They are **missing historical evidence**, not instructions to rerun these observed failures.

## 领域：browser

原领域报告：[domain-browser.md](domain-browser.md)；结构化取证：[domain-browser.json](domain-browser.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Browser failure analysis — cases 003 and 004

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Full exact cell code, toolCall IDs, original structured PythonResponses, action ordinals/timestamps and evidence pointers: [domain-browser.json](domain-browser.json). Reproducible read-only probes and outputs: [domain-browser-queries.md](domain-browser-queries.md). Original evidence/source/configuration was not changed.

#### Findings and confidence

| Case | Proven outcome / immediate cause | Root distinction |
|---|---|---|
|003 BrowserMaze | Zero reward; X stopped at (3,1), two Right moves short. Gate admitted20 UI actions and refused the next. Six native direction element clicks had no visible effect; coordinate touch did move X. | **Confirmed Agent behavior failure:** unverified six-action batch consumed recovery margin. **Unknown lower-level click mechanism**, not an AMKernel Runtime diagnosis. |
|004 BrowserMultiply | Zero reward; final81000, but page still displayed10/Click Me. No product input or Submit call; seven permits unused. Five immediate reads returned9,9,10,10,10, not established fresh generations. | **Confirmed Agent behavior failure:** collection freshness/phase and in-app completion were not established. **Unknown click/accessibility timing mechanism.** Native-only context denial is Harness policy, not Runtime bug. |

Both attempts have valid string submissions, no invalidReason, and clean session quit. Proposed fixes are not approved or implemented mechanisms. Loaded Skill already contains the required freshness, phase-aware wait, unverified-basis probe, and completion invariants.

#### Shared oracle, initialization and dependency boundary

Official `android_world/android_world/task_evals/single/browser.py`:

* `BrowserTask.initialize_task:56–85` invokes base initialization, clears device storage and Chrome data, grants notification permission, substitutes `params.browser_task_seed` into inline HTML, and puts task.html in Downloads. Outer `params.seed` seeds Python initialization, **not** browser JavaScript. Chrome data clearing creates real cold-first-run overhead.
* `BrowserTask.initialize_device_time:49–54` enables automatic date/time. Both original prompts contain initialization reference2023-10-15T15:34:00+00:00, UTC; it is not live device time. Neither task is date-dependent.
* `BrowserTask.is_successful:98–109` obtains UI state and current package; reward0 unless package is com.android.chrome, then reward1 iff any UI element has exact text `Success!`. No partial credit, DB predicate, or chat-answer comparison.
* These classes inherit BrowserTask→TaskEval, **not MiniWoBTask**. The inline HTML has no external script/network requirement. MiniWoB uses another app and reward broadcasts (`task_evals/miniwob/miniwob_base.py:25–59,112–141`); that dependency is excluded. Chrome's No internet connection banner is not evidence the local puzzle is unavailable.

Harness `runner.py:716–737` finishes agent/owned-session cleanup **before** evaluator790–796; task teardown follows at821–826. Both agent `driver.quit()` calls return and audit has zero active sessions. Evaluator-time UI trees were not retained, so exact post-quit package/tree remains unknown. Both tasks are nevertheless unfinished **before** final/quit; no evidence supports successful task state erased solely by cleanup.

`submission.parse_submission:45–93` parses original JSON, requires nonempty string, strips whitespace, never coerces numbers. `omp_supervisor.py:211–234` selects first assistant stop before cleanup/cutoff. Maze first final raw line4067; Multiply line5205. Archived answers exactly match those first finals; later cleanup prose is ignored. For browser tasks even a correct numeric final cannot replace in-app solving.

Harness19-input identity证据保持原共享收据。独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。 Browser revision文件hash及31行列表见review原件；历史初始化task.html、JS变量/时序未归档，源码条件重建仍不能冒充当时运行变量。

<a id="case-003"></a>

#### 003 — BrowserMaze

##### Exact request and randomized board

Goal: “Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.” Actual raw original goal/control prompt is JSONL line9, fully reproduced in JSON. Params: browser_task_seed1364588068, outer seed3308742614. Complexity2 allocates20 interactions (`suite_utils._allocate_step_budget:491–502`).

`BrowserMaze.HTML:181–247` uses a32-bit LCG and randomized DFS-like stack ordering. Exact extracted JS with actual seed produces this board, matching **all16 visible cells** in retained screenshots (zero-based row/column):

```text
X . # #
# . . .
. . . .
. . . $   ($ is green goal)
```

Walls=(0,2),(0,3),(1,0); start=(0,0); goal=(3,3). Full topology is **known**, not extrapolated from incomplete accessibility. Shortest path R,D,D,D,R,R is six moves. Source-only exact JS probe reaches(3,3) and replaces body with `<h1>Success!</h1>`. Moves must stay in bounds and avoid walls (`browser.py:278–320`). The six-step attempted route was correct; no wall/path error explains no movement.

##### Historical execution and complete action accounting

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

##### Locator, timing and policy distinctions

Call19/3498–3499 exposes native button labels/bounds: Up[8,842][115,918], Down[124,842][276,918], Left[283,842][409,918], Right[418,842][562,918]. Right touch(490,880) and Down(200,880) are inside observed controls. Six element clicks leave start unchanged; subsequent right touch visibly moves. Thus semantic click delivery was not established before widening. No per-click on-device dispatch trace distinguishes native accessibility click behavior, delayed dispatch, or other Appium/Chrome event effects. Coordinate success is page/geometry-specific evidence, not a universal fallback mandate.

WEBVIEW_chrome appeared in driver.contexts; call17/3226–3227 failed `UnknownMethodException: Only native Android context is supported`. Exact string comes from `AppiumAuditProxy._authorize`, appium_proxy.py878–880. Prompt explicitly requires native interactions. This is **intentional Harness policy**, not kernel failure, broken Chromedriver readiness, or proof AMKernel lacks WebView support. No setup repair follows from that refusal.

FirstRunActivity hosts multiple pages: call9 timeout is reconciled by fresh Turn on sync? state. Call11 timeout followed by same prompt is real no-observed-progress, but does not prove why dismissal did not land. Phase predicates avoid invalid activity-only waits; that alone does not recover the six wasted maze permits.

##### Cause and proposed fixes

**Confirmed proximate cause:** gate closure two moves short. **Confirmed behavior root:** six-action batch used unverified input and consumed recovery margin. Loaded amkernel-appium.md (raw read end96, embedded text114–150; current source113–149) already requires probing unverified basis, business change rather than HTTP success, reconciliation before retry, and stopping dependents on divergence. No missing Skill rule is established.

**Proposed adherence change, not implemented:** define X-position postcondition, use first intended move as small probe, inspect effect, widen only after delivery is reliable. If unchanged, distinguish pending from ineffective input using fresh bounded evidence before an evidence-backed touch. Count remaining actions. Ten startup +six effective moves fits20 with four permits spare; **counterfactual ledger, not rerun result**. Do not blanket-convert element clicks to taps or blindly retry late clicks.

**Decision-needed prompt clarity only:** runner.PROMPT_TEMPLATE could distinguish advertised WEBVIEW contexts from native-only permitted selection. This avoids a failed observation, not a consumed UI step, and does not diagnose no-effect clicks. Prompt changes affect future comparison identity.

<a id="case-004"></a>

#### 004 — BrowserMultiply

##### Exact request, state machine and collection boundary

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

##### Actual collection, phase and complete ledger

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

##### Locator/timing explanation and confidence limits

Source exposes bare HTML ids button/number through native accessibility. AppiumBy.ID(button) lookup failed, while UiSelector text Click Me and resourceId(number) succeeded. UiAutomator2 ID auto-qualification is **plausible, not proven**; actual lookup normalization/config was not retained. No AMKernel parser/kernel bug is established.

Five element-click requests HTTP200, reads9,9,10,10,10 never reach form. Ineffective/delayed native clicks and stale accessibility reads are alternatives; per-click browser events/source timestamps are missing. Under current source/no-reload assumptions, final10 is consistent with only one effective generation advance, but exact live clickCount is **unknown**. **Confirmed:** requested five clicks did not establish the five-click phase transition; fresh source and final screenshot retain old controls. **Not confirmed:** specific Runtime/Appium/Chrome/accessibility-cache defect.

WEBVIEW denial at call14 has the same exact native-only Harness-policy origin as Maze, after charged Keep Google. Native source stayed observable, kernel alive. No unrestricted WebDriver route, arbitrary script, or new session was authorized or needed to explain score.

##### Cause and proposed fixes

**Confirmed immediate/behavior root:** agent substituted repeated immediate reads for acknowledged generation, omitted initial number in collector, then stopped without entering/submitting despite seven unused permits and visible pre-form state. Not budget shortage or pure multiplication error. Existing loaded Skill explicitly says reads do not prove freshness, values may legitimately repeat, retain initial disappearing task data, and verify phase—not stable label/activity.

**Proposed adherence change:** preserve initial visible value, establish interaction efficacy, acknowledge phase without requiring numeric difference, require fifth-click button/number disappearance plus input appearance. If freshness is unresolved retain uncertainty, not guesses/replays. Then input product, Submit, observe Success!. Do not hardcode diagnosis-derived20250 into future agents. Nine startup +five puzzle clicks +one input +Submit fits22, excluding extra focus/recovery; no future success claimed.

**Decision-needed wording:** BrowserMultiply.goal336–342 could say remember initially displayed number plus each subsequent generated number, then after five clicks enter product. Existing goal can be correctly interpreted from app flow; benchmark wording change affects comparability and does **not** repair ineffective clicks or missing submit. No oracle implementation bug demonstrated.

#### Evidence gaps / hand-off

Maze topology is complete. Multiply expected source sequence uses actual seed, but runtime JS variables/initialized HTML not independently archived. Internal native-click delivery, per-click freshness and evaluator-time UI after quit remain unknown, not Runtime-fault conclusions. No device/API calls, formal task/score reruns, tests/builds/linters/formatters were run. Only recorded offline queries/probes exercised. No temporary scripts created. Proposed behavior/prompt changes are unimplemented/unapproved; independent amkernel-owner mechanism analysis remains separate. Parent may validate report JSON/schema/cross-case integration after all domain reports land.

## 领域：editing

原领域报告：[domain-editing.md](domain-editing.md)；结构化取证：[domain-editing.json](domain-editing.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Editing-domain failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.
Scope: **014 ExpenseAddMultipleFromMarkor**, **023 MarkorAddNoteHeader**, **024 MarkorChangeNoteContent** only.

#### Findings and confidence

| Case | Established outcome | Causal finding | Confidence boundary |
|---|---|---|---|
| 014 | Both reimbursable entries saved and reopened in app detail views; reward 0; historical oracle warns expected Laundry missing | Source note adds `. Reimbursable.` to target note fields, while oracle compares unchanged original notes. Faithful source copying fails the 0.9 fuzzy predicate | Source inconsistency and comparator rejection confirmed; actual final DB values not archived, so precise episode field-level causation probable |
| 023 | Correct 67-character header/content string visible after Save; no rename; 12/12 actions | Ungrounded title/settings rename exploration reached actual contextual Rename only at last allowed action | Missing rename behavior confirmed; historical disk existence/content probable/unknown rather than a captured filesystem result |
| 024 | Correct 20-character replacement visible after Save; no rename; 11/12 actions | Same wrong rename workflow; voluntary incomplete final despite one action unused | Missing rename behavior confirmed; **not actual budget exhaustion**; disk bytes unknown |

The reports do **not** attribute these failures to Runtime death. All 60 structured execution responses in these three cases report `kernelState=alive`: 49 completed, 11 failed. Failures are explicit client/API, syntax, selector/wait or proxy-protocol errors with successful continuation. These are not missing tool results or fabricated successful calls.

#### Evidence and method

`domain-editing.json` is the detailed machine-readable deliverable. Each record contains complete exact raw Python request code, actual returned structured response facts/errors, full toolCall IDs, 1-based physical JSONL line anchors, stages/receipt clock anchors, oracle source symbols/ranges, action ledger mapping, uncertainty, responsibilities and proposed fixes. Original result/events/submission files were never modified.

The large raw JSONL files (approximately 103 MB, 64 MB and 91 MB) were streamed. Only complete `tool_execution_start/end` records and relevant messages were extracted; message-update snapshots, encrypted thinking and private/base64 trees were not dumped. `tool_execution_start.args.content` is parsed as the original JSON Python request. `tool_execution_end.result.content[].text` is parsed as the returned PythonResponse. Returned values are kept distinct from interpretation; `status=failed` is not treated as rollback.

`domain-editing-queries.md` records exact executed offline probe code and actual output. It verifies all 102 source-note rows against **actual initialized parameters**, isolates the exact pure source comparator with AST, and compares actual captured editor strings. It never imports device modules or queries a device. No task/score replay, tests, build, formatter, ADB, Appium or MCP execution was performed.

Source line references describe the current checkout; SHA256 values are in JSON. Parent receipt `shared-offline-checks.json` reports frozen/current harness-source digest agreement, original prompt/clock/string contract and parsing/receipt checks. That harness digest is **not** represented here as an independent proof of frozen AndroidWorld oracle-source equivalence. Historical raw prompt/cells/results and the expense oracle warning provide the episode evidence.

##### Clock and submission

Each exact initial user prompt is physical raw line 9. It includes the corresponding `result.task.goal`, initialized `2023-10-15T15:34:00+00:00` reference clock, UTC timezone, explicit UI-action allowance, native-interaction restrictions and first-business-final nonempty string contract.

| Case | First business final raw line | Receipt seconds | Evaluator start Unix | Cleanup cell raw start/end |
|---|---:|---:|---:|---|
| 014 | 6014 | 224.76301295799203 | 1794247487.9014661 | 6089–6090 |
| 023 | 3558 | 194.24156875000335 (finalization phase) | 1794249347.257635 | 3628–3629 |
| 024 | 3927 | 181.25186045805458 | 1794249563.627269 | 3997–3998 |

The archived business answer is the first assistant `stop`, not later cleanup prose. All three archived submissions are valid string taskOutcome contracts. These are state tasks: none of these oracles scores the prose answer instead of saved app/file state. No raw-to-stripped answer conversion explains a failure here.

Raw tool events do not carry wall-clock timestamps; executionCount/durationMs are real returned Runtime facts, not invented wall timestamps. JSON retains the actual result.stages timeline and receipt anchors.

Parent source analysis places `adapter.finish` and owned-session cleanup before official evaluator, and task teardown after evaluator (`runner.py:716–737,745,790–796`). Each dedicated `driver.quit()` returns true before evaluation. No cleanup cell restores business content or performs rename. Post-quit disk state is not captured, so absence of cleanup rollback evidence is not proof of persistent bytes. Later task teardown clears these app data and cannot be used to reconstruct historical final state now.

<a id="case-014"></a>

#### 014 — ExpenseAddMultipleFromMarkor

##### Exact initialized transaction collection

Visible task: “Go through the transactions in my_expenses.txt in Markor. Log the reimbursable transactions in the pro expense.”

Official source `task_evals/single/expense.py:328–360` uses two target rows and 100 noise rows. The expense table is cleared, noise is inserted, and `before` is snapshotted by `SQLiteApp`/`AddMultipleRows` (`common_validators/sqlite_validators.py:257–310`). The source note consists of copies of targets with `. Reimbursable.` appended to note, plus all noise, shuffled, written under `/storage/emulated/0/Documents/Markor/my_expenses.txt` by `write_to_markor`.

The source note was **actually read in full**, not inferred from params or a random seed: raw L1188–1189, execution 6, `call_PlkNLBnz2WNT6r6Gs96twEnK`. Returned editor text is 4,608 characters, 103 lines including header, 102 data rows, no terminal LF; SHA256 `ebb5adfcb8b638a179403c9d13d8bcd9b7168587eb516730fe88a4e3d25d35ca`. Header is `name|amount_dollars|category_name|note`. The first data row is Educational/$296.94/Donation/Want to have; last is Jeans/$139.3/Clothes/Want to have. Every parsed row equals the actual initialized target-plus-noise multiset; missing and unexpected sets are empty. Full observed text and all 102 rows are preserved in JSON.

Exactly two rows contain the classification marker:

| Physical source-note line | Name | Amount | Category / DB ID | Source note | Oracle reference note |
|---:|---|---|---|---|---|
| 59 | Laundry | $96.3 = 9630 cents | Clothes / 8 | `Urgent. Reimbursable.` | `Urgent` |
| 72 | Car Insurance | $303.01 = 30301 cents | Transportation / 7 | `I may repeat this. Reimbursable.` | `I may repeat this` |

This reconstructs the complete source collection and selection boundary: there is no unexplained third reimbursable transaction, missed page, or premature end of note.

##### Actual transfer and historical persistence evidence

- Execution 12 raw L2934–2935 types Laundry, `96.3`, `Urgent. Reimbursable.`, then hides keyboard. A `UiScrollable` lookup is rejected because a locator cannot hide multiple interactions. **Those prior field mutations remain.** Execution 13 L3091–3092 returns all three exact typed field values.
- Executions 14/15 swipe the category carousel and click Clothes. Returned text nodes all report `selected=false`; these text-node flags do not prove the actual category-selection state. Execution 16 L3726–3727 saves; Home list includes Laundry/96.3.
- Execution 17 L4305–4306 types Car Insurance, `303.01`, `I may repeat this. Reimbursable.` and hides keyboard, returning exact fields. Executions 18 and 19 fail AST compilation with unmatched `)` **before** their initial swipe, so they do not save or duplicate the entry. Execution 20 L5239–5240 swipes, clicks Transportation and saves; Home lists both target names/amounts.
- Execution 21 clicks Car Insurance then wrongly waits for an editable field; timeout does not undo the click. Execution 22 L5699–5700 captures the actual **Expense Detail** view: Car Insurance, `303.01`, USD, `I may repeat this. Reimbursable.`.
- Execution 23 L5970–5971 closes Car detail and reopens Laundry: returned name Laundry, amount `96.3`, note `Urgent. Reimbursable.`, title Expense Detail.

Reopened record-detail views are materially stronger persistence evidence than a filled form, but are **not a DB dump**. Category IDs, exact cents conversion, full table size and preservation of 100 original noise rows are not captured. The snapshot after quit is also absent.

##### Oracle contradiction and pure causal probe

`_ExpenseAddMultiple.validate_addition_integrity` (`expense.py:264–285`) compares `name,amount,category,note`, fuzzy only for name/note. `AddMultipleRows.is_successful:304–310` passes **unchanged** `self.params[ROW_OBJECTS]`, not the source-note marker-bearing copies.

`validate_rows_addition_integrity:149–192` requires every reference row to match some final row, exact final length `before+2`, and every original row unchanged. `fuzzy_match_lib.py:20–51` uses case-insensitive `difflib.SequenceMatcher(...).ratio() >= 0.9`. No per-expense subscore exists.

The exact isolated pure comparator produces:

- `Urgent` vs `Urgent. Reimbursable.`: 0.4444444444444444 → false.
- `I may repeat this` vs `I may repeat this. Reimbursable.`: 0.6938775510204082 → false.
- Constructed candidates with actual target cents/category and **observed** marker-bearing notes fail; same candidates without classification suffix pass. This construction isolates the note mismatch; it does not pretend the unarchived final DB equals the construction.

Historical evaluator output independently corroborates the reference side: `evidence/.../run-full.log:279` says:

```text
WARNING:absl:Expected row Expense(name='Laundry', amount=9630, category=8, note='Urgent', created_date=1697320800000, modified_date=1697320800000, expense_id=-1) not found in the 'after' state.
```

This proves the historical missing-reference branch, not merely a zero label. It still does not print the row that was present, so category/cents error in addition to the note discrepancy cannot be excluded. The incidental ffmpeg warning immediately before it is not evidence that media infrastructure caused this SQLite failure.

**Root:** confirmed task source/reference inconsistency and comparability risk; probable concrete episode score cause. **Not root:** selection coverage, action exhaustion, Runtime failure, answer parsing.

##### Exact accepted-action budget

33/60 interactions; no exhaustion, no rejected budget admission, 27 unused.

| Accepted steps | Count | Actual purpose |
|---|---:|---|
| 1–3 | 3 | Drawer swipe, Markor launch, source note open |
| 4–8 | 5 | Back twice, Home key, drawer swipe, Pro Expense launch |
| 9–19 | 11 | Add Laundry; three focus/input pairs; hide keyboard; category swipe/click; Save |
| 20–30 | 11 | Add Car; three focus/input pairs; hide keyboard; category swipe/click; Save |
| 31–33 | 3 | Open Car details, close, open Laundry details |

Breakdown: 4 gesture actions, 18 clicks, 2 Back, 1 Home press, 6 inputs, 2 hide-keyboard. The rejected UiScrollable observation is a protocol denial outside this accepted ledger; syntax failures consume no UI action. `referenceStepsExecuted=34` includes terminal loop accounting and is not the 33 actual mutations.

Business final correctly names both entries, but overstates category certainty: categories were clicked, not reopened in a category-bearing persistent view. The notes were copied literally; there is no visible instruction that reimbursable text is transient selection metadata to omit.

##### Proposed correction choices

Decision required, not an already approved fix:

1. **Align references with source notes**: make the target reference notes include the same marker the user sees, while retaining cents/category strictness and unchanged-noise validation. This matches natural “log these transactions” copying.
2. **Explicit metadata policy**: preserve original reference notes but clearly label marker as classification metadata in goal/representation and tell the agent which data to copy. Changes prompt/comparability rather than silently expecting hidden stripping.
3. **Task-local marker normalization**: accept a narrowly defined marker-present/absent equivalence. Do not lower global fuzzy threshold or weaken unrelated tasks.

A bounded before/after comparison diagnostic captured before teardown would resolve the remaining historical uncertainty. It requires a privacy/retention decision; this investigation adds no instrumentation. A marker-policy fix is falsified as a sufficient episode fix if the actual historical row also has incorrect cents/category or is absent.

<a id="case-023"></a>

#### 023 — MarkorAddNoteHeader

##### Required file/content boundaries

Original full name `2023_08_10_neat_wolf.txt`; destination `busy_wolf_2023_07_23.txt`; header `RnI8sP34yDzJQbvkfplR`; source sentence `Weekend plans: Hiking trip to Blue Mountain.`.

`markor.py:754–774` clears directory via base initialization, creates the exact target and 1–20 variant noise files. `file_utils.create_file:134–169` uses shell echo, adding LF. Actual source editor raw L1478, execution 8, contains `Weekend plans: Hiking trip to Blue Mountain.\n`; the trailing newline is observed, not guessed.

Oracle `markor.py:784–806` demands original path absent, destination path present, then **exact** CR-normalized `header + "\n\n" + original_content + "\n"`. The 67-character requested result is:

```json
"RnI8sP34yDzJQbvkfplR\n\nWeekend plans: Hiking trip to Blue Mountain.\n"
```

No content-only partial score is awarded. A correct editor string cannot compensate for missing rename.

##### Exact action chain and why rename was missed

- Exact accessibility row `File 2023_08_10_neat_wolf.txt ` opens the target at L1317–1318; source text matches params. It is not a similarly named wolf backup.
- Execution 9 L1683–1684 constructs `expected = header + "\n\n" + old`, then calls nonexistent `editor.set_value(expected)`. Returned AttributeError occurs before editor mutation/Save; kernel remains alive.
- Execution 10 L1886–1887 uses `clear(); send_keys(expected)`, checks editor equality, clicks Save and returns the exact 67-character string with `matchesExpected=true`. Offline exact comparison agrees with oracle content expectation, **in UI only**.
- Execution 11 L2104–2105 clicks document title, then waits merely for an EditText. The existing note editor already satisfies that wait. Returned facts show the same original document, not a filename dialog. The “Opening note rename dialog” intent is not evidence of such a dialog.
- Execution 12 opens More options: File settings, Share, Tools, Info, Reload. Execution 13 selects File settings and waits for **no ListView**. The replacement File settings menu also has a list, so this postcondition times out. Execution 14 returns Wrap words, Syntax highlighting, Auto-format, Font Size, Format, Preview—the wrong surface for rename.
- Execution 15 backs to editor, original title unchanged. Execution 16 tries default Selenium ActionChains click-and-hold; proxy rejects its non-single-touch payload with “Use one touch pointer and one contact cycle per step.” No accepted UI action is recorded for it.
- Execution 17 L3310–3311 backs to file list. Visible wolf candidates include exact original, `_2023_02_21` variant and `_backup`. This is a substring-filtered visible sample, not the complete noise directory.
- Execution 18 L3512–3515 uses native `mobile: longClickGesture` on the **exact original**. The response finally exposes `Rename`, resource `action_rename_selected_item`, and `Selected 2023_08_10_neat_wolf.txt`. No rename dialog, destination input or confirmation follows.
- During this admitted long-click, raw L3513 steering announces action exhaustion; L3515 still delivers the actual completed result. The first final at L3558 honestly states header updated but rename incomplete. Cleanup execution19 quits only.

The actual causal error is ungrounded rename navigation and false-positive transition detection, not a mysteriously too-small action number. It used the whole allowance before reaching the correct contextual action. The loaded Skill file/notes section already required distinguishing displayed title from full filename and preserving line breaks; missing behavior is not proof the Skill lacked that invariant.

##### Accepted-action ledger

12/12; exhausted true; closure `step_budget`. Python cells: 19, including cleanup.

| Step | Action | Cell |
|---:|---|---:|
| 1 | Drawer swipe | 3 |
| 2 | Markor click | 5 |
| 3 | Exact original file click | 7 |
| 4 | Clear editor | 10 |
| 5 | Input expected header/content | 10 |
| 6 | Save | 10 |
| 7 | Ineffective document title click | 11 |
| 8 | More options | 12 |
| 9 | File settings | 13 |
| 10 | Back settings | 15 |
| 11 | Back editor to list | 17 |
| 12 | Exact file native long-click; Rename exposed | 18 |

AttributeError and rejected ActionChains do not appear in accepted ledger. `rejectedActionCount=0` is gate accounting, not a claim that no unsupported command was rejected. No mutation was attempted after the gate closed.

##### Persistence limit, root and fixes

The original full-name row remains in the list after Save/navigation and is selected at the end. No rename request exists in raw history. Thus missing rename behavior is confirmed and original-path oracle rejection is probable. The oracle filesystem branch and file bytes were not captured after quit; do not promote UI “savedField” naming into disk proof. No cleanup restore occurred; teardown later deletes files.

Propose using the observed exact-file contextual Rename path earlier, with native one-touch selection, then inspecting the actual filename/extension fields. Avoid unsupported set_value and wait for rename-specific identity, not any EditText. Preserve the observed terminal LF and blank line exactly.

A content-first plan of opening target, clear/input/Save, Back, native long-click, Rename and dialog editing is a **proposed** action allocation, not demonstrated successful 12-step execution: the rename dialog never opened, so field count/extension handling remain unknown. Rename-first is another option but may cost more navigation. Skill reinforcement is proposed only; no coordinated amkernel owner fix has been approved here.

<a id="case-024"></a>

#### 024 — MarkorChangeNoteContent

##### Actual original and exact requested changes

Original `strong_jacket_h1hZ.txt`; destination `lively_fox_2023_03_22.md`; replacement `inNqu8UNNtyXBHCZpYp7`.

Unlike header task, initial random content is not in params. It is **captured** by raw L2186, execution8: `pZwh1hZwvmPj5inNqu8U\n` (20 generated characters plus LF). No random regeneration was used to guess it.

Oracle `markor.py:700–721` first requires original path absent, new full path present, then `check_file_content` with default fuzzy matching. That helper removes CR, strips persisted content and compares to requested text at 0.9 threshold. Therefore the exact LF requirement from case023 does **not** transfer to this task. The `.txt`→`.md` filename boundary does matter, but no rename/extension field was ever opened.

##### Raw execution chain

- Execution2 fails importing unnecessary `lxml` before any action; execution3 uses standard-library ElementTree successfully. This is a recovered observation issue, not device failure.
- Launcher Search click, input `Markor`, app click; execution7 finds exact target title but relative XPath parent `..` lookup throws before click. Execution8 then opens the exact accessibility row `File strong_jacket_h1hZ.txt `; original content and title captured.
- Execution9 repeats unsupported `editor.set_value` and gets AttributeError before mutation. Execution10 L2615–2616 performs clear/input; exact requested text returned. Execution11 L2873–2874 clicks Save, returns original title and requested replacement.
- Execution12 opens More options; its tuple-list return is bounded non-JSON representation, **not visible menu evidence**. Execution13 explicitly returns labels File settings, Share, Tools, Info, Reload. Execution14 chooses File settings; facts show only formatting options.
- Execution15 L3662–3663 backs to editor and returns title `strong_jacket_h1hZ`, `clickable=false`, `longClickable=false`.
- Despite this evidence, execution16 L3893–3894 clicks title. Returned facts still show the same original title and the replacement editor. No rename dialog exists.
- Business final L3927 says content saved but filename could not be changed “within the UI interaction budget.” This is an incomplete self-report, **not evidence of an exhausted gate**. Execution17 quits.

##### Action ledger and root distinction

11/12 accepted, exhausted false, rejectedActionCount 0, closure `agent_finished`; one action unused. Search/launch/open cost 4; clear/input/Save cost 3; options/File settings/Back/ineffective title click cost 4. No contextual file-list selection, Rename click, destination name input or confirmation occurred.

The remaining single interaction would not by itself finish an unopened multistage rename. That does not make budget exhaustion the root: the ledger proves the Agent voluntarily stopped, and four post-save interactions went down the wrong route. The task was not silently marked successful—final admits partial outcome—but the required two-part behavior was not delivered.

Original content replacement is confirmed in editor after Save and again after unsuccessful title click. It is not reopened from disk. Original title remains throughout, and no rename request was issued, making original-path-still-exists the probable zero branch. Final filesystem bytes and oracle per-branch trace remain unknown.

**Root behavior:** wrong rename route and continuation/acceptance planning. **Not established:** Runtime defect, intrinsic impossibility in12 actions, saved-file corruption, hidden extension-only mistake or answer coercion.

Propose allocating actions for both text and exact full filename before mutation, using a lower-cost drawer launch when observed and the actual file-list contextual action rather than non-clickable document title. Case023 proves the same APK exposes contextual Rename, but this is cross-case mechanism evidence—not an observed024 dialog. Inspect separate name/extension fields before entry; do not assume `.md` from a title. Rename-first vs edit-first requires observing the actual dialog/action count; no completion feasibility claim was tested. Report actual gate status and distinguish Save/editor evidence from filesystem persistence.

#### Ownership and next decisions

All edits are diagnosis artifacts under this domain only. No product, Skill, configuration, source, tests, manifest, original evidence or device state was changed.

- **014:** owner decision on visible-marker semantics and benchmark comparability; retain original score/history. A task-local explicit policy is preferable to global fuzzy weakening.
- **023/024:** Agent workflow failures; Skill changes remain proposed, not proof of absent guidance. amkernel owner supplies its separate mechanism/fix assessment.
- **Evidence gap:** bounded pre-teardown filesystem/DB predicate evidence would discriminate persisted-state alternatives. Current historical evidence cannot be recreated from a fresh device or random seed.
- **Checks for integrator:** inspect these three JSON records and their exact raw anchors; no product test/build is needed to consume this diagnosis. Offline probe output is already recorded; no formal task or score rerun is authorized.

## 领域：notes

原领域报告：[domain-notes.md](domain-notes.md)；结构化取证：[domain-notes.json](domain-notes.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Notes failure analysis — cases 030 and 033

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.

#### Conclusions and confidence

| Case | Strongest demonstrated finding | What remains unknown |
|---|---|---|
| 030 MarkorDeleteNewestNote | After nine actions exploring/opening menus, the final permitted action was a guessed horizontal swipe. The sole post-swipe check saw **neither note and zero file-title rows**, yet final claimed deletion. Official reward0.0, step-budget termination. Confirmed strategy/acceptance failure. | Whether the swipe deleted anything, changed tab/view, or exposed a transient/empty hierarchy; exact oracle timestamp list and physical failed predicate. |
| 033 MarkorMergeNotes | Read all three correct sources; saved and reopened **mIObBbo4.md** with three lines. Oracle requires exact extensionless **mIObBbo4** and five lines with blank separators. Readback equality was only equality to the Agent's own wrong construction. Confirmed observed artifact mismatch. | Exact first oracle failure branch and final file bytes after quit; no filesystem inventory was retained. Exact-name gate failure is probable, not directly logged. |

No Runtime defect is established in either case. All28 returned Python executions had `kernelState=alive`; case030 has13 completed/4 failed, case033 has11 completed. Both have a successful dedicated quit, no task-state restoration in cleanup, official evaluator after quit, and task teardown after evaluation. Loaded guidance already explicitly covered filename identity, independent acceptance, source terminators, survivor retention and budgets; these traces are not proof that the Skill omitted those invariants.

The companion [`domain-notes.json`](domain-notes.json) contains full per-call toolCallIds, exact historical code, selected original PythonResponse fields, timestamps, structured causal responsibilities and proposals. [`domain-notes-queries.md`](domain-notes-queries.md) contains exact executed read-only query code/output and current source hashes. The parent's [`shared-offline-checks.json`](shared-offline-checks.json) owns shared first-final/parser/frozen Harness checks. No product/config/source/test changes, device calls, formal task/score reruns or test suites were performed.

#### Provenance and evidence interpretation

Paths below are relative to campaign root `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/`. `raw:L` denotes the original per-attempt `raw-private/agent-events.jsonl` JSONL line/event sequence. A start event supplies the executed code in `args.content`; its paired end supplies the actual structured PythonResponse. Python `result.deleted` and `persistedMatch` fields are **caller-created interpretations**, not native oracle results.

Recorded AndroidWorld revision`55ddaf5edc6f6c25673aed343907d5b9dca66f84`，package0.1.0。独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。 Markor2.10.9/code146、APK hash `1a328c5324b3b33d6cb4d55085637707252569d98c0ffe1cb7089aebbd903256`仍来自正式资产/attestation；metadata、post-quit文件/内容缺口未被source blob核对关闭。

---

<a id="case-030"></a>

#### 030 — MarkorDeleteNewestNote

##### Goal, initialized population and time ordering

Exact original prompt at `episodes/030-MarkorDeleteNewestNote/attempt-1/raw-private/agent-events.jsonl:9`:

> Delete the newest note in Markor.

Params: `seed=1958615684`; allocated10 UI actions. Reference clock `2023-10-15T15:34:00+00:00`, UTC, is visible in the prompt. It is the **initialization reference**, not the live clock after note creation.

Source: `android_world/android_world/task_evals/single/markor.py:317-372`. Initialization creates2–6 `_generate_random_note()` files in `/storage/emulated/0/Documents/Markor`; after each creation it advances the clock by a random minute delta in **[-500,500]**, which can go backwards (`markor.py:324-346`; `datetime_utils.advance_system_time:161-183`). Creation sequence cannot be treated as chronological newest. Base setup resets time/apps, seeds random (`task_eval.py:137-157`), and clears nonhidden Markor entries (`markor.py:57-66`; `file_utils.py:102-130`). `.app` can remain because wildcard clearing does not remove dot entries.

Actual bounded initial semantic snapshot: cell5, `raw:1182-1183`, short ID `call_udqJeYe8KonRPNQmb86zlGNo`:

| Row | Type | Actual displayed time | Meaning |
|---|---|---|---|
| `final_friendly_king.md` | Note/file | `10/15/2023, 15:34` | Selected target; newer by17 displayed minutes. |
| `fine_jelly_final.md` | Note/file | `10/15/2023, 15:17` | Intended survivor. |
| `.app` | Folder | `10/15/2023, 15:35` | Later time but **not a note**; do not delete as newest note. |
| `..` | Parent folder | `/storage/emulated/0/Documents` | Parent navigation, not a note. |

The query returned25 semantic facts, below its100-entry cap, with only two file rows. That is a strong visible two-note population, **not an independent top-level regular-file inventory** proving no hidden/filtered file exists. Neither raw initialized metadata nor exact creation sequence was returned. Opening the target in cell6 (`raw:1430-1431`) yielded title `final_friendly_king` and body `Better late than never.\n`. The other note's body is unknown. UI timestamps suggest the selected target is correct; no contrary evidence supports a wrong-visible-candidate diagnosis. Oracle timestamp alignment is separate.

##### Exact oracle and source-level ambiguity

`MarkorDeleteNewestNote.is_successful:348-368`:

1. Read current top-level regular files using `file_utils.get_file_list_with_metadata`.
2. Sort both initial and current lists ascending by `.change_time`.
3. For **every current index**, require current filename and timestamp to equal initial filename and timestamp at that index. Any mismatch returns0.
4. Return1 only if the new list has exactly one fewer file.

Equivalent success: remove only the final sorted initial file and leave every earlier file's recorded timestamp unchanged. It does **not** check content, size, full_path or directories, and has no partial score. For the visible population, expected task state is target absent, `fine_jelly_final.md` retained; the oracle additionally requires survivor timestamp unchanged. Extra files can reach an unchecked initial-list index; ties have no explicit semantic rule. Neither edge is observed here.

**Separate comparability issue:** `FileWithMetadata` documents `.change_time` as ctime (`file_utils.py:60-74`), but actual helper command is `ls directory -ll -au` (`495-549`, specifically519-520). Upstream Toybox documents `-u` as **atime**, and long output uses that selected time for display ([primary source](https://raw.githubusercontent.com/landley/toybox/master/toys/posix/ls.c)). Parsed time removes the last3 fractional characters and omits the timezone. This is a confirmed mismatch in the inspected source contract; access-time preservation can make a read affect oracle state depending on mount policy. It is **not a confirmed cause of this episode's0.0**: no actual initial/final `ls` output or atime policy exists here, and current upstream help is not a byte-verified emulator binary. Do not silently substitute UI modified time for oracle atime/ctime or infer final mtimes from the reference clock.

##### Reconstructed execution and action ledger

Read `episodes/030-MarkorDeleteNewestNote/attempt-1/result.json.stepBudget.actions` together with the original code; sanitized ledger entries alone have no locator meaning.

| Action | Cell / raw start–end | Actual effect / evidence |
|---:|---|---|
| 1 | 4 /1001–1002 | Activate Markor; MainActivity. |
| 2 | 6 /1430–1431 | Open `final_friendly_king.md`; read title/body. No deletion. |
| 3 | 7 /1619–1620 | Open document More options; subsequent wait for `Delete` times out. The click remains consumed. |
| 4 | 9 /1992–1993 | Enter File settings. Menu is Wrap words, Syntax highlighting, Auto-format, Font Size, Format; no delete. |
| 5–7 | 10 /2320–2321 | Back, More options, Tools. Only `Speed Read` is observed. |
| 8–9 | 11 /2429–2430 | Back twice to file list; target still present. |
| 10 | 15 /3418–3419 | One valid right-to-left touch swipe over target row, HTTP200; returns only `{"admitted":true}`. This exhausts budget. |

**Non-admitted failures and recovery**:

- Cell2, `raw:603-604`, `ModuleNotFoundError: No module named 'lxml'`; failed before UI query. Cell3 switches to stdlib ElementTree and sees launcher. This is an optional dependency assumption, not dead Runtime.
- Cell7's menu wait fails after action3. Read-only cell8 (`1788-1789`) observes actual overflow: File settings, Share, Tools, Info, Reload. No Delete was captured.
- Cell12, `2843-2844`, short ID `call_Hpn7zgrTJpwDwozMJezsesar`: `ActionChains(driver)` appends a touch device but still builds through default `pointer_action`; proxy rejects `Only a single native touch pointer is supported`. This is pre-admission schema rejection: **0 consumed actions**, `appiumSessionAudit.deniedCommandCount=1`; it is not gate rejection.
- Cell13, `3023-3024`: both note names still present. This properly reconciles the failed gesture instead of assuming rollback/success.
- Cell14, `3249-3250`: `PointerActions.move_to_location() got an unexpected keyword argument 'duration'` before `builder.perform()`. No UI pointer-down was sent;0 actions.
- Cell15 corrects local construction and sends the final admitted gesture. Harness budget steering at `raw:3424` forbids more mutations but explicitly allows read-only observations. No subsequent mutation is attempted.

Totals: **10/10** accepted =1 activation +5 clicks +3 Back +1 gesture. Seven actions are route exploration/return after the target is opened. Seventeen Python executions are not17 UI actions:13 completed,4 failed, all alive; advisory30 calls is not the task budget. Gate `rejectedActionCount=0` and proxy denied1 refer to different stages (`appium_proxy.py:_validate_actions:271-306`, `_authorize:830-908`). No actual over-budget action refusal occurred.

##### Final evidence does not prove a deletion

Cell16 `raw:3553-3554`, short ID `call_wwBbOezFyFUZYEoXjTlBqcRD`, executes:

```python
src=driver.page_source
{'activity':driver.current_activity,
 'deleted':'final_friendly_king.md' not in src,
 'remainingNewestPresent':'fine_jelly_final.md' in src,
 'visibleTexts':[e.attrib.get('text') for e in ET.fromstring(src).iter()
                 if e.attrib.get('resource-id','').endswith('opoc_filesystem_item__title')]}
```

Original result:

```json
{"activity":".activity.MainActivity","deleted":true,"remainingNewestPresent":false,"visibleTexts":[]}
```

The label `deleted=true` is merely substring absence. **Both target and required survivor vanish from this UI query, and there are zero title rows.** Nothing proves the queried source is a stable current Files population, same folder/tab, a successful delete confirmation, or persistent one-file removal. A navigation/switched-tab/transient/empty accessibility surface remains possible. An actual wrong/multiple deletion also remains possible; do not select a convenient mechanism without evidence. Current Harness source forwards GET source after exhaustion and does not synthesize an empty source (`appium_proxy.py:856-861`; forwarding506-538). This does not diagnose the app/accessibility mechanism.

At `raw:3678`, the **first** business final is `{"taskOutcome":"Deleted the newest note in Markor."}`. Its reasoning in the same original message explicitly says the absence is ambiguous, possible switched tab/empty list, but the final ignores that qualification. That is a confirmed unsupported-completion behavior, not proof of persistent deletion. The receipt is finalization phase at144.99028741696384 seconds, within cutoff144.99939066695515 and business limit720. Valid string parsing preserves the same answer; cleanup cannot overwrite it (shared receipt; `submission.py:45-93`; `omp_supervisor.py:211-234`).

Dedicated cleanup cell17 (`3762-3763`) only calls `driver.quit()` and returns success. Evaluator later returns0.0, then teardown clears task state. `result.json` has no error or invalidReason. No file list/body/timestamp before or after quit exists, so neither the exact failure predicate nor quit side effects can be isolated. The separate pre-run rehearsal has no metadata and is not final-state evidence.

##### Cause, responsibility and minimal proposals

**Confirmed root:** Agent route/budget and acceptance failure. The target selection is consistent with observed times, but the Agent spent the budget on irrelevant document menus, guessed swipe-delete semantics, then accepted empty-hierarchy absence without survivor retention. **Unknown physical root:** actual swipe effect and exact oracle file/timestamp discrepancy. **Separate code-level concern:** helper's documented ctime versus `-u` access-time mismatch, not proven score causation.

Loaded `amkernel-appium.md` is actually archived in this trace (`raw:95-96`): historical content184-211 requires independent acceptance/full identity/persistence;283-295 requires intended deletion and retained unique survivors;344-352 requires budget accounting and truthful incomplete reporting. Thus no unsupported “missing Skill rule” or generic Runtime blame.

1. **Proposed Agent strategy/acceptance fix:** establish full observed target/survivor population, inspect native row/context affordances early, and require a semantically identified Delete flow rather than presumed swipe behavior. Budget for confirmation before spending nine actions on editor menus. Accept only target absent **and retained survivor present in a stable correct-scope nonempty collection**; otherwise report unverified. A long-press/context menu might be useful but no exact successful route/action cost is proven by this record. Do not implement Runtime auto-delete/auto-correction. **Risk:** promising an unobserved route or adding a verification mutation after exhaustion. **Falsification:** future captured recognized Delete+confirmation with stable target-absent/survivor-present evidence but oracle0 moves root investigation toward metadata/persistence.
2. **Proposed caller gesture fix:** when an actually justified gesture is needed, use one supported native-touch builder and API signature; the successful cell15 form already avoids the two construction errors. This removes wasted failed calls, not the unproven delete semantics. **Risk:** successful swipe transport still does not mean deletion. **Falsification:** a retained supported single-touch payload receiving the same denial would refute caller-construction attribution.
3. **Decision-needed oracle/helper fix:** define newest timestamp semantics first, then use an explicit intended field with deterministic ties; align task wording and visible evidence. Do not silently replace shared helper default or retroactively award success. Archive bounded initial/final metadata in future evaluator diagnostics. **Risks:** benchmark comparability/shared callers, and this episode could still fail because no valid delete happened. **Falsification:** recovered frozen implementation/binary semantics differ or final metadata proves timestamp mismatch irrelevant; historical branch remains unknown without files.

---

<a id="case-033"></a>

#### 033 — MarkorMergeNotes

##### Goal, actual files and initialization

Original exact goal at `episodes/033-MarkorMergeNotes/attempt-1/raw-private/agent-events.jsonl:9`:

> Merge the contents of Markor notes tough_frog_2023_08_05.txt, proud_cat_edited.txt and 2023_08_21_friendly_koala.md (in the same order) into a new Markor note named mIObBbo4 and save it. Add a new line between the content of each note.

Params seed2594989658; budget78 UI actions, business4800s; reference2023-10-15T15:34Z/UTC visible but not relevant to merge comparison. Source `markor.py:510-650`; base Markor clears task directory; `CreateFile.initialize_task` clears commonly used regular-file storage/downloads before creating the three source notes (`file_validators.py:191-197`; `user_data_generation.py:458-485`). The output is **not** precreated. `file_utils.create_file:134-169` writes with `echo`, appendingLF.

Actual source read evidence, cells5–6 `raw:990-991,1232-1233`:

| Required order | Filename | Exact returned editor text (escaped) |
|---:|---|---|
| 1 | `tough_frog_2023_08_05.txt` | `m4kMyOGWaENoPj6FqLjd\n` |
| 2 | `proud_cat_edited.txt` | `fxHXZsqrmnwYjXvte9pg\n` |
| 3 | `2023_08_21_friendly_koala.md` | `f42GOjFWb2aKHogAFQSY\n` |

All lengths21 =20 captured alphanumeric characters +LF, and all match the exact task params. The source order is correct. Expected source paths are under `/storage/emulated/0/Documents/Markor`; no raw final directory/file metadata or final source-preservation snapshot was captured. No source deletion/edit/overwrite call appears, but that is not direct final filesystem proof.

##### Exact oracle gates, filename and newline conditions

`MarkorMergeNotes.__init__:542-560` creates a `CreateFile` validator with exact `file_name="mIObBbo4"` and:

```python
"\n\n".join([file1_content, file2_content, file3_content]) + "\n"
```

Expected exact identity is `/storage/emulated/0/Documents/Markor/mIObBbo4`, **not** `.md`. Expected text (escaped):

```text
m4kMyOGWaENoPj6FqLjd\n\nfxHXZsqrmnwYjXvte9pg\n\nf42GOjFWb2aKHogAFQSY\n
```

Three ordered gates, binary reward/no partial credit:

1. `CreateFile.is_successful`, `file_validators.py:199-209`: recursive `find`, require exact full path membership (`file_utils.check_file_or_folder_exists:228-258`). No extension normalization or title matching. Missing exact path immediately0.
2. `file_validators.py:211-224`: `cat` exact path, decode/removeCR/strip; fuzzy compare with expected. `fuzzy_match_lib.py:20-51` uses case-insensitive difflib ratio≥0.9.
3. Only if gate1–2 pass: `markor.py:603-638` rereads exact path, removeCR/strip, splitLF and require exactly5 lines with empty lines at indices1 and3. The added separators must produce **blank lines** because each initialized source already has a terminatorLF.

The task prompt could be read superficially as “three lines separated by LF”; however preserving each complete original source including its terminator **and adding a new LF** supports the oracle blank-line requirement. This is wording/comparability risk, not demonstrated oracle code defect. Naming a note with no extension can also be confused with its display title/default extension, but the visible goal does not grant automatic `.md` normalization. Loaded Skill already warns about both. Source comment609-611 says content less than20 while generator640-650 actually emits20; it does not affect the predicate here.

##### Execution and actual action ledger

Cell3 activates Markor and immediate enumeration is empty (`687-688`); cell4 waits2s and captures screenshot (`787-789`). Later exact semantic note reads succeed; screenshot is not needed to establish the identity/format defects. No assertion here depends on interpreting it.

| Action | Cell / raw start–end | Meaning |
|---:|---|---|
| 1 | 3 /687–688 | Activate Markor. |
| 2 | 5 /990–991 | Open first exact source. |
| 3–6 | 6 /1232–1233 | Back/open second; Back/open third; capture all source strings. |
| 7–8 | 7 /1468–1469 | Back; New file/folder. |
| 9–13 | 8 /1776–1777 | Clear Name; enter `mIObBbo4`; confirm; focus editor; send constructed text. |
| 14–17 | 10 /2501–2502 | Save; Back twice; reopen listed output. |

Cell7's **original result** exposes distinct fields: Name=`my_note`, extension=`.md`, Type=`Markdown`. Cell8 changes only Name. Code is decisive:

```python
name.clear(); name.send_keys('mIObBbo4')
driver.find_element(AppiumBy.ID,'android:id/button1').click()
# ...find editor...
expected=''.join(source_texts)
editor.click()
editor.send_keys(expected)
actual=editor.get_attribute('text')
# returned matched = actual == expected
```

No extension-field clear/rename is executed; no new separator is inserted. SourceLF terminators are retained, but merely concatenated. `matched=true` in cell8 (`raw:1777`) is equality to that63-byte construction, not independent task acceptance.

Cell10, short ID `call_73yP4P6gk93sy28aP5iDUc9g`, genuinely saves, leaves editor through two Back actions, returns to MainActivity, finds a filename containing `mIObBbo4`, reopens it and reads editor. Its code **deliberately allows** a displayed extension, but task oracle does not. Actual original response `raw:2502`:

```json
{"listedAs":"mIObBbo4.md","title":"mIObBbo4","readback":"m4kMyOGWaENoPj6FqLjd\nfxHXZsqrmnwYjXvte9pg\nf42GOjFWb2aKHogAFQSY\n","expected":"m4kMyOGWaENoPj6FqLjd\nfxHXZsqrmnwYjXvte9pg\nf42GOjFWb2aKHogAFQSY\n","persistedMatch":true}
```

This is strong **app-level persistence** for the wrong-identity/wrong-format artifact, not just an unsaved visible editor. Title hides suffix; actual list identity exposes it. It is not raw filesystem proof at evaluation, and it does not independently show that an extensionless sibling was absent. Only one created output is observed, output was not initialized, and all writes target the default-suffix new note: first exact-path failure is therefore **probable**, not directly logged.

Totals: **17/78 accepted actions,61 unused**, kinds1 activation+8 clicks+5 Back+1 clear+2 inputs, zero denials/rejections. Reference loop count18 includes done iteration; do not count as18 UI actions. Eleven Python calls, all completed/alive; advisory30 not exceeded. Failure was not budget-constrained. No source-destructive operation, recovery or uncertainty timeout occurs.

##### Pure causal probe and final outcome

Executed read-only string probe (full code/output in query companion), using actual captured source/readback and exact params, not invented task answers:

| Comparison | Actual result |
|---|---:|
| Captured source lengths | `[21,21,21]` |
| Reopened UTF-8 bytes |63 |
| Oracle expected bytes |65 |
| Reopened text equals Agent construction |true |
| Reopened text equals oracle expected text |false |
| LF lines after strip |3, none blank |
| Strict five-line/blank-index predicate |false |
| General fuzzy ratio |0.9763779527559056 ≥0.9, passes |

Thus **even if captured bytes were placed at the exact required path**, strict blank-line shape would fail. That is a pure counterfactual predicate calculation, not proof gate3 ran in the actual evaluator; wrong filename probably short-circuited gate1. No final filesystem inventory/cat was archived to show actual branch.

First final at `raw:2543` claims “Created and saved Markor note mIObBbo4 … separated by new lines.” Receipt business phase128.13530791690573 seconds, cutoff128.1428666249849, within4800s. Valid string archive/strip preserves it. Prose is not the task oracle: `runner.py:787-792` only assigns interaction_cache for InformationRetrieval, and these are file tasks. Separate cleanup cell11 (`2616-2617`) only quits successfully. Official evaluator then0.0; teardown afterward clears task state. No evidence that quit transformed name/content, but no after-quit raw file proof exists either.

##### Cause, responsibility and minimal proposals

**Confirmed root:** Agent used self-constructed `expected` and extension-hidden title as acceptance; independently observable output name and requested additional separators were not enforced. Correct source order/acquisition and successful app save do not negate those defects. **Probable scoring mechanism:** exact-name gate sees no extensionless target; strict shape independently rejects the observed saved content if evaluated under that name. **Not supported:** Runtime text corruption, wrong source order, save loss, budget exhaustion, answer coercion or cleanup overwriting the first business final.

Historical loaded `amkernel-appium.md` (`raw:51-54`, content184-211) already says readback equality only proves input consistency; verify full filename including extension; distinguish existing terminators from newly requested separators. This is an execution/acceptance failure despite present guidance, not a proven missing-rule defect.

1. **Proposed Agent acceptance/construction fix:** derive exact full output identity and requested separator before creating. For these actual21-character source strings, `"\n".join(source_texts)` preserves their terminators and adds the requested LF, yielding65 bytes. Use an app-supported exact-name creation/rename path after inspecting the separate extension field; clearing `.md` may be minimal but was **not exercised here**, so do not claim proven support. Reopen exact filename and compare against goal-derived identity/order/format, not only same-variable construction. Preserve sources. **Risks:** blind trim/double-LF normalization can destroy meaningful source trailing blank lines on other notes; forcing every extensionless title into a universal policy is wrong; no Runtime auto-renaming/auto-correction. **Falsification:** exact-named artifact with independently verified ordered65-byte expected content still0 under matching frozen oracle would require path/cleanup/evaluator investigation instead.
2. **Decision-needed oracle wording/comparability change:** consider explicitly requesting exact extensionless filename and one **additional** LF between complete source contents (blank line for initialized notes). Alternative policy accepting `.md` or three-line interpretation changes benchmark semantics and must not be silently adopted or retroactively rescore this attempt. **Risk:** overfitting hidden expected bytes rather than clarifying the user-visible contract; wording alone cannot enforce Agent adherence to already-present generic guidance. **Falsification:** if frozen authoritative task guidance already unambiguously exposes both details, extra wording adds nothing needed.

#### Remaining evidence gaps

- Case030: exact initialized/final regular-file metadata/order, all mtimes/ctimes/atimes, post-swipe correct scope/tab/folder, actual deletion/undo/confirmation and final source/filesystem state are unavailable. Zero rows cannot distinguish navigation/accessibility loss/no deletion/wrong or multiple deletion.
- Case033: exact extensionless target existence at evaluation and actual first failing gate, final source-file preservation/metadata and after-quit bytes are unavailable. Do not call `.md` app readback a filesystem snapshot or assert gate3 executed.
- No final Markor DB snapshot exists; these task oracles operate on files, not a proven app DB. Same-campaign rehearsal records are separate initializations and contain no missing file metadata.
- Review已核31-file revision内容；历史import/安装bytes及具体文件metadata仍缺。缺失数据或evaluator0不许可伪造状态、重播RNG填历史或新任务/评分/设备操作。

All proposals are **unapplied**, separate from causes, and not approval of any amkernel-owner mechanism/fix report.

## 领域：recipe

原领域报告：[domain-recipe.md](domain-recipe.md)；结构化取证：[domain-recipe.json](domain-recipe.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Recipe failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope is **049 RecipeAddSingleRecipe** and **052 RecipeDeleteDuplicateRecipes3** only. This is diagnosis, not a proposed score change or a product/config/test patch. Machine-readable detail, original generated Python code, complete per-command ledgers, returned facts, full toolCall IDs, and initialization params are in `domain-recipe.json`.

#### Evidence and method

- Root C: `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.
- Case A49: `C/episodes/049-RecipeAddSingleRecipe/attempt-1`; A52: `C/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1`.
- Raw anchors below are **1-based JSONL line/event sequence** in each attempt's immutable `raw-private/agent-events.jsonl`. A `tool_execution_start.args.path` naming `xd://mcp__amkernel_python_exec` holds code; actual Python status/UI evidence comes from its paired `tool_execution_end.result.content[].text` JSON response, not the normalized success flag. Full logs were streamed; no base64 or full raw log was dumped.
- Read-only queries inspected archived params, exact tool code/structured responses, original prompt, business submission and result stage ordering. A pure stdlib AST extraction exercised the current fuzzy comparison; grouping used actual archived initialization rows, not generated substitutes. No AndroidWorld import with device side effects, device/ADB/Appium/MCP call, task/score replay, test suite, or source/config edit occurred.
- 原共享prompt/parser/hash/Harness收据保持原样。独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。
- The agent actually read the frozen Skill at raw end lines32/54/55 in both attempts. Returned bodies equal the corresponding current local Skill bodies modulo one terminal newline. Thus focus/readback, budget reservation, duplicate equivalence, and occurrence preservation guidance were already present. A trace violating guidance does **not** show guidance was absent.

##### Persistence and cleanup boundary

`recipe.py:28-49` targets `/data/data/com.flauschcode.broccoli/databases/broccoli`, table `recipes`, primary key `recipeId`. `SQLiteApp.list_rows` delegates to `sqlite_utils.get_rows_from_remote_device`; that helper pulls a DB into a temporary local directory and executes `SELECT * FROM recipes;` (`sqlite_utils.py:53-103`). Inserts omit `recipeId`, commit, push DB and close the app (`sqlite_utils.py:173-212`; `sqlite_schema_utils.insert_into_db:439-468`). `recipeId=-1` in result params is an insertion placeholder, **not** the real identity. No original before/after DB export, WAL/SHM snapshot, assigned IDs, or per-predicate evaluator diagnostic is present in either attempt directory.

`SQLiteApp.initialize_task` clears DB, initializes the app, clears again, then inserts noise (`sqlite_validators.py:257-263`). Addition captures that noise as `before`; deletion inserts the two target copies, captures `before`, and takes the last two returned rows as target IDs (`:280-283,348-358`). No guessed DB ID is used in this analysis.

`runner.py:716-737` finishes the agent and verifies/cleans its session **before** `agent_protocol` and evaluator (`:745-796`). Each actual cleanup cell only calls `driver.quit()`; no cleanup UI mutation appears. Task teardown and its DB clear occur **after** evaluator (`:821-838`). Thus task teardown did not clear the DB before scoring; however no post-quit/pre-evaluator persistence snapshot exists, so cleanup's effect on persistence cannot be directly measured. A successful quit is not itself proof of business-state preservation.

<a id="case-049"></a>

#### Case 049

##### Request, oracle and initialized data

Goal: add **Chicken Caesar Salad Wrap** with:

| Field | Requested value |
|---|---|
| description | An ideal recipe for experimenting with different flavors and ingredients. |
| servings | `3-4 servings` |
| preparationTime | `2 hrs` |
| ingredients | `as desired` |
| directions | Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand. |

Archived seed is374064309 and text representation is `text_block`. Ten archived noise recipes initialize the app: Quinoa Salad with Vegetables; Garlic Butter Shrimp; Turkey and Cheese Panini; Stuffed Bell Peppers; Raspberry Almond Smoothie; Lentil Soup; Quick Fried Rice; Vegetarian Chili; Avocado Toast with Egg; Greek Salad Pita Pockets. They are **initialization inputs**, not individually exported persistent records. The requested target is not inserted initially; desired final count is11.

Exact current-source oracle:

- `RecipeAddSingleRecipe` (`recipe.py:412-417`) uses `_RecipeAddMultipleRecipes.validate_addition_integrity` (`:354-384`) and `AddMultipleRows.is_successful` (`sqlite_validators.py:304-310`). Binary reward only; no subscores.
- For every reference target, some after row must match `title, description, servings, preparationTime, source, ingredients, directions, favorite`.
- First seven fields are free-form: `fuzzy_match` lowercases values and accepts `difflib.SequenceMatcher(...).ratio() >=0.9` (`fuzzy_match_lib.py:20-51`). `favorite` must match exactly0. Empty source must also match under that predicate. Target `imageName` and target ID are not compared, but all original noise rows are preserved by full dataclass equality, including their IDs and imageName.
- After count must equal before+1 (11); every before row must remain unchanged (`validate_rows_addition_integrity:149-190`). No answer-text scoring is involved.

##### Chronology and earliest proven deviation

1. Session creation succeeds, returned `newCommandTimeout=300`; all15 structured PythonResponses say `kernelState=alive`.
2. Calls3–5 open app drawer, Broccoli, New Recipe. The initial semantic form observation exposes title, description, source, servings, time, ingredients and directions IDs (raw1280).
3. Call6 fills title and description (steps4–7), then `find_element(new_servings)` fails before sending servings (raw1683→1684, `NoSuchElementException`). Call7 observes only title/categories/description/source while description remains focused. **Earliest execution divergence:** assumed form visibility did not survive keyboard/layout change. No rollback occurred; title/description stayed entered.
4. Call8 hides keyboard and scrolls (steps8–9), then sees lower fields. Call9 pre-caches four element handles, types servings (steps10–11), clicks preparation time (step12), and raises its own `Focus failed` before typing time (raw2320). The click returned200 but did not satisfy focus. A failed Python cell was not a failed/rolled-back prefix.
5. Call10 hides keyboard and scrolls (steps13–14). **Earliest directly observed wrong business value:** raw2564 reports `new_servings="3-4 serving size "`, not `3-4 servings`. The supplied input literal was correct, but the mutation's layer is not shown.
6. Call11 focuses servings (step15) then raises `AttributeError: 'WebElement' object has no attribute 'set_value'` (raw2919). This is an unsupported client API choice, not a kernel death or completed replacement. Its planned verification/save never ran.
7. Call12 clears and sends servings again (steps16–17), then a fresh lookup for preparation time fails (`NoSuchElementException`, raw3202). **No readback** validates the repaired servings. Earlier mismatch is therefore not resolved by evidence.
8. Call13 reuses lower handles cached in call9. It performs six clicks/inputs for time, ingredients and directions plus SAVE (steps18–24). It omits the earlier focus checks and all field-value checks. Result `{"actionsSubmitted":7}` (raw3416) is the code's own count, not business verification. This last SAVE succeeds at HTTP200 and exhausts the gate.
9. Read-only call14 (raw3654) shows `.recipe.details.RecipeDetailsActivity`, title and description exact, time2hrs, ingredients`as desired`, full requested directions, and **servings `3-4 serving size of y`**. `Mark as favorite` is consistent with unfavorited UI state, not a DB export.
10. First business final raw3700 accurately reports the saved servings discrepancy. Dedicated cleanup call15 raw3788→3789 returns `quitReturned=true`; cleanup prose raw3808 cannot replace the business submission. Recorded evaluator returns0.0, then teardown clears task state.

##### Action ledger and budget

Allocated24 = `int(10*2.4)`, consumed24, all admitted HTTP statuses200. Breakdown: 11clicks,7inputs,3W3C actions (drawer/form swipes),2hideKeyboard,1clear. There are15Python calls, not15UI steps; advisory30calls is not a hard step limit. No rejected actions, denied commands, timeout or business-deadline exhaustion. Four admitted operations (two hides and two form swipes) were keyboard/layout mitigation beyond initial drawer launch; the duplicate servings click/input/clear work and missing `set_value` API consumed correction capacity. Exact attribution follows; free observations/failed lookups are omitted from this charged ledger but retained in call table.

| Step | Call / raw start→end | Kind | Actual admitted effect |
|---:|---|---|---|
| 1 | 3 / 831→832 | `actions` | Open app drawer |
| 2 | 4 / 1062→1063 | `click` | Open Broccoli |
| 3 | 5 / 1279→1280 | `click` | Open New Recipe |
| 4 | 6 / 1683→1684 | `click` | Focus title |
| 5 | 6 / 1683→1684 | `input` | Enter title |
| 6 | 6 / 1683→1684 | `click` | Focus description |
| 7 | 6 / 1683→1684 | `input` | Enter description |
| 8 | 8 / 1952→1953 | `mobile: hideKeyboard` | Hide keyboard |
| 9 | 8 / 1952→1953 | `actions` | Scroll form |
| 10 | 9 / 2319→2320 | `click` | Focus servings |
| 11 | 9 / 2319→2320 | `input` | Enter 3-4 servings |
| 12 | 9 / 2319→2320 | `click` | Click preparation time; focus check fails |
| 13 | 10 / 2563→2564 | `mobile: hideKeyboard` | Hide keyboard |
| 14 | 10 / 2563→2564 | `actions` | Scroll form |
| 15 | 11 / 2918→2919 | `click` | Focus servings; following set_value is unavailable |
| 16 | 12 / 3201→3202 | `clear` | Clear servings |
| 17 | 12 / 3201→3202 | `input` | Enter 3-4 servings again |
| 18 | 13 / 3415→3416 | `click` | Click cached preparation-time handle |
| 19 | 13 / 3415→3416 | `input` | Enter 2 hrs |
| 20 | 13 / 3415→3416 | `click` | Click cached ingredients handle |
| 21 | 13 / 3415→3416 | `input` | Enter as desired |
| 22 | 13 / 3415→3416 | `click` | Click cached directions handle |
| 23 | 13 / 3415→3416 | `input` | Enter full directions |
| 24 | 13 / 3415→3416 | `click` | SAVE |

| Call | Raw lines | ToolCall prefix | PythonResponse | UI steps |
|---:|---|---|---|---|
| 1 | 406→407 | `call_b38eaa91e2c94f82830ab74c8ca7f7d7` | completed; no error; alive | none |
| 2 | 591→592 | `call_ntnKtkkFxRdPqK2sbpP8p6f4` | completed; no error; alive | none |
| 3 | 831→832 | `call_EKGeqz0gNxDtpNqYp6ylPIOH` | completed; no error; alive | 1 |
| 4 | 1062→1063 | `call_J9nt8Zd8mzsVF3RmeE2fdVYH` | completed; no error; alive | 2 |
| 5 | 1279→1280 | `call_M5gPLL4UIIbSKBDB9xwYt2Ya` | completed; no error; alive | 3 |
| 6 | 1683→1684 | `call_Jmof1XMtptSleJefMP9popjO` | failed; selenium.common.exceptions.NoSuchElementException; alive | 4,5,6,7 |
| 7 | 1797→1798 | `call_RjhBVBO1dskCCg9qqPj0jBc5` | completed; no error; alive | none |
| 8 | 1952→1953 | `call_m5If3DWufMUaFyrBQH1qTSQv` | completed; no error; alive | 8,9 |
| 9 | 2319→2320 | `call_Yy4ZRACasZFOvoqFX1WKlimJ` | failed; RuntimeError; alive | 10,11,12 |
| 10 | 2563→2564 | `call_3syYQmpnxFHEqn2NTdxv1YEa` | completed; no error; alive | 13,14 |
| 11 | 2918→2919 | `call_cImUz1nS9jz6KFO0ZCmNVr8n` | failed; AttributeError; alive | 15 |
| 12 | 3201→3202 | `call_xnJd0fKCXsoNILwB3kFaFduZ` | failed; selenium.common.exceptions.NoSuchElementException; alive | 16,17 |
| 13 | 3415→3416 | `call_XZHd8fqa2g9QQaUJLNx4TNyk` | completed; no error; alive | 18,19,20,21,22,23,24 |
| 14 | 3653→3654 | `call_dPlQkBfA2hogADsk8UMhgViU` | completed; no error; alive | none |
| 15 | 3788→3789 | `call_44j78YvzG98yuL8xg09mGtcL` | completed; no error; alive | none |

##### Final answer, cleanup and score causation

Original first business `rawText` is:

```json
{"taskOutcome":"Recipe saved, but servings is incorrect: displayed as \"3-4 serving size of y\" instead of \"3-4 servings\"."}
```

The immutable archive has `validContract=true`, reason`valid`, string taskOutcome and the same stripped answer. Receipt is event3700, phase`finalization`, received167.91274245805107s; action gate finalization started154.41219520801678s; cleanup requested168.0404818750685s. No type conversion or cleanup precedence explains this result. Business budget was1560s and was not reached.

Actual evaluator stage:1794255169.2410629→1794255169.3760252 Unix; teardown starts1794255169.3760252. Quit result precedes evaluator at1794255165.781. UI proof therefore exists before cleanup and aggregate DB score after cleanup, but **not** an archived persistent row connecting the two.

**Outcome confidence:** confirmed wrong post-save UI field, confirmed reward0/step_budget, unknown exact DB rowset. **Root confidence:** confirmed Agent invariant failure (save without validating repaired content); probable that the displayed servings mismatch caused the DB oracle rejection; unknown origin of phrase transformation. Pure current-source comparison of the actual displayed string gives ratio0.7272727272727273 and false at0.9. This is a sufficient conditional explanation if DB stored that displayed value, not proof that no additional oracle predicate failed.

Do **not** label this an AMKernel mutation/serialization bug: the Python literal and response disagree at the UI boundary, but no IME/input trace identifies the changing layer. IME composition/autocorrection, UiAutomator2 input delivery and app transformation remain alternatives. No persistent data shows which.

##### Mechanism targets and falsification

- **Agent / existing Skill enforcement, proposed:** `.agents/skills/amkernel/references/android-execution.md`, Input/submit and budget sections. Preserve executed-prefix/readback locals; reacquire after layout changes; compare every requested field after final input before SAVE; reserve correction+save permits. Existing frozen guidance already requires focus/readback and acceptance; an additional generic example is reinforcement, not evidence of a missing rule. Falsify sufficiency if a captured field is correct pre-save and only becomes wrong after verified save.
- **Agent client API, proposed:** raw2918 `.set_value` is absent; use only observed supported official-client methods, and ensure replacement clear+input has positive focus and equality readback. Avoid calling a removed method as a one-action workaround. Falsify the diagnosis only with evidence this exact run exposed that method; the captured AttributeError currently rules that out.
- **Environment boundary, decision needed:** obtain existing historical IME/input metadata or an authorized isolated generic text-entry trace before prescribing a keyboard/device change. No blanket autocorrect-disable recommendation and no config change in this diagnosis. A layer-specific trace is the discriminator.

<a id="case-052"></a>

#### Case 052

##### Request and exact oracle

Visible goal: “Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains.”

`RecipeDeleteDuplicateRecipes3` (`recipe.py:272-315`) sets complexity3.4, noise30 and inserts two identical targets. It starts with22 random non-Avocado rows, removes one as target, adds3Avocado noise rows, and adds same-title/same-description target variants until30noise rows. The variants are not necessarily exact duplicates. Actual archived params, rather than generator possibilities, determine this case.

Exact duplicate **initialization** predicate is equality across every Recipe dataclass field except `recipeId`: `title, description, servings, preparationTime, source, ingredients, directions, favorite, imageName` (`sqlite_schema_utils.py:197-214`; `DeleteDuplicateRows._validate_candidates:383-398`). Equality of title and description alone does not meet it.

Exact **score** is the OR of two removal-integrity checks (`RecipeDeleteDuplicateRecipes.validate_deletion_integrity:200-211`): remove target1's actual captured ID while every other before row remains exactly unchanged, **or** remove target2's ID with that same preservation rule. Every remaining after row must have existed before; no changed/new row is allowed (`sqlite_validators.validate_rows_removal_integrity:73-115`). Binary1/0, no subscores. With32initial rows this requires31after rows and one target copy retained. It does not merely check that same-title counts fell.

##### Actual initialized collection, not guessed duplicate answers

Offline exact-field grouping of the **archived params** gives32occurrences,31full-content groups, and exactly one duplicate group: zero-based concatenated occurrence indices`[30,31]` (the two `row_objects`, not actual DB IDs). The10Butternut occurrences are`[0,12,24,25,26,27,28,29,30,31]`; only30/31are equal. All32rows and original per-origin params references are in JSON. Distinct content must survive, even when title/description match.

All10Butternut rows have title **Butternut Squash Soup** and description **A quick and easy meal, perfect for busy weekdays.**, favorite0, empty source/imageName, and the same base directions “Sauté onions and garlic, add cubed butternut squash and broth. Puree until smooth and season with nutmeg, salt, and pepper.” They differ as follows. Directions suffixes: **T**=`Try adding a pinch of your favorite spices for extra flavor.`; **G**=`Garnish with fresh herbs for a more vibrant taste.`; **F**=`Feel free to substitute with ingredients you have on hand.`

| Param occurrence | Servings | Time | Ingredients | Directions suffix |
|---:|---|---|---|---|
|0|6 servings|4 hrs|as desired|T|
|12|3-4 servings|1 hrs|subject to change|G|
|24|8 servings|4 hrs|varies|F|
|25|2 servings|45 mins|subject to change|F|
|26|8 servings|2 hrs|to your liking|G|
|27|8 servings|45 mins|flexible ingredients|T|
|28|3-4 servings|1 hrs|varies|F|
|29|1 serving|1 hrs|quantities to taste|F|
|30 target|3-4 servings|30 mins|quantities to taste|G|
|31 target|3-4 servings|30 mins|quantities to taste|G|

Other same-title populations are Avocado3, BBQ Chicken Quesadillas2, Grilled Cheese with Tomato and Basil2, Pan-Seared Salmon with Quinoa2; all are unique by full content. The other13titles have one occurrence each. Params prove the intended initialized population, while task initialization completed and UI scans corroborate its shape; lack of DB export means no claim that param index maps to a particular primary key.

##### Raw UI identities, coverage and first deviation

1. Calls3–4 open drawer/Broccoli (steps1–2). Call6 records7bounded list windows using6scrollGesture actions (steps3–8) and returned `canScrollMore=false` (raw1863). It reaches the bottom, but windows overlap and have only title/summary/source/bounds; repeated equal summaries lack stable row IDs. The full window facts are in JSON. They nominate many Butternut candidates but cannot reconstruct an exact occurrence count or pair from titles alone.
2. Search opens (step9), full Butternut title entered (step10). Call8 returns only a repr of a2-element nested tuple list (raw2578), **not two total recipes**. Agent reasoning raw2897 explicitly says keyboard leaves only two visible and total may be10.
3. **Earliest execution divergence:** call9 raw2898→2899 tries the first title's `../..` parent, fails before click, and consumes no action. Read-only call10 raw3147 shows3currently visible CardViews: clipped first `[21,422][1059,609]` with description only, second `[21,630][1059,945]`, third `[21,966][1059,1281]`. They are viewport occurrences, not the full filtered collection.
4. Call11 opens visible `cards[1]` (step11). Raw3352 shows a Butternut detail with3-4servings,30mins,`quantities to taste`, Gdirections, matching content of initialized target30/31. **One target-content instance is now observed; which copy/ID is unknown.**
5. Call12 captures its seven-field `detail_signature`, navigates up (step12), opens visible `cards[2]` (step13), captures a second signature. Raw3745 collapses the dict containing tuple lists to repr, losing comparison data at that response boundary. Read-only calls13–14 recover exact inequality: first3-4servings/30mins/G versus second1serving/1hrs/F (raw3824,3909). Second matches unique noise29. Neither equality nor duplicate deletion is authorized. `detail_signature` also omits source, favorite, imageName and any offscreen detail, so equality of that partial signature would still need a completeness boundary.
6. Call15 opens More options (step14). Its tuple-list response is repr (raw4879); call16 recovers menu labels Edit/Delete (raw5063). **Seeing Delete is not clicking Delete.** No destructive operation follows.
7. Call17 dismisses menu and navigates to search (steps15–16), then `.set_value` raises AttributeError. Call18 clears/enters Gsuffix text (steps17–18), observes no cards. These actions do not identify the missing Butternut counterpart. Underlying search fields/index semantics are not captured.
8. The agent leaves the unresolved Butternut group. Call19 spends5actions (steps19–23) comparing Avocado visible cards0/2; readback proves unequal servings6vs3-4, time4hrsvs1hrs, ingredients`various amounts`vs`n/a`. These correspond to unique noise21/23, not duplicates.
9. Call20 navigates/clears/types full `Pan-Seared Salmon with Quinoa` (steps24–26), then its explicit wait times out. Call21 shows correct query but zero cards, not lost session. Call22 clears/types `Pan` (steps27–28), now sees two candidates. This establishes query-specific behavior, **not** a proven punctuation/root cause.
10. Call23 compares Pan cards0/1 (steps29–31), returns unequal servings6vs1, ingredients`n/a`vs`varies`, TsuffixvsFsuffix. Those match unique noise7/13. No deletion is correct for this pair.
11. Call24 returns to search and clears/types `Butternut` (steps32–34), ending with3currently visible cards (raw7319). It does not enumerate10candidates, bind the true counterpart, click Delete, or confirm deletion. The last input exhausts the34action gate. Honest first business final says no recipes deleted. Quit-only cleanup succeeds.

**Strategy deviation versus safety:** preserving unequal/uncertain candidates was correct. The failure is not an unsafe deletion based on names; it is failing to complete an occurrence-aware comparison/deletion path. After a target-content instance was found, remaining actions migrated to unrelated groups/search recovery without retaining a fully addressable Butternut counterpart or commit reserve. This is a probable strategy cause, not proof of a generally feasible34-operation solution. No claim that positional guessing would have been a legitimate fix.

##### Action ledger and budget

34=`int(10*3.4)` permits, consumed34, all forwarded statuses200, rejected0/denied0. Breakdown:15clicks,6scrollGesture,6input,5clear,1back,1W3C drawer gesture.25Python calls, advisory30. No business deadline reached (2160s available).

Charged phases: launch2; initial list scan6; Butternut title search+first two details5 (steps9–13); menu exploration/dismiss/navigation3; directions search2; Avocado search/detail comparison5; failed full-Pan query3; shorter-Pan recovery2; Pan comparison3; return-to-Butternut search3. Sum34. Zero charged operations are Delete or deletion confirmation. API/locator exceptions before an action cost no permit; executed prefixes retain their charges.

| Step | Call / raw start→end | Kind | Actual admitted effect |
|---:|---|---|---|
| 1 | 3 / 948→949 | `actions` | Open app drawer |
| 2 | 4 / 1144→1145 | `click` | Open Broccoli |
| 3 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 1 |
| 4 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 2 |
| 5 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 3 |
| 6 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 4 |
| 7 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 5 |
| 8 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 6 |
| 9 | 7 / 2451→2452 | `click` | Open Search |
| 10 | 8 / 2577→2578 | `input` | Enter Butternut Squash Soup |
| 11 | 11 / 3351→3352 | `click` | Open filtered visible cards[1] |
| 12 | 12 / 3744→3745 | `click` | Navigate up |
| 13 | 12 / 3744→3745 | `click` | Open filtered visible cards[2] |
| 14 | 15 / 4878→4879 | `click` | Open More options |
| 15 | 17 / 5277→5278 | `back` | Back dismisses menu |
| 16 | 17 / 5277→5278 | `click` | Navigate up |
| 17 | 18 / 5437→5438 | `clear` | Clear search |
| 18 | 18 / 5437→5438 | `input` | Enter Garnish with fresh herbs |
| 19 | 19 / 5804→5805 | `clear` | Clear search |
| 20 | 19 / 5804→5805 | `input` | Enter Avocado Toast with Egg |
| 21 | 19 / 5804→5805 | `click` | Open avocado cards[0] |
| 22 | 19 / 5804→5805 | `click` | Navigate up |
| 23 | 19 / 5804→5805 | `click` | Open avocado cards[2] |
| 24 | 20 / 6276→6277 | `click` | Navigate up |
| 25 | 20 / 6276→6277 | `clear` | Clear search |
| 26 | 20 / 6276→6277 | `input` | Enter Pan-Seared Salmon with Quinoa |
| 27 | 22 / 6678→6679 | `clear` | Clear search |
| 28 | 22 / 6678→6679 | `input` | Enter Pan |
| 29 | 23 / 6960→6961 | `click` | Open Pan cards[0] |
| 30 | 23 / 6960→6961 | `click` | Navigate up |
| 31 | 23 / 6960→6961 | `click` | Open Pan cards[1] |
| 32 | 24 / 7316→7319 | `click` | Navigate up |
| 33 | 24 / 7316→7319 | `clear` | Clear search |
| 34 | 24 / 7316→7319 | `input` | Enter Butternut |

| Call | Raw lines | ToolCall prefix | PythonResponse | UI steps |
|---:|---|---|---|---|
| 1 | 424→425 | `call_lptsFXe2wMafe7iPQ3QEVYOg` | completed; no error; alive | none |
| 2 | 684→685 | `call_mNySStgvwVDpakQxmh8A6qeX` | completed; no error; alive | none |
| 3 | 948→949 | `call_mKQsem7LQXhFVZeYt6q0jN7k` | completed; no error; alive | 1 |
| 4 | 1144→1145 | `call_f2cd2765a48d436e8f3fd052286a949b` | completed; no error; alive | 2 |
| 5 | 1531→1532 | `call_y22CB6ZV1IyAs9uL13A5FT8f` | completed; no error; alive | none |
| 6 | 1862→1863 | `call_iuq2CafKXWeI02UBPVhiTLLh` | completed; no error; alive | 3,4,5,6,7,8 |
| 7 | 2451→2452 | `call_z5e8Fl5r2L7pC4nGbP8b9qjc` | completed; no error; alive | 9 |
| 8 | 2577→2578 | `call_IEOi6eZN00YSLdHoFfhiaPR4` | completed; no error; alive | 10 |
| 9 | 2898→2899 | `call_LMaB3aGXwqShCZMZSIvAT1Wh` | failed; selenium.common.exceptions.NoSuchElementException; alive | none |
| 10 | 3146→3147 | `call_hUsGKG9RZR7aOFJUrPMmUZmF` | completed; no error; alive | none |
| 11 | 3351→3352 | `call_xnAizmYTpbhg75eJ24IEuAtu` | completed; no error; alive | 11 |
| 12 | 3744→3745 | `call_YTGriLGANTuOZALe2X3avfU3` | completed; no error; alive | 12,13 |
| 13 | 3823→3824 | `call_q8X9NNnIS6gPzC2lfZC98hxU` | completed; no error; alive | none |
| 14 | 3908→3909 | `call_tfyXBBPRsyVL7D8imSXyPGBU` | completed; no error; alive | none |
| 15 | 4878→4879 | `call_7IYSBXLbneSVEP9PQURSAdum` | completed; no error; alive | 14 |
| 16 | 5062→5063 | `call_ewI9RLWHr1NHC94y0A9UAXQT` | completed; no error; alive | none |
| 17 | 5277→5278 | `call_R0yYD6gJd3mDDmP50Ndz9Jpi` | failed; AttributeError; alive | 15,16 |
| 18 | 5437→5438 | `call_38hzfS78D1KgkD60zfNwpbL6` | completed; no error; alive | 17,18 |
| 19 | 5804→5805 | `call_vQH3vxMAywlmQDoXc3Q0Fp4X` | completed; no error; alive | 19,20,21,22,23 |
| 20 | 6276→6277 | `call_6mMVPgoMpyKfcyIc395GZqga` | failed; selenium.common.exceptions.TimeoutException; alive | 24,25,26 |
| 21 | 6410→6411 | `call_XcedW4FQ7FfQBVs40uzybOTV` | completed; no error; alive | none |
| 22 | 6678→6679 | `call_HkcAqAhqVwVSDul1MBbu9O5c` | completed; no error; alive | 27,28 |
| 23 | 6960→6961 | `call_AqGMuEIzLYMgDnLTiVwizqfz` | completed; no error; alive | 29,30,31 |
| 24 | 7316→7319 | `call_WRmX0rgt0Q9zqRlb24TP74C2` | completed; no error; alive | 32,33,34 |
| 25 | 7423→7424 | `call_VWSF8b0DuVCq4WoIrQR7Rg4L` | completed; no error; alive | none |

##### Submission, surviving recipes and confidence

Original first business rawText:

```json
{"taskOutcome":"Unable to complete: no recipes were deleted before the UI action budget was exhausted."}
```

Valid parsed nonempty string, receipt event7353, phase`finalization`, received317.76614945789333s; finalization started312.4733818329405s; cleanup requested318.16660199989565s. Raw7326 is the exhaustion control; raw7363 separate cleanup control; raw7424 quit success; raw7436 cleanup-only final is ignored for business answer.

Evaluator1794255980.097749→1794255980.240979 Unix follows quit result1794255970.214, precedes task teardown1794255980.240979. Reward0.0 is expected if the initial pair remained; no persistent snapshot independently confirms all32surviving rows. **Proven:** no Delete/confirmation call in the complete action ledger, no claimed deletion, last main-view search still shows3visible Butternut cards, and reward0. **Strong inference, not DB proof:** all initialized recipes including both target copies survived because only inspection/navigation/search occurred. **Unknown:** exact final row IDs/contents and any cleanup-time persistence effect. Three visible cards do not mean only three survived.

Outcome confidence is confirmed for no attempted UI deletion and aggregate failure; persistent final collection unknown. Root confidence is probable for incomplete occurrence tracking and budget allocation. No observed transport/kernel failure supports Runtime blame; all25responses are alive. Nested tuple repr loss in calls8/12/15 is a real observation limitation and cost recovery calls, but does not by itself establish the cause of the wrong task outcome or a serializer defect.

##### Concrete mechanism targets and offline discriminators

- **Agent / existing Skill, proposed:** `amkernel-appium.md` coverage, content-equivalence and budget sections. Maintain a temporary occurrence-aware candidate ledger; distinguish overlapping windows from distinct equal-content objects; complete a promising group before changing groups; reserve actual menu/confirmation/retention actions. Never infer duplicates from titles or appended DB position. Existing frozen Skill already states these invariants; reinforcement requires decision, not an assertion that the Skill caused failure.
- **Agent output payload, proposed:** raw3744 `detail_signature` returns tuples. Use JSON-native string dictionaries/lists plus explicit completeness/occurrence evidence; do not rely on partial signatures or `zip` differences as full equivalence proof. A JSON-native scalar follow-up recovered the inequality here, so no wrong deletion resulted from omitted values.
- **Runtime serialization interface, decision needed:** raw2578/3745/4879 return bounded repr instead of the nested primitive facts. A separately owned pure serializer probe can distinguish intentional unsupported tuple behavior from a preserveable result-shape defect. Mechanism owner must identify the exact serializer symbol; no coordinated fix is approved in this report. Boundedness and safe object handling must remain invariant.
- **Harness comparability, decision needed:** official allocator is complexity×10, but proxy charges each clear/input/focus/navigation interaction separately. Reaching34with no deletion is observed; universal infeasibility is not. Any future authorized feasibility study must preserve this attempt/reward and show a legal occurrence/equivalence/deletion/retention route, not raise the frozen budget or give the Agent initialization answers.
- **Search environment boundary, unknown:** full Pan title returned0, `Pan` returned2. Existing logs cannot discriminate tokenizer/query syntax/index state. An offline source/APK inspection or authorized separate query study is the discriminator; do not install a speculative search fix from this trace.

#### Reproducible offline checks

The following exact read-only query combines the pure checks exercised during this investigation. It does not import AndroidWorld modules, evaluate a formal task or contact a device. The displayed malformed servings string is copied from raw3654, not assumed from the submission. IDs in the equivalence result are occurrence positions in params, not persistent recipeIds.

```python
import ast, collections, difflib, json, pathlib
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
r49 = json.loads((C / "episodes/049-RecipeAddSingleRecipe/attempt-1/result.json").read_text())
r52 = json.loads((C / "episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/result.json").read_text())
# Pure source extraction; imports only stdlib difflib, no AndroidWorld imports/device effects.
p = pathlib.Path("android_world/android_world/utils/fuzzy_match_lib.py")
tree = ast.parse(p.read_text())
selected = ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef))], type_ignores=[])
ns = {}
exec(compile(ast.fix_missing_locations(selected), "<offline-fuzzy-source>", "exec"), ns)
expected, observed = r49["task"]["params"]["row_objects"][0]["servings"], "3-4 serving size of y"
print({"expected": expected, "observed": observed, "ratio": difflib.SequenceMatcher(None, expected.lower(), observed.lower()).ratio(), "threshold": ns["_MIN_DIFF_SIMILARITY"], "oracleFuzzyMatch": ns["fuzzy_match"](expected, observed)})
p = r52["task"]["params"]
rows = p["noise_row_objects"] + p["row_objects"]
groups = collections.defaultdict(list)
for i, row in enumerate(rows):
    groups[tuple(sorted((k, v) for k, v in row.items() if k != "recipeId"))].append(i)
print({"initializedRowsFromParams": len(rows), "uniqueFullContentGroups": len(groups), "duplicateOccurrenceIndices": [v for v in groups.values() if len(v) > 1], "butternutOccurrences": [i for i, row in enumerate(rows) if row["title"] == "Butternut Squash Soup"], "titleCounts": dict(collections.Counter(row["title"] for row in rows))})
# For addition, only noise rows are inserted initially, not target rows.
print({"case49InitialNoiseRows": len(r49["task"]["params"]["noise_row_objects"]), "case49RequestedNewRows": len(r49["task"]["params"]["row_objects"])})
```

Actual outputs:

```json
{"expected": "3-4 servings", "observed": "3-4 serving size of y", "ratio": 0.7272727272727273, "threshold": 0.9, "oracleFuzzyMatch": false}
{"initializedRowsFromParams": 32, "uniqueFullContentGroups": 31, "duplicateOccurrenceIndices": [[30, 31]], "butternutOccurrences": [0, 12, 24, 25, 26, 27, 28, 29, 30, 31], "titleCounts": {"Butternut Squash Soup": 10, "Raspberry Almond Smoothie": 1, "Beef Stir Fry": 1, "BBQ Chicken Quesadillas": 2, "Grilled Cheese with Tomato and Basil": 2, "Salmon with Dill Sauce": 1, "Stuffed Bell Peppers": 1, "Pan-Seared Salmon with Quinoa": 2, "Lentil Soup": 1, "Chicken Alfredo Pasta": 1, "Quick Fried Rice": 1, "Garlic Butter Shrimp": 1, "Mango Chicken Curry": 1, "Sweet Potato and Black Bean Tacos": 1, "Pesto Pasta with Peas": 1, "Lemon Garlic Tilapia": 1, "Veggie and Hummus Sandwich": 1, "Avocado Toast with Egg": 3}}
{"case49InitialNoiseRows": 10, "case49RequestedNewRows": 1}
```

Limitations: the fuzzy false result is conditional on DB containing the captured UI value; grouping proves initialized input equivalence, not post-agent persistence. No final DB/subscore was fabricated. No tests/build/lint were run. All proposed changes are separate from causes and remain unimplemented; only these diagnosis artifacts were created.

## 领域：retro

原领域报告：[domain-retro.md](domain-retro.md)；结构化取证：[domain-retro.json](domain-retro.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Retro Music failure analysis — current r15 campaign

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope: cases **058 RetroCreatePlaylist** and **060 RetroPlaylistDuration**, attempt1 only. Structured record: [domain-retro.json](domain-retro.json). Exact offline query code/output and limitations: [domain-retro-queries.md](domain-retro-queries.md). Original evidence remains immutable; no product/config/test changes, device/ADB/Appium/MCP execution, task replay, score rerun, suite, or package installation.

#### Findings and confidence

| Case | Proven business outcome | Root diagnosis | Confidence / layer |
|---|---|---|---|
|058|Reopened named playlist has **one song, Dreamer's Awake**, not the requested three ordered songs; official reward0.|Broad containing-ancestor XPath can repeatedly select the first song's menu; per-add membership never checked. Actual clicked IDs absent.|Outcome confirmed; root **probable Agent locator/code-generation failure**.|
|060|Playlist displays **14 Songs •01:08:25**, not45–50min; action budget closes before removal is committed; official reward0.0.|Unmeasured Select all bulk addition, followed by unmeasured correction selection without a commit budget.|Outcome and **Agent aggregate-planning behavior confirmed**. Exact metadata/DB cause unknown.|

**Important task identity correction:** despite the name, **RetroPlaylistDuration is a mutation task**, not a duration question or InformationRetrieval task. The visible original prompt says “Create a playlist…with a duration between45 and50minutes.” Both classes are directly registered in `android_world/android_world/registry.py:175–178`. Information-retrieval registration contains neither class. The official evaluator does not compare the business answer with a numerical duration. Adding answer-normalization fixes would solve the wrong problem.

A separate **current-source oracle initialization omission** is confirmed: `RetroPlaylistDuration.initialize_task` skips its base initializer and internal-storage clearing. This is a reproducibility/isolation risk, **not demonstrated to cause the observed bulk-add failure**. It prevents deriving actual song durations from the declared seed. No historical r12 case is used.

#### Evidence conventions and provenance

`R58` = `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/result.json`; `L58` = the same attempt's `raw-private/agent-events.jsonl`; `R60/L60` likewise for060. Raw physical JSONL line numbers also identify receipt event sequence for the first finals. Each JSON timeline entry includes full original toolCall ID, start/end raw lines, execution count, code/excerpt, and structured response facts. The readable table below uses execution counts plus physical lines; it does not pretend the sanitized action ledger retained locators.

Actual responses are parsed from **tool_execution_end**, never inferred from code that intended to run or from outer isError alone. All25/31 Python responses have `kernelState=alive`. Three failed cells in each case are recorded, not treated as Runtime death.

Shared-offline-checks保留原goal/参考时钟/合法string/首final/parser和Harness身份的已完成证据。独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。 Retro初始化时的实际MP3随机metadata和存储状态仍未归档。

#### Shared official oracle and lifecycle boundary

`retro_music.py:41–76` pulls `/data/data/code.name.monkey.retromusic/databases/playlist.db` and joins `PlaylistEntity pe` with `SongEntity se` on `pe.playlist_id=se.playlist_creator_id`. It projects playlist name, `se.title`, `se.duration` (duration_ms), and computes:

```sql
ROW_NUMBER() OVER (
  PARTITION BY pe.playlist_name ORDER BY se.song_key
) - 1 AS order_in_playlist
```

This is persisted SQLite evidence used by the evaluator, not merely the currently displayed UI order. Empty playlists contribute no rows because of INNER JOIN. **No pulled DB or evaluator row projection was archived for these attempts**, so reward0 is proof only that the official predicate returned false, not a reconstruction of actual rows/order/durations.

`runner.py:716–737` completes the agent and owned-session cleanup before `agent_protocol:745` and evaluator invocation `790–796`. Task teardown follows evaluation. The cleanup cells here contain only retained session ID + `driver.quit()` + exact successful cleanup return; they do not remove/rename/edit playlist contents. There is no captured post-quit app/DB observation, so absolute persistence invariance is unknown. Nevertheless, both business failures were visibly present **before quit**, not discovered only after cleanup. No evidence makes cleanup the primary cause.

<a id="case-058"></a>

#### Case058 — RetroCreatePlaylist

##### Goal, initialization and exact acceptance

Original prompt `L58:9`:

> Create a playlist in Retro Music titled "Hip Hop Bangers 270" with the following songs, in order: Golden Days, Dreamer's Awake, Hidden Paths

Params: name `Hip Hop Bangers 270`; target files in order `Golden Days.mp3`, `Dreamer's Awake.mp3`, `Hidden Paths.mp3`; seed916405052. Twelve noise names are retained in JSON and R58.task.params.

`retro_music.py:147–160` calls base initialization (time/apps/cache, seed), clears internal storage and playlist tables, writes all15 MP3s with title=file stem, randomized artists and requested durations180000–300000ms, scans music and closes app. Source-requested duration is immaterial to this acceptance criterion and is not actual encoded metadata proof.

`RetroCreatePlaylist.is_successful:162–170` calls `sqlite_validators.verify_playlist:30–70`:

1. Count all rows whose playlist name fuzzy-matches the requested name, ignoring case. Count must be **exactly3**.
2. For each expected zero-based index, find a matching-name row with **exact title equality** and query-computed `order_in_playlist==index`.
3. Return integer0/1; no partial name/order/membership subscores.

The fuzzy-name helper (`utils/fuzzy_match_lib.py:20–50`) lowercases strings and requires `difflib.SequenceMatcher(...).ratio()>=0.9`. This tolerates approximate playlist names, not approximate song titles. Other dissimilar playlist names do not automatically fail058. Exact requested accepted tuple is `(Golden Days,0), (Dreamer's Awake,1), (Hidden Paths,2)` within the matching playlist rows. Playlist creation alone is insufficient; export is not requested.

##### Captured actions and narrowing causal chain

- Exec1 creates one UiAutomator2 session, returns completed/alive; exec2–7 navigate launcher and open observed Retro Music. Exec3 returns a **bounded repr instead of the intended facts**, which limits that particular observation but does not prevent later semantic launch. No generalized Runtime defect is assigned here.
- Exec8 (`L58:2134–2135`) sees no playlists. Exec9–11 create the exact name; exec11 response shows **0Songs •00:00**.
- Exec12 (`3334–3335`) sees Songs in this order: Dreamer's Awake first, Golden Days fifth, Hidden Paths seventh. All required targets exist in returned visible facts. Their bounds differ: Dreamer title `[163,326][951,383]`, Golden `[163,1038][951,1095]`, Hidden `[163,1394][951,1451]`.
- Exec13 (`3656–3657`) parent-inspection loop fails with NoSuchElementException on cell line4. Kernel survives. Exec14–15 query bounded XML snippets. Exec15 shows Golden title, artist Hana and menu **within the same closing android.view.ViewGroup**, menu bounds`[951,1034][1077,1160]`. This evidence was sufficient to distinguish row scope from arbitrary containing-screen scope.
- Exec16 (`4284–4285`, `call_izuPucEfeCh4OFZsQDtWAuSM`) submits:

```python
menu = driver.find_element(AppiumBy.XPATH,
    "//android.view.ViewGroup[.//*[@text='Golden Days']]"
    "//*[@resource-id='code.name.monkey.retromusic:id/menu']")
menu.click()
```

  Exec17 selects Add to playlist; exec18 chooses the named playlist. The only postcondition returned is12 song menus and Golden still visible; this does **not** prove which song was added.
- Exec19 (`5021–5022`, `call_CtlyaFbOoRh4tCnoGRwVWBEt`) repeats the same broad selector shape for Dreamer's Awake, then Add to playlist and picker confirmation. Exec20 (`5299–5300`, `call_KwM3kNmp7aqZ4HTl7txn5vfK`) repeats it for Hidden Paths. Both return `songMenus:12`, not playlist membership.
- Exec21 (`5653–5654`) is a SyntaxError from apostrophe quoting in the final verification expression; **nothing in the cell runs**. The pure compiler probe confirms this and exact cell line6. Exec22 (`5987–5988`) is the corrected cell: Playlists click and named row click execute, then the all-three-title wait times out. These are the two accepted actions in the ledger, not the failed compilation's intended actions.
- Exec23 (`6249–6250`) independently reads reopened playlist **Hip Hop Bangers270 /1Song •03:50 /Dreamer's Awake /Olivia**. Count1 + sole visible song supports a complete one-item UI collection. It does not expose SongEntity order keys or post-quit database contents.
- Exec24 (`6590–6591`) opens playlist-wide overflow: Play, Play next, Add to playing queue, Add to playlist, Rename, Delete, Save as file. This is not a membership repair. First business final at`6630` honestly reports incomplete. Exec25 (`6703–6704`) quits successfully; cleanup final at`6723` cannot overwrite business answer.

##### Cause and responsibility, not merely terminal label

**Confirmed symptom:** requested membership and order are not present in the reopened UI. **Probable root:** row locator aliasing. The predicate matches every ViewGroup that contains the target somewhere below it. A broad containing view can also contain all song menus, so “first matching menu” can be the first visible Dreamer's Awake regardless of target. Repeating an add to that same song is consistent with final count1; app duplicate suppression is plausible, not directly proven.

The exact clicked menu element IDs are absent. Full historical DOM is not retained. The synthetic standard-library counterexample in queries Q3 shows the structural nonuniqueness, **not Appium replay or certainty about the historical result**. If correctly scoped distinct clicked IDs were later recovered, an app-side add/dedup/DB issue would need consideration. Current evidence makes Agent scoping failure stronger than Runtime or oracle failure.

Action exhaustion is excluded: only23/24 interactions were accepted; closure is`agent_finished`. The reference loop reports24steps because its control/final step is not the same measure as actual Appium interactions. All25 structured Python responses are alive (22completed,3failed). Python-call advisory30 and1560s business deadline did not cause termination.

##### Actual accepted-action ledger

Every row below has status200 in R58.stepBudget.actions. Target labels are from submitted code; the ledger itself retains kind/path/status only. Full tool IDs are in JSON.

| Step | Kind | Intended action from code | Exec / raw lines |
|---:|---|---|---|
| 1 | actions | Swipe launcher app drawer | 3 / 910–911 |
| 2 | click | Focus launcher search input | 6 / 1576–1577 |
| 3 | input | Enter Retro Music | 6 / 1576–1577 |
| 4 | click | Open Retro Music icon | 7 / 1830–1831 |
| 5 | click | Open Playlists | 8 / 2134–2135 |
| 6 | click | Open playlist overflow | 9 / 2345–2346 |
| 7 | click | New playlist | 10 / 2571–2572 |
| 8 | click | Focus playlist name | 11 / 2999–3000 |
| 9 | input | Enter Hip Hop Bangers 270 | 11 / 2999–3000 |
| 10 | click | Create playlist | 11 / 2999–3000 |
| 11 | click | Open Songs | 12 / 3334–3335 |
| 12 | click | Open menu nominally for Golden Days; broad ancestor XPath | 16 / 4284–4285 |
| 13 | click | Add to playlist | 17 / 4461–4462 |
| 14 | click | Choose Hip Hop Bangers 270 | 18 / 4734–4735 |
| 15 | click | Open menu nominally for Dreamer's Awake; same broad ancestor shape | 19 / 5021–5022 |
| 16 | click | Add to playlist | 19 / 5021–5022 |
| 17 | click | Choose Hip Hop Bangers 270 | 19 / 5021–5022 |
| 18 | click | Open menu nominally for Hidden Paths; broad ancestor XPath | 20 / 5299–5300 |
| 19 | click | Add to playlist | 20 / 5299–5300 |
| 20 | click | Choose Hip Hop Bangers 270 | 20 / 5299–5300 |
| 21 | click | Open Playlists | 22 / 5987–5988 |
| 22 | click | Open Hip Hop Bangers 270 | 22 / 5987–5988 |
| 23 | click | Open playlist overflow; not a repair | 24 / 6590–6591 |

##### Proposed fixes and falsification

1. **Agent locator correction (proposed):** bind the observed title to its nearest actual song-row container; require exactly one menu inside that row and disambiguate using observed same-row attributes/bounds. Do not select all arbitrary ancestors or replace the problem with guessed global indices. Preserve apostrophe-safe locator construction.
2. **Agent acceptance plan (proposed):** distinguish picker closure from membership. A bounded first-add readback can detect aliasing before three repetitions; final acceptance must compare exact count3 and ordered titles. Reserve correction budget rather than spend the last useful action opening unrelated playlist overflow.
3. Existing captured Skill already says a successful find is only a candidate, keep repeated-item fields together (`android-execution.md`, captured raw60 event55 content90–115), and derive/persistently compare identity/content/order (`amkernel-appium.md`, event54 content182–188). A concrete nearest-container example is an optional proposed refinement, **not proof missing policy caused the failure**, and no change was implemented/approved.

Falsification: distinct correct row/menu identities followed by continued one-song state would shift investigation to app-side insertion/dedup/persistence. Correct pre-quit ordered DB rows followed by score0 would shift toward cleanup or oracle translation. Neither evidence exists in the archive.

<a id="case-060"></a>

#### Case060 — RetroPlaylistDuration

##### Goal and official predicate: no answer-normalization scoring

Original prompt `L60:9`:

> Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.

Name `Reggae Rhythms51`, seed217200551. The10 source target files and5 noise files appear in the corpus table below. The visible prompt never exposes hidden target partition membership; source params are diagnostic evidence, not an execution route the agent was entitled to use.

`RetroPlaylistDuration.is_successful` (`retro_music.py:286–293`) reads the same joined rows, requires **every joined row's playlist name exactly equals** requested name (a row from another nonempty playlist immediately fails), sums raw`duration_ms`, and returns:

```python
float(45 * 60 * 1000 <= total_ms <= 50 * 60 * 1000)
# inclusive [2_700_000, 3_000_000] milliseconds
```

There is no order predicate, no exact title-set predicate, and no partial credit. Unlike058, name equality here is exact, not fuzzy. An empty playlist contributes zero and fails the lower bound. Hidden “noise” songs are not forbidden by the oracle if an actual chosen set meets duration and name conditions.

Registration and dispatch prove no official numeric answer comparison: both classes are single task classes, not`InformationRetrieval`; runner787–788 assigns stripped answer to`interaction_cache` **only** for that IR type. Official IR comparison (`information_retrieval.py:109–119`) is therefore inapplicable. The business envelope was valid, but its text does not create playlist state or change the reward.

##### Initialization: intended metadata is not observed app duration

Current source260–284 clears playlist tables and constructs a nonnegative integer partition of**2,850,000ms=47.5min** across the10target files. The helper236–243 draws/sorts random cuts and allows zero-length parts. Noise requests each lie180000–300000ms. `user_data_generation.py:307–355` makes silent audio and exports MP3, then copies it; the scanner/app may expose encoded metadata, not necessarily the exact requested silence lengths. Neither generated MP3s nor actual scan metadata were archived.

The duration override does **not** call`super().initialize_task`, `TaskEval.initialize_task`, `clear_internal_storage`, or`random.seed`. It therefore bypasses normal TaskEval clock/app snapshot/cache/reset/initialized guard and seed initialization (`task_eval.py:142–157`), and unlike058 does not clear music storage. Campaign manifest says`paramsTransport:json`; runner `_task:471–484` does not seed when explicit params JSON is supplied. This is why a local replay of random seed217200551 would not recover the actual initialized duration set. Source provenance does not prove a specific missing file or stale item; this is a confirmed code-path omission and independent comparability risk.

##### Complete-collection boundary and known data

**We cannot rebuild a complete actual14-song/duration collection from this archive.** That is a material missing-evidence result, not a license to invent benchmark answers.

Exec18 (`L60:5213–5214`) returns exactly12 visible titles. Exec22 (`6659–6660`) says14selected. No bottom scroll or full-corpus return exists. All5 declared noise titles are among those12. None of the31 Python responses contains a per-song duration detail; the first nonzero duration evidence is the final playlist aggregate. The exact14 members and all individual duration_ms values remain unknown.

| Source-declared song | Role | Seen among visible 12? | Actual duration |
|---|---|---|---|
| Silent Dreams | target partition member | yes | unknown |
| Hidden Paths | target partition member | yes | unknown |
| Whispering Wind | target partition member | not captured | unknown |
| Return to Paradise | target partition member | yes | unknown |
| Endless Summer | target partition member | not captured | unknown |
| Falling Feathers | target partition member | yes | unknown |
| Heartbeat Away | target partition member | yes | unknown |
| Orbiting Stars | target partition member | yes | unknown |
| Through the Storm | target partition member | not captured | unknown |
| Forever Young | target partition member | yes | unknown |
| Golden Days | noise | yes | unknown |
| Beyond the Horizon | noise | yes | unknown |
| Moonlight Sonata | noise | yes | unknown |
| City of Stars | noise | yes | unknown |
| Eternal Flame | noise | yes | unknown |

Declared15 minus visible12 = **Endless Summer, Through the Storm, Whispering Wind**. Under an additional no-contamination assumption only, exactly2of these3would complete14; the archive does not prove which. An apparent zero-length file/scan omission is a hypothesis, not a finding. Do not infer missing Endless Summer solely from title order without proving sort coverage, actual initialized corpus and boundaries. Duration initializer's storage omission means even the no-contamination assumption is not guaranteed.

##### Captured behavior and why the failure is not rounding

- Exec2 (`699–700`) attempts lxml import, fails ModuleNotFoundError; exec3 uses standard-library ElementTree successfully. This was an optional agent import assumption, not a required amkernel dependency failure. No UI action consumed.
- Exec8 sees visible song titles and artists, not durations. Exec9 explores Songs overflow. Exec10–14 creates correct named empty playlist. Exec15 opens it, then times out because its wait incorrectly expects “not0Songs” after merely opening an empty playlist. Exec16 proves the session/UI survives and the playlist is still0Songs. Exec17 explores playlist overflow; exec18 returns to Songs.
- Exec19 (`5757–5758`) generic Selenium ActionChains click-and-hold is denied “Use one touch pointer and one contact cycle per step.” This is one **proxy policy denial, not an accepted action or gate rejection**. Exec20 uses explicit touch PointerInput and succeeds, selecting Beyond the Horizon.
- Exec21 opens selection overflow; exec22 Select all returns14selected. No duration evidence has been gathered. Exec23–24 add all14to Reggae Rhythms51.
- Exec25 (`7669–7670`) now reads **14Songs •01:08:25**, and exec26 (`8559–8560`) reopens target and reads the same total. This is first positive aggregate evidence, after indiscriminate bulk commit.
- `01:08:25` interpreted as HH:MM:SS is**4105s=68min25s**, exceeding50min by**1105s=18min25s**. Official predicate uses inclusive raw milliseconds; it does not round to minutes. App formatter implementation is not archived, but ordinary second rounding cannot explain this overshoot: even a conditional nearest-second lower bound4,104,500ms exceeds3,000,000ms by1,104,500ms. No exact source/app per-song conversion was demonstrated.
- Exec27 selects Beyond the Horizon; exec29 adds City of Stars, Eternal Flame, Falling Feathers to selection, resulting4selected. Three are declared noise, Falling Feathers is a target partition member; the agent has no numeric contribution evidence for this removal set. Selecting is **not removal**.
- Exec30 (`9791–9794`) uses the30th accepted action to open selection overflow. Returned options include **Remove from playlist**, but it is never clicked. No deletion/removal/save result exists. Raw9801 delivers exhaustion control; raw9855 business final honestly reports incomplete. Exec31 quits, preserving no further edits.

The official zero is consistent with visible overshoot, but without DB rows its exact predicate branch is unknown; another nonempty playlist or post-quit difference cannot be excluded absolutely. Visible failure and aggregate planning are independently evidenced, not derived solely from reward.

##### Actual accepted-action ledger and denial/exhaustion sequence

All30 accepted actions have status200. Breakdown:23click,2input,3back,2actions. One unsupported ActionChains denial before step18 is separate; accepted count remains30and gate rejectedActionCount0. The final accepted call returned completed/alive before the business submission; no invented missing result or post-exhaustion mutation. The31Python calls exceed advisory30, which explicitly does not affect reward. Business deadline was not reached (termination retains over1500business seconds).

| Step | Kind | Intended action from code | Exec / raw lines |
|---:|---|---|---|
| 1 | click | Open launcher Search | 4 / 1147–1148 |
| 2 | input | Enter Retro Music | 5 / 1403–1404 |
| 3 | click | Open Retro Music icon | 6 / 1638–1639 |
| 4 | click | Open Songs | 8 / 2282–2283 |
| 5 | click | Open Songs overflow | 9 / 2706–2707 |
| 6 | back | Close Songs overflow | 10 / 2971–2972 |
| 7 | click | Open Playlists | 10 / 2971–2972 |
| 8 | click | Open playlist overflow | 11 / 3218–3219 |
| 9 | click | New playlist | 12 / 3528–3529 |
| 10 | click | Focus playlist name | 13 / 3713–3714 |
| 11 | input | Enter Reggae Rhythms 51 | 13 / 3713–3714 |
| 12 | click | Create playlist | 14 / 3949–3950 |
| 13 | click | Open empty Reggae Rhythms 51 | 15 / 4317–4318 |
| 14 | click | Open playlist overflow | 17 / 4834–4835 |
| 15 | back | Close playlist overflow | 18 / 5213–5214 |
| 16 | back | Return to Playlists | 18 / 5213–5214 |
| 17 | click | Open Songs | 18 / 5213–5214 |
| 18 | actions | Touch long-press Beyond the Horizon | 20 / 6173–6174 |
| 19 | click | Open selection overflow | 21 / 6494–6495 |
| 20 | click | Select all: 14 selected | 22 / 6659–6660 |
| 21 | click | Open selection overflow | 23 / 7064–7065 |
| 22 | click | Add to playlist | 23 / 7064–7065 |
| 23 | click | Choose Reggae Rhythms 51 | 24 / 7335–7336 |
| 24 | click | Open Playlists; 14 Songs • 01:08:25 | 25 / 7669–7670 |
| 25 | click | Open Reggae Rhythms 51; same total | 26 / 8559–8560 |
| 26 | actions | Long-press Beyond the Horizon; 1 selected | 27 / 8890–8891 |
| 27 | click | Select City of Stars | 29 / 9578–9579 |
| 28 | click | Select Eternal Flame | 29 / 9578–9579 |
| 29 | click | Select Falling Feathers; now 4 selected | 29 / 9578–9579 |
| 30 | click | Open selection overflow; Remove from playlist is visible, not clicked | 30 / 9791–9794 |

##### Cause, proposed fixes, and independent oracle risk

**Confirmed root at behavior level:** unmeasured Select all was used before a numeric acceptance plan, then correction actions lacked measured contributions and a remaining commit/readback budget. It is not proof the agent believed14songs necessarily meant47.5min, but its executed route did not establish the needed measure before mutation.

The captured shared Skill already requires aggregate numeric evidence, states that a selected count/titles/empty-container zero do not prove an aggregate, and permits only safe reversible **in-budget small batches** when increments are unknown (raw60 event54, returned content247–258). Captured Android guide explicitly budgets navigation/input/confirmation/save/readback/correction (event55 content271–276). The trace deviates from existing guidance; a Skill edit remains proposed/decision_needed, not an established missing invariant. No Runtime blame from wrong total or source-seeded metadata mismatch is warranted.

Proposals are independent from causal claims and are fully structured with invariants/risks/falsification in JSON:

1. **Agent numeric plan (proposed):** get reliable per-song contributions from a currently observed allowed Details path/visible numeric surface, or a genuinely in-budget reversible small aggregate batch; compute a set with interior margin before commit. No hidden oracle subset or invented duration API. The archive does not prove a complete low-action route exists within30steps, so do not promise it.
2. **Agent budget plan (proposed):** budget correction through Remove from playlist, confirmation if required, and final target readback. Distinguish Remove from playlist from destructive Delete from device. Four selected rows or an open menu are not a saved-state correction.
3. **Oracle-owner decision needed:** restore intended TaskEval base initialization and explicit storage isolation, or otherwise version/document equivalent deterministic setup; separately archive bounded actual initialized song metadata and evaluator row projections in future campaigns. Do not naively call the parent RetroCreatePlaylist initializer, which writes the wrong random-duration dataset before overwrite. Changing setup changes benchmark instances and comparison baselines; no patch or coordinated owner approval is claimed.

Falsification: actual pre-add numeric evidence predicting45–50min would point to metadata/app mismatch instead; a captured removal commit after9794would change the ledger, but none exists; frozen source/init traces showing correct base initialization/isolation would narrow the source-level omission concern. Absence of persistent evidence is an explicit limitation, not permission to claim success or blame cleanup.

#### Business-submission precedence and exact conversion

-058first business final is raw line**6630**, receipt phase`business`, received230.8372605420882s, valid string: “Incomplete: playlist Hip Hop Bangers270 contains only Dreamer's Awake; the requested three-song order was not established.” (Exact spacing/text/envelope retained in JSON/raw archive.)
-060first business final is raw line**9855**, receipt phase`finalization`, received329.42308699991554s, valid string reporting14songs and01:08:25. Both`result.agent.answerSubmission.ignoredFinalMessages=1` correspond to later cleanup finals, not replacement answers.

`omp_supervisor.py:211–234` selects the first assistant stop while no receipt exists, cleanup is not seen, and receipt time is within cutoff. `submission.py:45–93` parses finite JSON, requires dictionary/taskOutcome nonempty string, then **only strips leading/trailing whitespace**. Numeric strings are not coerced; neither case submits a number/object. The saved`rawText`, complete parsedValue and exact stripped answer are in each business-submission.json and copied in structured case record. Shared checks prove parser/archive fidelity. There is no unit conversion or “68:25answer vs47.5expectedanswer” comparison to fix in these mutation tasks.

#### Remaining unknowns and hand-off

058unknown: actual clicked menu identities, exact stored SongEntity rows/song_key order, app duplicate-suppression behavior, post-quit persistence.060unknown: full14song set, all actual individual durations, missing/stale initialization items, exact formatter/codec offsets, post-quit/evaluator rows and any other nonempty playlist. No purported successful song subset is reconstructed.

Completed only diagnosis artifacts. No build/lint/test suite/device checks were run or are needed to prove these archival findings. Any future product/Skill/oracle fix needs its own owner decision and acceptance verification; this report does not claim it exists or is approved.

## 领域：retrieval

原领域报告：[domain-retrieval.md](domain-retrieval.md)；结构化取证：[domain-retrieval.json](domain-retrieval.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### Retrieval failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Scope: cases 076,091,106,107. This is diagnosis, not a product/config/test modification. Historical official rewards remain unchanged.

#### Findings at a glance

| Case | Recorded answer / reward | Strongest finding | Root confidence |
|---|---|---|---|
|076 SimpleCalendarFirstEventAfterStartTime|Appointment for Budget Planning /0|Template inserts expected Grocery Shopping **at**17:20 but asks for first event **after**17:20. The Agent excludes equality and opens next day; that does not prove complete or date-scoped correctness.|Confirmed oracle wording/generation inconsistency; strict-after answer correctness unknown|
|091 SportsTrackerTotalDistanceForCategoryOverInterval|1996 /0|1996 is one1.24mi activity, not the total of both captured template-only candidates. Second2.80mi contribution implies probable6502m total, after per-row initialization conversion.|Confirmed single-item answer and missing coverage; exact total probable source/display reconstruction|
|106 TasksCompletedTasksForDate|Participate in brainstorming session, Plan family reunion /0, step_budget|Two items submitted against three relevant title slots; third title never captured. Misnavigation, filter ambiguity, ineffective gestures and policy-denied compounds prevent full collection.|Confirmed cardinality rejection; precise completed-toggle state probable/unknown|
|107 TasksDueNextWeek|20 /0|All26rows reconstructed, but weekday-string predicate wrongly includes14past-week distractors. Literal oracle count is6; six actual source/captured members identified without seed replay.|Confirmed authored-predicate defect; absolute noise dates source-derived, not DB readback|

Full structured records—including exact params, goal, full toolCall IDs, every Python cell's original request code, inner status, action ledger, root/fix separation and unknowns—are in `domain-retrieval.json`. Reproducible read-only query code, actual pure-probe outputs and limitations are in `domain-retrieval-queries.md`.

#### Shared mechanism, provenance and limits

- Official tasks are dynamic classes registered from `information_retrieval_registry.py:51-112`. `InformationRetrieval.__init__` copies the task template and sets complexity from the proto (`information_retrieval.py:65-80`); `initialize_task:82-107` formats the proto, may reword prompt dates, then initializes the app. Manifest params are **not** a frozen dump of instantiated relevant rows. `_without_replacement` formatting removes each params value from candidate pools before further random selection (`proto_utils.py:254-268,271-325,336-403`). No seeded initialization was replayed here.
- Frozen actual budgets are10/20/10/10; do not infer12/22 from registry class complexity overrides1.2/2.2. The instance copies proto complexity1/2, and the recorded budgets agree with `suite_utils._allocate_step_budget:491-502` (`int(10*complexity)`). No budget or reward repricing is proposed.
- `InformationRetrieval.is_successful:109-119` compares `env.interaction_cache` to expected values extracted **only from initialized relevant proto**, not the live DB. The base method merely checks initialization (`task_eval.py:166-180`). COUNT/SUM return one numeric answer; string retrieval returns all title values (`proto_utils.py:183-251`). Each of these four tasks has one all-or-nothing success criterion; no partial subscores.
- String answers are comma-split and stripped per item; STRING_MATCH uses case-insensitive difflib similarity>=0.9 (`fuzzy_match_lib.py:20-51`). Cardinality must match; then each submitted item can match any expected item (`proto_utils.py:147-180`). This is order-independent but not one-to-one. The synthetic duplicate probe confirms a latent false-positive weakness, **not** the cause of the two-versus-three rejection. A proposed occurrence-aware fuzzy matching fix is recorded separately in JSON.
- First business/finalization assistant stop wins (`omp_supervisor.py:211-234`). Only a nonempty string `taskOutcome` is accepted; outer whitespace is stripped, not content-coerced (`submission.py:45-93`). Runner reparses the archived raw text and places the exact answer string in the IR interaction cache (`runner.py:771-788`). Parent `shared-offline-checks.json.receiptPrecedenceProbe` confirms the first receipt and archived raw text agree and precede cutoffs. All four archived envelopes are valid strings. Correct format is not semantic correctness.
- Cleanup/quit precedes evaluation (`runner.py:716-737,790-796`), task teardown follows it. Each scoped cleanup cell only calls quit and returns its successful owned-session receipt. Because these IR expected values are in-memory proto values, no cleanup-induced change to expected membership is evidenced. There is no per-attempt SQLite snapshot; a UI observation is not promoted to persisted DB proof.
- Initial user prompt is raw JSONL line9 in each case and includes the exact goal, initialized reference clock `2023-10-15T15:34:00+00:00`, timezoneUTC, business/string contract and actual step limit. Thus missing-clock or legacy number-envelope explanations are excluded here. The runtime clock is explicitly described as initialization reference, not a live device clock measurement.
- Original result, normalized events, raw JSONL and business submission files were read only.65 actual Python responses were inspected (7/24/19/15):56 completed,9 failed, **all kernelState alive**.33 accepted UI actions total. A failed cell can follow a successful prefix action. No device/Appium/ADB/MCP command, formal task/score rerun, test, build, linter or formatter was invoked by this investigation.
- 独立review的31-file历史Git revision blob/hash比对与当前所引文件全部一致（review.json#/independentOfflineQueries/sourceIdentity）；本修订引用现有证据，不重跑。残余限制是历史运行import路径/实际安装task包bytes未归档，不能把revision内容等同提升为运行加载字节已证。 IR任务初始化proto/DB与历史UI证据的差别继续保留，不把31-file源码检查当新生成集合。
- The frozen Skill was actually loaded. Its `amkernel-appium.md` section **Prove scope, membership and coverage** already demands full population, business membership, precise date predicates/reference clock and correct measures/units (raw read ends076L57,091L54,106L57,107L54). These failures do not establish that the Skill lacks the rule or Runtime is defective. Workflow fixes below are proposed behavior changes, not claims of approved Skill/core changes; amkernel-owner mechanism analysis remains separately owned.

<a id="case-076"></a>

#### Case076 — equality boundary is not strict after

**Prompt:** What is my first event after5:20pm October29 2023 in Simple Calendar Pro? Titles only.

**Actual archive:** `{"taskOutcome":"Appointment for Budget Planning"}`; `parsedValue.taskOutcome` and stripped `answer` are that same string. First business final is raw L1782, received 93.553689s, before cleanup; reward 0, terminationcompleted.

##### Oracle and actual boundary facts

Template `tasks.textproto:858-893` creates exactly one relevant event using `{date}`, `{time}`, `{title}` and returns IDENTITY(title). Here title is directly bound (not without-replacement) to **Grocery Shopping**, at **Oct 29 17:20**, lasting60minutes. Calendar utility converts withUTC (`calendar_utils.py:56-130`), inserts this plus75 random events, shuffles, and excludes qualifying later same-day random spans (`133-155,192-331`). The oracle never computes minimum start time or applies a strict-after predicate; its expected title is the direct relevant title.

Raw endL1353 (`call_kPvttdCGaXq4Y3Ru9uaiaUMC`, cell 5) actually returns `October29(Sun)`, `Grocery Shopping`, `17:20-18:20`. Cell6 is a deliberate next-day arrow tap; raw endL1678 (`call_T8Hpx8zwhHfUly2h4wVFyGh9`) returns `October30(Mon)`, `Appointment for Budget Planning`, `08:35-09:35`. These are original structured Python response facts, not an inference from final text.

Pure isolated probe on those exact threshold facts yields strictAfter=false, inclusiveAfter=true, oracleExpectedTitles=[Grocery Shopping]. This confirms a **template wording/generation/oracle inconsistency**: the target is exactly at the boundary, whereas ordinary “after” excludes equality. It is not a Runtime or Harness parsing problem.

The date may also constrain search to Oct 29 rather than any future day; the goal does not make that scope explicit. There is no complete76-event inventory or proof that the next-day08:35event is the globally first strict-after event. The Agent's equality exclusion is reasonable but does **not** certify its answer as correct under either unresolved scope. Recorded reward is not changed.

##### Cause and separate fix

Immediate mismatch is submitted next-day title versus expected relevant-proto title. Confirmed root is the oracle task-contract inconsistency; complete Agent user-goal correctness remains unknown. Proposed decision: either explicitly say **at or after**, or separate query time from a strictly later inserted start and exclude earlier qualifying competitors, with clear date/tie semantics. That semantic cutover needs a new comparable identity. Do not instruct the execution model to memorize source answers or silently reprice this attempt.

<a id="case-091"></a>

#### Case091 — one correct conversion is not a total

**Prompt:** Total kayaking distance in OpenTracks from Oct 09 through Oct 10 2023 inclusive, integer meters.

**Actual archive:** `{"taskOutcome":"1996"}`; parsed and stripped answer1996string. First business final raw L3792, received 175.104071s; reward 0, terminationcompleted.12/20 actions,8 unused.

##### Collection and numeric reconstruction

Template `tasks.textproto:2932-2990` contains **two** relevant activities, both categorykayaking and start_dateOct9. It sums initialized `total_distance`. Distractor generation adds20 rows, rejecting lowercase categoryCONTAINSkayaking AND local startdate>=Oct 9 AND<=Oct 10 (`activity_app_utils.py:42-53,144-231`). Thus the interval is start-day based, not activity-end overlap; UTC day semantics include both dates.

`_create_activity_from_proto:65-110` mutates each proto distance before insertion/score extraction. Conversion is per-row `round(round(meters/1609.34,2)*1609.34)` (`56-62`). Numeric comparison is `abs(answer-expected)<10`, **strict**, not<=10 (`proto_utils.py:169-175`). Displayed miles should not be summed as original manifestdistance4000: that param is removed from the without-replacement pool, as are manifestname/time values. A source/display reconstruction is required.

Raw endL3301, cell 20, already contains these two candidates on Monday:

|Captured title|Time|Displayed distance|Offline source-linked reconstruction|
|---|---|---|---|
|Need more strength and conditioning|08:00|1.24mi|Unique allowed input2000m -> stored/proto 1996 m|
|Mindful Movement|06:15|2.80mi|Unique allowed input4500m -> stored/proto 4506 m|

Cell21 opens only the first; raw L3432 returns full Oct 9 08:00date and1.24mi. Cell22 exposes no category text. Historical screenshotL3606 shows a paddling/kayaking glyph; that alone would not prove taxonomy. Stronger offline basis: AST literal extraction confirms **neither title exists anywhere in the random-activity name corpus**, while both are in the relevant task name pool. With two relevant slots, both captured candidates are the relevant generated records under this source contract. The two distances uniquely map within the allowed distance domain. Probable reconstructed expected total is **1996+4506=6502m**. Submission differs by4506m, far beyond10m tolerance.

This6502is **not** an archived oracle return or persisted DB fact. The second full detail/category/start timestamp and initialized sports proto are missing; confidence in the exact total is probable source/display reconstruction. The direct behavioral evidence is stronger: answer1996is one observed activity's conversion, and complete category/date population was not established before finalizing.

Cell11's unfiltered aggregate is KAYAKING(4),14.53mi—not requested interval evidence. Filter dialog atL2289 shows Oct 15–21; opening its clipped From picker and clicking the header never returns a successful Oct 9/Oct 10date change, and the dialog is cancelled. Stale failures in cells7/13occur after successful prefix clicks; reconciliation cells8/14prove the changed surface. Neither is Runtime death. Some random names overlap category corpora (e.g.Waterway Paddle/Paddle Outing), so random-title intuition alone cannot classify them. Source excludes all qualifying noise, but all 22 DB rows were not independently captured: final bottom Kayak Expedition row is clipped and tail not fully traversed.

##### Cause and separate fix

Probable root is Agent aggregate-population failure: abandoned filter route, selected one detail, omitted a second already-visible source-linked candidate, and stopped with8 steps unused. Unit arithmetic alone is not the defect. Proposed behavior: establish verified category/date aggregate scope or enumerate and bind every candidate's identity/category/full date/distance before reducing. Keep ambiguous membership unknown rather than call a single item a total. Existing Skill already says this; an extra textual exemplar would need separate justification, and no core Runtime blame is supported.

<a id="case-106"></a>

#### Case106 — missing third member under an exhausted navigation budget

**Prompt:** Which tasks have I completed for Oct 16 2023 in Tasks? Titles only.

**Actual archive:** `{"taskOutcome":"Participate in brainstorming session, Plan family reunion"}`. The string is valid; first finalization final raw L5539 received 251.325493s, about21.186s after finalization started230.139016s, within120s and original720s business deadline. Reward0; terminationstep_budget.

##### Exact oracle collection; what cannot be known

Template `tasks.textproto:1527-1576` contains **three** relevant tasks. Each is dueOct16 and completedOct10 with selectedtimes. Exclusion is due_date==Oct 16, regardless completion state, for20 random distractors. Success returns all three relevant titles. It does **not** ask the DB for completion timestamps onOct16 and does not infer business status from checkboxes. `task_app_utils.py:55-96,176-236` stores completion timestamp milliseconds and0for incomplete. Due-time is absent, so relevant due date is midnightUTC. “Completed for” is less explicit than “completed tasks due on”; source chooses due-for date. Treat wording clarification as a decision, not a proven bad oracle.

RawL1417before filter manipulation shows two candidate titles, each dueTmrw; reference dateOct15makes that Oct 16. They match relevant-only title corpus, not noise titles. A third relevant title is never captured. **Do not substitute params.title=Plan team outing**: formatting removes that value before without-replacement title choices. Without replaying initialization or possessing the DB/proto snapshot, the exact third title cannot be computed.

The expected **cardinality 3** is nevertheless structural and computable without replay. Submitted cardinality 2 necessarily fails `check_agent_answer`'s length guard before any fuzzy comparison. Order is irrelevant. No complete expected title list is fabricated here.

##### Historical execution and failure layering

- Cell3's drawer swipe consumesstep1, then its chosen wait predicate times out; subsequent read proves drawer is open. Do not treat whole failed cell as a failed mutation.
- Cell6's right swipe intended to open the app drawer/navigation instead leaves the Agent on the launcher; subsequent read confirms wrong surface. Why the app exit occurred (e.g.edge gesture) is not proved.
- Cell8 relaunches Tasks and opens More options, using two steps. Cell9 toggles Show completed. Its tuple-bearing result is boundedrepr; cell 10recovers retained rows as JSON. Result is8 unchecked noise rows; initially seen target titles are absent. The menu's actual checked ON/OFFstate was not captured, so hiding completed is probable, not established solely by menu text.
- UiScrollable.scrollToEnd(12) in cell 11 is denied **before admission**, because one locator could conceal multiple UI interactions. It consumes0 accepted steps. Cell12's allowed swipe does not advance relevant rows. Cell13 Sort click is accepted, but its wait expects labels different from the actual Grouping/Sorting sheet and times out. Reads recover the real sort surface.
- Cell17back succeeds (step 9), then percent10scroll is denied before admission as beyond single-interaction bounds. Cell18percent1scroll consumesstep10, returnsfalse and the same 8 rows. Harness finalization message is raw L5122. Further mutations stop; the business answer reuses only the two initial candidates. Dedicated cleanupquit is raw L5611.

Both protocol denials are distinct from `stepBudget.rejectedActionCount=0`: `_authorize` validates before the action gate (`appium_proxy.py:494-502,309-319,871-872`). There are no post-budget rejected mutation attempts. All19 inner responses report kernelState alive;5 inner failures comprise 3 wait timeouts and 2 policy denials. Execution survival is not business success.

##### Cause and separate fix

Confirmed immediate cause is incomplete2-versus-3list. Behavior-level root is incomplete target collection after wrong-surface navigation, unverified filter scope and ineffective/unsupported scrolling, ending at10 steps. The exact filter-state subcause remains uncertain. Proposed behavior: reconcile surface after each timeout, compare same candidate rows/status across completed-filter changes, and use one bounded supportedgesture with measured row progress rather than compoundUiScrollable/percent10or unrelated sorting exploration. No guarantee that every task can be completed in10 steps is asserted; do not invent missing members after exhaustion. The Skill already requires these invariants.

<a id="case-107"></a>

#### Case107 — full traversal followed by an incorrect date-label predicate

**Prompt:** How many tasks due next week? Week startsMonday; integer.

**Actual archive:** `{"taskOutcome":"20"}`; string parsed unchanged. First business final raw L4268 received 172.391514s; reward 0, terminationcompleted.8/10 actions,2 unused.

##### Complete membership reconstruction

Reference clock is SundayOct15 2023 UTC, so next week is **Oct 16–Oct 22inclusive**, equivalently [Oct 16 00:00,Oct 23 00:00)UTC. Template `tasks.textproto:1398-1524` has **six** relevant rows; COUNT(tasks_app_tasks) therefore expects6independent of names/seed. Due-date choices without replacement are Oct 16–22 after excluding params.due_date Oct 19. Noise20rejects that whole date interval. No incomplete-only or currently-visible condition is in this oracle.

Two initial mobile scrollGestures returnfalse and unchanged, but subsequentW3C swipes actually advance. Therefore those earlyfalsevalues were not population-completeness proof. Four actual JSON row windows, stitched with longest contiguous overlaps5,3,6, give26 records. A final same-direction W3C swipe returns unchanged after progress, supporting terminal coverage. Raw cell 14 then explicitly merges 26 and counts 20.

The relevant task title corpus and random `_TASKS` corpus are disjoint (AST literal query returns empty intersection). Captured six relevant-title records therefore identify the membership below without seed replay. Generator window for noise is default14days centeredOct15 15:34, i.e.Oct 8 15:34 through Oct 22 15:33; exclusion removesOct16–22, so random due days are Oct 8–15. This permits mapping their ambiguousweekdaylabels to past week, **as a source-derived reconstruction**, not direct DB timestamp evidence.

|True member|Captured label|Reconstructed due date|
|---|---|---|
|Follow up on support tickets|Tmrw|Oct 16|
|Plan family reunion|Tue|Oct 17|
|Book flights for conference|Wed|Oct 18|
|Research market trends|Fri|Oct 20|
|Send report to manager|Sat|Oct 21|
|Organize files and folders|Oct 22|Oct 22|

The bug is the Agent-authored cell 14predicate:

```python
next_week_labels={'Tmrw','Mon','Tue','Wed','Thu','Fri','Sat','Oct 22'}
next_week=[... for r in all_rows if r['due'] in next_week_labels]
```

This includes14 past-week noise occurrences along with6 members. It is not an arithmetic issue or first-page count. It is also not a reason to deduplicate titles: there are multiple legitimate same-title occurrences, includingtwo identical Finish Project Proposal Oct 8 rows that the overlapmerge correctly preserves. Exact row IDs are absent; tuple overlap is not a universal stable identity guarantee, but captured sequence/multiplicities26=6+20andterminal window support this bounded reconstruction.

|#|Captured title|Label|Source-linked due date|In true week?|Agent counted?|
|---|---|---|---|---|---|
|1|Finish Project Proposal|Oct 8|2023-10-08|no|no|
|2|Finish Project Proposal|Oct 8|2023-10-08|no|no|
|3|Finish Project Proposal|Fri|2023-10-13|no|yes|
|4|Call Grandma|Wed|2023-10-11|no|yes|
|5|Call Grandma|Thu|2023-10-12|no|yes|
|6|Water Plants|Thu|2023-10-12|no|yes|
|7|Call Grandma|Today|2023-10-15|no|no|
|8|Reply to Emails|Fri|2023-10-13|no|yes|
|9|Water Plants|Yest|2023-10-14|no|no|
|10|Create Budget for Next Month|Fri|2023-10-13|no|yes|
|11|Read 'The Martian'|Today|2023-10-15|no|no|
|12|Follow up on support tickets|Tmrw|2023-10-16|yes|yes|
|13|Plan family reunion|Tue|2023-10-17|yes|yes|
|14|Book flights for conference|Wed|2023-10-18|yes|yes|
|15|Research market trends|Fri|2023-10-20|yes|yes|
|16|Send report to manager|Sat|2023-10-21|yes|yes|
|17|Organize files and folders|Oct 22|2023-10-22|yes|yes|
|18|Call Grandma|Wed|2023-10-11|no|yes|
|19|Brainstorm Blog Post Ideas|Thu|2023-10-12|no|yes|
|20|Read 'The Martian'|Thu|2023-10-12|no|yes|
|21|Back Up Computer Files|Fri|2023-10-13|no|yes|
|22|Attend Team Meeting|Tue|2023-10-10|no|yes|
|23|Water Plants|Mon|2023-10-09|no|yes|
|24|Reply to Emails|Wed|2023-10-11|no|yes|
|25|Renew Driver's License|Fri|2023-10-13|no|yes|
|26|Grocery Shopping|Today|2023-10-15|no|no|

##### Cause and separate fix

Confirmed defect is authored predicate semantics: weekday strings are treated as absolute next-week dates. Full initialized clock context was present and even the returned cell 14report labels the intended intervalOct16–22; merely supplying more clock prose is not the fix. ModuleNotFoundError for lxml and an incorrect Appium actions import failed before UIactions, were recovered using stdlib XML/Selenium imports, and did not cause20 versus 6.

Proposed behavior: resolve absolute date or trustworthy bounded interval from details/native datefilter before applying week membership; preserve ambiguousweekdayvalues asunknown rather than assume forward. Keep26occurrences and exactMondayboundary; do not smuggle the known templatecount 6into execution instructions. Existing Skill already contains the reference-clock/date invariants. No Runtime or Harness semantic defect is established.

#### Actual action ledgers

Each row is one admitted Appium UI interaction. Status200means upstream mutation completed; a laterwait/staleexception can still fail the cell. Session creation, read-only observations, imports and quit are not step actions. Original full code/tool IDs and inner errors are retained in JSON.

##### 076 — 3/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|3 /883–884|Launch Calendar|200|
|2|5 /1351–1353|Tap Oct 29 calendar day|200|
|3|6 /1677–1678|Next-day arrow to Oct 30|200|

##### 091 — 12/20

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|4 /843–844|Launcher drawer swipe|200|
|2|5 /973–974|Launch OpenTracks|200|
|3|7 /1276–1277|Introduction next (post-click enumeration stale)|200|
|4|9 /1504–1505|Introduction next to list|200|
|5|11 /1941–1942|Open aggregated statistics|200|
|6|13 /2177–2178|Open Filter (post-click enumeration stale)|200|
|7|15 /2503–2504|Expand From date picker|200|
|8|18 /2929–2930|Click date-picker header (no changed date evidenced)|200|
|9|19 /3197–3198|Cancel filter|200|
|10|19 /3197–3198|Navigate up to TrackListActivity|200|
|11|20 /3300–3301|Swipe list to older activities|200|
|12|21 /3431–3432|Open Need more strength and conditioning detail|200|

##### 106 — 10/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|3 /973–974|Launcher drawer swipe (post-action wait timeout)|200|
|2|5 /1416–1417|Launch Tasks|200|
|3|6 /1744–1745|Right swipe intended drawer, later found launcher; wait timeout|200|
|4|8 /2262–2263|Relaunch Tasks|200|
|5|8 /2262–2263|Open More options|200|
|6|9 /2686–2687|Toggle Show completed|200|
|7|12 /3433–3434|Swipe list; no business-row progress evidenced|200|
|8|13 /3595–3596|Open Sort; wait predicate misses actual Grouping/Sorting sheet|200|
|9|17 /4781–4782|Back from Sort|200|
|10|18 /5112–5115|One bounded scroll; returns false and unchanged first eight rows|200|

##### 107 — 8/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|5 /1677–1678|Launcher drawer W3C swipe|200|
|2|6 /1951–1952|Launch Tasks|200|
|3|7 /2436–2437|mobile scroll down; false/unchanged|200|
|4|8 /2561–2562|mobile scroll up; false/unchanged|200|
|5|10 /3054–3055|W3C swipe advances window|200|
|6|11 /3319–3320|W3C swipe advances window|200|
|7|12 /3580–3581|W3C swipe reaches final rows|200|
|8|13 /3838–3839|W3C swipe unchanged establishes terminal window|200|


## 领域：system-sms

原领域报告：[domain-system-sms.md](domain-system-sms.md)；结构化取证：[domain-system-sms.json](domain-system-sms.json)。以下保留该领域完整分析正文；路径约定与当前目录一致。

### System / SMS failure diagnosis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope: **085 SimpleSmsSendClipboardContent** and **098 SystemBrightnessMaxVerify**, attempt1 only. These are diagnosis documents, not product/configuration/test fixes. Original result, normalized event, business submission and raw event files were read only. No device, ADB, Appium, MCP execution, formal task/scoring rerun, build, formatter or test suite was invoked. Retained screenshots were decoded in memory; no new screenshot was captured.

#### Findings at a glance

| Case | Proven outcome | Strongest causal finding | Root confidence |
|---|---|---|---|
| 085 | Official0; never got beyond recipient entry, no message-body/paste/send operation in trace; honest inability final | Six initial UI permits did not advance requested app flow; recipient presence was accepted without confirmed composer; all12 permits consumed. Appium clipboard helper failed independently, but is not a demonstrated Runtime cause. | **Confirmed behavior/planning failure**; underlying helper root unknown |
| 098 | Official0 despite success final;3/10 permits used | Literal-node零匹配、source非空、一次swipe及缺numeric验收为事实；初末整数、geometry、XML与swipe是否改变亮度unknown | **Confirmed acceptance gap; actual state-loss mechanism unknown**, not established initialized255 regression |

Outcome confidence and root confidence are deliberately separate. Reward0 is not a substitute for provider rows, exact settings output, or component subscores. The companion JSON contains complete structured records, exact executed code, original structured Python response facts, full toolCall IDs, source anchors, timeline/ledger, proposed fixes, falsification conditions and unknowns.

#### Paths and provenance

- `C = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`
- `A085 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1`
- `A098 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1`
- `A097 = campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/097-SystemBrightnessMax/attempt-1` (targeted same-campaign successful mechanism counterexample only).
- Shared Appium log: `evidence/screenshot-video-controls-20261106T231029Z/appium.log`. The campaign service receipt `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/service-receipt.json:13-17` identifies that service/log. Queries below are limited to owned sessions `fb607e05-8328-496b-b945-d7384303e186` and `d5ecafcc-25b3-4721-af53-e79c6bbdb9fc`; other campaigns in that shared file are out of scope.
- Both results record AndroidWorld0.1.0 at revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, AMKernel0.1.4. Device readiness records Android13/API33,1080x2400, UTC; no live readiness checks were performed here.
- Parent receipt `shared-offline-checks.json:1081-1088` proves current19-file Harness digest equals frozen manifest digest `861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`. Its per-case archive checks establish exact goal/reference clock/string contract and faithful first-final parsing. AndroidWorld task/helper code cited here is current checkout code; this domain did not independently hash every task file against a frozen snapshot. Installed UiAutomator2/Settings helper source is explanatory current local source, not a byte-attested historical snapshot.
- Raw `tool_execution_start.args.path` is `xd://mcp__amkernel_python_exec`; `args.content` holds actual code. Paired `tool_execution_end.result.content[type=text]` holds the returned structured Python result. The raw tool events have no timestamp; JSON labels the immediately preceding assistant-message timestamp as such. Appium log timestamps below have no encoded timezone and are not silently converted.

<a id="case-085"></a>

#### Case 085

##### Exact request, initialization and oracle

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

##### Constraints and first divergence

The initial prompt requires official Appium Python Client/UiAutomator2, one retained session, `noReset=True`, `autoLaunch=False`, `skipUnlock=True`, `newCommandTimeout=300`, session-creation execution timeout90, native interactions only, no shell/app-data APIs, exact12 UI-step limit, advisory30 Python calls, business840seconds, and no undo of requested final state. A forwarded failed UI action consumes a permit. Observations and quit remain available after closure; first business final wins; cleanup cannot replace it.

**First divergent action:** cell3 clicks launcher text `Messages` (raw731-732; Appium560179) and returns `com.google.android.apps.messaging/.ui.ConversationListActivity`. The Agent's raw assistant message_end730 explicitly wonders whether this could be Simple SMS. It was not. Cells4-8 then spend Back,drawer swipe,focus search,type search,and clicking the exact search text. Cell9 proves that exact text is the **search `android.widget.EditText`**, bounds`[214,156][886,301]`, not an application result. The correct app is finally activated in cell10, the seventh UI action.

##### Complete executed-cell sequence

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

##### Actual action ledger

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

##### Clipboard and recipient branches: what actually failed

**Clipboard:** cell12 fails at its **first** statement, `clipboard_text = driver.get_clipboard_text()`. The following click in that same cell never executes. Original structured error is `selenium.common.exceptions.WebDriverException: Appium Settings app is not running after 5000ms` (raw2663). Appium561269-561271 confirms `mobile: getClipboard` returned500 after5101ms. It is not a returned empty string and does not prove a copied value was absent or initialization failed.

Explanatory local source:

- Python client `.venv/.../appium/webdriver/extensions/clipboard.py:70-95`: `get_clipboard_text()` -> `mobile: getClipboard` -> base64 decode.
- Installed `~/.appium/node_modules/appium-uiautomator2-driver/lib/commands/clipboard.ts:7-12`: API>=29 -> `settingsApp.getClipboard()`.
- `node_modules/io.appium.settings/lib/commands/clipboard.ts:16-30`: `requireRunning(shouldRestoreCurrentApp=True)` happens **before** clipboard broadcast and temporary IME context.
- `node_modules/io.appium.settings/lib/client.ts:78-133`: launches Settings helper, waits up to5000ms for service dumpsys output containing `isForeground=true`, then throws that error. This predicate proves the local failure class, not whether the service really failed to start, its permission/OS cause, or an erroneous detection predicate.

The Agent did not force-start shared services or create another session, which is correct. Cell13 succeeds in opening a conversation with the same live driver. No later clipboard read, Clipper UI inspection, native paste, or message body is captured. Getter failure is a real contributing blocker for that strategy, but **not a demonstrated AMKernel Runtime defect and not a sufficient explanation for earlier budget loss or missing recipient confirmation**.

**Recipient:** cell14 sends `'+15459061746\n'`. Returned text is `'+15459061746 '` with trailing **space**, still `.activities.NewConversationActivity`. Its wait is `activity_changed OR number_text_present`; the second condition becomes true from typing alone, so that wait does not validate recipient acceptance. Cell15 KEYCODE_ENTER returns but its activity-change wait times out. Cell16 shows the same recipient EditText and `No contacts found`; cell17 removes the trailing space but still shows only recipient entry. Observations filter for text or non-null contentDescription, potentially excluding a visually meaningful unlabeled confirmation control; **the full source/screenshot for this stage was not retained**, so no exact Next/arrow control is invented here. Cell18 `mobile: performEditorAction done` receives a sanitized500; underlying exception details are unknown.

##### Submission, cleanup and persistence boundary

Finalization starts175.402140s after Agent start; first business final at180.648145s is raw event3936, before295.402140s finalization deadline. It says unable to send. Duplicate event3969 is ignored; cleanup prose4070 cannot replace it. The exact valid envelope and stripped answer are archived in `business-submission.json`; no type coercion/clock/first-final error is implicated.

Cell19 only retains ID,quits,and returns `quitReturned=True`. Appium561707-561711 returns DELETE200 and subsequent same-session GET404. There is **no agent Back/home/restore operation**. Harness `runner.py:716-737,790-826` and formal stage timestamps show quit/cleanup precedes evaluation; task teardown starts **after** reward. There is no post-quit package/DB readback in the domain evidence. Last observed package is correct; last page is recipient entry. Aggregate0 does not identify a particular missing provider row or package subcondition. No sent-provider rows are persisted in evidence, and no Sending exception occurred.

##### Causal conclusion and proposed targets

**Confirmed behavior failure:** under the fixed budget, identity discovery and phase acceptance spent the task's mutations before any body/send. The newline-as-confirmation and number-present wait are concrete Agent-authored mistakes, not a Runtime locator translation failure. Outcome is confirmed; exact final database state remains unknown.

**Helper root unknown:** Settings foreground-service readiness failed. Missing historical service/logcat/error details prevent attributing its underlying cause. The structured failed response plus subsequent alive calls contradict a generic dead Runtime explanation.

**Proposed only, not approved fixes:** refine existing Android app-identity/stage examples and whole-outcome budgeting in `.agents/skills/amkernel/references/android-execution.md`; do not assume text equality proves app launch or recipient confirmation; retain contentless actionable controls before claiming no route. Existing **loaded** guidance already says similar icon/search echo is not target proof (raw tool-end55 embedded lines42-46), helper failure is symptom (embedded253-257), native shortcuts may be literal, and budget must include recipient/send/readback (embedded271-275); raw tool-end32 embedded170-173 and54 embedded344-352 cover acceptance/reservation. Thus a lack of core Skill guidance is **not established**. Helper/prequalification changes are **decision-needed** pending exact service evidence; do not force-start services, change capabilities, expand12steps, or leak hidden clipboard body into the prompt. No claim is made that saving the six wrong-route actions alone guarantees completion within12.

<a id="case-098"></a>

#### Case 098

##### Exact request and oracle

Visible goal (raw `A098/raw-private/agent-events.jsonl` message_end **line9**, `result.json:687-699`):

> Turn brightness to the max value.

Params max,seed770927068；Verify子类源码请求`set_brightness(max)`，执行`settings put system screen_brightness255`，不是正式初始整数已被独立读回。源码不设automatic mode，初始整数/mode仍unknown。初始化completed和另一预演initialStateReturn1不能替代正式时刻状态，也不证明所有native读回路线可达/不可达。

`_SystemBrightnessToggle.is_successful`, `system.py:41-52`, executes **`shell settings get system screen_brightness`**, decodes/strips, converts toint, returns1 iff the integer is **exactly255**. It does not read answer text, screenshot appearance, gamma-slider text, UI percentage, or automatic mode. There are no subscores. Under that cited normal-return code, reward0 implies comparator input was not255; the actual int was **not archived** and must not be reconstructed from a bar picture.

##### Complete sequence and observed source mismatch

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

Cells3,4,6的literal`iter(node)`返回0匹配；原source响应长度非零，不支持“空树/坏accessibility”。邻案097留存的prefix为hierarchy/class-name tags并暴露SeekBar65535；**这只令098的parser格式不匹配成为probable机制**，不证明098实际XML采用同格式。098完整source、slider范围/值和brightness整数未归档，不能由097补成历史事实。

##### Screenshots, intent and actual mutation

Retained images were decoded from paired original tool-end `content[type=image]` in memory, no new capture:

| Cell/raw line | Original image SHA256 | Bounded observation and interpretation |
|---|---|---|
| 4/1090 | `1c3f34b6e4b96d8ceb2941cf108cdd27e7d0aa50c326aa6fa720dbad1de42ef1` | Notification shade visible; Internet/Bluetooth/notifications. This contradicts using launcher package alone to call shade opening unsuccessful. |
| 5/1345 | `ea75cdea7c5bc7c32ee2395daecd17b6d5f3769671288bb93f86393d66e8dffd` | Expanded quick settings; broad light-blue brightness bar near y420. Agent explicitly described it as already max. Numeric255 cannot be proven visually. |
| 7/2140 | `ba9fda334a27069e02d2a7abad90cd00a38980b08bdad3e1a711c24886347b0a` | Same expanded panel and gesture trace ending x976,y420 near sun/thumb graphic. Visually full/near full; no exact property readback. |

原Agent将x976的thumb/fill解释为already max，并在cell7调用`swipe(300,420,976,420,500)`；这是Agent的pixel estimate与已记录命令，不是经证实的active track/端点。x42..1038外框与thumb不能推出真实几何或亮度。tuple imageSize造成auxiliary dict有界repr而图像仍留存；这不证明Runtime导致scalar失分。

该swipe是一次获准输入请求；是否改变亮度、初值是否255、末值是否靠近最大值均unknown。未做semantic/numeric验收且3/10主动结束可证，但不能称其破坏已满足状态或将“内侧拖动”作为最强/已证失分机制。

##### Actual action budget, not “inefficient” shorthand

`result.json:646-680`:3admitted HTTP200 interactions,0rejected, closure`agent_finished`,7unused permits. `referenceStepsExecuted=4` is not a fourth hidden action: `stepped_agent.py:113-124,131-156` counts3mutations plus terminal done=True reference step.

| Step | Cell | Action | HTTP | Appium log line |
|---:|---:|---|---:|---:|
| 1 | 2 | Open notifications | 200 | 588620 |
| 2 | 5 | Expand quick settings: swipe (540,250)->(540,1650) | 200 | 588662 |
| 3 | 7 | Drag brightness at y420 from x300 to x976 | 200 | 588678 |

The sole failed Python cell2 consumed only the opening-shade action; its package wait failed afterward. Observations did not spend mutations.8Python executions include dedicated cleanup. Agent finished211.595821s with a valid first business final; business deadline not reached.

##### Targeted same-campaign successful counterexample 097

This was read narrowly for **native XML and exact slider endpoint mechanism**, not used to invent a benchmark answer.097 has same visible goal, same max predicate, but initialization starts atmin rather thanmax and its slider appears in a brightness dialog at another y-coordinate.

| Raw097 anchors | Actual control/operation | Actual returned fact |
|---|---|---|
| 3290-3291 | Native source prefix and SeekBar rect | Class-name XML tags; rectx42,y149,width996,height126, rightx1038 |
| 3761-3762 | Clickx1032,y212 | Native slider text`65140.0` |
| 3923-3924 | Swipe to1037,y212 | Native slider text`65469.0` |
| 4182-4183 | Swipe beyond right bound to1075,y212 | Native slider text`65535.0` |
| result.json:561 | Same state oracle after completion | officialReward1.0 |

This proves a near-right location can be **measurably below maximum** and a native numeric semantic value is available on this stack. It does **not** establish098's exact value, map every dialog/expanded-panel hitbox, or justify hardcoding gamma65535 everywhere. It also rules out the blanket explanation that all max tasks are impossible under this device/oracle.

##### First final, cleanup and oracle distinction

First business final (event2238,211.595821s) is exact `{"taskOutcome":"Brightness set to maximum."}`; archive retains it as a valid string. It is not numerically interpreted by the oracle. Cleanup user message_end2248 follows; cell8 at2330-2331 calls only quit and returns true; Appium588682-588686 DELETE200,588687-588688 GET404. The Agent does **not** restore brightness or invoke Back/home in cleanup.

Current driver `lib/driver.ts:508-615` has conditional animation/IME and hidden-API-policy restoration, not brightness restoration. The historical log explicitly records only hidden API policy restoration in that quit section; it is not an exhaustive device settings audit. Therefore no explicit cleanup brightness mutation is observed, **but no setting value before/after quit exists**, so externally stable state across cleanup cannot be proved. Harness correctly matters here: evaluator1794265680.306703 occurs **after quit**, while task teardown starts1794265680.3549619, **after reward** (`result.json:614-629`; frozen `runner.py:716-737,790-826`). Post-reward task teardown cannot explain0. Earlier driver cleanup/asynchronous change remains logically possible but unsupported.

##### Causal conclusion, oracle risk and proposed targets

- **Confirmed observations / MA09:** literal-node零匹配但source非空，未做exact-state验收，一次swipe、3/10主动结束。格式不兼容仅邻097支持的假设；实际098XML、numeric route可达性和active geometry未证。
- **State-loss cause unknown:** 初始化源码请求max不等于正式初始255；没有证据证明drag改变或破坏它。input/asynchronous/cleanup/actual-initial-state候选不能分离，不给某一回退机制最强因果地位。仅在引用谓词成功读int条件下，reward0逻辑含义为!=255，不是独立scalar readback。
- **Not proved:** oracle source bug, a false negative despite actual255, actual brightness restoration by cleanup, or any particular numeric final value. Visual-vs-exact-state observability is a comparability risk, not evidence that the official predicate is wrong.
- **Proposed only:** improve native-source examples to inspect actual tags or prefer direct semantic class/resource locators; wait on overlay controls, not forced package switch; provide Android stop-if-already-satisfied and slider endpoint/range/readback examples. Loaded generic guidance already says package/activity cannot establish page/result, HTTP success is not outcome proof, controls-first semantic evidence and preserve requested state. Lack of the core invariants is not established; targeted examples are a proposal, not an approved coordinated fix.
- **Decision-needed diagnostics only:** for a separately authorized future isolated investigation, retain exact state-oracle component before/after cleanup and actual comparator input/mode, without exposing score hints to the Agent or modifying this campaign. Do not weaken255 comparison or move formal scoring timing to make this score pass. Falsification: historical proof of255 after drag and before evaluator would shift focus to intervening state changes/oracle execution rather than endpoint placement.

#### Offline methods and output

The analysis used stdlib JSON/pathlib streaming of original JSONL, paired exact tool IDs, static source reads, and PIL/base64 only to **view already captured** images in memory. No AndroidWorld/Appium module was imported and no external command/device call was executed. Full original Python code and relevant original returned fields are preserved in JSON timeline; source/query interpretation is separate.

##### Reproducible bounded event, action and helper query

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

##### Minimal pure causal probes (actual input from097, not fabricated UI)

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

