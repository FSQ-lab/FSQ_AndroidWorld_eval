# r4 harness侧逐案调查：early（15唯一案例）

范围：001, 002, 003, 004, 007, 008, 009, 010, 011, 013, 014, 015, 016, 017, 019。只读存量调查；未设备probe/ADB/Appium、未新模型调用、未重跑任务/评分/测试/构建/lint，未改代码或原产物。

## 证据与版本约定

- `BASE` = `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`。每例下列 `E`/`R` 相对BASE；表格中R/指该例native run。
- `AW` = `/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world`，来自candidate-final-manifest.json的identities.androidWorld.installed；直接读冻结installed，不用当前仓库替代，不import任务，不重建shuffle/随机参数，不新泛验hash。
- 写预算与输出契约直接读episode001冻结worker-site：`fsq_native.py::NativeDispatchBudget.dispatch:85–118`（setup/teardown与失败写都计费，before-forward拒绝）；`fsq_worker.py::select_main_answer:27–57`（单个successful exact main runner，parsed task_run_v1+合法summary；verifier不可冒充main）。
- FSQ lifecycle driver当前源码`drivers/android/_uiautomator2.py:94–107`经FSQ owner既存source_identity SHA匹配冻结包；本调查直接读该段：launch只app_start即passed，kill解析params.app_id或self.app_id后app_stop。目标包可核对，但不等于已观测评分瞬间屏幕。
- 所有修复仅方案；未来验证均未执行。不得改rubric、oracle泄漏答案、私加预算或同题重试凑分。
- 13官方passed/reward1必须保留；14官方failed/reward0。exact_main_summary不合约不使official分失效。14若与Markor专题重叠，父报告按唯一index合并，不新增计数。
- 本文harness独立侧已完成。001/007/008/009/010/011/015/016/017/019已逐节读FSQ分案并逐例反馈，最终FSQ回执仍pending；不自称双方已全部确认。

## 首要可证实因果

- 001录音已16秒保存、标题精确正确，但官方是完整磁盘路径存在检查；实际磁盘名未存，双.m4a只能候选。
- 002/003原生页面已Success!，不是业务未完成；评分还要求Chrome前台，随后app_stop是交接破坏的强推断。003静态“仍见X”验证目标与成功页替换网格冲突。
- 004五数9×10×9×5×5=20250正确，唯独从未点Submit；漏提交是独立已证直接失败。
- 007零秒Start是官方initialize清数据后的设计预置，不是precondition mismatch；Start再Pause多余。007/008/009官方读取当前DeskClock UI，不读内部持久秒表/timer实例；业务终态后app_stop，评分瞬间UI未存。
- 010/015输入正确但Save被before-forward预算拒；双launch/launcher导航等消耗与未预留commit是更前面的机制，不能只说预算太小。011缺的是Work选择，未Save正是要求。
- 013官方三行新增已完全通过，但大量证据切片后100-turn runner失败，无main summary；014未新增任何yes，局部no被当全文件结论，再重复search旧AI解释55次至100-turn。
- 016两个Public Transit已同屏，却转去无关filter探查至写满；017停在Oct2未达Oct1真重复，且有3条同名近似不能误删；019 Pet最初就在Streaming下一行，却遗忘后单向向下找，23/34未耗尽而提前结束。

## 001 — AudioRecorderRecordAudioWithFileName

**官方：failed，reward=0.0；native=success / verifier=success。**
- `E` = `next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName`
- `R` = `next-stage-plan/execution/run/episodes/001-AudioRecorderRecordAudioWithFileName/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-001-20261110T154725Z-70bee4`
- Goal原文（`R/sources/000-goal.txt`）：Record an audio clip and save it with name "presentation_fGwr.m4a" using Audio Recorder app.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

调用CreateFile初始化并清空AUDIORECORDER_DATA；本次冻结参数file_name=presentation_fGwr.m4a，text为空；参考时间2023-10-15 15:34 UTC。

二元评分：清空录音目录后，检查完整文件名 presentation_fGwr.m4a 是否存在于 /storage/emulated/0/Android/data/com.dimowner.audiorecorder/files/Music/records。不是检查列表显示标题，也不检查音频时长。 helper对find的完整路径集合做base_path/target精确相等；不去后缀、不fuzzy、不接受其他目录或子目录中的同名文件。

- `AW/task_evals/single/audio_recorder.py:95-123` — `AudioRecorderRecordAudioWithFileName.initialize_task/is_successful`。
- `AW/env/device_constants.py:29` — `AUDIORECORDER_DATA`。
- `AW/utils/file_utils.py:228-258` — `check_file_or_folder_exists`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The app visibly lists the newly saved audio clip as "presentation_fGwr.m4a".

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-2` / 3 | passed；首次launch成功后观察仍为launcher；后续再次launch、应用抽屉和图标导航增加写操作。 | `R/artifacts/tools/000002-ui_snapshot.json` |
| `agent-input_text-13` / 25 | passed；New name对话框原值Record-1；输入完整字符串presentation_fGwr.m4a。截图无可据以证明实际后缀的独立文件路径字段。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-13-finalize-after-action-1-adc4f56acd17.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-13-finalize-after-action-1-5b59be9892a0.png` |
| `agent-tap_on-14` / 27 | passed；Save成功后UI标题presentation_fGwr.m4a，信息0.19 Mb, M4a,44.1kHz，duration=00:16。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-0bd84723b33a.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-361c0b809bac.png` |
| `agent-assert_visible-18` / 35 | passed；精确列表标题断言成功。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-18-prepare-before-action-1-8393e19065dd.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-18-prepare-before-action-1-8a659e938851.png` |
| `agent-kill_app-19` / 37 | passed；显式app_id=com.dimowner.audiorecorder的kill成功；文件型oracle不要求前台，不能把这个kill单独当本例原因。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-19-prepare-before-action-1-5db531c93687.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-19-prepare-before-action-1-0353beac697c.png` |

**预期 vs 实际：** 需要磁盘上完整basename存在；实际只证明应用内显示标题和录音已保存，official=0说明oracle精确路径检查未通过。native=success，mainAnswer valid，与官方文件契约有证据粒度差。
**直接失败点：** 没有获得官方目标路径下完整文件名存在的证据；官方检查返回0。

### 根因分层与证据边界

**已证实**
- 录音16秒已保存且列表精确显示presentation_fGwr.m4a（step14/18截图与XML）。
- native verification_goal只要求可见列表标题，弱于完整文件名/目录的官方目标。
- 冻结helper L244-258在目录不存在时0，否则find后精确比较base/target；没有后缀normalize。

**强推断**
- 强推断：UI显示名与实际落盘文件名/目录的映射没有纳入验证，形成误报success；不是录音没启动。

**无法确认与缺证据**
- 未存录音目录清单或文件属性；无法确认实际是presentation_fGwr.m4a.m4a、存到了另一目录、或其他命名映射。重复.m4a仅候选，绝不可写成已证实。

**备选及区分**
- 自动追加扩展名
- 应用存储位置与oracle目录不同
- 实际文件创建/重命名未持久化；现有UI不能区分

责任层：FSQ规划/应用文件语义验证；应用UI标题与文件系统状态边界；harness证据不足。

### 预算与输出协议

- 写额度admitted=10/20，attempted=10，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=1320，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "success", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ planner verification_goal / Audio Recorder UI保存流程`**：保留用户完整文件名语义；在应用可见文件详情/导出文件名等合法UI中核对实际完整basename与保存位置，再决定是否需要只填stem。未查清前禁止全局去掉或重复追加.m4a。
- **P1 / harness / `harness evaluator diagnostics / AudioRecorderRecordAudioWithFileName.is_successful`**：在私有评分侧记录被检查目录、目标存在布尔和不含答案泄露的文件名差异证据；不把oracle目录/期待值回灌执行agent。

### 将来验证（未执行）

