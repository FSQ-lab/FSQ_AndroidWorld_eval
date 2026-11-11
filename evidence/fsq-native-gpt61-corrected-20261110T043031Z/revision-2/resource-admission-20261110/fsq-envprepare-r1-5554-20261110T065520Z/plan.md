# 官方固定地图准备＋一次新资格：最小可执行方案，尚未执行

新 run ID：`fsq-envprepare-r1-5554-20261110T065520Z`。当前仅为计划及 host/source 调查；不复用原失败输出、不改变 candidate／源码／模型／期望 hash，不执行设备、Appium、业务或新资格命令。

## 一、已交付的真实失败与 cleanup

完整终态见 `../actual-qualification-terminal.json`。原资格输出位于：

`../future-live-qualify-smoke-5554-7f139c2e/qualify/`

- 唯一资格 attempt：shell exit2，qualified=false；设备地图 `sha256sum` exit1；原 readiness SHA256 `b9827ef2398aa68e3b77e1ba96b48f8f6f5095240c01ac2c0013dc4643ed4018`，原 child readiness/checkpoint/process.log 永久保留。
- 原 `_adb` 的 `capture_output=True` 捕获过输出，但 `_qualification` 仅持久化异常 type＋str；两份 readiness 无 stdout/stderr，process.log 为0字节。**原错误文本在现存产物中不可恢复**。没有重跑失败命令，不能从 rc1 区分 ENOENT、不可读、权限／context。
- 失败前只完成只读设备／22 app 身份及 APK pins 检查；API33、UTC，bootId `0f36e370-012a-4423-a1f9-959beae8f90d`。环境 not_created，snapshotRestores=[]；无 gRPC environment、原生 u2/business worker、model call、task initializer 或官方评分。
- 资格外层子进程正常退出2，forced=false；同步 ADB client 已返回。无共享 Appium／模拟器停止、重启或 session 清理。没有声称全局进程／远端 effects 不存在。FSQ-first 保留，不自动释放 AMK。

## 二、能够确定的根因边界

不是 host 资产缺失或未通过 pin：`.cache/androidworld-assets/Liechtenstein_europe.obf` 已存在，原资格 host artifact identity 已通过。固定文件为7241271字节，SHA256 `57a1955c6f517a114999fa50480ecc1402ed9b524db602540ac1c08f57ff140e`，本调查未重算来确认旧失败。

官方目标目录／文件与资格使用完全一致：`/storage/emulated/0/Android/data/net.osmand/files/Liechtenstein_europe.obf`。同一现存 target 的历史 boot lineage 上，11月7日及9日 OsmAnd rehearsal 记录过 `restored_and_verified` 和相同 hash；不能称为“从未部署地图”。旧 campaign 初始 bootId 与本次失败一致；各单题地图 receipt 本身不独立记录 bootId，因此也不升级为当前可读性证明。

**确定的失败类别是 prepared-map 的设备读取前置未满足；当前是被移除还是权限／上下文变化，旧输出不足以定案。** 有明确的初始化顺序解释，而不是要求用户猜原因：资格的 map gate 在 `load_environment`、root／helper／gRPC、快照恢复之前，故它不会自动 provision／修复此资产。官方 private app 快照覆盖 `/data/data/<package>`，不包含该 external map；仅恢复 private snapshot 不能恢复此地图。

源据：`fsq_campaign.py:369-371,439-451,489-552`；`environment.py:256-285`；官方 `setup_device/apps.py:550-598`；历史具体路径见 `findings.json`。

## 三、不做“七数据库预造”的理由

当前 FSQ `_base_data` 在全部快照恢复后、任何 task.initialize 之前要求七个数据库非空。这是**比官方 pre-task 生命周期更强的附加条件**，不是一个已有“官方七库 bootstrap CLI”。冻结 evaluator-site 的 `task_evals/utils/sqlite_utils.py:149-152` 明确在缺表／库时启动 app 建库；`common_validators/sqlite_validators.py:257-263` 在 base initialize／snapshot 恢复前后调用该流程；Expense initializer 也会在缺表时调用官方 Expense setup。

官方 `setup.setup_app` 是 app.setup 后保存快照，部分 app 有显式 DB 初始化，部分仅启动／关闭；它不保证七库全部非空。历史 `present:false` 仅是历史探测结果，且旧嵌套 `sh -c` quoting 存在测量不确定性，不能说七库当时确实缺失，更不能推断当前状态。

因此本方案**不重置22 app、不重建／替换快照、不造 SQLite schema／文件、不把 task.initialize 或 noise insertion 偷放在准备阶段**。新资格若触发 DB gate，保留真实失败，报告这一生命周期契约差异，由总管决定独立适配修正／新 revision；本次不改或绕开该 gate，也不保证 map 修复即可资格通过。

## 四、最小真实准备及副作用

选择直接、target-specific、无重试的 ADB 操作，复现既有官方 map helper 的固定资产副作用，而不为了复制7.2MB地图先创建 AndroidEnv controller：

