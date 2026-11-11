# 052 RecipeDeleteDuplicateRecipes3：父复核

## 简单结论

这项不是051的“误判完成”，也不是040的“答案没交进去”。原Agent最终明确报告failed并承认误删；但它在操作时把列表上的摘要相同当作完整内容重复，先删除非目标食谱，再比较另一组内容。诚实报告失败值得保留，但不能抵消前面的破坏性判断缺口。

本项没有确认AMKernel Runtime执行/传输故障。主责任在模型规划、对象等价判断与技能指导可改善的安全前提，不能只凭reward0归因Runtime。

## 原记录与调用范围

- 冻结原r12 v2 index52，RecipeDeleteDuplicateRecipes3，seed2676632063，参数SHA `76a838d9d504ef8cd9ff928b7f30ddc1c11b2674e5ee08e14b797f7baf8ac90a`；身份与原manifest登记一致。
- 原执行30/34个计步动作，未预算耗尽；30次Python调用，26completed、4failed，全30次kernel alive。原reward0、error/invalidReason null。
- 原final为JSON，taskOutcome="failed"，evidence自认删除了不同Avocado变体。它同时把Pan与部分Avocado称为duplicate，这个称呼仍不受参数等价关系支持；不能把整段final当成已验证数据库事实。
- 原quit返回true，所属session verified absent；task teardown完成、environment关闭。这里是原清理记录，不是本次重新检查服务。

父只读原raw，按toolCallId保留最后完整代码/参数和响应，并记录首次出现相同完整代码的流事件行。所有30个codeSHA逐项匹配原result；三原件hash及抽取位于本目录 `original-source-identity.json`、`original-python-executions.json`。独立复核仍需分别核参数和响应，不以代码hash替代所有字段证明。

## 原任务参数证明什么

父实际普通Python比较与安装版纯validator调用见 `parent-parameter-equivalence-smoke.json`、`parent-installed-predicate-smoke.json`：

- 32逻辑行，31种完整业务内容；唯一重复对属于Butternut。
- Pan两行是两种不同内容；Avocado三行也有三种不同内容。相同标题或简介不能证明可删。
- Butternut十行有九种完整内容，只是其中两份完全重复，不是十份全部重复。
- 对原参数分配显式合成ID、构造数据对象，仅调用安装版 `RecipeDeleteDuplicateRecipes3.validate_deletion_integrity`，不构造环境、不初始化任务、不跑is_successful、不查DB。
- 只删目标对中的任一份且保全其余时True；不删、两目标全删时False；任一Pan或Avocado单删False，即使同时正确删了一份目标，再删noise仍False。枚举一Pan加两Avocado的六种组合均False。

以上证明业务等价与保全语义，不是原前后DB、原IDs、新官方评分，也不能推定原scorer首个失败分支。脚本的ffmpeg RuntimeWarning已完整保留，纯方法实际退出0，不为该警告修改依赖或环境。

## 最早偏离与后来发生的事情

1. 原raw2074已提出同标题/简介三项“likely duplicates”；raw2364继续按窗口中同摘要重复讨论删除。它们是可见的模型假设，不是完整等价证据。
2. exec7（raw2073/2078）固定五次滑动，保存六窗口，同时用seen_sigs集合式去重摘要，丢掉同摘要的独立出现次数。exec8返回18种摘要，exec9保留窗口重复。片段有裁切空简介且没有到末尾判据，不能把18摘要直接当32对象的完整枚举，也不能相加窗口条数。
3. exec11（raw2870/2875）打开一份Pan详情，没有另一份详情作为保留对照。原参数证明两份Pan内容不同；最终删除前没有完整等价对。
4. exec12–15进入菜单、删除和确认；首次不可逆确认是exec15（raw3874/3879）。确认点击与列表等待在前，第三行读取父节点才抛NoSuchElementException。整次failed不能解释为未执行点击或已回滚。exec16随后只读刷新页面，这一步是合适的恢复观察，应保留，不能诬称重放同一次删除。
5. exec17（raw4087/4092）UiScrollable被原Harness计步策略拒绝，提示use admitted driver.swipe。它是明确边界，不是AMKernel缺乏滚动能力；后续改用普通搜索。
6. exec20–21分别按全局标题数组和简介数组取值。exec21显示两标题、三简介，没有同卡片绑定证据。exec22（raw5125/5130）按titles[0]打开并串联确认Avocado删除，返回两个相同简介。注释“first A-description card”没有由实际卡片身份来证明。
7. exec23（raw5242/5247）寻找Undo，返回空。exec24（raw5583/5588）又按首条执行另一轮删除确认，返回一标题/简介。能直接说的是“查撤销未果后又删除”；附近思考只有签名、空正文，不能伪称精确知道它在24前已经主观确认误删。
8. exec25搜索Butternut；exec26–29读取四份详情，返回不同份数、时间、材料或步骤，比较均不相等。原raw3736虽然意识到同摘要可能不同，却又猜Butternut可能都是副本；到这里才落实部分详情比较。四份不同不证明十份中没有真正重复对，也不能由点击索引推定全列表覆盖。
9. 后续没有Butternut删除调用；exec30正常quit。原final承认failed，不把它改写为错误完成。原轨迹没有可信恢复动作，也没有凭模板新建食谱；不能把原思考里曾设想恢复当作实际实施了恢复。

三次删除确认调用与其返回/后续可见页面是保留证据；历史持久删除的精确数量、ID和完整前后DB未知。

## 分层与整体修改意见

- 模型/技能：完整内容比较、保留副本、扫描时保留候选次数与覆盖依据、同卡片身份绑定、错误后先核实、找不到可靠撤销时停止破坏链。已经写进 `../skill-optimization-proposal.md` 的052节及整体候选位置。
- 该意见保留Python内部有条件的批量观察与操作，不要求每次点击都回模型，不增加状态机、自动恢复或任务特例。
- 额外调用成本：exec2导入lxml失败，exec7/20的tuple结果为有界repr，exec18等待错误控件类而失败；已有标准库解析、JSON-native输出、真实控件类型和部分执行后观察指导应复用。这些不是已证明的误删主因，不为此安装包或硬改Runtime。
- Harness：exec17明确拒绝UiScrollable是本次评测计步边界，不绕过或放宽；没有证据说这项因为040式答案字段契约得0。
- 原预算未耗尽，不能把全部问题简化成预算不够，也不增加预算制造成功。

## 协同与边界

按用户要求用herdr协调评测项目w4:p1与w4:p2。p1负责安装源码/RECORD、参数差异、纯判断函数和独立owner五件；p2负责raw重新join、责任边界与最终独立验收；父亲读原调用/思考、亲跑参数及安装纯方法，并维护父review和整体建议。各自文件不覆盖。

本项零设备、ADB、Appium操作、新session、DB查询、环境初始化、完整评分、服务改动、安装升级、生产/正式技能改动或build/lint/test suite/formatter。仅离线诊断及修改意见，无新官方成绩、无外部资源需要清理，不推进060或全量评测。