- 可离线：离线以存量应用文件命名实现/文件属性证据区分自动后缀与存储目录；若不可得明确未知。
- 需设备，独立样例：独立录音样例经UI保存带/不带扩展名后，私有评分侧核对完整basename；严格保持原maxActions，不同题重试凑分。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:46-63`。**已核对；实际落盘名未知**。
- 源码答复/分歧：官方是精确完整目标路径存在（audio_recorder L114-123、file_utils L228-258、device_constants L29），没有后缀normalize。UI完整title成功，实际文件路径/命名追加规则未存；.m4a.m4a只能候选。
- actual kill target：com.dimowner.audiorecorder。
- 剩余unknown：磁盘/导出文件名与实际目录未知，不用kill解释文件oracle。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- 已确认oracle精确完整路径，无后缀normalize；能否找到既存APK命名实现、导出文件名或目录证据区分suffix/目录候选？
- 当前缺真实磁盘名，双后缀仍未知，保持UI标题success不等价oracle存在。

## 002 — BrowserDraw

**官方：failed，reward=0.0；native=success / verifier=success。**
- `E` = `next-stage-plan/execution/run/episodes/002-BrowserDraw`
- `R` = `next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1`
- Goal原文（`R/sources/000-goal.txt`）：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then create a drawing using the three colors shown at the top and hit submit.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

browser_task_seed=461184702。任务需经Files打开task.html/Chrome；清Chrome导致first-run提示，真实step11/13/15/21处理并重开文件，不能当可删初始化噪声。

初始化清storage、清Chrome、按冻结seed写Downloads/task.html；Browser开启自动时间。页面逐像素确认三种目标颜色均存在后显示Success!；官方还要求评估时当前package=com.android.chrome且UI含精确Success!。

- `AW/task_evals/single/browser.py:49-85,98-109` — `BrowserTask.initialize_device_time/initialize_task/is_successful`。
- `AW/task_evals/single/browser.py:596-629` — `BrowserDraw.evaluateTask/showResult`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The drawing submitted in task.html uses all three colors displayed at the top of the task.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-assert_with_ai-23` / 45 | passed；读取顶部三目标色与palette位置。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-23-prepare-before-action-1-6c7242859a69.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-23-invoke-assert-with-ai-1-70203060df9f.png` |
| `agent-swipe-25` / 49 | passed；先选teal再画第一笔。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-swipe-25-finalize-after-action-1-7107d7a041f8.json`；截图 `R/artifacts/screenshots/screenshot-agent-swipe-25-finalize-after-action-1-67d8109ef789.png` |
| `agent-swipe-28` / 55 | passed；选择magenta画第二笔。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-swipe-28-finalize-after-action-1-2145b7d6a8d2.json`；截图 `R/artifacts/screenshots/screenshot-agent-swipe-28-finalize-after-action-1-eb6610acf118.png` |
| `agent-swipe-30` / 59 | passed；选择dark navy画第三笔。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-swipe-30-finalize-after-action-1-e9eee285a3a3.json`；截图 `R/artifacts/screenshots/screenshot-agent-swipe-30-finalize-after-action-1-ea56ddd0e0e8.png` |
| `agent-tap_on-32` / 63 | passed；点击Submit。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-32-finalize-after-action-1-c0e0b5ddb5cd.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-32-finalize-after-action-1-6dcca130c400.png` |
| `agent-assert_visible-34` / 67 | passed；result=Success!且截图三笔与目标色一致。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-34-prepare-before-action-1-e5619630b7f1.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-34-prepare-before-action-1-684b5c6e5664.png` |
| `agent-kill_app-35` / 69 | passed；默认kill_app成功，resolved app_id=Chrome；driver L102-107已核对self.app_id→app_stop。评分瞬间UI未存。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-35-prepare-before-action-1-8462f14fcff8.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-35-prepare-before-action-1-60e616ed4838.png` |

**预期 vs 实际：** 业务已经得到页面原生Success!，native/main均success；official在agent退出后才取前台UI而返回0。
**直接失败点：** 业务成功画面与评估边界之间有成功的kill_app，官方要求的前台Chrome/Success!不是持久化状态。

### 根因分层与证据边界

**已证实**
- step34原截图和XML显示Success!，不是AI只凭颜色猜成功。
- step35 teardown发生在native返回和official diagnostic.startedAtUnix之前；记录的resolved app_id为Chrome。
- 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。

**强推断**
- 强推断：native teardown移走Chrome前台，破坏BrowserTask.is_successful的前台条件；official0不是画色错误。

**无法确认与缺证据**
- 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。

**备选及区分**
- 除前台交接破坏外，若评分state/activity采样陈旧也可能造成0；缺评分瞬间快照不能区分，三色业务失败已由Success!排除。

责任层：FSQ生命周期/teardown与harness评分时序；不是rubric错误。

### 预算与输出协议

- 写额度admitted=19/20，attempted=19，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=1320，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "success", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P0 / FSQ+harness / `native Android teardown / BudgetedAndroidHarness.close与官方is_successful调用边界`**：将应用终态保持到官方评分完成；清理会话/服务与杀业务app分离，app kill留到评分之后的harness清理；不要通过修改BrowserTask rubric解决。

### 将来验证（未执行）

- 可离线：离线事件顺序断言：业务终态截图→官方评估→可改变前台的cleanup；不允许中间kill。
- 需设备，独立样例：新独立BrowserDraw样例保持Chrome前台，评分侧存activity与Success!快照；同样20写预算。

### FSQ待逐例回应的问题

- 目标Chrome及app_stop调用已核对；是否存在评分state/activity采样滞后，能否只保留为缺证备选而不凭0反推？
- 前台状态何时被teardown改变，能否只释放driver服务而保留业务UI直到评分？
- 默认目标与driver.app_stop已核对；请最终回执其与官方前台谓词的边界，保留评分瞬间activity/forest未记录这一unknown。

## 003 — BrowserMaze

**官方：failed，reward=0.0；native=failed / verifier=failed。**
- `E` = `next-stage-plan/execution/run/episodes/003-BrowserMaze`
- `R` = `next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c`
- Goal原文（`R/sources/000-goal.txt`）：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

清Chrome/下载目录并写maze HTML；经Files打开，完成Chrome first-run。Browser自动时钟不能用静态参考时间误判运行时钟。

seed=1364588068的maze；移动到goal后checkGoalReached立即用<h1>Success!</h1>替换整个document.body，网格和X按设计消失。官方只认Chrome前台+Success!。

- `AW/task_evals/single/browser.py:56-85,98-109` — `BrowserTask.initialize_task/is_successful`。
- `AW/task_evals/single/browser.py:278-321` — `BrowserMaze.moveCharacter/checkGoalReached`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The task.html grid in Chrome visibly shows X in the bottom-right cell.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-assert_with_ai-23` / 45 | failed；用于查看网格的AI断言失败；后续存在方向按钮动作。不可把其摘要替代实际终态。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-23-prepare-before-action-1-d3d3526729df.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-23-invoke-assert-with-ai-1-774ec504e350.png` |
| `agent-tap_on-24` / 47 | passed；Right。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-24-finalize-after-action-1-f11962d601b8.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-24-finalize-after-action-1-a1bbf2b05089.png` |
| `agent-tap_on-25` / 49 | passed；Down。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-25-finalize-after-action-1-9c956d34c5b8.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-25-finalize-after-action-1-02776a9ec14b.png` |
| `agent-tap_on-26` / 51 | passed；Down。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-26-finalize-after-action-1-3e32a68ba407.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-26-finalize-after-action-1-b432b158ca02.png` |
| `agent-tap_on-27` / 53 | passed；Down。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-27-finalize-after-action-1-ec6813d09cf2.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-27-finalize-after-action-1-8b8b3e4c67cb.png` |
| `agent-tap_on-28` / 55 | passed；Right。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-28-finalize-after-action-1-faec131cfb3e.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-28-finalize-after-action-1-20d537b25013.png` |
| `agent-tap_on-29` / 57 | passed；Right。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-29-finalize-after-action-1-7a1241c57bc3.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-29-finalize-after-action-1-f64944be952a.png` |
| `agent-assert_with_ai-31` / 61 | failed；原截图和XML：Maze Puzzle中为Success!，无X/网格；因prompt强制X仍可见而判失败。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-31-prepare-before-action-1-9657d927a8d2.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-31-invoke-assert-with-ai-1-ca3b431a67dc.png` |
| `agent-kill_app-32` / 63 | passed；默认kill成功，metadata resolved app_id=Chrome，随后才official0。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-32-prepare-before-action-1-f7570de51d22.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-32-prepare-before-action-1-8c2a4b02a1e3.png` |

**预期 vs 实际：** 原任务是到达目标，不是完成后仍展示X；真实业务成功终态Success!反被native静态视觉契约判失败，且又在评分前kill。
**直接失败点：** 两条独立差距：native verification_goal与网页成功状态机冲突；official评分时前台被teardown影响的强可能性。

### 根因分层与证据边界

**已证实**
- report.task.verification_goal要求grid visibly shows X in bottom-right，这与源码goal到达后删grid冲突。
- step31成功终态截图清楚写Success!；native failed不能视为没走到终点。
- 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。

**强推断**
- official0最可能由step32 kill与前台Chrome要求导致；不能把AI false当官方0的解释。

**无法确认与缺证据**
- 无评分瞬间activity/forest；最早step23视觉描述与方向动作前UI之间的矛盾需FSQ核对，勿声称初始就成功。

**备选及区分**
- 即便修好verifier的Success!解释，不修评分前kill仍会得0；这两项必须分别处理。

责任层：FSQ planner验收语义；FSQ/harness生命周期。

### 预算与输出协议

- 写额度admitted=18/20，attempted=18，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=1320，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ planner verification_goal / verifier`**：依据用户到达目标的语义接受页面合法终态，不添加“X必须永远可见”的静态附加要求；识别UI任务已切换成功页即停止方向操作。
- **P0 / FSQ+harness / `Android teardown→official BrowserTask.is_successful边界`**：保持Chrome成功页到官方评估后再清理；不改官方rubric。

### 将来验证（未执行）

- 可离线：离线用该HTML checkGoalReached与终态截图验证：Success!替代grid不得算失败；无oracle答案注入。
- 需设备，独立样例：独立maze实例到达后保留前台；官方评估成功后才kill。

### FSQ待逐例回应的问题

- planner为何把“navigate X to”收紧成终态必须看见X？
- 核对step23与24-29之间原始工具结果，不用verifier文字声称maze初始已完成。
- 默认目标与driver.app_stop已核对；请最终回执其与官方前台谓词的边界，保留评分瞬间activity/forest未记录这一unknown。

## 004 — BrowserMultiply

**官方：failed，reward=0.0；native=inconclusive / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/004-BrowserMultiply`
- `R` = `next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c`
- Goal原文（`R/sources/000-goal.txt`）：Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

browser_task_seed=3143940091；真实显示数列9（初始）、10、9、5、5，乘积20250。不import官方/不重新生成参数。

初始generateNumber生成第1个数；前4次click生成第2-5个数，第5次只显示form。checkAnswer必须由Submit调用，答案正确才出现Success!；官方Chrome前台+Success!。

- `AW/task_evals/single/browser.py:98-109` — `BrowserTask.is_successful`。
- `AW/task_evals/single/browser.py:407-439` — `BrowserMultiply.generateNumber/handleButtonClick/checkAnswer`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The answer field in task.html opened in Chrome visibly contains the product of the five numbers displayed after exactly five button clicks.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-20` / 39 | passed；number=9，尚未第一次task-button点击。 | `R/artifacts/tools/000021-ui_snapshot.json` |
| `agent-ui_snapshot-22` / 43 | passed；第1次后number=10。 | `R/artifacts/tools/000023-ui_snapshot.json` |
| `agent-ui_snapshot-24` / 47 | passed；第2次后number=9。 | `R/artifacts/tools/000025-ui_snapshot.json` |
| `agent-ui_snapshot-26` / 51 | passed；第3次后number=5。 | `R/artifacts/tools/000027-ui_snapshot.json` |
| `agent-ui_snapshot-28` / 55 | passed；第4次后number=5。 | `R/artifacts/tools/000029-ui_snapshot.json` |
| `agent-tap_on-29` / 57 | passed；第5次Click Me显示form，无新数字。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-29-finalize-after-action-1-5d589849c9f7.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-29-finalize-after-action-1-6702f7354849.png` |
| `agent-input_text-32` / 63 | passed；输入20250。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-32-finalize-after-action-1-97bdf492eb7a.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-32-finalize-after-action-1-e3c0c33ca24c.png` |
| `agent-assert_state-33` / 65 | failed；按text=20250断言找不到控件，属可访问性文本带hint差异。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-state-33-prepare-before-action-1-feacb044496a.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-state-33-prepare-before-action-1-eb2f79beba8f.png` |
| `agent-assert_state-35` / 69 | passed；使用text=20250, Enter the product成功；截图Submit仍在且无Success!。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-state-35-prepare-before-action-1-112d0c753891.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-state-35-prepare-before-action-1-a2e170c4caa2.png` |
| `agent-kill_app-36` / 71 | passed；kill Chrome，未有Submit动作。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-36-prepare-before-action-1-504df5db8c3e.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-36-prepare-before-action-1-ab718384072d.png` |

**预期 vs 实际：** 数列/算术和五次点击均正确，但只填answer没有Submit，因此checkAnswer未执行；native planner仅要求输入框有乘积，漏最终提交。
**直接失败点：** 未提交是官方0的充分业务原因；另有评分前kill。verifier称初始数不应算入5数与实际JS相反。

### 根因分层与证据边界

**已证实**
- 原始五张snapshot读到9,10,9,5,5；HTML明确初始生成+4次生成。
- step32-36无Submit，终态截图仍是填写表单而非Success!。

**强推断**
- 强推断：planner把完整网页交互缩成answer字段存在，导致未执行用户任务隐含的提交/结果确认；verifier又以错误的“每click后都应显示数”契约给inconclusive。

**无法确认与缺证据**
- 即使补Submit，仍需修前台生命周期才能评分；不声称未运行的Submit会得到实测reward1。

**备选及区分**
- 不是20250算错，不是初始9多算；官方源码直接排除这两个解释。

责任层：FSQ规划遗漏提交；FSQ verifier时间/计数状态机理解；teardown时序。

### 预算与输出协议

- 写额度admitted=17/22，attempted=17，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=1440，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ Browser form planner / verification_goal`**：将表单输入与提交后反馈作为完整动作，显式点击页面Submit并确认自然成功反馈；以真实UI阶段跟踪“初始数+四次新数”，不硬编码本题答案。
- **P1 / FSQ / `FSQ verifier evidence reasoning`**：允许首次可见初始数字计入显示序列；区分第5次切换form，不因字面“after five clicks”误拒有效序列。
- **P0 / FSQ+harness / `Android teardown边界`**：官方评分前保持Chrome前台。

### 将来验证（未执行）

- 可离线：离线依据JS状态机断言：5个显示值、5click，第5次不新增值；仅填框≠Success!。
- 需设备，独立样例：独立BrowserMultiply实例提交正确结果、保留成功UI至评分；22写预算不变。

### FSQ待逐例回应的问题

