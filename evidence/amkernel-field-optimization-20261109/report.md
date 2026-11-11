# AMKernel 真实现场小范围诊断与通用修复

## 结论与成绩边界

- 冻结基线仍是 **r12 v2**：116 启动、116 有效终态，80 成功、36 失败；其中 17 步数预算终止、19 正常结束但 reward=0。不是旧冻结协议成绩。
- 已实施一个 Runtime 修复：通过现有安全消息路径保留 `InvalidElementStateException.msg`。另修补通用技能指导的观察、输入、状态验证与交接边界。没有为任务答案添加特例。
- 代表失败主要暴露模型/UI 推理与 API 使用问题，不能整体归因于 AMKernel。Clock 还复现了原生状态与官方观察/判分的交接时序差异，未修改 Harness/evaluator 来消除它。
- 下列是真实应用上的**人工控制诊断**，不是同模型 Agent 复评，没有新成功率、没有替换原失败，也没有启动另一轮 116 项。后述动作减少不能解释成模型能力已提升。

## 1. 证据、隔离与现场所有权

首先读取了用户指定的四份冻结文件：

1. `evidence/headless-fullcoverage-20261107T004632Z/report.md`
2. 同目录 `v2-ready-full-independent-recalculation.json`
3. 同目录 `v2-ready-full-manual-independent-audit.json`
4. `campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/manifest.json`

以下将该 campaign 根目录简称 `B`；所有原始调用行号都是 `B/episodes/<episode>/attempt-1/raw-private/agent-events.jsonl` 的原始行，不是重建对话。

现场核对，而非复用报告尾部 PID：

- 当前 headless `AndroidWorldAvd`：emulator PID **22585**、端口 5554 / gRPC 8554；Appium PID **16153**、127.0.0.1:4723、版本 3.7.0。两者实验前后命令与启动时间相同。
- `/sessions` 在此服务器返回 404，不能将其当作“零 session”。从现有服务器日志提取 169 个真实 session 身份，逐个只读 GET，全部 404；设备没有 UiAutomator2 server/test 进程。未删除任何非本次自有 session。
- 新 MCP server 使用开发树 `/Users/qunmi/Documents/FSQ_LAB/amkernel/.venv/bin/python -m amkernel`；没有使用或覆盖冻结 uv-tools 安装。读取相关 Issue #125/#143、Project #2、HANDOFF 和运行契约；没有擅改项目状态。
- 诊断使用官方 MCP `ClientSession`，Appium 操作全部在 `python_exec` 中经官方 Appium Python Client 发出。没有原始 HTTP UI 操作；HTTP GET 仅用于服务发现和确认 session 缺席。
- 诊断 URL 直连现有 Appium，**没有通过 campaign gate 执行模型**。动作数由共享 Appium HTTP 日志按现有 gate 的 UI 路由规则事后审计；各个正式对照路径均未超过原任务预算。这不等于已完成相同协议的独立 Agent 测评。
- 使用原 manifest 的任务名、params、seed、maxSteps，官方 task initialize/is_successful/tear_down，原无窗口 AVD 与原时间冻结设置。标准任务初始化/teardown 属于任务生命周期；未额外清空共享数据、重启共享服务、修改模型/预算/重试策略/evaluator 或升级依赖。
- 连接配置保留 `noReset=True`、`autoLaunch=False`、`newCommandTimeout=300`，并显式使用 `skipDeviceInitialization=True` / `skipServerInstallation=True` 复用已核验的服务器安装；因此也不能把诊断描述成逐位相同的冻结 campaign 运行。
- 本目录之外，没有直接写入原 campaign、manifest、结果或冻结技能/依赖。原服务器按原配置继续追加共享日志；本目录另存本次 session 日志切片。

证据：[preflight.json](preflight.json)、[session 身份核对](preflight-session-reconciliation.json)、[开发运行身份](development-runtime-identity.json)、[冻结文件前置哈希](frozen-before-sha256.json)。

### 诊断工具自身异常的处理

最初两次控制器启动失败发生在设备操作之前（缺少 MCP 模块；已安装 MCP SDK 的 timeout 类型与旧式用法不同）。随后一次混用已有 Python 环境引起 SDK schema 校验异常：**异常发生在远端执行之后**，不能推断连接未创建。

