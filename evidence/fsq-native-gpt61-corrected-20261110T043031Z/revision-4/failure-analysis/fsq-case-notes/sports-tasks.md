# Sports / Tasks 八例原生轨迹离线因果分析

## 范围、证据口径与路径

仅覆盖 **087、090、091、092、106、107、108、110**。八例原始 officialReward 均为 **0.0**，没有改分；不是 101 的 invalid/null，也不涉及其他 partial/passed 案例。此文只记录原生运行的观察与将来修复方案，没有改项目、SDK、配置或旧结果，没有设备访问、ADB、测试、安装、评分或模型调用。文中图片均读取/渲染了已保留的图片文件，不以路径存在代替视觉观察。

`BASE` = `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`（FSQ_AndroidWorld_eval 内）。下文 `E编号` 为该 episode，`R编号` 为真实 native run，`W编号=E编号/raw-private/fsq-native/worker`。所有 step 编号指 `R/execution-result.json.steps[].step_id` 的 `agent-…-N` 后缀，`eN` 指同目录 `events.jsonl.sequence`，`aN` 指 `W/native-action-audit.jsonl.sequence`；它们不是互相可替换的计数。

- `E087` = `next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek`；`R087` = `E087/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-087-20261110T213955Z-895101`。
- `E090` = `next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity`；`R090` = `E090/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-090-20261110T215043Z-1f10e6`。
- `E091` = `next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval`；`R091` = `E091/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-091-20261110T215344Z-372744`。
- `E092` = `next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek`；`R092` = `E092/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-092-20261110T215815Z-5c3801`。
- `E106` = `next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate`；`R106` = `E106/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-106-20261110T223129Z-6dcd59`。
- `E107` = `next-stage-plan/execution/run/episodes/107-TasksDueNextWeek`；`R107` = `E107/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-107-20261110T223419Z-83207a`。
- `E108` = `next-stage-plan/execution/run/episodes/108-TasksDueOnDate`；`R108` = `E108/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-108-20261110T223732Z-c3b1bc`。
- `E110` = `next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate`；`R110` = `E110/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-110-20261110T224320Z-b7af07`。

每例均交读了 `R/sources/000-goal.txt`、`R/events.jsonl`、`R/execution-result.json`、`R/report.json`、`W/fsq-task-result.private.json`、`W/native-action-audit.jsonl`，并读 `E/raw-private/task-initialization.json`、`E/raw-private/evaluator-diagnostics.json`、`E/raw-private/fsq-worker-outcome.json`。原 diagnostics 都是 `outcome=returned, officialReward=0.0, exception=null`；`componentResults.status=not_provided`，不能据此编出逐组件官方失败理由。report 的 `failure_classification="planning issue"` 是本地报告分类，不代替下面的因果拆解。

### 公共机制证据（各例按需引用）

