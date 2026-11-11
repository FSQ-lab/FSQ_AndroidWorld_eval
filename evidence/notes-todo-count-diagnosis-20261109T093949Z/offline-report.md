# 原r12v2 040 NotesTodoItemCount：离线调查

## 结论与归因层级

**本项直接留存的失败点是答案提交契约未通过：`agentAnswer.validContract=false`、`sha256=null`，不是已证明Ideas计数错误。** 原业务final已被捕获，JSON合法且taskOutcome为数值3；原prompt末段要求JSON包装，却没有明示该字段必须是字符串。保存的旧r12 helper只接受字符串，因此把该final提取为None。这是历史Harness提示/类型接口的不完整，不能直接归为模型不遵守“single number”。

按保存源码链路，未提取到答案就不写interaction_cache；空缓存使InformationRetrieval在111–112行立即返回0，尚不进入NUMBER_MATCH。**空缓存值及这次具体早返是源码推导链，不是原内存/分支dump；保存的诊断Harness也不是与原4a4b…整树逐字一致的冻结副本。** 直接记录的答案拒绝成立，helper提供吻合的充分机制，证据等级不混用。

不把原JSON全文假定成传给float的输入，不把四舍五入的evaluator时长0.0当作根因证明，也不把模板预期3或可见UI3冒充同次DB验证/已通过的官方答案比较。

本项仅离线收口；无设备/当前DB查询、无初始化/回放、无源码或技能改动、无新reward，不推进其它项。当前已存在的新字符串模板不算本次fix或成效。

## 原身份、结果与来源

