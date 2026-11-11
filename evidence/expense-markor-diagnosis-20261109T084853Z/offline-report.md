# 原r12v2 014 ExpenseAddMultipleFromMarkor：离线调查结论

## 决定与当前进度

**本轮离线调查可以完成，不需要、不授权任何现场回放或设备查询。** 已确定原scorer的实际失败分支，已证明本项输入渲染与reference之间的note表示差异及其充分失败机制；历史实际after DB未保留，不能证明原数据库中唯一不匹配字段就是note。新跑也不能恢复已经丢失的历史DB。

本项没有修改生产、AndroidWorld、AMKernel、技能、renderer、reference、fuzzy阈值、参数、预算、重试或原成绩；不能把“查明”写成“已fix”。后续版本若要消除marker歧义，必须先确定任务契约，不在本轮实施。原reward仍为0.0；没有新reward，也不推进下一项。

## 原身份与实际执行

仅使用 `campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/014-ExpenseAddMultipleFromMarkor/attempt-1`，不是r11。

- goal：`Go through the transactions in my_expenses.txt in Markor. Log the reimbursable transactions in the pro expense.`
- paramsSha256：`23de427b2cc14ba77e7fc9e4f767e4a6b1e4049661a80c3ce0b957c65120c929`；seed3053860270，complexity6，预算60；原manifest的paramsTransport是**seed**，不能照搬009的JSON transport。
- 目标为Laundry/$96.30/Clothes和Car Insurance/$303.01/Transportation，reference notes分别是 `Urgent` 与 `I may repeat this`。
- 原执行20/60业务动作、21个reference steps；25次Python调用中24 completed、1 failed，全部Kernel alive，无timed_out。exec2在import lxml即失败，exec3改用标准库ElementTree恢复，没有安装包、重建session或扩大预算。不是本项原零分的未恢复阻断。
- 已直接遍历原raw，逐项核对父提取的25段完整代码及25个原响应，三个源hash均吻合：result `198faa876422efc67531fc1f3b318013a660e2af295fc7dfc2fc8f82b57ef6bd`；normalized `5d5b1de0ef465e8165e33fe73510e601fe4fe60104f29a14efdcd31010e89456`；raw `690dac2ad773a09f3b41f2ded10dd7d6df2486352eccdb9637debf3eb86b79e4`。

## 已确定的原scorer分支

`evidence/headless-fullcoverage-20261107T004632Z/v2-ready-run-full.log:302` 是本次真实原日志：

> Expected row Expense(name='Laundry', amount=9630, category=8, note='Urgent', created_date=1697320800000, modified_date=1697320800000, expense_id=-1) not found in the 'after' state.

该完整reference对象在冻结manifest中只对应index14，前面的21个reference steps与原result一致，不是拿旧r11 warning推断本项。

实际继承链：`ExpenseAddMultipleFromMarkor` → `_ExpenseAddMultiple` → `AddMultipleRows.is_successful`。该scorer读取 `after=self.list_rows(env)`，调用原 `validate_addition_integrity(self.before, after, self.params[ROW_OBJECTS])`。

原expense validator比较 `name/amount/category/note`；name和note使用fuzzy_match，阈值0.9；amount和category直接比较。日期、主键虽显示在reference对象及warning中，但不在这四个compare_fields里，不能把日期差异直接归为本次匹配失败原因。

实际warning对应 `sqlite_validators.py:166–171`：首个reference Laundry找不到任何匹配after row，返回False，外层返回0.0。**尚未执行**后面的数量检查（173–181）及原行保全检查（183–190），不能把这些分支写成passed；Car Insurance的reference匹配也因首条短路而未被该次调用验证。

## 最早表示差异及原UI证据

`expense.py:343–355` 在任务初始化时对目标创建dataclass副本，把 `. Reimbursable.` 附加到note后渲染进Markor；原reference params没有相同改动。该子类明确使用pipe-separated CSV，尽管冻结通用参数text_representation_type为text_block。

原exec8（raw2088/2089）已通过Markor UI读到102笔数据。正文第59及72行为：

| 字段 | Laundry | Car Insurance |
|---|---|---|
| 原reference note | Urgent | I may repeat this |
| Markor原note列/实际输入 | Urgent. Reimbursable. | I may repeat this. Reimbursable. |
| 原输入exec/raw行 | 13 / 3352–3353 | 21 / 4981–4982 |
| 类别选择回读 | exec17：Clothes | exec23：Transportation |
| 金额输入 | 96.3 | 303.01 |
| 原保存后列表观察 | exec19有Laundry/96.3 | exec24有Car Insurance/303.01 |
| 原安装fuzzy结果 | false，ratio 0.444444 | false，ratio 0.693878 |

