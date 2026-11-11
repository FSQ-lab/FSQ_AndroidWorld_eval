# 正常结束但官方失败第1项：BrowserDraw

## 结论

**这是Agent观察到成功、官方却判0的明确不一致，不能归为已证实的Agent误判完成。**

原任务要求在Chrome打开Downloads/task.html，用顶部三色绘图并Submit。Agent用了17/20个UI动作、26次python_exec，正常结束。提交后原截图显示三色三角形和Success!；同一次Appium page_source提取也返回Success!，package为com.android.chrome。原normalized.finalText保留completed及证据，agentCompleted=true，cleanupRequested=false。官方reward仍为0。

尚不能确认判零是错误包名、AndroidWorld UI树缺少Success、状态时点差异或其他观察链路问题。原包未记录evaluator当时的package、UI树与截图，不能补造根因或改判原成绩。

## 原始调用与动作分账

锚点相对 `episodes/002-BrowserDraw/attempt-1/raw-private/agent-events.jsonl`。

|动作|原调用|结果|
|---|---|---|
|1–2|cell3/5，717/943行，上滑、Files|进入文件管理器|
|无UI动作|cell7/9，1322/1571行|相对XPath/父节点查找失败；不是文件不存在，1457行已找到task.html|
|3–4|cell10/12，1795/2052行|点唯一文件card、选Chrome，进入首次使用流程|
|5–7|cell14/16/18，2422/2699/3161行|同意条款、两次negative_button；第一次等待超时，重新观察仍在初始流程，第二次回到Files|
|8–10|cell19/20/22，3390/3522/3881行|重新打开文件、选Chrome、关闭promo，进入页面|
|11–16|cell24，4356行|一次Python内3次选色tap、3次绘线swipe，三色三角形已出现|
|17|cell25，4672行|点击Submit；等待1秒后读取树、截图，树中包含Success!，package=Chrome|
|清理|cell26，4746行|driver.quit返回；无后续Agent业务UI动作|

**1+1+1+1+1+1+1+1+1+1+6+1=17**，与原gate逐个action kind一致。cell26仅清理，不消耗UI动作。原最终JSON在4786行；不是预算耗尽后被丢弃的答案。

## 可直接复核的成功证据

- [提交前截图](original-image-2-rawline-4356.png)：青绿、品红、深蓝三条边已形成三角形；细蓝十字线属于屏幕指针叠加，不能当作绘图目标色证据。
- [提交后截图](original-image-3-rawline-4672.png)：三角形保留，Submit下方显示Success!。
- [原调用提取](original-python-executions.json)：cell25的visibleTexts明确有Success!，不是只有Agent口头声明。
- 原BrowserDraw页面JS（`android_world/.../task_evals/single/browser.py:596–628`）在canvas像素包含所有taskColors时设置Success!。该判据不要求三角形，也不要求只能用三色。Agent绘三角形是自己的选择，不能追加benchmark要求。

截图和可访问树都是同次cell25、quit之前的证据；不能把它们称为evaluator时点证据。分析host没有PIL，自动像素计数未执行，未安装依赖；图片采用直接读取。页面Success与Appium树已足以证明Agent当时的完成判断有直接依据。

## 官方判据与证据缺口

现有源码 `BrowserTask.is_successful()`（`browser.py:98–109`）：

1. `state = env.get_state()`；
2. 另取当前activity并提取package；若不是com.android.chrome，返回0；
3. 遍历state.ui_elements，存在text严格等于Success!返回1，否则0。

它不读取Agent的completed字符串，也不在Python evaluator重新计算canvas色值。

Harness `runner.py:698–707,751–765` 在adapter.finish与session清理审计之后调用task.is_successful。原Appium成功观察发生在quit之前，所以**成功观察到判分之间有session清理边界**。但没有证据证明quit关闭了Chrome或清掉画布，不能因此给清理定罪。

