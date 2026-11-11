# r4 FSQ 原生失败离线逐案分析：媒体、联系人与Markor

范围：001、007、008、009、010、011、023、024、027、029、030、032、033、036，共14例。本文只分析保留artifact；没有设备/ADB/模拟器操作，没有安装、构建、测试、任务重跑、评分或新模型调用，没有修改源代码/配置/旧结果。未来验证均未执行。

## 阅读约定与证据边界

- `BASE` = `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`（FSQ_AndroidWorld_eval根目录）。下表E为episode相对BASE路径，R为实际native run相对BASE路径。`S数字`是原始`agent-<tool>-数字`step后缀；`E数字`在段落内指该R的`events.jsonl/sequence`，与路径别名E001区分。
- 每例实际读取了原始public goal、native执行记录、完整events、native result、report、action audit、initialization、workerRequest、official evaluator diagnostics与worker outcome；读取相关UI XML，并实际渲染以下各案列出的截图。拼图仅内存显示、未写新图，不以截图路径/元数据冒充视觉证明。不同step自动截图和随后ui_snapshot是不同capture时刻，动态秒数不混作同一帧。
- 每例官方诊断接口均是scalar reward，无componentResults、logging records为空（不是证明没有发生错误）。保留官方奖励：027=0.5，其余本slice均0；native success/failed/inconclusive和模型总结不能覆盖官方分。
- `[事实]`=原始artifact/已核对源码支持；`[强推断]`=合理但缺最后一环；`[未知]`=保留证据不能判。实例的ReferenceTime是2023-10-15T15:34:00+00:00；2026 host时间只表示执行时间，不是任务日期。
- FSQ包sha256 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`。所引FSQ模块全部属于parent已与frozen逐文件hash匹配的16文件集合。源码路径均相对`FSQ/fsq_agent/`。producer另引每episode真实`raw-private/fsq-native/worker-site/fsq_androidworld_eval/fsq_native.py`快照；14份SHA256均`0af6d9b3802fcfd5708bc9dcdf2132bf48a9e3da01ae0401fafa6ae9ad468e13`，因此统一简称`producer::NativeDispatchBudget`，不冒用当前新代码。

### 共享机制定位（逐案再给适用因果）

| 标识 | 冻结源码/函数及行号 | 本文使用范围 |
|---|---|---|
| 启动/清理 | `drivers/android/_uiautomator2.py::UiAutomator2AndroidDriver.launch_app:94–100; kill_app:102–107; close:77–78` | app_start/app_stop调用后passed不等于已前台/状态不变；close是no-op |
| 文本替换 | 同文件`input_text:137–151` | click→可选clear_text→set_text；不按光标插入 |
| 目标寻址 | 同文件`tap_on:109–116; long_press_on:128–135; _selector/_selector_query:356–379` | target只匹配text，accessibilityId匹配description；动作通过不是业务操作完成 |
| 观察/断言 | 同文件`assert_visible:187–193; assert_state:205–221; ui_snapshot:237–276; _compact_ui_snapshot_attributes:321–335` | selector存在不证明持久化；text/content-desc/hint截50字符；视频内像素不在XML |
| Skill生命周期 | `resources/skills/android-harness.md:5–10,14–19,23–26` | 固定launch→业务验证→kill，与需保留运行/草稿页的意图有冲突风险 |
| 目标生成 | `agent/_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS:15–46; agent/_core.py::FsqAgent._augment_goal_only_task_with_pre_plan:145–164,201` | 单一verification_goal可遗漏合取子目标，生成后安装为Task目标 |
| 验证边界 | `agent/_verification_task.py::VerificationEvidenceBuilder.build:31–58; _load_artifacts:137–157; VERIFICATION_AGENT_INSTRUCTIONS:183–198; agent/_verifier.py::Verifier._from_payload:77–95` | 只验供给目标/历史tool文本和artifact预览，不重检像素，不自动恢复公开goal遗漏；载入runtime verdict |
| 原生预算 | 各episode producer `fsq_native.py::NativeDispatchBudget.dispatch:85–118; _finish:120–128; snapshot:134–142` | setup/teardown、失败写调用都计名额，超额在forward前拒绝；observation/assertion不计写；本slice无business deadline |

### 原始路径索引

| 案例 | episode E | native run R |
|---|---|---|
| 001 | `E001 = next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName` | `R001 = next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4` |
| 007 | `E007 = next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify` | `R007 = next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96` |
| 008 | `E008 = next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning` | `R008 = next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e` |
| 009 | `E009 = next-stage-plan/execution/run/episodes/009-ClockTimerEntry` | `R009 = next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4` |
| 010 | `E010 = next-stage-plan/execution/run/episodes/010-ContactsAddContact` | `R010 = next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240` |
| 011 | `E011 = next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft` | `R011 = next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998` |
| 023 | `E023 = next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader` | `R023 = next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061` |
| 024 | `E024 = next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent` | `R024 = next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0` |
| 027 | `E027 = next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms` | `R027 = next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd` |
| 029 | `E029 = next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes` | `R029 = next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9` |
| 030 | `E030 = next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote` | `R030 = next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa` |
| 032 | `E032 = next-stage-plan/execution/run/episodes/032-MarkorEditNote` | `R032 = next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53` |
| 033 | `E033 = next-stage-plan/execution/run/episodes/033-MarkorMergeNotes` | `R033 = next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f` |
| 036 | `E036 = next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo` | `R036 = next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947` |


## 案例 001 — AudioRecorderRecordAudioWithFileName

交叉核对：已核对、有保留（harness Early冻结源/trace复核）。audio_recorder.py:114–123→file_utils:228–258精确比较base/完整filename，无suffix normalize、DB或时间戳判据；S19目标AudioRecorder已证，不归前台oracle。实际路径未存，双.m4a仍仅候选。

### 目标与结果
公开目标要求在 Audio Recorder 录制并保存完整文件名 `presentation_fGwr.m4a`；未指定时长。官方奖励 **0**，FSQ main runner / verifier 均 success；两者不可互换。预算仅10/20，没有拒绝、超时或provider错误。

### 执行、偏离与直接失败
- E19/S1、E23/S3 两次 launch_app 都返回 passed，但截图仍是 launcher；S4 上滑、S6 点 Audio Recorder 后才进入录音页。这是最早可证的启动契约异常，不足以说明未安装或任何具体 Android 启动原因。
- S8 开始录音，S10 wait 3000ms，S11 停止进入 New name 对话框；总录音显示16s（交互耗时也在录音，不能把wait时长当总时长）。S13把带 `.m4a` 的完整名输入 `input_name`，S14 Save；S16/S17列表显示 `presentation_fGwr.m4a`、M4a、00:16；S18 exact text断言通过；S19 kill_app通过。
- [事实] 没有可证的录音/列表业务偏离；直接失败仅可确定为官方0与局部显示成功不一致。首个**证据覆盖收窄**在 `report.json/task.verification_goal`：将“保存指定文件名”降成“列表可见指定文字”，E65 verifier只证明后者。
- [候选，非已证实] 名称输入框的stem/扩展处理可能使显示名与实际完整filename不同，包括双.m4a可能性；本case没有实际路径，不据此定罪或建议无条件去扩展。harness冻结audio_recorder.py:114–123→file_utils:228–258已确认精确比较base/完整filename，不做suffix normalize，不读DB/时间戳，也不是前台判据。官方精确匹配失败的本次实际路径原因仍未知。

### 机制与修复
- 证据源：`R001/report.json`的task/agent_output、`R001/execution-result.json` verification，events E47–60，audit无denied。FSQ `agent/_core.py::FsqAgent._augment_goal_only_task_with_pre_plan:155–159,201`装入生成的验证目标；`agent/_verification_task.py::VerificationEvidenceBuilder.build:49–56`和 `Verifier._from_payload:77–95`不会补回未纳入目标的持久文件名语义；Android `assert_visible:187–193`只是selector存在。
- **MM-AUDIO（P1，FSQ preplan/Android应用知识owner）**：让生成的verification_goal保留“已保存、完整目标文件名、可重读”的约束；在实际应用可见的重命名/详情/导出确认页验证完整名，并由已确认的UI命名规则决定stem还是完整名，禁止根据隐藏答案硬编码去扩展。若UI无法证明实际名，只报证据不足，不报等价完成。边界：不能增加磁盘特权探测或私有oracle；也不能把所有带点名称都剥掉扩展。
- **MM-LAUNCH（P1，FSQ Android driver owner）**：`UiAutomator2AndroidDriver.launch_app:94–100`目前只调用app_start即passed；应只读核对实际前台/package readiness，区分“请求已发”与“目标已打开”，不靠重置/force-stop修复。未来验证：同预算录制含/不含显式扩展的公开目标，核对UI完整名与独立官方结果；验证启动返回状态真实。当前未运行。
- 剩余未知：录音实际完整路径及应用扩展追加/显示stem规则。官方检查路径/完整filename的类型已由冻结源码闭合；不得再保留DB、时间戳、前台作为官方判据候选。

### 原始证据入口与已看画面
- 公开目标：`R001/sources/000-goal.txt`；执行：`R001/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E001/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=10/20，attempted=10，denied=0，deadlineExceeded=False。
- 官方边界：`E001/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=success。
- 实际渲染：S1 `finalize/after-action`，`R001/artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-2b0856b54280.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S13 `finalize/after-action`，`R001/artifacts/screenshots/screenshot-agent-input-text-13-finalize-after-action-1-5b59be9892a0.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S16 `finalize/after-action`，`R001/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-d2fead1db26d.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=com.dimowner.audiorecorder | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Audio Recorder | passed  |
| S8 / E35 | tap_on：resourceId=com.dimowner.audiorecorder:id/btn_record | passed  |
| S10 / E39 | wait_ms：duration_ms=3000; reason=Allow a short audio clip to record. | passed  |
| S11 / E41 | tap_on：resourceId=com.dimowner.audiorecorder:id/btn_record_stop | passed  |
| S13 / E47 | input_text：resourceId=com.dimowner.audiorecorder:id/input_name; text=presentation_fGwr.m4a; textType=literal | passed  |
| S14 / E49 | tap_on：resourceId=com.dimowner.audiorecorder:id/dialog_positive_btn | passed  |
| S16 / E53 | tap_on：resourceId=com.dimowner.audiorecorder:id/btn_records_list | passed  |
| S18 / E57 | assert_visible：resourceId=com.dimowner.audiorecorder:id/list_item_name; text=presentation_fGwr.m4a; optional=False | passed  |
| S19 / E59 | kill_app：app_id=com.dimowner.audiorecorder | passed  |