- planner为什么只写answer、不包含可见Submit？
- verifier能否以冻结HTML行为而非错误时间字面收紧解释数字序列？
- 底层kill默认目标与评分边界是否与2/3共因？

## 007 — ClockStopWatchPausedVerify

**官方：failed，reward=0.0；native=success / verifier=success。**
- `E` = `next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify`
- `R` = `next-stage-plan/execution/run/episodes/007-ClockStopWatchPausedVerify/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-007-20261110T160930Z-b1db96`
- Goal原文（`R/sources/000-goal.txt`）：Pause the stopwatch.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。无其他时间参数。

初始化清Clock数据，秒表本来为00/00且Start；官方要求当前activity含DeskClock、Start存在、Stopwatch标签数>=2，不要求非零elapsed，更不要求先启动。

- `AW/task_evals/single/clock.py:103-122` — `_ClockEval.initialize_task/tear_down`。
- `AW/task_evals/single/clock.py:43-63,177-208` — `_is_stopwatch_paused/ClockStopWatchPausedVerify.is_successful`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The stopwatch is paused with its elapsed time retained.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-9` / 17 | passed；首个秒表UI就是00秒/00百分秒、Start，已经满足暂停的可见业务语义。 | `R/artifacts/tools/000010-ui_snapshot.json` |
| `agent-tap_on-10` / 19 | passed；无必要地Start。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-c3def63dfe3c.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-4a44d6055dd6.png` |
| `agent-tap_on-12` / 23 | passed；Pause后8.46秒；这是秒/百分秒，不是8分46秒。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-514780c056c6.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-1fba2dea3cb2.png` |
| `agent-assert_visible-16` / 31 | passed；非零08文本与Start断言成功；截图暂停，原elapsed文本在部分snapshot中不可见但先前snapshot13有08/46。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-16-prepare-before-action-1-585ced36268a.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-16-prepare-before-action-1-9bafdd834218.png` |
| `agent-kill_app-17` / 33 | passed；显式kill com.google.android.deskclock成功，发生在官方评估前。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-17-prepare-before-action-1-507424d7b71f.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-17-prepare-before-action-1-4e5f331c7626.png` |

**预期 vs 实际：** 任务只要求暂停；native额外把“保留非零elapsed”当目标，先Start再Pause虽仍暂停，却多花2写。官方0不能归咎8.46秒，因为rubric不看elapsed；评分前kill破坏前台更吻合。
**直接失败点：** 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

### 根因分层与证据边界

**已证实**
- 初始化后的秒表本已Start/零；额外Start/Pause来自native计划而非官方前置需求。
- 最终Start+Stopwatch足以满足paused谓词的UI部分；step17显式目标Clock，随后official0。
- 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。
- FSQ分案初稿所称00/Start precondition mismatch不成立：官方initialize主动清数据且类doc明确零暂停预置。本调查反馈修正，待对方回执。

**强推断**
- 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。

**无法确认与缺证据**
- 评分瞬间activity/forest未记录；不能假定原本存在非零运行会话，亦不能把官方设计的零暂停当预检故障。

**备选及区分**
- 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。

责任层：FSQ生命周期与harness评估边界；FSQ额外任务约束/无效写操作。

### 预算与输出协议

- 写额度admitted=8/10，attempted=8，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=720，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "success", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ planner key_actions / verification_goal`**：对Pause这类保持型任务先检查当前是否已达标；不得凭空要求非零时间而先Start。
- **P0 / FSQ+harness / `FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`**：业务UI保持到评分完成，不在native验证后立刻kill Clock；会话资源关闭与业务app停止分开，由评分后cleanup统一处理。

### 将来验证（未执行）

- 可离线：离线零秒Start+两个Stopwatch标签应满足官方paused谓词；08/46是秒与百分秒。
- 需设备，独立样例：独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:90-109`。**存在实质分歧：初始零暂停不是precondition mismatch**。
- 源码答复/分歧：clock.py L103-118明确initialize清Clock数据；L177-184说明预置零暂停。00/Start是设计状态，不能推断初始化/预检异常，也不能要求原有运行会话身份。L194-208→L43-63只看当前DeskClock+Start+>=2Stopwatch。Start→Pause多余但不是官方0的充分原因。
- actual kill target：com.google.android.deskclock。
- 剩余unknown：缺评分瞬间activity/forest；前台被app_stop破坏仍强推断。秒表内部是否归零/暂停无证据也非评分读取对象。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- 请据官方clock.py L103-118及177-184修正“零Start是precondition mismatch/初始化异常”及要求保留原运行会话的结论。
- app_stop目标Clock已源码+receipt核对；剩余问题只在评分时前台/forest没有保存，能否列为强推断而不定案内部暂停/归零？

## 008 — ClockStopWatchRunning

**官方：failed，reward=0.0；native=success / verifier=success。**
- `E` = `next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning`
- `R` = `next-stage-plan/execution/run/episodes/008-ClockStopWatchRunning/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-008-20261110T161139Z-7dbd3e`
- Goal原文（`R/sources/000-goal.txt`）：Run the stopwatch.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。无其他时间参数。

初始化清Clock数据，起点零/Start；官方要求当前activity含DeskClock且content_description Pause与Lap同时出现。无需精确运行几秒。

- `AW/task_evals/single/clock.py:103-122` — `_ClockEval.initialize_task/tear_down`。
- `AW/task_evals/single/clock.py:25-40,215-245` — `_is_stopwatch_running/ClockStopWatchRunning.is_successful`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The stopwatch is running and its displayed elapsed time is advancing.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-9` / 17 | passed；初始00/00且Start。 | `R/artifacts/tools/000010-ui_snapshot.json` |
| `agent-tap_on-10` / 19 | passed；点击fab开始。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-1da1ec65e382.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-93e52162aa1f.png` |
| `agent-wait_ms-12` / 23 | passed；等待2秒供非写观察核对增长。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-wait-ms-12-finalize-after-action-1-9ded2207f28f.json`；截图 `R/artifacts/screenshots/screenshot-agent-wait-ms-12-finalize-after-action-1-87332336f060.png` |
| `agent-assert_visible-13` / 25 | passed；stopwatch_time_text数值>3断言通过；不是分钟字段。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-13-prepare-before-action-1-f379df18e030.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-13-prepare-before-action-1-952d0c5b4feb.png` |
| `agent-assert_visible-14` / 27 | passed；原XML显示18秒48百分秒、Pause和Lap，运行态已达成。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-14-prepare-before-action-1-4b408184bca6.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-14-prepare-before-action-1-18a40c70b802.png` |
| `agent-kill_app-15` / 29 | passed；空参数kill成功，metadata.harness_output.app_id=com.google.android.deskclock；具体底层driver源码L102-107已核对为app_stop。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-15-prepare-before-action-1-7f73ceb87fb3.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-15-prepare-before-action-1-80d5a1bf7423.png` |

**预期 vs 实际：** 真实UI有Pause/Lap且计时增加，native success；official0在kill后，非业务未启动或计时不前进。
**直接失败点：** 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

### 根因分层与证据边界

**已证实**
- step14 XML的Pause、Lap直接覆盖官方UI条件；18/48表示18.48秒。
- step15 resolved app_id记录Clock，默认入参没有显式app_id。
- 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。

**强推断**
- 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。

**无法确认与缺证据**
- 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。

**备选及区分**
- 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。

责任层：FSQ生命周期与harness评估边界。

### 预算与输出协议

- 写额度admitted=7/10，attempted=7，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=720，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "success", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P0 / FSQ+harness / `FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`**：业务UI保持到评分完成，不在native验证后立刻kill Clock；会话资源关闭与业务app停止分开，由评分后cleanup统一处理。

### 将来验证（未执行）

- 可离线：离线用step14 UI验证Pause+Lap条件，不引入精确秒数要求。
- 需设备，独立样例：独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:134-153`。**已核对；补足官方前台UI判据**。
- 源码答复/分歧：L231-245→L25-40读取当前DeskClock、Pause与Lap，不是内部service或elapsed持久值；业务运行态在kill前达成，不能推导app_stop必停或归零。
- actual kill target：com.google.android.deskclock。
- 剩余unknown：评分瞬间activity/forest未记录，foreground破坏为强推断。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- 是否把“释放会话”误实现成官方评估前kill业务app？
- 默认目标与driver.app_stop已核对；请最终回执其与官方前台谓词的边界，保留评分瞬间activity/forest未记录这一unknown。

## 009 — ClockTimerEntry

**官方：failed，reward=0.0；native=success / verifier=success。**
- `E` = `next-stage-plan/execution/run/episodes/009-ClockTimerEntry`
- `R` = `next-stage-plan/execution/run/episodes/009-ClockTimerEntry/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-009-20261110T161350Z-4835a4`
- Goal原文（`R/sources/000-goal.txt`）：Create a timer with 0 hours, 16 minutes, and 35 seconds. Do not start the timer.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

_ClockEval.initialize_task清app data；冻结referenceTime=2023-10-15T15:34:00+00:00。params hours=0, minutes=16, seconds=35。

官方要求DeskClock当前activity，UI text=00h 16m 35s或content-desc=0 hours, 16 minutes, 35 seconds；goal额外明确不得Start。不是16分35秒倒计时运行。

- `AW/task_evals/single/clock.py:103-122` — `_ClockEval.initialize_task/tear_down`。
- `AW/task_evals/single/clock.py:66-100,125-160` — `_is_timer_set/ClockTimerEntry.is_successful`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The timer displays a configured duration of 0 hours, 16 minutes, and 35 seconds and has not been started.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-tap_on-10` / 19 | passed；timer_setup_digit_1。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-edde7820f6e5.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-deee992bfde3.png` |
| `agent-tap_on-11` / 21 | passed；digit6。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-11-finalize-after-action-1-7bffa0844a3b.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-11-finalize-after-action-1-e2a0837d675c.png` |
| `agent-tap_on-12` / 23 | passed；digit3。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-2cb998f0f659.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-1fb881134606.png` |
| `agent-tap_on-13` / 25 | passed；digit5；得到00h16m35s。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-13-finalize-after-action-1-fa002e5f51ac.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-13-finalize-after-action-1-bc7577fc341f.png` |
| `agent-assert_with_ai-15` / 29 | passed；XML/text/content-desc完全对应0小时16分35秒，Start可用且无Start调用，AI成功。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-15-prepare-before-action-1-af9ab9abf211.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-15-invoke-assert-with-ai-1-b88839d412a3.png` |
| `agent-kill_app-16` / 31 | passed；空参数kill成功，metadata resolved app_id=Clock；第10个计费写（含setup/kill），无denied。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-16-prepare-before-action-1-870c638cf5db.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-16-prepare-before-action-1-49fae0b3f991.png` |

**预期 vs 实际：** 时间值与未启动约束都满足；official0不是数字顺序或秒/分钟错，而是终态未保留到评估。
**直接失败点：** 官方UI型oracle在agent退出后获取当前activity，前置成功终态后存在teardown kill。

### 根因分层与证据边界

**已证实**
- 原step15 XML有00h 16m 35s与完整content-desc，截图显示数字键盘+Start；无启动timer行为。
- 预算10/10是含kill的已用满，不是业务动作被拒；deadlineExceeded=false。
- 冻结绑定FSQ driver L102-107已读：默认app_id或self.app_id调用app_stop；结合本例invoke.harness_output明确实际目标。评分瞬间UI仍未记录。

**强推断**
- 强推断：评分前kill改变DeskClock前台，导致当前activity条件失败；应用内是否保留计时数据与此无关。

**无法确认与缺证据**
- 评分瞬间activity/forest未记录；底层目标解析与app_stop调用已核对，但实际终态采样缺失。

**备选及区分**
- 若kill无前台副作用，则需核对官方forest与native UI XML的采样/可访问性差异；不是修改官方谓词。

责任层：FSQ生命周期与harness评估边界。

### 预算与输出协议

- 写额度admitted=10/10，attempted=10，denied=0，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=720，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "success", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P0 / FSQ+harness / `FSQ Android teardown / BudgetedAndroidHarness.close → harness Clock.is_successful`**：业务UI保持到评分完成，不在native验证后立刻kill Clock；会话资源关闭与业务app停止分开，由评分后cleanup统一处理。

### 将来验证（未执行）

- 可离线：离线断言输入1635对应HH=0/MM=16/SS=35；最后一次计费kill，不把exhausted当denied。
- 需设备，独立样例：独立Clock样例：保存业务终态、评估时activity/forest、再cleanup三阶段；不得以改rubric或先运行oracle决定动作。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:178-197`。**已核对；补足纯UI entry判据**。
- 源码答复/分歧：L143-160→L66-100检查当前DeskClock+完整00h16m35s或content-desc，不要求内部timer实例；不得Start来自goal。10/10无denied。
- actual kill target：com.google.android.deskclock。
- 剩余unknown：无kill后UI/评分forest，不能编造按过Start/数字错。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- 本例10/10但无拒绝，不能归到budget导致输入失败，请交叉核对。
- 默认目标与driver.app_stop已核对；请最终回执其与官方前台谓词的边界，保留评分瞬间activity/forest未记录这一unknown。