AndroidWorld `interface.py:240–241,292–295` 的get_state经controller.step读取；`android_world_controller.py:225–250`存在A11y forwarder和UIAutomator两种观察路径。Appium page_source与AndroidWorld UIElement不是同一份保存对象。这里仅说明可能存在观察链路差异，**没有证明本次是缓存、过滤、服务陈旧或某一具体机制**。0.057秒的evaluator时长同样不能证明缓存根因。

原证据包只保存reward及duration，没有返回0的分支、当时package/activity、UI forest/ui_elements与截图。原任务已teardown，不能今天再读设备来还原当时状态。

## 分层归因与方案影响

- **模型规划/技能**：前置XPath猜父节点和Chrome首次使用处理有无效往返，但Agent已恢复且仍有3步余量；没有证据把它们当本次判零根因。最终完成判断用了原图+原树的Success，符合业务后置条件，不应要求继续盲点Submit。
- **AMKernel Runtime/MCP**：26个envelope均kernel alive；异常后复用同一driver继续；三色绘制、截图传递和quit均有证据。未发现本项Runtime修复点。
- **Appium/应用环境**：初始引导与文件重开造成额外动作，但随后任务页面确实成功。没有证据表明画图动作无效。
- **Harness/评测观察**：当前调查重点是Agent成功观察与官方观察之间的差异；不是已确认的evaluator错误，也不是此前预算收尾答案问题。根因待独立复现。

现有候选skill足够表达按阶段等待、失败后重观察、图像补证、脚本内批量动作与最终状态验证。**不为本项新增规则，不修改候选或正式skill。** 自动多等几秒、再次Submit或重开页面都没有因果证据支持，可能反而破坏已成功状态。

## 给评测侧的最小诊断建议

开发隔离重跑时，在不改任务/evaluator/预算的前提下，保留同次判分实际使用的state.ui_elements及package/activity；给这个返回0记录分支原因。可配套保存判分附近的截图，并明确额外截图的时点，避免额外get_state刷新后冒充原判分输入。

同时关联提交后、quit后与官方判分的时间线，再判断是状态变化还是两条观察链路不同。若没有这组证据，不应擅自按Appium树补判成功或把官方树换成Appium树。

## 本轮检查与清理边界

已提取26次原调用和3张完整原图，直接读取提交前后图；离线对齐17动作账本，检查Appium树Success、最终JSON保留、提交后仅quit。见[观察回放](observation-replay.json)。这不是新Android复现或新官方成绩。

原结果：一个session创建、一个删除，deniedCommandCount=0、errors=[]；quit返回、远端验证absent，task teardown完成、environment关闭。这里是原历史清理证据，不是今天共享服务状态。

原campaign、manifest、结果与冻结安装只读。本轮没有设备操作、依赖安装、正式代码/skill修改或新测评。停在本项讨论，不自动进入下一项。

## 跨项目单次复现后的更新

评测项目已在独立目录完成一次诊断：quit后、官方本次判分取得的截图仍显示Success!，package/activity仍为Chrome；实际A11y forwarder输入为零窗口forest、ui_elements=[]，在browser.py:109返回0.0，结果保存值相同。上述原记录中“缺少判分输入”的限制已由这次新实验补齐，但不改写原campaign事实或分数。

AMKernel侧随后离线对齐第18次Submit与第19次quit：请求代码、执行结果和Appium wire一致，两次均completed/kernel alive；quit响应HTTP200，约4.947秒后开始官方判分。没有发现本次调用交付/顺序问题。

进一步源码追踪与本地库回放发现：没有新RPC不会自动构造空forest；收到的零窗口forest会正常进入extras，而累积区可能保留旧空forest。另有本地Appium保护accessibility服务的配置文件，但本次进程/会话没有加载该能力的证据。两者是后续可检验线索，不是已确认的历史根因；不能认定quit或服务压制造成空树。

详见[跨项目追踪结果与下一次最小诊断](cross-project-followup-20261109/findings.md)。本侧没有新设备运行、生产修复或skill改动；原复现目录保持只读。本项仍是评测观察链路故障调查，不归为已证实的Agent误判完成。
