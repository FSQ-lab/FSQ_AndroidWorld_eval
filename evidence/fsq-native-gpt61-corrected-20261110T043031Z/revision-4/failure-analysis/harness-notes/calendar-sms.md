# Calendar / SMS：harness 侧离线逐例调查

覆盖 **68、69、70、71、72、74、76、78、81、82、84、85、86，共13唯一案例**；每例原reward均为 **0.0**。只写本cluster调查，未改代码、原产物或评分。未运行设备probe、模型、任务、评分、测试、构建、lint或安装。

## 证据与版本边界

- 项目相对基址：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`。JSON的每例 `actualTrace.nativeRunPath` 是该例 `artifacts/...` 路径根；`nativeExecutionPointer` 精确指向原 execution-result 的 steps 数组，eventSequence 是原 events.jsonl 行/sequence。
- 官方判据读取manifest指定冻结安装：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world`；distribution 0.1.0，installed tree SHA `0ac9428da2e9d78d0303c44c682184268e708a3116134646401d5c8425671b94`。没有用当前repo同名源码替代，也没有import/实例化官方任务重建随机数据。
- FSQ driver/skill源的版本绑定引用 `failure-analysis/fsq-evidence-index.json#/source_identity`：FSQ owner已对所列16文件与冻结SHA逐一比对。此处已独立阅读native原轨迹、XML及全部13例决定性PNG；**双侧逐例因果核对仍pending，由父agent整合**。
- IR答案进入官方的是exact main runner的`task_run_v1.summary`，不是verifier摘要（harness `fsq_evidence.py:256-272`、`fsq_runner.py:357-366`）。本组mainAnswer均valid，这不等于业务答案正确，更不作废official0。

## 先读的共性结论

1. **68/69/71/72/76：月视图日期是画在网格上的像素，XML不提供对应数字text节点。** `Go to date`在该视图打开月/年picker，OK不等于已选目标日。反复相同导航和numeric text locator耗尽写预算，不能用“点击失败/预算耗尽”停止根因解释。
2. **70/74：真正日picker的输入/相邻项点击也未成为所选日。** 74尤其有原after-action截图：`input_text(20)` passed但选中值仍15；后续逐日只到18(Wed)，未到20(Fri)。具体NumberPicker提交失败分支仍未知。
3. **78：正确Board meeting及其22:35时间已取到。** 现存15:35 Oct15截图、按时间排序agenda与事件详情足以构成最早未来候选证据，main却仍交无法确定说明；两次详情/标题assert只证明存在，不证明min(start>now)。`clock.text=15:35`与content-desc=23:35须分源，不泛称timezone。
4. **81：目标号码正确，但未输入、未发送。** 12写花在启动/中途kill/错误Google Messages/launcher恢复与冗余composer tap；两次input被预算明确拒绝。
5. **82/84/85/86：已发送视觉证据成立，不是错收件人或草稿。** 冻结SMS官方还AND评分时前台包；四例原kill invoke均显式停止`com.simplemobiletools.smsmessenger`，然后完整native返回，之后评分。foreground冲突是**强推断主候选**，不是无component证据的唯一已证实0因。
6. SMS provider为共享Telephony `content://sms/sent`；app_stop本身不删该库。setup设置默认SMS不等于每例ROLE_SMS已观测；缺role/provider行/activity必须保留unknown。四例发送动作结束到官方调用仅47.604/34.374/50.869/40.386秒，小于5分钟；但宿主间隔不能替代provider.date和get_android_time。
7. **86独立分层**：Oscar起始Add to contacts预填表单不是保存成功证明；source attribution欠证与“地址已发Gabriel”及official0原因分开。官方继承谓词本身不检验Oscar名称来源。

### 官方共享源码索引

- IR：`information_retrieval.py:82-119` initialize/score；`proto_utils.py:147-210` 逗号分项、项数相等与STRING_MATCH；`fuzzy_match_lib.py:20-50` 忽略大小写、SequenceMatcher≥0.9；`calendar_utils.py:133-155,215-331` 相关事件+75噪声与排噪跨度/端点。
- 删除：`calendar.py:264-288,323-364,367-418`；`sqlite_validators.py:73-115,348-369` 目标行删净、非目标原样、无新增。
- SMS：`sms_validators.py:211-217` 共享provider；`:93-152` address/body/date；`:228-232`设备now；`:234-253`每题initialize；`:255-276` sent与foreground合取；`:289-295` Sending异常。
- SMS角色：冻结`env/setup_device/apps.py:406-433`设置secure sms_default_application并点Set as default；`env/adb_utils.py:1426-1446`仅settings put secure。每例initialize不重新检查ROLE_SMS。
- 生命周期：匹配冻结FSQ `resources/skills/android-harness.md:7-10`要求末尾kill；driver `kill_app:103-107`执行app_stop。harness `fsq_runner.py:330-373`保持完整native返回后评分。这是未来契约修订点，不是改r4分数理由。

## 068 SimpleCalendarAnyEventsOnDate — reward 0.0

**公开goal：** Do I have any events October 28 in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与初始化**
- date：公开goal为October 28、未写年；初始化参考2023-10-15，实际日期选择器明确2023，故此处目标2023-10-28而非2026当前宿主日期。
- output：当天全部标题；多项逗号分隔，不能回答yes或导航报告。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af/sources/000-goal.txt`。

**官方判据：** tasks.textproto 362-405生成同日3个1小时相关事件；title_without_replacement/time_without_replacement会从候选池另选，frozen params.title=Birthday party并非该例三标题。排除该日随机噪声；get_expected_answer取相关state的3个title，按逗号拆分、数量相等、忽略大小写模糊相似度>=0.9逐项匹配。
- 冻结源 `task_evals/information_retrieval/information_retrieval.py:82-119`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:147-210`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `task_evals/information_retrieval/proto/tasks.textproto:362-405`。
- 冻结源 `task_evals/information_retrieval/calendar_utils.py:133-155,215-331`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:297-306,336-403`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.calendar.pro"}`。
- `agent-tap_on-4` / events#25 / `/steps/3`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-6` / events#33 / `/steps/5`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-tap_on-8` / events#37 / `/steps/7`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-10` / events#41 / `/steps/9`：failed；`{"locator":{"text":"28"}}`；Target was not found.。
- `agent-tap_on-12` / events#47 / `/steps/11`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-tap_on-14` / events#51 / `/steps/13`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-16` / events#59 / `/steps/15`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-tap_on-18` / events#63 / `/steps/17`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-21` / events#73 / `/steps/20`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value","accessibilityId":null,"text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-22` / events#75 / `/steps/21`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000010-ui_snapshot.json`：选择器仅月Oct/年2023；月视图没有day EditText。
- 原UI `artifacts/tools/000012-ui_snapshot.json`：返回October月视图；原XML无text=28的可定位节点。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-10-prepare-before-action-1-99d86c030af4.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Unable to verify the complete October 28 event titles before the harness action budget was exhausted.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The run returned an inability-to-verify report rather than the requested event titles, so the verification goal was not met.
- 预算：maximum=10、admitted=10、attempted=12、denied=2、failed dispatch=1；写构成`{"launch_app": 2, "tap_on": 8}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** 官方要求3标题；截图可确证Date night并见另外两条截断标题，强推断为Game night、Product demo；实际提交为无法验证说明。

**直接失败：** 没有进入10月28日日视图或取得完整标题；main summary是Unable to verify...，官方IR得到的正是这句而非标题。

**根因置信度**
- **已证实**
  - agent-tap_on-10(text=28)报Target was not found；其prepare截图清楚画出28与三条事件，原XML却只暴露toolbar，证明视觉日期与可访问节点不是一回事。
  - top_value→OK流程在steps6/8、12/14、16/18共三次只确认月/年，并未选择28；10个写预算全部消耗为2launch+8tap。
  - 本例mainAnswer.status=valid，非exact_main_summary契约错误；reward=0来自业务答案未匹配，不是official分数无效。
- **强推断**
  - 终极机制为以可视月网格日期当text locator且未改换有效导航路径，随后重复无进展月/年确认；预算是该路径耗尽的截断点。
  - 截图28格的Game nig / Product / Date night与唯一候选名对应Game night、Product demo、Date night（强推断）；只有Date night在截图未截断。缺少生成后proto/完整日详情，不能把三标题均称已确证。
- **无法确认与备选**
  - 未存生成后relevant_state的完整proto；禁止重新初始化/random重建来补三标题。
  - launch_app返回passed但初始仍launcher的底层原因待FSQ侧核对。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**：`drivers/android/_uiautomator2.py::launch_app (95-100)`, `resources/skills/android-harness.md::Case Lifecycle`, `src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`。launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**：`FSQ main runner task_run_v1.summary`, `src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)`, `src/fsq_androidworld_eval/fsq_runner.py (357-366)`。IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**
- 离线用月网格只有像素无day节点的固定UI fixture，断言不对不存在的text=28重复派发；有设备的未来验证应证明切换/截图坐标导航后显示目标日期且读齐3条标题。
- 离线答案协议fixture断言只有UI取证的三标题进入summary，不把冻结params.title当答案；不得把本例私有标题注入future agent。

**逐例FSQ核对问题 / 当前harness侧结论**
- 月视图截图已含28但XML缺节点时，native为何继续text locator及三轮top_value/OK，而未用有证据坐标或日视图？
- 请核对title_without_replacement是否已有冻结生成后state；若无，不应把Birthday party当标准答案。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 069 SimpleCalendarDeleteEvents — reward 0.0

**公开goal：** In Simple Calendar Pro, delete all the calendar events on 2023-10-27

**约束与初始化**
- date：明确2023-10-27全天，不能只删一个或本周其它日。
- integrity：删除3条目标事件且20条非目标噪声不变。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c/sources/000-goal.txt`。
  - 目标行 `Review session for Project X`，`2023-10-27T11:00:00+00:00`→`2023-10-27T11:15:00+00:00`。
  - 目标行 `Call with the Team`，`2023-10-27T21:00:00+00:00`→`2023-10-27T21:15:00+00:00`。
  - 目标行 `Catch up on Project X`，`2023-10-27T12:00:00+00:00`→`2023-10-27T12:30:00+00:00`。
  - 非目标噪声20行，要求不变。

**官方判据：** SimpleCalendarDeleteEvents.n_rows=3；initialize添加目标行并记before/rows_to_delete；is_successful比较目标id消失、其余行原样且无新增。不是只看屏幕为空。
- 冻结源 `task_evals/single/calendar/calendar.py:264-288`。
- 冻结源 `task_evals/common_validators/sqlite_validators.py:73-115,348-369`。
- 冻结源 `task_evals/single/calendar/calendar_evaluators.py:24-45`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-tap_on-3` / events#23 / `/steps/2`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-5` / events#31 / `/steps/4`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-7` / events#35 / `/steps/6`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-9` / events#39 / `/steps/8`：passed；`{"target":"OK"}`。
- `agent-tap_on-11` / events#43 / `/steps/10`：failed；`{"target":"27"}`；Target was not found.。
- `agent-tap_on-12` / events#47 / `/steps/11`：failed；`{"target":"More options"}`；Target was not found.。
- `agent-tap_on-15` / events#59 / `/steps/14`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-17` / events#63 / `/steps/16`：passed；`{"locator":{"text":"Go to date"}}`。
- `agent-tap_on-19` / events#67 / `/steps/18`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-21` / events#71 / `/steps/20`：failed；`{"locator":{"text":"27"}}`；Target was not found.。
- `agent-tap_on-24` / events#81 / `/steps/23`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-26` / events#85 / `/steps/25`：passed；`{"locator":{"text":"Go to date"}}`。
- `agent-tap_on-28` / events#89 / `/steps/27`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-30` / events#97 / `/steps/29`：failed；`{"target":null,"locator":{"resourceId":null,"accessibilityId":"More options","text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000011-ui_snapshot.json`：Go to date打开的是Oct/2023二列月年选择器，并无27日字段。
- 原UI `artifacts/tools/000027-ui_snapshot.json`：仍October月视图；没有day=27可定位文本；未出现Delete确认。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-11-prepare-before-action-1-9c15c76ea524.png`（相对该例nativeRunPath）。
- 原task result `/steps/4` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Could not complete event deletion or verify that October 27, 2023 is empty. The harness action budget was exhausted during navigation.
- 原task result `/steps/5` / `agent_runtime.verifier`：businessStatus=inconclusive，summary：The supplied evidence does not establish whether the calendar view for October 27, 2023 shows no remaining events.
- 预算：maximum=14、admitted=14、attempted=16、denied=2、failed dispatch=3；写构成`{"launch_app": 1, "tap_on": 13}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** 目标2023-10-27 11:00 Review session for Project X、12:00 Catch up on Project X、21:00 Call with the Team应消失，20噪声保留；实际停在月视图。

