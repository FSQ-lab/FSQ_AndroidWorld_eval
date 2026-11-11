# ClockTimerEntry：009正常结束但官方失败任务

## 结论与归属

**本次009原配置受控单确定重现：时间正确且未Start，但官方实际消费空forest/UIElement列表而判零。既有共存与生命周期生产修复组合在另一固定单恢复正确官方输入、原判据判一。** 这是009本项的新现场证据，不是套用008超时或NPE。

历史原009判分时的官方输入未保存，其唯一历史根因仍未知；不回填历史成绩。本次不是正式campaign或正式r14 qualification，formalScore=null。没有修改AMKernel核心、技能、任务参数、模型、预算、重试边界或evaluator，也没有增加009特例。

唯一设备操作方为Herdr w4:p1；父会话w3:p1与独立作者w4:p2只读落盘证据。运行仅原配置A、生产修复B各一次，没有按分数重跑。

## 历史原任务与最早可确认的边界

原campaign：`amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z`；原目标为创建0小时16分35秒、不要启动。params seed=1172248264，complexity=1，paramsSha256=`3c6dc22a2339a8e10eab5472bd837b52efb43b0125410cd5522c8ce88a29192b`。

历史7/10动作，正常结束，reward=0、error/invalidReason=null。原11次Python调用全部completed/alive，没有timed_out、异常或Kernel重建。原始代码/返回完整提取见[original-python-executions.json](original-python-executions.json)。

| 原execution | 原raw调用/响应行 | 实际动作或观察 |
|---|---|---|
| 1–2 | 338/339、529/530 | 唯一session创建、newCommandTimeout=300；启动器观察。 |
| 3–4 | 733/734、865/866 | 点击Search打开启动器搜索，观察Clock候选。 |
| 5–6 | 971/972、1127/1128 | 点击Clock，返回正确包名/DeskClock activity；观察应用。 |
| 7–8 | 1261/1262、1417/1418 | 进入Timer，selected=true；读取设置页。 |
| 9 | 1699/1700 | 点击1/6/3/5，返回精确text=`00h 16m 35s`及description=`0 hours, 16 minutes, 35 seconds`。 |
| 10 | 1880/1881 | duration精确正确、setupVisible=true、Start enabled=true、Timer selected=true。 |
| 11 | 1953/1954 | 唯一session quit成功、kernel alive。 |

历史没有可确认的错误业务动作或无进展循环；最早可确认的证据断点是**成功的原生观察/quit与随后官方判零之间，未保存原官方输入**。原exec9/10没有同时返回最终activity，不拿此前activity充当该时刻快照。历史无图像返回，亦不补称看过历史屏幕。

## 009本次真实前后对照

独立新目录：[timer-entry-ab-20261109T082047Z](../../../timer-entry-ab-20261109T082047Z/)。两单保留原task、模型`github-copilot/gpt-5.6-sol`、真实全文prompt（只归一化动态proxy端口）、152份原技能身份及原时间/预算/重试策略。不是让新技能改变Agent对照。

| 单元 | 实际配置 | 动作/预算 | 官方选中recv | windows/nodes/UIElements | 原timer分支 | 原reward |
|---|---|---:|---:|---|---|---:|
| TimerEntryOriginalP0 | 原APK副本；实际cap请求/响应省略 | 7/10 | 1132 | 0/0/0 | line100 false | 0.0 |
| TimerEntryPatchedP1 | 生产APK；实际显式true并确认 | 7/10 | 998 | 2/36/27 | line98 true | 1.0 |

两单业务动作均为一次抽屉滑动、Clock、Timer、数字1/6/3/5，无Start、重输或人工追加动作。与历史原Search点击不同，不能称为逐调用重放。

两单prequit原Appium XML均有精确时间text/description、显示中的setup及enabled Start。所有者逐单亲读四张原PNG；父会话另亲读各单官方state像素及postquit-later像素，均为16m35s数字输入盘+Start，而非倒计时运行界面。结合全部原代码与点击对象语义，证明未Start，不单凭reward或Agent提交。

quit后没有活Appium session，故本次没有postquit Appium XML；认可的观察组合为prequit原XML、postquit双原生PNG、同次官方原PB/forest/UIElements/pixels及动作ledger。没有新建session、uiautomator dump或伪装成原XML的派生内容。

### 原谓词与真实对象闭环

未改官方`clock._is_timer_set`实际kwargs为hours=0/minutes=16/seconds=35，activity均为DeskClock。A真正实参列表与state.ui_elements同一对象ID5019801600、为空，原line100返回false；原scorer和保存reward均0。实际PB为空字节，SHA256=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

B真正实参列表与同次state.ui_elements同一对象ID5052825344；原列表index2、elementID5053206544为正确timer元素，原text分支line95短路至98返回true。实际recv998 PB SHA256=`f259286df2d17cbe859716c23b962963b5673bbaf9f8e0ae20b8a30e9f9f0c88`，原scorer和保存reward均1。

父会话另重算两份原PB hash，核对保存元素与实际参数逐项相等、列表身份一致，并使用未改官方clock.py对两份真实序列化UIElements离线核对false/true，命令退出0。模块完整hash=`b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c`。[parent-raw-consistency.json](../../../timer-entry-ab-20261109T082047Z/parent-raw-consistency.json)仅为离线一致性核对，不是新判分或新reward。

### 本项实际失效机制：不套008

