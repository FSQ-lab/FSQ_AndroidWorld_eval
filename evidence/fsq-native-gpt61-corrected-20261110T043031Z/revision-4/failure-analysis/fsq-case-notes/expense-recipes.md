# FSQ r4：费用与菜谱八例离线调查

覆盖且仅覆盖 **015、016、017、019、046、047、050、052**；不覆盖父调查者负责的 013、014、048、049。八例原始 officialReward 均为 **0.0**，本笔记不重评分。只读取已保留文件、解析轨迹与渲染已有截图；未触碰设备、ADB、模拟器，未运行任务、测试、安装或模型调用，未改变项目、SDK、配置和旧结果。

## 阅读约定与证据边界

- `BASE` = `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`（FSQ_AndroidWorld_eval 仓库内）。
- `P015` 等 = `BASE/next-stage-plan/execution/run/episodes/015-ExpenseAddSingle`；其余按下文案例名替换。`RNNN` 是该 episode 下的 `raw-private/fsq-native/workspace/.fsq/runs/android/<下表run目录>`。
- 每例 `E序号` 均指 `RNNN/events.jsonl` 的 `sequence`；`S后缀` 指 `RNNN/execution-result.json.steps[step_id="agent-后缀"]`，不是推测的 AndroidWorld step。动作参数以事件 `tool_call_started.tool_arguments` 和 invoke phase 的 `safe_replay_params` 为准。
- 每例均已读取原 `execution-result.json`、`events.jsonl`、`report.json`、`sources/000-goal.txt`，以及 `PNNN/raw-private/fsq-native/worker/{fsq-task-result.private.json,native-action-audit.jsonl,request.json}`、`PNNN/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。已解析这八例所有执行 phase 引用的保留 UI JSON（分别 27、27、37、44、54、55、23、43 份），并实际渲染初始、关键分岔、最终的相关截图。UI XML 的压缩/截断元数据不被当作完整数据库；视觉结论只取实际已渲染的画面。
- **fixture 时间**：八例初始化 `initializationReferenceTime.referenceTime=2023-10-15T15:34:00+00:00`，timezone UTC。下文 Today/Yesterday 和 October 范围以此解释；不能拿 2026 年宿主执行时间替代。
- **事实**＝参数、审计、UI或官方日志直接支持；**强推断**＝多证据一致但没有留存数据库终态；**未知**＝当前材料不能区分。模型总结、assert_with_ai 的解释、FSQ verifier 与官方 reward 分层列出，互不替代。
- 私有 `frozenTaskSpec.params` 只作为事后解释初始构造的证据；不作为未来模型的目标答案或定位提示。未发现这八例有保留的 before/after SQLite 数据库，因此不伪造逐行终态证明。

| R别名 | run目录 |
|---|---|
| R015 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-015-20261110T164716Z-176566` |
| R016 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-016-20261110T165000Z-725bae` |
| R017 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-017-20261110T165331Z-6053d7` |
| R019 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-019-20261110T170134Z-7f8f64` |
| R046 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-046-20261110T183830Z-e687b6` |
| R047 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-047-20261110T184424Z-a393d7` |
| R050 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-050-20261110T190605Z-9e00e8` |
| R052 | `fsq-native-gpt61-r4-clock-lifecycle-20261110-run-052-20261110T191501Z-60f662` |

## 冻结实现的共用证据与责任边界

