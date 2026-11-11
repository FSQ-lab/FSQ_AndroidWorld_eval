# 预算耗尽第74项：SimpleCalendarEventsInTimeRange

## 结论

本项没有读到目标日的数据，最终 raw 答案 `unresolved` 是诚实的，但不是题目要求的标题列表。Agent 正确地把 “Friday” 解析为 2023-10-20（当前日视图是 October 15 (Sun)），但选择 Daily view 后用日期选择器改日期；`2373` 先调用不存在的 `set_value`，`2723` 改用 clear/send_keys/OK 后日期仍停在 10-15，`2963` 只读观察确认未变。之后用剩余两次动作切 Weekly view，`3526` 在读取 `top_value` 时 `NoSuchElementException`，没有保存切换后的元素树；随后 quit。

因此 primary layer 是 **model planning（导航/日期输入与恢复）**，并叠加 **Appium/app 的 NumberPicker 输入未产生业务状态变化**；answer-capture 契约也把最终文本丢了，但即使保留 `unresolved` 也不满足 IR 的标题契约。现有 proposal 中“HTTP 200 不等于业务证据、超时后观察真实状态、按页面阶段等待”完全适用，但它不能提供正确的日期选择器操作路径，也不需要为此新增规则。

## 原任务与结果

- manifest index=74，seed=481426288，maxSteps=10，businessSeconds=720。
- 目标：Simple Calendar Pro 中 Friday 16:15–20:00 的事件标题，逗号分隔。
- 原执行：10/10 UI 动作，14 次 `python_exec`，Agent 148.983 秒；termination=`step_budget`。
- reward=0.0；`agentFinished=true`，`agentIndicatedDone=false`；最后 raw JSON 的 `taskOutcome="unresolved"`，`normalized.finalText=null`、`agentAnswer.validContract=false`。
- `information_retrieval.py:111-112`：`interaction_cache` 为空时直接返回 0；本项没有转发任何答案，进入该分支。即使 finalText 被保留，`unresolved` 也会因不是 Friday 标题列表而失败。
- cleanup：quit 返回 true，环境侧 `absentVerified=true`；无残留 session。

## 动作分账

|UI动作|原始行|内容|结果|
|---|---|---|---|
|1|779|launcher 垂直上滑|露出 Calendar 候选|
|2|1353|点击 Calendar 候选|进入 Simple Calendar Pro|
|3|1634|Change view|打开视图菜单|
|4|1851|Daily view|日视图，`October 15 (Sun)`|
|5|2140|点击 `top_value`|打开日期选择器（Oct / 15 / 2023）|
|6|2723|`clear()`|HTTP 返回，但后续状态未改变|
|7|2723|`send_keys('20')`|HTTP 返回，但后续状态未改变|
|8|2723|点击 OK|HTTP 返回；等待 `'20' in top_value` 超时|
|9|3526|Change view|打开视图菜单|
|10|3526|Weekly view|点击后读取 `top_value` 失败|

`2373` 的 `day.set_value('20')` 抛 `AttributeError`，没有执行任何 UI 动作，因此不计入 10 次动作；它是被冻结运行时不支持的 WebElement 客户端 API，不是 app 拒绝。`3612` 是独立 quit。

## 最早偏离与原始锚点

行号相对 `episodes/074-SimpleCalendarEventsInTimeRange/attempt-1/raw-private/agent-events.jsonl`。

