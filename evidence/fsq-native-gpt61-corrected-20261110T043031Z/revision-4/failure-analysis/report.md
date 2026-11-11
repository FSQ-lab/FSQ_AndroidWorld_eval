# FSQ r4：59唯一案例根因、双方核对与未来修复方案

## 阅读指引与术语

先读“必须先解决的跨层问题”，再从案例入口定位具体任务；逐例按“官方判据→原关键轨迹→差距与机制→未来修复/验证”阅读。“已核对”表示双方核对过材料，不表示全部因果已证实；事实、强推断和未知须分开看。

- **main runner**：执行任务并生成正式主输出的主Agent。
- **verifier**：独立核验证据者；不能代替主Agent的输出。
- **official oracle**：AndroidWorld官方评分函数；其reward不等同于主Agent或verifier的判断。
- **dispatch成功**：操作请求已获派发/工具返回成功，不等于应用业务目标已完成。
- **P0 / P1**：P0优先处理影响协议、正确性或测量有效性的问题；P1随后处理具体执行能力与可靠性问题，并非可忽略。


## 范围与结论边界

这是一份**离线调查**，不是修复完成报告。只读原goal、初始化、native execution/events/UI/截图、action audit、worker outcome、官方diagnostics，以及manifest绑定源码。没有启动设备、服务、模型、任务、评分、安装或测试；没有修改项目代码、配置、原report或奖励。未来验证均未执行。

“已证实”限既存原证据/匹配源码；“强推断”有相符链但缺评分边界或反事实；“未知”列明缺什么，不由0分反推。原生主runner、独立verifier、官方oracle是三个不同主体，状态不可互换。prepare截图是动作前，不能称kill后图。宿主2026审计时间不是fixture业务参考2023-10-15 15:34 UTC。

| 唯一案例原身份 | 数量 | 保留方式 |
|---|---:|---|
| failed，官方0 | 54 | 不由native success推成pass |
| failed，官方0.5 | 2 | 027、113；不编造分项 |
| passed，官方1但main契约失败 | 2 | 013、049原passed保留 |
| invalid_evaluator，reward null | 1 | 101不可改0/补评 |

集合为56 failed + 101 invalid_evaluator + 四项main异常去重；014/048本就在failed里，最终59唯一case。每例保留原goal、官方判据、关键轨迹、差距、分层归因、owner/P、修法与未来验证，不以“budget/规划问题”替代根因。

## 必须先解决的跨层问题

1. **P0，FSQ Skill/生命周期 + harness测量契约**：Browser002/003、Clock007/008/009、OpenApp041、SMS082/084/085/086及113已有业务UI正证，随后真正app_stop目标包；这些oracle还检查评分时前台UI。因此“业务完成→统一kill→完整native返回后评分”存在一般性末态冲突。具体0分由kill造成仍是主强推断：没有评分瞬间activity/forest或SMS provider rows。主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
2. **P0，FSQ Android driver**：多例launch回passed/app_id而下一原画面仍launcher，是后置条件缺口。冻结launch_app只dispatch app_start，未验证前台。底层u2当前3.5.2仅版本证据、不逐字节绑定，不把某个SDK默认值或monkey异常当当次原因。未来明确dispatch/ready/pending/failed与可观测实际包，不做盲重试/依赖重装。
3. **P1，FSQ主执行/工件工具**：013/014/048/049真实100turn EngineError，伴23slice/55search/81slice/66slice；写额度未尽、非business timeout。工件多层JSON字符串、历史淘汰与缺候选/断言ledger是机制强推断。提供带source refs的短结构化结果、已读cursor/候选状态、有界无进展反馈与原100turn内合法收尾机会；不加预算、不把异常转成功、不用verifier补main。
4. **P1，FSQ规划/Skill**：保留原goal所有合取子目标、提交动作及完整集合，不把前缀可见、输入框有值、单项/单屏成功、视觉近满当最终成功。正文替换与插入、text与content-desc、像素月网格与可定位节点、当前帧与跨屏证据分别建模。producer应向模型公开当前dispatch计量/剩余预算，但不泄露oracle参数或答案；固定M不变。
5. **P0，harness阶段调度**：原“任何invalid立即停止”的承诺与冻结halt谓词不一致，101后实际继续102..115，四项main异常也未停止。最终qualified=false/exit2不是及时停止。必须承认实施/指令偏差，未来对齐invalid/operational contract与cleanup后停止条件，并支持正常题间stop请求；不靠篡改授权/identity或强杀不明进程。详见[四项main异常与调度偏差](contract-deviation.md)。
6. **fixture/evaluator证据边界**：001实际录音落盘路径未存，不能坐实双扩展；101广播原文/前台/权限未存，不能坐实缺权限；059完整queue oracle与公开追加语义/未保证清队列初始化有边界，不能擅清用户队列；106due/completion自然语言歧义须记录；不可把这些测量限制硬归模型。

## 证据入口与版本

- [59原始清单](case-inventory.json)、[FSQ逐例独立笔记索引](fsq-case-notes/index.md)、[FSQ源码身份与逐例入口](fsq-evidence-index.json)。
- [结构化完整调查](cases.json)、[双方逐例核对记录](crosscheck-receipts.json)、[离线文档验收](validation.json)。
- [原正式report](../next-stage-plan/execution/run/report.json)、[原最终汇报](../final-handoff/report.md)：只作原证据，不覆盖。
- FSQ冻结包/source SHA256 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`；16关键FSQ源逐文件hash匹配。官方源是manifest指定isolated installed evaluator-site，不是随意当前checkout。harness阶段源另已绑定SHA256 `fe0b3280562b2801b3faca509e34b4a98db79c247ebfe41bbaaba5bab57e3210`。
- harness-notes各分块是独立调查底稿，含当时pending状态；此处及cases.json的最终crosscheck记录为联合核对口径。保留分歧/修正及未知不等于“全部归因已证”。

## 逐例调查

案例入口：[001](#case-001) · [002](#case-002) · [003](#case-003) · [004](#case-004) · [007](#case-007) · [008](#case-008) · [009](#case-009) · [010](#case-010) · [011](#case-011) · [013](#case-013) · [014](#case-014) · [015](#case-015) · [016](#case-016) · [017](#case-017) · [019](#case-019) · [023](#case-023) · [024](#case-024) · [027](#case-027) · [029](#case-029) · [030](#case-030) · [032](#case-032) · [033](#case-033) · [036](#case-036) · [040](#case-040) · [041](#case-041) · [044](#case-044) · [046](#case-046) · [047](#case-047) · [048](#case-048) · [049](#case-049) · [050](#case-050) · [052](#case-052) · [059](#case-059) · [060](#case-060) · [068](#case-068) · [069](#case-069) · [070](#case-070) · [071](#case-071) · [072](#case-072) · [074](#case-074) · [076](#case-076) · [078](#case-078) · [081](#case-081) · [082](#case-082) · [084](#case-084) · [085](#case-085) · [086](#case-086) · [087](#case-087) · [090](#case-090) · [091](#case-091) · [092](#case-092) · [097](#case-097) · [098](#case-098) · [101](#case-101) · [106](#case-106) · [107](#case-107) · [108](#case-108) · [110](#case-110) · [113](#case-113)

<a id="case-001"></a>
### 案例 001 — AudioRecorderRecordAudioWithFileName

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Record an audio clip and save it with name "presentation_fGwr.m4a" using Audio Recorder app.

**约束与冻结初始化**

- **publicGoal**：Record an audio clip and save it with name "presentation_fGwr.m4a" using Audio Recorder app.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4/sources/000-goal.txt
- **requirementsNote**：需要磁盘上完整basename存在；实际只证明应用内显示标题和录音已保存，official=0说明oracle精确路径检查未通过。native=success，mainAnswer valid，与官方文件契约有证据粒度差。
- **nativeDerivedVerificationGoal**：The app visibly lists the newly saved audio clip as "presentation_fGwr.m4a".
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4/report.json
- **判据**：调用CreateFile初始化并清空AUDIORECORDER_DATA；本次冻结参数file_name=presentation_fGwr.m4a，text为空；参考时间2023-10-15 15:34 UTC。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：二元评分：清空录音目录后，检查完整文件名 presentation_fGwr.m4a 是否存在于 /storage/emulated/0/Android/data/com.dimowner.audiorecorder/files/Music/records。不是检查列表显示标题，也不检查音频时长。 helper对find的完整路径集合做base_path/target精确相等；不去后缀、不fuzzy、不接受其他目录或子目录中的同名文件。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-2 passed：首次launch成功后观察仍为launcher；后续再次launch、应用抽屉和图标导航增加写操作。
- agent-input_text-13 passed：New name对话框原值Record-1；输入完整字符串presentation_fGwr.m4a。截图无可据以证明实际后缀的独立文件路径字段。
- agent-tap_on-14 passed：Save成功后UI标题presentation_fGwr.m4a，信息0.19 Mb, M4a,44.1kHz，duration=00:16。
- agent-assert_visible-18 passed：精确列表标题断言成功。
- agent-kill_app-19 passed：显式app_id=com.dimowner.audiorecorder的kill成功；文件型oracle不要求前台，不能把这个kill单独当本例原因。

原dispatch额度 10/20，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 需要磁盘上完整basename存在；实际只证明应用内显示标题和录音已保存，official=0说明oracle精确路径检查未通过。native=success，mainAnswer valid，与官方文件契约有证据粒度差。
- 没有获得官方目标路径下完整文件名存在的证据；官方检查返回0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 录音16秒已保存且列表精确显示presentation_fGwr.m4a（step14/18截图与XML）。
  - native verification_goal只要求可见列表标题，弱于完整文件名/目录的官方目标。
  - 冻结helper L244-258在目录不存在时0，否则find后精确比较base/target；没有后缀normalize。
- **强推断**：
  - 强推断：UI显示名与实际落盘文件名/目录的映射没有纳入验证，形成误报success；不是录音没启动。
- **无法确认与缺证据**：
  - 未存录音目录清单或文件属性；无法确认实际是presentation_fGwr.m4a.m4a、存到了另一目录、或其他命名映射。重复.m4a仅候选，绝不可写成已证实。
- **备选及区分**：
  - 自动追加扩展名
  - 应用存储位置与oracle目录不同
  - 实际文件创建/重命名未持久化；现有UI不能区分
- **责任层**：
  - FSQ规划/应用文件语义验证
  - 应用UI标题与文件系统状态边界；harness证据不足

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ planner verification_goal / Audio Recorder UI保存流程`：保留用户完整文件名语义；在应用可见文件详情/导出文件名等合法UI中核对实际完整basename与保存位置，再决定是否需要只填stem。未查清前禁止全局去掉或重复追加.m4a。
- **P1 / harness**；`harness evaluator diagnostics / AudioRecorderRecordAudioWithFileName.is_successful`：在私有评分侧记录被检查目录、目标存在布尔和不含答案泄露的文件名差异证据；不把oracle目录/期待值回灌执行agent。

**未来验证（全部未执行）**

- 离线以存量应用文件命名实现/文件属性证据区分自动后缀与存储目录；若不可得明确未知。
- 独立录音样例经UI保存带/不带扩展名后，私有评分侧核对完整basename；严格保持原maxActions，不同题重试凑分。

**双方逐例核对**

已核对，有保留：UI录音/标题正证；官方完整路径精确检查，实际文件路径未存，双扩展只能候选。

