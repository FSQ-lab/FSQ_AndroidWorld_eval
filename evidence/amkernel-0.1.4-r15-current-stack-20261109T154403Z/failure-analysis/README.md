# AMKernel 0.1.4正式Android测评：20项失败分析

## 状态与范围

**已完成跨项目调查与两阶段独立复核整合，最终模块纠偏版本已锁定。** 20案、44eval/37owner来源提案按既有7组去重，不直接相加。MA01–MA13全部接受并落实，无剩余报告分歧或外部等待；确认／可能／未知分层保留，不宣称全部历史根因已证。

唯一campaign：`amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`。正式116完成、96passed/20failed/0invalid/0cleanupfailure/0attemptretry，reward总和96.5，`fullValidScore=0.8318965517241379`（83.1897%，包含部分得分），`officialScore=null`。本分析保留原结果；115 `VlcCreateTwoPlaylists` reward=0.5，其余19个失败项reward=0。校准、预演不混入正式成绩。

被测身份：正式AMKernel0.1.4，发布commit `4d0a863e6a65288bfdb7ce2756410908fb097416`；wheel SHA256 `6a26fa8469c28c8f125e19e4da15f94476375604da58cf1e89f7ee00ef2788de`；模型`github-copilot/gpt-5.6-sol`，Harnessr15／OMP18.18.3。原116任务、seed30、单实例/单业务attempt、参数/顺序/动作/时间预算沿用。历史r12／OMP18.12.6不同，不能把差异纯归于AMKernel或Skills。

## 阅读入口

| 文件 | 用途 |
|---|---|
| [cases.md](cases.md) | 20案完整索引和8领域完整叙述：goal/oracle/初始化、时间线、实际代码/输出锚点、动作账本、因果与独立fix |
| [cases.json](cases.json) | 按原index排序的20案结构化总入口；完整params、oracle source/symbol/行、原工具调用/响应、分维confidence、缺口、44fix落点与证伪；按case查询，不整体倾倒 |
| [module-map.md](module-map.md) | 共性问题去重，测评项目/AndroidWorld、Agent/Skill、Runtime、Harness、环境的精确责任与fix边界 |
| [shared-offline-checks.json](shared-offline-checks.json) | 公共只读探针的可复现Python与实际输出：20案prompt、raw→parsed→answer、首个final/截止、391响应、352动作、Harness身份 |
| `domain-*.json` / `domain-*.md` / `domain-*-queries.md` | 原领域深查及pure probes；Recipe与System/SMS的查询/输出直接保存在领域md中 |
| [review.md](review.md) / [review.json](review.json) | 独立review原件，只读保留；31-file历史revision blob证据与逐fix审查 |
| [review-resolution.md](review-resolution.md) / [review-resolution.json](review-resolution.json) | R01–R07及MA01–MA13逐项处理、最终版本锁定、7组去重及最终核对 |
| [AMKernel模块报告](../../../../amkernel/evidence/android-eval-0.1.4-failure-analysis-20261110/module-analysis.md) / [JSON](../../../../amkernel/evidence/android-eval-0.1.4-failure-analysis-20261110/module-analysis.json) | 最终纠偏版20案/37提案/7组；accepted_all_13，最终SHA256见下；旧review锁定版及override仅保留历史溯源 |

`domain-*`及`shared-offline-checks.json`、`integration-checks.json`保留初版取证/执行收据，不改成事后重新验证；本批修订以四个主报告及`review-resolution`为准。独立review两文件只读保留，旧领域文本中的源码身份缺口与混合置信由主报告的R02/R04结构化结论明确收窄/替代。

## 初版重大结论：root cause与fix分列

### 1. 三处已证任务契约不一致，不等于三案都可直接改判

- **001录音命名**：goal/generator给完整`.m4a`名，`AudioRecorderRecordAudioWithFileName.is_successful`再加`.m4a`。源码矛盾confirmed；原始物理文件名/路径缺失，本次失分因果probable。**Fix需decision**：统一完整名或stem，不让Agent猜双扩展。
- **014费用备注**：完整102行源已还原，两个报销目标均已输入并重新打开；显示源追加`. Reimbursable.`，oracle却保留未加标记的note。实际可见备注被当前pure comparator拒绝；历史日志也有missing reference。源码分裂confirmed，最终DB/类别/金额未留全，本次精确失分分支仍probable。**Fix需decision**：标记究竟是持久备注还是筛选元数据，显示/参考/goal必须一致。
- **076日历边界**：模板期望事件恰在17:20，prompt问after17:20，oracle只返回该绑定title。契约不一致confirmed；Agent选次日不等于已证明自然语言答案正确。**Fix需decision**：明确at-or-after或生成严格更晚的事件并定义日期/并列最早范围。

