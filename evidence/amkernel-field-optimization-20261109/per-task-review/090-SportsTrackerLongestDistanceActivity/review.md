# 预算耗尽第90项：SportsTrackerLongestDistanceActivity

## 结论

数值换算本身正确：保存的 Skill work 统计是 `0.75 mi`，按 `0.75 × 1609.344 = 1207.008 m` 四舍五入为 **1207**。但关键前提没有在捕获状态中被验证：Agent 只读了 Scenic Cycling 的 edit screen（category=`biking`），从未使用 Activity type 过滤，也从未打开 Skill work 的 edit screen，没有在 Skill work 的 stats 中看到分类；最终却把 Skill work 当成 mountain biking 活动。原始 task metadata 的 distance=1200 m 与 1207 m 相差 7 m，在该任务 10 m tolerance 内，这是元数据交叉检查，不替代对 category 的观测。

更直接的结果是 answer contract 双重丢失：raw final 在 cleanup 阶段产生（`normalized.finalText=null`），且 `taskOutcome` 是对象 `{"answerMeters":1207}`，而 `runner.py:171-180` 明确要求字符串；即使 finalText 被捕获，`_task_outcome` 仍会返回 `None`，答案不会进入 `interaction_cache`，IR evaluator 在 `information_retrieval.py:111-112` 直接 0。因此 official 0 是 **Harness/contract** 的直接结果；模型侧叠加了 **category 未验证** 和动作预算分配问题，但数值答案在观测距离上是对的。

## 原任务与结果

- manifest index=90，seed=1671790926，maxSteps=10，businessSeconds=720。
- 目标：OpenTracks 中本周（周一开始）mountain biking 活动的最长距离，单位米、四舍五入到整数。
- 原执行：10/10 UI 动作，17 次 `python_exec`，Agent 194.701 秒；termination=`step_budget`。
- reward=0.0；`agentFinished=true`，`agentIndicatedDone=false`；最后 raw JSON 的 taskOutcome 是对象，`normalized.finalText=null`、`agentAnswer.validContract=false`。
- cleanup：quit 返回 true，环境侧 `absentVerified=true`；无残留 session。

## 动作分账

|UI动作|原始行|内容|结果|
|---|---|---|---|
|1|1283|launcher 垂直上滑|露出 OpenTracks 候选|
|2|1707|点击 OpenTracks|进入 app|
|3|1967|点击 intro `next`|跳过介绍页|
|4|2141|点击 intro `next`|进入 track list|
|5|2546|点击 Scenic Cycling|打开 Scenic Cycling stats（11.60 mi）|
|6|3494|点击 More options|动作返回；随后等待 Edit 时 StaleElementReferenceException|
|7|3862|点击 Edit|edit screen 的 activity type=`biking`|
|8|4545|点击 Cancel|退出 edit screen|
|9|4545|点击 Navigate up|回到 track list|
|10|4545|点击 Skill work|stats 显示 0.75 mi；第10次动作关闭预算|

`994` 的 `ModuleNotFoundError` 发生在指针动作前，没有产生 UI 动作。`4617` 是独立 quit。`2546` 的 track list 只捕获了部分可见行，不是整周完整枚举。

需要记录一个账本细节：`stepBudget.actions` 的 10 条记录全部标为 `click`；原始代码中的第1次是 launcher `actions` 上滑，后9次是 click。总 gated action 数都是10，但 `kind` 记录与原始代码不一致；本报告的动作顺序以原始 Python 代码/观察为准，不依赖该 `kind` 字段。

## 最早偏离与原始锚点

行号相对 `episodes/090-SportsTrackerLongestDistanceActivity/attempt-1/raw-private/agent-events.jsonl`。

