# ClockStopWatchPausedVerify：第三个正常结束但官方失败任务

> 更新：以下原审查保留冻结 episode 007 的历史证据边界；本轮已完成新的四格受控复现，确认空官方输入及两个修复路径，见文末。新实验不替换或重判旧记录。

## 结论

**高度疑似与 BrowserDraw 属于同类的官方观察／判分输入不一致问题；不能据原记录直接断言官方 forest 为空。** Agent 留下的 Appium 观察满足暂停判据，实际调用官方安装函数进行离线回放也返回 true；原官方 reward 却为 0。历史缺少官方判分时实际使用的 forest、ui_elements 和 current_activity，根因尚不能进一步锁定。

与 CameraTakePhoto 不同：这里没有发现走错应用或把相反状态判断成成功。不能为了让它“多做点事”要求 Agent 先启动再暂停，因为官方任务明确以零时刻已暂停为前提。

## 原始执行轨迹

Campaign `amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z`；episode `007-ClockStopWatchPausedVerify/attempt-1`；目标 `Pause the stopwatch.`。

- 原官方 reward 0.0，evaluator 无异常，耗时 0.055 秒。
- 11 次 python_exec 全部 completed，kernel alive、非 error；3/10 个 UI 动作，非预算耗尽。
- UI 动作依次为打开应用抽屉、点击 Clock、点击 Stopwatch 标签。没有操作启动／暂停按钮。
- 第 5 次执行确认 `com.google.android.deskclock` / `com.android.deskclock.DeskClock`。
- 第 8 次执行点击 Stopwatch，并等待标签 selected=true。
- 第 9 次执行读到 Start 按钮，以及 3 个符合官方 Stopwatch 文本／content-description 条件的元素。
- 第 10 次执行间隔 1.2 秒读取两次：control=Start，time=00，hundredths=00，tabSelected=true；两次相同，stable=true。
- 第 11 次执行正常 quit；所属 session 创建／删除各 1，结果记录 absent。

最早偏离：**没有在原 Agent 轨迹中发现明确偏离。** 可定位的矛盾出现在 Agent 观察成功状态与后续官方判分结果之间。

## 官方判据与实际离线执行

当前评测安装 `android_world/task_evals/single/clock.py`：

- 177–185：任务前提明确为 stopwatch 已暂停于零时刻；只有 Verify 版本。
- 194–207：使用现有 `env.get_state().ui_elements` 和 ADB 获取的 current_activity 判分。
- 43–63：activity 含 DeskClock、存在 content_description == Start、至少 2 个元素的 content_description 或 text == Stopwatch。

将原第 9 次执行保存的 Appium 元素字段映射到官方 UIElement，并使用原第 5 次执行的 activity，真实调用安装中的 `_is_stopwatch_paused`：

| 条件 | 原 Appium 观察／回放 |
|---|---|
| activity 含 DeskClock | 是 |
| 存在 Start | 是 |
| Stopwatch 匹配元素数 | 3 |
| 实际暂停谓词返回 | true |
| 原官方 reward | 0.0 |

离线进程退出码 0；代码、实际输入、输出和 stderr 留存在 [predicate-replay.json](predicate-replay.json)。**这不是原官方 forest 的回放，也不是新官方成绩。** Appium 观察和官方 forwarder 是不同数据源，采样时点也不同；不能用此给历史任务补分。

## 时序与缺失证据

Appium master log `evidence/screenshot-video-controls-20261106T231029Z/appium.log`：

- 59736–59737：Clock 点击 200。
- 60956–60957：Stopwatch 标签点击 200。
- 61722–61726：quit 请求 06:42:07.215Z，响应 06:42:07.391Z，HTTP 200。
- 原 result.json：官方 evaluate 从 06:42:12.162497Z 开始，约在 quit 响应 4.77 秒后（startedAtUnix=1794033732.162497）。

没有保存判分当次的 ui_elements 或 current_activity，也没有本任务的 forest 来源序号。可能分支包括：官方收到空树、收到非空但缺少相关节点的树、拿到旧／过渡状态，或判分时前台 activity 改变。**这些是待检验分支，不是已确认事实。** 无法仅凭共享同一 Appium server，把 BrowserDraw 新实验的全部机制直接移植到这个历史任务。

## 归属与下一步

- 当前分类：Harness／AndroidWorld 官方观察输入不一致疑点，Appium 共存／forwarder 生命周期为已知相关风险；未确认 AMKernel Runtime/MCP 故障。
- 不需要新增“强制先启动再暂停”的技能规则，不建议通过多点几次、额外等待或替换 evaluator 观察后端来碰运气。
- 应把该任务加入 BrowserDraw 修复的小范围回归：保留原任务、模型、预算与判据；被动保存原有 get_state 返回的 forest/ui_elements，以及原有 ADB current_activity 返回值，记录 Start 与 Stopwatch 元素匹配数量、来源序号／接收年龄。
- 若官方输入为空且同期界面正确，才可确认同类空 forest；若树非空但计数不足，应继续检查节点生成／转换／过渡状态；若 activity 不符，应追踪 quit 前后前台变化。
- 沿用显式保护 accessibility 服务的对照配置时，必须验证实际能力投递、绑定状态和官方原结果，不以 Appium 观察成功代替官方成功。

本次只读取冻结证据并运行离线官方谓词，没有设备操作、session 创建、生产代码／正式 skill 修改，原 campaign 未改动。没有原始截图可展示：本 episode 的 tool results 未包含 image content；本文依据保存的原 Appium 元素和状态返回，不冒充视觉证明。

## 跨会话受控复现：已确认本次失败机制与修复路径

