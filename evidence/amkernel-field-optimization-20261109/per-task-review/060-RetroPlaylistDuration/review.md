# 预算耗尽项：RetroPlaylistDuration

## 结论

播放列表“Reggae Rhythms 51”确实创建成功，最终观察到 **12 Songs • 01:01:13**；总时长 3673 秒，高于 45–50 分钟（2700–3000 秒）的上界 673 秒，因此业务后置条件不成立。Agent 如实报告 incomplete，没有错误宣告完成。

主因是规划/观察边界：在没有任何单曲时长证据的情况下，cell20 一次批量点选 9 个可见标题（加上先前长按的一行达到 “10 selected”），cell25 又追加 2 首达到 “12 selected”，直到 cell27 才第一次读到总时长。此时已超出范围，打开列表修正的 cell28 又被预算拒绝。次要因素才是 Appium/应用 API 的摩擦（cell12 的 `NoSuchElementException`、cell21 的 `TypeError`，二者都没有消耗 UI 动作配额）以及 30 步硬预算。不能把本项归成单一 harness 原因：超出范围在选择阶段已经形成，调整失败只是让错误无法挽回。

## 原任务与结果

- manifest index=60，task=`RetroPlaylistDuration`，complexity=3，maxSteps=30。
- 目标：用给定歌曲在 Retro Music 创建名为 `Reggae Rhythms 51` 的播放列表，总时长在 45–50 分钟之间。
- 原执行：30/30 UI 动作，29 次 python_exec，335.385 秒；业务预算仍有约 1584 秒；termination=`step_budget`，`cleanupRequested=true`。
- reward=0；`agentIndicatedDone=false`；`agentFinished=true`。
- 原始最终自报（line 7717）：`{"taskOutcome":"incomplete","sessionCleanup":"completed","evidence":"Playlist 'Reggae Rhythms 51' was created with 12 songs, but its observed duration was 01:01:13, outside the required 45–50 minutes. Action budget closed before adjustment. driver.quit() returned successfully."}`。自报与 line 7208 的独立观察一致。

## 动作分账

|UI动作|内容|原始锚点|结果|
|---|---|---|---|
|1–2|启动器搜索 Retro Music 并输入|cell4 / 1105|成功|
|3|打开 Retro Music|cell5 / 1314|成功|
|4|打开 Playlists|cell7 / 1907|成功|
|5|More options|cell8 / 2064|成功|
|6|tap New playlist|cell10 / 2459|弹出新建对话框|
|7–8|输入名称、点 Create|cell11 / 2814|创建 `Reggae Rhythms 51`，当时 `0 Songs • 00:00`（cell14）|
|9|打开刚创建的播放列表|cell14 / 3646|成功|
|10|More options|cell15 / 3737|进入歌曲库路径|
|11–13|Back、Navigate up、Songs|cell17 / 4324|进入 Songs，列表只有标题/艺人，没有时长字段|
|14|长按第一行进入选择|cell18 / 4699|进入 selection|
|15–23|批量点选 9 个可见标题|cell20 / 5282|等待到 `10 selected`；`visible_titles` 为 City of Stars、Endless Summer、Eternal Flame、Falling Feathers、Forever Young、Golden Days、Heartbeat Away、Hidden Paths、Moonlight Sonata|
|24|滑动歌曲列表|cell22 / 5804|露出更多标题；cell23 读到 Return to Paradise、Silent Dreams 等|
|25–26|追加 Return to Paradise、Silent Dreams|cell25 / 6401|等待到 `12 selected`|
|27|More options|cell25 / 6401|成功|
|28|tap Add to playlist|cell26 / 6712|出现 Add to playlist 对话框，含 `Reggae Rhythms 51`|
|29–30|点目标播放列表、点 Playlists|cell27 / 7208|读回 `12 Songs • 01:01:13`|
|31|尝试打开播放列表准备修正|cell28 / 7472|失败；无 UI 动作被接受，`UnknownMethodException`，消息被省略；audit 只有 1 个 denied command：`step budget exhausted`|

**23 click + 4 actions + 2 input + 1 back = 30；1 次请求被拒绝。** cell12/21 在提交动作前失败，不计 UI 动作；cell19 只是回到播放列表页，也未计动作。