FSQ 冻结包 SHA256 为 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`，version 0.1.2；观察到 HEAD 7e3f079 但工作区 dirty，不能仅凭 HEAD 当作执行身份。下面引用的 FSQ 文件均在父调查者已逐文件核对一致的 `failure-analysis/fsq-evidence-index.json.source_identity.mechanism_files` 内。源码路径相对 `/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/`：

1. **生命周期不是业务成功**：`resources/skills/android-harness.md:5-10` 要求先 launch、最终取证后 kill；`drivers/android/_uiautomator2.py::launch_app:94-100` 只调用 `device.app_start` 并返回 passed，没有前台包/活动的成功后置条件。八例首个 launch 后截图仍是 launcher 是事实，**不足以断言 app 未安装、驱动必坏或设备不可用**；随后从 launcher 点击图标均能进入应用。启动语义由父调查者与 harness owner 另核。
2. **定位参数有精确定义**：`UiAutomator2AndroidDriver::_selector:356-369` 对 XPath 原样交给 `device.xpath`，而 `target` 只变成 `device(text=...)`；`_selector_query:371-381` 中 `accessibilityId` 才映射 description。`tap_on:109-116` 没有命中就返回 target missing，不会自动从 text 回退到 content-desc。现有 Skill `android-harness.md:14-18` 已要求从当前结构中取 resourceId/accessibilityId，失败后刷新观察；不能把所有 missing target 统称坐标问题。
3. **长字段观测是有损的**：`UiAutomator2AndroidDriver::ui_snapshot:237-276` 与 `_compact_ui_snapshot_attributes:321-335` 把 text/content-desc/hint 截至前 50 字符，报告 partial coverage。`adapters/coding_agent/_runtime.py::_ToolOutputBudgetFilter.__call__:93-115` 会把非最近/超预算的工具结果换成 artifact 指针，`_artifact_path_for:117-135` 保留可再读原文；这是可解释反复读旧转录的机制，不是“结果已丢失”的证明，也不直接证明每次重读都由过滤器强迫。
4. **预算边界是真实的外层准入，不是模型轮次**：实际 producer 快照 `P046/raw-private/fsq-native/worker-site/fsq_androidworld_eval/fsq_native.py::NativeDispatchBudget.dispatch:85-118` 先计 admitted，再 forward；返回失败也不返还。`WRITE_CAPABILITIES:20-26` 包含 launch/kill/tap/input/key/swipe，不含 snapshot/assert。八个 episode 的这份快照 SHA256 均为 `0af6d9b3802fcfd5708bc9dcdf2132bf48a9e3da01ae0401fafa6ae9ad468e13`。所以观察次数多会浪费轮次/推理，但不能说它们直接耗尽 write budget。
5. **预算没有被这条输入链显式交给规划/主模型**：producer `fsq_worker.py::execute_worker:191-197` 用公开 goal 建 Task，将 budget 作为 harness/cancellation 边界；`_runtime.py::run_task:308-315` 调 `_build_task_input(task)`；`agent/_pre_plan.py::build_pre_plan_input:60-85` 没有 maxActions/remaining/deadline；`agent/_prompt.py::PromptModelBuilder.build_task_prompt:65-96` 虽有 runtime_policy 入口，但该调用没有传预算策略。这支持“约束不可见”的跨边界缺口，而不是证明模型完全不知道任何限制。
6. **runner success≠业务完成≠官方成功**：`_runtime.py::run_task:431-444` 对正常返回的结构化输出记运行步骤 success，业务仍可 inconclusive。019/046/047/052 原 `fsq-task-result.private.json` 的 `agent_runtime.runner` 均为 status success、error null；没有 max_turns 异常证据。它们的 native audit 也没有 action-budget 或 deadline 拒绝。046/047 自述“time limit”时，全服务返回还分别距 businessDeadline 约 3393/3396 秒；不能把自述包装成实际硬超时。015/016/017/050 才有真实 action_budget 拒绝。
7. **pre-plan 没有把任务缩成一个对象**：`agent/_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS:37-46`、`build_pre_plan_input:60-85` 和各例 E7/E8 所得计划都要求完整集合/每道 recipe。主要落差发生在主执行过程中，而非公开目标被 planner 错改。`agent/_verification_task.py::VerificationEvidenceBuilder.build:48-56`、`VERIFICATION_AGENT_INSTRUCTIONS:183-198` 要求证据不足用 inconclusive；verifier 是只读收尾，不会替主 agent 补录或删除。

以下 ER-* 均为**未来改进建议**，不是已实施修复。不提高预算、不增加未授权重试，不向模型泄漏私有记录，不放宽 exact-duplicate 或持久化标准。

## 案例 015 — ExpenseAddSingle

**交叉核对：已核对。** 四字段正确、Save未forward、diagnostic168 missing row；不声称原12写必无解。

### 目标与结果

公开目标（`R015/sources/000-goal.txt`）：新增 Therapy Sessions，$307.01，Health Care，note `I may repeat this`。必须保存一条记录，不能把填好表单当完成。officialReward **0.0**；原生任务/verifier 最后 failed，主 runner 的业务总结 inconclusive。

### 实际决策与屏幕转换

1. E19/Slaunch_app-1 以默认 app 启动，Sui_snapshot-2 与 launch after 截图仍为 launcher；E23/Slaunch_app-3 显式 `com.arduia.expense` 再启一次后仍在 launcher。E25/Sswipe-4 拉开 app drawer，E31/Stap_on-6 按 accessibilityId `Pro Expense` 进入 Home。启动返回 passed 不证明已进入 app。
2. E35/Stap_on-8 点 `fb_main_add`，进入 Expense Entry。E39/Sinput_text-10 填 `edt_name=Therapy Sessions`，E41/Sinput_text-11 填 `edt_amount=307.01`；E43/Spress_key-12 Back 收键盘。
3. E47/Sswipe-14 在类别条作水平滑动，当前类别由 Food/Income/Housing 等变为 Entertainment/Transportation/Clothes/Health Care；E51/Stap_on-16 点 Health Care。E53/Sinput_text-17 填 `edt_note=I may repeat this`；E55/Spress_key-18 再 Back。最终截图可见金额、备注和选中色 Health Care，SAVE 仍在；UI 的 checked 状态也支持类别已选，**不是填错类别或金额**。
4. E59/Stap_on-20、E61/Stap_on-21 均点 `btn_save`，但都在 dispatch 之前被 `NativeActionBudgetExceeded: action_budget` 拒绝；E63/Skill_app-22 也被拒绝。审计 sequence 1–38 已累计 12 次 admitted write，seq39/40/41 分别拒绝 Save/Save/kill，seq44 才返回。第二次 Save 不是有效提交重试。

### 首次偏离、直接失败、机制

- **首次可证低效偏离**：Slaunch_app-3 在同样 launcher 状态再消耗一次 write；它未达到启动后置条件。尚不能据此把整个启动问题归因给 FSQ；首个**确定阻断业务**的点是 Stap_on-20 保存被拒。
- **直接失败【事实】**：只完成内存中的编辑表单，零次 Save dispatch 真正转给 native driver。官方 `P015/raw-private/evaluator-diagnostics.json` 在 `validate_rows_addition_integrity:168` 报 expected row not found（参数对象被省略）；这与未保存一致。
- **根机制【事实+强推断】**：12 次有限 writes 被启动/导航、输入及键盘关闭分完，没有为提交保留动作；producer 硬边界没有错把 Save 当观察，问题是执行层不知道/未规划这条边界。Save 失败后重复同类调用也无法恢复额度。pre-plan 和主执行输入的预算缺口见共用证据4–5。
- **未知**：本次为什么 app_start 未使前台进入 Pro Expense；若更有效导航，完整链在12单位内的实际最短合法路径还没有执行验证。不能承诺单删一个动作就同时给 Save 和 kill 腾够额度。

### 可定位改进

**ER-015，P0，owner：FSQ runtime + harness producer 共同**。在 `fsq_worker.execute_worker:191-197` 与 `_runtime.run_task:308-315` 的公开运行约束交界，将现有最大/剩余额度、write分类、终止原因传入 runtime_policy/每次 tool result；`PromptModelBuilder.build_task_prompt:65-96` 和 `build_pre_plan_input:60-85` 接收这一非私有约束。提交型任务执行时先为 Save 和必要 teardown 留额度；明确 action_budget 是本轮不可恢复拒绝，不再重发同一 Save。`launch_app:94-100` 的成功条件应由启动语义调查决定，不能靠免费额外动作或“忽略启动”掩盖。

预防点：让“表单已填”到“提交落盘”的边界先被规划，避免输入成功却没有提交资格。边界/风险：不合并或免费化已经计费的动作，不自动取消用户数据，不把键盘 Back 一律删掉；启动检查须能处理合法跨应用目标。未来验证：同12预算、同公开目标的受控回归检查只发生一次成功 Save、重开后四字段仍一致，并验证拒绝后不会生成第二次无效提交；当前未运行。

### 精确取证入口与待核问题

- 表单最终像素：`R015/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-26872d04ee3a.png`；其同一步 phase 的 `ui_snapshot` 引用给出 checked Health Care。
- 初始：`screenshot-agent-launch-app-1-finalize-after-action-1-651a837c4b1b.png`；开表单：`screenshot-agent-tap-on-8-finalize-after-action-1-5b4647628b9e.png`；类别横移后：`screenshot-agent-swipe-14-finalize-after-action-1-7ecb2837f7e0.png`，均在 R015/artifacts/screenshots 下。
- 请 harness owner 确认未保存的 expected-row 缺失诊断及启动实际语义；保留没有 SQLite 终态的证据缺口。

## 案例 016 — ExpenseDeleteDuplicates

**交叉核对：已核对、有保留。** 同屏两条Public Transit仅候选非已核exact；XPath失败计费合约；oracle仅删一个target ID且noise不变，终DB未知。

### 目标与结果

公开目标：Pro Expense 中每组**完全相同**费用只保留一条，每种不同费用至少留一条。不是按同名/金额直接删。officialReward **0.0**；FSQ 最终 inconclusive。

### 实际决策与屏幕转换

1. Slaunch_app-1/3、Sswipe-4、Stap_on-6 与015同样经过两次 launch、app drawer、图标才进 Home。
2. E35/Stap_on-8 用 `//node[@resource-id='...:id/toolbar']/node[@class='android.widget.ImageButton']` 找汉堡菜单，Target was not found；E37/Stap_on-9 改成 wildcard 但仍以 class 属性筛选，同样未命中。当前保留 XML 中 toolbar 下确有无标签 ImageButton，bounds `[0,128][147,275]`。E39/Stap_at-10 用当前证据点 `(74,200)` 才展开 drawer；没有证据说坐标这一步点错。
3. E47/Stap_on-12 进入 Expense Logs，区间 **2023 Oct 1–14 . DESC**。该步 XML 已同时列出两条 Public Transit，均 Oct1、204.41；截图中该候选出现在列表下端，但不能凭列表就知道 note/category 是否完全一样。E49/Sui_snapshot-13 后 E51 读列表 artifact。
4. 没有打开任一 Public Transit 详情，也没按 Delete。E53/Stap_on-14 打开 Filter，E57/Stap_on-16 打开起始日期，E61/Stap_on-18 点年份进入 year selector，E65/Stap_on-20 CANCEL 回 Filter，没有选新日期、没有 APPLY FILTER。
5. E69/Spress_key-22、E71/Spress_key-23 的 Back 以及 E73/Skill_app-24 均被 action_budget 拒绝，停在 Filter。审计 seq15/17 为两次失败 XPath 的 admitted writes，seq39 第12单位是 CANCEL，seq43–45 是三个拒绝。

