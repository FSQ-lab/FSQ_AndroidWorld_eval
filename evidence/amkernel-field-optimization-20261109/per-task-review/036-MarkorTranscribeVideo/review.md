# 预算耗尽第6项：MarkorTranscribeVideo

## 结论

视频是24秒的短时序观察任务。前半程逐次查询和模型往返期间播放持续推进，看到0:15的控制条后，下次暂停查找时控件已不存在，随后已回到Files。第二次播放时Agent改为一次Python调用连续采集35帧并拼图，是AMKernel批量能力的正面用法。

但前置导航、重播和Launcher恢复已消耗较多动作，进入Markor创建弹窗时只剩2个动作；只清空并填完名称，下一次清扩展名被预算拒绝，未创建目标文件、未输入转录、未保存。没有证据表明ext.clear不受支持或输入焦点造成了本次中断。

现有方案的阶段验证、脚本内批量和恢复部分数据仍适用。建议讨论把“短暂连续内容先在本地脚本连续采集、留时间戳，再返回模型分析”明确为批量原则的具体模式，不改成每帧往返模型。本轮只记录证据，不修改正式skill或候选方案。

## 原任务与结果

- manifest index=36，seed=1222528574，maxSteps=20。
- 通过VLC观看Download中的 `ZwUN_moment_70_.mp4`，把画面字符串依次转录为逗号分隔列表，写入Markor文件 `ZwUN_moment_70__transcription.txt`。
- 原执行：20/20 UI动作、41次python_exec、426.039秒；业务时间预算1320秒，termination=step_budget，官方reward=0。
- 20个已执行动作均HTTP200，另一次ext.clear被预算gate拒绝，rejectedActionCount=1。最终Agent报告incomplete_action_budget_closed，没有错误宣告完成。
- session创建和退出各1次，远端缺席验证通过，任务teardown完成。

## 20个动作的去向

|动作号|内容|结果|
|---|---|---|
|1–5|应用抽屉、Files、Videos筛选、Search、输入文件名|筛选后未直接找到文件，搜索后确认目标文件名|
|6–9|打开视频、选择VLC、Just once、关闭VLC教程|进入播放器；画面持续随时间推进|
|10|点击播放器显示控制条|观察到0:15 / 0:24、Pause；下一次查找暂停控件已失败，未执行暂停点击|
|11–12|重新打开视频、Just once|重播后在单次Python中采集35帧，约24秒|
|13–17|Home、滑动、Back恢复Launcher、再滑动、打开Markor|第一次滑动未找到Markor，恢复后进入Markor|
|18|Create a new file or folder|出现新文件对话框，默认my_note、.md|
|19–20|清空名称、输入目标名称主体|下一步ext.clear被预算拒绝，OK、正文输入和保存均未执行|

**5 + 4 + 1 + 2 + 5 + 1 + 2 = 20。**逐一将原代码、异常栈和stepBudget.actions种类对齐，避免把失败查找误算成实际点击。映射见 [state-and-action-replay.json](state-and-action-replay.json)。

## 最早偏离与关键调用

行号相对原始 `episodes/036-MarkorTranscribeVideo/attempt-1/raw-private/agent-events.jsonl`：