交叉核对：已核对、有保留（harness Early冻结源/trace复核）。audio_recorder.py:114–123→file_utils:228–258精确比较base/完整filename，无suffix normalize、DB或时间戳判据；S19目标AudioRecorder已证，不归前台oracle。实际路径未存，双.m4a仍仅候选。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例001，起始第46行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/0`。
- [原公开goal](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/audio_recorder.py；lines：95-123；symbol：AudioRecorderRecordAudioWithFileName.initialize_task/is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py；lines：29；symbol：AUDIORECORDER_DATA；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：228-258；symbol：check_file_or_folder_exists；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-002"></a>
### 案例 002 — BrowserDraw

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then create a drawing using the three colors shown at the top and hit submit.

**约束与冻结初始化**

- **publicGoal**：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then create a drawing using the three colors shown at the top and hit submit.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/sources/000-goal.txt
- **requirementsNote**：业务已经得到页面原生Success!，native/main均success；official在agent退出后才取前台UI而返回0。
- **nativeDerivedVerificationGoal**：The drawing submitted in task.html uses all three colors displayed at the top of the task.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/report.json
- **判据**：browser_task_seed=461184702。任务需经Files打开task.html/Chrome；清Chrome导致first-run提示，真实step11/13/15/21处理并重开文件，不能当可删初始化噪声。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：初始化清storage、清Chrome、按冻结seed写Downloads/task.html；Browser开启自动时间。页面逐像素确认三种目标颜色均存在后显示Success!；官方还要求评估时当前package=com.android.chrome且UI含精确Success!。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-assert_with_ai-23 passed：读取顶部三目标色与palette位置。
- agent-swipe-25 passed：先选teal再画第一笔。
- agent-swipe-28 passed：选择magenta画第二笔。
- agent-swipe-30 passed：选择dark navy画第三笔。
- agent-tap_on-32 passed：点击Submit。
- agent-assert_visible-34 passed：result=Success!且截图三笔与目标色一致。
- agent-kill_app-35 passed：默认kill_app成功，invoke metadata.harness_output.app_id=com.android.chrome；driver L102-107已核对默认解析self.app_id并调用app_stop；评分瞬间UI未存。

原dispatch额度 19/20，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 业务已经得到页面原生Success!，native/main均success；official在agent退出后才取前台UI而返回0。
- 业务成功画面与评估边界之间有成功的kill_app，官方要求的前台Chrome/Success!不是持久化状态。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step34原截图和XML显示Success!，不是AI只凭颜色猜成功。
  - step35 teardown发生在native返回和official diagnostic.startedAtUnix之前；记录的resolved app_id为Chrome。
  - 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
- **强推断**：
  - 强推断：native teardown移走Chrome前台，破坏BrowserTask.is_successful的前台条件；official0不是画色错误。
- **无法确认与缺证据**：
  - 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。
- **备选及区分**：
  - 除前台交接破坏外，若评分state/activity采样陈旧也可能造成0；缺评分瞬间快照不能区分，三色业务失败已由Success!排除。
- **责任层**：
  - FSQ生命周期/teardown与harness评分时序
  - 不是rubric错误

**修复方案（未实施）**

- **P0 / FSQ+harness**；`native Android teardown / BudgetedAndroidHarness.close与官方is_successful调用边界`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线事件顺序断言：业务终态截图→官方评估→可改变前台的cleanup；不允许中间kill。
- 新独立BrowserDraw样例保持Chrome前台，评分侧存activity与Success!快照；同样20写预算。

**双方逐例核对**

已核对：Success与actual Chrome kill已证；评分前台破坏为主强推断，评分瞬间UI未存。

**交叉核对：已核对（FSQ↔harness owner逐例批B）。双方一致：Success画面和Chrome kill目标已证实；官方前台+Success判据已定位；kill导致0为主强推断，评分瞬间状态仍缺证。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例002，起始第7行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/1`。
- [原公开goal](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：49-85,98-109；symbol：BrowserTask.initialize_device_time/initialize_task/is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：596-629；symbol：BrowserDraw.evaluateTask/showResult；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-003"></a>
### 案例 003 — BrowserMaze

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.

**约束与冻结初始化**

- **publicGoal**：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/sources/000-goal.txt
- **requirementsNote**：原任务是到达目标，不是完成后仍展示X；真实业务成功终态Success!反被native静态视觉契约判失败，且又在评分前kill。
- **nativeDerivedVerificationGoal**：The task.html grid in Chrome visibly shows X in the bottom-right cell.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/report.json
- **判据**：清Chrome/下载目录并写maze HTML；经Files打开，完成Chrome first-run。Browser自动时钟不能用静态参考时间误判运行时钟。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：seed=1364588068的maze；移动到goal后checkGoalReached立即用<h1>Success!</h1>替换整个document.body，网格和X按设计消失。官方只认Chrome前台+Success!。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-assert_with_ai-23 failed：用于查看网格的AI断言失败；后续存在方向按钮动作。不可把其摘要替代实际终态。
- agent-tap_on-24 passed：Right。
- agent-tap_on-25 passed：Down。
- agent-tap_on-26 passed：Down。
- agent-tap_on-27 passed：Down。
- agent-tap_on-28 passed：Right。
- agent-tap_on-29 passed：Right。
- agent-assert_with_ai-31 failed：原截图和XML：Maze Puzzle中为Success!，无X/网格；因prompt强制X仍可见而判失败。
- agent-kill_app-32 passed：默认kill成功，metadata resolved app_id=Chrome，随后才official0。

原dispatch额度 18/20，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 原任务是到达目标，不是完成后仍展示X；真实业务成功终态Success!反被native静态视觉契约判失败，且又在评分前kill。
- 两条独立差距：native verification_goal与网页成功状态机冲突；official评分时前台被teardown影响的强可能性。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - report.task.verification_goal要求grid visibly shows X in bottom-right，这与源码goal到达后删grid冲突。
  - step31成功终态截图清楚写Success!；native failed不能视为没走到终点。
  - 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
- **强推断**：
  - official0最可能由step32 kill与前台Chrome要求导致；不能把AI false当官方0的解释。
- **无法确认与缺证据**：
  - 无评分瞬间activity/forest；最早step23视觉描述与方向动作前UI之间的矛盾需FSQ核对，勿声称初始就成功。
- **备选及区分**：
  - 即便修好verifier的Success!解释，不修评分前kill仍会得0；这两项必须分别处理。
- **责任层**：
  - FSQ planner验收语义
  - FSQ/harness生命周期

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ planner verification_goal / verifier`：依据用户到达目标的语义接受页面合法终态，不添加“X必须永远可见”的静态附加要求；识别UI任务已切换成功页即停止方向操作。
- **P0 / FSQ+harness**；`Android teardown→official BrowserTask.is_successful边界`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线用该HTML checkGoalReached与终态截图验证：Success!替代grid不得算失败；无oracle答案注入。
- 独立maze实例到达后保留前台；官方评估成功后才kill。

**双方逐例核对**

已核对：成功路线与Success已证；持续可见X是额外验证条件，official0另有kill前台冲突强推断。

**交叉核对：已核对（逐例批B）。双方一致：右下路线/Success已证；FSQ自造终态条件导致自身否决；官方0与Chrome kill前台冲突高度一致但缺边界快照，二者不得混为同一已证原因。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例003，起始第30行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/2`。
- [原公开goal](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：56-85,98-109；symbol：BrowserTask.initialize_task/is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：278-321；symbol：BrowserMaze.moveCharacter/checkGoalReached；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-004"></a>
### 案例 004 — BrowserMultiply

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.

**约束与冻结初始化**

- **publicGoal**：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/sources/000-goal.txt
- **requirementsNote**：数列/算术和五次点击均正确，但只填answer没有Submit，因此checkAnswer未执行；native planner仅要求输入框有乘积，漏最终提交。
- **nativeDerivedVerificationGoal**：The answer field in task.html opened in Chrome visibly contains the product of the five numbers displayed after exactly five button clicks.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/report.json
- **判据**：browser_task_seed=3143940091；真实显示数列9（初始）、10、9、5、5，乘积20250。不import官方/不重新生成参数。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：初始generateNumber生成第1个数；前4次click生成第2-5个数，第5次只显示form。checkAnswer必须由Submit调用，答案正确才出现Success!；官方Chrome前台+Success!。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-20 passed：number=9，尚未第一次task-button点击。
- agent-ui_snapshot-22 passed：第1次后number=10。
- agent-ui_snapshot-24 passed：第2次后number=9。
- agent-ui_snapshot-26 passed：第3次后number=5。
- agent-ui_snapshot-28 passed：第4次后number=5。
- agent-tap_on-29 passed：第5次Click Me显示form，无新数字。
- agent-input_text-32 passed：输入20250。
- agent-assert_state-33 failed：按text=20250断言找不到控件，属可访问性文本带hint差异。
- agent-assert_state-35 passed：使用text=20250, Enter the product成功；截图Submit仍在且无Success!。
- agent-kill_app-36 passed：kill Chrome，未有Submit动作。

原dispatch额度 17/22，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 数列/算术和五次点击均正确，但只填answer没有Submit，因此checkAnswer未执行；native planner仅要求输入框有乘积，漏最终提交。
- 未提交是官方0的充分业务原因；另有评分前kill。verifier称初始数不应算入5数与实际JS相反。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 原始五张snapshot读到9,10,9,5,5；HTML明确初始生成+4次生成。
  - step32-36无Submit，终态截图仍是填写表单而非Success!。
- **强推断**：
  - 强推断：planner把完整网页交互缩成answer字段存在，导致未执行用户任务隐含的提交/结果确认；verifier又以错误的“每click后都应显示数”契约给inconclusive。
- **无法确认与缺证据**：
  - 即使补Submit，仍需修前台生命周期才能评分；不声称未运行的Submit会得到实测reward1。
- **备选及区分**：
  - 不是20250算错，不是初始9多算；官方源码直接排除这两个解释。
- **责任层**：
  - FSQ规划遗漏提交
  - FSQ verifier时间/计数状态机理解
  - teardown时序

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ Browser form planner / verification_goal`：将表单输入与提交后反馈作为完整动作，显式点击页面Submit并确认自然成功反馈；以真实UI阶段跟踪“初始数+四次新数”，不硬编码本题答案。
- **P1 / FSQ**；`FSQ verifier evidence reasoning`：允许首次可见初始数字计入显示序列；区分第5次切换form，不因字面“after five clicks”误拒有效序列。
- **P0 / FSQ+harness**；`Android teardown边界`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线依据JS状态机断言：5个显示值、5click，第5次不新增值；仅填框≠Success!。
- 独立BrowserMultiply实例提交正确结果、保留成功UI至评分；22写预算不变。

**双方逐例核对**

已核对：20250正确、未Submit是确定差距；kill另末态风险，不归算术。

**交叉核对：已核对（逐例批B）。双方确认20250计算正确、未Submit是确定差距；不得定性算术失败；Chrome kill为另一个已执行末态风险。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例004，起始第53行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/3`。
- [原公开goal](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：98-109；symbol：BrowserTask.is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/browser.py；lines：407-439；symbol：BrowserMultiply.generateNumber/handleButtonClick/checkAnswer；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-007"></a>
### 案例 007 — ClockStopWatchPausedVerify

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Pause the stopwatch.

**约束与冻结初始化**

- **publicGoal**：Pause the stopwatch.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96/sources/000-goal.txt
- **requirementsNote**：任务只要求暂停；native额外把“保留非零elapsed”当目标，先Start再Pause虽仍暂停，却多花2写。官方0不能归咎8.46秒，因为rubric不看elapsed；评分前kill破坏前台更吻合。
- **nativeDerivedVerificationGoal**：The stopwatch is paused with its elapsed time retained.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96/report.json
- **判据**：_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。无其他时间参数。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：初始化清Clock数据，秒表本来为00/00且Start；官方要求当前activity含DeskClock、Start存在、Stopwatch标签数>=2，不要求非零elapsed，更不要求先启动。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-9 passed：首个秒表UI就是00秒/00百分秒、Start，已经满足暂停的可见业务语义。
- agent-tap_on-10 passed：无必要地Start。
- agent-tap_on-12 passed：Pause后8.46秒；这是秒/百分秒，不是8分46秒。
- agent-assert_visible-16 passed：非零08文本与Start断言成功；截图暂停，原elapsed文本在部分snapshot中不可见但先前snapshot13有08/46。
- agent-kill_app-17 passed：显式kill com.google.android.deskclock成功，发生在官方评估前。

原dispatch额度 8/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 任务只要求暂停；native额外把“保留非零elapsed”当目标，先Start再Pause虽仍暂停，却多花2写。官方0不能归咎8.46秒，因为rubric不看elapsed；评分前kill破坏前台更吻合。
- 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 初始化后的秒表本已Start/零；额外Start/Pause来自native计划而非官方前置需求。
  - 最终Start+Stopwatch足以满足paused谓词的UI部分；step17显式目标Clock，随后official0。
  - 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
  - FSQ分案初稿所称00/Start precondition mismatch不成立：官方initialize主动清数据且类doc明确零暂停预置。本调查反馈修正，待对方回执。
- **强推断**：
  - 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。
- **无法确认与缺证据**：
  - 评分瞬间activity/forest未记录；不能假定原本存在非零运行会话，亦不能把官方设计的零暂停当预检故障。
- **备选及区分**：
  - 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。
- **责任层**：
  - FSQ生命周期与harness评估边界
  - FSQ额外任务约束/无效写操作

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ planner key_actions / verification_goal`：对Pause这类保持型任务先检查当前是否已达标；不得凭空要求非零时间而先Start。
- **P0 / FSQ+harness**；`FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线零秒Start+两个Stopwatch标签应满足官方paused谓词；08/46是秒与百分秒。
- 独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

**双方逐例核对**

已核对并实质修正FSQ初稿：00暂停为合法官方预置，不是precondition mismatch；当前DeskClock UI oracle，kill前台冲突强推断。

交叉核对：已核对、实质修正（harness owner亲读冻结installed clock.py后逐例回执）；删除此前已被源码否定的precondition mismatch与初始化异常候选，原reward0不变。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例007，起始第90行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/4`。
- [原公开goal](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：103-122；symbol：_ClockEval.initialize_task/tear_down；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：43-63,177-208；symbol：_is_stopwatch_paused/ClockStopWatchPausedVerify.is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-008"></a>
### 案例 008 — ClockStopWatchRunning

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Run the stopwatch.

**约束与冻结初始化**

- **publicGoal**：Run the stopwatch.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e/sources/000-goal.txt
- **requirementsNote**：真实UI有Pause/Lap且计时增加，native success；official0在kill后，非业务未启动或计时不前进。
- **nativeDerivedVerificationGoal**：The stopwatch is running and its displayed elapsed time is advancing.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e/report.json
- **判据**：_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。无其他时间参数。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：初始化清Clock数据，起点零/Start；官方要求当前activity含DeskClock且content_description Pause与Lap同时出现。无需精确运行几秒。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-9 passed：初始00/00且Start。
- agent-tap_on-10 passed：点击fab开始。
- agent-wait_ms-12 passed：等待2秒供非写观察核对增长。
- agent-assert_visible-13 passed：stopwatch_time_text数值>3断言通过；不是分钟字段。
- agent-assert_visible-14 passed：原XML显示18秒48百分秒、Pause和Lap，运行态已达成。
- agent-kill_app-15 passed：空参数kill成功，metadata.harness_output.app_id=com.google.android.deskclock；具体底层driver源码L102-107已核对为app_stop。

原dispatch额度 7/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 真实UI有Pause/Lap且计时增加，native success；official0在kill后，非业务未启动或计时不前进。
- 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step14 XML的Pause、Lap直接覆盖官方UI条件；18/48表示18.48秒。
  - step15 resolved app_id记录Clock，默认入参没有显式app_id。
  - 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
- **强推断**：
  - 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。
- **无法确认与缺证据**：
  - 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。
- **备选及区分**：
  - 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。
- **责任层**：
  - FSQ生命周期与harness评估边界

**修复方案（未实施）**

- **P0 / FSQ+harness**；`FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线用step14 UI验证Pause+Lap条件，不引入精确秒数要求。
- 独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

**双方逐例核对**

已核对：kill前运行已证，oracle仅当前DeskClock+Pause+Lap；不能声称service必停或elapsed归零。

交叉核对：已核对（harness owner冻结clock.py逐例回执）；actual Clock kill已双侧确认，前台破坏为主强推断，评分UI未留存。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例008，起始第134行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/5`。
- [原公开goal](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：103-122；symbol：_ClockEval.initialize_task/tear_down；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：25-40,215-245；symbol：_is_stopwatch_running/ClockStopWatchRunning.is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-009"></a>
### 案例 009 — ClockTimerEntry

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Create a timer with 0 hours, 16 minutes, and 35 seconds. Do not start the timer.

**约束与冻结初始化**

- **publicGoal**：Create a timer with 0 hours, 16 minutes, and 35 seconds. Do not start the timer.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4/sources/000-goal.txt
- **requirementsNote**：时间值与未启动约束都满足；official0不是数字顺序或秒/分钟错，而是终态未保留到评估。
- **nativeDerivedVerificationGoal**：The timer displays a configured duration of 0 hours, 16 minutes, and 35 seconds and has not been started.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4/report.json
- **判据**：_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。params hours=0, minutes=16, seconds=35。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：官方要求DeskClock当前activity，UI text=00h 16m 35s或content-desc=0 hours, 16 minutes, 35 seconds；goal额外明确不得Start。不是16分35秒倒计时运行。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-tap_on-10 passed：timer_setup_digit_1。
- agent-tap_on-11 passed：digit6。
- agent-tap_on-12 passed：digit3。
- agent-tap_on-13 passed：digit5；得到00h16m35s。
- agent-assert_with_ai-15 passed：XML/text/content-desc完全对应0小时16分35秒，Start可用且无Start调用，AI成功。
- agent-kill_app-16 passed：空参数kill成功，metadata resolved app_id=Clock；第10个计费写（含setup/kill），无denied。

原dispatch额度 10/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 时间值与未启动约束都满足；official0不是数字顺序或秒/分钟错，而是终态未保留到评估。
- 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 原step15 XML有00h 16m 35s与完整content-desc，截图显示数字键盘+Start；无启动timer行为。
  - 预算10/10是含kill的已用满，不是业务动作被拒；deadlineExceeded=false。
  - 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
- **强推断**：
  - 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。
- **无法确认与缺证据**：
  - 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。
- **备选及区分**：
  - 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。
- **责任层**：
  - FSQ生命周期与harness评估边界

**修复方案（未实施）**

- **P0 / FSQ+harness**；`FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 离线断言输入1635对应HH=0/MM=16/SS=35；最后一次计费kill，不把exhausted当denied。
- 独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

**双方逐例核对**

已核对：00:16:35未启动UI达成；oracle当前DeskClock+输入UI，kill后状态缺证。

交叉核对：已核对（harness owner冻结clock.py逐例回执）；actual Clock kill已双侧确认，前台破坏为主强推断，评分UI未留存。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例009，起始第178行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/6`。
- [原公开goal](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：103-122；symbol：_ClockEval.initialize_task/tear_down；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/clock.py；lines：66-100,125-160；symbol：_is_timer_set/ClockTimerEntry.is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-010"></a>
### 案例 010 — ContactsAddContact

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Create a new contact for Hugo Pereira. Their number is +13920741751.

**约束与冻结初始化**

- **publicGoal**：Create a new contact for Hugo Pereira. Their number is +13920741751.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240/sources/000-goal.txt
- **requirementsNote**：目标为持久化Contact；真实终态仍draft（Hugo/Pereira/+1 392-074-1751），Save拒，official0符合provider契约。
- **nativeDerivedVerificationGoal**：The saved contact details show Hugo Pereira with phone number +13920741751.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240/report.json
- **判据**：frozen name=Hugo Pereira，number=+13920741751；初UI No contacts yet，并有Contacts intro overlay。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：清空联系人；评分从联系人provider列出并比对Contact(name=Hugo Pereira,cleaned number)。必须保存为实际联系人，draft显示文字不算；格式化+1 392-074-1751可清理为期望号码。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-2 passed：第一次launch后仍launcher。
- agent-launch_app-3 passed：第二次launch声明成功；后续仍需抽屉/icon。
- agent-press_key-8 passed：Back退出再进Contacts，增加导航成本。
- agent-tap_on-10 passed：dismiss og_tooltip_scrim_view。
- agent-tap_on-12 passed：开新联系人表单。
- agent-input_text-14 passed：First name Hugo。
- agent-input_text-15 passed：Last name Pereira。
- agent-input_text-16 passed：Phone +13920741751。
- agent-press_key-17 passed：Back收键盘是第12写；保存尚未完成。
- agent-tap_on-19 failed：Save在dispatch前被NativeActionBudgetExceeded拒；after XML仍Create contact且Save可见。
- agent-kill_app-20 failed：teardown亦被拒。

原dispatch额度 12/12，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 目标为持久化Contact；真实终态仍draft（Hugo/Pereira/+1 392-074-1751），Save拒，official0符合provider契约。
- 第12写用在收键盘，关键第13写Save不可admit。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - audit seq1/5/7/11/15/17/19/23八写先用于启动/导航/overlay；seq27/29/31输入三字段，seq33 Back用尽12。
  - audit seq37拒Save；无任何后续成功保存；不是号码格式错误。
- **强推断**：
  - 强推断：launch调用成功但没有实际进入目标前台，导致双启动+抽屉+重进成本，再叠加对完成动作无预算预留；在小额度中消耗了commit所需写。
- **无法确认与缺证据**：
  - 没有driver launch底层源码确认前，不能把前台未进入的原因直接定为SDK bug；可能生命周期/激活语义不符。
- **备选及区分**：
  - 号码正确但尚未保存是充分失败原因，不需假设Contacts provider异常。
- **责任层**：
  - FSQ启动/导航计划与写预算分配
  - harness NativeDispatchBudget真实拒绝，非误报

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ AndroidDriver.launch_app与planner启动策略`：先核对实际前台并使用一次真正有效启动；重用现有观察，移除无效果重复launch/Back再进。
- **P1 / FSQ**；`FSQ planner/runner remaining action budget`：显式为Save保留动作并在budget不可恢复拒绝后终止无意义重试；仍计入现有12写，不能私增预算。

**未来验证（全部未执行）**

- 离线audit重放计数：Save前12写，拒绝不forward；删除无效启动/导航后应保留commit槽位，不以加预算替代。
- 独立AddContact任务确认保存后详情，再官方provider查到姓名+clean number；12写不变。

**双方逐例核对**

已核对：字段/号码正确，Save未forward充分失败；持久Contact oracle非前台，kill也拒绝。

交叉核对：已核对（harness Early逐例回执）。官方持久Contact(name,clean number)，不是前台；姓名号码正确、Save未forward是充分失败，号码UI格式化不算错号，kill亦拒绝。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例010，起始第223行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/7`。
- [原公开goal](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/contacts.py；lines：27-32；symbol：ContactsAddContact；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/contacts_validators.py；lines：38-55；symbol：AddContact.initialize_task/_has_contact/is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-011"></a>
### 案例 011 — ContactsNewContactDraft

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Go to the new contact screen and enter the following details: First Name: Grace, Last Name: Taylor, Phone: 799-802-1530, Phone Label: Work. Do NOT hit save.

**约束与冻结初始化**

- **publicGoal**：Go to the new contact screen and enter the following details: First Name: Grace, Last Name: Taylor, Phone: 799-802-1530, Phone Label: Work. Do NOT hit save.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998/sources/000-goal.txt
- **requirementsNote**：三字段已填，Do NOT Save守住；Work没选择。official0不能仅解释为“键盘挡住”——其forest明确含不可见控件；真正缺失Work才是核心。
- **nativeDerivedVerificationGoal**：The unsaved new-contact form displays First Name Grace, Last Name Taylor, phone 799-802-1530, and phone label Work.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998/report.json
- **判据**：普通TaskEval恢复Contacts快照、设置参考时钟；无Draft特有清联系人逻辑。frozen Grace/Taylor/799-802-1530/Work；实际起点有intro overlay。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：0

**官方判据**

- **判据**：与AddContact相反，不Save；官方从forest含不可见节点读取hint=First name/Last name/Phone的字段、忽略号码非数字格式，电话label必须Work+Work Phone或位于phone下方的Work。仅键盘遮挡不是官方天然失败条件。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch后launcher。
- agent-tap_on-10 passed：绕回Contacts后dismiss intro。
- agent-input_text-14 passed：Grace。
- agent-input_text-15 passed：Taylor。
- agent-press_key-16 passed：先收键盘花一写。
- agent-input_text-18 passed：电话号码是第12写。
- agent-press_key-19 failed：Back被预算拒绝。
- agent-press_key-20 failed：不可恢复额度下重复Back再拒。
- agent-assert_with_ai-22 failed：截图Grace/Taylor/799-802-1530可见，键盘遮label；原XML仍有Delete Mobile Phone，不是Work。
- agent-kill_app-23 failed：kill亦被拒，draft保持，没误点Save。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 三字段已填，Do NOT Save守住；Work没选择。official0不能仅解释为“键盘挡住”——其forest明确含不可见控件；真正缺失Work才是核心。
- 没有选择Work的任何动作；label保持Mobile（delete_button_container desc=Delete Mobile Phone），budget用满后连收键盘都不可再做。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step22原XML/Delete Mobile Phone，与先前Mobile字段一致；动作序列没有label dropdown/Work选择。
  - 官方号码clean规则允许799-802-1530；未Save本身是本例要求而非缺陷。
- **强推断**：
  - 强推断：导航/双launch耗掉setup写，再在填完phone前未预留Work选择所需动作，导致必填label未达标；verifier只说遮挡弱化了实际漏字段。
- **无法确认与缺证据**：
  - 没有评分forest快照，不能逐节点证明oracle最终看到哪个Work元素；现有Mobile内容描述+零选择动作已强烈支持未改label。
- **备选及区分**：
  - 即便hide keyboard也不会自动把Mobile变Work；不能只改可视断言、也不能通过Save修Draft。
- **责任层**：
  - FSQ预算规划与字段完整性
  - FSQ verifier可见截图与官方含不可见forest的边界

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ ContactsDraft planner/字段清单`：把phone_label作为独立字段完成，先消除无效启动/重进，为dropdown→Work和必要收键盘留额度；禁Save保持原任务。
- **P1 / FSQ**；`FSQ verifier`：区分“未看到”和“当前已选Mobile”，不要把遮挡当最终根因；使用已有合法UI语义/属性核对label。

**未来验证（全部未执行）**

- 离线断言Draft goal四字段且not-save；Mobile不能因为被遮挡而当Work，不按AddContact保存流程复用。
- 独立Draft实例12写内完成Work并保持draft，评分侧保留forest检查label和hint。

**双方逐例核对**

已核对并补实：未Save符合draft目标；缺Work选择、原XML Mobile不能只归键盘遮挡；kill拒绝。

交叉核对：已核对、有补实（harness Early逐例回执）。contacts.py:206–225从含invisible的forest读四字段，无独立activity前台；:35–138检查Work标签/hint邻接。S22实际仍Delete Mobile Phone且未选Work，不仅是键盘遮挡，kill拒绝未执行。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例011，起始第268行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/8`。
- [原公开goal](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/contacts.py；lines：35-138,206-225；symbol：_contact_info_is_entered/_find_phone_label_element/ContactsNewContactDraft.is_successful；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/task_eval.py；lines：116-157；symbol：TaskEval.initialize_task/_initialize_apps；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-013"></a>
### 案例 013 — ExpenseAddMultipleFromGallery

**原身份：passed / officialReward=1.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the expenses from expenses.jpg in Simple Gallery Pro to pro expense.

**约束与冻结初始化**

- **publicGoal**：Add the expenses from expenses.jpg in Simple Gallery Pro to pro expense.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/sources/000-goal.txt
- **requirementsNote**：officialReward=1.0/classification=passed必须保留：完整DB新增契约已由官方通过。独立native runner error/输出契约失败不倒扣官方分。verifier inconclusive仅因证据未对Dental category重开和无main summary。
- **nativeDerivedVerificationGoal**：Pro Expense shows saved entries matching every expense and its corresponding details in expenses.jpg.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/report.json
- **判据**：目标Dress/43635分/Clothes(8)/Paid by card；Furnishing/35007分/Housing(4)/A need；Dental Care/3954分/Health Care(9)/A need。需认准expenses.jpg，不是old_expenses。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：10

**官方判据**

- **判据**：初始Expense DB仅10个noise；Gallery写expenses.jpg为3目标与10个old_expenses_*.jpg为noise。评分新增3行：name/note fuzzy、amount分整数与category id精确；after条数=before+3且原10行逐行不变。不是每字段独立分数，而是完整完整性布尔1/0。created/modified时间与新ID不与参考行比较。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：1.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-tap_on-14 passed：Gallery搜索expenses、打开文件名expenses.jpg。
- agent-assert_with_ai-15 passed：原source截图与transcription完整3条，逐字段同冻结目标。
- agent-tap_on-33 passed：Dress表单填436.35、Clothes、Paid by card后SAVE。
- agent-tap_on-45 passed：Furnishing填350.07、Housing、A need后SAVE。
- agent-tap_on-58 passed：Dental Care填39.54、Health Care、A need后SAVE。
- agent-assert_with_ai-62 passed：保存Dental Care详情确认name/amount/note，未展示category。
- agent-assert_with_ai-66 failed：Furnishing detail缺可见category导致AI fail，不是值错。
- agent-assert_with_ai-68 passed：EDIT重开Furnishing，Housing选中；恢复该项验证。
- agent-assert_with_ai-74 passed：EDIT重开Dress，Clothes选中；输入与note吻合。
- agent-ui_snapshot-76 passed：三条记录在recent列表；随后多次read_artifact_slice直至100 turn失败，无main结构化summary。

原dispatch额度 46/60，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- officialReward=1.0/classification=passed必须保留：完整DB新增契约已由官方通过。独立native runner error/输出契约失败不倒扣官方分。verifier inconclusive仅因证据未对Dental category重开和无main summary。
- 业务已完成但runner在出结构化task_run_v1前耗尽配置100 turns，error精确为Agent exceeded the configured turn limit.；不是Main runner did not succeed这个外层筛选reason，也不是写额度不足。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - source screenshot15三条与输入/保存动作完全对应；diagnostic官方返回1，无异常、无missing-row日志。
  - events seq221 run_failed精确turn limit；nativeResult.steps[0]同错误，privateOutcome.result.nativeTarget.maxTurns=100。
  - events tool_call_started计read_artifact_slice=23；末段seq209/211/217/218反复读已存在AI结果；write admission46/60，deadline=false、denied0。
- **强推断**：
  - 强推断：大体积/嵌套证据取回和保存后重复核验未做收敛/终结，消费与写预算独立的turns，最终无结构化交付；不能将AI66不可见category当作原业务字段错误。
- **无法确认与缺证据**：
  - 未在本调查重演FSQ max-turn控制；具体每个provider turn计数边界和artifact filter为何要求额外slice交FSQ核对。官方1已排除本次Dental实际保存category不匹配。
- **备选及区分**：
  - 只放宽verifier到success不能修复main runner结构化输出缺失；只加turn预算不是根治。
- **责任层**：
  - FSQ runtime turn管理/证据取回与终结输出
  - harness严格main summary契约，官方reward独立

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ runtime artifact filter/read_artifact_slice与agent loop`：将AI verdict/explanation/引用以紧凑结构直接暴露，避免重复切片同一结果；追踪已覆盖字段证据，已有等价证据不再重复抓取，保留终结输出轮次。
- **P1 / FSQ**；`FSQ main runner AgentFinalOutput终结路径`：在现有100-turn范围内及时输出task_run_v1；检查与业务字段相关的真实缺证据，而非不停重读已完成的Dress/Furnishing断言。
- **P0 / harness**；`harness fsq_worker.select_main_answer/统计展示`：保持严格summary契约，但独立呈现official1、runner-error、verifier-inconclusive；不得用verifier替代main或把passed改失败。

**未来验证（全部未执行）**

- 离线events去重与计数：read_slice23、write46/60、seq221 turn-limit；exact main_summary失败但officialReward仍1。
- 独立图库新增实例：不额外增加maxTurns/maxActions，保存后生成完整main summary，并在私有官方评分中确认3行/字段/无副作用。

**双方逐例核对**

已核对：保存三费用且passed1保留；23artifact读后100turn主summary失败，不改成invalid。

**交叉核对：已核对（FSQ↔harness owner逐例回执）。原passed/1保留；configured turn limit、46/60且零拒绝/无deadline、23次重复读与三条保存已核对；main summary缺失单列，不重标invalid_agent。工件封装/历史裁剪的因果仍为强推断。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例013，起始第75行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/9`。
- [原公开goal](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：247-281；symbol：_ExpenseAddMultiple.validate_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：118-192,257-310；symbol：SQLiteApp/AddMultipleRows/validate_rows_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：379-408；symbol：ExpenseAddMultipleFromGallery.initialize_task；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-014"></a>
### 案例 014 — ExpenseAddMultipleFromMarkor

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Go through the transactions in my_expenses.txt in Markor. Log only the rows whose reimbursable field is yes in the pro expense; do not log rows marked no. Copy each original note unchanged from the note field. The reimbursable field is selection metadata, not part of the note.

**约束与冻结初始化**

- **publicGoal**：Go through the transactions in my_expenses.txt in Markor. Log only the rows whose reimbursable field is yes in the pro expense; do not log rows marked no. Copy each original note unchanged from the note field. The reimbursable field is selection metadata, not part of the note.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/sources/000-goal.txt
- **requirementsNote**：官方missing expected row日志与reward0符合两条yes均未新增；native错误也是100turn无main summary。但不能根据若干可见no断言初始化没有yes，不能把已有no噪声当违规新增。
- **nativeDerivedVerificationGoal**：Pro Expense contains one newly saved expense for each source row marked reimbursable=yes, none for rows marked no, with transaction details matching the source and each note exactly equal to its original note field without added reimbursable metadata.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/report.json
- **判据**：期望yes两行Laundry $96.30/Clothes(8)/Urgent，Car Insurance $303.01/Transportation(7)/I may repeat this。与100 no行有同名/近似值风险，不按name猜。冻结源码说明应有102行，存量证据未保存原始设备文件字节/生成后的完整文档，不重建shuffle。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：100

**官方判据**

- **判据**：清Expense DB插入100 noise，并冻结2目标。Markor CSV pipe分隔，header含reimbursable；2个row_objects写yes、100个noise写no，shuffle后完整文件my_expenses.txt。只新增yes；name fuzzy，amount分整数/category精确，note严格相等（_free_form_fields仅name），条数before+2，原100行不变。selection metadata不得拼进note。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：
    - **createdAtUnix**：1794329209.8207538
    - **logger**：absl
    - **level**：30
    - **file**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py
    - **function**：validate_rows_addition_integrity
    - **line**：168
    - **messageTemplate**：Expected row %s not found in the 'after' state.
    - **arguments**：
      - **type**：tuple
      - **items**：
        - **omittedType**：Expense
        - **reason**：unsupported_type_or_size_or_depth
      - **omittedItems**：0

**原关键轨迹**

- agent-tap_on-7 passed：打开my_expenses.txt。
- agent-tap_on-9 passed：切preview。
- agent-assert_with_ai-11 passed：只转录当前可见若干no行，自己说明还需scroll；UI XML长text压成前50字符，不能据XML搜yes判整文件没有。
- agent-assert_with_ai-13 passed：下滚后局部可见行全no，AI称apparent bottom；不是102行全覆盖证明。
- agent-assert_with_ai-16 passed：回顶部读取header至Gym Membership；局部均no。
- agent-assert_with_ai-18 passed：中间viewport均no；没有原始完整源文件计数或连续覆盖证明。
- agent-tap_on-23 passed：切Pro Expense，未开新增表单。
- agent-ui_snapshot-24 passed：已有noise例如Reimbursements385.81/Doctor Visits75.54，并不能当本次新增no行。
- agent-ui_snapshot-42 passed：最后仍重复取Pro Expense快照；整个轨迹无新增/save。

原dispatch额度 12/60，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 官方missing expected row日志与reward0符合两条yes均未新增；native错误也是100turn无main summary。但不能根据若干可见no断言初始化没有yes，不能把已有no噪声当违规新增。
- 没有任何expense-entry/save动作，2条期望未新增；切Pro Expense后以重复检索旧AI“都是no”结论代替继续读全源文档。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 官方diagnostic log sqlite_validators.validate_rows_addition_integrity L168：Expected row not found；不是异常评分。
  - report verification_goal正确保留yes筛选与原note；执行未实施，不是planner公开目标漏note约束。
  - events seq73是最后一个业务写tap Pro Expense；之后seq79、85、87至213/215/217重复search同AI输出的explanation，ui_snapshot循环，无doc滚动/无entry。
  - events tool starts search_artifact=55；seq221 run_failed turn-limit；write12/60、denied0、deadline=false，故不属于动作或墙钟超限。
  - step11/13原UI snapshot compaction.text_attribute_limit=50；长文档text只留header前50字符。截图含更多行，但不能用截断XML文本检索来证明全文件no。
- **强推断**：
  - 强推断：把局部可视转录“当前均no”升级成全文件无yes的消极结论，再用不改变业务状态的证据检索回路寻求确认，导致完全未新增并耗尽turn；同时UI XML 50字符长文本裁剪妨碍全文件定位。
- **无法确认与缺证据**：
  - 现存source截图并不覆盖全部102行；无法最终区分yes在未遍历区域、Markor preview显示/滚动范围截断、或初始化源文件内容与冻结预期不一致。不得声称已证实初始化正确，也不得声称文件真的全no。
- **备选及区分**：
  - 若将来私有初始化文件证明只写了no，则责任转为harness初始化/文档写入，不能只归模型阅读；当前证据无法定案。
  - 已有no条目来自初始化noise，不能当作本run新增违规。
- **责任层**：
  - FSQ长文档覆盖/negative证据推理
  - FSQ无进展artifact-loop/turn预算
  - harness初始化原文件证据缺口待区分

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ Markor长文档reader / UI snapshot语义压缩`：保留长text的截断标记/原artifact可定位边界；按连续viewport、首末行/滚动停滞建立覆盖表，搜选取字段而非仅读取局部no；未全覆盖不得宣称无yes。不得注入冻结目标行。
- **P1 / FSQ**；`FSQ artifact evidence reader / runner termination`：search相同artifact/explanation无新信息时停止重复读取，返回源文档补最小缺口或结构化说明未知；在既有100turn内收敛，不靠加预算。
- **P1 / harness**；`harness ExpenseAddMultipleFromMarkor.initialize_task诊断产物`：私有保存生成后的源文件字节/row数/yes-no数量与写入回读凭据供离线调查；不向agent提供oracle期待行；不改note或评分。

**未来验证（全部未执行）**

- 离线仅对既存init与完整源字节（若能找到）核对102行和2yes；当前缺源字节，明确为缺证据而非重建数据。
- 独立Markor来源任务在合法UI全覆盖后只新增yes，note逐字、金额/cat精确且噪声不变；同时确保main结构化输出，预算60/100不变。

**双方逐例核对**

已核对，有保留：无新增+55search+100turn；局部no不证明全文件no，目标行缺口/渲染原因未知。

**交叉核对：已核对、有保留（逐例回执）。12/60零拒绝、55次search、无新增及max_turns双方一致；局部no不能证明全文件no。yes所在未覆盖段或渲染异常仍未知，不把模型漏看具体yes写成事实；原failed/0保留。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例014，起始第97行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/10`。
- [原公开goal](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：247-281；symbol：_ExpenseAddMultiple.validate_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：118-192,257-310；symbol：SQLiteApp/AddMultipleRows/validate_rows_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：324-372；symbol：ExpenseAddMultipleFromMarkor._get_expenses_as_text/initialize_task；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/utils/user_data_generation.py；lines：203-216；symbol：write_to_markor；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-015"></a>
### 案例 015 — ExpenseAddSingle

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the following expenses into the pro expense:
> Expense: Therapy Sessions
>  amount_dollars: $307.01
>  category_name: Health Care
>  note: I may repeat this
> 

**约束与冻结初始化**

- **publicGoal**：Add the following expenses into the pro expense: / Expense: Therapy Sessions /  amount_dollars: $307.01 /  category_name: Health Care /  note: I may repeat this / 
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566/sources/000-goal.txt
- **requirementsNote**：输入表单不是新增数据库；Save从未执行，官方missing row=0符合契约。不是金额分/美元换算或分类错误。
- **nativeDerivedVerificationGoal**：The saved Therapy Sessions expense shows an amount of $307.01, category Health Care, and note "I may repeat this".
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566/report.json
- **判据**：Expense DB清空后插10noise。goal已直接给全部四字段，无需跨app找来源。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：10

**官方判据**

- **判据**：仅新增Therapy Sessions，amount=30701分、category=9 Health Care，note=I may repeat this；name/note fuzzy、amount/category精确；总条数+1且原10noise完全保持。创建时间不按冻结参考expense.created_date比对。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：
    - **createdAtUnix**：1794329373.618113
    - **logger**：absl
    - **level**：30
    - **file**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py
    - **function**：validate_rows_addition_integrity
    - **line**：168
    - **messageTemplate**：Expected row %s not found in the 'after' state.
    - **arguments**：
      - **type**：tuple
      - **items**：
        - **omittedType**：Expense
        - **reason**：unsupported_type_or_size_or_depth
      - **omittedItems**：0

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch1成功但看到launcher。
- agent-launch_app-3 passed：第二次launch。
- agent-tap_on-6 passed：应用抽屉选择Pro Expense才进入。
- agent-tap_on-8 passed：打开Entry。
- agent-input_text-10 passed：name Therapy Sessions。
- agent-input_text-11 passed：amount307.01。
- agent-press_key-12 passed：收键盘。
- agent-swipe-14 passed：水平滚动类别栏。
- agent-tap_on-16 passed：选择Health Care。
- agent-input_text-17 passed：note I may repeat this。
- agent-press_key-18 passed：收键盘，第12写。
- agent-tap_on-20 failed：Save被dispatch预算拒；after截图Entry四字段都对、Health Care有勾、SAVE仍在。
- agent-tap_on-21 failed：同一不可恢复拒绝再尝试Save，再失败。
- agent-kill_app-22 failed：kill也拒。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 输入表单不是新增数据库；Save从未执行，官方missing row=0符合契约。不是金额分/美元换算或分类错误。
- 12写用尽才Save，第13写起全部拒绝。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 原Entry截图四字段完整且Health Care选中；目标30701分正确输入307.01 USD。
  - audit前4写为双launch+抽屉+icon；Save拒seq39/40；diagnostic L168 missing expected row。
- **强推断**：
  - 强推断：无效启动路径额外消费约3写，planner又没有为commit预留写槽；以输入完成代替save完成判断进度，Save成为预算边界外动作。
- **无法确认与缺证据**：
  - 具体launch成功但仍launcher的底层原因交FSQ owner；不能假定设备故障。
- **备选及区分**：
  - 即便UI时间显示15Oct与目标参考created_date不同，官方不按created_date比较新增，不能拿日期当失败原因。
- **责任层**：
  - FSQ launch/预算规划
  - harness如约计费拒绝

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ launch_app / task planner预算模型`：一次有效启动，避免重复launch+launcher迂回；安排输入/选category/Save的完整commit路径并在原12写内预留Save；NativeActionBudgetExceeded后不重试。

**未来验证（全部未执行）**

- 离线断言前12write均admitted，第13Save未forward；表单字段正确但row未新增。
- 独立ExpenseAddSingle在12写内保存，官方校验4字段与+1/噪声保持；不增加预算。

**双方逐例核对**

已核对：字段正确但Save预算前拒，missing expected row诊断相容；不宣称原12写必无解。

**交叉核对：已核对。** 四字段正确、Save未forward、diagnostic168 missing row；不声称原12写必无解。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例015，起始第40行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/11`。
- [原公开goal](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：247-281；symbol：_ExpenseAddMultiple.validate_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：118-192,257-310；symbol：SQLiteApp/AddMultipleRows/validate_rows_addition_integrity；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：308-313；symbol：ExpenseAddSingle；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-016"></a>
### 案例 016 — ExpenseDeleteDuplicates

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.

**约束与冻结初始化**

- **publicGoal**：Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae/sources/000-goal.txt
- **requirementsNote**：需要比较并删掉一条Public Transit；实际两条已在可读artifact/截图中却进入无必要的日期探查，从未删除。official0是完整DB仍有重复，native inconclusive只因为它未用初始化事实。
- **nativeDerivedVerificationGoal**：Pro Expense contains exactly one instance of each originally distinct expense, with no exact duplicates remaining and no unique expense lost.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae/report.json
- **判据**：Public Transit金额20441分/Transportation7/note A need/created=modified1696132800000；实际两个204.41/2023Oct1在一屏列表底部已同时可见。参考日期Oct15，但列表默认筛选Oct1-14；该范围已包含两条目标。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：5

**官方判据**

- **判据**：清DB插5noise+两个完全相同的Public Transit，初始化验证行数7且除expense_id外每字段相同。成功仅能删除两个target ID之一，另一个与全部5noise必须原样保留，不得新增/误删。不是只凭相同name判断，也不是删除两条。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-2 passed：首次launch后launcher，重复launch+抽屉/icon。
- agent-tap_on-8 failed：XPath //node[...]查不到；这是源XML node标签与底层Appium类树差异的可能点，不能当终极根因。
- agent-tap_on-9 failed：仅换/*仍查不到，第二次计费失败。
- agent-tap_at-10 passed：坐标打开drawer。
- agent-ui_snapshot-13 passed：原artifact000014包含完整7行：5noise+Public Transit两条，均204.41/Oct1；截图下一步filter前亦可见。
- agent-tap_on-14 passed：不先比目标details，转去filter。
- agent-tap_on-16 passed：点start date。
- agent-tap_on-18 passed：点year。
- agent-tap_on-20 passed：Cancel回filter；日期范围未改。
- agent-press_key-22 failed：第13写Back被预算拒；filter还开着。
- agent-press_key-23 failed：无恢复可能重复Back再拒。
- agent-kill_app-24 failed：kill亦拒，无删除。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 需要比较并删掉一条Public Transit；实际两条已在可读artifact/截图中却进入无必要的日期探查，从未删除。official0是完整DB仍有重复，native inconclusive只因为它未用初始化事实。
- 没有expense deletion动作；写12/12在导航、两次失效XPath和filter date/year/cancel上耗尽，目标组早已可见。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 000014-ui_snapshot.json中两条Public Transit与对应204.41/Oct1均在原XML和截图出现；不是“因过滤器完全看不到目标”。
  - 官方初始化会创建并验证这对真实duplicate，因此不能沿用native verifier“没证明初始有duplicate”的保守假设。
  - seq15/17两次failed tap也各消耗一写；seq43/44/45拒Back/Back/kill，无删除。
- **强推断**：
  - 强推断：将全局无重复证明当作必须先取消任何日期filter，忽略已足够定位的可见组；再用不匹配底层树的XPath重复试与日期探查消耗完commit预算。
- **无法确认与缺证据**：
  - 未存最终DB完整快照，但源初始化+零删除+official0已充分支持未去重；无需推测误删。
  - XPath底层接受的树格式具体接口由FSQ owner确认。
- **备选及区分**：
  - 日期filter的Oct14确与Oct15参考日不同，但不是本例目标不可见原因，也不应直接修改初始化/rubric。
- **责任层**：
  - FSQ观察→动作规划失配
  - FSQ selector基于真实动作空间能力
  - harness预算成本

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ duplicate planner/数据字段比较`：先消费已有7行与两相同候选的证据，打开候选details比较字段，只删一条；不用为“证明全局范围”先走与当前组无关的filter日期流程。
- **P1 / FSQ**；`FSQ selector生成/runner budget`：使用真实Appium class tree的已暴露定位器或已有明确图标/可访问性定位；第一次Target not found后用新观察修正，不重复同错误树假设；保留delete+confirm预算。

**未来验证（全部未执行）**

- 离线用该7行artifact证明两目标同屏及filter包含Oct1；预算成本归因为12写而非额外墙钟。
- 独立小型duplicate实例：删除一条后私有DB严格剩6行，所有noise与保留target字段不变，原12写。

**双方逐例核对**

已核对：同屏不等于已证exact；XPath失败照约计费，仅删1target/保noise要求不变；DB终态未知。

**交叉核对：已核对、有保留。** 同屏两条Public Transit仅候选非已核exact；XPath失败计费合约；oracle仅删一个target ID且noise不变，终DB未知。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例016，起始第74行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/12`。
- [原公开goal](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369,380-415；symbol：validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：148-195；symbol：_ExpenseDeleteDuplicates.validate_deletion_integrity/ExpenseDeleteDuplicates；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-017"></a>
### 案例 017 — ExpenseDeleteDuplicates2

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.

**约束与冻结初始化**

- **publicGoal**：Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7/sources/000-goal.txt
- **requirementsNote**：需要找到Oct1真重复、核对details并删一条；真实滚动只至Oct2，中途多次filter无改动且未跟踪全列表覆盖，official0符合零删除。
- **nativeDerivedVerificationGoal**：Pro Expense contains exactly one instance of every originally present unique expense, with all surplus exact duplicates removed and no unique expense lost.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7/report.json
- **判据**：真重复Jeans49636分/Clothes8/note Want to have/created=modified1696118400000（Oct1）；近似Jeans49938、50010、50198分，日期也不同，均不得删。默认filter2023Oct1-15覆盖这些日期，不能只看名字。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：40

**官方判据**

- **判据**：42行=40noise+2完全相同Jeans，仅允许删除这两个target ID之一；必须保留其余所有行，包括3条同名但金额和created/modified不同的Jeans近重复。保留一条每unique的公开goal，与官方只删精确一ID一致。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-11 passed：首个expense log列表范围Oct1-15，底部出现较近日期的Jeans近似行。
- agent-tap_on-12 passed：第一次filter。
- agent-tap_on-14 passed：start date后Back/Back，不应用新范围。
- agent-tap_on-20 passed：重复filter→Back。
- agent-ui_snapshot-25 passed：滑到Jeans等日期Oct12/9/7区域，不是targetOct1。
- agent-ui_snapshot-27 passed：继续降序到Oct6附近Jeans。
- agent-ui_snapshot-29 passed：继续到Oct3。
- agent-tap_on-30 passed：又filter→Back，范围未改。
- agent-ui_snapshot-35 passed：最后列表只到Gym Membership/Oct2；还没读到Oct1重复目标。
- agent-assert_state-36 failed：contains filter text失败，属于断言文本处理非任务目标。
- agent-assert_visible-38 passed：同一个完整filter label可见断言成功，但没有验证去重。
- agent-kill_app-39 failed：18/18写用满，kill拒；仍从未执行删除。

原dispatch额度 18/18，denied=1，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 需要找到Oct1真重复、核对details并删一条；真实滚动只至Oct2，中途多次filter无改动且未跟踪全列表覆盖，official0符合零删除。
- 零删除，真实重复组尚在最后未遍历区域；label断言成功不能替代数据库去重。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - source初始化验证双target；真实target与三变体的金额/日期不同均在冻结params中，不能删除同名就算。
  - 000042/000044 snapshot最后可见Gym Membership Oct2；同屏没有真target496.36。
  - 18写分解：双launch/抽屉/icon4；drawer/log2；filter/date/Back/Back/filter/Back6；4次swipe4；最后filter/Back2；共18，无delete。
- **强推断**：
  - 强推断：重复filter未带来新范围或新信息占去关键写槽；对排序列表缺少明确覆盖/尾部判据，停在Oct2便结束，没有到达Oct1真实组。保守不误删近似Jeans正确，但计划未完成必要查找。
- **无法确认与缺证据**：
  - 没有最终DB逐行快照；不能声称近似Jeans被误删（轨迹没有删除）。
  - 不得根据最后label Oct1-15就宣称已经遍历该全区间；label只是过滤条件。
- **备选及区分**：
  - 不是“filter排除了Oct1目标”；已见标签范围明确包括Oct1，失败在遍历未完成与预算分配。
- **责任层**：
  - FSQ列表覆盖/精确重复判别规划
  - artifact片段与全集合混淆
  - harness写预算

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ duplicate collection traversal/coverage memory`：建立按排序日期/首末可见行的覆盖，未到scroll end不宣称全面；只对同名候选比较amount/category/note/日期，保留近似变体；不要重复打开不需改的filter。
- **P1 / FSQ**；`FSQ planner预算收敛`：原18写内移除重复filter和无效启动，把额度用于到达列表尾与一次delete/confirm；拒绝后不无意义cleanup重试。

**未来验证（全部未执行）**

- 离线断言真重复496.36两条与499.38/500.10/501.98近似三条不可混组；最后Oct2≠全覆盖。
- 独立40noise dedupe样例仅删一真重复，剩41行，3近似行逐字段不变，18写不变。

**双方逐例核对**

已核对：真Oct1组尚未覆盖，三近似金额应保留；未尝试删，唯一denied为kill。

**交叉核对：已核对。** Oct1尾两条Jeans496.36未覆盖，499.38/500.10/501.98必须保留；从未删，唯一denied为kill，不写删除被挡。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例017，起始第109行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/13`。
- [原公开goal](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369,380-415；symbol：validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：163-174,198-230；symbol：_ExpenseDeleteDuplicates.validate_deletion_integrity/ExpenseDeleteDuplicates2.generate_random_params；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-019"></a>
### 案例 019 — ExpenseDeleteMultiple2

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete the following expenses from pro expense: Streaming Services, Unexpected Expenses, Pet Supplies.

**约束与冻结初始化**

- **publicGoal**：Delete the following expenses from pro expense: Streaming Services, Unexpected Expenses, Pet Supplies.
- **publicGoalPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64/sources/000-goal.txt
- **requirementsNote**：实际只删Streaming/Unexpected。Pet从最初同屏就可见、第一次删除后仍可见，但没有任何Pet删除动作；official0不是它从一开始就不存在。
- **nativeDerivedVerificationGoal**：The Pro Expense expense list no longer contains Streaming Services, Unexpected Expenses, or Pet Supplies.
- **nativeReportPath**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64/report.json
- **判据**：目标Streaming48725分/Entertainment6/Oct15 03:00，Unexpected26950分/Others1/Oct11，Pet19095分/Others1/Oct15 00:00；默认Oct1-15降序。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseRowCount**：50

**官方判据**

- **判据**：53行=50noise+Streaming Services、Unexpected Expenses、Pet Supplies各一目标；3个target ID必须全删，所有50noise完全不变，不得新增。二元评分，不按删两项给2/3。
- **diagnostic**：
  - **path**：evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/evaluator-diagnostics.json
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
  - **outcome**：returned
  - **reward**：0.0
  - **exception**：null
  - **logRecords**：

**原关键轨迹**

- agent-ui_snapshot-11 passed：000012原XML和随后longpress12前截图，Pet Supplies190.95/Today12:00AM就在Streaming下一行。
- agent-long_press_on-12 passed：选择Streaming。
- agent-tap_at-14 passed：点关联delete。
- agent-tap_on-16 passed：confirm；snapshot17 Streaming消失，Pet Supplies仍在列表顶部。
- agent-ui_snapshot-17 passed：000021再确认Pet Supplies可见，之后却只搜Unexpected并下滑。
- agent-long_press_on-22 passed：定位Unexpected。
- agent-tap_at-24 passed：误点Restaurant Meal详情（142.94、Oct12、note I may repeat this），不是Delete确认；随后btn_close关闭，未误删。
- agent-tap_on-26 passed：Close关闭Restaurant Meal详情，未删除该非目标。
- agent-tap_at-28 passed：重新按Unexpected关联delete坐标。
- agent-tap_on-30 passed：confirm后snapshot31 Unexpected消失。
- agent-ui_snapshot-41 passed：一路向较早日期滚到Oct1；Pet是Oct15顶部，后续只在离开顶部后的snapshots搜Pet。
- agent-assert_not_visible-43 passed：只证明当前屏没有Pet，绝非全列表无Pet。
- agent-kill_app-44 passed：显式kill Expense成功；DB型oracle不要求app前台，不是此例核心因果。

原dispatch额度 23/34，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 实际只删Streaming/Unexpected。Pet从最初同屏就可见、第一次删除后仍可见，但没有任何Pet删除动作；official0不是它从一开始就不存在。
- 漏掉最初可见的Pet；之后单向下滚和当前屏not_visible掩盖漏项，未回到顶部。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 000012/000015/000021三份原UI均含Pet Supplies；本调查直接读XML并看截图，不接受native“Pet未定位”的总结为事实。
  - events seq47只搜初始列表Streaming；Pet第一次search出现在seq101对000039（已远离顶部），之后seq107/113/119/125/131也只搜后续更早日期view，从未回查000012/000021。
  - 只有两次已确认删除流程，预算23/34、denied0、deadline=false，尚余11写；不是预算或墙钟自然逼停。
- **强推断**：
  - 强推断：多目标任务没有维护每目标见过的位置/完成状态，先为一个target导航后遗忘同屏另一target；后来把局部absence当全局absence，提前终结。工具大XML片段化使这一遗漏更容易，但不是证据缺失。
- **无法确认与缺证据**：
  - 没有评分时完整after DB来排除所有噪声副作用；第一次错误打开Restaurant Meal详情后已关闭、未删除，后续两目标确认与快照吻合；不虚构具体噪声损坏。
- **备选及区分**：
  - 不是Pet被日期filter排除；初始范围内它清楚可见。不是UI不支持delete；其他两条已成功。
- **责任层**：
  - FSQ多目标状态记忆/列表搜索策略
  - FSQ assertion范围语义
  - 非harness budget限制

**修复方案（未实施）**

- **P1 / FSQ**；`FSQ multi-target planner/working memory`：维护每目标observed位置、pending/deleted集合；同屏目标均登记，滚走后可回定位。对局部not_visible严格标viewport，不当full collection证明；回查既有完整artifact或回顶部处理Pet。
- **P1 / FSQ**；`FSQ before-delete locator binding`：每个delete图标绑定同一行name/id，并在confirm前核对dialog，保留已有取消误点的正确行为。

**未来验证（全部未执行）**

- 离线断言初始/首删后Pet存在；对000039以后的not_visible只证明该viewport；task pending应仍含Pet。
- 独立多删除53行实例3目标全无、其余50行逐字段保持，34写内完成，不重复同题凑分。

**双方逐例核对**

已核对并补正：Pet先可见后只下搜，23/34无denied正常提前停；Restaurant Meal详情不是Delete确认/误删。

**交叉核对：已核对、有保留。** Pet首屏可见后来只下搜且正常提前停；S24 Restaurant Meal142.94详情、S26关闭非误删。Pet残留强推断，终DB未存，不称唯一已证0因。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例019，起始第144行。
- [harness独立完整源码/step/截图记录](harness-notes/early.json)，JSON pointer `/cases/14`。
- [原公开goal](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/expense.py；lines：72-99,140-145；symbol：_ExpenseDeleteMultiple.validate_deletion_integrity/ExpenseDeleteMultiple2；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369,380-415；symbol：validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows；version：candidate-final-manifest.json identities.androidWorld.installed（本调查直接读冻结installed，不使用当前仓库替代）`

<a id="case-023"></a>
### 案例 023 — MarkorAddNoteHeader

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Update the Markor note 2023_08_10_neat_wolf.txt by adding the following text, along with a new blank line before the existing content: "RnI8sP34yDzJQbvkfplR", and rename it to busy_wolf_2023_07_23.txt.

**约束与冻结初始化**

- 给2023_08_10_neat_wolf.txt加RnI8sP34yDzJQbvkfplR，后接一空行与原文；最终重命名为busy_wolf_2023_07_23.txt。
- 官方要求最终内容与文件名，不要求特定“插入-only”交互。
- **已记录初始化**：清空MARKOR_DATA，创建带末尾换行的原文Weekend plans: Hiking trip to Blue Mountain.及同名干扰文件；初始化冻结referenceTime=2023-10-15T15:34:00+00:00。step9实际看到了目标原文。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：先检查旧名必须不存在、新名必须存在；新文件精确匹配header+\n\n+original_content+\n。不是仅看编辑器前缀，也没有部分分。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch通过却仍在Launcher。
- agent-ui_snapshot-9 passed：原文真实可见，header内容可从goal取得。
- agent-input_text-11 passed：Move Home后调用的是清空再替换；此时原文被覆盖。
- agent-ui_snapshot-12 passed：只剩header与空行，证实不是插入。
- agent-input_text-13 passed：用刚读到的原文重建完整期望文本。
- agent-tap_on-14 passed：Save调用通过。
- agent-tap_on-19 passed：误入File settings而不是重命名入口。
- agent-ui_snapshot-20 passed：实际是Wrap words/Font Size设置页，无Rename。
- agent-press_key-21 failed：首个拒绝：第13个write，action_budget。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 内容补救曾输入正确组合且Save通过，但旧名仍在编辑标题、未进入/确认重命名，官方第一项“旧名消失”不满足。不能仅以UI截断文本证明落盘逐字一致。
- 重命名根本未完成；12次admitted全部用尽后Back和teardown被拒。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 启动成功标签未对应前台，消耗2次launch+swipe+launcher tap后才真正进入Markor（steps1-7，共4个write）。
  - 输入替换契约与“插入”预计划不一致，产生第13步重写补救；随后进入File settings，未找到rename。
  - budget audit seq41/42/43拒绝Back/Back/kill；deadlineExceeded=false。
- **强推断**：
  - 无重命名调用、旧名标题及official 0共同支持在is_successful的旧名存在分支返回0。diagnostic未提供分支日志，不能称已直接读取最终文件系统。
- **无法确认及备选**：
  - 未有oracle时刻文件内容/目录快照；最终精确字节与旧名分支是强推断而非独立私有文件转储。
  - 启动为何停在Launcher由FSQ owner核对；不能归咎旧AMK。
- **责任层**：
  - FSQ launch/text contract
  - FSQ UI flow selection
  - harness fixed dispatch budget amplifies

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 / FSQ skill/planner owner**；`resources/skills/android-harness.md; drivers/android/_uiautomator2.py::input_text description; goal pre-plan`：把input_text的click/clear/set_text整字段替换语义告知planner。header任务先读取可见原文，用现有replacement写入header+指定换行+已观察原文，再Save；不把Move Home+input_text误当插入，不添加官方没有的“必须只用插入操作”验收。长文读不全时先取得完整UI证据，不能拿frozen私有params补内容。
- **P1 / FSQ planner/knowledge owner**；`Markor rename flow using observed file-browser selection controls`：Save后回到文件列表，长按当前精确文件名→action_rename_selected_item→输入新名→OK；不在File settings试探。只存公开app交互知识，不存任务答案。

**未来验证（全部未执行）**

- 离线fake selector：input_text清空+set_text语义、header恢复文本组合及所需write预算均与计划一致；不改变12上限。
- 设备新题：rename确认后从UI重开正确新名；官方单次oracle核对旧名不存在及新文件精确换行/末尾换行。

**双方逐例核对**

已核对：替换误当插入后恢复，错进File settings且rename未做；落盘字节未知。

交叉核对：已核对。替换误当插入→恢复→File settings不是rename；旧名/落盘字节未存，不假称磁盘核验。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例023，起始第315行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/0`。
- [原公开goal](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：754-774；symbol：MarkorAddNoteHeader.initialize_task；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：784-806；symbol：MarkorAddNoteHeader.is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：555-584；symbol：check_file_content exact bytes when exact_match=True；versionBinding：official_installed_frozen`

<a id="case-024"></a>
### 案例 024 — MarkorChangeNoteContent

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Update the content of strong_jacket_h1hZ.txt to "inNqu8UNNtyXBHCZpYp7" in Markor and change its name to lively_fox_2023_03_22.md.

**约束与冻结初始化**

- 将strong_jacket_h1hZ.txt内容改为inNqu8UNNtyXBHCZpYp7并重命名为lively_fox_2023_03_22.md。
- **已记录初始化**：清空Markor目录；创建原名随机内容与噪声文件。step9读到pZwh1hZwvmPj5inNqu8U，符合现场初始化而非拿私有params猜原文。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：旧名不存在、新名存在，再由check_file_content判新文件内容；三者同时满足才1。官方没有“最终必须展示某屏”的额外评分条件。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch通过却仍Launcher。
- agent-input_text-10 passed：替换为要求的新内容。
- agent-ui_snapshot-12 passed：编辑器可见正确新内容。
- agent-tap_on-13 passed：Save通过。
- agent-long_press_on-16 passed：回文件列表长按精确旧名。
- agent-ui_snapshot-19 passed：重命名对话框真实打开。
- agent-input_text-20 passed：新名称进入new_name，但尚未提交。
- agent-tap_on-21 failed：OK前write预算已满，未派发到设备。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 内容输入和Save已执行，rename仅填写输入框；OK两次均budget拒绝，不能把“键入新名”算改名完成。
- 重命名提交被拒，旧文件未完成改名，因此即便原文件内容已更新也拿0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 4个write才从Launcher进入Markor；此后编辑/Save/返回/长按/Rename/输入新名恰好耗完12。
  - audit seq41/42/43拒绝OK重试及kill，deadline未到。
- **强推断**：
  - official 0最可能由旧名仍在直接返回；缺最终目录转储但对话框未确认事实充分。
- **无法确认及备选**：
  - 无最终落盘字节或oracle分支日志。
  - 如果启动后置条件修复，能否在同预算下完成全部业务需未来设备验证，不能直接宣布必过。
- **责任层**：
  - FSQ launch postcondition
  - FSQ commit-aware planning
  - harness budget boundary

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 / FSQ planner owner**；`Markor rename state tracking / goal pre-plan`：把rename的OK提交列为必须动作并在固定预算内规划；输入框文本不算完成。保留Save/提交动作优先于重复launch和无效retry。

**未来验证（全部未执行）**

- 预算离线回放在第12次admission后准确拒绝新write，不把拒绝的OK标成功。
- 设备新题：全程预算12，内容编辑后完成rename OK；官方只评一次，核对旧名/新名/内容。

**双方逐例核对**

已核对：正文replacement正确，rename OK未forward；不套023原文破坏。

交叉核对：已核对。replacement正确、rename OK未forward，不套023原文破坏；持久字节仍未知。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例024，起始第363行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/1`。
- [原公开goal](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：671-690；symbol：MarkorChangeNoteContent.initialize_task；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：700-721；symbol：MarkorChangeNoteContent.is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：555-584；symbol：check_file_content fuzzy default；versionBinding：official_installed_frozen`

<a id="case-027"></a>
### 案例 027 — MarkorCreateNoteAndSms

**原身份：failed / officialReward=0.5；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Create a new note in Markor named fair_ant_XOdi.txt with the following text: Actions speak louder than words.. Share the entire content of the note with the phone number +13192815309 via SMS using Simple SMS Messenger

**约束与冻结初始化**

- 创建fair_ant_XOdi.txt，文本为Actions speak louder than words.，并通过Simple SMS Messenger将全文发给+13192815309。
- public goal的模板再追加句号，实际出现words..；runner按可见goal输入双句号，不可据此单独判定正文根因。
- **已记录初始化**：清空Markor，构造note子任务；SMS初始化关闭飞行模式并清空SMS/threads，避免旧记录给分。本次diagnostic仅标量返回0.5、无子分日志。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：(MarkorCreateNote + SimpleSMSSendSms)/2。note是精确路径存在+fuzzy正文；SMS需目标号码/body近似匹配的已发记录在时间窗内且当前前台是com.simplemobiletools.smsmessenger。0.5是完成一子任务，不是全失败。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.5
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-2 passed：Markor launch仍Launcher。
- agent-input_text-14 passed：按public goal的双句号输入正文。
- agent-tap_on-17 failed：target Save用text精确查找失败；toolbar Save在UI是content-desc。
- agent-tap_on-19 passed：用resourceId Save恢复通过。
- agent-ui_snapshot-25 passed：Android分享面板确有完整双句号正文。
- agent-input_text-28 passed：填写正确收件号码。
- agent-press_key-29 passed：Enter调用通过但未确认收件人。
- agent-ui_snapshot-30 passed：仍New conversation recipient entry，未进入发送。
- agent-tap_on-31 failed：收件人confirm被预算拒绝，Send计划未执行。

原dispatch额度 18/18，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- note已创建/保存/分享且正文fuzzy可容忍句号；SMS只到收件人输入，未确认、无Send和已发记录。结合0.5，note=1/SMS=0为强证据推导，diagnostic本身未单独吐这两个数字。
- 0.5部分完成保留；SMS业务提交未发生是直接缺口，note1/SMS0只列强推断而非独立子分日志，不能称全失败。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 18个write全部admitted，包括无效果的2次launch、launcher绕路、Save target失败及Enter未完成确认。
  - audit seq61拒绝recipient confirm、seq62拒绝kill；未发生发送，deadlineExceeded=false。
  - official reward为0.5且composite官方平均公式成立。
  - 原report.json/task.verification_goal仅剩SMS已发送目标，遗漏独立note持久子目标；这次未因此伪报success，但未来必须保留两者合取。
- **强推断**：
  - 子分note1/SMS0：轨迹没有SMS发送、但note保存与分享正文可见，且总分0.5。没有标量诊断以外的子分日志，须保留此证据级别。
- **无法确认及备选**：
  - 没有最终note私有字节或sent-table快照；不编造SMS provider/网络发送错误。
  - S32默认kill目标为Markor，且action_budget在forward前拒绝，没有杀SMS。仅未来确实停止前台SMS才有foreground风险，不能从默认kill Markor推导该风险已发生。
- **责任层**：
  - FSQ launch/locator contract
  - FSQ SMS recipient flow
  - harness fixed budget
  - FSQ composite verification-goal coverage loss

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 / FSQ skill/locator owner**；`drivers/android/_uiautomator2.py::_selector; Markor/SMS UI flow`：根据UI属性使用Save的resourceId/accessibilityId，不把target当content-desc；SMS在收件框后点当前new_conversation_confirm，再检查compose/body并Send，Enter无状态变化不能算确认。
- **P1 / FSQ preplan/verification owner**；`agent/_core.py::_augment_goal_only_task_with_pre_plan:155-159,201; agent/_verification_task.py::VerificationEvidenceBuilder.build:51-56`：保留公开复合goal的两个独立合取条件：精确命名note已保存 AND 全文SMS已发；分别检查证据，不让verification_goal只剩最后SMS动作。该遗漏不是本次未Send的直接原因，但完成短信后也不能据此忽略note。原kill默认Markor且被拒，不改写为已杀SMS。
- **P2 / harness reporting owner**；`composite score reporting (private diagnostics only)`：继续保存数字0.5与已有标量诊断；若以后增加子项审计，必须在同一次官方评估中非侵入记录，不改变平均rubric也不向业务agent泄露子项oracle。

**未来验证（全部未执行）**

- 离线：composite报告保留0.5；target精确text与accessibilityId区别；不把SMS收件输入成功当发送。
- 设备新题：同18上限完成note、recipient确认、Send并保持SMS前台至单次官方评估；私有审计区分note与SMS两个条件。

**双方逐例核对**

已核对：note/SMS合取被verification_goal漏项；短信无Send，0.5分解强推断；kill默认Markor且未forward。

交叉核对：已核对。goal漏note是独立coverage缺陷；note1/SMS0仅强推断、原0.5保留。默认kill Markor且forward前拒，绝非已杀SMS。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例027，起始第409行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/2`。
- [原公开goal](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/composite/markor_sms.py；lines：39-68；symbol：MarkorCreateNoteAndSms.template/initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：426-440；symbol：MarkorCreateNote；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/file_validators.py；lines：199-226；symbol：CreateFile.is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：234-276；symbol：SimpleSMSSendSms.initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50；symbol：fuzzy_match 0.9；versionBinding：official_installed_frozen`

<a id="case-029"></a>
### 案例 029 — MarkorDeleteAllNotes

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete all my notes in Markor.

**约束与冻结初始化**

- Delete all my notes in Markor：删除全部笔记，不是删除.app/snippets配置目录。
- **已记录初始化**：step7实际有art_project_sketches_st16.md、backup_favorite_book_quotes.md、final_budget_home_renovation.md三份笔记及.app配置目录；非原AMK轮次的更多文件。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：initialize在Markor目录生成2–6个噪声笔记；is_successful重新取得该目录文件metadata列表，非空就是0。源码注释已给出长按一个+点选其余+批量删的正常UI做法，不是必须逐个删除。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-7 passed：当前三份目标笔记清楚可见。
- agent-tap_on-8 passed：进入.app。
- agent-ui_snapshot-11 passed：进入snippets后空目录。
- agent-ui_snapshot-14 passed：两次Back回笔记列表。
- agent-ui_snapshot-16 passed：已选第一份笔记。
- agent-ui_snapshot-18 passed：More options是Clipboard/Move/Copy等，无Select all。
- agent-tap_on-21 failed：尝试grocery_list_st16.txt，当前UI未出现该文件，target not found。
- agent-ui_snapshot-25 passed：三份笔记已全部Selected，Delete尚未执行。
- agent-tap_on-26 failed：Delete被预算拒绝。
- agent-assert_visible-28 passed：最终断言仍可见第一份笔记通过。

原dispatch额度 14/14，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 直到14个write耗尽才把实际三份文件选齐；Delete/确认均未设备派发，至少第一份明确还在。
- 删除事务未发生，末态仍有笔记，正对官方非空列表给0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - .app/snippets往返花4个write；More options/back花2个；未见文件grocery_list_st16.txt又耗一次失败admission。
  - audit seq51/52拒绝Delete两次，seq55拒绝kill；deadline未到。
- **强推断**：
  - 探索配置目录和无证据文件名使业务提交之前预算耗尽；不是确认框点错、更非不能批删。
- **无法确认及备选**：
  - grocery_list_st16.txt来源不明，原trace没有这个目标文件的有效观测；不能断言来自AMK旧记忆或模型幻觉机制。
  - 最终完整文件列表未私有转储，但assert_visible已足以证明至少一份未删。
- **责任层**：
  - FSQ action grounding / plan scope
  - FSQ launch overhead
  - harness fixed budget

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 / FSQ planner/knowledge owner**；`Markor file-browser multi-select; goal-preplan action grounding`：只把当前实际文件节点作为候选，排除.app配置目录；长按一份后点选其余实际文件、Delete并OK。对“all notes”不私自扩展成清理所有配置文件夹；未观察到的grocery_list不得作为动作目标。

**未来验证（全部未执行）**

- 离线golden trace断言每个文件动作目标均有先前UI证据，3份multiselect后紧接Delete/确认，不进.app。
- 设备新题：14上限内批量删除并观察空列表；官方单次oracle列表为空，配置目录保持可用。

**双方逐例核对**

已核对：.app探索仅低效；无观测支持grocery target为明确偏离，选齐后Delete未执行。

交叉核对：已核对。.app探索仅低效；无观察支持的grocery target才是明确偏离；选齐后Delete没执行。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例029，起始第462行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/3`。
- [原公开goal](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：375-408；symbol：MarkorDeleteAllNotes.initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：495-549；symbol：get_file_list_with_metadata regular files only；versionBinding：official_installed_frozen`

<a id="case-030"></a>
### 案例 030 — MarkorDeleteNewestNote

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete the newest note in Markor.

**约束与冻结初始化**

- 只删除最新笔记；其他笔记不得发生文件名或change_time变化。
- **已记录初始化**：现场实际仅两份：final_friendly_king.md（UI 15:34）与fine_jelly_final.md（15:17）；列表.app不是一份笔记。初始化记录referenceTime15:34，但随机时钟推进后初始UI14:29，不能把这个时间变化误判deadline。最终初始change_time私有列表未存入task-initialization。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：初始化2–6份笔记并在每份后随机推进系统时间，按change_time排序保存initial_file_list_sorted。评分要求最终恰少一份、余下顺序前缀的file_name/change_time均与初始化一致；即删除change_time最大那份而不是随便删一份。 注意helper把ls -ll -au的时间列命名为change_time（-u对应访问时间），不能在报告中擅自等同POSIX ctime；本轮无确认删除这个直接失败不依赖时间语义争议。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-7 passed：两份文件及修改时间可见。
- agent-ui_snapshot-9 passed：打开Sort菜单但未更改Date。
- agent-ui_snapshot-13 passed：已选final_friendly_king.md。
- agent-ui_snapshot-15 passed：详情显示精确位置/storage/emulated/0/Documents/markor及Last modified15:34。
- agent-tap_on-18 passed：Delete只打开确认框。
- agent-ui_snapshot-19 passed：Confirm Delete/CANCEL/OK真实待提交。
- agent-tap_on-20 failed：OK因10上限拒绝，下一次retry同拒。

原dispatch额度 10/10，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 选中的文件看上去是两份中最新，但正式评分按change_time而非UI的Last modified；本次无论候选对否都没按下确认、文件数量没减少。
- 删除确认未派发，不能满足恰少一份。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 首4个write用于启动绕路；Sort/Back与Info/OK又4个write，直到第10次Delete才显示确认框。
  - audit seq39/40拒绝OK，seq41拒绝kill；deadline未到。
- **强推断**：
  - 删除未提交是充分失败原因；不能把失分终结为选错最新文件，因为没有官方初始change_time列表来证明候选错。
- **无法确认及备选**：
  - 初始化metadata完整数组未保存；UI Last modified与官方helper的ls -au/change_time列不同，不能凭界面完全重建应删目标。
- **责任层**：
  - FSQ commit-aware planning
  - FSQ launch overhead
  - harness budget/diagnostic boundary

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 / FSQ planner owner**；`Markor newest-note flow; ordered destructive action plan`：用实际可见时间/必要排序识别最新，保留确认动作；无需确认前反复打开无改变的Sort和已知文件Info。其他文件不可编辑；完成后刷新列表确认只少目标。
- **P2 / harness diagnostics owner**；`task-initialization private audit for MarkorDeleteNewestNote`：将官方initialize已构造的initial_file_list_sorted及实际helper时间列语义以私有诊断序列保留（不额外调用oracle、不向agent暴露），便于区分候选识别错与确认没做；修复agent不得悄悄把现有官方时间口径改成另一个。

**未来验证（全部未执行）**

- 离线fixture：按官方helper生成的change_time字段（ls -au访问时间列），而非UI mtime/名称确定应删目标；未提交确认不能记为完成。
- 设备新题：同10上限，删除确认完成且只少change_time最大文件，余下file_name/change_time保持不变；只评一次。

**双方逐例核对**

已核对并补官方口径：change_time来自ls -ll -au时间列，不等UI Last modified/ctime；候选正确未知，确认未提交充分失败。

交叉核对：已核对、有补正。official change_time来自ls -ll -au时间列，不等UI Last modified或ctime；候选是否最新仍unknown。确认未提交已充分失败，不反推选错。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例030，起始第512行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/4`。
- [原公开goal](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：324-368；symbol：MarkorDeleteNewestNote.initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：495-549；symbol：get_file_list_with_metadata: field change_time parsed from ls -ll -au；versionBinding：official_installed_frozen`

<a id="case-032"></a>
### 案例 032 — MarkorEditNote

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Edit note_SiFbv.txt in Markor. Add to the top of the note Hello, World!

**约束与冻结初始化**

- 在note_SiFbv.txt顶部添加Hello, World!，保留原文；没有改名要求。
- 官方只验文件内容最终状态，不要求“插入-only”交互。
- **已记录初始化**：实际原文Don't forget to water the plants while I'm away.（step9），并有相似note_SiFbv_final.txt等噪声。未import/重建随机句子。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：读取精确文件路径、去CR/首尾空白后，与header+\n+initialize生成的original_content进行0.9阈值fuzzy match。编辑器assert_state存在不等于文件已落盘。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-9 passed：真实读取完整原文。
- agent-input_text-11 passed：Move Home后只写Hello, World!和换行，替换掉原文。
- agent-ui_snapshot-13 passed：原文消失，证实replacement。
- agent-ui_snapshot-15 passed：第一次undo只恢复到空，反映clear/set_text的多个undo状态。
- agent-ui_snapshot-17 passed：第二次undo恢复原文。
- agent-input_text-18 passed：再用完整header+原文重建编辑内容。
- agent-tap_on-20 failed：Save被预算拒绝。
- agent-assert_state-21 passed：element text完全匹配存在，仍只证明当前editor状态。

原dispatch额度 12/12，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 最终editor含正确header与原文，但Save没派发、重开没做，官方文件评分0。不能把编辑器assert passed抬成持久化成功，也不能把插入-only不满足说成官方失分原因。
- 显式Save未forward；当前buffer正确但持久状态未证且official为0，不能确定最终文件字节或auto-save是否生效。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - input_text源137-151明确clear/set_text；本轮UI连续展示原文→仅header→空→原文，非套用旧AMK根因。
  - 2次launch+swipe+launcher tap花4 write；原文覆盖后的2次undo与完整重写消耗余量；audit seq39 Save拒绝，seq42 kill拒绝，deadline未到。
- **强推断**：
  - 恢复后editor对、official0且唯一Save被拒，更支持持久化环节缺失；但没有最终文件读回，不能排除未记录的auto-save行为或其他评分内容差异。
- **无法确认及备选**：
  - Markor自动保存时机/最终文件字节未采集，不能严格声称磁盘仍是某一具体旧版本。
- **责任层**：
  - FSQ text semantic contract
  - FSQ persistence verification
  - harness budget

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 / FSQ skill/planner owner**；`resources/skills/android-harness.md; drivers/android/_uiautomator2.py::input_text description; goal pre-plan`：把input_text的click/clear/set_text整字段替换语义告知planner。header任务先读取可见原文，用现有replacement写入header+指定换行+已观察原文，再Save；不把Move Home+input_text误当插入，不添加官方没有的“必须只用插入操作”验收。长文读不全时先取得完整UI证据，不能拿frozen私有params补内容。
- **P1 / FSQ planner/verifier owner**；`Markor Save/read-back state distinction`：区分editor状态和持久化状态；在既定预算内正确合成一次替换→Save→重开核对，不靠两次undo试探，也不把assert_state当保存证明。

**未来验证（全部未执行）**

- 离线fake editor含clear与set_text两个undo事务，确保计划不把input_text作为insert、assert_state不声称落盘。
- 设备新题：12上限正确合成header+已观测原文并Save；私有单次评分读取文件，UI重开验证。

**双方逐例核对**

已核对：两Undo合理恢复，buffer正确但Save未forward；autosave/最终字节未知。

交叉核对：已核对。两Undo是合理恢复；最终buffer正确、Save未forward；autosave/最终字节unknown，不称磁盘必旧。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例032，起始第556行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/5`。
- [原公开goal](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：209-254；symbol：MarkorEditNote.initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50；symbol：fuzzy_match；versionBinding：official_installed_frozen`

<a id="case-033"></a>
### 案例 033 — MarkorMergeNotes

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Merge the contents of Markor notes tough_frog_2023_08_05.txt, proud_cat_edited.txt and 2023_08_21_friendly_koala.md (in the same order) into a new Markor note named mIObBbo4 and save it. Add a new line between the content of each note.

**约束与冻结初始化**

- 按tough_frog_2023_08_05.txt → proud_cat_edited.txt → 2023_08_21_friendly_koala.md顺序合并到新Markor note mIObBbo4并保存，内容间增加换行。
- 原goal新名没有扩展名；不能默认为mIObBbo4.md与官方精确路径等价。
- **已记录初始化**：创建三源文件，实际step9已读到第一份m4kMyOGWaENoPj6FqLjd；第二/三份冻结文本分别fxHXZsqrmnwYjXvte9pg、f42GOjFWb2aKHogAFQSY。后两项是私有评分上下文，不能作为agent修复路径的取值来源。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：CreateFile要求精确文件名mIObBbo4存在且正文fuzzy匹配三段以双换行分隔；后续额外检查去首尾空白后split(\n)恰5项、第1和3（从0计）项空白。track没有partial；只有正确内容+空行+精确路径才1。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-9 passed：第一源内容实际可见。
- agent-tap_on-13 passed：Select all后Copy调用passed，只是UI派发成功。
- agent-ui_snapshot-18 passed：创建对话框默认ext=.md。
- agent-input_text-19 passed：只填basename mIObBbo4，未清扩展名。
- agent-tap_on-23 failed：目的文件Paste找不到；UI只见Autofill，不代表有可粘贴内容。
- agent-ui_snapshot-30 passed：列表出现mIObBbo4.md，路径已与官方目标不同。
- agent-tap_on-37 passed：重试Copy第一源，但未随之完成目的文件粘贴。
- agent-ui_snapshot-42 passed：重开mIObBbo4.md后editor空。
- agent-assert_with_ai-43 failed：关键原截图确实空白；视觉断言failed。

原dispatch额度 26/78，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 实际保存的是空mIObBbo4.md而非精确mIObBbo4；第二/三源未打开、未合并；即使将来只修Paste，也会因扩展名和缺两源仍失败。
- 精确输出路径与内容两个独立充分失败：新名带默认.md，重开为空；不是仅缺最终Save或预算耗尽。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - Paste目标未出现（step23 target not found），第二次Copy后直接重开并最终断言，没有再次Paste或正文输入。
  - main pre_plan明确第二/三源与append steps全部skipped。
  - 26/78 write，0 denied，deadlineExceeded=false；runner正常返回inconclusive；events seq134主agent requests58<maxTurns100。不能把runner“execution window”措辞当wall timeout。
- **强推断**：
  - CreateFile在mIObBbo4不存在分支即可返回0；没有私有文件转储证实该分支，但实际列表带.md、未清扩展名与路径check源码一致。
  - Copy passed但Paste缺失说明未验证跨屏剪贴板可用；不能进一步把剪贴板清空归因于特定SDK/系统隔离。
- **无法确认及备选**：
  - 剪贴板实际内容/生命周期没有本轮存证，不能复用旧AMK clipboard根因。
  - 未耗尽动作或deadline却选择结束的具体agent停止策略需FSQ owner核对。
- **责任层**：
  - FSQ filename/creation semantics
  - FSQ cross-screen clipboard evidence discipline
  - FSQ premature completion policy

**修复方案（未实施）**

- **P0 / FSQ planner/knowledge owner**；`Markor create dialog + merge strategy`：创建时显式清空ext以保留无扩展名mIObBbo4（不修rubric）；逐一从UI读取三源并保存完整字符串，按源文件末尾换行与goal要求构造双换行间隔，用已有replacement一次写目的文本，Save并重开。若继续剪贴板路线，必须先验证可Paste/已Paste正文，不能以Copy dispatch通过当数据已传达。
- **P1 / FSQ runner/planner owner**；`agent plan completion and recovery policy`：失败的Paste不是全部merge不可做的结论；在剩余52 write和未到deadline时，按已观察文本/已提供UI功能继续独立业务步骤，或明确具体不可用能力。不得仅用模糊execution window提前终结。

**未来验证（全部未执行）**

- 离线创建对话框fixture默认.md：无扩展名goal必须得到精确路径；三源顺序和双换行构造能通过官方split5条件。
- 设备新题：只用实际UI取得三段，文件浏览器显示精确无扩展名且重开非空；官方单次oracle核对路径、fuzzy内容、5行空行位置。

**双方逐例核对**

已核对并补正式口径：目标空/缺两源/Copy后无写入；严格完整路径使默认.md为独立缺口，另5行两空行。

交叉核对：已核对、有补正。空目标、缺两源、重复Copy后没写均一致；official严格完整路径等值，默认.md为独立缺口，另要求两个空行形成5行结构，不再保留后缀normalize未知。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例033，起始第605行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/6`。
- [原公开goal](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：542-582；symbol：MarkorMergeNotes.__init__/initialize_task；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：603-638；symbol：MarkorMergeNotes.is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/file_validators.py；lines：199-226；symbol：CreateFile.is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/file_utils.py；lines：228-258；symbol：check_file_or_folder_exists exact full path equality；versionBinding：official_installed_frozen`

<a id="case-036"></a>
### 案例 036 — MarkorTranscribeVideo

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Transcribe the contents of video ZwUN_moment_70_.mp4 by watching it in VLC player (located in Download) and writing the sequence of strings shown on each frame to the text file ZwUN_moment_70__transcription.txt in Markor as a comma separated list. For example, if the first frame shows the text "edna" and the second frame shows the text "pineapple", then the text file should contain only the following text: "edna, pineapple".

**约束与冻结初始化**

- 从Download中的ZwUN_moment_70_.mp4观看每一帧字符串序列，在Markor创建ZwUN_moment_70__transcription.txt，只含按序逗号分隔列表。
- 原goal示例有comma-space，但官方fuzzy并非字节级空格/逗号限定；不把只一个空格差异说成本次根因。
- **已记录初始化**：正式frozen params指定三词与顺序，视频在Download；本调查只读取冻结参数，未import任务重建媒体。实际VLC列表找到目标，24秒时长在UI。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：初始化用messages=[Maria,Charlotte,Emilia]、每词8秒生成24秒视频，并加7份干扰视频；文件评分由CreateFile精确路径存在+正文fuzzy匹配Maria,Charlotte,Emilia。不评分VLC操作顺序本身，但本任务真实要求观看。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **storage**：
  - **constant**：MARKOR_DATA
  - **value**：/storage/emulated/0/Documents/Markor
  - **源码**：
    - **path**：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/device_constants.py
    - **lines**：30-34
    - **symbol**：MARKOR_DATA/DOWNLOAD_DATA
    - **versionBinding**：official_installed_frozen
  - **uiCasingNote**：某些实际UI显示/storage/emulated/0/Documents/markor（小写）；不把大小写差异擅自判为本轮根因：initialize目标文件真实可见，27还取得note子任务支持的0.5。未设备探查文件系统大小写规则。

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch VLC通过但还是Launcher，靠两次swipe找到VLC。
- agent-tap_on-11 passed：正确视频被打开，初次有tips覆盖。
- agent-tap_on-14 passed：tips关掉后原after-action截图在0:04显示Maria，非空视频。
- agent-ui_snapshot-15 passed：播放器7.9秒/24秒，Pause存在，id=player_overlay_play。
- agent-tap_on-16 failed：约4秒后同id找不到，耗时11.6秒等待；随后已回视频列表。
- agent-ui_snapshot-22 passed：再次播放10.9秒/24秒，Pause仍以相同id出现在新快照。
- agent-tap_on-23 failed：约4秒后又找不到；不是静态id明显拼错。
- agent-assert_with_ai-28 passed：原截图及视觉断言实际显示Charlotte；仅这一词被runner转成可读证据。
- agent-ui_snapshot-30 passed：又回到视频列表。
- agent-kill_app-31 passed：仅VLC teardown，未任何Markor创建/写入动作。

原dispatch额度 17/20，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 存量截图已亲看S14 Maria、S16 Emilia、S21 Charlotte及S28 Charlotte，三个词都有局部像素证据；但来自多次播放的散落capture不能冒充主runner已建立从起点至结尾的完整有序覆盖。runner只确认Charlotte并跳过所有Markor阶段，无创建动作。
- 没有创建转录文件；上游播放器未及时暂停/定位，短视频仍在流逝，控制条快照过期后重复查找失败，未建立完整有序转录。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 原始S14截图Maria、S16截图Emilia、S21及S28截图Charlotte，非“视频不可见/没有文字”；此前本报告未看S16而称无Emilia的句子已更正。
  - UI step15/22有正确Pause id，下一action却报target not found；控件显隐/播放完毕是动态现场状态，不能单标“点击失败”。
  - 17/20 writes，0 denied，deadlineExceeded=false；events seq102主agent requests42，正常返回；不支持预算耗尽或硬timeout。
- **强推断**：
  - 控制条自动隐藏与等待/取证耗时导致目标过期，是两轮“观察存在→操作找不到→返回列表”最小一致解释；是否藏条先于视频结束未直接逐帧采集。
  - 已有三词像素截图而main只显式读取S28的Charlotte，强支持动态媒体观察消费/时序整合策略不足；不直接断言所有截图从未提供给主planner。
- **无法确认及备选**：
  - SDK何时隐藏overlay、Space是否真正pause没有状态证据，不认定Space可靠。
  - 不能从私有messages直接生成答案来修复agent；也没有本轮媒体损坏、AMK probe或文件不存在证据。
- **责任层**：
  - FSQ transient video UI control
  - FSQ observation/vision availability
  - FSQ plan completion

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 / FSQ driver/skill and planner owners**；`VLC playback control strategy; observation/image consumption`：用当前可见播放器控件即时暂停，随后重新观测已暂停时间；必要先唤出控制条，不拿数秒前的快照重用等待。逐段seek到每个新词时取得静态截图并读回，记录时间顺序、覆盖首尾。短视频取证要先冻结状态再调用慢视觉assert。保留完整序列后才进入Markor创建/Save，不能用oracle messages补词。
- **P1 / FSQ observer/runner owner**；`Screenshot artifact to business observation path`：明确after-action图片是否真正提供给主agent；若只提供XML与路径，必须有无需猜文件路径的受控图片读取接口或视觉观察，确保画布文字如Maria可被业务规划消费。

**未来验证（全部未执行）**

- 离线复用本轮截图应可读Maria/Emilia/Charlotte三个局部词；仍不能把散落capture当连续全程覆盖或主runner已完成顺序记忆；动态控件fixture模拟观察后隐藏。
- 设备新媒体：24秒三词，不泄露生成params，先暂停确认时间再逐段观察；20上限内转录文件创建/Save并单次正式内容评分。

**双方逐例核对**

已核对，有capture口径保留：S16 Emilia/S21 Charlotte已看，散落三词非完整顺序；explicit kill VLC，05s/7.9s可为不同capture不混帧。

交叉核对：已核对、有capture口径保留。harness已亲看S16 Emilia、S21 Charlotte；三词散落不等完整时序main覆盖，S31明确kill VLC。S15截图约05s与invokeXML7.9s属不同capture可能，保留差异不拼为同帧或主失败。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/media-contacts-markor.md)，案例036，起始第664行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/7`。
- [原公开goal](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/markor.py；lines：884-921；symbol：MarkorTranscribeVideo.template/initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/file_validators.py；lines：199-226；symbol：CreateFile.is_successful；versionBinding：official_installed_frozen`

<a id="case-040"></a>
### 案例 040 — NotesTodoItemCount

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> How many to-dos do I have in the 'Ideas' folder in the Joplin app? Express your answer as just a single number.

**约束与冻结初始化**

- 只统计Joplin Ideas文件夹中is_todo项，不统计全部notes、其他文件夹或标题里含Ideas的笔记；答案只给一个数。
- 官方COUNT没有todo_completed过滤，故“已完成todo”也不应私自排除。
- **已记录初始化**：初始化记录params含folder=Ideas/title=Meeting Agenda/body参数，但任务的title_without_replacement/body_without_replacement实际由数据生成选择，不等于只数名叫Meeting Agenda的记录。真实Ideas UI显示Recipe Ideas、Financial Plan、Work Tasks三个checkbox条目，下面大量无checkbox普通note。冻结源码支持official期望3，未实例化重建数据。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：tasks.textproto relevant_state恰3个folder={folder},is_todo=True条目；初始化100份噪声通过排除条件AND（is_todo=True且folder=Ideas）避免额外合格todo。COUNT is_todo得到3；NUMBER_MATCH将完整agent答案字符串按逗号拆分后float转换，不抽取叙述里的数字。harness只取唯一主runner.tool_output.summary放入interaction_cache；不取verifier、pre_plan或evidence。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown

**原关键轨迹**

- agent-ui_snapshot-2 passed：launch通过却仍Launcher。
- agent-tap_on-8 passed：尚在All notes时点text Ideas。
- agent-ui_snapshot-9 passed：实际打开Health中的Workout Routine - Strength Training，不是Ideas文件夹。
- agent-tap_on-12 passed：Back后打开Sidebar。
- agent-tap_on-14 passed：这时才选择真正Ideas notebook。
- agent-ui_snapshot-15 passed：真实folder Ideas顶部三条todo和下方普通note；关键截图可见checkbox。
- agent-ui_snapshot-17 passed：向下滚只见大量普通notes，未形成完整列表断言。
- agent-ui_snapshot-19 passed：Search框打开，但含侧边栏/键盘。
- agent-input_text-20 failed：第11个write试图搜索被拒，搜索内容未实际派发。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 官方期望数值3；主runner step4 summary实际为“Could not verify the total number of to-dos in Ideas before the harness action budget was exhausted.”，不是数也没提交其他业务答案。主output结构有效（mainAnswer.status=valid）不代表NUMBER_MATCH通过；failure不是“误把3算成其他数”，而是未给数值+未建立完整覆盖。
- interaction_cache收到有效task_run_v1的叙述summary，float解析失败由IR evaluator捕获ValueError并返回0。早期误开其他笔记和启动绕路耗掉预算，正确folder已可见3个todo却未完成数量确认/数值提交。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - mainAnswer valid、businessStatus inconclusive，非exact_main_summary契约异常；不要混入其他四例main-summary缺失造成official无效。
  - 10/10write，seq39搜索input拒绝、seq40kill拒绝；deadline未到。
  - actual截图确见Ideas+三个checkbox；源码排除条件为AND而非OR，不是把所有Ideas普通笔记或所有folder todo都排掉。
  - S8 prepare XML含Ideas [39,740][614,797]与Workout Routine [119,740][1041,797]重叠bounds，原prepare PNG实际All notes而drawer未展开；节点存在与前景可交互并非同一事实。
- **强推断**：
  - 强支持未展开drawer的Ideas节点被exists命中后点击其bounds落到前景Workout note；当前driver按exact text，不是contains匹配。但无实际u2点击坐标回执，不能升级为已证selector选错。
  - official数3由冻结proto三条+排除筛选决定；UI顶部三个todo与之吻合，但agent只看顶部截图本身不能证明完整total。
- **无法确认及备选**：
  - 未有本轮完整Joplin数据库/所有屏尾私有dump；不假造完整列表读完。
  - 隐藏drawer与前景note坐标重叠已有证据，实际点击坐标/底层可交互判定未采集；不认定oracle数据错。
- **责任层**：
  - FSQ navigation/grounding
  - FSQ IR answer protocol adaptation
  - harness exact-summary transport correct as frozen

**修复方案（未实施）**

- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 / FSQ planner/IR adapter owner**；`Joplin notebook navigation + task_run_v1.summary answer convention`：先Sidebar并确认Ideas标题，再用公开Joplin UI的notebook+is_todo筛选或完整列表覆盖计数；不要把普通note/其他folder/完成状态条件私加进计数。结果仅数字写到主runner summary（推理/错误仍放其他结构字段）；不可从verifier/evidence自动回填数字或正则摘数，更不可把私有expected3注入。
- **P1 / harness protocol owner**；`fsq_worker.select_main_answer / manifest.answerProfile / agent-facing answer instructions`：未来把“IR业务答案必须放summary且遵守原goal单数字格式”显式告知native agent，同时保留原始summary严格传递；不要悄悄把解释型summary改写成oracle可过的答案。
- **P1 / FSQ driver/navigation Skill owner**；`drivers/android/_uiautomator2.py::tap_on/_selector/_wait_for_exists:109-116,356-389`：保留原始UI树，但显式提供未展开容器/离屏或遮挡的证据；exists不能作为可点击前景充分条件。此例先展开Sidebar再定位Ideas并核对页标题，避免点击隐藏drawer节点的bounds。不能粗暴删除全部drawer节点，也不能只改为text contains或忽略missing target。

**未来验证（全部未执行）**

- 离线：summary="3"可作为数值、summary叙述不能被数字提取修复；mainAnswer valid不等于business answer correct。fixture含Ideas普通note、其他folder todo、已完成todo，按folder AND is_todo计数；另覆盖drawer隐藏/展开且节点bounds与前景note重叠，禁止exists即当可交互。
- 设备新题：10上限导航到目标notebook，建立完整筛选/覆盖后只在summary报数，官方单次oracle；不复用本题3。

**双方逐例核对**

已核对：隐藏Ideas与前景bounds重叠支持误点击强推断，缺坐标回执；COUNT期望3可确认，actualDB覆盖未知，main解释句不数字。

交叉核对：已核对、有保留。S8隐藏Ideas与前景Workout bounds重叠、drawer未展开支持隐藏exists后点前景主强推断，缺点击坐标；冻结proto3条COUNT期望3仅事后判据，actualDB/全集仍未知。唯一main step4解释summary非数字，不能从其它payload提数。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例040，起始第51行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/8`。
- [原公开goal](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：3433-3480；symbol：NotesTodoItemCount task proto；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119；symbol：InformationRetrieval.initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/joplin_app_utils.py；lines：38-66；symbol：setup_task_state；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/joplin_app_utils.py；lines：276-336；symbol：_check_note_conditions AND exclusion；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：111-120,147-180,193-208；symbol：_cast_answers_to_type/check_agent_answer/get_expected_answer；versionBinding：official_installed_frozen`
- `path：src/fsq_androidworld_eval/fsq_worker.py；lines：27-57；symbol：select_main_answer；versionBinding：current_harness_source_read_not_new_hash_attested`
- `path：src/fsq_androidworld_eval/fsq_runner.py；lines：357-366；symbol：interaction_cache assignment and official oracle；versionBinding：current_harness_source_read_not_new_hash_attested`

<a id="case-041"></a>
### 案例 041 — OpenAppTaskEval

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Open the contacts app. Clear any pop-ups that may appear by granting all permissions that are required.

**约束与冻结初始化**

- Open contacts并清required权限/启动pop-ups；官方评估时Contacts仍应是当前active package。
- 业务目标是contacts，frozen apps列表只是camera/clock/contacts/settings/dialer可选全集，不能把首项camera当本实例目标。
- **已记录初始化**：frozen app_name=contacts，原worker request却appId=com.android.camera2；这是_primary_app_id选择全app_names第一项，与public goal不一致。step1因此launch Camera，后由agent显式launch Contacts纠正；2个launch均未把业务app显到前台，实际用Launcher Contacts icon。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：OpenAppTaskEval没有自定义initialize，基类恢复app_names所有快照；is_successful只比较当前activity解析后的package与com.google.android.contacts。没有查历史曾打开，也没有私自要求截图得分；popup清理是goal要求但评分代码不单独检查。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown

**原关键轨迹**

- agent-launch_app-1 passed：默认实际目标Camera，与goal contacts不同。
- agent-launch_app-3 passed：显式Contacts纠偏。
- agent-ui_snapshot-5 passed：仍应用抽屉。
- agent-tap_on-6 passed：点Contacts launcher才真正进入。
- agent-ui_snapshot-7 passed：Contacts主屏，有startup tooltip而无permission dialog。
- agent-tap_on-8 passed：关闭og_tooltip_scrim_view。
- agent-assert_with_ai-9 passed：原截图与视觉断言表明主屏可用无提示。
- agent-kill_app-10 passed：随后成功app_stop Contacts，先前前台终态被改变。

原dispatch额度 6/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 业务曾实现：无popup的Contacts主屏可用；但native强制teardown先kill Contacts、再return给harness，官方此时才看前台而拿0。主runner报success与official0不矛盾，判断时刻不同。
- 成功后的kill_app破坏active-app任务终态；不是没grant权限、没清tooltip、超预算或模型不会开Contacts。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step9真实截图无提示、可搜索/create；step10 kill passed。
  - 官方reward0、无异常，预算仅6/10且deadline未到；oracle顺序明确在完整native返回后。
  - request appId确是camera2，goal/frozen app_name确是contacts；首app选择错误为独立harness配置缺陷，但本次被业务纠正，非最终0唯一原因。
- **强推断**：
  - app_stop导致当前activity不是Contacts，是源码行为+step9→10+official0支持的最强直接因果；diagnostic未提供oracle当时具体activity，不能断言一定是某个Launcher包。
- **无法确认及备选**：
  - kill之后/oracle时刻的完整activity字符串未记录；故不编造Launcher组件名。
  - 正常launch返回但停Launcher的底层启动原因仍由FSQ核对。
- **责任层**：
  - harness primary app binding defect
  - FSQ mandatory lifecycle vs official terminal foreground contract

**修复方案（未实施）**

- **P0 / harness owner**；`fsq_runner.py::_primary_app_id and episode target construction`：对于公开参数选择app的任务，按本实例app_name映射构造native app target，而不是从任务app_names可选全集取第一个；新增同类复合/动态目标契约覆盖，不从oracle结果倒推包名。
- **P0 / FSQ lifecycle + harness integration owners**；`resources/skills/android-harness.md::lifecycle; fsq_runner.py::oracle/cleanup ordering; manifest protocol.lifecycle`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
- **P0 / FSQ driver/skill owner**；`drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P2 / harness diagnostics owner**；`EvaluatorDiagnostics foreground task evidence`：私有记录同一次official检查实际active activity，区分业务达成后被cleanup覆盖与根本没达成；不额外probe设备用于本次调查，也不向agent输oracle值。

**未来验证（全部未执行）**

- 离线纯参数：app_name=contacts→com.google.android.contacts而非camera，分别覆盖5种OpenApp变体；生命周期fixture验证oracle读取发生在清理之前的保留状态，而非拿中途截图冒充末态。
- 将来设备新题：Contacts无popup，完整native return保留前台；官方只评一次，再清理；对照audit记录实际package。

**双方逐例核对**

已核对：request误选Camera映射与实际explicit killContacts是独立问题；kill造成评估非Contacts主强推断，缺边界activity。

交叉核对：已核对。S10显式kill Contacts、invoke passed/audit19 attempted20 succeeded，非默认Camera；初始Camera由_primary_app_id:97–105取app_names首项造成的映射缺陷独立。业务达成后前台破坏主强推断，缺kill后activity；改生命周期需批准新合同，不移动旧取样边界。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例041，起始第73行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/9`。
- [原公开goal](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/task_eval.py；lines：116-157；symbol：TaskEval.initialize_task/_initialize_apps；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/system.py；lines：450-499；symbol：OpenAppTaskEval mapping/is_successful；versionBinding：official_installed_frozen`
- `path：src/fsq_androidworld_eval/fsq_runner.py；lines：97-105；symbol：_primary_app_id chooses first app_names；versionBinding：current_harness_source_read_not_new_hash_attested`
- `path：src/fsq_androidworld_eval/fsq_runner.py；lines：349-373；symbol：official evaluation after complete native return；versionBinding：current_harness_source_read_not_new_hash_attested`
- `path：/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/resources/skills/android-harness.md；lines：7-10；symbol：lifecycle forced kill after verification；versionBinding：FSQ_source_peer_hash_matched`
- `path：/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py；lines：102-107；symbol：kill_app app_stop；versionBinding：FSQ_source_peer_hash_matched`

<a id="case-044"></a>
### 案例 044 — OsmAndTrack

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Save a track with waypoints Schönberg, Liechtenstein, Triesen, Liechtenstein, Bendern, Liechtenstein in the OsmAnd maps app in the same order as listed.

**约束与冻结初始化**

- 在OsmAnd保存一条track，依次经过Schönberg, Liechtenstein → Triesen, Liechtenstein → Bendern, Liechtenstein。
- frozen track_name不是goal文字要求，也不在oracle检查名称条件中；不能私自要求特定GPX文件名或route模式/导航成功。
- **已记录初始化**：正式前已有map-baseline补充操作及qualified readiness：Liechtenstein_europe.obf sha256=57a1955c6f517a114999fa50480ecc1402ed9b524db602540ac1c08f57ff140e，7241271bytes；代码在每个osmand任务initialize前恢复并校验这张共享map。该张地图可被其他官方文件任务清理，所以不能当永久身份；本episode未单独保存restore返回值，但初始化正常完成、后续真实本地地名搜索/详细地形截图都反驳“地图缺失”为既成事实。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **sourcePolicy**：只读冻结参数和installed源码；未import/实例化任务/重建随机数据。

**官方判据**

- **判据**：initialize清除tracks并从预装地点字典确定三个目标经纬度；is_successful拉取/data/media/0/Android/data/net.osmand/files/tracks的直接子文件逐个XML解析，只提取GPX namespace下trk/trkseg/trkpt（不是rtept或wpt），按原顺序用delta_deg=0.001匹配三个目标，允许中间其他点。不校验track_name、UI最终必须停地图或完整驾车路径规划。
- **diagnostic**：
  - **outcome**：returned
  - **officialReward**：0.0
  - **exception**：null
  - **componentResults**：
    - **status**：not_provided
    - **源码**：scalar_return_interface
  - **logRecords**：
  - **boundary**：after_agent_exit_and_submission_before_task_teardown
- **targetCoordinatesPrivateOnly**：
  - **name**：Schönberg, Liechtenstein
  - **lat**：47.1303814
  - **lon**：9.5930117
  - **name**：Triesen, Liechtenstein
  - **lat**：47.106997
  - **lon**：9.5274854
  - **name**：Bendern, Liechtenstein
  - **lat**：47.2122151
  - **lon**：9.5062101
- **coordinateBoundary**：每一经纬度分量绝对差均严格<0.001；不能将这些私有oracle坐标作为业务agent修复答案。

**原关键轨迹**

- agent-ui_snapshot-7 passed：初始地图200mi，Position not yet known，不是规划失败错误。
- agent-ui_snapshot-13 passed：新route编辑器points:0。
- agent-ui_snapshot-17 passed：Schönberg在当前搜索中心5mi无结果。
- agent-ui_snapshot-19 passed：增到10mi仍无结果。
- agent-ui_snapshot-21 passed：输入完整地点只找到3296mi外Country Liechtenstein，说明当前搜索中心离目标很远。
- agent-ui_snapshot-32 passed：选择国家后重搜，真实出现Schönberg山峰1.92mi和Haus Schönberg；本地map已可用。
- agent-ui_snapshot-34 passed：选中正确Schönberg山峰详情，但route仍points:0，地点选择不等于加入route。
- agent-ui_snapshot-40 passed：返回route编辑器，缩放0.25mi，仍points:0。
- agent-tap_on-41 passed：点route Add后才加第1点。
- agent-ui_snapshot-42 passed：终态points:1、0ft；未有第2/3点或Done/Save。
- agent-assert_with_ai-43 failed：关键原截图含Schönberg地形及一草稿点，明确不是saved三点track。
- agent-kill_app-44 passed：kill通过，但此前保存流程尚未开始。

原dispatch额度 23/120，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 实际只有Schönberg附近的一点草稿，没有访问/添加Triesen/Bendern，没有Done/Save；official0与未生成合格GPX轨迹吻合。本轮无GPX目录/字节转储，所以只能确定“没有满足oracle的track”，不能声称具体GPX为空、被存成rtept、错子目录或命名错误。
- 地点搜索恢复后没有执行剩余两站与保存，终态仍一草稿点；不足以满足3个有序trkpt文件条件。没有任何路线计算报错证据，不能归为规划引擎失败。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 首轮无结果来自5/10mi局部搜索，国家选择后同词命中真实Schönberg；最终截图地图细节可见。
  - 保存相关steps在main pre_plan全部skipped；23/120 writes、0 denied、deadlineExceeded=false；events seq138主agent requests60<maxTurns100，正常inconclusive返回。
  - diagnostic标量0、exception=null，无GPX解析/读取异常；不能把0改成评分无效。
- **强推断**：
  - 选country重新定心后本地搜索恢复，说明前期搜索中心/半径而非缺地图是主要搜索障碍。
  - 到第一点后主动结束/策略停机是不完整执行直接近因；main“execution window”措辞没有deadline硬边界支持，需FSQ核对停止策略。
- **无法确认及备选**：
  - 本次缺私有GPX目录列表及内容、首点精确坐标，无法分辨first point是否在0.001度容差内。
  - 不能证明不存在任何文件；只能依据official0认定没有被该oracle读到并满足条件的track。
  - episode的restore_shared_assets返回值未存档，只有既存资格链和代码调用及UI证据；不升级成逐episode新SHA实测。
- **责任层**：
  - FSQ geospatial search-center strategy
  - FSQ route point/commit state modeling
  - FSQ premature completion
  - harness evidence granularity (not confirmed map defect)

**修复方案（未实施）**

- **P0 / FSQ planner/knowledge owner**；`OsmAnd Plan a route search/add/save UI flow`：先以国家/城市公开UI定位搜索中心，识别正确山峰而不是酒店；选地点后确认route point count递增，再找Triesen、Bendern并分别Add，最终Done/Save到Tracks。区别place selection、map center、route point、saved GPX四层状态；不向agent注入私有oracle经纬度、不要求驾车路径规划、不靠手写GPX绕过UI。
- **P1 / FSQ runner/planner owner**；`Completion policy with remaining budget`：当前仅1点且两段/保存全skip不能收为成功；预算/时间未满时按已知UI能力继续完成。若真有不可达能力，报告具体阻断，不用execution window笼统替代实际限额。
- **P2 / harness diagnostics owner**；`OsmAnd private evaluator GPX/shared-assets audit`：保留每episode共享地图restore返回，以及同一次oracle遍历的文件相对路径、GPX节点类型/点数/匹配进度（私有且不泄露oracle坐标给业务）；用于将来区分草稿未保存、目录/格式错、坐标顺序错。不改现有rubric，也不重跑本题。

**未来验证（全部未执行）**

- 离线官方GPX fixture：有序trkpt和中间点通过，反序/仅rtept/仅wpt/少点不通过；track_name任意不影响；默认只遍历tracks直接子文件的既有规则保持不变。
- 设备新题：保持120既定write上限、无答案坐标，三次UI Add使points从0到3，Save确认；单次oracle后私有检查实际GPX路径/节点/顺序。另检查共享map每episode恢复证据，不能以“搜索初始无结果”直接宣称缺图。

**双方逐例核对**

已核对：一点草稿、未后两站/未Save是确定差距；不查track_name/驾车规划，不归缺图/猜GPX格式路径。

交叉核对：已核对。一点草稿、未后两站/未Save是直接差距；official读net.osmand/files/tracks直接子文件trk/trkseg/trkpt，序列经纬度每分量<0.001，不查track_name/不要求驾车规划。已有地图资格+地形地名，不归缺图；无最终GPX字节，不猜错格式/路径/空文件。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例044，起始第91行。
- [harness独立完整源码/step/截图记录](harness-notes/markor.json)，JSON pointer `/cases/10`。
- [原公开goal](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/osmand.py；lines：32-56；symbol：_DEVICE_FILES/_PRELOADED_MAP_LOCATIONS；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/osmand.py；lines：310-387；symbol：_clear_tracks/_track_matches/_track_points；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/osmand.py；lines：405-443；symbol：OsmAndTrack.goal/initialize_task/is_successful；versionBinding：official_installed_frozen`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：550-552,581-593；symbol：OsmAndApp.DEVICE_MAPS_PATH/MAP_NAMES/setup；versionBinding：official_installed_frozen`
- `path：src/fsq_androidworld_eval/environment.py；lines：256-285；symbol：restore_shared_assets；versionBinding：current_harness_source_read_not_new_hash_attested`
- `path：src/fsq_androidworld_eval/fsq_runner.py；lines：269-270；symbol：per-episode restore_shared_assets；versionBinding：current_harness_source_read_not_new_hash_attested`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/osmand.py；lines：63-77；symbol：_coords_match: abs(delta latitude/longitude) strictly <0.001；versionBinding：official_installed_frozen`

<a id="case-046"></a>
### 案例 046 — RecipeAddMultipleRecipesFromImage

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the recipes from recipes.jpg in Simple Gallery Pro to the Broccoli recipe app.

**约束与冻结初始化**

- **publicGoal**：Add the recipes from recipes.jpg in Simple Gallery Pro to the Broccoli recipe app.
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-046-20261110T183830Z-e687b6/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：10
- **fixture**：Broccoli预先10条noise；Gallery recipes.jpg只含3条target，文字按60列wrap。Chickpea Vegetable Soup还存在noise同标题但1 serving/see directions，与目标2 servings/as desired不同。

**官方判据**

- **判据**：SQLiteApp清空Broccoli并插入noise；AddMultipleRows记录before。添加评分逐一要求所有target行存在，比较title/description/servings/preparationTime/source/ingredients/directions/favorite，除favorite外均大小写不敏感SequenceMatcher ratio>=0.9；after长度必须为before+target数，所有原before行不可改变或删除；全部条件合取，返回0.0或1.0，无按菜谱部分分。空source和favorite=0同样是正式条件。
- **不要求**：不比较imageName/图片或categories，不要求另填图片；不能把图片附件缺失当根因。

**原关键轨迹**

-  ：源图三菜已读出，但仅Eggplant Parmesan一套字段输入并保存/重开；没有Baked Cod或Chickpea目标的录入。

原dispatch额度 27/60，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 期望新增3个完整target（Broccoli共13行且noise不变）；实际动作只新增Eggplant Parmesan一条，Baked Cod with Lemon and Dill和目标Chickpea Vegetable Soup均无录入动作。Eggplant输入8 servings/10 mins/varies/完整描述与directions，save后重开截图匹配；不能从此反推全套任务成功。正式诊断validate_rows_addition_integrity:168返回Expected row missing。
- 全量转录未完成；不是图库读不到、图片未附着，也不是已证明字段被持久化截断。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step10已识别三条源菜谱；step20-38只录入第一条，step44 kill_app后runner以inconclusive正常结束；写预算27/60且deadlineExceeded=false。
  - step16和41把页面标题New Recipe当列表入口，失败；step18实际fab_recipes成功。驱动target仅text选择：/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:356-369。
  - 官方不做whitespace normalization：fuzzy_match只忽略大小写，SequenceMatcher阈值0.9。step35把Bake until bubbly.与Garnish...之间空格换成一个LF；这不是精确字符串相等，但单个字符替换相对于这段完整长文本不足解释跌至阈值以下，不应当作0分根因。
- **强推断**：
  - 执行计划没有以三条源记录的完成ledger约束结束，局部save/assert被接受为提前退出点；重复每字段Back+snapshot和非实际控件目标消耗路径。
- **unconfirmedOrMissing**：
  - 原after DB未保存，无法声明第一条已过逐字段oracle或指出诊断第一个缺失target。runner自称run time limit，但外层3720秒预算没有耗尽，327067ms提前结束的时间提示来源需FSQ核对。
- **alternatives**：
  - 若有额外未见持久化变化仍需原DB才可确认；本轮已读方向录入与源只见一个句间LF替换，不能据此指称格式错误。正式诊断省略具体Recipe，确认的充分业务差距始终是仅完成1/3。
- **责任层**：
  - FSQ跨应用数据转录执行/完成条件
  - Android locator语义说明（辅助）
  - 正式oracle正常拒绝不完整集合

**修复方案（未实施）**

- **P1 / FSQ执行策略/工具契约 owner**；`FSQ main runner：源记录ledger与TaskRunOutput收尾门`：从公开图像提取的每条title+字段建立待办/已保存/已重开核对状态；未完记录仍有可用预算时继续UI流程，不把第一条assert当全集完成。此ledger不接触frozen params或oracle。 保存后按title+servings+time+ingredients复合identity读回，尤其Chickpea有原noise同标题，不能误读旧条；所有三条分别核对完成。
- **P1 / FSQ执行策略/工具契约 owner**；`UiAutomator2AndroidDriver._selector / Android工具说明`：明确target只按text精确匹配；入口使用观测到的fab_recipes resourceId，新增每菜使用同一已观察业务路径，而不是猜New Recipe文字入口。

**未来验证（全部未执行）**

- 离线用本episode行动证据断言保存对象数=1，完成ledger仍有两项pending，不得自动宣称3/3。
- 经授权的新设备运行：公开图像三条全部录入且关闭重开后六可见字段保持；正式oracle检查after=before+3且noise完全不变。

**双方逐例核对**

已核对：仅1/3充分0；微小空格换行不足单独解释0，无whitespace normalize但fuzzy>=.9；未耗尽原写额度。

**交叉核对：harness owner 批B已逐例确认主要失败链，父调查者同意；字节终态与首个缺失行仍未决。** owner 经父调查者传回：冻结 evaluator `recipe.py:354-384` 逐字段比较 title/description/servings/preparationTime/source/ingredients/directions/favorite，free-form 使用 fuzzy≥0.9；`fuzzy_match_lib:20-50` 忽略大小写、使用 SequenceMatcher，不做 whitespace normalize。本调查未自行读取该额外源码，以上为明确归属的协作核对证据。双方一致：只保存1/3、余2未录已构成充分完成差距，单个空格换行不能作为0分主解释。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例046，起始第180行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/0`。
- [原公开goal](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-046-20261110T183830Z-e687b6/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-046-20261110T183830Z-e687b6/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:339-384`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:118-192,257-284,304-310`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py:20-50`

<a id="case-047"></a>
### 案例 047 — RecipeAddMultipleRecipesFromMarkor

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the recipes from recipes.txt in Markor to the Broccoli recipe app.

**约束与冻结初始化**

- **publicGoal**：Add the recipes from recipes.txt in Markor to the Broccoli recipe app.
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-047-20261110T184424Z-a393d7/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：10
- **fixture**：Markor recipes.txt仅3 target，Broccoli已有10 noise；noise_row_objects[2]是Thai Peanut同名同描述/方向，但3-4 servings、2 hrs、optional ingredients。

**官方判据**

- **判据**：SQLiteApp清空Broccoli并插入noise；AddMultipleRows记录before。添加评分逐一要求所有target行存在，比较title/description/servings/preparationTime/source/ingredients/directions/favorite，除favorite外均大小写不敏感SequenceMatcher ratio>=0.9；after长度必须为before+target数，所有原before行不可改变或删除；全部条件合取，返回0.0或1.0，无按菜谱部分分。空source和favorite=0同样是正式条件。
- **不要求**：不比较imageName/图片或categories，不要求另填图片；不能把图片附件缺失当根因。

**原关键轨迹**

-  ：第一条保存后立即详情正确；按title重开后命中原noise同名项，非证实保存回滚。

原dispatch额度 27/60，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 目标需Thai Peanut Noodle Salad(8 servings/3 hrs/as desired)、Garlic Butter Shrimp(3-4 servings/30 mins/to preference)、BBQ Chicken Quesadillas(8 servings/20 mins/per individual taste)全部新增。step21-37只输入并保存Thai；step38显示8 servings/3 hrs/as desired且step39完整directions定向断言通过。step43用title重开，截图变成3-4 servings/2 hrs/optional ingredients，恰为初始化noise[2]。Garlic和BBQ从未输入，正式0分充分成立。
- 新增集合缺2条；另有重开对象身份歧义造成假“保存字段变了”的验证差距。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 源文本三条完整读取（step12）；仅一次save(step37)；step38正确新条详情与step43错误同名详情的全部可见差异和noise[2]一致。
  - step44 title+directions吻合但ingredients失败；并非所有字段相同的一个对象被证实发生变更。
  - 27/60写预算，deadlineExceeded=false，323270ms结束。
- **强推断**：
  - 以title作为唯一重开身份，把不同recipe当同一对象核对；新条8/3/as desired没有被后续动作修改，更强解释是命中已存在同名noise。
  - 因验证歧义及局部完成即停止，漏掉余下两菜。
- **unconfirmedOrMissing**：
  - 无recipeId/after DB留存，不能100%识别step43对应数据库ID；也不能证明所有新条字段通过oracle。自称time limit不是业务deadline证据。
- **alternatives**：
  - 实际存储写错是弱备选：需同时解释新条save后正确、重开全部元数据与原noise精确吻合，现有证据更支持错对象而非持久化损坏。
- **责任层**：
  - FSQ实体身份/集合完成与字段验证
  - 正式oracle正常检查全集
  - 不归因AMK持久化或App数据回滚

**修复方案（未实施）**

- **P1 / FSQ执行策略/工具契约 owner**；`FSQ recipe重开选择/完成ledger`：新保存记录用title+description+servings+time+ingredients形成公开UI复合指纹；同标题候选分别读取，定位正确新条后核对，不覆盖/删除原noise。保持3项独立完成状态。
- **P1 / FSQ执行策略/工具契约 owner**；`FSQ runner收尾决策`：检查一个字段失败时先辨认选中对象，不直接认定存储损坏或提前收尾；在未耗尽约束内完成Garlic与BBQ。

**未来验证（全部未执行）**

- 离线回放step38与step43，对照冻结noise[2]，断言这是候选身份冲突，不能输出“saved ingredient was corrupted”确定结论。
- 新设备fixture含同名不同字段noise；新增后精确重开目标，noise保持原字段，3条完整新增。

**双方逐例核对**

已核对：新旧字段与noise吻合支持选旧同名，不等保存损坏；另两未录充分0，after DB/recipeId未知。

**交叉核对：harness owner 批B已逐例确认主要失败链，父调查者同意；新旧持久ID仍未决。** owner经父调查者核对原S38新条为8/3/as desired，S43重开为3-4/2/optional，与 `noise_row_objects[2]` 精确一致；支持误选旧同名而非保存损坏，另两道未新增已构成充分完成差距。此为协作核对，不冒充本调查读取了最终数据库。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例047，起始第216行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/1`。
- [原公开goal](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-047-20261110T184424Z-a393d7/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-047-20261110T184424Z-a393d7/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:339-384`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:118-192,257-284,304-310`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py:20-50`

<a id="case-048"></a>
### 案例 048 — RecipeAddMultipleRecipesFromMarkor2

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the recipes from recipes.txt in Markor that take 10 mins to prepare into the Broccoli recipe app.

**约束与冻结初始化**

- **publicGoal**：Add the recipes from recipes.txt in Markor that take 10 mins to prepare into the Broccoli recipe app.
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：40
- **fixture**：40条noise已在Broccoli；recipes.txt将3 target+40 noise打乱写为CSV pipe分隔，目标prep_time=10 mins，noise的prep_time均非10 mins。不是只显示3条的小文件。

**官方判据**

- **判据**：SQLiteApp清空Broccoli并插入noise；AddMultipleRows记录before。添加评分逐一要求所有target行存在，比较title/description/servings/preparationTime/source/ingredients/directions/favorite，除favorite外均大小写不敏感SequenceMatcher ratio>=0.9；after长度必须为before+target数，所有原before行不可改变或删除；全部条件合取，返回0.0或1.0，无按菜谱部分分。空source和favorite=0同样是正式条件。
- **不要求**：不比较imageName/图片或categories，不要求另填图片；不能把图片附件缺失当根因。

**原关键轨迹**

-  ：只读Markor前部，首屏已有Beef Stir Fry 10 mins；未进入Broccoli、没有任何input/save。

原dispatch额度 9/60，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 需筛选43源行中3条10 mins：Raspberry Almond Smoothie(2 servings/n/a)、Beef Stir Fry(2 servings/as per recipe)、Pan-Seared Salmon with Quinoa(8 servings/n/a)，保留各自完整描述/方向并新增，最终Broccoli43行。实际step10读出Beef目标；step12/14/16在未到底的局部无目标页面返回failed，但optional=true；step17最后swipe后主体陷入artifact读取，未新增任何行，正式missing row、0.0。
- 业务缺所有3条新增；独立输出契约失败：native runner step1错误Agent exceeded the configured turn limit，主summary不存在；后续verifier inconclusive不能充当主summary。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - events 63-218反复read_artifact_slice相同工具产物片段；全程81次slice，仅12组唯一参数，其中重复最多一组19次；219明确max-turn错误。
  - 读片段offset1000返回嵌套/转义工具JSON，包含旧assertion输出；没有推进设备或源文件到底。
  - 写预算仅9/60，不是Android动作预算/业务deadline耗尽；Source读取用assert_with_ai，局部无10 mins导致断言failed并不代表文件不存在目标。
- **强推断**：
  - 工具结果获取/停止条件在同一片段上无进展，吃掉runner回合，阻断剩余源收集与目标录入；业务失败和summary失败有共同的artifact无进展循环。
- **unconfirmedOrMissing**：
  - 不能仅由trace证明循环由backend历史转换、tool filter、模型选择哪一处触发，FSQ owner需逐层对照；无after DB不能给逐字段差异。
- **alternatives**：
  - source很长或观察裁剪只是触发条件，不能单独解释同一artifact相同offset反复读取几十次；也不能把max_turns改大当永久修复。
- **责任层**：
  - FSQ artifact工具输出/runner无进展与structured收尾
  - FSQ源采集策略（断言与数据提取混用）
  - 正式oracle正常拒绝缺新增

**修复方案（未实施）**

- **P0 / FSQ工具协议 owner**；`HarnessToolAdapter._format_runner_result/_result_summary；read_artifact_slice输出协议；AgentTools历史过滤`：保持关键result.status/output.explanation为一次可读结构，避免为了读取源文本只能在双重转义工具JSON固定offset上反复找；相同artifact+offset+length返回稳定结构并把已读片段作为可用证据。具体循环注入点待FSQ owner确认，不能提前指定某层bug。
- **P1 / FSQ执行策略/工具契约 owner**；`agent_engine._runner max_turns循环 / 主runner完成状态`：不以加turn limit解决；追踪同一源片段无新证据的重复访问，在正常回合内重新推进源文件/使用Markor可见搜索，再继续UI录入并输出诚实结构化总结。异常路径保留真实runner error，verifier不得冒充主summary。
- **P1 / FSQ执行策略/工具契约 owner**；`Markor源收集执行策略`：把局部无匹配当过滤结果而非源契约失败；使用公开可见搜索10 mins并记录候选完整行/上下文与去重，直到覆盖源到底，不读取oracle。

**未来验证（全部未执行）**

- 用原events 63-218离线喂同一artifact响应，断言没有相同片段无进展循环；219错误必须原样传递，主summary缺失与verifier状态分开。
- 新设备含43行CSV、3个分散10 mins目标；公开UI源筛选覆盖、完整新增3项；写预算60与业务预算不变。

**双方逐例核对**

已核对：首artifact已有完整Beef Stir Fry10mins，却无Broccoli录入，81slice+100turn；不是全看不清。

**交叉核对：已核对（逐例回执及harness RecipeMedia独立调查）。000011已完整记录Beef Stir Fry/10mins、81次slice、未录入Broccoli、9/60未耗尽及max_turns双方一致；不能说全部看不清。原failed/0保留。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例048，起始第120行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/2`。
- [原公开goal](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:339-384`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:118-192,257-284,304-310`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py:20-50`

<a id="case-049"></a>
### 案例 049 — RecipeAddSingleRecipe

**原身份：passed / officialReward=1.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the following recipes into the Broccoli app:
> Recipe: Chicken Caesar Salad Wrap
>  description: An ideal recipe for experimenting with different flavors and ingredients.
>  servings: 3-4 servings
>  preparationTime: 2 hrs
>  ingredients: as desired
>  directions: Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand.
> 

**约束与冻结初始化**

- **publicGoal**：Add the following recipes into the Broccoli app: / Recipe: Chicken Caesar Salad Wrap /  description: An ideal recipe for experimenting with different flavors and ingredients. /  servings: 3-4 servings /  preparationTime: 2 hrs /  ingredients: as desired /  directions: Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand. / 
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：10
- **fixture**：Broccoli10 noise；公开goal直接给唯一target六个字段，需新增Chicken Caesar Salad Wrap而不是读Markor。

**官方判据**

- **判据**：SQLiteApp清空Broccoli并插入noise；AddMultipleRows记录before。添加评分逐一要求所有target行存在，比较title/description/servings/preparationTime/source/ingredients/directions/favorite，除favorite外均大小写不敏感SequenceMatcher ratio>=0.9；after长度必须为before+target数，所有原before行不可改变或删除；全部条件合取，返回0.0或1.0，无按菜谱部分分。空source和favorite=0同样是正式条件。
- **不要求**：不比较imageName/图片或categories，不要求另填图片；不能把图片附件缺失当根因。

**原关键轨迹**

-  ：有效save与全部字段定向核对成功，之后无修改；主runner在冗余artifact读取后max-turn，业务评分仍1。

原dispatch额度 18/24，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 18次admitted写中一次time字段未找到(step15)在Back后step18成功补录；step25保存，step26截图title/描述/3-4 servings/2 hrs/as desired/完整directions均匹配公开goal。step27无element的text equals输出空串而failed；step28按direction_text+完整text定位通过，29-33其余字段通过。official1.0/passed原样保留。唯一未满足项为主runner structured summary契约，非菜谱任务未完成。
- 本例无官方业务失败；passed=1.0但exact_main_summary failed，因为nativeResult.steps[0]为Agent exceeded the configured turn limit。后续verifier success不修复主runner缺summary。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 成功save与全部目标字段核对后无App修改，oracle正常返回1.0且无warning。
  - step27调用assert_state(text.equals)无element，_selector退回self.device()，_assert_text_state取根selector.get_text()返回空；不是方向文字没保存。源码/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:205-220,356-369,487-495。
  - native events 91-218大部分连续读同一assertion产物；全程66次slice、11组参数，同一3组各12次；219触发max_turns。
- **强推断**：
  - 业务完成后陷入工具证据重复读取而未及时structured收尾，造成输出协议错误；与48同属无进展artifact循环，但业务后果不同。
- **unconfirmedOrMissing**：
  - 哪个FSQ输出转换/历史机制促发重复请求需FSQ owner确认；无原DB快照不自行重评分，但本轮official1.0已是正式持久化验收证据。
- **alternatives**：
  - 初始time定位失败和全局text断言空值均已恢复，不能当最终business根因；不能把passed改failed来与native error对齐。
- **责任层**：
  - FSQ主runner收尾/工具协议
  - Android assert_state语义说明
  - 官方业务评分有效且通过

**修复方案（未实施）**

- **P0 / FSQ工具与runtime owner**；`read_artifact_slice / HarnessToolAdapter._format_runner_result/_result_summary / runner收尾`：业务字段断言已全部通过后使用已收集证据生成TaskRunOutput，不重复读同样offset的小片段；离线定位工具历史转换根因，不私加回合或同题重试。
- **P1 / FSQ执行策略/工具契约 owner**；`UiAutomator2AndroidDriver.assert_state / _selector / 工具参数说明`：明确text断言针对所选元素，不是全屏拼接文本；方向用element(resourceId=direction_text,text=完整源文)或定向text属性断言；拒绝/清楚解释无element的全局text用法，不做空串特殊通过。

**未来验证（全部未执行）**

- 原49离线证据断言business reward=1、classification=passed、mainAnswer=failed三者可共存；verifier success不得冒充runner summary。
- 完成已知六字段后及时结构化返回；全局text根空值与定向元素存在分开验收；budget24不变。

**双方逐例核对**

已核对：保存/字段验证且passed1；66slice+100turn主summary异常，不能用verifier补主输出。

**交叉核对：已核对（逐例回执及harness独立字段核对）。保存字段、66次slice、18/24未耗尽和max_turns无main双方一致；原passed/1保留，exact_main_summary只标主输出契约异常，不推导reward无效或重标invalid_agent。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例049，起始第142行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/3`。
- [原公开goal](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:339-384`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:118-192,257-284,304-310`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py:20-50`

<a id="case-050"></a>
### 案例 050 — RecipeDeleteDuplicateRecipes

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains

**约束与冻结初始化**

- **publicGoal**：Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-050-20261110T190605Z-9e00e8/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：5
- **fixture**：5 noise+2条Chicken Alfredo Pasta，完全重复字段：6 servings/45 mins/see directions/同description及directions。共7行，期望只删任意一个target ID，剩6行。

**官方判据**

- **判据**：初始化插入noise及两条仅recipeId不同的完全重复target；RecipeDeleteDuplicateRecipes.validate_deletion_integrity只接受删除target两ID中的任意一个，并保证另一个与全部原noise行仍存在且未修改，不能新增行。不是按title去重，删同名不同字段noise会失败；返回0.0或1.0。

**原关键轨迹**

-  ：7条fixture双份target已全字段比对；菜单用target而非content-desc导致最后admitted写失败，后续两次预算拒绝，无delete。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 实际step12/17打开两条；step14/19截图读出title、6 servings、45 mins、see directions、完整描述与方向一致，已具备删除候选证据。第10个admitted写step20 target=More options失败，虽然UI树content-desc=More options仍可见；step22显式accessibilityId重试在调用driver前被budget拒绝，step23 kill同样拒绝。未出现Delete菜单/确认/删除动作，official0。
- 本应删掉一份Chicken Alfredo Pasta，但没有任何删除发生；预算用尽是直接阻断，不是最深根因。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 写#1 launch无app、#2 launch带app仍停launcher，#3 swipe/#4点Broccoli才入app；#5/#6为库上下滚；#7/9打开两份，#8返回；#10用target=More options。
  - More options是content-desc非text；_selector的target分支强制device(text=...)，因此稳定找不到而不是控件不存在。源码/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:356-369。
  - 动作预算按admitted写dispatch包含launch、swipe、Back、失败尝试与kill；step22/23属于denied不执行。
- **强推断**：
  - 短预算未给关键delete/confirm预留步骤，启动前台后置条件缺失又消耗恢复动作；已知菜单属性却用错误target语义，使最后一个写机会浪费。
- **unconfirmedOrMissing**：
  - 起始app_start为何不把App前台化需FSQ/driver owner核对已有机制，当前无设备probe；不能断言只改一个菜单locator就在原10动作内一定能完成（还需delete/confirm）。
- **alternatives**：
  - 官方重复比较不是简单看标题，前面完整比对是必要安全步骤；不能通过省掉比对盲删或加预算凑通过。
- **责任层**：
  - Android前台启动与locator契约
  - FSQ action-aware路径规划
  - 预算边界工作正常，非评分异常

**修复方案（未实施）**

- **P0 / FSQ Android driver owner**；`UiAutomator2AndroidDriver.launch_app / tap_on / _selector`：启动成功需要明确前台后置条件，避免成功dispatch仍需2次launch+launcher恢复；More options使用已观察accessibilityId，不把content-desc当text target。正式动作预算定义不偷偷改变。
- **P1 / FSQ执行策略/工具契约 owner**；`FSQ前计划与写预算ledger`：规划时计入启动、两条全字段比较所需导航、菜单/delete/confirm；同屏候选已明显存在时避免无关往返scroll。若在现有10写内仍不可行，报告预算实验而非改分或取消必要比对。

**未来验证（全部未执行）**

- 离线固定10个admitted写，断言step20文本selector失败与step22预算拒绝分开，未dispatch的重试不能算删除。
- 新设备以7行fixture测最短安全路径：前台启动、两条全字段核对、accessibility菜单删除并确认，只删1条且其他6行逐ID不变；若10写不足，独立记录预算可达性实验。

**双方逐例核对**

已核对：完整双份比较已做；text More options错属性，后accessibility恢复未forward；无删；不保证仅修locator就够10写。

**交叉核对：已核对。** 完整双份比较14/19必要且已做；S20第10admitted用text More options错属性；恢复S22正确accessibility与kill23均在forward前预算拒绝，无删除。仅修定位不保证原10写够，不加预算凑成功。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例050，起始第252行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/4`。
- [原公开goal](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-050-20261110T190605Z-9e00e8/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-050-20261110T190605Z-9e00e8/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:183-211`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:73-115,348-369,380-415`

<a id="case-052"></a>
### 案例 052 — RecipeDeleteDuplicateRecipes3

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains

**约束与冻结初始化**

- **publicGoal**：Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-052-20261110T191501Z-60f662/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：30
- **fixture**：30 noise+2条Butternut target，共32。生成器专门把3条Avocado同名但不同字段noise排列表上端，另加Butternut同title/description却不同字段noise。真正重复是Butternut：3-4 servings/30 mins/quantities to taste/方向以Garnish...结尾。

**官方判据**

- **判据**：初始化插入noise及两条仅recipeId不同的完全重复target；RecipeDeleteDuplicateRecipes.validate_deletion_integrity只接受删除target两ID中的任意一个，并保证另一个与全部原noise行仍存在且未修改，不能新增行。不是按title去重，删同名不同字段noise会失败；返回0.0或1.0。

**原关键轨迹**

-  ：全库滚动看见大量Butternut同名候选，却只搜索/打开Avocado三条不同noise；完全没有delete。

原dispatch额度 22/34，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 期望仅删两条Butternut完全重复中的任一条，剩31条且全部变体保持原样；实际step10-14已显示一串Butternut同标题相同描述，未打开任何Butternut详情。之后搜索Avocado并打开三条分别6 servings/4 hrs/various amounts，3-4 servings/1 hrs/n/a，6 servings/2 hrs/as needed；它们确实不同，但不是排除全库重复的证据。所有43native steps passed而official0，因为零删除，写22/34仍可用。
- 真正重复target一份也未删；没有操作错误不代表任务达标。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - fixture明确Butternut双份target及30 noise，UI step10-14大量同名候选可见；实际只比较Avocado三条不同noise。
  - 原nativeResult runner明确No recipes were deleted，claim execution window而budget22/34/deadlineExceeded=false。
- **强推断**：
  - 候选优先级/collection覆盖ledger丢失：先滚完全库再被列表首部Avocado同名诱饵吸引，没有把已遇到的Butternut簇加入待比较队列；因未证实exact-match就保守停手。
- **unconfirmedOrMissing**：
  - 无After DB，无法全库逐行核实，然而没有任何delete动作足以解释target仍存在；为何282246ms即以execution window收尾由FSQ核对。
- **alternatives**：
  - 同名并不等于exact重复；不能建议按标题批量删Butternut或Avocado。当前未错删是正确安全性，但缺完整完成策略。
- **责任层**：
  - FSQ候选分组/跨页面覆盖与完成判定
  - 任务fixture有意制造同名不同字段干扰，非初始化损坏
  - oracle正常拒绝零删除

**修复方案（未实施）**

- **P1 / FSQ执行策略/工具契约 owner**；`FSQ重复候选ledger与浏览策略`：按公开UI title+description将候选簇登记并保留页面定位，优先检查多条同描述Butternut；用servings/time/ingredients/directions复合指纹排除变体，再只删除精确重复的一份。不要把Avocado三条不同就当全库无重复。
- **P1 / FSQ执行策略/工具契约 owner**；`FSQ主runner提前收尾`：所有候选簇须标已比较/已排除/未处理，存在未处理簇且预算未触顶时不静默结束；结束时输出未处理对象而不是all steps passed=完成。

**未来验证（全部未执行）**

- 离线候选账本应同时保留Butternut与Avocado；仅Avocado完成不能把全库状态标resolved。
- 新设备32行含3个Avocado及8个Butternut变体：只删除一份真正Butternut目标，所有variant recipeId及字段不变；重复候选全部有处理证据。

**双方逐例核对**

已核对：Avocado三不同正确保留，已见Butternut却未处理；22/34零拒绝正常停，非强制timeout。

**交叉核对：已核对。** Butternut已见但只解Avocado三不同，正确保留后未回候选簇，22/34零拒绝正常停、零删除，非强制超时。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/expense-recipes.md)，案例052，起始第287行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/5`。
- [原公开goal](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-052-20261110T191501Z-60f662/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-052-20261110T191501Z-60f662/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:183-211`
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:73-115,348-369,380-415`

<a id="case-059"></a>
### 案例 059 — RetroPlayingQueue

**原身份：failed / officialReward=0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Add the following songs, in order, Through the Storm, Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away to my playing queue in Retro music.

**约束与冻结初始化**

- **publicGoal**：Add the following songs, in order, Through the Storm, Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away to my playing queue in Retro music.
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-059-20261110T194558Z-40f104/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：10
- **fixture**：files有序为Through the Storm、Hidden Paths、Forever Young、Whispers of the Past、Heartbeat Away；10 noise各3–5分钟随机duration。frozen params未保存实际duration或初始playing_queue。

**官方判据**

- **判据**：读取music_playback_state.db的SELECT title from playing_queue，按返回列表与五首目标title逐项完全相等；不接受仅相对顺序、包含子序列、多余歌曲或同曲重复。没有检查是否新append的独立历史条件。
- **initializationCaveat**：继承RetroCreatePlaylist.initialize_task清媒体存储、清PlaylistEntity/SongEntity并写5目标+10noise、扫描后关App；_clear_playlist_dbs未清playing_queue，initialize没有显式清播放DB。不能由此单独证明跨episode污染，但空队列前置条件未由该源码保证。

**原关键轨迹**

-  ：四个后续歌曲确实连续入尾；最终队列还含全库noise，Through不在连续尾段；验证从连续改成相对顺序。

原dispatch额度 30/32，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- oracle期望队列严格只有指定5首。最终step53/55树与step56截图有Under the Sky、Falling Feathers、Dreamer's Awake、Eternal Flame等noise以及重复Hidden Paths；step55可见Through后是Silent Dreams/Chasing Shadows/Beyond the Horizon/Whispering Wind，然后才是Hidden/Forever/Whispers/Heartbeat。step56连续断言失败，step57改成允许其他歌穿插的相对顺序通过，official仍0。
- 最终队列整体不等于五首目标序列，绝非“仅缺Through是否新append证据”。后者是native verifier强调的局部疑点，不是官方0分的最小充分解释。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - FSQ planning_update seq8主动加入preserve the existing queue，原goal没有该限制；official is_successful是严格列表相等。
  - step16界面toast Added 1 title to the playing queue和Through mini-player可见，之后尾部只有另外四首连续；初次操作后是否自动全库建队列/原有队列未被记录。
  - step56失败后改step57弱化为相对顺序，无法完成更强原目标，更不满足exact oracle；30/32写但无硬拒绝。
  - 官方initializer未显式清playing_queue；原episode没有DB/MP3快照或初始队列截图。
- **强推断**：
  - 执行追加策略假设可保留任意原队列，未在开始建立可见队列基线/检查结果全集，与严格终态契约不匹配；单次tap passed也不证明该业务后置条件。
- **unconfirmedOrMissing**：
  - 无法区分初始残留队列、首个Add在空队列自动装载全库、第一条XPath选错导致播放/重建等起源；没有初始/首个Add后playing_queue证据，不能断言跨episode污染已发生。
  - 无DB直接证据解释SQLite物理返回顺序与UI视图关系，但截图明确含非目标已是充分失败证据。
- **alternatives**：
  - 仅修首首locator仍不能自动解决最终多余15首/同名重复；仅用relative order判成功会掩盖问题。
- **责任层**：
  - FSQ计划引入额外preserve限制与验证弱化
  - 官方fixture队列前置状态隔离待核实（非已证实污染）
  - Android业务后置条件与定位（辅助）

**修复方案（未实施）**

- **P1 / FSQ执行策略/工具契约 owner**；`FSQ queue计划/最终验证`：只以公开goal约束规划，不自行添加preserve任意原队列；先观察当前queue基线，逐项添加后核对完整终态/重复与顺序，不能从consecutive失败降级relative-order成功。若前置状态与add语义有冲突，诚实报告而非擅删真实用户队列。
- **P1 / AndroidWorld fixture owner**；`RetroPlayingQueue.initialize_task（新fixture版本，不回改r4）`：task owner核实并在初始化层保证确定的空播放队列或可证明的既定基线，初始化证据保存在private侧，不向agent泄露目标文件/正确序列；保持is_successful原rubric不变，历史r4 official0不重解释为无效。
- **P1 / FSQ执行策略/工具契约 owner**；`UiAutomator2AndroidDriver.tap_on + FSQ locator业务postcondition`：首个菜单在当前目标row内唯一定位并确认popover出现；特别是20/22 passed但没有menu，不能继续假定已打开。通过可见queue变化确认真正追加的是目标。

**未来验证（全部未执行）**

- 原53/55/56截图/树离线断言非目标存在足以失败；verifier summary不得把它缩成Through的新append证据不足。
- 经授权独立实验对空/非空播放队列分别记录首个Add前后UI与evaluator-private DB，再辨别App自动全库建队列 vs residue；目标五首精确最终序列，无额外歌曲、无重复，budget32不变。

**双方逐例核对**

已核对并修正正式边界：完整queue==expected，非suffix/delta/相对顺序；noise/重复充分0；init未清不等跨题污染，不擅清用户队列凑分。

交叉核对：已核对轨迹、有契约冲突保留。retro_music.py:79–97/203–206完整playing_queue title列表==5expected，不是suffix/delta/相对顺序；noise/重复充分失败。初始queue缺证，不坐实跨题污染。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例059，起始第52行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/6`。
- [原公开goal](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-059-20261110T194558Z-40f104/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-059-20261110T194558Z-40f104/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/059-RetroPlayingQueue/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/retro_music.py:79-107,147-160,190-206`

<a id="case-060"></a>
### 案例 060 — RetroPlaylistDuration

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.

**约束与冻结初始化**

- **publicGoal**：Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.
- **源码**：/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-060-20261110T195314Z-4b9455/sources/000-goal.txt
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **noiseCount**：5
- **fixture**：files10首目标理论生成duration整数列表总和2850000ms=47.5min；另外5noise各随机3–5min。此initialize覆盖未调用super/clear_internal_storage，只清playlist DB再写媒体/扫描。frozen params仅文件名，不含实际逐曲duration；无存量MP3/DB，不能重建本轮精确逐曲长度。

**官方判据**

- **判据**：_get_playlist_data对PlaylistEntity JOIN SongEntity只返回有歌曲行；is_successful遍历所有返回歌曲，若任何行playlist_name不是目标即False，否则累加duration_ms，检查闭区间[2700000,3000000]（45–50分钟）。不要求特定曲序或files集合；不把空playlist名创建当成功，空JOIN总和0。
- **publicVsRubric**：公开goal仍要求使用provided songs，不能借较弱oracle忽略公开约束。官方只统计实际SongEntity.duration，不采用源生成理论时长或播放时长。

**原关键轨迹**

-  ：只探一首noise Beyond the Horizon的4:44，无选曲求和，无任何Add to playlist；建成的是0 Songs/00:00空壳。

原dispatch额度 25/30，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 需目标名Reggae Rhythms 51且SongEntity持久化曲目总长45–50min。实际只检查第一首noise Beyond the Horizon(04:44)，没形成时长表/组合，也无Add to playlist调用；step44 Create成功后step45树与截图0 Songs • 00:00。step46全局text contains失败输出根空串，不能否定屏幕实际0歌；step47仅title断言成功，正式0.0。
- 命名playlist已持久化但无歌曲，最终duration=00:00；不是duration求和精度边界，更不是已添加歌曲但oracle漏算。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step12播放第一首noise；step14打开player，16/18退出、22长按、26-30读Details4:44；这些均未建立playlist歌曲映射。
  - step33 target=Playlists和37 target=More options使用text失配后，35 resourceId、39 accessibilityId恢复；step41-44只创建playlist。
  - step45明确0歌；25/30写、deadlineExceeded=false，runner以窗口消耗为由把选曲/添加标skipped。
  - step46与49-step27同类无element根text断言，驱动get_text空值，不是UI数据证据缺失。
- **强推断**：
  - 前期逐曲播放/详情探索和导航恢复耗费写路径，却未把duration采集/组合/批量加入这三个真正业务步骤建立完成账本；收尾只验证可见标题，未以0歌触发继续补充。
- **unconfirmedOrMissing**：
  - 10个target实际媒体duration未留存，无法仅凭params给出精确组合，也不能宣称47.5min在实际编码后精确不变；playlist仍空已足以判失败。
  - 初始化未清内部storage是潜在隔离问题，但当前UI15首与fixture一致，无证据本例因跨题残留失败。
- **alternatives**：
  - App写入bug不是当前主解释：没有Add to playlist动作，空SongEntity是正常预期。改总时长边界/通过空playlist均是改rubric不可取。
- **责任层**：
  - FSQ duration规划/歌曲加入与终态完成
  - Android locator/assert契约（辅助）
  - 官方fixture可复现duration审计数据缺失（诊断限制，不是本例已证实根因）

**修复方案（未实施）**

- **P1 / FSQ执行策略/工具契约 owner**；`FSQ playlist业务计划/ledger`：从公开UI建立song→duration表并组合45–50min，再以多选/逐曲Add to playlist确认SongEntity对应的可见曲目数量和总时长；title存在且0歌必须继续而非收尾。不要把开发者私有files/生成器答案注入agent。
- **P1 / FSQ执行策略/工具契约 owner**；`UiAutomator2AndroidDriver._selector / assert_state 与前台启动`：使用实际resourceId/accessibilityId，避免把content-desc当text；曲目总长核对选择展示duration的元素而非无element全局contains；复用前台启动修复减少launcher恢复。
- **P2 / AndroidWorld harness owner**；`RetroPlaylistDuration fixture私有初始化证据`：今后留存生成后的每文件实际duration/媒体元数据及必要DB基线到evaluator-private审计产物，agent仍只通过UI可见数据完成；保留原rubric与预算。

**未来验证（全部未执行）**

- 原45树及44截图离线断言目标playlist存在但song_count=0/duration=0；46根空text不能推翻截图。
- 经授权设备新实例公开UI测时长并选曲，加入后关闭重开playlist仍有曲目、sum在含边界45/50min范围；noise/多playlist与空playlist均按原rubric判定。

**双方逐例核对**

已核对：仅读noise一首、零Add、空playlist充分0；按指定playlist JOIN实际duration_ms评分，理论47.5min不是本轮读得组合。

交叉核对：已核对。只读noise一首04:44，零Add，0Songs/00:00与根assert空串分开；25/30零拒绝正常停非硬timeout。retro_music.py:41–76/286–293按指定playlist JOIN实际duration_ms总和45–50min，空总0充分失败。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例060，起始第88行。
- [harness独立完整源码/step/截图记录](harness-notes/recipe-media.json)，JSON pointer `/cases/7`。
- [原公开goal](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-060-20261110T195314Z-4b9455/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-060-20261110T195314Z-4b9455/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/retro_music.py:41-76,236-293`

<a id="case-068"></a>
### 案例 068 — SimpleCalendarAnyEventsOnDate

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Do I have any events October 28 in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- **date**：公开goal为October 28、未写年；初始化参考2023-10-15，实际日期选择器明确2023，故此处目标2023-10-28而非2026当前宿主日期。
- **output**：当天全部标题；多项逗号分隔，不能回答yes或导航报告。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：initialize_proto先格式化真实绝对date与相关state，再_maybe_replace_date改写公开goal日期；calendar_utils.clear DB+相关事件+75噪声+shuffle。没有导入/实例化官方任务或重建随机state。

**官方判据**

- **判据**：tasks.textproto 362-405生成同日3个1小时相关事件；title_without_replacement/time_without_replacement会从候选池另选，frozen params.title=Birthday party并非该例三标题。排除该日随机噪声；get_expected_answer取相关state的3个title，按逗号拆分、数量相等、忽略大小写模糊相似度>=0.9逐项匹配。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.calendar.pro
- `agent-tap_on-4` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-6` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-8` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-10` failed；target：null；locator：resourceId：null；accessibilityId：null；text：28；className：null；xpath：null；Target was not found.
- `agent-tap_on-12` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-14` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-16` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-18` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-21` failed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-22` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000010-ui_snapshot.json
- **finding**：选择器仅月Oct/年2023；月视图没有day EditText。
- **path**：artifacts/tools/000012-ui_snapshot.json
- **finding**：返回October月视图；原XML无text=28的可定位节点。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 官方要求3标题；截图可确证Date night并见另外两条截断标题，强推断为Game night、Product demo；实际提交为无法验证说明。
- 没有进入10月28日日视图或取得完整标题；main summary是Unable to verify...，官方IR得到的正是这句而非标题。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - agent-tap_on-10(text=28)报Target was not found；其prepare截图清楚画出28与三条事件，原XML却只暴露toolbar，证明视觉日期与可访问节点不是一回事。
  - top_value→OK流程在steps6/8、12/14、16/18共三次只确认月/年，并未选择28；10个写预算全部消耗为2launch+8tap。
  - 本例mainAnswer.status=valid，非exact_main_summary契约错误；reward=0来自业务答案未匹配，不是official分数无效。
- **强推断**：
  - 终极机制为以可视月网格日期当text locator且未改换有效导航路径，随后重复无进展月/年确认；预算是该路径耗尽的截断点。
  - 截图28格的Game nig / Product / Date night与唯一候选名对应Game night、Product demo、Date night（强推断）；只有Date night在截图未截断。缺少生成后proto/完整日详情，不能把三标题均称已确证。
- **无法确认与备选**：
  - 未存生成后relevant_state的完整proto；禁止重新初始化/random重建来补三标题。
  - launch_app返回passed但初始仍launcher的底层原因待FSQ侧核对。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**；`drivers/android/_uiautomator2.py::launch_app (95-100)；resources/skills/android-harness.md::Case Lifecycle；src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`：launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**；`FSQ main runner task_run_v1.summary；src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)；src/fsq_androidworld_eval/fsq_runner.py (357-366)`：IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**

- 离线用月网格只有像素无day节点的固定UI fixture，断言不对不存在的text=28重复派发；有设备的未来验证应证明切换/截图坐标导航后显示目标日期且读齐3条标题。
- 离线答案协议fixture断言只有UI取证的三标题进入summary，不把冻结params.title当答案；不得把本例私有标题注入future agent。

**双方逐例核对**

已核对：grid无text日期/picker仅月年；Oct28三title withoutreplacement，完整生成值缺证。

交叉核对：已核对。grid无数字text、picker仅月年；Oct28三title withoutreplacement，完整生成标题缺证，未到目标集合非已转录错。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例068，起始第122行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/0`。
- [原公开goal](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：147-210`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：362-405`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/calendar_utils.py；lines：133-155,215-331`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：297-306,336-403`

<a id="case-069"></a>
### 案例 069 — SimpleCalendarDeleteEvents

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> In Simple Calendar Pro, delete all the calendar events on 2023-10-27

**约束与冻结初始化**

- **date**：明确2023-10-27全天，不能只删一个或本周其它日。
- **integrity**：删除3条目标事件且20条非目标噪声不变。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。

**官方判据**

- **判据**：SimpleCalendarDeleteEvents.n_rows=3；initialize添加目标行并记before/rows_to_delete；is_successful比较目标id消失、其余行原样且无新增。不是只看屏幕为空。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-tap_on-3` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-5` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-7` passed；target：Go to date；locator：null
- `agent-tap_on-9` passed；target：OK；locator：null
- `agent-tap_on-11` failed；target：27；locator：null；Target was not found.
- `agent-tap_on-12` failed；target：More options；locator：null；Target was not found.
- `agent-tap_on-15` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-17` passed；target：null；locator：resourceId：null；accessibilityId：null；text：Go to date；className：null；xpath：null
- `agent-tap_on-19` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-21` failed；target：null；locator：resourceId：null；accessibilityId：null；text：27；className：null；xpath：null；Target was not found.
- `agent-tap_on-24` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-26` passed；target：null；locator：resourceId：null；accessibilityId：null；text：Go to date；className：null；xpath：null
- `agent-tap_on-28` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-30` failed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000011-ui_snapshot.json
- **finding**：Go to date打开的是Oct/2023二列月年选择器，并无27日字段。
- **path**：artifacts/tools/000027-ui_snapshot.json
- **finding**：仍October月视图；没有day=27可定位文本；未出现Delete确认。

原dispatch额度 14/14，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 目标2023-10-27 11:00 Review session for Project X、12:00 Catch up on Project X、21:00 Call with the Team应消失，20噪声保留；实际停在月视图。
- 整个执行没有进入目标事件详情，也未执行任何Delete；官方目标三行没有可证实的删除行为，reward=0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - events43与71请求text/target 27（steps11/21）均Target was not found；step12 More options同样失败。
  - steps5/7/9、15/17/19、24/26/28重复菜单Go to date→OK，只返回月视图。14预算=1launch+13tap，3个失败尝试也被计入；step30及kill遭拒。
- **强推断**：
  - 把月视图Go to date误当可以选择某一天，并在无日节点的canvas网格坚持文本点击，是导航闭环失效；不是删除操作本身失败。
- **无法确认与备选**：
  - 没有评分时DB before/after dump，不能量化副作用；现存动作无Delete，官方0与此一致。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**

- 离线核对冻结三目标行与20噪声的删除集合判据；未来设备验证应逐条删除/确认后核对目标日为空且非目标日期未变，不运行oracle驱动导航。

**双方逐例核对**

已核对：循环无Delete，3target20noise冻结可确认；after DB未知。

交叉核对：已核对。无Delete且循环；冻结3target/20noise可确认，afterDB未知，不假称读到终态。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例069，起始第155行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/1`。
- [原公开goal](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar.py；lines：264-288`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar_evaluators.py；lines：24-45`

<a id="case-070"></a>
### 案例 070 — SimpleCalendarDeleteEventsOnRelativeDay

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> In Simple Calendar Pro, delete all events scheduled for this Monday.

**约束与冻结初始化**

- **date**：公开this Monday，冻结参考2023-10-15周日，应指2023-10-16周一；不是按宿主2026日期或状态栏content-desc推算。
- **integrity**：删除该日两条事件，保留20噪声。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。

**官方判据**

- **判据**：SimpleCalendarDeleteEventsOnRelativeDay.n_rows=2，goal周一来自冻结day_of_week/2023-10-16；继承DeleteMultipleRows精确目标行移除与其它行不变。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.calendar.pro
- `agent-tap_on-4` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-6` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/change_view；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-8` passed；target：Daily view；locator：null
- `agent-tap_on-10` failed；target：More options；locator：null；Target was not found.
- `agent-tap_on-12` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-14` passed；target：Go to date；locator：null
- `agent-tap_on-16` passed；target：16；locator：null
- `agent-tap_on-17` passed；target：OK；locator：null
- `agent-tap_on-19` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-21` passed；target：Review session for Budget Planning；locator：null
- `agent-tap_on-23` failed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/delete；accessibilityId：null；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-tap_on-24` failed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/delete；accessibilityId：null；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-25` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000016-ui_snapshot.json
- **finding**：日期选择器中15是NumberPicker编辑值；tap target 16是相邻可视项，不等于提交16。
- **path**：artifacts/tools/000019-ui_snapshot.json
- **finding**：OK后仍October 15 (Sun)。
- **path**：artifacts/tools/000021-ui_snapshot.json
- **finding**：step19右箭头后October 16 (Mon)，00:00 Budget Planning、10:00 Project X两事件。
- **path**：artifacts/tools/000023-ui_snapshot.json
- **finding**：已打开Budget Planning详情；目标日期与00:00确认。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 2023-10-16 00:00 Review session for Budget Planning及10:00 Review session for Project X均删除，20噪声不变；实际只打开前者详情。
- 定位到正确周一且打开第一条详情时预算恰好用尽；首次Delete step23未获准派发，后续重试24同样拒绝，两个目标事件未删除。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - steps1/3重复launch、step10 More options失败、step16 tap16后17 OK仍回15，额外step19右箭头才到16。
  - 12个写名额=2launch+10tap；首次Delete与重试分别events65/67，均预算拒绝，非点击命中后删不掉。
- **强推断**：
  - 日期选择动作未核验有效提交，加上启动恢复和一次无效菜单点击耗尽业务路径；预算不足是开销与规划契约不匹配的结果，不是日期/时区错。
- **无法确认与备选**：
  - 若无启动开销/无效日期动作，固定12预算是否足够逐条删除两事件仍需未来设备路径验证；不可凭此私加预算。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ Android driver + harness契约owner**；`drivers/android/_uiautomator2.py::launch_app (95-100)；resources/skills/android-harness.md::Case Lifecycle；src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`：launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ Android driver/规划owner**；`drivers/android/_uiautomator2.py::input_text (138-151)；FSQ日历日期导航规划`：NumberPicker不能只以set_text未抛错判成功；在通用文本输入结果中暴露实际值/提交后值，规划需依据当前控件支持的滑轮或编辑提交方法完成日期选择，并核对返回日视图日期。不要硬编码本题20或扩大预算。
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**

- 离线NumberPicker fixture证明tap相邻16不被当作提交；设备验证固定原12预算内从正确启动状态完成两条删除并保留噪声，若不可行另列跨任务预算研究而不改本题成绩。

**双方逐例核对**

已核对：已到Monday=本fixtureOct16，两Delete未forward；后续确认成本未知。

交叉核对：已核对。本fixture Monday=Oct16已确认且已到；两Delete未forward，不再留Monday日期未知，后续确认成本未知。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例070，起始第187行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/2`。
- [原公开goal](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar.py；lines：264-288`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar_evaluators.py；lines：24-45`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar.py；lines：367-418`

<a id="case-071"></a>
### 案例 071 — SimpleCalendarDeleteOneEvent

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> In Simple Calendar Pro, delete the calendar event on 2023-10-24 at 23h with the title 'Workshop on Project X'

**约束与冻结初始化**

- **date**：2023-10-24 23:00，仅标题Workshop on Project X的一条；不能删除其它同日或相似标题。
- **integrity**：目标23:00–23:30消失，其余20行原样。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。

**官方判据**

- **判据**：SimpleCalendarDeleteOneEvent.n_rows=1，沿用目标id删除完整性判定；冻结row_objects含唯一23:00 Workshop on Project X。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-tap_on-3` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-5` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-7` passed；target：Go to date；locator：null
- `agent-tap_on-9` passed；target：OK；locator：null
- `agent-tap_on-11` failed；target：24；locator：null；Target was not found.
- `agent-tap_on-13` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-15` passed；target：Go to date；locator：null
- `agent-tap_on-17` passed；target：OK；locator：null
- `agent-tap_on-19` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/change_view；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-21` passed；target：Daily view；locator：null
- `agent-tap_on-23` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-input_text-25` failed；target：null；locator：resourceId：null；accessibilityId：null；text：null；className：null；xpath：//android.widget.EditText[@text='15']；text：24；textType：literal；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-26` failed；app_id：null；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000011-ui_snapshot.json
- **finding**：Go to date仅Oct/2023，不选24日。
- **path**：artifacts/tools/000015-ui_snapshot.json
- **finding**：October月视图XML无24日文本；step11 target24失败。
- **path**：artifacts/tools/000033-ui_snapshot.json
- **finding**：后来切Daily view后仍October15，非24。

原dispatch额度 12/12，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 唯一2023-10-24 23:00–23:30 Workshop on Project X删除；实际仍10月15日日导航阶段。
- 没到10月24日也没有打开或删除目标；最后尝试把日期编辑值15改24（step25）在派发前被预算拒绝。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - step11 target24 Target was not found；两轮菜单Go to date→OK未选择日。
  - 改Daily view至step21、再点top_value至23已消耗12/12；input_text25与kill26遭拒；原轨迹无Delete。
- **强推断**：
  - 先把月年对话框当日选择，再过晚切换真正可编辑日的路径；无day节点场景未及早切换可访问视图导致任务终止。
- **无法确认与备选**：
  - 未执行被拒绝的input_text24，不能将74的NumberPicker未提交直接当成本例已发生；本例的输入没有真正调用。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**

- 离线保证月年picker不会被标记为完成日导航；设备固定12预算验证到24后只选23:00目标并删除，核对20噪声不变。

**双方逐例核对**

已核对：input25是预算前拒，非74输入失效；23:00-23:30不跨日。

交叉核对：已核对。input25在forward前预算拒绝，不套074输入passed但值无效；fixture目标23:00–23:30不跨日，失败仍在导航/未删。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例071，起始第221行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/3`。
- [原公开goal](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar.py；lines：264-288`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py；lines：73-115,348-369`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar_evaluators.py；lines：24-45`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/calendar/calendar.py；lines：323-364`

<a id="case-072"></a>
### 案例 072 — SimpleCalendarEventOnDateAtTime

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What is on my schedule for October 27 2023 at 8:00pm in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- **date**：公开绝对2023-10-27 8:00pm即20:00。
- **output**：该时刻所有标题，逗号分隔；不是当天全部事件。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：initialize_proto先格式化真实绝对date与相关state，再_maybe_replace_date改写公开goal日期；calendar_utils.clear DB+相关事件+75噪声+shuffle。没有导入/实例化官方任务或重建随机state。

**官方判据**

- **判据**：tasks.textproto 239-275放入2023-10-27 20:00 Product demo持续15min；噪声排除该时点重叠（calendar_utils组合绝对datetime、含端点）；success取相关title并做STRING_MATCH。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.calendar.pro
- `agent-tap_on-4` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-6` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-8` passed；target：Go to date；locator：null
- `agent-tap_on-10` passed；target：OK；locator：null
- `agent-tap_on-12` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-14` passed；target：Go to date；locator：null
- `agent-tap_on-16` passed；target：OK；locator：null
- `agent-tap_on-18` failed；target：More options；locator：null；Target was not found.
- `agent-tap_on-20` failed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-21` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000011-ui_snapshot.json
- **finding**：Go to date为Oct/2023月年picker，无目标日选择。
- **path**：artifacts/tools/000018-ui_snapshot.json
- **finding**：第二轮同样只月/年。
- **path**：artifacts/tools/000020-ui_snapshot.json
- **finding**：仍October月视图，未显示27日20:00详情。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- Product demo（冻结相关事件20:00–20:15），实际提交无能为力说明。
- 未到10月27日，也未读20:00事件；actual main summary为Unable to determine...，非Product demo，official=0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - Go to date→OK在steps6/8/10、12/14/16重复，未有日值修改；step18抽象More options Target was not found；step20及kill21遭预算拒绝。
  - 10写=2launch+8tap，未出现目标event标题读取或时刻判断，不能归为8pm边界判错。
- **强推断**：
  - 月年picker与目标日导航混淆，加上不验证进展导致重复路径；标题输出失败为该导航失败的后果。
- **无法确认与备选**：
  - 无法从未访问目标日的native轨迹判断agent会否正确处理跨日重叠边界；本例不能据此指控时间推理。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**；`drivers/android/_uiautomator2.py::launch_app (95-100)；resources/skills/android-harness.md::Case Lifecycle；src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`：launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**；`FSQ main runner task_run_v1.summary；src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)；src/fsq_androidworld_eval/fsq_runner.py (357-366)`：IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**

- 离线固定绝对20:00和含端点重叠fixture检查筛选逻辑；未来设备证明目标日标题、时间均可见且summary只含UI证实标题，绝不把冻结Product demo传给future agent。

**双方逐例核对**

已核对：未到目标日；oracle预定相关时刻覆盖及端点标题，非动态读UI过滤。

交叉核对：已核对。未到目标日；oracle预定相关时刻覆盖/端点title，并非动态读UI筛选，不将未执行at谓词当本轮算法错误。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例072，起始第254行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/4`。
- [原公开goal](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：147-210`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：239-275`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/calendar_utils.py；lines：133-155,215-331`

<a id="case-074"></a>
### 案例 074 — SimpleCalendarEventsInTimeRange

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Do I have any events between 4:15pm and 8pm Friday in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- **date**：公开Friday，初始化reference 2023-10-15 Sunday，因此冻结目标2023-10-20 Friday；不是2026-11-13。
- **range**：4:15pm至8pm即16:15–20:00；公开between应检查边界，官方生成包含起点，排除条件>=16:15且<=20:00，实现按事件跨度重叠排噪。
- **output**：符合区间事件标题，非截图上任意其它日标题。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：initialize_proto先格式化真实绝对date与相关state，再_maybe_replace_date改写公开goal日期；calendar_utils.clear DB+相关事件+75噪声+shuffle。没有导入/实例化官方任务或重建随机state。

**官方判据**

- **判据**：tasks.textproto 964-1006的相关事件Cooking Class从16:15持续1h（17:15结束），含下界；噪声由calendar_utils.check_event_conditions按起止时点OR及日期相交排除；official本身不重新查UI区间，而从相关state取title匹配。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-tap_on-3` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-5` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/change_view；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-7` passed；target：Daily view；locator：null
- `agent-tap_on-9` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-input_text-11` passed；target：null；locator：resourceId：null；accessibilityId：null；text：null；className：null；xpath：//android.widget.EditText[@text='15']；text：20；textType：literal
- `agent-tap_on-12` passed；target：OK；locator：null
- `agent-tap_on-14` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-15` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-16` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-18` failed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-tap_on-19` failed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_right_arrow；accessibilityId：null；text：null；className：null；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-20` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000012-ui_snapshot.json
- **finding**：picker日值15，可见月Oct、年2023。
- **path**：artifacts/tools/000015-ui_snapshot.json
- **finding**：input_text20 passed及OK之后仍October15(Sun)，输入没有成为选择值。
- **path**：artifacts/tools/000019-ui_snapshot.json
- **finding**：连续三次右箭头后只有October18(Wed)，到Friday还差2天。

原dispatch额度 10/10，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- Cooking Class（2023-10-20 16:15–17:15，处在含下界区间内），实际无法确定说明；未发生端点错选。
- 关键输入step11对NumberPicker set_text20返回passed，但after-action截图选中项仍15；其后只能逐日前进，18日时10预算耗尽，最终未检查20日16:15–20:00。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 原after截图可直接读15，不是猜测输入失败；step11前后compact UI的sha相同，step12 OK后日视图也仍15。
  - events49/51/53三次右箭头使15→18；events57/59两次继续导航均denied，不是到了Friday后筛错区间。
  - main预计划写overlapping；本例没有看到Friday日程，不能把start-only/overlap的语义差异当实际失败原因。
- **强推断**：
  - input_text实现只selector.click/clear/set_text后直接passed（138-151）缺少NumberPicker提交值核验，模型信任这个低层成功；再用逐日导航消耗配额，直接造成未到目标日。
- **无法确认与备选**：
  - 值为什么未提交：NumberPicker忽略文本、焦点/IME与commit回滚等需最小未来控件验证区分，现存after截图不能区分底层分支。
- **责任层**：
  - FSQ Android driver输入成功语义/NumberPicker提交证据
  - FSQ日期导航状态后置条件与IR输出协议

**修复方案（未实施）**

- **P1 / FSQ Android driver/规划owner**；`drivers/android/_uiautomator2.py::input_text (138-151)；FSQ日历日期导航规划`：NumberPicker不能只以set_text未抛错判成功；在通用文本输入结果中暴露实际值/提交后值，规划需依据当前控件支持的滑轮或编辑提交方法完成日期选择，并核对返回日视图日期。不要硬编码本题20或扩大预算。
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ输出协议owner + harness owner**；`FSQ main runner task_run_v1.summary；src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)；src/fsq_androidworld_eval/fsq_runner.py (357-366)`：IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**

- 离线以本例前后原UI与截图fixture断言dispatch passed≠日期已改；设备用非本题合成日期检查编辑/提交后的NumberPicker值和日视图一致。
- 边界未来独立fixture覆盖start=16:15、end=16:15、start=20:00、晚于20:00与跨午夜；保持官方现有rubric，不能改变为只看start以提高分数。

**双方逐例核对**

已核对：input20 passed→after仍15→OK仍15→仅到18；底层提交失败分支未知，非overlap算法错。

交叉核对：已核对。input20 passed→after仍15→OK仍15→只走到18；底层提交分支未知，非overlap算法错。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例074，起始第287行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/5`。
- [原公开goal](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：147-210`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：964-1006`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/calendar_utils.py；lines：133-155,215-331`

<a id="case-076"></a>
### 案例 076 — SimpleCalendarFirstEventAfterStartTime

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Among events starting on October 29 2023 between 00:00 and 23:59 in Simple Calendar Pro, which starts first strictly after 21:00? Answer with the titles only. If multiple events share the earliest qualifying start time, format their titles as a comma separated list.

**约束与冻结初始化**

- **date**：明确2023-10-29，候选仅当天00:00–23:59开始的事件。
- **range**：严格晚于21:00，不含21:00；只返回最早合格start及全部同start并列标题；跨日结束不应排除当日21:30开始事件。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：initialize_proto先格式化真实绝对date与相关state，再_maybe_replace_date改写公开goal日期；calendar_utils.clear DB+相关事件+75噪声+shuffle。没有导入/实例化官方任务或重建随机state。

**官方判据**

- **判据**：修正后tasks.textproto 857-894以同一hour生成21:30 Grocery Shopping，持续3h至次日00:30；排除同日严格>21:00的噪声。expected title仅Grocery Shopping，严格边界与跨日结束均由冻结模板保证。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.calendar.pro
- `agent-tap_on-4` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-6` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/top_value；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-8` passed；target：null；locator：resourceId：android:id/button1；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-10` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-12` passed；target：Go to date；locator：null
- `agent-tap_on-14` passed；target：OK；locator：null
- `agent-tap_on-16` failed；target：29；locator：null；Target was not found.
- `agent-tap_on-18` passed；target：null；locator：resourceId：null；accessibilityId：More options；text：null；className：null；xpath：null
- `agent-tap_on-20` failed；target：Go to date；locator：null；NativeActionBudgetExceeded: action_budget
- `agent-kill_app-21` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000009-ui_snapshot.json
- **finding**：top_value为月/年picker，非选择29日。
- **path**：artifacts/tools/000017-ui_snapshot.json
- **finding**：Go to date再次为Oct/2023月年picker。
- **path**：artifacts/tools/000019-ui_snapshot.json
- **finding**：月视图XML无29日文本；step16 target29失败。
- **path**：artifacts/screenshots/screenshot-agent-tap-on-16-prepare-before-action-1-a37144650d6e.png
- **finding**：独立看像素可见29格Grocery Shopping标题，但没有21:30开始时间；不能把可见标题当已完成最早合格时间判断。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- Grocery Shopping（2023-10-29 21:30开始，严格晚于21:00；结束次日00:30不改变候选资格），actual inability summary。
- 未打开29日日程或21:30事件详情，月网格截图虽能看见Grocery Shopping字样但未核对start时间；summary仍是inability而非标题，official=0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - steps6/8月年确认后steps10/12/14再菜单月年确认，step16 text29 Target was not found；step18只重开菜单，step20及kill遭拒。
  - 10写=2launch+8tap；未到时间筛选，不能把旧版FirstEvent语义/21:00严格边界错判当实际根因。
- **强推断**：
  - 可视月日没有可定位文本、策略仍循环月年picker，是导航机制失配；有明确日期并未因timezone跨日。
- **无法确认与备选**：
  - native未读相关21:30–00:30事件，不能确定其会否误按结束日排除或漏并列。
- **责任层**：
  - FSQ可访问月网格/日期导航状态规划
  - 写预算为该错误路径的截断点，不是终极根因

**修复方案（未实施）**

- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**；`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md；drivers/android/_uiautomator2.py::tap_on/input_text`：将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**；`drivers/android/_uiautomator2.py::launch_app (95-100)；resources/skills/android-harness.md::Case Lifecycle；src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`：launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**；`FSQ main runner task_run_v1.summary；src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)；src/fsq_androidworld_eval/fsq_runner.py (357-366)`：IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**

- 离线合成strictly-after fixture：21:00不选、21:30并列全选、次日00:01开始不选、当日跨夜结束仍选；未来设备验证日期导航与titles-only协议，不传oracle标题。

**双方逐例核对**

已核对：修正版目标21:30至次日00:30，失败在导航；strict-after未实际误算。

交叉核对：已核对。修正版目标事件21:30至次日00:30已确认，开始日符合目标日，跨午夜结束不排除；失败在导航，未发生strictafter误算，不回填私有title。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例076，起始第322行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/6`。
- [原公开goal](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：147-210`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：857-894`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/calendar_utils.py；lines：133-155,215-331`

<a id="case-078"></a>
### 案例 078 — SimpleCalendarNextEvent

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What is my next upcoming event in Simple Calendar Pro? Answer with the title only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- **date**：next upcoming锚定冻结初始化2023-10-15 15:34 UTC；实际下拉截图明确Sun Oct15、15:35。
- **clockSources**：UI XML clock text=15:35但content-desc=23:35，同一快照有不一致；截图可见时间支持15:35，不可泛称timezone造成整任务时间错乱。
- **output**：最早未来事件标题，不能只证明某事件存在。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：initialize_proto先格式化真实绝对date与相关state，再_maybe_replace_date改写公开goal日期；calendar_utils.clear DB+相关事件+75噪声+shuffle。没有导入/实例化官方任务或重建随机state。

**官方判据**

- **判据**：tasks.textproto 125-168放入当日22:35–22:45 Board meeting；排除当日15:30到目标时刻（含端点）的噪声，保证其是预设now之后最早。expected=Board meeting。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-tap_on-3` passed；target：null；locator：resourceId：null；accessibilityId：Predicted app: Calendar；text：null；className：null；xpath：null
- `agent-tap_on-5` passed；target：null；locator：resourceId：com.simplemobiletools.calendar.pro:id/change_view；accessibilityId：null；text：null；className：null；xpath：null
- `agent-tap_on-7` passed；target：Simple event list；locator：null
- `agent-swipe-9` passed；direction：down；start：null；end：null；reference_screen_size：null；duration：null
- `agent-swipe-10` passed；direction：null；start：x：530；y：1；end：x：530；y：1100；reference_screen_size：width：1080；height：2400；duration：500
- `agent-press_key-12` passed；key：Back
- `agent-tap_on-15` passed；target：Board meeting；locator：null
- `agent-press_key-17` passed；key：Back
- `agent-tap_on-19` passed；target：null；locator：resourceId：null；accessibilityId：null；text：Board meeting；className：null；xpath：null
- `agent-assert_state-21` passed；element：resourceId：com.simplemobiletools.calendar.pro:id/event_title；accessibilityId：null；text：Board meeting；className：null；xpath：null；enabled：null；checked：null；selected：null；clickable：null；focused：null；text：null；optional：false
- `agent-press_key-22` failed；key：Back；NativeActionBudgetExceeded: action_budget
- `agent-press_key-23` failed；key：Back；NativeActionBudgetExceeded: action_budget
- `agent-tap_on-25` failed；target：null；locator：resourceId：null；accessibilityId：null；text：null；className：android.widget.ImageButton；xpath：null；NativeActionBudgetExceeded: action_budget
- `agent-assert_state-26` passed；element：resourceId：com.simplemobiletools.calendar.pro:id/event_title；accessibilityId：null；text：Board meeting；className：null；xpath：null；enabled：null；checked：null；selected：null；clickable：null；focused：null；text：null；optional：false
- `agent-kill_app-27` failed；app_id：com.simplemobiletools.calendar.pro；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000008-ui_snapshot.json
- **finding**：Simple event list列15 Sunday：02:28/04:01/08:32过去事件、22:35 Board meeting、22:57 Appointment；16 Monday后续。
- **path**：artifacts/tools/000012-ui_snapshot.json
- **finding**：坐标从y=1下拉误打开通知面板，可见15:35 Sun Oct15。
- **path**：artifacts/tools/000025-ui_snapshot.json
- **finding**：Board meeting详情确认October15、22:35–22:45。
- **path**：artifacts/tools/000032-ui_snapshot.json
- **finding**：第二次打开同一详情；step21/26只assert标题存在。

原dispatch额度 10/10，denied=4，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- Board meeting；actual是无法确定最早未来事件的说明，即使title assertions passed仍没有提交业务答案。
- 已经读到并两次确认正确Board meeting详情，但没有把list顺序、当前截图时间与事件时间结合为最早未来事件证据；main最终仍Could not conclusively determine...，official=0。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - first list同日三个早晨事件均早于截图15:35，下一条22:35且后一条22:57；可见证据足以支持Board meeting，无需读oracle。
  - step10坐标swipe从屏幕y=1下拉打开通知栏，step12 Back恢复；steps15/19重复打开Board meeting，剩余writes耗在重复查看。
  - 10预算用完后仍两次Back及额外tap遭拒；assert_state21/26属于不计写观察，仅能确认标题，不证明min(start>now)。
- **强推断**：
  - 终极推理缺口是未对已获得的时间与有序agenda做候选排除闭环，加之边缘滑动/重复详情浪费预算；存在clock accessibility label与可见时间冲突，可能增加不确定性，但无已存内部思考证明它就是决策原因。
- **无法确认与备选**：
  - 无法证实agent是否采信23:35 content-desc；不能将该标签差异当已证实timezone根因。
- **责任层**：
  - FSQ IR候选筛选/证据聚合
  - FSQ内容滚动与输出协议

**修复方案（未实施）**

- **P1 / FSQ输出协议owner + harness owner**；`FSQ main runner task_run_v1.summary；src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)；src/fsq_androidworld_eval/fsq_runner.py (357-366)`：IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。
- **P1 / FSQ planner/driver owner**；`FSQ日历IR规划/证据聚合；drivers/android/_uiautomator2.py::swipe`：以原可见当前时间、日期及agenda有序列表建立start>now且无更早候选的证据；clock text/content-desc冲突时区分来源并用截图而非任意解释为时区。滚动限定内容区域，禁止从状态栏边缘起手的内容滚动；完整证据已足够时不重复打开同一详情。

**未来验证（全部未执行）**

- 离线用原list/详情/通知栏截图fixture断言22:35是15:35之后最早可见候选，明确早晨past与次日future；独立clock-label冲突fixture记录依据不臆断timezone。
- 未来设备只需验证内容区swipe不拉开通知栏；min/start排序推理与summary协议可离线验证。

**双方逐例核对**

已核对：已有较充分候选却summary不答；clock text15:35/contentdesc23:35并存，模型采何者未知。

交叉核对：已核对、有时钟capture保留。较充分候选已读但summary不答；clock text15:35/content-desc23:35并存，模型采用哪项未知，不把15点解释当已证唯一当前时间。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/calendar-retro.md)，案例078，起始第355行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/7`。
- [原公开goal](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/information_retrieval.py；lines：82-119`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto_utils.py；lines：147-210`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/proto/tasks.textproto；lines：125-168`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/information_retrieval/calendar_utils.py；lines：133-155,215-331`

<a id="case-081"></a>
### 案例 081 — SimpleSmsReply

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Reply to +18407874306 with message: Yoga class every Tuesday and Thursday at 6 PM. in Simple SMS Messenger

**约束与冻结初始化**

- **recipient**：+18407874306已有收到消息的会话，不是任意最近会话。
- **body**：Yoga class every Tuesday and Thursday at 6 PM.（含句号），必须实际发送而非草稿。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：SimpleSMSSendSms.initialize_task关闭飞行模式、清sms与threads、读设备时间与sent；子类按目标插入收件/clipboard/contact。不会每题验证ROLE_SMS holder；setup配置不等于本题角色观测。

**官方判据**

- **判据**：SimpleSmsReply.initialize_task先清短信，随机插入噪声与目标号码收件；继承SimpleSMSSendSms要求共享Telephony sent provider有匹配number/body、设备5分钟时间窗，且评分时前台包为Simple SMS Messenger。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.smsmessenger
- `agent-kill_app-4` passed；app_id：null
- `agent-launch_app-5` passed；app_id：null
- `agent-swipe-7` passed；direction：up；start：null；end：null；reference_screen_size：null；duration：null
- `agent-tap_on-9` passed；target：null；locator：resourceId：null；accessibilityId：Messages；text：null；className：null；xpath：null
- `agent-press_key-11` passed；key：Home
- `agent-swipe-12` passed；direction：up；start：null；end：null；reference_screen_size：null；duration：null
- `agent-swipe-14` passed；direction：up；start：null；end：null；reference_screen_size：null；duration：null
- `agent-tap_on-16` passed；target：null；locator：resourceId：null；accessibilityId：SMS Messenger；text：null；className：null；xpath：null
- `agent-tap_on-18` passed；target：null；locator：resourceId：null；accessibilityId：null；text：+18407874306；className：null；xpath：null
- `agent-tap_on-20` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：null；className：null；xpath：null
- `agent-input_text-21` failed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：null；className：null；xpath：null；text：Yoga class every Tuesday and Thursday at 6 PM.；textType：literal；NativeActionBudgetExceeded: action_budget
- `agent-input_text-22` failed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：null；className：null；xpath：null；text：Yoga class every Tuesday and Thursday at 6 PM.；textType：literal；NativeActionBudgetExceeded: action_budget
- `agent-assert_visible-23` failed；target：null；locator：resourceId：null；accessibilityId：null；text：Yoga class every Tuesday and Thursday at 6 PM.；className：null；xpath：null；optional：false；Target was not found.
- `agent-kill_app-24` failed；app_id：com.simplemobiletools.smsmessenger；NativeActionBudgetExceeded: action_budget
- **path**：artifacts/tools/000012-ui_snapshot.json
- **finding**：误点Messages后前台是com.google.android.apps.messaging，页面提示不是默认SMS app。
- **path**：artifacts/tools/000017-ui_snapshot.json
- **finding**：真正SMS Messenger列表含目标+18407874306，收到Book club meets next Tuesday to discuss 1984。
- **path**：artifacts/tools/000022-ui_snapshot.json
- **finding**：目标会话正确，composer仍Type a message…，没有请求正文或发送气泡。

原dispatch额度 12/12，denied=3，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 在+18407874306会话实际发出精确Yoga...正文并保留正确前台；actual目标会话空composer，无发送步骤。
- 会话找对，但step21/22两次输入都在dispatch前被预算拒绝，未输入更未发送；最终assert_visible找不到请求正文。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - 前12写被3launch、一次中途kill、3swipe、一次Home、4tap占满；其中进入Google Messages是错误app分支。
  - 目标号码已通过step18打开，step20另点composer消耗最后write；input_text本身已包含click/clear/set_text，因此此前单独tap不是必要原语。
  - 本例最终kill被拒，不能套用其它4例“发送后kill造成前台冲突”作为本例0分原因；这里只存在中途kill。
- **强推断**：
  - 启动工具未保证前台加上根据launcher标签误选Messages、恢复漫游及冗余composer tap，把有限写配额花在到达app/会话之前；不是收件人选择错误或输入内容格式错。
- **无法确认与备选**：
  - Google Messages非默认的UI不能证明当时哪一个包是ROLE_SMS holder；也不能把这个提示当Simple SMS Messenger非默认的证据。
- **责任层**：
  - FSQ启动成功语义与app身份恢复规划
  - 写预算契约下的重复/冗余导航

**修复方案（未实施）**

- **P1 / FSQ Android driver + harness契约owner**；`drivers/android/_uiautomator2.py::launch_app (95-100)；resources/skills/android-harness.md::Case Lifecycle；src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`：launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ planner owner**；`FSQ短信规划/资源skills；drivers/android/_uiautomator2.py::input_text (138-151)`：依公开Simple SMS Messenger app身份确认package，不能把Messages launcher标签当同一app；已确定composer后直接用复合input_text，不额外tap后再耗配额；action_budget明确拒绝后不要同语义重试。

**未来验证（全部未执行）**

- 离线用两个Messages/SMS Messenger图标与Google非默认页fixture验证身份区分；未来设备固定12预算要求目标会话输入并发送，不能增加预算或同题再试计分。

**双方逐例核对**

已核对：号码正确但input/Send未派发；Google非默认提示不证明Simple角色错。

交叉核对：已核对。号码正确但input/Send未派发；Google Messages非默认不等Simple SMS角色错误，kill尾部亦拒。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例081，起始第107行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/8`。
- [原公开goal](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：93-152,211-276`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/sms.py；lines：115-155`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：406-433`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/adb_utils.py；lines：1426-1446`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`

<a id="case-082"></a>
### 案例 082 — SimpleSmsReplyMostRecent

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Reply to the most recent text message using Simple SMS Messenger with message: A quick brown fox.

**约束与冻结初始化**

- **recipient**：most recent received text的发送号码；公开goal不直接给号码，必须从会话顺序/时间识别。实际最顶+17594820731。
- **body**：A quick brown fox.
- **actualSend**：在该收到The early bird catches the worm.的会话实际发送，而非新建错会话或草稿。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：SimpleSMSSendSms.initialize_task关闭飞行模式、清sms与threads、读设备时间与sent；子类按目标插入收件/clipboard/contact。不会每题验证ROLE_SMS holder；setup配置不等于本题角色观测。

**官方判据**

- **判据**：SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.smsmessenger
- `agent-assert_state-13` passed；element：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：A quick brown fox.；className：null；xpath：null；enabled：null；checked：null；selected：null；clickable：null；focused：null；text：null；optional：false
- `agent-tap_on-14` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_send_message；accessibilityId：null；text：null；className：null；xpath：null
- `agent-assert_state-16` passed；element：resourceId：com.simplemobiletools.smsmessenger:id/thread_message_body；accessibilityId：null；text：A quick brown fox.；className：null；xpath：null；enabled：null；checked：null；selected：null；clickable：null；focused：null；text：null；optional：false
- `agent-assert_visible-17` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_success；accessibilityId：null；text：null；className：null；xpath：null；optional：false
- `agent-assert_with_ai-18` passed；prompt：Verify the current conversation is with +17594820731 and contains the received message 'The early bird catches the worm.' and the outgoing reply 'A quick brown fox.' with a successful sent indicator, not merely draft text.；optional：false
- `agent-kill_app-19` passed；app_id：com.simplemobiletools.smsmessenger
- **path**：artifacts/tools/000012-ui_snapshot.json
- **finding**：列表最顶+17594820731、15:34、The early bird catches the worm.；其它会话其后。
- **path**：artifacts/tools/000014-ui_snapshot.json
- **finding**：进入同号码并见原入站内容。
- **path**：artifacts/tools/000018-ui_snapshot.json
- **finding**：发送后出现A quick brown fox.消息体，composer为空；最终kill prepare截图有右侧气泡checkmark。

原dispatch额度 9/12，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 共享sent provider应有+17594820731的A quick brown fox.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。
- 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - events43/45打开正确最近会话；step12 input_text+step13 assert_state核对正文；step14（events51）点Send；steps16/17/18核对消息体/成功标识/可视发送状态。
  - 9/12 admitted、0 denied，非预算/timeout失败；kill step19成功（audit37→38），native returned audit41，官方之后评价0。
  - 初始化sms.py71-112最后插入params.number的非目标正文并按inbox检查；实际列表与目标入站符合，不存在本例选错most recent的证据。
  - 本例kill的原events#63显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅47.604秒（宿主事件时钟），小于300秒。
- **强推断**：
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**：
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- **责任层**：
  - 主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误
  - 次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）

**修复方案（未实施）**

- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**；`resources/skills/android-harness.md::Case Lifecycle (7-10)；drivers/android/_uiautomator2.py::kill_app (103-107)；src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)；android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
- **P1 / harness诊断owner**；`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics；src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`：仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**

- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**双方逐例核对**

已核对：正确发送，recency只业务识别风险非额外oracle谓词；sent AND foreground，actual killSMS，主强推断不唯一。

交叉核对：已核对。确发；recency仅业务识别风险、非额外oracle谓词。actual kill目标SMS已证，sent AND foreground中前台冲突为主强推断；评分row/activity缺失永久保留。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例082，起始第123行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/9`。
- [原公开goal](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：93-152,211-276`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/sms.py；lines：57-112`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：406-433`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/adb_utils.py；lines：1426-1446`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`

<a id="case-084"></a>
### 案例 084 — SimpleSmsSend

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Send a text message using Simple SMS Messenger to +16597910719 with message: Beauty is in the eye of the beholder.

**约束与冻结初始化**

- **recipient**：+16597910719
- **body**：Beauty is in the eye of the beholder.
- **actualSend**：必须已发送，不仅输入；保持指定Simple SMS Messenger app的官方前台要求。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：SimpleSMSSendSms.initialize_task关闭飞行模式、清sms与threads、读设备时间与sent；子类按目标插入收件/clipboard/contact。不会每题验证ROLE_SMS holder；setup配置不等于本题角色观测。

**官方判据**

- **判据**：SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.smsmessenger
- `agent-tap_on-18` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_send_message；accessibilityId：null；text：null；className：null；xpath：null
- `agent-assert_visible-20` passed；target：null；locator：resourceId：null；accessibilityId：null；text：+16597910719；className：null；xpath：null；optional：false
- `agent-assert_visible-21` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_message_body；accessibilityId：null；text：Beauty is in the eye of the beholder.；className：null；xpath：null；optional：false
- `agent-assert_visible-22` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_success；accessibilityId：null；text：null；className：null；xpath：null；optional：false
- `agent-kill_app-23` passed；app_id：com.simplemobiletools.smsmessenger
- **path**：artifacts/tools/000015-ui_snapshot.json
- **finding**：收件人输入+16597910719。
- **path**：artifacts/tools/000017-ui_snapshot.json
- **finding**：确认收件人后会话header同号码。
- **path**：artifacts/tools/000019-ui_snapshot.json
- **finding**：发送前composer含精确Beauty...正文。
- **path**：artifacts/tools/000021-ui_snapshot.json
- **finding**：发送后正文在thread_message_body，composer清空；kill prepare截图右侧气泡带checkmark。

原dispatch额度 11/12，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 共享sent provider应有+16597910719的Beauty is in the eye of the beholder.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。
- 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - events45输入号码→49确认→53输入正文→57点Send；native steps20-22依次验证号码/正文/thread_success成功。
  - 11/12 admitted、0 denied，无预算阻断；kill23成功（audit45→46），native return49；官方之后scalar0。
  - 无来源内容间接检索，本例公共goal直接给号码和正文，视觉轨迹逐项一致。
  - 本例kill的原events#67显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅34.374秒（宿主事件时钟），小于300秒。
- **强推断**：
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**：
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- **责任层**：
  - 主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误
  - 次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）

**修复方案（未实施）**

- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**；`resources/skills/android-harness.md::Case Lifecycle (7-10)；drivers/android/_uiautomator2.py::kill_app (103-107)；src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)；android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
- **P1 / harness诊断owner**；`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics；src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`：仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**

- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**双方逐例核对**

已核对：confirm/body/checkmark空composer支持已发；不写provider未提交已证，actual kill与前台冲突强推断。

交叉核对：已核对。confirm/body/checkmark/空composer支持已发，不写provider未提交已证；actual SMS kill前台冲突主强推断，评分row/activity缺失。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例084，起始第139行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/10`。
- [原公开goal](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：93-152,211-276`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/sms.py；lines：28-34`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：406-433`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/adb_utils.py；lines：1426-1446`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`

<a id="case-085"></a>
### 案例 085 — SimpleSmsSendClipboardContent

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Send a message to +15459061746 with the clipboard content in Simple SMS Messenger

**约束与冻结初始化**

- **recipient**：+15459061746
- **bodySource**：公开goal只给clipboard source，不能把oracle params.message告诉future agent；实际在消息框长按Paste得到I think, therefore I am.。
- **actualSend**：粘贴来源内容后必须点击Send，正文变成气泡且composer清空。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：SimpleSMSSendSms.initialize_task关闭飞行模式、清sms与threads、读设备时间与sent；子类按目标插入收件/clipboard/contact。不会每题验证ROLE_SMS holder；setup配置不等于本题角色观测。

**官方判据**

- **判据**：SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-launch_app-3` passed；app_id：com.simplemobiletools.smsmessenger
- `agent-tap_on-20` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_send_message；accessibilityId：null；text：null；className：null；xpath：null
- `agent-assert_visible-22` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_message_body；accessibilityId：null；text：I think, therefore I am.；className：null；xpath：null；optional：false
- `agent-assert_visible-23` passed；target：null；locator：resourceId：null；accessibilityId：null；text：+15459061746；className：null；xpath：null；optional：false
- `agent-assert_with_ai-24` passed；prompt：Verify the conversation with +15459061746 shows the outgoing sent message 'I think, therefore I am.' (the exact text pasted from the clipboard), not merely text remaining in the composer. Check the message bubble and sent status indicators.；optional：false
- `agent-kill_app-25` passed；app_id：com.simplemobiletools.smsmessenger
- **path**：artifacts/tools/000015-ui_snapshot.json
- **finding**：输入收件人+15459061746。
- **path**：artifacts/tools/000019-ui_snapshot.json
- **finding**：long press触发Paste菜单。
- **path**：artifacts/tools/000021-ui_snapshot.json
- **finding**：Paste后composer实见I think, therefore I am.。
- **path**：artifacts/tools/000023-ui_snapshot.json
- **finding**：Send后正文为消息体，composer为空；kill prepare截图有checkmark。

原dispatch额度 12/12，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 共享sent provider应有+15459061746的I think, therefore I am.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。
- 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - sms.py168-170初始化设置clipboard=params.message；native events53长按、57点击Paste，没有通过业务调用/私有参数取正文。
  - step20点Send（events61）；steps22/23/24核对发送正文/收件人/可视checkmark，非仅草稿。
  - 12/12 admitted且0 denied：本例exhausted=true只是恰好用完，发送及kill25均成功（audit49→50），native returned53；不能把exhausted标签当因果。
  - 本例kill的原events#73显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅50.869秒（宿主事件时钟），小于300秒。
- **强推断**：
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**：
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- **责任层**：
  - 主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误
  - 次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）

**修复方案（未实施）**

- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**；`resources/skills/android-harness.md::Case Lifecycle (7-10)；drivers/android/_uiautomator2.py::kill_app (103-107)；src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)；android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
- **P1 / harness诊断owner**；`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics；src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`：仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**

- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**双方逐例核对**

已核对：真实Paste并发，12/12无denied，宿主间隔<5min不代provider.date/device now；readback未知。

交叉核对：已核对。真实Paste并发送，12/12无denied，不把无剩余写等同拒绝；actual SMS kill前台冲突主强推断，评分row/activity缺失。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例085，起始第155行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/11`。
- [原公开goal](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：93-152,211-276`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/sms.py；lines：158-170`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：406-433`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/adb_utils.py；lines：1426-1446`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`

<a id="case-086"></a>
### 案例 086 — SimpleSmsSendReceivedAddress

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Text the address of the event to Gabriel Ibrahim that Oscar Mohamed just sent me in Simple SMS Messenger

**约束与冻结初始化**

- **recipient**：Gabriel Ibrahim；contact picker显示其+19696338338，不能把源号码+14379969633当收件人。
- **bodySource**：从Oscar Mohamed刚发来的事件地址取得；实际读源号码会话789 E Oak St, Phoenix AZ 85006并发送该原文。
- **contactEvidence**：起始Oscar+号码Add to contacts编辑表单不等于联系人已保存；后续源会话只号码，source attribution证据不全。
- **referenceTime**：
  - **referenceTime**：2023-10-15T15:34:00+00:00
  - **timezone**：UTC
- **privateParamsPolicy**：本调查离线读取用于解释官方初始化；修复与future agent不得接收私有参数/标准答案。
- **初始化机制**：SimpleSMSSendSms.initialize_task关闭飞行模式、清sms与threads、读设备时间与sent；子类按目标插入收件/clipboard/contact。不会每题验证ROLE_SMS holder；setup配置不等于本题角色观测。

**官方判据**

- **判据**：SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。

**原关键轨迹**

- `agent-launch_app-1` passed；app_id：null
- `agent-press_key-3` passed；key：Back
- `agent-launch_app-5` passed；app_id：com.simplemobiletools.smsmessenger
- `agent-swipe-6` passed；direction：up；start：null；end：null；reference_screen_size：null；duration：null
- `agent-input_text-9` passed；target：null；locator：resourceId：com.google.android.apps.nexuslauncher:id/input；accessibilityId：null；text：null；className：null；xpath：null；text：SMS；textType：literal
- `agent-tap_on-11` passed；target：SMS Messenger；locator：null
- `agent-tap_on-13` passed；target：+14379969633；locator：null
- `agent-press_key-15` passed；key：Back
- `agent-tap_on-17` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/conversations_fab；accessibilityId：null；text：null；className：null；xpath：null
- `agent-press_key-19` passed；key：Back
- `agent-input_text-23` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：null；className：null；xpath：null；text：789 E Oak St, Phoenix AZ 85006；textType：literal
- `agent-assert_state-24` passed；element：resourceId：com.simplemobiletools.smsmessenger:id/thread_type_message；accessibilityId：null；text：789 E Oak St, Phoenix AZ 85006；className：null；xpath：null；enabled：null；checked：null；selected：null；clickable：null；focused：null；text：null；optional：false
- `agent-tap_on-25` passed；target：null；locator：resourceId：com.simplemobiletools.smsmessenger:id/thread_send_message；accessibilityId：null；text：null；className：null；xpath：null
- `agent-assert_with_ai-27` passed；prompt：Verify Gabriel Ibrahim's conversation shows a sent outgoing message containing exactly '789 E Oak St, Phoenix AZ 85006', with a successful sent indicator and empty composer.；optional：false
- `agent-kill_app-28` passed；app_id：com.simplemobiletools.smsmessenger
- **path**：artifacts/tools/000002-ui_snapshot.json
- **finding**：初始Add to contacts表单：Oscar/Mohamed/+1 437-996-9633与Save仍可见；不能当存库证明。
- **path**：artifacts/tools/000014-ui_snapshot.json
- **finding**：唯一源号码+14379969633的列表预览为完整地址。
- **path**：artifacts/tools/000016-ui_snapshot.json
- **finding**：源会话收到789 E Oak St, Phoenix AZ 85006，header只有号码。
- **path**：artifacts/tools/000020-ui_snapshot.json
- **finding**：new conversation picker只有Gabriel Ibrahim与+19696338338，确认目标收件映射。
- **path**：artifacts/tools/000026-ui_snapshot.json
- **finding**：进入Gabriel会话；最终assert/kill prepare原UI及截图确认发出地址与checkmark/空composer。

原dispatch额度 14/18，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 共享sent provider应有+19696338338的789 E Oak St, Phoenix AZ 85006且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。
- 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**更底层机制、责任层、置信度与缺证据**

- **已证实**：
  - sms.py216-239先add_contact(name1,target_number)，再add_contact(name2,new_random_number)，随后向name2_number注入地址；contacts_utils39-70用INSERT intent+find_and_click SAVE但不读回联系人。
  - 首次ui_snapshot仍Oscar预填表单；step3 Back离开；不能声称Oscar持久化成功，也不能把初始化残留页面导致的姓名未显示一概归为agent遗漏。
  - events47打开源号码读地址；65选择Gabriel；71输入同地址；75点Send；step27 AI+原截图证明Gabriel正确已发送。
  - 14/18 admitted、0 denied，无预算阻断；kill28成功（audit55→56），native return59；主runner因Oscar来源未确认写inconclusive，但native verifier竟称success。official只按sent+foreground判定，不把runner此source attribution状态当0条件。
  - 本例kill的原events#81显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅40.386秒（宿主事件时钟），小于300秒。
- **强推断**：
  - 初始化保存Oscar的UI流程未完成或未持久化是强推断：初始还在Add to contacts表单，后续源会话只有号码且picker仅Gabriel；但也可能UI缓存/保存后仍停留，必须读回contacts才可区分。
  - native verifier“支持Oscar来源”的结论超出保存联系人证据；这不会自动解释official0，官方继承谓词不检验Oscar名称归属。
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**：
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- **责任层**：
  - 主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误
  - 次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）

**修复方案（未实施）**

- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**；`resources/skills/android-harness.md::Case Lifecycle (7-10)；drivers/android/_uiautomator2.py::kill_app (103-107)；src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)；android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。
- **P1 / harness诊断owner**；`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics；src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`：仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。
- **P1 / harness/AndroidWorld初始化owner**；`android_world.utils.contacts_utils.add_contact (39-70)；android_world.task_evals.single.sms.SimpleSmsSendReceivedAddress.initialize_task (216-239)`：初始化联系人后以既有list_contacts只读校验name→number落库并等待界面退出，再交付业务agent；失败应归初始化而不是要求future agent猜源联系人。不要修改SMS成功rubric或把私有源号码直接泄给future agent。
- **P1 / FSQ verifier owner**；`FSQ native verifier::evidence scope；FSQ main runner source-attribution evidence`：verifier区分“号码会话读取到地址且已发给Gabriel”与“Oscar联系人映射已证实”，不能根据初始化预填表单/goal断言联系人保存成功；保持unknown直到公开UI可确认。

**未来验证（全部未执行）**

- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**双方逐例核对**

已核对并实质修正：来源身份/联系人仅初始化及业务证据，不是独立扣分谓词；官方sent(number/body/window) AND foreground，Oscar DB未知、Gabriel发送正证与0因三层分离。

交叉核对：已核对、有实质oracle修正。来源身份保留属于业务/main-verifier分歧，不是独立评分分支；sent(number/body/window) AND foreground，actual SMS kill前台冲突主强推断。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例086，起始第171行。
- [harness独立完整源码/step/截图记录](harness-notes/calendar-sms.json)，JSON pointer `/cases/12`。
- [原公开goal](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sms_validators.py；lines：93-152,211-276`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/sms.py；lines：173-243`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/setup_device/apps.py；lines：406-433`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/env/adb_utils.py；lines：1426-1446`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py；lines：20-50`
- `path：/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/contacts_utils.py；lines：39-70,80-107`

<a id="case-087"></a>
### 案例 087 — SportsTrackerActivitiesCountForWeek

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> How many running activities did I do this week in the OpenTracks app? Assume the week starts from Monday. Express your answer as a single integer.

**约束与冻结初始化**

- How many running activities did I do this week in the OpenTracks app? Assume the week starts from Monday. Express your answer as a single integer.

**官方判据**

冻结IR proto2053-2107：本周为fixture参考2023-10-15所在Oct9..15，running相关活动COUNT，单整数；InformationRetrieval109-119/proto_utils147-179只判main原summary与期望，不把解释句当数值。

**原关键轨迹**

- launch1/3仅dispatch而snapshot2仍launcher；swipe4+tap6进入app，tap8/10首启两页说明，业务前耗6写。
- snapshot11已见活动表；swipe13由y1向下拉通知，assert15只确认Sun Oct15；Back16后tap18开更多菜单，press20/kill21被额度拒绝。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 没有完整running类别计数，main输出Unable...而非整数。
- 官方0来自无可匹配的整数答案，不是证实某个数字算错。

**更底层机制、责任层、置信度与缺证据**

- 已证实启动返回未验前台+首启导航成本；随后为确认日期拉系统通知、进非筛选菜单，未形成类别/本周覆盖证据表。缺少视图状态与目标查询进展的约束，预算耗尽是上述路径的结果，不是终极根因。
- **责任层**：FSQ adapter/Skill/检索规划
- **置信度**：强推断

**修复方案（未实施）**

- **P0 / FSQ**；`drivers/android/_uiautomator2.py:launch_app`：调用返回后验证前台或明确pending/failed，不能以app_id回显当启动成功
- **P1 / FSQ**；`Android Skill + agent retrieval planning`：一次读取可见日期锚后在app内按类别/日期搜集候选并记录覆盖，避免重复通知栏/无关菜单

**未来验证（全部未执行）**

- 离线回放既存view链验证无进展状态可识别；将来设备用公开UI设置混合类别和跨周活动，必须只计目标类别且完整覆盖。原M10不变，另加预算只能独立实验。

**双方逐例核对**

已核对：未建running周覆盖；首启/launch成本与非业务菜单无进展，未交整数。

**交叉核对：已核对（harness owner读完全文后逐例回执）。** 未建立类别/周覆盖、菜单无进展及原动作/预算链双方一致；启动底层原因仍未知，不由此推定设备故障。主summary为Unable，原0不是已提交整数算错。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例087，起始第36行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/0`。
- [原公开goal](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-087-20261110T213955Z-895101/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-087-20261110T213955Z-895101/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/087-SportsTrackerActivitiesCountForWeek/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:2053-2107`
- `frozen information_retrieval.py:82-119`
- `frozen proto_utils.py:147-179`

<a id="case-090"></a>
### 案例 090 — SportsTrackerLongestDistanceActivity

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What was the longest distance covered in a mountain biking activity in the OpenTracks app this week? Assume the week starts from Monday. Express your answer as a single number in meters rounded to the nearest integer.

**约束与冻结初始化**

- What was the longest distance covered in a mountain biking activity in the OpenTracks app this week? Assume the week starts from Monday. Express your answer as a single number in meters rounded to the nearest integer.

**官方判据**

冻结proto2487-2538：Oct9..15 mountain biking最大距离，单位米；NUMBER_MATCH绝对差<10m（不是<=10）。

**原关键轨迹**

- launch1/3未带来前台；drawer/说明tap6/8/10后进入列表。
- swipe12 y1拉通知，Back14回表；tap16进入Wave Exploration Oct15详情8.09mi，未证明该项是mountain biking；Back18后tap20/kill21额度拒绝。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 未完成类别筛选和最大值比较，未给米数；Miles显示需注意换算/显示精度但不是本次已计算错误的证据。
- main是Unable maximum说明句，官方0。

**更底层机制、责任层、置信度与缺证据**

- 初始启动/首启成本之外，选择首项详情代替类别过滤与候选最大值比较，消费剩余额度；无query进度/候选类别证明与日期锚复用。
- **责任层**：FSQ adapter/Skill/检索规划
- **置信度**：强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill retrieval plan`：先类别+周边界筛选再比较，保存单位/候选来源，不以列表首项代替类别证据
- **P0 / FSQ**；`UiAutomator2AndroidDriver.launch_app`：启动结果带前台观测，避免重复无效launch

**未来验证（全部未执行）**

- 将来构造不同类别首项距离更大且跨周的公开UI数据，断言不选错类；公里/英里值换米须满足原<10m容差，不改rubric。

**双方逐例核对**

已核对：mountain-biking候选MAX未建；英制精度只是未解决约束，未发生算术/round错误。

**交叉核对：已核对（逐例最终回执）。** mountain-biking类别/MAX候选未建立、计算未执行双方一致；8.09mi不是已提交答案。英制显示精度是未来约束，不是本轮既成算错，原0保留。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例090，起始第73行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/1`。
- [原公开goal](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-090-20261110T215043Z-1f10e6/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-090-20261110T215043Z-1f10e6/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/090-SportsTrackerLongestDistanceActivity/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:2487-2538`
- `frozen proto_utils.py:168-179`

<a id="case-091"></a>
### 案例 091 — SportsTrackerTotalDistanceForCategoryOverInterval

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What was the total distance covered for kayaking activities in the OpenTracks app from October 09 2023 to October 10 2023? Express your answer as a single number in meters rounded to the nearest integer.

**约束与冻结初始化**

- What was the total distance covered for kayaking activities in the OpenTracks app from October 09 2023 to October 10 2023? Express your answer as a single number in meters rounded to the nearest integer.

**官方判据**

冻结proto2931-2987：kayaking且Oct9至Oct10闭区间距离SUM，米，绝对差<10m。

**原关键轨迹**

- search12/input14 kayaking/Enter15后已有按类别结果。
- tap17和21重复打开Oct14 Waterway Paddle，均超目标区间；tap25/29才读Oct9两条详情（1.24mi/2.80mi）。
- Back33误退launcher，tap35 target-not-found，tap37重入；tap39/kill40被原M20拒绝。

原dispatch额度 20/20，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 没有完成日期内集合及精度一致求和，main是Unable exact total。
- 官方0来自非数值主答案，不代表已给错误的sum。

**更底层机制、责任层、置信度与缺证据**

- 已执行类别搜索但缺失筛选后按日期排除与已访问身份记忆；重复选超区间首项、过度Back导致离开业务页，丢失可用预算。
- **责任层**：FSQ检索状态/Skill/adapter
- **置信度**：强推断

**修复方案（未实施）**

- **P1 / FSQ**；`agent检索状态 + Android Skill`：记录(category,date,identity,value,unit,visited)，排除Oct14并避免重复首项；Back必须验证目标列表且不退出app

**未来验证（全部未执行）**

- 离线利用原steps17/21识别同identity重复；将来设备数据包含区间外同类首项、两条同日不同值，保证每目标唯一计一次并保留原M20。

**双方逐例核对**

已核对：确有kayaking搜索；重复Oct14、Back退出与stale target；SUM/米精度未执行。

**交叉核对：已核对（逐例最终回执）。** 确有kayaking搜索、重复打开Oct14、Back退出后stale target双方一致；SUM/精度计算未执行，不虚构错误米答案。精确米值如何经合法UI获得仍未知。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例091，起始第109行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/2`。
- [原公开goal](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-091-20261110T215344Z-372744/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-091-20261110T215344Z-372744/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:2931-2987`
- `frozen proto_utils.py:168-179`

<a id="case-092"></a>
### 案例 092 — SportsTrackerTotalDurationForCategoryThisWeek

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What was the total duration of running activities in the OpenTracks app this week? Assume the week starts from Monday. Express your answer in minutes as a single integer.

**约束与冻结初始化**

- What was the total duration of running activities in the OpenTracks app this week? Assume the week starts from Monday. Express your answer in minutes as a single integer.

**官方判据**

冻结proto2708-2762：Oct9..15 running活动duration求和，分钟整数。

**原关键轨迹**

- 两次launch仍launcher，drawer/首启tap6/8/10后见列表。
- swipe12 y0拉通知，Back14；tap16只读Oct14一条30:00 running详情，Back18；swipe20/kill21预算拒绝。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 未覆盖周内所有running活动，不能用单项30分钟充当总和；主答案Unable。
- 官方0是缺整数总和。

**更底层机制、责任层、置信度与缺证据**

- 重复启动与公共日期确认耗费后，未先类别筛选/累计跨记录，查询计划退化为查看单条详情；无完整性账本。
- **责任层**：FSQ adapter/Skill
- **置信度**：强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill/检索计划`：在同一周锚内逐目标累计分钟，区分30:00与h:mm:ss，非目标类跳过；保存已访问集
- **P0 / FSQ**；`driver.launch_app`：验证前台并显式首启状态

**未来验证（全部未执行）**

- 将来公开UI含两条running、干扰类型与跨周记录，断言只求目标集合，时长单位转换正确。

**双方逐例核对**

已核对：只读一条30分钟，非总和、非30秒；moving/total同值，不能说已选错字段。

**交叉核对：已核对（逐例最终回执）。** 一条30min不能充全周总和、swipe20被拒双方一致；不能写30秒、已算错分钟或已选错moving字段。原0保留。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例092，起始第147行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/3`。
- [原公开goal](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-092-20261110T215815Z-5c3801/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-092-20261110T215815Z-5c3801/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/092-SportsTrackerTotalDurationForCategoryThisWeek/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:2708-2762`

<a id="case-097"></a>
### 案例 097 — SystemBrightnessMax

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Turn brightness to the max value.

**约束与冻结初始化**

- Turn brightness to the max value.

**官方判据**

SystemBrightnessMax init为min，最终官方is_successful必须settings system screen_brightness整型255（system.py29-52/104-112）。

**原关键轨迹**

- snapshot6 UI range文本0.0；swipe7 x90,y420→1037,y420；snapshot8=65469.0，未到UI上限65535。
- assert_with_ai9置信0.99视觉宣称最右端，原图显示近满；kill10之后官方0。

原dispatch额度 5/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 视觉近满≠精确max；未记录评分瞬间原始亮度整数，不猜是253/254。
- 原official0只能证明非255，AI断言未建立数值端点。

**更底层机制、责任层、置信度与缺证据**

- 坐标拖动停在端点以内，且用像素AI判断替代可见SeekBar数值range比较；观察已有65469并未触发语义纠正。
- **责任层**：FSQ Skill/数值控件操作与验证
- **置信度**：已证实UI未达数值上限；其与official非255的具体映射为强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill + UiAutomator2AndroidDriver slider动作/断言`：基于bounds及可观察range min/max判端点，保留已经达标状态；验证数值最大而非笼统图像接近满，不用私有settings oracle给agent

**未来验证（全部未执行）**

- 离线用range0/65469/65535与近满图边界防假阳性；将来设备比较公开UI端点操作与独立官方settings值，保留exact255 rubric和原M10。

**双方逐例核对**

已核对：0→65469近满AI通过不等exact255；系统实值/控件映射未存，不猜254。

交叉核对：已核对。0→65469、AI近满通过与exact255不等价，visual goal收窄；系统实读整数/SeekBar映射未留，永久unknown，不补probe不猜254。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例097，起始第187行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/4`。
- [原公开goal](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-097-20261110T220905Z-8c0e3f/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-097-20261110T220905Z-8c0e3f/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/097-SystemBrightnessMax/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen single/system.py:29-52,104-112`

<a id="case-098"></a>
### 案例 098 — SystemBrightnessMaxVerify

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Turn brightness to the max value.

**约束与冻结初始化**

- Turn brightness to the max value.

**官方判据**

Verify变体init已set max；相同goal无须改变满足的状态（system.py74-86），最终exact255。

**原关键轨迹**

- snapshot6=65535.0已到数值上限；仍swipe7 x540→1035,y420；snapshot8降为65338.0。
- assert_with_ai9又以0.99判视觉最大；官方0。

原dispatch额度 5/10，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 已满足预置被不必要的近似拖动破坏；不是预算不够（admitted5/10、无拒绝）。
- 被动保持预置应满足，当前拖动后的精度与oracle不符。

**更底层机制、责任层、置信度与缺证据**

- 缺少幂等前置检查：模型套用“拖到右侧”而没有以可见range已max作停止条件，AI视觉验证掩盖数值倒退。
- **责任层**：FSQ Skill/控件幂等性
- **置信度**：已证实预置值及数值下降；未存系统整数映射为强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill + slider verification`：行动前比较range.current=max则不写；行动后禁止由满值降低仍声称成功

**未来验证（全部未执行）**

- 未来有已max和未max两夹具，对已max断言零亮度变更，对近max不能通过精确max声明；不得把官方255改为宽容。

**双方逐例核对**

已核对：65535→65338不必要倒退；main success/verifier inconclusive区分，幂等不写与数值range验证，不强迫verifier pass。

交叉核对：已核对。初始max+65535→65338是不必要倒退；main success/verifier inconclusive保留。幂等不写+range数值验证，不强迫verifier pass；系统实值永久unknown。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例098，起始第205行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/5`。
- [原公开goal](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-098-20261110T221109Z-190872/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-098-20261110T221109Z-190872/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/098-SystemBrightnessMaxVerify/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen single/system.py:74-86,41-52`

<a id="case-101"></a>
### 案例 101 — SystemCopyToClipboard

**原身份：invalid_evaluator / officialReward=None；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Copy the following text to the clipboard: Tracking #: 5K672F4C

**约束与冻结初始化**

- Copy the following text to the clipboard: Tracking #: 5K672F4C

**官方判据**

官方先reset剪贴板，再get_clipboard_contents读取并fuzzy比较；本次single official call在_extract_clipper_output因parsed data None抛RuntimeError，reward null invalid_evaluator。

**原关键轨迹**

- launch1目标Clipper但snapshot2仍launcher；转用launcher搜索框输入精确目标；longpress7后菜单Copy可见，tap9/11操作后clear13清空框。
- paste验证前longpress17仅出现Autofill；tap19 Paste targetnotfound，后续longpress21及24无成功paste，24/kill25预算拒绝。
- 主runner诚实inconclusive；原diag RuntimeError缺broadcast payload，未存raw output/foreground/permission快照。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 业务侧没证明剪贴板目标确复制且能paste；评分侧是采集异常，不能给0、更不能从错误文案断定权限缺失。
- 缺payload使官方无分；paste失败是另一个已证业务未验证点。

**更底层机制、责任层、置信度与缺证据**

- 双层：FSQ在脆弱launcher输入域选择/复制后未通过paste闭环；fixture/evaluator依赖Clipper前台/权限/广播data，但具体前提哪项失败无法确认，可能空/不可解析payload或前台时序，不能硬归模型。
- **责任层**：FSQ Skill + fixture/evaluator（具体环境子因未知）
- **置信度**：业务未验证/官方异常已证实；具体Clipper前提无法确认

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill text-selection flow`：选择稳定公开可编辑场景，按整串选择/Copy后在独立空字段paste核对，失败不宣称成功；不读取oracle expected state
- **P0 / Harness/fixture**；`harness qualification/evaluator diagnostics`：将来资格前验证Clipper采集前提，单次official调用时私有记录raw broadcast/status/前台/role，不重试补分

**未来验证（全部未执行）**

- 只提出将来授权设备区分：启动前台/权限各已知状态及空clipboard时保留同次广播原文，定位None来源；单次失败仍null/invalid，绝不重复评分。

**双方逐例核对**

已核对：Copy dispatch不等已读clipboard，Paste失败不等复制失败；官方None payload异常独立invalid/null，权限/前台/解析候选未知。

**交叉核对：已核对（逐例回执）。Copy dispatch成功不证明clipboard内容、Paste失败不证明复制失败；10/10恢复拒绝属于业务验证链。官方RuntimeError/Clipper None payload独立保留invalid_evaluator/null；权限、前台、解析等候选仍未知，绝不改0。**

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/core-contract-browser.md)，案例101，起始第165行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/6`。
- [原公开goal](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen single/system.py:297-333`
- `frozen env/adb_utils.py:1119-1173`

<a id="case-106"></a>
### 案例 106 — TasksCompletedTasksForDate

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Which tasks have I completed for October 16 2023 in Tasks app? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- Which tasks have I completed for October 16 2023 in Tasks app? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**官方判据**

proto1526-1574三relevant任务due Oct16，completed_date Oct10；oracle取其title，不是完成timestamp在Oct16。goal completed for有自然语义歧义。

**原关键轨迹**

- launch1/3后launcher，drawer4/tap6入Tasks。
- 菜单tap8/Back10；drawer12/Back14；再次menu15/Back17；快照显示Show completed已勾（主runner引000023），没有完成目标日期全列表检索。
- tap19/kill20预算拒绝；主答案Unable titles而非逗号标题。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 没有给标题集；不能把for-date改解为completion timestamp来辩称评分错误。
- 0来自未返回标题答案；具体匹配标题全集原库未保留，不编造。

**更底层机制、责任层、置信度与缺证据**

- 导航在已启用Show completed及drawer间反复，没有消费已有状态或有效滚动候选；另fixture due/completed_date不一致使goal词义有歧义，作为测量限制而非唯一失败因。
- **责任层**：FSQ检索状态/Skill；task fixture表述歧义
- **置信度**：强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill task queries`：记住checked过滤状态，按公开日期证据维护候选，不重复开同菜单
- **P2 / Benchmark maintainer**；`Tasks IR fixture文档/上游任务规范`：把dueDate与completionDate语义差异透明记录；若上游澄清prompt属于单独新fixture版本，不改本次rubric或教agent硬编码oracle解释

**未来验证（全部未执行）**

- 未来以dueDate≠completedDate的公开夹具检验自然语言契约；离线同菜单checked状态重复不应再分配导航动作；本次不重放。

**双方逐例核对**

已核对，有语义保留：dueOct16/completedOct10，for不等completiontimestamp；未实际执行错过滤，Showcompleted只是visibility。

**交叉核对：已核对、有保留（逐例最终回执）。** frozen tasks.textproto:1526–1574的relevant dueOct16/completedOct10，oracle不是completiontimestamp=Oct16；Show completed只是visibility。歧义未实际形成一次错误过滤，双方不把潜在语义风险当已发生算法bug。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例106，起始第182行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/7`。
- [原公开goal](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-106-20261110T223129Z-6dcd59/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-106-20261110T223129Z-6dcd59/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/106-TasksCompletedTasksForDate/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:1526-1574`

<a id="case-107"></a>
### 案例 107 — TasksDueNextWeek

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> How many tasks do I have due next week in Tasks app? Assume the week starts from Monday. Express your answer as a single integer.

**约束与冻结初始化**

- How many tasks do I have due next week in Tasks app? Assume the week starts from Monday. Express your answer as a single integer.

**官方判据**

proto1397-1465 COUNT六relevant任务due Oct16..22；无显式completed过滤，背景同区间都排除。

**原关键轨迹**

- launch1/3→launcher/drawer4/tap6后；swipe8 y30、12 y0、16 y0三次同类下拉均进通知栏，分别Back10/14/18回列表；swipe20/kill21额度拒绝。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 从未建立下周列表完整覆盖，主答案Unable count；不是0个任务。
- 无数值答案导致0。

**更底层机制、责任层、置信度与缺证据**

- 为获取日期有意打开通知栏，第一次已读Sun Oct15后仍重复两次同一渠道，未保存已知月日weekday/仍缺year的有限状态，故无新信息又未转向任务覆盖。不能误写为本意滚列表却坐标错误。
- **责任层**：FSQ检索状态/规划反馈
- **置信度**：重复同日通知栏及未返回整数已证实；为何未复用日期证据仅强推断

**修复方案（未实施）**

- **P1 / FSQ**；`Android Skill/agent progress feedback`：一次读取日期后保留来源与缺失字段；需要year时转向能补year的新公开UI，不重复同一通知栏；范围明确后再做列表覆盖

**未来验证（全部未执行）**

- 离线原8/12/16 notification链应识别重复无新日期；未来月日weekday已知而year未知的公开数据要求选新证据路径，原预算不变。

**双方逐例核对**

已核对并修正parent措辞：三次有意取日期通知栏，无新证据重复而非笼统坐标错误；year缺口未被同字段补齐。

**交叉核对：已核对（逐例最终回执）。** 三次通知栏重复取日期而不推进任务列表双方一致；这是证据复用/进展缺口，不是笼统坐标错误（手势本意即取日期）。frozen tasks.textproto:1397–1465的COUNT范围既有规则保留，不新增completed过滤。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例107，起始第219行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/8`。
- [原公开goal](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-107-20261110T223419Z-83207a/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-107-20261110T223419Z-83207a/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/107-TasksDueNextWeek/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:1397-1465`

<a id="case-108"></a>
### 案例 108 — TasksDueOnDate

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> What tasks do I have due October 24 2023 in Tasks app? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- What tasks do I have due October 24 2023 in Tasks app? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**官方判据**

proto1078-1123三个due Oct24相关title；逗号分隔，数量须一致且逐项fuzzy；不能返回Unable。

**原关键轨迹**

- snapshot7 XML已列Follow up on support tickets/Draft marketing email/Research market trends配Oct24。
- tap8开首项编辑、tap10开日期picker、assert12确认日期、Back13/15后出现discard，tap17才回列表；耗费可用写额度。
- swipe19后XML仍有Draft和Research；swipe21拒绝，assert22仅请求两个当前同屏标题且图像不支持Draft（出屏），不是明显AI误判。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 此前分步候选未累积为完整title/date表，最后只给Unable；不能让最后一张图的不可见抹掉先前有来源的候选。
- 0来自非标题答案及未闭合全集核对。

**更底层机制、责任层、置信度与缺证据**

- 只读查询转入可编辑日期对话框并产生discard路径；缺少跨页面证据记忆/稳定任务identity与查询完整性，错误把当前同屏双项断言当全集验证。
- **责任层**：FSQ检索策略/证据聚合
- **置信度**：实际迂回及输出差距已证实；策略机制强推断

**修复方案（未实施）**

- **P1 / FSQ**；`retrieval evidence ledger/Android Skill`：从公开列表保存每项title+date+sourceStep，必要再读详情，不为了读日期进入编辑；验证历史各项而非要求当前全部同屏

**未来验证（全部未执行）**

- 将来列表跨屏三项匹配，返回全标题且不打开可编辑datePicker；AI当前视图断言与跨step集合结论必须区分；仍用原长度+fuzzy rubric。

**双方逐例核对**

已核对：年份picker有价值但成本高，跨屏XML与当前帧裁切并存；非AI误判，缺完整集合不能补答。

**交叉核对：已核对（逐例最终回执）。** 年份picker核对有价值但成本高；跨屏XML完整字符串与当前frame标题裁切可并存，视觉assertion failed不写AI误判。frozen tasks.textproto:1078–1123/proto_utils:147–179的完整集合判据保留，不用私有第三项补summary。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例108，起始第256行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/9`。
- [原公开goal](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-108-20261110T223732Z-c3b1bc/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-108-20261110T223732Z-c3b1bc/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/108-TasksDueOnDate/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:1078-1123`
- `frozen proto_utils.py:147-179`

<a id="case-110"></a>
### 案例 110 — TasksHighPriorityTasksDueOnDate

**原身份：failed / officialReward=0.0；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Which tasks with high priority are due October 18 2023 in the Tasks app? Answer with the title only. If there are multiples titles, format your answer in a comma separated list.

**约束与冻结初始化**

- Which tasks with high priority are due October 18 2023 in the Tasks app? Answer with the title only. If there are multiples titles, format your answer in a comma separated list.

**官方判据**

proto1316-1348：due Oct18且importance0的一relevant标题；未设completed谓词。

**原关键轨迹**

- 原列表snapshot7有Marketing Campaign Launch/Wed；drawer8/选MyTasks10，Sort12→grouping14→By priority16，Back18到snapshot19 High priority三候选。
- 目标详情tap20与kill21被额度拒绝；主答案Unable titles。

原dispatch额度 10/10，denied=2，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- High priority分组确已建立，但相对Wed的绝对year/日期及全局覆盖尚未闭合；候选详情在剩余写额度为0时被拒。
- 未返回任何匹配标题，官方0。

**更底层机制、责任层、置信度与缺证据**

- drawer8再选同一My Tasks10先浪费2写；之后By priority四写确提供新的优先级证据，不应贬为无效。入口4+往返2+分组4用完10，未给绝对日期核验/覆盖留动作；是两谓词计划与预算反馈不足，而非high/medium识别或必须禁止分组。
- **责任层**：FSQ规划/Skill
- **置信度**：强推断

**修复方案（未实施）**

- **P1 / FSQ**；`preplan/Android Skill Tasks retrieval`：当前已在目标列表时不绕drawer；保留有效priority分组及row关联，提前规划公开时间锚仍缺year的核验与全局覆盖，分配同一原预算

**未来验证（全部未执行）**

- 未来公开UI高优先级三项不同dueDate，保留分组对优先级的有效证据，验证不做同列表drawer往返且为第二谓词留动作；原M10不变。

**双方逐例核对**

已核对并修正parent措辞：Bypriority有效，drawer往返和未为日期核验留动作才是问题，不禁sort。

**交叉核对：已核对（逐例最终回执）。** By priority有效，根在drawer往返及没给日期核验留动作，不应禁sort。frozen tasks.textproto:1316–1348的importance0+dueOct18既有规则保留；主summary Unable不是已提交错标题。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sports-tasks.md)，案例110，起始第294行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/10`。
- [原公开goal](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-110-20261110T224320Z-b7af07/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-110-20261110T224320Z-b7af07/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/110-TasksHighPriorityTasksDueOnDate/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen tasks.textproto:1316-1348`

<a id="case-113"></a>
### 案例 113 — TurnOnWifiAndOpenApp

**原身份：failed / officialReward=0.5；双方状态：双方已逐例核对；保留限定与未知。**

**公开goal（原文）**

> Turn on Wifi, then open the settings app

**约束与冻结初始化**

- Turn on Wifi, then open the settings app

**官方判据**

复合system.py25-49平均wifi与openApp两分；wifi_on∈{1,2}；OpenAppTaskEval484-499要求评分时前台Settings。

**原关键轨迹**

- snapshot6 Wi-Fi off，tap7开WiFi/断言8checked；tap14进Settings，snapshot15/断言16证实Settings首页。
- kill17 invoke resolved app_id=com.android.settings并成功；FSQ源kill_app103-107调用app_stop。官方0.5，原diag无分项/评分瞬间前台。

原dispatch额度 9/20，denied=0，deadlineExceeded=False；主runner/verifier原状态见对应原生结果，不以dispatch passed代表业务成功。

**期望—实际差距与直接失败**

- 业务验证时两目标看似完成，但native末尾关目标app与评分前台目标冲突；wifi1/app0是强推断非直接分项记录。
- partial0.5需保留，不能称整个Wifi动作失败。

**更底层机制、责任层、置信度与缺证据**

- 一般Skill无条件末尾kill破坏“打开并留下app”的用户末态，官方又在完整native含teardown后取前台；不是改变oracle/提前评分能修的单点。
- **责任层**：FSQ Skill生命周期与harness测量契约
- **置信度**：kill目标/前台业务证据已证实；哪半分保留为强推断

**修复方案（未实施）**

- **P0 / FSQ + Harness joint**；`Android Skill teardown + AndroidHarness生命周期契约`：主推荐仅用于未来版本：修改FSQ通用Android Skill/生命周期；close仅释放连接及owned临时资源，不无条件force-stop业务app，默认保持用户终态。harness仍在完整native返回后调用原官方评分一次，评分边界/rubric不变，不按case名特判kill。确需app_stop时，仅按公开任务/授权语义明确执行并保留证据。本轮frozen skill、原分数和产物不改，不移动原取样边界。

**未来验证（全部未执行）**

- 未来公开“打开设置”目标完成后完整native返回仍保持业务前台；仍执行一次after-full评分，分项私有记录供区分，正常资源close不等于force-stop业务app。

**双方逐例核对**

已核对：WiFi checked及Settings可见/actualSettings kill已证；wifi1/open0仅强推断，verification_goal遗漏WiFi独立缺陷。

交叉核对：已核对。Wifi checked与Settings可见两链、actual Settings kill双方一致；wifi1/app0仍强推断无分项。then顺序及verification_goal漏WiFi是独立计划质量缺陷。

**精确证据入口**

- [FSQ原生侧独立因果分析](fsq-case-notes/sms-system-navigation.md)，案例113，起始第223行。
- [harness独立完整源码/step/截图记录](harness-notes/parent.json)，JSON pointer `/cases/11`。
- [原公开goal](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-113-20261110T225201Z-521d36/sources/000-goal.txt) · [原native execution](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-113-20261110T225201Z-521d36/execution-result.json) · [原native result](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/fsq-native/worker/fsq-task-result.private.json)。
- [原初始化](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/task-initialization.json) · [原官方diagnostic](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/evaluator-diagnostics.json) · [action audit](../next-stage-plan/execution/run/episodes/113-TurnOnWifiAndOpenApp/raw-private/fsq-native/worker/native-action-audit.jsonl)。

官方源码定位：
- `frozen composite/system.py:25-49`
- `frozen single/system.py:131-144,484-499`

## 验收与保留未知

文档验收只检查集合/原身份一致、59份双方记录、必需分析字段、原report与episode结果字节及本调查文档链接。它不是设备、任务、评分或修复验证。实际离线输出见 [validation.json](validation.json)。

无法从既存材料补出的评分瞬间activity/forest、SMS provider行/ROLE_SMS/device now、101广播原文/授权前提、001实际文件路径、Markor/Recipe实际after DB/文件字节、059初始queue来源、036不同capture时刻及英制更高精度UI路径均按各例保留。不补probe、不回填分项、不以修辞关闭未知。