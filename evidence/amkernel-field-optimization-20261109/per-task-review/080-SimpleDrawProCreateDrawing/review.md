# 预算耗尽项：SimpleDrawProCreateDrawing

## 结论

Agent 的总体路线是正确的：打开 Simple Draw Pro、新建画布、画了一笔、点 Save、把文件名设为 `adipiscing_fair_jelly_final.png`、进入设备存储下的 Pictures。真正阻止成功的是第 19 次 mutation：在 18/18 动作已用尽、harness 已发出 cleanup steer 之后，最后点击 SAVE 被预算 gate 拒绝（`UnknownMethodException`，消息被省略；audit 唯一 denied command 为 `step budget exhausted`）。文件是否落盘未被独立观察；evaluator=0 与 SAVE 被拒支持“未持久化”的推断 [INFERENCE]。

这不是单纯的模型路线错误，也不是单纯的 Appium 故障。前 10 个动作中有 7 个消耗在“启动器点击后应用没有前台化 → 重新搜索 → 观察到 Android System Intelligence 崩溃对话框 → 关闭/滑动恢复”这一串上；如果第一次启动就成功，SAVE 会在预算内。最后在 cleanup steer 之后仍尝试 SAVE，是对“预算关闭后不再做 UI mutation”契约的违反，但即使不尝试，也没有证据表明文件已持久化 [INFERENCE]。应分三层记录：应用启动未前台化及并发的系统环境异常 + harness 18 步硬边界；模型在超时后重试搜索的观察/规划次因；最终 post-steer 的 SAVE 尝试是明确的流程错误。

## 原任务与结果

- manifest index=80，task=`SimpleDrawProCreateDrawing`，complexity=1.8，maxSteps=18。
- 目标：在 Simple Draw Pro 新建绘图，命名为 `adipiscing_fair_jelly_final.png`，保存到 Pictures。
- 原执行：18/18 UI 动作，23 次 python_exec，220.077 秒；业务预算剩余约 980 秒；termination=`step_budget`，`cleanupRequested=true`。
- reward=0；`agentIndicatedDone=false`；`agentFinished=true`；`deniedCommandCount=1`。
- 原始最终自报（line 5272）：`{"taskOutcome":"incomplete","sessionCleanup":"completed","evidence":"Drawing created and filename set to adipiscing_fair_jelly_final.png; Pictures folder selected under device storage. Final SAVE action was rejected because the action budget closed, so file persistence was not verified."}`。自报没有夸大完成。
- 独立观察：line 4923 的 page_source 显示 Pictures 列表为空（`No items`），底部有目标文件名和 SAVE；line 5040 的 SAVE 请求失败；audit 拒绝原因为 `step budget exhausted`。文件是否存在未做独立设备文件系统读取；reward=0 与 denied SAVE 一致。

## 动作分账

|UI动作|内容|原始锚点|结果|
|---|---|---|---|
|1–2|启动器 Search、输入 `Simple Draw Pro`|cell4 / 1277|成功|
|3|点 Simple Draw Pro0 条目|cell6 / 1654|点击返回后才开始等待；package 未离开 launcher，等待超时|
|4–6|重新 Search、输入、点结果行|cell8 / 1951|再次等待 package 变化，超时|
|—|第三次搜索|cell9 / 2207|在第一个 wait 就超时，未提交 UI 动作|
|7|关闭 Android System Intelligence 对话框|cell11 / 2643|成功；对话框文本在 cell10 / 2467 观察到|
|8–9|两次滑动恢复桌面/进入应用列表|cell11 / 2643；cell12 / 2821|成功|
|10|点 Draw 图标|cell13 / 3004|Simple Draw Pro 前台化|
|11|画布滑动|cell15 / 3523|画了一笔|
|12|点 Save|cell15 / 3523|打开系统保存对话框|
|13–15|clear 文件名、输入目标名、点 OK|cell17 / 4028|进入 documentsui 保存选择器|
|16|点 Show roots|cell19 / 4490|进入根列表路径|
|17|点设备存储根 `sdk_gphone64_arm64`|cell20 / 4753|看到 Pictures 等目录|
|18|点 Pictures|cell21 / 4923|Pictures 为空，目标文件名已就绪|
|19（被拒）|点 SAVE|cell22 / 5040|拒绝：step budget exhausted；持久化未确认 [INFERENCE]|

**3 actions + 11 click + 3 input + 1 clear = 18；第 19 次 SAVE 被拒 1 次。** cell9 在第一个 wait 就超时，未提交 UI 动作；cell6/cell8 的等待失败发生在 click 之后，click 仍计动作；cell22 的错误类型是 `UnknownMethodException`，原始消息被省略，但 audit 的单一 denial 与它相邻，可归因于预算 gate。

## 最早偏离与决定性证据

