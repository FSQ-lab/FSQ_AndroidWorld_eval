# FSQ 单目标资源准入：交 w6:p2 一次决策

**离线代码与 model 门禁已完成；资源非冲突边界仍未获足够 authority 证明，本包不自签 live。** 不再重复这些门禁，也不继续 discovery／寻找 registry 旁路。

## 已完成的只读证据

| 观察 | 实际结果 | 证据与限制 |
| --- | --- | --- |
| C 原 GET `/sessions` | 404 | 从已有 `appium.log:610980–610981` 恢复同次 `06:00:13.505` 结果，未重发；原 C 收据未修改。 |
| 本次获新授权的一次 GET `/appium/sessions` | 500，WebDriver `unknown error` | `06:28:37Z`；明确安全消息：`Potentially insecure feature 'session_discovery' has not been enabled`。session 数量仍 unknown；未重试、启用 flag、重启或创建／删除 session。 |
| 既有 master-list 生命周期历史 | 322 注册／322 后续移除，保留历史中未配对注册 0 | 非连续覆盖证明，不能升级为当前零 session、global-free 或 lease。 |

Appium 3 [官方迁移事实](https://appium.io/docs/en/3.0/guides/migrating-2-to-3/#session-discovery-requires-feature-flag)：旧 `/sessions` 被 `/appium/sessions` 替代，后者需 `*:session_discovery`。当前安装路由证据与实际 HTTP 安全拒绝分别记录；未把本地 compiled 字节等同运行中的字节。既有配置文件有 flag，不代表当前服务加载了它。

完整脱敏证据：`host-resource-evidence.json`、`supported-session-discovery.json`、`supported-session-discovery-error-detail.json`。只保留生命周期／目标／端口／时间和必要 controller 进程元数据，无完整 capabilities、模型、凭据或业务内容。

## 当前 controller 与真正剩余风险

现存 Appium 的只读 listener 发现与文件描述符确认既有日志及本项目 cwd；其 immediate parent 是已有 OMP 进程。仅提取 PID 的 Herdr process-info 查询未在 12 个已知 registry pane 中找到该父进程，**不能指认实际 accountable controller**；未据此读取进程内存、终端／模型内容或操作 PID。qemu 身份仍引用 C 的既有5554/8554对应收据，本轮没有再探测设备／qemu。未发现可确证的新活跃 session ID；也没有证据证明当前不存在 session。

三项既有声明已原样进入草案：w6:p1 无保留／无在途真实任务，w1:p1、w2:p1 无预约；另记录真人明确 **FSQ first，AMKernel 等显式释放**。仅能证明各自边界，不能造全局空闲。已向三方请求仅依据既有记录补充 controller／启动／交接出处；交本包时尚未收到补充，因此不把“已请求”记成“已交接”。

**缺的不是再跑 API 或重签已完成代码门禁，而是实际目标 authority 的一次 accountable 控制／可处置 guest-state 决策。** 由 w6:p2 取得 current controller 交接，或请真实目标 authority 明确接管并确认该现存 AndroidWorldAvd 的 guest 状态可供 FSQ 官方恢复／任务修改，约束受控调用方不得并发，并对尚未枚举的 session／旧 supervisor 不确定性作明确决定。不能仅凭三 holder 无预约自动补出这项事实；若识别出未知当前活跃控制者／session，停而不清，先取得其交接。若无法作这项实际风险决定，明确不能继续并按协调决定释放，不无限重试 discovery。

## 已准备、无需重复询问的精确字段

`authorization-draft.json` 已绑定：

- candidate `94a33fc3719cb2b289b274a415e78d91aeef5d9c34f8a63fedeac0e638e615f2`；
- 已批准独立 final review `5a941efe9bbe6d66f8a487c2995ea77946d7cccca898c0d422aef5fc02e612f6`；
- 已接受 genuine model receipt `58d96868e5e4ccb139eb16e688178de0f2e9acbad40bc1f0035a293e0dd47323`。

目标固定：`emulator-5554`／`AndroidWorldAvd`／console5554／ADB companion5555／gRPC8554；ADB `/Users/qunmi/Library/Android/sdk/platform-tools/adb`。Appium4723 保持原生命周期，不是 FSQ control path；无重启／杀共享服务、新建或替换 AVD、第二目标。

w6:p2 在实际风险决定后，只需一次出具独立正式授权文件 `authorization-approved-qualify-smoke.json`：标准 `schemaVersion=1`、`kind=fsq_execution_authorization`、上述固定绑定；明确选择 `approvedStages`，建议当前仅 `qualify`＋一次 `smoke`；将实际已批准的 `resource.exclusive/disposable/mutationsAllowed`、有限 `notBeforeUnix/validUntilUnix`、accountable `authority` 写实。这些值现在故意未签，不是要再次询问已知技术字段。不要把本 draft 改名当批准；正式文件使用实际 schema 和已批准事实。

guest 官方快照／基线恢复和任务修改是 proposed live effects；原生 u2 支持服务器／instrumentation 初始化及缺 helper 时 SDK 的正常 provisioning 风险也已列出，供同一次 effect-scope 决定，不临时自动修复或篡改 native 行为。真实 server-returned model 仍 unknown，不重做 model 调用。

## 资格与一次 smoke：命令已备、未执行

`prospective-commands.sh` 的两个独立分支已备好，正式授权与资源边界满足后由协调者才可调用：`qualify`；资格确证后再一次 `smoke`。本轮仅 `bash -n` 与无参数拒绝路径，未执行两个 live 分支。

smoke 固定原校准顺序首题 **index102 `SystemWifiTurnOff`**，M10、B720s、完整 envelope1330s；它修改 Wi-Fi，非默认无害授权。资格 envelope1210s；两段 envelope 合计2540s再加实际 overhead，由协调者给有限窗口，不虚构 TTL／窗口起止。完整命令／输出路径／effects 在 `stage-plan.md`，不改正式116范围。

授权或窗口后续变更会改变 readiness 绑定；不默改已经签发的授权、不重新标记旧 receipts。若未来整轮不在本次授权内，再按当时真实阶段决定；不自动扩 scope。

完成批准范围或明确不能继续时，报告 task/environment、owned worker/group/outer 清理及未知状态，并**显式释放给 w6:p1**；过期、退出、FSQ-first 均不等于已释放。当前没有 stage／guest 变更，也没有独占 lease 消费。
