# 原r12v2 009 ClockTimerEntry：固定两单诊断

## 确定结论、root cause、怎么fix、当前状态

**本次A的零分不是数字输错、误按Start或MCP超时，而是无障碍采集链把空列表交给原官方timer谓词。旧helper解绑后旧tree发送线程仍存活；quit重绑后同进程出现第二个发送线程，非空树与空树交错，实际官方选择空recv1132，原line100返回false/reward0。**

**通用修复已在生产存在，本次B现场验证通过，无需再新增009专用修复：** Harness实际上游显式传递并确认 `appium:disableSuppressAccessibilityService=true`；生产forwarder把唯一worker/channel绑定到已连接service生命周期，在unbind/destroy停止旧worker。B实际原谓词使用有效recv998里的原timer元素，line98返回true/reward1。此次未修改AMKernel、技能、任务、evaluator、冻结资产或生产guard。

确定的判零直接原因与接收对象身份已经闭环；旧APK没有发送者instance/thread元数据，不能把某一条recv1132进一步伪称为已精确对应某个TID。A/B同时改变APK/build-stack和cap，不能把组合通过拆成单组件净贡献。

本报告只对本次固定A→B各一次诊断下结论。历史009原判分forest未保存；不回填、改判历史，也不把本次结果冒充正式campaign分数。formalScore=null。

## 原任务与实际两单

原目录为 `campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/009-ClockTimerEntry/attempt-1`，不是r11。

- 原goal：`Create a timer with 0 hours, 16 minutes, and 35 seconds. Do not start the timer.`
- params：hours0/minutes16/seconds35/seed1172248264；complexity1，预算10；SHA256 `3c6dc22a2339a8e10eab5472bd837b52efb43b0125410cd5522c8ce88a29192b`。
- 原历史11次Python调用均completed/alive；原exec9输入1/6/3/5并返回精确文本和description，exec10确认setup与Start，exec11成功quit；原动作7/10，reward0/error=null。这些原记录不支持把本项解释成超时。
- 两个新Agent均使用原 `github-copilot/gpt-5.6-sol`，真实全文prompt仅动态proxy端口不同。原全文SHA256 `50df765d5359f644d0a8224a4f4048d225684c078932e7dc30225dd156e40081`，最早原raw第8行。
- 原152技能文件身份 `0ff33bb8ee50c160d87842ed11324e557f6fe5fc81c8e4fe06230a4d7bf792b8`，两单工作区及最终当前项目均核对。
- 原720秒business、180秒cleanup、120秒recovery、10秒termination grace、1330秒episode等策略，以及retry与单session限制保留；无按reward重跑，无人工替代模型输入。

| 实测项 | A：TimerEntryOriginalP0 | B：TimerEntryPatchedP1 |
|---|---|---|
| 实际helper SHA256前缀 | 97a56a544e44，原APK独立副本 | 0987ded41c12，生产修复APK |
| 实际cap请求/响应 | 目标cap均省略 | 目标cap显式true并确认 |
| 原官方reward | 0.0 | 1.0 |
| 业务动作/预算 | 7/10 | 7/10 |
| 原逻辑get_state | 1 | 1 |
| 官方选中recv | 1132 | 998 |
| windows / nodes / UIElements | 0 / 0 / 0 | 2 / 36 / 27 |
| state.ui_elements与原实参同一列表ID | 5019801600 | 5052825344 |
| 原timer返回分支 | line100 false | line98 true |
| MCP执行 | 8 completed/alive | 9 completed、3 failed，均alive |
| timed_out调用 | 0 | 0 |
| pre-quit额外采集秒数 | 0.734711 | 0.667045 |
| post-quit额外采集秒数 | 0.914345 | 0.907552 |

## 原timer谓词与实际输入闭环

当前原 `clock.py` 未改，完整SHA256为 `b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c`。

使用的原谓词是 `_is_timer_set`：DeskClock Activity且某原元素text精确等于 `00h 16m 35s`，或content_description精确等于 `0 hours, 16 minutes, 35 seconds`。不是running Pause/Lap，也不是paused Start谓词。

每单仅按原scorer流程调用一次原get_state；两个wrapper层的返回事件属于同一个state对象。保存实际state/forest/list及每个元素对象ID、原kwargs、text_format/content_desc_format、原line95/96事件、原return及原float reward。未额外get_state、重放或更换原谓词。

- **A：** DeskClock通过；原kwargs确为0/16/35，原格式字符串正确；真实实参列表为空，同原state列表ID5019801600。原循环无元素，line100返回false，原scorer及result均0.0。选中forest.pb为0字节，SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。
- **B：** 第2号原列表元素、对象ID5053206544就是精确timer TextView。原trace在该元素上执行line95后直接到line98并返回true；OR短路，这个元素不需要再执行line96。原kwargs、两种格式字符串及完整元素参数均保留，不把离线比对当新判分。原forest.pb SHA256 `f259286df2d17cbe859716c23b962963b5673bbaf9f8e0ae20b8a30e9f9f0c88`，原scorer/result均1.0。

## 数字正确且未Start：不是只看reward

已逐单亲读真实模型所有Python代码/响应及各四张原PNG：pre-quit、post-quit、later、同次官方state.pixels。八张均显示 `00h 16m 35s` 的数字输入盘和三角Start控件，没有进入运行倒计时界面。

两单业务ledger均为一次抽屉滑动、点击Clock、点击Timer、点击数字1/6/3/5；没有点击Start、Pause、重设数字或为通过追加操作。pre-quit原Appium XML同时证明：

- `com.google.android.deskclock:id/timer_setup_time` text/description均精确正确，displayed=true；
- Start控件enabled=true，仍处于设置界面；
- 与post-quit双原生PNG和同次官方像素交叉一致。

