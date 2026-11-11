# 本轮失败分析：模块与责任边界

Campaign：`amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`。跨项目调查与两阶段独立复核整合完成；20案、44eval/37owner来源提案按既有7组去重。MA01–MA13全部接受/落实，最终owner纠偏版本已锁，无剩余报告分歧或外部等待。历史disagree/different-scope保留溯源，不吞并为新产品bug或消除unknown。

## 已验证的公共边界

| 边界 | 具体模块／文件／symbol | 实际证据与结论 | 不能推出的结论 |
|---|---|---|---|
| Agent 可见输入 | `FSQ_AndroidWorld_eval/src/fsq_androidworld_eval/runner.py:PROMPT_TEMPLATE` 136–155、`_agent_prompt` 276–295 | 20案第一条原始 user prompt 均含 exact goal、初始化参考时钟和非空 string 输出契约 | 时钟可见不证明 Agent 正确使用；prompt 不是数据库快照 |
| 初始化 | `runner.py` 640–670；`task_time.py:task_time_context` 21–28 | 冻结 params 在初始化前保存；goal 和参考时钟在 `initialize_task` 后读取，环境 `freeze_datetime=True` | 原始 params 不等于初始化后完整 proto/DB/实际 UI 集合，不能用事后猜测代替历史状态 |
| 首个业务提交 | `omp_supervisor.py:run_omp` 211–234、278–295 | 全20案实际 receipt 均指向首个 assistant stop；原文与 business-submission archive 完全相同，receipt 均在截止内 | 业务值正确性不由合法 JSON 或正常停止证明 |
| 提交解析 | `submission.py:parse_submission` 45–93；`runner.py` 771–788 | 全20案 parser 输出与归档精确相同，都是合法非空 string；仅 `.strip()`，未把 number/object 转成 string | 不能把本轮失败归于旧版缺 final、cleanup 覆盖答案或数值被外层强转 |
| IR 答案比对 | `runner.py` 787–792；`information_retrieval.py:InformationRetrieval.is_successful` 109–119 | 合法 string 的 `answer` 赋给 `env.interaction_cache`，再进入官方 `proto_utils.check_agent_answer` | 每案 predicate 是否拒绝仍需对应模板、完整集合、单位和边界证据 |
| 原子动作计费 | `action_budget.py:ActionGate.submit/advance_step` 90–157、`ActionPermit.complete` 45–53 | 获准操作先计费，即使上游失败；拒绝不算执行。20案共352个获准动作，1个预算拒绝请求 | `python_exec` 次数不是 UI steps；9个 `step_budget` 不能直接作为根因；不证明所有合法路线均可行或不可行 |
| Python 执行响应 | 原 result `agent.normalized.toolCalls[].amkernel`，原 `tool_execution_end` | 391个结构化执行响应：328 completed、63 failed，均报告 kernelState=alive；另20次只是工具路由文档 read | alive 不是语义正确性；failed 不是 AMKernel bug；异常类别和具体失败调用需逐案分析 |
| 清理与 evaluator | `runner.py` 716–737、790–796、821–838 | Agent finish/quit 与 session 缺席核验在 evaluator 前；task teardown、DB clear 与 environment close 在 evaluator 后。所有20案顺序一致 | 成功 quit 不证明业务状态未变；缺少 post-quit/pre-evaluator 持久快照时，必须保留该因果缺口 |
| evaluator 留证 | `runner.py` 790–796 | 当前 result 保留 scalar officialReward 和耗时，没有各 predicate/subscore 的统一收据 | reward=0 不识别唯一失败分支；VLC reward=0.5不能当全零，也不能仅凭总分确定哪一份持久播放列表通过 |

公共离线代码、实际输出、20案原文→parsedValue→answer、receipt行号及限制见 [shared-offline-checks.json](shared-offline-checks.json)。391统计含业务和清理执行；target-only 初始查询还包含20次工具文档 read，已在收据明确剔除为非执行，不把 unrecorded 当超时或无响应。

## 源码身份与可比性