- **line 1654（cell6）**：第一次点击 Simple Draw Pro0 后，等待 launcher package 改变超时；这是最早的可观察异常。此时已消耗 3 个动作。应用为什么没有前台化，原 raw 不能单独证明；line 2467 之后观察到 Android System Intelligence 崩溃对话框，提示环境干扰，但不是充分因果。
- **line 1951（cell8）**：Agent 没有先读取 cell7（line 1758）的 launcher 当前状态并处理异常，而是从搜索开始重做一遍；这次重试消耗 3 个动作，是本项最早的模型侧可避免浪费。line 2207（cell9）又在第一个 wait 就超时，未提交动作。现有方案的“无进展先区分、不要盲目重复”直接命中这里。
- **line 2467（cell10）**：观察到 `Android System Intelligence keeps stopping`；随后 line 2643 关闭对话框并滑动，line 2821 再滑动。该对话框证明运行中存在并发的系统环境异常，但原 raw 没有建立它导致首次启动失败的因果链；因此既不能把 7 个前置动作全部算成模型规划错误，也不能把该对话框当作已证明的根因。
- **line 3004（cell13）**：Draw 点击后应用才前台化。到此已用 10 个动作；剩余 8 个动作，而 Save 流程还需要 9 个（滑动、Save、clear、输入、OK、Show roots、存储根、Pictures、SAVE），预算结构上已经差 1。
- **line 4923（cell21）**：Pictures 已选中、无文件、目标文件名在字段中；业务前提已准备完毕。
- **line 4928（cleanup steer）**：harness 明确要求预算关闭后不再做 UI mutation。
- **line 5040（cell22）**：Agent 仍尝试 SAVE；这是第 19 次 mutation，也是唯一被拒绝的请求（audit: `step budget exhausted`）。若先前的启动重试少 1 个动作，SAVE 就会成为第 18 次并可能执行；但实际没有，且没有证据表明文件已持久化 [INFERENCE]。

## 独立回放与方案适用性

使用原始 stepBudget、raw 错误和 audit 做无设备回放，见 [observation-replay.json](observation-replay.json)：

1. 18 个 granted 动作的逐项映射与 stepBudget 的 3/11/3/1 计数一致；第 19 项正是 cell22 的 SAVE。
2. `deniedCommandCount=1`，原因 `step budget exhausted`；line 5040 的失败与它相邻，且原始错误消息被省略，不能把 `UnknownMethodException` 单独解释成应用拒绝保存。
3. 文件名、Pictures 选择、画布已创建均有文本观察；文件持久化没有独立设备读取，只能依据 evaluator=0 和 denied SAVE 作“未持久化”的推断 [INFERENCE]，不是文件系统实证。
4. 没有读取隐藏 evaluator 答案，也没有运行 Android/Appium。

与现有候选方案的对应：

- “无进展时先区分：异步更新、输入未生效、定位依据变化、目标/状态理解错误；不盲目重复操作”：直接适用。cell6 超时后应该先读当前页面/异常对话框，而不是 cell8 重新搜索。
- “等待应基于足以区分页面阶段的条件，不仅是 package/activity”：直接适用。package 变化等待没有覆盖“点击后未前台化，需要重新观察当前页面和并发的系统异常”的情形。
- “交互方式或定位依据尚未验证时先小批试探；确认效果后扩大批量”：部分适用。首次启动失败后应先小批验证应用是否真的前台，而不是重复整套启动流程。
- “预算关闭/偏离后停止，保留已完成阶段”：直接适用。Agent 保留了画布和文件名，但仍在 cleanup steer 后尝试 SAVE；正确做法是停止并如实报告。
- 方案不能覆盖：18 步硬预算、Android System Intelligence 崩溃对话框、第一次点击为何没有拉起应用。也不能保证在该预算下一定成功；本项说明“减少浪费”能改变结果，但需要一个动作的余量。

是否需要新增通用规则：**不需要**。现有“超时后观察、无进展不重试、阶段等待、偏离停止”已经覆盖本项可预防部分；专项修复应属于 harness/环境层，不应写进通用 skill。

## 不确定性与残留

- 截图图片负载未解码；画布、保存对话框、Pictures 空列表的结论均来自文本 page_source 和动作返回。
- `Simple Draw Pro0` 条目是否是唯一/正确图标、首次启动为何失败，原 raw 没有足够证据；崩溃对话框只能说明环境异常，不能证明唯一根因。
- 任务文本写 `sdk_gphone_x86_64 storage area`，实际 picker 根目录显示 `sdk_gphone64_arm64`，两者命名不一致；没有证据表明这导致失败，评估路径与 Pictures 选择仍应以原环境为准。
- 文件是否绝对不存在未做设备侧独立读取；保留“evaluator=0 + SAVE 被拒”的证据边界。
- 未修改原始 campaign/manifest/result/raw，未启动设备，未重跑，未产生新分数。
