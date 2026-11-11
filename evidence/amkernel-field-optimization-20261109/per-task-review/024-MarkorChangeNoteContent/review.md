# 预算耗尽第4项：MarkorChangeNoteContent

## 结论

正文替换成功且精确读回；重命名入口探索失败。末次输入直接发给标题TextView，而不是已确认的重命名输入框，返回InvalidElementStateException。主要是规划与目标控件判断错误，不能把这个异常泛化成Appium输入故障，也不能仅靠给原标题聚焦来解决。

现有候选方案已经要求确认目标可编辑、验证目标阶段、偏离后停止，无需为本项新增规则或Markor特例。方案能覆盖无效输入前置条件与错误等待，不保证自动找到正确重命名路径或12步内成功。正式skill仍未修改。

## 原任务与结果

- manifest index=24，seed=1984626982，maxSteps=12。
- 在Markor将 `strong_jacket_h1hZ.txt` 正文替换为 `inNqu8UNNtyXBHCZpYp7`，并重命名为 `lively_fox_2023_03_22.md`。
- 原执行：12/12 UI动作、18次python_exec、165.458秒；业务时间预算840秒，termination=step_budget。
- reward=0。Agent最终报告partial、renameCompleted=false，没有错误宣告完成。
- 已执行动作11次HTTP200、1次HTTP400；没有另一个被拒绝的UI请求。第12次输入失败也消耗一次预算，随后进入清理。
- session创建和退出各1次，远端缺席验证通过，任务teardown完成。

## 动作分账

|UI动作|内容|结果|
|---|---|---|
|1–3|滑出应用抽屉、打开Markor、打开精确文件对应条目|进入正确笔记；等待完整带扩展名文件名超时，但后续观察显示无扩展名原标题和正文编辑器|
|4–6|clear、send_keys、Save|正文精确读回为目标内容|
|7–8|More options、File settings|菜单没有Rename；File settings是换行/语法高亮/格式设置|
|9–10|Back、点击标题|仍是原正文页；“任意EditText存在”的等待被正文编辑器满足|
|11|长按标题|观察仍为原标题TextView和正文EditText，没有已观察到的重命名表单|
|12|向原标题TextView发送新文件名|HTTP400，InvalidElementStateException；最后原标题未变，正文仍正确|

**3 + 3 + 2 + 2 + 1 + 1 = 12。**不存在的set_value方法报错不计入UI动作。

## 最早偏离与原调用锚点

行号相对原始 `episodes/024-MarkorChangeNoteContent/attempt-1/raw-private/agent-events.jsonl`：

- 1193（cell7）：打开指定文件后，等待完整字符串strong_jacket_h1hZ.txt出现在page_source，超时。1357（cell8）显示正确DocumentActivity、标题strong_jacket_h1hZ（没有.txt）、正文编辑器。等待依赖未验证的显示格式，不是打开失败的充分证据；Agent此后正确继续修改正文。
- 1566（cell9）：clear/send_keys/Save后等待全文精确匹配，返回目标正文。没有重新打开文件验证落盘，不能将此扩大成独立持久化证明。
- 1754（cell10）：打开More options后直接等Rename而超时。1898（cell11）列出实际菜单File settings、Share、Tools、Info、Reload。
- 2077（cell12）：进入File settings，返回Wrap words、Syntax highlighting、Auto-format、Font Size、Format。这是重命名路径的错误探索，不是点击失效。
- 2290（cell13）：返回后点标题，等任意EditText>0；原正文EditText早已存在，条件无法证明重命名界面出现。返回观察仍为原标题和已更新正文。
- 2483（cell14）：长按标题，返回的标题仍是android.widget.TextView，唯一观察到的EditText仍是正文编辑器。
- 2634（cell15）：title.set_value报AttributeError，未执行UI输入。2860行Agent推理仍考虑“试一下TextView是否能设置”。
- 2862（cell16）：title.send_keys(new_name)返回InvalidElementStateException，消耗第12次UI动作。原错误文字被省略；此前Runtime错误信息修复针对可诊断性，不把该TextView变成可编辑控件。
- 2981（cell17）：最后原标题未变，正文正确。3049（cell18）quit成功。3105行为如实partial报告。

## 独立检查与方案适用性

使用保存的原始观察执行谓词/目标检查，见 [observation-predicate-replay.json](observation-predicate-replay.json)：

1. 点击标题之前与之后，“存在EditText”均为true；原谓词不能区分目标阶段。
2. 长按后发送输入的目标class=android.widget.TextView；已观察到的EditText是正文编辑器，不是重命名输入框。
3. 最终正文精确匹配请求，原标题仍旧。

这是历史观察回放，不是新的Android现场复现，不证明正确重命名路径或更新skill收益。完整调用见 [original-python-executions.json](original-python-executions.json)。

与现有候选方案的对应：

- “输入前确认预期可编辑目标，再确认焦点”：直接适用。应先识别真正的重命名表单，不是把焦点强行落在原标题或对任意EditText输入。
- “验证目标阶段而非泛化控件存在”：直接适用。正文EditText不能充当进入重命名的证据。
- “超时后观察真实状态”：直接适用。打开文件和菜单均有动作成功但假设不成立的情况。
- “保留批量”：正文修改、精确读回和保存可以继续在一次Python调用内完成，不必退化成单步工具。
- “不确定时不要盲试”：原目标已显示为TextView，单击与长按都未观察到目标阶段，不应再因尚有一次预算就试send_keys。

上述都属于现有方案，不新增规则。识别并选择正确重命名入口仍是模型规划任务，没有据此新增兼容API、自动重试、固定菜单路径或Runtime修改。

## 本轮边界

原campaign、manifest、原始结果和调用保持只读。没有创建Android/Appium session、清数据、重启共享服务或运行新官方任务。只新增单项分析及原观察回放证据。按预算耗尽类原顺序，下一项是index=28的MarkorCreateNoteFromClipboard，本轮不自动进入。
