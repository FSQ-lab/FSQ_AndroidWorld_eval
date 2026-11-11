# 最终独立验收报告

## 验收结论

**通过本次固定六单开发诊断的验收；不接受“历史唯一根因已证明”“跨构建纯生命周期效果已隔离”或“全冻结安装完整性已证明”的扩大结论。**

六单矩阵自然 completed，error=null；未因 reward 重跑。本审查只读已落盘材料，没有设备查询、构建、安装、额外实验、重新判分或历史改写。正式 campaign 分数保持原样，本实验 formalScore=null。

机器可读完整记录：`independent-final-review.json`；四格细查：`independent-clock-review.json`；独立 hash 对比：`independent-integrity-review.json`。

## 六单原结果与计数

P0 为目标 capability 省略，P1 为实际转发给 Appium 且响应确认 `appium:disableSuppressAccessibilityService=true`。采用相同受控代理；不是替换官方观察后端或判据。

| 单元 | 保存的官方 reward | 实际动作/预算 | 官方选中 recv | 节点 / ui_elements |
|---|---:|---:|---:|---:|
| ClockOriginalP0 | 0.0 | 3/10 | 773 | 0 / 0 |
| ClockOriginalP1 | 1.0 | 3/10 | 846 | 25 / 15 |
| ClockPatchedP0 | 1.0 | 3/10 | 457 | 25 / 15 |
| ClockPatchedP1 | 1.0 | 4/10 | 1089 | 25 / 15 |
| BrowserDrawPatchedP1 | 1.0 | 17/20 | 1776 | 54 / 43 |
| SimpleCalendarEventsOnDatePatchedP1 | 1.0 | 3/10 | 不适用：答案型判分 | 不冒造判分状态 |

ClockPatchedP1 第四个动作来自 Search→输入 Clock→点 Clock→点 Stopwatch；其余三格从应用抽屉进入，均没有 Start/Pause 操作。动作与观察时序不完全匹配，计数不能外推为固定技能阈值或效率定律。

## 四格复现和机制：能确认什么

1. **OriginalP0 本次失败分支已闭环。** 官方原 `get_state`/原 predicate 实际使用同一份空树及空 ui_elements；DeskClock activity 门通过，`start_present=false`、`n_stopwatch=0`，原 predicate 第63行返回 false，原 scorer 0.0 与保存 reward 0.0 一致。原截图仍为秒表暂停零值。失树从 session 创建阶段开始，不是先到 quit 才丢；后续构造 worker NPE 是另一个故障点，不得混成首次丢树原因。
2. **能力保护路径得到同原 APK 对照支持。** OriginalP1 使用同一原 APK，目标 capability 实际请求/响应均为 true；forwarder 在 UiAutomation 并存时保持 Bound，850 次接收均非空，官方原 predicate true。OriginalP0 省略该能力后出现 unbound 和301次空树接收。这支持这些样本中的 capability 干预效果，不是总体成功率估计。
3. **PatchedP0 停止—重连恢复是直接日志链，不是 reward 倒推。** PID31266 的 `31266:1/gen1` 在 device epoch4085.469记 Worker stopped、4085.472记 Disconnected/unbind；旧实例 host recv1–427 后停止，接收间隔43.740073秒。quit 后同 PID 新实例 `31266:2/gen1` 于 device epoch4129.087 Connected，复用 `10.0.2.2:61730`，recv428–462恢复35份非空树；官方实际选 recv457、sender新实例、sender sequence30。**不是同实例 generation2，也不能因 TID31303 复用说旧 worker 一直活着。** 原日志使用完整 epoch 见 JSON；此处简写仅用于定位，不能与 host 时间直接相减。
4. **PatchedP1 是另一条路径。** `1868:1/gen1` 单实例1094次非空接收，官方选1089；没有把 stop/reconnect 路径与并存持续采集路径混称。

## BrowserDraw 回归闭环

原参数：`browser_task_seed=461184702`，`seed=1466251684`，paramsSha256=`899d6f67cdd687dc3d29a6918010a3ba15348ec5e9caa772f4f4f2cdffb03956`。

已直接读原 `evaluator-0/pixels.png` 及 pre/post-quit PNG：Chrome 页面显示三色笔划和 Success!。官方原 evaluator **第108行** `exact_success_text_found` 返回1.0，保存 reward 同为1.0；不是按 Appium 树补判。

原判分仅一次逻辑 get_state，实际选 recv1776，2窗54节点、43个 ui_elements；Chrome 的 `Success!` 索引10。原 forest.pb 的 SHA-256 与原 trace 一致：`f66beabdd7738c2a9be919f1f7dfe1ed56bec2a3351bd4dbbbad3ec27f4a73ef`。sender=`4231:1/gen1/seq1776`。原 error/invalid=null、trace errors=[]、进程退出0。

证据根：`clock-matrix/BrowserDrawPatchedP1/`，核心为 `episode/result.json`、`evaluator-calls.json`、`evaluator-0/{pixels.png,forest.pb,ui-elements.json}`、`forest-trace.json`、`clock-probe/captures.json`、`appium-run.log`。所有者结论：`browserdraw-regression-conclusion.json`。

