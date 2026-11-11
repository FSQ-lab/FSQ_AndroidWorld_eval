# FSQ r4：SMS、系统与导航逐例调查（11 例）

## 范围、证据等级与路径约定

只分析 040、041、044、081、082、084、085、086、097、098、113。原始官方 reward 不改：前十例均 0，113 为 **0.5**。这是离线调查，不运行任务、评分、模型、测试或设备命令；未修改 FSQ、harness、SDK、配置或旧结果。

- **事实**：原始事件、工具 invoke 结果、UI XML 或实际查看的截图直接支持。
- **强推断**：多条证据形成因果链，但缺少执行时底层状态或完整回执。
- **未知**：现有材料不能区分的原因；不把模型 summary、AI 断言或 native success 当官方通过。
- 初始化参考时间是 `2023-10-15T15:34:00+00:00`，截图中的短信和系统时钟为该 fixture 时间附近。2026 年宿主机执行时间不是业务参考时钟。

`BASE` 为本 revision-4 目录；`E(N)` 为 `BASE/next-stage-plan/execution/run/episodes/NNN-TaskName`。`R(N)` 为该 episode 下 `raw-private/fsq-native/workspace/.fsq/runs/` 中如下唯一目录：

| N | 原始 run 目录名 |
|---|---|
|040|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7|
|041|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2|
|044|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b|
|081|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7|
|082|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb|
|084|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2|
|085|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370|
|086|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0|
|097|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-097-20261110T220905Z-8c0e3f|
|098|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-098-20261110T221109Z-190872|
|113|fsq-native-gpt61-r4-clock-lifecycle-20261110-run-113-20261110T225201Z-521d36|

每例均读取：`R/sources/000-goal.txt`、`R/execution-result.json`、`R/events.jsonl`、`R/evidence-events.jsonl`、`R/report.json`、`E/raw-private/fsq-native/worker/fsq-task-result.private.json`、`native-action-audit.jsonl`、`request.json`、`E/raw-private/task-initialization.json`、`evaluator-diagnostics.json`、`fsq-worker-outcome.json`。以下 `ev` 指 `events.jsonl.sequence`，`audit` 指 action audit.sequence，`ee` 指 evidence-events 外层 sequence，`step` 指 execution-result.steps[].step_id；三者不能混用。截图路径均相对 R；只把实际渲染内容写为视觉事实。**kill 的截图在这些例中只有 prepare/before-action；不是 kill 之后的前台截图。**

## 冻结 FSQ 机制参照

