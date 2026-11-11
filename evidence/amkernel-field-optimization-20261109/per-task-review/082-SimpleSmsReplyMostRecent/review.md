# 082-SimpleSmsReplyMostRecent 预算耗尽复核

> 原始对象：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/082-SimpleSmsReplyMostRecent/attempt-1`。以下 `raw:N` 均指 `raw-private/agent-events.jsonl` 第 N 行。原始 campaign/result/raw/manifest 只读，本报告未修改，也没有启动新的 Android/Appium 会话。

## 结论

**任务要求**：用 Simple SMS Messenger 回复最近一条短信（收件号码 `+17594820731`），内容 `A quick brown fox`。**实际结果**：12/12 个 UI 动作耗尽，`officialReward=0.0`；目标应用从未成为前台，短信从未发送，Google Messages 被误打开，最后停在 launcher/Google Search 界面。

**最早偏离**：动作 1（cell 3，`raw:695`）按可访问性文本 `Messages` 点击，实际打开的是 `com.google.android.apps.messaging/.ui.ConversationListActivity`（`raw:696`），不是 Simple SMS Messenger。该动作本身是全局最早的错误起点。**独立性**：本报告不把 084/086 的根因当作前提；082 的不可恢复分支是搜索表面/环境，而不是 084 的换行或 086 的第 19 个发送动作。

**本案例的实际根因不是单一 Runtime**：动作 2–4 从 home 回 launcher 后上滑，实际进入的是主屏幕定制面板（`raw:934` 读到 `Wallpaper & style`、`Widgets`、`Home settings`），随后按 back 退出；动作 5–6（`raw:1246`）改用 Google Search 搜索 `Simple SMS Messenger`。搜索返回十行带数字后缀的重复文本（`Simple SMS Messenger0` … `Simple SMS Messenger9`），这些是 **Text 节点且 `clickable=false`**；动作 7、10 点击/坐标 tap 均未启动目标应用（`raw:2300`、`raw:2888`）。到截图时刻，查询词已进一步变成 `Simple SMS Messenger0`、结果变成 `00`…`09`，说明这些后缀是动态追加/重复的观察值，不是可用的应用名。截图 `captured-launcher-search-asi-crash.png`（来自 `raw:3054`，sha256 `43fb…b4bcd`）同时显示 **“Android System Intelligence keeps stopping”** 对话框（App info / Close app），遮挡下方结果；动作 11 就是点 `Close app`（`raw:3192`）。因此本案例是 **模型规划/UI 推断失败 + 应用/launcher 搜索环境异常**的叠加，不是 AMKernel 执行异常或 evaluator 误判。

## 动作分账（12/12）

| # | cell（raw 行） | 实际动作 | 观察到的效果 |
|---|---|---|---|
| 1 | 3（695–696） | click `Messages` | 打开 Google Messages；错误应用 |
| 2 | 4（933） | press Home | 回 launcher |
| 3 | 4（933–934） | swipe | 打开主屏幕定制面板（Wallpaper & style/Widgets/Home settings），不是 app drawer |
| 4 | 5（1246） | back | 退出定制面板，回 launcher |
| 5 | 5（1246） | click Search | 进入 Google Search 表面 |
| 6 | 5（1246） | input `Simple SMS Messenger` | 出现重复后缀搜索结果 |
| 7 | 11（2300） | click `Simple SMS Messenger0` | 点击非 clickable 文本，10.5 s 后 package 未变 |
| 8 | 13（2705） | click Search | 再次进入搜索 |
| 9 | 13（2705） | input `Simple SMS Messenger0` | 再次出现重复后缀行 |
| 10 | 14（2888） | tap `(350,400)` | 标题区域，无启动 |
| 11 | 16（3192） | click `Close app` | 关闭 ASI 崩溃对话框 |
| 12 | 17（3262） | back | 回 launcher；随后 quit |

`stepBudget.executedActionCount=12`、`rejectedActionCount=0`；18 次 Python 调用，4 次整体失败（父节点爬取 `NoSuchElement`、点击后等待超时等），kernel 始终 `alive`。失败调用中已经执行的动作仍计入上表，未把“Python 抛异常”当成“没有动作”。AMKernel 的批量观察/本地过滤和持久命名空间没有被破坏；问题在路线选择，不在批量执行能力。

## 最早偏离与原调用锚点

1. `raw:695`：`driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Messages').click()`；`raw:696` 返回 Google Messages。**这是可验证的最早错误动作**。没有在点击后比较目标应用/页面，也没有切换到目标应用。
2. `raw:934`：home 上滑的等待只检查“任意 TextView”，结果读到主屏幕定制面板，并非 app drawer；`raw:1246` 随后 `driver.back()` 并点击 Search，才进入 Google Search。该 cell 是搜索路线取代 app drawer 的转折点；其后的重复搜索没有引入新证据。
3. `raw:2300`、`raw:2888`：点击非 clickable 文本 / 点标题区域，均未启动目标应用。`raw:1814`、`raw:1988` 的父节点遍历失败说明当时的 XPath `..` 无法提供祖先结构；这不是本案例的必然阻塞，因为备用启动路径未尝试。
4. `raw:3054` 的完整截图是独立于模型文本的证据：Google Search + 重复 suggestion 行 + ASI 崩溃对话框。仅凭模型最终自述不足以证明环境，截图补上了这一层。
5. `raw:3389` 有原始 assistant 最终 JSON，但 `normalized.finalText=null`、`agentCompleted=false`、`agentIndicatedDone=false`；清理 steer 在 `raw:3343`。该 JSON 属于 cleanup 阶段，未转发为正式 `agentAnswer`。**SMS evaluator 要求 DB sent 记录且当前 app 为 Simple SMS Messenger**：trace 中没有任何 successful send action，当前前台也观测为 launcher/Google Messages；DB 中无 sent 记录是从“无成功发送动作”推断的，未独立查询 DB，官方 0 与该观测一致。无论是否转发 final answer 都不可能成功，因此不能用“finalText 为空”替代本案例的失败原因。

