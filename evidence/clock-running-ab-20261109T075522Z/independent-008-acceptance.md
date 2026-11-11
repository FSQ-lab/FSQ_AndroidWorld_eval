# 008 ClockStopWatchRunning：独立只读验收

署名：**w4:p2 独立审查助手**。审查时间：**2026-11-09T08:13:04Z**（Unix 1794211984.730992）。运行所有者：w4:p1；父会话：w3:p1。

本报告专属于 `clock-running-ab-20261109T075522Z` 的新两单诊断，不沿用旧六单验收。机器可读完整记录：`independent-008-acceptance.json`。

## 确定结论与验收决定

**验收通过：本次原臂确实复现“秒表在运行、官方判0”，直接原因是原官方谓词实际收到空 UIElement 输入；生产修复组合臂本次确实通过原 Pause+Lap 判据，原返回值与保存 reward 一致。** 这是固定两单的实测结论，不是对历史008唯一根因的追认，不是纯生命周期补丁效果估计，也不意味着所有 Appium/MCP 延迟已修好。

| 本次单元 | 原 scorer / 保存 reward | 动作/预算 | 官方选中 recv | 窗/节点/UIElement | 原 line40 Pause / Lap / 返回 |
|---|---:|---:|---:|---:|---|
| ClockRunningOriginalP0：原APK、cap实际省略 | 0.0 / 0.0 | 4/10 | 2118 | 0 / 0 / 0 | false / false / false |
| ClockRunningPatchedP1：生产APK、cap实际true | 1.0 / 1.0 | 4/10 | 1414 | 2 / 27 / 17 | true / true / true |

矩阵 completed、error=null；恰好按A→B各一次，宿主子进程分别74074/75025，均退出0。两单原 result 的 error/invalidReason 均为null；无 reward 导向重跑。formalScore=null，不改原 campaign。

## 008身份：不是脚本代跑或替换任务

- 直接核对原 result/manifest 与两变体 manifest：`ClockStopWatchRunning`，index8，seed3429360255，complexity1，预算10；paramsSha256=`fe15fe1739bca1ce130f387e2e84d273c4a55e5403a5c174c7a2ec65119afaf9`。实际 goal 是 **Run the stopwatch.**，不沿用早先摘要误写的 Start the stopwatch.
- 两单原 raw Agent 事件第10行起的 assistant provider/model 均为 `github-copilot/gpt-5.6-sol`，与原 manifest/result 一致；不是仅检查launcher声明，也不是人工重放历史动作。
- 独立遍历历史 raw JSONL：只找到一个不同的完整目标 prompt，最早第8行，全文 SHA=`952af5c25db36a402f354b7699240f19764fd8182db0d6f1f78532c6372bed9e`。两单 `actual-agent-prompt.json` 的真实传入全文只归一化各自一个动态 loopback proxy 端口后逐字相同，不只是模板 digest 相同。
- 独立读取当前 `.agents` 全部152个常规文件，逐文件对照并按原 canonical path/hash 算法重算：aggregate=`0ff33bb8ee50c160d87842ed11324e557f6fe5fc81c8e4fe06230a4d7bf792b8`；metadata=`cd10df3d883ca08c52f8ebbcc7c052a77fa852bd130c2326405e42269c1a29e0`；official manifest=`235e9bc07365f0822db0893f4334848cb09e93e2a1673021499146738238aff6`。均与原冻结身份一致，两单工作区技能也各自152文件匹配。被拒绝的 Git HEAD 0.1.2快照不是运行资产。
- 原 timeBudget 720秒business、180秒cleanup、120秒recovery、1330秒episode等字段逐项保持；MCP transport120000ms、session创建90秒、单episode最多1session；fullTaskRetryLimit=0、invalidRetryLimit=1等原限制在变体manifest逐项一致。本次实际无任务重试。
- 已核对六个诊断脚本的当前hash、launch protocol和两单 executed identity一致；原安装 `clock.py` 全文件SHA均为 `b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c`。源码版本/命令/实际prompt与技能证据保存在各单 `executed-identity.json`、`run-command.json`、`actual-agent-prompt.json`、`agent-workspace-skill-identity.json`。

## 实际判分输入与原分支闭环