FSQ 包身份：0.1.2，package/source SHA256 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`；观察到的 HEAD 7e3f079 是 dirty，不能单独代表执行代码。下面 FSQ 文件在共享 `failure-analysis/fsq-evidence-index.json.source_identity.mechanism_files` 中均已由 parent 校验与冻结 manifest 逐文件 hash 一致。没有引入未经 hash 核对的其他当前 FSQ 文件。

- **S1 生命周期**：`fsq_agent/resources/skills/android-harness.md`，Case Lifecycle，5–10：先 launch、最终取证后 kill；`drivers/android/_uiautomator2.py::launch_app` 94–100 只调用 `device.app_start` 并回报 app_id，`kill_app` 102–107 调用 `device.app_stop`；`close` 77–78 是 no-op。launch 的 passed 不含“目标已前台可用”的后置证明。
- **S2 点击与输入**：同 driver，`tap_on` 109–116 只等 selector 存在后 click；`_selector/_selector_query/_wait_for_exists` 356–389 把 exact text/resourceId 转给 u2，只检查 exists，不验证遮挡/可交互前景；`input_text` 137–151 自带 click、可选 clear、set_text，不必先多做一次 tap。
- **S3 坐标与数值证据**：同 driver，`swipe` 162–182 仅实施坐标/方向手势；`_scaled_point/_clamp_coordinate` 468–481 只做屏幕缩放/屏幕内裁剪，不保证某控件达到业务端点；`ui_snapshot` 244–277 输出 XML 并标记 partial/semantic_compaction；`_assert_element_states` 503–515 可校验 checked 等状态，但不是系统 setting 持久化读回。
- **S4 目标收敛**：`agent/_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS` 14–46，尤其 37–40 要求一个完整最终目标；`agent/_core.py::FsqAgent._augment_goal_only_task_with_pre_plan` 151–201 只检查非空并注入生成目标；`agent/_prompt.py::PromptModelBuilder.build_task_prompt` 65–95 把 verification_goal 设为唯一成功目标。复合用户目标若被收窄，后续 verifier 不会自动补齐。
- **S5 事后 verification**：`agent/_core.py::FsqAgent.run_in_context` 100–110 在主执行后运行 verifier；`agent/_verification_task.py::VerificationEvidenceBuilder.build` 31–58、`VERIFICATION_AGENT_INSTRUCTIONS` 183–198 要求只依据 bundle，把 agent claims 当 claims，AI 断言若无冲突可采信，不重新看图；不自动获得 Android provider DB 或系统 setting。`models/_agent_io.py::AgentFinalOutput` 39–50 的 summary 是自由字符串，不等于数值型问答结果。
- **S6 原生预算/输出 producer**：执行时快照位于各 `E/raw-private/fsq-native/worker-site/fsq_androidworld_eval/`，非当前 SDK。`fsq_native.py::NativeDispatchBudget.dispatch` 85–118：write 在转发前计数并拒绝超额，launch/kill/tap/input/swipe 都算；能力清单 20–26；`BudgetedAndroidHarness.invoke_action` 164–166、`close` 177–184：close 明记 deviceRestored=false。`fsq_worker.py::select_main_answer` 22–57 只接受唯一成功主 runner 的有效 task_run_v1.summary；valid 表示输出结构合法，不代表任务、答案或评分正确。


**H1 已读的冻结 AndroidWorld 官方规则（只用于事后解释，不输入模型）。** `AW` = `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world`。`AW/task_evals/single/system.py::_SystemBrightnessToggle.is_successful` 41–52，读取 `settings get system screen_brightness`，max 必须为整数255；`SystemBrightnessMaxVerify.initialize_task` 74–86 初始设置max，`SystemBrightnessMax.initialize_task` 104–116 初始设置min。`_SystemWifiToggle.is_successful` 131–144 读取global wifi_on，on只接受'1'/'2'，不检查SSID/网络连通。`OpenAppTaskEval.is_successful` 484–499比较当前activity package与expected package。`AW/task_evals/composite/system.py::TurnOnWifiAndOpenApp.is_successful` 45–49取Wi-Fi和open-app两分平均。parent转达harness owner已核对这些源码；本笔记也直接只读了上述段落。代码揭示检查规则，不代表本次实际读取值已留存。

## 跨例合同边界（修复编号 SN）

1. **SN-L（P0，FSQ lifecycle/producer coordinator 共同所有）**：生产自动化必须保留用户要求的终态，同时按资源所有权释放连接/会话。对“打开/保持运行”等目标，业务提交/观测边界与破坏性 app_stop 不能混在同一个末尾。应由 coordinator 明确支持的 terminal-state/lifecycle policy：将资源 close 与目标 app 状态分开，一般生产行为优先保留用户末态；若实验合同强制杀 app 且与 foreground rubric 互斥，就明确记录无法同时满足的实验契约冲突，不改变旧评分或取样时点。**不能私自停用现有 Skill kill、移到评分后以刷分，或 kill 后偷偷重开掩盖冲突。** 这是产品合同决策，不是一个模型提示特判。
2. **SN-A（P1，FSQ driver/runtime）**：`launch_app` 的请求包和返回包应附目标前台身份/启动完成证据；不在仍为 launcher 时把 passed 当“已打开”。先核实被冻结 u2 启动语义，再修正使用该 backend 的前台启动路径；不要盲目重复 launch 或增预算。041 还存在 request.appId 明确配成 Camera 的 producer 映射错误，不能全归为 u2。
3. **SN-B（P1，producer + FSQ tool/runtime）**：保持现有最大 write 数不变，向主执行暴露剩余可用 write 与计数单位，在新分支前核算业务动作和既定清理成本；`NativeActionBudgetExceeded` 已是不可重试的当轮硬边界，不再同参数重试。没有批准前不把 teardown 移出预算。纠正多余 tap、错误 app 与隐藏控件误点，而不是只提高上限。
4. **SN-D（P0，FSQ lifecycle+harness归因；P1证据）**：冻结sms.py:173–243继承SimpleSMSSendSms无评分override，联系人仅initialize:216–239；sms_validators:255–276检查sent(number/body/window) AND foreground。082/084/085/086均实际kill目标SMS，前台冲突为主强推断，缺评分activity/row/role实读，不能称已证哪分支。send→eval分别47.604/34.374/50.869/40.386s排除执行耗时>5min，但不替代provider.date/device now。按SN-L修一般末态合同；不得盲重发/提前评分/重开补分，也不把UI ack当官方通过。recency/Oscar来源绑定属于业务识别与本地验证，不是独立oracle扣分项。

## 案例 040 — NotesTodoItemCount

交叉核对：已核对、有保留。S8隐藏Ideas与前景Workout bounds重叠、drawer未展开支持隐藏exists后点前景主强推断，缺点击坐标；冻结proto3条COUNT期望3仅事后判据，actualDB/全集仍未知。唯一main step4解释summary非数字，不能从其它payload提数。

**目标与原分。** 只回答 Joplin `Ideas` folder 的 to-do 总数，输出必须是一个数；官方 0。数的是 to-do 条目，不是正文里列举的事项或普通 notes。公开目标没有提供正确总数。

**实际序列。**

- ev19/23，step launch_app-1/-3 请求 Joplin；首个截图仍在 launcher；ev25 swipe、ev31 tap Joplin 才进入 All notes。
- ev37，step tap_on-8 用 exact text `Ideas`。prepare XML 同时含 All notes 的 `Workout Routine - Strength Training`（bounds `[119,740][1041,797]`）和 drawer 的 `Ideas`（`[39,740][614,797]`）；实际点击后屏幕变成 **Health / Workout Routine - Strength Training**，不是 Ideas。
- ev41 Back，ev45 Sidebar，ev51 tap Ideas（step14）后真正进入 Ideas。`artifacts/tools/000016-ui_snapshot.json` 与截图显示 Recipe Ideas、Financial Plan、Work Tasks 三个带 checkbox 的 to-do，后面是大量普通 notes；这只证明当前页，不证明 folder 全量只有三项。
- ev57 swipe（step16）检查后续列表；ev63 Search（step18）；ev67 input `notebook:Ideas type:todo`（step20）被拒，audit39/ee310。ev69 kill（step21）亦被拒，audit40/ee328。共 10/10 admitted，非 deadline。
- 主 runner 输出 inconclusive，`mainAnswer.summary` 是“Could not verify…”而非单个数字；native verifier 正确 failed。不存在已核实总数却只丢了格式的证据。

**首次偏离／直接失败／根机制。** 首个可证明的导航偏离是 step8 点“树中 Ideas”却打开 Health 笔记；直接业务失败是完整计数/数值回答都未完成，随后搜索被预算挡住。**强推断**：未展开 drawer 的节点仍在 UI hierarchy，exists 命中后点击其坐标落在前景 note；S2 只有存在性检查，解释了屏幕与命中文字不一致，但缺少 u2 点击坐标回执，不能写成已证实驱动选错 selector。错误路径和恢复耗费有限 write，预算拒绝是后果，不是计数能力的唯一根因。**未知**：真实总数、是否还有离屏 to-do；不从 hidden params 或三条可见项猜答案。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-7cd0357478fa.png`（launcher）；`screenshot-agent-tap-on-8-finalize-after-action-1-764caef6e206.png`（Health 误入）；`screenshot-agent-tap-on-14-finalize-after-action-1-2ecfa6ea86ad.png`（Ideas 首屏）；`screenshot-agent-input-text-20-finalize-after-action-1-dfa94f79bfec.png`（空搜索框）。后三者同 screenshots 目录。原始 UI 锚点：`artifacts/ui-snapshots/ui_snapshot-agent-tap-on-8-prepare-before-action-1-23192bc7c118.json`、`...-8-finalize-after-action-1-59e67f1e84be.json`、`artifacts/tools/000019-ui_snapshot.json`。