## 独立重放检查

`observation-replay.json` 只重放已保存的 envelope、stepBudget 和 PNG：

- 观测到的 package 只有 `com.google.android.apps.nexuslauncher` 与 `com.google.android.apps.messaging`；目标应用 `com.simplemobiletools.smsmessenger` **从未出现**。
- 20 个搜索文本全部带数字后缀；对应节点的 `clickable=false`。因此“点击文本 → 启动应用”不成立。
- 全部动作中没有 `thread_type_message` / `thread_send_message`；代码中也没有发送按钮点击。
- 最后观察到的 package 是 launcher；没有可回放的发送记录。
- 限制：PNG 是保存时的一次性画面；无法从只读日志判断 ASI 崩溃是否瞬时、重复搜索标签的上游生成逻辑，也无法验证当时若改用 package activation 是否一定成功。未运行新设备，不补测。

## 方案适用性

当前候选 skill 的多条规则都能提前拦截，但原 episode 没有遵循：

- “A launch is ready only when the intended app and relevant page/control are observed together”：动作 1 后直接把 Google Messages 当成目标。
- “A successful find is only a candidate… use relevant attributes… to disambiguate”：点击了 `clickable=false` 的文本行。
- “If an action leaves the same relevant state, observe before another attempt… repeating… is not progress”：动作 7、10 后仍继续搜索/tap，没有改用 app drawer 或 `activate_app`。
- “For an installed app, obtain its package… use the observed client's supported options/activation API”：已有目标应用名，但没有走 activation fallback。

**是否需要新增通用规则：否。** 当前候选规则覆盖“验证目标应用/页面、非 clickable 候选、无进展重试、activation fallback”。这是候选规则与历史 frozen run 的事后对照，只能说明候选文本能针对该失败，不能证明原 agent 当时看到了这些指导或违反了当时可见的规则；也未证明遵循候选就能得到成功结果。唯一可讨论的补充是“当搜索表面返回重复/不可点击行且被系统对话框遮挡时，关闭对话框并改用 package activation”，但它只是上述规则的具体组合，且容易过拟合本机 launcher；不作为新规则建议。

## 边界与保留

- 不把 ASI 崩溃、搜索标签异样或 `finalText=null` 单独当成官方 0 的唯一原因；三者分别是环境证据、观察异常和 harness 转发边界。
- 未使用隐藏 evaluator 结果来指导 Agent；官方 0 只用于独立核对最终状态。
- 未修改冻结 campaign、manifest、result、raw、skill 或 proposal；未重跑、未重评、未补分。
