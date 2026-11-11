# 预算耗尽第 2 项：BrowserMultiply

## 结论

与 BrowserMaze 可以共用“保留批量、验证进展、偏离停止”的方案，但这项原脚本已经有 WebDriverWait；问题是检查条件过弱且不覆盖阶段切换，不能仅要求“加等待”。它还揭示了读取初始状态、保留部分证据和区分重复新值/陈旧值的重要性。

尚未定位原生点击/可访问性刷新时序问题的底层机制；未修改正式 skill 或 Runtime，未启动 Android 任务重跑。桌面浏览器诊断只验证原页面语义和方案边界，不是新的官方成绩。

## 原任务与结果

- manifest index=4，BrowserMultiply；browser_task_seed=3143940091，seed=1325351943，maxSteps=22。
- 目标：在 Downloads 打开 task.html，选择 Chrome；点击按钮五次，记住显示的数字，输入它们的乘积。
- 原执行：22/22 UI actions，35 次 python_exec；331.671s，业务时间预算1440s。termination 位于 agent.termination.reason=step_budget，不是顶层 termination。
- 官方 reward=0。Agent 没有宣告完成。创建/退出 session 各1次，远端缺席验证通过，任务 teardown 完成。
- 原目录：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/004-BrowserMultiply/attempt-1/`。

## 动作分账

|UI动作|内容|证据|
|---|---|---|
|1–10|启动 Files、文件打开、Chrome 首次启动/同步/搜索引擎提示与重新打开文件|第10步后开始操作 Memory Task|
|11–15|批量五次原生按钮点击|HTTP200；读取数字列表为 [9,9,9,9,9]，但稍后页面显示10且按钮仍在，没有进入预期表单|
|16|试图上滑找表单|前后仍为数字10和 Click Me，没有找到表单|
|17–20|又批量四次点击，每次 sleep(1.0) 后等数字非空|最后一次执行进入表单阶段，但脚本继续等已经隐藏/不存在的数字节点，TimeoutException|
|21|直接向 answer.send_keys('65610')|HTTP400，InvalidElementStateException；后续观察字段未聚焦，仍为 Enter the product|
|22|点击 answer 并等 focused=true|点击成功、等待通过；下一条 send_keys 才被 budget gate 拒绝，未执行|

**10 + 5 + 1 + 4 + 1 + 1 = 22。**原记录一共发出9个 Click Me 点击，不等于已经证明页面接收了9次有效点击。

另有不消耗UI动作的失败：缺少 lxml 后改用标准库；Files ancestor XPath 找不到节点；AppiumBy.ID('button') 不能定位，而按树中精确 resource-id 的 XPath 可以定位；切换 WEBVIEW 被 native-only 协议拒绝。不能把这些全部算成 UI 预算损失。

## 最早偏离与关键调用

行号相对原始 `raw-private/agent-events.jsonl`：

1. **4688，cell24：初始可见数字9已经在树中。**后续没有把初始值纳入可靠的观察账本。
2. **4856，cell25：原生 ID 定位失败，没有执行点击。**5087行通过 XPath 查到了 number=9 和 Click Me。
3. **5380，cell27：五次批量点击中的检查为数字文本非空。**它从第一轮起就可能被旧的9立即满足，结果 [9,9,9,9,9]、product=59049。请求成功和文本可读不能证明得到的是本次动作后的结果。
4. **5771，cell28：page_source 显示10与 Click Me。**此前的观察不足以还原每次点击后的数字，原 Agent 自己也提出可能丢失了中间值。6055行上滑后仍为10和 Click Me。
5. **6585，cell30：effective_numbers=[10]，又循环四次点击。**检查仍只接受非空数字，没有接受“表单出现”的分支。最后等数字超时；6975行明确显示 form、answer、Submit，number和button不再出现在可访问树。这是正常阶段切换，不是证明页面没响应。
6. **7816行原 Agent 推理、7818行cell32：开始猜乘积65610并尝试输入。**原 Agent 不确定实际记录了哪些数字，提出59049或65610作为候选；没有先读取持久命名空间中的 effective_numbers。该列表可能保留了异常前的数据，但原记录没有读取，不能补报其内容或保证它足以救回任务。
7. **7975，cell33：answer为EditText、enabled/focusable=true、focused=false，文字仍是提示语。**8266行点击聚焦后，下一次输入被预算拒绝。8336行quit成功。

原始35次 Python 调用与结果见 [original-python-executions.json](original-python-executions.json)。

## 独立页面语义复现

将当前仓库 `android_world/android_world/task_evals/single/browser.py` 中 BrowserMultiply 的原 HTML 替换为原 seed，在独立桌面浏览器标签页运行。没有改页面处理函数、生成算法或种子，没有访问隐藏的 numbers/clickCount 来完成交互；只通过可见数字、控件可见性、输入框和按钮操作。

|点击次数|可见数字|表单可见|
|---|---|---|
|0|9|否|
|1|10|否|
|2|9|否|
|3|5|否|
|4|5|否|
|5|数字区隐藏|是|

观察得到的五个数为9、10、9、5、5，Python计算20250，填入并读回后提交，页面显示 Success!。这与原 Agent 猜测的65610不同，但**它是独立桌面页面复现，不是原 Android 中间画面的完整录像或新官方reward**。

它证明三点：

- 初始数字在第一次点击前就存在，需要保留。
- 相邻有效点击可以产生相同数字：因此不能把“必须不同于旧值”作为通用等待条件。
- 第五次点击应隐藏数字与按钮并展示表单：因此不能一直等旧数字节点。

五次点击及阶段观察在一次 Python Eval 中完成，不要求每步模型往返。第一次诊断对后续值作了错误的9假设，断言失败；检查已完成的真实观察得到5、5后修正断言，继续使用原标签页，没有重新跑成功的点击前缀。真实结果和这一诊断纠正保留于 [desktop-page-semantics-smoke.json](desktop-page-semantics-smoke.json)。页面截图见 [desktop-page-success.png](desktop-page-success.png)。标签页已关闭。

**未覆盖：Android Chrome、Appium native element.click、可访问树刷新延迟、冻结 Agent 遵循新 skill 的能力。**因此不能把桌面成功宣称为原生点击问题已修复。

## 共用方案如何调整

|候选规则|本项结论|
|---|---|
|交互未验证前先小批试探|适用；先确认输入与读取方式可信，不直接五次消耗|
|脚本内反馈，减少模型往返|适用；已有可靠页面信号时，用阶段分支控制循环|
|读到了内容就是进展|不成立；旧9可以立即满足非空条件|
|数值没变就是无进展|不成立；本页面合法输出可以重复|
|检查数字更新或下一阶段出现|适用；表单出现是成功阶段切换，不是等旧控件超时|
|批量异常后保留并恢复部分结果|适用；利用持久Python命名空间先读取已有列表，不立即猜答案或重新点击|
|现有规则足以解决所有问题|不成立；输入聚焦、原生点击/读取时序和观测歧义仍需独立验证|

缺少可区分旧值/重复新值的信号时，应保留不确定性，不能为“确认”而盲目再点击。只增加sleep或只增加WebDriverWait不构成通用修复。

## 分层归因

- **模型/技能，明确**：非空检查没有因果关联；没有覆盖阶段切换；没有可靠保存初始及中间证据；部分执行后未查询现存数据而猜答案；无表单证据时试图滚动；输入前未验证当前字段交互状态。
- **Appium/Chrome，待定**：批量读取旧值、后续10才出现在树中，说明需要隔离输入与观察时序，但不能仅据此宣称点击丢失或具体缓存缺陷。
- **Runtime既有可诊断性缺陷**：本项也出现InvalidElementStateException消息被省略；此前已实施的错误信息修复针对可诊断性，不会自动恢复数字或修复页面输入。
- **Harness/评测契约**：预算按22次交互消耗，包括HTTP400输入；第23次交互被拒绝。页面第五次点击展示表单，与Agent继续等数字的假设不同；无证据支持修改任务、预算或evaluator。

## 本轮边界

未改正式 skill、依赖、模型、冻结安装、campaign、任务参数、预算、重试或 evaluator。未创建 Android/Appium session、未清 Chrome 数据、未重启共享服务。只新增方案和诊断证据。下一项是 MarkorAddNoteHeader，本轮不自动进入。