下面 FSQ 文件属于 parent 已按冻结 manifest SHA256 核对一致的 16 个文件，版本 0.1.2，冻结包/source SHA256 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`。没有用未核实的当前源码解释旧运行。producer 文件用的是 **087 episode 保留的 worker-site 原始快照**，而不是当前 harness 源码。

- **S-L（启动成功边界）**：`fsq_agent/drivers/android/_uiautomator2.py::UiAutomator2AndroidDriver.launch_app:95–100` 调 `device.app_start(app_id, **options)` 后直接返回 passed；该函数没有核对前台包/活动。八例观测到的是“返回目标 app_id 但画面仍 launcher”，不能仅凭它推成未安装、崩溃、错误包名或某个 u2 参数默认值。实际 SDK 启动行为由 parent 单独查证。
- **S-O（观察/图片边界）**：同文件 `ui_snapshot:244–277` 返回 compact XML，标注 `coverage.status=partial`/`semantic_compaction`，长属性限 50 字符；`HarnessToolAdapter._format_runner_result:147–183` 和 `_result_summary:185–218`（`adapters/coding_agent/_harness_tools.py`）把 harness_output、artifact refs 和 runner result 序列化为 JSON 字符串。不能把 artifact refs 自动等同于 main 已看过像素。OpenTracks 多个分类图标在 XML 都只是 `content-desc="Track"`；Tasks 的 completeBox 在已读 XML 是 ImageView，不提供 checked，而菜单的 Show completed checkbox 确实提供 checked。不能把这种差异笼统说成“快照都不可用”，更不能断言一定是 compaction 删了状态。
- **S-G（手势含义）**：driver `swipe:163–182` 显式坐标直接下发；`_swipe_points:431–443` 的普通 down 从屏高 25% 到 75%。这些调用成功只证明手势执行，不证明通知栏日期已读取、任务列表已翻页或计数已完成。
- **S-K（Skill 生命周期/断言）**：`resources/skills/android-harness.md:5–10` 要求先 launch、最后 kill；`:14–18` 要求使用当前 UI 的 locator 并检查 stale target；`:23–26,79–80` 规定确定性/视觉断言的使用。这使最后 kill 即使业务已经停止仍会被尝试，但它本身不是业务失败的起点。
- **S-B（预算不是超时）**：`E087/raw-private/fsq-native/worker-site/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch:85–118` 在 admitted 达 maximum 后、转发前拒绝写动作；`:20–26` 明确 launch/kill/tap/input/key/swipe 是写，ui_snapshot/assertions 不算该写预算；`snapshot:134–142` 定义计量单位。`BudgetedAndroidHarness.invoke_action:164–166` 使用同一 dispatch。失败的 admitted 写动作也消耗预约，read/search 次数不能直接当写动作次数。八例均 `deadlineExceeded=false`；091 是 20 admitted/22 attempted/2 denied，其余是 10/12/2。108 另有不计写预算的失败 AI 断言。
- **S-P（计划与公开预算）**：`fsq_native.py` 的预算构造在 worker `fsq_worker.py::execute_worker:168,191–197`；后者创建 Task 只带 goal，不把 maxActions 注入 Task。FSQ `agent/_pre_plan.py::build_pre_plan_input:60–86` 传 reference、tools、knowledge、skills；`DefaultCodingAgentRuntime.run_task:308–315` 调 `_build_task_input(task)`；`_build_task_input:1160–1169` 虽有 runtime_policy 参数，本处没给 producer 预算。**事实**是预算在执行边界，**强推断**是模型/前置计划缺少有效的该次剩余写预算反馈，而不是已证明模型故意无视某个已显示的剩余额度。
- **S-A（答案与状态边界）**：`models/_agent_io.py::AgentFinalOutput:39–50` 有 status、summary、evidence，没有独立 user_answer；runtime `run_task:431–445` 将合规结果记为 `agent_runtime.runner` 的 `StepResult(status="success")`，即使其业务 status 是 inconclusive。保留 producer `fsq_worker.py::select_main_answer:27–57` 仅选择唯一成功 main runner 的合法 `tool_output.summary`；不能拿 verifier summary、evidence 里的候选或隐藏标准答案替换。八例的 `mainAnswer.status=valid` 只是传输/结构有效，业务都 inconclusive。`agent/_core.py::run_in_context:103–110` 在主执行后调用独立 verification；本地 verifier 的 failed 也不是官方 oracle 的分数来源。

时间锚：每例初始化均是 **`2023-10-15T15:34:00+00:00`，UTC**；设备画面显示 `Sun, Oct 15`，有详情显示 2023 年。2026 年宿主事件 timestamp 是审计时间，不能替代 fixture 的业务时间。本周按 Monday 的分析区间是 **2023-10-09…15**，下周是 **2023-10-16…22**；若细分“整周”与“截至现在”，原任务未出现未来记录处理分歧的证据，不能拿这个推测解释已发生失败。

下列hidden/proto只记录harness owner事后判据，用于检验因果，不把fixture ID/答案喂给未来模型。八例最终逐例回执已记录在各节；已核对不等于剩余精度/终态/模型采用来源已实测，保留明确未知。

## 案例 087 — SportsTrackerActivitiesCountForWeek

**交叉核对：已核对（harness owner读完全文后逐例回执）。** 未建立类别/周覆盖、菜单无进展及原动作/预算链双方一致；启动底层原因仍未知，不由此推定设备故障。主summary为Unable，原0不是已提交整数算错。

### 目标与约束

公共 goal 要问 OpenTracks **本周 running 活动数量**，周一开始，答案只能是一个整数。计数对象是活动条目，不是分钟、距离或标题含 run 的条数；同名不应天然合并，不应因一条名称像运动便认定 category。初始化参考周为 Oct 9…15。owner 事后确认 frozen sports proto `COUNT` 的对象是该周 running（其所读 proto:2053–2107）；没有把它当模型可见列表。

### 实际序列与屏幕转换

1. `launch_app-1`（e19）返回 `de.dennisguse.opentracks` passed，`ui_snapshot-2`（e21–22）实际还是 launcher；显式 `launch_app-3`（e23–24）仍是 launcher。`swipe-4` 打开 drawer，`tap_on-6(OpenTracks)` 才进入介绍页；`tap_on-8/10(next_button)` 经过第二张地图说明，进入活动列表。业务起点已经花了 **6 写**，不是“只用了一次 launch”。
2. 列表（step10/11）有 Today、Yesterday、Friday…Tuesday 的活动；可读到 Saturday 的 `Trying and failing to keep up with John`、Friday 的 `Active Rest Day` 等。图片中图标有区别，但其 XML 图标统一为 Track。屏底还在 Tuesday 的 `Skateboard Ride`，没有到本周 Monday 边界，**此屏不能证明周覆盖完整**。
3. `swipe-12(down)`（e45）没有带来业务列表前进；`swipe-13`（e47，起点 y=1）才打开通知栏。e51 的 search_artifact 查 `date`；`assert_state-15`（e53–54）证 `Sun, Oct 15` 存在。这个 assertion 仅证日期，不是活动计数。
4. `press_key-16(Back)` 返回列表；e59 搜索该列表文本。`tap_on-18(More options)`（e61）打开 **Settings/Help**，未得到分类筛选/计数。第 10 写已用完，`press_key-20(Back)`（e65/a39）被 action_budget 拒绝，菜单留在屏幕；`kill_app-21`（e67/a40）亦被拒。
5. main 是 `W087/fsq-task-result.private.json` **step4**：summary 为 `Unable to establish a verified integer count before the harness action budget was exhausted.`；status=inconclusive。verifier step5 说缺 integer/完整 tally；官方 diagnostics 仍独立保留 reward0。

### 首偏离、直接失败、根机制

- **首个可证系统偏离〔事实〕**：step1 的“launch passed”未达到前台业务页，step3重复消耗一写而画面仍相同（S-L）。这是可观测后置条件缺口，不是已证安装故障。
- **业务首个可证无进展〔事实〕**：step12 在首屏向下，没有向旧日期推进；之后 step18走仅含 Settings/Help 的菜单。**强推断**：在分类文本缺失和有限剩余动作下，计划没有尽快选择分类检索/视觉分类加周边界遍历，而把预算花在日期与非业务菜单。
- **直接失败〔事实〕**：a39拒绝 Back，main 没给整数，未完成 running 集合或完整周覆盖。**没有证据**表明已经算错某个整数，也不能从可见两条 running 图标直接断言完整答案。
- 层次：preplan 的“定周界→枚举→计数”方向没错；主 runner 的导航/证据聚合不足，加上 S-L/S-P 放大固定 10 写约束。Skill 要求 kill 导致尾部第二次拒绝，但不应反因果地当成缺整数的原因。未见 provider error、max_turns、deadline 或设备断连证据。

### 修复计划（只计划，不执行）

- **ST-087 / P1，FSQ Agent/Skill owner**：在 `agent/_pre_plan.py::build_pre_plan_input:60–86` 的计划要求和 `resources/skills/android-harness.md:14–26` 落实“计数查询=类别证据+日期区间+覆盖终点”的工作表。category 不在 XML 时明确走可见搜索（需验证 category 搜索语义）或当前截图的视觉分类，逐屏按条目/时间记录，读到早于 Monday 的边界才允许标完整。这样避免依标题猜 running、把日期 assertion 当 tally 或停在 Tuesday；风险是同名条目、图标歧义、过滤并非 category-only，不能以空搜索直接宣称 0。
- **ST-L / P0，FSQ Android driver + harness owner**：在 S-L 的 `launch_app:95–100` 加可观测的目标前台后置状态并准确区分“启动请求已发”与“应用已就绪”，使失败不再诱导重复相同启动；不加盲重试，不擅自放大预算。S-P 把公开 maxActions/计量规则/剩余数送进 runtime_policy 和 preplan，仍由 producer 同一边界强制执行；防止 fixed10 计划把所有业务额外花在非必要往返。风险：permission/onboarding 等前台覆盖须区分，不能把任何系统 UI 都当永久失败。
- **未来验证**：只在另获授权后，以“首启两页+launcher未前台+跨周多屏+同名异 category”的离线 fixture 检查动作计划与覆盖凭证；验证不是把旧隐藏计数注入 prompt。S-A 应在集合完整时把 count 本身写 summary，说明留 evidence；集合未完整时如实 inconclusive，不伪造整数。

### 关键原证据

`R087/events.jsonl:e19–28,e31–42,e45–68`；`R087/execution-result.json.steps[agent-launch_app-1,agent-swipe-13,agent-assert_state-15,agent-press_key-20]`；`W087/native-action-audit.jsonl:a1,5,7,11,15,19,23,25,31,35,39,40`。以下截图已实际查看，路径均相对 R087：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-5d9ac40871b8.png`。
- step10：`artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-fd587eefd6a6.png`。
- step18：`artifacts/screenshots/screenshot-agent-tap-on-18-finalize-after-action-1-5f8e56124ec5.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-21-prepare-before-action-1-4e7b151309b6.png`。