这三项的文件/symbol/行、替代方案、风险和证伪条件见module-map的O1–O3。不得重算旧reward，也不提供“修正后成绩”。

### 2. 多项失败是具体Agent行为，不是笼统MCP失效

- **003/004**：原生点击/页面freshness未经确认即批量执行或采样；003完整迷宫拓扑和最短路线已恢复，6次element click未移动，coordinate touch有效；004还停在数字生成页面，未输入或Submit，7步未用。底层click为何无效/是否快照迟到unknown。
- **023/024/033/036**：文件身份与独立验收。改文未rename、默认`.md`替代extensionless名、少额外空行、源目录被当输出目录分别取证。033通用fuzzy通过但严格五行形状失败；036的`Moria`与参考字符串仍达到0.913 fuzzy，因此不能把该拼写差异当独立失分原因。
- **049/052/058**：049最后修复未读回即Save，文本变形层unknown；052原params为32occurrences/31内容类、恰一个二重对，不代表真实DB/完整UI已覆盖，34步内无Delete；058三次添加后1首，wrong-menu为probable且具体element IDs未捕获。
- **060/091/106/107**：060未测时长Select all后14首/68:25；091提交1996m单项，不是已证完整总数；106两项对三槽必拒绝，第三title/真实group/可达性未知；107原label谓词计20、oracle6，suffix-prefix合并保留重复occurrences，具体噪声日期/formatter仅source-linked或probable，不立merge根因。
- **085/098/030/115**：085未确认收件人且无正文/发送；098只证literal-node/验收缺口与一次swipe，初末整数、geometry、XML、是否改变数值unknown，不认定drag破坏255；030实际删除unknown；115反序可见、已读row menu，无Move up/down不证明所有路线不可行，gate closed(reason=agent_finished)、46/48非耗尽、哪份DB分项通过unknown，保留0.5。

