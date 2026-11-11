# BrowserDraw 空 forest：协查结论

## 结论与归属

**已确认的问题在 AndroidWorld 官方观察链与 Appium/UiAutomator2 的 accessibility 共存、服务生命周期交界；目前没有 AMKernel 执行核心的修复依据。** 历史保存证据是画面和 Appium 树有 Success、官方 forest 为空并返回 0；本轮进一步实测了服务解绑、持续空消息及退出后的竞争消息流。

**尚未证明历史那一次 0 分的唯一底层原因。** 本轮 A、B 都获官方 1.0，没有复现或改写历史失败。A 捕获到相符的故障机制，但没有捕获官方最终选择空树；B 验证了一个候选规避配置，并非证明所有同类失败已经修复。

## 实际执行与对照

FieldOwner 是唯一设备操作方；DiagnosticAudit 只读独立审查；主 Agent 对齐原证据、审查追踪语义、读取 A/B 实际判分截图并离线验证已安装 APK 字节码。没有可连接的既有 Collab host，使用受控协作 Agent，并未冒称接管旧 TUI。

| 项目 | A：省略保护能力 | B：显式 true |
|---|---:|---:|
| 官方 reward | 1.0 | 1.0 |
| UI 动作 / 原预算 | 17 / 20 | 17 / 20 |
| 官方 get_state 次数 | 1 | 1 |
| 接收 forest 总数 | 1938 | 2245 |
| 零窗口空 forest | 1417 | 0 |
| 创建响应至 quit 响应期间空 forest | 1339 | 0 |
| quit 响应后空 forest | 71 | 0 |
| session-created 样本中 forwarder 已绑定 | 否 | 是 |
| 官方最终选中接收序号 | 1901 | 2228 |

两次都完成三色、三条线绘制并提交；实际判分截图显示 Success。相同模型 github-copilot/gpt-5.6-sol、任务参数、原 prompt hash、20 步预算、时间限制和官方 evaluator。B 只在隔离代理转发 POST /session 的请求体中加入 `appium:disableSuppressAccessibilityService: true`；原始请求、实际转发请求、返回能力和 instrumentation 参数均留存。

这是**动作重新采样的配置对照，不是逐动作回放**。Python 调用 A 为 26 次、B 为 32 次，不能声称执行轨迹相同。A/B 初始服务状态不同；正常官方初始化都执行原有 forwarder 安装/启用流程并更换进程，但并非完整的顺序反转或状态配平实验。追踪保留所有消息对象并后台采样系统状态，未插入新的 get_state、等待、重试或观察后端切换；诊断开销仍可能影响调度。

## 故障证据链

### A：定位到的真实服务与消息变化

1. 正常官方初始化后 forwarder 已绑定。Appium 创建 session 期间开始收到新产生的零窗口消息；不是接收器凭空补出空对象，也不只是旧空树一直留在缓存。
2. session-created 样本显示 UiAutomation 存在，forwarder 配置项仍启用，但 Bound services 为空；quit 期间重新绑定。
3. quit 附近同一 forwarder 进程的旧、新两个线程继续交错发送；接收端出现 `1898 空 / 1899 Success / 1900 空 / 1901 Success / 1902 空 / 1903 Success`。
4. 官方最终 drain 7 返回 1901，实际选择与 evaluator 捕获保持同一个强引用对象，2 windows、54 nodes、含 Success。因此这次实际得 1.0。当前 A 的权威 drain 没有返回空树，不能把竞争风险写成已经发生的 0 分。
5. 接收器 latest-only 与 wrapper 选择最后累积项的组合使末次到达消息影响判分；空消息覆盖有效观察可以解释历史症状，但历史消息来源序号未保存，无法事后证明那次具体选中路径。

### B：候选规避配置的实测效果

显式能力到达实际 instrumentation：`-e DISABLE_SUPPRESS_ACCESSIBILITY_SERVICES true`，返回能力也为 true。session-created 样本中 forwarder 仍绑定；本轮追踪覆盖期间的 2245 条接收消息中没有空 forest。官方最终 drain 8 返回 2228，实际选择和 evaluator 捕获为同一对象，2 windows、54 nodes、含 Success。

