# 原008 ClockStopWatchRunning：固定两单诊断

## 结论

A中秒表确实继续计时，但原官方 running 谓词实际接到空列表，按原分支返回 false、reward 0.0。B中秒表继续计时，原谓词实际接到 Pause 和 Lap，返回 true、reward 1.0。不是把已停止谓词、离线回放或事后截图分析替代为官方判分。

本目录是全新开发诊断，不是正式116项campaign，也不是正式r14资格或分数；formalScore 保持 null。A/B固定顺序、各一次，没有按分数追加实验或重跑。历史008当时的判分forest未保存，本次不能补造或改写其输入、结果或归因。

| 实测项 | A：ClockRunningOriginalP0 | B：ClockRunningPatchedP1 |
|---|---|---|
| helper APK SHA256前缀 | 97a56a544e44（原冻结APK副本） | 0987ded41c12（生产修复APK） |
| 实际转发请求中的 disableSuppressAccessibilityService | 缺省；已捕获原请求 | alwaysMatch 显式 true；已捕获原请求 |
| 官方原始 reward | 0.0 | 1.0 |
| 官方逻辑 get_state 调用 | 1 | 1 |
| 原谓词实参列表对象ID | 5026249856 | 5086192960 |
| 实际选中 recv | 2118 | 1414 |
| 选中forest windows / nodes / UI elements | 0 / 0 / 0 | 2 / 27 / 17 |
| 原 line40 Pause / Lap | false / false | true / true |
| 执行动作 / 上限 | 4 / 10 | 4 / 10 |
| quit后两张原生截图计时 | 2:26.49 → 2:27.35 | 1:16.52 → 1:17.35 |
| 同次官方state.pixels计时 | 2:31.35 | 1:22.79 |

## 原契约与实际执行

- 沿用原008任务：`Run the stopwatch.`，seed `3429360255`，参数SHA256 `fe15fe1739bca1ce130f387e2e84d273c4a55e5403a5c174c7a2ec65119afaf9`。
- 两单均为 `github-copilot/gpt-5.6-sol`；真实Agent prompt与历史实际prompt只差动态代理端口。模板SHA256 `463118879bbe14a14abfd987920f115fff29f128db4566dc282e75dc0aa906aa`。
- 两单Agent工作区152文件身份均匹配原技能资产SHA256 `0ff33bb8ee50c160d87842ed11324e557f6fe5fc81c8e4fe06230a4d7bf792b8`。当前项目技能文件另做终态复核，未变。
- 10步预算、720秒业务、180秒清理、120秒恢复、10秒终止宽限、1330秒episode、910秒force，以及原会话/重试策略均核对保留。没有通过延长预算或重试拿到B结果。
- A的能力缺省仅在明示的诊断身份内例外放行；没有把它冒充生产r14门禁通过。两臂分别新做准备，准备后均禁用并停止本任务自有forwarder，确认PID空，再进入单项初始化；不带入上单worker或receiver。
- 原官方 `clock.py` 未改，SHA256 `b71344f13576f6b848a6c34dc4286962e94ec228e9643a3bdfc11b299265a65c`。原 `_is_stopwatch_running` 检查DeskClock Activity与精确Pause/Lap content_description，实际返回分支均为line40。
- 每单 `unit-audit.json` 的24项身份、输入、原分数、只读观察及清理核对均通过；原始结果不被审计输出覆盖。

## A的首个可观察断点与后续恢复边界

`forest-trace.json` 最后非空为recv447，首空为recv448；此后至记录结束共1671条均空。首空早于session创建响应约0.436695秒。系统采样显示：session-request时Bound/PID11137；session-created与quit-request时Enabled仍保留而Bound为空。

quit/rebinding阶段的原生日志另记录PID11137/Thread3的空Context异常：`AccessibilityForwarder._init_$lambda`，`kt:51`，位于 `device-logcat.txt:12164–12176`。这是比首次空树更晚的事件，不能把这个晚发异常冒充首空的唯一原因。

原判分实际选中空recv2118，真实 `state.ui_elements` 与原谓词实参是同一个列表对象。两个state-return trace事件属于同一逻辑get_state、同一state/forest/list，并非两次判分获取。

