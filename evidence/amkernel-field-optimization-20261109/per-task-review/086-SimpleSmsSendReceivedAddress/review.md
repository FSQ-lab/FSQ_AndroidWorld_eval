# 086-SimpleSmsSendReceivedAddress 预算耗尽复核

> 原始对象：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/086-SimpleSmsSendReceivedAddress/attempt-1`。以下 `raw:N` 均指 `raw-private/agent-events.jsonl` 第 N 行。原始文件只读；没有新设备/Appium 运行。

## 结论

**任务要求**：把 Oscar Mohamed 短信中的地址 `789 E Oak St, Phoenix AZ 85006` 发给 Gabriel Ibrahim（`+19696338338`），使用 Simple SMS Messenger。**实际结果**：18/18 个 UI 动作耗尽，`officialReward=0.0`；目标会话与正文编辑框已经到达，正文输入作为第 18 个动作被接受，但紧接着的发送点击成为第 19 个请求，被 action budget gate 拒绝。没有发出短信。

**最早偏离**：动作 1（cell 3，`raw:823`）打开 Google Messages（`raw:824` 返回 `com.google.android.apps.messaging/.ui.ConversationListActivity`），不是目标应用。动作 2–5 又进入 home/系统 UI 与 launcher 导航（`raw:1039`、`raw:1515`），直到动作 12（cell 15，`raw:3306`）才用 `driver.activate_app('com.simplemobiletools.smsmessenger')` 恢复。11 个动作在目标应用之外被消耗。**独立性**：本案例的直接边界是 18 步硬预算与第 19 个发送点击被拒；084 的换行问题和 082 的 ASI/搜索环境都不是这里的阻塞。

**决定性边界**：动作 18（cell 24，`raw:4991`）成功输入正文后被计入；动作 19 的发送点击在 `raw:4994` 以 `UnknownMethodException` 被拒绝。`stepBudget.executedActionCount=18`、`maxSteps=18`、`rejectedActionCount=1`；因此“正文输入成功但发送未获准入”是直接失败点，而非应用返回了错误，也不是 evaluator 判错。

## 动作分账（18 个已准入 + 1 个被拒绝）

| # | cell（raw 行） | 实际动作 | 结果 |
|---|---|---|---|
| 1 | 3（823–824） | click `Messages` | 打开 Google Messages，错误应用 |
| 2 | 4（1039） | press Home | 回 launcher |
| 3 | 4（1039） | swipe | 等待含 `SMS` 文本超时；进入的不是预期 app |
| 4 | 7（1515） | press Back | 离开系统/主屏覆盖层 |
| 5 | 7（1515） | swipe | 等待 `search_box_input` 超时 |
| 6 | 9（1897） | click 搜索框 | launcher 搜索表面 |
| 7 | 9（1897） | input `Simple SMS Messenger` | 重复后缀 suggestions |
| 8 | 11（2335） | click `Simple SMS Messenger0` | 非 clickable 文本，10.5 s 后 package 未变 |
| 9 | 14（3125） | swipe | 打开 launcher 搜索/列表 |
| 10 | 14（3125） | click 搜索框 | 进入搜索 |
| 11 | 14（3125） | input `Simple SMS Messenger0` | 再次出现重复行 |
| 12 | 15（3306） | `activate_app` | 目标 app，验证 package 成功 |
| 13 | 17（3690） | click `top_toolbar_search` | 应用内搜索 |
| 14 | 17（3690） | input `Gabriel Ibrahim` | 出现 Gabriel 结果 |
| 15 | 18（3885） | click `Back` | 关闭搜索/回列表；却等待 `new_conversation`，超时 |
| 16 | 21（4373） | tap FAB | 进入 New conversation |
| 17 | 22（4579） | click `Gabriel Ibrahim` | 点击后等待 `message` 超时，但 cell 23 证明会话已打开 |
| 18 | 24（4991） | input 正文 | 接受；发送按钮变为 clickable |
| (19) | 24（4991–4994） | click `thread_send_message` | **拒绝**；未执行 |

动作 15 和 17 是“调用失败但已有副作用”的两个实例：15 的 Back 已关闭搜索，17 的点击已打开 Gabriel 会话；模型在 cell 23 重新观察并继续，没有把 timeout 当作无效果。动作 3/5 也消耗了已准入动作，即使等待超时。

`pythonCalls=25`，7 次整体失败；kernel 始终 `alive`。AMKernel 的批量/本地 XML 归约、`activate_app` 和同 session 观察都正常，本案例不是批量能力失败。截屏 `captured-sms-main-before-new-conversation.png`（`raw:4186`，sha256 `b3b8…19e2e`）显示 Simple SMS Messenger 主列表：Oscar Mohamed、地址 `789 E Oak St, Phoenix AZ 85006`、右下 FAB。该截图独立于模型自述，证明地址来源与目标 app 已到达。

## 最早偏离与决定性证据

1. **`raw:823–824`**：动作 1 沿用 `Messages` 可访问性文本打开 Google Messages。三个 SMS 案例最初都犯了这一错误，但后续分支不同；本案例没有把它当作唯一根因。
2. **`raw:1039`、`raw:1515`**：home 后 swipe 的等待条件与 `Wallpaper & style`/launcher 搜索相关，说明动作 2–5 在系统/主屏表面绕行；具体是哪一个系统表面没有被截图保留，不能过度断言。
3. **`raw:3306`**：`activate_app` 后等待 `current_package == com.simplemobiletools.smsmessenger`，目标 app 恢复；这证明 package activation 是可用的恢复路径，而不是环境不允许。
4. **`raw:4745`**：cell 23 观测到 `package=com.simplemobiletools.smsmessenger`、标题 `Gabriel Ibrahim`、`thread_type_message`（EditText）和 `thread_send_message`（Button, `clickable=false`）。收件人/会话是正确的。
5. **`raw:4991`**：动作 18 输入正文。代码随后执行的等待是 `thread_send_message` 的 `clickable=='true'`；错误发生在下一行点击，所以该等待已经通过——**发送按钮在输入后变为 clickable 是由 traceback 行号推断的强证据，不是直接读回**。
6. **`raw:4994`**：点击发送被拒。`stepBudget.rejectedActionCount=1`，而动作列表第 18 项是 input，说明这 1 个拒绝正是发送点击。HTTP/代理侧将 `StepBudgetExceeded` 映射为 unsupported operation（`src/fsq_androidworld_eval/appium_proxy.py:436-438`、`omp_supervisor.py:135-138`）；Selenium 侧因此表现为 `UnknownMethodException`，消息文本被 AMKernel 的敏感词过滤（含 `session`）。
7. **`raw:5223`** 有原始 assistant 最终 JSON，自述“send action was rejected after action budget closed”，与独立重放一致；但 `normalized.finalText=null`、`agentCompleted=false`、`agentIndicatedDone=false`，cleanup steer 在 `raw:5001`。该 JSON 未转发；官方 0 与 trace 中无 successful send action 一致，DB 中无 sent 记录是从此推断、未独立查询 DB，不能把 finalText 边界当作发送未发生的替代解释。

## 独立重放检查

`observation-replay.json` 的只读重放结果：

- 目标 package 在 cell 15 出现；cell 23 的 package、线程标题、composer、send button 全部与上述一致。
- 第 18 个动作是 input；动作列表中不存在第 19 个已执行 click，`rejectedActionCount=1`。
- 发送按钮在输入前 `clickable=false`；错误发生在等待 clickable 之后，故可推断输入已被接受并使按钮启用。但**没有**发送后的 UI 观察，无法证明草稿内容在拒绝后仍保留。
- trace 中没有 successful send action，也没有发送后的 UI 观察；`is_successful` 要求 DB 中存在 sent message。DB 中无 sent 记录是从 trace 推断的，未独立查询 DB；官方 0 与该观测一致。即使 evaluator 的 `current app` 分支因 quit 改变，也不会改变“无成功发送动作”这一观测。
- 限制：最后一次 `UnknownMethodException` 消息被过滤，不能直接读到“预算耗尽”文本；但动作数、拒绝数、traceback 行号和代理实现共同支持这一解释。未重跑设备，不能验证当时的 composer 文本或 UI 最终态。

## 与已修复 Runtime 异常消息的关系

- 本案例的最终异常类型是 `UnknownMethodException`，不是此前修复的 `InvalidElementStateException`。该类型本来就在 `_WEBDRIVER_NAMES` 中；消息被隐藏是因为它包含 `session`，命中 `_WEBDRIVER_SENSITIVE`，不是“异常类型未识别”。
- 该隐藏不改变动作是否被允许：发送点击被 gate 拒绝，`rejectedActionCount=1` 已足够证明。过滤只降低了可诊断性，模型随后也收到了 cleanup steer（`raw:5001`）并正确自述预算关闭。
- 因此本案例**不能**归因于“异常消息修复缺失”，也不能用来验证那次修复；它属于冻结 harness 的预算/清理契约 + 模型在 18 步内的规划分配。
- 可讨论的仅是诊断层的改进（让 gate 拒绝以不含敏感词的类型/消息出现），但这不是本组所需的新通用 skill 规则；父级如要做 Runtime 诊断增强，应单独立项。

## 方案适用性

当前候选 skill 的预算与阶段规则可直接覆盖：

- “Bound the sequence by the actual action budget, including failed admitted actions”：动作 2–11 的绕行和失败等待都计费；18 步时已没有发送余量。
- “A launch is ready only when the intended app and relevant page/control are observed together”：动作 1 的错误 package 没有立即纠正，直到动作 12。
- “For an installed app… use the observed client's supported activation API”：`activate_app` 在第 12 步才使用；若在动作 1 后立即使用，可节省大量动作。
- “If an action leaves the same relevant state, observe before another attempt”：重复搜索没有带来目标启动。
- 输入后读回与阶段检查：动作 18 输入前已由 cell 23 确认正确会话和收件人，但没有在输入脚本内重复校验标题；这不是最终失败原因，真正的边界仍是预算。

**是否需要新增通用规则：否。** 当前候选规则在文本上覆盖预算/激活/阶段检查，但这是候选规则与历史 frozen run 的事后对照；历史 frozen skill 是否包含这些文本未逐字核对，不能断言原 agent 违反了当时可见的指导，也未证明遵循候选就能在 18 步内成功。直接路径的 18 步算术只是一个未测试的下界提议，不是已证明的结果。不要为“发送按钮恰好是第 19 个动作”添加 SMS 专用规则或坐标路线。

## 边界与保留

- 不把“最终 `UnknownMethodException` 消息为空”当成执行未发生；拒绝计数和动作列表独立证明发送未准入。
- 不把模型自述当作发送状态证据；正文是否真正进入输入框只有输入接受 + 按钮 clickable 的间接证据。
- 未修改原始 campaign/result/raw、skill 或 proposal；未重跑、未重评、未清理或新建会话。
