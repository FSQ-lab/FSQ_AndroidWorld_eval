# 040 NotesTodoItemCount：独立离线验收

署名：**w4:p2 独立离线契约验收助手**。签署时间：**2026-11-09T09:49:47Z**。

目录：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/notes-todo-count-diagnosis-20261109T093949Z`。

## 裁定与责任

**Owner最终五文件、generic-skills-candidates、父040 review及proposal新增040节的事实边界验收通过。仅限离线诊断与建议事实，不是fix验收。** 五件实际SHA均匹配最终交付manifest；完整签署版本及父文档/新增节SHA见本JSON。

直接已证：原final是合法JSON，`taskOutcome`为数值3；原Harness记录`agentAnswer.validContract=false`、`sha256=null`。原prompt末尾要求JSON包装，却没有明示该字段必须是字符串。主要责任在**旧Harness提示/类型/提交接口**，不能责怪模型用了JSON包装，也不能由0分反推3数错。

本作者独立执行保存旧helper，原数值字段返回None，类型仅改为字符串的受控候选才提取为字符串。**未写cache→空cache→IR111–112早返是有来源的源码推导链，不是原缓存或首分支的内存观测。** 不误述为JSON全文送入float失败；不把当前新string模板倒推为历史模型已收到的指令。

UI另有范围/覆盖与失败检查被弱化的问题，但不是已观察的本次0首因。不查设备、不回放、不再恢复历史源码或缓存、不推进下一项。

## 原身份与独立重验

原r12v2 index40，seed1631305569，paramsTransport **json**，params SHA256 `3a13b8c96c83d595c5cf072ad7e423072e50d51731faded1c313a83180c9d99e`。原5/10业务动作、6reference steps、reward0；12次Python调用10 completed、2 failed，全部alive、无AMKernel timed_out。

独立逐原raw比对全部12段code及12个response，与父提取逐对象一致；result/normalized/raw三件SHA均与已登记及父身份一致。详见 `independent-040-original-evidence.json`。七个实际安装源码/数据由本作者逐件对distribution RECORD核对一致。未沿用014/033的归因或验收。

## 直接证据与推导必须分层

| 证据层级 | 本次核对 | 不得升级为 |
|---|---|---|
| 原直接记录 | raw9原prompt含single-number业务要求和compact JSON控制要求，未明示string字段；raw2674为numeric3；原validContract=false/null | 模型未遵守当前新模板、官方已经比较并否定3 |
| 本作者真实纯smoke | 旧`_agent_prompt`渲染逐字等原prompt，模板SHA463118…匹配；旧`_task_outcome`对原final返回None、受控字符串字段返回字符串 | 原env/cache/首返回分支现场trace或新reward |
| 保存源码链 | TaskEval145清cache；旧runner753–760仅有效字符串才赋值；stepped adapter无ANSWER路线；IR109–119先判空再比较 | 已逐字恢复完整原冻结Harness或已保存历史内存 |
| 当前任务模板纯函数 | COUNT取3条relevant proto的is_todo字段；受控字符串能匹配模板 | 同次DB查询、原3官方已判对、真实全folder UI覆盖 |

本次没有创建env或调用initialize_task/is_successful。纯函数receipt为 `independent-040-contract-smoke.json`，不是完整评分。

## 官方计数及初始化语义

本项由实际 `InformationRetrievalRegistry` 动态构造为 `abc.NotesTodoItemCount`，继承 `InformationRetrieval.is_successful`。`tasks.textproto:3434–3480`定义三条相关todo以及COUNT/NUMBER_MATCH；初始化生成100条noise，排除条件合取为is_todo=True且folder=Ideas。因此普通note仍可出现在Ideas，不足以据此判错folder。

`proto_utils.py:183–208,234–251`从任务relevant-state proto收集字段计数，正式答案判分不读取Joplin当前DB。非空答案才进入`check_agent_answer`，NUMBER_MATCH使用float；原整段JSON并非保存runner会提交的答案值。模板结果与可见数碰巧相同不补成原DB或实际答案比较的验收。

## UI最早验证偏离与范围边界

- **exec9/raw2050–2051：** 点击Ideas后，实际主视图顶部Ideas在`[163,128][817,264]`；与抽屉Ideas的`[39,740][614,797]`不同。这支持当时主内容标题已切到Ideas，不应草率说导航错误。同树仍有Notebooks，不能单独证明抽屉可见、遮挡或错误folder。
- 该次等待只验证宽泛文本/前几个TextView条件，未绑定主标题定位、稳定可见层或统计覆盖；这是最早的验证条件不足，不是已证实的错误业务状态。
- **exec10/raw2342–2343：** Sidebar动作之后，line2等待Notebooks消失超时；后面的title/todo读取没有执行。这是最早直接留存的未满足后置条件，不能补称该次已经取得计数。
- **exec11/raw2581–2582：** `hasIdeasTitle`实际仅为全texts包含Ideas；`hasNotebooks=true`仍在。统计是整份当次tree内带to-do前缀的CheckBox数，不是有列表终点/覆盖依据的全folder总数。Recipe Ideas、Financial Plan、Work Tasks三项与exec9相同；不是Workout Routine。
- 原12calls没有Joplin列表终点或遍历覆盖证明。三项可见计数不等于已证明全集，但也不等于数3错误。Selenium显式等待失败且kernel alive，不是MCP执行超时或运行时死亡。

故技能候选应是绑定活动范围、证明覆盖、失败后恢复原强后置条件，而非替Harness猜测未声明的字段类型。不能把这些候选写成修复本次0的充分证据。

## 版本身份、原日志与辅助成功接口样本

实际使用的保存runner SHA为`11a1a396…`，它是private r12诊断重建。原prompt与其模板逐字/SHA绑定只证明这一部分；**整树不能冒称原冻结4a4b…版本**。已亲读owner关于登记commit ebd085恢复helper AST一致、但aggregate192ab…仍不等4a4b…以及editable distribution无独立runner的局限；本作者没有重复git恢复，也不把当前源码当原源码。

原log699–705仅六步后done，没有原cache或精确答案评分trace；697/698附近a11y-retry没有任务标签，不归count/answer根因。原evaluator四舍五入0.0秒也不是分支证明。

另亲读父039同campaign辅助收据，并独立核对其原result登记hash、调用同旧helper取得`3/4 cup`、计算UTF8 SHA `56e795…`精确等原agentAnswer.sha，原validContract=true、reward1。这增强旧helper与原接口记录的相容性；是**已完成历史记录的只读样本**，不是新任务/重跑、040因果对照、完整冻结版本证明或040数3官方正确的证据。无需owner为此重开文件。

## 父review、proposal及owner最终交付

已亲读父 `per-task-review/040-NotesTodoItemCount/review.md` 和既有 `skill-optimization-proposal.md` 的新增040节，**未发现与本次已核对证据冲突的事实**。proposal清楚分开Harness接口责任与skills范围/覆盖/强恢复，保留批量观察与统计，不要求每次滚动都往返模型；没有数值强转特例、裸数字绕过包装或固定任务答案。建议均未实施为正式修改，也未宣称0→1成效。

Owner最终 `offline-report.md`、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json` 全部已亲读，五件实际SHA匹配 `owner-final-delivery.json`。summary最终SHA `6e8c3e23f73cf9a8d3c6d0a8e26ac3d9e4e124805e2920e65aa0b5968ad30ebb`。另签署generic候选文件SHA；所有签署版本记入本JSON。

Owner2186历史/152技能/7安装源收据已审阅相符，未冒称本作者重跑其全量扫描。本作者独立范围为040三原件、12原始调用对、七源码/数据RECORD与指定旧协议/父文档/辅助样本，非全机或完整历史源码树审计。

本作者零设备/ADB/Appium/session/env/init/is_successful/DB/cache写入/回放/服务/build/lint/test suite/formatter/生产/依赖/技能改动；未覆盖owner、父或历史文件。当前已存在的新模板不是本次fix，未做新官方判分。

署名产物：`independent-040-acceptance.md/json`、`independent-040-contract-smoke.json`、`independent-040-original-evidence.json`、`independent-040-readonly-receipt.json`。**仅本项离线诊断与建议事实验收完成，供父复核后交付。**