相应Skill原则多数已实际加载；不遵循不证明缺指导。模块报告提供具体产品/Skill落点，但MA03/06/07/08/09/10/11纠正错误前提后才采用条件方案。跨项目可执行优先级、owner/file/symbol、最小fix/替代/风险/验收/decision见[module-map](module-map.md#cross-project-priority)；反事实实验均未执行。

### 3. 额外代码／协议风险与失败因果隔离

- **030 metadata语义**：helper文档ctime与`ls -u`访问时间语义不一致；历史Toybox/mount/metadata未捕获，不能说它导致本次失分。
- **060初始化**：duration override没有调用基类初始化/storage隔离链，存在seed/时钟/应用/旧存储可比性风险；实际歌曲集合/时长未归档，不能用该风险替代已见68:25行为链。
- **IR列表matcher**：synthetic pure probe证实长度相等后的`any`非一对一可能接受重复答案，是latent false-positive缺陷；**不是106两项对三槽被拒原因**。
- **Runtime结果契约**：17次有界repr跨10案，`output.truncated=false`不否定`result.kind=repr/result.truncated=true`结构损失；不是传输截断或10案根因confirmed。`src/amkernel/runner.py:_normalize_result/_bounded_repr`、`protocol.py:_json_encoded_size`已定位，优先caller JSON-native投影。outer`isError=false`/inner failed是结构化契约；failed前缀不回滚。SDK不存在方法/default mouse与Harness手势拒绝分层，不标Runtimebug。InvalidElementStateException诊断缺口原391无实例，非本轮因果。
- **原生-only/gesture约束**：WEBVIEW、复合UiScrollable、部分pointer payload在admission前被Harness明确拒绝；须与上游HTTP500、HTTP200无进展、Python异常和budget拒绝分开。不能自行打开DOM/多动作或增预算。

## 公共离线核查：实际输出

以下为初版、第一review及模块owner已完成的收据，本批仅引用，不重跑公式/源码blob/Runner/SDK/任务/评分/资格。实际第二review追加已读并采用全部13项；本次最终仅一次report field/link/保护字段与原证据保护核对，输出在review-resolution.json.finalVerification。

[公共收据](shared-offline-checks.json)保存了执行代码和20案逐条输出：

- 20/20原始第一条user prompt含exact goal、初始化参考时钟及非空string提交契约。
- 20/20归档parser结果精确相等、submission字节摘要匹配；实际raw receipt均为首个assistant stop，文本与归档一致，均在截止内。
- 391个结构化`python_exec`响应：328completed、63failed，全部`kernelState=alive`；另20次仅为工具路由文档read，未冒充执行或超时。统计含业务和cleanup响应。
- 352个获准UI动作，1个budget拒绝请求；20案终止为11completed/9step_budget。每案完整动作耗费而非“效率不足”见正文/JSON。
- 当前19个Harness身份输入摘要与冻结manifest精确一致：`861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`。
- quit/Agent finish在evaluator前，task teardown/DB clear在evaluator后。状态任务缺post-quit/pre-evaluator持久快照，不能从UI或正常quit推出精确磁盘/DB；IR的原始answer和task内存proto比对另行核清。

领域pure验证包括：fuzzy/严格换行的条件反证；费用102行与recipe32occurrence等价分组；迷宫拓扑/JavaScript源条件重建；Tasks26行重叠/日期边界；单位逐行舍入与严格容差；列表matcher latent重复缺陷。每个结果注明来自captured facts、current-source projection还是synthetic discriminator，不冒充初始化重放、历史DB或新官方reward。

## 数据缺口与置信规则

- 多数状态任务没有最终文件/DB/分项predicate收据；115哪份持久播放列表通过unknown，030是否真实删除unknown，098评估时亮度整数unknown。
- 060完整实际歌曲集合/各时长、106第三title、部分转录早期影像被RPC帧省略，不能补造；0916502m仅probable源/显示重建，00420250仅current-source/recorded-seed条件重建，不是历史JS变量。
- 原独立review31-file历史Git blob证据与模块owner17个current retained installed文件/13个发布Runtime模块收据互补；MA01核17digest与旧blob一致，不把31+17相加。执行者/来源分列；本批未重跑hash/probe。正式时刻完整import/安装/helper bytes与实际DB缺口仍未知；Harness Appium5.3.1与Agent5.2.5属不同解释器。
- 每案`confidenceAssessment`独立列`sourceDefectConfidence`、`observedBehaviorConfidence`、`episodeFailureCauseConfidence`和逐项`unknowns`；这些字段优先于保留的旧叙述标签，禁止把源码或行为confirmed升级为已证历史失分分支。
- R05保留085历史Node/Appium/helper lock/hash/实际加载字节和同时刻service证据缺口；当前`requireRunning`源码只解释可能机制。098完整XML、数值slider与评分时亮度整数未留存，097仅是同campaign机制反证，不能替代098历史状态。

## 原始结果与工作边界

原始入口：[最终summary](../../../campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/summary.json)、[checkpoint](../../../campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/checkpoint.jsonl)、[launch-state](../launch-state.json)、[最终handoff](../startup-handoff.json)、[release pins](../release-pins.json)。每案原result/raw/normalized/submission路径保存在cases.json；原始材料只读。

本阶段只新建/修改当前`failure-analysis/`内分析文件。没有连接设备/ADB/Appium/MCP，未操作共享服务，未重放正式任务/初始化/评分，未跑测试套件，未修产品/测试/运行配置，未改原manifest/result/checkpoint/raw，未commit/push。查询在隔离内存/纯进程中执行，可复现代码及实际输出保存在文档/JSON中；本目录未新增临时脚本，未把原始日志或图像base64倾倒到此主报告。

## 最终交付与未实施事项

1. 原独立review与实际R07追加`R07-moduleAlignment-20261110T005702Z`已完成并采用；13项处理/证据优势/裁定见[review-resolution](review-resolution.md)。这不声称新改文已被复核者重新审查。
2. 003采用原PNG六click无进展/恢复touch有效；107采用原suffix-prefix拼接与冗余窗，不立merge根因；106的Completed是排序设置，不证group/第三项可达；036条件fuzzy与物理path分开；076跨日scope歧义保留；060无唯一合法测量路线；098不立初始255/drag回退因果；115哪份持久分项过未知。
3. **最终引用已锁定，无外部等待**：owner纠偏收据`verification.moduleAlignmentCorrection`为accepted_all_13、remainingDisagreements=[]。JSON SHA256 `9531afd8194cb4d027a139af7439de726616b78574a0f35649c2b2ae3ef934cd`；MD SHA256 `a728d25151ac7447f68245cf9a899e46f2ed20a283cdcc2bd3fc8efd5af33011`。review原读取hash/历史override另存收据，不冒充对最终版重新做13项审计。
4. 不授权fix或新实验；语义/协议/资格变化须独立决定，不覆盖正式20failed/VLC0.5，也不提供改判成绩。