**具体修复与未来验证。** SN-040（P1，FSQ driver + navigation Skill）：在 S2 的 `tap_on/_selector` 流程确认目标位于当前可交互前景；保留原始树但把离屏/遮挡/未展开容器证据暴露给调用者，不粗暴删掉所有 drawer 节点；模型必须先打开 Sidebar 再定位 notebook，检查页标题后开始计数。计数采用 folder 内有明确边界的过滤结果或去重遍历，未见终点不报总数。结合 SN-B，避免盲点与反复恢复消耗搜索 write。`PromptModelBuilder.build_task_prompt` 明确用户的 number-only 约束，成功时供 `select_main_answer` 的 summary 必须是该用户答案，而不是格式良好的过程总结；当前未核实则保持不猜。未来覆盖 drawer 隐藏/展开、普通 note 与 to-do 混排、跨页重复和缺失尾页、数值输出格式；不把本例可见三条写成预置答案。源码依据 S2、S4、S6。

**已闭合/剩余未知。** producer只取唯一main step4的解释summary，不能从其它payload提取数字替换；冻结proto COUNT期望3是事后判据，不向模型补答案。actualDB/可见全集和实际点击坐标未存，永久unknown。

## 案例 041 — OpenAppTaskEval

交叉核对：已核对。S10显式kill Contacts、invoke passed/audit19 attempted20 succeeded，非默认Camera；初始Camera由_primary_app_id:97–105取app_names首项造成的映射缺陷独立。业务达成后前台破坏主强推断，缺kill后activity；改生命周期需批准新合同，不移动旧取样边界。

已取得的源码级交叉核对：已收到harness owner官方foreground规则，并直接核对H1；本次stop后activity未留存。

**目标与原分。** 打开 Contacts，若有 pop-up 则授予所需权限并清除；官方 0。没有要求新增联系人，也没有要求为截图额外弹出权限窗口。

**实际序列。** `request.json.appId` 是 **com.android.camera2**；ev19 launch_app(null) 的执行结果也回报该包，说明默认映射错误是事实。ev23 改用 `com.google.android.contacts`，随后仍从 launcher 经 swipe、ev31/step6 tap Contacts 进入应用。ev35/step8 点击 `og_tooltip_scrim_view` 清除 startup tooltip；ev37/step9 `assert_with_ai` passed，截图确有 Contacts tab、Search contacts、create-contact `+`，无阻挡 pop-up。ev39–40/step10 **显式 kill com.google.android.contacts** 成功，audit19–20、ee153。没有后续 reopen。6/10 write，所有工具 passed，native 最终 failed，因为“已打开”的终态被 teardown 破坏。

**首次偏离／直接失败／根机制。** 首次可证的配置偏离在任何业务操作前：Contacts 任务的默认 appId 是 Camera；该问题已被模型经 launcher 恢复，不能把它单独当官方 0 的直接原因。最终致败偏离是 step10 的 app_stop。**事实**：前台 Contacts 曾可用、目标包确被成功 stop；**强推断**：这导致 evaluator 取样时不再是所需 app。缺少 kill 后截图/foreground dump，不假装视觉亲见离开；native verifier 也据成功 kill 而非 kill 后图判 failed。S1 的强制 kill 与 public open-app 目标冲突，是可直接定位的集成合同缺陷，不是模型随意退出。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-68d6aa97ba99.png`（launcher）；`screenshot-agent-tap-on-6-finalize-after-action-1-d4040711df44.png`（Contacts）；`screenshot-agent-assert-with-ai-9-invoke-assert-with-ai-1-cedd77d624a5.png`（清理后的主屏）；`screenshot-agent-kill-app-10-prepare-before-action-1-9a0ce788c1b2.png`（仍是 kill **之前** 的 Contacts）。启动 tooltip 见 `artifacts/tools/000008-ui_snapshot.json`；kill 目标和 passed 见 execution step10.invoke.metadata.harness_output。

**具体修复与未来验证。** SN-041a（P1，producer）：修正 OpenAppTaskEval 的 app-name→package 映射，不能 fallback 到 Camera；保留公开 app 名与映射结果作为请求一致性证据。SN-L（P0）由 coordinator 明确终态保留和清理边界，再更新 S1 与 `FsqAgent.run_in_context`（S5）对应的终态/资源清理合同；一般生产任务结束释放 harness 资源，不应该无条件杀死用户刚要求打开的 app。SN-A（P1）让 `launch_app` 证明前台包，而不是“发起启动即 passed”。未来分别验证错误默认映射、tooltip/所需权限、已经打开的 Contacts、主执行后到提交时的前台身份；不能只把 kill 前截图当验收。

**已闭合/剩余未知。** 官方foreground规则及初始Camera映射来源已闭合，kill显式Contacts不是默认Camera；评分activity/kill后图未存，永久unknown。任何生命周期改动须新合同授权，不改旧取样时点。

## 案例 044 — OsmAndTrack

交叉核对：已核对。一点草稿、未后两站/未Save是直接差距；official读net.osmand/files/tracks直接子文件trk/trkseg/trkpt，序列经纬度每分量<0.001，不查track_name/不要求驾车规划。已有地图资格+地形地名，不归缺图；无最终GPX字节，不猜错格式/路径/空文件。

**目标与原分。** 在 OsmAnd **保存** track，waypoints 必须按 Schönberg, Liechtenstein → Triesen, Liechtenstein → Bendern, Liechtenstein；官方 0。搜索命中、地图标记、route 草稿、单个当前中心点，都不等于已保存的有序 track。

**实际序列。** ev19/23 launch 后仍经 launcher；ev31/step6 tap OsmAnd。ev35 menu → ev41 Plan a route → ev45 Create new route，进入 `points:0` editor。ev51 search，ev57 输入 Schönberg；`000019-ui_snapshot` 报 5mi 无结果，ev67 increase radius 后 10mi 仍无；ev71 输入含国家的字符串，ev77/step22 点到 **Liechtenstein / Country**，不是第一个 waypoint。ev83/87/91 Back 回 editor，仍 0 point。ev99/101 再搜 Schönberg，ev107/step33 选中 `Mountain peak, Near Mittlervalorsch, Triesenberg`，仅显示 POI sheet；ev113/117/121 三次 Back 退出 sheet/search，仍 points:0。ev127/step41 Add 才令 `000054-ui_snapshot` 变 **points:1**。ev133/step43 的最终 AI 断言明确 failed；ev135/step44 kill 成功。没有输入 Triesen/Bendern 的动作，没有 Done/save 的动作。23/120 write，deadlineExceeded=false；全 run 约 300 秒，business budget 7320 秒。

**首次偏离／直接失败／根机制。** 早期搜索受当前位置/半径影响是观测事实，不能据此认定地图未安装或环境无法完成。首个明确的语义不闭环是“选中 POI 后退出搜索但未确认其进入 track”（step33→35/37/39），`points:0` 证明 **查看 place ≠ 添加 waypoint**。Country 选择可能用于重定位，不能武断称为不可恢复错误。最终直接失败是模型在一个点草稿上结束，没有有序三点和保存。**事实**：不是 action-budget 耗尽、不是记录到的 deadline；“execution window”只来自主 runner 自述，不能升级为外部 timeout。**强推断**：主决策没有用 route 点数/有序名单作为每次添加的 milestone，搜索/返回动作均 passed 却不推进目标；引擎没有阻止任何加点/保存，verifier 的失败判定正确。**未知**：唯一草稿点的准确坐标/是否完全等于选中 POI、实际 GPX 内容；地图上的 Schönberg 标签不能证明已存 waypoint 语义。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-87ff622a69dc.png`（启动 splash）；`screenshot-agent-tap-on-22-finalize-after-action-1-e260ff3bcea7.png`（Country sheet）；`screenshot-agent-tap-on-33-finalize-after-action-1-dd23e6ebc630.png`（Schönberg POI）；`screenshot-agent-assert-with-ai-43-invoke-assert-with-ai-1-98108de07bf2.png`（Plan a route，points:1）。UI 原始对照为 `artifacts/tools/` 下 `000027-ui_snapshot.json`、`000029-ui_snapshot.json`、`000041-ui_snapshot.json`、`000044-ui_snapshot.json`、`000051-ui_snapshot.json`、`000054-ui_snapshot.json`。ee682 是最终 assertion failed。

