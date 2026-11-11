# 009 ClockTimerEntry：独立验收、根因与修复结论

署名：**w4:p2 独立只读验收助手**。审查时间：**2026-11-09T08:32:54Z**（Unix 1794213174.033993）。运行所有者w4:p1，父会话w3:p1。

本报告专属于 `timer-entry-ab-20261109T082047Z`，不沿用008或旧六单passed。机器可读完整记录：`independent-009-acceptance.json`。

## 最终结论与实际进度

**验收通过。固定两单已各一次完成、原证据核对完成、生产恢复及清理核对完成。已有通用共存/lifecycle修复组合覆盖本次009观察到的故障，无需新增fix、等待、判据特例或benchmark专用规则。**

**本次A判零的确定根因是原官方观察链实际交付空forest/UIElement，而非数字错误、误按Start、activity不符或MCP超时。** 机制证据进一步显示：Appium创建期间原helper解绑；quit重绑后同PID旧/新native采集线程并行发树，空与非空消息交错；原选择逻辑最终选了空recv1132，原timer谓词按该空输入正确返回false。不能把每个recv逐条指派给某TID。

| 本次单元 | 原scorer / 保存reward | 动作/预算 | 官方选中recv | 窗/节点/UIElement | 原timer返回 |
|---|---:|---:|---:|---:|---|
| TimerEntryOriginalP0：原APK、cap实际省略 | 0.0 / 0.0 | 7/10 | 1132 | 0 / 0 / 0 | line100 false |
| TimerEntryPatchedP1：生产APK、cap实际true | 1.0 / 1.0 | 7/10 | 998 | 2 / 36 / 27 | line98 true |

矩阵completed、error=null，按A→B恰好各一次；两个新宿主子进程77506/78262均退出0，两单result.error/invalidReason均null。没有按reward重跑、增session或增任务。formalScore=null。

## 原009取证：只认r12v2

原源为 `campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/009-ClockTimerEntry/attempt-1/`。独立从其raw JSONL重提全部11次Python代码及响应，并与父提取逐项核对，三个原文件SHA吻合。**11次全部completed/alive，没有原调用超时；不能移用008延迟结论，也不能拿r11的6动作/7cells代替。**

原动作7/10：Search、Clock、Timer、数字1/6/3/5。原exec9回传exact `00h 16m 35s` 及 `0 hours, 16 minutes, 35 seconds`；exec10 setupVisible=true、Timer selected、Start enabled；exec11 quit返回。原记录支持输入正确且未启动，但历史官方实际输入未保留，故原历史reward0的唯一原因不能追溯证明、不能改判。

## 本次任务、模型、全文prompt和技能身份

- 任务是 `ClockTimerEntry`、index9、complexity1、seed1172248264、hours0/minutes16/seconds35；paramsSha256=`3c6dc22a2339a8e10eab5472bd837b52efb43b0125410cd5522c8ce88a29192b`。两单result.task与原r12v2逐字段一致。
- 原精确goal：`Create a timer with 0 hours, 16 minutes, and 35 seconds. Do not start the timer.`
- 新raw assistant事件直接确认两单实际provider/model是 `github-copilot/gpt-5.6-sol`，不是只看启动配置或人工重放。
- 独立遍历历史raw，唯一不同的完整目标prompt最早在第8行，SHA=`50df765d5359f644d0a8224a4f4048d225684c078932e7dc30225dd156e40081`。两单实际传入prompt全文只归一化一个动态loopback proxy端口后逐字相同；真实全文/hash在各单 `actual-agent-prompt.json`。
- 重新独立读取当前152个技能资产并逐文件对照，aggregate=`0ff33bb8ee50c160d87842ed11324e557f6fe5fc81c8e4fe06230a4d7bf792b8`，与原冻结身份一致；两单workspace技能也各152文件匹配，结束后fresh hash未变。未安装或替换指导。
- 两变体manifest的原task row及model/promptTemplate/timeBudget/stepBudget/retry/session等14项协议字段逐项一致。business720秒、cleanup180秒、recovery120秒、episode1330秒；MCP120000ms、session创建90秒、单episode最多1session；fullTaskRetryLimit0、invalidRetryLimit1。实际两单无任务重试。
- 六个诊断脚本当前hash与launch protocol、两单executed identity一致；原安装clock.py全文件SHA为 `b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c`。各单命令和执行代码身份原件均保留。