## 案例 007 — ClockStopWatchPausedVerify

交叉核对：已核对、实质修正（harness owner亲读冻结installed clock.py后逐例回执）；删除此前已被源码否定的precondition mismatch与初始化异常候选，原reward0不变。

### 目标与结果
公开目标“Pause the stopwatch.”。冻结`clock.py::_ClockEval.initialize_task:116–118`调用`_close_clock_app:103–108`清data，`ClockStopWatchPausedVerify.initialize_task:177–184`明文初始已paused、00:00:00；因此00/Start是设计，不是异常前置态。官方 **0**；FSQ success；预算8/10，无denied，非动作/业务超时。原生preplan的elapsed retained不是公开额外要求，官方亦不查原会话身份或elapsed。

### 执行、偏离与直接失败
- S1/S3 launch通过但仍launcher，S4上滑、S6 Clock、S8 Stopwatch。第一次可见秒表为 **00/Start**（S8/S9），并不是已运行的用户秒表。
- E39/S10主动按Start，S11取快照，E43/S12按Pause；S14等待2s后的截图为08.46/Start，S15/S16断言Start和秒数字08；S17 kill_app成功。它证明kill前已暂停。Start→Pause是不必要的状态往返，但不能作为官方0的充分原因。
- [事实] 冻结官方`clock.py:194–208→43–63`只检查当前DeskClock UI、Start、至少两个Stopwatch文本，不检查原会话或elapsed。初始化已paused的事实否定“初始00来自预检/首次构造破坏原有运行状态”的旧候选；不再保留该解释。
- [主强推断] S17实际stop DeskClock破坏官方所需当前应用前台，与原0高度一致。缺少评分瞬间UI/kill后图，不能提升为已测postkill状态；也不以SDK app_stop推导秒表必定归零。2023参考时间不使用2026宿主时间替代。

包核对：`E007/raw-private/fsq-native/worker/request.json/appId`和`R007/execution-result.json/steps`中S17的`phase_reports[invoke].metadata.harness_output.app_id`均为`com.google.android.deskclock`，不是把默认kill目标凭任务名猜出来；但这些记录仍不含kill后业务状态。

### 机制与修复
- FSQ skill `resources/skills/android-harness.md:7–10`强制先launch、末kill；driver `launch_app:94–100`无就绪保证，`kill_app:102–107`直接app_stop。E59 verifier称“later kill_app是teardown、无reset证据”，不能据此豁免官方当前前台UI约束。官方源码级判据由harness owner亲读冻结installed源提供，本报告明确归属协作证据，不声称取得了评分瞬间画面。
- **MM-CLOCK-PAUSE（P0，FSQ Skill/主runner/verification owner）**：把暂停终态和所需前台保留到handoff，分离资源close与app_stop；当前已满足paused时直接验证而不启动新计时。修复不要求保留某个未被用户/官方要求的原会话或elapsed，也不以“必须先运行才可暂停”拒绝此合法初始化。
- 边界：不是移除所有cleanup；只处理业务末态与破坏性teardown冲突，不提前oracle或kill后重开补分。未来验证同时覆盖初态已paused00与运行后暂停，检查最终DeskClock/Start/Stopwatch UI及完整native返回后的交接；本轮未运行。
- 剩余未知仅保留本次评分瞬间UI/前台实读；初始化与UI-versus-service判据已由冻结源码闭合，不再作为待问候选。

### 原始证据入口与已看画面
- 公开目标：`R007/sources/000-goal.txt`；执行：`R007/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E007/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=8/10，attempted=8，denied=0，deadlineExceeded=False。
- 官方边界：`E007/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=success。
- 实际渲染：S8 `finalize/after-action`，`R007/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-8c921aabc64f.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S14 `finalize/after-action`，`R007/artifacts/screenshots/screenshot-agent-wait-ms-14-finalize-after-action-1-c806ac7f858b.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=com.google.android.deskclock | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Clock | passed  |
| S8 / E35 | tap_on：resourceId=com.google.android.deskclock:id/tab_menu_stopwatch | passed  |
| S10 / E39 | tap_on：resourceId=com.google.android.deskclock:id/fab; accessibilityId=Start | passed  |
| S12 / E43 | tap_on：resourceId=com.google.android.deskclock:id/fab; accessibilityId=Pause | passed  |
| S14 / E47 | wait_ms：duration_ms=2000; reason=Verify paused elapsed time stays unchanged. | passed  |
| S15 / E49 | assert_visible：resourceId=com.google.android.deskclock:id/fab; accessibilityId=Start; optional=False | passed  |
| S16 / E51 | assert_visible：resourceId=com.google.android.deskclock:id/stopwatch_time_text; text=08; optional=False | passed  |
| S17 / E53 | kill_app：app_id=com.google.android.deskclock | passed  |


## 案例 008 — ClockStopWatchRunning

交叉核对：已核对（harness owner冻结clock.py逐例回执）；actual Clock kill已双侧确认，前台破坏为主强推断，评分UI未留存。

### 目标与结果
公开目标“Run the stopwatch.”；目标交接时仍应运行。官方 **0**；FSQ main/verifier success，预算7/10，未耗尽。

### 执行、偏离与直接失败
- S1/S3 launch返回passed仍在launcher，S4上滑、S6 Clock、S8 Stopwatch显示00/Start。E39/S10点击fab启动；S11结构快照记录03.68及Pause（自动after-action截图更早为01.28，二者是不同capture时刻而非矛盾）。
- S12 wait2000后after-action截图10.23/Pause，同step随后UI XML为10.36/Pause；S13 XPath断言秒数>3，S14断言Pause，均通过，证明kill前运行。E51/S15随后kill_app成功，audit记录teardown计费；无评估边界截图。
- [事实] 首个可能破坏“交接时持续运行”的主动行为是S15 app_stop；runner自己总结“before teardown”。直接业务失败是官方0，不能把kill前正例当成已成功。
- [主强推断] 状态型目标被统一生命周期cleanup破坏，而verifier只判断此前证据，不检查交接后状态。冻结`clock.py:231–245→25–40`明确要求当前DeskClock UI、Pause与Lap，不读取service；因此不再保留“官方可能读service”的候选。S15实际stop Clock与原0高度一致，但缺评分瞬间UI，不能声称已测kill后状态。首个launch未前台化是独立异常。

包核对：`E008/raw-private/fsq-native/worker/request.json/appId`和`R008/execution-result.json/steps`中S15的`phase_reports[invoke].metadata.harness_output.app_id`均为`com.google.android.deskclock`，不是把默认kill目标凭任务名猜出来；但这些记录仍不含kill后业务状态。

### 机制与修复
- 源码：skill Case Lifecycle:7–10；`UiAutomator2AndroidDriver.kill_app:102–107`；`VerificationEvidenceBuilder.build:51–55`允许根据历史tool证据验目标；`Verifier._from_payload:77–95`直接采用verifier结论。本案E57 diagnostics承认kill_app后没有暂停/reset证据，却仍success，未检查有效证据是否覆盖最终交接。
- **MM-CLOCK-RUN（P0，FSQ Skill/runner/verification owner）**：将用户要求的持续状态写入执行结束不变量；本目标达成后不执行app_stop，资源close保持无业务副作用；verifier使用最后一个可能改变状态的动作之后的证据，不能仅以“teardown”名称豁免其影响。若无边界证据，inconclusive而不是历史success。
- 边界：不能默认“app在后台秒表必停”，不追加长时保持要求；官方只检查其现有当前UI规则。未来验证同预算开始→advancing→资源释放→native返回后DeskClock/Pause/Lap仍满足；本轮未运行。
- 剩余未知：008评分瞬间实际UI/前台；官方UI判据已闭合，service状态不是本例官方得分通道。