- **1851（第4次动作）**：Daily view 的 `top_value` 是 `October 15 (Sun)`；当时可见事件都在 10-15，Friday 10-20 的事件不可见。选择 Daily view 本身不是错误，但把任务变成了额外的日期导航。
- **2140（第5次动作）**：日期选择器字段为 month=`Oct`、day=`15`、year=`2023`，按钮 `Cancel`/`OK`。Agent 需要把 day 改为 20。
- **2373**：`day.set_value('20')` → `AttributeError: 'WebElement' object has no attribute 'set_value'`；异常发生在计划点击 OK 之前，**该 cell 没有执行 UI 动作**，也没有改变日期。这是一个工具 API 知识错误，但没有造成状态副作用。
- **2723–2724（第6–8次动作）**：`day.clear()`、`day.send_keys('20')`、点击 OK 都返回；随后 `WebDriverWait(... lambda d: '20' in top_value.text)` 超时，traceback 第7行指向等待而非三个动作。**这是最早的“HTTP 200/动作返回但业务状态未变”分歧**：输入/确认没有把日期改成 20。
- **2963（只读）**：失败后的真实状态仍是 `October 15 (Sun)`、Daily view；与 `'20' in top_value` 的假值一致。Agent 正确地观察了失败，但没有读回选择器字段值，也没有在 spend 前验证 day 字段。
- **3526（第9–10次动作）**：点击 Change view、点击 Weekly view，然后在读取 `top_value` 时 `NoSuchElementException`（traceback 第11行）。第11行是最终 facts 表达式，说明前面的 Change view/Weekly view 点击和 “Daily view 消失” 等待已通过，Weekly view 很可能已打开；但 Agent 继续读取 Daily view 专用的 `top_value`，失败后没有捕获周视图事件树，因此仍不能证明 Friday 的事件当时是否可见。随后预算关闭，`3612` quit。
- **3659（最终 raw JSON）**：`taskOutcome="unresolved"`；`normalized.finalText=null`。即使它被转发，IR 也会把 `unresolved` 当作答案文本，而不是 Friday 的标题集合，无法满足契约。

**最早可判定的不可胜点**：`2723` 日期改变未生效。更早的 `2373` 是无效 API 调用但无状态副作用；`1851` 的 Daily view 选择只是策略。`2723` 之后仅剩两次动作，而 Agent 把这两次用于 Weekly view 切换且没有取得观察结果。

## 未解决的数据问题

没有捕获 Friday 10-20 的任何事件列表或时间范围数据，因此不能从证据中枚举正确答案，也不能判断正确标题数量。报告不猜测答案；`unresolved` 是当前证据下唯一诚实的结论。缺少的证据：

1. `clear()`/`send_keys('20')` 后、点击 OK 前 day 字段的实际值。
2. Weekly view 切换后的元素树/事件列表；`3526` 在最终表达式失败前没有返回事实字典。

## 独立检查与方案适用性

见 [observation-predicate-replay.json](observation-predicate-replay.json)。回放只使用保存的文本/字段：当前 top_value 为 `October 15 (Sun)`，picker day=15；请求 20；失败后 top_value 仍为 `October 15 (Sun)`，`contains20=false`、`dateChanged=false`、`fridayEventsRead=false`。这是历史状态回放，没有新的 Android/Appium 运行。

与现有候选方案的对应：

- **HTTP 200 不等于业务证据**：`2723` 的 clear/input/OK 都返回，但日期没变；方案要求用业务后置条件判断成功，正好命中。
- **超时后观察真实状态**：`2723` 超时后 `2963` 读回仍是 10-15，处理正确；方案要求不要只根据动作返回或超时猜状态，适用。
- **按页面阶段等待**：`'20' in top_value` 比 page_source 子串更接近业务状态，但仍未验证 picker 字段本身；方案的“可区分页面/阶段”原则适用。
- **不要盲目重复**：Agent 没有重复同一个 `set_value`，而是换了 clear/send_keys；但新的输入方法仍无效，且没有读回字段。方案的“观察后重试”只部分适用。
- **不能覆盖**：具体日期选择器的正确输入方式（NumberPicker 的 clear/send_keys 行为、是否需要先聚焦/使用加减按钮）以及 Weekly view 的 header 差异，是 app/Appium 交互知识，不是通用 skill 规则；本项不新增规则。

## 本轮边界

原 campaign、manifest、result 与 raw events 保持只读；未创建 Android/Appium session，未清数据、未重启服务、未重跑官方任务。只新增本项分析与原观察回放。原始文件 sha256 前后一致，见 [review-verification.json](review-verification.json)。
