# ClockStopWatchRunning：第四个正常结束但官方失败任务

## 结论

**原 Agent 确实发出了启动动作，之后在同一 session 读到了正确 Clock 包名、Pause 和非零计时片段。不能把原 reward=0 直接归因为模型没有启动秒表。** 原记录能够确定两个验证调用被原生查找拖到 AMKernel 单调用超时；它们不是预算耗尽，也没有导致 Kernel 或 session 丢失。

**现已在本次008真实受控运行中确定复现：秒表持续运行，但原官方判据实际消费空forest/UIElement列表而判零；既有生产修复组合在另一固定单中恢复有效官方输入并判一。** 这是008本身的新证据，不是借用007或旧六单成绩。历史原008未保存当时官方输入，其唯一历史根因仍未知，不回填旧成绩；现场证据见末节。

最初分析为离线取证与已安装官方谓词smoke。用户随后明确要求Herdr联合测评，故由唯一设备所有者w4:p1在新独立目录执行固定两单；父会话w3:p1与独立作者w4:p2均只读落盘材料，不查询或操作设备。原campaign及原成绩保持只读。

## 原任务与结果

- 冻结 campaign：`amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z`，r12 v2；原任务 `ClockStopWatchRunning`，原 `result.task.goal` 及官方 template 均为 `Run the stopwatch.`，冻结 params 为 `{"seed":3429360255}`，complexity=1，paramsSha256=`fe15fe1739bca1ce130f387e2e84d273c4a55e5403a5c174c7a2ec65119afaf9`。
- 原 officialReward=0.0，error/invalidReason 均为 null；Agent 正常 stop，原最终提交为 success。
- 原预算10，实际4个 UI 动作：应用抽屉滑动、Clock点击、Stopwatch点击、Start点击；未耗尽，无拒绝动作。
- 九次 python_exec：七次 completed，两次 timed_out，所有响应 kernelState=alive。没有重建 session 或重放 Start。

## 原始调用与最早无效验证

原始 JSONL 下列行号为完整文件的1-based行号。提取副本及每次原代码/原响应见 [original-python-executions.json](original-python-executions.json)。

| executionCount | 原始调用/响应行 | 行为及可见结果 |
|---|---|---|
| 1 | 374/375 | 创建唯一 Appium session；newCommandTimeout=300。 |
| 2 | 661/662 | 启动器 package/activity 与有界控件观察。 |
| 3 | 873/874 | 滑动打开应用抽屉，观察到 Clock 候选。 |
| 4 | 1108/1109 | 点击 Clock，返回正确包名、`.DeskClock` activity 和应用控件。 |
| 5 | 1345/1346 | 进入 Stopwatch；观察到 Start、主计时00、百分秒00。 |
| 6 | 1675/1676 | 点击 Start 后，5秒 WebDriverWait 内连续执行多个原生 find；10秒单调用预算在10009ms到期，timed_out/alive。 |
| 7 | 1832/1833 | 未重复点击；再次逐控件查询，另一10秒预算在10003ms到期，timed_out/alive。 |
| 8 | 1968/1969 | 同一 session 查询包名并读取一次 page_source，10097ms完成；返回 Clock、Pause、Stopwatch、40、96。 |
| 9 | 2037/2038 | 唯一 session quit 返回；随后原 Agent 提交 running/success，将计时片段解释为40.96。 |

**最早可确认的低效点是 execution 6 的动作后验证，不是启动动作本身。** 原 Appium 日志62906–62913显示 Start点击72ms成功返回，随后 stopwatch_time_text 的原生查找耗时10103ms；62914–62915的下一次fab查找耗时10042ms，均返回HTTP 200。execution 6的Python 5秒轮询期限无法中断一个超过它的同步原生调用。

execution 7仍使用同样的逐元素读取路径，未引入足以避开原生等待的新观察方式；execution 8才改为同一session的包名和一次source读取。它没有重复Start、盲建session或擅改driver设置。约10秒原生耗时与持续变化界面的UI-idle等待相容，但历史Appium日志没有内部等待trace，**具体是哪一项driver等待不可直接确证**。

Appium日志：`evidence/screenshot-video-controls-20261106T231029Z/appium.log:62906-62928`。source本身耗时10067ms、HTTP 200，日志仅保留响应大小而无完整XML。

## 官方判据和缺失证据

已安装官方 `clock._is_stopwatch_running` 要求：

1. activity包含 `DeskClock`；
2. UIElement中存在 `content_description == "Pause"`；
3. UIElement中还存在 `content_description == "Lap"`。

原 execution 8 的本地正则只返回 **Stopwatch/Pause/Start/数字**，不包含Lap匹配分支。因此列表中没有Lap，**不能解释成真实屏幕或官方树缺少Lap**。此时也没有返回当前activity，先前execution 4的activity不能冒充最终官方activity。