没有盲建替代 session：在同一个存活 kernel 中读取既有 `owned_session_id`，退出该 session，写出核对证据，再从服务器确认 404，随后才建立隔离了 SDK 依赖的正式诊断控制器。没有安装/升级包。

证据：[控制器 stderr](field-worker-stderr.log)、[不确定响应核对](client-validation-reconciliation.json)、`004`–`006` 命令记录。该次 session 没有 UI 动作。

## 2. 全部失败的分层筛查

对 36 个失败读取结果与原始执行 envelope，详细结果见 [all-failure-screening.json](all-failure-screening.json)。解析得到 **694 个** `python_exec` 状态 envelope，全部报告 kernel alive；normalized 计数为 695，另 1 个未解析成完整状态 envelope，未把它伪称成已验证响应。没有由这些记录证明的 kernel 死亡、隐式重建或 session 泄漏。

分层不是互斥计数，也不是把每个 reward=0 塞进一个 Runtime 类别：

|层级|确认证据|归因与处置|
|---|---|---|
|模型规划 / UI 推理|Camera 选到 Lens；SMS 选到另一款 Messages；Markor 对未出现的 Rename 菜单和非编辑标题猜测操作|任务决策问题。没有添加 benchmark 特例；不宣称 Runtime 修复能替模型规划|
|技能指导 / API 使用|16 个失败 episode 出现 tuple 列表等 bounded non-JSON 观察；SMS 未注意输入后新出现的无标签确认控件，换行覆盖号码；弱等待把“任何文本框”当作目标弹窗|修补通用指导；JSON-native 返回值保留观察细节，关注无标签控件，输入后重新观察并验证业务状态|
|AMKernel Runtime / MCP|BrowserMultiply、MarkorChangeNoteContent 两次真实 `InvalidElementStateException` 的消息被 `<custom __str__ omitted…>` 取代|已最小修复。不是两项失败的充分原因，也未证明 transport 丢失操作|
|Appium / 应用环境|Clock 的 source / element 原生请求各约 10 秒，客户端 polling wait 无法限制嵌套请求；动态 UI 已变化但取值调用超时|未改变 driver 设置或预算；技能解释请求边界，改为单次 source 本地归约、分开观察与同 session 核对|
|Harness / 评测契约 / 观察交接|Clock 在相同 4 个 UI 动作下原生计时增长、Pause/Lap 存在；官方即时判 0；无后续 UI 动作，69.293 秒后的只读诊断判 1|确认存在时序敏感现象；具体组件根因仍未隔离。没有修改 evaluator、重试限制或用后值替换即时值|

其余具体症状包括：42 次 Selenium TimeoutException、17 次 NoSuchElementException、14 次 ModuleNotFoundError（lxml 10、错误的 Appium action_chains 模块路径 3、IPython 1）。13 次 UnknownMethodException 含 native-context 限制、禁止滚动搜索、触摸步定义等协议边界。**这些计数不能作为根因计数。**

图像方向也核查了唯一 `DisplayError`：MarkorTranscribeVideo 原始第 5433 行把 PIL Image 直接传给 `display(..., mime_type='image/jpeg')`，错误为 `content must be bytes-like`。当前技能已明确要求编码后的 bytes；本次没有为这个 API 误用扩大 Runtime 接受类型。

四个代表 episode 已详细阅读原始调用；其他 32 个仅完成结构化筛查，**尚未独立复现逐项根因**。

## 3. 代表失败：最早偏离与独立诊断

### 084 SimpleSmsSend：预算耗尽