## 010 — ContactsAddContact

**官方：failed，reward=0.0；native=failed / verifier=failed。**
- `E` = `next-stage-plan/execution/run/episodes/010-ContactsAddContact`
- `R` = `next-stage-plan/execution/run/episodes/010-ContactsAddContact/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-010-20261110T161609Z-0d7240`
- Goal原文（`R/sources/000-goal.txt`）：Create a new contact for Hugo Pereira. Their number is +13920741751.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

frozen name=Hugo Pereira，number=+13920741751；初UI No contacts yet，并有Contacts intro overlay。

清空联系人；评分从联系人provider列出并比对Contact(name=Hugo Pereira,cleaned number)。必须保存为实际联系人，draft显示文字不算；格式化+1 392-074-1751可清理为期望号码。

- `AW/task_evals/single/contacts.py:27-32` — `ContactsAddContact`。
- `AW/task_evals/common_validators/contacts_validators.py:38-55` — `AddContact.initialize_task/_has_contact/is_successful`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The saved contact details show Hugo Pereira with phone number +13920741751.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-2` / 3 | passed；第一次launch后仍launcher。 | `R/artifacts/tools/000002-ui_snapshot.json` |
| `agent-launch_app-3` / 5 | passed；第二次launch声明成功；后续仍需抽屉/icon。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-launch-app-3-finalize-after-action-1-8314372c08c8.json`；截图 `R/artifacts/screenshots/screenshot-agent-launch-app-3-finalize-after-action-1-4c5387653061.png` |
| `agent-press_key-8` / 15 | passed；Back退出再进Contacts，增加导航成本。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-8-finalize-after-action-1-e7d27501fff4.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-8-finalize-after-action-1-9f2f2964bfb0.png` |
| `agent-tap_on-10` / 19 | passed；dismiss og_tooltip_scrim_view。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-972a845171a4.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-1b9184e36992.png` |
| `agent-tap_on-12` / 23 | passed；开新联系人表单。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-b39a04aeab94.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-cef9e6f1e449.png` |
| `agent-input_text-14` / 27 | passed；First name Hugo。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-14-finalize-after-action-1-5bdcb1c021eb.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-14-finalize-after-action-1-7e29ea4f90a7.png` |
| `agent-input_text-15` / 29 | passed；Last name Pereira。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-15-finalize-after-action-1-cc08a33f9033.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-15-finalize-after-action-1-0c310d180ad3.png` |
| `agent-input_text-16` / 31 | passed；Phone +13920741751。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-16-finalize-after-action-1-539c76636f98.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-16-finalize-after-action-1-077186f993e9.png` |
| `agent-press_key-17` / 33 | passed；Back收键盘是第12写；保存尚未完成。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-17-finalize-after-action-1-238fed9241fb.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-17-finalize-after-action-1-25fc650370d1.png` |
| `agent-tap_on-19` / 37 | failed；Save在dispatch前被NativeActionBudgetExceeded拒；after XML仍Create contact且Save可见。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-19-finalize-after-action-1-ac43a61fd6f4.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-19-finalize-after-action-1-f12542ab31ea.png` |
| `agent-kill_app-20` / 38 | failed；teardown亦被拒。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-20-prepare-before-action-1-94b3bba51b69.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-20-prepare-before-action-1-1e76a246abb9.png` |

**预期 vs 实际：** 目标为持久化Contact；真实终态仍draft（Hugo/Pereira/+1 392-074-1751），Save拒，official0符合provider契约。
**直接失败点：** 第12写用在收键盘，关键第13写Save不可admit。

### 根因分层与证据边界

**已证实**
- audit seq1/5/7/11/15/17/19/23八写先用于启动/导航/overlay；seq27/29/31输入三字段，seq33 Back用尽12。
- audit seq37拒Save；无任何后续成功保存；不是号码格式错误。

**强推断**
- 强推断：launch调用成功但没有实际进入目标前台，导致双启动+抽屉+重进成本，再叠加对完成动作无预算预留；在小额度中消耗了commit所需写。

**无法确认与缺证据**
- 没有driver launch底层源码确认前，不能把前台未进入的原因直接定为SDK bug；可能生命周期/激活语义不符。

**备选及区分**
- 号码正确但尚未保存是充分失败原因，不需假设Contacts provider异常。

责任层：FSQ启动/导航计划与写预算分配；harness NativeDispatchBudget真实拒绝，非误报。

### 预算与输出协议

- 写额度admitted=12/12，attempted=14，denied=2，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=840，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ AndroidDriver.launch_app与planner启动策略`**：先核对实际前台并使用一次真正有效启动；重用现有观察，移除无效果重复launch/Back再进。
- **P1 / FSQ / `FSQ planner/runner remaining action budget`**：显式为Save保留动作并在budget不可恢复拒绝后终止无意义重试；仍计入现有12写，不能私增预算。

### 将来验证（未执行）

- 可离线：离线audit重放计数：Save前12写，拒绝不forward；删除无效启动/导航后应保留commit槽位，不以加预算替代。
- 需设备，独立样例：独立AddContact任务确认保存后详情，再官方provider查到姓名+clean number；12写不变。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:223-239`。**已核对**。
- 源码答复/分歧：contacts_validators.py L38-55清联系人后以provider持久Contact(name,clean number)比对；格式化正确，S19 Save未forward是充分失败点，前台不是评分条件。
- actual kill target：无实际kill（S20预算拒绝，配置目标Contacts不等于已stop）。
- 剩余unknown：launch未前台化底层原因仍未知；不把maxActions12自身当bug。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- launch两次为何都没带来预期目标前台？
- planner是否知道setup/kill也计费，是否可优先Save而不是用尽额度后才commit？

## 011 — ContactsNewContactDraft

**官方：failed，reward=0.0；native=inconclusive / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft`
- `R` = `next-stage-plan/execution/run/episodes/011-ContactsNewContactDraft/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-011-20261110T161839Z-806998`
- Goal原文（`R/sources/000-goal.txt`）：Go to the new contact screen and enter the following details: First Name: Grace, Last Name: Taylor, Phone: 799-802-1530, Phone Label: Work. Do NOT hit save.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

普通TaskEval恢复Contacts快照、设置参考时钟；无Draft特有清联系人逻辑。frozen Grace/Taylor/799-802-1530/Work；实际起点有intro overlay。

与AddContact相反，不Save；官方从forest含不可见节点读取hint=First name/Last name/Phone的字段、忽略号码非数字格式，电话label必须Work+Work Phone或位于phone下方的Work。仅键盘遮挡不是官方天然失败条件。

- `AW/task_evals/single/contacts.py:35-138,206-225` — `_contact_info_is_entered/_find_phone_label_element/ContactsNewContactDraft.is_successful`。
- `AW/task_evals/task_eval.py:116-157` — `TaskEval.initialize_task/_initialize_apps`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The unsaved new-contact form displays First Name Grace, Last Name Taylor, phone 799-802-1530, and phone label Work.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-2` / 3 | passed；launch后launcher。 | `R/artifacts/tools/000002-ui_snapshot.json` |
| `agent-tap_on-10` / 19 | passed；绕回Contacts后dismiss intro。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-6ba07fb1b5d2.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-7e746db3d2cf.png` |
| `agent-input_text-14` / 27 | passed；Grace。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-14-finalize-after-action-1-55138b83b4f1.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-14-finalize-after-action-1-c4a09e73a84b.png` |
| `agent-input_text-15` / 29 | passed；Taylor。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-15-finalize-after-action-1-16c518d2fcc7.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-15-finalize-after-action-1-d07ecec362f8.png` |
| `agent-press_key-16` / 31 | passed；先收键盘花一写。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-16-finalize-after-action-1-97983a07039c.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-16-finalize-after-action-1-cacf11fee1a9.png` |
| `agent-input_text-18` / 35 | passed；电话号码是第12写。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-18-finalize-after-action-1-6c4b754edd01.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-18-finalize-after-action-1-087391fdda4f.png` |
| `agent-press_key-19` / 37 | failed；Back被预算拒绝。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-19-finalize-after-action-1-f9c0246b0932.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-19-finalize-after-action-1-0b50fc6c1d3c.png` |
| `agent-press_key-20` / 38 | failed；不可恢复额度下重复Back再拒。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-20-finalize-after-action-1-bfe9fdcc21e4.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-20-finalize-after-action-1-52ce7b07acbc.png` |
| `agent-assert_with_ai-22` / 41 | failed；截图Grace/Taylor/799-802-1530可见，键盘遮label；原XML仍有Delete Mobile Phone，不是Work。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-22-prepare-before-action-1-3e640f70010d.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-22-invoke-assert-with-ai-1-3974f125bb56.png` |
| `agent-kill_app-23` / 43 | failed；kill亦被拒，draft保持，没误点Save。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-23-prepare-before-action-1-72b0f73dc47f.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-23-prepare-before-action-1-30c2ccf18bd8.png` |

**预期 vs 实际：** 三字段已填，Do NOT Save守住；Work没选择。official0不能仅解释为“键盘挡住”——其forest明确含不可见控件；真正缺失Work才是核心。
**直接失败点：** 没有选择Work的任何动作；label保持Mobile（delete_button_container desc=Delete Mobile Phone），budget用满后连收键盘都不可再做。

### 根因分层与证据边界

**已证实**
- step22原XML/Delete Mobile Phone，与先前Mobile字段一致；动作序列没有label dropdown/Work选择。
- 官方号码clean规则允许799-802-1530；未Save本身是本例要求而非缺陷。

**强推断**
- 强推断：导航/双launch耗掉setup写，再在填完phone前未预留Work选择所需动作，导致必填label未达标；verifier只说遮挡弱化了实际漏字段。

**无法确认与缺证据**
- 没有评分forest快照，不能逐节点证明oracle最终看到哪个Work元素；现有Mobile内容描述+零选择动作已强烈支持未改label。

**备选及区分**
- 即便hide keyboard也不会自动把Mobile变Work；不能只改可视断言、也不能通过Save修Draft。

责任层：FSQ预算规划与字段完整性；FSQ verifier可见截图与官方含不可见forest的边界。