已实际运行冻结评测虚拟环境中官方函数，退出码0；安装包与仓库clock.py完整文件hash一致。明确构造的三个离线输入证明：空列表判false；仅Stopwatch/Pause的部分描述也判false；Pause和Lap同时存在且activity正确才判true。见 [predicate-branch-smoke.json](predicate-branch-smoke.json)。这些是**契约反例/合成最小见证，不是历史判分输入、重新判分、现场复现或新reward**。

历史Agent最后观察后先quit，官方判分随后执行；该顺序经过了与上一项相同的服务解绑/恢复风险边界。但是本项未保存官方实际输入，无法在“空树、缺少Lap、最终activity不符或其他官方观察不一致”之间作唯一归因。原始调用没有任何图像返回，不能补称已看过历史屏幕。

## 分层归因与修改决定

| 层 | 本项能证明的结论 | 不能扩大的结论 |
|---|---|---|
| 模型规划 | 走到了正确应用/Stopwatch页，Start只点击一次；事后有Pause和非零计时片段。验证第二次沿用了昂贵逐控件路径。 | 不能据reward=0断言未启动，也不能仅凭部分描述证明官方全部条件成立。 |
| 技能指导 | 原生等待不受外层轮询期限约束；一次有界source可减少逐元素往返。当前Android指导已经明确覆盖该问题。 | 本项没有发现需要新增的benchmark专用规则；不改预算或driver设置掩盖耗时。 |
| AMKernel Runtime/MCP | 两个timed_out/alive如实返回；后续同namespace、同session继续执行并完成quit。 | 没有证据证明Runtime丢失状态、错误执行或隐式重建Kernel。 |
| Appium/应用环境 | 启动后原生查询耗时约10秒，是两次验证超时的直接边界。 | 没有内部driver trace，不把UI-idle等待具体机制写成已测事实；这也不是官方判零的充分原因。 |
| Harness/评测观察链 | Agent观察与原官方reward不一致；官方判据需要历史未保留的完整输入。上一项观察链修复相关。 | 历史008唯一根因未知；不得把007受控复现、或其修复后的成功，冒充本项现场验证。 |

**本项不新增生产修改。** 当前 `src/amkernel/skill/references/android-execution.md` 已要求对持续变化界面避免逐元素等待、超时后协调同一session，且明确session缺席不等于独立观察链健康；共享Appium指导也已要求验证相关变化状态、避免无证据重复等待。没有必要重复建立第二套约定或修改AMKernel核心。

上述离线取证之后，已按用户要求完成008原配置/生产修复配置两单联合现场诊断，详见末节。没有新增benchmark专用生产修补，亦没有将离线契约smoke冒充正式任务结果。

## 原清理及完整性

原session创建/删除各1，active/pending/unknown creation均0；Agent quit返回，独立session查询HTTP404，`absentVerified=true`、`verificationStatus=absent`，teardown和environment_close完成。原嵌套 `verification.status=unknown` 保留，不改写该字段。

离线阶段逐项核对原 `result.json`、`normalized-agent-events.json`、`raw-private/agent-events.jsonl` 哈希，范围仅这些登记源文件，不代表完整冻结安装树。哈希与当时离线复核结果见 [review-verification.json](review-verification.json)；该文件保留为离线阶段记录，不冒充后续现场验收。父会话没有操作设备；新现场运行与清理记录由w4:p1单独落盘。

## Herdr联合现场诊断：008本项已确定复现与修复后验证

新独立目录：[`clock-running-ab-20261109T075522Z`](../../../clock-running-ab-20261109T075522Z/)。设备唯一所有者w4:p1；父会话w3:p1核对原始帧/像素/PB；w4:p2负责本次独立验收，不沿用旧六单passed。

固定顺序仅执行A、B各一次，不按reward重跑。原seed、complexity、params hash、模型、10步预算、时间策略及重试边界保持；实际传入prompt与历史raw第8行唯一原文仅归一化动态loopback proxy端口后逐字相同。逐单工作区152份技能文件digest与原manifest一致；没有安装新技能或让新指导改变对照。

| 单元 | 实际配置 | 动作/预算 | 官方选中recv | 节点/UIElement | 原Pause/Lap分支 | 保存的官方reward |
|---|---|---:|---:|---:|---|---:|
| ClockRunningOriginalP0 | 原APK、实际转发cap省略 | 4/10 | 2118 | 0/0 | false/false | 0.0 |
| ClockRunningPatchedP1 | 生产APK、实际显式true并确认 | 4/10 | 1414 | 27/17 | true/true | 1.0 |

### A：真实运行与空官方输入同时成立

A的prequit XML包含精确Pause/Lap；四张已落盘屏幕由所有者/独立作者亲读，显示2:25.83、2:26.49、2:27.35、官方state像素2:31.35，计时持续增长。父会话另亲读后两张，确认不是暂停状态。

原scorer真正调用的是未更改的running谓词：正确DeskClock activity通过，真实输入list ID5026249856与state.ui_elements同一对象，列表为空，line40原返回false，scorer原0.0与保存reward一致。实际选中recv2118的PB为0字节，SHA256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855；真实drain7返回该对象，不是从旁路抓取一棵空树代替官方输入。