## 案例 090 — SportsTrackerLongestDistanceActivity

**交叉核对：已核对（逐例最终回执）。** mountain-biking类别/MAX候选未建立、计算未执行双方一致；8.09mi不是已提交答案。英制显示精度是未来约束，不是本轮既成算错，原0保留。

### 目标与约束

问本周 **mountain biking** 活动中最长距离，周一开始；输出单一数值、单位米、最后四舍五入到整数。集合过滤应先有 category 与 Oct9…15，再对距离取 **MAX**，不是总和、不是任意 cycling、不是全局列表第一条。owner 事后确认 frozen sports proto:2487–2538 是 MAX 米（oracle 自有 10m 容差，不改变公共的最近整数要求，也不建议放宽标准）。

### 实际序列

1. step1/e19启动 passed→step2 launcher；step3显式启动仍 launcher；step4 drawer→step6点 OpenTracks→step8/10通过介绍和地图说明。进入列表前已用 **6 写**，与087相同而非纯检索10写。
2. step10/11列表已跨到 `8 Oct`、`7 Oct`，当前屏能看见本周与上一周分界。可见 `Scenic Cycling` 有 Tuesday 和 8 Oct 两条同名；`Skill work` Tuesday 的距离以 0.75mi 显示。**这些是原 UI 候选信息，不是本报告替模型给出的答案。** XML 图标仍只是 Track，title 和 cycling 名称不足以区分 road bike/mountain bike。
3. step12/e45从 y=1拉通知栏，step13/e47取快照；e49查 Oct（`artifacts/tools/000017-search_artifact.json` 的完整结果给出 Sun, Oct15）。step14 Back 返回列表，step15再观察。
4. `tap_on-16(Wave Exploration)`（e59）打开 Today/`Oct 15, 2023, 2:09:00 AM`、8.09mi、3:54:00 的详情；该详情没有证实 mountain biking category。之后 step18 Back 回列表，再读若干 list/search/detail artifact，未形成 category候选全集、最大值比较或米计算。
5. `tap_on-20`（e73）准备点 `Scenic Cycling`，含 xpath `[1]` 来区分同名；a39在转发前拒绝。因此不能把这一次算作已检查过 Tuesday 那条详情。step21 kill也拒绝。
6. main在 `W090/...private.json` **step6**，summary=`Unable to determine the maximum distance before the harness action budget was exhausted.`；verifier step7未确认最大值；官方 reward0，不是“8.09mi 已换算后答错”。

### 因果拆分

- **首系统偏离〔事实〕**仍是 step1 passed/launcher 不一致（S-L）。**首业务策略偏离〔强推断〕**是 step16先开列表首条 Wave Exploration，而没有先建立 mountain biking 分类证据；并不能仅据标题/泛化箭头图标绝对证明它是什么其他 category。它既未解决分类，也不能解决 MAX。此判断比“坐标错误/单位换算错误”有更直接的轨迹支持。
- **直接失败〔事实〕**是预算阻断下一条详情且最终不交数字；**根机制〔强推断〕**是有限预算里按全列表逐条探查、缺分类证据→候选比较与单位精度阶段完全未执行，启动/首启成本放大问题（S-L/S-P）。不存在已执行错误四舍五入的证据。
- **单位风险〔事实+推导〕**：列表/详情是小数点后两位 mi；单个0.01mi显示步长约16.09m，直接以显示值乘1609.344不一定能还原最近1m。即使拿了最大显示值，也还需要数值精度证据。此处 model 根本没走到计算，精度是未解决约束，不应倒写为已发生计算错误。
- **覆盖保留**：本屏看到了上一周边界，但尚不证明搜索/其他列表没有遗漏；重复标题必须与所属日期行关联，不能全局 text第一匹配任意取一。

### 修复计划

- **ST-090 / P1，FSQ preplan/Skill owner**：修改 `build_pre_plan_input:60–86` 的检索计划要求（S-P）和 Android Skill 观察策略（S-K:14–26），先显式获取 mountain biking 分类的 UI 证据，固定当前时间区间后只检查候选。构造逐行 `标题+日期+分类依据+距离原文+单位` ledger，按相同单位比较 MAX，明确排除上周同名行；已知category不在XML时用定向视觉查询而非盲点首条。此举避免 Wave Exploration 式无类别详情往返；风险是 category搜索范围未知，需以UI结果验证，不硬编码应用私有分类答案。
- **ST-090-U / P1，FSQ查询计划 owner**：在首次发现 mi 时先评估精度再制定单位获取路径，优先使用应用可见且获准的足够精度米值/展示；如需单位设置导航，应在预算计划中计费、记录是否可恢复。没有足够精度就明确未知，不能把两位mi当精确数。不要更改oracle容差或通过后台数据库读取答案。启动与预算反馈复用 ST-L（S-L:95–100；S-P worker:191–197/runtime:308–315）。
- **未来验证**：授权后用 mountain/road bike混合、跨周同名、多条候选、英制精度边界的离线数据检查分类→MAX→单位→summary；不扩大10写。最终仅在证据闭合后由 S-A 的 summary承载整数，而非把详情任意数字当答案。

