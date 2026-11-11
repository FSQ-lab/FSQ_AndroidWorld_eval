# 预算耗尽第5项：MarkorCreateNoteFromClipboard

## 结论

创建笔记并执行Paste的证据存在，但粘贴只替换了Agent自行插入的测试文字中的一个单词，留下无关后缀。Agent仅验证“文本变了”，随后点击Save并最终报告completed，没有验证正文是否完整来自剪贴板。

这项主要属于模型执行策略和业务后置条件不足；同时原截图证明浮动文字菜单有可访问树未呈现的信息，应按已有观察原则用图像补证，不能把树里没有Paste当成界面没有Paste。没有证据要求修改Runtime。现有候选方案已经涵盖图像补观察、目标状态验证及无进展诊断，不为此新增benchmark特例。

## 原任务与结果

- manifest index=28，seed=1852838440，maxSteps=14。
- 用户目标：创建名为 `2023_09_08_active_umbrella.txt` 的Markor笔记，在笔记中执行粘贴并保存。
- 原执行：14/14个UI动作、21次python_exec、292.086秒；业务时间预算960秒，termination=step_budget，官方reward=0。
- 原Agent最后JSON写taskOutcome=completed，但stepBudget.agentIndicatedDone=false。这里区分最终文本自述和Harness标志，不能用任一字段覆盖另一个。虽然按预算类归档，该项也存在完成判断过宽。
- session创建和退出各1次，远端缺席验证通过，任务teardown完成。

## 动作分账

|UI动作|内容|观察|
|---|---|---|
|1–3|滑出应用抽屉、打开Markor、Create a new file or folder|出现名称、扩展名输入框|
|4–8|clear/input名称、clear/input扩展名、OK|创建后进入DocumentActivity；标题省略.txt，导致等待完整文件名超时，但正文为空且已聚焦|
|9|空白编辑器长按|等Paste超时，随后树中未见Paste；没有同期截图，不能确认该次是否实际出现菜单|
|10|输入active umbrella作为临时文字|读回精确为active umbrella|
|11|长按文本|树中未列Paste，但稍后原截图显示浮动菜单与选中的单词active|
|12|根据截图点击Paste坐标|正文变为ILRmaKdNIH umbrella；只替换了选中单词，保留后缀|
|13|点击Save|正文仍为ILRmaKdNIH umbrella；没有观察到Saved提示|
|14|Back并等MainActivity|等待超时；没有最终文件列表或重新打开文件的证据，随后quit|

**3 + 5 + 1 + 1 + 1 + 1 + 1 + 1 = 14。**全部已执行动作均HTTP200，没有另一个被拒绝的UI动作。预算耗尽不是最终正文错误的充分解释：错误正文已在第12步明确出现，原Agent仍继续保存并宣告完成。

## 原调用关键锚点

行号相对原始 `episodes/028-MarkorCreateNoteFromClipboard/attempt-1/raw-private/agent-events.jsonl`：

- 1011（cell3）：从不存在的appium.webdriver.common.action_chains导入失败；1239（cell4）改用Selenium导入成功。这不消耗UI动作，不是Runtime丢失能力。
- 2232（cell8）：Agent读了名称和扩展名字段的焦点，名称已focused=true。2331（cell9）检查官方Client方法，确认只有clear、send_keys，没有猜set_value。这些是较好的诊断动作。
- 2662（cell10）：名称/扩展名填写后创建，等待完整文件名超时。2882（cell11）显示标题不含扩展名，空正文EditText已focused=true。3084（cell12）再次确认该字段已聚焦。
- 3460（cell13）：空白处长按后等待Paste超时；3671（cell14）树中仍无文字浮动菜单。
- 3948（cell15）：自行插入active umbrella；这是开始污染最终目标状态的位置。临时文字本身不是必然错误，但后续必须恢复，不能让其残留在交付正文。
- 4208（cell16）：长按，返回树里仍没有Paste等菜单项。4371（cell17）发出截图，明确显示Cut、Copy、Paste、Share、Select all，且只有active被选中，umbrella未选中。
- 4571（cell18）：点击截图中Paste坐标，等待条件仅为正文不等于active umbrella。返回ILRmaKdNIH umbrella。这个条件证明变化，不证明最终正文正确。
- 4902（cell19）：Save后正文仍有umbrella后缀；saveAcknowledgement=[]。没有提示不能据此断定保存失败，但点击Save也不能替代文件读回。
- 5113（cell20）：Back后等MainActivity超时；没有返回最终文件列表。5197（cell21）quit成功。
- 5267：最终JSON自述completed，依据仅为执行了Paste、Save被激活、正文仍可见；没有指出残留测试文字。