- 540（cell2）：从IPython导入display失败；715（cell3）使用已有display成功。993（cell4）滑动后才因AppiumBy未定义失败；会保留已经完成的滑动，不能认为整个cell未执行。
- 2182（cell12）：Videos筛选后等目标文件超时，之后改搜索。2629（cell14）等待任何节点包含查询串，返回的是输入框自身，不是搜索结果；2714（cell15）才单独确认真实目标文件。这是此前“泛化存在条件”在新界面的重现。
- 3190（cell18）：选择VLC并进入VideoPlayerActivity。3458（cell20）看到Video player tips，3574（cell21）关闭教程并确认消失。
- 3985（cell23）：点击显示控制条，返回0:15 / 0:24、Pause。4155（cell24）查找暂停控件在第1行即NoSuchElement，没有暂停点击发生；4367（cell25）stdout已是Files，在查player_root时失败。原轨迹与视频播放结束/退出相符，不是已确认的控件点击失效。
- 4706（cell26）：再次打开文件成功，但假定选择器仍含独立VLC选项，查找VLC失败。4886（cell27）实际选择器为Open with VLC、Just once、Always，随后正确仅点Just once。
- 5433（cell28）：点击Just once后，循环35次截图，按0.7秒目标间隔采样，保存frames与sheets。最后直接display(PIL.Image)报DisplayError: content must be bytes-like，采集并未因此回滚。
- 5547（cell29）：复用已有sheets，编码JPEG bytes再display；返回captured=35、elapsed=23.9993秒、三个display元数据。没有重播或重采，利用了持久命名空间。
- 5722（cell30）：Home和滑动已执行，随后等Markor超时。6065（cell33）Back并换滑动后确认Markor可见；6170（cell34）进入Markor。
- 6454（cell36）：打开新文件对话框。6596（cell37）猜测set_value方法，AttributeError，未执行输入；6718（cell38）确认name=my_note、ext=.md、名称已聚焦、扩展名未聚焦。
- 6989（cell39）：name.clear和name.send_keys执行完后，栈定位第3行ext.clear，返回UnknownMethodException。结合原gate计数，属于预算拒绝，不是证明clear方法不可用或扩展名输入失败。
- 7213（cell40）：在原对话框观察字段，返回tuple列表只有bounded repr，实际值没有展开；没有后续精确读回。7296（cell41）quit成功。

完整调用见 [original-python-executions.json](original-python-executions.json)。

## 证据边界：不能声称已独立看清转录内容

本轮成功提取并核对哈希的原图只有两张：

- [Files列表](original-image-1-rawline-2342.png)
- [尚未填名称的新文件对话框](original-image-2-rawline-6718.png)

其他7个inline image字段（包括三个转录拼图）在归档JSONL中含省略号，base64已截断，不能完整解码。原display元数据有大小和sha256，但不是完整图像。提取失败与元数据已记录于 [image-extraction.json](image-extraction.json)。没有用截断数据生成伪完整截图，也没有把归档截断归因于AMKernel发送失败。

原Agent最终自述首词为Mario，任务参数首词为Maria；由于本轮无法完整复核原拼图，只能记录这处不一致，不能假装独立确认每帧文字或将识别错误定为唯一根因。没有读取隐藏答案来替Agent完成转录。

## 原观察与动作回放

实际执行的回放核对：

1. 20个推导动作类型与原stepBudget.actions完全一致。
2. 暂停查找在cell24第1行失败，没有实际暂停动作；后续观察已是Files。
3. 原捕获结果确认为35帧、约24秒、三个图像display；display报错后的恢复复用已有数据，未重做UI操作。
4. 末次输入批量在cell39第3行ext.clear被截断；之前两个名称动作正好耗尽20步，之后步骤未执行。
5. 两张可恢复原图的sha256与原display元数据一致。

这不是新Android现场复现，不证明更新skill后20步内能成功。

## 对通用优化方案的判断

- **保留批量能力：强支持。**短时序画面不能把每帧都交给模型后再继续采集。原第二次播放的连续采样体现了正确方向，不应被“每步确认”规则破坏。
- **值得明确的执行模式：先采集、后解读。**对会消失的时序证据，在允许的截图接口上连续采样并带时间戳，处理完遮挡后及时开始；采样覆盖和可读性仍要验证，固定0.7秒不是通用答案，也不保证不漏帧。是否补进候选方案留待本项讨论。
- **阶段验证仍适用。**搜索词出现在输入框不等于文件结果出现；重新打开的Resolver不能假定与第一次结构一样。先看当前状态，再继续依赖它的批量。
- **保留部分执行成果仍适用。**display参数类型错误后frames/sheets还在，应修编码并复用，不重启session或重播。原Agent在此做对了。
- **批量不改变预算。**最后一个cell有多次UI交互，合并成一个脚本不会变成一次动作；进入写入阶段只有2步余量，不能靠一次调用包住全部步骤突破预算。
- **没有确认的新Runtime缺陷。**IPython不存在、set_value不存在、display要求bytes是接口使用问题；最终UnknownMethod结合gate记录是预算拒绝。无需为本项增加兼容方法、自动重试或例外计数。

## 本轮边界

原campaign、manifest、原结果和调用只读；只提取原图、运行原状态/动作回放并记录图像证据缺失。未创建Android/Appium session、清数据、重启共享服务、改变模型/预算/evaluator、修改正式skill或候选方案。不启动新官方任务，先停在本项讨论。
