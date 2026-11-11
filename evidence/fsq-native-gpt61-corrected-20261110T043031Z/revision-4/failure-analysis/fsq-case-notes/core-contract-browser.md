# FSQ核心契约、浏览器与剪贴板逐例调查

只读r4存量证据。`事实`=原trace/像素/冻结匹配源直接可见；`强推断`=证据一致但没有反事实或完整wire prompt；`未知`=缺存量数据。主runner（执行并产出正式summary）、独立verifier（事后审查证据）、官方oracle（给reward）三者不能互相代替。下文事件编号为各case原events.jsonl的sequence，step为原execution-result.json的step_id。

FSQ关键源hash与冻结manifest一致，详细见 ../fsq-evidence-index.json.source_identity。额外tools/_tool_artifacts.py亦已逐文件比对匹配；SDK app_start当前3.5.2仅版本匹配、无冻结逐字节绑定，不把其推测当当次执行事实。

## 案例 002 — BrowserDraw

原分类 **failed**，官方reward **0.0**。

用户目标：> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then create a drawing using the three colors shown at the top and hit submit.

**事实与轨迹。** 目标是用顶端三色作画并提交。Files/Chrome 首启处理占用前21步；随后 step23 视觉识别三色，step24/25、27/28、29/30依次选色与画线，step31做图像比较，step32点击 Submit，step33/34观察并断言 `Success!`。实际查看 step23 与 step35.prepare 截图：青绿、品红、深蓝三条线及 Success 均可见。写入19/20，未发生预算拒绝；主 runner、独立 verifier 均 success。

**首个偏离与直接失败。** 作画/提交上没有可证偏离；首个已执行的末态破坏动作是step35 kill。worker request.appId及该step invoke.metadata.harness_output.app_id均精确为`com.android.chrome`；冻结匹配driver调用`app_stop`。harness逐例核对的冻结`android_world/task_evals/single/browser.py::BrowserTask.is_successful:98–109`要求Chrome仍在前台且当前element.text精确`Success!`，并无文件/下载落盘结果通道。**主强推断**：用户目标达成后，Skill统一kill破坏官方读取所需前台。**未知**：没有评分瞬间activity/forest或kill后图，不能提升为已实测postkill状态；官方0保留，不编造坐标错误。