## 数字正确且未Start：独立业务核对

已亲读A/B各四张原PNG：pre-quit Appium、post-quit native、later native及原官方state.pixels。**八张均是00h16m35s设置输入盘及Start/play控件，不是倒计时运行页。**

已解析两单pre-quit原Appium `source.xml`：`timer_setup_time.text` 精确为 `00h 16m 35s`、description精确为 `0 hours, 16 minutes, 35 seconds`、displayed=true；fab为Start且enabled=true，Timer tab selected=true。完整原模型代码与proxy ledger相互核对，两单真实业务动作均为一次抽屉滑动、Clock、Timer、四个数字；没有Start点击。不能仅以官方reward代替这个业务约束。

B有12次Python调用，其中9 completed、3 failed/alive，无timed_out：

| B execution | 原失败 | 实际副作用和后续 |
|---|---|---|
| 3 | ModuleNotFoundError：appium.webdriver.common.actions不存在 | import即失败，未执行该cell的手势 |
| 4 | TypeError：move_to_location不接受duration参数 | perform前失败，未发出该cell手势 |
| 5 | NameError：WebDriverWait未定义 | 前面的driver.swipe已实际成功；随后只读复核，没有重复滑动 |

该表依据原代码、原异常及唯一actions请求/总7动作交叉核对。failed不等于UI动作未发生；这些是本次模型代码错误且自行恢复，不是被隐藏的successful调用，也没有被当作新的AMKernel/生产缺陷。A共8次调用，全部completed/alive；原历史009则是11次全completed。预算未变不意味着代码或调用数相同，不新增固定调用计数规则。

## 原timer谓词、真实对象与原reward闭环

已亲读原 `_is_timer_set:66–100` 和 `ClockTimerEntry.is_successful:143–160`：要求activity包含DeskClock，且某个原UIElement.text精确等于 `00h 16m 35s`，**或**其description精确等于 `0 hours, 16 minutes, 35 seconds`。不是running的Pause/Lap，也不是paused的Start/count。

已亲读本实验observer：只用sys.settrace记录原frame/参数/return，保持原state/list/元素强引用，原scorer只调用一次并原样返回。没有新get_state、树替换、过滤空消息、重放predicate或按Appium树补判。两个wrapper层的get_state返回记录指向同一原state，去重后各一份逻辑判分输入。

- **A：** 原state ID5019889680，predicate与其ui_elements是同一列表ID5019801600，确为空；原activity=`com.google.android.deskclock/com.android.deskclock.DeskClock`，kwargs确为0/16/35，frame内text_format和content_desc_format均正确。空列表不进入比较，第100行false→原scorer0.0→保存0.0。实际选recv1132/drain8，PB为0字节，SHA=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，原接收/选择对象identity无错配。
- **B：** state ID5052357008，实际列表与predicate同ID5052825344。原27个UIElement中索引2就是timer_setup_time，element ID5053206544与原line95/98事件及原参数元素ID相同；text和description均exact。**本次实际由line95文本相等短路命中，不能说该元素还执行了line96比较。** 第98行true→原scorer1.0→保存1.0。原有效recv998的PB SHA=`f259286df2d17cbe859716c23b962963b5673bbaf9f8e0ae20b8a30e9f9f0c88`，与实际trace一致；sender=`20200:1/gen1/seq998`。

两单原trace/scorer-trace errors为空。核心原件在各单 `clock-probe/evaluator-calls.json`、`clock-probe/evaluator-000/state-00/{pixels.png,forest.pb,ui-elements.json}`、`forest-trace.json`。

## 本次A根因时序：不能复制008

