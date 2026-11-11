# 预算耗尽第 1 项：BrowserMaze

## 当前结论

这项不是已经证明的“迷宫规划错误”或“AMKernel 执行失败”。Agent 从截图选出的 6 步路线本身可行，但连续 6 次 native WebElement.click() 返回 HTTP 200 后，X 仍在起点。直到改用当前按钮 rect 中心的坐标 tap，截图才证明 X 向右移动了一格。它在确认第一步是否生效前已花完六个方向点击，这是可确定的预算浪费。

底层为什么 element.click 没有推动网页状态，尚未独立现场复现；不能据此宣布 Appium 或 AMKernel bug 已确认。不能将随后三个只返回 package 的 tap 算作已证明有效移动。本项未修改代码、未修改预算、未重跑官方任务，没有新官方分数。

## 原任务与计数单位

- 目标：在文件管理器 Downloads 打开 task.html，选择 Chrome，使用方向按钮把 X 移到右下角。
- manifest index=3；browser_task_seed=1364588068，seed=3308742614。
- 原任务：20/20 gated UI actions，26 次 python_exec，官方 reward=0；session 创建 1 次、退出 1 次，远端缺席验证通过。
- Agent duration=285.088s，业务时间预算 1320s。触发的是 UI 动作预算，不是 26 次 Python 调用限制或墙钟超时。
- 原目录：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/003-BrowserMaze/attempt-1/`。

## 20 个动作如何花掉

|动作号|行为|可观察结果|
|---|---|---|
|1–4|滑出应用抽屉、Files、task.html、Just once|进入 Chrome 首次启动界面|
|5|Accept & continue|进入同步提示；仍是 FirstRunActivity，旧 activity 等待谓词错误超时|
|6|首次点击 No thanks|等待超时，下一观察仍有同步提示，未证明有效变化|
|7|改用 negative_button 资源 ID 点击 No thanks|退出 Chrome 回到 Files|
|8–10|再次打开 task.html、Just once、Keep Google|终于显示 Maze Puzzle|
|11–16|同一个 cell 连续 element.click：Right, Down, Right, Down, Down, Right|六次均 HTTP 200；之后截图证明 X 仍在左上角，页面几何尺寸发生变化|
|17|读取当前 Right.rect，点击其中心|截图证明 X 从第1行第1列移到第1行第2列|
|18–20|同样方式 tap Down、Right、Down|HTTP 200，只返回 package；没有位置快照，不能声称均已有效移动|
|21，未获准|再 tap Down|gate 因 budget exhausted 拒绝，不计作第21个执行动作|

**计数分解：10 个导航/首次启动动作 + 6 个无迷宫进展的 element 点击 + 4 个坐标 tap = 20。**

原始 `stepBudget.actions` 中 20 个动作全为 HTTP 200。另有一次切换 WEBVIEW 被 native-only 协议拒绝，没有消耗 UI action；最后一次 Down 才是预算拒绝。Appium audit 总计两条 denied commands，分别为 unsupported operation 和 step budget exhausted。

## 原始调用关键锚点

以下行号相对原始 `raw-private/agent-events.jsonl`：

- 1656：cell 7，Accept & continue 后等待离开 FirstRunActivity 超时。1805 行已显示 Turn on sync?，说明页面其实变了，等待条件不对。
- 1922 / 2078：首次 No thanks 点击与后续仍在同步提示的观察。
- 2384：资源 ID 点击之后返回 Files。
- 3232：尝试 WEBVIEW_chrome，原协议返回 Only native Android context is supported。
- 3465：原生可访问树列出方向按钮，Right.bounds=[418,842][562,918]。
- 3638：初始迷宫截图已发出，之后因猜测原生 resource-id=maze 查询失败；AMKernel 没有丢掉错误前已产生的图像。
- 3837：一口气执行六个方向 element.click；返回 mazeText=['X']。只看 X 字符存在并不能判断位置，不能作为完成证据。
- 3944：之后截图仍在起点。
- 4307：坐标 tap Right，rect={x:498,y:944,width:172,height:92}，截图 X 右移一格。
- 4516 / 4631 / 4746：后续三个 tap，仅 package 证据。
- 4863：再一次 Down 被预算限制拒绝。
- 4938：driver.quit 成功，官方记录已确认 session 缺席。

提取后的完整调用见 [original-python-executions.json](original-python-executions.json)；没有把全部 75MB 原始日志载入讨论上下文。

## 图像证据与独立重算

- [执行六步前](original-1-rawline-3638.png)：X 在左上角。
- [六个 element.click 之后](original-2-rawline-3944.png)：X 仍在左上角；格子与按钮显示尺寸比前图变大。尺寸变化是观察事实，其机制未确定。
- [一次坐标 Right tap 后](original-3-rawline-4307.png)：X 在第1行第2列。

根据截图可见的 4×4 网格与黑格，独立运行了离线坐标模拟：

`(0,0) → Right(0,1) → Down(1,1) → Right(1,2) → Down(2,2) → Down(3,2) → Right(3,3)`

该路线不穿黑格，6 步到达画面绿色目标。它来自截图，不是读取隐藏 evaluator 答案来代 Agent 完成。详细重算见 [diagnostic-facts.json](diagnostic-facts.json)。

如果六次方向输入都实际生效，保守沿用本次已经消耗的 10 个前置动作，合计只需 16 个动作。**这仅是证据支持的反事实预算分析，不是完成了 16 步官方重跑。**不能由此保证任意 Appium 输入都会成功。

## 分层归因

- **模型执行策略，确定**：没有逐步验证 X 位置；在未确认第一步生效时批量消耗六个 UI 动作。等待谓词过弱/不符页面生命周期，另尝试协议不支持的 WEBVIEW。
- **Appium/Chrome 输入与几何状态，现象确定、底层原因未定**：native element.click 全返回 200 但迷宫无进展；fresh rect 中心 tap 有图像证明的有效移动。页面缩放/几何、native WebView 节点点击实现、页面加载时序等尚未隔离，不能任选一个当根因。
- **技能指导**：应先做一次合法输入并核对 X 位置，确认后再执行短序列；状态不变就重新观察当前 bounds/页面几何，而不是把 HTTP 200 当移动成功。现有指导已补充业务后置条件，本轮未再添加未经现场验证的 click/tap fallback。
- **AMKernel Runtime/MCP**：这份记录没有证明调用丢失、kernel 死亡、异常前图像丢失或隐式重建。不改核心绕过它。
- **Harness/预算契约**：20 动作确实被正确计数、按约拒绝第21次；前置首次启动流程开销较大，但六次无进展输入是明确可避免的损失。没有修改计数单位、budget、evaluator 或重试政策。

## 本轮操作与待讨论点

本轮只读取原结果、原调用、原 Appium 审计，提取原图并运行离线状态重算；对当前服务/session 做了只读核对，没有新建 Appium session、重置 Chrome 或清空设备数据。原官方 BrowserTask.initialize_task 会清设备存储并清 Chrome 数据，不为求复现擅自调用它。

当前已定位“预算在哪里白花”，尚未定位“为什么这组 element.click 不推动网页”。后续若继续此项现场 A/B，应使用独立且不清共享数据的诊断页面，比较单次 element.click 与 fresh-rect tap 的实际状态变化、几何和 native 请求；不能以放大预算或把 tap 封装成静默兜底代替根因确认。

先停在这一项讨论，不自动进入下一项 BrowserMultiply。
