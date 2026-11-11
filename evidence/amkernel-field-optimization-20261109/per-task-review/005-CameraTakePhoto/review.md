# CameraTakePhoto：第二个正常结束但官方失败任务

## 结论

**原始证据指向模型选错应用与错误完成判定，不是 BrowserDraw 的官方空 forest 判分机制。** 官方照片判据通过 ADB 比较 `/sdcard/Pictures` 前后文件名集合，不读取 accessibility forest。

相似处仅是“Agent 自报完成、官方返回 0”的外观，以及观察结果被误读；不能因此把两个任务归给同一 Appium/forwarder 根因。

## 冻结原证据

Campaign：`amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z`；episode `005-CameraTakePhoto/attempt-1`。

- 目标 `Take one photo.`，seed 3729977769；官方 reward 0.0，evaluator 无异常，耗时 0.021 秒。
- 5/10 个 UI 动作，非预算耗尽；16 次 python_exec 全部 completed、kernel alive、非 error；所属 session 创建/删除各 1，结果记录 absent。
- 官方 app 映射：`com.android.camera2/com.android.camera.CameraLauncher`；冻结 device-readiness.json:31–36 记录该应用存在。

### 最早偏离与后续轨迹

| python_exec | 原始行为／返回 | 判定 |
|---|---|---|
| 2–3 | Launcher；控件提取为空后读取截图 | 尚未选定目标应用 |
| 4 | tap(930,2195)，返回 `com.google.android.googlequicksearchbox` / `com.google.android.apps.search.lens.LensActivity` | 第一次 UI 动作已进入 Lens，不是已登记的相机应用 |
| 5–6 | 再次返回 Lens，并读取其截图 | 有机会识别并纠偏，但未返回找相机 |
| 7–12 | 在 Lens 内继续打开相机入口、授权；第 7 次调用标题明确为 Start the Lens camera | 偏离后继续执行 |
| 14 | tap(540,1990)，仍为 LensActivity | 把 Lens 搜索抓帧当成拍照 |
| 15–16 | 截图显示 Google Lens / Looking for results…，随后正常 quit | 没有证明照片已经保存 |

最终自报证据是 Google Lens 显示 captured image 和 Looking for results…，没有普通相机保存后可查看新照片的证据。

[原始第 15 次调用截图](original-image-15-Lens-result.png)由 raw-private/agent-events.jsonl 的原 image content 解码得到，73386 bytes，SHA-256 `6586e8f555d4614a2915ab983ee5acab7feff0a7eb1928282b299cbafdae2794`，与原 envelope 对齐。已实际读取图片，未操作设备或重跑任务。

## 为什么不像 BrowserDraw

冻结安装的 `android_world/task_evals/single/camera.py:103–129`：initialize_task 对 PHOTOS_DATA 做 ls；is_successful 再 ls；仅在 `len(after_photos - before_photos) == 1` 时返回 1。`env/device_constants.py:35` 指定 PHOTOS_DATA 为 `/sdcard/Pictures`。

因此 accessibility forest 为空不是这段判分的直接输入。历史没有保存 before/after 的实际目录列表，本次也未读取当前设备数据冒充历史状态：**只能确认新增文件数不等于 1，不能把 reward=0 直接翻译为绝对没有新增文件。** Lens 未证明完成目标与官方返回 0 一致，但不应伪造目录差集。

## controls=[] 的边界

Agent 多次只遍历 `root.iter('node')`，提取结果为空；它没有把原 XML 输出进 envelope。原 Appium master log 的同 session `/source` 四次请求均 200，响应大小分别 25828、61950、66007、10815 bytes（`evidence/screenshot-video-controls-20261106T231029Z/appium.log:58435–58494`）。因此不能把空提取列表当成 Appium 返回空内容，尤其不能等同于官方 forwarder 的空 forest。标签假设可能漏掉类名标签节点，但原 XML 未留存，具体漏选原因仍待证，未写成已确认根因。

## 归属与通用方案

- 主要归属：模型规划／目标身份核对，以及把临时预览、识图结果当成持久保存的错误完成判定。
- 技能指导方向：应用切换后核对实际 package/activity 与目标语义；有明显矛盾先纠偏，不因存在相机画面就当普通相机。验证用户所需的持久结果，不把 preview、搜索中或按钮成功返回当完成。
- 控件提取为空时检查原始 XML 的节点结构和实际匹配范围，不能直接宣布 UI 无内容。这是通用指导，不是为 CameraTakePhoto 写 package、路径或 evaluator 答案特例。
- 原有定位／状态验证方案适用；不需要为此修改 AMKernel Runtime/MCP，也没有证据说 BrowserDraw 的能力开关能解决本项模型错误。

本次为冻结证据复核，执行了原图解码及哈希对齐并读取原截图；未创建 session、未触碰现场设备、未修改生产代码／正式 skill／原 campaign，未把诊断结果替换原失败。