1. 首失前最后非空是recv480，首空481；首空在Appium创建响应前约0.530秒。global最后非空1142不是首失前last good。
2. 创建前helper Bound，创建后仍Enabled但不Bound，UiAutomation存在。quit-response实际accessibility命令host1794212788.934195–1794212788.9540842已经观察到**同PID17373恢复Bound**，早于scorer返回1794212792.954365；不是008的只在事后才观察到Bound。
3. quit后recv1054起已有非空；采样整体完成1794212789.076607至scorer前，74条是**38空、36非空**，不是74空或全程永久空。紧邻的1131非空、1132空、1133非空，最终原选择确实取1132。
4. 已亲读A native日志10829–10864：同PID17373，旧TID17399持续tree-send，新TID19213同时processNodes/tree-send，约0.1秒周期交错。与原新旧采集竞争的生命周期缺陷相符；原sender metadata为空，不能给1132编造TID归属。
5. 本次A当前日志未见forwarder FATAL/NPE，不移用008的constructor空Context崩溃。A原state返回时消息host receive-age约0.01789999秒，稍后保存describe为0.224239秒——是新近收到的空输入，不是008的5.297秒陈旧消息；两者都不是设备生成age。

这组证据说明“已经Bound”与“原collector输出健康”不能等同；本次失败是空/非空竞争流中的实际空输入被原逻辑选中，不是调整timer判据或补等待能被现有证据正当化的问题。

## 已有fix：独立代码审查与本项真实验证

本审查亲读 `forwarder/src/AccessibilityForwarder.kt` 的连接/停止/发送路径：onServiceConnected创建连接唯一worker、重复回调不加worker；onUnbind/onDestroy清空current connection、cancel job/RPC、close channel并join；stub拒绝过期/不活跃connection，发送前ensureActive。**不按timer/任务文本特判，不过滤真实空forest。** 20个release-source hash及本地APK字节重新计算均与发布provenance一致。

A实际上游POST与返回cap均省略目标字段，部署原APK SHA=`97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a`；B实际上游POST和返回cap确认true，部署生产SHA=`0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`，不是只看默认值或模型原请求。B接收1003条全部非空，来自同一 `20200:1/gen1`，本项原timer判据及未Start业务约束均实际通过。

因此**已有通用共存配置+连接生命周期修复组合覆盖本次009，不需要新的生产修复**。这不是单独隔离lifecycle或cap效果的试验：两臂同时改变APK/build-stack和cap；也不是全部模型API使用错误都已消除的声明。

本次native字段必须原样保留：**A日志5171 Init flags=0，B日志4837也Init flags=0**。不改写B为008的1；actual cap=true、五点Bound样本、有效recv各自是不同证据，不能相互代替或由Init日志单独推出最终有效flags数值。

## 清理、恢复与限定完整性

逐单核对session创建/删除各1，active/pending create/pending request/unknown creation均0，Agent quit确返回、逐session absentVerified=true、verificationStatus=absent；环境closed、task teardown completed。原嵌套verification.status=unknown保留，不靠改写字段证明清理。

原 `workspace-post-exit-absence.json` 未覆盖；额外各一份 `workspace-parent-post-exit-absence.json` 明确在对应子进程退出后观察workspace及临时父目录皆absent。已亲读所有者 `final-native-restoration.json` 原stdout：生产APK SHA正确，Bound有helper、Binding/Crashed空；权威sessionHashes=[]、UiA2及active instrumentation空。bootID/enabledServices/accessibility_enabled与本次preflight原stdout逐字相同。只确认已保存恢复快照，不另查设备或新做健康实验。

**独立重新读取并SHA-256计算14,558,243,765字节，3793/3793登记路径，0改动、0缺失。** 范围是2185个campaign文件+1缓存原APK+1607个已完成008证据常规文件（排除其symlink缓存），不冒称整个冻结安装树/登记外路径未变；本次152技能资产另行前后fresh hash不变。

## 验收边界及交付

- 原r12v2 009历史官方输入缺失，当前复现不能证明它的唯一根因或改判原成绩。
- 当前A判零输入/原分支已确定，双采集线程和交错流支持通用生命周期机制；无逐消息native TID映射，不补造它。
- A/B各一次、组合干预；不声称组件效果已拆分或总体成功率。
- 只有pre-quit原Appium XML；quit后没有活session，按事先确认的原生双PNG/官方原state及完整ledger核对，不建新session、不跑uiautomator dump、不把PB派生XML冒充原件。pre/post额外观察与0.6秒截图分隔有已记录的时序开销，不冒称未加诊断原时序复刻。

本审查只读已落盘材料、图片及源码，做离线一致性与hash核对；零设备查询、零session、零构建、零生产源码修改、不覆盖所有者报告。结论和实际进度仅基于本次已观测数据。