关键证据：`R090/events.jsonl:e19–28,e31–49,e59–76`；`R090/execution-result.json.steps[agent-tap_on-16,agent-tap_on-20]`；`W090/native-action-audit.jsonl:a1,5,7,11,15,19,23,27,31,35,39,40`；`R090/artifacts/tools/000017-search_artifact.json`。以下图片相对 R090，均已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-c6629f816e91.png`。
- step10：`artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-9dcc6df9e14c.png`。
- step16：`artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-776920249bac.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-21-prepare-before-action-1-2f590117f5d2.png`。

## 案例 091 — SportsTrackerTotalDistanceForCategoryOverInterval

**交叉核对：已核对（逐例最终回执）。** 确有kayaking搜索、重复打开Oct14、Back退出后stale target双方一致；SUM/精度计算未执行，不虚构错误米答案。精确米值如何经合法UI获得仍未知。

### 目标与约束

公共 goal 是 **kayaking、2023-10-09 到10-10（两端包含）总距离 SUM**，转换为米后只在总和处四舍五入一次，输出一个数。不是本周所有 kayaking，也不是取最大。owner 事后读 frozen sports proto:2931–2987确认 inclusive日期+SUM米，不能据此回填 UI没读到的距离。

### 实际序列

1. step1、3启动 passed但launcher，step4 drawer、step6点图标、step8/10两页说明，业务前 **6写**。本例上限20，不应错记10。
2. `tap_on-12(search_button)`（e45），step14/e53输入 kayaking，`press_key-15(Enter)`（e55）提交；结果是 Waterway Paddle/Yesterday，Need more strength and conditioning/Monday，Mindful Movement/Monday，Kayak Expedition/3Oct。这里确实做了分类相关搜索，不可说本例从未用过过滤；结果包含名称不含kayaking的条目，支持搜索能触及类别，但其完整/精确匹配语义未由当前app源码核实。
3. step17/e59打开 Waterway Paddle，step18详情明确 `Oct14,2023,2:22PM`、1.76mi；step19 Back、20快照。**step21/e67再次打开同一 Waterway Paddle**，step22仍是Oct14和同一数值；step23才返回。这一重复没有新增区间或距离精度证据。
4. step25/e75开 Need more strength and conditioning：Oct9 8:00AM、1.24mi；step27返回。step29/e83开 Mindful Movement：Oct9 6:15AM、2.80mi；step31返回。没有Oct10条目被读到，也没有记录“无Oct10且搜索覆盖完整”的断言。
5. e91对旧详情搜 distance、e93对Oct9详情搜 stats_start。`press_key-33(Back)`（e95）从已回到列表的状态把App退出到drawer；step34新快照已可见drawer。随后 `tap_on-35(More options)`（e99）仍用App菜单目标，失败 `Target was not found.`，是 **已消耗的第19写**，不是预算拒绝。step37/e105点OpenTracks重新进入无kayaking搜索的全列表，是第20写；step39菜单（e109/a77）、step40 kill（e111/a78）才是 action_budget拒绝。
6. main `W091/...private.json` **step5** summary=`Unable to verify an exact total in meters before the harness action budget was exhausted.`；其计划明确精度未获证、SUM/round skipped。verifier step6与官方reward0保持分开。

### 首偏离与根机制

- 系统最早偏离仍为启动passed但非前台（S-L）。**首个确定可避免的业务重复是step21**：step18已经给了Oct14日期，仍重复打开区间外同一记录。首次step17也不在目标区间，但它可能同时在帮助确立绝对日期，不能把一次日期核对与第二次无新信息打开一概而论。
- **第二个独立偏离〔事实〕**：step33 Back后已见drawer，step35仍找App的More options，违反S-K:17的“用当前画面重新评价目标”；既丢了搜索状态又损失一写。不能把 step35 的missing target与step39 budget拒绝合成同一个坐标故障。
- **直接失败〔事实〕**：相应精度与全集仍未知，后续设置导航/teardown被拒，main不交数字。**根机制〔强推断〕**是未缓存“排除Oct14”的行级事实、没有把导航状态与已读证据结合、发现英制精度不足太晚；不是SUM算式已算错。
- **精度〔事实+推导〕**：已读两条是1.24mi与2.80mi。这是显示值，不是精确距离；两条各有约±8.05m量化不确定性，简单相加转换可累积约±16.09m，不保证最近整数。报告不提供由此猜出的米答案。即使owner确认oracle有容差，也不能把它当精度缺口已经闭合。

### 修复计划

- **ST-091 / P1，FSQ主执行/Skill owner**：针对S-K:14–18与 `HarnessToolAdapter._format_runner_result:147–183` 已提供的 step、输出与artifact信息，要求维护行级ledger和页面状态：Oct14标“区间外/已读”，Oct9条目标“日期已证、mi精度不足”，返回后重新识别列表/详情/drawer。禁止无新证据地重新开已排除行；Back不是通用“关闭搜索”的假定。这样阻断step21重复和step35 stale target；风险是同名不同时刻不能被错误合并，应以日期/时间/行关联区分。
- **ST-091-U / P1，FSQ preplan owner**：S-P `build_pre_plan_input:60–86` 在累加型查询一开始就规划类别、inclusive时间窗、覆盖凭证、原单位与所需精度；单位发现为英制时，在遍历前确定合法足够精度的可见显示路径，再累加原始精确值并最后round一次。不得假设改成km就必然有1m精度，无法获得时保留unknown。S-B:85–118预算照常计费，不重试补预算。
- **未来验证**：授权后离线检验“分类搜索4行，其中区间外两行、区间内同日两行；误Back到drawer；两位mi精度”的计划与状态转移；要求排除条目不重开、missing target前读当前页、SUM只在全集/精度确认后输出。启动与公开预算反馈仍用ST-L，不扩大20写。

关键证据：`R091/events.jsonl:e45–87,e91–112`；`R091/execution-result.json.steps[agent-tap_on-17,21,25,29,agent-press_key-33,agent-tap_on-35,39]`（数字缩写仅指相同action前缀）；`W091/native-action-audit.jsonl:a33,41,49,57,65,69,73,77,78`。以下图片相对 R091，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-7a5a5b40fbbb.png`。
- step15：`artifacts/screenshots/screenshot-agent-press-key-15-finalize-after-action-1-56a3821ae6b7.png`。
- step25：`artifacts/screenshots/screenshot-agent-tap-on-25-finalize-after-action-1-482543ef603b.png`。
- step29：`artifacts/screenshots/screenshot-agent-tap-on-29-finalize-after-action-1-f9993b3de61e.png`。
- step33：`artifacts/screenshots/screenshot-agent-press-key-33-finalize-after-action-1-fe60d4706419.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-40-prepare-before-action-1-05c0742719a4.png`。

## 案例 092 — SportsTrackerTotalDurationForCategoryThisWeek

**交叉核对：已核对（逐例最终回执）。** 一条30min不能充全周总和、swipe20被拒双方一致；不能写30秒、已算错分钟或已选错moving字段。原0保留。

### 目标与约束

公共 goal：本周 running 的 **total duration SUM**，Monday起，输出 **分钟单整数**。初始化区间Oct9…15；单位不是秒，不是距离，不能混入cycling等category。owner事后读 frozen sports proto:2708–2762确认SUM分钟；没有把隐藏duration参数替代实读UI。

### 实际序列