### 预算与输出协议

- 写额度admitted=12/12，attempted=15，denied=3，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=840，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ ContactsDraft planner/字段清单`**：把phone_label作为独立字段完成，先消除无效启动/重进，为dropdown→Work和必要收键盘留额度；禁Save保持原任务。
- **P1 / FSQ / `FSQ verifier`**：区分“未看到”和“当前已选Mobile”，不要把遮挡当最终根因；使用已有合法UI语义/属性核对label。

### 将来验证（未执行）

- 可离线：离线断言Draft goal四字段且not-save；Mobile不能因为被遮挡而当Work，不按AddContact保存流程复用。
- 需设备，独立样例：独立Draft实例12写内完成Work并保持draft，评分侧保留forest检查label和hint。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/media-contacts-markor.md:268-285`。**已核对；补足invisible forest与Mobile语义**。
- 源码答复/分歧：contacts.py L206-225使用含不可见节点的forest，没有单独activity谓词；L35-138核对姓名hint/phone/Work标签。S22原XML Delete Mobile Phone，所有动作无Work选择；不能仅说键盘遮挡，未Save正是要求。
- actual kill target：无实际kill（S23预算拒绝）。
- 剩余unknown：官方forest未存；tooltip/Mobile本次可见但是否所有实例固定未知。
- 已逐例反馈Main；最终FSQ接受/修订回执pending。

### FSQ待逐例回应的问题

- 为什么field plan漏Work直到写预算耗尽？
- 可否交叉核对step22 Delete Mobile Phone；verifier“标签值无法确认”是否过于保守而漏报真实Mobile？

## 013 — ExpenseAddMultipleFromGallery

**官方：passed，reward=1.0；native=error / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery`
- `R` = `next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6`
- Goal原文（`R/sources/000-goal.txt`）：Add the expenses from expenses.jpg in Simple Gallery Pro to pro expense.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

目标Dress/43635分/Clothes(8)/Paid by card；Furnishing/35007分/Housing(4)/A need；Dental Care/3954分/Health Care(9)/A need。需认准expenses.jpg，不是old_expenses。

初始Expense DB仅10个noise；Gallery写expenses.jpg为3目标与10个old_expenses_*.jpg为noise。评分新增3行：name/note fuzzy、amount分整数与category id精确；after条数=before+3且原10行逐行不变。不是每字段独立分数，而是完整完整性布尔1/0。created/modified时间与新ID不与参考行比较。

- `AW/task_evals/single/expense.py:247-281` — `_ExpenseAddMultiple.validate_addition_integrity`。
- `AW/task_evals/common_validators/sqlite_validators.py:118-192,257-310` — `SQLiteApp/AddMultipleRows/validate_rows_addition_integrity`。
- `AW/task_evals/single/expense.py:379-408` — `ExpenseAddMultipleFromGallery.initialize_task`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：Pro Expense shows saved entries matching every expense and its corresponding details in expenses.jpg.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-tap_on-14` / 27 | passed；Gallery搜索expenses、打开文件名expenses.jpg。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-282d4addfce2.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-4ea00780d513.png` |
| `agent-assert_with_ai-15` / 29 | passed；原source截图与transcription完整3条，逐字段同冻结目标。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-15-prepare-before-action-1-3a1659246245.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-15-invoke-assert-with-ai-1-273d0ae75593.png` |
| `agent-tap_on-33` / 65 | passed；Dress表单填436.35、Clothes、Paid by card后SAVE。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-33-finalize-after-action-1-468d6c666e20.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-33-finalize-after-action-1-1fef2ea12e06.png` |
| `agent-tap_on-45` / 89 | passed；Furnishing填350.07、Housing、A need后SAVE。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-45-finalize-after-action-1-b2d1e2356e69.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-45-finalize-after-action-1-a77fd24482a1.png` |
| `agent-tap_on-58` / 115 | passed；Dental Care填39.54、Health Care、A need后SAVE。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-58-finalize-after-action-1-dbb60930c958.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-58-finalize-after-action-1-bff20a6e462a.png` |
| `agent-assert_with_ai-62` / 123 | passed；保存Dental Care详情确认name/amount/note，未展示category。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-62-prepare-before-action-1-de4eedebb3c9.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-62-invoke-assert-with-ai-1-253cff1fd2db.png` |
| `agent-assert_with_ai-66` / 131 | failed；Furnishing detail缺可见category导致AI fail，不是值错。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-66-prepare-before-action-1-f4a631e53c12.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-66-invoke-assert-with-ai-1-6fcd7c2fb330.png` |
| `agent-assert_with_ai-68` / 135 | passed；EDIT重开Furnishing，Housing选中；恢复该项验证。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-68-prepare-before-action-1-e5527e3b7825.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-68-invoke-assert-with-ai-1-08dfe83b3ba3.png` |
| `agent-assert_with_ai-74` / 147 | passed；EDIT重开Dress，Clothes选中；输入与note吻合。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-74-prepare-before-action-1-8414c8e1206c.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-74-invoke-assert-with-ai-1-ff90c94b43fb.png` |
| `agent-ui_snapshot-76` / 151 | passed；三条记录在recent列表；随后多次read_artifact_slice直至100 turn失败，无main结构化summary。 | `R/execution-result.json/steps/75` |

**预期 vs 实际：** officialReward=1.0/classification=passed必须保留：完整DB新增契约已由官方通过。独立native runner error/输出契约失败不倒扣官方分。verifier inconclusive仅因证据未对Dental category重开和无main summary。
**直接失败点：** 业务已完成但runner在出结构化task_run_v1前耗尽配置100 turns，error精确为Agent exceeded the configured turn limit.；不是Main runner did not succeed这个外层筛选reason，也不是写额度不足。

### 根因分层与证据边界

**已证实**
- source screenshot15三条与输入/保存动作完全对应；diagnostic官方返回1，无异常、无missing-row日志。
- events seq221 run_failed精确turn limit；nativeResult.steps[0]同错误，privateOutcome.result.nativeTarget.maxTurns=100。
- events tool_call_started计read_artifact_slice=23；末段seq209/211/217/218反复读已存在AI结果；write admission46/60，deadline=false、denied0。

**强推断**
- 强推断：大体积/嵌套证据取回和保存后重复核验未做收敛/终结，消费与写预算独立的turns，最终无结构化交付；不能将AI66不可见category当作原业务字段错误。

**无法确认与缺证据**
- 未在本调查重演FSQ max-turn控制；具体每个provider turn计数边界和artifact filter为何要求额外slice交FSQ核对。官方1已排除本次Dental实际保存category不匹配。

**备选及区分**
- 只放宽verifier到success不能修复main runner结构化输出缺失；只加turn预算不是根治。

责任层：FSQ runtime turn管理/证据取回与终结输出；harness严格main summary契约，官方reward独立。

### 预算与输出协议

- 写额度admitted=46/60，attempted=46，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=3720，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"reason": "Main runner did not succeed", "source": "agent_runtime.runner.tool_output.summary", "status": "failed"}`。
- `R/events.jsonl sequence=221`：Agent exceeded the configured turn limit.；真实runner错误同见nativeResult的agent_runtime.runner，而非仅外层Main runner did not succeed。
- tool_call_started计数（events，不是可能覆写的tool artifact数量）：`{"read_knowledge_index": 1, "launch_app": 1, "press_key": 12, "ui_snapshot": 24, "swipe": 4, "search_artifact": 2, "tap_on": 19, "input_text": 10, "assert_with_ai": 6, "read_artifact_slice": 23}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ runtime artifact filter/read_artifact_slice与agent loop`**：将AI verdict/explanation/引用以紧凑结构直接暴露，避免重复切片同一结果；追踪已覆盖字段证据，已有等价证据不再重复抓取，保留终结输出轮次。
- **P1 / FSQ / `FSQ main runner AgentFinalOutput终结路径`**：在现有100-turn范围内及时输出task_run_v1；检查与业务字段相关的真实缺证据，而非不停重读已完成的Dress/Furnishing断言。
- **P0 / harness / `harness fsq_worker.select_main_answer/统计展示`**：保持严格summary契约，但独立呈现official1、runner-error、verifier-inconclusive；不得用verifier替代main或把passed改失败。

### 将来验证（未执行）

- 可离线：离线events去重与计数：read_slice23、write46/60、seq221 turn-limit；exact main_summary失败但officialReward仍1。
- 需设备，独立样例：独立图库新增实例：不额外增加maxTurns/maxActions，保存后生成完整main summary，并在私有官方评分中确认3行/字段/无副作用。

### FSQ待逐例回应的问题

- maxTurns=100的扣账边界、read_slice23的证据压缩回路如何导致未终结？
- 已重开Furnishing/Dress后仍重复读取结果，能否传递紧凑AI verdict避免嵌套JSON检索？
- 请双侧保留passed=1与main summary契约失败并列，不以外层reason当根因。

## 014 — ExpenseAddMultipleFromMarkor