### 原始证据入口与已看画面
- 公开目标：`R008/sources/000-goal.txt`；执行：`R008/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E008/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=7/10，attempted=7，denied=0，deadlineExceeded=False。
- 官方边界：`E008/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=success。
- 实际渲染：S8 `finalize/after-action`，`R008/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-044b150b59ad.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S12 `finalize/after-action`，`R008/artifacts/screenshots/screenshot-agent-wait-ms-12-finalize-after-action-1-87332336f060.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S15 `prepare/before-action（不能当kill后屏幕）`，`R008/artifacts/screenshots/screenshot-agent-kill-app-15-prepare-before-action-1-80d5a1bf7423.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：默认 | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Clock | passed  |
| S8 / E35 | tap_on：resourceId=com.google.android.deskclock:id/tab_menu_stopwatch | passed  |
| S10 / E39 | tap_on：resourceId=com.google.android.deskclock:id/fab | passed  |
| S12 / E43 | wait_ms：duration_ms=2000; reason=Verify that elapsed stopwatch time advances. | passed  |
| S13 / E45 | assert_visible：xpath=//*[@resource-id='com.google.android.deskclock:id/stopwatch_time_text' and number(@text) > 3]; optional=False | passed  |
| S14 / E47 | assert_visible：resourceId=com.google.android.deskclock:id/fab; accessibilityId=Pause; optional=False | passed  |
| S15 / E51 | kill_app：默认 | passed  |


## 案例 009 — ClockTimerEntry

交叉核对：已核对（harness owner冻结clock.py逐例回执）；actual Clock kill已双侧确认，前台破坏为主强推断，评分UI未留存。

### 目标与结果
公开目标：0小时16分35秒，**不得启动**。官方 **0**；FSQ success；10/10只表示恰用完，所有写动作获准，没有budget denial。

### 执行、偏离与直接失败
- S1/S3 launch成功但launcher未变；S4上滑、S6 Clock、S8 Timer出现00h00m00s输入页。S10–13依次按1、6、3、5；UI过渡00:00:01→00:00:16→00:01:63→**00h16m35s**，中间63s是键盘录入显示，不能据此判最终非法。
- S14观察，S15 assert_with_ai返回passed，截图/结构均为输入键盘、00:16:35、Start可用；未发现Start动作。E53/S16 kill_app成功。无kill后输入页证据。
- [事实] 目标UI在S13–15真实达成；最早可证的业务风险是S16在要求保留未启动输入页时终止Clock。直接失败为官方0；不能编造“按过Start”或“数字输错”。
- [主强推断] 统一kill清理使评估不再见目标UI。冻结`clock.py:143–160→66–100`已确认要求当前DeskClock和匹配的输入UI，不要求内部运行timer实例，因此不再保留该旧候选。S16实际stop Clock已证，评分瞬间UI未留存，前台破坏不提升为实测；preplan“configured duration”不能反向授权启动。

包核对：`E009/raw-private/fsq-native/worker/request.json/appId`和`R009/execution-result.json/steps`中S16的`phase_reports[invoke].metadata.harness_output.app_id`均为`com.google.android.deskclock`，不是把默认kill目标凭任务名猜出来；但这些记录仍不含kill后业务状态。

### 机制与修复
- 源码：skill:7–10，driver `kill_app:102–107`；`VerificationEvidenceBuilder.build:51–55`和`Verifier._from_payload:77–95`只认已供的历史目标证据，没有teardown后屏幕检查。
- **MM-CLOCK-ENTRY（P0，FSQ Skill/runner owner）**：对“停在输入页/不启动”目标保留activity状态至handoff；不要为持久化而点击Start，也不要kill后再靠重开恢复草稿。最终验证以00:16:35、Start仍未执行且相同entry状态为准。目标意图来自公开goal，不读取隐藏期望。
- 边界：数字键盘录入本身本案正确，不改值、不放宽官方rubric、不增预算。未来验证：在原10写动作内留在entry页，验证资源关闭不离开该状态；另用启动timer目标证明条件分支不会漏清理。当前未运行。
- 剩余未知：009评分瞬间实际前台和timer输入UI；官方检查当前UI的契约已由冻结源码闭合，不再追问内部timer实例。

### 原始证据入口与已看画面
- 公开目标：`R009/sources/000-goal.txt`；执行：`R009/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E009/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=10/10，attempted=10，denied=0，deadlineExceeded=False。
- 官方边界：`E009/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=success。
- 实际渲染：S8 `finalize/after-action`，`R009/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-67200f92b7c7.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S13 `finalize/after-action`，`R009/artifacts/screenshots/screenshot-agent-tap-on-13-finalize-after-action-1-bc7577fc341f.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S16 `prepare/before-action（不能当kill后屏幕）`，`R009/artifacts/screenshots/screenshot-agent-kill-app-16-prepare-before-action-1-49fae0b3f991.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：默认 | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Clock | passed  |
| S8 / E35 | tap_on：resourceId=com.google.android.deskclock:id/tab_menu_timer | passed  |
| S10 / E41 | tap_on：resourceId=com.google.android.deskclock:id/timer_setup_digit_1 | passed  |
| S11 / E43 | tap_on：resourceId=com.google.android.deskclock:id/timer_setup_digit_6 | passed  |
| S12 / E45 | tap_on：resourceId=com.google.android.deskclock:id/timer_setup_digit_3 | passed  |
| S13 / E47 | tap_on：resourceId=com.google.android.deskclock:id/timer_setup_digit_5 | passed  |
| S15 / E51 | assert_with_ai：当前页面视觉断言; optional=False | passed  |
| S16 / E53 | kill_app：默认 | passed  |


## 案例 010 — ContactsAddContact

交叉核对：已核对（harness Early逐例回执）。官方持久Contact(name,clean number)，不是前台；姓名号码正确、Save未forward是充分失败，号码UI格式化不算错号，kill亦拒绝。

### 目标与结果
创建并保存Hugo Pereira，号码`+13920741751`。官方 **0**；native failed；预算12/12，Save和kill均被拒，不是模型超时。

### 执行、偏离与直接失败
- S1/S3启动仍launcher，S4上滑/S6打开Contacts。首次页是“No contacts yet”，有蓝色引导提示。E35/S8按Back不是只关引导，而是退回应用抽屉；S9重开后提示仍在，S10点具体`og_tooltip_scrim_view`才消除。
- S12打开Create contact；S14 First name=Hugo，S15 Last name=Pereira，S16 Phone输入+13920741751，UI格式化为+1 392-074-1751（是显示格式，不能称错号）；S17 Back收键盘。E57/S19 Save在dispatch前被budget拒；S20 kill同样拒绝。终屏仍Create contact未保存。
- [事实] 第一处业务路径可证的无效回退是S8；启动两次未前台化又支出额外动作。直接失败精确为Save未forward，不是“保存后没验证”。audit #37/#38记denied；此前12个写名额已经消耗。
- [强推断] app-launch就绪契约、引导层误处理和缺少预算感知共同挤掉提交；不能仅把maxActions=12本身称bug，更不应直接加大预算。

### 机制与修复
- 源码：`launch_app:94–100`无前台确认；skill:17–19要求按观测处理菜单，然而Back未验证是否为可关闭overlay；producer `NativeDispatchBudget.dispatch:85–118`setup/teardown也计费，失败保留reservation、超额before-forward；`input_text:137–151`一次计费复合清空设值，三次输入本身正确。
- **MM-CONTACT-SAVE（P1，FSQ Android driver/runner owner）**：可靠前台启动并提供真实ready结果；基于当前UI里的scrim精准dismiss，若Back离开应用立即标记该路径不能复用；将剩余写额度反馈runner并预留Save作为必需commit，不为验证前再隐藏键盘花掉最后提交名额。预算仍12，禁止把普通完成改成草稿成功。
- 边界：不要用硬编码坐标或Contacts内部数据库直写；资源清理不能优先于用户commit。未来验证：同12动作、带初次引导完成保存，再从详情UI核对名字/号码。当前未运行。
- 已核对官方读取持久Contact的name/clean number，不读取本例前台。剩余原诊断未留DB行；Save未forward已经足够解释未完成，不将kill或号码显示格式当直接失败。

### 原始证据入口与已看画面
- 公开目标：`R010/sources/000-goal.txt`；执行：`R010/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E010/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=12/12，attempted=14，denied=2，deadlineExceeded=False。
- 官方边界：`E010/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S6 `finalize/after-action`，`R010/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-5315bce08f5b.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S19 `finalize/after-action`，`R010/artifacts/screenshots/screenshot-agent-tap-on-19-finalize-after-action-1-f12542ab31ea.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=com.google.android.contacts | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Contacts | passed  |
| S8 / E35 | press_key：key=Back | passed  |
| S9 / E37 | tap_on：accessibilityId=Contacts | passed  |
| S10 / E39 | tap_on：resourceId=com.google.android.contacts:id/og_tooltip_scrim_view | passed  |
| S12 / E43 | tap_on：resourceId=com.google.android.contacts:id/floating_action_button | passed  |
| S14 / E47 | input_text：text=First name; text=Hugo; textType=literal | passed  |
| S15 / E49 | input_text：text=Last name; text=Pereira; textType=literal | passed  |
| S16 / E51 | input_text：text=Phone; text=+13920741751; textType=literal | passed  |
| S17 / E53 | press_key：key=Back | passed  |
| S19 / E57 | tap_on：resourceId=com.google.android.contacts:id/toolbar_button | failed NativeActionBudgetExceeded: action_budget |
| S20 / E59 | kill_app：默认 | failed NativeActionBudgetExceeded: action_budget |