## Calendar：参数—提交—界面—官方结果

原参数：date=`October 24 2023`、title=`Trivia Night`、time=`11:00am`、duration=`25 minutes`、seed=`1569884782`；paramsSha256=`35497446bdb86198a6893a5d4f8f62a987bf1f2bf6f4615b00dd405b3cf0bc91`。

原任务只要求标题。原 `episode/raw-private/business-submission.json` 的 `answer` 以及最终 JSON 的 `taskOutcome` 均为 **Trivia Night**。已亲读原 pre/post-quit PNG，均显示 October 24 (Tue)、Trivia Night、11:00–11:25，与原参数和答案一致。原保存 officialReward=1.0，3动作，error/invalid=null、trace errors=[]、进程退出0。

这是答案/字符串判分任务，不伪造其“官方选中 forest”。没有另存与 Browser 相同的原 evaluator 返回帧/状态快照，因此不声称有该类原始证据。补注：原审查时所有者摘要曾为 `submittedOutcome:null`，现已更正为 `Trivia Night`；先前摘要误取原提交顶层 `taskOutcome`，实际答案位于 `answer` / `parsedValue.taskOutcome`。已核对原提交 SHA-256 与原审查内容一致，原提交文件未改动；原始审查时间保留。本补注同时核对所有者 `final-audit.json` 为六单 passed、errors=[]、6个不同宿主子进程，不扩大原验收边界。

证据根：`clock-matrix/SimpleCalendarEventsOnDatePatchedP1/`；核心为 `episode/result.json`、`episode/raw-private/business-submission.json`、`clock-probe/{pre-quit-000,post-quit-001}/pixels.png`。所有者结论：`calendar-regression-conclusion.json`。

## 六单清理与最终设备状态

逐单核对原 result/audit：session created=1、deleted=1、active=0，pending create/request=0、unknown creation outcome=0，Agent quit 返回、逐 session absentVerified=true、verificationStatus=absent；环境 closed、task teardown completed。六个原进程均退出0。

六份 `workspace-post-exit-absence.json` 均明确在对应进程完成之后观察，agent-workspace 与临时父目录皆不存在。本审查未删除或重写原清理材料。原嵌套 `verification.status=unknown` 保留；不把它重写为 closed，明确以原逐 session 缺席证据和已返回 quit 为依据。

所有者稍后保存的 `final-restoration-verification.json`（observedAtUnix=1794209786.619885）原 dumpsys 已核对：**Bound services 确有 helper；Binding services 为空**。这与更早“Bound空、Binding中”的过渡快照不同。该最终快照 forwarder PID9639，安装 APK SHA=`0987ded41c12807d4f75d0789002912de143eec866fa7b389ad8efdb8b0d07bb`，UiA2 server/test PID 均不存在，adb forwards为空，bootId对照一致。共享 emulator/Appium未停止。只确认这次原始恢复快照，不声称另做了 SendForest 健康或端到端判分验证；本审查未查询设备。

## 历史完整性：独立重算与覆盖边界

不是复述 `unchanged:true`：本审查逐文件读取并计算 SHA-256，共 **14,434,241,098字节**，与 `historical-integrity-before.json` 的每条基线摘要比较：**2186条、2186已检查、0改动、0缺失**。基线自身摘要及各 campaign 分组在 `independent-integrity-review.json`。

**范围为2185个 campaign 文件，加 `.cache/androidworld-assets/2024.05.13-accessibility_forwarder.apk` 一个原 APK。** 这是基线列出的路径完整性，不是整套冻结 Python/AMKernel/安装树清单，不能据此说“全部冻结安装文件均未改”；也不覆盖基线外新增路径。各单 `executed-identity.json` 提供实际代码/版本/请求身份，不能代替未列入基线的安装树完整性证明。

## 仍未知及结论禁区

- 历史原 campaign/007 没有当时实际判分输入，不能唯一归因，不能追溯改分；本次回归成功也不反证历史结果。
- 每格仅一次、固定顺序、没有重复随机化；Patched APK还含 build-stack、签名、proto/default 等差别。四格结果不能隔离“纯生命周期 patch”的跨构建因果大小。
- ClockPatchedP1 导航多一步；诊断 pre/post 观察及采集开销改变时序。没有证明与历史运行或其他格动作/时序完全等价。
- 原 APK sender 元数据为空，不能补造原实例/代际；host receive age不是设备生成 age。官方初始化会改设备时间，不可直接跨时钟减 epoch。
- native `Init flags=0` 日志必须保留。AOSP callback/connect赋值顺序只提供解释可能，不等于实测该设备最终flags=1；最终实际数值仍未观测。
- 新实验构建曾有 gRPC默认值缺陷；修正前置构建不等于历史原 APK具有该缺陷，不得回填成历史根因。
- 动作数是原 telemetry，不形成新的计数规则；基线外安装文件及最终绑定后的传输健康不在本验收证明范围。

**AMKernel侧：本六单验收没有新增必须排查的阻断项。历史唯一根因、最终 flags 数值和未覆盖安装树仍未知；不自行开启新实验。**
