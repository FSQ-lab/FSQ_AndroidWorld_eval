# 独立116项无窗口测评与最终审计

## 结果与分数边界

已从第1项开始完成全新独立 campaign：`amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z`。协议：`r12.full_coverage_after_verified_recovery.v2`。

| 项目 | 实际结果 |
|---|---:|
| 计划任务 | 116 |
| 实际启动任务 / attempts | 116 / 116 |
| 有终态任务 | 116 |
| 有效结果 / 有效覆盖率 | 116 / 100% |
| 成功 | 80 |
| 失败 | 36 |
| invalid | 0 |
| null reward | 0 |
| 原始清理门禁异常 | 0 |
| 未启动任务 | 0 |
| 官方 evaluator reward 合计 | 80.0 |
| 新协议完整有效分数 `fullValidScore` | 0.6896551724137931（68.97%） |

新协议完整有效结果成立，`qualified=true`。它不是旧 r11 冻结协议的正式分数：`officialScore` 与 `legacyOfficialScore` 均保留 null。没有把新协议分数或全集冒充旧协议结果，没有把失败改写为成功。

## 冻结输入与独立来源

源 manifest：`campaigns/amkernel-3388314-r11-timeout300-full-20261106T142607Z/manifest.json`。

- 源文件 SHA256：`2345c5af27c75f7c1a7c6e263b77963f426864a6486a51e845468430a50ea856`。
- 全116项规格摘要：`f41b2dac8a427ddd22bbe4ea04b0104ae9feea8280c9295b2fe1dfbc6671d417`。
- 新 manifest 的全部任务规格与源规格相等；全部116项实际记录的初始化前参数快照也与源规格相等。
- `prepare --inherit-manifest` 不生成新参数。官方初始化中的日期/UI表达转换照常执行，原 evaluator、reward 与目标语义不变。
- 对照源 Runtime，除本次获授权修改的 Harness 源码摘要外，所有 Runtime 身份字段无差异；原模型、AMKernel、OMP、依赖、Agent资产、预算、工具/动作策略与单项重试限制保留。
- 原 r12 v1 三项暂停轮的 manifest、checkpoint、summary、metadata 摘要保持不变。没有续跑、覆盖或把该轮结果拼入本轮；新校准只作为资格证据，116项结果全部来自新目录的 `episodes/`。

## 最终源码门禁与行为验证

- 全套回归：484 passed，2个既有警告保留；没有为消除警告更改依赖。见 `v2-ready-regression-verification.json`。
- 最终源码的新资格与116项真实无Agent预演全部通过；`agentInvoked=false`、独立逐项摘要和生命周期验证通过。见 `v2-ready-rehearsal-independent-validation.json`。
- 新12项校准：12项有效，8成功、4失败、0 invalid、0清理异常；独立重算与 summary 一致。校准资格不要求把业务失败伪装成成功。
- 本轮实际执行了新增 UTC 恢复路径，以及恢复后的新鲜身份、会话缺席、readiness、核心服务与核心进程边界检查。核心进程变化会暂停；没有以一次健康返回绕过重启协调。

## 环境与视频证据

同一 AndroidWorldAvd、`emulator-5554`、console 5554、gRPC 8554、Appium 4723。最终仍为模拟器 PID 22585、原 Appium PID 16153。

实际启动参数包含 `-read-only -no-snapshot-load -no-snapshot-save -no-window`；没有 `-gpu` 参数，没有显式改选图形后端，没有清空基础镜像数据。

实际 Vulkan：lavapipe / llvmpipe LLVM21.1.4；实际 GLES：swangle / ANGLE SwiftShader LLVM10。添加 `-no-window` 后自动选择的 GLES 与原窗口模式不同，不能将结果解释为单一“无窗口修复”的因果证明。

全量运行之前已实际验证：静态32次截图、同一故障视频不截图播放至 EOF、视频播放中32次连续截图、Maria/Emilia不同时段画面、session quit 与404。独立 HTTP 请求审计共65次截图，其中1次为额外视觉验证。见 `headless-controls-summary.json` 与 `headless-controls-report.md`。