**机制与方案 CORE-LIFECYCLE（P0，FSQ Skill/runner/verification主责，harness核对契约）**：`resources/skills/android-harness.md:7–10`强制先采最终证据再kill；`UiAutomator2AndroidDriver.kill_app:102–107`直接app_stop，与用户要求保持的末态不自动相容。应将用户末态约束与资源释放分开，一般化判断前台/持续状态是否为交付不变量，不按Browser任务名特判；资源close不得破坏必要业务态，verifier不得把kill前证据当kill后保证。若实验仍坚持无条件kill，必须明确其与前台rubric互斥而非重开Chrome后评分、提前评分或改旧分。风险：需要明确一般清理与保留状态边界；未来在批准环境以同一完整native返回后一次oracle核对submit→close→前台状态，同时覆盖允许清理的数据持久化任务。本轮仅方案。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-assert_with_ai-23 prepare](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/artifacts/screenshots/screenshot-agent-assert-with-ai-23-prepare-before-action-1-69add8a6eb03.png)；prepare是动作前，不当动作后。
- 已实际查看像素：[agent-kill_app-35 prepare](../../next-stage-plan/execution/run/episodes/002-BrowserDraw/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-002-20261110T155002Z-54c0a1/artifacts/screenshots/screenshot-agent-kill-app-35-prepare-before-action-1-60e616ed4838.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（FSQ↔harness owner逐例批B）。双方一致：Success画面和Chrome kill目标已证实；官方前台+Success判据已定位；kill导致0为主强推断，评分瞬间状态仍缺证。**

## 案例 003 — BrowserMaze

原分类 **failed**，官方reward **0.0**。

用户目标：> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then navigate the X to the bottom-right cell, by using the direction buttons.

**事实与轨迹。** 目标是用方向按钮把X移至右下。前22步打开文件并处理Chrome首启；step23截图为4×4格，X在左上、右下绿格；按step24–29的 Right→Down→Down→Down→Right→Right，step30出现 Success。step31 AI断言明确要求“仍可见X及右下格”，实际截图只剩 Success，故断言 failed；主输出 inconclusive，独立 verifier failed。写入18/20，无预算拒绝。

**首个偏离与直接失败。** **事实**：FSQ把“达到右下”的转换收紧成“最终屏幕仍显示格子与X”的新增条件，成功后网格已被Success替换，故pre-plan/step31要求额外终态导致原生否决，不是路线走错。官方冻结`BrowserTask.is_successful:98–109`只要求Chrome前台+element.text=`Success!`，不会要求网格继续存在。另step32 kill的invoke输出和request都指`com.android.chrome`。因此**官方0主强推断为后续kill破坏前台**，原生验证失配是独立问题；缺评分瞬间activity/forest，不能把任何一条推断写成postkill实测。

**方案 CORE-TRANSITION（P1，FSQ）+CORE-LIFECYCLE（P0）**：具体改`agent/_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS:37–40`和`agent/_verification_task.py::VerificationEvidenceBuilder.build:31–58`，保留用户状态转换而不新增持续可见条件，使用最后一步前后证据关联Success；同时按一般用户末态优先原则修Skill生命周期，不允许靠提前oracle或评分前重开掩盖冲突。`agent_engine.run_agent:155–173`本案正常返回业务inconclusive，不是引擎异常。风险：并非任意Success文案都可采信，必须和实际任务路径关联。未来离线fixture验证成功后网格替换及不额外按键，另获批准才验证完整native返回后的前台与单次oracle。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-assert_with_ai-23 prepare](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/artifacts/screenshots/screenshot-agent-assert-with-ai-23-prepare-before-action-1-246373944982.png)；prepare是动作前，不当动作后。
- 已实际查看像素：[agent-assert_with_ai-31 prepare](../../next-stage-plan/execution/run/episodes/003-BrowserMaze/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-003-20261110T155454Z-035d6c/artifacts/screenshots/screenshot-agent-assert-with-ai-31-prepare-before-action-1-8925a2352fe2.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（逐例批B）。双方一致：右下路线/Success已证；FSQ自造终态条件导致自身否决；官方0与Chrome kill前台冲突高度一致但缺边界快照，二者不得混为同一已证原因。**

## 案例 004 — BrowserMultiply

原分类 **failed**，官方reward **0.0**。

用户目标：> Open the file task.html in Downloads in the file manager; when prompted open it with Chrome. Then click the button 5 times, remember the numbers displayed, and enter their product in the form.

**事实与轨迹。** 目标要求点击5次、记数并将积填入表单。step20后初始页面已显示一个数，step21/23/25/27/29共5次 Click Me；观察到数列后计算并在step32填写20250。step33 exact text定位失败，step35用包含placeholder的实际节点文本校验通过；最终 step36.prepare 截图仍见答案20250与可点击 Submit，全轨迹无 Submit 点击。native runner/verifier均 inconclusive，因为它们纠结“初始数算不算点击后的数”。写入17/22，无动作预算拒绝。

**首个偏离/直接失败。** **事实**：数列9×10×9×5×5=20250正确，缺口是输入值后没有点击页面Submit，因此没有产生Success结果。冻结同组Browser判据要求Chrome前台+Success，表单框有值并不足够。首次可证偏离在step32以后只验输入框、未完成提交；原生纠结初始数的时序是验证建模问题而非真实算术错误。step36又实际kill Chrome，是第二条终态风险，不能用其掩盖更早的未提交。

**方案 CORE-SUBMIT（P1，FSQ）+CORE-LIFECYCLE**：具体改`PRE_PLAN_AGENT_INSTRUCTIONS:37–40`及主runner表单完成策略，区分填值与提交；对本授权任务执行必要Submit并验证页面结果，而不以输入框assertion作终态。不要为满足自造“五个post-click显示”条件多点第6次；成功后保留用户需要的前台状态。风险：支付/发送等副作用任务不得泛化为未经授权的自动提交；应按既有用户意图边界。未来以首数预先显示、第五次切换表单的离线fixture验证计数、积、提交与结果证据；不执行本轮重评。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-kill_app-36 prepare](../../next-stage-plan/execution/run/episodes/004-BrowserMultiply/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-004-20261110T155850Z-a9df1c/artifacts/screenshots/screenshot-agent-kill-app-36-prepare-before-action-1-ab718384072d.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（逐例批B）。双方确认20250计算正确、未Submit是确定差距；不得定性算术失败；Chrome kill为另一个已执行末态风险。**

## 案例 013 — ExpenseAddMultipleFromGallery

原分类 **passed**，官方reward **1.0**。

用户目标：> Add the expenses from expenses.jpg in Simple Gallery Pro to pro expense.

**事实与轨迹。** 原正式 passed/1 必须保留，本例新增调查是 mainAnswer 生产契约失败。source `000016-assert_with_ai.json` 从 expenses.jpg转录Dress436.35/Clothes/Paid by card、Furnishing350.07/Housing/A need、Dental Care39.54/Health Care/A need；事件71–165填写并保存三笔。事件167后逐笔重开并断言；事件191/207确认Housing/Clothes，Dental Care保存前有Health Care选中，保存后未单独确认该category。主循环过程中反复读取相同source artifact23次；末尾事件217/218又读取已保存断言切片，事件221 `run_failed` 的实际error为 `Agent exceeded the configured turn limit.`，主runner step1 failed，未产出正式summary。写入46/60、denied0、deadlineExceeded=false；不是动作预算/外层超时。独立verifier inconclusive不能替代main summary。

**机制。** `agent_engine/_runner.py:141–174` 对每次模型响应计turn，工具调用后continue，达到max_turns直接抛EngineError；`adapters/coding_agent/_runtime.py:343–375`返回失败runner而非AgentFinalOutput。重复读历史证据是事实；工具工件多层JSON字符串及历史输出淘汰可能诱发失去已读进度，是**强推断**而非有完整wire prompt的证实。首个可证恢复效率偏离是相同范围反复读却不形成稳定记录表；直接契约失败是100turn结束无final，而非费用未保存。

**方案 CORE-ARTIFACT/CORE-TERMINAL（P1，FSQ）**：`tools/_tool_artifacts.py:23–45,51–64`提供由原生结果生成的结构化status/result/explanation投影或可按字段定位的读取，避免反复在转义JSON任意字符窗口寻值；保留原始artifact不删证据。`_ToolOutputBudgetFilter:93–115`淘汰历史大输出时保留简短、带artifact身份的已确认事实与cursor，不仅剩路径。`run_agent`/runtime加入不增加max_turns的进度检查与预留终结阶段：相同artifact hash+范围+相同输出且无新进度时显式提示完成/未知，给模型机会返回合法inconclusive；不能把异常强转成功或用verifier补summary。风险：必要重读不能被一刀切禁止；预留终结占用同一预算，修改须独立设计确认。将来用本案已有trace做离线引擎仿真，验证重复读有界、所有异常保持错误语义、成功/未知均由主runner合法输出。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-press_key-16 prepare](../../next-stage-plan/execution/run/episodes/013-ExpenseAddMultipleFromGallery/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-013-20261110T162850Z-4fb1f6/artifacts/screenshots/screenshot-agent-press-key-16-prepare-before-action-1-45eaa7cefd12.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（FSQ↔harness owner逐例回执）。原passed/1保留；configured turn limit、46/60且零拒绝/无deadline、23次重复读与三条保存已核对；main summary缺失单列，不重标invalid_agent。工件封装/历史裁剪的因果仍为强推断。**

## 案例 014 — ExpenseAddMultipleFromMarkor

原分类 **failed**，官方reward **0.0**。

用户目标：> Go through the transactions in my_expenses.txt in Markor. Log only the rows whose reimbursable field is yes in the pro expense; do not log rows marked no. Copy each original note unchanged from the note field. The reimbursable field is selection metadata, not part of the note.

**事实与轨迹。** 目标明确仅导入reimbursable=yes、排除no、note原样且不包含筛选metadata。打开Markor my_expenses.txt后，source断言000012转录当前32行并明确“整个文件未见，需滚动”；000014称末尾可见，000018称顶部可见，000021仅列当前可见行，所有转录窗口均报告no。事件65回Home、73开Pro Expense，但整个native trace没有任何新增费用input/save。随后对同一批assert artifact的search_artifact共55次，反复查explanation；事件221 max_turns，主runner1 failed，无main summary。写入12/60、无拒绝/无deadlineExceeded。官方failed0。

**首个偏离与根因。** **事实**：只在读过的viewport断言no，未建立逐行覆盖集合，却停止文件探索并在Pro Expense空转搜旧结果；最终既未写入也未闭合源覆盖。**强推断**：把局部“当前无yes”提升成全文件候选无匹配，随后缺少可操作的覆盖/转录记忆；独立verifier的“可能无需新增”不是官方无目标的证明。frozen params另有两条目标行，但不能事后把目标直接交模型。**未知**：目标行位于未覆盖何段、是否可见metadata渲染异常，需官方fixture+源画面定位；没有磁盘文件快照，不硬断AI把yes看成no。

**方案 CORE-COVERAGE + CORE-ARTIFACT（P1，FSQ）**：在pre-plan对筛选导入任务生成带首尾/相邻重叠anchor的viewport ledger，已观察局部否定不能作全局空集；使用原生观察证据提取稳定字段（name,amount,category,note,reimbursable）后保留完整源行及筛选理由，再做写入。`ToolArtifactStore.search:66–95`按转义原文搜索本身不会产生全文件覆盖；runtime须避免同一search结果无限重复而给出未知/不完整。note字段只能复制源note，不串入reimbursable。风险：不能把fixture目标数、hidden yes行直接传入策略；覆盖不确定必须停为inconclusive而不是猜导入。未来离线用含大量no和跨屏yes的公开合成源测覆盖及原note保持，再另行批准端到端验证。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-swipe-12 prepare](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/artifacts/screenshots/screenshot-agent-swipe-12-prepare-before-action-1-f2776ae6eb81.png)；prepare是动作前，不当动作后。
- 已实际查看像素：[agent-swipe-21 prepare](../../next-stage-plan/execution/run/episodes/014-ExpenseAddMultipleFromMarkor/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-014-20261110T163817Z-c88635/artifacts/screenshots/screenshot-agent-swipe-21-prepare-before-action-1-6d02f666de71.png)；prepare是动作前，不当动作后。