**具体修复与未来验证。** SN-044（P1，FSQ preplan/Android navigation guidance）：在 S4 的路线类计划明确区分 search-result→POI selection→route point addition→Points 列表核对→保存确认；使用当前真实控件，不凭 Add/Marker 的同名按钮猜作用。每次添加后必须确认点数递增且 Points 顺序对应用户列举地点，发现 points 不变则修复当前导航语义而非继续 Back 循环；第三点后执行当前 UI 的 Done/save，再从 saved track details 核对，而不是把地图标签当 track。风险：route geometry 与 GPX waypoint 不是同义，实际应用保存格式需 harness 确认，不能把 editor points 硬等同官方 waypoint。未来验证三种同名 place、Country 重定位、POI 未加入路线、route draft 未保存、逆序点和保存后 details；不要求增预算或让 assertion optional 掩盖失败。源码依据 S1–S5，实际缺陷属于 main model/navigation，而非 producer 预算或 verifier。

**已闭合/剩余未知。** 官方轨迹为tracks直接子文件的trk/trkseg/trkpt坐标序列，每分量容差<0.001，不检查名称/驾车模式；不能把route editor一点当已保存序列。原最终GPX未留，永久unknown，不猜文件格式、路径或空文件，亦不probe。

## 案例 081 — SimpleSmsReply

交叉核对：已核对。号码正确但input/Send未派发；Google Messages非默认不等Simple SMS角色错误，kill尾部亦拒。

**目标与原分。** 在 Simple SMS Messenger 给 `+18407874306` 回复完整指定文本 `Yoga class every Tuesday and Thursday at 6 PM.`；官方 0。必须正确 recipient、输入正文并发送；打开对应 conversation 不够。

**实际序列。** ev19 launch(null)、ev23 explicit launch、ev25 kill、ev27 launch 后仍在 launcher；这些重复生命周期都是计数 write。ev31 swipe，ev39/step9 误点 launcher 的 **Messages**，出现“make it your default SMS app”的 Google Messages 页面；它不是要求的 SMS Messenger。ev43 Home、ev45/49 swipe、ev53/step16 tap **SMS Messenger** 才进入正确列表。ev59/step18 打开正确号码；ev63/step20 单独点 composer，消耗第 12 个 write。ev65/step21 输入被拒（audit41，ee328），ev67/step22 **同样输入再次被拒**（audit42）；ev69 assert_visible 找不到新正文；ev71 kill 也被拒（audit45）。12/12 admitted；没发生成功 input，也没发生 Send tap。

**首次偏离／直接失败／根机制。** 首个明确错误 app 选择是 step9 Messages，不把前面的 launcher 观测直接解释为包未安装。直接失败是写入正文前预算耗尽，最终仍只有原 book-club 来信、空 composer、disabled send。根机制是启动/清理重复 + 错 app 恢复 + 多余 composer tap 挤占已知有限 write；S2 的 input_text 已会 click，因此额外 tap 在此确实无必要。S6 正确在转发前拒绝，没有“文字输进去了但 UI 未刷新”；模型在硬预算拒绝后重试是第二个可定位缺陷。预计划 recipient/body/send 三步本身没有遗漏；verifier failed 正确，producer 没把主 runner 的 inconclusive 当成功。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-6e03b5aed598.png`（launcher）；`screenshot-agent-tap-on-9-finalize-after-action-1-b78e3c555242.png`（错误 Messages/default 提示）；`screenshot-agent-tap-on-18-finalize-after-action-1-67fa946e556a.png`（正确 conversation）；`screenshot-agent-assert-visible-23-prepare-before-action-1-7fbee0e4838f.png`（仅旧来信、无新回复）。`artifacts/tools/000022-ui_snapshot.json` 与 execution step21 的 invoke failure/before-after 相同 UI hash 互证。

**具体修复与未来验证。** SN-081（P1，FSQ Android Skill/tool runtime）：在 S1/S2 上执行 SN-A/SN-B；按明确包/label 区分 Google Messages 和 SMS Messenger，启动失败不反复 kill/launch；直接对已定位 composer 调 `input_text`，硬预算耗尽终止写路径而不重试。保留固定 12 write，不能借移除必要最终清理来“挤出”发送；若正确主路径+合同清理确实超额，应由 coordinator 判定预算合同不匹配。未来在 launcher 中两种短信 app 同时存在、默认 role 提示、最后 write 恰好用尽等场景核对 recipient→draft→send 事件和拒绝前后状态；绝不自动重发以防重复短信。源码依据 S1、S2、S6。

**待 harness 问题。** 是否已有 SMS foreground 启动的原生原因定位？本例发送未发生已可证明，不应混入 082/084/085/086 的 UI/official 分歧集合。

## 案例 082 — SimpleSmsReplyMostRecent

交叉核对：已核对。确发；recency仅业务识别风险、非额外oracle谓词。actual kill目标SMS已证，sent AND foreground中前台冲突为主强推断；评分row/activity缺失永久保留。

**目标与原分。** 对 Simple SMS Messenger **最近收到的**文本回复 `A quick brown fox.`；公开目标没有给 recipient 号码；官方 0，native success。冻结 params 只能用于事后解释，不能把号码回灌成模型答案。

**实际序列。** ev19/23 launch 后通过 ev25/33 swipe、ev39/step8 tap SMS Messenger 进入 app；`000012-ui_snapshot` 首行 `+17594820731 / The early bird catches the worm. / 15:34`，其余来信显示同一分钟。ev43/step10 打开此行；ev47/step12 input exact正文，ev49 assert_state composer passed；ev51/step14 点 Send；ev53 snapshot、ev55 message_body exact、ev57 thread_success、ev61/step18 AI 均通过。最终画面有右侧正文、checkmark、空 composer；ev63 kill 成功。audit 的 input23/Send27/kill37（均 succeeded），9/12 admitted，无拒绝、无 deadline。

**失败链分层。** 选首行有recency依据，分钟精度不足是业务识别风险，不是独立官方谓词。input→Send→body/checkmark→空composer已证发送UI；后续actual SMS kill已证。官方sent(number/body/window) AND foreground契约下，cleanup破坏前台为主强推断，缺评分瞬间activity/row不升级为已测；不捏造未发送、kill删短信或角色错误。send→eval47.604s非执行超过5min，provider.date/device now仍未留存。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-979d7ed72cba.png`；`screenshot-agent-tap-on-10-finalize-after-action-1-9f15fca74721.png`（原来信/号码）；`screenshot-agent-input-text-12-finalize-after-action-1-a9076f62b999.png`（draft）；`screenshot-agent-assert-with-ai-18-invoke-assert-with-ai-1-f61ce6f85eb0.png`（已发出气泡和 checkmark）。`artifacts/tools/000018-ui_snapshot.json` 及 step14.finalize 的 `ui_snapshot-agent-tap-on-14-finalize-after-action-1-d5a806b23f81.json` 记录后态。主 runner summary 是发送陈述，不是评分证据。