- **2546（第5次动作）**：track list 前100个已捕获元素可见 `Wave Exploration`（Today，8.09 mi）、`Road Bike Ride`（Thursday，8.65 mi）、`Downhill Skiing`（Wednesday，5.00 mi）；Agent 通过 `track_list_item_name` 找到并点击了未出现在前100个已捕获元素中的 `Scenic Cycling`，随后 stats 显示 `Oct 10, 2023, 12:16 PM`、distance=`11.60`、unit=`mi`。保存的列表不是完整枚举。
- **2919**：Scenic Cycling stats 的 distance=`11.60`、unit=`mi`；stats 没有 category 文本。
- **3862（第7次动作）**：Scenic Cycling edit screen 的 activity type 字段为 `biking`。该字段不等于任务的 mountain biking，不能作为已确认的 mountain biking 候选；它也没有提供 Skill work 的分类。
- **4545（第8–10次动作）**：Cancel、Navigate up、点击 Skill work。Skill work stats 为 `Skill work`、`Oct 10, 2023, 7:00:00 AM`、distance=`0.75`、unit=`mi`、description=`Stepped outside my comfort zone.`；**没有 category 字段**。Agent 没有打开 Skill work 的 edit screen，也没有其他 category 证据。
- **4545 之后**：第10次动作关闭预算；最终答复只能落在 cleanup 阶段。
- **4790（最终 raw JSON）**：`taskOutcome={"answerMeters":1207}`，`sessionCleanup={"quitReturned":true}`；`taskOutcome` 不是字符串。`runner.py:171-180` 首先检查 `isinstance(value.get("taskOutcome"), str)`，对象直接导致 `_task_outcome` 返回 `None`。
- **result.json**：`officialReward=0.0`，`normalized.finalText=null`，`agentAnswer.validContract=false`；`interaction_cache` 为空，IR evaluator 111–112 直接 0。`omp_supervisor.py:160-169` 只在 `not cleanup_requested` 时保存 `task_final`，`203-208` 不把 cleanup 阶段 prose 当作答案。

**最早的内容/证据分歧**：`4545`。Agent 读取了 Skill work 的日期和距离，但没有读取 category，随后却把它当作 mountain biking 活动；这是“读了统计就以为验证了目标状态”的典型缺口。**最早的结果契约分歧**：`4790` 的 taskOutcome 对象；cleanup 边界则在 `4545` 第10次动作后已经注定。两者独立：即使修正对象类型，cleanup 仍会丢 finalText；即使 finalText 被捕获，对象类型仍会被 runner 拒绝。

数值回放：`0.75 × 1609.344 = 1207.008 → 1207`，与 raw final 中的 1207 一致。该换算没有舍入/单位错误；不确定性只在“Skill work 是否属于 mountain biking”以及“本周是否还有未观察到的更长 mountain biking 活动”。保存的 track list 不完整，不能排除这两点。

## 独立检查与方案适用性

见 [observation-predicate-replay.json](observation-predicate-replay.json)。回放只使用保存的字段：周窗口 2023-10-09..2023-10-15；Scenic Cycling category=`biking`；Skill work 0.75 mi、category 缺失；换算 1207.008→1207。没有新的 Android/Appium 运行。

与现有候选方案的对应：

- **读取成功不等于证据、观察必须区分目标状态**：Agent 读了 Skill work 的 stats，但 stats 没有 category；它没有继续打开 edit screen 或寻找其他 category 证据。方案中的“观察必须能区分目标状态”正是这个缺口，适用。
- **批量/持久命名空间**：17 次 Python 调用中多次在单 cell 内完成点击、观察、读取 stats；`2919` 一次返回多字段，属于应保留的 AMKernel 强项。
- **HTTP 200/动作返回不等于业务证据**：`3494` 点击 More options 返回但等待 Edit 时 stale，`4545` 点击 Skill work 返回后才得到 stats；方案要求以业务后置条件判断，适用。
- **不能覆盖**：最终 `taskOutcome` 必须是字符串、cleanup 阶段 finalText 不被捕获，都是冻结 harness 契约，不是 skill 文案能解决的。`taskOutcome` 对象化可以在 skill 中写成明确契约，但这属于 benchmark/answer-contract 知识，不是通用 Android 技能；本轮不新增规则，也不修改正式 skill。
- **可避免的规划浪费**：Scenic Cycling 的 stats + edit screen + cancel + navigate up 用了 5 次动作（5–9），使 Skill work 成为第10次动作；如果更早确认候选、更早读取 category，或直接使用 Activity type=mountain biking 过滤，可能有空间在动作预算关闭前提交文本答案。但这不是本项 official 0 的唯一原因。

## 本轮边界

原 campaign、manifest、result 与 raw events 保持只读；未创建 Android/Appium session，未清数据、未重启服务、未重跑官方任务。只新增本项分析与原观察回放。原始文件 sha256 前后一致，见 [review-verification.json](review-verification.json)。