Laundry另有exec18/raw4243–4244的pre-save字段回读，仍为正确name/amount及带marker note。以上是输入/选择/保存列表证据，不是保存后detail回读，不是DB值，不把最终Agent prose当作数据库。

**最早可定位的差异在任务初始化的渲染/reference边界，早于模型输入；不是AMKernel替换了note。** 原模型随后照Markor note列输入两条带marker文本。实际安装比较函数不能接受这两种note作为各自base note的近似匹配。

父与独立作者的离线原validator受控候选smoke也证明：用原100 noise加带marker的两条候选，实际validator返回False并产生与302相同的Laundry warning；用base-note候选返回True。它说明**如果实际DB保留了原UI输入note，就足以导致该失败机制**；这些候选不是历史before/after DB，不是新官方判分。

## 历史DB缺口与能下的结论

在原attempt、原campaign持久化结构及所查evidence的DB文件范围，没有取得同次原before/after DB快照或完整actual row列表。原result只保存reward与阶段摘要。

原源码能解释这项留证缺口：

- `sqlite_utils.get_rows_from_remote_device` 通过原pull_file临时目录读取数据库。
- `AndroidWorldController.pull_file`委托 `file_utils.tmp_directory_from_device`；其finally执行shutil.rmtree，原本地副本不长期保留。
- 原runner判分后执行task teardown，原记录为completed；`SQLiteApp.tear_down`清expense表，Markor任务tear_down清其目录。因此事后读取当前设备既不是同次原输入，也无法补成历史DB；本轮没有这样读取。

结论分层：

1. **已证：** 原reference Laundry没有在实际after列表中匹配；原代码在首行匹配分支返回False/0，而不是后续count/preservation分支。
2. **已证：** 源note表示与reference不同，原模型真实复制了该表示；当前安装原fuzzy/validator对这种输入有充分失败机制，且原warning与之吻合。
3. **未证：** 历史after DB里具体保存的note及所有字段；不能据此证明原失败的唯一字段原因就是note，也不能保证只有这一字段不匹配。
4. **不推出：** 任务无解。受控base-note候选可通过原validator；这不是对Agent提供参考答案或建议增加benchmark特例。

## 与旧r11 issue145候选、修复状态的关系

本轮没有借issue编号替代取证，也未联网确认issue145的处理状态。本项已有自己的原raw、reference、真实warning、安装源码及离线函数结果；可称为相同类型的marker/reference表示问题，不能把旧r11结果拼到本次。

- lxml import失败：原模型已用ElementTree恢复，不需要新增依赖或AMKernel修复。
- 本项render/reference差异：当前安装源码仍存在；本轮没有修改，不能声称已fix。
- 原失败分支/留证：已查明；历史完整DB缺口仍明确保留。
- 若未来要修改renderer/reference或marker处理，应先决定marker是筛选元数据还是应持久化note正文，并在新任务契约下保持用户输入与reference一致。**本轮不strip后缀、不改阈值、不放宽比较、不改原成绩或加入特例。**

## 是否需要现场、最小契约

**本轮不需要现场即可完成上述离线调查。父已明确不授权回放/设备查询。** 见 `minimal-contract.json`：仅提出后续版本必须先明确marker语义的契约要求，没有待执行现场步骤。

现有证据不能宣称恢复了原DB；再运行也只能产生一份新状态，不能补证原历史唯一字段根因。本轮不为补一条成功结果另做试验。

## 证据与操作边界

- `owner-raw-field-proof.json`：25个原code/response逐项核对、Markor原行、实际输入/选择/保存观察。
- `historical-scorer-warning.json`：本次原日志279–303窗口与确切失败分支。
- `owner-scorer-source-proof.json`：实际继承scorer、7个已导入依赖文件hash及安装distribution RECORD一致性、原DB留证路径、实际fuzzy调用输出。
- 父及独立作者：`parent-original-field-evidence.json`、`parent-installed-validator-smoke.json`、`independent-014-contract-smoke.json`；各自署名与原产物不由本执行者覆盖。
- `immutability.json`与`zero-operations.json`：限定核对范围及本轮零设备/会话/生产修改收据。独立验收另行署名，本报告不代其宣布通过。