- 当前19个 Harness 身份输入的规范摘要与冻结 manifest 完全一致：`861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`。算法与实际输出在公共收据 `sourceIdentity`。
- 独立review的31-file历史revision blob比对全部一致：`review.json#/independentOfflineQueries/sourceIdentity`提供完整hash和复现代码，对应revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`。本修订不重跑；剩余缺口仅为历史运行import路径/安装task包目录字节未归档，不再声称所引revision内容未核。31项不涵盖历史Node/helper依赖字节。
- MA01补充：模块owner另有17个current retained installed文件及13个发布Runtime模块的一致收据，17项digest与旧Git31核验吻合。31与17范围不同不相加；执行者归属owner/原review，不是本批重跑，也不是完整正式时刻import/Node-helper安装快照。
- 本轮是 r15／OMP18.18.3 current-stack，历史 r12 continuation v2／OMP18.12.6 不同。即使任务种子、参数、次数、预算沿用，也不能作纯 AMKernel／Skills 单变量归因。
- 原始116项正式成绩、资格、116预演、12校准彼此独立；分析不修改 score、增加重试、扩大预算或放宽 oracle。

## 留证缺口对应的方案（不是本轮根因或已实施修复）

**目标模块**：`FSQ_AndroidWorld_eval/src/fsq_androidworld_eval/runner.py` evaluator 边界 790–796，及对应官方 task/oracle。现有 scalar 收据不足以区分多个失败 predicate；这是一项观测能力缺口，不等于已证实评分实现有错。

**最小方案，decision_needed**：在未来新身份的调查运行中，保存私有 evaluator 输入／predicate 分项及必要的前后持久状态签名，标注初始化后、业务提交后、quit后、evaluator前后各阶段；禁止把 expected answer／隐藏行集暴露给执行 Agent。应按任务限制最小化 DB、文件内容和媒体数据，保留原始值与转换值。

**备选与取舍**：仅保存 predicate booleans＋散列更省隐私和空间，但不能重建错值；任务专用、最小化的私有持久快照更有因果力，但涉及隐私、体积和采集扰动。不能用模型自述代替 DB/file 证明，也不应默认给全116项增加全库转储。

**不变量／风险**：不改当前 frozen oracle、prompt、动作预算或原始结果；诊断数据不进入 Agent context；采集不可写设备状态或改变计时；来源、时区、单位、时间戳必须自描述。

**可证伪验证**：用隔离、明确授权的合成状态检查新增收据是否能区分“保存前已错／quit后改变／oracle转换拒绝”，并核对采集前后状态和耗时不变量。若收据仍只有总分、泄漏答案或产生状态差异，该方案失败。本轮未实施或运行该验证。

## 一、任务／oracle契约：修复测量定义，不给模型喂答案

| 编号／案例 | 已证问题与因果置信 | 责任project／具体模块 | 独立fix方案、决策与证伪 |
|---|---|---|---|
| O1／001 | generator/goal给完整`.m4a`名，oracle再追加`.m4a`。源码契约问题confirmed；物理文件路径未归档，失分因果probable | 测评项目内AndroidWorld：`android_world/android_world/task_evals/single/audio_recorder.py:AudioRecorderRecordAudioWithFileName` 90–123、154–157 | **decision_needed**：统一完整文件名或stem语义，推荐完整名原样检查；不能同时改模型去猜双扩展。新版本比较完整名/无后缀/带后缀输入与实际文件。若历史双扩展文件本就存在或冻结源码不同，该问题不足以解释本次0 |
| O2／014 | initialize显示行note追加`. Reimbursable.`，validator比较未追加的reference；两条实际可见保存备注均被当前pure comparator拒绝。源码分裂confirmed；最终DB/类别缺失，失分因果probable | `single/expense.py:ExpenseAddMultipleFromMarkor.initialize_task` 343–356；`_ExpenseAddMultiple.validate_addition_integrity` 264–285；`common_validators/sqlite_validators.py:AddMultipleRows.is_successful` 304–310 | **decision_needed**：明确标记是可保存备注还是仅筛选元数据；自然转录方案须让显示值/参考一致，另一方案须在goal明示剥离规则。不放宽0.9阈值。若原DB还缺行/错类别/错金额，备注契约修复不能单独使该attempt通过 |
| O3／076 | 模板期望事件恰在17:20却问after17:20；oracle仅取绑定title而不查strict-after/minimum。confirmed契约不一致；Agent次日答案正确性unknown | `information_retrieval/proto/tasks.textproto:SimpleCalendarFirstEventAfterStartTime` 858–893；`proto_utils.py:get_expected_answer/_get_field_values` 183–251；`calendar_utils.py`日期转换/排除 | **decision_needed**：明确at-or-after，或拆开查询阈值与严格更晚的事件并定义日期、并列最早及排除集。不能静默改旧reward；新的task身份和资格需要另行授权 |

上表后两行短路径均相对`android_world/android_world/task_evals/`；全部完整source/依赖/精确谓词在[cases.json](cases.json)各案`oracle`，实际pure代码及输出在对应`domain-*-queries.md`。本调查没有重新评分或计算“修正后成绩”。

## 二、额外源码问题／可比性风险：不是本轮失分根因的替身

| 案例关联 | 具体模块／事实 | 裁定 | 独立方案与验证边界 |
|---|---|---|---|
| 030 | `android_world/android_world/utils/file_utils.py:get_file_list_with_metadata` 495–549使用`ls ... -ll -au`，`FileWithMetadata` 60–74却称ctime；`markor.py:MarkorDeleteNewestNote` 317–372按该字段排序并要求survivor时间不变 | 检查源码的ctime/atime接口不一致confirmed；历史Toybox字节、atime挂载策略和前后metadata均缺，episode因果unknown | **decision_needed**：先定creation/change/modification/访问时间中的哪一种才是“newest”；选择明确字段，归档原始metadata与tie policy。不能用Agent观察到的列表顺序替代oracle时间排序，不能事后断言一定删错 |
| 060 | `single/retro_music.py:RetroPlaylistDuration.initialize_task` 260–284没有调用基类；基类`TaskEval.initialize_task` 142–157负责cache/时钟/apps/seed，父`RetroCreatePlaylist.initialize_task` 147–160另含storage清理 | 当前源码漏初始化链confirmed；影响实际MP3随机时长/存储隔离的具体extent unknown。68:25的可见聚合行为失败与该风险分列 | **decision_needed**：未来版本恢复预期初始化/清理与可复现seed边界，保存最小实际歌曲metadata；不能用params的15个名字捏造当时14首/完整时长，不把遗漏super当本次所有失分原因 |
| 106（latent，非本次原因） | `information_retrieval/proto_utils.py:check_agent_answer` 147–180先比长度再对每个提交项做`any`模糊匹配，未消费expected occurrence | 实际synthetic pure probe证明重复同一个正确项可满足多个expected槽，是潜在false-positive代码缺陷；**本次2对3在长度处拒绝，与此缺陷无因果关系** | **decision_needed**：保留原fuzzy语义但要求一对一／多重集合匹配；若fuzzy关系交叉应验证存在合法匹配而非简单贪心。用缺项、重复项、交换顺序、同名多occurrence的纯输入证伪；不改本次reward |
| 033／036 | `single/markor.py:MarkorMergeNotes.template/is_successful` 510–650对exact extensionless名和附加LF有隐含要求；`MarkorTranscribeVideo`＋`file_validators.CreateFile`只接受Markor notebook输出目录 | 033的实际文件名/形状差异已见，wording存在解释空间但不是已证坏oracle；036 source-folder与output-folder混淆与隐藏目录scope风险并存 | 明确future goal的完整文件名、独立extension、附加分隔符和输出目录。禁止为了让旧attempt通过而自动接受任意目录/改成宽松标题匹配 |

## 三、跨项目去重修复优先级与责任

<a id="cross-project-priority"></a>

沿用模块owner既有7组，不建立新修复体系。44项eval与37项owner是两组来源提案，**不相加为81项**；每项eval保留一个primaryGroup，equivalent与partial/different-scope另列。现有Skill已加载多数不变量，行为违背不等于缺规则，更不等于Runtime实现bug。优先级为未来授权工作的先后，不是本批实施授权。

最终模块纠偏版已按总管通知锁定，13项全部接受；旧review snapshot及override保留历史溯源，锁定hash见[review-resolution.md](review-resolution.md)。以下所有验收/替代路线是尚未执行的反事实实验，无成功或分数收益保证。

### E-TASK-CONTRACT — P0 先定测量语义；非无冲突行为改进的等待条件

**受影响case／负责人**：001, 004, 014, 030, 033, 036, 060, 076, 098, 106, 115；FSQ_AndroidWorld_eval / AndroidWorld task owner；Harness证据owner协作。

**根因置信**：001/014/076源码契约confirmed；030 metadata、060初始化链和106 matcher是另立源码问题，episode因果unknown/非causal；033/036措辞及路径scope、098精确状态为风险/unknown，不标新坏oracle。 episode各案独立为 001=probable；004=probable；014=probable；030=unknown；033=probable；036=probable；060=unknown；076=probable；098=unknown；106=confirmed；115=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `FSQ_AndroidWorld_eval` / AndroidWorld task/oracle / `android_world/android_world/task_evals/single/audio_recorder.py` / **AudioRecorderRecordAudioWithFileName.generate_random_params / is_successful**
- `FSQ_AndroidWorld_eval` / AndroidWorld task/oracle / `android_world/android_world/task_evals/single/expense.py` / **ExpenseAddMultipleFromMarkor.initialize_task / _ExpenseAddMultiple.validate_addition_integrity**
- `FSQ_AndroidWorld_eval` / AndroidWorld IR / `android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto` / **SimpleCalendarFirstEventAfterStartTime / TasksCompletedTasksForDate**
- `FSQ_AndroidWorld_eval` / AndroidWorld files / `android_world/android_world/task_evals/single/markor.py` / **MarkorMergeNotes.template / MarkorTranscribeVideo.template / MarkorDeleteNewestNote**
- `FSQ_AndroidWorld_eval` / AndroidWorld metadata / `android_world/android_world/utils/file_utils.py` / **get_file_list_with_metadata / FileWithMetadata**
- `FSQ_AndroidWorld_eval` / AndroidWorld media / `android_world/android_world/task_evals/single/retro_music.py` / **RetroPlaylistDuration.initialize_task / is_successful / _get_playlist_info_query**
- `FSQ_AndroidWorld_eval` / AndroidWorld IR matcher / `android_world/android_world/task_evals/information_retrieval/proto_utils.py` / **check_agent_answer / get_expected_answer**
- `FSQ_AndroidWorld_eval` / private evaluator diagnostics / `src/fsq_androidworld_eval/runner.py` / **run (evaluator boundary790–796)**

**最小fix**：001统一stem/完整名；014统一显示note与参考/筛选元数据；076明确>=/>、跨日范围与tie。033/036/106另澄清可见合同，不改旧oracle；030先定newest时间字段，060先定初始化/隔离继承契约，latent matcher一对一另列。私有分项/状态签名是未来诊断，不是本轮修复成功。

**替代／取舍**：若意图已确定可仅澄清goal而非放宽判据；booleans+hash替代完整私有快照；004 future wording/step-unit仅独立可比性决策。

**风险**：改变实例/协议需新身份与授权资格；诊断可能扰动计时/隐私，expected/隐藏行集不得进Agent上下文。不得用scalar0或0.5改判。

**验收（未实施／未运行）**：未来授权neutral generator→display→literal output→validator边界可反证；错误值仍拒绝。私有收据能区分保存前、quit后与predicate拒绝且不泄漏、不写状态。未实施/未运行。

**语义决策**：是：业务语义、初始化/时间字段、matcher语义、收据隐私与采集边界；本轮不决策改分。

**来源提案（独立命名空间）**：eval 001-F00, 004-F01, 014-F00, 014-F01, 030-F02, 033-F01, 036-F01, 060-F02, 076-F00, 098-F02, 115-F02；owner 001-F2, 014-F1, 033-F2, 076-F1。

### G-ACCEPT — P1 独立验收与失败后修复

**受影响case／负责人**：001, 004, 023, 024, 030, 033, 036, 049, 098；执行Agent行为；amkernel shared/Android Skill owner仅条件示例；FSQ提供可见目标scope。

**根因置信**：动作/验收缺口confirmed；具体持久失分多数probable，030与098实际状态/精确失分机制unknown。036 fuzzy仅条件字符串关系，非evaluator pass。 episode各案独立为 001=probable；004=probable；023=probable；024=probable；030=unknown；033=probable；036=probable；049=probable；098=unknown。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Verify the requested outcome independently / For files and notes (181–211)**
- `amkernel` / Skill Android / `src/amkernel/skill/references/android-execution.md` / **Input, submit and verify / Input, submission and persistence are separate outcomes (183–219)**
- `amkernel` / Runtime prefix semantics reference, not fix target / `src/amkernel/runner.py` / **_compile_and_execute / _execute_cell (545–599)**

**最小fix**：先从独立goal确定完整name/ext/folder/content与app-level commit；失败cell后先读现状/重取句柄，保留已执行前缀，不整批重放。098只在独立观测到满足时stop；未获numeric/geometry证据就保留exact scalar unknown。

**替代／取舍**：既有规则已包含多数不变量，先检验执行遵循；必要时补中性边界例，不默认扩写Skill有效。若允许surface不足则如实未验证，不猜后缀/目录/255。

**风险**：强验收可能揭露不可完成而非提高成功率；整批重放会重复副作用；不能硬编码benchmark答案或普遍清空extension。

**验收（未实施／未运行）**：未来中性双字段文件名/保留源终止符/失败前缀/应用提交fixture，按独立目标读回；截图近满不能认证exact scalar。无未观测mutation的虚假成功。未执行。

**语义决策**：行为不变量无需改语义；Skill措辞仍需owner批准；隐藏目标scope和diagnostic需E-TASK先裁定。

**来源提案（独立命名空间）**：eval 001-F01, 004-F00, 030-F00, 033-F00, 036-F00, 036-F02, 049-F00, 049-F02, 098-F00, 098-F01；owner 001-F1, 004-F2, 030-F1, 033-F1, 036-F1, 049-F1, 098-F1, 098-F2。

### G-ROUTE — P1 获准控制效果/SDK/admission与动作路径

**受影响case／负责人**：003, 004, 023, 024, 030, 049, 052, 060, 085, 091, 106, 115；执行Agent；amkernel Android Skill；FSQ Harness仅协议可见性与冻结预算。

**根因置信**：003六elementclick无进展、恢复4touch有效与九budget闭包confirmed；底层dispatch、每案可行替代路线及预算内成功unknown。SDK/pointer契约confirmed，非Runtime实现bug。 episode各案独立为 003=probable；004=probable；023=probable；024=probable；030=unknown；049=probable；052=probable；060=unknown；085=probable；091=probable；106=confirmed；115=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill Android / `src/amkernel/skill/references/android-execution.md` / **Locate from current evidence / Navigate, scroll and handle system UI (87–119,165–181)**
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Batch predictable steps; checkpoint real progress / Bound operations by observable failure states (113–146,300–321)**
- `FSQ_AndroidWorld_eval` / Harness admission / `src/fsq_androidworld_eval/appium_proxy.py` / **_validate_actions / _validate_gesture / AppiumAuditProxy._authorize (271–319,853–908)**
- `FSQ_AndroidWorld_eval` / Harness budget / `src/fsq_androidworld_eval/action_budget.py` / **ActionGate.submit / advance_step**
- `Appium-Python-Client5.2.5 / Selenium4.52.0` / measured SDK source / `appium/webdriver/webelement.py; selenium/webdriver/common/actions/action_builder.py` / **WebElement.send_keys / ActionBuilder.__init__**

**最小fix**：保留in-cell批处理但每个依赖动作确认真实阶段；实际观测context row/菜单，单touch正确payload与存在的SDK方法；clear+send_keys算两次，获准500已扣费，admission拒绝不扣。区分outer isError/inner status，失败后读现状。085 helper先保留环境缺口，不启服务。

**替代／取舍**：兼容原生touch或已观测tap式修复皆为条件路线；不开放WEBVIEW/DOM、shell、多pointer/隐藏多交互，不加预算重试。115已读row menu，无Move up/down不排除所有修复；不得由clickable=false或swipe名称断定机制。

**风险**：盲重放可能重复已执行前缀；局部SDK失败耗时间但未必耗UI；闭包后caller可能不再调cell，免费观察必须排在可执行窗口内。

**验收（未实施／未运行）**：未来neutral fixture验证phase progress、触摸wire、clear/value分账、拒绝vs获准上游失败、partial-prefix读回；同原授权预算，不以固定sleep或值必须改变当ack。修复路径必须观测affordance且实际算全成本；未执行。

**语义决策**：可见性/示例可提案；step unit、授权面、计费或重试改变必须单独协议/可比性决策，不采纳为本轮fix。

**来源提案（独立命名空间）**：eval 003-F00, 003-F01, 023-F00, 023-F01, 024-F00, 024-F01, 030-F01, 049-F01, 052-F03, 085-F00, 085-F01, 115-F01；owner 003-F1, 003-F2, 004-F1, 023-F1, 024-F1, 085-F1, 091-F2, 115-F2。

### G-COVER — P1 occurrence/row-scope/真实集合

**受影响case／负责人**：052, 058, 060, 091, 106, 107；执行Agent；amkernel shared/Android Skill。

**根因置信**：052未Delete、058可见仅1首、106两项对三槽confirmed；真实DB/行ID、058具体clicked menu及106第三title可达性unknown。107不存在已证merge/global-dedup根因。 episode各案独立为 052=probable；058=probable；060=unknown；091=probable；106=confirmed；107=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Prove scope, membership and coverage / Remove duplicates only after content equivalence (212–245,263–299)**
- `amkernel` / Skill Android / `src/amkernel/skill/references/android-execution.md` / **Locate from current evidence / Navigate, scroll and handle system UI (108–118,165–181)**

**最小fix**：区分input multiset、生成下界、viewport和DB身份；observed最近真实行内唯一control；完整相关字段定义重复并保留一份，不按title/位置删。群体与完成状态只从真实业务surface建立；106排序配置不是任务group。107记录overlap与未变窗口冗余依据，不强制再拼重复窗口。

**替代／取舍**：可用可信总数/详情或有序遍历/重叠账本；不要求总是打开每行或宣称固定预算可全覆盖。106仅若实际group存在才考虑进入，不能泄漏hidden count/title。

**风险**：fingerprint不等DB ID；“32/31”和>=8不能证明UI全达；same-title与virtualization使错误删除风险高。

**验收（未实施／未运行）**：未来中性虚拟列表含同title不同内容、非相邻真重复、同窗重复与冗余未变窗口，保留occurrences且只删已证等价；sort settings不得被当group内容。未执行。

**语义决策**：不改业务语义；若要稳定身份/新接口或协议能力需独立决策，不能自动绕UI。

**来源提案（独立命名空间）**：eval 052-F00, 058-F00, 106-F00；owner 052-F1, 052-F2, 058-F1, 058-F3, 060-F2, 106-F1, 106-F2, 107-F2。

### G-ORDER-AGG — P1 有序构造/有界聚合及完整commit

**受影响case／负责人**：033, 058, 060, 115；执行Agent；amkernel shared Skill；FSQ oracle owner仅诊断/初始化风险。

**根因置信**：可见sequence/14首68:25/未commit观测confirmed；060最终DB分支unknown，115哪份持久Boolean过unknown；不宣称修复可在预算内完成。 episode各案独立为 033=probable；058=probable；060=unknown；115=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Prove scope, membership and coverage / Aggregate targets / ordered-content acceptance (212–262)**
- `FSQ_AndroidWorld_eval` / AndroidWorld media predicates / `android_world/android_world/task_evals/single/retro_music.py; android_world/android_world/task_evals/single/vlc.py` / **RetroPlaylistDuration.is_successful / _get_playlist_info_query; VlcCreateTwoPlaylists.is_successful**

**最小fix**：预先解析目标成员与顺序，按goal序插入、逐container读回；数值聚合先用实际合法单项证据，未建立单项路线时才考虑预算内可逆增量且读聚合。不先Select all猜时长；预留完整Remove-from-playlist确认/readback而非设备Delete。

**替代／取舍**：已观测的原生重排、remove/reappend或rebuild均只在保留对象与全成本满足时候选；没有唯一合法测量方式或普遍可行修复断言。060评分读playlist.db joined duration_ms，不直接由MediaStore假定。

**风险**：未知时长不能预测一定落区间或最少删除数；更正顺序可能破坏已正确container；115menu已打开但不证明所需修复语义/affordability。

**验收（未实施／未运行）**：未来中性有序容器独立校验membership/order/cardinality，未知贡献fixture不作落点保证；预算不足或affordance未证则保留partial而不伪称gate耗尽。未执行。

**语义决策**：行为不变量本身否；新测量接口/初始化链改动、分项收据与任何预算变更另行决策。

**来源提案（独立命名空间）**：eval 058-F01, 060-F00, 060-F01, 115-F00；owner 058-F2, 060-F1, 115-F1, 115-F3。

### G-TIME-ANSWER — P1 日期成员/单位后再reduce；076先澄清语义

**受影响case／负责人**：004, 076, 091, 106, 107；执行Agent；amkernel shared Skill；FSQ IR task owner负责契约。

**根因置信**：oracle bound-title/COUNT、单项误总数及2vs3长度事实按案confirmed；076跨日strict-first答案、091精确6502重建、107formatter/各噪声日期probable/unknown，不吞并为完整失分因果。 episode各案独立为 004=probable；076=probable；091=probable；106=confirmed；107=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Apply date and priority predicates exactly / Aggregate targets / Report the business answer and control status separately (238–256,332–351)**
- `FSQ_AndroidWorld_eval` / AndroidWorld IR / `android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto; android_world/android_world/task_evals/information_retrieval/proto_utils.py` / **SimpleCalendarFirstEventAfterStartTime / SportsTrackerTotalDistanceForCategoryOverInterval / TasksCompletedTasksForDate / TasksDueNextWeek; get_expected_answer / check_agent_answer**

**最小fix**：先明确参考时钟/时区、绝对日期、范围边界、类别/单位和输出schema，再证明成员集再count/sum。076保留timestamp阈值与day-only两读歧义，不能强制定日或迎合hidden title；107保留原suffix-prefix拼接，纠正label predicate而非捏造merge错误。

**替代／取舍**：已应用的可信date filter或逐行绝对日期皆可；缺证时分列unknown，不从params距离/title或weekday标签填生成状态。

**风险**：绝对标签formatter未钉，单项换算精确仍可能不是total；合法string envelope不是正确业务答案。

**验收（未实施／未运行）**：未来中性>/>=、跨日/tie、Monday周、已知绝对日期隐藏行、总数/集合/单位容差fixture；未证范围保留歧义，未知值不造。未执行。

**语义决策**：076以及due/completion wording是；常规成员/单位/报告遵循否；不得默改old oracle。

**来源提案（独立命名空间）**：eval 091-F00, 107-F00；owner 076-F2, 091-F1, 107-F1。

### G-BOUNDARY — P2 结果边界/诊断效率，不作10案失分收益承诺

**受影响case／负责人**：003, 014, 024, 052, 058, 085, 091, 098, 106, 115；执行Agent JSON-native返回；amkernel Skill；Runtime owner仅契约/独立诊断问题。

**根因置信**：17次有界repr/10案confirmed且output.truncated=false与result.truncated=true并存；各案未恢复字段导致业务失分未统一证明。 episode各案独立为 003=probable；014=probable；024=probable；052=probable；058=probable；085=probable；091=probable；098=unknown；106=confirmed；115=probable。不得将局部confirmed聚合成整案已证。

**具体project/module/file/symbol或Skill section**：
- `amkernel` / Skill shared / `src/amkernel/skill/references/amkernel-appium.md` / **Keep evidence bounded (103–110); JSON-native result examples**
- `amkernel` / Runtime serialization / `src/amkernel/runner.py` / **_normalize_result / _bounded_repr (602–665)**
- `amkernel` / Runtime strict JSON / `src/amkernel/protocol.py` / **_json_encoded_size (642–710)**
- `amkernel` / MCP result contract / `src/amkernel/server.py` / **_structured_result / _map_tool_result (288–351,515–535)**
- `amkernel` / noncausal exception diagnostics / `src/amkernel/runner.py` / **_WEBDRIVER_NAMES / _webdriver_shape / _webdriver_message (140–152,771–836)**

**最小fix**：调用者返回有界dict/list/scalars并读result.kind/truncated；恢复所需字段后再决策。outer isError=false只表示工具封装成功，业务判inner status/kernelState/error。保留strict JSON为当前契约；缺少InvalidElementStateException安全msg是独立已知诊断限制，原391无该异常。

**替代／取舍**：Runtime安全tuple支持保留为eval052-F02未采纳主路线的条件契约选择，需深度/循环/资源安全决策；不任意repr/遍历用户对象，不取消限制。

**风险**：增加文字/JSON体积未证明模型更遵循；自动coercion改变契约与资源行为。不能把unpublished诊断修正称本轮被测改进。

**验收（未实施／未运行）**：未来授权中性嵌套tuple/list对照与consumer inner-failed处理；若扩支持必须验证cycle/depth/bytes和安全边界；真实Agent先恢复关键字段再动作才有行为证据。本轮仅引用owner既有pure probe，未再执行。

**语义决策**：Skill例子owner审批；Runtime类型支持或outer映射改变是公开契约决策，不以接近症状定bug。

**来源提案（独立命名空间）**：eval 052-F01, 052-F02；owner 052-F4, 085-F2。


## 四、跨模块作用：Runtime／Skill／Harness不能混判

### R1 strict JSON与有界repr：结构损失confirmed，不是10案Runtime根因

采用发布源码映射 `amkernel/src/amkernel/runner.py:_normalize_result/_bounded_repr` (602–665)、`src/amkernel/protocol.py:_json_encoded_size` (642–710)。17次结果覆盖003/014/024/052/058/085/091/098/106/115；每次`output.truncated=false`但`result.kind=repr/result.truncated=true`。这是整个非JSON结果降为有界summary，不是stdout/stderr/传输截断。后续JSON-native恢复情况决定是否影响具体决策，不能推出17次crash或10案失分因果。

| case | executionCount | 原raw起止行 |
|---|---|---|
| 003 | 4 | 1028-1029 |
| 014 | 2 | 438-439 |
| 014 | 7 | 1392-1393 |
| 024 | 5 | 1228-1229 |
| 024 | 12 | 3024-3025 |
| 052 | 8 | 2577-2578 |
| 052 | 12 | 3744-3745 |
| 052 | 15 | 4878-4879 |
| 058 | 3 | 910-911 |
| 085 | 7 | 1687-1688 |
| 091 | 2 | 481-482 |
| 098 | 4 | 1088-1090 |
| 098 | 5 | 1343-1345 |
| 098 | 7 | 2138-2140 |
| 106 | 9 | 2686-2687 |
| 106 | 14 | 3721-3722 |
| 115 | 8 | 1956-1957 |

完整原raw路径与summary见`cases.json#/moduleAlignment/reprOccurrences`；MA02是实际独立复核，本批不再解析原raw或执行owner pure probe。caller JSON-native投影及例子是G-BOUNDARY主路线；eval052-F02的bounded tuple支持只是非等价的独立安全/公开契约选择，未批准实施。