1. step1/3启动→launcher；step4 drawer、6图标、8/10两页首启，累计6写到列表。
2. 列表step10/11可见 `More tired than usual today` Yesterday `30:00 (2.80mi)`、`Quick Sweat` Friday `1:15:00 (0.50mi)` 以及skiing、bike、climbing等。最下方是Monday的Skateboard Challenge，底部还有未证明完结的列表，且题目类别不能按标题猜。XML的category仍为Track图标通用描述。
3. step12/e45从y=0拉通知栏，step13/e47快照；e49 search date的完整结果（`artifacts/tools/000017-search_artifact.json`）确含 Sun, Oct15。step14 Back、step15列表；e55再读列表，e57再读同一date搜索artifact。这些read不算写，但说明已读日期证据多次被提取。
4. `tap_on-16`（e59）打开 More tired than usual today；详情给 `Oct14,2023,11:00AM`，MOVING TIME=30:00、TOTAL TIME=30:00；这里是30分钟，不是30秒。category未在该详情XML显式给出；不能从min/mi单独断定running而不是其他pace运动。
5. step18 Back、19列表。e67再读列表，e69再次读同一date搜索artifact；`swipe-20(up)`（e71/a39）在进一步覆盖列表前被action_budget拒绝，画面没前进；step21 kill也拒。没有成功的业务列表滚动到早于Monday边界。
6. main `W092/...private.json` **step5** summary=`Unable to determine a verified integer total before the harness action budget was exhausted.`；计划“收集每条running时长”failed、“sum转分钟”skipped。verifier step6未确认完整总和；official reward0。

### 因果与未知

- 最早系统偏离是S-L；**业务策略偏离〔强推断〕**是先进入单条详情，再回列表尝试全局滚动，之前既无running过滤也无覆盖ledger。打开候选核对字段本身不必然错误，因此不能伪称step16是一次已证错误category选择。
- **可证直接失败**是第11写请求（swipe20）拒绝；已有一条30min，其他候选与Monday尾部未读全，故未交分钟总数。**根机制〔强推断〕**：先有局部duration核对、后做集合筛选/遍历，在首启耗6写后无法闭合全周证据。不是算术、分钟转换或rounding已执行错误。
- moving与total在这条记录恰好相同；不能以本例证明选错了moving而非total。其他活动是否不同、是否还有running、是否存在秒尾数都未知。当前截图能辨图标与时长，但没有视觉分类调用形成main的完整集合。

### 修复计划

- **ST-092 / P1，FSQ检索计划/Skill owner**：在S-P `build_pre_plan_input:60–86` 要求 duration查询先过滤category并缓存周界，再逐条收集同一语义duration字段与单位；结构没有category时使用可见搜索/定向视觉检查（S-K:23–26），不能因pace显示便自动认running。列表已有可信duration时优先整屏读取，而非每条都详情往返；只有字段/单位不明的行才开详情。S-G:163–182用于有覆盖目标的列表手势，并以新旧边界行判实际翻页，避免把swipe passed当完整。
- ledger对`30:00`与`1:15:00`分别按mm:ss和hh:mm:ss解析成统一秒，最后总计转分钟；若公共任务的整数舍入规则或moving/total语义不明需显式保留，不从本例同值推所有记录。该规则防止未来混秒/分钟，但**不是宣称本run已出现该bug**。风险是时长格式/小数秒和单位本地化；须由实际UI标签决定。
- 启动/公开剩余预算采用ST-L（driver launch:95–100，worker:191–197/runtime:308–315）；S-A成功summary只放最终整数。**未来验证**：获授权后离线覆盖2/3段时长格式、running与walking同pace、多屏跨Monday、moving≠total的数据；保证计数对象完整再求和，不提高10写上限。

关键证据：`R092/events.jsonl:e45–74`；`R092/artifacts/tools/000017-search_artifact.json`；`R092/execution-result.json.steps[agent-tap_on-16,agent-swipe-20]`；`W092/native-action-audit.jsonl:a19,23,27,31,35,39,40`。以下图片相对 R092，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-bc010d6cba9e.png`。
- step10：`artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-89175afe93e6.png`。
- step16：`artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-b663da9c0991.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-21-prepare-before-action-1-43659d40234a.png`。

## 案例 106 — TasksCompletedTasksForDate

**交叉核对：已核对、有保留（逐例最终回执）。** frozen tasks.textproto:1526–1574的relevant dueOct16/completedOct10，oracle不是completiontimestamp=Oct16；Show completed只是visibility。歧义未实际形成一次错误过滤，双方不把潜在语义风险当已发生算法bug。

### 目标与约束

公共 goal问 `Which tasks have I completed for October16 2023`，只给标题，多项逗号分隔。需要**已完成状态**与“for日期”的任务归属证据；Show completed只是是否显示，不是只筛已完成。事后oracle支持“dueDate=Oct16且completed”而非“在Oct16当天完成”。未来模型不能获知私有completed_date/预期标题；不要把“for”擅自转成completed timestamp谓词，也不要把所有Oct16任务无状态地输出。

### 实际序列

1. step1/3 launch passed→launcher，step4 drawer→step6 Tasks。进入My Tasks累计 **4写**（Tasks没有OpenTracks的两页首启）。step7列表可见多条标题和Thu/Tue/Wed/Fri/Tmrw日期，底部两条Tmrw；但列表行completeBox在XML是ImageView，无checked字段。图片能显示勾/划线，不能仅按XML缺checked就判全部未完成。
2. step8/e39 More options，step9菜单为 Clear Completed、Collapse/Expand subtasks、**Show completed已勾选**、Show unstarted已勾选。菜单snapshot child checkbox 的checked=true与视觉勾选一致。main并没有误把它关掉；step10 Back。
3. step12/e53通过bottomAppBar ImageButton打开drawer，step13只见My Tasks、Today、Recently modified、Default list等；step14 Back。没有选择完成任务筛选或遍历列表。
4. step15/e59再开相同More options，step16仍相同Show completed=true；step17 Back，step18仍同一My Tasks首屏。该循环既未改变显示条件，也未读出每行completed状态或Oct16精确到期信息。
5. step19/e71尝试再次打开drawer，a37因预算拒；step20 kill/a38也拒。除drawer/menu往返外没有成功业务列表滚动、日期详情或状态断言。
6. main `W106/...private.json` **step4** summary=`Unable to determine the completed task titles for October 16, 2023 before the harness action budget was exhausted.`；计划说Show completed already enabled，不给titles。verifier step5仅确认未交付；official reward0。

### 因果与边界

- 全局首偏离S-L；**首个确定业务重复〔事实〕**在step15再次打开已知checked的同一菜单，接着又退出（17）。step8首次查看visibility是合理信息获取，不能把整个菜单动作都判错。
- **直接失败**是step19被拒且无标题集合。**根机制〔强推断〕**：模型在“显示completed”“过滤completed”“读取row视觉completed状态”之间未推进为可执行的行级筛选，转而反复drawer/menu；S-O显示菜单状态可读，列表完成态却不可直接从该XML读取，这种接口不均衡需要定向视觉/详情，而不是再开同一菜单。
- **没有证据**表明model真的按completion timestamp Oct16过滤过，也没有证据它把未完成任务当完成后提交。因此自然语言歧义是潜在规格/计划风险，不是本run已发生的过滤算法bug。全列表覆盖、完整completed集合均未知，不能从底部两条Tmrw直接还原官方三条fixture标题。

### 修复计划

- **ST-106 / P1，FSQ preplan/Skill owner**：`build_pre_plan_input:60–86` 的计划需把 `completed=true`、due/for日期、completion timestamp三者分列，并引用每条谓词的公共来源；未明确的“for”不得硬转timestamp。利用S-K:23–26在第一次列表观察后对当前行的勾/划线进行定向视觉确认，或经有明确状态标签的详情取证；Show completed=true只记录为visibility，不重复开启。为completed moved-to-bottom和跨屏覆盖保留遍历计划。这样避免此次visibility检查循环以及未来“完成日=到期日”的错误；风险是划线/颜色的可访问性和已完成子任务，不能通过点击completeBox来“探测”并改变数据。
- **ST-106-N / P1，FSQ主runner owner**：用S-K:17和已返回step/屏幕证据维护“菜单已读、无新状态变化”的导航状态，若同菜单重复不增加所需谓词证据，转向任务行而不是再次drawer往返；S-P公开预算反馈使4写入口后仅剩6写的约束可见。启动采用ST-L，不修改oracle解释或增加重试额度。
- **未来验证**：获授权后离线用“Oct16到期但Oct10已完成、Oct16完成但到期不同、同到期未完成、已完成任务在列表下部”测试谓词来源、图像状态读取与覆盖；最后S-A summary只放完整标题CSV，状态解释留evidence。不使用旧relevant ID或oracle标题作prompt答案。

关键证据：`R106/events.jsonl:e19–34,e39–74`；`R106/execution-result.json.steps[agent-tap_on-8,agent-tap_on-12,agent-tap_on-15,agent-tap_on-19]`；菜单UI snapshot `artifacts/ui-snapshots/ui_snapshot-agent-tap-on-15-finalize-after-action-1-fb0c78f5ae28.json`；`W106/native-action-audit.jsonl:a15,19,23,27,29,33,37,38`。以下图片相对 R106，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-b5d5293247cb.png`。
- step8：`artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-5e09f40ec718.png`。
- step12：`artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-c14d9264b2d5.png`。
- step15：`artifacts/screenshots/screenshot-agent-tap-on-15-finalize-after-action-1-108844aae4b0.png`。
- step6：`artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-5eb93a548c73.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-20-prepare-before-action-1-c37859e52967.png`。

