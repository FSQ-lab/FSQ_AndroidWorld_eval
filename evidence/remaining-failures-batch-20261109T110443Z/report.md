# 060之后全部18个原失败项：离线批量诊断与Harness修复

## 结论与范围

已逐项分析原r12 v2 campaign中060之后全部18个失败项；每案有`report.md`、`diagnosis.json`和原完整tool ID/arguments/code证据。模型/技能问题、应用环境症状、提交/捕获契约和评分内容边界分开处理；没有因reward0推定AMKernel故障。

本阶段遵循后续授权的“先汇总skill意见、后统一fix；确认Harness问题可修复”边界：**正式AMKernel skill与Runtime未改；没有现场设备操作、任务重放、Agent重跑、新官方评分或全量campaign。** 不把本次离线验证冒充原用户最初要求的现场收益验收。此前阶段的现场实验不算本批验证。

本批唯一新增产品修复位于评测仓库：**r15初始化参考时钟接口**。原第一提示缺可信相对日期锚点；开发版现在在官方`initialize_task`成功后，将`task.device_time`的aware时刻和规范UTC-offset timezone传入`task.timeContext`，在exact-goal之外交付Agent，标明`initialization_reference_not_live`。这是Harness责任，不是AMKernel Runtime修复；缺接口已证实，但未证明它是任何单案0分的唯一原因。

## 原记录与证据统计

以下全部是冻结历史统计，不是重跑成绩：18案均reward0；9案`step_budget`、9案`completed`；合计185个已接受动作。原308份PythonResponse为261 completed、47 failed，全部报告kernel alive。另有docs/skill读取及110的内层JSON拒绝，不能混进PythonResponse数量。

原记录显示这18案的受管session均已quit并确认缺席、官方teardown及环境close完成。它只证明历史清理，不证明当前共享服务/session状态。本批没有获取设备/session资源，因此无新增设备资源需要回收。

证据：`inventory.json`、`parent-original-runtime-response-tally.json`、`parent-observed-original-summary.json`、`parent-final-original-call-proof-audit.json`。父级对全部18案完成原raw/normalized/作者proof的完整ID与参数/code SHA核对；家族proof schema差异和Unicode序列化导致的审计脚本输入修正保留在收据，不隐藏首轮错误，也未改原证据。

## 逐项结论

每行链接包含完整时间线、最早支持的偏离与未知项。这里的候选答案兼容性不是新reward，未补造历史数据库、初始化后proto或原评分首个失败分支。