## 案例 011 — ContactsNewContactDraft

交叉核对：已核对、有补实（harness Early逐例回执）。contacts.py:206–225从含invisible的forest读四字段，无独立activity前台；:35–138检查Work标签/hint邻接。S22实际仍Delete Mobile Phone且未选Work，不仅是键盘遮挡，kill拒绝未执行。

### 目标与结果
公开约束：First Grace、Last Taylor、Phone799-802-1530、Label **Work**，保持新联系人草稿，**不得Save**。官方 **0**；FSQ inconclusive；12/12，后续3写动作被拒。

### 执行、偏离与直接失败
- S1/S3仍launcher；S4上滑、S6 Contacts，S8 Back误退应用抽屉，S9重开，S10按scrim关闭提示，S12打开新建页；截图初始Label=Mobile。
- S14/15填姓名，S16 Back收键盘，S18填号码。S19和S20重复Back均在budget boundary被拒；S21快照数字键盘遮挡Label，S22 assert_with_ai失败说明Work不可见；S23 kill也拒。全trace**没有打开Label下拉或选择Work**，没有Save动作。
- [事实] 最早明确导航偏离同S8；独立、必需业务遗漏是Work从未被选择。不能只说“键盘遮住导致无法验证”——此前Mobile可见且无改label动作；即使看不到终值，执行链已证未完成选择。直接失败是必需label缺失，budget拒绝挡住修复，不是“未保存”失败；未保存正是要求。
- [补实事实] harness逐例复核S22实际仍有`Delete Mobile Phone`，与初始Mobile及全程没有选Work互相支持；因此不是仅缺视觉证明。冻结contacts.py:206–225从含invisible forest读四字段，:35–138检查phone Work标签/hint邻接；没有独立activity前台检查。缺组件日志仍不虚构字段实读值。

### 机制与修复
- 源码：`UiAutomator2AndroidDriver.press_key:153–160`只发Back；skill:17–19要求新观察定位、但统一末kill:7–10与草稿最终态不相容；producer `NativeDispatchBudget.dispatch:97–118`使已经耗尽后的同动作重试永不forward；`Verifier`最终inconclusive是诚实局部判断，非完成证明。
- **MM-CONTACT-DRAFT（P1，FSQ runner/Skill owner）**：用公开goal建立四字段+unsaved终态清单，Work选择必须有可见控件变更证据；优先完成label而不是耗尽后重复Back/无条件kill；已知不可恢复的action_budget直接停止写重试，仍允许只读收集证据。复用MM-LAUNCH节约前置动作。不得按“新建联系人一般需要Save”补提交。
- 边界：保留草稿生命周期，不以后台kill为清理手段；不能只把AI断言改成宽松匹配。未来验证：12动作内含tooltip场景完成Work，终态仍有Save按钮且未点；与010已保存目标对照。当前未运行。
- 已闭合：草稿oracle读取四字段含Work标签/hint邻接，并无独立activity前台条件；本轮kill被拒，不能归为实际cleanup破坏。剩余未知只保留未留存的评分forest/组件实读，不以没Save解释0。

### 原始证据入口与已看画面
- 公开目标：`R011/sources/000-goal.txt`；执行：`R011/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E011/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=12/12，attempted=15，denied=3，deadlineExceeded=False。
- 官方边界：`E011/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=inconclusive。
- 实际渲染：S12 `finalize/after-action`，`R011/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-a8c546093a48.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S18 `finalize/after-action`，`R011/artifacts/screenshots/screenshot-agent-input-text-18-finalize-after-action-1-087391fdda4f.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=com.google.android.contacts | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Contacts | passed  |
| S8 / E35 | press_key：key=Back | passed  |
| S9 / E37 | tap_on：accessibilityId=Contacts | passed  |
| S10 / E39 | tap_on：resourceId=com.google.android.contacts:id/og_tooltip_scrim_view | passed  |
| S12 / E43 | tap_on：resourceId=com.google.android.contacts:id/floating_action_button | passed  |
| S14 / E47 | input_text：text=First name; text=Grace; textType=literal | passed  |
| S15 / E49 | input_text：text=Last name; text=Taylor; textType=literal | passed  |
| S16 / E51 | press_key：key=Back | passed  |
| S18 / E55 | input_text：text=Phone; text=799-802-1530; textType=literal | passed  |
| S19 / E57 | press_key：key=Back | failed NativeActionBudgetExceeded: action_budget |
| S20 / E59 | press_key：key=Back | failed NativeActionBudgetExceeded: action_budget |
| S22 / E63 | assert_with_ai：当前页面视觉断言; optional=False | failed 视觉断言未通过 |
| S23 / E65 | kill_app：app_id=com.google.android.contacts | failed NativeActionBudgetExceeded: action_budget |


## 案例 023 — MarkorAddNoteHeader

交叉核对：已核对。替换误当插入→恢复→File settings不是rename；旧名/落盘字节未存，不假称磁盘核验。

### 目标与结果
把`2023_08_10_neat_wolf.txt`前加`RnI8sP34yDzJQbvkfplR`及一个空白行，保留原内容，并改名`busy_wolf_2023_07_23.txt`。官方 **0**；FSQ failed；预算12/12，非timeout。

### 执行、偏离与直接失败
- S1/S3启动仍launcher，S4上滑/S6 Markor；S8打开精确原文件，S9原文`Weekend plans: Hiking trip to Blue Mountain.\n`。S10 Move Home，E43/S11调用input_text只输入前缀和两个换行；after-action截图只剩前缀、原文消失，**这是首次已证业务偏离**，不是cursor移动未生效的猜测。
- S12观察、E47/E49搜索新旧artifact；S13再次input_text输入前缀+空白行+此前观察原文完整组合，S14 Save成功。恢复内容在结构快照截到50字，不应称屏幕缺失尾巴；实际工具参数含完整原文和换行。
- S15 Back只隐藏键盘，S17 More options、S19 **File settings**进入Wrap words/Syntax highlighting等设置，不是Rename；S21/S22试图退回均被budget拒；S23 kill也拒。始终未打开真正rename、无目标名输入、无最终保存重读证据。直接失败为文件未改名，不能仅归“坐标错误/超时”。

### 机制与修复
- [事实] Android `UiAutomator2AndroidDriver.input_text:137–151`固定click→clear_text→set_text，明确是**替换**，而主模型把它用作光标插入；按Move Home不改变该语义。skill/当前tool description“Enter text into a focused target”没有在这次计划中阻止误用。原文恢复虽可行，但耗掉一次input和导航，后续又错进设置，最终12额度耗尽；producer `dispatch:85–118`是确定的拒绝位置，而不是首因。
- `ui_snapshot:237–276`主动把text等裁到50字符，是恢复后只见前半的独立观测限制；`report.json/task.verification_goal`保留两个子目标，verifier没有将内容子目标误当整体成功。
- **MM-PREPEND（P1，FSQ Android driver schema/runner/Skill owner）**：让input_text对模型明确为replace-all；prepend任务先获取完整公开UI原文再一次设置`prefix + 原文`，不能以Move Home+replace当insert。若原文超过快照截断能力，必须提供有边界的完整控件文本读取或真正的插入能力，而非用50字截断副本覆盖。保留用户实际内容，不注入私有fixture答案。
- **MM-RENAME-PATH（P1，FSQ Markor知识/runner owner）**：从实际文件列表长按后可见Rename进入，区分编辑器File settings和文件操作；在原12额度内先完成必需rename，不在预算已尽后重试Back。边界：不能声称这条路径在本case执行过；它由024实际可见的Rename工具栏证据支持，未来仍须回归。未来验证：同预算前插、保留多行长原文、rename，并重开目标名检查无原文损失。当前未运行。
- 问 harness：官方评估前原文件内容是否已经正确保存、旧名是否仍在？需把“内容恢复成功/改名未做”与整体0分分别确认；无磁盘证据时只认Save工具成功不认持久字节已验。

### 原始证据入口与已看画面
- 公开目标：`R023/sources/000-goal.txt`；执行：`R023/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E023/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=12/12，attempted=15，denied=3，deadlineExceeded=False。
- 官方边界：`E023/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S8 `finalize/after-action`，`R023/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-3d9f31791253.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S11 `finalize/after-action`，`R023/artifacts/screenshots/screenshot-agent-input-text-11-finalize-after-action-1-4c13fc1d39f7.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S13 `finalize/after-action`，`R023/artifacts/screenshots/screenshot-agent-input-text-13-finalize-after-action-1-600b617876c8.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S19 `finalize/after-action`，`R023/artifacts/screenshots/screenshot-agent-tap-on-19-finalize-after-action-1-0d8222a488e8.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：text=2023_08_10_neat_wolf.txt | passed  |
| S10 / E41 | press_key：key=Move Home | passed  |
| S11 / E43 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=RnI8sP34yDzJQbvkfplR\n\n; textType=literal | passed  |
| S13 / E51 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=RnI8sP34yDzJQbvkfplR\n\nWeekend plans: Hiking trip to Blue Mountain.\n; textType=literal | passed  |
| S14 / E53 | tap_on：resourceId=net.gsantner.markor:id/action_save | passed  |
| S15 / E55 | press_key：key=Back | passed  |
| S17 / E59 | tap_on：accessibilityId=More options | passed  |
| S19 / E63 | tap_on：text=File settings | passed  |
| S21 / E67 | press_key：key=Back | failed NativeActionBudgetExceeded: action_budget |
| S22 / E69 | press_key：key=Back | failed NativeActionBudgetExceeded: action_budget |
| S23 / E71 | kill_app：app_id=net.gsantner.markor | failed NativeActionBudgetExceeded: action_budget |