**直接失败：** 整个执行没有进入目标事件详情，也未执行任何Delete；官方目标三行没有可证实的删除行为，reward=0。

**根因置信度**
- **已证实**
  - events43与71请求text/target 27（steps11/21）均Target was not found；step12 More options同样失败。
  - steps5/7/9、15/17/19、24/26/28重复菜单Go to date→OK，只返回月视图。14预算=1launch+13tap，3个失败尝试也被计入；step30及kill遭拒。
- **强推断**
  - 把月视图Go to date误当可以选择某一天，并在无日节点的canvas网格坚持文本点击，是导航闭环失效；不是删除操作本身失败。
- **无法确认与备选**
  - 没有评分时DB before/after dump，不能量化副作用；现存动作无Delete，官方0与此一致。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**
- 离线核对冻结三目标行与20噪声的删除集合判据；未来设备验证应逐条删除/确认后核对目标日为空且非目标日期未变，不运行oracle驱动导航。

**逐例FSQ核对问题 / 当前harness侧结论**
- 为何Go to date只呈月/年后仍尝试text=27并重复该导航？应由何状态提示将其切换为Daily view或坐标导航？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 070 SimpleCalendarDeleteEventsOnRelativeDay — reward 0.0

**公开goal：** In Simple Calendar Pro, delete all events scheduled for this Monday.

**约束与初始化**
- date：公开this Monday，冻结参考2023-10-15周日，应指2023-10-16周一；不是按宿主2026日期或状态栏content-desc推算。
- integrity：删除该日两条事件，保留20噪声。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd/sources/000-goal.txt`。
  - 目标行 `Review session for Project X`，`2023-10-16T10:00:00+00:00`→`2023-10-16T10:30:00+00:00`。
  - 目标行 `Review session for Budget Planning`，`2023-10-16T00:00:00+00:00`→`2023-10-16T01:00:00+00:00`。
  - 非目标噪声20行，要求不变。

**官方判据：** SimpleCalendarDeleteEventsOnRelativeDay.n_rows=2，goal周一来自冻结day_of_week/2023-10-16；继承DeleteMultipleRows精确目标行移除与其它行不变。
- 冻结源 `task_evals/single/calendar/calendar.py:264-288`。
- 冻结源 `task_evals/common_validators/sqlite_validators.py:73-115,348-369`。
- 冻结源 `task_evals/single/calendar/calendar_evaluators.py:24-45`。
- 冻结源 `task_evals/single/calendar/calendar.py:367-418`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.calendar.pro"}`。
- `agent-tap_on-4` / events#25 / `/steps/3`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-6` / events#31 / `/steps/5`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/change_view"}}`。
- `agent-tap_on-8` / events#35 / `/steps/7`：passed；`{"target":"Daily view"}`。
- `agent-tap_on-10` / events#39 / `/steps/9`：failed；`{"target":"More options"}`；Target was not found.。
- `agent-tap_on-12` / events#43 / `/steps/11`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-14` / events#47 / `/steps/13`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-16` / events#51 / `/steps/15`：passed；`{"target":"16"}`。
- `agent-tap_on-17` / events#53 / `/steps/16`：passed；`{"target":"OK"}`。
- `agent-tap_on-19` / events#57 / `/steps/18`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow"}}`。
- `agent-tap_on-21` / events#61 / `/steps/20`：passed；`{"target":"Review session for Budget Planning"}`。
- `agent-tap_on-23` / events#65 / `/steps/22`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/delete","accessibilityId":null,"text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-tap_on-24` / events#67 / `/steps/23`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/delete","accessibilityId":null,"text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-25` / events#69 / `/steps/24`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000016-ui_snapshot.json`：日期选择器中15是NumberPicker编辑值；tap target 16是相邻可视项，不等于提交16。
- 原UI `artifacts/tools/000019-ui_snapshot.json`：OK后仍October 15 (Sun)。
- 原UI `artifacts/tools/000021-ui_snapshot.json`：step19右箭头后October 16 (Mon)，00:00 Budget Planning、10:00 Project X两事件。
- 原UI `artifacts/tools/000023-ui_snapshot.json`：已打开Budget Planning详情；目标日期与00:00确认。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-23-prepare-before-action-1-f80b4a437c3d.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Deletion could not be completed because the harness action budget was exhausted. An empty Monday day view was not verified.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The selected Monday was not cleared. Its day view listed two scheduled events, and both subsequent Delete attempts were blocked by the exhausted action budget.
- 预算：maximum=12、admitted=12、attempted=15、denied=3、failed dispatch=1；写构成`{"launch_app": 2, "tap_on": 10}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** 2023-10-16 00:00 Review session for Budget Planning及10:00 Review session for Project X均删除，20噪声不变；实际只打开前者详情。

**直接失败：** 定位到正确周一且打开第一条详情时预算恰好用尽；首次Delete step23未获准派发，后续重试24同样拒绝，两个目标事件未删除。

**根因置信度**
- **已证实**
  - steps1/3重复launch、step10 More options失败、step16 tap16后17 OK仍回15，额外step19右箭头才到16。
  - 12个写名额=2launch+10tap；首次Delete与重试分别events65/67，均预算拒绝，非点击命中后删不掉。
- **强推断**
  - 日期选择动作未核验有效提交，加上启动恢复和一次无效菜单点击耗尽业务路径；预算不足是开销与规划契约不匹配的结果，不是日期/时区错。
- **无法确认与备选**
  - 若无启动开销/无效日期动作，固定12预算是否足够逐条删除两事件仍需未来设备路径验证；不可凭此私加预算。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ Android driver + harness契约owner**：`drivers/android/_uiautomator2.py::launch_app (95-100)`, `resources/skills/android-harness.md::Case Lifecycle`, `src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`。launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ Android driver/规划owner**：`drivers/android/_uiautomator2.py::input_text (138-151)`, `FSQ日历日期导航规划`。NumberPicker不能只以set_text未抛错判成功；在通用文本输入结果中暴露实际值/提交后值，规划需依据当前控件支持的滑轮或编辑提交方法完成日期选择，并核对返回日视图日期。不要硬编码本题20或扩大预算。
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**
- 离线NumberPicker fixture证明tap相邻16不被当作提交；设备验证固定原12预算内从正确启动状态完成两条删除并保留噪声，若不可行另列跨任务预算研究而不改本题成绩。

**逐例FSQ核对问题 / 当前harness侧结论**
- tap16/OK为何没有提交日期？启动重复和失败菜单调用可否在不增加预算下消除？
- 首次Delete前已12/12，native是否知道剩余write quota，是否有必要避免对确定action_budget再重试？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 071 SimpleCalendarDeleteOneEvent — reward 0.0

**公开goal：** In Simple Calendar Pro, delete the calendar event on 2023-10-24 at 23h with the title 'Workshop on Project X'

**约束与初始化**
- date：2023-10-24 23:00，仅标题Workshop on Project X的一条；不能删除其它同日或相似标题。
- integrity：目标23:00–23:30消失，其余20行原样。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868/sources/000-goal.txt`。
  - 目标行 `Workshop on Project X`，`2023-10-24T23:00:00+00:00`→`2023-10-24T23:30:00+00:00`。
  - 非目标噪声20行，要求不变。

**官方判据：** SimpleCalendarDeleteOneEvent.n_rows=1，沿用目标id删除完整性判定；冻结row_objects含唯一23:00 Workshop on Project X。
- 冻结源 `task_evals/single/calendar/calendar.py:264-288`。
- 冻结源 `task_evals/common_validators/sqlite_validators.py:73-115,348-369`。
- 冻结源 `task_evals/single/calendar/calendar_evaluators.py:24-45`。
- 冻结源 `task_evals/single/calendar/calendar.py:323-364`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-tap_on-3` / events#23 / `/steps/2`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-5` / events#31 / `/steps/4`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-7` / events#35 / `/steps/6`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-9` / events#39 / `/steps/8`：passed；`{"target":"OK"}`。
- `agent-tap_on-11` / events#49 / `/steps/10`：failed；`{"target":"24"}`；Target was not found.。
- `agent-tap_on-13` / events#59 / `/steps/12`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-15` / events#63 / `/steps/14`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-17` / events#67 / `/steps/16`：passed；`{"target":"OK"}`。
- `agent-tap_on-19` / events#77 / `/steps/18`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/change_view"}}`。
- `agent-tap_on-21` / events#81 / `/steps/20`：passed；`{"target":"Daily view"}`。
- `agent-tap_on-23` / events#85 / `/steps/22`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-input_text-25` / events#89 / `/steps/24`：failed；`{"target":null,"locator":{"resourceId":null,"accessibilityId":null,"text":null,"className":null,"xpath":"//android.widget.EditText[@text='15']"},"text":"24","textType":"literal"}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-26` / events#91 / `/steps/25`：failed；`{"app_id":null}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000011-ui_snapshot.json`：Go to date仅Oct/2023，不选24日。
- 原UI `artifacts/tools/000015-ui_snapshot.json`：October月视图XML无24日文本；step11 target24失败。
- 原UI `artifacts/tools/000033-ui_snapshot.json`：后来切Daily view后仍October15，非24。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-11-prepare-before-action-1-45452fa65e18.png`（相对该例nativeRunPath）。
- 原task result `/steps/4` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Deletion was not completed or verified because the harness action budget was exhausted during date navigation.
- 原task result `/steps/5` / `agent_runtime.verifier`：businessStatus=inconclusive，summary：The evidence does not establish whether October 24, 2023 no longer shows 'Workshop on Project X' at 23:00. Execution stopped during date navigation without observing the target day's final calendar state.
- 预算：maximum=12、admitted=12、attempted=14、denied=2、failed dispatch=1；写构成`{"launch_app": 1, "tap_on": 11}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** 唯一2023-10-24 23:00–23:30 Workshop on Project X删除；实际仍10月15日日导航阶段。

**直接失败：** 没到10月24日也没有打开或删除目标；最后尝试把日期编辑值15改24（step25）在派发前被预算拒绝。

**根因置信度**
- **已证实**
  - step11 target24 Target was not found；两轮菜单Go to date→OK未选择日。
  - 改Daily view至step21、再点top_value至23已消耗12/12；input_text25与kill26遭拒；原轨迹无Delete。
- **强推断**
  - 先把月年对话框当日选择，再过晚切换真正可编辑日的路径；无day节点场景未及早切换可访问视图导致任务终止。
- **无法确认与备选**
  - 未执行被拒绝的input_text24，不能将74的NumberPicker未提交直接当成本例已发生；本例的输入没有真正调用。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。

**未来验证（全部未执行）**
- 离线保证月年picker不会被标记为完成日导航；设备固定12预算验证到24后只选23:00目标并删除，核对20噪声不变。

**逐例FSQ核对问题 / 当前harness侧结论**
- 为何在两个Go to date循环与失败text24后才切Daily view？请区分input_text25预算拒绝与已执行无效的NumberPicker输入。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 072 SimpleCalendarEventOnDateAtTime — reward 0.0