B保留三个模型代码错误：exec3错误导入 `appium.webdriver.common.actions` 导致ModuleNotFoundError；exec4把duration传给不支持它的 `PointerActions.move_to_location` 导致TypeError；exec5实际swipe已成功，后面的WebDriverWait未定义导致NameError。模型随后只读查看已打开抽屉，继续Clock/Timer/数字并quit，没有重复已成功swipe。不是Harness任务重试、Kernel死亡或计时器Start。原响应及恢复完整保存在B的unit-audit与raw events，不用最终reward掩盖。

**原始格式边界已由父与独立作者事前确认：** 只有pre-quit Appium原XML；quit后没有可用原session XML。post-quit使用真实双PNG及同次官方原forest/PB/UIElements/像素，不建额外session、不运行uiautomator dump、不把派生XML伪装成原件。本次未生成派生XML。

## A的当前首失、恢复与双发送者证据

1. 首失前最后非空recv480；首空481，在session创建响应前约0.530099秒。创建前Bound；创建后原helper仍Enabled、PID17373仍在，但Bound为空，UiAutomation存在。recv481–1053连续573条空。
2. quit-response实际采样 `1794212788.848423–1794212789.076607` 已Bound同PID17373，**早于**原scorer return `1794212792.954365`；postrun同样Bound。不能套用008的晚时点恢复描述。
3. recv1054已恢复非空，随后非空/空交错；Bound采样结束至scorer前74条中38空、36非空。不是“从未恢复”，也不是“从首空以后全空”。最后的官方选择确为空recv1132。
4. 本次原生日志直接看到两个并发tree发送者：初始旧TID17399持续发送；重绑后TID19213在同PID处理windows并发送。设备epoch1697384152–4156窗口内：旧TID有39次tree-send而0次processNodes日志；新TID有38次tree-send、76次processNodes日志。原文行10839起可核；完整有界提取见 `original-A-concurrent-workers.json`。这支持旧collector未随解绑停止、重绑后新旧发送竞争的生命周期问题，而非单看Bound即可认定采集健康。
5. 此次A保存日志定向扫描没有forwarder FATAL/NPE，不能写成008的构造器NPE。此次native Init记录A0/B0；不能照抄008的A0/B1，也不能把初始化日志当最终有效flags数值测量。实际cap、Bound及非空消息分别留证。
6. 选中消息在原state返回时的host receive age约0.017900秒，之后保存describe约0.224239秒；B相应为0.083079秒与0.296011秒。不是设备生成age，也不是008的旧空消息年龄。设备初始化曾调整时间，host/device epoch不直接相减。

完整时间线见 `original-A-first-loss-timeline.json`，其中global最后非空1142与首失前最后非空480分别命名，避免混淆。

## 通用fix与本次验证进度

当前生产实现已经处理这类观察链问题：

- `src/fsq_androidworld_eval/appium_proxy.py`：实际转发显式true并核对响应，矛盾/未确认时fail closed；诊断A省略只在本独立身份内例外，不放宽生产guard。
- `forwarder/src/AccessibilityForwarder.kt`：onServiceConnected后启动唯一worker；unbind/destroy取消RPC/worker、关闭所属channel并等待退出，重连按连接生命周期重新采集。真实空树不被过滤。
- 当前生产APK完整SHA256：`0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`。

B本次1003条接收全部非空、同sender `20200:1/gen1`；五个Appium生命周期采样点均Bound同PID20200。原业务未Start，原timer输入对象有效、原reward1.0，构成本项真实回归证明。

本次没有新发现必须另改AMKernel/技能才能解决的通用缺陷，没有新增生产修复或benchmark专用指导。B三个局部代码错误已由本次模型自身恢复；保留为已发生的不利结果，不扩大为未观测的Runtime故障。

## 清理、恢复、历史完整性

- 每单真实Agent quit返回；create/delete各1，active/pending create/pending request/unknown creation均0，逐session absent；task teardown completed、environment closed。
- 原嵌套verification.status=unknown保留，不改为closed；成功依据为真实quit及独立absent证据。
- 退出后Agent workspace及TemporaryDirectory父目录均实测缺席。原退出前receipt未覆盖，新增原post-exit及parent receipt分别保存。
- 矩阵恢复后另做只读确认：生产APK字节正确，实际Bound、Binding空/Crashed空；权威sessionHashes=[]、UiA2进程和active instrumentation空。bootID/enabledServices/accessibility_enabled与009 preflight原stdout逐字相同。未重启共享服务；设备所有权已交回父，会后无设备操作。
- 登记3793路径全部重新计算SHA256，共14,558,243,765字节，0变更、0缺失。范围为原2186（campaign2185+缓存原APK1）加008已完成证据1607常规文件，不含symlink缓存，不泛称整安装树未变。当前152技能文件及原clock.py另行核对未变。

## 证据入口与独立审查

- `summary.json`、`diagnostic-contract.json`、`original-call-provenance.json`、`launch-command.json`、两单 `executed-identity.json`：原任务、实际模型/prompt/技能、策略和六份本目录脚本实际hash。
- 各单 `episode/result.json`、`unit-audit.json`、`clock-probe/evaluator-calls.json`、`forest-trace.json`、`appium-run.log`：原frame、精确对象/参数、实际cap请求响应、原分数和原模型代码/响应。
- 各 `clock-probe/pre-quit-000/source.xml` 与四张原PNG、官方 `forest.pb/ui-elements.json`：业务与原输入证据。
- `final-native-restoration.json`、`historical-immutability-audit.json`、`registered-historical-{baseline,after}.json`：恢复及限定范围完整性。
- 父的 `parent-raw-consistency.json` 仅为离线一致性核对，不是新判分。独立作者w4:p2另行验收，本报告不代其署名或提前宣布通过。