## 案例 024 — MarkorChangeNoteContent

交叉核对：已核对。replacement正确、rename OK未forward，不套023原文破坏；持久字节仍未知。

### 目标与结果
将`strong_jacket_h1hZ.txt`内容精确改为`inNqu8UNNtyXBHCZpYp7`，并改名`lively_fox_2023_03_22.md`。官方 **0**；FSQ failed；12写动作耗尽。

### 执行、偏离与直接失败
- S1/S3仍launcher，S4上滑、S6打开Markor、S8打开原文件。S10 input_text完整替换为目标短文本，本案语义正确；S11 Back隐藏键盘、S13 Save成功、S14 Back返列表。
- S16长按原文件，工具栏有Rename，S18点击`action_rename_selected_item`；S20在`new_name`输入目标完整名；截图Rename仍悬浮、OK可见。E67/S21、E69/S22点OK都在budget前拒；S23 kill同拒。**输入rename字段不等于文件已重命名**，旧名仍在背景选中。
- [事实] 最早观测异常是S1已报告启动成功但并未前台化；业务编辑和rename路径本身没有已证内容偏离，首个不可完成动作就是S21未forward的commit。直接失败为rename未提交。额外launch/launcher导航耗费既有12额度、提交前未保留额度是强机制链，而非必须扩预算的证据。

### 机制与修复
- 源码：driver `launch_app:94–100`无就绪保证；`input_text:137–151`的替换恰为本目标所需；producer `NativeDispatchBudget.dispatch:97–118`拒绝点发生在forward前；`VerificationEvidenceBuilder.build:51–54`将dialog草稿与最终目标分开，本case verifier拒绝success合理。
- **MM-RENAME-COMMIT（P1，FSQ Android启动/runner owner，harness budget反馈配合）**：修复ready状态，避免两次无效launch；runner维护可见剩余额度并把rename的OK当必需commit，而不是字段输入后完成。确认过的`resourceId`路径本次正确，应保留，禁止通过宽松最终断言“目标名可见”把dialog文本当成功。budget exhausted时不重试同一OK；不加预算、不让producer豁免正常写操作。
- 边界：Save内容与Rename提交是两个状态，不能用前者代替后者；不能把本例改成023的“input_text插入问题”。未来验证：同12额度完成短文本replace、原名消失和新名可重开，重命名后扩展变化也正确。当前未运行。
- 问 harness：原文件内容子目标是否已持久成功？rename dialog未commit是否为官方0的直接解释？需保留scalar没有组件得分的事实。

### 原始证据入口与已看画面
- 公开目标：`R024/sources/000-goal.txt`；执行：`R024/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E024/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=12/12，attempted=15，denied=3，deadlineExceeded=False。
- 官方边界：`E024/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S8 `finalize/after-action`，`R024/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-2645c7976bc5.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S10 `finalize/after-action`，`R024/artifacts/screenshots/screenshot-agent-input-text-10-finalize-after-action-1-83db49e7bc1f.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S20 `finalize/after-action`，`R024/artifacts/screenshots/screenshot-agent-input-text-20-finalize-after-action-1-2623cec49827.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：text=strong_jacket_h1hZ.txt | passed  |
| S10 / E41 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=inNqu8UNNtyXBHCZpYp7; textType=literal | passed  |
| S11 / E43 | press_key：key=Back | passed  |
| S13 / E47 | tap_on：resourceId=net.gsantner.markor:id/action_save | passed  |
| S14 / E49 | press_key：key=Back | passed  |
| S16 / E53 | long_press_on：text=strong_jacket_h1hZ.txt | passed  |
| S18 / E59 | tap_on：resourceId=net.gsantner.markor:id/action_rename_selected_item | passed  |
| S20 / E65 | input_text：resourceId=net.gsantner.markor:id/new_name; text=lively_fox_2023_03_22.md; textType=literal | passed  |
| S21 / E67 | tap_on：resourceId=android:id/button1 | failed NativeActionBudgetExceeded: action_budget |
| S22 / E69 | tap_on：resourceId=android:id/button1 | failed NativeActionBudgetExceeded: action_budget |
| S23 / E71 | kill_app：app_id=net.gsantner.markor | failed NativeActionBudgetExceeded: action_budget |


## 案例 027 — MarkorCreateNoteAndSms

交叉核对：已核对。goal漏note是独立coverage缺陷；note1/SMS0仅强推断、原0.5保留。默认kill Markor且forward前拒，绝非已杀SMS。

### 目标与结果
公开goal有**两个子目标**：Markor创建`fair_ant_XOdi.txt`、指定文本；将完整笔记内容经Simple SMS Messenger发给`+13192815309`。goal串在文本与后一句连接处有`words.. Share`，模型本次输入`Actions speak louder than words..`；报告不以隐藏答案擅改标点。官方原奖励 **0.5** 必须保留，不能因native failed写成0。

### 执行、偏离与直接失败
- S1/S3启动仍launcher；S4/S6进入Markor空列表。S8新建对话框，S10名称stem=`fair_ant_XOdi`，S11扩展`.txt`，S12 OK；S14输入上述全文，S15 Back收键盘。E57/S17用`target:Save`失败“Target was not found”；S18重新观察后S19使用已见`action_save`成功。
- S20 More options→S22 Share→S24 Plain Text，系统sharesheet明确预览相同内容→S26 SMS Messenger进入New conversation→S28输入号码。S29按Enter后仍停在号码选择页；S30观察、E87–91查确认控件；E93/S31点击`new_conversation_confirm`因budget耗尽拒；S32默认kill同拒。没有进入短信编辑会话、没有Send、没有sent消息证据。
- [事实] 第一处业务路径错误是S17使用text fallback去找content-desc为Save的图标；`target:Save`与真实resourceId不是等价locator。S29 Enter未确认收件人但耗一个写动作。直接失败是短信未送出；note子目标有创建/写入/Save成功和分享全文的本地支持，官方0.5与此相容，但**不能从0.5无组件结果断言官方哪一半具体通过**。
- [事实] preplan/`report.json/task.verification_goal`只剩“sent outgoing SMS...”而没有独立持久note约束，是第二种问题：全目标被压缩为最后子目标。即使以后短信成功，verifier仍可能漏检笔记文件；本次并未因这一漏洞伪报success。

### 机制与修复
- 源码：`UiAutomator2AndroidDriver._selector:356–379`对target只按exact text，而accessibilityId按description；`tap_on:109–116`target missing也会消耗已admitted预算，producer `dispatch:105–127`明确失败不退额度。`FsqAgent._augment_goal_only_task_with_pre_plan:155–159,201`装入单一生成目标；`VerificationEvidenceBuilder.build:51–56`禁止补其他目标，解释子目标丢失。
- **MM-NOTE-SMS（P1，FSQ runner/Android知识owner）**：严格按当前snapshot把Save图标用resourceId/accessibilityId寻址，收件人使用可见confirm，不把Enter“工具成功”当语义确认；在既定18写动作内给confirm+Send保留额度，不增加预算或自动重试。完整goal必须保留“命名文件已保存 AND 指定完整内容发出”的合取，分别出证据，不把partial变成pass。
- 边界：不得把官方隐藏预期短信文本给模型，不放宽内容匹配；本次kill默认配置为Markor，且被拒**未forward**，不能写成“杀SMS导致失败”。未来验证：18额度原生分享全流程，对照文件持久内容和sent UI独立确认、验证只完成note仍保持partial而非改分。当前未运行。
- 问 harness：0.5各组件实际结果是什么、标点分隔如何解析？同意短信无Send；请区分note通过证据与仅模型Save声称。不要给未来模型私有答案。

### 原始证据入口与已看画面
- 公开目标：`R027/sources/000-goal.txt`；执行：`R027/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E027/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=18/18，attempted=20，denied=2，deadlineExceeded=False。
- 官方边界：`E027/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.5；native=failed。
- 实际渲染：S6 `finalize/after-action`，`R027/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-39a3daa797d6.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S14 `finalize/after-action`，`R027/artifacts/screenshots/screenshot-agent-input-text-14-finalize-after-action-1-aee3fbb79154.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S24 `finalize/after-action`，`R027/artifacts/screenshots/screenshot-agent-tap-on-24-finalize-after-action-1-d96cd7db4cdb.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S31 `finalize/after-action`，`R027/artifacts/screenshots/screenshot-agent-tap-on-31-finalize-after-action-1-6b52c401e1c7.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：target=Markor | passed  |
| S8 / E35 | tap_on：resourceId=net.gsantner.markor:id/fab_add_new_item | passed  |
| S10 / E41 | input_text：resourceId=net.gsantner.markor:id/new_file_dialog__name; text=fair_ant_XOdi; textType=literal | passed  |
| S11 / E43 | input_text：resourceId=net.gsantner.markor:id/new_file_dialog__ext; text=.txt; textType=literal | passed  |
| S12 / E45 | tap_on：target=OK | passed  |
| S14 / E51 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=Actions speak louder than words..; textType=literal | passed  |
| S15 / E53 | press_key：key=Back | passed  |
| S17 / E57 | tap_on：target=Save | failed Target was not found. |
| S19 / E61 | tap_on：resourceId=net.gsantner.markor:id/action_save | passed  |
| S20 / E63 | tap_on：accessibilityId=More options | passed  |
| S22 / E67 | tap_on：target=Share | passed  |
| S24 / E71 | tap_on：target=Plain Text | passed  |
| S26 / E75 | tap_on：target=SMS Messenger | passed  |
| S28 / E81 | input_text：resourceId=com.simplemobiletools.smsmessenger:id/new_conversation_address; text=+13192815309; textType=literal | passed  |
| S29 / E83 | press_key：key=Enter | passed  |
| S31 / E93 | tap_on：resourceId=com.simplemobiletools.smsmessenger:id/new_conversation_confirm | failed NativeActionBudgetExceeded: action_budget |
| S32 / E95 | kill_app：默认 | failed NativeActionBudgetExceeded: action_budget |


## 案例 029 — MarkorDeleteAllNotes

交叉核对：已核对。.app探索仅低效；无观察支持的grocery target才是明确偏离；选齐后Delete没执行。

### 目标与结果
公开goal“Delete all my notes in Markor.”，不授权删除内部应用配置。官方 **0**；FSQ failed；14写动作已用尽，3次denied。

### 执行、偏离与直接失败
- S1/S3仍launcher，S4/S6进入Markor，当前可见3个笔记与`.app`目录。S8进入`.app`、S10进入snippets发现空，S12/S13两次Back返根。此探索4个写动作没有删除任何note；“所有notes”可有跨目录意图，因此进入目录本身只标低效探索，不能单独定为错误。
- S15长按`art_project_sketches_st16.md`；S17 More options只有Clipboard/Move/Copy/Create shortcut/Share，S19 Back。E71/S21试图选择 **`grocery_list_st16.txt`**，当前所有观测均没有该文件，target not found并消耗一个额度。这是首次确定的无证据target业务偏离，不能从任务名推导grocery一定存在。
- S23、S24成功选另外两个可见笔记；3项都有红勾。S26/S27两次Delete均在budget前拒，未出现Confirm Delete，S28反向assert_visible第一个笔记通过、证明仍残留；S29 kill拒。直接失败为所有笔记仍在，没有已成功删除动作。

### 机制与修复
- [事实] 根目录3项可见、内部`.app/snippets`为空；没有证据证明其他全盘目录有多少note，也没有授予模型私有目录清单。根机制是模型未保持当前可见候选集合，进入无关菜单/空目录后仍花费写额度选不存在名字，producer `NativeDispatchBudget.dispatch:105–127`失败target消耗额度，最终必需删除没forward。
- FSQ `tap_on/_selector:109–116,356–379`按模型原样定位；skill:14–18要求当前可见locator和刷新观测；`Verifier`最终基于残留断言判failed正确，不是assert工具本身错。
- **MM-DELETE-SET（P1，FSQ runner/Markor知识owner）**：以当前UI建立“待删notes集合/真实子目录”而非模型想象名；选择前确保候选来自当前snapshot，内部`.app`不默认视为用户笔记；批量选择后立即Delete并确认，再核对余项，不为探菜单花掉commit额度。若确有用户文件夹，逐层只读检查后按公开UI明确范围，不整盘删除配置。
- 边界：不能用静默忽略missing target使budget看起来够用；保留失败名额原规则。未来验证：原14额度、三文件+空内部目录以及含真实用户子目录两种公开fixture，全删除而不删除配置；明确出确认与残留证据。当前未运行。
- 问 harness：此case初始化user notes范围是否仅这3项？`.app`是应用生成非note对吗？官方0是否全数残留？不存在的grocery target是否可确认不在任何当前页，而不向模型提供隐藏目录清单？

### 原始证据入口与已看画面
- 公开目标：`R029/sources/000-goal.txt`；执行：`R029/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E029/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=14/14，attempted=17，denied=3，deadlineExceeded=False。
- 官方边界：`E029/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S6 `finalize/after-action`，`R029/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-31345bf37029.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S10 `finalize/after-action`，`R029/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-079692c7fdc9.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S24 `finalize/after-action`，`R029/artifacts/screenshots/screenshot-agent-tap-on-24-finalize-after-action-1-80456295c312.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：text=.app | passed  |
| S10 / E41 | tap_on：target=snippets | passed  |
| S12 / E45 | press_key：key=Back | passed  |
| S13 / E47 | press_key：key=Back | passed  |
| S15 / E55 | long_press_on：text=art_project_sketches_st16.md | passed  |
| S17 / E61 | tap_on：accessibilityId=More options | passed  |
| S19 / E65 | press_key：key=Back | passed  |
| S21 / E71 | tap_on：text=grocery_list_st16.txt | failed Target was not found. |
| S23 / E77 | tap_on：text=backup_favorite_book_quotes.md | passed  |
| S24 / E79 | tap_on：text=final_budget_home_renovation.md | passed  |
| S26 / E83 | tap_on：accessibilityId=Delete | failed NativeActionBudgetExceeded: action_budget |
| S27 / E85 | tap_on：accessibilityId=Delete | failed NativeActionBudgetExceeded: action_budget |
| S28 / E87 | assert_visible：text=art_project_sketches_st16.md; optional=False | passed  |
| S29 / E89 | kill_app：app_id=net.gsantner.markor | failed NativeActionBudgetExceeded: action_budget |