## 最早偏离与决定性证据

- **line 4324（cell17）**：Songs 列表的已知文本只有标题和艺人（`title`/`text`），没有 `mm:ss` 时长字段。Agent 在这个不满足“时长可计算”前提的页面上继续。
- **line 5282（cell20）**：这是最早真正把错误状态提交下去的动作——批量点选 9 个标题，加上先前长按达到 `10 selected`；代码没有任何单曲时长读取或总时长检查。Agent 当时可见的只有标题和选中状态；“每首歌属于什么类别”不是它可用的证据，也没有改变本项归因。
- **line 6401（cell25）**：再追加 2 首到 `12 selected`，把超出范围的选择继续扩大；此后的 More options/Add to playlist 已经依赖这个错误选择。
- **line 7208（cell27）**：第一次得到业务证据 `12 Songs • 01:01:13`。3673 秒不在 2700–3000 秒内，证据明确否定了目标状态。
- **line 7213（cleanup steer）**：cell27 读到总时长后，harness 关闭预算并要求不再做 UI mutation。
- **line 7472（cell28）**：尝试打开列表修正时，第 31 次 mutation 被拒绝；audit 的唯一拒绝原因正是 step budget exhausted。修正机会在错误已经形成、预算关闭之后才出现，不能把 61:13 说成只是预算造成。line 7717 的最终自报如实承认失败。

## 独立回放与方案适用性

使用原始观察和 stepBudget 做无设备回放，见 [observation-replay.json](observation-replay.json)：

1. `12 Songs • 01:01:13` → 12 首、3673 秒；要求区间 2700–3000 秒；`withinRequiredRange=false`，超上界 673 秒。
2. cell17 的歌曲列表没有时长字段（`songListShowedDurationField=false`）；第一次时长观察出现在 cell27。
3. UI 动作数 30/30，且只有 1 个 denied request；动作分账与 stepBudget 的 23/4/2/1 计数一致。
4. 没有读取隐藏 evaluator 答案，也没有运行 Android/Appium；结论完全来自原观察。

与现有候选方案的对应：

- “状态可由已有且可靠的文本/属性判断时，脚本内批量、逐阶段验证；偏离即停止依赖它的后续动作”：直接适用。这里应先把“总时长尚未知”当作未验证前提，不能先把 12 首全部提交。
- “执行前明确预期可观察业务变化；HTTP 200/无异常不能替代业务证据”：直接适用。选择模式显示 `10/12 selected` 不是 45–50 分钟的业务证据；cell27 的总时长才是。
- “批量方式选择：交互/定位依据尚未验证先小批试探”：部分适用。真正缺的是“聚合属性（总时长）必须先取得当前值，再决定是否扩大批量”，而不仅是点击定位是否可靠。
- “偏离后停止/保留已完成阶段”：适用但来得太晚；cell28 才尝试修正，预算已关闭。
- 方案不能覆盖：Songs 列表本身不显示时长，现有技能没有可靠方式凭空得到每首歌时长；也不能保证在 30 步内完成修正式的搜索。不能为某个应用添加特定菜单路线或隐藏参数查询。

是否需要新增通用规则：**不需要为本项强行新增**。现有“聚合/业务后置条件 + 批量前确认可观察状态 + 偏离停止”已经覆盖了主要可预防部分；如果后续跨案例继续出现“加法/区间目标先提交大批量”，可考虑把“聚合目标先读当前聚合值并预留一次修正”作为最小澄清，但本项单独不足以证明新规则的通用收益。正式 skill 未修改。

## 不确定性与残留

- 最终 12 首的完整标题清单没有被最终页面独立读回；我们能确认的是 12 首、总时长 61:13，以及 cell20/23 观察到的部分标题。因此选择范围的具体构成仍不完整，长按首行的确切标题也未被后续页面独立确认。
- 截图内容（cell9/15/16/19/25 等）是图片负载，未解码为证据；菜单状态结论依据文本 page_source。
- 未修改原始 campaign/manifest/result/raw，未启动设备，未重跑，未产生新分数。