已亲读本实验的 `clock_probe.py`：仅通过 `sys.settrace` 观察原 frame，调用原 `ClockStopWatchRunning.is_successful` 一次并原样返回。没有重放谓词、替换观察后端、过滤空树或额外调用 `get_state`。两个wrapper层记录的get_state返回指向同一原state，去重后各一份逻辑判分输入，不冒称两次独立采样。

**A：** state ID5026074704；其实际ui_elements列表与原predicate参数同ID5026249856；列表确为空。原activity调用返回 `com.google.android.deskclock/com.android.deskclock.DeskClock`，所以不是activity门失败。原 `_is_stopwatch_running` 的 Pause/Lap赋值分支均未执行，第40行以false/false返回false，原scorer返回0.0，与原result保存0.0一致。实际选 recv2118，经真实drain7进入官方选择；0字节 forest.pb 的SHA=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，原对象identity追踪无错配。

**B：** state ID5087254928；实际列表与predicate参数同ID5086192960。17个原UIElement中索引3为Pause、4为Lap，包均为 `com.google.android.deskclock`。还独立匹配了原第37/39行赋值事件的element对象ID分别等于这两个原参数元素ID；第40行原返回true，原scorer返回1.0，与保存1.0一致。实际选recv1414；forest.pb SHA=`06442ba3b97c22192b00f8acee3a7f99a7b62b13806e60373cc6ab17a3eb1c06` 与trace一致；sender=`14073:1/gen1/seq1414`。

两单原trace和scorer trace errors均为空。核心原证据在各单 `clock-probe/evaluator-calls.json`、`clock-probe/evaluator-000/state-00/{pixels.png,forest.pb,ui-elements.json}` 及 `forest-trace.json`。Appium XML没有替代官方UIElement输入。

## 动作、真实计时与不利运行结果

两单均只做一次滑动、点Clock、点Stopwatch、点Start；Start没有因超时重复点击，没有Pause或Lap业务动作。已逐条读取原Python执行代码与响应。已亲读两单各四张原PNG，计时变化如下；截图时间记录是host请求/完成窗口，不是设备render时间。

| 单元 | pre-quit Appium | post-quit | later截图 | 原官方state.pixels |
|---|---|---|---|---|
| A | 2:25.83 | 2:26.49 | 2:27.35 | 2:31.35 |
| B | 1:15.92 | 1:16.52 | 1:17.35 | 1:22.79 |

两单pre-quit原Appium XML均精确存在Pause和Lap，截图也显示暂停控件和递增时间。A官方原pixels仍在运行，但同次原forest/UIElement为空——证明本次判零不是“没按Start”。

**保留不利证据：** A有11次MCP执行，其中3次分别以30/20/60秒budget返回timed_out，其余8次completed；B有9次，6次completed、2次timed_out（30.015秒/15.011秒），另1次在8.008秒返回 `urllib3.exceptions.ReadTimeoutError`。所有Kernel响应均alive，最终均在同一owned session成功quit。

B第8个模型生成cell把HTTP read timeout设为8秒，触发loopback read timeout；第9个cell恢复30秒再quit。这是实际模型行为，既不是Harness偷偷改timepolicy，也不是本报告推荐调整driver设置。两单动作类别相同不等于代码、调用时序相同；尤其不能把A三次超时说成精确复现历史两次10秒超时，或声称修复组合消除了全部MCP/UI-idle延迟。当前材料没有足够内部driver等待trace来唯一指认每次慢调用的内部机制。

## Appium/forwarder因果与时序