### R1a 外层成功／内层失败、failed前缀与SDK不能混层

- `amkernel/src/amkernel/server.py:_structured_result/_map_tool_result` (288–351,515–535)：63个inner failed配outer`isError=false`是现有结构化结果契约；consumer应判`status/kernelState/error`，不是MCP吞异常。
- `amkernel/src/amkernel/runner.py:_compile_and_execute/_execute_cell` (545–599)：已执行失败前缀/namespace不回滚。owner既有pure receipt保留saved=41、下一cell42，仅证明Python持久语义；外部UI效果逐案看原轨迹，不据此保证重放安全。
- Agent解释器Appium-Python-Client5.2.5、Selenium4.52.0，与Harness5.3.1不是版本冲突；default ActionBuilder的mouse与不存在`WebDriver.start_activity`/`WebElement.set_value`属于caller/SDK兼容问题。单touch/native-only拒绝是Harness admission，不是Runtime注入/功能缺失。
- 9个真实`step_budget`为003/023/030/036/049/052/060/085/106；其余11个`agent_finished`。115 gate最终closed=true、reason=agent_finished、46/48非耗尽。read/find/source免费不等于caller闭包后还会调新cell；最后readback需放可执行窗口。
- 本轮20案读取主Skill/Android/shared/schema不等于遵循。缺例子可提案，不能说未加载或缺规则已证导致失分。
- `runner.py:_WEBDRIVER_NAMES/_webdriver_shape/_webdriver_message`的InvalidElementStateException安全msg缺口是独立已知诊断限制，391原响应没有该异常；不算本轮失败因果或已测未发布修正。