现场由 AndroidWorld 评测会话 `w4:p1` 唯一操作；`w4:p2` 独立审查，本会话离线核对原结果、实际判分对象、原谓词分支及界面图片。固定四格各运行一次，不按结果重试；之后执行 BrowserDraw 和原成功日历任务回归。任务参数、模型、原 prompt、预算和官方 evaluator 保持原约定；这些是开发诊断，不是新正式 campaign 分数。

### 确定的复现根因

`ClockOriginalP0` 中，Appium 创建 session 期间 forwarder 从实际 Bound 变为仅 Enabled、未 Bound；原采集 worker 仍每约 100ms 发送空 forest。最后非空 recv472 后，从 recv473 起持续为空。quit 时又出现构造阶段访问未绑定 Context 的 NPE，杀死 forwarder 进程；重启后未恢复有效树入流。

官方原有 `get_state()` 实际选中 recv773：零窗口、零节点、空 ui_elements。保留对象与原暂停谓词参数列表身份一致，原 activity 是 DeskClock，原 if/elif 计数为 Start=false、Stopwatch=0，原 scorer 返回 0。三时点图片均显示零时刻暂停；prequit Appium 字段满足 Start=true、Stopwatch=3。因此本次失败确定属于 AndroidWorld 观察链／集成生命周期，不是 Agent 未暂停，也未发现 AMKernel Runtime/MCP 执行故障。

### 现场对照

P0 表示上游实际请求省略 `appium:disableSuppressAccessibilityService`；P1 为实际转发 true。

| helper APK | 能力 | 原判分树节点数 | UI 动作数 | 原官方 reward |
|---|---|---:|---:|---:|
| 原 APK | P0 | 0 | 3 | 0 |
| 原 APK | P1 | 25 | 3 | 1 |
| 修复 APK | P0 | 25 | 3 | 1 |
| 修复 APK | P1 | 25 | 4 | 1 |

两条修复路径都有链路证据，不只看 reward：

- **保护能力**：原 APK 不变，P1 保留采样时的实际绑定，850 条接收均非空，官方原谓词 true。
- **生命周期修复**：patched P0 仍被临时解绑，但旧 worker 取消并停止发送；同进程在 quit 后创建新 service 实例，沿用原 gRPC 配置，恢复有效发送。实际选中的 recv457 来自新实例 `31266:2/gen1/forestSeq30`。不是同实例 generation2，也不能把线程池复用 TID 当作旧 worker 残留。
- 实现方向：Harness 显式投递并核对保护能力；forwarder 在 `onServiceConnected()` 启动采集，在 `onUnbind()`／`onDestroy()` 取消 RPC、关闭通道并等待 worker 退出，禁止旧连接继续发布。不改 AMKernel 核心，不增加强制先启动再暂停规则，不用最近非空树回退掩盖问题。

### 回归、清理与证据边界

BrowserDraw 修复配置回归：17/20 动作，原官方 reward=1，原判分图像可见三色笔划及 Success!，原 evaluator 分支为 `exact_success_text_found`。原成功 `SimpleCalendarEventsOnDate` 回归：3/10 动作，原官方 reward=1；界面显示 October 24 的 Trivia Night，Agent 提交同名标题。

六次所属 session 均有缺席验证，pending 请求／创建和未知创建计数均为零；任务 teardown、environment close 完成。六份退出后补充记录确认 workspace 及临时父目录不存在，原清理记录未覆盖。最终生产 patched helper 已恢复实际 Bound，安装身份匹配，UiA2 instrumentation 已退出；共享模拟器 boot ID 未变，未重启共享模拟器或 Appium。基线登记的 2186 个历史文件 hash 全同，零缺失；不对未登记路径作完整性声明。

每格仅一次；新旧 APK 构建栈有差异，patched P1 多一次搜索导航而非秒表启动／暂停动作，预后观察也引入诊断开销。因此不宣称纯单一代码改动的统计效应、全任务稳定性或历史精确时间窗复现。原 APK 无 sender instance/generation 元数据；Init 日志中的 flags=0 不是最终有效 flags 的实测，不能据保护能力回显补造 flags=1。

**冻结 episode 007 的唯一历史根因仍不能追溯确认：原判分输入未保存。已确定的是本轮同任务、同类失败的实际机制与受控修复效果。原 80/116 成绩和该 episode 的 reward=0 均保持原样。**

主要证据：

- [四格原输入、生命周期、清理与边界](../../../accessibility-coexistence-repair-20261109T064155Z/clock-factorial-conclusion.json)
- [首次丢树与 quit 崩溃时间线](../../../accessibility-coexistence-repair-20261109T064155Z/clock-first-loss-timeline.json)
- [BrowserDraw 回归](../../../accessibility-coexistence-repair-20261109T064155Z/browserdraw-regression-conclusion.json)
- [最终恢复验证](../../../accessibility-coexistence-repair-20261109T064155Z/final-restoration-verification.json)
- [历史文件完整性核对](../../../accessibility-coexistence-repair-20261109T064155Z/historical-integrity-after.json)
- [独立最终验收与完整性覆盖边界](../../../accessibility-coexistence-repair-20261109T064155Z/independent-final-report.md)

独立最终验收已通过本次固定六单开发诊断。独立重算的 2186 条完整性基线具体覆盖 2185 个 campaign 文件和一个缓存原 APK，不代表全冻结安装树；完整性结论限于这些登记路径。清理中的原嵌套 `verification.status=unknown` 未覆盖；逐 session 的 absentVerified、已返回 quit 和退出后目录缺席是本次清理依据。最终恢复快照证明 Bound 与安装身份，不额外宣称恢复后另做过 SendForest 或判分健康验证。
