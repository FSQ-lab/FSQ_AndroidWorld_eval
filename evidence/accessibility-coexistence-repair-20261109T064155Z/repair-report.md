# Accessibility 共存与 forwarder 生命周期修复

## 结论与审计入口

永久修复已接入 Harness 14；固定六单开发诊断自然完成，不重跑、不补判、不改写历史成绩。独立验收通过本次诊断范围；`formalScore=null`，不是正式116项分数，也没有完成新协议全量门禁。

- 所有者最终审计：[final-audit.json](final-audit.json)，六单检查通过、`errors=[]`。
- 独立验收标识：**w4:p2**；[独立报告](independent-final-report.md)、[机器报告](independent-final-review.json)、[Clock细查](independent-clock-review.json)、[独立完整性复核](independent-integrity-review.json)。独立作者文件不由执行所有者覆盖。
- 文档：[forwarder/README.md](../../forwarder/README.md)，包含生命周期契约、构建依赖/命令、产物更新与证明边界。

## 实际永久修复

核心文件：

- `src/fsq_androidworld_eval/appium_proxy.py`：W3C候选规范化，实际转发显式 `appium:disableSuppressAccessibilityService=true`；矛盾请求拒绝，响应缺失/false确认时 fail closed，已创建session仍归属本任务以便回收；有界记录真实请求和响应。
- `src/fsq_androidworld_eval/{campaign,runner,preparation,rehearsal,scorer}.py`：把共存配置身份绑定到准备、manifest、episode、资格和审计。r12/r13历史读取/评分保留；r14仅允许替换明确命名的helper pin，不允许暗改其他冻结资产或任务参数。
- `src/fsq_androidworld_eval/environment.py`：使用仓库内固定hash/大小的生产helper，环境关闭后释放临时getter租约，不覆盖原缓存APK。
- `forwarder/src/AccessibilityForwarder.kt`：从 `onServiceConnected` 启动唯一连接worker；unbind/destroy取消worker/RPC、打断采集、关闭所属channel并等待退出；重连后新连接/实例重新采集。`onInterrupt` 不再关闭进程全局采集。真实空forest不被过滤。
- `forwarder/src/LogFlags.kt` 与 `FlagsBroadcastReceiver.kt`：保留可工作的默认gRPC传输和已有flag控制；初次本地构建的默认传输缺陷已保留在失败资格证据中，修正后资格见 `qualification-r2/`。不把该开发失误归到历史原APK。
- `forwarder/{build.gradle.kts,settings.gradle.kts,gradle.properties,schema-provenance.json,src/main/proto/}`：独立构建及未改语义的官方schema输入；源码/构建摘要见生产资产JSON。原许可证保存在 `forwarder/LICENSE`。
- `assets/fsq-accessibility-forwarder-lifecycle-v1.{apk,json}`：新资产及构建来源。生产APK SHA256为 `0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`；旧APK `97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a` 未覆盖。

对应Harness行为回归位于 `tests/`；native行为回归位于 `forwarder/src/*Test.kt`。受控代理、trace/probe和矩阵脚本保存在本证据目录用于复现诊断，不是放宽生产guard的兼容路径。

## 已执行验证

`regression-summary.json` 保存 Harness **619 passed**、native **33 tests / 0 failures / 0 errors**，以及实际构建/资格证据入口。不是只凭测试交付：以下六单真实运行均保留原官方判分。

P0为实际请求省略目标capability，P1为实际请求及响应确认true；使用相同受控代理。A臂仅诊断准入例外，不作为正式r14协议通过。

| 单元 | 原官方reward | 动作/预算 | 原判分选择recv | 节点 / elements |
|---|---:|---:|---:|---:|
| ClockOriginalP0 | 0.0 | 3/10 | 773 | 0 / 0 |
| ClockOriginalP1 | 1.0 | 3/10 | 846 | 25 / 15 |
| ClockPatchedP0 | 1.0 | 3/10 | 457 | 25 / 15 |
| ClockPatchedP1 | 1.0 | 4/10 | 1089 | 25 / 15 |
| BrowserDrawPatchedP1 | 1.0 | 17/20 | 1776 | 54 / 43 |
| SimpleCalendarEventsOnDatePatchedP1 | 1.0 | 3/10 | 不适用：答案型 | 不冒造判分forest |