**官方：failed，reward=0.0；native=error / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor`
- `R` = `next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635`
- Goal原文（`R/sources/000-goal.txt`）：Go through the transactions in my_expenses.txt in Markor. Log only the rows whose reimbursable field is yes in the pro expense; do not log rows marked no. Copy each original note unchanged from the note field. The reimbursable field is selection metadata, not part of the note.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

期望yes两行Laundry $96.30/Clothes(8)/Urgent，Car Insurance $303.01/Transportation(7)/I may repeat this。与100 no行有同名/近似值风险，不按name猜。冻结源码说明应有102行，存量证据未保存原始设备文件字节/生成后的完整文档，不重建shuffle。

清Expense DB插入100 noise，并冻结2目标。Markor CSV pipe分隔，header含reimbursable；2个row_objects写yes、100个noise写no，shuffle后完整文件my_expenses.txt。只新增yes；name fuzzy，amount分整数/category精确，note严格相等（_free_form_fields仅name），条数before+2，原100行不变。selection metadata不得拼进note。

- `AW/task_evals/single/expense.py:247-281` — `_ExpenseAddMultiple.validate_addition_integrity`。
- `AW/task_evals/common_validators/sqlite_validators.py:118-192,257-310` — `SQLiteApp/AddMultipleRows/validate_rows_addition_integrity`。
- `AW/task_evals/single/expense.py:324-372` — `ExpenseAddMultipleFromMarkor._get_expenses_as_text/initialize_task`。
- `AW/task_evals/utils/user_data_generation.py:203-216` — `write_to_markor`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 日志：validate_rows_addition_integrity:168 Expected row %s not found in the 'after' state.

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：Pro Expense contains one newly saved expense for each source row marked reimbursable=yes, none for rows marked no, with transaction details matching the source and each note exactly equal to its original note field without added reimbursable metadata.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-tap_on-7` / 13 | passed；打开my_expenses.txt。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-7-finalize-after-action-1-6ceb02637f88.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-7-finalize-after-action-1-756976260d70.png` |
| `agent-tap_on-9` / 17 | passed；切preview。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-9-finalize-after-action-1-bbf66f4366a9.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-9-finalize-after-action-1-74de7e03e271.png` |
| `agent-assert_with_ai-11` / 21 | passed；只转录当前可见若干no行，自己说明还需scroll；UI XML长text压成前50字符，不能据XML搜yes判整文件没有。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-11-prepare-before-action-1-38e0b81e03e3.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-11-invoke-assert-with-ai-1-83a8fe57b797.png` |
| `agent-assert_with_ai-13` / 25 | passed；下滚后局部可见行全no，AI称apparent bottom；不是102行全覆盖证明。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-13-prepare-before-action-1-5ecd662ad6a0.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-13-invoke-assert-with-ai-1-2966ebe4aad8.png` |
| `agent-assert_with_ai-16` / 31 | passed；回顶部读取header至Gym Membership；局部均no。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-16-prepare-before-action-1-66797fe3ae1b.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-16-invoke-assert-with-ai-1-396ad72aee9a.png` |
| `agent-assert_with_ai-18` / 35 | passed；中间viewport均no；没有原始完整源文件计数或连续覆盖证明。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-with-ai-18-prepare-before-action-1-fdae17ec96d1.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-with-ai-18-invoke-assert-with-ai-1-8feb800b379b.png` |
| `agent-tap_on-23` / 45 | passed；切Pro Expense，未开新增表单。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-23-finalize-after-action-1-3dc00cea4d3d.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-23-finalize-after-action-1-f4e54abf6de4.png` |
| `agent-ui_snapshot-24` / 47 | passed；已有noise例如Reimbursements385.81/Doctor Visits75.54，并不能当本次新增no行。 | `R/artifacts/tools/000029-ui_snapshot.json` |
| `agent-ui_snapshot-42` / 83 | passed；最后仍重复取Pro Expense快照；整个轨迹无新增/save。 | `R/execution-result.json/steps/41` |

**预期 vs 实际：** 官方missing expected row日志与reward0符合两条yes均未新增；native错误也是100turn无main summary。但不能根据若干可见no断言初始化没有yes，不能把已有no噪声当违规新增。
**直接失败点：** 没有任何expense-entry/save动作，2条期望未新增；切Pro Expense后以重复检索旧AI“都是no”结论代替继续读全源文档。

### 根因分层与证据边界

**已证实**
- 官方diagnostic log sqlite_validators.validate_rows_addition_integrity L168：Expected row not found；不是异常评分。
- report verification_goal正确保留yes筛选与原note；执行未实施，不是planner公开目标漏note约束。
- events seq73是最后一个业务写tap Pro Expense；之后seq79、85、87至213/215/217重复search同AI输出的explanation，ui_snapshot循环，无doc滚动/无entry。
- events tool starts search_artifact=55；seq221 run_failed turn-limit；write12/60、denied0、deadline=false，故不属于动作或墙钟超限。
- step11/13原UI snapshot compaction.text_attribute_limit=50；长文档text只留header前50字符。截图含更多行，但不能用截断XML文本检索来证明全文件no。

**强推断**
- 强推断：把局部可视转录“当前均no”升级成全文件无yes的消极结论，再用不改变业务状态的证据检索回路寻求确认，导致完全未新增并耗尽turn；同时UI XML 50字符长文本裁剪妨碍全文件定位。

**无法确认与缺证据**
- 现存source截图并不覆盖全部102行；无法最终区分yes在未遍历区域、Markor preview显示/滚动范围截断、或初始化源文件内容与冻结预期不一致。不得声称已证实初始化正确，也不得声称文件真的全no。

**备选及区分**
- 若将来私有初始化文件证明只写了no，则责任转为harness初始化/文档写入，不能只归模型阅读；当前证据无法定案。
- 已有no条目来自初始化noise，不能当作本run新增违规。

责任层：FSQ长文档覆盖/negative证据推理；FSQ无进展artifact-loop/turn预算；harness初始化原文件证据缺口待区分。

### 预算与输出协议

- 写额度admitted=12/60，attempted=12，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=3720，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"reason": "Main runner did not succeed", "source": "agent_runtime.runner.tool_output.summary", "status": "failed"}`。
- `R/events.jsonl sequence=221`：Agent exceeded the configured turn limit.；真实runner错误同见nativeResult的agent_runtime.runner，而非仅外层Main runner did not succeed。
- tool_call_started计数（events，不是可能覆写的tool artifact数量）：`{"read_knowledge_index": 1, "launch_app": 1, "ui_snapshot": 26, "swipe": 6, "search_artifact": 55, "tap_on": 4, "assert_with_ai": 4, "read_artifact_slice": 4, "press_key": 1}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ Markor长文档reader / UI snapshot语义压缩`**：保留长text的截断标记/原artifact可定位边界；按连续viewport、首末行/滚动停滞建立覆盖表，搜选取字段而非仅读取局部no；未全覆盖不得宣称无yes。不得注入冻结目标行。
- **P1 / FSQ / `FSQ artifact evidence reader / runner termination`**：search相同artifact/explanation无新信息时停止重复读取，返回源文档补最小缺口或结构化说明未知；在既有100turn内收敛，不靠加预算。
- **P1 / harness / `harness ExpenseAddMultipleFromMarkor.initialize_task诊断产物`**：私有保存生成后的源文件字节/row数/yes-no数量与写入回读凭据供离线调查；不向agent提供oracle期待行；不改note或评分。

### 将来验证（未执行）

- 可离线：离线仅对既存init与完整源字节（若能找到）核对102行和2yes；当前缺源字节，明确为缺证据而非重建数据。
- 需设备，独立样例：独立Markor来源任务在合法UI全覆盖后只新增yes，note逐字、金额/cat精确且噪声不变；同时确保main结构化输出，预算60/100不变。

### FSQ待逐例回应的问题

- 能否找到本episode原始my_expenses.txt字节或初始化写入receipt，区分未遍历yes与初始化/preview截断？
- 为什么Pro Expense打开后55次search主要回读旧assertion的explanation，无新源文档动作？
- 请按index14仅计一次；与Markor专题重叠时保留同一根因证据，不重复算失败。

## 015 — ExpenseAddSingle

**官方：failed，reward=0.0；native=failed / verifier=failed。**
- `E` = `next-stage-plan/execution/run/episodes/015-ExpenseAddSingle`
- `R` = `next-stage-plan/execution/run/episodes/015-ExpenseAddSingle/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566`
- Goal原文（`R/sources/000-goal.txt`）：Add the following expenses into the pro expense:
Expense: Therapy Sessions
 amount_dollars: $307.01
 category_name: Health Care
 note: I may repeat this

- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

Expense DB清空后插10noise。goal已直接给全部四字段，无需跨app找来源。

仅新增Therapy Sessions，amount=30701分、category=9 Health Care，note=I may repeat this；name/note fuzzy、amount/category精确；总条数+1且原10noise完全保持。创建时间不按冻结参考expense.created_date比对。

- `AW/task_evals/single/expense.py:247-281` — `_ExpenseAddMultiple.validate_addition_integrity`。
- `AW/task_evals/common_validators/sqlite_validators.py:118-192,257-310` — `SQLiteApp/AddMultipleRows/validate_rows_addition_integrity`。
- `AW/task_evals/single/expense.py:308-313` — `ExpenseAddSingle`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 日志：validate_rows_addition_integrity:168 Expected row %s not found in the 'after' state.

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The saved Therapy Sessions expense shows an amount of $307.01, category Health Care, and note "I may repeat this".

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-2` / 3 | passed；launch1成功但看到launcher。 | `R/artifacts/tools/000002-ui_snapshot.json` |
| `agent-launch_app-3` / 5 | passed；第二次launch。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-launch-app-3-finalize-after-action-1-4b876bf49cda.json`；截图 `R/artifacts/screenshots/screenshot-agent-launch-app-3-finalize-after-action-1-249b6eea2140.png` |
| `agent-tap_on-6` / 11 | passed；应用抽屉选择Pro Expense才进入。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-6-finalize-after-action-1-7fbbbaee709b.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-42f90c02a88f.png` |
| `agent-tap_on-8` / 15 | passed；打开Entry。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-8-finalize-after-action-1-c4bb2f47d827.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-5b4647628b9e.png` |
| `agent-input_text-10` / 19 | passed；name Therapy Sessions。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-10-finalize-after-action-1-bfcc6921e3d5.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-10-finalize-after-action-1-078578433072.png` |
| `agent-input_text-11` / 21 | passed；amount307.01。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-11-finalize-after-action-1-003b0d3e40d6.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-11-finalize-after-action-1-f59ebba3fcd6.png` |
| `agent-press_key-12` / 23 | passed；收键盘。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-12-finalize-after-action-1-373e4e96d0e0.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-12-finalize-after-action-1-896ed438582c.png` |
| `agent-swipe-14` / 27 | passed；水平滚动类别栏。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-swipe-14-finalize-after-action-1-241a6f2bddf5.json`；截图 `R/artifacts/screenshots/screenshot-agent-swipe-14-finalize-after-action-1-7ecb2837f7e0.png` |
| `agent-tap_on-16` / 31 | passed；选择Health Care。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-e35946fde1f9.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-b3504354da45.png` |
| `agent-input_text-17` / 33 | passed；note I may repeat this。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-input-text-17-finalize-after-action-1-e3ed010a5179.json`；截图 `R/artifacts/screenshots/screenshot-agent-input-text-17-finalize-after-action-1-fb5822bdbaa3.png` |
| `agent-press_key-18` / 35 | passed；收键盘，第12写。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-18-finalize-after-action-1-8bd17b8e9bc3.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-18-finalize-after-action-1-9416e4b31388.png` |
| `agent-tap_on-20` / 39 | failed；Save被dispatch预算拒；after截图Entry四字段都对、Health Care有勾、SAVE仍在。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-20-finalize-after-action-1-c8e72a8c2555.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-26872d04ee3a.png` |
| `agent-tap_on-21` / 40 | failed；同一不可恢复拒绝再尝试Save，再失败。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-21-finalize-after-action-1-4004801cdb5f.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-21-finalize-after-action-1-15835bab5300.png` |
| `agent-kill_app-22` / 41 | failed；kill也拒。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-22-prepare-before-action-1-d329d797c131.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-22-prepare-before-action-1-79fd630d6eec.png` |

**预期 vs 实际：** 输入表单不是新增数据库；Save从未执行，官方missing row=0符合契约。不是金额分/美元换算或分类错误。
**直接失败点：** 12写用尽才Save，第13写起全部拒绝。

### 根因分层与证据边界

**已证实**
- 原Entry截图四字段完整且Health Care选中；目标30701分正确输入307.01 USD。
- audit前4写为双launch+抽屉+icon；Save拒seq39/40；diagnostic L168 missing expected row。

**强推断**
- 强推断：无效启动路径额外消费约3写，planner又没有为commit预留写槽；以输入完成代替save完成判断进度，Save成为预算边界外动作。

**无法确认与缺证据**
- 具体launch成功但仍launcher的底层原因交FSQ owner；不能假定设备故障。

**备选及区分**
- 即便UI时间显示15Oct与目标参考created_date不同，官方不按created_date比较新增，不能拿日期当失败原因。

责任层：FSQ launch/预算规划；harness如约计费拒绝。

### 预算与输出协议

- 写额度admitted=12/12，attempted=15，denied=3，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=840，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ launch_app / task planner预算模型`**：一次有效启动，避免重复launch+launcher迂回；安排输入/选category/Save的完整commit路径并在原12写内预留Save；NativeActionBudgetExceeded后不重试。

### 将来验证（未执行）

- 可离线：离线断言前12write均admitted，第13Save未forward；表单字段正确但row未新增。
- 需设备，独立样例：独立ExpenseAddSingle在12写内保存，官方校验4字段与+1/噪声保持；不增加预算。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/expense-recipes.md:40-72`。**已核对，无实质分歧**。
- 源码答复/分歧：四字段正确但Save未forward；官方expense.py L263-281/sqlite_validators L118-192与304-310要求新增匹配行、+1/噪声不变，L168 missing-row与未保存一致。不能承诺删单一动作即同12写内完成所有要求，最短合法路径未执行。
- actual kill target：无实际kill（S22预算拒绝）。
- 剩余unknown：app_start为何不前台、最终DB字节、同12写最短合法路径均未实测。
- 已逐例反馈Main；最终FSQ回执pending。