原故障任务 `MarkorTranscribeVideo` 在本轮得到有效失败终态，官方 reward=0.0；没有改写该失败，也没有将控制实验通过当作该任务成功。

## 恢复、终止与重启边界

- 40次异常终态后的恢复验证：36个 reward=0 的失败，另有4个 reward=1但以原步数预算终止的有效样本。
- 其中3次调用官方 `android_world.utils.datetime_utils.setup_datetime` 恢复 UTC；任务索引为2、3、4。只恢复允许的时间设置，不冻结日期、不初始化任务、不增加重试，不改写原 reward、终止或清理记录。
- 每次先保存并 fsync 恢复前证据、绑定 checkpoint，随后才允许状态恢复；恢复后重新探测，所有本轮恢复边界均未观察到 boot ID、system_server 或 SurfaceFlinger 变化。
- campaign 内0次模拟器冷重启/核心进程重启边界；从启动前控制实验到最终核对，boot ID 均为 `0f36e370-012a-4423-a1f9-959beae8f90d`，system_server=500，SurfaceFlinger=333。
- 开始本轮前曾按授权将原窗口模拟器冷切换为同一AVD无窗口实例；该边界在正式结果之前，并单独记录于 `environment-mode.json` 与预切换证据，不隐藏为原环境未变。
- 每个 Agent 的原始终止、exitCode、processExited、cleanup 和 reward 均保留在本轮 result 与 `v2-ready-full-manual-independent-audit.json`，未启动列表为空。

## 两路最终审计

1. 独立 scorer 重算：`v2-ready-full-independent-recalculation.json`。`matchesSummary=true`，`coverageAudit.valid=true`，`coverageAudit.complete=true`，errors为空。
2. 原始 checkpoint/result 审计：`v2-ready-full-manual-independent-audit.json`。独立核对实际启动/终态键、任务规格和路径绑定、原 result 字节摘要、原 reward/null、初始化前参数快照及旧轮摘要。116项真实启动且终态齐全、116 attempts，无缺失终态、无未启动项、issues为空。

116行记录并非本轮完整性的唯一依据：实际启动 checkpoint、终态 checkpoint、result 字节与输入来源均已逐项绑定并验证。

## 临时权限与最终资源状态

通过官方 Appium Client 在正常 Android Settings UI 将 VLC “Allow access to manage all files” 从 checked=true 恢复为 false。最终 appops 为 `Uid mode: MANAGE_EXTERNAL_STORAGE: deny`，恢复原有效拒绝状态。

权限恢复阶段出现一次30秒 MCP transport 创建中止及一次默认初始化因可选 `io.appium.settings` 未安装而失败。这些发生在 campaign 完成后，不是测评记录。两个创建身份均先协调并验证404，再进行后续连接；没有盲建并发 session、重启服务或安装缺失 helper。最终使用已通过资格的设备及既有UiAutomator2服务包完成原生UI恢复，不依赖可选 Settings helper。

最终恢复 session 成功 `driver.quit()`，其自身和两个失败/中止创建身份均独立确认404，UiAutomator2服务/test进程为空。见 `v2-ready-final-permission-ui.json`、`v2-ready-final-restoration-cleanup.json`、`v2-ready-final-resource-verification.json`。

最终 activity/package/settings/window、ADB、Appium与gRPC真实探测均可用，见 `v2-ready-final-core-health.json`。模拟器和原 Appium 保持运行；没有用停服务代替 session 清理。

## 执行附记

工具 `wait` 在未完成的后台任务上反复短返回，已报告工具问题；后续等待使用宿主原生文件系统完成事件，不轮询进度、不操作测评中的设备。

冻结 troubleshooting 技能的相对 `contexts/...` 引用在 `skill://appium-troubleshooting/` 下不可直接读取，实际文档位于 vendored skill 仓库；该路径解析问题已定位。建议技能明确“相对上下文路径按 vendored repository root 解析”，并在长创建指导中区分30秒 MCP transport 与 cell deadline。未改动冻结技能资产，也未执行文档中的 ADB reset/helper卸载建议。

汇总入口：`v2-ready-final-summary.json`。本报告只陈述已观察的本轮结果，不声称图形故障永久修复或同等旧协议分数成立。
