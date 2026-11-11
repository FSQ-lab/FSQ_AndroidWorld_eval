# Revision4：官方时钟生命周期与稳定身份准入分离

## 实际失败与证据边界

原七天grant下，同grant资格通过；真实无Agent116预演在4/116 attempts后按原fail-closed停止。原`execution/rehearse/report.json`：qualified=false、haltReason=unknown_or_failed_cleanup。index0 AudioRecorderRecordAudio、1 AudioRecorderRecordAudioWithFileName、2 BrowserDraw均完整official生命周期，error=null、operationalErrors=[]、taskTearDown completed/environment closed、Agent=false、officialReward=null；evaluatorProbe0合法。

index3 BrowserMaze的原stderr完整保留在revision3/subsequent-phases-static-plan/execution/rehearse/process-003/process.log：`_episode → attest_readiness → _device_probe`抛`RuntimeError: existing official target must be API 33 and UTC; no automatic repair is authorized`。这是**admission**，在BrowserMaze environment/init/evaluator之前，不是import、task本体、FSQ能力或正式得分失败。原getprop返回值未持久化，因此不声称从原件还原API或timezone值。

该child exit1、forced=false、spawnCount1，未触其1930秒原cap；owned stage service exit2。Popen等待证明outer leader已退出并回收；此预演outer收据没有独立process-group disappearance观测，不能据此声称全局或所有descendants为零。原fallback record的task/environment cleanup unknown不改，亦不伪造BrowserMaze teardown。源码与stack能证明此任务未进入environment构造，故没有一个已创建BrowserMaze环境等待我们去quit；但这不能覆盖guest全局未知状态。前3个official close成功保持原证据含义。

原partial report/checkpoint/first3成功/第4unknown、旧资格/smoke、SDK/source历史产物均不重写、不重跑、不补评分。原grant依总管指令已**操作上终止**，字节/期限不改；FSQ-first独占保留，不把尚未到期的旧文件当继续执行许可，不resume第4。

## 唯一新设备观察，不能伪装成历史读值

仅按追加明确授权执行一次两条target-specific只读命令；详`current-target-property-observation.json`：
- 当前时刻2026-11-10T13:29:24.692241Z，ro.build.version.sdk=33、persist.sys.timezone=Asia/Shanghai，均rc0，完整stdout/stderr保留。
- 不是UTC等价别名；不是原失败瞬间的值。不把当前API33升级为证明历史API分支不可能。
- 没再读auto_time/auto_time_zone或其它属性；这些当前值仍未知。没root、restart、load_environment、改属性、task/model/评分或原check重放。

## 确切契约错误与因果限度

官方`BrowserTask.initialize_device_time`开启auto_time及auto_time_zone，teardown只关闭它们，**不把timezone恢复UTC**。BrowserDraw继承该逻辑且已有完整生命周期成功收据。AndroidWorld普通TaskEval和env_launcher另有各自clock准备：env_launcher.setup_env(freeze_datetime=True)调用官方datetime_utils.setup_datetime；TaskEval默认initializer准备reference date/time，而Browser特意覆写为自动时间。不能改官方任务或强制其任务体永远UTC来提分。

旧adapter却把timezone塞进device永久identity，且每题在environment/official clock setup之前强制`apiLevel==33 AND timezone==UTC`。合法Browser生命周期之后的时区变化会被下一题当成target漂移并提前阻断官方恢复。此冲突由源码直接证明，当前Asia/Shanghai观察支持它；不虚构原失败属性或把所有环境错误都归到它。当前证据没有显示API/hash漂移，也不宣称只看两属性就已全面认证target。

## 最小语义修复

运行时变更仅`fsq_campaign.py`：

