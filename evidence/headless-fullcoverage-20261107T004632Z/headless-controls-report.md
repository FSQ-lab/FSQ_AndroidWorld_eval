# 无窗口环境资格前控制

同一 AndroidWorldAvd 已冷启动为 `-no-window`，未改变基础镜像、AVD 配置、serial、端口或显式 GPU 参数；未加载/保存模拟器快照，未清空基础数据。旧诊断会话均经查询为404，诊断 Future 已结束、Executor 已关闭，切换前实时 COW 副本已留存。这些副本不是经过关机验证的可恢复备份。

## 实际后端

启动日志显示 Vulkan 为 lavapipe/llvmpipe LLVM21.1.4，GLES 为 swangle/ANGLE SwiftShader LLVM10。原有窗口环境为 Vulkan lavapipe、GLES host/Apple Metal。后端变化是 Emulator 添加 `-no-window` 后的自动选择，不是显式 `-gpu` 切换。此次不能解释为仅改变宿主窗口的隔离实验，也不能证明原图形故障已永久修复。

## 已执行控制

| 场景 | Appium日志独立计数的截图请求 | 已观察结果 |
|---|---:|---|
| 启动器静态画面，间隔0.75秒 | 32 | 完成，23.712秒 |
| 视频初始视觉确认 | 1 | 实际画面显示Charlotte |
| 同一故障视频，无截图 | 0 | MediaSession PLAYING，VLC日志EOF，36秒终态为MainActivity，之后MediaSession STOPPED/inactive |
| 同一视频，间隔0.75秒截图 | 32 | 完成，23.598秒，单次最长0.481秒；采样图像实际显示Maria和Emilia |

视频SHA256：`8b01c2da29a1926302172bca43c6f7600e5d1b143a7870f4b5ddc7601b4e87cc`。通过真实UI关闭首启与播放器教程、系统全屏提示；没有把Activity名称代替实际播放证据。

控制前后boot ID为`0f36e370-012a-4423-a1f9-959beae8f90d`，SurfaceFlinger PID333、system_server PID500未变化；activity/settings/window服务可用，留存日志中watchdog杀进程计数为0。

## 清理与冻结边界

- 诊断仅建立一个官方Appium客户端会话，协商newCommandTimeout为300；保留同一个Future等待构造，未重放创建请求。
- `driver.quit()`返回，独立GET session为404，Appium日志一次创建与一次DELETE相匹配。
- 公共诊断视频已恢复冷启动原字节，SHA256为`2f077a7d79f7dd987ef5e8667cfaa39139cec3d3f5400471af2d45d70901bc5b`。
- VLC原有效所有文件权限为未授权；用户本轮授权通过系统UI临时开启。本报告时仍临时开启，以支持后续门禁/测评；结束必须恢复有效未授权状态。
- 冷启动临时层没有官方应用快照；已在任何资格重建之前检查并保留此事实及VLC真实首启状态。资格须正常重建临时层快照；基础数据不作清空。
- 原OMP备份`omp.1793971378851.67365.0.bak`为18.12.6，SHA256与冻结记录完全一致；本轮使用任务局部PATH别名，不使用全局18.17.0。冻结AMKernel与依赖的非Harness身份字段匹配。
- 指定冻结manifest文件SHA256与116项数量、MarkorCreateFolder冻结参数均已核对；未生成新参数。旧门禁不复用，此控制不是116项预演或12项校准的替代。

证据：`environment-mode.json`、`controls-http-independent-audit.json`、`static-control.json`、`video-zero-control.json`、`video-zero-playing.json`、`video-zero-end.json`、`video-zero-log.json`、`video-screenshot-control.json`、`video-frame-9.png`、`video-frame-26.png`、`diagnostic-cleanup.json`、`headless-post-controls.json`、`headless-watchdog.json`、`frozen-source-verification.json`。
