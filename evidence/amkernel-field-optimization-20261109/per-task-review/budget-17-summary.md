# 17项预算耗尽复核结果

## 结论与范围

17/17已完成逐项原始调用复核，不再逐项等待讨论。调查对象仍是冻结的 **r12 v2** campaign，不是旧冻结协议。全部原官方reward仍为0；本轮没有新Android重跑、重评分或成绩提升。

**预算耗尽是终止机制，不是统一根因。** 已确认的问题主要是模型规划、UI状态判断和业务完成证据；另有应用/启动器异常以及冻结Harness的答案提交边界。不能把17项都记为AMKernel故障，也不能声称一份skill方案能修好17项。

每项报告包含最早偏离、原调用行号、UI动作分账、分层归因、方案适用范围及不确定性。下面分类允许重叠，不作互斥“根因占比”。原始任务参数或evaluator用于事后解释的地方，不代表Agent可用这些信息完成任务。

## 全量清单

动作列为原已执行/上限；名称链接到单项报告。

|索引|任务|动作|最关键的失败证据与归因|
|---|---|---|---|
|003|[BrowserMaze](003-BrowserMaze/review.md)|20/20|十次路径点击缺少节点级反馈，后来点击候选非当前节点；存在正常变化，但目标未证实。模型/技能为主，原生点击机制未隔离。|
|004|[BrowserMultiply](004-BrowserMultiply/review.md)|22/22|非空等待可立即读到旧9，未处理表单出现分支；失去中间数后猜乘积。桌面页面复现证明合法数字可以重复，不证明Android时序修复。|
|023|[MarkorAddNoteHeader](023-MarkorAddNoteHeader/review.md)|12/12|正文已改，重命名未完成；等待不存在的菜单ID，菜单实际已打开。阶段判据错误，不是整个任务都没效果。|
|024|[MarkorChangeNoteContent](024-MarkorChangeNoteContent/review.md)|12/12|正文已改，把非编辑态标题TextView当重命名输入框；未找到正确入口。定位语义/规划问题。|
|028|[MarkorCreateNoteFromClipboard](028-MarkorCreateNoteFromClipboard/review.md)|14/14|Paste实际执行，但只替换临时文字中的一个词，正文留下自加umbrella；以“不同于旧值”误判正确。|
|036|[MarkorTranscribeVideo](036-MarkorTranscribeVideo/review.md)|20/20|前期模型往返错过短视频；后期单cell连续35帧采集是正确模式，但只填了名称字段；扩展名清空、文件创建、正文输入及保存均未执行。原拼图截断，不能补证转录正确。|
|038|[NotesMeetingAttendeeCount](038-NotesMeetingAttendeeCount/review.md)|10/10|观察已支持计数25；前置侧栏/点击失败耗步，第10动作才打开目标笔记。最后输出整数taskOutcome且处清理阶段，无规范化答案进入判分。|
|060|[RetroPlaylistDuration](060-RetroPlaylistDuration/review.md)|30/30|未取得时长依据便批量选曲；最终12首、61:13，明确超出45–50分钟；准备修正时gate已关闭。聚合目标规划问题。|
|073|[SimpleCalendarEventsInNextWeek](073-SimpleCalendarEventsInNextWeek/review.md)|10/10|已观察到周一窗口内两个事件，末尾字符串与观察相符；最后两动作再复核后进入清理，答案未提交。Harness边界是直接判零原因。|
|074|[SimpleCalendarEventsInTimeRange](074-SimpleCalendarEventsInTimeRange/review.md)|10/10|改日期返回但仍为15日，未取得目标20日数据；转周视图后仍读日视图专用字段而失败。输入/阶段识别与恢复问题。|
|080|[SimpleDrawProCreateDrawing](080-SimpleDrawProCreateDrawing/review.md)|18/18|启动异常与重复搜索耗步，出现Android System Intelligence崩溃框；最后Pictures/文件名就绪，SAVE作为第19动作被拒，持久化未确认。|
|082|[SimpleSmsReplyMostRecent](082-SimpleSmsReplyMostRecent/review.md)|12/12|首击进Google Messages，后续搜索非可点击重复结果；截图有系统崩溃框，始终未到目标app。目标识别/无进展恢复叠加环境异常。|
|084|[SimpleSmsSend](084-SimpleSmsSend/review.md)|12/12|先开错app；正确收件号码输入后用换行“提交”，字段变空，最后动作只够重填号码。输入语义与观察问题。|
|086|[SimpleSmsSendReceivedAddress](086-SimpleSmsSendReceivedAddress/review.md)|18/18|第12动作才激活正确app；第18动作输入正文，下一发送点击被gate拒绝。规划绕行先消耗余量，不是MCP丢发送。|
|090|[SportsTrackerLongestDistanceActivity](090-SportsTrackerLongestDistanceActivity/review.md)|10/10|0.75mi→1207m换算正确，但候选mountain biking类别与完整覆盖未证明；最后对象型taskOutcome又不满足外层字符串契约，且未提交。|
|106|[TasksCompletedTasksForDate](106-TasksCompletedTasksForDate/review.md)|10/10|边缘手势返回Launcher、开关方向理解不清、两次滚动观察完全相同；最后标题缺完整日期/完成状态证据，且未提交。|
|110|[TasksHighPriorityTasksDueOnDate](110-TasksHighPriorityTasksDueOnDate/review.md)|10/10|编辑器已打开却因错误谓词超时；实体转义用于selector导致未命中；最后候选详情未打开便猜高优先级，且未提交。另一次无效JSON在执行前拒绝。|

## 五层归因

### 模型规划