- 原始 action 1 / cell 3 打开 `com.google.android.apps.messaging`，而非目标 SMS Messenger。最早偏离发生在应用身份验证。
- 原始第 1163 行尝试 `UiScrollable.scrollIntoView`，被原协议拒绝，没有消耗 UI action；这是已存在的契约限制，不是 Runtime 执行损坏。
- 第 1458 行第一次 `send_keys` 正确号码；第 1666 行证明 `send_keys('\n')` 后原有号码不再保留。第 1759 行恢复号码；此后没有正文输入，也没有发送尝试。12/12 动作耗尽。
- 原始 cell 15 的五字段观察遗漏空文本/空描述但可点击的 `new_conversation_confirm`。完整 XML 的 cell 16、UIA 控件枚举 cell 17 和自己的 cell 20 已包含它；确认控件并非整段隐藏不可得，遗漏不是全部原因。
- 现场复现号码先保留、再被文本换行覆盖。额外诊断还确认本版本 `press_keycode(66)` 不会触发该页确认：没有把它推广为通用提交方案。
- 干净验证路径依据当前 UI 的 `new_conversation_confirm`，观察到 ThreadActivity，输入任务正文，点击 Send 一次；列表出现发送内容。退出自有 session 后官方 reward=1。**没有从数据库/evaluator 获取完成路径。**

证据：`019-sms-before-input-semantics.json`、`032-sms-after-observe-keyboard-1.png`、`034-sms-after-reconcile-confirmation.json`、`089`–`102` 的 clean postquit 记录。原始动作/调用和最早偏离的独立分析见本节原始行号。

### 005 CameraTakePhoto：错误宣告完成

- 原始第 923 行坐标点击后进入 `com.google.android.googlequicksearchbox / LensActivity`；等待只检查离开 launcher。这是最早确定偏离。
- 第 1352 行以 `page_source is not None` 当作状态变化；第 2157 行所谓快门操作之后仍在 Lens。
- 第 2253 行验证只有 Lens 包/活动与截图大小，不能证明目标 Camera 保存照片；16 次 Python 调用、5/10 UI 动作，仍宣称完成，官方 reward=0。
- 独立现场通过观察到的 Camera 标签打开 `com.android.camera2 / .CameraActivity`，确认 `Shutter` 控件后只点击一次；图像中出现新拍摄内容的缩略图。退出 session 后官方文件计数判定 reward=1。
- agent 完成证据来自应用界面/图像，不是读取官方文件计数或数据库来完成任务。

证据：`043`–`051` Camera 记录；[拍摄后的原始截图](048-camera-after-visual-evidence-1.png)。

### 024 MarkorChangeNoteContent：预算耗尽，错误信息掩盖问题

- 原始第 1193/1357 行：打开文档后等待包含 `.txt` 的完整文件名，但当前标题不显示扩展名，浪费 11.094 秒；下一观察已证明 DocumentActivity 和编辑器存在。
- 第 1566 行替换正文、点击 Save 并读回成功。随后猜测 Rename 菜单，实际菜单只有 File settings/Share/Tools/Info/Reload，额外等待 5.264 秒。
- 第 2290 行将已有正文 EditText 当作“重命名弹窗”就绪；标题实际是 TextView。第 2634 行使用不存在的 `set_value`；第 2862 行对标题 `send_keys` 得到 InvalidElementStateException，同时消耗第 12 个 UI 动作。
- 原成功的正文改动不等于整个重命名任务完成。没有把此任务的错误 UI 路径硬编码进核心，也没有声称已修好其模型规划。
- 该真实异常消息省略问题另在 SMS 标题上独立复现并验证修复；不必重跑整个 Markor rename 才能证明同一个 Runtime 格式化边界。

### 008 ClockStopWatchRunning：等待边界与官方观察交接

原始第 1346 行 `00/00 + Start`，第 1676/1833 行动作后的元素检查两次 cell deadline；第 1969 行同 session source 恢复成功，显示非零计时和 Pause；官方仍为 0。原始 4/10 UI 动作，session 正常退出。

现场两次独立诊断分开解释：

1. 第一轮对元素重复查询的 cell 超时；**未新建替代 session**。同 kernel 中保留的 `first` 快照显示 `10.47 + Pause + Lap`。quit 前后官方 UI 树均为空、reward=0；该时刻系统 accessibility_enabled=0，forwarder 在 crashed 集合中。未修改权限或重启服务。
2. 边界隔离轮仍为 4 个 UI 动作。每个只取一次 source 的两个独立 cell 都完成，分别耗时 10.131 / 10.157 秒，读到 `17.88 → 28.03` 与 Pause/Lap。没有通过延长任务预算或调整 native idle 设置处理。
3. 该轮 session 前官方观察有 19 个 UI 元素；session 内为 0。退出后首次观察有 16 个元素，但官方本次判分仍为 0。**约 69.293 秒后**，不做任何 UI 动作的只读诊断读取判为 1。
4. 第二轮期间 accessibility_enabled=1。因此“权限关闭”不能解释全部现象，也不能把第一轮的 disabled/crashed 直接当作冻结失败唯一根因。