| 原案 | 原动作/终态 | 最早支持的偏离或契约边界 | 分层结论与限制 |
|---|---|---|---|
| [073 Calendar next week](073-SimpleCalendarEventsInNextWeek/report.md) | 10/10；step_budget | raw2903周编号推理有误；raw3689清理指令后才有3804业务final | 旧Harness捕获缺失；跨页周日观察有价值，不能全算浪费。两标题候选与UI/模板兼容，未重判。 |
| [074 Calendar time range](074-SimpleCalendarEventsInTimeRange/report.md) | 10/10；step_budget | raw2373/2374不支持的`set_value`；2723/2724重试后超时，2963仍Oct15 | 模型/API恢复与输入提交验证不足；没有读到目标Friday结果。picker未提交的底层原因未知；另有旧final捕获缺失。 |
| [076 Calendar first after](076-SimpleCalendarFirstEventAfterStartTime/report.md) | 9/10；completed | raw3248含边界17:20事件，3384选择次日08:35 | 自然语言strict-after与官方模板恰在边界的期望有歧义。不能武断称模型算错；未重放评分。 |
| [080 Drawing](080-SimpleDrawProCreateDrawing/report.md) | 18/18；step_budget | raw1651/1654首次启动等待失败；1948/1951又走同路线 | 模型无进展恢复；ASI稍后出现，不能倒推为首次失败根因。最终SAVE被拒，原文件持久化状态未知；无新Harness计步修复。 |
| [082 SMS reply](082-SimpleSmsReplyMostRecent/report.md) | 12/12；step_budget | raw695/696首个Messages入口进入Google Messages | 目标身份/路线错误，未完成要求的回复；launcher占位与ASI为环境症状。旧SMS DB、scorer时刻包和唯一0分分支未知。 |
| [084 SMS send](084-SimpleSmsSend/report.md) | 12/12；step_budget | raw711/712先入错误包 | 后来到达目标app，但换行未确认收件人，未观察到正文/发送；模型/技能输入提交与预算问题。 |
| [085 SMS clipboard](085-SimpleSmsSendClipboardContent/report.md) | 8/12；completed | raw736/737先入错误包，最终诚实blocked | 不是硬预算终止；未到目标app，也未执行clipboard读取/粘贴。不能据此判clipboard实现坏或证明ASI因果。 |
| [086 SMS received address](086-SimpleSmsSendReceivedAddress/report.md) | 18/18；step_budget | raw823/824先入错误包；目标路线较晚 | 原sender Oscar与目标Gabriel不同。正文已输入，但发送click被动作门拒绝；一次额外click不保证官方成功，原DB/评分时包未知。 |
| [087 Sports count](087-SportsTrackerActivitiesCountForWeek/report.md) | 9/10；completed | raw3547最终答1；raw2441的候选行不足以证明完整类别映射 | 模型枚举/覆盖不足，静态模板COUNT2与1不符；另有旧string契约缺口，非Runtime故障。未保留历史initialized proto，不补造实际期望返回。 |
| [089 Sports duration](089-SportsTrackerActivityDuration/report.md) | 5/10；completed | raw2461提交number `135` | 旧提示未明确string，答案未通过原包装；2:15:00到135分钟的UI/算术兼容不能冒充新官方通过。 |
| [090 Sports longest](090-SportsTrackerLongestDistanceActivity/report.md) | 10/10；step_budget | raw4790晚final为nested object，normalized final缺失 | 旧捕获与类型双层问题；0.75mi到约1207m兼容，历史唯一评分分支/完整范围验证不补造。 |
| [091 Sports distance](091-SportsTrackerTotalDistanceForCategoryOverInterval/report.md) | 14/20；completed | raw5827提交nested object | 旧string契约；可见聚合4.04mi与候选6502m换算兼容。`without_replacement`格式化与舍入必须考虑，不能从seed params直接抄期望值。 |
| [092 Sports weekly duration](092-SportsTrackerTotalDurationForCategoryThisWeek/report.md) | 9/10；completed | raw4679提交nested object | 旧string契约；可见running聚合1:45:00支持105分钟。旧“480”基于seed参数的推断无效，不改原0分。 |
| [101 Clipboard](101-SystemCopyToClipboard/report.md) | 9/10；completed | raw2439/2442桌面mouse ActionChains被拒；3211后native modifier成文本 | 模型/native输入语义；3487字段含U+E009及c。不是预算耗尽。Appium Settings getter自行启动后等待5000ms失败；官方Clipper路径不同，历史实际剪贴板字节与helper启动原因未知。 |
| [106 Tasks completed](106-TasksCompletedTasksForDate/report.md) | 10/10；step_budget | raw2396/2397切换后3行消失，却继续按“显示完成项”计划 | 菜单/完成状态误读和恢复成本，加旧捕获缺失；三标题候选与行差分兼容，不声称已验证历史期望或唯一入口。 |
| [107 Tasks next week](107-TasksDueNextWeek/report.md) | 6/10；completed | raw1901把Fri直接认作下周日期；raw1735/2036并非日期排序 | 模型范围/覆盖问题。number20与source COUNT6不符；normalized捕获该number，但原string-only包装拒收。修类型仍不修业务值。sort/filter已见但实际可达性未知。 |
| [110 Tasks high priority](110-TasksHighPriorityTasksDueOnDate/report.md) | 10/10；step_budget | raw2167查找失败；3893/3894内层JSON invalid escape被拒；6882晚final未捕获 | 模型调用边界与旧捕获并存；20份PythonResponse、1 docs、1拒绝write必须分开。goal是high而非highest，候选title静态对应不是新分数。 |
| [111 Tasks incomplete by](111-TasksIncompleteTasksOnDate/report.md) | 6/10；completed | raw3910将17项宣称为unchecked成员 | **by Thursday解释正确**。源码noise排除due≤cutoff且completed=0；问题是未完成成员资格未核实。17对3会触发静态长度分支，不冒称原判分分支；重复标题来源未知。 |