### R2 原生-only／单交互策略拒绝：测评协议边界，不是传输故障

`src/fsq_androidworld_eval/appium_proxy.py:_authorize` 878–880拒绝WEBVIEW；`_validate_actions`限制单touch与gesture形状；UiScrollable隐藏多操作、percent10等也在admission前被拒绝。关联003/004/030/060/106/115。原request被明确拒绝与HTTP200后无UI进展、执行Python异常、step gate拒绝必须分开统计。

**方案，decision_needed**：如需改善交互契约可见性，明确native-only优先于通用Skill的context例子、允许手势形状和admission计费；不在本轮开放DOM、shell或复合操作。改变策略/step unit属于新协议可比性决策，必须独立身份，不能追溯给旧attempt追加步骤。当前调查不证明所有固定预算下均有可行路线或均不可行。

### R3 清理、持久化与分项缺口

公共顺序见开头：quit后评分、teardown后于评分。IR期望集合驻留task proto且runner重新赋合法answer，不应泛称quit删掉IR答案；状态类task则缺post-quit/pre-evaluator持久快照，不能从UI或successful quit断言磁盘与DB。未来收据方案见本文件留证缺口章节；它是分析能力改进，不是对本轮20案的统一根因修复。

## 整合状态与责任交接

20案/44fix/37来源方案实际对齐、两阶段复核及13裁定均已整合；模块最终纠偏receipt accepted_all_13、remainingDisagreements=[]，最终JSON/MD hash已锁。原review只覆盖其历史读取版本，本批只绑定最终收据/identity，不重复13项审计。无外部等待；未知持久状态和未来语义决策仍保留，非报告争议。