## 案例 107 — TasksDueNextWeek

**交叉核对：已核对（逐例最终回执）。** 三次通知栏重复取日期而不推进任务列表双方一致；这是证据复用/进展缺口，不是笼统坐标错误（手势本意即取日期）。frozen tasks.textproto:1397–1465的COUNT范围既有规则保留，不新增completed过滤。

### 目标与约束

公共 goal问下周到期任务**数量**，Monday起，答案单整数。以初始化Oct15 Sunday锚定，目标窗口是 **Oct16Monday…Oct22Sunday**，不是接下来7天滚动、不是本周、不是只看Today；公共goal没给未完成专属条件，不能自己添。相同标题可对应不同任务，不能以标题字符串去重成一个任务。

### 实际序列

1. step1/3 launch返回org.tasks但launcher；step4 drawer、step6打开My Tasks，累计4写。step7首屏有重复Finish Project Proposal/Oct8、同名Call Grandma的不同weekday，Water Plants等；不是完整可计数的下周集合。
2. step8/e37从y=30拉通知栏，step9快照。e41 search date的完整 `artifacts/tools/000013-search_artifact.json` 明确有 `Sun, Oct15`。step10 Back回同一列表，step11快照。
3. step12/e49再次从y=0拉通知栏，step13快照；e53读部分artifact、e55再搜date，完整 `000020-search_artifact.json`还是Sun, Oct15；step14 Back。同一日期字段没有年份，反复读取也没有增加年份信息。
4. step16/e63第三次从y=0拉通知栏，step17快照；e67 search Oct的完整`000026-search_artifact.json`仍Sun, Oct15；step18 Back。三次通知栏拉下/Back共 **6写**，与入口4写恰好用完10。
5. step19仍是相同My Tasks首屏；e73搜text；step20/e75的普通swipe down准备后续观察，却在a39拒绝；step21 kill/a40拒。整段没有成功业务列表翻页，没有打开某个任务的精确dueDate。
6. main `W107/...private.json` **step4** summary=`Unable to determine a verified task count before the harness action budget was exhausted.`，甚至将定日期/下周范围列failed。不能据此抹掉已实际观察到Sun, Oct15的事实；也不能把这些weekday本身当已证year+全部dueDate。verifier step5与official reward0分别记录。

### 首偏离与根机制

- 首系统偏离S-L；**首个可证业务无新信息重复是step12**：第一次date search已有同日证据，第二次同渠道再拉；step16第三次进一步固化循环。没有证据表明date字段在两次之间丢失或发生跨日，年份缺口也没因重复同字段而补齐。
- **直接失败**：6写用于三个通知栏循环，任务列表零翻页，首次后续手势被拒，未交整数。**根机制〔强推断〕**：日期证据未持久化为“已知月日weekday/年份仍缺”的有限状态，main反复重新发现同一字段，而不是选择能补年份/精确dueDate的新证据或开始覆盖。S-P缺公开预算反馈使这一策略无成本警觉；不能笼统归为坐标错误，因为y0/y30确实成功打开了想看的通知栏。
- **unknown**：没有提交数值，没有可评估的计数/去重算法输出；未见把2026宿主时间当业务日期的行为，不能替它造一个错年根因。completed条件也不是已执行错误过滤。

### 修复计划

- **ST-107 / P1，FSQ preplan/main owner**：在 `build_pre_plan_input:60–86` 与S-K:14–18规划一次性时间解析状态，记录原始 `Sun, Oct15` 来源、缺失year、派生Monday边界；若year确实必要，则要求新UI能给年份的证据，而非重开同一通知栏。已确认的时间信息在同run重用，不把宿主2026时间补进来。此处不请求更大budget或盲重试，防止第二/第三次拉下浪费6写中的4写。
- **ST-107-C / P1，FSQ查询Skill owner**：范围确定后按dueDate可见排序/过滤或多屏ledger枚举，任务身份使用行上下文/日期等证据，重复标题不等于重复任务；明确未完成不是公共goal自动谓词。覆盖必须证明区间上、下界与相关列表，不把某个首屏widget计数当全局结果。复用S-P的预算公开、S-L启动后置核对；S-A summary只承载已验证count。
- **未来验证**：另获授权后离线构造“Sunday参考日、通知栏只有month/day、任务详情有year、同名多条、跨两周边界”的观察回放，要求同一日期证据不重复拉栏且六条fixture数量不能靠硬编码通过。验证COUNT身份规则但不自行新增completed排除。