### 首次偏离、直接失败、机制

- **首次可证执行偏离【事实】**：Stap_on-8/9 两个未命中 selector 消耗写预算；不是“app没有可用删除能力”。S12 之后可见具体候选，主执行却先进入日期探索，没有开始内容比较。
- **直接失败【事实】**：全程没有删除或确认删除动作；exact-duplicate 比较也没有发生。
- **事后解释【事实+强推断】**：初始化 `frozenSpec.params.row_objects` 是两条完全相同的 Public Transit（20441 cents、category7、note A need、created/modified相同），噪声5条。该信息不应给未来 agent；它解释为何没有删除导致0分。没有数据库终态，不能把当前 XML 两条可见字段相同升级为模型当时已证实“exact duplicate”。
- **根机制**：一部分预算花在 compact XML 与 native XPath 接口间未经确认的定位表达；`_selector:356-365` 原样转发，不会解释 compact node 语义。两次未命中的底层原因未留存，不能断定是哪种 XPath backend 转换。随后“先完整改筛选再比较”的线性执行未随仅12预算调整；datepicker 取消操作对业务无进展。planner本来要求完整费用内容比较，主执行没落实。`android-harness.md:14-18` 的刷新与定位优先级已有规则，但未防止此处重复失配。

### 可定位改进

**ER-016，P1，owner：FSQ Android Skill/driver工具契约**。在 `android-harness.md:14-18` 与 `UiAutomator2AndroidDriver::_selector:356-381` 处明确“snapshot XML 表示不等于 XPath backend 的可执行节点类型”；给无 resourceId/desc 的单个可点击元素保留可消费的当前 bounds/locator证据，第一次明确 missing 后不得只换等价写法再试。不要静默把任意失败 XPath 改成盲坐标。

**ER-016B，P1，owner：FSQ pre-plan/main prompt**。`PRE_PLAN_AGENT_INSTRUCTIONS:37-46`、`PromptModelBuilder.build_task_prompt:65-96` 对 collection任务要求先记当前可见候选和已覆盖范围，再决定是否确需改时间过滤；改过滤必须有明确目标区间和回到业务列表的剩余额度。对已见 Public Transit 类候选按完整公开内容比较，而不是本案私有名称硬编码。风险：不能因预算小就删除未比对的记录或跳过全局保留约束。未来验证：同12额度下使用公开UI获取各字段、只删冗余实例，验证其余5种费用不变；另用缺失字段/日期范围不完整场景确认保守保留。当前未运行。

### 精确取证入口与待核问题

- `R016/execution-result.json` S8/9 prepare XML 的 toolbar 子节点与 invoke missing target；S12 finalize XML 的两条 Public Transit；native审计 seq15–20、39、43–48。
- 已渲染列表：`R016/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-d18badb0b05a.png`；year selector：`screenshot-agent-tap-on-18-finalize-after-action-1-3340a4d7115c.png`；最终 Filter：`screenshot-agent-kill-app-24-prepare-before-action-1-e8f76868164c.png`；初始：`screenshot-agent-launch-app-1-finalize-after-action-1-e698a921d1fb.png`。
- 官方 diagnostic 没有行级失败日志。请核对 producer 对失败 selector 仍计费是否与既定合同一致（源码当前确实如此），以及未删重复记录的最终诊断；不要求改变计费或重评分。

## 案例 017 — ExpenseDeleteDuplicates2

**交叉核对：已核对。** Oct1尾两条Jeans496.36未覆盖，499.38/500.10/501.98必须保留；从未删，唯一denied为kill，不写删除被挡。

### 目标与结果

公开目标与016同：全费用集合按完整内容去重、每种唯一费用保留一条。officialReward **0.0**，FSQ inconclusive。额度18 admitted/18，唯一拒绝是 teardown；不是一个删除调用被预算拒绝。

### 实际决策与屏幕转换

1. S1/3 launch 后 launcher、S4 app drawer、S6 图标入 Home。S8 用 Android class tag XPath 成功开 drawer，S10 入 Expense Logs，区间 **2023 Oct1–15 . DESC**。
2. E47/Stap_on-12 开 Filter，E51/Stap_on-14 开 From 日期；E55/Spress_key-16、E59/Spress_key-18 连续 Back 回原列表。没有改范围或 APPLY。E65/Stap_on-20 又开同一个 Filter，E69/Spress_key-22 又关。
3. E75/Sswipe-24、E81/Sswipe-26、E87/Sswipe-28 向下浏览。可见 Jeans 的不同条目先后是 **Oct12/500.1、Oct11/501.98、Oct6/499.38**；这些不是同额同日记录，不能因为都叫 Jeans 就删。日志也显示不同金额的 Dividends、Non-Profit Support 等。
4. E93/Stap_on-30 第三次开 Filter，E97/Spress_key-32 关闭；E101/Sswipe-34 到 Oct5–Oct2 区段，底部 Gym Membership/Oct2/164.38。没有滑到 Oct1 的完整尾部，也没有任何费用详情比较。
5. E107/Sassert_state-36 用 text contains 检查日期标签，返回 Text assertion failed；E111/Sassert_visible-38 改成精确标签 `2023 Oct 1 - 15 . DESC` 后通过。这两个断言都没有验证去重。E113/Skill_app-39 被预算拒绝（审计seq77）；最后业务前的 S34 是第18次 write，观察/断言未计write。

