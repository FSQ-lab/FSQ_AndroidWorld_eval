# 040 NotesTodoItemCount：父复核

## 结论与责任

本项直接证据是：Agent返回数值类型taskOutcome=3，但原Harness记录agentAnswer.validContract=false、sha256=null，未记录有效业务答案。原提示要求JSON包装，却没有明示该字段必须是字符串。主要问题在Harness答案接口/提示契约，不能直接归为模型数错、未遵守single-number任务文字或AMKernel执行故障。

保存的r12源码与原记录相容的机制为：只接字符串的提取器拒绝数值3，不执行答案缓存setter，InformationRetrieval在空缓存时先返回0，不进入数值答案比较。这是源码推导链，不是原缓存/首返回分支的内存观测；不得改说JSON全文进入float转换失败。

另有独立skills优化候选：目标容器与统计覆盖验证，以及等待失败后的真实恢复；不能把它们直接当本项0分根因。建议已补入既有 `../skill-optimization-proposal.md` 的040节。本次无正式技能、Harness或Runtime修复，无新官方成绩。

## 原始身份

来源：原r12 v2 `040-NotesTodoItemCount/attempt-1`，seed1631305569，params SHA256 `3a13b8c96c83d595c5cf072ad7e423072e50d51731faded1c313a83180c9d99e`。

- result：`1fb8a4f041ca8a64dd456aa136e6c4f9bb755b49afe9bb66f285994f751c93b2`
- raw：`89b1520e03cb6832fe1b8d15a7ef9ecde5356b2da579fae5bdce6d5d202984b6`
- normalized：`f806895f8496c438e28acc05245dfb84e17e78d03e50f99e8f692d63ae266c9e`

父逐原raw提取12对code/response，见本目录 `original-python-executions.json` 与 `original-source-identity.json`。原5/10业务动作、6reference steps；12次Python调用中10 completed、2 failed，全部kernel alive、无AMKernel timed_out。第二次失败是调用内WebDriverWait TimeoutException，不等同于AMKernel执行超时。

## 直接原记录

- raw9的原user prompt：任务文字要求single number；末尾控制要求compact JSON with taskOutcome/sessionCleanup/evidence，没有字段类型声明。原prompt逐字匹配保存模板，模板SHA `463118879bbe14a14abfd987920f115fff29f128db4566dc282e75dc0aa906aa` 与原result匹配。
- raw2674：模型返回 `{"taskOutcome":3,"sessionCleanup":"completed","evidence":"Ideas folder showed 3 to-dos."}`，数值类型int；原normalized final语义相同。
- 原result：agentAnswer.validContract=false、sha256=null；officialReward=0.0。不能仅凭evaluator耗时四舍五入为0.0就认定具体分支。
- 原log699–705：六步后done，没有记录本项答案缓存或精确评分分支。附近a11y retry没有任务标签，不归为本项根因。

## 实际运行的离线验证与版本边界

父从保存r12 runner中提取原样 `_task_outcome` AST实际执行：原numeric3字段返回None，只将该字段改成字符串"3"的受控候选返回"3"；直接输出裸数字3也返回None。见证据目录 `parent-historical-extractor-smoke.json`。未运行完整Harness、环境、任务初始化、is_successful或设备访问。

该runner是既有私有诊断重建，不是字节一致的冻结Harness整树。所有者另从已登记commit ebd085只读恢复，helper AST相同，但aggregate仍不匹配原4a4b...；这不补成精确原运行源码证明。父receipt明确保存此限制。

父亲读实际安装 `information_retrieval.py:109–119`：空interaction_cache先返回0，非空才调用check_agent_answer。所有者核对动态NotesTodoItemCount的继承关系、初始化清缓存、条件setter及stepped adapter不写ANSWER，七个安装源码/数据匹配distribution RECORD。模板纯函数得出计数3与字符串"3"可匹配，但不是同次实际DB核验，不能宣布原3已由官方判对，更不能称新reward=1。

## 独立于提交问题的UI/skills缺口

- exec9（raw2050/2051）有主视图顶部Ideas，bounds `[163,128][817,264]`，可与抽屉Ideas `[39,740][614,797]` 区分。主列表显示Recipe Ideas、Financial Plan、Work Tasks三个待办控件，后续多条普通笔记。不是Workout Routine。
- 同一返回也含Notebooks及抽屉节点，不能仅凭其存在认定错误文件夹或视觉遮挡；原响应未证明可见层/动画稳定。
- exec10（raw2342/2343）点击Sidebar后等Notebooks消失失败；exec11（raw2581/2582）仍有Notebooks，仅检查任意texts包含Ideas及全树checkbox数3后结束，没有列表终点或全量覆盖证据。
- 原模型推理称三项“probably represent all my to-dos”，是未完成覆盖验证，不等同于已经证明答案数错。

因此skills应指导：绑定主视图和范围、区分可见计数与全量、在有覆盖依据时批量遍历/统计、等待失败后恢复原业务条件而非弱化条件。它不能替Harness猜测未声明的答案字段类型。

## 操作和交付范围

证据目录：`evidence/notes-todo-count-diagnosis-20261109T093949Z/`。父亲读原prompt/calls/result、原log、所有者source-proof，亲跑上述pure extractor；不冒称冻结整树完全恢复或历史DB/缓存已保存。

本slice设备查询、Appium动作、新session、任务初始化、评分重跑、服务操作、安装升级、生产/技能修改均为0，无新增外部资源需要清理。不改原campaign、成绩或当前既有新模板；不默认推进下一项。
