# 预算耗尽第16项：TasksCompletedTasksForDate

## 结论

10/10 UI动作、14次python_exec、官方reward=0。存在明确的导航与状态理解损失，但不能把reward=0直接解释为答案内容错误：原末尾有三个标题的JSON，结果中normalized.finalText=null、agentAnswer.validContract=false。冻结Harness没有把清理阶段的末尾文字转交IR evaluator。

## 最早偏离与动作分账

原始锚点均相对 `episodes/106-TasksCompletedTasksForDate/attempt-1/raw-private/agent-events.jsonl`。

|动作|调用及证据|结果|
|---|---|---|
|1|cell3，797行，上滑后等All apps/Apps list或activity改变|错误超时；1045行已显示应用抽屉与Tasks，activity不必改变|
|2|cell5，1169行，点Tasks|进入org.tasks|
|3|cell7，1522行，从屏幕最左边横滑，猜测Completed抽屉|超时；1762行已经回到Launcher。与系统返回手势一致，但未独立隔离机制|
|4–5|cell9，2063行，重进Tasks、打开More options|发现Show completed|
|6|cell10，2397行，点击Show completed|只余8个普通任务；菜单消失不足以证明目标已显示|
|7–8|cell11/12，2604/2812行，两次上滑|两份返回观察完全相同，未获得新任务|
|9–10|cell13，3388行，再打开菜单、点Show completed|出现额外3行，均Tmrw、completeBox checked=false；新增行的完成状态未验证，Agent仍把标题作答案|

**1+1+1+2+1+2+2=10**，与原gate的每个action kind一致。3559行driver.quit成功；原清理记录远端缺席、零活动session、任务teardown完成。

## 判断边界

- 目标为“October 16 2023已完成任务”，新增行显示Tmrw；原Agent也承认未核实它是截止日期还是完成日期。原树的completeBox均checked=false，不能把这个泛化属性当作完成状态的可靠编码。
- 第一次切换后普通8行、第二次切换后增加3行，可以支持切换了可见范围；不能单凭列表差集证明完整日期条件。两次滚动完全相同，已足以要求改变观察/导航策略，而非继续滚动。
- 末尾3612行有三个标题的taskOutcome。但结果normalized.finalText=null、agentCompleted=false、agentAnswer.validContract=false。`omp_supervisor.py:135-138,160-169,203-208`：gate关闭后转清理，清理阶段文字不作任务答案；`runner.py:751-762`只转交规范化答案；IR `information_retrieval.py:109-119`在interaction_cache为空时直接返回0。该契约解释当前无答案提交，不证明三个标题内容必错，也不能擅改冻结协议补分。
- 直接解析raw的最终text可以取得三个标题；磁盘结果的null来自supervisor在清理阶段的规范化重写，不是raw缺少最终文字。回放工件分开记录thinkingText、finalText和磁盘结果，避免混淆。

## 分层与方案适用性

- 模型规划/判断：猜测抽屉入口，边缘手势后回到Launcher；完成过滤开关的方向未先确认；用模糊日期与列表差集代替完整查询条件。
- 技能候选：阶段级等待、无进展停止、保留完整上下文适用。对查询应按各条件建立证据链，并保留行的关联；不是多加一个“存在”条件即可。无需新增Tasks菜单路线或Runtime自动兜底。
- Harness/评测契约：本项即时判零另有答案提交边界。原预算与清理边界应照实报告；不把事后文字重新计为业务答案。
- AMKernel Runtime/MCP：未发现执行丢失、kernel隐式重建或session生命周期缺陷。菜单和滚动均有返回；不能从reward推断Runtime失效。

## 已执行检查与边界

[原调用提取](original-python-executions.json)、[观察及动作回放](observation-replay.json)。离线核对10种动作顺序、两次滚动返回完全相等、两次切换前后的标题差集及规范化答案为空。不是新Android复现，不证明候选skill能在10步内成功。原campaign只读，本轮无设备操作、正式skill修改或新官方成绩。