### 首次偏离、直接失败、机制

- **首次确定的无进展重复【事实】**：S20/22 在 S12–18 已读完并原样退出之后，再开关同一 Filter；S30/32 再重复。第一个开日期不自动等于错误，但没有新问题/修改目标的反复开关是可证额外消耗。
- **直接失败【事实】**：没有任何删除和 exact-match detail 比较，列表覆盖也没到 Oct1。
- **事后原因【事实+强推断】**：私有初始化有40条噪声，真正同一组是两条 Oct1 的 Jeans、496.36、category8、note Want to have、时间字段相同；它们不在已停留的Oct2终屏。较早看到的同名Jeans金额不同，保留是正确的局部安全判断，不能说“看见重复但没删”。初始构造+无删除使未去掉冗余副本成为强推断，官方0分与之相容。
- **根机制**：主执行没有维护“已覆盖日期/候选字段/未覆盖尾部”的工作表，拿过滤器标签断言代替推进业务；8次与 Filter 有关的写操作占掉18额度的重要部分。Skill和 planner 已要求全内容比较，但缺乏进展约束；不是 verifier 误打成功，也无模型API错误证据。`assert_state:206-221` 的具体失败在此只是次要断言错误，后继成功标签不改变未去重事实。

### 可定位改进

**ER-017，P1，owner：FSQ collection执行策略**。在 `_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS:37-46` 和 `_prompt.py::PromptModelBuilder.build_task_prompt:65-96` 增加任务内有界覆盖表：观察到的列表顺序、首尾边界、每个候选公开字段、未解析组。过滤器原值已知且无修改目标时，禁止重复开关“再看看”；下一步必须推进未覆盖页面或比较候选。日期标签可作导航检查，不计入内容去重完成证据。

理由：把实际剩余任务从笼统“inspect all”拆为可推进的尾部/候选，避免在Oct2停下却不知Oct1未覆盖。边界：不能从本例私有日期或名称给 agent 指定目标；日期相同也不等于完整重复；多次同名但字段不同的条目必须保留。未来验证：保留公开UI路径，既有大量同名不同金额又有完全相同副本时，覆盖到列表尾部、比较完整内容、删除仅冗余一条；对重复开关过滤器作离线轨迹回归；不扩大18额度。当前未运行。

### 精确取证入口与待核问题

- 原生事件 E47–73（两轮filter）、E75–105（滚动与第三轮filter）、E107–114（无关业务断言及kill拒绝）；audit seq23–45、59–68、77–80。
- 初始：`R017/artifacts/screenshots/screenshot-agent-launch-app-1-finalize-after-action-1-0bdc921ca191.png`；进入列表：`screenshot-agent-tap-on-10-finalize-after-action-1-f9bf762df6b6.png`；重复filter：`screenshot-agent-tap-on-20-finalize-after-action-1-f3fb81f8fe65.png`；终屏：`screenshot-agent-swipe-34-finalize-after-action-1-7b73be1ac5e2.png`。
- 待核：隐藏判定是否确系初始化的 Oct1 冗余副本仍存；无保留终态DB，不把该推断说成直接读到DB。不得将18次已用概括成“预算在删除时耗尽”——本例从未尝试删除。

## 案例 019 — ExpenseDeleteMultiple2

**交叉核对：已核对、有保留。** Pet首屏可见后来只下搜且正常提前停；S24 Restaurant Meal142.94详情、S26关闭非误删。Pet残留强推断，终DB未存，不称唯一已证0因。

### 目标与结果

公开目标仅删除 **Streaming Services、Unexpected Expenses、Pet Supplies**。officialReward **0.0**；FSQ inconclusive。23/34 writes，零拒绝、deadlineExceeded=false；全服务返回仍有约1844秒，不能归因预算或已证实的硬超时。

### 实际决策与屏幕转换

1. S1/3 launch、S4 app drawer、S6 图标入Home；S8开drawer、S10入 Expense Logs，范围 **Oct1–15 DESC**。S10 XML和截图已显示 Streaming Services/Today3AM/487.25，紧接 **Pet Supplies/Today12AM/190.95**。这不是私有oracle才知道的定位信息。
2. E49/Slong_press_on-12 长按 Streaming Services，显示关联 Delete 控件；E57/Stap_at-14 `(971,901)` 打开 Delete Items，E61/Stap_on-16 点 `btn_confirm`。S16列表 Streaming Services 消失，**Pet Supplies 仍在同屏第四条**；这是已经看见而未处理的待删除目标。
3. E67/Sswipe-18、E73/Sswipe-20 向下找 Unexpected Expenses，后者位于 Oct11/269.5。E77/Slong_press_on-22 后，E83/Stap_at-24 却点 `(971,292)`，打开的是 **Restaurant Meal** 详情（142.94、Oct12、note I may repeat this），不是目标的Delete。E87/Stap_on-26 `btn_close` 关掉详情，未删除Restaurant Meal。
4. E91 搜索当前 artifact 得到 Unexpected Expenses 相关 Delete bounds `[925,960][1017,1052]`；E93/Stap_at-28 改点中心 `(971,1006)`，进入 Delete Items，E97/Stap_on-30 确认。S30列表该目标消失，支持这条删除流程实际执行成功。
5. 从 E101 起才找 Pet Supplies，却只在当前Oct11以下 snapshot 搜索，然后 Sswipe-32/34/36/38/40/42 持续向下，直到 Oct1 尾部；S40、S42最后两屏相同。**没有一次向上回到早已见过Pet Supplies的位置**，也没有对它进行 long_press/delete/confirm。
6. E137/Sassert_not_visible-43 在列表尾部对 Pet Supplies 通过；E139/Skill_app-44 正常结束。主runner诚实注明仅当前屏缺席不足证明全列表不存在；verifier也没有把该断言升级为成功。

### 首次偏离、直接失败、机制

- **最早可证的目标跟踪缺口**：S16已看见第二个可立即处理的目标Pet Supplies，下一步仍按原计划顺序离开该屏找Unexpected。单独离开不是不可恢复错误，但后续没有记录/回访，使其成为可追溯漏项起点。
- **首次错误点击【事实】**：S24用错误行坐标打开Restaurant Meal，幸而关闭而没有误删。该错误已纠正，不是最终唯一根因。
- **直接失败【事实+强推断】**：两个确认删除流程完成；Pet Supplies从未被删除，且在最后一次离开顶部前仍存在。无后续删除动作，留下它是强推断。官方0分支持任务未完整完成，不能声称已读到最终DB中残留的那一行。
- **根机制**：主模型的多对象计划按目标顺序线性执行，没有“可见位置/已处理/待处理”账本；从中部向下搜不到名字后没有回到已知先前位置。`UiAutomator2AndroidDriver::assert_not_visible:195-203` 只查当前 selector 的存在，不扫描列表、更不检查数据库；当前屏断言通过本身符合工具契约。历史输出替换artifact的机制见 `_ToolOutputBudgetFilter.__call__:93-115`，可能增加早期位置信息丢出当前上下文的风险，但是否直接触发遗忘是**强推断而非可见思维链**。

