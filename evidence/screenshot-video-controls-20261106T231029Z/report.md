# 截图与视频播放对照验证

## 结论

同一故障视频的“播放 + 原节奏连续截图”在恢复后的环境中未复现系统级故障。现有证据不能认定截图本身是根因，也不能据此认定偶发图形栈问题已永久修复。

模拟器和 Appium 已恢复可用。没有续跑、拼接或重新启动正式 campaign；没有产生官方分数。

## 对照结果

| 场景 | 实际截图调用数 | 观察结果 |
|---|---:|---|
| Android 启动器静态画面，目标间隔 0.75 秒 | 32 | 全部完成，采集历时 23.704 秒；核心服务正常 |
| 原视频播放，不截图 | 0 | 播放中 MediaSession 为 PLAYING；24 秒视频到达 EOF，之后正常停止 |
| 原视频播放，目标间隔 0.75 秒连续截图 | 32 | 全部完成，采集历时 23.536 秒；最后一次请求开始于 23.252 秒，单次截图最长 0.305 秒 |

截图数量不是从 Agent 声明推断：独立解析 Appium HTTP 请求日志，得到三个窗口分别为 32、0、32，共 64 次。逐帧时间、字节数及摘要也已保存。

视频无截图组：播放按钮被观察为 Pause；播放后约 20.66 秒，MediaSession 仍为 PLAYING；约 36.82 秒的终态采样为 STOPPED/inactive，原生 VLC 日志记录 EOF reached。没有将初始处于教程/暂停状态的播放器误算为已播放。

视频截图组：采样期间 MediaSession 为 PLAYING；保留画面中可观察到 Charlotte 和 Emilia 两个不同时段的文字。第 0 帧为播放器刚打开的黑色过渡帧，不当作已显示的文字帧。

## 同一输入与环境边界

- 使用从原故障模拟器取出的真实视频，未重新生成参数或媒体内容。
- 视频 SHA256：`8b01c2da29a1926302172bca43c6f7600e5d1b143a7870f4b5ddc7601b4e87cc`。
- 现有 imageio-ffmpeg 二进制完整解码验证成功：24 秒、720 帧、320×240、30 fps、MPEG-4 Simple Profile。没有安装 ffmpeg 或其他依赖。
- 同一 AndroidWorldAvd、原 Emulator 37.2.13、原 Appium 3.7.0、原 UiAutomator2 8.7.0、原冻结 AMKernel 及客户端。
- 没有改动图形选项。实际冷启动日志明确显示 Vulkan=lavapipe、GLES=host、Apple M4/Metal；不是全部路径都由软件渲染。
- 这是新的冷启动只读临时层，不是原失败时累积了大量正式任务状态的长时间进程。原 3 个临时 qcow2 层已经复制保存；副本不是经过正常关机验证的完整可恢复备份。基础 AVD 数据没有清空，未调用 prepare、qualify 或应用快照重置。
- 原测试视频通过 VLC 支持的文件 URI 打开，不是原 Agent 的媒体列表点击序列。文件字节、播放器、视频长度与截图路径一致；没有重放前 35 项任务，不能排除累积状态、长期运行或其他操作顺序的影响。

## 恢复过程中的独立门槛

1. 第一次启动被此前未提交的崩溃报告同意窗口阻挡，尚无 guest transport。停止该任务拥有的启动后，以临时参数 `-crash-report-mode never` 再启动；没有上传崩溃报告。该选项使 Emulator 删除了未提交的 Crashpad 报告，旧进程 console、host sample 和 guest watchdog 证据此前已经独立保存。
2. 真实会话初始化约需 31 秒，超过当前 MCP 的 30 秒传输边界。两次同步构造未拿到客户端结果，但服务端建立了已识别会话；均先协调身份并删除，没有直接复制启动请求。随后通过保留 Future 完成同一个官方客户端构造。没有调整应用、图形、评分或预算规则。
3. 新临时层中的 VLC 没有所有文件访问权限。文件选择器返回的 fd URI无法播放，直接打开文件弹出权限请求。没有自动授权；用户选择“临时授权并继续”后才通过系统 UI 开启权限。完成后已经通过系统 UI 关闭。
4. 首次播放器教程及 Android 全屏提示被正常关闭。实验期间确实验证了播放状态，而不只是 VideoPlayerActivity 名称。

## 系统级证据

实验前后 boot ID 均为 `d7fa5bd9-83b9-446b-bf4f-3b0cddf6657f`，SurfaceFlinger PID 340、system_server PID 505 未改变。activity、settings、window 始终可用。

留存 Watchdog/SystemServer 日志中：0 次 watchdog 杀进程，只有 1 次初始 system_server 启动。新冷启动没有出现原来的 framework 重启循环。

## 清理与保留状态

- 独立核对 4 个服务端 session 创建与删除身份，全部匹配，没有未删除项。
- 两个未返回构造的孤立 session 经官方 AppiumConnection 删除；两个实际诊断客户端的 driver.quit() 均返回成功。最后一个 session 再查询为 HTTP 404。
- 临时 VLC 所有文件访问权限已关闭；AppOps 当前为 deny。先前状态为 default（有效权限同样未授权），不是声称权限记录逐字节恢复。
- 额外的应用自有目录试验文件已删除。
- Download 下原有视频已按冷启动基线字节恢复；恢复 SHA256：`2f077a7d79f7dd987ef5e8667cfaa39139cec3d3f5400471af2d45d70901bc5b`。
- VLC 播放已停止，界面返回 Android 启动器。
- VLC 的首次启动/教程状态由本次交互完成，未通过清数据将其撤销；这属于当前新临时层状态变化。
- 恢复后的模拟器及 Appium 保留运行，以维持恢复结果。诊断会话和后台执行线程已经结束。没有升级、重装或修改冻结测评代码、协议、清单。

设备执行可用不等于正式 readiness、预演与校准门禁已经重新通过。不能把本次对照验证作为正式 campaign 的门禁替代。

## 无窗口模式

`-no-window` 关闭宿主图形窗口，可减少部分宿主 UI 开销；不关闭 Android 显示、视频解码、屏幕合成和截图所需的图形处理。此次没有切换到无窗口模式，也没有测量节省量或证明其改善故障。

若后续做无窗口对照，应记录实际 Vulkan/GLES 后端。自动后端选择可能受启动条件影响，不能将渲染后端变化误算为仅关闭宿主窗口的效果。它是可验证的环境方案，不是已验证修复。

## 技能/驱动文档缺口（冻结资料未改）

- `contexts/tools/appium/troubleshooting/references/uiautomator2-session-startup.md`：socket hang up 不能只归到 helper/ADB；activity/settings 缺失时应先看 framework watchdog 和宿主图形栈。
- 已安装 UiAutomator2 README 的 mobile:startActivity：提供 legacy intent 时，action/uri 会被忽略；使用 component/action/uri 组合才能保留所需意图。带 `$` 的 Settings Activity 名需要处理 Android shell 转义。该差异已在实际启动输出中验证。
- AMKernel/Appium 长请求指导：MCP transport deadline 与 cell deadline 不同；超过传输边界时必须协调服务端 session 身份，不能盲目重建。首启教程也要求通过真正的播放状态/EOF 验证，不以 Activity 名替代。

## 证据入口

`independent-audit.json`、`cleanup.json`、`static-screenshots.json`、`video-without-screenshots.json`、`video-with-screenshots.json`、`video-no-shot-playing.json`、`video-no-shot-playback-log.json`、`post-controls-watchdog-log.json`、`final-platform.json`、`video-visual-proof.png`。稳定 Appium 请求证据另存 `appium-frozen.log`。