首失时间线：最后非空recv447；首空448在session创建响应前约0.437秒；其后1671个接收均空。保存的绑定快照从session-request时Bound变为session-created后Enabled但Unbound，原worker仍持续发送空树。quit重新绑定时同PID11137的另一构造线程TID13053发生null Context NPE，源堆栈指向constructor lambda内getWindows。**首失早于quit NPE；这是两个阶段的故障，不能把后者当首失原因。**

postrun快照后来观察到新PID13131已Bound。该快照采样晚于原scorer返回，不等于实际绑定转变必在判分后；也不能据此宣称从未恢复、或反证这次确实消费空输入。原APK没有sender生成时间，host receiveAge不能冒充设备生成age。

原证据：[A结论](../../../clock-running-ab-20261109T075522Z/original-A-conclusion.json)、[首失时间线](../../../clock-running-ab-20261109T075522Z/original-A-first-loss-timeline.json)、[绑定时序边界](../../../clock-running-ab-20261109T075522Z/original-A-binding-chronology.json)。

### B：既有生产修复恢复了本项正确判分

B的官方state像素为运行中的1:22.79；父会话另亲读postquit later像素1:17.35，确认计时继续。真正predicate输入list ID5086192960与同次state.ui_elements一致；DeskClock activity正确，Pause/Lap均true，line40原返回true，scorer原1.0与保存reward一致。

实际选中recv1414有2窗口、27节点、17个UIElement，PB SHA256=06442ba3b97c22192b00f8acee3a7f99a7b62b13806e60373cc6ab17a3eb1c06。父会话直接对A/B原PB文件重算hash，并在未改官方clock.py（b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c）上离线运行两份真实序列化UIElements，得到false/true，与原帧一致，命令退出0。该动作只是离线一致性核对，不是新判分或新reward：[父会话核对receipt](../../../clock-running-ab-20261109T075522Z/parent-raw-consistency.json)。

### 没有被本项修好的内容与因果限制

- A本次11次MCP含30/20/60秒三次timed_out/alive，不能称为历史两次10秒超时的逐调用复现。
- B本次九次MCP仍有两次timed_out（30.015/15.011秒），另有一次8.008秒的urllib3.exceptions.ReadTimeoutError；Kernel均alive。**此次修复验证的是观察链及正确判分，不是消灭全部原生等待、MCP超时或Client读超时。**
- A额外prequit采集约11.037秒、postquit约1.155秒；包含0.6秒间隔的双图观察。它们不算业务动作、不替代官方状态，但确实改变时序。两单模型输出/超时序列不相同，不可称逐调用时序完全一致。
- A和B同时改变APK与capability；每臂只有一次且固定顺序。因此证明的是既有生产修复组合在本次008正确工作，不单独量化各补丁贡献，不构成全量提升或长期稳定性证明。
- 历史原008官方输入依旧缺失；新复现不能回填历史唯一根因，formalScore保持null，原campaign不改分。

### 清理与恢复

两单均自然结束，error/invalidReason为null；真实quit返回，逐session absent，environment close/teardown完成，workspace及临时父目录退出后缺席。原嵌套verification.status=unknown保留，不把它覆盖成passed。

[最终原生恢复快照](../../../clock-running-ab-20261109T075522Z/final-native-restoration.json)确认生产helper实际hash0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb、normalBindingObserved=true、bootID不变、enabledServices/accessibility_enabled与前置一致、runner所属sessionHashes为空。GET /sessions在Appium3的404只记录为不支持，不拿它充当无session证明。没有追加任务、重跑、重启共享服务或全量测评。

### 本次独立验收已完成

独立作者w4:p2于2026-11-09T08:13:04Z完成新署名验收，结论 `PASS_FOR_THIS_FIXED_TWO_RUN_DIAGNOSTIC_WITH_EXPLICIT_LIMITS`，不是沿用旧六单结果。独立亲读两单原帧、实际input identity/PB与八张截图，核对原prompt/模型/技能及清理；另逐文件重算2186条登记基线（2185个campaign文件+一个缓存原APK），0改动、0缺失，不扩大为全冻结安装完整性。父会话已亲读其完整验收和机器结论。

- [本次所有者总报告](../../../clock-running-ab-20261109T075522Z/report.md)
- [本次新署名独立验收](../../../clock-running-ab-20261109T075522Z/independent-008-acceptance.md)
- [独立机器验收](../../../clock-running-ab-20261109T075522Z/independent-008-acceptance.json)
- [所有者终态核对](../../../clock-running-ab-20261109T075522Z/final-acceptance-checks.json)

设备所有权已由运行所有者释放；父会话与审查方没有追加设备操作、session或实验。最终工程结论：**本次008失败由空官方输入确定触发，既有生产修复组合在本次008恢复正确判分；不需要再向AMKernel核心或技能添加特例，但原生调用延迟/Client读超时仍存在。** 历史唯一归因、纯单组件贡献及长期稳定性保持未证明。

