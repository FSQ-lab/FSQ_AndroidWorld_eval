# 原r12v2 052 RecipeDeleteDuplicateRecipes3：离线诊断

## 结论

**052的冻结参数中只有Butternut Squash Soup目标pair是全字段重复；Pan两份、Avocado三份均为不同内容的noise，必须全部保全。** 原Agent最终诚实返回`failed`并承认误删，不是错误宣告完成；但final中把Pan/Avocado称为“duplicate”仍然有事实错误，不能替它写成真去重成功。

实际安装纯predicate已执行：只删除任意一份目标且保全其余行可以通过；目标pair完全不动会失败；任意Pan/Avocado noise缺失会失败，即使另已正确删除一份目标。**这是冻结参数与受控纯执行证明的独立充分机制，不是原数据库删数、IDs或历史首失败分支的还原。** 原official0保留，原before/after DB未保存，无法唯一归因。

仅本项离线诊断及通用建议完成。不查设备、不初始化、不重跑、不读DB、不修改生产/安装/正式skill，不推进060；不套051的历史DB结论。

## 原身份与直接记录

原attempt：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/`。

Goal：`Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains`。

- manifest index52；seed2676632063；参数transport为**seed**；complexity3.4，maxSteps34；params SHA256 `76a838d9d504ef8cd9ff928b7f30ddc1c11b2674e5ee08e14b797f7baf8ac90a`。只读取原冻结参数，未重新生成。
- 原30/34业务动作、31个reference steps；30次Python调用，26 completed、4 failed，全部Kernel alive，无AMKernel timed_out。Agent正常终止，未耗尽动作预算。
- 原officialReward0.0，error/invalidReason均null；原evaluator0.127秒；task teardown、environment close完成；quit返回成功并核实session absent。
- 原final为`taskOutcome:"failed"`，并说保存唯一recipe的要求未实现。它是模型自述，不是DB dump，也不是官方评分输入。
- 三原件独立重算：result `ad96838a4ff5631247bc8d4a36bc59a5f6673c6e83b20654e0b6420172256890`；normalized `ee9a5e6b45cfaaf251f3112bdd7b825bb25cee1abd00ed4a5e52a48f18c3050d`；raw `606de86de517d38042ecd9c3091b750e48c4839ab8fbc337b8da5bcb00d825d9`。

父提取位于 `evidence/amkernel-field-optimization-20261109/per-task-review/052-RecipeDeleteDuplicateRecipes3/original-python-executions.json`。owner核对其中全部30份code SHA与原result逐项一致，读取本项有关原字段/调用响应；p2负责独立逐raw响应复核。owner不借用父/p2署名宣称自己已独立解析全部原raw响应。

## 实际安装身份、初始化和完整保全契约

源码均来自实际安装 `.venv/lib/python3.11/site-packages/android_world/`；`recipe.py`、`sqlite_validators.py`、`sqlite_schema_utils.py`三个文件的SHA均与AndroidWorld0.1.0安装distribution RECORD一致。原result记录revision55ddaf5edc6f6c25673aed343907d5b9dca66f84、Harness12。当前文件/RECORD核对不是未留存的原完整安装树证明。

### 目标与noise如何进入判据

- `recipe.py:272–315`为本任务类：n_rows_noise30，生成逻辑会制造靠顶部的Avocado变体及同名目标变体，真正目标只重复一次。**本轮没有调用generate_random_params**；判定以原params逐字段内容为准。
- `sqlite_validators.py:257–264`初始化先加入noise；`348–358`再加入目标，读取`before`，按新行在末尾的代码约定取得`rows_to_delete`；`411–415`校验参数pair并保存duplicate_rows。它是源码意图/绑定逻辑，不是已留存的历史before顺序或IDs。
- `DeleteDuplicateRows._validate_candidates:383–398`比较Recipe每个dataclass字段，唯独跳过db_key。Recipe共有9个非ID业务字段：title、description、servings、preparationTime、source、ingredients、directions、favorite、imageName。不是标题或标题+简介去重，也没有fuzzy阈值。
- `sqlite_schema_utils.py:197–214`的recipeId=-1是未从DB读取时的哨兵；不能把原params中的-1当成历史主键。实际判据使用原初始化后取到的两份target IDs，本项未留存这些值。

### 真正scorer与纯predicate

本任务继承的实际scorer是 **`DeleteMultipleRows.is_successful`**（`sqlite_validators.py:360–369`）：读取after，再用before/after执行具体validator，最后返回1或0。不是根据final的failed或success字符串评分。

具体validator是 **`RecipeDeleteDuplicateRecipes.validate_deletion_integrity`**（`recipe.py:200–211`）：

- 分别尝试删除target1或target2的ID，两种合法选择为OR关系；保留哪一份都可以。
- `validate_rows_removal_integrity:73–115`要求指定ID属于before；对应原完整对象不再在after；before中其他每个完整对象仍在after；after不能出现before中没有的新对象。
- 因此在合法唯一主键行状态下，30份noise和另一份target都必须原样保留。误删noise并不因“目标那份也删对了”而豁免。
- 函数基于ID和完整dataclass成员关系，没有单独的after行数检查；不能把它简化成“少一行就成功”。受控唯一ID场景中，合法结果为32→31行。

详情及三源码hash见 `owner-scorer-source-proof.json`。

## 冻结参数中的重复与逐字段差异

32份逻辑行去掉recipeId后共有31种完整内容：**唯一重复组是两份target Butternut**。其余30份noise与它们及彼此不完全相同。Butternut同名共有10行/9种内容，Pan2行/2种，Avocado3行/3种。

目标pair的共同特征包括：`preparationTime=30 mins`、`servings=3-4 servings`、`ingredients=quantities to taste`；description为`A quick and easy meal, perfect for busy weekdays.`，directions末句为`Garnish with fresh herbs for a more vibrant taste.`；其他字段也完全一致。

### Pan不是重复

两份Pan都同标题、同quick/easy简介、同1 hrs，但以下字段不同：

| 原noise索引（从0起） | servings | ingredients | directions末句 |
|---|---|---|---|
| 7 | 6 servings | n/a | Try adding a pinch of your favorite spices for extra flavor. |
| 13 | 1 serving | varies | Feel free to substitute with ingredients you have on hand. |

它们是两份不同recipe，均不是本次目标。

### Avocado也没有真正重复

| 原noise索引（从0起） | description类别 | preparationTime | servings | ingredients | directions末句 |
|---|---|---|---|---|---|
| 21 | A quick and easy meal… | 4 hrs | 6 servings | various amounts | Try adding a pinch of your favorite spices for extra flavor. |
| 22 | An ideal recipe for experimenting… | 2 hrs | 6 servings | as needed | Garnish with fresh herbs for a more vibrant taste. |
| 23 | A quick and easy meal… | 1 hrs | 3-4 servings | n/a | Try adding a pinch of your favorite spices for extra flavor. |

21/23即使标题、description和directions一致，仍有ingredients、time、servings三个差异。21/22差description、directions、ingredients、time；22/23另差servings。标题+简介不能作exact-duplicate证明。

完整原值及所选组所有pairwise字段差异见 `owner-parameter-field-differences.json`。表格是参数层，不冒充原DB记录或真实持久化ID。

## 实际纯predicate执行：明确合成ID，不伪造历史DB

`owner-installed-predicate-smoke.json`记录本作者真实调用安装函数的结果。只构造未初始化的本地任务和Recipe对象，使用原32行的字段值；为逻辑noise指定**合成ID70000+索引**、两份target指定**合成ID71000/71001**。这些值没有历史含义。

未调用env、initialize_task、is_successful、数据库、设备或外部服务。调用的是原实际bound `validate_deletion_integrity`及原generic removal predicate；为了展示条件，也分别独立计算两个target分支。后者不是原OR表达式或原官方判分的逐分支执行trace。

| 受控逻辑状态 | 实际原predicate |
|---|---|
| 不删任何行，目标pair都保留 | False |
| 只删target0，其余全部保全 | True |
| 只删target1，其余全部保全 | True |
| 两份target都删掉 | False |
| 单独删任一Pan/Avocado noise，targetpair都不动（5种） | 全部False |
| 正确删target0，再删任一Pan/Avocado noise（5种） | 全部False |
| Pan与Avocado五个noise都删掉，targetpair不动 | False |
| 正确删target0，但修改保留noise字段 | False |

这证明两类**条件充分失败机制**：

1. 遗漏目标去重——两份指定target都仍存在，本身已足以False，即使noise完全没动。
2. 破坏noise保全——任一非目标完整行缺失，本身就会使两个合法target分支都False，即使目标去重做对。

两target都不保留也不行；需要保留其中一份。父另有实际安装纯predicate与参数等价smoke，包含1Pan+2Avocado的6个组合，均False；不把这些候选当作原实际删掉了哪三份。

## 原动作轨迹、失败与诚实终止

以下原行来自父署名提取（30份code SHA已由owner对原result核对）；独立逐raw join由p2另署名。

- exec11 raw2870/2875打开Pan详情，UI返回1 serving、1 hrs、varies及substitute方向文本，与noise13的可见业务字段相符；未先对另一份的完整详情建立相等证明。
- exec14 raw3735/3740进入`Delete this recipe?`确认框。exec15 raw3874/3879先点击确认，line2等列表，随后**line3观察失败**。failed不等于整cell回滚，也不能因此盲目再删一次。exec16 raw3963/3968仍能读取列表。这里只证明请求/界面转换，不给持久删数盖章。
- exec17 raw4087/4092的UiScrollable.scrollToBeginning(20)被Harness明示政策拒绝：`Only pure UiSelector observations are supported; scrolling searches consume multiple interactions`。这是本轮动作策略边界，不归成AMKernel/Android SDK故障，也不建议绕过。
- exec18 raw4215/4220点击Search后等待EditText超时；Kernel仍alive。exec2的lxml import失败也已被后续标准库路径恢复。这些失败不等于设备不可用。
- exec21 raw4770/4775分别查询title数组和description数组，长度不一致；不能按全局索引强行拼成可靠的每条recipe身份。
- exec22 raw5125/5130打开列表首项并确认删除；返回两个同标题、quick/easy description。exec23 raw5242/5247查询Undo，返回空。**它只证明查询了恢复入口，不证明恢复成功或当时主观已知误删。**
- exec24 raw5583/5588再次打开首项并确认删除，返回一个Avocado标题及简介。22–24附近thinking文本为空、只留签名，不能从中编造“24前已经知道误删还故意继续”的内心状态。
- exec25 raw5829/5834搜索Butternut，只回读四个可见标题、三个description。exec26–29 raw6187/6192、6316/6321、6594/6599、6792/6797检查四个详情，并发现各不相同。其已返回字段与noise0、12、24、25相符，而非30 mins的目标pair；仍不是整个十份同名记录或真实ID的穷尽DB检查。
- exec30 raw7241/7246 quit成功；最终taskOutcome为failed并承认唯一recipe保全未达成。**诚实失败应保留，不把它改写为伪造完成。** 但final对Pan/Avocado“duplicate”的标签不被参数证据支持。

可说原登记动作没有对Butternut确认删除；不可把它直接升级为“已从DB证明两target原样存活”。同理不能从可见数/返回数组给出历史持久删数或主键列表。

## 未闭环的历史证据与当前修复状态

原before/after DB、实际rows_to_delete的主键和值、原generic predicate的逐分支返回/首失败对象没有持久化输入可供本slice还原。原task teardown已完成；当前DB不是原判分输入，本轮也没有去读取。

因此：

- **直接原记录：** 官方0、原calls/界面回读、真实failed终止及清理。
- **参数/源码推导：** 唯一目标pair与所有noise不应删除的语义；显示字段不足以证明完整recipe相等。
- **合成纯执行：** 原字段+显式合成唯一ID下两类独立失败机制。
- **未知：** 原持久化删掉了哪些实际IDs、准确多少行，原首个失败条件或唯一历史根因。

不套051的DB结论，不证明任务无解，不宣称AMKernel缺陷。没有生产fix、正式skill修改、新官方reward或新campaign执行；原0.0不变。

## 通用修改建议候选（不代改父proposal）

详见 `owner-generic-suggestions.json`：

1. 破坏性去重前按记录容器绑定身份，比较足够的完整业务字段；同标题/简介只做候选筛选。只要已见字段有差异，就不是exact duplicate，不应删除来试。
2. 独立标题/简介列表长度不一致时不得按索引强配；需要同一卡片/详情的字段关联与稳定定位。目标可能在可见区域之外，少数候选检查不等于穷尽。
3. 原动作可能已生效而后续观察报错时，先只读协调实际状态，不能把failed当成回滚后重放破坏性动作；尊重Harness动作政策，不用被拒的批量滚动规避预算。
4. **一旦通过实际观察确认误删或身份已不可靠，停止扩大破坏性操作**，仅在确知的正常恢复入口可用且授权范围内恢复并验证；无恢复证据就如实报告partial/failed及未知，不虚构undo、修复或完成。该建议不反推原模型的主观发现时点。
5. 保留原最终failed的诚实性，同时业务证据也应准确：未经逐字段核验的条目不得在final中称为真duplicate。

这些是通用候选意见，不泄露本项冻结target/IDs给执行Agent，不加自动重试/DB恢复/删除豁免，不承诺改skill即可拿1。

## 交付

最终owner五文件为本报告、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`。owner前缀文件保存具体来源、逐字段差异、纯执行与建议；父和p2另署名，互不覆盖。最终五件SHA冻结在`owner-final-delivery.json`后通知父/p2验收。
