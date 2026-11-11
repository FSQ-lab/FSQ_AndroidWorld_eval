# BrowserDraw 现场诊断 handoff

## 结论

**一次独立运行复现：Appium 截图和树含 `Success!`，官方原始返回值与保存 reward 均为 `0.0`。**

这次官方判分自己的截图仍显示三色三角形和 `Success!`，实际 activity 仍是 Chrome；但同一份官方 state 的原始 accessibility forest 为空，`ui_elements=[]`。`BrowserTask.is_successful()` 执行到 `browser.py:109` 的末尾 `return 0.0`，不是错误包名分支，也不是 reward 保存转换错误。

**定位到官方 accessibility 观察链路为空；尚未定位空 forest 的产生机制。** 不把本次结论追溯冒充原 campaign 的判分输入，不改原成绩。

## 实验与约束

- 实验绝对路径：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/browserdraw-field-diagnosis-20261109T052514Z`。
- 只运行一次 BrowserDraw；没有自动重跑、再次 Submit、补判或更换观察后端。
- 模型 `github-copilot/gpt-5.6-sol`；任务参数 `{"browser_task_seed":461184702,"seed":1466251684}`；参数 SHA256 `899d6f67cdd687dc3d29a6918010a3ba15348ec5e9caa772f4f4f2cdffb03956`。
- 原任务 20 步预算；本次 17 个 UI 动作、19 次 python_exec，正常结束。时间预算维持 business=1320s、cleanup=180s、grace=10s、recovery=120s。
- 原提示模板 SHA256 与本次一致：`463118879bbe14a14abfd987920f115fff29f128db4566dc282e75dc0aa906aa`。Agent workspace digest、154 个文件与 sandbox SHA256 均匹配原 campaign。
- 诊断没有注入等待、动作或额外设备状态读取。模型自行在 Submit 后生成了 `time.sleep(2)`；历史模型调用是 1 秒。这是同模型重新采样，不是逐条调用重放；未修改模型、提示、任务参数或预算来要求这一差异。完整代码保存在 `python-cells/018.py`。
- 设备与服务复用；实验目录、Agent 临时 workspace、AMKernel 数据目录隔离。AMKernel 安装与原 campaign 不写入。

## 设备与 session 所有权

证据：[preflight.json](preflight.json)、[ownership.json](ownership.json)、[session-log-lifecycle.json](session-log-lifecycle.json)。

- 唯一在线设备 `emulator-5554`，boot ID `0f36e370-012a-4423-a1f9-959beae8f90d` 与原 campaign 相同。
- 预存 emulator PID 22585、Appium PID 16153 属共享资源；未重启、停止或修改服务配置。
- Appium 3.7.0；`GET /sessions` 不受支持、返回 404，**未把它当空 session 列表**。启动前日志 176 个 master session 创建记录均有移除记录；设备没有 UiAutomator2 server/test 活进程，也没有 ADB forward。
- 一次过宽的历史 UUID 只读核对包含了 element ID，120s 后中断；它不是 session 清单。随后使用实际 master-session 创建/移除日志及进程事实核对；细节保留在 ownership.json，无删除历史 session 的操作。
- 本次唯一 session：`5bc92b8e-0705-432d-b471-a9093f4e17d7`。只清理此实验创建的 session。

## 时间线与原始证据

以下均为 host UTC。Appium 时间是既有 HTTP 响应取得时点；不宣称多个字段原子同时取得。

|事件|时间|证据|
|---|---|---|
|Submit 对应触摸请求开始 / 返回|05:33:58.340893 / 05:33:58.735331|`appium-timeline.json` 数组索引 224–225；`python-cells/018.py`|
|Submit 后页面树返回|05:34:00.907668|[0227.xml](appium-responses/0227.xml)，含 `Success!`|
|Submit 后截图返回|05:34:01.010920|[0229.png](appium-responses/0229.png)，已直接读图核对三色图形与 `Success!`|
|包名返回|05:34:01.036076|[0231.json](appium-responses/0231.json)：`com.android.chrome`|
|activity 返回|05:34:01.052447|[0233.json](appium-responses/0233.json)：`org.chromium.chrome.browser.ChromeTabbedActivity`|
|quit HTTP 请求开始 / 上游响应返回|05:34:05.610510 / 05:34:05.823115|`appium-timeline.json` 索引 236–237；HTTP 200|
|官方 evaluator 开始|05:34:10.770394|[evaluator-calls.json](evaluator-calls.json)|
|这次官方 `get_state()` 调用 / 返回|05:34:10.770500 / 05:34:10.818946|同上；只有一次|
|官方 activity 返回|05:34:10.843734|同上，ChromeTabbedActivity|
|官方函数在第 109 行返回|05:34:10.843750|同上，float `0.0`|

**quit 时钟边界：**记录的是真实 `DELETE /session` 在代理的入口和上游响应返回，不伪装成 Python 函数内部精确 entry/exit。专用第 19 次 python_exec 的结构化返回为 `status=completed`、`kernelState=alive`、`durationMs=213`、`quitReturned=true`，证明 `driver.quit()` 确实返回。代码：[019.py](python-cells/019.py)。对应 Appium 原始日志：[appium-run.log](appium-run.log) 第 300–304 行。

完整既有响应及时间：[appium-timeline.json](appium-timeline.json)、`appium-responses/`。模型原始事件：`episode/raw-private/agent-events.jsonl`；第 18 次调用在 4952–4954 行，第 19 次调用在 5016–5017 行。可读提取：[python-executions.json](python-executions.json)。

## 官方实际判分输入与分支

- [evaluator-0/pixels.png](evaluator-0/pixels.png)：**官方这次 `get_state()` 返回对象的 pixels**，已直接读图，quit 后仍显示 `Success!`；不是额外截图。另存无损数组 `pixels.npy`。
- [evaluator-0/forest.json](evaluator-0/forest.json)：`{}`；原始 protobuf [forest.pb](evaluator-0/forest.pb) 为 0 字节。
- [evaluator-0/ui-elements.json](evaluator-0/ui-elements.json)：`[]`。不是只有过滤后的 Success 节点缺失，原始 forest 本身就没有内容。
- 实际观察后端：`A11yMethod.A11Y_FORWARDER_APP`，未修改。
- 官方既有 activity 调用返回 `com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity`；提取 package 为 `com.android.chrome`，通过第 103 行包名检查。
- 遍历空 `ui_elements` 后执行第 109 行 `return 0.0`；未执行第 104 行错误包名返回，也未命中第 108 行成功返回。
- [evaluator-calls.json](evaluator-calls.json) 保存实际执行行、调用时间、activity 原始返回、局部 state 的证据路径及原始返回类型。通过原函数 `sys.settrace` 留存，不重新调用 `env.get_state()`。
- [stderr.log](stderr.log) 有两条未带时间的 `Could not get a11y tree, retrying.`；**不能把它们归到这次判分调用**，也不能据此认定因果。实际官方原函数本次用时约 73ms。

## evaluator 返回值与保存 reward

- 原始返回：`0.0`，Python 类型 `float`，见 evaluator-calls.json。
- 最终保存：`episode/result.json` 的 `officialReward=0.0`，`error=null`、`invalidReason=null`。
- 离线关联：[correlation.json](correlation.json)，`rawAndSavedRewardEqual=true`、`officialEvaluatorCalls=1`。
- 汇总索引：[evidence-index.json](evidence-index.json)。本次未因截图成功而改判 reward。

## 实际版本、诊断改动与命令

- Harness 仓库 HEAD：`ebd085561651b8ba4b2a1a53ef6321e0305c06b3`；工作树在本次期间有别的开发改动，**不能只用 HEAD 代表运行版本**。
- AndroidWorld revision：`55ddaf5edc6f6c25673aed343907d5b9dca66f84`。实际执行文件来自 `.venv/lib/python3.11/site-packages/android_world/...`，相关源文件与 checkout 逐文件 SHA256 相同，见 [official-source-identity.json](official-source-identity.json)；副本在 `official-source/`。
- Harness Python 3.11.16、android-world 0.1.0、android-env 1.2.3；完整实测版本：[harness-package-versions.json](harness-package-versions.json)。这不是 AMKernel Runtime 的依赖版本表。
- AMKernel Runtime 使用原冻结 `amkernel-3388314/uv-tools/amkernel/bin/python`，安装版本 0.1.3；每次执行实际 Runtime 身份保存在 python-executions.json。没有使用开发版 Runtime 替换它。
- 当前工作树已经在改 r13 submission 流程。为不把新流程混入诊断，在 `source-snapshot/` 私有副本保留原提示/r12 调用顺序，并使用 git HEAD 的旧 supervisor、action gate、proxy；不回滚或覆盖原工作树。**不宣称这个私有重建版本与历史 aggregate harness-source hash 逐字节相同。**执行文件逐个哈希见 [executed-identity.json](executed-identity.json)，具体隔离说明见 [diagnostic-changes.json](diagnostic-changes.json)。
- 新增观测只有两处：`RecordingProxy` 在内存旁路留存原有 Appium 请求边界和响应；官方 evaluator trace 留存同次调用的局部对象与返回行，原函数返回后才序列化。没有新增 get_state、刷新后端、重试或 sleep。追踪有 CPU 开销，wrapper duration 包含事后序列化，不用它替代原函数时间。
- 入口及完整代码：[launch.py](launch.py)、[diagnose.py](diagnose.py)。本次实际启动命令：

```sh
.venv/bin/python evidence/browserdraw-field-diagnosis-20261109T052514Z/launch.py
```

- 完整子命令、参数、环境覆盖：[launch.json](launch.json)、[run-command.json](run-command.json)；子进程完成：[process-result.json](process-result.json)、[launcher-result.json](launcher-result.json)，exit code 均为 0。
- `summarize.py` 仅离线处理保存的证据，不访问设备；本次执行命令为 `.venv/bin/python evidence/browserdraw-field-diagnosis-20261109T052514Z/summarize.py`。

## 清理与只读证明

- [protected-input-verification.json](protected-input-verification.json)：原 campaign 全部文件、冻结安装全部文件和正式 `.agents` 共 **3782 个文件**前后 SHA256 相同，无新增或删除。完整清单 `protected-before-sha256.json` / `protected-after-sha256.json`。
- `episode/result.json`：Agent quit 归属已证明；session absent 验证；`taskTearDown=completed`、`environment=closed`。
- [postrun-cleanup.json](postrun-cleanup.json)：判分和 teardown 后的独立清理观察，**不是判分输入**。自有 session 查询 404，UiAutomator2 进程不存在，共享服务仍在、boot ID 不变。
- [workspace-cleanup.json](workspace-cleanup.json)：临时 Agent workspace 已删除。
- [runtime-state-cleanup.json](runtime-state-cleanup.json)：隔离 AMKernel 数据目录已归档至 `runtime-state-archive/` 后删除；未改冻结 state。
- 未安装依赖、未修改正式源码/skill/判据，未停止共享 emulator 或 Appium。诊断源代码保留为复核证据，不是未清理的活服务。

## 未解决问题与 AMKernel 侧交接

1. **未解决：**A11y forwarder 为什么交付空 protobuf：服务启用/连接、forwarder→gRPC 数据、UiAutomator2 并存或生命周期影响，尚无本次边界内的内部追踪证据。
2. **未解决：**空 forest 在 quit 前是否已经存在。本次没有额外读取官方 state，故不能声称 quit 导致了空树；也不能把 Appium 的非空树当作 forwarder 在 quit 前正常的证明。
3. **已排除本次候选：**错误包名、quit 后应用画布/成功提示消失、最终 reward 覆盖、模型只有口头成功声明、原始 forest 有 Success 但仅转换过滤丢失。
4. **AMKernel 是否继续排查：需要边界协作，不支持先改核心。**请对方把第 18/19 次结构化调用与这些 HTTP 响应对齐，确认交付/quit 链没有遗漏；现场证据表明它们都成功返回。目前主调查点应移到 AndroidWorld A11y forwarder/gRPC 与 Appium 生命周期交界，不能据此宣称 AMKernel 核心有缺陷，也不应先改 evaluator、加等待或换成 Appium 树补判。
5. 本次只完成这一轮隔离诊断；如要进一步区分空树出现时点，应另行约定一次带 forwarder 内部原数据时间戳的诊断，不在本目录连续自动重跑。
