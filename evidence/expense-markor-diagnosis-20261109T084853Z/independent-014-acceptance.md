# 014 ExpenseAddMultipleFromMarkor：独立只读契约验收

署名：**w4:p2 独立只读验收助手**。本次机器记录签署时间：**2026-11-09T08:54:44Z**。

目录：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/expense-markor-diagnosis-20261109T084853Z`。

## 裁定与收口决定

**本项可在当前证据边界内离线收口，无需再跑。** 本项已独立确认：任务生成的可见 note 与判分 reference 不一致；历史官方确实在首条 Laundry reference 的 row-matching 分支失败；照抄原可见 note 是经实际安装 validator 验证的充分失败机制。它们不等于已证明唯一历史 DB 原因、任务无解或修复验收通过。

新增回放不能恢复原同次 DB；若当前交付是原任务的生成/官方 DB 验证契约诊断，现有源码、原输入及原真实 warning 足以收口。只有另行要求证明“真实持久化 DB 中仅 note 导致拒绝”，才需要获准后单次诊断回放。**本 slice 未开跑，也不建议为重复获得同一 warning 而重跑。**

这是一份本次014新署名验收，不沿用008/009的 passed，也不沿用旧r11 issue145的结论。未实施或验收新 fix；不改原成绩。

## 1. 来源身份与独立核对

原件：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/014-ExpenseAddMultipleFromMarkor/attempt-1/`。