**公开goal：** What is on my schedule for October 27 2023 at 8:00pm in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与初始化**
- date：公开绝对2023-10-27 8:00pm即20:00。
- output：该时刻所有标题，逗号分隔；不是当天全部事件。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b/sources/000-goal.txt`。

**官方判据：** tasks.textproto 239-275放入2023-10-27 20:00 Product demo持续15min；噪声排除该时点重叠（calendar_utils组合绝对datetime、含端点）；success取相关title并做STRING_MATCH。
- 冻结源 `task_evals/information_retrieval/information_retrieval.py:82-119`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:147-210`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `task_evals/information_retrieval/proto/tasks.textproto:239-275`。
- 冻结源 `task_evals/information_retrieval/calendar_utils.py:133-155,215-331`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.calendar.pro"}`。
- `agent-tap_on-4` / events#25 / `/steps/3`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-6` / events#31 / `/steps/5`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-8` / events#35 / `/steps/7`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-10` / events#39 / `/steps/9`：passed；`{"target":"OK"}`。
- `agent-tap_on-12` / events#45 / `/steps/11`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-14` / events#49 / `/steps/13`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-16` / events#53 / `/steps/15`：passed；`{"target":"OK"}`。
- `agent-tap_on-18` / events#59 / `/steps/17`：failed；`{"target":"More options"}`；Target was not found.。
- `agent-tap_on-20` / events#65 / `/steps/19`：failed；`{"target":null,"locator":{"resourceId":null,"accessibilityId":"More options","text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-21` / events#67 / `/steps/20`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000011-ui_snapshot.json`：Go to date为Oct/2023月年picker，无目标日选择。
- 原UI `artifacts/tools/000018-ui_snapshot.json`：第二轮同样只月/年。
- 原UI `artifacts/tools/000020-ui_snapshot.json`：仍October月视图，未显示27日20:00详情。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-18-prepare-before-action-1-51e1e18c0b51.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Unable to determine the event titles from the available calendar evidence.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The recorded answer reports an inability to determine the event titles rather than providing the required titles-only answer.
- 预算：maximum=10、admitted=10、attempted=12、denied=2、failed dispatch=1；写构成`{"launch_app": 2, "tap_on": 8}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** Product demo（冻结相关事件20:00–20:15），实际提交无能为力说明。

**直接失败：** 未到10月27日，也未读20:00事件；actual main summary为Unable to determine...，非Product demo，official=0。

**根因置信度**
- **已证实**
  - Go to date→OK在steps6/8/10、12/14/16重复，未有日值修改；step18抽象More options Target was not found；step20及kill21遭预算拒绝。
  - 10写=2launch+8tap，未出现目标event标题读取或时刻判断，不能归为8pm边界判错。
- **强推断**
  - 月年picker与目标日导航混淆，加上不验证进展导致重复路径；标题输出失败为该导航失败的后果。
- **无法确认与备选**
  - 无法从未访问目标日的native轨迹判断agent会否正确处理跨日重叠边界；本例不能据此指控时间推理。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**：`drivers/android/_uiautomator2.py::launch_app (95-100)`, `resources/skills/android-harness.md::Case Lifecycle`, `src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`。launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**：`FSQ main runner task_run_v1.summary`, `src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)`, `src/fsq_androidworld_eval/fsq_runner.py (357-366)`。IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**
- 离线固定绝对20:00和含端点重叠fixture检查筛选逻辑；未来设备证明目标日标题、时间均可见且summary只含UI证实标题，绝不把冻结Product demo传给future agent。

**逐例FSQ核对问题 / 当前harness侧结论**
- Go to date二次仍只月年时为何没有变更导航策略？8pm事件本身未访问，请避免仅用time-range或模型标签。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 074 SimpleCalendarEventsInTimeRange — reward 0.0

**公开goal：** Do I have any events between 4:15pm and 8pm Friday in Simple Calendar Pro? Answer with the titles only. If there are multiples titles, format your answer in a comma separated list.

**约束与初始化**
- date：公开Friday，初始化reference 2023-10-15 Sunday，因此冻结目标2023-10-20 Friday；不是2026-11-13。
- range：4:15pm至8pm即16:15–20:00；公开between应检查边界，官方生成包含起点，排除条件>=16:15且<=20:00，实现按事件跨度重叠排噪。
- output：符合区间事件标题，非截图上任意其它日标题。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48/sources/000-goal.txt`。

**官方判据：** tasks.textproto 964-1006的相关事件Cooking Class从16:15持续1h（17:15结束），含下界；噪声由calendar_utils.check_event_conditions按起止时点OR及日期相交排除；official本身不重新查UI区间，而从相关state取title匹配。
- 冻结源 `task_evals/information_retrieval/information_retrieval.py:82-119`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:147-210`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `task_evals/information_retrieval/proto/tasks.textproto:964-1006`。
- 冻结源 `task_evals/information_retrieval/calendar_utils.py:133-155,215-331`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-tap_on-3` / events#23 / `/steps/2`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-5` / events#31 / `/steps/4`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/change_view"}}`。
- `agent-tap_on-7` / events#35 / `/steps/6`：passed；`{"target":"Daily view"}`。
- `agent-tap_on-9` / events#39 / `/steps/8`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-input_text-11` / events#43 / `/steps/10`：passed；`{"locator":{"xpath":"//android.widget.EditText[@text='15']"},"text":"20","textType":"literal"}`。
- `agent-tap_on-12` / events#45 / `/steps/11`：passed；`{"target":"OK"}`。
- `agent-tap_on-14` / events#49 / `/steps/13`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow"}}`。
- `agent-tap_on-15` / events#51 / `/steps/14`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow"}}`。
- `agent-tap_on-16` / events#53 / `/steps/15`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow"}}`。
- `agent-tap_on-18` / events#57 / `/steps/17`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow","accessibilityId":null,"text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-tap_on-19` / events#59 / `/steps/18`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_right_arrow","accessibilityId":null,"text":null,"className":null,"xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-20` / events#61 / `/steps/19`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000012-ui_snapshot.json`：picker日值15，可见月Oct、年2023。
- 原UI `artifacts/tools/000015-ui_snapshot.json`：input_text20 passed及OK之后仍October15(Sun)，输入没有成为选择值。
- 原UI `artifacts/tools/000019-ui_snapshot.json`：连续三次右箭头后只有October18(Wed)，到Friday还差2天。
- 独立读像素：`artifacts/screenshots/screenshot-agent-input-text-11-finalize-after-action-1-a25e0360dddb.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Unable to determine the matching event titles before the harness action budget was exhausted.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The completed run returned an inability-to-determine message, not matching event titles or an indication that none match.
- 预算：maximum=10、admitted=10、attempted=13、denied=3、failed dispatch=0；写构成`{"launch_app": 1, "tap_on": 8, "input_text": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** Cooking Class（2023-10-20 16:15–17:15，处在含下界区间内），实际无法确定说明；未发生端点错选。

**直接失败：** 关键输入step11对NumberPicker set_text20返回passed，但after-action截图选中项仍15；其后只能逐日前进，18日时10预算耗尽，最终未检查20日16:15–20:00。

**根因置信度**
- **已证实**
  - 原after截图可直接读15，不是猜测输入失败；step11前后compact UI的sha相同，step12 OK后日视图也仍15。
  - events49/51/53三次右箭头使15→18；events57/59两次继续导航均denied，不是到了Friday后筛错区间。
  - main预计划写overlapping；本例没有看到Friday日程，不能把start-only/overlap的语义差异当实际失败原因。
- **强推断**
  - input_text实现只selector.click/clear/set_text后直接passed（138-151）缺少NumberPicker提交值核验，模型信任这个低层成功；再用逐日导航消耗配额，直接造成未到目标日。
- **无法确认与备选**
  - 值为什么未提交：NumberPicker忽略文本、焦点/IME与commit回滚等需最小未来控件验证区分，现存after截图不能区分底层分支。
- 责任层：FSQ Android driver输入成功语义/NumberPicker提交证据；FSQ日期导航状态后置条件与IR输出协议。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ Android driver/规划owner**：`drivers/android/_uiautomator2.py::input_text (138-151)`, `FSQ日历日期导航规划`。NumberPicker不能只以set_text未抛错判成功；在通用文本输入结果中暴露实际值/提交后值，规划需依据当前控件支持的滑轮或编辑提交方法完成日期选择，并核对返回日视图日期。不要硬编码本题20或扩大预算。
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ输出协议owner + harness owner**：`FSQ main runner task_run_v1.summary`, `src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)`, `src/fsq_androidworld_eval/fsq_runner.py (357-366)`。IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**
- 离线以本例前后原UI与截图fixture断言dispatch passed≠日期已改；设备用非本题合成日期检查编辑/提交后的NumberPicker值和日视图一致。
- 边界未来独立fixture覆盖start=16:15、end=16:15、start=20:00、晚于20:00与跨午夜；保持官方现有rubric，不能改变为只看start以提高分数。

**逐例FSQ核对问题 / 当前harness侧结论**
- 为什么input_text20返回passed但after截图仍15？请核对FSQ/SDK对NumberPicker的click-clear-set_text是否有提交步骤。
- 规划是否已看到OK后October15却仍选择5次逐日移动而不把日期输入视为未完成？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 076 SimpleCalendarFirstEventAfterStartTime — reward 0.0

**公开goal：** Among events starting on October 29 2023 between 00:00 and 23:59 in Simple Calendar Pro, which starts first strictly after 21:00? Answer with the titles only. If multiple events share the earliest qualifying start time, format their titles as a comma separated list.

**约束与初始化**
- date：明确2023-10-29，候选仅当天00:00–23:59开始的事件。
- range：严格晚于21:00，不含21:00；只返回最早合格start及全部同start并列标题；跨日结束不应排除当日21:30开始事件。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7/sources/000-goal.txt`。

**官方判据：** 修正后tasks.textproto 857-894以同一hour生成21:30 Grocery Shopping，持续3h至次日00:30；排除同日严格>21:00的噪声。expected title仅Grocery Shopping，严格边界与跨日结束均由冻结模板保证。
- 冻结源 `task_evals/information_retrieval/information_retrieval.py:82-119`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:147-210`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `task_evals/information_retrieval/proto/tasks.textproto:857-894`。
- 冻结源 `task_evals/information_retrieval/calendar_utils.py:133-155,215-331`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.calendar.pro"}`。
- `agent-tap_on-4` / events#25 / `/steps/3`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-6` / events#31 / `/steps/5`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/top_value"}}`。
- `agent-tap_on-8` / events#35 / `/steps/7`：passed；`{"locator":{"resourceId":"android:id/button1"}}`。
- `agent-tap_on-10` / events#43 / `/steps/9`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-12` / events#47 / `/steps/11`：passed；`{"target":"Go to date"}`。
- `agent-tap_on-14` / events#51 / `/steps/13`：passed；`{"target":"OK"}`。
- `agent-tap_on-16` / events#55 / `/steps/15`：failed；`{"target":"29"}`；Target was not found.。
- `agent-tap_on-18` / events#61 / `/steps/17`：passed；`{"locator":{"accessibilityId":"More options"}}`。
- `agent-tap_on-20` / events#65 / `/steps/19`：failed；`{"target":"Go to date","locator":null}`；NativeActionBudgetExceeded: action_budget。
- `agent-kill_app-21` / events#67 / `/steps/20`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000009-ui_snapshot.json`：top_value为月/年picker，非选择29日。
- 原UI `artifacts/tools/000017-ui_snapshot.json`：Go to date再次为Oct/2023月年picker。
- 原UI `artifacts/tools/000019-ui_snapshot.json`：月视图XML无29日文本；step16 target29失败。
- 原UI `artifacts/screenshots/screenshot-agent-tap-on-16-prepare-before-action-1-a37144650d6e.png`：独立看像素可见29格Grocery Shopping标题，但没有21:30开始时间；不能把可见标题当已完成最早合格时间判断。
- 独立读像素：`artifacts/screenshots/screenshot-agent-tap-on-16-prepare-before-action-1-a37144650d6e.png`（相对该例nativeRunPath）。
- 原task result `/steps/4` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Unable to determine the event titles from the available evidence.
- 原task result `/steps/5` / `agent_runtime.verifier`：businessStatus=failed，summary：The completed run returned an inability statement rather than the required event titles, so the verification goal was not satisfied.
- 预算：maximum=10、admitted=10、attempted=12、denied=2、failed dispatch=1；写构成`{"launch_app": 2, "tap_on": 8}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** Grocery Shopping（2023-10-29 21:30开始，严格晚于21:00；结束次日00:30不改变候选资格），actual inability summary。

**直接失败：** 未打开29日日程或21:30事件详情，月网格截图虽能看见Grocery Shopping字样但未核对start时间；summary仍是inability而非标题，official=0。

**根因置信度**
- **已证实**
  - steps6/8月年确认后steps10/12/14再菜单月年确认，step16 text29 Target was not found；step18只重开菜单，step20及kill遭拒。
  - 10写=2launch+8tap；未到时间筛选，不能把旧版FirstEvent语义/21:00严格边界错判当实际根因。
- **强推断**
  - 可视月日没有可定位文本、策略仍循环月年picker，是导航机制失配；有明确日期并未因timezone跨日。
- **无法确认与备选**
  - native未读相关21:30–00:30事件，不能确定其会否误按结束日排除或漏并列。
- 责任层：FSQ可访问月网格/日期导航状态规划；写预算为该错误路径的截断点，不是终极根因。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ规划/Android driver owner（具体机制待FSQ侧核对）**：`fsq_agent agent/_pre_plan.py + resources/skills/android-harness.md`, `drivers/android/_uiautomator2.py::tap_on/input_text`。将日期导航作为有后置条件的状态转换：月视图无可定位日期节点时改用当前截图有依据的坐标或Daily view；确认日/月/年实际改变再继续，不把OK或passed等同目标日期。只依据公开goal与当前UI，不能读取oracle参数/答案。
- **P1 / FSQ Android driver + harness契约owner**：`drivers/android/_uiautomator2.py::launch_app (95-100)`, `resources/skills/android-harness.md::Case Lifecycle`, `src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`。launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ输出协议owner + harness owner**：`FSQ main runner task_run_v1.summary`, `src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)`, `src/fsq_androidworld_eval/fsq_runner.py (357-366)`。IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。

**未来验证（全部未执行）**
- 离线合成strictly-after fixture：21:00不选、21:30并列全选、次日00:01开始不选、当日跨夜结束仍选；未来设备验证日期导航与titles-only协议，不传oracle标题。

**逐例FSQ核对问题 / 当前harness侧结论**
- 请按已冻结修正版判据核对，不要回套旧版21:00/next-day标签；numeric29文本缺失时为何未使用有证据的替代导航？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 078 SimpleCalendarNextEvent — reward 0.0

**公开goal：** What is my next upcoming event in Simple Calendar Pro? Answer with the title only. If there are multiples titles, format your answer in a comma separated list.

**约束与初始化**
- date：next upcoming锚定冻结初始化2023-10-15 15:34 UTC；实际下拉截图明确Sun Oct15、15:35。
- clockSources：UI XML clock text=15:35但content-desc=23:35，同一快照有不一致；截图可见时间支持15:35，不可泛称timezone造成整任务时间错乱。
- output：最早未来事件标题，不能只证明某事件存在。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93/sources/000-goal.txt`。