**交叉核对：已核对、有保留（逐例回执）。12/60零拒绝、55次search、无新增及max_turns双方一致；局部no不能证明全文件no。yes所在未覆盖段或渲染异常仍未知，不把模型漏看具体yes写成事实；原failed/0保留。**

## 案例 048 — RecipeAddMultipleRecipesFromMarkor2

原分类 **failed**，官方reward **0.0**。

用户目标：> Add the recipes from recipes.txt in Markor that take 10 mins to prepare into the Broccoli recipe app.

**事实与轨迹。** 目标为导入Markor recipes.txt中准备时间10 mins的菜谱。000011-assert_with_ai.json真实转录含完整 Beef Stir Fry / 2 servings /10 mins /as per recipe/完整directions；实际查看source画面也能见该行。后续000013/18/20只是其他viewport无完整10mins行，并均说未到文件底。主执行未打开Broccoli、没有任何创建/保存。read_artifact_slice共81次，后半反复读相同4个source断言，事件219 max_turns，主runner1 failed。写入9/60、无deadlineExceeded，official failed0。

**首个偏离/机制。** 至少一条合格完整候选已被公开源感知并存入artifact，却没有进入待导入记录集；后续局部无匹配窗口压过先前正例，全部时间耗于重新读取而非推进。它不是“所有10mins文本都看不清”，更不是写预算不足。直接失败为未创建+100turn无final。原生结果/历史裁剪/JSON字符串封装机制见CORE-ARTIFACT；缺稳定候选集合与覆盖ledger是**强推断**，模型内部记忆不在存量证据中。