原attempt：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/040-NotesTodoItemCount/attempt-1/`。

Goal：`How many to-dos do I have in the 'Ideas' folder in the Joplin app? Express your answer as just a single number.`

- manifest index40，JSON参数transport，seed1631305569，complexity1，预算10；params SHA256 `3a13b8c96c83d595c5cf072ad7e423072e50d51731faded1c313a83180c9d99e`。folder=Ideas、title=Meeting Agenda，body参数仍为原文，未重新生成。
- 原5/10业务动作、6个reference steps；12个Python调用，10 completed、2 failed，全部Kernel alive，无AMKernel timed_out。未耗尽动作预算，Agent正常完成；officialReward0.0，error/invalidReason均null。
- 原task teardown、environment close完成；原quit成功、session absent。原business final非null，不是cleanup之后未被捕获的答案。
- 三原件独立重算：result `1fb8a4f041ca8a64dd456aa136e6c4f9bb755b49afe9bb66f285994f751c93b2`；normalized `f806895f8496c438e28acc05245dfb84e17e78d03e50f99e8f692d63ae266c9e`；raw `89b1520e03cb6832fe1b8d15a7ef9ecde5356b2da579fae5bdce6d5d202984b6`。
- 从原raw独立提取12份code/response；12个原请求code SHA逐项匹配原result。父另有独立提取与身份，未覆盖。

详见 `owner-original-calls.json`、`owner-raw-field-proof.json`。

## 原prompt与真实final：业务答案和传输包装不能混为一谈

原raw8/9的user prompt同时包含：

1. goal要求业务答案是single number。
2. 末段要求 `Return one compact JSON object with taskOutcome, sessionCleanup, and evidence`。

**该历史末段没有要求 `taskOutcome` 是string。** 用当前更新后的“Numeric answers must also be encoded as strings”反过来指责原模型，不符合版本证据。

原raw2674真正final为：

```json
{"taskOutcome":3,"sessionCleanup":"completed","evidence":"Ideas folder showed 3 to-dos."}
```

normalized只做等价键顺序调整，taskOutcome仍为int3；与原raw逐对象一致。原模型遵守了要求的JSON外包装，字段里也确实是一个数字。不能仅因不是裸文本3就说它违背single number。

本作者把保存旧r12模板渲染为本项原URL、目标、预算与timeout参数，逐字匹配原raw prompt；模板SHA `463118879bbe14a14abfd987920f115fff29f128db4566dc282e75dc0aa906aa` 与原result/manifest相同。

## 真实任务类、初始化、计数与答案判分

当前实际安装AndroidWorld0.1.0中的本项不是静态单任务class，而是 `InformationRetrievalRegistry` 从 `proto/tasks.textproto` 动态构造的 `abc.NotesTodoItemCount`；实际继承的scorer为 **`android_world.task_evals.information_retrieval.information_retrieval.InformationRetrieval.is_successful`**，不是仅凭result里泛化implementation标签猜测。

7个直接相关实际安装源码/数据文件（IR scorer、动态registry、proto_utils、Joplin helper、task base、env interface、tasks.textproto）已逐一SHA对安装distribution RECORD一致。原result记录AndroidWorld revision55ddaf5edc6f6c25673aed343907d5b9dca66f84、Harness revision12、AMKernel0.1.3、github-copilot/gpt-5.6-sol；当前实际文件核对不冒充原完整安装树快照。

### 初始化与预期计数

- `tasks.textproto:3434–3480`相关状态有3条notes，folder均为参数folder，is_todo均为True；noise排除条件为 `is_todo=True AND folder={folder}`。成功条件是对relevant proto的is_todo字段执行COUNT、NUMBER_MATCH。
- `information_retrieval.py:82–107`格式化任务proto后调用Joplin setup。`joplin_app_utils.py:38–66`清DB，生成100条排除相关条件的noise，加3条相关note，shuffle后写入。原title/body用without_replacement生成不同目标，不能把参数title本身当成三份UI目标的固定标题。
- `joplin_app_utils.py:276–336`按所有exclusion条件合取排除noise；并非把所有普通note从Ideas排除。因此原UI里3条todo后仍有普通note，符合这类初始化，不足以推断错误folder。
- `proto_utils.py:183–208,234–251`从**任务relevant-state proto**收集is_todo字段并计数，不在判分时读取Joplin DB，也不把UI CheckBox总数直接当reference。
- 本作者仅构造未初始化的本地任务读取模板并调用实际纯函数：`get_expected_answer(task.task)`得到 `[3]`，`check_agent_answer("3",task.task)`为True。这是模板级逻辑验证，不是原DB或原env的再次判分。

### 答案判分次序

- `TaskEval.initialize_task:145`先将interaction_cache置空。AsyncAndroidEnv创建/reset也置空；原AppiumSteppedAgent不提交AndroidWorld ANSWER action。
- `InformationRetrieval.is_successful:109–112`先检查interaction_cache；为空即0，未进入下游答案比较。
- 只有有答案时，才在114–119调用 `proto_utils.check_agent_answer`。NUMBER_MATCH在`proto_utils.py:119–120`使用float转换；COUNT来自相关proto；不是读取当前DB。
- 因此“全文JSON如果送入float会失败”仅是与本项传输链无关的条件说明，**不是原实际零分解释**。

## Harness提取/提交链、源码身份和恢复边界

采用的旧r12保存逻辑在：

`evidence/browserdraw-forest-provenance-20261109T060244Z/source-snapshot/fsq_androidworld_eval/runner.py`

该文件SHA `11a1a39602904b02d66a9d316686291194bba46d7fb219366d2ad4c4bdac589d`；139–148行 `_task_outcome`先json.loads，再要求dict里的taskOutcome是str，trim后才返回，否则None。753–760行只把成功提取的answer写入env.interaction_cache，并保存validContract与answer hash；不是传JSON全文。

本次真实纯函数smoke从这份保存源码AST提取原helper执行，未导入/运行完整Harness：

| 输入 | 实际helper返回 |
|---|---|
| 原raw/normalized的JSON，taskOutcome为数值3 | None |
| 仅将该字段变为字符串"3"的受控候选 | "3" |
| 裸文本3 | None |

该结果与原 `agentAnswer=false/null` 一致；受控候选不替换原记录、不送执行Agent、不产生新reward。父另有 `parent-historical-extractor-smoke.json`，独立作者也另做验收。

**版本局限必须保留：**

- 原manifest的整树Harness摘要是 `4a4b045f56a9c09ec84bf22e2369c59a3489b8c24e0afe5d22001403920b3f27`。
- 保存诊断源码的origin记录（`browserdraw-field-diagnosis-20261109T052514Z/diagnostic-changes.json`）明确声明它是private r12重建，保留原prompt及提交前逻辑，不声称等于原冻结整树。
- 已按原登记source-identity中的commit `ebd085561651b8ba4b2a1a53ef6321e0305c06b3`做一次只读git对象恢复；得到runner SHA `a0e5e5d14fc8bce2b5de927a44ed3322bde5912563a801e32142090a715a48c2`，其helper AST与保存旧r12完全相同，但该commit整树摘要也不匹配原4a4b…。没有把它冒充精确原运行源码。
- 安装的fsq-androidworld-eval0.1.0是指向当前项目的editable，distribution中没有独立runner.py可恢复，不能用当前更新后的源倒推历史。
- 原raw prompt及原拒绝标志为直接留存；旧helper/setter和IR早返是核对后的保存源码推导；**未保存原env.interaction_cache值或分支trace**。这不阻止报告直接的答案提交失败，但限制了原具体内存路径的实证措辞。

见 `owner-scorer-source-proof.json`、`owner-harness-recovery-limit.json`、`owner-pure-contract-smoke.json`。没有因源码局限发起新现场，因为它无法补回历史内存。

## 原UI计数：支持什么、不支持什么

| 原exec / raw code、response行 | 实际证据 | 限制 |
|---|---|---|
| 2 / 570、571 | lxml import失败 | 原3用ElementTree恢复，无安装/重建session |
| 9 / 2050、2051 | 主内容顶部Ideas位于 `[163,128][817,264]`；3个todo CheckBox为Recipe Ideas、Financial Plan、Work Tasks；下面还有普通note | 抽屉Notebooks与另一Ideas节点也在tree中；不能仅因它们存在判成错误folder |
| 10 / 2342、2343 | 点Sidebar后，在line2等待Notebooks消失超时，cell failed/alive | 后面的title/todo读取没有执行，不能补称该次已返回计数 |
| 11 / 2581、2582 | hasIdeasTitle=true、hasNotebooks=true、todoCount=3，列出相同三项 | hasIdeasTitle只是全texts成员检查，不是toolbar定位；未保存列表终点/覆盖证据 |
| 12 / 2639、2640 | quit成功 | 原会话清理，并非当前新操作 |

原三条可见todo与模板计数3一致，但这不是同次DB验收，且UI全列表覆盖未闭环。**不能由官方0倒推3错，也不把“UI覆盖还不完整”升格为本次先行零分原因。** exec10是Selenium显式等待失败，不是AMKernel timed_out或Kernel死亡；exec11完成了存活后的只读观察，但条件比“确认抽屉关闭+目标toolbar”弱。

## 原run-full.log

`evidence/headless-fullcoverage-20261107T004632Z/v2-ready-run-full.log:696–708`中，本项按manifest零基顺序对应699–705：6个Completed step后done。前41段reference-step序列与原result逐项一致，是序号归属，不伪称日志有任务名标签。

697/698有a11y-retry warning，但没有本任务/答案标签；不据此指认UI计数错误或答案丢失。没有答案拒绝warning或原cache dump；IR空值早返本就没有logging分支输出。原evaluator记录0.0秒是round到三位的小量时长，单独不能证明提前返回。

## 通用建议候选与责任边界

见 `generic-skills-candidates.json`；仅候选，没有修改父proposal或正式skill。

- **Harness责任优先：** caller必须显式定义业务答案与传输包装、字段类型、接收/拒绝语义；旧prompt要求JSON却隐藏string约束。应在后续授权版本验证接口一致性，不靠task专属后处理补救。当前模板已有明确string说明，不能把它算作本轮新增fix或效果。
- **Skills统计范围：** 统计要绑定活动内容区域和目标标题，区分普通条目/待办与抽屉重复节点；可见数不自动等于全集，范围/覆盖需证据。
- **Skills等待恢复：** 后置条件失败后，明确区分未执行语句与已完成动作；用足够强的上下文条件确认当前状态，不以更弱的全tree文本存在代替原目标。不因此盲目重放动作或加测评特例。

这些UI候选独立于已直接记录的Harness提交失败；不能把本例改写成“改skill即可保证从0到1”。没有新fix/新score声明，也不建议为拿1重跑。

## 交付与不可变性

owner五文件为 `offline-report.md`、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`。具体来源、纯函数输出及版本局限另有独立文件。原campaign/install源码/技能只读；只新增本目录owner证据，不覆盖父或p2署名。独立验收由p2另行签署。
