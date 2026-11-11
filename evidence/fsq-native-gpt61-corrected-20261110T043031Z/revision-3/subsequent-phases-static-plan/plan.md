# 冻结后续阶段静态计划：同一不可变总grant

当前仅静态准备：未签新grant、未启动新qualify/rehearse/calibrate/run，未探测设备或其他会话。candidate d9f3237c0d6d26f512bfdd3870fd4563519fc24f6cae160beb93a015a597a057 / review a693ebb96c2ef044beb33c9358a4dedb250a964c3e692a8c6bfc450c2915c1f6 / native model58d96868e5e4ccb139eb16e688178de0f2e9acbad40bc1f0035a293e0dd47323及源/SDK/任务保持不变。

## 总授权与真实stage token

已采纳总管选择：新不可变总grant `approvedStages=[qualify,rehearse,calibrate,run]`。正式真实token是 **run**，不是formal/full。`authorization-draft-frozen-stage-plan.json`已备，draft=true、issued/expires/resource窗口为null，尚不是执行授权。

实际签发时notBefore=真实now，validUntil=now+604800秒（7天），同一exact5554/AndroidWorldAvd/console5554/grpc8554/现ADB、真实用户已交接经w6:p2、exclusive/disposable/mutationsAllowed=true。总grant持有期限不是预估需时、不是业务budget；每题仍需剩余window覆盖其完整原envelope。不足停报，不能改原grant或暗中续期，不能为塞进window缩budget。

源码readiness与stage报告均绑定整个authorization SHA，且起止时间必须位于同grant；因此本总grant先正常qualify产新readiness，再产同grant rehearsal/calibration。当前97所属旧90m readiness不迁移；之后各stage之间不再换grant，不因换授权重做已完成阶段。常规source/import/receipt完整性检查照原入口进行，不重跑独立closure/test suite/native Responses模型门禁。

`run`仅列入技术schema授权；执行必须同grant所有前置操作门禁/cleanup通过，且总管读取真实收据明确启动。脚本额外要求届时显式 `FSQ_RUN_RELEASED_BY_COORDINATOR=yes`，不新设评分门槛，也不因approvedStages里有run就自动启动。

## 清单、依赖与计时

完整116顺序与每题index/name/family/M/各budget/paramsSHA在`plan.json.all116Order`，直接复制冻结manifest，不重新生成参数。116为91 android+25 information_retrieval；两轮都按原顺序全覆盖，不跳IR、不换任务。

| stage | 固定清单 | 入场依赖 | 完整每episode envelope秒 | Σ episode caps秒，非stage硬wall期限 |
|---|---|---|---:|---:|
| qualify | 全22-app设备/资产/快照/baseData正常资格 | 总grant、冻结candidate/review/model | 1210 | 1210 |
| rehearse | 原manifest index0…115，116项各一次 | 本grant新readiness | 1330–7930 | 225620 |
| calibrate | 下表原12固定顺序，各一次 | 同readiness＋本grant全116合格rehearsal | 1330–2770 | 18600 |
| run | 原manifest index0…115，116项各一次 | 同readiness＋同rehearsal＋同原12校准＋总管明确启动 | 1330–7930 | 225620 |

总Σ=471050秒，604800秒授权外余133750秒用于实际admission/driver/artifact验证等开销。**源码没有整stage全局watchdog**：总和只是episode child timeout预算和，不是整stage wall-clock严格上界或运行预估。强制停止、进程回收及宿主验证还可能有开销，不能虚称已施加7天硬stage watchdog。完整116的M范围10–120、B720–7320；校准M10–34、B720–2160。所有题B=max(600,120+60M)，完整envelope=B+610（close180/grace10/recovery120/overhead300），不改原cap。执行长stage不能外套3600秒等短工具deadline来砍掉原cap；采用可观察长进程，保留原per-episode watchdog/有限grant。

### 原12校准，不能因smoke结果改名单

| 序 | index | name | M | B秒 | 完整envelope秒 |
|---:|---:|---|---:|---:|---:|
| 1 | 102 | SystemWifiTurnOff | 10 | 720 | 1330 |
| 2 | 97 | SystemBrightnessMax | 10 | 720 | 1330 |
| 3 | 8 | ClockStopWatchRunning | 10 | 720 | 1330 |
| 4 | 9 | ClockTimerEntry | 10 | 720 | 1330 |
| 5 | 10 | ContactsAddContact | 12 | 840 | 1450 |
| 6 | 26 | MarkorCreateNote | 16 | 1080 | 1690 |
| 7 | 32 | MarkorEditNote | 12 | 840 | 1450 |
| 8 | 22 | FilesMoveFile | 20 | 1320 | 1930 |
| 9 | 63 | SimpleCalendarAddOneEvent | 34 | 2160 | 2770 |
| 10 | 5 | CameraTakePhoto | 10 | 720 | 1330 |
| 11 | 109 | TasksHighPriorityTasks | 10 | 720 | 1330 |
| 12 | 75 | SimpleCalendarEventsOnDate | 10 | 720 | 1330 |