## 独立review修订：44项fix精确责任登记

<a id="review-fix-location-register"></a>

R03原指出26项需要更精确落点；本修订为全部44项加`fixId`、`proposalType`及`location.primary/related`。旧`target`保留叙述意图，实施落点以`location`为准。行为建议直接绑定不可变原Agent cell与已加载Skill确切heading；不把行为policy包装成产品缺陷。环境历史file/hash未知时保留未知，主落点为实际caller或future diagnostic边界。

**来源分类**保留：44eval中27行为、1条件产品、5诊断、11协议决策；所有`readyForImplementation=false`。Runtime仓库symbol已由正式owner报告与MA02定位；52-F02类型扩展不是已证Runtimebug修复，也不等同owner052-F4文档/caller方案。

| fixId／类型 | project／module | 精确file／symbol或Skill section／原cell | 责任与证据边界 |
|---|---|---|---|
| 001-F00 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/audio_recorder.py` — `AudioRecorderRecordAudioWithFileName.is_successful` | 完整related落点及限制：`cases.json#/cases/0/fixes/0/location`；非实施授权 |
| 001-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/001-AudioRecorderRecordAudioWithFileName/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 9,10`；cell9 L3074-3075, cell10 L3439-3440 | 完整related落点及限制：`cases.json#/cases/0/fixes/1/location`；非实施授权 |
| 003-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/003-BrowserMaze/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 20,21,22`；cell20 L3699-3701, cell21 L3777-3779, cell22 L3961-3962 | 完整related落点及限制：`cases.json#/cases/1/fixes/0/location`；非实施授权 |
| 003-F01 / protocol_decision | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/runner.py` — `PROMPT_TEMPLATE` | 完整related落点及限制：`cases.json#/cases/1/fixes/1/location`；非实施授权 |
| 004-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/004-BrowserMultiply/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 17,18,19,21`；cell17 L4164-4165, cell18 L4538-4539, cell19 L4778-4779, cell21 L5186-5188 | 完整related落点及限制：`cases.json#/cases/2/fixes/0/location`；非实施授权 |
| 004-F01 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/browser.py` — `BrowserMultiply.goal` | 完整related落点及限制：`cases.json#/cases/2/fixes/1/location`；非实施授权 |
| 014-F00 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/expense.py` — `ExpenseAddMultipleFromMarkor.initialize_task` | 完整related落点及限制：`cases.json#/cases/3/fixes/0/location`；非实施授权 |
| 014-F01 / diagnostic_proposal | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/runner.py` — `run (evaluator stage)` | 完整related落点及限制：`cases.json#/cases/3/fixes/1/location`；非实施授权 |
| 023-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/023-MarkorAddNoteHeader/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 13,14,15,16,17,18`；cell13 L2602-2603, cell14 L2848-2849, cell15 L2972-2973, cell16 L3183-3184, cell17 L3310-3311, cell18 L3512-3515 | 完整related落点及限制：`cases.json#/cases/4/fixes/0/location`；非实施授权 |
| 023-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/023-MarkorAddNoteHeader/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 10,13,14,15,16`；cell10 L1886-1887, cell13 L2602-2603, cell14 L2848-2849, cell15 L2972-2973, cell16 L3183-3184 | 完整related落点及限制：`cases.json#/cases/4/fixes/1/location`；非实施授权 |
| 024-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/024-MarkorChangeNoteContent/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 12,13,14,15,16`；cell12 L3024-3025, cell13 L3096-3097, cell14 L3321-3322, cell15 L3662-3663, cell16 L3893-3894 | 完整related落点及限制：`cases.json#/cases/5/fixes/0/location`；非实施授权 |
| 024-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/024-MarkorChangeNoteContent/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 16`；cell16 L3893-3894 | 完整related落点及限制：`cases.json#/cases/5/fixes/1/location`；非实施授权 |
| 030-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/030-MarkorDeleteNewestNote/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 13,14,15,16`；cell13 L3023-3024, cell14 L3249-3250, cell15 L3418-3419, cell16 L3553-3554 | 完整related落点及限制：`cases.json#/cases/6/fixes/0/location`；非实施授权 |
| 030-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/030-MarkorDeleteNewestNote/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 14,15`；cell14 L3249-3250, cell15 L3418-3419 | 完整related落点及限制：`cases.json#/cases/6/fixes/1/location`；非实施授权 |
| 030-F02 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/utils/file_utils.py` — `get_file_list_with_metadata` | 完整related落点及限制：`cases.json#/cases/6/fixes/2/location`；非实施授权 |
| 033-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/033-MarkorMergeNotes/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 8,10`；cell8 L1776-1777, cell10 L2501-2502 | 完整related落点及限制：`cases.json#/cases/7/fixes/0/location`；非实施授权 |
| 033-F01 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/markor.py` — `MarkorMergeNotes.template / generate_random_params / is_successful` | 完整related落点及限制：`cases.json#/cases/7/fixes/1/location`；非实施授权 |
| 036-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/036-MarkorTranscribeVideo/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 14,21,22,23,24`；cell14 L4574-4575, cell21 L6307-6308, cell22 L6509-6510, cell23 L6873-6874, cell24 L7301-7304 | 完整related落点及限制：`cases.json#/cases/8/fixes/0/location`；非实施授权 |
| 036-F01 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/markor.py` — `MarkorTranscribeVideo.template` | 完整related落点及限制：`cases.json#/cases/8/fixes/1/location`；非实施授权 |
| 036-F02 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/036-MarkorTranscribeVideo/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 8,9,10,11,12,21,22,23,24`；cell8 L2388-2390, cell9 L2636-2637, cell10 L2931-2934, cell11 L3397-3400, cell12 L3863-3865, cell21 L6307-6308, cell22 L6509-6510, cell23 L6873-6874, cell24 L7301-7304 | 完整related落点及限制：`cases.json#/cases/8/fixes/2/location`；非实施授权 |
| 049-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/049-RecipeAddSingleRecipe/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 6,9,12,13,14`；cell6 L1683-1684, cell9 L2319-2320, cell12 L3201-3202, cell13 L3415-3416, cell14 L3653-3654 | 完整related落点及限制：`cases.json#/cases/9/fixes/0/location`；非实施授权 |
| 049-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/049-RecipeAddSingleRecipe/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 11,12,13`；cell11 L2918-2919, cell12 L3201-3202, cell13 L3415-3416 | 完整related落点及限制：`cases.json#/cases/9/fixes/1/location`；非实施授权 |
| 049-F02 / diagnostic_proposal | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/049-RecipeAddSingleRecipe/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 9,10,12,14`；cell9 L2319-2320, cell10 L2563-2564, cell12 L3201-3202, cell14 L3653-3654 | 完整related落点及限制：`cases.json#/cases/9/fixes/2/location`；非实施授权 |
| 052-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24`；cell9 L2898-2899, cell10 L3146-3147, cell11 L3351-3352, cell12 L3744-3745, cell13 L3823-3824, cell14 L3908-3909, cell15 L4878-4879, cell16 L5062-5063, cell17 L5277-5278, cell18 L5437-5438, cell19 L5804-5805, cell20 L6276-6277, cell21 L6410-6411, cell22 L6678-6679, cell23 L6960-6961, cell24 L7316-7319 | 完整related落点及限制：`cases.json#/cases/10/fixes/0/location`；非实施授权 |
| 052-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 8,12,15`；cell8 L2577-2578, cell12 L3744-3745, cell15 L4878-4879 | 完整related落点及限制：`cases.json#/cases/10/fixes/1/location`；非实施授权 |
| 052-F02 / proposed_product_change | amkernel (published 0.1.4 wheel) / result serialization | `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/amkernel-0.1.4-py3-none-any.whl:amkernel/runner.py` — `_normalize_result / _bounded_repr` | 完整related落点及限制：`cases.json#/cases/10/fixes/2/location`；非实施授权 |
| 052-F03 / protocol_decision | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/stepped_agent.py` — `AppiumSteppedAgent.step` | 完整related落点及限制：`cases.json#/cases/10/fixes/3/location`；非实施授权 |
| 058-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 16,17,18,19,20`；cell16 L4284-4285, cell17 L4461-4462, cell18 L4734-4735, cell19 L5021-5022, cell20 L5299-5300 | 完整related落点及限制：`cases.json#/cases/11/fixes/0/location`；非实施授权 |
| 058-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 16,17,18,19,20,21,22,23,24`；cell16 L4284-4285, cell17 L4461-4462, cell18 L4734-4735, cell19 L5021-5022, cell20 L5299-5300, cell21 L5653-5654, cell22 L5987-5988, cell23 L6249-6250, cell24 L6590-6591 | 完整related落点及限制：`cases.json#/cases/11/fixes/1/location`；非实施授权 |
| 060-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/060-RetroPlaylistDuration/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 18,22,25`；cell18 L5213-5214, cell22 L6659-6660, cell25 L7669-7670 | 完整related落点及限制：`cases.json#/cases/12/fixes/0/location`；非实施授权 |
| 060-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/060-RetroPlaylistDuration/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 25,26,27,28,29,30`；cell25 L7669-7670, cell26 L8559-8560, cell27 L8890-8891, cell28 L9096-9097, cell29 L9578-9579, cell30 L9791-9794 | 完整related落点及限制：`cases.json#/cases/12/fixes/1/location`；非实施授权 |
| 060-F02 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/single/retro_music.py` — `RetroPlaylistDuration.initialize_task` | 完整related落点及限制：`cases.json#/cases/12/fixes/2/location`；非实施授权 |
| 076-F00 / protocol_decision | FSQ_AndroidWorld_eval / vendored AndroidWorld task/oracle | `android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto` — `tasks[name=SimpleCalendarFirstEventAfterStartTime]` | 完整related落点及限制：`cases.json#/cases/13/fixes/0/location`；非实施授权 |
| 085-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18`；cell3 L731-732, cell4 L1022-1023, cell5 L1166-1167, cell6 L1514-1515, cell7 L1687-1688, cell8 L1786-1787, cell9 L1941-1942, cell10 L2048-2049, cell11 L2338-2339, cell12 L2662-2663, cell13 L2982-2983, cell14 L3226-3227, cell15 L3428-3429, cell16 L3606-3607, cell17 L3800-3801, cell18 L3899-3900 | 完整related落点及限制：`cases.json#/cases/14/fixes/0/location`；非实施授权 |
| 085-F01 / diagnostic_proposal | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 12`；cell12 L2662-2663 | 完整related落点及限制：`cases.json#/cases/14/fixes/1/location`；非实施授权 |
| 091-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 20,21,22`；cell20 L3300-3301, cell21 L3431-3432, cell22 L3545-3546 | 完整related落点及限制：`cases.json#/cases/15/fixes/0/location`；非实施授权 |
| 098-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 3,6`；cell3 L940-941, cell6 L1644-1645 | 完整related落点及限制：`cases.json#/cases/16/fixes/0/location`；非实施授权 |
| 098-F01 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 7`；cell7 L2138-2140 | 完整related落点及限制：`cases.json#/cases/16/fixes/1/location`；非实施授权 |
| 098-F02 / diagnostic_proposal | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/runner.py` — `run (evaluator stage)` | 完整related落点及限制：`cases.json#/cases/16/fixes/2/location`；非实施授权 |
| 106-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/106-TasksCompletedTasksForDate/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 6,9,11,12,13,14,15,16,17,18`；cell6 L1744-1745, cell9 L2686-2687, cell11 L3129-3130, cell12 L3433-3434, cell13 L3595-3596, cell14 L3721-3722, cell15 L3916-3917, cell16 L4299-4300, cell17 L4781-4782, cell18 L5112-5115 | 完整related落点及限制：`cases.json#/cases/17/fixes/0/location`；非实施授权 |
| 107-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/107-TasksDueNextWeek/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 14`；cell14 L4251-4252 | 完整related落点及限制：`cases.json#/cases/18/fixes/0/location`；非实施授权 |
| 115-F00 / behavioral_policy | FSQ_AndroidWorld_eval (archived evaluated Agent) / Agent-generated Appium/Python execution policy; not a product implementation | `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/115-VlcCreateTwoPlaylists/attempt-1/raw-private/agent-events.jsonl` — `python_exec cells 13,14,15,27`；cell13 L3262-3263, cell14 L3543-3544, cell15 L3842-3843, cell27 L7007-7008 | 完整related落点及限制：`cases.json#/cases/19/fixes/0/location`；非实施授权 |
| 115-F01 / protocol_decision | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/appium_proxy.py` — `_validate_actions` | 完整related落点及限制：`cases.json#/cases/19/fixes/1/location`；非实施授权 |
| 115-F02 / diagnostic_proposal | FSQ_AndroidWorld_eval / Harness | `src/fsq_androidworld_eval/runner.py` — `run (evaluator stage)` | 完整related落点及限制：`cases.json#/cases/19/fixes/2/location`；非实施授权 |