## 案例 030 — MarkorDeleteNewestNote

交叉核对：已核对、有补正。official change_time来自ls -ll -au时间列，不等UI Last modified或ctime；候选是否最新仍unknown。确认未提交已充分失败，不反推选错。

### 目标与结果
公开goal“Delete the newest note in Markor.”，newest须由可见时间信息确定而非文件名猜测。官方 **0**；FSQ failed；10/10，确认删除两次被拒。

### 执行、偏离与直接失败
- S1/S3启动仍launcher；S4/S6进入Markor。可见`final_friendly_king.md` Last modified=10/15/2023 15:34，`fine_jelly_final.md`=15:17；`.app`=15:35但为目录，不是note。顶部系统时间14:29与这些fixture时间不同，只报告差异，不用2026 host时间推断排序。
- S8打开Sort by，S10 Back未改排序；S12长按final_friendly_king，S14 Info确认路径`/storage/emulated/0/Documents/markor`、15:34、24Bytes；S16 OK关Info；S18 Delete得到**Confirm Delete**对话框及准确文件路径。S20/S21两次OK都因budget denied，S22 kill也denied。
- [事实] 本次选中的note有可见时间支持为两note中较新者，没有证据证明“选错最新”。首个启动契约异常仍是launch passed但launcher；业务删除流程首个确定不能达成点为S20确认未forward。直接失败是待删确认未提交、文件仍在，不是把打开对话框当删除成功。

### 机制与修复
- 源码：`launch_app:94–100`返回仅dispatch通过；producer `NativeDispatchBudget.dispatch:97–118`精确阻断确认。Skill:14–18合理要求当前证据，但缺预算反馈导致模型在已显示足够比较时间后仍打开sort、Info各往返，10额度耗尽。read/search本身不计写；应区分观测成本与实际导航写成本。
- **MM-DELETE-COMMIT（P1，FSQ runner/Android启动owner）**：保留“最新note不是目录”判据，并复用已有完整可见时间比较，避免可选sort/Info往返；可靠启动避免重复launch；预算反馈中为Delete+确认预留两次写。在能见时间不足时仍允许查Info，不能为了省动作猜文件名；预算不足应诚实失败而非扩大额度。
- 边界：不按隐藏mTime选对象，不将“final”词当最新；未来验证：原10额度，日期逆序、目录更新较晚、同名相似note场景，删除后原路径不见而另note保留。当前未运行。
- 官方时间来源已核对为`ls -ll -au`时间列，不等同UI Last modified/ctime；本次候选是否符合官方newest仍未知。确认未forward已经充分失败，不需补测或反推选错；未来方案应先闭合公开UI时间语义而非把现有Last modified自动等价为oracle时间。

