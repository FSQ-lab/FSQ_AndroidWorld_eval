# 052 RecipeDeleteDuplicateRecipes3：独立离线验收

署名：**w4:p2 独立052离线复核助手**。签署时间：**2026-11-09T10:36:47Z**。

目录：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/recipe-duplicate-052-diagnosis-20261109`。

## 裁定

**最终owner五文件与通用建议、修订父review及proposal052节验收通过。仅限052离线诊断事实与候选意见，不是fix验收。** 五件实际SHA匹配冻结manifest，summary为`983e906d555d01b04041ce6a97513064703cf2312cc94e8fe1695a8dea773503`。本人逐项署名版本见JSON。

本项主偏离在模型把摘要候选升格为完整等价、对象字段未同卡片绑定，以及未满足保全前提便提交删除。原final诚实报告failed，不能改写成错误完成；其中“duplicate Pan/Avocado”仍是未经成立的标签。没有证据确立AMKernel执行/传输故障，也不因官方0推定原DB删数、IDs或首个失败条件。

## 身份、raw重join与已修冲突

只查原r12v2 **index52**，seed **2676632063**，paramsTransport **seed**，params SHA `76a838d9d504ef8cd9ff928b7f30ddc1c11b2674e5ee08e14b797f7baf8ac90a`。不是051/040，不推进060。

本人独立按**完整toolCallId**重建canonical tool_execution_start/end，再与父采用的toolcall_end/message_end表示逐一对应；排除一次只有文档读取而无code的请求。全部30份**code、完整arguments、response**逐对象匹配父提取，30个codeSHA均等原result，三原件SHA均与已登记一致；不是只比代码hash或盲信原行号。详见 `independent-052-raw-join-proof.json`。

初审发现父review混入错误seed/SHA、六处调用锚点及title/description数量颠倒，已通过herdr直接反馈，由父自行修正。已亲读修订版：review SHA **`45c03a556be1870998b50657058986b578d10de44e5ec398cdfdb7fd91043894`**，exec21明确**两title/三description**。审计保存在 `independent-052-review-conflict-audit.json`，列出旧观察值、正确值及原tool快照`7A7D`；纠正前没有独立捕获字节SHA，**未编造旧SHA**。原30提取和原件未改，本作者未覆盖父文件。此前父自报的exec19→18修正不算作本作者发现。

## Direct：原思考、扫描与首次破坏性确认

已亲读原raw可见的16条非空thinking摘要（summary=true）及全部37条空/非空元记录；未解密签名，未把空正文补成心理状态。原文另存 `independent-052-original-thinking.json`。

- raw2074提出同标题/简介三项“likely duplicates”；作为候选筛选尚可，但不足以授权exact-duplicate删除。raw2364已注意丢失出现次数，却仍依赖窗口摘要重复。
- exec7固定5次swipe、6个观察窗口。`seen_sigs`按title/description/source去重会丢失其自身的出现次数；**windows没有去重，exec9保留同窗口重复**，不能说所有扫描信息都已消失。跨窗口重叠缺稳定对象身份，末窗到Raspberry不是到末尾判据。
- exec8的18种观察摘要与冻结参数投影的21种摘要不是历史漏对象数：裁切可能出现空description，窗口会重叠，摘要不等于对象。不能据18对21宣布漏3条，也不能直接相加窗口项数。
- exec11只看一份Pan详情，没有另一份保留对照。raw3736虽然认识同摘要可能不同，又猜Butternut可能都是副本；没有在Pan删除前落实完整等价对。
- **首次破坏性确认是exec15的line1**；line2列表等待已过，line3父节点观察才抛NoSuchElement。failed不是未点击、不是回滚。exec16只读刷新是正确的部分执行后核实，不是重放删除。这里确认请求前缀与界面转换，不为持久化DB变化盖章。
- exec17收到明确Harness政策拒绝：Only pure UiSelector observations are supported; scrolling searches consume multiple interactions。它不是AMKernel没有滚动能力。exec18点Search后等待EditText超时，exec19只读检查成功；不能把19错写成失败调用。

## Direct：Avocado错绑、Undo与后来的比较

exec20/21独立查询全局title/description数组；exec21为2对3。exec22注释称“first A-description card”，实际只重新查询`titles[0]`，没有同卡片描述关联、稳定对象身份或完整详情对照；导航、过滤和删除后索引也不能继续当对象身份。

exec22返回两条A简介；exec23查Undo为空；exec24又重新取首title并提交一次删除，返回一条title/简介。这些是直接行为和观察；无同卡片绑定，不能仅按数组给历史逻辑行或主键定名。三个Avocado在参数层本就全异，即使点中“想要的A”也没有完整等价删除前提。

raw5126/5243/5584的thinking正文为空、signature非空、summary=false。**不能由查Undo或这些空记录断言24前已主观确认误删，也不能反向断言它必然不知道。** 规范性的“身份冲突或确认误删后应止损”不补成历史内心trace。

exec26–29读取四份Butternut详情，返回字段两两不同；按已返回的可见字段可与冻结noise0/12/24/25对应，但这不是DB ID。四份不同不覆盖全部10份同名记录，也不否定真正重复pair。之后没有Butternut确认删除调用；exec30正常quit；原final为failed且承认保全未达成。曾设想恢复不等于实施了恢复。

## 参数/源码：真实exact-duplicate与保全契约

独立按Recipe全部9个非ID业务字段比较冻结32逻辑行，得到31种完整内容：唯一重复组是两份Butternut target。Butternut共有10行/9种内容；Pan2份各不同，Avocado3份各不同，均为应保留的noise。Pan不同字段为servings、ingredients、directions；Avocado也含time/servings/ingredients等差异。

实际三个安装源码已由本作者逐件对distribution RECORD核对一致。scorer继承`DeleteMultipleRows.is_successful`，**未调用**；具体predicate是`RecipeDeleteDuplicateRecipes.validate_deletion_integrity`，对target1或target2的removal integrity做OR。完整其他before对象必须保留，after不能有新对象；没有独立after行数检查。参数recipeId=-1是哨兵，实际rows_to_delete来自初始化before，不能冒称已掌握历史IDs。

## 合成：实际纯predicate，不是历史DB或reward

本人实际调用安装版bound predicate，使用原32行完整字段，仅指定**显式合成ID820000+noise索引、830000/830001 target**。本地task未初始化；没有env/init/is_successful/DB。

20个受控例：只删任一target且保全其余为True；不删、全删target、任意Pan/Avocado单删、正确target再删noise均False；一Pan加两Avocado的6种组合也全部False。完整输出见 `independent-052-installed-predicate-smoke.json`。owner/父的独立收据不代替本作者实际执行。

因此有两条独立**条件充分失败机制**：若实际targetpair保持不变，遗漏目标去重足以失败；若任一实际noise丢失，即使删对一份target仍会保全失败。不能把合成候选或原UI调用升格为某一历史分支实际先触发。

## Unknown：本次没有越过的边界

原before/after DB、实际rows_to_delete主键、持久删掉的精确数量/IDs、实际首false行或唯一0因未知。原登记只看到三次确认请求及其后续UI；不因此宣布原DB精确删3份，也不把“没对Butternut发删除”当作DB证明target原样存活。

原30/34动作未耗尽，30次Python中26完成、4失败（2/15/17/18），全kernel alive。诚实failed不等于安全执行，也不能被误标为虚假成功。无新fix、正式skill修改、reward或任务无解声明，不套051历史DB结论。

## 最终文件、建议与只读范围

owner五文件及`owner-generic-suggestions.json`全部亲读，实际SHA匹配`owner-final-delivery.json`。父修订review、proposal新增052节及“分层和正式修改候选位置”已亲读并各记录接受版本SHA。保留批量观察与有条件动作；在身份冲突/不可逆前提失效时截断依赖链，而不是每点击都往返模型；没有工作流状态机、自动恢复、任务答案特例或DB补造建议。候选意见不是已验证收益。

owner2186历史/152技能/3源码收据已审阅相符；本作者没有重跑其全量hash扫描，也不借其署名代替本人的30参数/响应核对。本人独立范围见 `independent-052-readonly-receipt.json`：原三件、30完整ID配对、30codeSHA、三源码RECORD、20纯候选及指定文档。零设备/ADB/Appium/session/env/init/is_successful/DB/服务/现场/回放/生产/正式skill/build/tests/formatter；只新增本目录independent-052产物。

**052离线诊断及建议事实验收完成，供父复核后交付；无待执行现场动作，不推进060。**