**官方判据：** tasks.textproto 125-168放入当日22:35–22:45 Board meeting；排除当日15:30到目标时刻（含端点）的噪声，保证其是预设now之后最早。expected=Board meeting。
- 冻结源 `task_evals/information_retrieval/information_retrieval.py:82-119`。
- 冻结源 `task_evals/information_retrieval/proto_utils.py:147-210`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `task_evals/information_retrieval/proto/tasks.textproto:125-168`。
- 冻结源 `task_evals/information_retrieval/calendar_utils.py:133-155,215-331`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-tap_on-3` / events#23 / `/steps/2`：passed；`{"locator":{"accessibilityId":"Predicted app: Calendar"}}`。
- `agent-tap_on-5` / events#31 / `/steps/4`：passed；`{"locator":{"resourceId":"com.simplemobiletools.calendar.pro:id/change_view"}}`。
- `agent-tap_on-7` / events#35 / `/steps/6`：passed；`{"target":"Simple event list"}`。
- `agent-swipe-9` / events#41 / `/steps/8`：passed；`{"direction":"down"}`。
- `agent-swipe-10` / events#43 / `/steps/9`：passed；`{"start":{"x":530,"y":1},"end":{"x":530,"y":1100},"reference_screen_size":{"width":1080,"height":2400},"duration":500}`。
- `agent-press_key-12` / events#51 / `/steps/11`：passed；`{"key":"Back"}`。
- `agent-tap_on-15` / events#65 / `/steps/14`：passed；`{"target":"Board meeting"}`。
- `agent-press_key-17` / events#71 / `/steps/16`：passed；`{"key":"Back"}`。
- `agent-tap_on-19` / events#79 / `/steps/18`：passed；`{"locator":{"text":"Board meeting"}}`。
- `agent-assert_state-21` / events#83 / `/steps/20`：passed；`{"element":{"resourceId":"com.simplemobiletools.calendar.pro:id/event_title","text":"Board meeting"},"optional":false}`。
- `agent-press_key-22` / events#85 / `/steps/21`：failed；`{"key":"Back"}`；NativeActionBudgetExceeded: action_budget。
- `agent-press_key-23` / events#87 / `/steps/22`：failed；`{"key":"Back"}`；NativeActionBudgetExceeded: action_budget。
- `agent-tap_on-25` / events#97 / `/steps/24`：failed；`{"target":null,"locator":{"resourceId":null,"accessibilityId":null,"text":null,"className":"android.widget.ImageButton","xpath":null}}`；NativeActionBudgetExceeded: action_budget。
- `agent-assert_state-26` / events#99 / `/steps/25`：passed；`{"element":{"resourceId":"com.simplemobiletools.calendar.pro:id/event_title","text":"Board meeting"},"optional":false}`。
- `agent-kill_app-27` / events#101 / `/steps/26`：failed；`{"app_id":"com.simplemobiletools.calendar.pro"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000008-ui_snapshot.json`：Simple event list列15 Sunday：02:28/04:01/08:32过去事件、22:35 Board meeting、22:57 Appointment；16 Monday后续。
- 原UI `artifacts/tools/000012-ui_snapshot.json`：坐标从y=1下拉误打开通知面板，可见15:35 Sun Oct15。
- 原UI `artifacts/tools/000025-ui_snapshot.json`：Board meeting详情确认October15、22:35–22:45。
- 原UI `artifacts/tools/000032-ui_snapshot.json`：第二次打开同一详情；step21/26只assert标题存在。
- 独立读像素：`artifacts/screenshots/screenshot-agent-press-key-12-prepare-before-action-1-7030f9162e82.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Could not conclusively determine the earliest upcoming event.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The recorded final answer reports inability to determine the event instead of containing only the required event title or comma-separated titles.
- 预算：maximum=10、admitted=10、attempted=14、denied=4、failed dispatch=0；写构成`{"launch_app": 1, "tap_on": 5, "swipe": 2, "press_key": 2}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** Board meeting；actual是无法确定最早未来事件的说明，即使title assertions passed仍没有提交业务答案。

**直接失败：** 已经读到并两次确认正确Board meeting详情，但没有把list顺序、当前截图时间与事件时间结合为最早未来事件证据；main最终仍Could not conclusively determine...，official=0。

**根因置信度**
- **已证实**
  - first list同日三个早晨事件均早于截图15:35，下一条22:35且后一条22:57；可见证据足以支持Board meeting，无需读oracle。
  - step10坐标swipe从屏幕y=1下拉打开通知栏，step12 Back恢复；steps15/19重复打开Board meeting，剩余writes耗在重复查看。
  - 10预算用完后仍两次Back及额外tap遭拒；assert_state21/26属于不计写观察，仅能确认标题，不证明min(start>now)。
- **强推断**
  - 终极推理缺口是未对已获得的时间与有序agenda做候选排除闭环，加之边缘滑动/重复详情浪费预算；存在clock accessibility label与可见时间冲突，可能增加不确定性，但无已存内部思考证明它就是决策原因。
- **无法确认与备选**
  - 无法证实agent是否采信23:35 content-desc；不能将该标签差异当已证实timezone根因。
- 责任层：FSQ IR候选筛选/证据聚合；FSQ内容滚动与输出协议。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。scalar无分量；按原source和轨迹区分失败，不改评分。

**精确修复方案（未实施）**
- **P1 / FSQ输出协议owner + harness owner**：`FSQ main runner task_run_v1.summary`, `src/fsq_androidworld_eval/fsq_evidence.py::_main_answer (256-272)`, `src/fsq_androidworld_eval/fsq_runner.py (357-366)`。IR公开任务要求titles-only时，把已从UI取得并核验的业务答案作为exact main summary；保留执行诊断在errors/evidence而非掺入答案。无法取证仍诚实inconclusive，不能从oracle补答案，也不能将verifier摘要替换main答案。
- **P1 / FSQ planner/driver owner**：`FSQ日历IR规划/证据聚合`, `drivers/android/_uiautomator2.py::swipe`。以原可见当前时间、日期及agenda有序列表建立start>now且无更早候选的证据；clock text/content-desc冲突时区分来源并用截图而非任意解释为时区。滚动限定内容区域，禁止从状态栏边缘起手的内容滚动；完整证据已足够时不重复打开同一详情。

**未来验证（全部未执行）**
- 离线用原list/详情/通知栏截图fixture断言22:35是15:35之后最早可见候选，明确早晨past与次日future；独立clock-label冲突fixture记录依据不臆断timezone。
- 未来设备只需验证内容区swipe不拉开通知栏；min/start排序推理与summary协议可离线验证。

**逐例FSQ核对问题 / 当前harness侧结论**
- 已经有15:35 Oct15截图、15 Sunday按start排序列表和22:35详情，为何仍不能形成earliest-upcoming证据？是否因clock content-desc23:35，还是验证器需要额外未暴露条件？
- 两次详情与两次标题assert为何未让summary回到已取证的Board meeting；有无final-answer与run-summary分离机制？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 081 SimpleSmsReply — reward 0.0

**公开goal：** Reply to +18407874306 with message: Yoga class every Tuesday and Thursday at 6 PM. in Simple SMS Messenger

**约束与初始化**
- recipient：+18407874306已有收到消息的会话，不是任意最近会话。
- body：Yoga class every Tuesday and Thursday at 6 PM.（含句号），必须实际发送而非草稿。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7/sources/000-goal.txt`。

**官方判据：** SimpleSmsReply.initialize_task先清短信，随机插入噪声与目标号码收件；继承SimpleSMSSendSms要求共享Telephony sent provider有匹配number/body、设备5分钟时间窗，且评分时前台包为Simple SMS Messenger。
- 冻结源 `task_evals/common_validators/sms_validators.py:93-152,211-276`。
- 冻结源 `task_evals/single/sms.py:115-155`。
- 冻结源 `env/setup_device/apps.py:406-433`。
- 冻结源 `env/adb_utils.py:1426-1446`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-081-20261110T212034Z-a84bf7/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- `agent-kill_app-4` / events#25 / `/steps/3`：passed；`{}`。
- `agent-launch_app-5` / events#27 / `/steps/4`：passed；`{}`。
- `agent-swipe-7` / events#31 / `/steps/6`：passed；`{"direction":"up"}`。
- `agent-tap_on-9` / events#39 / `/steps/8`：passed；`{"locator":{"accessibilityId":"Messages"}}`。
- `agent-press_key-11` / events#43 / `/steps/10`：passed；`{"key":"Home"}`。
- `agent-swipe-12` / events#45 / `/steps/11`：passed；`{"direction":"up"}`。
- `agent-swipe-14` / events#49 / `/steps/13`：passed；`{"direction":"up"}`。
- `agent-tap_on-16` / events#53 / `/steps/15`：passed；`{"locator":{"accessibilityId":"SMS Messenger"}}`。
- `agent-tap_on-18` / events#59 / `/steps/17`：passed；`{"locator":{"text":"+18407874306"}}`。
- `agent-tap_on-20` / events#63 / `/steps/19`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message"}}`。
- `agent-input_text-21` / events#65 / `/steps/20`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message","accessibilityId":null,"text":null,"className":null,"xpath":null},"text":"Yoga class every Tuesday and Thursday at 6 PM.","textType":"literal"}`；NativeActionBudgetExceeded: action_budget。
- `agent-input_text-22` / events#67 / `/steps/21`：failed；`{"target":null,"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message","accessibilityId":null,"text":null,"className":null,"xpath":null},"text":"Yoga class every Tuesday and Thursday at 6 PM.","textType":"literal"}`；NativeActionBudgetExceeded: action_budget。
- `agent-assert_visible-23` / events#69 / `/steps/22`：failed；`{"locator":{"text":"Yoga class every Tuesday and Thursday at 6 PM."},"optional":false}`；Target was not found.。
- `agent-kill_app-24` / events#71 / `/steps/23`：failed；`{"app_id":"com.simplemobiletools.smsmessenger"}`；NativeActionBudgetExceeded: action_budget。
- 原UI `artifacts/tools/000012-ui_snapshot.json`：误点Messages后前台是com.google.android.apps.messaging，页面提示不是默认SMS app。
- 原UI `artifacts/tools/000017-ui_snapshot.json`：真正SMS Messenger列表含目标+18407874306，收到Book club meets next Tuesday to discuss 1984。
- 原UI `artifacts/tools/000022-ui_snapshot.json`：目标会话正确，composer仍Type a message…，没有请求正文或发送气泡。
- 独立读像素：`artifacts/screenshots/screenshot-agent-input-text-21-prepare-before-action-1-0c30d4ae011c.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Execution was blocked by the harness action budget before the reply could be entered and sent. The required outgoing message was not verified.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=failed，summary：The verification goal was not met. Text entry was blocked by the exhausted action budget, and the final visibility assertion could not find the requested reply.
- 预算：maximum=12、admitted=12、attempted=15、denied=3、failed dispatch=0；写构成`{"launch_app": 3, "kill_app": 1, "swipe": 3, "tap_on": 4, "press_key": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。

**期望 vs 实际：** 在+18407874306会话实际发出精确Yoga...正文并保留正确前台；actual目标会话空composer，无发送步骤。

**直接失败：** 会话找对，但step21/22两次输入都在dispatch前被预算拒绝，未输入更未发送；最终assert_visible找不到请求正文。

**根因置信度**
- **已证实**
  - 前12写被3launch、一次中途kill、3swipe、一次Home、4tap占满；其中进入Google Messages是错误app分支。
  - 目标号码已通过step18打开，step20另点composer消耗最后write；input_text本身已包含click/clear/set_text，因此此前单独tap不是必要原语。
  - 本例最终kill被拒，不能套用其它4例“发送后kill造成前台冲突”作为本例0分原因；这里只存在中途kill。
- **强推断**
  - 启动工具未保证前台加上根据launcher标签误选Messages、恢复漫游及冗余composer tap，把有限写配额花在到达app/会话之前；不是收件人选择错误或输入内容格式错。
- **无法确认与备选**
  - Google Messages非默认的UI不能证明当时哪一个包是ROLE_SMS holder；也不能把这个提示当Simple SMS Messenger非默认的证据。
- 责任层：FSQ启动成功语义与app身份恢复规划；写预算契约下的重复/冗余导航。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/081-SimpleSmsReply/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。SMS evaluator以logging.info记录messages，但该例root/absl effectiveLevel30，records=[]不能推导sent为空。

**精确修复方案（未实施）**
- **P1 / FSQ Android driver + harness契约owner**：`drivers/android/_uiautomator2.py::launch_app (95-100)`, `resources/skills/android-harness.md::Case Lifecycle`, `src/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch`。launch_app应在成功返回前证明目标package/activity实际前台，明确未前台的结果；从当前UI选择一次有证据的恢复，不重复空launch/kill/launcher漫游。现行写预算不增加，失败动作仍依原契约计数。
- **P1 / FSQ planner owner**：`FSQ短信规划/资源skills`, `drivers/android/_uiautomator2.py::input_text (138-151)`。依公开Simple SMS Messenger app身份确认package，不能把Messages launcher标签当同一app；已确定composer后直接用复合input_text，不额外tap后再耗配额；action_budget明确拒绝后不要同语义重试。

**未来验证（全部未执行）**
- 离线用两个Messages/SMS Messenger图标与Google非默认页fixture验证身份区分；未来设备固定12预算要求目标会话输入并发送，不能增加预算或同题再试计分。

**逐例FSQ核对问题 / 当前harness侧结论**
- launch_app为何返回成功却需要3次launch和launcher漫游？误选Messages可否通过前台包语义阻止？
- 预算拒绝后input_text重试是否在native技能里被误当一般可恢复错误？单独点击composer为何未利用input_text的复合click？
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 082 SimpleSmsReplyMostRecent — reward 0.0

**公开goal：** Reply to the most recent text message using Simple SMS Messenger with message: A quick brown fox.

**约束与初始化**
- recipient：most recent received text的发送号码；公开goal不直接给号码，必须从会话顺序/时间识别。实际最顶+17594820731。
- body：A quick brown fox.
- actualSend：在该收到The early bird catches the worm.的会话实际发送，而非新建错会话或草稿。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb/sources/000-goal.txt`。

**官方判据：** SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。
- 冻结源 `task_evals/common_validators/sms_validators.py:93-152,211-276`。
- 冻结源 `task_evals/single/sms.py:57-112`。
- 冻结源 `env/setup_device/apps.py:406-433`。
- 冻结源 `env/adb_utils.py:1426-1446`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-082-20261110T212404Z-22e8bb/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- `agent-assert_state-13` / events#49 / `/steps/12`：passed；`{"element":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message","text":"A quick brown fox."},"optional":false}`。
- `agent-tap_on-14` / events#51 / `/steps/13`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_send_message"}}`。
- `agent-assert_state-16` / events#55 / `/steps/15`：passed；`{"element":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_message_body","text":"A quick brown fox."},"optional":false}`。
- `agent-assert_visible-17` / events#57 / `/steps/16`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_success"},"optional":false}`。
- `agent-assert_with_ai-18` / events#61 / `/steps/17`：passed；`{"prompt":"Verify the current conversation is with +17594820731 and contains the received message 'The early bird catches the worm.' and the outgoing reply 'A quick brown fox.' with a successful sent indicator, not merely draft text.","optional":false}`。
- `agent-kill_app-19` / events#63 / `/steps/18`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- 原UI `artifacts/tools/000012-ui_snapshot.json`：列表最顶+17594820731、15:34、The early bird catches the worm.；其它会话其后。
- 原UI `artifacts/tools/000014-ui_snapshot.json`：进入同号码并见原入站内容。
- 原UI `artifacts/tools/000018-ui_snapshot.json`：发送后出现A quick brown fox.消息体，composer为空；最终kill prepare截图有右侧气泡checkmark。
- 独立读像素：`artifacts/screenshots/screenshot-agent-kill-app-19-prepare-before-action-1-ea51277b7f07.png`（相对该例nativeRunPath）。
- 原task result `/steps/3` / `agent_runtime.runner`：businessStatus=success，summary：Sent “A quick brown fox.” in Simple SMS Messenger as a reply to the most recent received text message.
- 原task result `/steps/4` / `agent_runtime.verifier`：businessStatus=success，summary：The supplied evidence supports that the conversation containing the most recent received text shows “A quick brown fox.” as a sent outgoing reply.
- 预算：maximum=12、admitted=9、attempted=9、denied=0、failed dispatch=0；写构成`{"launch_app": 2, "swipe": 2, "tap_on": 3, "input_text": 1, "kill_app": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。
- 本例kill显式args与invoke safe_replay/output：`{"app_id": "com.simplemobiletools.smsmessenger"}`，step `agent-kill_app-19` / events#63。
- Send `agent-tap_on-14`结束 `2026-11-10T21:25:32.669948Z`；官方开始 `2026-11-10T21:26:20.273842+00:00`；宿主间隔 **47.604秒**，并非设备provider时间字段。

**期望 vs 实际：** 共享sent provider应有+17594820731的A quick brown fox.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。

**直接失败：** 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**根因置信度**
- **已证实**
  - events43/45打开正确最近会话；step12 input_text+step13 assert_state核对正文；step14（events51）点Send；steps16/17/18核对消息体/成功标识/可视发送状态。
  - 9/12 admitted、0 denied，非预算/timeout失败；kill step19成功（audit37→38），native returned audit41，官方之后评价0。
  - 初始化sms.py71-112最后插入params.number的非目标正文并按inbox检查；实际列表与目标入站符合，不存在本例选错most recent的证据。
  - 本例kill的原events#63显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅47.604秒（宿主事件时钟），小于300秒。
- **强推断**
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- 责任层：主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误；次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/082-SimpleSmsReplyMostRecent/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。SMS evaluator以logging.info记录messages，但该例root/absl effectiveLevel30，records=[]不能推导sent为空。

**精确修复方案（未实施）**
- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**：`resources/skills/android-harness.md::Case Lifecycle (7-10)`, `drivers/android/_uiautomator2.py::kill_app (103-107)`, `src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)`, `android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`。未来正式版本必须显式解决native要求最终kill与官方要求评分时前台app的冲突：声明可延迟teardown的业务完成/评分屏障，在官方评价后执行原kill行为；若仍要求原样完整native先返回则该组合需报告为不兼容，不能悄悄重启app凑in_correct_app、删除该rubric或改写r4分数。新边界须版本化且不绕过完整native/verifier证据。
- **P1 / harness诊断owner**：`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics`, `src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`。仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**
- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**逐例FSQ核对问题 / 当前harness侧结论**
- confirm：收件人/正文正确，发送后气泡checkmark/空composer；native verifier success，official0。
- confirm：本例kill显式目标包及invoke output均com.simplemobiletools.smsmessenger。
- disagree：将official0解释成错号码、仅草稿或未发送；无此证据。
- disagree：将kill描述为清空Telephony sent数据库；源码仅app_stop。
- unknown：actual was_sent/in_correct_app分量；ROLE_SMS holder及provider.date。
- confirm：收件人、正文与已发送视觉状态正确；disagree：错号码/停草稿/未点击发送解释。
- unknown：请逐例核对评分时current_package与匹配sent row是否有既存证据；如无，应保留“foreground强推断+provider/role/date缺证”，不能将其升级唯一已证实根因。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 084 SimpleSmsSend — reward 0.0

**公开goal：** Send a text message using Simple SMS Messenger to +16597910719 with message: Beauty is in the eye of the beholder.

**约束与初始化**
- recipient：+16597910719
- body：Beauty is in the eye of the beholder.
- actualSend：必须已发送，不仅输入；保持指定Simple SMS Messenger app的官方前台要求。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2/sources/000-goal.txt`。

**官方判据：** SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。
- 冻结源 `task_evals/common_validators/sms_validators.py:93-152,211-276`。
- 冻结源 `task_evals/single/sms.py:28-34`。
- 冻结源 `env/setup_device/apps.py:406-433`。
- 冻结源 `env/adb_utils.py:1426-1446`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-084-20261110T213010Z-5fd1d2/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- `agent-tap_on-18` / events#57 / `/steps/17`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_send_message"}}`。
- `agent-assert_visible-20` / events#61 / `/steps/19`：passed；`{"locator":{"text":"+16597910719"},"optional":false}`。
- `agent-assert_visible-21` / events#63 / `/steps/20`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_message_body","text":"Beauty is in the eye of the beholder."},"optional":false}`。
- `agent-assert_visible-22` / events#65 / `/steps/21`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_success"},"optional":false}`。
- `agent-kill_app-23` / events#67 / `/steps/22`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- 原UI `artifacts/tools/000015-ui_snapshot.json`：收件人输入+16597910719。
- 原UI `artifacts/tools/000017-ui_snapshot.json`：确认收件人后会话header同号码。
- 原UI `artifacts/tools/000019-ui_snapshot.json`：发送前composer含精确Beauty...正文。
- 原UI `artifacts/tools/000021-ui_snapshot.json`：发送后正文在thread_message_body，composer清空；kill prepare截图右侧气泡带checkmark。
- 独立读像素：`artifacts/screenshots/screenshot-agent-kill-app-23-prepare-before-action-1-5cb61d0fbe2d.png`（相对该例nativeRunPath）。
- 原task result `/steps/4` / `agent_runtime.runner`：businessStatus=success，summary：Sent “Beauty is in the eye of the beholder.” to +16597910719 using Simple SMS Messenger and verified the message and sent-success indicator in the conversation.
- 原task result `/steps/5` / `agent_runtime.verifier`：businessStatus=success，summary：The supplied execution evidence confirms that the conversation with +16597910719 shows “Beauty is in the eye of the beholder.” as a sent outgoing message.
- 预算：maximum=12、admitted=11、attempted=11、denied=0、failed dispatch=0；写构成`{"launch_app": 2, "swipe": 2, "tap_on": 4, "input_text": 2, "kill_app": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。
- 本例kill显式args与invoke safe_replay/output：`{"app_id": "com.simplemobiletools.smsmessenger"}`，step `agent-kill_app-23` / events#67。
- Send `agent-tap_on-18`结束 `2026-11-10T21:31:47.712915Z`；官方开始 `2026-11-10T21:32:22.086591+00:00`；宿主间隔 **34.374秒**，并非设备provider时间字段。

**期望 vs 实际：** 共享sent provider应有+16597910719的Beauty is in the eye of the beholder.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。

**直接失败：** 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**根因置信度**
- **已证实**
  - events45输入号码→49确认→53输入正文→57点Send；native steps20-22依次验证号码/正文/thread_success成功。
  - 11/12 admitted、0 denied，无预算阻断；kill23成功（audit45→46），native return49；官方之后scalar0。
  - 无来源内容间接检索，本例公共goal直接给号码和正文，视觉轨迹逐项一致。
  - 本例kill的原events#67显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅34.374秒（宿主事件时钟），小于300秒。
- **强推断**
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- 责任层：主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误；次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/084-SimpleSmsSend/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。SMS evaluator以logging.info记录messages，但该例root/absl effectiveLevel30，records=[]不能推导sent为空。

**精确修复方案（未实施）**
- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**：`resources/skills/android-harness.md::Case Lifecycle (7-10)`, `drivers/android/_uiautomator2.py::kill_app (103-107)`, `src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)`, `android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`。未来正式版本必须显式解决native要求最终kill与官方要求评分时前台app的冲突：声明可延迟teardown的业务完成/评分屏障，在官方评价后执行原kill行为；若仍要求原样完整native先返回则该组合需报告为不兼容，不能悄悄重启app凑in_correct_app、删除该rubric或改写r4分数。新边界须版本化且不绕过完整native/verifier证据。
- **P1 / harness诊断owner**：`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics`, `src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`。仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**
- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**逐例FSQ核对问题 / 当前harness侧结论**
- confirm：收件人/正文正确，发送后气泡checkmark/空composer；native verifier success，official0。
- confirm：本例kill显式目标包及invoke output均com.simplemobiletools.smsmessenger。
- disagree：将official0解释成错号码、仅草稿或未发送；无此证据。
- disagree：将kill描述为清空Telephony sent数据库；源码仅app_stop。
- unknown：actual was_sent/in_correct_app分量；ROLE_SMS holder及provider.date。
- confirm：收件人、正文与已发送视觉状态正确；disagree：错号码/停草稿/未点击发送解释。
- unknown：请逐例核对评分时current_package与匹配sent row是否有既存证据；如无，应保留“foreground强推断+provider/role/date缺证”，不能将其升级唯一已证实根因。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 085 SimpleSmsSendClipboardContent — reward 0.0

**公开goal：** Send a message to +15459061746 with the clipboard content in Simple SMS Messenger

**约束与初始化**
- recipient：+15459061746
- bodySource：公开goal只给clipboard source，不能把oracle params.message告诉future agent；实际在消息框长按Paste得到I think, therefore I am.。
- actualSend：粘贴来源内容后必须点击Send，正文变成气泡且composer清空。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370/sources/000-goal.txt`。

**官方判据：** SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。
- 冻结源 `task_evals/common_validators/sms_validators.py:93-152,211-276`。
- 冻结源 `task_evals/single/sms.py:158-170`。
- 冻结源 `env/setup_device/apps.py:406-433`。
- 冻结源 `env/adb_utils.py:1426-1446`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-085-20261110T213259Z-0e4370/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-launch_app-3` / events#23 / `/steps/2`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- `agent-tap_on-20` / events#61 / `/steps/19`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_send_message"}}`。
- `agent-assert_visible-22` / events#67 / `/steps/21`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_message_body","text":"I think, therefore I am."},"optional":false}`。
- `agent-assert_visible-23` / events#69 / `/steps/22`：passed；`{"locator":{"text":"+15459061746"},"optional":false}`。
- `agent-assert_with_ai-24` / events#71 / `/steps/23`：passed；`{"prompt":"Verify the conversation with +15459061746 shows the outgoing sent message 'I think, therefore I am.' (the exact text pasted from the clipboard), not merely text remaining in the composer. Check the message bubble and sent status indicators.","optional":false}`。
- `agent-kill_app-25` / events#73 / `/steps/24`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- 原UI `artifacts/tools/000015-ui_snapshot.json`：输入收件人+15459061746。
- 原UI `artifacts/tools/000019-ui_snapshot.json`：long press触发Paste菜单。
- 原UI `artifacts/tools/000021-ui_snapshot.json`：Paste后composer实见I think, therefore I am.。
- 原UI `artifacts/tools/000023-ui_snapshot.json`：Send后正文为消息体，composer为空；kill prepare截图有checkmark。
- 独立读像素：`artifacts/screenshots/screenshot-agent-kill-app-25-prepare-before-action-1-4faa741c2ea6.png`（相对该例nativeRunPath）。
- 原task result `/steps/4` / `agent_runtime.runner`：businessStatus=success，summary：Pasted the existing clipboard text, “I think, therefore I am.”, and sent it to +15459061746 in Simple SMS Messenger.
- 原task result `/steps/5` / `agent_runtime.verifier`：businessStatus=success，summary：The evidence supports that the conversation with +15459061746 shows a sent outgoing message matching the pasted clipboard text, “I think, therefore I am.”
- 预算：maximum=12、admitted=12、attempted=12、denied=0、failed dispatch=0；写构成`{"launch_app": 2, "swipe": 2, "tap_on": 5, "input_text": 1, "long_press_on": 1, "kill_app": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。
- 本例kill显式args与invoke safe_replay/output：`{"app_id": "com.simplemobiletools.smsmessenger"}`，step `agent-kill_app-25` / events#73。
- Send `agent-tap_on-20`结束 `2026-11-10T21:34:46.873622Z`；官方开始 `2026-11-10T21:35:37.742154+00:00`；宿主间隔 **50.869秒**，并非设备provider时间字段。

**期望 vs 实际：** 共享sent provider应有+15459061746的I think, therefore I am.且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。

**直接失败：** 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**根因置信度**
- **已证实**
  - sms.py168-170初始化设置clipboard=params.message；native events53长按、57点击Paste，没有通过业务调用/私有参数取正文。
  - step20点Send（events61）；steps22/23/24核对发送正文/收件人/可视checkmark，非仅草稿。
  - 12/12 admitted且0 denied：本例exhausted=true只是恰好用完，发送及kill25均成功（audit49→50），native returned53；不能把exhausted标签当因果。
  - 本例kill的原events#73显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅50.869秒（宿主事件时钟），小于300秒。
- **强推断**
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- 责任层：主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误；次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/085-SimpleSmsSendClipboardContent/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。SMS evaluator以logging.info记录messages，但该例root/absl effectiveLevel30，records=[]不能推导sent为空。

**精确修复方案（未实施）**
- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**：`resources/skills/android-harness.md::Case Lifecycle (7-10)`, `drivers/android/_uiautomator2.py::kill_app (103-107)`, `src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)`, `android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`。未来正式版本必须显式解决native要求最终kill与官方要求评分时前台app的冲突：声明可延迟teardown的业务完成/评分屏障，在官方评价后执行原kill行为；若仍要求原样完整native先返回则该组合需报告为不兼容，不能悄悄重启app凑in_correct_app、删除该rubric或改写r4分数。新边界须版本化且不绕过完整native/verifier证据。
- **P1 / harness诊断owner**：`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics`, `src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`。仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。

**未来验证（全部未执行）**
- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**逐例FSQ核对问题 / 当前harness侧结论**
- confirm：收件人/正文正确，发送后气泡checkmark/空composer；native verifier success，official0。
- confirm：本例kill显式目标包及invoke output均com.simplemobiletools.smsmessenger。
- disagree：将official0解释成错号码、仅草稿或未发送；无此证据。
- disagree：将kill描述为清空Telephony sent数据库；源码仅app_stop。
- unknown：actual was_sent/in_correct_app分量；ROLE_SMS holder及provider.date。
- confirm：收件人、正文与已发送视觉状态正确；disagree：错号码/停草稿/未点击发送解释。
- unknown：请逐例核对评分时current_package与匹配sent row是否有既存证据；如无，应保留“foreground强推断+provider/role/date缺证”，不能将其升级唯一已证实根因。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。

## 086 SimpleSmsSendReceivedAddress — reward 0.0

**公开goal：** Text the address of the event to Gabriel Ibrahim that Oscar Mohamed just sent me in Simple SMS Messenger

**约束与初始化**
- recipient：Gabriel Ibrahim；contact picker显示其+19696338338，不能把源号码+14379969633当收件人。
- bodySource：从Oscar Mohamed刚发来的事件地址取得；实际读源号码会话789 E Oak St, Phoenix AZ 85006并发送该原文。
- contactEvidence：起始Oscar+号码Add to contacts编辑表单不等于联系人已保存；后续源会话只号码，source attribution证据不全。
- 初始化参考：`2023-10-15T15:34:00+00:00`；原初始化 `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/task-initialization.json`。
- goal原件：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0/sources/000-goal.txt`。