关键证据：`R107/events.jsonl:e37–78`；`R107/artifacts/tools/000013-search_artifact.json,000020-search_artifact.json,000026-search_artifact.json`；`R107/execution-result.json.steps[agent-swipe-8,12,16,20]`；`W107/native-action-audit.jsonl:a15,19,23,27,31,35,39,40`。以下图片相对 R107，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-c62401d30e00.png`。
- step8：`artifacts/screenshots/screenshot-agent-swipe-8-finalize-after-action-1-6fb222c8f858.png`。
- step12：`artifacts/screenshots/screenshot-agent-swipe-12-finalize-after-action-1-eeced1db0bdc.png`。
- step16：`artifacts/screenshots/screenshot-agent-swipe-16-finalize-after-action-1-b5f60b84283e.png`。
- step6：`artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-bf321329419e.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-21-prepare-before-action-1-c46c8c140164.png`。

## 案例 108 — TasksDueOnDate

**交叉核对：已核对（逐例最终回执）。** 年份picker核对有价值但成本高；跨屏XML完整字符串与当前frame标题裁切可并存，视觉assertion failed不写AI误判。frozen tasks.textproto:1078–1123/proto_utils:147–179的完整集合判据保留，不用私有第三项补summary。

### 目标与约束

公共 goal问 **Oct24,2023到期的所有任务标题**，只标题，多个逗号分隔；没有priority或completed筛选。不能以“两个在末屏可见”代替跨屏完整集合，也不应把旧fixture私有title作为额外答案来源。

### 实际序列

1. step1/3 launch passed却launcher；step4 drawer→step6 Tasks，4写。step6/7首屏实际显示 `Follow up on support tickets`、`Draft marketing email`、`Research market trends` 均标Oct24；这些是已观察候选，**不是本文声明的完整官方答案**。全局列表的完整性当时还未证明。
2. step8/e37打开第一条详情，step9显示Tuesday,October24；step10/e43点日期进入picker。e47搜2023；step12/e49用 `assert_state(accessibilityId="24 October2023",selected=true)`成功核对该日期（实际payload含标准空格）。这确实验证了2023年，不能说只看了month/day。
3. step13 Back回编辑页，step15 Back触发 `Are you sure you want to discard your changes?`；step17/e59点`android:id/button2`丢弃返回列表。**没有证据证明持久修改了task**，但一次日期核对带来打开详情/日期、Back两次、Discard共5写的模态路径成本。
4. step19/e65 swipe up首次推进列表。新屏第一条Draft的title bounds只有 **[147,128][912,143]（高15px）**，几乎全部被上边缘截去；它的note/date仍有残留。Research market trends完整显示。step20快照XML仍保留两个完整title字符串，不能当作两个标题在像素上都可读。
5. e69/e71在新旧list artifact查Oct24；step21/e73 swipe down拟将上条露出，a41被预算拒。step22/e75在未改变的末屏发AI断言“当前同时显示Draft与Research各dueOct24”，正常返回 **passed=false, confidence=.99**，解释仅Research可见，Draft无法验证；这不是provider/JSON错误。该断言不计写预算，a42 attempted/a43 failed；step23 kill/a44拒。
6. main `W108/...private.json` **step4** summary=`Unable to verify the complete set of tasks due October 24, 2023 before the harness action budget was exhausted.`，声明全集未verified、不是CSV。verifier step5也承认首屏三个候选/日期assertion，并不提供替代最终答案；official reward0。

### 因果与不同证据层

- 首系统偏离S-L。**策略成本〔强推断〕**：在尚未做覆盖前，step8–17把一个本可见date候选升级成多层编辑/日期模态核对，5写挤占遍历。该核对有补年份价值，不能直接把step8判成错误操作或声称更简路径已由本run证实可用。
- **首个确定断言语义偏离〔事实〕**是step22：把跨屏已读的candidate变成“现在两标题都可见”的断言，忽略Draft高15px、当前frame标题不可读；step21被拒后并没有重新得到能显示它的页面。S-O原结构完整文本不等于像素完整可见。视觉否决与实际末帧一致，不能归为AI“看漏了明明可见的完整标题”。
- **直接失败〔事实〕**：budget阻止回滚视窗、局部视觉断言failed、最终不交CSV。**根机制〔强推断〕**：跨屏候选ledger/coverage与当前单帧assertion混用，加上高成本详情核对，丢失了“已经见过什么/还缺全局覆盖什么”的分层。缺全集不能靠把局部两项改为assert passed补救。
- completed图标/划线不是本题谓词；不能因为末屏许多已完成任务就自行排除它们。标题<50字的这些候选未被XML的文本限长截断；本例的关键截断是视口bounds，不是长字符串compaction。

### 修复计划

- **ST-108 / P1，FSQ主runner/Skill owner**：以S-O `_format_runner_result:147–183` 的原artifact/step关联建立跨屏候选ledger，并分开“已观察row关系”“当前frame可视”“全部列表覆盖”。S-K:23–26的断言一次只验证当前可见且bounds足够完整的内容；跨屏集合验证引用逐屏证据，不要求所有候选同时出现，不把partial帧当集合缺项证明。这样防止step22断言scope错位，又不压制真实AI失败；风险是bounds只能提示裁切，不能替代真正视觉判断。
- **ST-108-N / P1，FSQ preplan owner**：在 `build_pre_plan_input:60–86` 为只读IR预估详情/日期picker/Back/Discard代价；先收集首屏与后续屏的title/date候选，再仅对有歧义行核对年份，避免不必要编辑modal。若必须开编辑页，应明确无保存/Discard路径并计入同一预算；不把UI写动作从S-B中豁免。修复不是删除年份核对或弱化完整集合。
- **ST-108-A / P1，FSQ output owner + producer owner**：S-A保持唯一main summary来源；完成后summary必须是公共要求的完整titles CSV、分析另放evidence。不能把main的inconclusive摘要替换成evidence里的两项候选，也不能由verifier/oracle补齐第三项。**未来验证**：授权后离线用三项跨两屏、顶部15px残留title、年份picker与Discard的fixture检查ledger/可视断言/CSV数量边界；不扩大10写。

关键证据：`R108/events.jsonl:e37–78`；`R108/execution-result.json.steps[agent-assert_state-12,agent-press_key-15,agent-swipe-19,agent-swipe-21,agent-assert_with_ai-22]` 的invoke.harness_metadata.ai_assertion；`W108/native-action-audit.jsonl:a23,25,29,33,37,41–44`；`artifacts/ui-snapshots/ui_snapshot-agent-swipe-19-finalize-after-action-1-478737dc8467.json`中的title bounds。以下图片相对 R108，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-ee96e3a4d480.png`。
- step6：`artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-117806c3b7b6.png`。
- step10：`artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-580ac0124faa.png`。
- step19：`artifacts/screenshots/screenshot-agent-swipe-19-finalize-after-action-1-514084579fec.png`。
- step22：`artifacts/screenshots/screenshot-agent-assert-with-ai-22-invoke-assert-with-ai-1-b4e61bd18995.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-23-prepare-before-action-1-f77e453733c2.png`。