### 可定位改进

**ER-019，P0，owner：FSQ main execution/Android Skill**。在 `_prompt.py::PromptModelBuilder.build_task_prompt:65-96` 与 `android-harness.md:21-26` 对有限名称集合建立当前任务清单（仅来自公开goal）：每项保存最近可见证据、列表相对位置、delete确认回执、最终核对范围。优先处理同屏目标或明确记下回访点；搜索无结果时先对照“曾见”信息，不能无变化地单方向重复滚动。删除坐标必须绑定当前行bounds，不能沿用其它行坐标；有详情标题不符就回退而不是继续破坏。

另保留 `assert_not_visible:195-203` 当前屏语义，并在工具说明/返回结果显式标注 scope=viewport，禁止把它作为全集合缺席的单一证据。理由：同时阻止漏项和危险的错误对象删除，修正业务证据范围而不弱化rubric。边界：不新增隐私DB读取、不因名字相同推定唯一、不改工具为“自动搜索删除”。未来验证：同34预算让三目标散布首屏/中部、列表有非目标近邻，证明三个准确确认删除、Restaurant Meal等非目标不变，并验证尾部not_visible不能证明首屏目标已删；当前未运行。

### 精确取证入口与待核问题

- `R019/execution-result.json` S10/S16 finalize XML里直接出现Pet Supplies；S24 finalize XML标题Restaurant Meal；S28/S30为纠正后确认删除；S40/S42为重复尾屏。`R019/events.jsonl` E45、63、83–99、101–140；审计seq47–62记录错误点击及纠正，seq63–88为向下找与teardown。
- 已渲染关键图：`R019/artifacts/screenshots/` 下 S16 finalize（可按 execution-result 的 artifact_refs 精确定位）、S24 finalize（Restaurant Meal详情）、S43 before（末屏not_visible）；初始 S1 finalize 亦已渲染。图像定位以原 step 引用为准，避免凭本笔记猜文件哈希。
- 待核：Pet Supplies未删是否对应唯一官方失败项；两个确认删除是否持久化且没有额外受损行。缺少行级diagnostic和最终DB，不能把“两个确认通过”当作完整删除完整性证明。

## 案例 046 — RecipeAddMultipleRecipesFromImage

**交叉核对：harness owner 批B已逐例确认主要失败链，父调查者同意；字节终态与首个缺失行仍未决。** owner 经父调查者传回：冻结 evaluator `recipe.py:354-384` 逐字段比较 title/description/servings/preparationTime/source/ingredients/directions/favorite，free-form 使用 fuzzy≥0.9；`fuzzy_match_lib:20-50` 忽略大小写、使用 SequenceMatcher，不做 whitespace normalize。本调查未自行读取该额外源码，以上为明确归属的协作核对证据。双方一致：只保存1/3、余2未录已构成充分完成差距，单个空格换行不能作为0分主解释。

### 目标与结果

公开目标：将 Simple Gallery Pro 的 **recipes.jpg** 中 recipes 加入 Broccoli；不是只录一张卡片。officialReward **0.0**；原生/verifier inconclusive。实际只使用27/60 writes、零拒绝。原主runner正常返回（duration约291秒），其“time limit”自述没有对应硬deadline或max_turns证据。

### 源读取、复制决定与屏幕转换

1. E19/Slaunch_app-1 指定 Gallery 后仍launcher；Sswipe-3 拉drawer，Stap_on-5 点第一个 Gallery，Stap_on-7 进DCIM，Stap_on-9 开媒体，画面标题明确 **recipes.jpg**。E39/Sassert_with_ai-10 请求完整转录，而非只从文件名猜内容。
2. 该步实际截图可完整读出三道：**Eggplant Parmesan、Baked Cod with Lemon and Dill、Chickpea Vegetable Soup**。第一道字段为 description `An ideal recipe for experimenting with different flavors and ingredients.`、8 servings、10 mins、ingredients `varies`，directions含茄子/酱/芝士烘烤及 fresh herbs 句；后两道也有独立字段。图片没有具体数量，`varies` 等是原文，不是本次模型虚构的配料。AI转录与已渲染源图在这些内容上相符。
3. E41/Spress_key-11 Home、Sswipe-12、Stap_on-14 入 Broccoli。最初列表已有 **Chickpea Vegetable Soup**，但其字段尚未打开核对；不能因同标题就判已满足源配方。E53/Stap_on-16 用 `target="New Recipe"` 失败，因为按钮是 content-desc；E59/Stap_on-18 改 `resourceId=fab_recipes` 成功开表单。
4. 六次 input_text仅针对第一道：S20 title Eggplant Parmesan；S23 description；S26 `8 servings`；S29 `10 mins`；S32 `varies`；S35 directions。每次之间反复搜索或读取同一个 `artifacts/tools/000011-assert_with_ai.json`（共7次search、4次slice读取该转录），并多次Back关键盘。E105/S35 把最后一句前插入 `\n`；保存后详情因而显示**两个编号步骤**。
5. E113/Stap_on-38 SAVE 成功，S39 Back到列表。E121/Stap_on-41 又用同一 `target="New Recipe"`，在已知该用法失败且已知resourceId后仍失败。随后不再创建第二道，E123/Stap_on-42 按标题开 Eggplant Parmesan，E125/Sassert_with_ai-43 只要求核对该道 title/ingredients/directions，通过；它没有覆盖另外两道。最终 Skill_app-44 正常。

### 首次偏离、直接失败、机制