**具体修复与未来验证。** SN-082（P1，FSQ preplan/verification）：在 S4 最近消息计划中区分 incoming 与最近更新 conversation，只在可观察时间/排序语义足以确定时声明“most recent”；保留选择所据证据、若同分钟不可辨则报告范围，不凭隐藏号码断言。评分归因采用 SN-D（P0，harness），逐例核对实际 scorer query 是否找到了对应 outgoing 行；在这个条件解释前不改发送代码、不重发、不放宽 latest 规则。未来验证 incoming/outgoing 混排、同分钟/不同时区、明确 recipient 的已发送后态与 provider 一致性；只向模型提供公开 UI/正常应用信息。源码依据 S2、S4、S5、S6。

**永久未知。** 实际评分sent row/activity/role未记录，不补probe；recency只为业务识别非独立oracle谓词，不再要求评分器额外latest分支。

## 案例 084 — SimpleSmsSend

交叉核对：已核对。confirm/body/checkmark/空composer支持已发，不写provider未提交已证；actual SMS kill前台冲突主强推断，评分row/activity缺失。

**目标与原分。** 给 `+16597910719` 发送 `Beauty is in the eye of the beholder.`；官方 0，native success。

**实际序列。** ev19/23 launch、两次 drawer swipe 后 ev37/step8 打开 SMS Messenger，初始“no stored conversations”。ev41/step10 new conversation；ev45/step12 输入号码；ev49/step14 confirm recipient；ev53/step16 输入 exact message；ev57/step18 **Send**；ev59 snapshot；ev61/63/65 分别断言 recipient、exact `thread_message_body`、`thread_success`，全部 passed；ev67/step23 kill 成功。audit23/27/31/35/45 依次对应 recipient input/confirm/body input/send/kill；11/12 write，没有预算或运行异常。

**失败链分层。** recipient/body/confirm/Send UI无可证偏离，draft已变右侧body/checkmark且composer空；遗漏发送、预算挡发送均不成立。actual SMS kill在官方sent AND foreground条件下构成前台冲突主强推断；缺评分activity/row不称已测postkill或provider未提交。send→eval34.374s排执行>5min，不替代provider.date/device now。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-e07d05f9520f.png`（launcher）；`screenshot-agent-input-text-12-finalize-after-action-1-ba3e25ecbe9d.png`（号码输入）；`screenshot-agent-input-text-16-finalize-after-action-1-2ece70495c2a.png`（draft）；`screenshot-agent-assert-visible-22-prepare-before-action-1-611c84bd063d.png`（correct header、sent bubble/checkmark、空 composer）。`artifacts/tools/000021-ui_snapshot.json` 与 `ui_snapshot-agent-tap-on-18-finalize-after-action-1-aafd2a1d5de8.json` 是发送后 XML。ee358 是 kill 成功，不是短信 provider 删除证据。

**具体修复与未来验证。** SN-084复用SN-L一般末态合同，资源close不等app_stop，不能私自提前评分或重开。SN-D未来仅在批准验证保留实际row/type/body/time/foreground等私有诊断，FSQ区分UI ack/持久化/official；本轮未记录的值永久如实unknown，不要求补probe。不改正确正文、不盲重发、不提高预算。

**永久未知。** 本次actual sent row/type/address/time及activity未记录，不能补取或猜provider未提交；未来获授权验证才补私有诊断。

## 案例 085 — SimpleSmsSendClipboardContent

交叉核对：已核对。真实Paste并发送，12/12无denied，不把无剩余写等同拒绝；actual SMS kill前台冲突主强推断，评分row/activity缺失。

**目标与原分。** 把**已有 clipboard 内容**发给 `+15459061746`；公开目标未给正文；官方 0，native success。必须证明来源是 clipboard，不能从 frozen params 读出一句话再 input。

**实际序列。** launcher→ev37/step8 SMS Messenger→ev41 new conversation→ev45 输入号码→ev49 confirm。ev53/step16 对 composer long_press，ev55 snapshot 显示系统 **Paste** 菜单；ev57/step18 tap Paste；ev59/`000021-ui_snapshot` composer 出现 `I think, therefore I am.`。没有对正文调用 input_text 或先写 clipboard 的动作。ev61/step20 Send；ev63/`000023-ui_snapshot` 显示同文 `thread_message_body`、thread_success、空 composer；ev67/69 recipient/body 可见断言、ev71/step24 AI 均通过；ev73/step25 kill 成功。audit31/35/39/49 分别 long_press/Paste/Send/kill；12/12 admitted，但 **无 denied**，不能把“到达预算上限”错写成“超额导致失败”。

**失败链分层。** Paste→新composer内容→同文outgoing bubble是真实来源链，非私有答案回填；没有粘贴错/仅草稿/预算挡kill证据。actual SMS kill与官方foreground条件冲突为主强推断；send→eval50.869s排执行>5min，但provider.date/device now、role/sentrow/activity本轮未留，永久unknown，不说已测postkill或剪贴板被覆盖。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-d4d5a2f932b2.png`；`screenshot-agent-long-press-on-16-finalize-after-action-1-2494faf6df31.png`（Paste menu）；`screenshot-agent-tap-on-18-finalize-after-action-1-2016eb88ccc1.png`（Paste 后 draft）；`screenshot-agent-assert-with-ai-24-invoke-assert-with-ai-1-96f5d984c925.png`（sent bubble/checkmark、空 composer）。另有 `artifacts/tools/000019-ui_snapshot.json`、`artifacts/tools/000021-ui_snapshot.json`、`artifacts/tools/000023-ui_snapshot.json`和 `ui_snapshot-agent-tap-on-20-finalize-after-action-1-31012869b49f.json`。ee391/392 记录 kill invoke 成功。