可反复观察到：先认错目标app、猜入口/页面、弱等待条件、把“发生变化”当业务正确、无进展后重复、证据丢失后猜答案、未核实筛选条件便取候选。成功执行的一部分不能被整体failed/timeout抹掉；后续策略必须基于实际状态。

### 技能指导

现有候选方案已经能描述大多数可预防模式：脚本内批量与阶段分支、输入前后校验、无进展先观察、异常后读取保留的数据、业务后置条件及部分完成报告。

这里是**把新候选方案对照历史失败**，不等于已证明原Agent违反当时可见的冻结技能，也不等于已验证新Agent会遵循候选方案。不能用“规则已写”代替效果验证。

### AMKernel Runtime/MCP

[原结果清单](budget-17-inventory.json)合计 **250个已执行UI动作、371次python_exec工具尝试、370个已观察执行envelope**；370个envelope均报告kernel alive。110有一次内层JSON在进入Python执行前被拒绝，解释工具尝试数与envelope数差1。日志没有支持kernel死亡、隐式重建、长请求丢失或session偷偷替换的证据；不把“没发现”升级为排除所有Runtime问题。

此前现场阶段已修复的InvalidElementStateException信息省略属于**可诊断性缺陷**；BrowserMultiply确有该异常。修复不自动恢复数字、纠正输入路线或提高官方成绩。这里未新增Runtime修复。预算gate拒绝经协议映射出现UnknownMethodException时，应结合拒绝账本判断，不能只凭异常名误判客户端不支持。

### Appium/应用环境

082与080有Android System Intelligence崩溃框证据；这是环境异常，不足以单独证明所有启动失败的底层原因。BrowserMultiply原生点击/可访问树时序、074日期选择器输入未生效、110底部条目点击不进入详情仍需独立隔离，不编造缓存、焦点或驱动根因。没有因此重启共享服务、升级依赖或更换环境。

### Harness/评测契约

全部17项都到达原动作上限。单cell不豁免动作，失败cell中已准入的动作仍计入。

其中6项是信息查询：**038、073、074、090、106、110**。原结果全部`normalized.finalText=null`、`agentAnswer.validContract=false`。代码证据：

- `omp_supervisor.py:135-138,160-169,203-208`：gate关闭后转清理，清理阶段文字不作task_final。
- `runner.py:171-180,751-762`：仅接受规范化finalText中的字符串taskOutcome，然后写入interaction_cache。
- `information_retrieval.py:109-119`：没有interaction_cache直接判0。

因此，“raw最后写了答案”与“正式提交了答案”不同。038、073的观察已足以支持内容答案，但未得到正式提交；038还是number类型，090还是object类型，均不满足外层字符串要求。074本来没读到目标数据；090/106/110仍有内容证据缺口。**六项不能一概声称答案正确，也不能一概声称推理错误。**

状态型任务则不同：例如SMS没有成功发送动作，丢失末尾文字不能解释为已完成发送。短信数据库缺记录未在本轮独立查询，属于由动作轨迹和官方结果支持的推断。

这是应单独讨论的测评协议边界，而非AMKernel技能补丁。当前不改冻结Harness、不重新解释原分数、不把清理文字补送evaluator。若未来决定调整提交/清理边界，须明确新协议身份与独立成绩；也可以保留原契约，两种选择影响可比性，本轮不代替用户决定。

## 通用方案收敛建议

不扩成17条任务配方，不加固定坐标、特定菜单、自动重试或特殊答案。保持候选方案的主干，仅建议明确两种已被案例支持的用法；本轮尚未写入正式skill，也未修改候选方案原文：

1. **短暂时序内容：先脚本内连续采集、保留时间/序列，再返回模型解读。** 036后半程是正面证据；采样间隔及覆盖要求依内容决定，不能固定35帧或固定间隔。
2. **查询与聚合目标：证据必须覆盖完整条件及关联。** 日期/完成状态/优先级/类别/区间/候选覆盖，不能由名称猜、由差集猜或由“有变化”替代。没有可靠信号就保留不确定性；不能靠读取隐藏参数或数据库答案完成Agent任务。

继续保留：一次Python内多次观察与交互、本地过滤计算、持久命名空间中的中间结果。不要为了每步证明而强制模型往返；也不要为了批量而跨越未验证的依赖。合法输出可重复，不能把“必须不同于旧值”写成通用进展规则。

这些是有证据依据的候选指导，不是现场收益承诺。17项不能据此估算可提升多少成功率。若正式落地技能，仍需隔离开发版小样本真实运行和少量原成功样本回归；不默认再跑116项。

## 检查、回归与清理边界

- 本轮完成：全部单项原调用/结果复核；对应保存状态与动作回放；必要的原图直接读取；结果清单汇总；来源哈希与报告链接核验。前6项已有的桌面页面语义诊断与此前现场修复证据仍保持各自边界，不冒充本轮新Android实验。
- 原17项：quit均返回成功，远端session均验证absent，task teardown均completed、environment均closed。这是历史证据，不是今天共享服务实时状态声明。
- 本轮新建Android/Appium session为0，因此无新设备session待清理；未清数据、未重启服务、未触碰冻结安装。
- 本轮无行为变更、无新官方运行、无新增成功样本回归；不能把只读回放称为真实应用修复验证。
- 另外19项“Agent结束但官方失败”未纳入本轮分析，等本结果讨论后再进入。基线80/116不变。

## 证据入口

- [17项原结果与清理清单](budget-17-inventory.json)
- [Notes/Retro/Draw分组核验](notes-media-draw-summary.json)
- [Calendar/Sports分组核验](calendar-sports-summary.json)
- [SMS分组核验](sms-budget-summary.json)
- [现有候选方案，未改动](skill-optimization-proposal.md)
- [此前现场修复与真实回归报告](../report.md)