### R04 / R05：置信与依赖不得聚合

`sourceDefectConfidence`只评价具名源码缺陷；`observedBehaviorConfidence`只评价原轨迹动作/读回；`episodeFailureCauseConfidence`不因前两项confirmed而升级。060持久分支、030实际删除、098整数/完整XML、106第三title/filter、115获胜分项独立保留unknown。

085的原helper readiness error是confirmed；当前npm `io.appium.settings/lib/client.ts:requireRunning`只是解释性源码，历史Node lock/hash/实际加载bytes与service根因仍unknown。098的node格式不兼容是097支持的probable推断，而非098完整XML事实。诊断接口实际位于`src/fsq_androidworld_eval/runner.py:run`（定义541，evaluator边界790–796），不是同文件不存在的`run_episode`；不据此执行任何新诊断。

处理明细和原review证据指针见[review-resolution.md](review-resolution.md)及[review-resolution.json](review-resolution.json)。

## 20案跨报告裁定索引

| case | 关系（仅具体claim） | 最终采用与证据优势 |
|---|---|---|
| 001 | compatible-but-different-scope | Filename contract mismatch plausibly explains zero; exact existence-helper input/result not retained. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 003 | disagree | 十个导航动作后，六个element.click批量结束截图仍X=(0,0)；一次Right坐标tap后X=(0,1)，随后获准三个Down后末X=(3,1)，下一个Right预算拒绝。四次恢复touch有效，不是四次撞墙；不能将四次恢复进展归给之前六click。底层dispatch/快照时序unknown。 控制裁定：MA03 |
| 004 | agree_on_scoped_observations | No entry/Submit and persistent pre-form state support noncompletion; historical JS variables and evaluator UI unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 014 | compatible-but-different-scope | Marker-bearing saved UI notes fail reviewed comparator; final accounting.db/category/cents unavailable. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 023 | agree_on_scoped_observations | Rename was never executed; evaluator-time original/new paths are not independently captured. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 024 | agree_on_scoped_observations | No rename recorded; exact post-quit disk contents/path remain unavailable. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 030 | agree_on_scoped_observations | Physical deletion, survivor set and exact failing filesystem predicate cannot be established. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 033 | compatible-but-different-scope | Exact-name/default extension and line shape diverge; actual evaluator short-circuit branch not captured. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 036 | compatible-but-different-scope | 捕获UI字串按真实fuzzy规则的条件关系>=0.9，不代表文件存在或evaluator已比较/通过内容。可见创建breadcrumb为Download，oracle限定Documents/Markor；物理文件路径/短路分支未捕获，因此目录失分probable。视觉采样不足可改进，但不能以Moria为本次已证失分原因。 控制裁定：MA05 |
| 049 | agree_on_scoped_observations | Wrong saved servings UI and unverified repair explain a probable mismatch; DB and text-changing layer unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 052 | compatible-but-different-scope | 原params共32occurrences/31完整内容类、恰一个二重对；特定title出现10次不等于10个重复。生成器至少8个同title/description贡献是通用下界，不是完整UI group；42视窗观测非42独立记录。未完成Delete confirmed，完整真实DB/行身份/合法34步可行性unknown。 控制裁定：MA04 |
| 058 | agree_on_scoped_observations | Wrong visible membership confirmed; actual clicked-menu IDs, DB insert/dedup/order mechanism unobserved. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 060 | disagree | 已见Select all14首/68:25与移除未commit是业务观测。evaluator读playlist.db joined duration_ms；并无历史最终行集/分支。RetroPlaylistDuration未调用基类初始化/存储隔离是独立源码风险，影响实际集合/seed范围unknown。只知道该次投影未显示per-song数值，不知道所有合法Details/原生路线都不存在。 控制裁定：MA06 |
| 076 | compatible-but-different-scope | 源码期望Grocery Shopping恰17:20却问after，契约冲突confirmed；Agent提交次日title与原oracle不符confirmed。它是否符合strict-after、该日限定/跨日范围及全局first未知；既不认定Agent正确，也不凭解释偏好认定跨日必违规。 控制裁定：MA07 |
| 085 | agree_on_scoped_observations | Wrong route/missing recipient/body/send directly explain noncompletion; historical helper root and evaluator provider rows unknown. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 091 | compatible-but-different-scope | Answer is one observed contribution; second membership/6502m total source-linked probable, no original proto/DB total. 按现有分维confidence；原响应/账本与source条件关系分开 |
| 098 | compatible-but-different-scope | 已见匹配literal node为0、未做semantic/numeric验收、一次swipe候选动作和reward0。正式初始整数、实际XML标签、active geometry、是否改变数值及精确末值未独立留证。若历史实际加载的谓词成功读int，则0逻辑含义为!=255；不是独立读值。无证据排除所有授权native Settings读回路线，也无证据证明初始255被该drag破坏。 控制裁定：MA09 |
| 106 | disagree | 固定proto三title与最终两title必长度拒绝confirmed；第三身份/在UI何处/是否可达/10步内能否完整遍历unknown。Show completed操作后两candidate离开当前viewport是观测，不由menu词/checkbox或排序配置标签证明真实group已存在/可进入，更不据此排除app/visibility问题。 控制裁定：MA10 |
| 107 | disagree | 提交20而oracleCOUNT6及采用label-membership谓词confirmed。各噪声具体绝对日期/formatter语义仅source-linked或probable。四个变化窗口拼接报告26行且保留同窗重复occurrences；被省略的窗口经原回包证为未变，不能认定丢数据或独立merge根因。稳定DB/row IDs仍缺，不据fingerprint声称任意情况下覆盖必正确。 控制裁定：MA08 |
| 115 | disagree | 可见Adventure最后两项反序及追加顺序confirmed；持久DB与UI映射、哪份Boolean通过仍unknown/probable。原分0.5且46/48主动结束，不是budget耗尽；gate结束时closed(agent_finished)。两次policy拒绝不计UI步骤。确已打开行菜单，未发现Move up/down；不等于所有合法reorder/repair不可能。 控制裁定：MA11 |