### 原始证据入口与已看画面
- 公开目标：`R030/sources/000-goal.txt`；执行：`R030/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E030/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=10/10，attempted=13，denied=3，deadlineExceeded=False。
- 官方边界：`E030/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S6 `finalize/after-action`，`R030/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-51094837655a.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S14 `finalize/after-action`，`R030/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-35063181934b.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S18 `finalize/after-action`，`R030/artifacts/screenshots/screenshot-agent-tap-on-18-finalize-after-action-1-f08566ab17c1.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：resourceId=net.gsantner.markor:id/action_sort | passed  |
| S10 / E41 | press_key：key=Back | passed  |
| S12 / E47 | long_press_on：text=final_friendly_king.md | passed  |
| S14 / E53 | tap_on：resourceId=net.gsantner.markor:id/action_info_selected_item | passed  |
| S16 / E59 | tap_on：resourceId=android:id/button1 | passed  |
| S18 / E65 | tap_on：resourceId=net.gsantner.markor:id/action_delete_selected_items | passed  |
| S20 / E69 | tap_on：resourceId=android:id/button1 | failed NativeActionBudgetExceeded: action_budget |
| S21 / E71 | tap_on：resourceId=android:id/button1 | failed NativeActionBudgetExceeded: action_budget |
| S22 / E73 | kill_app：app_id=net.gsantner.markor | failed NativeActionBudgetExceeded: action_budget |


## 案例 032 — MarkorEditNote

交叉核对：已核对。两Undo是合理恢复；最终buffer正确、Save未forward；autosave/最终字节unknown，不称磁盘必旧。

### 目标与结果
给`note_SiFbv.txt`顶部增加`Hello, World!`并保留原文；并非要求使用特定“插入”手势，最终内容正确即可。官方 **0**；FSQ inconclusive；12/12，Save和kill被拒。

### 执行、偏离与直接失败
- S1/S3仍launcher，S4/S6进入Markor；S8打开精确目标（列表另有`note_SiFbv_final.txt`，模型没有误选相似名）。S9观察原文`Don't forget to water the plants while I'm away.\n`。
- S10 Move Home，S11 input_text只给`Hello, World!\n`后原文消失，这是首个可证业务偏离。S12 Back，S14 Undo后编辑器为空，S16第二次Undo才恢复原文；两次Undo是对真实替换/clear过程的恢复，不应笼统叫无意义重试。
- S18完整replace为前缀+原文，S19 Back收键盘；S20 Save因budget denied；S21 assert_state passed/exists=true，证明当前editor匹配目标text但不证明已保存到文件。S22 kill拒。未离开并重开文件、没有持久字节证据。
- [事实] 官方0与“正确buffer但无Save”相容；直接可证阻断是显式Save未forward。Markor自动保存是否已发生未知，不能把未Save工具成功就断言磁盘必旧，也不能因editor断言通过当持久成功。runner plan_updates称“did not preserve insertion-only interaction”是模型自加判据；公开goal**没有规定插入-only交互**，不据此增加失败理由。

### 机制与修复
- 源码：`UiAutomator2AndroidDriver.input_text:137–151`固定清空替换；`assert_state:205–221`此参数是在selector中匹配text后返回exists=true，不执行文件持久验证；`ui_snapshot:237–276`text限50字，长文件不能只靠其预览恢复；producer `dispatch:97–118`挡最后Save。
- **MM-EDIT-PERSIST（P1，FSQ driver schema/runner owner）**：明确replace语义，先读取完整可见原文再一次构造前缀+原文（与023共用MM-PREPEND）；为Save和必要重开持久核对保留额度。验证只检查用户要求的最终内容/文件身份，不要求特定手势；对buffer和persisted文档分别标记证据。
- 边界：长文本若截断不得覆盖丢尾，不以“只要Hello可见”放宽保留原文约束；不从私有期望重建原文。未来验证：12额度短/长多行笔记prepend，保存重开字节/内容等价，另验证未保存buffer不误报success。当前未运行。
- 问 harness：本案Markor是否自动保存、官方读取的目标文件在评估时是什么？若未留下数据，直接原因应写“持久状态未证+官方0”，不要把显式Save被拒等同自动保存被禁。

### 原始证据入口与已看画面
- 公开目标：`R032/sources/000-goal.txt`；执行：`R032/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E032/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=12/12，attempted=14，denied=2，deadlineExceeded=False。
- 官方边界：`E032/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=inconclusive。
- 实际渲染：S8 `finalize/after-action`，`R032/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-2ab8cf309b6b.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S11 `finalize/after-action`，`R032/artifacts/screenshots/screenshot-agent-input-text-11-finalize-after-action-1-51ba7c07cb66.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S18 `finalize/after-action`，`R032/artifacts/screenshots/screenshot-agent-input-text-18-finalize-after-action-1-edc386e52127.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：text=note_SiFbv.txt | passed  |
| S10 / E41 | press_key：key=Move Home | passed  |
| S11 / E43 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=Hello, World!\n; textType=literal | passed  |
| S12 / E45 | press_key：key=Back | passed  |
| S14 / E49 | tap_on：resourceId=net.gsantner.markor:id/action_undo | passed  |
| S16 / E53 | tap_on：resourceId=net.gsantner.markor:id/action_undo | passed  |
| S18 / E57 | input_text：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=Hello, World!\nDon't forget to water the plants while I'm away.\n; textType=literal | passed  |
| S19 / E59 | press_key：key=Back | passed  |
| S20 / E61 | tap_on：resourceId=net.gsantner.markor:id/action_save | failed NativeActionBudgetExceeded: action_budget |
| S21 / E63 | assert_state：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor; text=Hello, World!
Don't forget to water the plants while I'm away.
; optional=False | passed  |
| S22 / E65 | kill_app：app_id=net.gsantner.markor | failed NativeActionBudgetExceeded: action_budget |


## 案例 033 — MarkorMergeNotes

交叉核对：已核对、有补正。空目标、缺两源、重复Copy后没写均一致；official严格完整路径等值，默认.md为独立缺口，另要求两个空行形成5行结构，不再保留后缀normalize未知。

### 目标与结果
依次合并三个指定源文件，段间两个空行形成5行结构，另存完整目标路径对应note `mIObBbo4`。harness冻结判据已确认严格完整路径等值，不做后缀normalize。官方 **0**；FSQ failed；**26/78，未耗尽、无denied、businessDeadlineReached=false**；execution window自述非timeout。

### 执行、偏离与直接失败
- S1/S3仍launcher，S4/S6 Markor；S8打开第一源，内容非空`m4kMyOGWaENoPj6FqLjd\n`。S10长按、S12 Select all，S13 Copy均passed；S14/S15 Back关键盘返列表。S17新建，S19名称`mIObBbo4`，默认扩展`.md`，S20 OK创建空目标。
- S22在目标长按后**只出现Autofill，不出现Paste**；E79/S23仍请求`target:Paste`，target not found。此为第一次确定的业务动作偏离：当前菜单无此项仍按记忆调用。不能仅凭Copy返回passed认定clipboard里有目标内容；现有artifact未采集clipboard，系统剪贴板跨app/secure字段/文本输入为何不可粘贴未知。
- S24观察仍空，E83–95多次读/搜索artifacts排查；S25/S27/S29 Back逐步回列表；S31再开第一源，S33长按、S35 Select all、S37 Copy再次passed，S38/S39返回；**S41重开目标后没有再次Paste或input_text**，直接S43 assert_with_ai失败、S44 kill Markor成功。没有打开第二/第三源、没有写合并文本；最终真实截图为空。
- [事实] 目标`mIObBbo4.md`空白已充分失败；另默认.md与官方严格完整目标路径不等，是独立命名缺口，不能再留后缀normalize候选。合并内容还需两个空行形成5行结构。26/78仍有52写、没有max_turns或business deadline错误。

### 机制与修复
- 源码：`long_press_on:128–135`、`tap_on:109–116`、`_selector:356–379`只做当前selector操作，不保证Copy→Paste业务完成。skill:14–18要求重观测；模型却在Paste未出现时调用，然后恢复后没有继续写入。`input_text:137–151`可完整替换目标，用**公开UI读取到的三源全文**构造合并是一条可实现路径，但未执行过不能冒称成功。
- **MM-MERGE-CONTENT（P1，FSQ runner/Markor知识owner）**：把每源全文/顺序/目标内容累积作为状态，Copy只记尝试而不当目标完成；Paste入口不存在则停止该假设，在不读取私有oracle的前提下读取UI已授权的源全文并明确一次写合并，或先验证clipboard/可见Paste再继续；第二次Copy后必须验证目标实有内容，不能以复开空文件结束。保留原78额度，不新增盲重试。
- 边界：内容可能长于50字，`ui_snapshot:237–276`不可当完整文本；需合法完整控件文本能力，否则inconclusive并保存证据，不能拿预期答案凑合并。未来验证：空目标、clipboard无Paste、有换行和长源，三源均重读并按顺序核对保存后目标；保留源不改写。当前未运行。
- 已核对官方严格完整路径及5行/两个空行结构。剩余未知仅保留clipboard为何没有Paste与未留存的实际剪贴板；不把输入新名改变clipboard当已证根因。未来写入须同时符合准确完整目标路径和分隔结构，不无条件追加.md。