完整调用见 [original-python-executions.json](original-python-executions.json)，原始截图提取见 [original-selection-before-paste.png](original-selection-before-paste.png)。截图哈希与原MCP display元数据一致。

## 任务与评测契约

读取源码仅用于独立解释官方判定，不给Agent提供隐藏答案或替代真实粘贴：

- `android_world/android_world/task_evals/single/markor.py:480-492`：初始化将file_content放入剪贴板，并检查设置正确；本例参数为ILRmaKdNIH。
- 同文件475-478、494-496：最终委托CreateFile检查指定文件名与正文。
- `task_evals/common_validators/file_validators.py:199-226`：检查文件存在，读取正文，再用fuzzy_match比较，不是仅检查Paste是否被点击。
- `utils/fuzzy_match_lib.py:20-51`：忽略大小写的SequenceMatcher阈值为0.9，并非严格字节相等。

对原观察正文运行同一个纯匹配函数：ILRmaKdNIH umbrella与ILRmaKdNIH相似度约0.6897，返回false。这说明若保存为所观察正文，会不满足官方内容条件。**未独立读回原设备文件，不能断言这是官方失败唯一条件，或已证明最终落盘内容。**

## 独立原观察回放

[selection-and-postcondition-replay.json](selection-and-postcondition-replay.json)记录实际执行的检查：

1. 原图显示active被选中；在active umbrella中只替换active，结果精确等于原返回的ILRmaKdNIH umbrella。
2. “文本不等于原测试文字”的旧等待为true，但无关后缀仍存在。
3. 原编辑器在第一次长按前已focused=true：本项不能归结为未聚焦。
4. 运行原纯内容匹配函数，原观察正文不满足阈值。

没有新的Android交互、没有官方重跑、没有通过隐藏file_content直接填写来制造成功。上述是原截图、原返回值和纯匹配函数的诊断回放。

## 对现有通用方案的检验

- **观察覆盖**：可访问树未给出浮动菜单时，图像可以补证。本例不是“Appium没有Paste能力”，原图与粘贴后的值已证明实际执行。
- **预期业务状态**：文本发生变化不足以代表正确完成。应判断选择范围和粘贴对完整正文的影响；临时探测内容不能未经恢复就当最终交付。
- **不依赖隐藏答案**：Agent无需读取file_content参数才能发现问题。它知道自己插入了active umbrella，且截图显示只选中active；保留的umbrella来自自己的探测，不是目标要求。
- **输入前置条件**：本项正文已经聚焦，输入成功；不应额外归因焦点或重复加一次点击。
- **批量能力**：有可靠选择范围/内容条件时，操作和验证可以在脚本内完成；无法从树判断时在关键点返回截图，不要求所有动作逐次模型往返。
- **边界**：图像补观察和最终业务验证属于已有候选原则，本轮不添加专门的Select all路线、固定坐标、静默重试或Runtime逻辑。正确粘贴路径和14步内成功仍未通过新Agent重跑验证。

## 本轮操作与清理

原campaign、manifest、原结果和调用保持只读；提取原图并核对哈希，运行原观察回放和纯文本比较。没有创建Android/Appium session、清数据、重启服务、修改模型/预算/evaluator或正式skill。先停在本项讨论，不自动进入下一项。