**官方判据：** SimpleSMSSendSms.is_successful读取content://sms/sent；was_sent对address去横线/空格后精确等于冻结number，body忽略大小写SequenceMatcher>=0.9，device_current_time_ms−row.date<=300000（没有非负下界）；最终AND评分时current activity提取包为com.simplemobiletools.smsmessenger。若get_state发现Sending前缀会抛异常；本例返回0且exception=null，非该异常。
- 冻结源 `task_evals/common_validators/sms_validators.py:93-152,211-276`。
- 冻结源 `task_evals/single/sms.py:173-243`。
- 冻结源 `env/setup_device/apps.py:406-433`。
- 冻结源 `env/adb_utils.py:1426-1446`。
- 冻结源 `utils/fuzzy_match_lib.py:20-50`。
- 冻结源 `utils/contacts_utils.py:39-70,80-107`。

**实际native因果链（原step/event）**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress`。
- execution：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0/execution-result.json`。
- events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-086-20261110T213626Z-b2c2e0/events.jsonl`；原task result：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/fsq-native/worker/fsq-task-result.private.json`。
- `agent-launch_app-1` / events#19 / `/steps/0`：passed；`{}`。
- `agent-press_key-3` / events#23 / `/steps/2`：passed；`{"key":"Back"}`。
- `agent-launch_app-5` / events#27 / `/steps/4`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- `agent-swipe-6` / events#29 / `/steps/5`：passed；`{"direction":"up"}`。
- `agent-input_text-9` / events#39 / `/steps/8`：passed；`{"locator":{"resourceId":"com.google.android.apps.nexuslauncher:id/input"},"text":"SMS","textType":"literal"}`。
- `agent-tap_on-11` / events#43 / `/steps/10`：passed；`{"target":"SMS Messenger"}`。
- `agent-tap_on-13` / events#47 / `/steps/12`：passed；`{"target":"+14379969633"}`。
- `agent-press_key-15` / events#51 / `/steps/14`：passed；`{"key":"Back"}`。
- `agent-tap_on-17` / events#55 / `/steps/16`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/conversations_fab"}}`。
- `agent-press_key-19` / events#61 / `/steps/18`：passed；`{"key":"Back"}`。
- `agent-input_text-23` / events#71 / `/steps/22`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message"},"text":"789 E Oak St, Phoenix AZ 85006","textType":"literal"}`。
- `agent-assert_state-24` / events#73 / `/steps/23`：passed；`{"element":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_type_message","text":"789 E Oak St, Phoenix AZ 85006"},"optional":false}`。
- `agent-tap_on-25` / events#75 / `/steps/24`：passed；`{"locator":{"resourceId":"com.simplemobiletools.smsmessenger:id/thread_send_message"}}`。
- `agent-assert_with_ai-27` / events#79 / `/steps/26`：passed；`{"prompt":"Verify Gabriel Ibrahim's conversation shows a sent outgoing message containing exactly '789 E Oak St, Phoenix AZ 85006', with a successful sent indicator and empty composer.","optional":false}`。
- `agent-kill_app-28` / events#81 / `/steps/27`：passed；`{"app_id":"com.simplemobiletools.smsmessenger"}`。
- 原UI `artifacts/tools/000002-ui_snapshot.json`：初始Add to contacts表单：Oscar/Mohamed/+1 437-996-9633与Save仍可见；不能当存库证明。
- 原UI `artifacts/tools/000014-ui_snapshot.json`：唯一源号码+14379969633的列表预览为完整地址。
- 原UI `artifacts/tools/000016-ui_snapshot.json`：源会话收到789 E Oak St, Phoenix AZ 85006，header只有号码。
- 原UI `artifacts/tools/000020-ui_snapshot.json`：new conversation picker只有Gabriel Ibrahim与+19696338338，确认目标收件映射。
- 原UI `artifacts/tools/000026-ui_snapshot.json`：进入Gabriel会话；最终assert/kill prepare原UI及截图确认发出地址与checkmark/空composer。
- 独立读像素：`artifacts/screenshots/screenshot-agent-kill-app-28-prepare-before-action-1-86499697bbc9.png`（相对该例nativeRunPath）。
- 原task result `/steps/5` / `agent_runtime.runner`：businessStatus=inconclusive，summary：Sent “789 E Oak St, Phoenix AZ 85006” to Gabriel Ibrahim and verified the outgoing message was successfully sent. The source conversation displayed only a phone number, so its attribution to Oscar Mohamed could not be confirmed.
- 原task result `/steps/6` / `agent_runtime.verifier`：businessStatus=success，summary：The evidence supports that Gabriel Ibrahim’s conversation shows a successfully sent outgoing message containing Oscar Mohamed’s event address: “789 E Oak St, Phoenix AZ 85006”.
- 预算：maximum=18、admitted=14、attempted=14、denied=0、failed dispatch=0；写构成`{"launch_app": 2, "press_key": 3, "swipe": 1, "input_text": 2, "tap_on": 5, "kill_app": 1}`；deadlineExceeded=False。计入setup/teardown与失败尝试，不增加原预算。
- 本例kill显式args与invoke safe_replay/output：`{"app_id": "com.simplemobiletools.smsmessenger"}`，step `agent-kill_app-28` / events#81。
- Send `agent-tap_on-25`结束 `2026-11-10T21:38:44.468881Z`；官方开始 `2026-11-10T21:39:24.855331+00:00`；宿主间隔 **40.386秒**，并非设备provider时间字段。