- **首次明确工具使用偏离**：S16把当前content-desc当text target，后来S41重复；此问题通过 `_selector:366-368` 可以直接解释，不是坐标错误。
- **复制内容的潜在首次语义变化【事实，非已证0分主因】**：S35引入方向字段换行，Broccoli最终屏确实分成两步。源图片的视觉排版也包含换行，私有冻结row为一句间空格。harness已确认无whitespace normalize，但free-form为fuzzy≥0.9；仅此单处差异不足解释整例0分。保留UI步骤结构变化的风险，不把AI语义匹配当成字节级一致，也不把这个细节盖过余两道未执行。
- **直接失败【事实】**：只有Eggplant Parmesan发生创建/保存。其余两道没有对应input/save流程；现存Chickpea同名条目没有内容核对。官方 `validate_rows_addition_integrity:168` 报expected Recipe not found，参数对象省略，不能指定究竟首先缺哪一道。
- **根机制【事实+强推断】**：源已完整读取，但执行没有稳定保存三道结构化源字段和逐项落盘清单；反复重读相同AI转录，最终收缩成只验证第一道并正常提前收尾。pre-plan E7/E8本来要求each recipe，故不是planner只规划一道。历史artifact过滤机制及50字符快照（共用证据3）加重工作记忆压力是强推断；没有证据是外层动作预算迫使停机。最终AI断言把description/servings/time说成“不在比较源里”，其真实含义是**当前assert prompt没列它们**，不是recipes.jpg没有它们。

### 可定位改进

**ER-046，P0，owner：FSQ pre-plan/main prompt + runtime历史输出策略**。在 `_pre_plan.py::build_pre_plan_input:60-85` 和 `_prompt.py::PromptModelBuilder.build_task_prompt:65-96` 对“从源复制多个记录”生成源记录数量、每项公开字段、对应保存/重开回执的任务内工作表；源仍可见时一次完成转录确认，随后按未完成条目推进，不在每个字段后重读整份artifact。`_ToolOutputBudgetFilter.__call__:93-115` 可保留有界的已确认源字段摘要/引用，避免非变化转录被反复回读；不是永久保留无限tool输出。

同时在 `android-harness.md:14-18` 明确target仅可用text，对New Recipe这类content-desc必须用accessibilityId或已证resourceId，禁止第二次等价失配。复制应区分文本自动折行、逻辑换段、真实步骤分隔；`input_text:137-151` 本来按给定文本原样输入，不能无依据在driver统一删换行。未来验证：同60额度，用图片含三道且目标app已有一条同名不同字段的场景，逐道保存并重开核对全部源字段；专设视觉换行/逻辑分步对照，按正式字段契约检查持久文本，而非只看AI语义通过。当前未运行。

### 精确取证入口与待核问题

- 源像素：`R046/artifacts/screenshots/screenshot-agent-assert-with-ai-10-invoke-assert-with-ai-1-34261f0a6f44.png`；原转录 `R046/artifacts/tools/000011-assert_with_ai.json`，执行S10 invoke `metadata.harness_output.explanation`亦保留全文。
- 最终像素：`R046/artifacts/screenshots/screenshot-agent-assert-with-ai-43-invoke-assert-with-ai-1-3d3fd372a442.png`，可见两编号Directions；E105精确输入包含换行。S38 finalize支持保存后详情，S39/42支持离开重开后的可见持久性，但不等同完整DB字段校验。
- 审计seq75为Save、81为第二次错误NewRecipe、83为重开、87为kill；seq91正常native_execution_returned。主结果 `steps[tool_name=agent_runtime.runner].tool_output.plan_updates`的time-limit说法与audit剩余约3393秒不符，保持分歧。
- 已核对：逐字段fuzzy边界及1/3保存的主要缺口，理由和协作来源见本例开头。仍未决：哪个expected row首先缺失、每道实际持久文本字节终态；不能从省略了对象参数的官方日志编造具体缺失行。单处换行不再列为主要0分原因。

## 案例 047 — RecipeAddMultipleRecipesFromMarkor

**交叉核对：harness owner 批B已逐例确认主要失败链，父调查者同意；新旧持久ID仍未决。** owner经父调查者核对原S38新条为8/3/as desired，S43重开为3-4/2/optional，与 `noise_row_objects[2]` 精确一致；支持误选旧同名而非保存损坏，另两道未新增已构成充分完成差距。此为协作核对，不冒充本调查读取了最终数据库。

### 目标与结果

公开目标：把 Markor **recipes.txt** 里的所有recipes加入Broccoli。officialReward **0.0**；FSQ inconclusive。27/60 writes，零拒绝；runner正常返回约286秒，“time limit”只有模型自述，audit返回距businessDeadline约3396秒。

### 文件、字段复制与同名记录选择

1. Slaunch_app-1后launcher；Spress_key-2 Home、Sswipe-4、Stap_on-6 accessibilityId Markor，进入文件列表。E35/Stap_on-8 精确点 `recipes.txt`，E39/Stap_on-10 点 `action_preview`，没有编辑或删除原文件。
2. E43/Sassert_with_ai-12 的已渲染preview完整可见三道：**Thai Peanut Noodle Salad、Garlic Butter Shrimp、BBQ Chicken Quesadillas**，末道结束后留白。第一道为8servings、3hrs、ingredients `as desired`，description和完整directions均可见。后两道各自有字段，不是文件读取失败。
3. S13 Home、S14 drawer、S15 Broccoli；S17 `target=New Recipe`失败，S19 `fab_recipes`成功。随后S21/24/27/30/33/36分别填第一道title、description、8servings、3hrs、as desired、完整directions。**没有输入后两道**。在E51、59、67、75、83、91、99、107、115、123共10次从offset0重读同一 `000013-assert_with_ai.json`，每次4800–6500字符，没有新增源页内容。
4. E109/Stap_on-37 `button_save_recipe`成功，S38后保存详情显示 **8servings、3hrs、as desired**。E113/Sassert_state-39 对完整directions locator存在通过；这个driver断言直接对native selector执行，不受保留XML的50字符截断限制。
5. S40 Back到列表、S42向下，当前XML明确有**两张同标题Thai Peanut Noodle Salad卡片**。E125/Stap_on-43 却只给 `target=Thai Peanut Noodle Salad`，没有指定新建那张。所开详情是 **3-4servings、2hrs、optional ingredients**；E127/Sassert_with_ai-44因此失败，随后kill。

### 首次偏离、直接失败、机制

- 首次工具失配是S17同046的text/content-desc错误，但已恢复。**关键对象身份偏离【事实】**是S43在已有两张同名卡片的当前证据下，仍按非唯一标题选择，得到与刚保存详情不同的记录。
- **直接失败【事实】**：未执行两道余下recipe的新增，且最后核验选了有歧义的同名条目。官方addition-integrity validator报告expected Recipe not found，未给具体行。
- **保存损坏与误选必须分开**：S37/S38/S39表明保存后字段与源一致；S42显示两张同名。私有噪声恰有同标题 **3-4servings/2hrs/optional ingredients**，与S43完全吻合。故“重开选中旧噪声而不是新条目”是**强推断**；不能把末次断言失败写成“driver把as desired存成optional ingredients”或证明app丢数据。无recipeId或DB终态仍有身份不确定性。
- **根机制**：多对象复制无完成清单，历史转录重读替代推进；保存实体的身份没有与回执绑定。`_selector:356-369` 对文本目标仅建text selector，不保证唯一；主模型没有利用当前重复卡片证据消歧。主runner收尾声称“reopened saved entry”超出其身份依据，verifier正确保留歧义，没有把它判成功。