立即 reward=0 被保留；后来的 1 **不是 scored retry、不作为修复成功项**。已证明原生任务状态与观察交接时序需要区分，尚未隔离是 UiAutomator2 suppression、forwarder 恢复、controller freshness 还是它们的组合。没有改 `_is_stopwatch_running`、等待策略或官方重试限制。

证据：`058`–`062` 首轮记录；`104`–`115` 边界记录、[accessibility 时间线](clock-boundary-accessibility-timeline.json)、[当前活动证据](clock-boundary-final-activity.txt)。安装驱动 README 的 `appium:disableSuppressAccessibilityService` 说明是相关机制线索，不是本次已证明根因，也未据此变更 capability。

## 4. 实施位置与安全性

开发仓库 `/Users/qunmi/Documents/FSQ_LAB/amkernel`：

|位置|实际修改|
|---|---|
|`src/amkernel/runner.py`，`_WEBDRIVER_NAMES`|仅增加 `InvalidElementStateException`；继续使用现有 plain-msg、descriptor 拒绝、敏感/超长消息过滤和 traceback 脱敏；不调用任意异常 `__str__`|
|`tests/runner/test_runner_process.py`|把该真实类别加入既有 recognized WebDriver 消息回归参数，覆盖可消费错误信息保留|
|`src/amkernel/skill/references/amkernel-appium.md`|指导返回 JSON-native 列表/字典，不用 tuple 列表丢失观察内容；不改变现有有界 repr 行为|
|`src/amkernel/skill/references/android-execution.md`|目标应用与目标控件联合验证；转换后重新观察；XML `.iter()` 兼容 class-tag；无标签控件；替换/提交区别；无进展动作；嵌套请求等待；同 session 核对及独立 observer 交接|
|`docs/HANDOFF.md`|记录现场修复、证据位置和不属于新 campaign 成绩的边界|

没有修改 exported API、task 参数、模型、预算、evaluator、Harness、Appium 依赖或冻结资产，没有补发一个 benchmark 答案/应用专用 wrapper。

真实异常前后：

- 修复前：`InvalidElementStateException: <custom __str__ omitted: selenium.common.exceptions.InvalidElementStateException>`。
- 修复后：`Cannot set the element to 'not editable'. Did you interact with the correct element?`，保留真实远端诊断，未展示原始 server stack/session 等对象字段。

证据：`020-sms-before-real-invalid-element.json`、`039-sms-after-real-invalid-element.json`；固定消息额外 smoke 为 `007-confirmed-before-invalid-element.json` 与 `024-after-invalid-element.json`。

## 5. 现场前后对照与原成功回归

动作包括失败的 admitted UI 动作，不计纯观察、session 创建/quit。原始动作数来自 `result.stepBudget`；诊断数由 [Appium action ledger](appium-action-ledgers.json) 与 [本次 session 日志](owned-appium-log.txt) 交叉确认。没有执行额外 app/db 操作来使任务成功。

|任务|冻结原始 动作/预算、reward|现场干净路径 动作/原预算|有效业务状态证据|现场官方结果|
|---|---|---|---|---|
|SimpleSmsSend|12/12，0|8/12|号码保留 → 正确 thread → 正文保留 → 发送条目出现|quit 后 1|
|CameraTakePhoto|5/10，0|3/10|正确 Camera → 一次快门 → 新缩略图|quit 后 1|
|ClockStopWatchRunning|4/10，0|4/10|Start/00 → Pause/Lap，17.88 → 28.03|quit 后即时 0；+69.293s 诊断 1，不计改分|
|MarkorCreateNote，原成功样本|8/16，1|8/16|指定 .md 标题、指定正文读回、Save|quit 后 1|
|SystemWifiTurnOffVerify，原成功样本|2/10，1|5/10|设置页确认 Wi-Fi switch checked=false；已是关闭，**目标状态变更 0 次**，不反复切换|quit 后 1|