1. 新授权下核对既有5554设备 ready 及上述 bootId，防止换 target；不是复现旧 map hash。
2. 读 whoami。仅非 root 时 `adb -s emulator-5554 root`，随后有界 wait-for-device、核对 root 和 bootId。**可能重启 guest adbd／中断该 target 的 ADB transport，不是 guest OS reboot**。不 unroot 回滚，因为这是供资格使用的标准准备状态。
3. `mkdir -p` 官方地图目录。
4. 从既有 pinned cache `adb push` **一个**固定 map 到官方目标文件。
5. 依官方 copy helper 设置该文件 `chmod 777`，依 OsmAnd setup 设置 `chcon u:object_r:media_rw_data_file:s0`。
6. **写后**执行 SHA校验并与原固定 hash 比较；这是有实际状态变更后的验收，不是为确认旧失败而重复。完整保留每条受限命令 stdout/stderr/rc；不改 hash、放宽 predicate 或自动重试。
7. 每条 ADB client 有界等待；准备总 cap300秒（仅此操作安全上限，不改变 FSQ 的 M/B/outer）。失败即停，不启动新资格；保留可能的部分 map／root变化和 remote-effect unknown，不虚构回滚成功。

源据：`environment.py:256-285` 的 `restore_shared_assets`；官方 `file_utils.py:423-445` 的 copy＋chmod；`apps.py:581-598` 的 map＋context。提供的 `prepare_official_map.py` 只执行上述同等固定资产操作，不调用 task／model／DB／Appium，也不替换任何业务 Harness。

**无需** host SDK／系统／Python依赖修改、下载、编译、APK重装、guest OS reboot、新AVD、Appium／模拟器重启或他人 session 清理。现有 broad guest disposal/标准资产准备意愿已由用户批准；本次需总管一次明确纳入 **guest adbd root transport interruption＋固定 map 目录/文件/mode/context** 的具体执行范围，以及一轮新资格，不是再询问是否愿意评测。

### 既有 qualification 的条件性 host ADB 风险，不能隐藏

准备脚本不使用 AndroidEnv，因此不发 host `kill-server/start-server`、无 controller retry。**随后不变的资格程序仍会创建 AndroidEnv**：当前安装 `.venv/lib/python3.11/site-packages/android_env/components/adb_controller.py:116-145` 会在 device-specific ADB错误后重试并调用 `_restart_server`，后者会停止／启动共享 host ADB server。未找到可逐次禁用的公开开关。

这不是 host SDK／系统安装，也非必需发生的恢复操作，但确实是原路径的**潜在共享服务副作用**；不能承诺“任何失败下也绝无 host ADB restart”。总管应在新资格范围中明确接受此既有恢复边界，或指出不可接受而先停；本方案不偷偷 patch 已冻结 controller 来关掉它。原生 accessibility helper/网络服务初始化也是既有环境构造行为，非重装业务 app。本轮 map准备本身没有这些 controller/helper effects。

## 五、新授权与可执行命令，原失败不覆盖

预留新文件（尚不存在、不自签）：

`authorization-approved-envprepare-r1-qualify-smoke.json`

沿用标准 `fsq_execution_authorization`、同一 candidate `94a33fc...`、已批准 review `5a941e...`、已接受 model `58d968...`、exact5554/AndroidWorldAvd/8554/现ADB、真实 window/authority。明确允许本节 prepare effects；`approvedStages` 至少 qualify。仅在总管明确包含 smoke 时，才允许仍未消费的一次 index102 `SystemWifiTurnOff`。旧90分钟授权及原失败 receipts 不改、不隐式续签；新文件绑定新环境准备及资格输出。

准备好的三个独立分支在 `proposed-commands.sh`。**本调查均未执行**：

```bash
# 仅总管给出上述独立授权后：
bash proposed-commands.sh prepare-map
# 只有 prepare result.complete=true 且 mapStatus=restored_and_verified：
bash proposed-commands.sh qualify
# 只有新资格实际通过、剩余window覆盖1330s且新授权明确包含smoke：
bash proposed-commands.sh smoke
```

完整绝对路径已在脚本固化；所有分支无自动串联／重试。Python准备还要求显式 `--execute-under-new-grant`。资格与 smoke 沿用已有入口，预算不变；不会启动116预演／12校准／116正式。

新输出目录：本目录的 `execution/environment-prepare/result.json`、`execution/qualify/readiness.json`、可选 `execution/smoke-102-SystemWifiTurnOff/` 及其 `.outer/`。旧输出目录完全不写。

新资格会自然重新验证 source/import/model-receipt/candidate及新 auth 绑定；这不是重跑已接受的独立closure／model诊断。若旧 grant窗口或新 grant剩余无法覆盖后续完整 envelope，停止报告，不改已签receipt或缩业务计时。

## 六、现在可直接决定的范围

建议总管放行**一次标准固定地图 prepare＋一次新资格**，同时明确 adbd root 与原资格的条件性 host ADB recovery 边界；不批准七库预造或全量app/snapshot重建。资格若通过再按明确阶段授权执行唯一 smoke，否则原样停报，不再沿未知前置自动试错。

保持 FSQfirst。完成本范围后仍不自动释放 AMK；由总管按实际结果续签后续或明确不能继续后决定释放。