**方案 CORE-COVERAGE + CORE-ARTIFACT/TERMINAL（P1，FSQ）**：将每次观察得到的合格行保留为带source refs的候选记录，后续无匹配窗口不得删除早先候选；仍需继续到可证明文件尾/覆盖闭合，不能把一条当全部。用稳定结构化字段提取取代80次字符切片读；在现有100turn内给合法收尾机会，不私加预算/重试。将来公开合成csv跨屏包含多个10mins与同名非10mins记录，验证完整性、字段不串行及无重复创建；本轮只方案。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-swipe-11 prepare](../../next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-048-20261110T185014Z-65e17d/artifacts/screenshots/screenshot-agent-swipe-11-prepare-before-action-1-0d6bc1314db9.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（逐例回执及harness RecipeMedia独立调查）。000011已完整记录Beef Stir Fry/10mins、81次slice、未录入Broccoli、9/60未耗尽及max_turns双方一致；不能说全部看不清。原failed/0保留。**

## 案例 049 — RecipeAddSingleRecipe

原分类 **passed**，官方reward **1.0**。

用户目标：> Add the following recipes into the Broccoli app: Recipe: Chicken Caesar Salad Wrap  description: An ideal recipe for experimenting with different flavors and ingredients.  servings: 3-4 servings  preparationTime: 2 hrs  ingredients: as desired  directions: Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand.

**事实与轨迹。** 原正式 passed/1不变。目标给定 Chicken Caesar Salad Wrap全部字段。事件39–69填写并Save；首次preparation-time输入失败后重定位重试成功，保存后对directions、description、servings、2hrs、ingredients和title逐项断言。实际查看step29/33.prepare截图可读全部指定内容。自事件85起开始读29–33号断言artifact，随后重复按固定字符窗口循环；read_artifact_slice共66次。事件219 `run_failed` max_turns，runner1 failed，但verifier success。写入18/24、未耗尽，无外层deadline证据。

**机制与偏离。** 保存/核验已成功后仍循环读取已通过断言，没有结束主agent并生成task_run_v1；第一可证无进展区间为事件99–107的固定五artifact模式及之后重复，直接mainAnswer失败是EngineError而非录入失败。`_runtime.run_task:343–375`不会把已完成UI强行当合法summary；这是正确的错误保留。**强推断**：工件封装/历史输出替换与模型未归纳断言状态共同诱发循环；无法从存量数据区分各自因果权重。

**方案 CORE-ARTIFACT + CORE-TERMINAL（P1，FSQ）**：为每个原生断言直接返回短、可机器读status和evidence ref，避免模型为读passed再翻巨大runner_result的转义字符串；使用带身份的assertion ledger，已读结果可查询而不是反复按offset。遇重复无进展引导完成合法主输出，且任何主执行错误仍不能用独立verifier冒充main summary。将来离线复用本案已通过的断言结果序列模拟重复五工件循环，验证不额外写库、不篡改官方passed和能在原turn预算收尾；不执行。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-assert_visible-29 prepare](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/artifacts/screenshots/screenshot-agent-assert-visible-29-prepare-before-action-1-99e4a198941d.png)；prepare是动作前，不当动作后。
- 已实际查看像素：[agent-assert_visible-33 prepare](../../next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-049-20261110T185806Z-24d4f8/artifacts/screenshots/screenshot-agent-assert-visible-33-prepare-before-action-1-215a96eef275.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（逐例回执及harness独立字段核对）。保存字段、66次slice、18/24未耗尽和max_turns无main双方一致；原passed/1保留，exact_main_summary只标主输出契约异常，不推导reward无效或重标invalid_agent。**

## 案例 101 — SystemCopyToClipboard

原分类 **invalid_evaluator**，官方reward **None**。

用户目标：> Copy the following text to the clipboard: Tracking #: 5K672F4C

**事实与轨迹。** 用户只要求复制精确字符串。主流程利用launcher搜索框：step5输入，step7长按，step9 Select all，step11 Copy成功返回；实际查看step11.prepare图，目标整串被全选且Copy菜单可见。之后step13清空原输入；pre-plan另增“粘贴空框验证”步骤，step15空字段selector失败，step16 AI证明空框，step17长按、19找text=Paste失败，step21再次长按，24恢复与25kill均因write预算10/10拒绝。主runner返回合法inconclusive，verifier failed。官方独立异常堆栈只说明Clipper广播未提取payload，original invalid_evaluator/null必须保留。

**分开的失败链。** **事实**：原生可见copy dispatch与未成功paste并存；未成功paste不等于未复制成功。新增剪贴板验证消耗了有限写预算，且locator混用Select all/Copy的accessibilityId与Paste的text，存在具体可查的target-resolution失败。**强推断**：额外验证策略/空框菜单状态不稳导致恢复闭环；不能从失败的Paste证明系统clipboard空。官方helper失败是另一条环境/评价链，既无raw broadcast output也无当时Clipper前台/权限证据，缺权限/前台/解析等均为候选，不能坐实模型造成。

**方案 CORE-CLIPBOARD（P1，FSQ主验证策略+harness诊断）**：pre-plan把复制目标和粘贴验证分开，验证不确定不要擦除唯一已观察内容后反复消耗写预算；针对当前menu实际语义定位而不猜text，保持预算不增且恢复/teardown需遵守同一门控。官方`get_clipboard_contents→_extract_clipper_output`需在允许的私有诊断内保留安全的广播exit/返回形状/前台与授权前提证据（不泄露用户剪贴板内容），供区分环境无效与业务失败；不能把invalid改0或补评。风险：clipboard是全局敏感状态，新验证能力必须遵循权限和任务边界；未来纯离线parser fixtures测缺payload/非OK/空值分支、另获设备许可后才验证前台时序。本轮不修权限、不重跑。

**原证据入口**：
- [publicGoalPath](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/sources/000-goal.txt)
- [nativeResultPath](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/worker/fsq-task-result.private.json)
- [nativeExecutionPath](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/execution-result.json)
- [nativeEventsPath](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/events.jsonl)
- [nativeActionAuditPath](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/worker/native-action-audit.jsonl)
- 已实际查看像素：[agent-tap_on-11 prepare](../../next-stage-plan/execution/run/episodes/101-SystemCopyToClipboard/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-101-20261110T222021Z-1d7fe0/artifacts/screenshots/screenshot-agent-tap-on-11-prepare-before-action-1-97342bf1197c.png)；prepare是动作前，不当动作后。

**交叉核对：已核对（逐例回执）。Copy dispatch成功不证明clipboard内容、Paste失败不证明复制失败；10/10恢复拒绝属于业务验证链。官方RuntimeError/Clipper None payload独立保留invalid_evaluator/null；权限、前台、解析等候选仍未知，绝不改0。**