**具体修复与未来验证。** SN-085（P1，FSQ evidence；P0，harness score attribution）：`VerificationEvidenceBuilder.build` 对 clipboard-origin 任务保留 **来源动作链**（long-press/Paste → observed inserted text → send ack）而非只留最终气泡；producer/私有诊断将初始化 clipboard 与 post-paste/send 记录的 hash/一致性结果关联，不把 secret clipboard 或 hidden expected text输入模型。执行 SN-D 对本例 outgoing 持久性和 scorer 条件核对。在已有正确 Paste/send 证据下，暂没有正当的重新复制正文或额外发送修补。未来验证 clipboard 非空/多行/特殊字符、来源被中途改变、Paste 与手输同文的区别、精确 12 write 全成功的边界。源码依据 S2 的 long_press_on/input_text、S5/S6。

**永久未知。** 初始化clipboard系统快照及评分provider row/activity未留；真实Paste来源与发送UI已证，不拿seed params代底层事实，不补probe。

## 案例 086 — SimpleSmsSendReceivedAddress

交叉核对：已核对、有实质oracle修正。来源身份保留属于业务/main-verifier分歧，不是独立评分分支；sent(number/body/window) AND foreground，actual SMS kill前台冲突主强推断。

**目标与原分。** 从 Oscar Mohamed 刚发的消息取得 event address，转发给 Gabriel Ibrahim；官方 0；主 runner businessStatus **inconclusive**，native verifier **success**，必须保留两者分歧。

**实际序列。** ev19/step1 launch 后保留的是 **Add to contacts 未保存表单**：Oscar / Mohamed / +1 437-996-9633；不能把它称为“已经保存的 Oscar 联系人”。ev23 Back，ev27 explicit launch，再经 launcher 搜 `SMS`（ev39/step9）与 ev43 tap SMS Messenger。ev47/step13 打开 `+14379969633`，`000016-ui_snapshot` 来信正文为 `789 E Oak St, Phoenix AZ 85006`，15:34；ev51 Back。ev55 new conversation；`000020-ui_snapshot` 真实显示 Gabriel Ibrahim 及 `+19696338338`。ev61 Back 后 ev65/step21 点击 Gabriel Ibrahim，实际进入同名 header 的 conversation；ev71/step23 输入从来信抄取的 address，ev73 assert_state passed，ev75/step25 Send，ev79/step27 AI 确认右侧气泡/checkmark/空 composer；ev81/step28 kill 成功。14/18 write、无失败/拒绝/deadline。

**三层分离。** ①公开业务provenance：Oscar未保存表单+同号码incoming支持来源关联，但不证明持久联系人；②main attribution inconclusive与verifier success分歧原样保留；③官方sms.py:173–243继承SimpleSMSSendSms无override，联系人仅initialize:216–239，sms_validators:255–276只sent(number/body/window) AND foreground。来源姓名/绑定不是独立扣分项，删除旧候选。actual SMS kill为前台冲突主强推断；send→eval40.386s排执行>5min，不代provider.date/device now。role/sentrow/activity原证据缺失永久保留，不把Oscar未保存直接解释0。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-0edc5632f9ee.png`（未保存 Oscar 表单）；`screenshot-agent-tap-on-13-finalize-after-action-1-e248a00cc2f9.png`（源号码和 address）；`screenshot-agent-tap-on-21-finalize-after-action-1-0b262599ccf0.png`（Gabriel conversation）；`screenshot-agent-assert-with-ai-27-invoke-assert-with-ai-1-af55b5f8a3e5.png`（sent）。`artifacts/tools/000002-ui_snapshot.json`、`artifacts/tools/000016-ui_snapshot.json`、`artifacts/tools/000020-ui_snapshot.json`、`artifacts/tools/000026-ui_snapshot.json` 为相应结构化证据；发送后 XML 位于 `artifacts/ui-snapshots/ui_snapshot-agent-tap-on-25-finalize-after-action-1-46e8c4a70c60.json`。

**具体修复与未来验证。** SN-086保留公开业务provenance以及main/verifier来源置信分歧，不擅自保存联系人、不回填hidden号码。官方生命周期用SN-L，归因用SN-D现有sent+foreground而非联系人评分分支；未来获授权才保留row/activity诊断并覆盖draft/同名/多号码/多行地址，禁止盲重发。用户业务证据充分度与official既有谓词分开。

**已闭合/剩余未知。** oracle不评分Oscar来源姓名或绑定，不能再追问其为独立扣分分支。未保存表单缘由属于业务环境证据缺口；本轮官方row/activity/role值未留存，永久unknown、不probe不重发。

## 案例 097 — SystemBrightnessMax

交叉核对：已核对。0→65469、AI近满通过与exact255不等价，visual goal收窄；系统实读整数/SeekBar映射未留，永久unknown，不补probe不猜254。

已取得的源码级交叉核对：harness owner已核对min初始化、exact255规则与0→65469轨迹；本次system实读值仍缺。

**目标与原分。** brightness 到 max；官方 0、native success。目标是亮度设置达到最大，不是仅“滑条看起来满了”。

**实际序列。** ev19 launch Settings 后仍见 launcher；ev23/step3 下拉，ev31/step5 再下拉展开 Quick Settings。`artifacts/tools/000006-ui_snapshot.json` 的 `com.android.systemui:id/slider` SeekBar text 是 **0.0**，bounds `[42,357][1038,483]`。ev37/step7 从 `(90,420)` 拖到 `(1037,420)`，1080×2400；ev39/`000009-ui_snapshot` 变 **65469.0**。ev41/step9 AI assertion passed=true/confidence=0.99，称 fully filled；ev43/step10 默认 kill，invoke 回报 `com.android.settings`。5/10 write，无拒绝。generated verification_goal 为 **“The Android brightness control visibly shows its maximum value.”**，较 public 设置目标偏向外观；verifier 最终接受此视觉证明。

**首次偏离／直接失败／根机制。** 第一个可定位的可疑决策是用接近控件右边界的坐标当“exact max”而不读确定性端点；后态 65469 与 098 实际观察到的 65535 不同。**事实**：拖动确实从低值升到高值，图上几乎满；不能从像素证明精确设置值。**强推断**：手势末端略不足/控件映射量化导致未到真实端点，AI“满”产生假阳性，加上 generated goal 只要求外观，使 native success 漏掉精确量值。**未知**：执行时持久化 `screen_brightness` 实际值；UI 约 0..65535 的显示量表不等于 Android 系统约 0..255 的存储量表，绝不能把 65469 直接解释成 system=255，也不能自行换算成254。H1冻结官方规则已确认：system max必须exact255，097初始化min；这支持“近满仍0”的解释，但实际系统读值未保留，不能伪造读取或换算。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-29ed04d55481.png`；`screenshot-agent-swipe-5-finalize-after-action-1-493138997922.png`（最小位置）；`screenshot-agent-swipe-7-finalize-after-action-1-dde4e4473cfd.png`（近满）；`screenshot-agent-assert-with-ai-9-invoke-assert-with-ai-1-f1e19a8e65d1.png`（外观近满）。数值证据来自上述 XML，不是由这些图精确读出。