### 可定位改进

**ER-047，P0，owner：FSQ main prompt/Android定位工具契约**。在 `PromptModelBuilder.build_task_prompt:65-96` 保留“源记录→创建回执→保存后字段→重开候选身份”工作表；重开时若当前多个同标题候选，必须用本轮保存后确认过的servings/time等公开字段消歧，再核对完整recipe。`UiAutomator2AndroidDriver::tap_on:109-116` / `_selector:356-381` 对显式精确文本目标可返回歧义而不是默取第一个（若未来设计采用此保护，应保留唯一匹配现有路径，不作不可见自动猜测）。不能通过修改旧同名条目来让末次断言变绿。

与ER-046共用源字段摘要/剩余配方清单，收尾按全部源配方核验，而不是仅第一道最终assert。边界：既有同名不同配方应保持，不能title去重，不能把噪声字段泄漏成将来定位答案。未来验证：三道源、目标已有同名旧条目，验证新条目正确持久化、旧条目未改、最终重开的是新条目、其余两道都保存；无未经批准追加轮次/预算。当前未运行。

### 精确取证入口与待核问题

- 源像素：`R047/artifacts/screenshots/screenshot-agent-assert-with-ai-12-invoke-assert-with-ai-1-7ff0a93f6574.png`；源转录 `R047/artifacts/tools/000013-assert_with_ai.json`。
- 保存后：S37 finalize/S38 tool snapshot `artifacts/tools/000047-ui_snapshot.json`；S42 finalize显示两同名卡片；错误候选像素：`R047/artifacts/screenshots/screenshot-agent-assert-with-ai-44-invoke-assert-with-ai-1-42beed1acc31.png`。原执行S39 invocation记录完整directions条件。
- audit seq73/74 Save成功，seq83–88为向下、按标题打开，seq89/90 kill；seq93正常返回。主结果业务inconclusive而操作runner success，不是max_turns错误。
- 已核对：S38与S43字段及后者匹配初始化noise_row_objects[2]，双方认为支持误选既存同名条目，现有材料不支持“保存字段被篡改”。仍未决：新旧recipe持久ID和最终DB逐字段终态；若没有该证据，误选仍按强推断而不写成直接读到实体ID。

## 案例 050 — RecipeDeleteDuplicateRecipes

**交叉核对：已核对。** 完整双份比较14/19必要且已做；S20第10admitted用text More options错属性；恢复S22正确accessibility与kill23均在forward前预算拒绝，无删除。仅修定位不保证原10写够，不加预算凑成功。

### 目标与结果

公开目标：Broccoli所有完全相同配方只留一份，每种不同配方保留。officialReward **0.0**，FSQ verifier failed，主业务总结inconclusive。10/10 writes，末次正确定位菜单与kill被拒。

### 实际副本比较与未完成删除

1. S1/3两次launch仍launcher，S4 drawer、S6图标入Broccoli。首屏有两张 **Chicken Alfredo Pasta**。S8向下看到其余条目，再S10向上回首屏；不是从没发现重复候选。
2. E47/Stap_on-12 以同标题cards的XPath `[1]` 打开第一份。E51/Sassert_with_ai-14 实际读取完整可见字段：6servings、45mins、description `An ideal recipe for experimenting with different flavors and ingredients.`、ingredients `see directions`、完整fettuccine/Alfredo/chicken/Parmesan/spices指令，无photo。
3. S15 Back回两张卡片，E57/Stap_on-17以XPath `[2]`打开另一份。E63/Sassert_with_ai-19 与第一份完整字段比较通过，也报告无下方额外内容。已渲染两份详情相符。私有初始化两行也完全相同，但当时公开UI/AI比较已经提供直接证据，不应说“只是同名”。
4. E65/Stap_on-20 为打开菜单给 `target="More options"`，失败。当前XML实际是 `content-desc="More options"` 的ImageView，并非text。该失败是第10次admitted write。E69/Stap_on-22终于改 `accessibilityId="More options"`，却在转发前action_budget拒绝；E71/Skill_app-23也拒绝。没有出现Delete菜单选择或确认。

### 首次偏离、直接失败、机制

- **最关键首次业务执行偏离【事实】**：S20在已有明确accessibility属性的情况下用text target，导致进入删除流程的最后一个可用write浪费。启动冗余与列表上下返程是更早的预算压力，但不能把安全的双副本内容比较说成浪费。
- **直接失败【事实】**：确定候选两份都还在，没有任何删除调用或确认；只读assert通过并不减少副本。官方0分与保留两份一致。
- **根机制**：`_selector:366-368`的text-only target语义与模型把“可见可读描述”当text混淆；`android-harness.md:15`本已推荐accessibilityId。native `dispatch:85-118`按admitted计费，target_resolution失败不返额度，使纠正selector已来不及。不能说第二次accessibility locator也找不到：它根本未执行。
- verifier比主总结更明确判failed有证据依据；主总结称“未完成比较”与S19已通过的比较并不完全一致，需保留这处分歧而非采信更保守叙述覆盖事实。

### 可定位改进

**ER-050，P0，owner：FSQ Android Skill/tool schema + runtime预算交接**。在 `_selector:356-381` 对target=text与accessibilityId的契约和现有 `android-harness.md:14-18` 提示增加具体约束：snapshot若只有content-desc，直接生成对应accessibility locator，不能先尝试text；对破坏性流程在确证重复后预留菜单/删除/确认所需剩余write，并复用ER-015的公开剩余额度注入。不要添加静默fallback、免费动作、自动删除或提高10预算。

边界：只有完整配方相符才能删冗余，不能为了省预算跳过内容比较；即使预算已不足也只能如实失败，不将比较assert充当去重完成。未来验证：同10额度验证规范启动进入app、两个内容完全相同副本分别核对、准确accessibility菜单、只删一份、确认所有不同配方保留；另测同标题但成分不同不误删。当前未运行。

### 精确取证入口与待核问题

- `R050/artifacts/screenshots/screenshot-agent-assert-with-ai-14-invoke-assert-with-ai-1-eb216ff42074.png` 与 `screenshot-agent-assert-with-ai-19-invoke-assert-with-ai-1-13c24e28caa0.png` 是实际比较的两份；S20 prepare XML包含More options的content-desc，before/after详情保持不变。
- 初始首屏：S6 finalize；末屏：S22 prepare/finalize；原工具转录 `artifacts/tools/000017-assert_with_ai.json`、`000023-assert_with_ai.json`。
- audit seq39/40为错误text菜单动作的admission/outcome，seq43为正确accessibility调用被拒，seq44 kill拒绝，seq47返回。
- 待核：harness是否确认始终未产生delete菜单/持久化删除；无需重复执行来证明这个已录事实。