- 任务 seed：`3053860270`；params SHA256：`23de427b2cc14ba77e7fc9e4f767e4a6b1e4049661a80c3ce0b957c65120c929`。manifest 与原 result 参数相同。
- 原 result SHA256：`198faa876422efc67531fc1f3b318013a660e2af295fc7dfc2fc8f82b57ef6bd`。
- 原 normalized SHA256：`5d5b1de0ef465e8165e33fe73510e601fe4fe60104f29a14efdcd31010e89456`。
- 原 raw SHA256：`690dac2ad773a09f3b41f2ded10dd7d6df2486352eccdb9637debf3eb86b79e4`。
- 我独立重算以上三件，并与父提取及此前 `frozen-before-sha256.json` 中这三条原登记一致。不是全历史 hash 审计。
- 原 result 记录 AndroidWorld `0.1.0` / revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`，AMKernel `0.1.3`，官方 reward `0.0`，业务动作 `20/60`。历史版本字段不冒充逐文件历史源码证明；本次实际 import 路径和七个直接判分链路源码 hash 见 `independent-014-readonly-receipt.json`。
- 唯一目标为 **Laundry / Car Insurance**。Dave/Sue 转述已撤回，未用于本次分析。父提取原件未被本作者覆盖。

我还从原 raw 独立解析并与父提取逐对象比对 exec13/17/18/19/21/23/24/25 的 code 和 response；锚点见 `independent-014-original-evidence.json`。

最终对齐：已亲读 `owner-scorer-source-proof.json`、父实际 validator smoke 及父 raw 字段证据。我独立验证 Laundry 精确目标在整个冻结 manifest 仅匹配 index14，实际继承的 scorer 确为 `AddMultipleRows.is_successful`，并将七个直接链路源码逐一与实际安装 distribution RECORD 的 SHA 核对一致。三原件及父提取在本次结束时仍未改变；限定范围收据为 `independent-014-readonly-receipt.json`，不冒称全机或全 campaign 不变审计。

owner source-proof 记录原登记证据未留 DB、既有 pull 临时目录 finally 删除、原 teardown 已清除 Expense/Markor。结合现有原件留存边界，历史 DB 缺口不是可由当前设备补回的阻塞项；本作者没有额外查设备或宣称重新找到了原 DB。与父最终决定一致：**本轮离线收口，不做新跑或回放，不改 renderer/reference/fuzzy。**

## 2. 实际安装的生成与 DB 契约

以下路径均以 `.venv/lib/python3.11/site-packages/android_world/` 为前缀，实际 import 来源已核实。

- `task_evals/single/expense.py:343–355`：只给目标行的 **dataclasses.replace 副本**追加 `. Reimbursable.`；原 `params.row_objects` 不变。Markor 初始化明确使用 `csv`，实际是 pipe-separated 文本，不依赖冻结参数中的 `text_representation_type=text_block`。
- 同文件 `230–246`：渲染 `name / amount_dollars / category_name / note`。`utils/sqlite_schema_utils.py:217–251` 定义分转换美元及 category 名称。
- `expense.py:264–285`：新增行比较字段为 `name, amount, category, note`；仅 `name, note` 使用 fuzzy。
- `task_evals/common_validators/sqlite_validators.py:280–310`：初始化已有 `self.before` 来自一次 `list_rows`；正式判分再次取得 `after`，把它与 `self.before`、**原 params.row_objects** 交给原 validator，返回 `1.0` 或 `0.0`。
- 同文件 `118–192` 的真实顺序：①每个 reference 须在 after 中找到一个字段匹配行；②总行数须为 before 加 reference 数；③每个完整 before dataclass 必须保留。新增行日期和 ID 不在指定比较字段内；旧行保留则是完整对象相等。不能把 docstring 中的描述扩张成代码没有单独实施的检查。
- `utils/fuzzy_match_lib.py:22–51`：转字符串、默认忽略大小写，`SequenceMatcher.ratio() >= 0.9`；无报销标记剥离、标点/空白归一化。`None` 不匹配。
- `expense.py:32–61`：DB 为 `/data/data/com.arduia.expense/databases/accounting.db`，表为 `expense`。
- `task_evals/utils/sqlite_utils.py:27–103`：已有 controller.pull_file 取得本地临时 DB；`SELECT * FROM expense` 后直接构造 `Expense(**row)`。此判分路径使用 DB 行，不依赖 UI 森林中的成功文本；没有 note 后缀转换。

## 3. 原数据的实际离线 smoke

直接在当前 `.venv/bin/python` 的保留 Python runtime 中调用实际安装的 `_get_expense_rows_as_text`、`ExpenseAddMultipleFromMarkor.validate_addition_integrity` 和 `fuzzy_match`。未调用 initialize_task、is_successful、环境或 controller；未做全套检查。

| 原目标 | reference note | 实际渲染 note | 实际 fuzzy ratio | 匹配 |
|---|---|---|---:|---|
| Laundry，9630 cents / Clothes | `Urgent` | `Urgent. Reimbursable.` | 0.4444444444 | false |
| Car Insurance，30301 cents / Transportation | `I may repeat this` | `I may repeat this. Reimbursable.` | 0.6938775510 | false |

取原100个 noise **逻辑行**保持不变，分别附加两条已知候选：

- 原渲染 note 候选：实际 validator **false**，发出与历史相同的 Laundry expected-row-missing warning。
- 原 base note 候选：实际 validator **true**。

两种受控候选仅 note 不同，证明这个差异足以触发拒绝。源参数中的 `expense_id=-1` 是生成哨兵，未伪称真实 DB 主键；这些 before/after 列表是原已知数据的受控候选，**不是历史 DB 快照，也不是新 reward**。

独立 receipt：`independent-014-contract-smoke.json`。父另有独立 receipt `parent-installed-validator-smoke.json`；本结论不以父 receipt 替代本作者实测。

## 4. 历史原件已证明什么

- raw `3352–3353` / exec13：输入 Laundry 名称、金额和带 marker 的 note，并读取当时输入字段。
- raw `4243–4244` / exec18：Laundry 保存前 Appium source；exec17 的 category 为 Clothes。
- raw `4981–4982` / exec21：Car Insurance 输入字段带 marker；随后 exec23 选择 Transportation。
- exec19/24：保存后列表观察。上述均不是保存后详情回读，也不是 DB；不把不同时间点拼成同一张已持久化记录。
- 原 `evidence/headless-fullcoverage-20261107T004632Z/v2-ready-run-full.log:279–303` 已亲读。**302** 明确记录 Laundry（9630、category8、note Urgent）的 `Expected row ... not found in the 'after' state.`，位于该段 done 后。其映射到实际 validator `166–171`：首条 reference 没找到匹配即 false。
- 所以原匹配失败分支并不缺失；它早于数量和旧行保留检查，后两分支本次未到达。日志 step 文本与 result 业务动作计数不是同一计数，不把末尾 Completed step21 改写为21个业务动作。

**尚缺原官方同次 DB before/after 内容。** 因而不能从该 warning 单独区分“note 不匹配”与“目标行未落库/金额或 category 等其他字段不同”，也不知道后续约束是否还存在差异。现有原 UI 输入和受控 smoke 强力支持 note 机制，但未排除并发存在的其他历史 DB 问题。

## 5. 必须明确的语义选择，不在本次实施

1. **marker 是筛选元数据。** source/goal 应清楚分开报销标签与真正 note；保留 base note 的 reference 才无歧义。不能把当前模糊字段偷偷变成仅此 benchmark 的 Agent 剥后缀规则。
2. **marker 是 note 正文。** 应从同一规范化目标对象同时生成可见文本与 reference，并明确语义；不能只追加渲染副本而评分仍取旧 note。

当前 goal 仅要求记录 reimbursable transactions，没有明说逐字保存全部 note。因此确有 render/reference 不一致，但尚不能推出逻辑上不可完成：离线 base-note 候选已经证明原谓词存在通过输入。降低 fuzzy 阈值、忽略 note、修改历史 reward 都不是本次诊断的结论。

## 6. 若另行要求真实 DB 因果闭环：仅一次方案

这不是当前收口的先决条件；以下仅建议，未执行。

- 核对设备/session 所有权后，隔离初始化同一原任务参数，按原 UI 动作及原带 marker 输入回放一次；不把 DB/reference 交给执行模型，不改输入、等待、重试、后端、判据或预算。诊断回放不冒称原模型成绩。
- 记录初始化**已有调用**取得的 self.before；正式判分记录**同一次 list_rows / execute_query** 返回的 after 和原 reference 参数。需要二进制时，保存该调用已有 pull_file 的本地临时 DB，不能另拉一份冒充原判分输入。
- 保留同一原 predicate 的实际分支、原始返回值与最终保存 reward；不靠第二次 predicate 或额外 get_state 替代正式输入。
- 能消除本次回放中的不确定性：marker 是否真实持久化；金额/category/name 是否正确；实际行数/旧行是否另有差异；究竟哪个真实字段使原谓词拒绝。
- 不能消除的边界：它不能恢复历史原 DB，不能由一次新复现证明历史唯一原因，也不能替任务定义方选择 marker 的业务语义。

当前不需要优先排查 AMKernel 或采集后端：最早可证差异在任务渲染前后，官方真实失败走 DB 谓词。若未来真实 DB 与原输入明显不一致，再沿保存/持久化/读取链查具体差异；现阶段没有新增 AMKernel fix 的证据。

## 7. 本次独立产物与边界

- `independent-014-acceptance.md`：本署名裁定。
- `independent-014-acceptance.json`：本次机读验收、实际源码 hash、收口决定及回放边界。
- `independent-014-contract-smoke.json`：实际 renderer/fuzzy/validator 结果。
- `independent-014-original-evidence.json`：三原件 hash、逐对象匹配的关键 raw 调用、真实原 warning 段落。

零设备查询、零 session、零 build、零生产/依赖/技能修改；未覆盖原 campaign、冻结安装、父提取或历史。只新增本目录独立证据，不新增规则或后缀补丁，不向执行模型泄露 reference/DB。当前收口不是修复完成声明，不推进下一项。

## 8. Owner最终五文件的独立验收

**验收通过，范围仅为014本轮离线分支/契约诊断交付。** 已亲读并核对 owner 的 `offline-report.md`、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`；五件被验收版本的 SHA256 与本次签署时间记入本 JSON 的 `ownerFinalDeliveryAcceptance`。未覆盖 owner 或父文件。

新增独立核对：25段 code 与25个 response 已全部逐对象比对原 raw（不再仅核对前述8个关键调用）；24 completed、1 failed、全部 alive 与 summary 一致。原任务身份、20个业务动作、原0分与现有原件一致。owner 的2186登记历史/152技能/7依赖源码收据数值与其 summary 相符，changed/missing为空；本作者没有重新执行其全量hash扫描，也不把owner自报零操作冒充全主机命令审计。此前本作者独立7源码 RECORD及限定原件核对收据仍有效。

五文件一致保留：首Laundry匹配失败后count/preservation及第二reference匹配未达；原DB note不可观测、不证明唯一历史字段原因、不证明任务无解。无fix/升级/新reward。`minimal-contract.json`明确不授权且不计划任何现场或下一任务。此前回放方案仅为已归档的条件性说明，**当前无待执行回放、设备查询、任务或服务操作**；历史DB缺口不再作为行动请求。

原第24行“六个源码hash”计数已更正为“七个直接判分链路源码hash”，指向已独立核对的readonly receipt。独立验收与owner最终离线收口决定一致，可交父复核后交付014；不推进下一项。
