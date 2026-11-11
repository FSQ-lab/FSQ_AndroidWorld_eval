# 预算耗尽第73项：SimpleCalendarEventsInNextWeek

## 结论

内容判断正确：按“下周从周一开始”计算，窗口是 2023-10-16 至 2023-10-22；保存的周视图和 Simple event list 在该窗口内只有 `Product demo` 和 `Movie night`。raw final 也正是这两个标题，且是 runner 期望的字符串形式。

但该答案在 cleanup 阶段才产生。`omp_supervisor.py` 只在 `cleanup_requested` 之前捕获 `task_final`；本项第10次 UI 动作已关闭 step budget 并触发 cleanup steer，因此 `normalized.finalText=null`，`runner.py` 的 `_task_outcome(None)` 返回 `None`，答案没有写入 `interaction_cache`，IR evaluator 在 `information_retrieval.py:111-112` 直接返回 0。这是冻结的 r12 v2 answer-capture 边界，不是本项的日历计算错误。

在模型侧，真正可避免的浪费是：到 `3393` 行，结合 `2899` 的周42 `Product demo` 与 `3393` 的周43 `Movie night`，已足以作答；Agent 仍用第9–10次动作切到 Simple event list 复核，导致最终答复只能落在 cleanup 阶段。`3200` 行的换行谓词超时只浪费一步，不是滑动失败。

## 原任务与结果

- manifest index=73，seed=1504700490，maxSteps=10，businessSeconds=720。
- 目标：Simple Calendar Pro 中下周（周一开始）的事件标题，逗号分隔。
- 原执行：10/10 UI 动作，13 次 `python_exec`，Agent 179.186 秒；termination=`step_budget`。
- reward=0.0；`agentFinished=true`，`agentIndicatedDone=false`；最后 raw 答案是合法 JSON，但 `normalized.finalText=null`、`agentCompleted=false`、`agentAnswer.validContract=false`。
- cleanup：owned session quit 返回 true，环境侧 `absentVerified=true`；没有残留 session。

## 动作分账

|UI动作|原始行|内容|结果|
|---|---|---|---|
|1|1041|点击 launcher 搜索入口|进入搜索|
|2|1373|输入 `Simple Calendar Pro`|观察候选|
|3–4|1699|clear、输入 `Calendar`|得到两个 Calendar 候选|
|5|2247|点击第二个 Calendar 候选|进入 Simple Calendar Pro|
|6|2571|Change view|打开视图菜单|
|7|2899|Weekly view|进入周视图，header `wk. 42`|
|8|3200|水平滑动到下一周|滑动后等待 `'S\n22' in page_source` 超时|
|9–10|3680|Change view、Simple event list|第10次动作关闭预算，列表显示 18–25 日|

只读观察 `670`、`1890`（截图）、`3393`、`3753`（quit）不计 UI 动作。`3753` 的 quit 是独立清理调用。

## 最早偏离与原始锚点

行号相对 `episodes/073-SimpleCalendarEventsInNextWeek/attempt-1/raw-private/agent-events.jsonl`。

- **2899（cell 7）**：周42网格为 `S\n15 M\n16 T\n17 W\n18 T\n19 F\n20 S\n21`；唯一事件 `Product demo` 的 bounds 为 `[536,1419][671,1496]`，列中心落在 `W\n18`，即 2023-10-18。周42只覆盖 10-15 至 10-21，这是因为日历网格从周日开始，不代表下周从周日开始。
- **3200（cell 8）**：`driver.swipe(900, 1100, 180, 1100, 500)` 已执行；随后 `WebDriverWait(..., lambda d: 'S\n22' in d.page_source)` 抛 `TimeoutException`（traceback 第2行）。**3393** 的只读观察显示 header 已是 `wk. 43`、首列为 `S\n22`，并出现 `Movie night`（bounds `[125,584][261,644]`）及 23–28 日的噪声事件。因此滑动本身推进了视图；超时更可能是 page_source 字符串编码/谓词问题，而非滑动失败。保存的 `3393` 结果是元素列表，不是原始 page_source 字符串，不能进一步断言具体转义形式。
- **3393（cell 10）**：结合 `2899` 的周42 `Product demo` 与 `3393` 的周43 `Movie night`，已覆盖 10-16..10-22 的两个观测事件；此时仍可作答。
- **3680（cell 12）**：第9次点击 Change view、第10次点击 Simple event list；列表首段为 `18 Wednesday → Product demo`，随后 `22 Sunday → Movie night`，再后为 23–25 日噪声。列表起始段为 18 日，且 19–21 日无 section，周视图中 16–17 日也无事件，支持“窗口内只有两个标题”。
- **3683 之后**：第10次动作关闭 step budget；cleanup steer 发出；`normalized.finalText` 因此没有被捕获。
- **3804（最终 raw JSON）**：`taskOutcome` 为字符串 `"Product demo, Movie night"`。按 `runner.py:171-180`，如果它被传入，会得到合法 answer；但 `omp_supervisor.py:160-169` 只在 `not cleanup_requested` 时保存 `task_final`，`203-208` 明确不把 cleanup 阶段 prose 当作答案，所以 `finalText=null`。
- **result.json**：`officialReward=0.0`，`agentAnswer.validContract=false`，`normalized.finalText=null`；`interaction_cache` 为空，`information_retrieval.py:111-112` 直接 0。

## 独立检查与方案适用性

使用保存的原始观察执行窗口/列映射谓词，见 [observation-predicate-replay.json](observation-predicate-replay.json)：

1. 周42 `Product demo` 的列 `W\n18` → 2023-10-18，在周一窗口内。
2. 周43 `Movie night` 的列 `S\n22` → 2023-10-22，在周一窗口内（周日是窗口最后一天）。
3. Simple event list 只出现 18、22、23、24、25 日 section；19–21 无 section，周视图 16–17 无事件。
4. 计算标题集合为 `{Product demo, Movie night}`，与 raw final 字符串一致。

这是历史观察回放，不是新的 Android 复现。未证明 `S\n22` 在 page_source 中的具体编码，也未证明如果 Agent 在 3393 后立即回答会被 evaluator 接受；但根据 runner 的字符串契约，它至少会进入 `interaction_cache`，而不是因 `finalText=null` 直接 0。

与现有候选方案的对应：

- **批量/持久命名空间**：本项 13 次 Python 调用中多次在单 cell 内完成点击、观察、条件读取；这是应保留的 AMKernel 强项。
- **等待必须区分页面阶段**：`3200` 的 `'S\n22' in page_source` 是脆弱的文本编码谓词；方案要求基于能区分阶段的状态，适用。正确做法仍是滑动后直接读取周 header/日期标签，而不是只信 page_source 子串。
- **HTTP 200 不等于业务证据、超时后观察真实状态**：`3200` 超时后 `3393` 立即读回真实 wk43，处理正确。
- **部分结果/足够证据时停止**：`3393` 已足够，继续第9–10次动作复核没有必要；方案的“阶段检查、偏离停止”部分适用，但不能保证模型在动作预算边界前主动提交。
- **不能覆盖**：最终答案在 cleanup 阶段被排除是 `omp_supervisor.py`/`runner.py` 的冻结契约行为，不是 skill 文案能修复的；本项不新增规则，也不修改正式 skill。

## 本轮边界

原 campaign、manifest、result 与 raw events 保持只读；未创建 Android/Appium session，未清数据、未重启服务、未重跑官方任务。只新增本项分析与原观察回放。原始文件 sha256 前后一致，见 [review-verification.json](review-verification.json)。