## 已修与未修

### 新修：Harness r15参考时钟接口

位置：评测仓库`src/fsq_androidworld_eval/task_time.py`、`runner.py`、`campaign.py`、`scorer.py`及对应tests、`forwarder/README.md`。生产runner只在官方初始化成功后取参考值；不以host时间补值、不标为实时设备测量、不修改exact goal或冻结params。r15迁移所有相关版本门，保留r13 receipt/private-evidence与r14 coexistence/actual-capability约束，旧r12/r13/r14不追补clock字段。

实际开发helper smoke覆盖18/18 exact goal字节不变、params不变、时钟context/provenance及序列化路径；禁用网络、环境/任务初始化。这是代码路径验证，不是设备或Agent重跑。详见`harness/repair-report.md`、`harness/clock-interface-after.json`与`independent-harness-acceptance.json`。

### 既有修复，不重复记功

开发版string-only输出提示、bounded first-business-final receipt/清理分离、coexistence guard此前已存在。本批不把这些算新增fix，不强转原number/object，不补入原晚final，不重算r12 v2成绩。

### 仅候选：AMKernel/技能

已汇总至共享[skill优化proposal](../amkernel-field-optimization-20261109/per-task-review/skill-optimization-proposal.md#073111-剩余18案身份业务成员资格输入提交和收尾边界)：目标身份、输入提交、业务成员资格、范围覆盖、日期谓词、调用边界、动作预算与环境症状分层。保留Python批量能力；不引入workflow状态机、自动重试、benchmark答案、固定包/坐标或Runtime业务判断。

本批未确认AMKernel Runtime/MCP实现故障导致这些失败。308份响应均报告alive只能支持原kernel存活记录，不能证明所有调用正确。101 helper故障、ASI及picker提交原因仍未知；不据此强启服务、换依赖或重建session。

## 验证、独立验收与不可变性

- Harness九文件focused首轮：**569 passed / 2 failed**。两项分别为旧scheduler硬编码r14的incidental断言和新增full协议测试断言字段问题；删除前者、修正后者后仅重跑这两项：**2 passed**。不是一次571全绿。原输出与修正保留在`harness/focused-checks*.json`。
- after smoke首次因输入摘要无stepBudget停止；保留失败，只改smoke输入后成功。clipboard helper smoke使用真实安装getter与纯内存ADB adapter，走自身启动与真实5000ms等待失败路径，未到broadcast/IME，未接触设备。101官方Client序列化smoke也不冒充UI复制或真实clipboard结果。
- 独立验收已18/18通过并保留逐案未知，总入口`independent-final-delivery.json`；36份最终report/diagnosis签名见`independent-case-acceptance.json`，共享proposal全文及新增165–189节也已签验。Harness最终源码/行为证据见`independent-harness-acceptance.json`；父级最终摘要绑定结果见`final-delivery-receipt.json`，不借用作者自验代替独立审查。
- 冻结清单、报告与原campaign文件按历史696件SHA基线对比；正式skill9件按本批开始SHA对比。最终结果见`final-delivery-receipt.json`。没有冻结安装写入或依赖变更；SHA覆盖范围以收据为准，不声称扫描所有机器文件。

## 下一步

本批离线诊断完成，不默认启动116项全量。正式skill仍待后续统一fix；其真实应用收益与少量原成功样本回归未在本阶段执行，也不能用离线smoke替代。若要评估提升，需独立Agent实验；r15身份已变更，先重建环境资格、完整无Agent预演与校准门禁，再在相同参数、模型、预算、重试和官方evaluator下做少量代表样本。新实验独立保存，不替换原失败，不混称旧冻结协议成绩。