- **产物/cap均核对真实路径。** A部署SHA=`97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a`，实际Appium日志POST/session体及响应均没有目标cap。B部署生产SHA=`0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`，实际上游POST体和返回cap均确认 `disableSuppressAccessibilityService=true`；不是仅看默认配置或模型原请求。生产本地APK字节也独立重算吻合。
- **A首失在创建期间。** 独立重算last nonempty recv447、first empty448；其后1671份直到2118全部空。首空早于创建响应约0.437秒，远早于quit，不把quit后NPE倒写为首次丢树原因。原系统快照显示创建前Bound helper、创建后helper仍Enabled但不Bound且UiAutomation存在，旧发送PID11137/TID11162仍持续发送。
- **A另有quit重绑崩溃。** 已亲读 `device-logcat.txt:12164–12176`：PID11137/TID13053 Thread-3在构造lambda访问空Context，经 `AccessibilityService.getWindows` / `AccessibilityForwarder.kt:51` NPE。quit-response快照Crashed且无helper PID；之后新PID13131出现。postrun的实际accessibility命令host1794211581.089761–1794211581.131486观察到Bound，晚于scorer返回1794211579.9959822。**这仅给观察时点，不证明绑定转变必在判分之后；native新进程启动本身可更早。** 不称从未/不会恢复；评分可确认事实仍是实际选中空recv2118，后来Bound不证明该次输入健康。
- **B为本次持续并存路径。** 1420份recv全部非空，均来自 `14073:1/gen1`，实际选1414；创建后/quit前后样本均可见Bound helper。本项不是stop/reconnect恢复路径的单独验证，不能拿其他任务的worker证据代替。
- **本次原native日志确实不同：** A `device-logcat.txt:5135` Init flags=0；B `device-logcat.txt:4821` Init flags=1。保留这些实际字段，不沿用旧矩阵不同日志，也不把Init字段推广成所有后续内部最终flags值的独立测量。
- A原state返回时选中消息host receive-age约5.297秒；B约0.108秒。后续保存时再describe可更大（如B约0.361秒），不互相冒充，更不把host receive-age当设备生成age。官方初始化改变设备时间，跨host/device时间必须用采样区间，不能直接减两个epoch。

额外诊断开销已明示：A pre/post约11.037/1.155秒；B约10.992/1.069秒。pre-quit source至多12秒；post-quit两截图之间0.6秒分隔。这些额外观察不计UI业务动作、不冒充官方输入，但影响时序，所以不声称未加诊断原时序完全复刻。

## 清理、最终恢复与历史完整性

逐单核对原result/audit：session创建/删除各1，active/pending create/pending request/unknown creation均0；Agent quit真正返回，逐session absentVerified=true，verificationStatus=absent，environment closed、task teardown completed。原嵌套verification.status=unknown保留，不改写来制造清理成功。

两单各有原 `workspace-post-exit-absence.json`，另有新增而未覆盖原件的 `workspace-parent-post-exit-absence.json`：各自进程退出以后workspace和临时父目录皆absent。

已亲读所有者 `final-native-restoration.json` 原stdout而不只看true字段：最终helper实际SHA恢复生产pin；Bound确有helper、Binding为空，PID16128；UiA2进程空。bootID、enabledServices、accessibility_enabled与preflight原stdout逐字相同；既有runner权威查询sessionHashes=[]。Appium3的直接GET /sessions返回404是**不支持该路由**，绝不据此证明无session。最终恢复快照不是新增SendForest健康测试。

本审查另行逐文件读取并SHA-256重算登记基线的14,434,241,098字节：2186/2186文件，0改动、0缺失。范围严格为2185个campaign文件+1个缓存原APK，不覆盖全冻结Python/AMKernel安装树或基线外新增路径；技能152文件另有上述独立范围。原008三份历史源文件也独立比对原登记摘要吻合。

## 限制和验收依据

**通过依据：** 原任务/模型/全文prompt/技能/预算与策略身份闭环；两单原输入对象、原Pause+Lap分支、原float返回和保存reward一致；真实计时与动作记录证明两个任务都已启动；cap/产物/forwarder时序证据支持本次观察链失败与生产组合通过；原始不利响应未隐藏；逐session及退出后清理、恢复和限定hash范围均可核对。

**仍未知/不接受的扩大结论：** 历史008缺实际官方输入，不能唯一归因或改判；历史最后正则不含Lap，不能用列表缺Lap证明原UI缺Lap；A/B同时改变APK/build-stack和cap且每臂仅一次，不能隔离单组件因果或估计总体成功率；原 sender元数据空，不能补造instance/generation；计数不形成benchmark专用规则；B仍有超时及失败，不能宣称所有原生等待问题已解决。

审查方只读文件与已保存图像、做离线一致性和hash计算；**零设备查询、零session、零构建、零生产源码修改**，不覆盖所有者报告、不新增实验、不新增benchmark专用指导。父会话的 `parent-raw-consistency.json` 是独立保存的父自查，不能冒用为本审查作者的运行或新reward。