**具体修复与未来验证。** SN-097（P1，FSQ driver/Skill + preplan）：S3 `swipe` 不应给出“业务端点已达成”的含义；用当前真实 slider bounds 和屏幕范围选择可饱和到端点的手势（末点可越过控件实际轨道但仍在屏幕内，而不是恰取 bounds.right−1 后宣称 maximum），随后用当前公开可见 range/current 等确定性信息验证；若 backend 不能暴露范围，则扩充已有 `ui_snapshot/assert_state` 的通用控件 range 证据，再允许精确 max 成功，不能仅凭 0.99 AI。S4 保留“设置达到最大”的最终目标，不退化成“看起来满”；S5 若只能证明外观则标证据不足。系统 persisted setting 的官方私有验证由 harness owner 留回执，不能给模型 oracle 值。未来验证低→max、端点量化、不同分辨率/滑条 padding、UI与系统不同量表以及 kill 后设置持久性；现分数不改、不放宽 exact max。源码依据 S3–S5。

**永久未知。** 本次系统实读整数及SeekBar映射没有记录，不能补取或猜254；只列未来授权验证，不要求harness补不存在的原证据。

## 案例 098 — SystemBrightnessMaxVerify

交叉核对：已核对。初始max+65535→65338是不必要倒退；main success/verifier inconclusive保留。幂等不写+range数值验证，不强迫verifier pass；系统实值永久unknown。

已取得的源码级交叉核对：harness owner已核对max初始化、exact255规则与65535→65338轨迹；本次system实读值仍缺。

**目标与原分。** public goal 与097相同；官方0、主 runner success、native verifier **inconclusive**，不是 failed也不是通过。

**实际序列。** launch→两次下拉；`000006-ui_snapshot` 在任何亮度调整前已显示 **65535.0**，同样 bounds `[42,357][1038,483]`。ev37/step7 仍从 `(540,420)` 拖到 `(1035,420)`；`000009-ui_snapshot` 降为 **65338.0**。ev41/step9 AI断言依旧 passed/confidence0.99；ev43默认 kill Settings成功。5/10 write、无 denied/deadline。事后 verifier 看到 before65535/after65338 的冲突，拒绝给出成功，但保持 inconclusive，因未见确定的系统量值。