- 首失前最后非空recv480；首空481早于session创建响应约0.530099秒。创建后原helper仍Enabled、PID17373存活，但不再Bound；481–1053连续573条空。
- quit-response原快照采样完成时已经Bound同PID17373，**早于本次评分**。recv1054已恢复非空；Bound采样结束至scorer前74条接收中38空、36非空。不是从此全空，更不是绑定永不恢复。global最后非空1142不是首失前的last good。
- 父亲读本次native log10839–10870，同PID旧TID17399与新TID19213并行tree-send，新线程还有processNodes。支持原worker未随解绑停止、重绑后新旧采集竞争的通用生命周期缺陷。原metadata缺失，不能把特定recv1132硬分配给某TID。
- 实际官方最终选择空recv1132，原predicate直接因此判零；它不是数字、Start或activity分支错误。
- 原state返回时消息host receive-age约0.017900秒，之后保存describe约0.224239秒；不是设备生成age，也不是008的陈旧5.297秒机制。
- 本次A定向日志扫描没有forwarder FATAL/NPE，不复制008构造器NPE。父亲读A5171、B4837均`Init UiAutomation ... flags=0`，不是008的A0/B1；初始化回调不等于最终有效flags。cap请求/响应、实际绑定和真实有效消息是分别留证的事实，不能相互替代。

时序及并发原文见[original-A-first-loss-timeline.json](../../../timer-entry-ab-20261109T082047Z/original-A-first-loss-timeline.json)、[original-A-concurrent-workers.json](../../../timer-entry-ab-20261109T082047Z/original-A-concurrent-workers.json)。

## 修改位置与当前状态

本项没有新增生产代码。此前已落地的通用修复位于评测仓库：

- `src/fsq_androidworld_eval/appium_proxy.py`：实际转发显式`appium:disableSuppressAccessibilityService=true`，核对返回确认，矛盾/未确认fail closed并保留session协调所有权。诊断A的缺省例外不放宽生产guard。
- `forwarder/src/AccessibilityForwarder.kt:72-142,199-232`：onServiceConnected启动唯一连接worker；unbind/destroy取消worker/RPC、关闭所属channel并join，拒绝旧connection重新发送。真实空树不被过滤，不靠丢弃空输入伪造成功。
- `assets/fsq-accessibility-forwarder-lifecycle-v1.apk`：本次生产字节SHA256=`0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`，既有实现说明见`forwarder/README.md`。

本次B有效接收全部来自生产sender20200:1/gen1；五个生命周期采样点同PID20200保持Bound，实际官方输入与业务状态一致，验证现有修复组合在009生效。**无需向AMKernel核心或技能增加benchmark特例。**

模型仍有局部代码错误，不能用判一掩盖：A8次全部completed/alive；B12次中9次completed、3次failed，均alive且没有timed_out。B exec3导入不存在的appium actions包；exec4使用不支持的duration参数；exec5已成功swipe后引用未定义WebDriverWait。模型自行读取已变状态后继续，没有重复swipe或重建session。错误归模型/API使用，不是Runtime丢失namespace；本项也不是“所有代码错误已修好”的证据。

A/B同时改变APK/build-stack和cap，每臂仅一次、固定顺序；只能证明修复组合本项现场覆盖，不能量化单组件贡献、长期可靠性或全116项增益。额外观察会改变时序：A prequit/postquit约0.734711/0.914345秒，B约0.667045/0.907552秒，包含双图观察间隔；不是业务动作，但不宣称零开销或逐调用等时序。

## 清理、完整性与后续边界

两单真实Agent quit返回、create/delete各1、逐session absent，active/pending create/pending request/unknown creation均0；task teardown completed、environment closed。原嵌套verification.status=unknown保留，不改写该值为passed。退出后的工作区及父TemporaryDirectory缺席，独立post-exit receipt新增保存，未覆盖原退出前receipt。

父已读[final-native-restoration.json](../../../timer-entry-ab-20261109T082047Z/final-native-restoration.json)原stdout：生产APK字节正确、Bound且Binding/Crashed空、权威sessionHashes=[]、UiA2进程/active instrumentation空；bootID、enabledServices、accessibility_enabled与preflight逐字一致。所有者已释放设备/服务，父未追加设备操作、session、共享服务重启或实验。

历史原009的result/normalized/raw三个登记源hash由父另行重算均匹配，见[review-verification.json](review-verification.json)。全局3793登记路径审计由所有者及本项独立作者负责，范围仅既有2186路径加008证据1607常规文件（排除symlink缓存），不冒称整个冻结安装树未变。原r12v2 campaign保持只读、原reward不改。

不默认追加009重跑或116项全量；若要宣称总体分数改善或正式新协议成绩，需要另行独立测评，本次两单不能替代。

## 本次新署名独立验收已完成

w4:p2于2026-11-09T08:32:54Z完成009专属独立只读验收并通过，不沿用008或旧六单passed。父已读完整署名报告及机器记录；独立作者亲读八张原PNG、原XML、实际对象/原帧、完整动作与错误，并复核已有生命周期源码、20个release-source及APK hash、3793个登记文件和152技能身份。0登记文件变化/缺失。

- [所有者本次总报告](../../../timer-entry-ab-20261109T082047Z/report.md)
- [本次新署名独立验收](../../../timer-entry-ab-20261109T082047Z/independent-009-acceptance.md)
- [独立机器验收](../../../timer-entry-ab-20261109T082047Z/independent-009-acceptance.json)
- [所有者终态核对](../../../timer-entry-ab-20261109T082047Z/final-acceptance-checks.json)
- [设备/服务所有权释放](../../../timer-entry-ab-20261109T082047Z/ownership-release.json)

**009本次诊断闭环：失败输入、原判分分支、通用生命周期机制、现有生产修复真实覆盖、独立验收与清理均有本项证据；历史原分数和唯一历史根因保持原状。** 不增加新规则、等待、任务动作或实验。