**期望 vs 实际：** 共享sent provider应有+19696338338的789 E Oak St, Phoenix AZ 85006且在设备5分钟窗内、评价时正确前台；actual UI已发送但之后kill，official0且分量未知。

**直接失败：** 实际UI收件人/正文/发送后气泡、checkmark和空composer均成立；native verifier success，但official scalar=0。不能把它改写为没有发送/错误号码。可证实存在发送后kill与评分前台判据的契约冲突；哪一个official合取项实际为false缺少component证据。

**根因置信度**
- **已证实**
  - sms.py216-239先add_contact(name1,target_number)，再add_contact(name2,new_random_number)，随后向name2_number注入地址；contacts_utils39-70用INSERT intent+find_and_click SAVE但不读回联系人。
  - 首次ui_snapshot仍Oscar预填表单；step3 Back离开；不能声称Oscar持久化成功，也不能把初始化残留页面导致的姓名未显示一概归为agent遗漏。
  - events47打开源号码读地址；65选择Gabriel；71输入同地址；75点Send；step27 AI+原截图证明Gabriel正确已发送。
  - 14/18 admitted、0 denied，无预算阻断；kill28成功（audit55→56），native return59；主runner因Oscar来源未确认写inconclusive，但native verifier竟称success。official只按sent+foreground判定，不把runner此source attribution状态当0条件。
  - 本例kill的原events#81显式tool_arguments.app_id=com.simplemobiletools.smsmessenger，kill invoke及输出同包，不是从默认app猜测；Send动作结束到evaluator started仅40.386秒（宿主事件时钟），小于300秒。