**首次偏离／直接失败／根机制。** 和097不同，**首个明确可证的退步就是 step7 的无必要写入：已在较大端值的控件被拖小**。H1冻结官方源码确认本例初始化max，097初始化min；这与UI before值互相支持，但不把初始化安排代替最终系统读回。直接失败是没保持精确 max，官方0。强推断根因是无“先验状态已满足则不改动”的幂等分支，近似坐标破坏原有满足态，再由视觉断言假阳性掩盖。native verifier 识别冲突是有效防护，不应通过改 prompt 强制 success 消除分歧。UI0..65535与system0..255不能混同，实际系统值仍缺。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-83ea28d3cefc.png`；`screenshot-agent-swipe-5-finalize-after-action-1-f48a91a369dc.png`（调整前已满外观）；`screenshot-agent-swipe-7-finalize-after-action-1-e841fef175b9.png`；`screenshot-agent-assert-with-ai-9-invoke-assert-with-ai-1-e858366b38a7.png`（调整后仍几乎满）。数值65535→65338由 XML 证明，像素不能可靠区分。

**具体修复与未来验证。** SN-098（P1，FSQ main planning/Android controls）：先读当前状态，若在公开可确认的 max 则不执行 swipe；否则执行 SN-097 的端点设置与确定性验证。`GoalPrePlan` 在S4生成的是状态目标，不应一律转成“必须再拖一次”的动作模板；`VerificationEvidenceBuilder.build` 在S5保留 before/current/range/changed 标识，冲突数值优先于近似视觉 verdict。风险：65535 只能作为本控件实际观测值，不硬编码为所有 Android slider 的最大值。未来专测初态已max时零亮度write、初态min时设置、焦点位置/端点误差和AI满格但数值非max。harness补执行时system exact读值，不换评分尺度。源码依据S3–S5。

**永久未知。** 本轮评分时system实值未记录，不补测；保留runner success/verifier inconclusive，不统一成模型错误。

## 案例 113 — TurnOnWifiAndOpenApp

交叉核对：已核对。Wifi checked与Settings可见两链、actual Settings kill双方一致；wifi1/app0仍强推断无分项。then顺序及verification_goal漏WiFi是独立计划质量缺陷。

已取得的源码级交叉核对：harness owner已接受Settings kill目标证据及两分平均规则；Wi-Fi=1/foreground=0的分解仍为强推断。

**目标与原分。** **先开启 Wi-Fi，再打开 Settings**；官方 **0.5**。必须分开两个子目标，不因 native failed 抹去已完成部分，也不能把 Internet tile On 等同 Wi-Fi On（移动数据也能让 Internet On）。

### Wi-Fi 子目标

- ev19 launch(null)；`request.json.appId=com.android.settings`，首图仍在launcher。ev23/step3下拉，ev29/step5点Internet。`artifacts/tools/000007-ui_snapshot.json` 明确 **Wi-Fi is off**，T-Mobile mobile data connected；这是Wi-Fi的初始状态，不是“Internet On所以无需操作”。
- ev33/step7点 `com.android.systemui:id/wifi_toggle`；ev35–36/step8 `assert_state` checked=true且invoke.harness_output `{"checked":true}`，audit15–16；随后Done。**事实**：Wi-Fi toggle已开启；没有要求或证据证明连上某SSID，不添加联网验收。

### 打开 Settings 子目标

- ev39/step10、ev45/step12下拉展开Quick Settings；ev51/step14点 `settings_button_container`。ev53/step15 snapshot，ev55–56/step16 assert_visible `com.android.settings:id/settings_homepage_container`通过；实际图是Settings主屏。
- ev57–58/step17 **kill_app({})**。原始execution step17.invoke.metadata.safe_replay_params={}，**harness_output.app_id=com.android.settings**；audit33–34成功，ee266/267成功。S1的driver以request配置包作为默认，因此不是杀SystemUI、不是只释放连接，而是确实stop Settings。其后无reopen。9/20 write，无预算/时间拒绝。

**首次偏离／直接失败／根机制。** Wi-Fi开启链没有可证失败。对open-app终态的明确致败偏离是step17，沿SN-L解释：主执行按Skill取最终证据后杀app，正好破坏用户要求保留的foreground app。**事实**：kill目标/成功已从完整invoke与workerRequest双重核实；**强推断**：评分半分对应Wi-Fi成功+foreground失败，H1中两分平均与foreground检查的冻结源码与此吻合；尚无kill后截图，不把before图误当post图。

另有独立计划质量缺陷：`R/report.json.task.verification_goal`只有 **“The Settings app's main screen is visible.”**，省略Wi-Fi。S4没有覆盖性校验，S5只检唯一生成目标，因此native最终failed只说明Settings终态，没有完整表示两子目标。这不是Wi-Fi实际没做，也不是0.5可被改写成0或1的理由。主runner的success.summary还限定“visible before teardown”，不能当任务最终成功。

**实际查看的截图。** `artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-f86ff3f866ba.png`（launcher）；`screenshot-agent-tap-on-7-finalize-after-action-1-4ccdaac6a2e6.png`（Wi-Fi已勾选/on）；`screenshot-agent-assert-visible-16-prepare-before-action-1-07af7c787c50.png`（Settings主屏）；`screenshot-agent-kill-app-17-prepare-before-action-1-fb85230fa88d.png`（kill **前** Settings）。Wi-Fi assertion原始XML：`artifacts/ui-snapshots/ui_snapshot-agent-assert-state-8-prepare-before-action-1-e948b204dcf5.json`。

**具体修复与未来验证。** SN-113a（P0，coordinator+FSQ lifecycle）：执行SN-L，明确业务终态与破坏性teardown边界；生产任务应在完成Wi-Fi操作后保留所请求Settings app，用资源close释放会话；若既定评估合同仍必须kill，先由coordinator明确互斥的实验合同并显式报告冲突；不得提前评分、不得清理后重开目标再评分，**本调查不建议私自禁用kill来拿分**。SN-113b（P1，FSQ preplan/core）：在`PRE_PLAN_AGENT_INSTRUCTIONS`及`FsqAgent._augment_goal_only_task_with_pre_plan`建立原公开目标约束覆盖检查，最终一个字符串也须表达“Wi-Fi enabled且Settings最终visible，动作顺序满足then”，而不是只保留最后一个动作；不能让verifier去猜遗漏的Wi-Fi。未来分别验证Wi-Fi off→on、已on幂等、仅mobile data On、打开后被kill、业务提交前后前台身份、顺序及两子目标结果；官方原0.5保留。源码依据S1、S3的checked断言、S4、S5、S6。

**永久未知。** 原scalar无分项，wifi1/app0仅强推断；未记录的实际组件值不补probe、不要求补原不存在日志。本轮不测不改分。

## 归因结论与未闭合证据

- 040：隐藏/未展开drawer命中后误入笔记，恢复和搜索耗尽write，未完成全量计数与number-only回答；未知总数不猜。
- 041：默认Contacts→Camera映射错误已观察；最终成功stop Contacts是另一条直接终态破坏链。
- 044：POI/marker、route draft point、保存track三个语义未闭环；只加一处草稿点就自主结束，不能写成预算或deadline耗尽。
- 081：错误Messages app与重复生命周期耗掉预算，正文/Send未成功发生；与随后四例明确不同。
- 082/084/085/086：各自业务来源/确认/Paste/Oscar链不同，但均确有发送UI且actual kill目标SMS；共同官方foreground冲突是主强推断。sentrow/role/activity仍unknown，recency/来源姓名不是额外oracle谓词，不伪称未发送。
- 097/098：前者从低值拖到近max并被视觉假阳性接受；后者初态已有max量值却被无必要写入降低，verifier正确识别冲突。两者UI量表和persisted setting量表必须分开。
- 113：Wi-Fi checked完成；Settings曾打开但随后按Skill被明确stop，原0.5不得丢失；generated verification_goal还遗漏Wi-Fi。

十一例均已收到harness owner逐例正式回执并落盘，事实一致、实质修正、保留与永久unknown分别记录；已核对不等于缺失的评分瞬间状态已实测。所有修复仅未来方案，未增加预算、重发、泄漏私有答案、削弱rubric、改变奖励或触碰设备。