### 原始证据入口与已看画面
- 公开目标：`R033/sources/000-goal.txt`；执行：`R033/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E033/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=26/78，attempted=26，denied=0，deadlineExceeded=False。
- 官方边界：`E033/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S8 `finalize/after-action`，`R033/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-5ba642fe3f72.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S22 `finalize/after-action`，`R033/artifacts/screenshots/screenshot-agent-long-press-on-22-finalize-after-action-1-918cf9e4e43c.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S41 `finalize/after-action`，`R033/artifacts/screenshots/screenshot-agent-tap-on-41-finalize-after-action-1-95b87f2206e6.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：默认 | passed  |
| S3 / E23 | launch_app：app_id=net.gsantner.markor | passed  |
| S4 / E25 | swipe：direction=up | passed  |
| S6 / E31 | tap_on：accessibilityId=Markor | passed  |
| S8 / E37 | tap_on：target=tough_frog_2023_08_05.txt | passed  |
| S10 / E41 | long_press_on：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor | passed  |
| S12 / E45 | tap_on：target=Select all | passed  |
| S13 / E47 | tap_on：target=Copy | passed  |
| S14 / E49 | press_key：key=Back | passed  |
| S15 / E51 | press_key：key=Back | passed  |
| S17 / E61 | tap_on：resourceId=net.gsantner.markor:id/fab_add_new_item | passed  |
| S19 / E67 | input_text：resourceId=net.gsantner.markor:id/new_file_dialog__name; text=mIObBbo4; textType=literal | passed  |
| S20 / E69 | tap_on：target=OK | passed  |
| S22 / E77 | long_press_on：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor | passed  |
| S23 / E79 | tap_on：target=Paste | failed Target was not found. |
| S25 / E89 | press_key：key=Back | passed  |
| S27 / E97 | press_key：key=Back | passed  |
| S29 / E101 | press_key：key=Back | passed  |
| S31 / E105 | tap_on：target=tough_frog_2023_08_05.txt | passed  |
| S33 / E109 | long_press_on：resourceId=net.gsantner.markor:id/document__fragment__edit__highlighting_editor | passed  |
| S35 / E113 | tap_on：target=Select all | passed  |
| S37 / E117 | tap_on：target=Copy | passed  |
| S38 / E119 | press_key：key=Back | passed  |
| S39 / E121 | press_key：key=Back | passed  |
| S41 / E125 | tap_on：target=mIObBbo4.md | passed  |
| S43 / E129 | assert_with_ai：当前页面视觉断言; optional=False | failed 视觉断言未通过 |
| S44 / E131 | kill_app：app_id=net.gsantner.markor | passed  |


## 案例 036 — MarkorTranscribeVideo

交叉核对：已核对、有capture口径保留。harness已亲看S16 Emilia、S21 Charlotte；三词散落不等完整时序main覆盖，S31明确kill VLC。S15截图约05s与invokeXML7.9s属不同capture可能，保留差异不拼为同帧或主失败。

### 目标与结果
观看Download内`ZwUN_moment_70_.mp4`，按每帧字符串顺序生成仅逗号空格分隔的内容，写入Markor `ZwUN_moment_70__transcription.txt`。官方 **0**；FSQ failed；17/20、无denied、无business deadline。不得以视频缩略图或单帧代替完整序列，更不把私有转录答案交给模型。

### 执行、偏离与直接失败
- worker默认appId是Markor，但E19/S1明确launch **VLC**，返回output.app_id=`org.videolan.vlc`后仍launcher；S3/S5上滑找到VLC，S7打开扫描列表，S9滑动后目标24s视频可见，S11打开进入教程，S13点close。
- S14截图约00:04显示Maria，结构不含像素单词；S15截图约05s而原invokeXML为7.9s，capture不同且不推成同一瞬间。S16请求player_overlay_play未找到，after-action图显示Emilia；S17旧player_root未找到后视频结束。首个可证控制缺口是未稳定暂停/起点便依赖自动隐藏控件，时序丢失；不拿capture差异当主失败。
- S19重开；S21显控截图08s显示 **Charlotte**，S22快照后S23 play target又未找到、回列表；S25再开、S27 Space；S28已有AI视觉断言解释当前字符串Charlotte（真实保留截图亦清晰），但只覆盖单帧。S29 player_root再次missing后回列表，S30观察；E95 read_file相对本地workspace路径失败，E97用read_artifact_slice恢复该AI断言结果。S31显式kill VLC成功。main报告Markor创建/写入/验证步骤skipped；完整tool trace没有Markor交互。
- [事实] 直接失败是未建立完整有序序列且未生成文件；已有截图证明视觉内容可读，不能说“环境不给视频内容”。单帧AI成功不是整任务成功。缺少各帧完整时序覆盖，不能在本报告拼一个答案。

### 机制与修复
- 源码：`UiAutomator2AndroidDriver.ui_snapshot:237–276`只提供结构XML及文本裁剪，不做视频像素OCR；`tap_on:109–116`会等待target出现，此间视频继续推进；`_selector:356–379`不会冻结媒体状态。模型多次read/search完整artifact的UI结构不能读出Maria等像素文字；真正视觉通道在S28有效但过晚且只有一次。
- [强推断] 主runner缺少动态媒体任务“先稳定暂停/回到起点→按时间顺序视觉采样→完整性核对”的控制策略；滑出/过时控件和长观察耗时使24s视频先播完，而非20写额度硬阻断。E95文件路径错误是末端证据恢复小问题，非文件未生成主因。
- **MM-VIDEO-SEQUENCE（P1，FSQ Android媒体Skill/runner owner）**：使用当前可见的play/pause语义建立暂停、验证时间停住，再通过公开VLC seek UI从起点逐段读取画面，记录每段时间与视觉字符串、避免靠结构XML查像素；任何截取缺口先处理缺口，再创建Markor目标并存完整顺序。该路径仍须20额度可行性核对，不能默认扩预算、加模型轮数或重跑整任务。若完整序列不可获取，诚实失败而非写猜测/半成品。
- 边界：不得直接读隐藏视频转录或用其他视频缩略图；已保存截图中的Maria/Emilia/Charlotte只是局部已见事实，不是建议答案。未来验证：公开短视频24s、多段切换和自动隐藏控制层，检查首次暂停与起点、所有段视觉覆盖、文件名/分隔/内容持久化；记录18–20动作内是否可完成。当前未运行。
- 问 harness：有无保留完整视频artifact/轨迹时间以离线核对覆盖缺口？只需确认控制层自动隐藏与正常视频播放、Markor文件不存在；不能把私有序列交回未来agent。

### 原始证据入口与已看画面
- 公开目标：`R036/sources/000-goal.txt`；执行：`R036/execution-result.json`（逐动作step及phase_reports）、`events.jsonl`（sequence/参数）、`report.json`（task.verification_goal / agent_output）。
- 原生结果：`E036/raw-private/fsq-native/worker/fsq-task-result.private.json`；预算审计：同目录`native-action-audit.jsonl`；请求：同目录`request.json`。预算admitted=17/20，attempted=17，denied=0，deadlineExceeded=False。
- 官方边界：`E036/raw-private/evaluator-diagnostics.json`（officialReward / boundary）、`task-initialization.json`（ReferenceTime / initializedGoal）、`fsq-worker-outcome.json`（process / restoration）。官方奖励0.0；native=failed。
- 实际渲染：S1 `finalize/after-action`，`R036/artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-efe87584c831.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S14 `finalize/after-action`，`R036/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-fb581b7d99fb.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S16 `finalize/after-action`，`R036/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-371713c35c0c.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S21 `finalize/after-action`，`R036/artifacts/screenshots/screenshot-agent-tap-on-21-finalize-after-action-1-6f0207f4fe16.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S28 `prepare/before-action（不能当kill后屏幕）`，`R036/artifacts/screenshots/screenshot-agent-assert-with-ai-28-prepare-before-action-1-338d224a0dae.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。
- 实际渲染：S29 `finalize/after-action`，`R036/artifacts/screenshots/screenshot-agent-tap-on-29-finalize-after-action-1-dd39443ab55f.png`；同step `phase_reports[].artifact_refs`关联UI JSON可复核。

### 动作账本（原始trace，ui_snapshot另见上述时序）
| step / event.sequence | 原始操作/决策（省略null字段） | 原生结果 |
|---|---|---|
| S1 / E19 | launch_app：app_id=org.videolan.vlc | passed  |
| S3 / E23 | swipe：direction=up | passed  |
| S5 / E33 | swipe：direction=up | passed  |
| S7 / E39 | tap_on：text=VLC | passed  |
| S9 / E45 | swipe：direction=up | passed  |
| S11 / E51 | tap_on：text=ZwUN_moment_70_ | passed  |
| S13 / E55 | tap_on：resourceId=org.videolan.vlc:id/close | passed  |
| S14 / E57 | tap_on：resourceId=org.videolan.vlc:id/player_root | passed  |
| S16 / E61 | tap_on：resourceId=org.videolan.vlc:id/player_overlay_play | failed Target was not found. |
| S17 / E63 | tap_on：resourceId=org.videolan.vlc:id/player_root | failed Target was not found. |
| S19 / E71 | tap_on：text=ZwUN_moment_70_ | passed  |
| S21 / E75 | tap_on：resourceId=org.videolan.vlc:id/player_root | passed  |
| S23 / E79 | tap_on：resourceId=org.videolan.vlc:id/player_overlay_play | failed Target was not found. |
| S25 / E83 | tap_on：text=ZwUN_moment_70_ | passed  |
| S27 / E87 | press_key：key=Space | passed  |
| S28 / E89 | assert_with_ai：当前页面视觉断言; optional=True | passed  |
| S29 / E91 | tap_on：resourceId=org.videolan.vlc:id/player_root | failed Target was not found. |
| S31 / E99 | kill_app：app_id=org.videolan.vlc | passed  |