## 案例 052 — RecipeDeleteDuplicateRecipes3

**交叉核对：已核对。** Butternut已见但只解Avocado三不同，正确保留后未回候选簇，22/34零拒绝正常停、零删除，非强制超时。

### 目标与结果

公开目标：Broccoli全库exact duplicates只留一份，其他不同配方保留。officialReward **0.0**，FSQ inconclusive。22/34 writes，无拒绝、deadlineExceeded=false；正常runner约251秒，未见max_turns或API错误。

### 实际集合浏览与三条非重复比较

1. S1/3 launch后launcher，S4 drawer、S6 Broccoli。首屏有三条 **Avocado Toast with Egg**，description已不完全相同。S8、S10、S12连续滚动可见大量 **Butternut Squash Soup** 同名同description卡片；它们只是候选，尚不能按标题批删。
2. S14/16/18/20/22/24继续扫至尾部，S22与S24末屏相同。期间E69–74回读先前 `000008/000010/000013/000015/000017-ui_snapshot.json` 的title，未形成可见的逐记录完整字段比较。全任务共10次swipe（含drawer），19次snapshot。
3. E83/Stap_on-26 打开搜索，E87/Sinput_text-28输入 `Avocado`，S29 Back收键盘。E93/Stap_on-31打开第1条，S33 AI读到 **6servings、4hrs、various amounts**、quick/easy描述及完整directions。
4. S34 Back，E103/Stap_on-36开第3条，得到 **3-4servings、1hrs、n/a**。S38 Back，E113/Stap_on-40开第2条，得到 **6servings、2hrs、as needed**、ideal/experimenting描述。S42 deterministic assert只确认其2hrs字段；这些三条公开字段不同，**不删除这三条是正确安全决定**。
5. 随即S43 kill；没有回到Butternut候选组、没有一次Delete/确认，也没有完整库去重终态核验。主总结报告无confirmed exact group、所有记录保留；verifier不把同名卡片当完全相同，保持inconclusive。

### 首次偏离、直接失败、机制

- **首次可证的进展停滞**：S24在S22已到相同尾屏后继续同向滚动；这不是大失败本身。核心分岔是全库已见多个未解析候选组，却只解决Avocado这一组的“不相同”分支后即结束，没有继续待处理集合。
- **直接失败【事实】**：所有配方都未删除，完整内容比较只覆盖三条非重复Avocado。不能因三条不同就推出全库无exact duplicates。
- **事后原因【事实+强推断】**：私有初始化含30条噪声及两条完全相同Butternut（3-4servings、30mins、quantities to taste，directions同为fresh herbs结尾，其他字段相同）。它们解释正式0分；未来模型绝不能获得这组隐藏定位答案。因全程零删除，真正冗余副本仍留是强推断，而不是当前UI直接证实哪两张相同。
- **根机制**：候选工作队列/覆盖表缺失，主执行从全库候选集缩成一个容易按title搜的组；对其余组没有逐字段排除或确认。50字快照只给title/description前缀，无法替代详情比较；但主agent能用AI读取完整详情，工具并非完全不可用。剩12个writes、尚有约1878秒就正常结束，不能写成预算/截止强制中断。安全不误删与任务未完成同时成立。

### 可定位改进

**ER-052，P1，owner：FSQ pre-plan/main集合策略**。`_pre_plan.py::PRE_PLAN_AGENT_INSTRUCTIONS:37-46`、`build_pre_plan_input:60-85` 和 `_prompt.py::PromptModelBuilder.build_task_prompt:65-96` 把“浏览全库→候选组→逐字段比较→保留代表→删多余→全库复核”转成有界公开证据队列；同名组内找到差异只排除已比较的pair，不清空其他pending组。列表无变化则标记边界，不再盲swipe；组优先级可按公开可见重复数量/字段相似度，不以隐藏fixture真相指定Butternut。

理由：保留正确的exact-match安全标准，同时防止一次负例比较结束整个去重任务。边界：不把相同description提升为exact，不自动从全库扫标题后批删，不强迫在字段无法读取时冒险。未来验证：多组同名、其中一组三条全不同、另一组有完全相同副本且夹杂近似项，要求用公开详情对各pending组闭环、只删确证多余者；同34额度，不追加重试。当前未运行。

### 精确取证入口与待核问题

- `R052/execution-result.json` S8/10/12 finalize（Butternut候选）；S22/24 finalize（相同末屏）；S31/33、S36、S40/42为三份Avocado字段。对应events E35–81、83–120；audit seq47/48为无变化额外swipe，seq61–84为三份详情及assert。
- 已渲染S10候选屏、三份Avocado详情、初始launcher及末详情；AI实际图片 `R052/artifacts/screenshots/screenshot-agent-assert-with-ai-33-invoke-assert-with-ai-1-1d97f5d1846c.png`。最后S40 finalize的directions末句与第一份亦有差别，进一步否定“title相同可直接删”。
- 待核：真重复组的事后持久性与正式判定；FSQ主/verifier inconclusive不是“认为任务已完成”，也不推翻0分。没有证据证明模型API/设备环境错误阻止访问剩余候选。

## 本slice的可合并结论

1. **015是提交边界未跨越**，而不是字段未填；**016/017是费用去重候选/范围处理未进入详情与删除**，两例不能混成同一个“预算不足”：016有两次selector失败及datepicker探索，017则多次无变化filter开关、未覆盖到尾部。
2. **019漏掉早已可见的Pet Supplies**；纠正过的Restaurant Meal误开是独立近失事件，不是最终唯一原因。当前屏not_visible是真实通过但不是全库删除证明。
3. **046/047源文件读取成功，三道均可视读；业务只创建第一道**。两例原生writes并未耗尽。046方向换行造成两编号步骤，评分影响待核；047末次断言针对同名旧配方的强证据很强，不能说新保存的数据损坏。
4. **050已建立具体exact-match候选却卡在text/content-desc混淆和计费后纠正**；**052比较的三条Avocado确实不同且应保留，但未继续其它候选组**。不能把“安全不删错”视作完成，也不能通过title去重降低标准。
5. 责任应分层：producer计费/截止实施、FSQ输入预算可见性与历史输出处理、Skill定位契约、主模型对象清单/候选进展、只读verifier、官方完整性判定。当前证据不足以给八例统一贴“模型坏”“坐标坏”“max_turns”“设备坏”标签。
6. 八例均已收到harness owner逐例正式回执，分别记录理由与剩余未决；046/047原批B与正式回执主链一致。字节/ID/终DB未留存不冒充已测；所有核对均为离线解释，非重跑许可。