这是事前已定的另一个phase，含102/97合法；不是重试/补评旧smoke。最后的SimpleCalendarEventsOnDate按原family/协议处理，不跳IR。每phase独立结果，不优化已暴露任务/提示/Skill/SDK来追分。

## 预演真实无Agent语义

不是mock/纯静态dry-run。每个冻结task重建后：创建真实official environment→reset/go_home→按依赖恢复pinned shared assets→strict official initialize_task→真实is_successful探针→strict tear_down→close。没有FsqAgent、模型调用、business worker或模型动作。源实现明确`agentInvoked=false`、`officialReward=null`；`evaluatorProbe`为合法有限0…1即可，0不使预演失败，也不计正式分。要求116生命周期/stages/覆盖顺序/params及cleanup均有效。

因而预演真实修改disposable guest（reference time、各任务数据库/文件/系统状态及snapshot恢复），并会对依赖OsmAnd任务做既有固定shared-map生命周期恢复；不是另开standalone prepare-map修复或装依赖。helper/adbd/已有AndroidEnv条件hostADB recovery沿用真人明确接受范围，不自行新增服务kill、重启guest/Appium或清别人session。

## 校准只判操作有效性，不要求高分

源`operational_errors`允许classification passed或failed，officialReward须有限且在0…1；要求完整native、exact provider/model/episode/summary、审计/预算、可信worker exit/group settlement、一次official evaluator且afterFullFsq/internalVerification、diagnostics绑定，以及实际cleanup。**无最低reward/通过率阈值**。kill absent/failed/denied/succeeded只验证观察与journal一致，不额外要求kill成功/指定main-final顺序、不补kill。原native FSQ返回/内部verify success不替代officialReward。

stage qualified要求全部固定attempt无operationalErrors且无halt，非12题全得1。97已经有有效official0，所以不是要求修能力后才测评的blocker。真实invalid/强制/unknown cleanup/evidence或全局drift依原fail-closed谓词处理，原记录保留、不自动重试。没有业务重试/resume，已存在输出目录不覆盖。

## 成绩与workspace隔离

原smoke102仍invalid_agent/null/0calls，97仍有效failed/0.0/1call；均不导入校准或正式reward。正式成绩只取run本身116个单次attempt，并保留valid/invalid/cleanup/coverage及带分母的统计。现有stage summary的reward均值分母为valid_official_rewards_only且标diagnosticOnly，不称官方leaderboard分数。

native episode identity使用campaign+stage+index；每个agent episode新建独占owned_root/workspace/.fsq和worker进程/新FsqAgent实例，旧目录存在即拒绝，不复用smoke或其它phase的workspace/上下文。私有frozen spec/expected/evaluator资料不送worker，只传正常初始化后的public goal；工作区仍受既有oracle/source/result-root隔离。目录级隔离不代表guest无影响，guest按official lifecycle恢复而非伪称native close复原。

## 精确命令与输出

`proposed-commands.sh`固化project、candidate、same AUTH与既有owned overlay；最终授权文件固定为本目录`authorization-approved-frozen-stage-plan.json`。入口均为 `.venv/bin/python -B -m fsq_androidworld_eval.fsq_campaign <token>`。

```bash
# 以下均未执行；只在总管后续实际签发并明确释放对应阶段后：
bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/subsequent-phases-static-plan/proposed-commands.sh qualify
bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/subsequent-phases-static-plan/proposed-commands.sh rehearse
bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/subsequent-phases-static-plan/proposed-commands.sh calibrate
# 只有总管读完真实前置收据并另下启动令：
FSQ_RUN_RELEASED_BY_COORDINATOR=yes bash evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-3/subsequent-phases-static-plan/proposed-commands.sh run
```

脚本实际flags：qualify输出`execution/qualify`；rehearse绑定`--readiness execution/qualify/readiness.json`；calibrate再绑定`--rehearsal execution/rehearse/report.json`；run再绑定`--calibration execution/calibrate/report.json`。各自新output=`execution/<stage>`，含checkpoint.jsonl、process-index/process.log、episodes/index-name/result.json及raw-private，最终report.json；qualify为readiness.json。每stage终态/cleanup立即同步，run前绝不自动串联。

## 已有真实交接，不新探测

97实际5/10 admitted writes，5成功、0拒绝/失败/inFlight，未触business deadline；模型kill一次成功，before native-return，relative-to-main-final unknown。outer/worker正常exit0、无强杀，official evaluator1次返回0、task teardown completed/environment closed/owned group disappearance observed；native close不保证guest恢复。已有qualify与smoke process.log只见ffmpeg warning和a11y retry，无hostADB restart专属诊断；未独立instrument，**不能说已证明没发生恢复**。不新查host/server/device/session。原日志/预算/kill/cleanup收据见`../next-qualify-smoke-097/actual-delivery.json`及actual-smoke-terminal.json。

FSQ-first继续独占，无其他会话probe，无AMK自动释放。所有新增文件只在本静态计划目录，不改candidate/源码/SDK/review closure或旧收据。当前仍无新live。