- **强推断**
  - 初始化保存Oscar的UI流程未完成或未持久化是强推断：初始还在Add to contacts表单，后续源会话只有号码且picker仅Gabriel；但也可能UI缓存/保存后仍停留，必须读回contacts才可区分。
  - native verifier“支持Oscar来源”的结论超出保存联系人证据；这不会自动解释official0，官方继承谓词不检验Oscar名称归属。
  - 原生skill规定最终kill；本例kill dispatch succeeded且匹配冻结FSQ driver::kill_app调用app_stop（103-107），harness评分在完整native返回之后；中间无重新launch。因此in_correct_app评分时为false是强推断。
  - UI显示sent checkmark/空composer使发送业务完成证据很强；但UI不是content://sms/sent原始行，不能仅凭它断言was_sent在provider上为true。
- **无法确认与备选**
  - 没有评分时activity/package、sent provider行或ROLE_SMS holder快照；diagnostic componentResults=not_provided、records=[]，不能唯一确认foreground而排除provider/时间/角色。
  - frozen setup源码apps.py406-433设置secure sms_default_application并点Set as default；每题initialize234-253只off airplane+clear sms/threads+读设备time/sent，不校验/重建ROLE_SMS。没有本例role holder证据，不应指控默认SMS角色错误。
  - kill_app只app_stop，不清Telephony provider；official query发生在kill后仍向共享provider读sent，并非读Simple SMS内存。不能声称kill擦除了已发数据库记录。
  - 发送动作→官方调用的宿主事件间隔小于5分钟（见actualTrace.timing）；因此“业务执行太久超过5分钟”没有证据。仍缺provider.date及get_android_time原值，不能由宿主间隔替代设备时间窗，也不能臆断timezone。
- 责任层：主候选：harness×FSQ生命周期契约不兼容（强推断）；非已发送业务错误；次要：official scalar诊断不可区分foreground/provider/date/role（已证实缺证）。
- 官方diagnostic：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/086-SimpleSmsSendReceivedAddress/raw-private/evaluator-diagnostics.json`；returned=returned、reward=0.0、exception=None、componentResults={"status": "not_provided", "source": "scalar_return_interface"}、records=[]。SMS evaluator以logging.info记录messages，但该例root/absl effectiveLevel30，records=[]不能推导sent为空。

**精确修复方案（未实施）**
- **P0 / harness生命周期契约owner + FSQ生命周期owner；不改官方rubric**：`resources/skills/android-harness.md::Case Lifecycle (7-10)`, `drivers/android/_uiautomator2.py::kill_app (103-107)`, `src/fsq_androidworld_eval/fsq_runner.py::run episode scoring boundary (330-373)`, `android_world.task_evals.common_validators.sms_validators.SimpleSMSSendSms.is_successful (255-276)`。未来正式版本必须显式解决native要求最终kill与官方要求评分时前台app的冲突：声明可延迟teardown的业务完成/评分屏障，在官方评价后执行原kill行为；若仍要求原样完整native先返回则该组合需报告为不兼容，不能悄悄重启app凑in_correct_app、删除该rubric或改写r4分数。新边界须版本化且不绕过完整native/verifier证据。
- **P1 / harness诊断owner**：`src/fsq_androidworld_eval/evaluator_diagnostics.py::EvaluatorDiagnostics`, `src/fsq_androidworld_eval/fsq_runner.py::official evaluator boundary`。仅在私有评价边界保留只读component证据：current package/activity、匹配sent记录的address/body/date及设备当前time、was_sent与in_correct_app布尔；不送给agent、不额外调用is_successful、不重放本题。scalar诊断不足时不能宣称唯一0分原因。
- **P1 / harness/AndroidWorld初始化owner**：`android_world.utils.contacts_utils.add_contact (39-70)`, `android_world.task_evals.single.sms.SimpleSmsSendReceivedAddress.initialize_task (216-239)`。初始化联系人后以既有list_contacts只读校验name→number落库并等待界面退出，再交付业务agent；失败应归初始化而不是要求future agent猜源联系人。不要修改SMS成功rubric或把私有源号码直接泄给future agent。
- **P1 / FSQ verifier owner**：`FSQ native verifier::evidence scope`, `FSQ main runner source-attribution evidence`。verifier区分“号码会话读取到地址且已发给Gabriel”与“Oscar联系人映射已证实”，不能根据初始化预填表单/goal断言联系人保存成功；保持unknown直到公开UI可确认。

**未来验证（全部未执行）**
- 纯离线合取判据fixture分别固定was_sent真/假、foreground真/假，断言“已发送+错前台”仍按现有rubric=0，保持r4分数不变。
- 未来设备单次受控发送后在私有评价边界保留provider/address/body/date及current package、ROLE_SMS holder；仅一次官方评价，评后再清理；对比持久化与foreground两项，不能重启app凑分、私加预算或同题重试。

**逐例FSQ核对问题 / 当前harness侧结论**
- confirm：收件人/正文正确，发送后气泡checkmark/空composer；native verifier success，official0。
- confirm：本例kill显式目标包及invoke output均com.simplemobiletools.smsmessenger。
- disagree：将official0解释成错号码、仅草稿或未发送；无此证据。
- disagree：将kill描述为清空Telephony sent数据库；源码仅app_stop。
- unknown：actual was_sent/in_correct_app分量；ROLE_SMS holder及provider.date。
- unknown：Oscar联系人是否保存；初始预填表单不是成功落库证据。
- confirm：Gabriel→+19696338338的picker映射、原地址、发送气泡checkmark/空composer；disagree：把源+14379969633当错收件人，或把本例称未发送。
- unknown：Oscar在Add to contacts预填表单是否真实保存？contacts_utils39-70无readback；请不要将表单视作联系人数据库成功。native verifier是否超出了source-attribution证据？
- unknown：在已发送业务完成之后，official0到底来自foreground还是provider/date/role？无raw sent/activity分量时保持强推断，不能改分。
- 双侧状态：**pending parent bilateral reconciliation**；以上不等于FSQ owner已确认。


## 后续：已逐节阅读FSQ原slice后的harness侧核对

本节是在FSQ六MD落地后，对本slice的13节逐一核对；前文pending指父agent尚未整合双方最终报告。本节状态为 **harness侧阅读/答复完成，父agent双侧整合仍pending**，不冒称FSQ已接受分歧。原分数、原产物不变。

已读取 `fsq-case-notes/calendar-retro.md` 068–078各指定节与 `sms-system-navigation.md` 081/082/084/085/086各节；以下逐例给理由与剩余unknown。

### 068：已核对：主因一致，官方日期与三标题生成机制补足。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:122-153`。
- **已核对/同意**：text28 missing、月网格有像素无数字text、top_value/Go to date只月年、重复OK无日级进展；原step10及后续循环一致。
- **已核对/同意**：main summary非标题、valid仅结构有效、不是no events；与IR官方0一致。
- **分歧或官方源补足**：本fixture官方日期可确认2023-10-28，不再笼统未知：initialize_proto先用绝对date构造state，_maybe_replace_date随后只改公开goal参数（information_retrieval.py82-97）。
- **分歧或官方源补足**：官方相关state含3个title_without_replacement，不是params.title=Birthday party（tasks.textproto362-405；proto_utils336-403）。
- **仍未知**：生成后三标题完整proto未留；月格Date night完整可读，Game nig/Product仅截断；不事后补交或向future agent泄漏。
- **仍未知**：数字节点缺失在原可访问性层与压缩层各占多少未区分；不能称压缩器确定删掉。