全部20案有`cases[].moduleAlignment`，逐claim强证据说明、owner mechanism/fix pointers及保留unknown；13项完整落实见[review-resolution.md](review-resolution.md)。


## 37项owner提案到44项eval提案的机制映射

E=同一最小变更；P=部分重叠或不同scope，**不能互换或合并当同一实现**；—=没有等价eval条目，保留owner来源ID而不制造新计数。owner F1与eval F01不是同一编号体系。未配owner逐案项的eval诊断、初始化/metadata/matcher风险与协议选择仍在对应7组内，非遗漏或自动采纳。

| owner fix | E：eval fix | P：eval fix | primaryGroup／采用限制 |
|---|---|---|---|
| 001-F1 | 001-F01 | — | G-ACCEPT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 001-F2 | 001-F00 | — | E-TASK-CONTRACT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 003-F1 | 003-F00 | — | G-ROUTE；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 003-F2 | — | 003-F01 | G-ROUTE；Owner authorized-native guidance overlaps eval Harness prompt visibility, not identical implementation or capability expansion. |
| 004-F1 | — | 004-F00 | G-ROUTE；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 004-F2 | — | 004-F00, 004-F01 | G-ACCEPT；App-level submit acceptance is behavior; eval004-F01 changes future task wording, not the same fix. |
| 014-F1 | 014-F00 | — | E-TASK-CONTRACT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 023-F1 | — | 023-F00, 023-F01 | G-ROUTE；Context route and native-touch idiom; not proof that the full alternate rename path fits the fixed budget. |
| 024-F1 | — | 024-F00, 024-F01 | G-ROUTE；Context route candidate and ledger discipline overlap, not a measured affordable complete rename. |
| 030-F1 | 030-F00 | — | G-ACCEPT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 033-F1 | — | 033-F00 | G-ACCEPT；Independent full identity supports policy; clearing extension must follow requested full-name semantics and observed dialog, never a global extensionless rule. |
| 033-F2 | 033-F01 | — | E-TASK-CONTRACT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 036-F1 | 036-F00 | 036-F01 | G-ACCEPT；Adopt MA05: UI breadcrumb is not physical-path proof. Eval036-F01 is separate goal-scope clarification. |
| 049-F1 | 049-F00 | 049-F01 | G-ACCEPT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 052-F1 | 052-F00 | 052-F01 | G-COVER；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 052-F2 | — | 052-F00 | G-COVER；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 052-F4 | 052-F01 | 052-F02 | G-BOUNDARY；Eval052-F01 caller JSON projection is primary. Eval052-F02 Runtime tuple-support choice is a non-equivalent conditional alternative, not a demonstrated bug fix. |
| 058-F1 | 058-F00 | — | G-COVER；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 058-F2 | 058-F01 | — | G-ORDER-AGG；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 058-F3 | — | 058-F00 | G-COVER；Fallback for an observed unsupported relative query; do not teach that all parent/ancestor operations are globally unsupported. |
| 060-F1 | — | 060-F00, 060-F01 | G-ORDER-AGG；MA06 overrides only-lawful measurement. Reversible aggregate increments are conditional if no legal per-item evidence route has been established; no feasibility or success guarantee. |
| 060-F2 | — | 060-F00 | G-COVER；Viewport versus population policy is not equivalent to eval060-F01 removal/commit reserve. Partial overlap only with eval060-F00 candidate coverage. |
| 076-F1 | 076-F00 | — | E-TASK-CONTRACT；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 076-F2 | — | — | G-TIME-ANSWER；Additional generic scope/ambiguity policy, not equivalent to eval076-F00 task-contract repair. MA07 rejects mandatory day-only interpretation for this goal. |
| 085-F1 | — | 085-F00, 085-F01 | G-ROUTE；Package/recipient/send strategy versus separate historical-helper diagnostic; preserve both scopes. |
| 085-F2 | — | — | G-BOUNDARY；Additional per-case JSON-native policy with cross-case analogue eval052-F01; do not manufacture a new085 eval fix or call it Runtime bug. |
| 091-F1 | — | 091-F00 | G-TIME-ANSWER；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 091-F2 | — | 091-F00 | G-ROUTE；Only observed picker modes; no invented editable header or guaranteed filter route. |
| 098-F1 | — | 098-F01 | G-ACCEPT；MA09: coordinate976 not proven wrong; active geometry and exact scalar unknown. Do not equate bounds/icon with active endpoint. |
| 098-F2 | — | 098-F01 | G-ACCEPT；MA09: stop only if target independently established. Initializer requests max, not proof actual initial255 or drag regression. |
| 106-F1 | — | 106-F00 | G-COVER；MA10: actual Completed strings are sort settings; no enterable group or third-title reachability established. Coverage guidance conditional on observed surface. |
| 106-F2 | — | 106-F00 | G-COVER；MA10: menu labels/toggle disappearance alone are not membership; actual grouping route remains conditional. |
| 107-F1 | 107-F00 | — | G-TIME-ANSWER；Same bounded proposal scope; existing loaded guidance does not establish a missing rule or measured effectiveness. |
| 107-F2 | — | — | G-COVER；MA08 rejects global-dedup/merge-loss premise. Only generic overlap/redundancy documentation remains; no equivalent eval107-F00 date-predicate change. Cross-case analogue eval052-F00 is not a107 root cause. |
| 115-F1 | 115-F00 | — | G-ORDER-AGG；Order-first prevention; do not infer which persisted Boolean component passed. |
| 115-F2 | — | 115-F01, 030-F01 | G-ROUTE；MA11: row menu was opened; pointer compatibility alone does not establish reorder affordance. Swipe is not universally scroll; clickable=false is not proof no drag. |
| 115-F3 | — | 115-F01 | G-ORDER-AGG；Conditional repair, not equivalent to eval115-F00 prevention. Row menu inspection occurred; no within-budget removal/reappend guarantee. |

原owner具体location、所有44eval的反向映射和review override IDs保存在`cases.json.moduleAlignment.proposalMapping`及每个`fixes[].moduleAlignment`。owner原始建议的错误前提不因保留source pointer而被采纳。

