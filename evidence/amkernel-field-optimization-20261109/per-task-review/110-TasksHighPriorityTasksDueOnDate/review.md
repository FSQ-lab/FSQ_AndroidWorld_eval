# 预算耗尽第17项：TasksHighPriorityTasksDueOnDate

## 结论

10/10 UI动作、21次python_exec工具尝试，其中1次内层JSON无效、20次实际执行。官方reward=0。查询中存在错误等待、字符串跨语法转义错误、未验证最后候选优先级却猜答案。没有证明AMKernel不支持观察优先级；Learn to Play Guitar的优先级裁剪清晰返回，不是最后Marketing候选的证据。

原末尾JSON也不等于已提交答案：normalized.finalText=null、agentAnswer.validContract=false，属于冻结Harness的预算耗尽后清理/答案隔离边界。

## 动作分账与最早偏离

原锚点相对 `episodes/110-TasksHighPriorityTasksDueOnDate/attempt-1/raw-private/agent-events.jsonl`。

|动作|调用|可观察结果|
|---|---|---|
|1–2|cell3/4，1015/1279行，上滑、Tasks|进入列表；原列表存在重复标题，必须关联到日期行|
|3|cell8，2538行，点Learn to Play Guitar|等待fab消失超时；2817行已是EditText标题与Save，编辑器实际已打开|
|4|cell12，4347行，Back|等待回列表超时；4511行是DISCARD/KEEP EDITING分支，后续查找未执行|
|5|cell14，4902行，DISCARD|返回列表；随后XPath未命中，没有第二次点击|
|6|cell16，5550行，按标题及Wed行几何关联点击正确License|进入编辑器，四个radio的第一个checked=true|
|7–9|cell17，5937行，Back、DISCARD、点Marketing Campaign Launch|编辑器等待超时；6139行仍为列表|
|10|cell19，6457行，对屏幕底部Marketing标题位置tap|仍fabCount=1、editTitleCount=0；未打开详情|

**2+1+1+1+1+3+1=10**，逐个action kind与原gate相符。cell6相对XPath查父节点失败发生在点击前，没有UI动作。6622行quit成功；原清理记录远端缺席、零活动session、teardown完成。

## 重要原始证据

- 2167行：`node.find_element(XPATH,'..')`查找失败；后续成功使用原title点击，不需要为本项新增父节点兼容层。
- 2538/2817行：用fab不存在作为编辑器判据错误；已观察到的EditText标题与Save更能区分阶段。动作成功和谓词错误必须拆开。
- 3322行：[原优先级裁剪](original-image-1-rawline-3322.png)来自Learn to Play Guitar，清楚显示灰、蓝、黄、红四档，黄色选中；原Agent解释为likely medium。可访问树缺少标签时用图像补证是成功模式，但它不证明Marketing的高优先级；颜色语义仍需合理确认，不能把截图存在算查询完成。
- 3893–3894行：工具content的JSON含无效转义，入口直接拒绝。见[原错误内容](malformed-call-evidence.json)。不是Python执行中断，也未消耗UI预算。
- 4902/5124行：定位字符串把标题写作`Renew Driver&apos;s License`；Appium selector和XPath表达式不是XML文档，实体不能当作通用跨语法转义。列表还有同名不同日期条目，随后用日期与行几何关联才命中目标。
- 5937/6139/6457行：第一次点底部Marketing标题和后来的坐标tap都没有打开编辑器；原因未隔离。不能声称tap修复，也不应固化该坐标。重新观察遮挡/可见交互区域是候选方法，不是已验证结果。
- 6882行：最终猜测Marketing为高优先级，原推理还承认可能有未看见的候选；未观察到该条目的优先级。不能通过排除两项推断剩余项必满足，也不能假设列表已穷尽。

## 评分边界

原normalized.finalText=null、agentAnswer.validContract=false。`omp_supervisor.py:135-138,160-169,203-208`在gate关闭后进入清理并排除清理文字；`runner.py:751-762`只转交normalized答案；IR evaluator `information_retrieval.py:109-119`在无interaction_cache时返回0。因此答案推断缺证和官方无答案提交是两层问题。不能拿原末尾猜测作新的官方成绩。
原6882行同时包含thinking和最终JSON text；直接解析raw可取得字符串Marketing Campaign Launch，磁盘finalText=null来自清理阶段的supervisor重写。回放明确分开thinkingText和finalText，不把推理文字当最终答案。

## 分层和通用方案

模型规划/状态识别为主：错误页面谓词、未处理丢弃确认分支、重复标题关联与转义错误、对未确认候选猜结论。Appium/应用有底部点击不进入详情的现象，底层原因未复现；Runtime/MCP无新确认缺陷。无效JSON被正确拒绝不是传输丢请求。

现有候选方案可覆盖阶段分支、点击后业务证据、布局变化后重新定位、图像补证和部分结果报告。查询类再明确“保留行关联、逐项证明筛选条件、确认候选覆盖范围”，但不新增固定日期算法、菜单路线或自动tap。正确转义属于按API写代码的责任，不为一次错误扩展Runtime协议。

## 已执行检查与边界

[原调用提取](original-python-executions.json)、[观察回放](observation-replay.json)。已离线对齐10种动作、确认超时后编辑器实际存在、最后tap无详情、无效JSON在执行前被拒绝，并直接阅读原优先级图片。本轮无新Android操作、skill正式修改或官方分数；不保证候选方案使本项10步内成功。
