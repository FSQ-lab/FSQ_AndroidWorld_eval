# 预算耗尽项：NotesMeetingAttendeeCount

## 结论

目标笔记最终被打开并读到了正确内容；“Employee Performance Evaluation”正文显示 `25 individuals were present`，Agent 最终自报也是 25。reward=0 不是数错、不是没找到笔记，也不是最后输入异常，而是答案没有跨过冻结 harness 的两道契约边界：

1. 10/10 动作用尽后，harness 在 raw line 4024 发 cleanup steer；Agent 在 line 4147 才给出最终 JSON。`omp_supervisor.py` 只在 `cleanup_requested` 之前捕获 `task_final`（160–169），因此磁盘上的 `normalized.finalText` 为 null；`runner.py` 752–756 只从 `normalized.finalText` 计算答案；null 时 `answer=None`，不写入 `interaction_cache`；`android_world/task_evals/information_retrieval/information_retrieval.py` 109–115 的 `is_successful` 只从 `interaction_cache` 取答案，因此 evaluator 收不到。
2. 即使捕获了原始最终文本，Agent 仍失败于外层字符串契约：`taskOutcome` 是整数 `25`，而 `runner._task_outcome` 只接受字符串。任务要求单个数字并不与 transport 的字符串字段矛盾；数字可以先表示为 `"25"`，所以这里是可兼容的表示差异，不是被证明的协议冲突。

这是“观察/规划正确，答案交付契约失败”的案例。前面确实有侧栏/点击目标导致的动作浪费，但它没有阻止最终读到正文，不能当作本项零分的主因。

## 原任务与结果

- manifest index=38，task=`NotesMeetingAttendeeCount`，complexity=1，maxSteps=10。
- 目标：在 Joplin 的 Meeting Notes 中找到 Employee Performance Evaluation，读出会议出席人数，按任务要求返回单个数。
- 原执行：10/10 UI 动作，18 次 python_exec，219.102 秒；业务预算剩余约 500 秒；termination=`step_budget`，`cleanupRequested=true`。
- reward=0；`agentAnswer.validContract=false`；`agentCompleted=false`；`agentIndicatedDone=false`；`agentFinished=true`。
- 原始最终文本存在（line 4147）：`{"taskOutcome":25,"sessionCleanup":"completed","evidence":"Employee Performance Evaluation displayed “25 individuals were present”."}`。
- 独立观察（line 4026）确实包含 `25 individuals were present`；最终自报与观察一致。

## 动作分账

|UI动作|内容|原始锚点|结果|
|---|---|---|---|
|1|滑出应用抽屉|cell4 / 943|成功|
|2|打开 Joplin|cell5 / 1184|成功|
|3|点 Meeting Notes|cell6 / 1392|进入正确笔记本|
|4|Back|cell7 / 1589|回到笔记列表|
|5|点 Search|cell8 / 1883|点击成功，随后等待搜索框超时；搜索仍可用|
|6|输入 `Employee Performance Evaluation`|cell11 / 2546|目标标题出现在列表|
|7|点搜索结果中心|cell12 / 2854|点击被侧栏/布局遮挡，等待打开超时|
|8|点 Sidebar|cell14 / 3299|点击成功，等待条件不成立|
|9|坐标 tap|cell15 / 3570|未打开目标；结果仍是列表|
|10|坐标 tap (900,429)|cell17 / 4026|打开目标笔记并读到正文；这是最后一次被授权动作|

**6 click + 3 actions + 1 input = 10；rejectedActionCount=0。** cell2 的 lxml `ModuleNotFoundError` 是本地环境缺包，不是 UI 动作。cell18 的 quit 不经过 UI gate。

## 最早偏离与决定性证据

- **line 4024（cleanup steer）**：第 10 次动作后预算关闭，harness 要求不再做 UI mutation，保留 session 并 quit。此后 Agent 的输出属于 cleanup 阶段。
- **line 4026（cell17）**：最终一次被授权坐标 tap 打开笔记，正文含 `25 individuals were present`。说明预算内已经完成业务观察；此处不是失败点。
- **line 4147（最终 assistant message）**：cleanup steer 之后才生成最终 JSON。原 raw 文本存在，但 `normalized.finalText=null`；因此 `_task_outcome(null)=None`，信息检索 evaluator 无答案。
- **line 4147（同为类型边界）**：原 `taskOutcome` 为 int 25。replay 显示 `_task_outcome(raw_text)` 返回 `None`；把同一文本改成 `"25"` 后返回 `"25"`。即使用 raw 文本替代 null，整数仍会被 runner 丢弃。
- 动作层较早的异常（line 2854 点击结果中心被遮挡、line 3299 侧栏、line 3570 坐标未命中）是效率问题；line 4026 已恢复并完成观察，不能把零分归因于这些 UI 异常。

## 独立回放与方案适用性

使用原始观察和冻结源码做无设备回放，见 [observation-replay.json](observation-replay.json)：

1. 笔记正文谓词：`25 individuals were present` → true；自报 25 与观察 25 一致。
2. 原始正常化：直接对 raw 运行 `_normalize_agent_events`，`finalText` 会保留、`agentCompleted=True`；但 `termination.cleanupRequested=true` 且最终文本行晚于 cleanup steer，`omp_supervisor` 的 cleanup 分支把磁盘 normalized 改写成 `finalText=null`、`agentCompleted=False`。
3. 契约谓词：raw int → `_task_outcome=None`；string 化 → `"25"`。两个条件独立地阻止答案进入 evaluator。

与现有候选方案的对应：

- “执行前明确预期可观察业务变化；HTTP 200 不能替代业务证据”适用于本项：Agent 确实读到了正文，观察是正确的。
- “读取成功不代表数据来自本次动作”也适用，但本项不需要再加强状态规则；失败发生在答案捕获与类型契约，不在技能流程。
- 现有方案完全不能覆盖 harness 的 cleanup 文本排除与 `taskOutcome` 字符串要求；也不应通过 skill 解决冻结 Harness 契约。正式 skill 不建议为本项新增规则。
- 保留 AMKernel 优势：一次 python_exec 内搜索、输入、观察和读取正文是合适的；不需要退化为单步工具。

## 不确定性与残留

- 本项不需要截图即可得出结论；没有解码任何图片。侧栏/结果行的精确视觉遮挡未独立核对，依据是文本观察和超时位置。
- 未修改任何原始 campaign、manifest、result、raw 或冻结依赖；未启动 Android/Appium，未重跑或重评分。
- 最终报告是“观察正确、答案未被 harness 接收”，不是“Agent 答错”。如果要修复，属于 Harness/answer-contract 层（不是 AMKernel Runtime），不属于通用技能提案。
