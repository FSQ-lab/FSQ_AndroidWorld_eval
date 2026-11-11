# 084-SimpleSmsSend 预算耗尽复核

> 原始对象：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/084-SimpleSmsSend/attempt-1`。以下 `raw:N` 均指 `raw-private/agent-events.jsonl` 第 N 行。原始 campaign/result/raw/manifest 只读；没有启动新设备或 Appium 会话。

## 结论

**任务要求**：向 `+16597910719` 发送短信 `Beauty is in the eye of the beholder`。**实际结果**：12/12 个 UI 动作耗尽，`officialReward=0.0`。最终停在 `NewConversationActivity`，只有收件号码，没有进入会话/消息编辑页，没有发送。trace 中没有任何 successful send action；DB 中无 sent 记录是从此推断的，未独立查询 DB，`official 0` 与该观测一致。`finalText=null` 只是 harness 的最终答案转发边界，不是本案例的 SMS 失败原因。

**最早偏离**：动作 1（cell 3，`raw:711`）按 `Messages` 打开了 Google Messages（`raw:712` 返回 `com.google.android.apps.messaging/.ui.ConversationListActivity`）。动作 1–7 共 7 个动作用于错误应用和导航（动作 2–7 为 back/搜索/两次 swipe），直到动作 8（cell 13，`raw:2290`）才进入目标 `com.simplemobiletools.smsmessenger`。**独立性**：与 082 的共同首击不构成同根假设；084 的不可恢复点不是搜索环境，而是换行清空收件人后没有确认控件/后续预算。

**本案例的决定性偏离**：动作 11（cell 18，`raw:2885`）对 `new_conversation_address` 执行 `send_keys('\n')`。该动作被计入，但等待“离开 NewConversationActivity”超时（10.9 s），随后 cell 19 的观测仍为 `NewConversationActivity`，地址字段读回为单个空格 `" "`（`raw:3045`）；这说明 `"\n"` 没有完成收件人确认，反而使已读回的 `+16597910719` 不再保留。动作 12（cell 20，`raw:3143`）重新输入同一号码并读回成功，但预算已尽，无法再点击确认/进入会话/输入正文/发送。

因此主层是 **模型输入语义与 UI 观察/规划**：过早打开错误应用浪费 7 个动作；在换行未生效后没有检查新出现的确认控件，而是重复输入。不是 Runtime/Appium 执行缺陷；本案例唯一的 `UnknownMethodException` 是 `UiScrollable` 被纯 UiSelector 契约拒绝（cell 10，`raw:1988`），消息完整保留且没有消耗动作，属已知协议边界。

## 动作分账（12/12）

| # | cell（raw 行） | 实际动作 | 效果/证据 |
|---|---|---|---|
| 1 | 3（711–712） | click `Messages` | 打开 Google Messages，错误应用 |
| 2 | 4（984） | back | 离开 Google Messages |
| 3 | 4（984） | click Search | 进入 launcher 搜索 |
| 4 | 4（984） | input `Simple SMS` | 产生重复后缀结果 |
| 5 | 6（1401） | back | 关闭搜索 |
| 6 | 7（1542） | actions swipe | 尝试打开 app drawer |
| 7 | 11（2088） | actions swipe | 打开/滚动列表；动作 8 找到目标 |
| 8 | 13（2290） | click `SMS Messenger` | 进入目标 app `.MainActivity` |
| 9 | 15（2548） | click FAB | 进入 `NewConversationActivity` |
| 10 | 17（2793） | input `+16597910719` | 地址字段读回正确 |
| 11 | 18（2885） | input `"\n"` | 等待离开 NewConversation 超时；地址变空 |
| 12 | 20（3143） | input `+16597910719` | 再次读回正确；无后续动作 |

`executedActionCount=12`、`rejectedActionCount=0`；21 次 Python 调用，2 次失败（cell 10 的 `UiScrollable` 契约拒绝、cell 18 的等待超时）；kernel `alive`。动作 11 虽然整体调用 failed，但 `send_keys` 发生在失败前，已实际执行并改变了地址字段——这里没有把“Python 调用失败”误记为“动作未发生”。AMKernel 的批量读取、局部状态检查与持久命名空间均正常；失败来自路线/输入语义，不是批量能力。

## 最早偏离与决定性证据

1. `raw:711–712`：首个 UI 动作打开 Google Messages；没有在点击后验证目标应用/页面。
2. `raw:1163` 附近是上一份现场报告引用的行号，但该行在本 campaign 中是 assistant thinking，不是 `UiScrollable` 调用；本报告不沿用该行号，改以 `raw:1988` 的实际 cell 10 错误为准。现场报告关于“换行不保留原号码、存在无标签 `new_conversation_confirm`”的结论与本 episode 的地址清空观察一致，但 `confirm` 节点不在本 campaign 保存的 15 条观察里，属于上一轮现场 XML 证据，不能当作本轮可重放的节点。
3. `raw:2793`：cell 17 读回 `value: "+16597910719"`，`activity: ".activities.NewConversationActivity"`。这是发送前唯一一次正确收件人状态。
4. `raw:2885–2886`：`send_keys('\n')` 后等待 activity 改变；超时。`raw:3045` 的后续观测仍是 `NewConversationActivity`，地址字段为 `" "`。这两条一起证明“换行不是确认，反而覆盖了单行收件人”。
5. `raw:3143`：cell 20 重新输入后读回 `+16597910719`；`raw:3229` quit。之后没有任何确认/进入会话/正文/发送动作。
6. `raw:3280` 有 assistant 最终 JSON（自述“recipient populated, no send”），但 `normalized.finalText=null`、`agentCompleted=false`、`agentIndicatedDone=false`，cleanup steer 在 `raw:3153`；该 JSON 未转发。对 SMS evaluator，未发送已经足以判 0，不能把最终答案边界当作根因。

## 独立重放检查

`observation-replay.json` 只使用保存的调用/stepBudget：

- 目标 package 与 `MainActivity` 出现于 cell 13；`NewConversationActivity` 出现于 cell 15、17、19、20。
- 动作 10 的地址值精确为 `+16597910719`；动作 11 后仍为 NewConversation 且字段读回 `" "`；动作 12 又读回 `+16597910719`。
- 所有观测中都没有 `thread_type_message` / `thread_send_message`，代码中也没有发送点击；没有正文输入。
- 保存的 cell 19 观察只有 15 个元素，且观察代码只取 text/desc/id/class，**不取 clickable/enabled/displayed**；因此即使确认控件存在于真实 UI，模型侧也没有把它呈现为可点击候选。当前候选 skill 的“无文本/描述也要带 clickable 状态”正是针对这一缺口。
- 限制：没有 084 截图；本 episode 的保存 XML 摘要无法独立证明 `new_conversation_confirm` 当时是否可见。上一轮现场报告提供了该节点的存在性证据，但本轮不重做现场诊断，故标记为“跨证据支持、非本 campaign 可重放”。

## 与已修复 Runtime 异常消息的关系

- 本案例的 cell 10 是 `UnknownMethodException`（`UiScrollable` 拒绝），错误消息完整：`Only pure UiSelector observations are supported; scrolling searches consume multiple interactions`。它说明已识别的 WebDriver 异常消息可以正常透出；但它不是此前的 `InvalidElementStateException` 修复路径，不能拿来证明或否定那次修复。
- 本案例的 cell 18 是普通 `TimeoutException`，消息为空；属于等待条件失败，不是消息被过滤。
- 三个 SMS 案例都没有出现 `InvalidElementStateException`，所以此前“异常消息修复”在本组中**未被触发**；本轮结论是“确认那次修复的机制在代码/单元层面已被上一轮确认”，而不是“本组原失败由它导致或已由它修复”。

## 方案适用性

当前候选 skill 已直接覆盖本案例的决定性点：

- “After typing, read back its value… Sending `"\n"` as text is not an IME submit action and can replace a recipient… After input changes a form, inspect newly exposed controls… Include resource-id/class and enabled/displayed/clickable state even when text and description are empty. Prefer the observed confirmation control.”
- “A launch is ready only when the intended app and relevant page/control are observed together.”
- “Bound the sequence by the actual action budget, including failed admitted actions.”

因此候选规则在文本上能覆盖该决定性点，但这是**候选规则与历史 frozen run 的事后对照**，不能断言原 agent 当时看到了该文本或违反了当时可见的指导，也不能把本案例当作候选规则已证明的收益。`needsNewRule=false`。当前 proposal 的“输入前确认焦点、读回、阶段检查、部分结果报告”也与这里一致，但同样只是候选方案，未在同一 frozen 环境做遵循性 smoke。

## 边界与保留

- 未把上一轮现场报告的成功配方（`reward=1`）当作本 campaign 的官方结果；本轮没有重新执行，也没有重新评分。
- 未修改原始 campaign/result/raw、skill 或 proposal；未清理任何会话、未启动新设备。
- 未独立解决 `new_conversation_confirm` 在本 episode 中的可见性；这是本报告最重要的保留项。