辅助诊断没有藏入干净路径：SMS before 使用 7 个动作（含换行覆盖和非编辑输入）；instrumented after 使用 10 个动作（含无效 native Enter 和错误消息验证）；首轮 Clock 使用 4 个动作；SDK 不确定响应核对 session 使用 0 个 UI 动作。独立目录完整保留这些记录，没有只保留成功样本。

SMS 第一条成功诊断在 quit 前读取 reward=1；后来额外运行上述 8 动作路径，严格在 quit 后调用官方 checker，使对照边界一致。没有用它覆盖第一次诊断或冻结结果。

### 自动检查与独立审查

- `.venv/bin/python -m pytest tests/runner/test_runner_process.py -k webdriver`：**42 passed，46 deselected，3.04s**。
- `.venv/bin/python -m ruff check src/amkernel/runner.py tests/runner/test_runner_process.py`：**All checks passed**。
- 独立 reviewer 检查真实 Selenium 类继承/存储形状、Appium error 映射、现有安全过滤和指导契约；初次与最终指导增补均无 findings。审查为静态，**没有冒称 reviewer 复现了现场结果**。
- 未运行全仓库测试、完整模型复评或全量 campaign。MCP 返回错误和真实 Appium 执行路径已现场 smoke，不仅是单元测试。

## 6. 清理与不可变证据

[cleanup.json](cleanup.json) 为结构化清理记录：

- 9 个本次自有 session 全部经 GET `/session/<id>` 返回 **404**，包含不确定响应的那个 session；没有靠非空 `driver.session_id` 判断远端存活。
- 8 次官方任务 teardown 完成；5 个成功启动的实验 MCP worker 正常关闭、退出码 0。2 个启动失败记录保留；没有实验控制器进程残留。
- 共享 Appium / emulator 的 PID、启动时间、命令不变；boot ID 不变，system_server / surfaceflinger PID 不变。没有 reboot、换 AVD、换 GPU、重启共享服务或升级依赖。
- 最终没有 UiAutomator2 server/test 进程；accessibility forwarder 最终已 bound、enabled=1、crashed 为空。没有手工更改这些权限；不能将 Clock 中途状态误称为最终状态。
- VLC MANAGE_EXTERNAL_STORAGE 前后仍是 Uid deny / app default，未授权或修改。
- 对原 campaign 和四份指定证据共 **696 个文件**逐一前后 SHA-256，**0 改变**。冻结安装/技能没有作为修复目标或命令写入目标；不声称对整个磁盘或非自有进程做了清理。
- 一次性控制器脚本在验证后移除；其每条实际操作代码、结果、时间、PNG 与官方 checker 回读保留在本独立目录 JSON 中，可以审计，不需要重写冻结记录。

## 7. 已修复、未归责与下一步

已修复的是**安全错误消息遗漏**，以及已用现场反例校正的**通用技能指导**。已证明 bytes 图像发出可被查看、JSON-native 观察可保留内容、真实输入语义与完成后状态核对可走通。没有声称 Runtime 自动阻止模型循环或保证执行正确。

不属于本次 AMKernel 修复的部分：错 app、猜菜单、未用已可获得的确认控件、对非编辑标题输入、把 PIL 对象当 bytes、native-context/滚动/触摸协议违规。它们主要是模型/API/契约遵循问题。Clock 的具体 observer 时序根因仍未定位，既不能改 evaluator 掩盖，也不能从一次晚到的 1 改写原成绩。

**需要新一轮独立小样本 Agent 测评，尚不需要默认全量 116。**建议预注册原失败 SMS/Camera、一个 Markor 预算样本及这两项原成功样本；固定同模型、同 params/seed、同 budget、同重试限制和 v2 协议，使用独立开发 artifact/技能快照。Clock 单列观察交接研究，先确认官方观察 freshness 和即时判分边界；任何 Harness 生命周期修复需独立审查并标注新实验身份，不能回填冻结成绩。本次未启动这些模型评测。
