# Revision3：新资格＋原序下一题 smoke 静态草案

状态：仅草案，未签发新授权、未启动任何live阶段。w4:p2独立delta review已获总管接受（review a693ebb9…、live=false）；真实回执已绑定草案，不把review本身当live许可。

预留run ID：`fsq-r3-qualify-brightness-097-20261110T130116Z`。

## 原序选题，不按index大小／难度挑题

冻结 `CALIBRATION_TASKS` 开头是 `SystemWifiTurnOff`、`SystemBrightnessMax`、`ClockStopWatchRunning`。已消费的唯一102对应第一项；下一项是 **index97 SystemBrightnessMax**（原校准序第2/12），不是index103。没有跳IR；本次下一题本身就是android/settings任务。若后续原序遇IR，同样不跳过。本草案不许可消费其余校准项。

直接取revision3冻结task row，不重新生成参数。该题params SHA：`456814afbb5aa8d07a0c14120c26c55e140a617fa909024b135f7d04d76fd9c1`，json transport，complexity1。不把private params或官方判定值给业务worker，只传正常初始化后的public goal。

| 项目 | 固定值 |
|---|---:|
| index | 97 |
| M：admitted native write dispatch | 10 |
| B：max(600,120+60×M) | 720秒 |
| native close allowance | 180秒 |
| termination grace | 10秒 |
| force boundary：B+190 | 910秒 |
| recovery allowance | 120秒 |
| episode overhead | 300秒 |
| smoke完整envelope：B+610 | 1330秒 |
| 新资格完整envelope：600+610 | 1210秒 |
| 两阶段envelope之和，不含host admission开销 | 2540秒 |
| 建议实际签发后resource window，沿用90分钟 | 5400秒 |

Resource window不是业务计时器。签发时剩余window须足够两阶段及host admission开销；草案5400秒相对2540秒有余量。命令在新资格前检查剩余>=2540，新资格/单题入口继续按原完整各自envelope检查；新资格通过后、开97前必须再次剩余>=1330。任何不足都停止向总管报告，不缩B/cleanup/envelope、不自行续签或回填时间。

## 新资格正常全门禁，不附加修复阶段

完全沿用现有qualify：真实source/import/receipt绑定；device/API/UTC/APK pins；现有固定map只读hash检查；official gRPC core observation、ADB capture隔离；严格恢复22个既有app snapshots；7个app DB＋audio-recorder目录共8项baseData；结束环境cleanup与最终identity attestation。

地图上轮已成功prepare，本草案无prepare-map分支、不无因重新push/chmod/chcon。若正常资格读到新问题，保留失败并停，不自动修。无需装依赖/重装app、另跑真实model readiness、重复独立closure gate或提前task.initialize。新资格不是复用revision2 readiness；只接受revision3 candidate和本次实际授权绑定的全新readiness。

## Guest effects及安全边界

沿用真实用户已批准的exclusive/disposable/mutationsAllowed、official恢复、WiFi/native u2 helper、必要guest adbd root transport及原AndroidEnv错误时条件host共享ADB recovery，不重做身份或使用意愿表单。

资格允许上述正常官方snapshot恢复、helper/gRPC/ADB生命周期及观察；不重启Android OS/Appium、不清他人session、不手工kill未知进程或服务。

97的官方生命周期：base initializer设置官方reference device time、恢复settings既有snapshot；`SystemBrightnessMax.initialize_task`随后将亮度设为官方minimum。业务模型通过原生FSQ UI改变亮度（含按原预算计数的setup/teardown/model-issued kill）。官方terminal evaluator只在完整native返回、证据及owned process settlement准入后调用一次。teardown再次调用settings snapshot恢复/close recents。native `close`不等于guest状态恢复，不承诺结束后brightness/WiFi恢复成未观察的旧值；以实际receipts/unknown记录为准。

不改source/SDK/task/params/hash/predicate/预算，不造DB、不替换快照、不补旧102评分、不重试旧102或本次失败、不扩到116，也不自动释放AMK。

## 最终授权如何直接绑定

候选与model固定：
- candidate `d9f3237c0d6d26f512bfdd3870fd4563519fc24f6cae160beb93a015a597a057`；source tree `69158f28eadbcd1921bd58a4dd9207b7dcbc10d5fd2756507604313d163bf99c`。
- 继续引用真实native model58d968：revision2/native-model-success.json SHA `58d96868e5e4ccb139eb16e688178de0f2e9acbad40bc1f0035a293e0dd47323`，不新调用模型门禁。
- 已绑定w4:p2实际批准回执：`revision-3/independent-closure/report.json`，SHA `a693ebb96c2ef044beb33c9358a4dedb250a964c3e692a8c6bfc450c2915c1f6`；未复制revision2旧review5a941e，也未修改closure。
- exact target不变：emulator-5554、AndroidWorldAvd、console5554/ADB companion5555、gRPC8554；ADB `/Users/qunmi/Library/Android/sdk/platform-tools/adb`。

`authorization-draft-r3-qualify-smoke-097.json`是标准schema的**不可执行草案**：draft=true、review已绑定实际approved回执；签发/到期和resource notBefore/validUntil仍为null。没有创建approved授权文件。

总管接受review后可直接签放两阶段：从该草案签发新的 `authorization-approved-r3-qualify-smoke-097.json`，清除draft标记，沿用已绑定的真实review/model引用，notBefore=实际签发Unix时间、validUntil=notBefore+5400，issuedAtUtc/expiresAtUtc与之对应。approvedStages=qualify+smoke，stageLimits仅一次qualify＋一次97，原102明确排除。旧授权/旧收据不改、不回填过去时间。

## 精确命令

脚本已固化完整绝对路径、既有owned overlay及全新输出位置；无新安装或服务命令。**下列命令本次未执行**：

```bash
# 仅上述最终新授权存在、实际review通过后：
bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/next-qualify-smoke-097/proposed-commands.sh qualify
# 实际新资格通过且cleanup已知、剩余window覆盖1330后：
bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/next-qualify-smoke-097/proposed-commands.sh smoke
```

脚本分别调用既有 `python -B -m fsq_androidworld_eval.fsq_campaign qualify` 与 `python -B -m fsq_androidworld_eval.fsq_runner --stage smoke --task-index 97`；正常入口自然验证全部绑定，不另跑模型call/check凑准入。获得一次完整两阶段真实grant后无需再问第二阶段实施意愿：资格真实结果同步后，若条件满足即执行唯一97；失败／cleanup unknown／window不足立即停止。

输出全新且不覆盖：本目录 `execution/qualify/{checkpoint.jsonl,process.log,readiness.json,qualification/readiness.json}`；`execution/smoke-097-SystemBrightnessMax/result.json`及raw-private；`execution/smoke-097-SystemBrightnessMax.outer/{outer-process.json,standalone-result.json,process.log}`。实际native root由现有worker写到新campaign/episode identity，原102 root不动。每阶段同步rc/真实结果/partial effects/owned cleanup；启动事件不是通过证据。

验证仅 `/bin/bash -n`，exit0；已移除脚本executable位。没有执行任何草案分支或SDK/设备/模型/资格/评分命令。新增内容全在evidence目录，不改review中的四个implementation/test/doc文件或candidate。FSQ-first保留。