## 案例 110 — TasksHighPriorityTasksDueOnDate

**交叉核对：已核对（逐例最终回执）。** By priority有效，根在drawer往返及没给日期核验留动作，不应禁sort。frozen tasks.textproto:1316–1348的importance0+dueOct18既有规则保留；主summary Unable不是已提交错标题。

### 目标与约束

公共goal要求 **high priority 且dueOct18,2023** 的所有title，多个逗号分隔；不能只按priority不看date、只按date不看priority，也不能自行增加未完成谓词。相对weekday需挂接2023年参考日期；初始launcher的Sun,Oct15能提供month/day/weekday，不能凭2026执行timestamp推Wed的绝对日期。

### 实际序列

1. step1/3 launch返回org.tasks但画面launcher；step4 drawer、6 Tasks，累计4写。初始My Tasks只有weekday(date)和无优先级文字的行；视觉checkbox颜色不同，XML completeBox无importance语义标签。
2. step8/e37打开drawer，step9见My Tasks/Today/Recently modified/Default list；step10/e41点My Tasks回同一列表，**2写往返没有缩小priority/date集合**。step11再次观察。
3. step12/e47点menu_sort打开Grouping/Sorting配置；step14/e51点Grouping；step16/e55选By priority；step18/e59 Back应用。此 **4写** 确实产生有效结构化分组，不是无效点击：step19显示High priority三行（Renew Driver's License/Fri、Attend Team Meeting/Today、Marketing Campaign Launch/Wed），接着明确Medium priority边界。
4. main此时有了priority分组与weekday，但没有任务详情绝对日期。`tap_on-20(Marketing Campaign Launch)`（e65/a39）想核对候选详情，在第11写请求前被拒；step21 kill/a40拒。因此不能说它已经读到该title的Oct18,2023详情。
5. main `W110/...private.json` **step4** summary=`Unable to verify all matching task titles before the harness action budget was exhausted.`，evidence说有三条High priority但weekday不足，review exact due dates failed、CSV skipped。verifier step5缺titles-only；official reward0。

### 因果与保留意见

- 最早系统偏离S-L；**首个确定无筛选收益的业务往返是step8→10**，先进入drawer又回My Tasks，随后才用sort/group。不能把step12–18同样判为无意义导航：By priority实际解决了XML没有priority文字的问题，是本例与106/107不同的有效决策。
- **直接失败〔事实〕**：入口4写+drawer往返2写+分组配置4写=10，候选精确dueDate详情在a39被拒，main不给title。**根机制〔强推断〕**是先探索list导航再做全局展示设置，预算未为第二个谓词（具体日期）保留路径，而不是误分high/medium。
- **未知**：本侧可确认当前High→Medium边界及三条行关系，但没有证明其他列表/已完成底部不存在相关项；不得将可见High组直接断言是所有数据的完整high集合。也没有实提交错误title或完成态过滤结果。
- **答案交付与本地保守性**：即使截图里能提出很强的候选，也不是合法main交付；model的“不能确证绝对日期”不等于官方认为候选一定错。不能以隐藏relevant title替它补答案。

### 修复计划

- **ST-110 / P1，FSQ preplan/Skill owner**：在 `build_pre_plan_input:60–86` 生成两谓词计划：先选一次能提供priority证据的UI（本例证明groupBy priority可用），同步记录公共日期锚/缺year点，然后保留exact due核对与覆盖所需动作。既有My Tasks首屏时不先drawer再回同项。S-K:14–18把“返回同列表且筛选状态未变”的动作记为无新增谓词证据；S-P将剩余写预算显式反馈，阻止10写全用于入口/分组。风险是改变group是持久显示设置，要在获准动作里计费，不替换/修改task importance或dueDate；若需恢复亦计费。
- **ST-110-F / P1，FSQ查询Skill owner**：ledger必须分别引用`High priority header→row`关系和该row精确dueDate；color无明确语义时用文字分组/定向视觉，不把所有Wed当Oct18，也不把相邻Medium行纳入High；不额外按completed排除。此策略保留本例有效分组，修的是前置浪费与交集未闭合，不是禁用sort。
- **未来验证**：另获授权后离线测试High/Medium同日、多列表、相对Wed与明确year、已完成底部和同名异priority，要求两个谓词及覆盖证据同时成立才输出S-A summary CSV；启动后置condition走ST-L（driver:95–100），producer预算边界S-B维持10，不靠retry或oracle候选通过。

关键证据：`R110/events.jsonl:e37–68`；`R110/execution-result.json.steps[agent-tap_on-8,10,12,14,16,agent-press_key-18,agent-tap_on-20]`；`W110/native-action-audit.jsonl:a15,19,23,27,31,35,39,40`；`R110/artifacts/tools/000020-ui_snapshot.json`。以下图片相对 R110，已查看：
- step1：`artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-a76d066ff3fc.png`。
- step6：`artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-5124468c1291.png`。
- step18：`artifacts/screenshots/screenshot-agent-press-key-18-finalize-after-action-1-0267e4e109ad.png`。
- terminal/kill前（kill被拒）：`artifacts/screenshots/screenshot-agent-kill-app-21-prepare-before-action-1-c5b3019e6bdc.png`。

## 本切片结论与待联合闭合项

八例都经历了“launch返回目标app_id但前台仍launcher→手动drawer图标进入”的可观测差异；OpenTracks另有两页首启，因此业务入口分别消耗6写和4写。但后续不能合并归因：087未建立running周覆盖；090未建mountain-biking候选最大值；091已分类搜索，却重复区间外详情并在Back后失去页面状态/精度；092只有局部duration、未枚举running全集；106重复visibility菜单而未读取行完成态；107重复三次同日通知栏；108跨屏ledger与当前帧可见断言混用；110分组确实有效，但另一谓词核对被前置往返挤出预算。没有一例提交了可被指出“数字算错/标题集合错项”的正常业务答案，不能用统一“模型格式差”掩盖这些前因。

与harness owner经parent转达的逐例事实/fixture判据总体一致；保留两类非争吵式边界：106“completed for”自然语义不等于completion timestamp，需文档澄清而非给模型私有值；108XML包含完整字符串与截图标题出屏可以同时成立，视觉assertion failed不构成明显模型错误。其余待闭合：启动请求的实际SDK前台语义由parent查证；英制显示下最近米精度如何在获准可见UI获得仍未知；列表/其他list/完成态在未遍历部分不得虚构。所有拟议验证都只列未来计划，本切片没有执行任何验证命令或重跑。