### FSQ待逐例回应的问题

- 是否与Contacts10同一launch无前台效果造成预算成本？
- 为何收到不可恢复NativeActionBudgetExceeded仍retry Save？怎样确保提交动作在规划而非末尾补做？

## 016 — ExpenseDeleteDuplicates

**官方：failed，reward=0.0；native=inconclusive / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates`
- `R` = `next-stage-plan/execution/run/episodes/016-ExpenseDeleteDuplicates/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae`
- Goal原文（`R/sources/000-goal.txt`）：Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

Public Transit金额20441分/Transportation7/note A need/created=modified1696132800000；实际两个204.41/2023Oct1在一屏列表底部已同时可见。参考日期Oct15，但列表默认筛选Oct1-14；该范围已包含两条目标。

清DB插5noise+两个完全相同的Public Transit，初始化验证行数7且除expense_id外每字段相同。成功仅能删除两个target ID之一，另一个与全部5noise必须原样保留，不得新增/误删。不是只凭相同name判断，也不是删除两条。

- `AW/task_evals/common_validators/sqlite_validators.py:73-115,348-369,380-415` — `validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows`。
- `AW/task_evals/single/expense.py:148-195` — `_ExpenseDeleteDuplicates.validate_deletion_integrity/ExpenseDeleteDuplicates`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：Pro Expense contains exactly one instance of each originally distinct expense, with no exact duplicates remaining and no unique expense lost.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-2` / 3 | passed；首次launch后launcher，重复launch+抽屉/icon。 | `R/artifacts/tools/000002-ui_snapshot.json` |
| `agent-tap_on-8` / 15 | failed；XPath //node[...]查不到；这是源XML node标签与底层Appium类树差异的可能点，不能当终极根因。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-8-finalize-after-action-1-320dd5ab8bee.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-e6d7a7260f8b.png` |
| `agent-tap_on-9` / 17 | failed；仅换/*仍查不到，第二次计费失败。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-9-finalize-after-action-1-4af14b859068.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-9-finalize-after-action-1-d570e085269f.png` |
| `agent-tap_at-10` / 19 | passed；坐标打开drawer。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-at-10-finalize-after-action-1-8f7c83bac4a6.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-at-10-finalize-after-action-1-34427ac87316.png` |
| `agent-ui_snapshot-13` / 25 | passed；原artifact000014包含完整7行：5noise+Public Transit两条，均204.41/Oct1；截图下一步filter前亦可见。 | `R/artifacts/tools/000014-ui_snapshot.json` |
| `agent-tap_on-14` / 27 | passed；不先比目标details，转去filter。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-c5b90c966c6a.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-9cff84f8be49.png` |
| `agent-tap_on-16` / 31 | passed；点start date。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-e73609a2c804.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-d943004ece02.png` |
| `agent-tap_on-18` / 35 | passed；点year。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-18-finalize-after-action-1-09f52d0e242b.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-18-finalize-after-action-1-3340a4d7115c.png` |
| `agent-tap_on-20` / 39 | passed；Cancel回filter；日期范围未改。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-20-finalize-after-action-1-d4426b923c02.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-6d64d2ccfff0.png` |
| `agent-press_key-22` / 43 | failed；第13写Back被预算拒；filter还开着。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-22-finalize-after-action-1-2c19235c69b7.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-22-finalize-after-action-1-7b3ebc0fc288.png` |
| `agent-press_key-23` / 44 | failed；无恢复可能重复Back再拒。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-press-key-23-finalize-after-action-1-86eca9f4fe0c.json`；截图 `R/artifacts/screenshots/screenshot-agent-press-key-23-finalize-after-action-1-dd37a1875879.png` |
| `agent-kill_app-24` / 45 | failed；kill亦拒，无删除。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-24-prepare-before-action-1-b0ace87d9f9d.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-24-prepare-before-action-1-e8f76868164c.png` |

**预期 vs 实际：** 需要比较并删掉一条Public Transit；实际两条已在可读artifact/截图中却进入无必要的日期探查，从未删除。official0是完整DB仍有重复，native inconclusive只因为它未用初始化事实。
**直接失败点：** 没有expense deletion动作；写12/12在导航、两次失效XPath和filter date/year/cancel上耗尽，目标组早已可见。

### 根因分层与证据边界

**已证实**
- 000014-ui_snapshot.json中两条Public Transit与对应204.41/Oct1均在原XML和截图出现；不是“因过滤器完全看不到目标”。
- 官方初始化会创建并验证这对真实duplicate，因此不能沿用native verifier“没证明初始有duplicate”的保守假设。
- seq15/17两次failed tap也各消耗一写；seq43/44/45拒Back/Back/kill，无删除。

**强推断**
- 强推断：将全局无重复证明当作必须先取消任何日期filter，忽略已足够定位的可见组；再用不匹配底层树的XPath重复试与日期探查消耗完commit预算。

**无法确认与缺证据**
- 未存最终DB完整快照，但源初始化+零删除+official0已充分支持未去重；无需推测误删。
- XPath底层接受的树格式具体接口由FSQ owner确认。

**备选及区分**
- 日期filter的Oct14确与Oct15参考日不同，但不是本例目标不可见原因，也不应直接修改初始化/rubric。

责任层：FSQ观察→动作规划失配；FSQ selector基于真实动作空间能力；harness预算成本。

### 预算与输出协议

- 写额度admitted=12/12，attempted=15，denied=3，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=840，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ duplicate planner/数据字段比较`**：先消费已有7行与两相同候选的证据，打开候选details比较字段，只删一条；不用为“证明全局范围”先走与当前组无关的filter日期流程。
- **P1 / FSQ / `FSQ selector生成/runner budget`**：使用真实Appium class tree的已暴露定位器或已有明确图标/可访问性定位；第一次Target not found后用新观察修正，不重复同错误树假设；保留delete+confirm预算。

### 将来验证（未执行）

- 可离线：离线用该7行artifact证明两目标同屏及filter包含Oct1；预算成本归因为12写而非额外墙钟。
- 需设备，独立样例：独立小型duplicate实例：删除一条后私有DB严格剩6行，所有noise与保留target字段不变，原12写。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/expense-recipes.md:74-107`。**已核对，无实质分歧**。
- 源码答复/分歧：两Public Transit同屏仅是候选，agent仍需公开UI详情比较；私有冻结init证明两完全重复+5noise。expense.py L163-174与validator L73-115要求仅删两个target ID之一并保留其余。失败selector照NativeDispatchBudget L85-118计费符合本次合同，不是免费观察；不确定底层XPath具体失配原因。
- actual kill target：无实际kill（S24预算拒绝）。
- 剩余unknown：最终DB未存，无行级diag；不能把可见列表同名同额视为agent已经知道note/category完整重复。
- 已逐例反馈Main；最终FSQ回执pending。

### FSQ待逐例回应的问题

- 为什么已读000014含双Public Transit还进入start-date/year而不比较候选？
- FSQ显示XML node与Appium执行树class名是否有契约失配，能否避免两次failed XPath计费？
- 请将原初始化存在duplicate的证据提供给离线verifier分析，不能把未知初始当业务未知。

## 017 — ExpenseDeleteDuplicates2

**官方：failed，reward=0.0；native=inconclusive / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2`
- `R` = `next-stage-plan/execution/run/episodes/017-ExpenseDeleteDuplicates2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7`
- Goal原文（`R/sources/000-goal.txt`）：Delete all but one of any expenses in pro expense that are exact duplicates, ensuring at least one instance of each unique expense remains.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

真重复Jeans49636分/Clothes8/note Want to have/created=modified1696118400000（Oct1）；近似Jeans49938、50010、50198分，日期也不同，均不得删。默认filter2023Oct1-15覆盖这些日期，不能只看名字。

42行=40noise+2完全相同Jeans，仅允许删除这两个target ID之一；必须保留其余所有行，包括3条同名但金额和created/modified不同的Jeans近重复。保留一条每unique的公开goal，与官方只删精确一ID一致。

- `AW/task_evals/common_validators/sqlite_validators.py:73-115,348-369,380-415` — `validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows`。
- `AW/task_evals/single/expense.py:163-174,198-230` — `_ExpenseDeleteDuplicates.validate_deletion_integrity/ExpenseDeleteDuplicates2.generate_random_params`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：Pro Expense contains exactly one instance of every originally present unique expense, with all surplus exact duplicates removed and no unique expense lost.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-11` / 21 | passed；首个expense log列表范围Oct1-15，底部出现较近日期的Jeans近似行。 | `R/artifacts/tools/000011-ui_snapshot.json` |
| `agent-tap_on-12` / 23 | passed；第一次filter。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-caccbf291eaa.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-3d4965ab9eef.png` |
| `agent-tap_on-14` / 27 | passed；start date后Back/Back，不应用新范围。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-d36172ed7d67.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-56997d43df92.png` |
| `agent-tap_on-20` / 39 | passed；重复filter→Back。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-20-finalize-after-action-1-706d4a787049.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-f3fb81f8fe65.png` |
| `agent-ui_snapshot-25` / 49 | passed；滑到Jeans等日期Oct12/9/7区域，不是targetOct1。 | `R/artifacts/tools/000028-ui_snapshot.json` |
| `agent-ui_snapshot-27` / 53 | passed；继续降序到Oct6附近Jeans。 | `R/artifacts/tools/000031-ui_snapshot.json` |
| `agent-ui_snapshot-29` / 57 | passed；继续到Oct3。 | `R/artifacts/tools/000034-ui_snapshot.json` |
| `agent-tap_on-30` / 59 | passed；又filter→Back，范围未改。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-30-finalize-after-action-1-6a6f3077f33f.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-30-finalize-after-action-1-67d6039baa0c.png` |
| `agent-ui_snapshot-35` / 69 | passed；最后列表只到Gym Membership/Oct2；还没读到Oct1重复目标。 | `R/artifacts/tools/000042-ui_snapshot.json` |
| `agent-assert_state-36` / 71 | failed；contains filter text失败，属于断言文本处理非任务目标。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-state-36-prepare-before-action-1-f6866048b1a2.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-state-36-prepare-before-action-1-0df4036a279b.png` |
| `agent-assert_visible-38` / 75 | passed；同一个完整filter label可见断言成功，但没有验证去重。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-visible-38-prepare-before-action-1-6a360c90111a.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-visible-38-prepare-before-action-1-568ba81b99fd.png` |
| `agent-kill_app-39` / 77 | failed；18/18写用满，kill拒；仍从未执行删除。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-39-prepare-before-action-1-cf56f73dd0c1.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-39-prepare-before-action-1-1d49354b1d23.png` |

**预期 vs 实际：** 需要找到Oct1真重复、核对details并删一条；真实滚动只至Oct2，中途多次filter无改动且未跟踪全列表覆盖，official0符合零删除。
**直接失败点：** 零删除，真实重复组尚在最后未遍历区域；label断言成功不能替代数据库去重。

### 根因分层与证据边界

**已证实**
- source初始化验证双target；真实target与三变体的金额/日期不同均在冻结params中，不能删除同名就算。
- 000042/000044 snapshot最后可见Gym Membership Oct2；同屏没有真target496.36。
- 18写分解：双launch/抽屉/icon4；drawer/log2；filter/date/Back/Back/filter/Back6；4次swipe4；最后filter/Back2；共18，无delete。

**强推断**
- 强推断：重复filter未带来新范围或新信息占去关键写槽；对排序列表缺少明确覆盖/尾部判据，停在Oct2便结束，没有到达Oct1真实组。保守不误删近似Jeans正确，但计划未完成必要查找。

**无法确认与缺证据**
- 没有最终DB逐行快照；不能声称近似Jeans被误删（轨迹没有删除）。
- 不得根据最后label Oct1-15就宣称已经遍历该全区间；label只是过滤条件。

**备选及区分**
- 不是“filter排除了Oct1目标”；已见标签范围明确包括Oct1，失败在遍历未完成与预算分配。

责任层：FSQ列表覆盖/精确重复判别规划；artifact片段与全集合混淆；harness写预算。

### 预算与输出协议

- 写额度admitted=18/18，attempted=19，denied=1，exhausted=True，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=1200，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ duplicate collection traversal/coverage memory`**：建立按排序日期/首末可见行的覆盖，未到scroll end不宣称全面；只对同名候选比较amount/category/note/日期，保留近似变体；不要重复打开不需改的filter。
- **P1 / FSQ / `FSQ planner预算收敛`**：原18写内移除重复filter和无效启动，把额度用于到达列表尾与一次delete/confirm；拒绝后不无意义cleanup重试。

### 将来验证（未执行）

- 可离线：离线断言真重复496.36两条与499.38/500.10/501.98近似三条不可混组；最后Oct2≠全覆盖。
- 需设备，独立样例：独立40noise dedupe样例仅删一真重复，剩41行，3近似行逐字段不变，18写不变。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/expense-recipes.md:109-142`。**已核对，无实质分歧**。
- 源码答复/分歧：filter包含Oct1，终屏停Oct2；真重复Oct1 Jeans496.36未覆盖，499.38/500.10/501.98近似须保留。expense.py L163-174/198-230仅删一target且其余41行不变。无删除尝试，唯一denied为kill，不能说delete在预算边界被挡。
- actual kill target：无实际kill（S39预算拒绝）。
- 剩余unknown：最终DB未存，真实冗余仍存由已验证初始化+零删除与官方0强支持，不冒充直接读到DB。
- 已逐例反馈Main；最终FSQ回执pending。

### FSQ待逐例回应的问题

- 为何在范围始终Oct1-15时仍三次filter探查，占去6写后没有到Oct1？
- planner如何把artifact文本片段/当前view与full collection分开，避免label断言替代业务断言？

## 019 — ExpenseDeleteMultiple2

**官方：failed，reward=0.0；native=inconclusive / verifier=inconclusive。**
- `E` = `next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2`
- `R` = `next-stage-plan/execution/run/episodes/019-ExpenseDeleteMultiple2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64`
- Goal原文（`R/sources/000-goal.txt`）：Delete the following expenses from pro expense: Streaming Services, Unexpected Expenses, Pet Supplies.
- 原始result：`E/result.json`；初始化：`E/raw-private/task-initialization.json`；评分：`E/raw-private/evaluator-diagnostics.json`；native输出：`E/raw-private/fsq-native/worker/fsq-task-result.private.json`。

### 初始化与官方rubric

目标Streaming48725分/Entertainment6/Oct15 03:00，Unexpected26950分/Others1/Oct11，Pet19095分/Others1/Oct15 00:00；默认Oct1-15降序。

53行=50noise+Streaming Services、Unexpected Expenses、Pet Supplies各一目标；3个target ID必须全删，所有50noise完全不变，不得新增。二元评分，不按删两项给2/3。

- `AW/task_evals/single/expense.py:72-99,140-145` — `_ExpenseDeleteMultiple.validate_deletion_integrity/ExpenseDeleteMultiple2`。
- `AW/task_evals/common_validators/sqlite_validators.py:73-115,348-369,380-415` — `validate_rows_removal_integrity/DeleteMultipleRows.initialize_task/is_successful/DeleteDuplicateRows`。

- 评分边界：`after_agent_exit_and_submission_before_task_teardown`；outcome=returned、exception=None。 无component细分/判错字段日志，不从scalar猜测组件分。

### 实际native轨迹与决定性证据

派生verification_goal（`R/report.json/task/verification_goal`）：The Pro Expense expense list no longer contains Streaming Services, Unexpected Expenses, or Pet Supplies.

| Step / audit.sequence | 状态与实际行为 | 原始证据 |
|---|---|---|
| `agent-ui_snapshot-11` / 21 | passed；000012原XML和随后longpress12前截图，Pet Supplies190.95/Today12:00AM就在Streaming下一行。 | `R/artifacts/tools/000012-ui_snapshot.json` |
| `agent-long_press_on-12` / 23 | passed；选择Streaming。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-long-press-on-12-finalize-after-action-1-3fb7440dde7b.json`；截图 `R/artifacts/screenshots/screenshot-agent-long-press-on-12-finalize-after-action-1-b05bf1c4b9a5.png` |
| `agent-tap_at-14` / 27 | passed；点关联delete。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-at-14-finalize-after-action-1-849431c9fce0.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-at-14-finalize-after-action-1-ca7ffa352e71.png` |
| `agent-tap_on-16` / 31 | passed；confirm；snapshot17 Streaming消失，Pet Supplies仍在列表顶部。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-53f2df41db16.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-4f13de6c1ccf.png` |
| `agent-ui_snapshot-17` / 33 | passed；000021再确认Pet Supplies可见，之后却只搜Unexpected并下滑。 | `R/artifacts/tools/000021-ui_snapshot.json` |
| `agent-long_press_on-22` / 43 | passed；定位Unexpected。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-long-press-on-22-finalize-after-action-1-a12e7982c991.json`；截图 `R/artifacts/screenshots/screenshot-agent-long-press-on-22-finalize-after-action-1-087f7474b185.png` |
| `agent-tap_at-24` / 47 | passed；误点Restaurant Meal详情（142.94、Oct12、note I may repeat this），不是Delete确认；随后关闭，未误删。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-at-24-finalize-after-action-1-51064356ee0f.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-at-24-finalize-after-action-1-f3d2fcc64b78.png` |
| `agent-tap_on-26` / 51 | passed；Close关闭Restaurant Meal详情，未删除该非目标。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-26-finalize-after-action-1-71480522a4f3.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-26-finalize-after-action-1-fb9767e8a15d.png` |
| `agent-tap_at-28` / 55 | passed；重新按Unexpected关联delete坐标。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-at-28-finalize-after-action-1-93fd690fe736.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-at-28-finalize-after-action-1-367ab9df5b5d.png` |
| `agent-tap_on-30` / 59 | passed；confirm后snapshot31 Unexpected消失。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-30-finalize-after-action-1-e0afc13d07d4.json`；截图 `R/artifacts/screenshots/screenshot-agent-tap-on-30-finalize-after-action-1-dfc29926609f.png` |
| `agent-ui_snapshot-41` / 81 | passed；一路向较早日期滚到Oct1；Pet是Oct15顶部，后续只在离开顶部后的snapshots搜Pet。 | `R/artifacts/tools/000054-ui_snapshot.json` |
| `agent-assert_not_visible-43` / 85 | passed；只证明当前屏没有Pet，绝非全列表无Pet。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-assert-not-visible-43-prepare-before-action-1-951e7c3f22d2.json`；截图 `R/artifacts/screenshots/screenshot-agent-assert-not-visible-43-prepare-before-action-1-95f9194d6dd8.png` |
| `agent-kill_app-44` / 87 | passed；显式kill Expense成功；DB型oracle不要求app前台，不是此例核心因果。 | `R/artifacts/ui-snapshots/ui_snapshot-agent-kill-app-44-prepare-before-action-1-5291723b5aba.json`；截图 `R/artifacts/screenshots/screenshot-agent-kill-app-44-prepare-before-action-1-ed2a07bbf12e.png` |

**预期 vs 实际：** 实际只删Streaming/Unexpected。Pet从最初同屏就可见、第一次删除后仍可见，但没有任何Pet删除动作；official0不是它从一开始就不存在。
**直接失败点：** 漏掉最初可见的Pet；之后单向下滚和当前屏not_visible掩盖漏项，未回到顶部。

### 根因分层与证据边界

**已证实**
- 000012/000015/000021三份原UI均含Pet Supplies；本调查直接读XML并看截图，不接受native“Pet未定位”的总结为事实。
- events seq47只搜初始列表Streaming；Pet第一次search出现在seq101对000039（已远离顶部），之后seq107/113/119/125/131也只搜后续更早日期view，从未回查000012/000021。
- 只有两次已确认删除流程，预算23/34、denied0、deadline=false，尚余11写；不是预算或墙钟自然逼停。

**强推断**
- 强推断：多目标任务没有维护每目标见过的位置/完成状态，先为一个target导航后遗忘同屏另一target；后来把局部absence当全局absence，提前终结。工具大XML片段化使这一遗漏更容易，但不是证据缺失。

**无法确认与缺证据**
- 没有评分时完整after DB来排除所有噪声副作用；第一次错误打开Restaurant Meal详情后已关闭、未删除，后续两目标确认与快照吻合；不虚构具体噪声损坏。

**备选及区分**
- 不是Pet被日期filter排除；初始范围内它清楚可见。不是UI不支持delete；其他两条已成功。

责任层：FSQ多目标状态记忆/列表搜索策略；FSQ assertion范围语义；非harness budget限制。

### 预算与输出协议

- 写额度admitted=23/34，attempted=23，denied=0，exhausted=False，deadlineExceeded=False；只读观察/断言不算计费写。
- businessSeconds=2160，maxTurns=100（`E/raw-private/fsq-worker-outcome.json/result/nativeTarget/maxTurns`）；独立于写额度，不把turn-limit说成业务timeout。
- mainAnswer：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 精确修复方案（未实施）

- **P1 / FSQ / `FSQ multi-target planner/working memory`**：维护每目标observed位置、pending/deleted集合；同屏目标均登记，滚走后可回定位。对局部not_visible严格标viewport，不当full collection证明；回查既有完整artifact或回顶部处理Pet。
- **P1 / FSQ / `FSQ before-delete locator binding`**：每个delete图标绑定同一行name/id，并在confirm前核对dialog，保留已有取消误点的正确行为。

### 将来验证（未执行）

- 可离线：离线断言初始/首删后Pet存在；对000039以后的not_visible只证明该viewport；task pending应仍含Pet。
- 需设备，独立样例：独立多删除53行实例3目标全无、其余50行逐字段保持，34写内完成，不重复同题凑分。

### 与FSQ分案逐例核对

- 已读`BASE/failure-analysis/fsq-case-notes/expense-recipes.md:144-178`。**已核对，补正本方错误dialog的泛称**。
- 源码答复/分歧：Pet在初始与首删后已可见，之后只向下搜索且23/34无拒绝。独立读S24原XML+截图：Restaurant Meal详情142.94/Oct12/note I may repeat this，S26关闭，不是Delete确认，也没误删。官方expense.py L88-99/validator L73-115要3target全无及50noise不变，两个确认通过不能替代整体完整性。
- actual kill target：com.arduia.expense（S44显式kill，DB型oracle不要求前台）。
- 剩余unknown：Pet末次仍存在+无后续删除支持漏项，但最终DB未存；不能确认它是唯一失败字段/排除所有噪声副作用。
- 已逐例反馈Main；最终FSQ回执pending。

### FSQ待逐例回应的问题

- 为什么初始000012和首删后000021已含Pet，但直到离开该区域才search Pet？
- 是否agent只能看到截断excerpt而未消费既有完整artifact；多目标记忆可否绑定首次出现的位置？
- 请不要把native“available window不足”当根因：23/34且无deadline，至少仍有11写。