1. `_device_probe`继续严验serial/console、API33、boot UUID/core services/core pids、app安装/version/APK hash；ABI/build/boot/screen/device/apps稳定字段继续与资格强绑定。**timezone不再进入stable device**。
2. 新`clock={timezone,autoTime,autoTimeZone}`只读观察与稳定identity分开。API失败诊断带实际API与clock；qualification错误收据保存实际clock，便于以后不再仅凭通用文案猜分支。没有放宽API/hash/source/model检查。
3. 新显式token **`prepare-clock`**。必须新授权明确包含它，并同时具有既有review/model/disposable/exclusive/qualify资格范围；先核对完整稳定target与pinned apps，再用现有official environment `freeze_datetime=True`调用官方clock setup。无自制setprop、不改host timezone、不先修再查target。
4. 准备独立记录before/after稳定identity及clock，要求identity不漂移、after为UTC/auto_time0/auto_time_zone0，环境close成功才prepared=true。恢复失败或cleanup unknown则prepared=false，保留可能已改变的clock，不伪装rollback。普通prepare-clock不跑task、snapshot全量重置、模型或oracle。
5. `qualify`仍**在任何environment mutation前**严格要求观察到UTC/auto00基线；不满足就失败，明确要求另授prepare-clock，绝不在失败分支偷偷修。readiness consumer同时验证`checks.utc`及结构化clock基线，不能只填flag绕过。
6. 每episode mutation前仍attest稳定identity；其后原有environment(freeze_datetime=True)及task initializer按官方职责准备clock。Browser自动时区语义保留，teardown不被adapter篡改成强制UTC；后续任务的正常官方setup负责其clock，而不是把前题合法可变状态误当设备换机。
7. prepare-clock通过现有parent/child preflight监督路径，**完整1210秒**，新输出`clock-preparation.json`；forced/missing report/unknown close不能prepared。原资格1210、全部task M/B/envelope、评分/kill/oracle/file隔离均不变。

这不是删除UTC基线检查、无条件改时区、等价别名特判或BrowserMaze特判。新基线必须由显式授权的官方prepare及后续真实资格收据建立。

## 离线证明

仅运行受影响`tests/test_fsq_campaign.py`：**82 passed，1.16s**，完整stdout/stderr见regression-final.json及logs；未重跑全313或R01–R08。新增消费者行为涵盖：
- timezone/auto-time合法状态变化后可继续稳定identity attestation；API/build/boot/APK hash漂移仍拒，且只读admission不偷偷修clock；
- qualification拒绝非UTC/auto-time-on而不创建env；explicit prepare后新资格才能通过；
- prepare须自身stage权限；UTC恢复失败与close失败保持false及真实partial effects/unknown；
- prepare前API漂移不触mutation，prepare中build/APK漂移也拒；
- readiness不能用UTC flag代替实际clock基线。

`offline-clock-entry-smoke.json`在独立临时root实际走新的`_episode prepare-clock → qualify`分支，使用离线property/environment协作者：Asia/Shanghai/auto11→UTC/auto00，两个entry exit0、prepared/qualified=true、close成功。它证明adapter entry状态转换，不是假装对真实设备恢复成功；没有执行真实任务/模型/ADB。临时root清除。`cli-help.json`实跑help，确认公开token为prepare-clock，无live。

## 新身份与限定review

新candidate SHA：`a8550aee3e1b9438377d34b5cf48ff4adde732785afe40aae2249f6266773030`。
新evaluator source tree SHA：`92b8bc71f0b26b19aacb1b23cd0944c3a3f614dbd46c72ab93076629590e2625`。

`source-closure.json`证明runtime delta仅fsq_campaign.py；116原冻结task rows逐值继承，未重生成clock-sensitive参数；SDK、AndroidWorld、provider/model、ADB/parser身份及target/protocol/budgets不变。新candidate gates全部pending，旧readiness/partial rehearsal/授权不迁移。

`review-handoff.json`绑定runtime、tests与README各SHA，只请求审这一clock语义/prepare/诊断与安全边界；建议独立只跑`pytest -q tests/test_fsq_campaign.py -k clock`，不重开无关R01–R08、全313、模型或设备门禁。当前待独立delta closure，不自签通过。

## 同target安全与下一步，不能无限等unknown

当前没有在运行的BrowserMaze Agent/业务worker；原stage已退出，前三环境有close成功收据，第四stack在环境创建前。但原fallback cleanup unknown、未独立证明的全局guest/helper状态继续unknown，不能把它改成clean或恢复完成。当前仅确认API33/AsiaShanghai，不足以单独放行任何任务。

可达的下一前提明确：独立review批准后，总管**新grant**显式授权prepare-clock及后续资格/全116前置。在稳定source/target/API/app pins准入不漂移的条件下，prepare建立并记录官方clock基线和owned env close；再fresh资格全门禁成功，才能全116从index0新预演。若稳定identity漂移或prepare/close/资格新失败，保留原始收据再停报，不循环试修、不杀未知服务，不为了清unknown冒充cleanup成功。

这次是无Agent环境生命周期验证，不是原业务题重试；但仍必须另授新candidate/grant，不自动执行。新的总grant若要接校准/正式须同一不可变授权绑定前置，run仍需总管读实际报告另令。旧102/97业务结果不补分、不再跑smoke，模型/Skill/提示不优化暴露任务。FSQ-first保留，释放只由总管明确决定。