六单 `error/invalidReason=null`、进程退出0、Agent quit返回；每单创建/删除各1，active/pending/unknown creation为0，逐session缺席已验证，teardown/环境关闭完成。六个宿主子进程不同；每单先停用并停止所属forwarder到无PID，重新建立官方receiver且接收序号从1开始。六份 `workspace-post-exit-absence.json` 另证with退出后workspace及临时父目录均不存在；未覆盖原with内部 `exists=true` 记录。

原嵌套 `verification.status=unknown` 原样保留。清理判断依据是已返回quit、逐session `absentVerified=true` 和 `verificationStatus=absent`，不是把该原字段改成closed。

## 因果闭环与限制

[clock-factorial-conclusion.json](clock-factorial-conclusion.json) 保存原state/list身份、实际predicate分支、sender和12张实际读取PNG的核对。

- OriginalP0本次判零由空官方输入触发：DeskClock activity通过，原谓词 `Start=false/count=0` 在63行返回false；三时点UI仍是零时刻暂停/Start。最后非空recv472后首空473出现在session创建响应前0.520942秒，不能说quit才首次丢树。后续构造worker空Context崩溃是另一故障点；详见 [clock-first-loss-timeline.json](clock-first-loss-timeline.json)。
- OriginalP1同原APK保留Bound及850份非空接收，原谓词true，支持这些样本中的能力保护路径。
- PatchedP0明确停止—重连：`31266:1/gen1` unbind后worker停止；host接收间隔43.740073秒，而不是持续发送空树。quit后同PID新实例 `31266:2/gen1` 恢复，实际选中recv457/该sender序号30。不是同实例generation2；线程池复用TID不表示旧worker存活。
- PatchedP1为单实例持续采集路径；四动作来自启动器Search、输入Clock、点Clock、点Stopwatch，不包含Start/Pause操作。其他三格使用抽屉导航，动作和耗时并不完全相同。
- BrowserDraw原 `browser.py` 第108行返回1.0；选中Chrome的真实Success!，官方PNG可见三色笔划和成功文本，详见 [browserdraw-regression-conclusion.json](browserdraw-regression-conclusion.json)。
- Calendar原business submission的 `answer` 和 `parsedValue.taskOutcome` 均为 `Trivia Night`，pre/post图与原日期/标题/时间一致，官方reward1.0；详见 [calendar-regression-conclusion.json](calendar-regression-conclusion.json)。它没有同类forest评分输入，不补造快照。

每格仅一次、固定顺序；APK对比还包含构建栈、签名/targetSDK等差别，不能隔离跨构建的纯生命周期效应大小。诊断前后截图/查询增加延迟，不是历史时序复现。原APK无sender实例元数据，host接收年龄也不是设备生成树年龄。

原native `Init ... flags=0` 保留；已有dumpsys未输出最终数值flags。[Android13 AOSP代码](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android13-release/core/java/android/app/UiAutomation.java)中callback日志可能先于连接调用返回后的 `mFlags=flags` 赋值，故该初始化日志不必意味着最终flags0，但这只是源码层面的解释可能，不是实测最终flags1，也不证明另一次重连。实际Bound及非空流与数值flags证明分开记录。

## 恢复、历史完整性与审查范围

[final-restoration-verification.json](final-restoration-verification.json) 是矩阵结束后的一次只读核验：生产APK hash匹配，helper实际Bound、Binding空，UiA2 server/test PID及adb forwards空，boot ID与preflight一致。较早matrix即时记录仍处于Binding中，未被覆盖；共享模拟器/Appium未停止或重启。该核验没有再建session或证明恢复后新增SendForest/评分路径，设备所有权已交回父会话，不再操作。

所有者及独立作者均逐文件对比基线：**2186条、0改动、0缺失**。范围严格为2185个campaign文件加1个原缓存APK，**不是完整冻结安装树证明**。旧正式成绩及历史007分类保持原样；缺失的历史判分输入未被追补为确定根因。

已完成的独立证据：w4:p2本次因果/回归验收及父会话转述的proxy准入静态复核，后者锚定 `controlled_proxy.py` SHA256 `5a24fd70061ffc156a8204a11c1c7c6c49b0c7cb51a72c07468f52ebb4502f9d`。未记录额外整仓生产代码独立reviewer作业完成标识；不把实现子代理 `CoexistenceConfig` / `ForwarderLifecycle` 冒充独立审查。

没有新增必须排查的本次六单阻断项。最终flags数值、基线外安装树、历史唯一根因和长campaign稳定性仍未证明。未启动其他实验，也未重建r14全116项预演/12项校准或正式全量campaign。