**两次 `UiAutomation: Init … flags=0` 日志相同，不能用该日志当最终连接 flags 的证据。** Android 13 连接回调可在 flags 字段赋值前打印对象；本结论依据请求/参数投递、实际绑定状态和消息流，而非把 Init 日志解释成运行时 flags dump。不要报告基于跨设备/host 时钟的“0.3 秒因果延迟”。

### 已安装 forwarder 本身的生命周期风险

主 Agent 使用本机已有 SDK dexdump 离线反汇编保存的 APK，未安装新工具或操作设备。APK SHA-256 `97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a`，与冻结缓存相同。

完整服务类字节码确认：构造期间启动捕获 service 实例的线程；线程持续对该实例调用 getWindows；没有自定义 onUnbind/onDestroy 取消逻辑，也不保存 worker handle；catch 只覆盖 ConcurrentModificationException。因而“旧实例断连后 worker 仍存活，新实例再创建 worker”有已安装代码支持，但两个 TID 对应的 Java 实例身份没有直接记录，仍标记为 **[INFERENCE]**。

历史 logcat 另有构造 worker 在 getWindows 的空 Context NPE，实际导致整个进程被杀。它支持初始化竞态风险，但不是本轮 A/B 的 crash，也不能归给冻结 BrowserDraw 那一次。

## 修改、清理与下一步决策

- 只新增独立诊断目录、被动追踪和 B 隔离代理补丁；没有修改 AMKernel 生产代码、正式 skill、共享 Appium 启动配置、原 campaign、manifest、结果或冻结安装资产。
- 原官方环境初始化会请求安装/重启同一冻结 forwarder APK，本轮原样保留。不能声称设备上完全没有发生 APK 安装或 forwarder 进程替换。
- A、B 各创建并删除 1 个所属 session，master log DELETE 200；清理验证无所属活进程、UiAutomator2 instrumentation 或 ADB forwards，临时 Agent workspace 已消失，共享 Appium 与无窗口 emulator 仍存活。
- 这是所属资源清理，**不是设备状态还原**。forwarder 留在正常环境初始化后的已绑定状态，B 后 PID 11143 持续存在。
- 修复方向应放在 AndroidWorld/Appium 集成配置与 forwarder 生命周期，不应把 reward=0 塞进 AMKernel 核心补丁。显式 true 是本次已验证的候选规避；本轮未将它升级为正式协议默认值。
- 若要正式固化能力，先做小范围配平的同条件重复与原成功任务回归，再明确记录为新协议配置。没有必要为本次定位直接启动 116 项全量；不得给旧 campaign 补分。

## 可核查证据

- A：[forest-provenance.json](forest-provenance.json)、[forest-trace.json](forest-trace.json)、[evaluator-calls.json](evaluator-calls.json)、[官方结果](episode/result.json)、[实际判分截图](evaluator-0/pixels.png)、[清理](postrun-cleanup.json)。
- B：[A/B 对照](../browserdraw-forest-capability-B-20261109T061859Z/comparison-A-B.json)、[能力投递](../browserdraw-forest-capability-B-20261109T061859Z/capability-injection.json)、[官方结果](../browserdraw-forest-capability-B-20261109T061859Z/episode/result.json)、[来源链](../browserdraw-forest-capability-B-20261109T061859Z/forest-provenance.json)、[清理](../browserdraw-forest-capability-B-20261109T061859Z/postrun-cleanup.json)。
- 已安装字节码：[完整服务类](forwarder-artifact/AccessibilityForwarder.dexdump.txt)（构造 75–133、worker 171–217、onInterrupt 1185–1206）、[命令与哈希](forwarder-artifact/parent-bytecode-verification.json)。132 MB 临时全 APK dump 已移除，只保留完整目标类。
- 上游机制：[Appium server 10.6.6 能力处理](https://github.com/appium/appium-uiautomator2-server/blob/v10.6.6/app/src/main/java/io/appium/uiautomator2/server/ServerInstrumentation.java#L280-L296)、[Android 13 flags 赋值顺序](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-13.0.0_r1/core/java/android/app/UiAutomation.java#L325-L337)、[异步 Init 日志](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-13.0.0_r1/core/java/android/app/UiAutomation.java#L1552-L1564)。

独立审查覆盖追踪语义、A/B 原始选择链、能力实际投递、绑定状态、已安装字节码及清理。最终结论不使用早期被撤回的“Init flags=0 即最终压制 flags”解释。