### 069：已核对：未发生Delete，导航循环主因一致；官方删除集合已闭合。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:155-185`。
- **已核对/同意**：step11/21 text27 missing、裸More options missing、三轮Go to date仅月年；无Delete事实一致。
- **分歧或官方源补足**：冻结row_objects是27日11:00 Review session for Project X、12:00 Catch up on Project X、21:00 Call with the Team；均非循环且同日结束。官方删除这3目标id并保持20噪声不变（calendar.py264-288；sqlite_validators348-369,73-115）。不把截图截断字当完整集合。
- **仍未知**：未存真实评分DB before/after，故副作用集合未知；但轨迹未有删除，足以支持业务未完成，不猜错删。

### 070：已核对：已到正确Monday、Delete均派发前拒绝；相对日期本fixture已确认。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:187-219`。
- **已核对/同意**：step16 tap相邻16 passed但仍15，箭头step19到Oct16，step21打开00:00事件；23/24 Delete未forward，不能写成删除后未确认。
- **分歧或官方源补足**：this Monday在本冻结实例明确Oct16，而非仍待推定：params day16/day_of_week Monday及calendar.py367-418取参考15后1..6日并格式化；两目标为00:00–01:00和10:00–10:30，无循环/跨日。一般语言周界不扩成此例评分未知。
- **仍未知**：Delete若获准后的真实确认成本未执行；不能宣称固定12预算一定不可行或加预算必要。

### 071：已核对：月年误用、过晚发现日picker，无删除；25输入未执行。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:221-252`。
- **已核对/同意**：step11 text24 missing；step25 input_text在dispatch前拒绝，与74已执行但不提交严格区分。
- **分歧或官方源补足**：本fixture唯一目标2023-10-24 23:00–23:30 Workshop on Project X，不跨午夜、repeat_interval/repeat_rule均0，20噪声；官方以目标id删除完整性评分（calendar.py323-364及264-288）。这些冻结初始化事实可闭合，不把未来边界混成已存未知。
- **仍未知**：无评分DB后态或实际Delete确认路径；不能称错删、23h换算错误或输入24被回滚。

### 072：已核对：未到目标日，主因一致；at的既有官方机制可补足。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:254-285`。
- **已核对/同意**：Go to date仅Oct/2023、两轮OK不选27日；未发生20:00筛选，不能归因12/24时换算或时区。
- **分歧或官方源补足**：官方非评分时对UI动态过滤：tasks.textproto239-275放入20:00 Product demo持续15min，success取相关title；噪声check_event_conditions组合绝对datetime并排除覆盖该时刻，含端点（calendar_utils220-311）。故此例expected可由冻结state模板确认，不能把official规则仍写成完全未知。
- **分歧或官方源补足**：公开at自然语言的更普遍解释不在此例执行根因中；不把私有标题注入future agent。
- **仍未知**：无真实日详情访问，无法评估agent到达后会否正确处理跨时段/端点；原失败仍在导航。

### 074：已核对：NumberPicker passed仍15的精确细节双侧一致；官方区间生成/提取补足。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:287-320`。
- **已核对/同意**：step11 input20真正succeeded，但before/after原XML选中15、afterPNG仍15；step12 OK后Sun15；箭头逐日16→17→18，后两次拒绝，未到Friday。
- **已核对/同意**：底层可能set_text/焦点/提交校验等，尚不能断言先写入再被应用重置。
- **分歧或官方源补足**：Friday本例为Oct20：绝对date冻结后才重措辞。tasks.textproto964-1006相关事件从16:15开始持续1h，噪声条件>=16:15与<=20:00，实现对起止时点OR检查跨度（calendar_utils289-324）；official success只是取相关state.title，非重新执行overlap/within过滤。
- **分歧或官方源补足**：FSQ preplan写overlapping确为可见具体化，但不能当本轮扣分原因；未来仍保留既有rubric，不能为分数改start-only或overlap定义。
- **仍未知**：NumberPicker值没变的底层分支；未存生成后所有噪声，跨午夜范围的普遍语义不能仅由本例scalar穷尽。

### 076：已核对：导航失败而非strict-after错；修正版官方相关事件可确认。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:322-353`。
- **已核对/同意**：无day29节点；月年循环、text29 missing与预算截断一致；主preplan保留strict-after/当天上界/tie规则。
- **分歧或官方源补足**：冻结修正版tasks.textproto857-894以同一hour生成Oct29 21:30 Grocery Shopping，持续3h至次日00:30；只有1个相关title，噪声排除同日阈值后项。官方expected并非完全未知，长事件只因结束跨日不应排除。
- **分歧或官方源补足**：我方独立month PNG可见29格Grocery Shopping完整标题，但无start时间；不是native已完成时间筛选。
- **仍未知**：没有目标日时间详情读取；未存生成后完整候选state，不能声称agent实际错用了>=或end排序。

### 078：已核对：候选排序证据足够强而summary未答；官方预设候选已确认，clock来源需补充。
- 对照FSQ节：`fsq-case-notes/calendar-retro.md:355-388`。
- **已核对/同意**：完整15 Sunday段到16 Monday、早晨三项过去、22:35 Board meeting早于22:57；详情证实同日22:35–22:45。误拉通知栏和重复详情/exists不能增加earliest证明。
- **已核对/同意**：不能因预算耗尽/kill拒绝抹掉已取证业务候选；main inability直接导致答案不匹配。
- **分歧或官方源补足**：官方模板tasks.textproto125-168明确将Board meeting放在Oct15 22:35，并排除当日15:30到该时刻的噪声；因此本例官方expected=Board meeting可事后确认，不是仍无标准答案。不得替模型补交。
- **分歧或官方源补足**：请保留clock.text15:35而content-desc23:35的不一致；实际通知截图可见15:35 SunOct15。可以否定已证明timezone漂移，但不能省掉两来源差异。
- **仍未知**：agent内部是否采信content-desc23:35、agenda隐藏过滤实际状态；无证据把它确定为动机或时区根因。

### 081：已核对：两侧一致，未发生输入/Send，与四例已发送分歧分组严格分开。
- 对照FSQ节：`fsq-case-notes/sms-system-navigation.md:107-121`。
- **已核对/同意**：Google Messages误入口、composer冗余tap占第12write、两次input被before-forward拒绝；最终正确号码空composer。
- **已核对/同意**：input_text自带click/clear/set_text，单独tap无需；预算拒绝后重试不能恢复配额。
- **分歧或官方源补足**：Google Messages不是默认的提示不能证明Simple SMS Messenger不是ROLE_SMS holder；当前底层launch未到前台原因未确认。
- **仍未知**：launch app_start成功后仍launcher的SDK原因；固定12上限最短完整UI路径仍需未来设备验证，不加预算。

### 082：已核对发送事实；补足foreground AND主候选，并收窄recency的评分分支。
- 对照FSQ节：`fsq-case-notes/sms-system-navigation.md:123-137`。
- **已核对/同意**：列表首行+17594820731与原来信、exact正文→Send→气泡checkmark/空composer均成立；不能推断错人或停草稿。
- **分歧或官方源补足**：官方SimpleSmsReplyMostRecent继承SimpleSMSSendSms，不在is_successful重算recency：sms.py71-112最后插入params.number，评分只查该number/body的sent+foreground（sms_validators255-276）。同分钟tie-break是UI识别风险，不是独立扣分谓词。
- **分歧或官方源补足**：本例kill19.invoke.safe_replay_params及harness_output显式app_id=SMS包；停止后评分，foreground冲突是强推断主候选，不宜只列provider/时钟未知而漏此AND。Send结束至评价47.604秒，不能说总耗时超过5分钟。
- **仍未知**：actual sent row/date、评价device now、current activity与role holder无存量；宿主47.604秒不代provider.date。

### 084：已核对新会话confirm/正文/发送；补足foreground AND主候选。
- 对照FSQ节：`fsq-case-notes/sms-system-navigation.md:139-153`。
- **已核对/同意**：号码输入并confirm、正文变右侧气泡、checkmark/空composer；无预算拒绝，不支持未confirm/未发。
- **分歧或官方源补足**：kill23.invoke.params与output显式com.simplemobiletools.smsmessenger；官方sent AND foreground，先app_stop后完整native返回再评分，foreground为强推断主候选。不是已知app/provider提交断层。
- **分歧或官方源补足**：Send结束至评价34.374秒，只排执行过久解释，不证明provider.date匹配；app_stop本身不删Telephony sent库。
- **仍未知**：缺sent row、current activity、ROLE_SMS及设备date原值；不能写唯一已证实foreground0因或确定持久化失败。

### 085：已核对真实Paste来源与Send，无预算拒绝；初始化来源与foreground判据补足。
- 对照FSQ节：`fsq-case-notes/sms-system-navigation.md:155-169`。
- **已核对/同意**：long_press→Paste→composer→Send→同文sent气泡链成立，无手输/重设clipboard；12/12但denied0，kill成功。
- **分歧或官方源补足**：官方初始化clipboard来源明确sms.py168-170→adb_utils.set_clipboard_contents(params.message)；这确认预期初始化操作，不等于保存了系统clipboard readback。
- **分歧或官方源补足**：kill25.invoke显式停SMS；官方sent AND foreground主候选同上。发送结束至评价50.869秒；不能套budget exhausted标签或执行超过5min解释。
- **仍未知**：初始化clipboard系统readback、sent provider与foreground/role/date实值均未留；不因body与params相符跳过provider边界。

### 086：部分同意，存在明确官方判据分歧：source/contact身份不是本例直接评分项。
- 对照FSQ节：`fsq-case-notes/sms-system-navigation.md:171-185`。
- **已核对/同意**：Oscar预填form与后续同号码address强关联但非保存成功证明；Gabriel picker映射、原地址、sent气泡checkmark/空composer成立。保留main inconclusive/native verifier success差异。
- **分歧或官方源补足**：L179将来源身份/联系人绑定列为official0的直接备选不符冻结源码：SimpleSmsSendReceivedAddress没有is_successful override，沿用sms_validators255-276，仅sent number/body/device-window AND foreground；联系人只在sms.py216-239 initialize使用。因此Oscar attribution可影响业务证据，但不是直接扣分谓词。
- **分歧或官方源补足**：“未保存表单”可作UI描述；联系人DB确定未保存仍无readback，只是强推断。contacts_utils39-70仅UI SAVE无确认，不能将fixture候选当已证明official0因。
- **分歧或官方源补足**：kill28.invoke显式停SMS；foreground冲突为强推断主候选；Send结束至评价40.386秒。
- **仍未知**：Oscar联系人是否真实持久化、source姓名归属、actual sent row/date/role/current activity缺证；已发送事实、初始化异常候选与官方0归因必须三层分离。