原scorer return位于host Unix约 `1794211579.99598`。postrun采样始于 `1794211580.97579`，此时已Bound新PID13131。**恢复快照观察在判分后，不等于绑定转变必在判分后；精确判分瞬间的Bound状态没有被该异步快照直接测量。** 不声称“从未恢复”或“不会恢复”。后时点Bound不能证明更早选中的判分输入健康；确定事实仍是原谓词接到空recv2118并判零。

详细边界分别保存在 `original-A-first-loss-timeline.json` 与 `original-A-binding-chronology.json`。

## B的实际健康判分输入

选中recv1414的forest SHA256为 `06442ba3b97c22192b00f8acee3a7f99a7b62b13806e60373cc6ab17a3eb1c06`。保存的protobuf字节、接收对象、同次state.forest、state.ui_elements、原谓词实参的身份与值均核对一致。17个UI elements中原谓词实际找到Pause和Lap，原分数1.0直接来自该次原scorer返回。

B记录1420条receive，均非空，sender instance均为 `14073:1`。session-request、created、quit-request、quit-response、postrun五个系统采样点均Bound同PID14073。原生日志可见UiAutomation初始化记录flags=1；初始化日志不是对最终有效flags数值的完整测量。

## 仍存在的延迟与因果限制

- A保留三次timed_out/alive，约30/20/60秒；B保留两次timed_out/alive，约30/15秒，以及一次约8秒failed/alive。B判分输入恢复不证明Appium idle等待或全部Runtime延迟已修复。
- A/B同时改变helper APK/构建栈与无障碍抑制能力；两单不能隔离二者各自的净贡献，也不能证明长期稳定性。
- 原Agent prompt、技能与预算一致，不代表模型的动态代码、各次调用时限和执行时序逐调用相同；此次A不是历史008调用时间线的逐项复刻。
- 只读观察有实测开销：A pre-quit 11.036873秒、post-quit 1.155450秒；B分别10.991821秒、1.069070秒。观察器不新建session、不quit Agent session、不执行业务UI动作，但不能宣称无观察时序等价。
- A/B逻辑state返回时的host receive age约5.297秒/0.108秒，**不是设备forest生成age**。设备epoch与host epoch不同，不能直接相减；A时间线单独保存了时钟采样区间。

## 清理、恢复与历史不可变性

- 两单Agent均真实quit返回，各自session确认absent；每单create/delete各1，active/pending-create/pending-request/unknown-creation均0。task teardown completed，environment closed。
- 保留原嵌套verification.status=`unknown`和其中quitReturned=false：它对应独立验证时会话已经不存在，不冒充该验证器执行了quit。外层真实Agent quitReturned=true、verificationStatus=absent及逐会话无错误证据分别保存。
- 子进程退出后，Agent workspace及其TemporaryDirectory父目录均实测不存在；保留退出前原receipt，另写 `workspace-post-exit-absence.json` 与 `workspace-parent-post-exit-absence.json`。
- 生产helper完整SHA256 `0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`已恢复，最终只读采样实测正常Bound、Binding空、Crashed空。matrix末尾的Binding过渡态不被冒充完成证明。
- 最终boot ID未变；enabled_accessibility_services及accessibility_enabled与前置逐字相同；未重启共享模拟器或Appium。既有runner会话查询结果为空，UiAutomator2进程为空。
- 直接GET `/sessions`返回404，已保留为不支持的检查；没有把404当作无会话证据，改用仓库既有权威查询。
- 登记的2186个历史文件全部重新计算SHA256，共14,434,241,098字节，无缺失或变更；当前152个技能资产文件同样无变更。范围仅为登记清单，不泛称所有仓库文件或共享活动日志都不变。

## 证据入口

- 汇总与契约：`summary.json`、`diagnostic-contract.json`、`clock-matrix/matrix-protocol.json`。
- 两单原始证据：各目录的 `episode/result.json`、`actual-agent-prompt.json`、`agent-workspace-skill-identity.json`、`unit-audit.json`、`forest-trace.json`、`system-samples.json`、`device-logcat.txt`、`appium-run.log`。
- 原判分与视觉：各 `clock-probe/evaluator-calls.json`、`evaluator-000/state-00/{forest.pb,ui-elements.json,pixels.png}`、`pre-quit-000/pixels.png`、`post-quit-001/{pixels.png,pixels-later.png}`。
- 恢复与范围：`final-native-restoration.json`、`historical-immutability-audit.json`、`registered-historical-{baseline,after}.json`。
- 独立验收由另一个只读会话w4:p2负责；本执行者报告不冒充其独立结论。
