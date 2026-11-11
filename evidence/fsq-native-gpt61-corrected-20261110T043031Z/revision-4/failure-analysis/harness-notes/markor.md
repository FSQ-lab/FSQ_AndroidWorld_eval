# Harness 离线逐例调查：Markor / Notes IR / OpenApp / OsmAnd

**范围：** 23、24、27、29、30、32、33、36、40、41、44，共11唯一案例。**全部11例已逐例完成双侧独立材料比对，各节列一致/分歧/剩余unknown；本回函尚待FSQ owner确认，不冒称对侧已接受。**

仅阅读存量原goal、初始化、官方诊断、native轨迹/audit/UI XML与关键已存截图。没有设备/ADB/Appium probe、没有模型业务调用、没有重跑任务/评分/测试/构建/lint/安装；没有改代码或原产物。精确路径、JSON pointer、动作参数、原UI文本及源行详见同名JSON。

## 版本与判定边界

- **O/** = manifest实际oracle installed根：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world`；记录的installed SHA为`0ac9428da2e9d78d0303c44c682184268e708a3116134646401d5c8425671b94`。只读这一安装源，不用当前repo任务副本替代。
- **F/** = `/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent`；driver/skill文件引用FSQ owner既存`failure-analysis/fsq-evidence-index.json#/source_identity`的逐文件匹配结论；未新做泛hash。
- harness当前`src/...`行号明确标为当前可读源，未新做hash承诺；原episode request/result/audit与复制worker-site给关键行为绑定。
- 11例官方diagnostic均正常returned、exception=null、仅标量子分未提供。native内部verifier不是官方成绩。27保留**0.5部分完成**，其余10例0。
- 固定预算是native write capability dispatch，不是业务动作/turn：setup、失败查找、kill也计；UI观察不计，input_text一单元内部clear+set。所有11例deadlineExceeded=false。不得用“timeout/预算不够”替代具体因果。
- 主答案严格取唯一main runner的`tool_output.summary`。40的mainAnswer有效，不属于exact_main_summary契约异常；有效来源≠数值业务答案。
- Markor官方常量为`/storage/emulated/0/Documents/Markor`（大写M）；部分UI显示小写markor。初始化目标真实可见且27有note给分支持，不能未经设备证据把大小写差异另立为根因。

## 概览

| index | task | reward | 直接缺口 | write / max |
|---:|---|---:|---|---:|
| 23 | MarkorAddNoteHeader | 0.0 | 重命名根本未完成；12次admitted全部用尽后Back和teardown被拒。 | 12/12 |
| 24 | MarkorChangeNoteContent | 0.0 | 重命名提交被拒，旧文件未完成改名，因此即便原文件内容已更新也拿0。 | 12/12 |
| 27 | MarkorCreateNoteAndSms | 0.5 | 部分完成；SMS业务提交未发生；note1/SMS0为强推断而非独立子分日志，不能称全失败。 | 18/18 |
| 29 | MarkorDeleteAllNotes | 0.0 | 删除事务未发生，末态仍有笔记，正对官方非空列表给0。 | 14/14 |
| 30 | MarkorDeleteNewestNote | 0.0 | 删除确认未派发，不能满足恰少一份。 | 10/10 |
| 32 | MarkorEditNote | 0.0 | 显式Save未forward；当前buffer正确但持久状态未证且official为0，最终文件字节/auto-save未知。 | 12/12 |
| 33 | MarkorMergeNotes | 0.0 | 精确输出路径与内容两个独立充分失败：新名带默认.md，重开为空；不是仅缺最终Save或预算耗尽。 | 26/78 |
| 36 | MarkorTranscribeVideo | 0.0 | 没有创建转录文件；上游播放器未及时暂停/定位，短视频仍在流逝，控制条快照过期后重复查找失败，未建立完整有序转录。 | 17/20 |
| 40 | NotesTodoItemCount | 0.0 | interaction_cache收到有效task_run_v1的叙述summary，float解析失败由IR evaluator捕获ValueError并返回0。早期误开其他笔记和启动绕路耗掉预算，正确folder已可见3个todo却未完成数量确认/数值提交。 | 10/10 |
| 41 | OpenAppTaskEval | 0.0 | 成功后的kill_app破坏active-app任务终态；不是没grant权限、没清tooltip、超预算或模型不会开Contacts。 | 6/10 |
| 44 | OsmAndTrack | 0.0 | 地点搜索恢复后没有执行剩余两站与保存，终态仍一草稿点；不足以满足3个有序trkpt文件条件。没有任何路线计算报错证据，不能归为规划引擎失败。 | 23/120 |

## 023 MarkorAddNoteHeader — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:315-360`。
- **已核对/一致：** 已核对：S11误用replace代insert→S13按已观测原文恢复→S19错进File settings→rename未发生，固定12额度只是最终阻断；根因/修法与FSQ的MM-PREPEND、MM-RENAME-PATH一致。
- **已核对/一致：** 只认Save dispatch通过，不冒称持久字节已验；50字符截断不代表尾文缺失。
- **分歧：** 无实质根因/修法分歧。
- **仍未知：** oracle时刻旧名目录项与正文原字节未采集；官方旧名存在分支为强推断。
- **仍未知：** launch_app停Launcher底层原因未决。

**原goal：** Update the Markor note 2023_08_10_neat_wolf.txt by adding the following text, along with a new blank line before the existing content: "RnI8sP34yDzJQbvkfplR", and rename it to busy_wolf_2023_07_23.txt.

**要求/官方rubric：** 先检查旧名必须不存在、新名必须存在；新文件精确匹配header+\n\n+original_content+\n。不是仅看编辑器前缀，也没有部分分。

**初始化：** 清空MARKOR_DATA，创建带末尾换行的原文Weekend plans: Hiking trip to Blue Mountain.及同名干扰文件；初始化冻结referenceTime=2023-10-15T15:34:00+00:00。step9实际看到了目标原文。

**官方源码：**
- `O/task_evals/single/markor.py:754-774`（MarkorAddNoteHeader.initialize_task）
- `O/task_evals/single/markor.py:784-806`（MarkorAddNoteHeader.is_successful）
- `O/utils/file_utils.py:555-584`（check_file_content exact bytes when exact_match=True）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/023-MarkorAddNoteHeader/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-023-20261110T171734Z-585061/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-2`：launch通过却仍在Launcher。
- `agent-ui_snapshot-9`：原文真实可见，header内容可从goal取得。
- `agent-input_text-11`：Move Home后调用的是清空再替换；此时原文被覆盖。
- `agent-ui_snapshot-12`：只剩header与空行，证实不是插入。
- `agent-input_text-13`：用刚读到的原文重建完整期望文本。
- `agent-tap_on-14`：Save调用通过。
- `agent-tap_on-19`：误入File settings而不是重命名入口。
- `agent-ui_snapshot-20`：实际是Wrap words/Font Size设置页，无Rename。
- `agent-press_key-21`：首个拒绝：第13个write，action_budget。

**预算/输出：** admitted 12/12，attempted 15，denied 3，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 6，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq41 `agent-press_key-21` (action_budget)；seq42 `agent-press_key-22` (action_budget)；seq43 `agent-kill_app-23` (action_budget)。

**期望与实际：** 内容补救曾输入正确组合且Save通过，但旧名仍在编辑标题、未进入/确认重命名，官方第一项“旧名消失”不满足。不能仅以UI截断文本证明落盘逐字一致。

**直接失败：** 重命名根本未完成；12次admitted全部用尽后Back和teardown被拒。

**根因分级：**
- **已证实：** 启动成功标签未对应前台，消耗2次launch+swipe+launcher tap后才真正进入Markor（steps1-7，共4个write）。
- **已证实：** 输入替换契约与“插入”预计划不一致，产生第13步重写补救；随后进入File settings，未找到rename。
- **已证实：** budget audit seq41/42/43拒绝Back/Back/kill；deadlineExceeded=false。
- **强推断：** 无重命名调用、旧名标题及official 0共同支持在is_successful的旧名存在分支返回0。diagnostic未提供分支日志，不能称已直接读取最终文件系统。
- **无法确认/备选与缺证据：** 未有oracle时刻文件内容/目录快照；最终精确字节与旧名分支是强推断而非独立私有文件转储。
- **无法确认/备选与缺证据：** 启动为何停在Launcher由FSQ owner核对；不能归咎旧AMK。

**责任层：** FSQ launch/text contract / FSQ UI flow selection / harness fixed dispatch budget amplifies

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 · FSQ skill/planner owner · `resources/skills/android-harness.md; drivers/android/_uiautomator2.py::input_text description; goal pre-plan`：** 把input_text的click/clear/set_text整字段替换语义告知planner。header任务先读取可见原文，用现有replacement写入header+指定换行+已观察原文，再Save；不把Move Home+input_text误当插入，不添加官方没有的“必须只用插入操作”验收。长文读不全时先取得完整UI证据，不能拿frozen私有params补内容。
- **P1 · FSQ planner/knowledge owner · `Markor rename flow using observed file-browser selection controls`：** Save后回到文件列表，长按当前精确文件名→action_rename_selected_item→输入新名→OK；不在File settings试探。只存公开app交互知识，不存任务答案。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线fake selector：input_text清空+set_text语义、header恢复文本组合及所需write预算均与计划一致；不改变12上限。
- 需设备的新题验证：设备新题：rename确认后从UI重开正确新名；官方单次oracle核对旧名不存在及新文件精确换行/末尾换行。

**给FSQ owner的逐例问题（pending）：**
- launch_app两次均passed却仍Launcher的具体u2调用语义？
- planner为何把replacement当插入，又为何认为File settings能重命名；是否prompt/skill缺少参数语义？

## 024 MarkorChangeNoteContent — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:363-406`。
- **已核对/一致：** 已核对：本例input_text replacement语义正确，不能套023 prepend根因；S20只是改名字段，S21/22 OK在forward前预算拒绝，直接缺口是rename未提交。
- **已核对/一致：** 同意MM-RENAME-COMMIT：修launch readiness、固定12内预留OK，不扩预算、不放宽为对话框目标名可见。
- **分歧：** 无实质根因/修法分歧。
- **仍未知：** 内容Save后实际落盘字节无私有读回；不能直接宣布内容子目标已官方通过。

**原goal：** Update the content of strong_jacket_h1hZ.txt to "inNqu8UNNtyXBHCZpYp7" in Markor and change its name to lively_fox_2023_03_22.md.

**要求/官方rubric：** 旧名不存在、新名存在，再由check_file_content判新文件内容；三者同时满足才1。官方没有“最终必须展示某屏”的额外评分条件。

**初始化：** 清空Markor目录；创建原名随机内容与噪声文件。step9读到pZwh1hZwvmPj5inNqu8U，符合现场初始化而非拿私有params猜原文。

**官方源码：**
- `O/task_evals/single/markor.py:671-690`（MarkorChangeNoteContent.initialize_task）
- `O/task_evals/single/markor.py:700-721`（MarkorChangeNoteContent.is_successful）
- `O/utils/file_utils.py:555-584`（check_file_content fuzzy default）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/024-MarkorChangeNoteContent/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-024-20261110T172032Z-0d04e0/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-2`：launch通过却仍Launcher。
- `agent-input_text-10`：替换为要求的新内容。
- `agent-ui_snapshot-12`：编辑器可见正确新内容。
- `agent-tap_on-13`：Save通过。
- `agent-long_press_on-16`：回文件列表长按精确旧名。
- `agent-ui_snapshot-19`：重命名对话框真实打开。
- `agent-input_text-20`：新名称进入new_name，但尚未提交。
- `agent-tap_on-21`：OK前write预算已满，未派发到设备。

**预算/输出：** admitted 12/12，attempted 15，denied 3，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 6，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq41 `agent-tap_on-21` (action_budget)；seq42 `agent-tap_on-22` (action_budget)；seq43 `agent-kill_app-23` (action_budget)。

**期望与实际：** 内容输入和Save已执行，rename仅填写输入框；OK两次均budget拒绝，不能把“键入新名”算改名完成。

**直接失败：** 重命名提交被拒，旧文件未完成改名，因此即便原文件内容已更新也拿0。

**根因分级：**
- **已证实：** 4个write才从Launcher进入Markor；此后编辑/Save/返回/长按/Rename/输入新名恰好耗完12。
- **已证实：** audit seq41/42/43拒绝OK重试及kill，deadline未到。
- **强推断：** official 0最可能由旧名仍在直接返回；缺最终目录转储但对话框未确认事实充分。
- **无法确认/备选与缺证据：** 无最终落盘字节或oracle分支日志。
- **无法确认/备选与缺证据：** 如果启动后置条件修复，能否在同预算下完成全部业务需未来设备验证，不能直接宣布必过。

**责任层：** FSQ launch postcondition / FSQ commit-aware planning / harness budget boundary

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 · FSQ planner owner · `Markor rename state tracking / goal pre-plan`：** 把rename的OK提交列为必须动作并在固定预算内规划；输入框文本不算完成。保留Save/提交动作优先于重复launch和无效retry。

**未来验证（只列方案）：**
- 无需设备的离线断言：预算离线回放在第12次admission后准确拒绝新write，不把拒绝的OK标成功。
- 需设备的新题验证：设备新题：全程预算12，内容编辑后完成rename OK；官方只评一次，核对旧名/新名/内容。

**给FSQ owner的逐例问题（pending）：**
- launch恢复为何重复相同launch而不是基于前台后置条件失败？
- planner能否在任务状态中区分new_name字段编辑与已提交rename？

## 027 MarkorCreateNoteAndSms — reward 0.5

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:409-459`。
- **已核对/一致：** 已核对：target Save的text/content-desc误配、Enter没确认收件人、confirm未forward、无Send；修复必须保留note已保存 AND SMS已发两个合取条件。
- **已核对/一致：** 新增已回原report确认：task.verification_goal仅剩SMS，漏独立note持久约束；此次没造成假success，但修复需分别举证。
- **已核对/一致：** 原kill默认目标Markor且因预算在forward前拒绝，没有杀SMS；0.5保留partial。
- **分歧/细化：** FSQ称无法断言哪个子项通过：同意不能作直接日志事实；harness依初始化清空SMS+全轨迹无Send+平均公式把note1/SMS0只列强推断，非已采集子分。
- **分歧/细化：** 收窄本报告旧的未来cleanup泛化：默认kill Markor本身不等于kill SMS；只有未来确实停止前台SMS时才有foreground风险，不是本例根因。
- **仍未知：** 没有组件日志/最终note字节/sent-table转储，故子分仍不提升为已证实。

**原goal：** Create a new note in Markor named fair_ant_XOdi.txt with the following text: Actions speak louder than words.. Share the entire content of the note with the phone number +13192815309 via SMS using Simple SMS Messenger

**要求/官方rubric：** (MarkorCreateNote + SimpleSMSSendSms)/2。note是精确路径存在+fuzzy正文；SMS需目标号码/body近似匹配的已发记录在时间窗内且当前前台是com.simplemobiletools.smsmessenger。0.5是完成一子任务，不是全失败。

**初始化：** 清空Markor，构造note子任务；SMS初始化关闭飞行模式并清空SMS/threads，避免旧记录给分。本次diagnostic仅标量返回0.5、无子分日志。

**官方源码：**
- `O/task_evals/composite/markor_sms.py:39-68`（MarkorCreateNoteAndSms.template/initialize_task/is_successful）
- `O/task_evals/single/markor.py:426-440`（MarkorCreateNote）
- `O/task_evals/common_validators/file_validators.py:199-226`（CreateFile.is_successful）
- `O/task_evals/common_validators/sms_validators.py:234-276`（SimpleSMSSendSms.initialize_task/is_successful）
- `O/utils/fuzzy_match_lib.py:20-50`（fuzzy_match 0.9）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/027-MarkorCreateNoteAndSms/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-027-20261110T172832Z-403bfd/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-2`：Markor launch仍Launcher。
- `agent-input_text-14`：按public goal的双句号输入正文。
- `agent-tap_on-17`：target Save用text精确查找失败；toolbar Save在UI是content-desc。
- `agent-tap_on-19`：用resourceId Save恢复通过。
- `agent-ui_snapshot-25`：Android分享面板确有完整双句号正文。
- `agent-input_text-28`：填写正确收件号码。
- `agent-press_key-29`：Enter调用通过但未确认收件人。
- `agent-ui_snapshot-30`：仍New conversation recipient entry，未进入发送。
- `agent-tap_on-31`：收件人confirm被预算拒绝，Send计划未执行。

**预算/输出：** admitted 18/18，attempted 20，denied 2，failed dispatch 1；deadlineExceeded=false。主runner TaskResult step 6，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq61 `agent-tap_on-31` (action_budget)；seq62 `agent-kill_app-32` (action_budget)。

**期望与实际：** note已创建/保存/分享且正文fuzzy可容忍句号；SMS只到收件人输入，未确认、无Send和已发记录。结合0.5，note=1/SMS=0为强证据推导，diagnostic本身未单独吐这两个数字。

**直接失败：** 0.5部分完成保留；SMS业务提交未发生是直接缺口，note1/SMS0只列强推断而非独立子分日志，不能称全失败。

**根因分级：**
- **已证实：** 18个write全部admitted，包括无效果的2次launch、launcher绕路、Save target失败及Enter未完成确认。
- **已证实：** audit seq61拒绝recipient confirm、seq62拒绝kill；未发生发送，deadlineExceeded=false。
- **已证实：** official reward为0.5且composite官方平均公式成立。
- **已证实（交叉核对新增）：** 原`report.json/task.verification_goal`只剩SMS已发送目标，遗漏独立note持久子目标；这次未因此伪报success，但未来必须保留两者合取。
- **强推断：** 子分note1/SMS0：轨迹没有SMS发送、但note保存与分享正文可见，且总分0.5。没有标量诊断以外的子分日志，须保留此证据级别。
- **无法确认/备选与缺证据：** 没有最终note私有字节或sent-table快照；不编造SMS provider/网络发送错误。
- **无法确认/备选与缺证据：** S32默认kill目标为Markor，且action_budget在forward前拒绝，没有杀SMS。仅未来确实停止前台SMS才有foreground风险，不能从默认kill Markor推导该风险已发生。

**责任层：** FSQ launch/locator contract / FSQ SMS recipient flow / harness fixed budget / FSQ composite verification-goal coverage loss

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 · FSQ skill/locator owner · `drivers/android/_uiautomator2.py::_selector; Markor/SMS UI flow`：** 根据UI属性使用Save的resourceId/accessibilityId，不把target当content-desc；SMS在收件框后点当前new_conversation_confirm，再检查compose/body并Send，Enter无状态变化不能算确认。
- **P1 · FSQ preplan/verification owner · `agent/_core.py::_augment_goal_only_task_with_pre_plan:155-159,201; agent/_verification_task.py::VerificationEvidenceBuilder.build:51-56`：** 保留公开复合goal的两个独立合取条件：精确命名note已保存 AND 全文SMS已发；分别检查证据，不让verification_goal只剩最后SMS动作。该遗漏不是本次未Send的直接原因，但完成短信后也不能据此忽略note。原kill默认Markor且被拒，不改写为已杀SMS。
- **P2 · harness reporting owner · `composite score reporting (private diagnostics only)`：** 继续保存数字0.5与已有标量诊断；若以后增加子项审计，必须在同一次官方评估中非侵入记录，不改变平均rubric也不向业务agent泄露子项oracle。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线：composite报告保留0.5；target精确text与accessibilityId区别；不把SMS收件输入成功当发送。
- 需设备的新题验证：设备新题：同18上限完成note、recipient确认、Send并保持SMS前台至单次官方评估；私有审计区分note与SMS两个条件。

**给FSQ owner的逐例问题（pending）：**
- 确认note1/SMS0推导；FSQ是否读到new_conversation_confirm但用Enter先试？
- text-only target Save与content-desc Save的语义是否已在tool schema说明？
- 未来SMS前台目标与强制kill_app如何按版本化协议协调，而非修改本次0.5？

## 029 MarkorDeleteAllNotes — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:462-509`。
- **已核对/一致：** 已核对：三份真实可见note；.app/snippets往返4write与菜单往返低效，第一次确定的target脱离观测是grocery_list_st16.txt；选齐后Delete/confirm没forward，非已删后又恢复。
- **已核对/一致：** 同意MM-DELETE-SET：只选当前有证据候选并预留commit；不删配置、不忽略missing target或豁免其预算。
- **分歧/细化：** 范围措辞细化：只读探索.app本身不能定为越权或确定业务错误；它是耗额旁路，真正可证偏离是不存在于当前页的grocery target。
- **仍未知：** initialize源码生成2–6根目录regular files，本轮UI三份；没有最终完整私有列表，不能宣称全盘只有三份或所有文件逐个已评。

**原goal：** Delete all my notes in Markor.

**要求/官方rubric：** initialize在Markor目录生成2–6个噪声笔记；is_successful重新取得该目录文件metadata列表，非空就是0。源码注释已给出长按一个+点选其余+批量删的正常UI做法，不是必须逐个删除。

**初始化：** step7实际有art_project_sketches_st16.md、backup_favorite_book_quotes.md、final_budget_home_renovation.md三份笔记及.app配置目录；非原AMK轮次的更多文件。

**官方源码：**
- `O/task_evals/single/markor.py:375-408`（MarkorDeleteAllNotes.initialize_task/is_successful）
- `O/utils/file_utils.py:495-549`（get_file_list_with_metadata regular files only）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/029-MarkorDeleteAllNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-029-20261110T173605Z-b204a9/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-7`：当前三份目标笔记清楚可见。
- `agent-tap_on-8`：进入.app。
- `agent-ui_snapshot-11`：进入snippets后空目录。
- `agent-ui_snapshot-14`：两次Back回笔记列表。
- `agent-ui_snapshot-16`：已选第一份笔记。
- `agent-ui_snapshot-18`：More options是Clipboard/Move/Copy等，无Select all。
- `agent-tap_on-21`：尝试grocery_list_st16.txt，当前UI未出现该文件，target not found。
- `agent-ui_snapshot-25`：三份笔记已全部Selected，Delete尚未执行。
- `agent-tap_on-26`：Delete被预算拒绝。
- `agent-assert_visible-28`：最终断言仍可见第一份笔记通过。

**预算/输出：** admitted 14/14，attempted 17，denied 3，failed dispatch 1；deadlineExceeded=false。主runner TaskResult step 4，businessStatus=failed，mainAnswer=valid。
拒绝审计事件：seq51 `agent-tap_on-26` (action_budget)；seq52 `agent-tap_on-27` (action_budget)；seq55 `agent-kill_app-29` (action_budget)。

**期望与实际：** 直到14个write耗尽才把实际三份文件选齐；Delete/确认均未设备派发，至少第一份明确还在。

**直接失败：** 删除事务未发生，末态仍有笔记，正对官方非空列表给0。

**根因分级：**
- **已证实：** .app/snippets往返花4个write；More options/back花2个；未见文件grocery_list_st16.txt又耗一次失败admission。
- **已证实：** audit seq51/52拒绝Delete两次，seq55拒绝kill；deadline未到。
- **强推断：** 探索配置目录和无证据文件名使业务提交之前预算耗尽；不是确认框点错、更非不能批删。
- **无法确认/备选与缺证据：** grocery_list_st16.txt来源不明，原trace没有这个目标文件的有效观测；不能断言来自AMK旧记忆或模型幻觉机制。
- **无法确认/备选与缺证据：** 最终完整文件列表未私有转储，但assert_visible已足以证明至少一份未删。

**责任层：** FSQ action grounding / plan scope / FSQ launch overhead / harness fixed budget

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 · FSQ planner/knowledge owner · `Markor file-browser multi-select; goal-preplan action grounding`：** 只把当前实际文件节点作为候选，排除.app配置目录；长按一份后点选其余实际文件、Delete并OK。对“all notes”不私自扩展成清理所有配置文件夹；未观察到的grocery_list不得作为动作目标。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线golden trace断言每个文件动作目标均有先前UI证据，3份multiselect后紧接Delete/确认，不进.app。
- 需设备的新题验证：设备新题：14上限内批量删除并观察空列表；官方单次oracle列表为空，配置目录保持可用。

**给FSQ owner的逐例问题（pending）：**
- 为什么计划扩展到.app/snippets及未观察到的grocery_list_st16.txt？
- FSQ能否在选择已齐时优先提交Delete而不是多余探索，并区分应用配置与用户笔记？

## 030 MarkorDeleteNewestNote — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:512-553`。
- **已核对/一致：** 已核对：所选final_friendly_king有UI较新时间支持，不能说选错；直接失败是Confirm Delete的OK未forward。
- **已核对/一致：** 同意MM-DELETE-COMMIT优先必要确认、减少无改变的Sort/Info往返，保持10上限。
- **分歧/细化：** 官方时间口径已补源：MarkorDeleteNewestNote按initial_file_list_sorted.change_time；file_utils.get_file_list_with_metadata:519/544-545实际解析ls -ll -au（-u访问时间）而非直接UI Last modified/创建时间/POSIX ctime。不能把可见mtime足够作为官方候选正确的已证事实。
- **仍未知：** 初始化change_time数组和评估末态文件列表未保存，无法证明候选是否满足该oracle排序；无确认删除已是充分失败。

**原goal：** Delete the newest note in Markor.

**要求/官方rubric：** 初始化2–6份笔记并在每份后随机推进系统时间，按change_time排序保存initial_file_list_sorted。评分要求最终恰少一份、余下顺序前缀的file_name/change_time均与初始化一致；即删除change_time最大那份而不是随便删一份。 注意helper把ls -ll -au的时间列命名为change_time（-u对应访问时间），不能在报告中擅自等同POSIX ctime；本轮无确认删除这个直接失败不依赖时间语义争议。

**初始化：** 现场实际仅两份：final_friendly_king.md（UI 15:34）与fine_jelly_final.md（15:17）；列表.app不是一份笔记。初始化记录referenceTime15:34，但随机时钟推进后初始UI14:29，不能把这个时间变化误判deadline。最终初始change_time私有列表未存入task-initialization。

**官方源码：**
- `O/task_evals/single/markor.py:324-368`（MarkorDeleteNewestNote.initialize_task/is_successful）
- `O/utils/file_utils.py:495-549`（get_file_list_with_metadata: field change_time parsed from ls -ll -au）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/030-MarkorDeleteNewestNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-030-20261110T173938Z-b9dbfa/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-7`：两份文件及修改时间可见。
- `agent-ui_snapshot-9`：打开Sort菜单但未更改Date。
- `agent-ui_snapshot-13`：已选final_friendly_king.md。
- `agent-ui_snapshot-15`：详情显示精确位置/storage/emulated/0/Documents/markor及Last modified15:34。
- `agent-tap_on-18`：Delete只打开确认框。
- `agent-ui_snapshot-19`：Confirm Delete/CANCEL/OK真实待提交。
- `agent-tap_on-20`：OK因10上限拒绝，下一次retry同拒。

**预算/输出：** admitted 10/10，attempted 13，denied 3，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 4，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq39 `agent-tap_on-20` (action_budget)；seq40 `agent-tap_on-21` (action_budget)；seq41 `agent-kill_app-22` (action_budget)。

**期望与实际：** 选中的文件看上去是两份中最新，但正式评分按change_time而非UI的Last modified；本次无论候选对否都没按下确认、文件数量没减少。

**直接失败：** 删除确认未派发，不能满足恰少一份。

**根因分级：**
- **已证实：** 首4个write用于启动绕路；Sort/Back与Info/OK又4个write，直到第10次Delete才显示确认框。
- **已证实：** audit seq39/40拒绝OK，seq41拒绝kill；deadline未到。
- **强推断：** 删除未提交是充分失败原因；不能把失分终结为选错最新文件，因为没有官方初始change_time列表来证明候选错。
- **无法确认/备选与缺证据：** 初始化metadata完整数组未保存；UI Last modified与官方helper的ls -au/change_time列不同，不能凭界面完全重建应删目标。

**责任层：** FSQ commit-aware planning / FSQ launch overhead / harness budget/diagnostic boundary

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 · FSQ planner owner · `Markor newest-note flow; ordered destructive action plan`：** 用实际可见时间/必要排序识别最新，保留确认动作；无需确认前反复打开无改变的Sort和已知文件Info。其他文件不可编辑；完成后刷新列表确认只少目标。
- **P2 · harness diagnostics owner · `task-initialization private audit for MarkorDeleteNewestNote`：** 将官方initialize已构造的initial_file_list_sorted及实际helper时间列语义以私有诊断序列保留（不额外调用oracle、不向agent暴露），便于区分候选识别错与确认没做；修复agent不得悄悄把现有官方时间口径改成另一个。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线fixture：按官方helper生成的change_time字段（ls -au访问时间列），而非UI mtime/名称确定应删目标；未提交确认不能记为完成。
- 需设备的新题验证：设备新题：同10上限，删除确认完成且只少change_time最大文件，余下file_name/change_time保持不变；只评一次。

**给FSQ owner的逐例问题（pending）：**
- 是否planner未预留Delete后的OK，还是重复启动造成不可避免额外开销？
- 原生runner以Last modified判newest，official helper却把ls -au访问时间列叫change_time；如何保证公开UI策略与官方现有字段口径一致，不改rubric？

## 032 MarkorEditNote — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:556-602`。
- **已核对/一致：** 已核对：真实替换丢原文，两次Undo分别撤set/clear恢复原文是有意义的补救，不是无意义重试；最后buffer匹配但Save未forward。
- **已核对/一致：** 同意MM-EDIT-PERSIST：一次读取完整公开原文后合成替换，保留Save/重开；不加插入-only交互rubric。
- **分歧：** 无实质根因/修法分歧。
- **仍未知：** 同意FSQ保留auto-save未知；官方0不能推出磁盘必是哪一旧版本，只有持久化不符/未证。

**原goal：** Edit note_SiFbv.txt in Markor. Add to the top of the note Hello, World!

**要求/官方rubric：** 读取精确文件路径、去CR/首尾空白后，与header+\n+initialize生成的original_content进行0.9阈值fuzzy match。编辑器assert_state存在不等于文件已落盘。

**初始化：** 实际原文Don't forget to water the plants while I'm away.（step9），并有相似note_SiFbv_final.txt等噪声。未import/重建随机句子。

**官方源码：**
- `O/task_evals/single/markor.py:209-254`（MarkorEditNote.initialize_task/is_successful）
- `O/utils/fuzzy_match_lib.py:20-50`（fuzzy_match）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/032-MarkorEditNote/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-032-20261110T174445Z-384f53/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-9`：真实读取完整原文。
- `agent-input_text-11`：Move Home后只写Hello, World!和换行，替换掉原文。
- `agent-ui_snapshot-13`：原文消失，证实replacement。
- `agent-ui_snapshot-15`：第一次undo只恢复到空，反映clear/set_text的多个undo状态。
- `agent-ui_snapshot-17`：第二次undo恢复原文。
- `agent-input_text-18`：再用完整header+原文重建编辑内容。
- `agent-tap_on-20`：Save被预算拒绝。
- `agent-assert_state-21`：element text完全匹配存在，仍只证明当前editor状态。

**预算/输出：** admitted 12/12，attempted 14，denied 2，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 4，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq39 `agent-tap_on-20` (action_budget)；seq42 `agent-kill_app-22` (action_budget)。

**期望与实际：** 最终editor含正确header与原文，但Save没派发、重开没做，官方文件评分0。不能把编辑器assert passed抬成持久化成功，也不能把插入-only不满足说成官方失分原因。

**直接失败：** 显式Save未forward；当前buffer正确但持久状态未证且official为0，不能确定最终文件字节或auto-save是否生效。

**根因分级：**
- **已证实：** input_text源137-151明确clear/set_text；本轮UI连续展示原文→仅header→空→原文，非套用旧AMK根因。
- **已证实：** 2次launch+swipe+launcher tap花4 write；原文覆盖后的2次undo与完整重写消耗余量；audit seq39 Save拒绝，seq42 kill拒绝，deadline未到。
- **强推断：** 恢复后editor对、official0且唯一Save被拒，更支持持久化环节缺失；但没有最终文件读回，不能排除未记录的auto-save行为或其他评分内容差异。
- **无法确认/备选与缺证据：** Markor自动保存时机/最终文件字节未采集，不能严格声称磁盘仍是某一具体旧版本。

**责任层：** FSQ text semantic contract / FSQ persistence verification / harness budget

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 · FSQ skill/planner owner · `resources/skills/android-harness.md; drivers/android/_uiautomator2.py::input_text description; goal pre-plan`：** 把input_text的click/clear/set_text整字段替换语义告知planner。header任务先读取可见原文，用现有replacement写入header+指定换行+已观察原文，再Save；不把Move Home+input_text误当插入，不添加官方没有的“必须只用插入操作”验收。长文读不全时先取得完整UI证据，不能拿frozen私有params补内容。
- **P1 · FSQ planner/verifier owner · `Markor Save/read-back state distinction`：** 区分editor状态和持久化状态；在既定预算内正确合成一次替换→Save→重开核对，不靠两次undo试探，也不把assert_state当保存证明。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线fake editor含clear与set_text两个undo事务，确保计划不把input_text作为insert、assert_state不声称落盘。
- 需设备的新题验证：设备新题：12上限正确合成header+已观测原文并Save；私有单次评分读取文件，UI重开验证。

**给FSQ owner的逐例问题（pending）：**
- input_text为何仍宣称focused target输入而未明确replace，pre-plan是否约束了错误插入交互？
- assert_state element.text匹配时报告exists=True，有无把它误用作文件保存证据的层间歧义？

## 033 MarkorMergeNotes — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:605-661`。
- **已核对/一致：** 已核对：Copy passed不保证Paste数据可用，目标仅Autofill/Paste absent；第二次Copy后未再次Paste或input_text，第二三源未读，最终空文件。
- **已核对/一致：** 同意MM-MERGE-CONTENT：有52write余量且无deadline/maxTurns错误，不能归timeout；可用公开UI完整三源正文合成后写入，不能借私有params。
- **分歧/细化：** FSQ把.md是否允许留未决；harness已读installed CreateFile:201-216及file_utils.check_file_or_folder_exists:255-258，严格full_target_path等值，故mIObBbo4.md不等于mIObBbo4，是与空内容独立的确定路径要求。原实际oracle分支无日志仍保留推断。
- **分歧/细化：** 分隔要求补充官方MarkorMergeNotes:632-636明确5行/两个空行；修复不只单换行字符串，须保留源末尾换行并新增分隔行。
- **仍未知：** clipboard实际内容/为何Paste缺失无本轮证据；不复用AMK历史clipboard根因。
- **仍未知：** 未满52余量为何选择结束待FSQ停止策略确认。

**原goal：** Merge the contents of Markor notes tough_frog_2023_08_05.txt, proud_cat_edited.txt and 2023_08_21_friendly_koala.md (in the same order) into a new Markor note named mIObBbo4 and save it. Add a new line between the content of each note.

**要求/官方rubric：** CreateFile要求精确文件名mIObBbo4存在且正文fuzzy匹配三段以双换行分隔；后续额外检查去首尾空白后split(\n)恰5项、第1和3（从0计）项空白。track没有partial；只有正确内容+空行+精确路径才1。

**初始化：** 创建三源文件，实际step9已读到第一份m4kMyOGWaENoPj6FqLjd；第二/三份冻结文本分别fxHXZsqrmnwYjXvte9pg、f42GOjFWb2aKHogAFQSY。后两项是私有评分上下文，不能作为agent修复路径的取值来源。

**官方源码：**
- `O/task_evals/single/markor.py:542-582`（MarkorMergeNotes.__init__/initialize_task）
- `O/task_evals/single/markor.py:603-638`（MarkorMergeNotes.is_successful）
- `O/task_evals/common_validators/file_validators.py:199-226`（CreateFile.is_successful）
- `O/utils/file_utils.py:228-258`（check_file_or_folder_exists exact full path equality）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-9`：第一源内容实际可见。
- `agent-tap_on-13`：Select all后Copy调用passed，只是UI派发成功。
- `agent-ui_snapshot-18`：创建对话框默认ext=.md。
- `agent-input_text-19`：只填basename mIObBbo4，未清扩展名。
- `agent-tap_on-23`：目的文件Paste找不到；UI只见Autofill，不代表有可粘贴内容。
- `agent-ui_snapshot-30`：列表出现mIObBbo4.md，路径已与官方目标不同。
- `agent-tap_on-37`：重试Copy第一源，但未随之完成目的文件粘贴。
- `agent-ui_snapshot-42`：重开mIObBbo4.md后editor空。
- `agent-assert_with_ai-43`：关键原截图确实空白；视觉断言failed。

**预算/输出：** admitted 26/78，attempted 26，denied 0，failed dispatch 1；deadlineExceeded=false。主runner TaskResult step 8，businessStatus=inconclusive，mainAnswer=valid。

**期望与实际：** 实际保存的是空mIObBbo4.md而非精确mIObBbo4；第二/三源未打开、未合并；即使将来只修Paste，也会因扩展名和缺两源仍失败。

**直接失败：** 精确输出路径与内容两个独立充分失败：新名带默认.md，重开为空；不是仅缺最终Save或预算耗尽。

**根因分级：**
- **已证实：** Paste目标未出现（step23 target not found），第二次Copy后直接重开并最终断言，没有再次Paste或正文输入。
- **已证实：** main pre_plan明确第二/三源与append steps全部skipped。
- **已证实：** 26/78 write，0 denied，deadlineExceeded=false；runner正常返回inconclusive；events seq134主agent requests58<maxTurns100。不能把runner“execution window”措辞当wall timeout。
- **强推断：** CreateFile在mIObBbo4不存在分支即可返回0；没有私有文件转储证实该分支，但实际列表带.md、未清扩展名与路径check源码一致。
- **强推断：** Copy passed但Paste缺失说明未验证跨屏剪贴板可用；不能进一步把剪贴板清空归因于特定SDK/系统隔离。
- **无法确认/备选与缺证据：** 剪贴板实际内容/生命周期没有本轮存证，不能复用旧AMK clipboard根因。
- **无法确认/备选与缺证据：** 未耗尽动作或deadline却选择结束的具体agent停止策略需FSQ owner核对。

**已实际看过的关键PNG（仅存量截图）：**
- `agent-assert_with_ai-43` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/033-MarkorMergeNotes/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-033-20261110T174733Z-14793f/artifacts/screenshots/screenshot-agent-assert-with-ai-43-invoke-assert-with-ai-1-6a1e984f3162.png`

**责任层：** FSQ filename/creation semantics / FSQ cross-screen clipboard evidence discipline / FSQ premature completion policy

**精确修复方案（未提交修改）：**
- **P0 · FSQ planner/knowledge owner · `Markor create dialog + merge strategy`：** 创建时显式清空ext以保留无扩展名mIObBbo4（不修rubric）；逐一从UI读取三源并保存完整字符串，按源文件末尾换行与goal要求构造双换行间隔，用已有replacement一次写目的文本，Save并重开。若继续剪贴板路线，必须先验证可Paste/已Paste正文，不能以Copy dispatch通过当数据已传达。
- **P1 · FSQ runner/planner owner · `agent plan completion and recovery policy`：** 失败的Paste不是全部merge不可做的结论；在剩余52 write和未到deadline时，按已观察文本/已提供UI功能继续独立业务步骤，或明确具体不可用能力。不得仅用模糊execution window提前终结。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线创建对话框fixture默认.md：无扩展名goal必须得到精确路径；三源顺序和双换行构造能通过官方split5条件。
- 需设备的新题验证：设备新题：只用实际UI取得三段，文件浏览器显示精确无扩展名且重开非空；官方单次oracle核对路径、fuzzy内容、5行空行位置。

**给FSQ owner的逐例问题（pending）：**
- 第二次Copy后为何没有再次Paste或用已读源正文input_text补救，余量充足却结束？
- 默认.md未清空是否planning/filename规格缺失；原生verifier仅说空白而遗漏精确路径错误？
- 本轮Clipboard具体是否失效未知，请勿套旧AMK标签。

## 036 MarkorTranscribeVideo — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/media-contacts-markor.md:664-715`。
- **已核对/一致：** 已核对：worker默认Markor但S1和S31显式实际VLC，不能按默认目标推断kill；S31成功kill VLC，不是Markor。
- **已核对/一致：** 接受FSQ新证据并亲看原PNG：S14 Maria、S16 Emilia、S21 Charlotte、S28 Charlotte；修正本报告先前“没有Emilia截图”。只是离线散落多次播放截图，不代表主runner建立完整时间顺序。
- **已核对/一致：** 同意MM-VIDEO-SEQUENCE：短视频需先暂停验证时间停止，再逐段seek视觉采样；XML不含像素字词，原17/20无denied/硬deadline、未生成文件，非地图/AMK式环境标签。
- **分歧/细化：** FSQ文字S15观察已05s与原execution S15 invoke XML的player_overlay_time=0:07/seekbar7900.0不一致；自动截图和随后snapshot应区分capture。此数秒差异不影响动态控件过期根因。
- **分歧/细化：** “无完整视频artifact/无最终文件”需收窄为未保留可证明完整序列的视频转储、未有创建动作且official0；本轮没有文件目录转储，不能声称已私有读取确认文件不存在。
- **仍未知：** overlay消失具体时刻、Space是否pause、主runner实际能否消费各after-action图片未决；只确认S28视觉断言被读取。
- **仍未知：** 为何尚有3write余量便跳过所有Markor阶段需FSQ核对策略；20预算全流程可行性只能未来新题验证。

**原goal：** Transcribe the contents of video ZwUN_moment_70_.mp4 by watching it in VLC player (located in Download) and writing the sequence of strings shown on each frame to the text file ZwUN_moment_70__transcription.txt in Markor as a comma separated list. For example, if the first frame shows the text "edna" and the second frame shows the text "pineapple", then the text file should contain only the following text: "edna, pineapple".

**要求/官方rubric：** 初始化用messages=[Maria,Charlotte,Emilia]、每词8秒生成24秒视频，并加7份干扰视频；文件评分由CreateFile精确路径存在+正文fuzzy匹配Maria,Charlotte,Emilia。不评分VLC操作顺序本身，但本任务真实要求观看。

**初始化：** 正式frozen params指定三词与顺序，视频在Download；本调查只读取冻结参数，未import任务重建媒体。实际VLC列表找到目标，24秒时长在UI。

**官方源码：**
- `O/task_evals/single/markor.py:884-921`（MarkorTranscribeVideo.template/initialize_task/is_successful）
- `O/task_evals/common_validators/file_validators.py:199-226`（CreateFile.is_successful）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-2`：launch VLC通过但还是Launcher，靠两次swipe找到VLC。
- `agent-tap_on-11`：正确视频被打开，初次有tips覆盖。
- `agent-tap_on-14`：tips关掉后原after-action截图在0:04显示Maria，非空视频。
- `agent-ui_snapshot-15`：播放器7.9秒/24秒，Pause存在，id=player_overlay_play。
- `agent-tap_on-16`：约4秒后同id找不到，耗时11.6秒等待；本step after-action截图仍显示Emilia，随后S17才回视频列表。
- `agent-ui_snapshot-22`：再次播放10.9秒/24秒，Pause仍以相同id出现在新快照。
- `agent-tap_on-23`：约4秒后又找不到；不是静态id明显拼错。
- `agent-assert_with_ai-28`：原截图及视觉断言实际显示Charlotte；仅这一词被runner转成可读证据。
- `agent-ui_snapshot-30`：又回到视频列表。
- `agent-kill_app-31`：仅VLC teardown，未任何Markor创建/写入动作。

**预算/输出：** admitted 17/20，attempted 17，denied 0，failed dispatch 4；deadlineExceeded=false。主runner TaskResult step 7，businessStatus=inconclusive，mainAnswer=valid。

**期望与实际：** 存量截图已亲看S14 Maria、S16 Emilia、S21 Charlotte及S28 Charlotte，三个词都有局部像素证据；但来自多次播放的散落capture不能冒充主runner已建立从起点至结尾的完整有序覆盖。runner只确认Charlotte并跳过所有Markor阶段，无创建动作。

**直接失败：** 没有创建转录文件；上游播放器未及时暂停/定位，短视频仍在流逝，控制条快照过期后重复查找失败，未建立完整有序转录。

**根因分级：**
- **已证实：** 原始S14截图Maria、S16截图Emilia、S21及S28截图Charlotte，非“视频不可见/没有文字”；此前本报告未看S16而称无Emilia的句子已更正。
- **已证实：** UI step15/22有正确Pause id，下一action却报target not found；控件显隐/播放完毕是动态现场状态，不能单标“点击失败”。
- **已证实：** 17/20 writes，0 denied，deadlineExceeded=false；events seq102主agent requests42，正常返回；不支持预算耗尽或硬timeout。
- **强推断：** 控制条自动隐藏与等待/取证耗时导致目标过期，是两轮“观察存在→操作找不到→返回列表”最小一致解释；是否藏条先于视频结束未直接逐帧采集。
- **强推断：** 已有三词像素截图而main只显式读取S28的Charlotte，支持动态媒体观察消费/时序整合策略不足；不直接断言所有截图从未提供给主planner。
- **无法确认/备选与缺证据：** SDK何时隐藏overlay、Space是否真正pause没有状态证据，不认定Space可靠。
- **无法确认/备选与缺证据：** 不能从私有messages直接生成答案来修复agent；也没有本轮媒体损坏、AMK probe或文件不存在证据。

**已实际看过的关键PNG（仅存量截图）：**
- `agent-tap_on-14` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-fb581b7d99fb.png`
- `agent-assert_with_ai-28` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/artifacts/screenshots/screenshot-agent-assert-with-ai-28-invoke-assert-with-ai-1-90ac9d030acf.png`
- `agent-tap_on-16` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-371713c35c0c.png`（交叉核对新增亲看）
- `agent-tap_on-21` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/036-MarkorTranscribeVideo/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-036-20261110T180141Z-5dd947/artifacts/screenshots/screenshot-agent-tap-on-21-finalize-after-action-1-6f0207f4fe16.png`（交叉核对新增亲看）

**责任层：** FSQ transient video UI control / FSQ observation/vision availability / FSQ plan completion

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P1 · FSQ driver/skill and planner owners · `VLC playback control strategy; observation/image consumption`：** 用当前可见播放器控件即时暂停，随后重新观测已暂停时间；必要先唤出控制条，不拿数秒前的快照重用等待。逐段seek到每个新词时取得静态截图并读回，记录时间顺序、覆盖首尾。短视频取证要先冻结状态再调用慢视觉assert。保留完整序列后才进入Markor创建/Save，不能用oracle messages补词。
- **P1 · FSQ observer/runner owner · `Screenshot artifact to business observation path`：** 明确after-action图片是否真正提供给主agent；若只提供XML与路径，必须有无需猜文件路径的受控图片读取接口或视觉观察，确保画布文字如Maria可被业务规划消费。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线复用本轮截图应可读Maria/Emilia/Charlotte三个局部词；仍不能把散落capture当连续全程覆盖或主runner已完成顺序记忆；动态控件fixture模拟观察后隐藏。
- 需设备的新题验证：设备新媒体：24秒三词，不泄露生成params，先暂停确认时间再逐段观察；20上限内转录文件创建/Save并单次正式内容评分。

**给FSQ owner的逐例问题（pending）：**
- 主agent实际拿到了step14的Maria截图，还是只拿到XML与artifact路径？
- ui_snapshot存在Pause但下一tap进入11秒等待，是否有工具延迟/auto-hide处理缺口？
- 42 requests、17writes未耗尽且deadline未到，跳过Markor的停止依据是什么？

## 040 NotesTodoItemCount — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/sms-system-navigation.md:51-71`。
- **已核对/一致：** 已核对：启动后仍Launcher、首次Ideas误入Health、Sidebar后才进目标folder；正确首屏3个checkbox不是完整计数证明，搜索在第11write前被拒，未提交数值。
- **已核对/一致：** 同意SN-040根因/修法：存在于UI树不等于可交互前景；先展开Sidebar、确认folder标题，再建立筛选/去重遍历终点；summary必须承载用户答案，不是过程总结。
- **已核对/一致：** 新增亲读S8 prepare XML与原PNG：Ideas bounds=[39,740][614,797]，Workout Routine bounds=[119,740][1041,797]，画面实际仅All notes且drawer未展开。重叠坐标支持FSQ隐藏节点被点穿的强推断，但没有实际u2点击坐标回执。
- **分歧/细化：** FSQ写真实总数未知需细分：官方期望值可从installed NotesTodoItemCount proto恰3个is_todo字段及COUNT确定，排除条件AND防止噪声增加Ideas todo；本轮实际DB全量未转储、agent未完成覆盖仍未知。不得把私有expected3给未来模型，也不把顶部3条冒充全量证明。
- **分歧/细化：** harness已回答提交口径：唯一主runner step4.tool_output.summary原样进入interaction_cache，本次是Could not verify叙述；无另取pre_plan/verifier/evidence或数字摘取payload修复。mainAnswer valid而NUMBER_MATCH失败。
- **仍未知：** 没有本轮全量Joplin库/尾页证据，也没有实际点击坐标；隐藏drawer节点命中是强推断，不升级为驱动选错selector的实测。
- **仍未知：** 之后正确搜索/遍历在原10预算内能否完成须未来新题验证，不私加额度。

**原goal：** How many to-dos do I have in the 'Ideas' folder in the Joplin app? Express your answer as just a single number.

**要求/官方rubric：** tasks.textproto relevant_state恰3个folder={folder},is_todo=True条目；初始化100份噪声通过排除条件AND（is_todo=True且folder=Ideas）避免额外合格todo。COUNT is_todo得到3；NUMBER_MATCH将完整agent答案字符串按逗号拆分后float转换，不抽取叙述里的数字。harness只取唯一主runner.tool_output.summary放入interaction_cache；不取verifier、pre_plan或evidence。

**初始化：** 初始化记录params含folder=Ideas/title=Meeting Agenda/body参数，但任务的title_without_replacement/body_without_replacement实际由数据生成选择，不等于只数名叫Meeting Agenda的记录。真实Ideas UI显示Recipe Ideas、Financial Plan、Work Tasks三个checkbox条目，下面大量无checkbox普通note。冻结源码支持official期望3，未实例化重建数据。

**官方源码：**
- `O/task_evals/information_retrieval/proto/tasks.textproto:3433-3480`（NotesTodoItemCount task proto）
- `O/task_evals/information_retrieval/information_retrieval.py:82-119`（InformationRetrieval.initialize_task/is_successful）
- `O/task_evals/information_retrieval/joplin_app_utils.py:38-66`（setup_task_state）
- `O/task_evals/information_retrieval/joplin_app_utils.py:276-336`（_check_note_conditions AND exclusion）
- `O/task_evals/information_retrieval/proto_utils.py:111-120,147-180,193-208`（_cast_answers_to_type/check_agent_answer/get_expected_answer）
- `src/fsq_androidworld_eval/fsq_worker.py:27-57`（select_main_answer）
- `src/fsq_androidworld_eval/fsq_runner.py:357-366`（interaction_cache assignment and official oracle）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-2`：launch通过却仍Launcher。
- `agent-tap_on-8`：尚在All notes时点text Ideas。
- `agent-ui_snapshot-9`：实际打开Health中的Workout Routine - Strength Training，不是Ideas文件夹。
- `agent-tap_on-12`：Back后打开Sidebar。
- `agent-tap_on-14`：这时才选择真正Ideas notebook。
- `agent-ui_snapshot-15`：真实folder Ideas顶部三条todo和下方普通note；关键截图可见checkbox。
- `agent-ui_snapshot-17`：向下滚只见大量普通notes，未形成完整列表断言。
- `agent-ui_snapshot-19`：Search框打开，但含侧边栏/键盘。
- `agent-input_text-20`：第11个write试图搜索被拒，搜索内容未实际派发。

**预算/输出：** admitted 10/10，attempted 12，denied 2，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 4，businessStatus=inconclusive，mainAnswer=valid。
拒绝审计事件：seq39 `agent-input_text-20` (action_budget)；seq40 `agent-kill_app-21` (action_budget)。

**期望与实际：** 官方期望数值3；主runner step4 summary实际为“Could not verify the total number of to-dos in Ideas before the harness action budget was exhausted.”，不是数也没提交其他业务答案。主output结构有效（mainAnswer.status=valid）不代表NUMBER_MATCH通过；failure不是“误把3算成其他数”，而是未给数值+未建立完整覆盖。

**直接失败：** interaction_cache收到有效task_run_v1的叙述summary，float解析失败由IR evaluator捕获ValueError并返回0。早期误开其他笔记和启动绕路耗掉预算，正确folder已可见3个todo却未完成数量确认/数值提交。

**根因分级：**
- **已证实：** mainAnswer valid、businessStatus inconclusive，非exact_main_summary契约异常；不要混入其他四例main-summary缺失造成official无效。
- **已证实：** 10/10write，seq39搜索input拒绝、seq40kill拒绝；deadline未到。
- **已证实：** actual截图确见Ideas+三个checkbox；源码排除条件为AND而非OR，不是把所有Ideas普通笔记或所有folder todo都排掉。
- **已证实（交叉核对新增）：** S8 prepare XML含Ideas [39,740][614,797]与Workout Routine [119,740][1041,797]重叠bounds，原prepare PNG实际All notes而drawer未展开；节点存在与前景可交互并非同一事实。
- **强推断：** 强支持未展开drawer的Ideas节点被exists命中后点击其bounds落到前景Workout note；当前driver按exact text，不是contains匹配。但无实际u2点击坐标回执，不能升级为已证selector选错。
- **强推断：** official数3由冻结proto三条+排除筛选决定；UI顶部三个todo与之吻合，但agent只看顶部截图本身不能证明完整total。
- **无法确认/备选与缺证据：** 未有本轮完整Joplin数据库/所有屏尾私有dump；不假造完整列表读完。
- **无法确认/备选与缺证据：** 隐藏drawer与前景note坐标重叠已有证据，实际点击坐标/底层可交互判定未采集；不认定oracle数据错。

**已实际看过的关键PNG（仅存量截图）：**
- `agent-tap_on-14` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-2ecfa6ea86ad.png`
- `agent-tap_on-8` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/040-NotesTodoItemCount/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-040-20261110T181343Z-e434c7/artifacts/screenshots/screenshot-agent-tap-on-8-prepare-before-action-1-cc90c7422a6c.png`（交叉核对新增亲看prepare图；不是点击后图）

**责任层：** FSQ navigation/grounding / FSQ IR answer protocol adaptation / harness exact-summary transport correct as frozen

**精确修复方案（未提交修改）：**
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P0 · FSQ planner/IR adapter owner · `Joplin notebook navigation + task_run_v1.summary answer convention`：** 先Sidebar并确认Ideas标题，再用公开Joplin UI的notebook+is_todo筛选或完整列表覆盖计数；不要把普通note/其他folder/完成状态条件私加进计数。结果仅数字写到主runner summary（推理/错误仍放其他结构字段）；不可从verifier/evidence自动回填数字或正则摘数，更不可把私有expected3注入。
- **P1 · harness protocol owner · `fsq_worker.select_main_answer / manifest.answerProfile / agent-facing answer instructions`：** 未来把“IR业务答案必须放summary且遵守原goal单数字格式”显式告知native agent，同时保留原始summary严格传递；不要悄悄把解释型summary改写成oracle可过的答案。
- **P1 · FSQ driver/navigation Skill owner · `drivers/android/_uiautomator2.py::tap_on/_selector/_wait_for_exists:109-116,356-389`：** 保留原始UI树，但显式提供未展开容器/离屏或遮挡的证据；exists不能作为可点击前景充分条件。此例先展开Sidebar再定位Ideas并核对页标题，避免点击隐藏drawer节点的bounds。不能粗暴删除全部drawer节点，也不能只改为text contains或忽略missing target。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线：summary="3"可作为数值、summary叙述不能被数字提取修复；mainAnswer valid不等于business answer correct。fixture含Ideas普通note、其他folder todo、已完成todo，按folder AND is_todo计数；另覆盖drawer隐藏/展开且节点bounds与前景note重叠，禁止exists即当可交互。
- 需设备的新题验证：设备新题：10上限导航到目标notebook，建立完整筛选/覆盖后只在summary报数，官方单次oracle；不复用本题3。

**给FSQ owner的逐例问题（pending）：**
- FSQ是否知道最终业务答案必须放summary而不是在structured fields或verifier？
- 第8步exact text Ideas为何实际打开Health/Workout Routine；是否UI位移或源树与可点击节点坐标不一致？
- 已看到3个todo后为何必须再search；完整覆盖边界怎样以UI证明且保持预算？

## 041 OpenAppTaskEval — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/sms-system-navigation.md:73-89`。
- **已核对/一致：** 已核对：request.appId=com.android.camera2为真实配置错误，后被业务纠正；S9 Contacts主屏已可用无popup，S10显式kill_app(app_id=com.google.android.contacts) invoke通过，audit19 attempted/20 succeeded，绝非按默认Camera猜kill。
- **已核对/一致：** 一致：直接近因是终态被成功app_stop覆盖；没有kill后画面/实际activity字符串，故official取样不再Contacts是源码+时序+0分支持的强推断，而非视觉亲见离开。
- **已核对/一致：** 同意SN-041a/SN-A/SN-L修法：修公开参数app-name映射，launch需前台就绪证据；由coordinator明确版本化终态/资源cleanup合同，不能静默停用现有kill、偷偷改取样时点或kill后重开刷分。
- **分歧/细化：** 补充映射来源已定位：当前harness fsq_runner.py::_primary_app_id:97-105遍历task.app_names取首个可映射包；OpenAppTaskEval.app_names是五种候选全集、首项camera，而本实例params.app_name=contacts。原request可直接佐证输出Camera；不能拿此配置缺陷单独解释最终0，因为Contacts已经打开。
- **分歧/细化：** 本报告“评分后cleanup”仅是coordinator批准的新生产协议候选，不是可在冻结r4/强制kill合同下单方挪动边界的修复；已进一步明确该约束。
- **仍未知：** is_successful当时实际activity字符串没有保存，不能编造Launcher组件名；也没有kill后Contacts状态新截图。
- **仍未知：** launch_app为何没有前台化仍需FSQ/u2机制区分，不拿旧AMK根因补空。

**原goal：** Open the contacts app. Clear any pop-ups that may appear by granting all permissions that are required.

**要求/官方rubric：** OpenAppTaskEval没有自定义initialize，基类恢复app_names所有快照；is_successful只比较当前activity解析后的package与com.google.android.contacts。没有查历史曾打开，也没有私自要求截图得分；popup清理是goal要求但评分代码不单独检查。

**初始化：** frozen app_name=contacts，原worker request却appId=com.android.camera2；这是_primary_app_id选择全app_names第一项，与public goal不一致。step1因此launch Camera，后由agent显式launch Contacts纠正；2个launch均未把业务app显到前台，实际用Launcher Contacts icon。

**官方源码：**
- `O/task_evals/task_eval.py:116-157`（TaskEval.initialize_task/_initialize_apps）
- `O/task_evals/single/system.py:450-499`（OpenAppTaskEval mapping/is_successful）
- `src/fsq_androidworld_eval/fsq_runner.py:97-105`（_primary_app_id chooses first app_names）
- `src/fsq_androidworld_eval/fsq_runner.py:349-373`（official evaluation after complete native return）
- `F/resources/skills/android-harness.md:7-10`（lifecycle forced kill after verification）
- `F/drivers/android/_uiautomator2.py:102-107`（kill_app app_stop）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-launch_app-1`：默认实际目标Camera，与goal contacts不同。
- `agent-launch_app-3`：显式Contacts纠偏。
- `agent-ui_snapshot-5`：仍应用抽屉。
- `agent-tap_on-6`：点Contacts launcher才真正进入。
- `agent-ui_snapshot-7`：Contacts主屏，有startup tooltip而无permission dialog。
- `agent-tap_on-8`：关闭og_tooltip_scrim_view。
- `agent-assert_with_ai-9`：原截图与视觉断言表明主屏可用无提示。
- `agent-kill_app-10`：随后成功app_stop Contacts，先前前台终态被改变。

**预算/输出：** admitted 6/10，attempted 6，denied 0，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 4，businessStatus=success，mainAnswer=valid。

**期望与实际：** 业务曾实现：无popup的Contacts主屏可用；但native强制teardown先kill Contacts、再return给harness，官方此时才看前台而拿0。主runner报success与official0不矛盾，判断时刻不同。

**直接失败：** 成功后的kill_app破坏active-app任务终态；不是没grant权限、没清tooltip、超预算或模型不会开Contacts。

**根因分级：**
- **已证实：** step9真实截图无提示、可搜索/create；step10 kill passed。
- **已证实：** 官方reward0、无异常，预算仅6/10且deadline未到；oracle顺序明确在完整native返回后。
- **已证实：** request appId确是camera2，goal/frozen app_name确是contacts；首app选择错误为独立harness配置缺陷，但本次被业务纠正，非最终0唯一原因。
- **强推断：** app_stop导致当前activity不是Contacts，是源码行为+step9→10+official0支持的最强直接因果；diagnostic未提供oracle当时具体activity，不能断言一定是某个Launcher包。
- **无法确认/备选与缺证据：** kill之后/oracle时刻的完整activity字符串未记录；故不编造Launcher组件名。
- **无法确认/备选与缺证据：** 正常launch返回但停Launcher的底层启动原因仍由FSQ核对。

**已实际看过的关键PNG（仅存量截图）：**
- `agent-kill_app-10` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/041-OpenAppTaskEval/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-041-20261110T181630Z-d66df2/artifacts/screenshots/screenshot-agent-kill-app-10-prepare-before-action-1-9a0ce788c1b2.png`

**责任层：** harness primary app binding defect / FSQ mandatory lifecycle vs official terminal foreground contract

**精确修复方案（未提交修改）：**
- **P0 · harness owner · `fsq_runner.py::_primary_app_id and episode target construction`：** 对于公开参数选择app的任务，按本实例app_name映射构造native app target，而不是从任务app_names可选全集取第一个；新增同类复合/动态目标契约覆盖，不从oracle结果倒推包名。
- **P0 · FSQ lifecycle + harness integration owners · `resources/skills/android-harness.md::lifecycle; fsq_runner.py::oracle/cleanup ordering; manifest protocol.lifecycle`：** 必须先由coordinator批准并版本化终态/资源cleanup合同；需要前台app的未来生产协议应保留用户末态，资源close不等于app_stop，可由harness在业务评估后清理。若仍要求原Skill强制kill且后采样foreground，则明确记录互斥契约，不能单方停kill/挪取样时点刷分。绝不追改r4、不调用两次oracle、不kill后重launch补终态。
- **P0 · FSQ driver/skill owner · `drivers/android/_uiautomator2.py::launch_app + resources/skills/android-harness.md`：** launch_app成功契约应包括目标包已前台且可观察；若原u2 app_start返回仍是Launcher，修正实际启动/等待语义并明确失败，避免再发一次同样launch后才绕应用抽屉。保持现有dispatch预算、不免计动作；用原轨迹区分SDK启动返回与FSQ成功标签。
- **P2 · harness diagnostics owner · `EvaluatorDiagnostics foreground task evidence`：** 私有记录同一次official检查实际active activity，区分业务达成后被cleanup覆盖与根本没达成；不额外probe设备用于本次调查，也不向agent输oracle值。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线纯参数：app_name=contacts→com.google.android.contacts而非camera，分别覆盖5种OpenApp变体；生命周期fixture验证oracle读取发生在清理之前的保留状态，而非拿中途截图冒充末态。
- 需设备的新题验证：将来设备新题：Contacts无popup，完整native return保留前台；官方只评一次，再清理；对照audit记录实际package。

**给FSQ owner的逐例问题（pending）：**
- 强制kill_app与OpenApp official当前前台判定冲突如何跨FSQ/harness明确版本化解决？
- 为何native默认Camera但pre-plan写configured Contacts；target绑定有没有使用goal-derived公开参数的接口？
- 是否已有其他前台rubric（如27 SMS）遭同类teardown风险？

## 044 OsmAndTrack — reward 0.0

**FSQ逐例交叉核对：harness已读对侧该节；本回函待FSQ owner确认。**
对侧依据：`failure-analysis/fsq-case-notes/sms-system-navigation.md:91-105`。
- **已核对/一致：** 已核对：Country重定位不等于不可恢复错误；选Schönberg POI后points仍0，直到S41 Add才1。未输入/加Triesen或Bendern、未Done/Save便结束；23/120、约300秒对7320业务预算，不是动作/记录deadline。
- **已核对/一致：** 同意SN-044根因/修法：用points递增与Points顺序区分search/POI/route addition/Save，不能拿地名标签或所有tap passed当saved track；尚无加点或保存引擎错误。
- **已核对/一致：** 共享地图证据已提供：formal前map-baseline/qualified readiness记录固定Liechtenstein_europe.obf，源逐episode恢复校验；本轮本地Schönberg搜索与详细地形截图可见，不支持缺图归因，但没有新增逐episodeSHA实测。
- **分歧/细化：** 回答官方GPX定义：installed osmand.py:426-443读取/data/media/0/Android/data/net.osmand/files/tracks直接子文件；_track_points:373-387只认gpx:trk/trkseg/trkpt，不是wpt/rtept。_track_matches按顺序允许间插点，_coords_match每分量严格<0.001；不查track_name、不要求特定导航/驾车规划模式。
- **分歧/细化：** 不能从points:1进一步推断唯一点坐标合格、实际GPX为空/错格式/错目录或地图缺失；本episode未保存GPX文件查询/字节，official0只说明未找到满足oracle的track。
- **仍未知：** 唯一草稿点准确坐标与最终实际GPX目录/字节未采集；保存步骤未执行，不能锁定导出格式/路径故障。
- **仍未知：** 余97write、deadline未到仍停止的主决策策略未闭环；修复后的三点Save流程可行性须未来新题验证。

**原goal：** Save a track with waypoints Schönberg, Liechtenstein, Triesen, Liechtenstein, Bendern, Liechtenstein in the OsmAnd maps app in the same order as listed.

**要求/官方rubric：** initialize清除tracks并从预装地点字典确定三个目标经纬度；is_successful拉取/data/media/0/Android/data/net.osmand/files/tracks的直接子文件逐个XML解析，只提取GPX namespace下trk/trkseg/trkpt（不是rtept或wpt），按原顺序用delta_deg=0.001匹配三个目标，允许中间其他点。不校验track_name、UI最终必须停地图或完整驾车路径规划。

**初始化：** 正式前已有map-baseline补充操作及qualified readiness：Liechtenstein_europe.obf sha256=57a1955c6f517a114999fa50480ecc1402ed9b524db602540ac1c08f57ff140e，7241271bytes；代码在每个osmand任务initialize前恢复并校验这张共享map。该张地图可被其他官方文件任务清理，所以不能当永久身份；本episode未单独保存restore返回值，但初始化正常完成、后续真实本地地名搜索/详细地形截图都反驳“地图缺失”为既成事实。

**官方源码：**
- `O/task_evals/single/osmand.py:32-56`（_DEVICE_FILES/_PRELOADED_MAP_LOCATIONS）
- `O/task_evals/single/osmand.py:310-387`（_clear_tracks/_track_matches/_track_points）
- `O/task_evals/single/osmand.py:405-443`（OsmAndTrack.goal/initialize_task/is_successful）
- `O/env/setup_device/apps.py:550-552,581-593`（OsmAndApp.DEVICE_MAPS_PATH/MAP_NAMES/setup）
- `src/fsq_androidworld_eval/environment.py:256-285`（restore_shared_assets）
- `src/fsq_androidworld_eval/fsq_runner.py:269-270`（per-episode restore_shared_assets）
- `O/task_evals/single/osmand.py:63-77`（_coords_match: abs(delta latitude/longitude) strictly <0.001）

**原证据定位：**
- episode：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack`
- goal：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/sources/000-goal.txt`
- 初始化：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/task-initialization.json`；评分：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/evaluator-diagnostics.json`
- native actions：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/execution-result.json`；main结果：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/worker/fsq-task-result.private.json`
- audit：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/worker/native-action-audit.jsonl`；events：`evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/events.jsonl`

**实际因果轨迹（每个step均指上列原execution-result）：**
- `agent-ui_snapshot-7`：初始地图200mi，Position not yet known，不是规划失败错误。
- `agent-ui_snapshot-13`：新route编辑器points:0。
- `agent-ui_snapshot-17`：Schönberg在当前搜索中心5mi无结果。
- `agent-ui_snapshot-19`：增到10mi仍无结果。
- `agent-ui_snapshot-21`：输入完整地点只找到3296mi外Country Liechtenstein，说明当前搜索中心离目标很远。
- `agent-ui_snapshot-32`：选择国家后重搜，真实出现Schönberg山峰1.92mi和Haus Schönberg；本地map已可用。
- `agent-ui_snapshot-34`：选中正确Schönberg山峰详情，但route仍points:0，地点选择不等于加入route。
- `agent-ui_snapshot-40`：返回route编辑器，缩放0.25mi，仍points:0。
- `agent-tap_on-41`：点route Add后才加第1点。
- `agent-ui_snapshot-42`：终态points:1、0ft；未有第2/3点或Done/Save。
- `agent-assert_with_ai-43`：关键原截图含Schönberg地形及一草稿点，明确不是saved三点track。
- `agent-kill_app-44`：kill通过，但此前保存流程尚未开始。

**预算/输出：** admitted 23/120，attempted 23，denied 0，failed dispatch 0；deadlineExceeded=false。主runner TaskResult step 7，businessStatus=inconclusive，mainAnswer=valid。

**期望与实际：** 实际只有Schönberg附近的一点草稿，没有访问/添加Triesen/Bendern，没有Done/Save；official0与未生成合格GPX轨迹吻合。本轮无GPX目录/字节转储，所以只能确定“没有满足oracle的track”，不能声称具体GPX为空、被存成rtept、错子目录或命名错误。

**直接失败：** 地点搜索恢复后没有执行剩余两站与保存，终态仍一草稿点；不足以满足3个有序trkpt文件条件。没有任何路线计算报错证据，不能归为规划引擎失败。

**根因分级：**
- **已证实：** 首轮无结果来自5/10mi局部搜索，国家选择后同词命中真实Schönberg；最终截图地图细节可见。
- **已证实：** 保存相关steps在main pre_plan全部skipped；23/120 writes、0 denied、deadlineExceeded=false；events seq138主agent requests60<maxTurns100，正常inconclusive返回。
- **已证实：** diagnostic标量0、exception=null，无GPX解析/读取异常；不能把0改成评分无效。
- **强推断：** 选country重新定心后本地搜索恢复，说明前期搜索中心/半径而非缺地图是主要搜索障碍。
- **强推断：** 到第一点后主动结束/策略停机是不完整执行直接近因；main“execution window”措辞没有deadline硬边界支持，需FSQ核对停止策略。
- **无法确认/备选与缺证据：** 本次缺私有GPX目录列表及内容、首点精确坐标，无法分辨first point是否在0.001度容差内。
- **无法确认/备选与缺证据：** 不能证明不存在任何文件；只能依据official0认定没有被该oracle读到并满足条件的track。
- **无法确认/备选与缺证据：** episode的restore_shared_assets返回值未存档，只有既存资格链和代码调用及UI证据；不升级成逐episode新SHA实测。

**已实际看过的关键PNG（仅存量截图）：**
- `agent-assert_with_ai-43` → `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/044-OsmAndTrack/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-044-20261110T182440Z-f4183b/artifacts/screenshots/screenshot-agent-assert-with-ai-43-invoke-assert-with-ai-1-98108de07bf2.png`

**地图/GPX边界：**
- `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/environment-map-baseline-r4/report.json` /mapBaseline：formal前补充restore成功，writtenSha256及7241271bytes；不是本次调查新验证。
- `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/qualify-after-map-baseline/readiness.json` /sharedAssets/0：qualified=true；该地图verified_existing，sha如初始化所述。
- `src/fsq_androidworld_eval/environment.py` 256-285：当前读取源的逐episode restore与checksum逻辑；没有重新hash泛验。
- GPX oracle目录为`/data/media/0/Android/data/net.osmand/files/tracks`直接子文件；提取`trk/trkseg/trkpt`，不是`rtept/wpt`。经纬度每分量差严格<0.001，允许间插点，不查track_name。本episode未存最终GPX目录/字节，不能虚构具体导出路径或格式错误。

**责任层：** FSQ geospatial search-center strategy / FSQ route point/commit state modeling / FSQ premature completion / harness evidence granularity (not confirmed map defect)

**精确修复方案（未提交修改）：**
- **P0 · FSQ planner/knowledge owner · `OsmAnd Plan a route search/add/save UI flow`：** 先以国家/城市公开UI定位搜索中心，识别正确山峰而不是酒店；选地点后确认route point count递增，再找Triesen、Bendern并分别Add，最终Done/Save到Tracks。区别place selection、map center、route point、saved GPX四层状态；不向agent注入私有oracle经纬度、不要求驾车路径规划、不靠手写GPX绕过UI。
- **P1 · FSQ runner/planner owner · `Completion policy with remaining budget`：** 当前仅1点且两段/保存全skip不能收为成功；预算/时间未满时按已知UI能力继续完成。若真有不可达能力，报告具体阻断，不用execution window笼统替代实际限额。
- **P2 · harness diagnostics owner · `OsmAnd private evaluator GPX/shared-assets audit`：** 保留每episode共享地图restore返回，以及同一次oracle遍历的文件相对路径、GPX节点类型/点数/匹配进度（私有且不泄露oracle坐标给业务）；用于将来区分草稿未保存、目录/格式错、坐标顺序错。不改现有rubric，也不重跑本题。

**未来验证（只列方案）：**
- 无需设备的离线断言：离线官方GPX fixture：有序trkpt和中间点通过，反序/仅rtept/仅wpt/少点不通过；track_name任意不影响；默认只遍历tracks直接子文件的既有规则保持不变。
- 需设备的新题验证：设备新题：保持120既定write上限、无答案坐标，三次UI Add使points从0到3，Save确认；单次oracle后私有检查实际GPX路径/节点/顺序。另检查共享map每episode恢复证据，不能以“搜索初始无结果”直接宣称缺图。

**给FSQ owner的逐例问题（pending）：**
- 为什么在23/120写、60requests、deadline未到时，完成首点便以execution window结束？
- Place详情选中后多次Back直到0points，是否planner未理解selected place与route point的提交差别？
- 有无隐藏的GPX Save工具/步骤故障？本轮未到Save，不能提前归因路径/GPX格式或地图缺失。

## 共同修复约束与验证边界

- 不改官方rubric，不使用私有frozen正文/期望数字/地图坐标喂给业务agent；修复只利用公开goal与实际UI。
- 不加预算、不以同题重试凑分。固定dispatch计数的公平性或视频观察延迟如需研究，另列版本化实验，不追改r4。
- 前台任务的cleanup冲突需FSQ/harness联动、显式版本化：业务结果完整返回后保留所需前台，official单次评分后再cleanup；不能拿中途截图替代末态、不能评分后重launch补分。
- 修复后只由主集成owner按上述离线断言和设备新题方案统一验证。本调查未运行任何检查。
