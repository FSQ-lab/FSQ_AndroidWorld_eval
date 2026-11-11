# 预算耗尽第 3 项：MarkorAddNoteHeader

## 结论

这是纯 Native 应用案例。正文添加成功且有精确读回，后续重命名路径探索失败，12个UI动作耗尽。它不是前两项网页点击/观察现象的重复，也没有出现输入异常。主要问题是对应用操作入口的猜测和不能区分目标阶段的等待条件。

通用方案可以覆盖错误等待与无进展识别，但不能代替模型找出正确的重命名入口。未验证更新skill是否能在12步内完成，不宣称本项已修复。本轮没有修改正式skill、Runtime或环境。

## 原任务与结果

- manifest index=23，seed=274419806，maxSteps=12。
- 在 Markor 打开 `2023_08_10_neat_wolf.txt`，在原正文前添加 `RnI8sP34yDzJQbvkfplR` 及一个空行，并重命名为 `busy_wolf_2023_07_23.txt`。
- 原执行：12/12 UI动作、17次python_exec、180.103秒；业务时间预算840秒，终止原因为step_budget。
- 官方reward=0。Agent最终如实报告partial、renameCompleted=false，没有错误宣告完成。
- session创建和退出各一次，远端缺席验证通过，任务teardown完成。

## 动作分账

|动作号|操作|证据|
|---|---|---|
|1–3|滑出应用抽屉、打开Markor、打开精确文件名对应笔记|进入DocumentActivity，读到正确文件名与正文|
|4–6|clear、send_keys、Save|读回内容精确等于标题文本＋两个换行＋原正文（含原有尾换行）|
|7–8|More options、File settings|实际进入Wrap words、Syntax highlighting等文档显示/格式设置；没有出现预想的Rename/Move/Delete|
|9–10|Back、点击笔记标题|仍是原笔记正文页；等待“有EditText”通过，但该EditText是原正文编辑器，不是重命名框|
|11|再次More options|菜单确实出现，但等待错误的android:id/title而超时；实际菜单标题ID为net.gsantner.markor:id/title|
|12|Back关闭菜单|随后第二个Back因预算耗尽被拒绝，仍在DocumentActivity|

**3 + 3 + 2 + 2 + 1 + 1 = 12。**所有12个已执行UI动作均HTTP200。重命名文本输入和重命名确认均未发生。

## 最早偏离与原调用锚点

行号相对原始 `episodes/023-MarkorAddNoteHeader/attempt-1/raw-private/agent-events.jsonl`：

- 1594（cell6）：打开正确笔记。正文为 `Weekend plans: Hiking trip to Blue Mountain.\n`，原正文EditText已存在。
- 1949（cell7）：尝试 `editor.set_value(new_text)`，报AttributeError，官方Client对象无该方法。尚未发生UI修改，不能把这个调用错误算成一个UI动作或Runtime故障。
- 2176（cell8）：改为clear＋send_keys，精确比较后点击Save。返回exactTextVisible=true。这里只证明编辑器读回与保存动作已发出；没有重新打开文件证明持久保存。
- 2382（cell9）：打开More options。等待“任意有text属性的节点数量>0”过弱，不是菜单已经出现的充分证据；本次实际返回了菜单观察。
- 2615（cell10）：点击File settings，然后等待Rename/Move/Delete。2883（cell11）的观察明确显示File settings、Wrap words、Syntax highlighting、Auto-format、Font Size、Format。这是第一个明确走错的操作分支，而不是点击没有响应。
- 3240（cell12）：Back后点击标题。标题节点此前显示clickable=false；点击返回200。随后只等任意EditText>=1，原正文编辑器本来就满足该条件，返回的仍是原标题与正文，没有证明进入重命名。
- 3391（cell13）：再次打开More options，等待android:id/title>0而超时。3642（cell14）却清楚显示已打开的菜单，五个菜单项的标题ID均属于net.gsantner.markor:id/title。这是等待条件的假阴性，不是菜单打不开。
- 3793（cell15）：连续两个Back，第一个执行、第二个被gate拒绝；4056（cell16）确认仍在DocumentActivity、标题未变、编辑内容仍可见。
- 4129（cell17）：quit成功。4217为Agent最终partial报告，明确renameCompleted=false。

## 原观察回放检查

直接用保存的原始观察执行对应谓词，见 [observation-predicate-replay.json](observation-predicate-replay.json)：

- 点击标题之前，“存在EditText”为true；之后仍为true。原条件无法区分进入新表单与停留原编辑器。
- 已打开的More options中android:id/title数量为0，而实际菜单项为File settings、Share、Tools、Info、Reload。错误ID等待会把成功打开菜单报成超时。
- 编辑器读回内容精确匹配本次请求的前缀及原正文。

这是一项实际执行的历史观察/谓词回放，不是新Android现场复现，不证明正确重命名路径或新skill效果。完整17次调用见 [original-python-executions.json](original-python-executions.json)。

## 对通用优化方案的检验

- **已适用**：检查条件必须能区分当前阶段和目标阶段。“任意EditText存在”与“非空文本存在”均可能被旧页面满足；这是BrowserMultiply中弱后置条件问题在Native界面的另一个表现。
- **已适用**：超时后观察真实状态，区分动作未生效与等待条件不成立。此处菜单已打开，只是期望了错误的ID；直接重试会增加无效操作。
- **已适用**：正文修改后精确读回是好的实践，可保留在一次脚本的clear/input/verify/save流程中，不需要拆成每步模型往返。
- **不应硬套**：该项没有证据支持输入焦点导致失败，也没有需要解释的WebView异步数值刷新。不能把所有失败归成同一个技术根因。
- **现有方案不保证**：找到正确重命名入口。File settings和点击标题都是未被当前证据验证的路径选择；状态验证能暴露偏离，但不自动产生正确计划。不新增Markor特定菜单路径作为通用skill规则。
- **不应额外归因**：set_value不存在属于Client API使用错误；它消耗一次Python调用但不消耗UI动作。没有证据要求增加兼容别名或修改Runtime。

## 本轮边界与下一步

原campaign、manifest、原始结果与调用保持只读。没有创建Appium session、改变设备数据、重启服务、放大预算或重跑官方任务；只新增单项证据与回放结果。真实应用正确重命名路径和更新skill后的任务成功率本轮未验证。

本项先停下来讨论，不自动进入下一项MarkorChangeNoteContent。
