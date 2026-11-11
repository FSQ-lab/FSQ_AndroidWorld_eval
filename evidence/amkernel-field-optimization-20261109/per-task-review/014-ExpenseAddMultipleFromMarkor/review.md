# 014 ExpenseAddMultipleFromMarkor：父复核

## 决定

本项按“原失败分支与任务契约诊断”离线收口；不是修复完成声明。不启动回放、设备查询、下一项或全量评测。原 r12 v2 reward 仍为 0.0。

证据目录：`evidence/expense-markor-diagnosis-20261109T084853Z/`。父已亲读所有者的 `offline-report.md`、`summary.json`、`owner-scorer-source-proof.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`，以及本次独立新署名的 `independent-014-acceptance.md` 和 `independent-014-readonly-receipt.json`。独立验收限于本项离线诊断，不沿用008/009或旧r11结论。

## 来源消歧

唯一来源为原 r12 v2 `014-ExpenseAddMultipleFromMarkor/attempt-1`：result SHA256 `198faa876422efc67531fc1f3b318013a660e2af295fc7dfc2fc8f82b57ef6bd`；raw SHA256 `690dac2ad773a09f3b41f2ded10dd7d6df2486352eccdb9637debf3eb86b79e4`；params SHA256 `23de427b2cc14ba77e7fc9e4f767e4a6b1e4049661a80c3ce0b957c65120c929`。目标为 Laundry / Car Insurance。父先前 Dave/Sue 转述错误，已撤回，未作为结论依据，原提取未被错误转述修改。

## 已证失败链

- 原执行20/60业务动作、21个reference steps；25次Python调用中24 completed、1 failed，全部kernel alive、无timed_out。exec2缺lxml后，exec3以标准库ElementTree恢复；不是本项未恢复的运行时阻断。
- 原 `v2-ready-run-full.log:302` 明确报 Laundry reference 未在 after 匹配。完整目标仅对应冻结manifest的index14，reference steps相合。
- 实际继承scorer为 `AddMultipleRows.is_successful`。该warning对应 `sqlite_validators.py:166–171` 首reference匹配失败立即返回false，外层返回0.0。第二reference、数量与旧行保全分支尚未执行，不能写成通过。
- `expense.py:343–355` 只给渲染副本note追加 `. Reimbursable.`，reference仍为原note。最早可证差异在任务输入/reference边界，早于模型输入；未发现AMKernel改写note的证据。
- 原UI观察及输入确为 Laundry `Urgent. Reimbursable.` 与 Car Insurance `I may repeat this. Reimbursable.`。exec18/21是保存前字段；exec19/24是保存后列表，不是详情回读或DB。

## 父实际验证

父使用实际安装的 `ExpenseAddMultipleFromMarkor.validate_addition_integrity`，以原100个noise逻辑行不变、原pre-save字段构造受控候选：带marker候选false，stderr为相同Laundry missing-after warning；仅恢复base note的受控候选true。模块SHA与实际安装证据一致。收据为 `parent-installed-validator-smoke.json`。独立作者另行实际验证，见 `independent-014-contract-smoke.json`。

两note与reference的实际fuzzy ratios为0.4444444444、0.6938775510，均低于0.9。这是充分失败机制，不是历史after DB的重建，也不是新官方reward。

## 保留边界与修复状态

1. 原同次before/after DB未保留；原pull临时目录finally删除，原teardown已清Expense与Markor。当前设备读取不能恢复该历史输入，本轮未这样读取。
2. 未证明历史唯一不匹配字段就是note，也不排除其它历史字段或持久化问题。
3. 不证明任务无解；base-note受控候选可通过原谓词。
4. 本项没有AMKernel/技能fix证据，因此未修改生产、renderer、reference、fuzzy或技能，不加入剥后缀特例。
5. 后续任务版本须先明确marker是筛选元数据还是note正文，再保持可见业务字段与reference语义一致；这属于另行授权的任务契约变更，不能改冻结成绩。

## 不变性及操作收据

所有者限定核对2186个已登记历史路径、152个技能文件、7个安装依赖源码，changed/missing均为空；7源码匹配安装distribution RECORD。独立方另核对原3件、父提取及7源码，不冒称全机或整个安装树不变。

本slice设备查询、Appium调用、新session、任务初始化/回放、服务操作、安装升级、生产/技能修改均为0，无新增设备资源需要清理。只新增独立调查证据。无新官方结果，不替换原失败，不推进下一项。
