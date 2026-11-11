# 20项failed独立交叉核验

Campaign：`amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`。复核截止：`2026-11-10T00:46:41.475038+00:00`。

**结论：主报告的主要行为链、三处任务契约风险和关键反证可接受；需要补源码身份、置信作用域及fix落点。没有独立证据证明AMKernel产品实现bug导致本轮20项失败。** 三处源码问题不等于三次已证误判；本review不改reward，不授权修复或重新测评。

仅写本目录`review.json`和`review.md`。未运行任务、初始化、评分、测试、Runtime或MCP；未操作设备/服务，未改源/配置/主报告/原始结果。标准库解析、散列、只读`git show`、文本公式关系与历史PNG解码均为本次独立执行；现有shared/integration收据未冒充本次执行。

## 本次独立证据

| 查询 | 实际输出 | 边界 |
|---|---|---|
| 正式summary失败集合对照 | 20/20，caseId集合精确一致 | 不混入校准/预演 |
| 原result ↔ 报告goal/params；raw SHA | 全20精确一致 | params不是最终DB或完整初始化状态 |
| 原raw执行响应计数 | 391：328 completed、63 failed；全alive | 含业务/cleanup；路由read不计执行；alive不保证语义正确 |
| 动作账本 | 352获准动作，1个gate预算拒绝；11 completed/9 step_budget | 获准请求即使上游失败也已计费；policy拒绝另列 |
| 首业务final/归档 | 20/20原文、JSON值、submission文件hash、截止内receipt一致 | 没有执行parse_submission；合法值不等于正确答案 |
| 时序 | 20/20 agent阶段结束先于evaluator；evaluator先于teardown | 状态任务quit后的持久输入仍缺 |
| 历史revision源码 | 31个被引AndroidWorld文件的Git blob均逐字节等于当前文件 | 记录revision内容已核；不等于历史import/安装目录字节已归档 |
| 正式wheel | SHA256与release pin一致 | 静态读`runner.py`/`protocol.py`，未运行Runtime |
| 完整嵌入code块 | 197块与原raw代码精确等同，无差异 | 其余timeline异构，不冒称全部代码块都已做字节等同 |
| 014原源文件解析 | 102行，仅Laundry/Car Insurance两条报销标记 | 不替代最终accounting.db字段 |
| 052原params全字段分组 | 32 occurrences/31 groups，仅一个二重组 | 去recipeId后分组；不推造历史DB IDs |
| 历史截图人工检查 | 003六click后仍原点、tap移动、末未到goal；004末10+Click Me | 只解码原PNG，不采新截图、不重评 |

复现代码、逐案输出、31条hash、原raw/result散列和截图摘要均在`review.json.independentOfflineQueries`及`originalEvidenceHashes`。一次只读查询因timeline异构报`AttributeError`，修正类型遍历后完成；无状态副作用。

## 优先级与整合意见

P1为高优先级归因/语义风险，不代表主报告写错；P2为需要整合补充的精度/映射/机制缺口。未发现P0，也未发现支持改判旧成绩的闭环证据。

| ID | severity | 性质 / caseId | 精确结论与交回动作 |
|---|---|---|---|
| R01 | P1 | confirmed_task_contract_risk_not_report_error / 001,014,076 | 三处任务源码契约问题成立；不得把它们整合成三个已证false-negative或三个Agent正确案例。 保留各自confirmed源码/probable episode/unknown自然语言正确性的分层；由oracle owner做未来语义决策，不改旧结果。 |
| R02 | P2 | provenance_update_with_residual_gap / 全部20案（相关重点见JSON） | README66与module-map24的“未逐文件从历史Git tree证明”已可补充：本review独立取31个引用文件对应revision blob，全部等于当前文件。 整合owner引用本review的31条hash与复现命令，收窄旧缺口为“历史运行import路径/包目录字节未归档”；保留此残余限制。 |
| R03 | P2 | fix_location_completeness / 全部20案（相关重点见JSON） | 44个fix都有字段不等于44个实现落点完整；例如014 fixes[1]只写evaluator evidence interface，052 fixes[2]仍写mechanism owner must identify exact symbol，若干Agent/Skill方案只有策略名。 逐fix显式标project/module/file/symbol或精确Skill section/raw cell；无产品bug证据的标behavioral policy或diagnostic proposal，不为了填target创造Runtime修复。 |
| R04 | P2 | confidence_field_granularity / 全部20案（相关重点见JSON） | rootCause/causal的顶层confirmed与内部probable/unknown并存，自动消费者容易把已证行为或源码问题读成已证历史失分分支。 保留060/098最终DB或整数unknown、106第三title/filter unknown、115获胜分项unknown；不得用reward反推完整末态。 |
| R05 | P2 | external_helper_revision_boundary / 085,098 | 当前Appium Settings/UiAutomator/helper源码或邻案097只能解释机制，不能替代085实际历史Node依赖字节或098实际source XML/slider值。 整合时保留同campaign邻案证据边界；若要产品/环境bug工单，先引用历史package lock/hash/对应源码和同时刻service证据，不操作现场补历史。 |
| R06 | P1 | counterevidence_guardrail_not_report_error / 全部20案（相关重点见JSON） | 必须保留Moria字符串关系可过、VLC部分分且未耗尽、391 alive、20业务final保留四项反证；它们排除特定解释，不证明任务成功或Runtime完全无bug。 整合owner不得用笼统MCP失效、缺final或VLC预算耗尽覆盖具体行为链，也不得从alive推出命令语义正确。 |
| R07 | P2 | module_alignment_unavailable / 全部20案（相关重点见JSON） | AMKernel owner预期module-analysis.json/.md在审查时均未出现，不能声称已对齐或虚构实际分歧。 补查tuple契约与仓库symbol、native click dispatch与proxy边界、Settings helper历史依赖、已加载Skill是否已有同指导；按原始历史响应>冻结发布源码>当前源码>proposal排序证据。 |

每项finding的报告指针、原始证据锚点和可改变结论的反证见`review.json.findings[]`。R01/R06是认可并要求保留的结论边界，不伪装成新发现的报告错误。

## 全20案coverage

下表预算以原result获准UI动作计，不以python_exec次数计。除115外其余reward均0；它们仍是原正式failed分类，未产生新成绩。

| caseId / task | severity | 原reward | 获准/上限 | termination / closure | 复核置信作用域 |
|---|---|---:|---:|---|---|
| [001 AudioRecorderRecordAudioWithFileName](#case-001) | P1 | 0 | 9/20 | completed / agent_finished | source_contract_confirmed; episode_cause_probable |
| [003 BrowserMaze](#case-003) | P2 | 0 | 20/20 | step_budget / step_budget | behavior_confirmed; native_dispatch_unknown |
| [004 BrowserMultiply](#case-004) | P2 | 0 | 15/22 | completed / agent_finished | noncompletion_confirmed; generation_mechanism_unknown |
| [014 ExpenseAddMultipleFromMarkor](#case-014) | P1 | 0 | 33/60 | completed / agent_finished | source_contract_confirmed; db_cause_probable |
| [023 MarkorAddNoteHeader](#case-023) | P2 | 0 | 12/12 | step_budget / step_budget | behavior_confirmed; persistent_branch_probable |
| [024 MarkorChangeNoteContent](#case-024) | P2 | 0 | 11/12 | completed / agent_finished | behavior_confirmed; disk_state_unknown |
| [030 MarkorDeleteNewestNote](#case-030) | P2 | 0 | 10/10 | step_budget / step_budget | acceptance_error_confirmed; filesystem_cause_unknown |
| [033 MarkorMergeNotes](#case-033) | P2 | 0 | 17/78 | completed / agent_finished | construction_mismatches_confirmed; oracle_branch_probable |
| [036 MarkorTranscribeVideo](#case-036) | P2 | 0 | 20/20 | step_budget / step_budget | output_scope_behavior_confirmed; persistence_cause_probable |
| [049 RecipeAddSingleRecipe](#case-049) | P2 | 0 | 24/24 | step_budget / step_budget | acceptance_behavior_confirmed; text_mutation_unknown; db_cause_probable |
| [052 RecipeDeleteDuplicateRecipes3](#case-052) | P2 | 0 | 34/34 | step_budget / step_budget | no_delete_confirmed; strategy_probable; feasibility_unknown |
| [058 RetroCreatePlaylist](#case-058) | P2 | 0 | 23/24 | completed / agent_finished | wrong_visible_membership_confirmed; locator_aliasing_probable |
| [060 RetroPlaylistDuration](#case-060) | P2 | 0 | 30/30 | step_budget / step_budget | aggregate_behavior_confirmed; persisted_failure_branch_unknown; init_risk_source_confirmed |
| [076 SimpleCalendarFirstEventAfterStartTime](#case-076) | P1 | 0 | 3/10 | completed / agent_finished | source_contract_confirmed; strict_after_answer_unknown |
| [085 SimpleSmsSendClipboardContent](#case-085) | P2 | 0 | 12/12 | step_budget / step_budget | behavior_confirmed; helper_readiness_error_confirmed; helper_root_unknown |
| [091 SportsTrackerTotalDistanceForCategoryOverInterval](#case-091) | P2 | 0 | 12/20 | completed / agent_finished | single_item_submission_confirmed; second_member_total_probable |
| [098 SystemBrightnessMaxVerify](#case-098) | P2 | 0 | 3/10 | completed / agent_finished | acceptance_gap_confirmed; parser_format_inferred; brightness_cause_probable |
| [106 TasksCompletedTasksForDate](#case-106) | P2 | 0 | 10/10 | step_budget / step_budget | cardinality_rejection_confirmed; UI_filter_probable; third_identity_unknown |
| [107 TasksDueNextWeek](#case-107) | P2 | 0 | 8/10 | completed / agent_finished | agent_predicate_confirmed; absolute_noise_dates_source_linked |
| [115 VlcCreateTwoPlaylists](#case-115) | P2 | 0.5 | 46/48 | completed / agent_finished | ordered_behavior_confirmed; passing_component_unknown |

所有20案都核对goal/原params、真实oracle谓词、原工具请求/响应、最早已证偏离、终止/动作账本、first-final与评分/teardown时序；没有仅抽样数案。每案完整原goal在JSON，不用当前源码生成的goal替换原prompt。

## 逐案裁定与能改变结论的反证

### case-001

**AudioRecorderRecordAudioWithFileName — supported_with_causal_limit**

- **观测 / claim**：输入stem presentation_fGwr；独立Records页可见6秒录音。
- **根因裁定**：完整名generator/goal与额外追加.m4a的oracle契约冲突成立；本次具体物理路径导致0仅probable。
- **第一次偏离**：契约在执行前已经分裂；cell9输入stem不能独立证明Agent违背goal。
- **真正oracle**：audio_recorder.py:90-123,154-159；exact full target presentation_fGwr.m4a.m4a是否存在，非标题/录音时长/内容比较。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/001-AudioRecorderRecordAudioWithFileName/attempt-1/raw-private/agent-events.jsonl`：cell9 L3074-3075；cell10 L3439-3440。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/001-AudioRecorderRecordAudioWithFileName/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3539，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/audio_recorder.py:85-159`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：若历史物理文件已经为双后缀，或实际加载源码不同，则此契约冲突不能解释该0；仍需历史find结果/安装源码留证。
- **fix审查**：统一未来任务file_name的完整名/stem语义；不得教Agent猜双后缀、兼容任意别名或改旧reward。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-003

**BrowserMaze — supported**

- **观测 / claim**：cell20连续6个方向element.click后X仍在(0,0)；cell21坐标tap到(0,1)；最后(3,1)，右移被gate拒绝。
- **根因裁定**：未先验证控制效果即批量执行、导航成本与20步封顶构成已见行为链；click无效的底层原因unknown。
- **第一次偏离**：cell20把未验证的原生方向点击批量化；并非已证迷宫路线错误。
- **真正oracle**：browser.py:98-109；前台Chrome且UI元素text恰为Success!；最终文字答案不参与。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/003-BrowserMaze/attempt-1/raw-private/agent-events.jsonl`：cell19 L3498-3499；cell20 L3699-3701；cell21 L3777-3779；cell22 L3961-3962；cell23 L4018-4020。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/003-BrowserMaze/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L4067，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/browser.py:98-109`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：延迟dispatch/快照迟到仍未排除，不能从HTTP200推onclick成功；截图可直接证实末态未到绿色格。
- **fix审查**：遵守已加载的单次探测/进展确认；保留native-only与20步，不无条件加fallback/retry。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-004

**BrowserMultiply — supported**

- **观测 / claim**：cell18读到[9,9,10,10,10]并算81000；后续树/截图仍为10和Click Me，未输入或Submit；15/22主动停。
- **根因裁定**：生成阶段/新鲜度未确认及未执行应用内验收成立；具体丢点击或stale机制unknown。
- **第一次偏离**：cell18清空numbers并把每次点击后的即时值当新的生成值；未保留初始9。
- **真正oracle**：同BrowserTask：Chrome AND Success!；不是数字答案直接比较。20250只能作记录seed/源码条件重建。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/004-BrowserMultiply/attempt-1/raw-private/agent-events.jsonl`：cell17 L4164-4165；cell18 L4538-4539；cell19 L4778-4779；cell21 L5186-5188。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/004-BrowserMultiply/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L5205，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/browser.py:98-109`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：81000乘法对已采样数组是正确的；不能将算术错误或7步不足作根因，也不能用条件JS结果当历史变量。
- **fix审查**：保留初值、可靠阶段ack、输入Submit并见Success!；相邻随机数可重复，不能用值必须变化作ack。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-014

**ExpenseAddMultipleFromMarkor — supported_with_causal_limit**

- **观测 / claim**：完整102行源含两条Reimbursable；保存后两详情备注仍带标记：Urgent. Reimbursable.与I may repeat this. Reimbursable.。
- **根因裁定**：initialize只修改展示用dataclass副本，不修改params.row_objects参考；note实际fuzzy关系均低于0.9。源码契约分裂confirmed，最终DB/类别/金额独立失分仍未排除。
- **第一次偏离**：initialize_task中的展示/参考分叉先于Agent；照抄显示备注本身不能当Agent代码bug。
- **真正oracle**：expense.validate_addition_integrity：name/note fuzzy>=0.9，amount/category精确；after=before+2且所有旧行完全保留；先missing reference再count/survivor。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/014-ExpenseAddMultipleFromMarkor/attempt-1/raw-private/agent-events.jsonl`：cell6 L1188-1189；cell13 L3091-3092；cell16 L3726-3727；cell20 L5239-5240；cell22 L5699-5700；cell23 L5970-5971。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/014-ExpenseAddMultipleFromMarkor/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L6014，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/expense.py:264-285,343-356`；`android_world/android_world/task_evals/common_validators/sqlite_validators.py:149-192,304-310`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：missing Laundry警告不定位字段；历史DB若缺行/错类别/错cents，修备注契约不保证这次通过。
- **fix审查**：未来任务明确报销标记是持久note还是筛选元数据，并同步goal/display/reference；不降fuzzy阈值。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-023

**MarkorAddNoteHeader — supported_with_persistence_limit**

- **观测 / claim**：已改header并Save；cell17列表仍有原名，cell18末步长按后才出现Rename；无rename输入/确认。
- **根因裁定**：错误标题/格式设置路线与宽泛EditText等待导致预算耗于探索；未执行rename行为confirmed，evaluator原路径存在仅probable。
- **第一次偏离**：编辑正文后转标题/设置而未走实际文件列表context Rename。
- **真正oracle**：原路径不存在AND新路径存在AND精确内容header+2LF+original+LF；check_file_content exact_match=True仅去CR，不strip。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/023-MarkorAddNoteHeader/attempt-1/raw-private/agent-events.jsonl`：cell10 L1886-1887；cell16 L3183-3184；cell17 L3310-3311；cell18 L3512-3515。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/023-MarkorAddNoteHeader/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3558，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/markor.py:784-805`；`android_world/android_world/utils/file_utils.py:577-584`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：UI原名不是post-quit文件清单；已验证header正确，不能把换行丢失作失分事实；未见rename dialog，不证明替代路线必在12步内。
- **fix审查**：先规划两个独立验收与commit路线；Rename入口已有原证据，dialog细节和12步可行性仍待另行授权验证。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-024

**MarkorChangeNoteContent — supported_with_persistence_limit**

- **观测 / claim**：替换内容精确读回；cell15标题clickable/longClickable均false，cell16仍点标题；未rename，11/12停。
- **根因裁定**：内容完成被误当接近全目标、rename路线未建立；不是gate耗尽。
- **第一次偏离**：post-save进入File settings/标题路线；不可把已有内容EditText视为rename框。
- **真正oracle**：原路径不存在AND精确新名存在AND新内容fuzzy>=0.9（cat去CR/strip）；全有或全无。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/024-MarkorChangeNoteContent/attempt-1/raw-private/agent-events.jsonl`：cell10 L2615-2616；cell11 L2873-2874；cell15 L3662-3663；cell16 L3893-3894。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/024-MarkorChangeNoteContent/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3927，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/markor.py:700-721`；`android_world/android_world/utils/file_utils.py:577-584`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：未见post-quit磁盘；final声称within budget不是gate证据；1步剩余也不证明足够完成rename。
- **fix审查**：使用实际文件行context路线，保留完整name/ext与内容独立验收；停止理由区分预计余步不足与实际closed gate。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-030

**MarkorDeleteNewestNote — supported_with_unknown_outcome_mechanism**

- **观测 / claim**：末次swipe返回admitted；随后deleted=true只由目标名不在source推得，同时survivor=false、visibleTexts=[]。
- **根因裁定**：空范围被当成功与无语义删除路线成立；是否真实删除、删除哪个文件和元数据失分分支unknown。
- **第一次偏离**：探索文档菜单未找到Delete后用最后一步猜swipe删除语义；再以目标absence单向验收。
- **真正oracle**：按helper change_time排序；所有survivor的name/time等于初始前缀且数量少1。-u与ctime文档不符是独立源码语义风险。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/030-MarkorDeleteNewestNote/attempt-1/raw-private/agent-events.jsonl`：cell13 L3023-3024；cell14 L3249-3250；cell15 L3418-3419；cell16 L3553-3554。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/030-MarkorDeleteNewestNote/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3678，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/markor.py:348-368`；`android_world/android_world/utils/file_utils.py:495-549`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：两个名字同时消失更支持范围/页面失去可见性，不证明删了两个或删错；无历史Toybox/mount/metadata，不证atime导致0。
- **fix审查**：观察到的语义Delete+survivor验收；时间字段语义必须由oracle owner另决策，不用宽松文件集合比对造成功。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-033

**MarkorMergeNotes — supported_with_persistence_limit**

- **观测 / claim**：源各带终止LF；cell8直接join为3行；cell10重新打开mIObBbo4.md，读回相同3行。
- **根因裁定**：默认.md而非extensionless完整名与少额外空白分隔行均有直接UI/code证据；落盘精确分支probable。
- **第一次偏离**：cell8保留默认ext，expected由同一错误构造自行生成并自比，不是独立goal验收。
- **真正oracle**：先CreateFile精确路径，再去CR/strip fuzzy>=0.9；通过后再cat/strip/split LF要求5行且1/3为空。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/033-MarkorMergeNotes/attempt-1/raw-private/agent-events.jsonl`：cell6 L1232-1233；cell7 L1468-1469；cell8 L1776-1777；cell10 L2501-2502。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/033-MarkorMergeNotes/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L2543，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/markor.py:535-560,603-638`；`android_world/android_world/task_evals/common_validators/file_validators.py:199-226`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：普通fuzzy关系0.97637795可接受捕获字符串，不等于task通过；五行guard仍独立拒绝。prompt有换行解释空间，不升级为已证坏oracle。
- **fix审查**：精确完整名/独立ext及附加LF，独立于自产expected验收；未来prompt澄清不追改旧reward。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-036

**MarkorTranscribeVideo — supported_with_causal_limit**

- **观测 / claim**：cell23创建txt；cell24内容Moria, Charlotte, Emilia且Save禁用；final明确Download输出。
- **根因裁定**：源媒体目录与输出notebook目录混淆是probable主因；没有历史最终find/cat不能锁定existence分支。转录首字拼写不是独立失分因果。
- **第一次偏离**：将位于Download的视频限定词带入新建输出目录；早期tips遮挡和非seek采样是贡献风险但不能由此推出本次转录谓词拒绝。
- **真正oracle**：精确Documents/Markor/ZwUN_moment_70__transcription.txt存在后，cat去CR/strip，对Maria,Charlotte,Emilia做case-insensitive SequenceMatcher>=0.9。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/036-MarkorTranscribeVideo/attempt-1/raw-private/agent-events.jsonl`：cell19 L5633-5634；cell20 L5906-5907；cell23 L6873-6874；cell24 L7301-7304。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/036-MarkorTranscribeVideo/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L7345，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/markor.py:877-941`；`android_world/android_world/task_evals/common_validators/file_validators.py:199-226`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：真实字符串关系0.91304348>=0.9；Moria与空格不够解释0。若app自动路由至Markor则路径假设被推翻；早期图像RPC省略不能补造首词。
- **fix审查**：分开source/output作用域并暴露future benchmark输出目录；视觉采样改善是策略，不得宣称修Moria即可过。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-049

**RecipeAddSingleRecipe — supported_with_causal_limit**

- **观测 / claim**：给定3-4 servings，先读回3-4 serving size，最后详情为3-4 serving size of y；最后save前未读回修复字段。
- **根因裁定**：最终修复未验收、预算未留纠正路径confirmed；输入变形源IME/UiAutomator/app unknown，UI到DB失分因果probable。
- **第一次偏离**：cell6已执行title/description前缀后失败；cell10最早证实servings值错误；失败cell不是事务回滚。
- **真正oracle**：8字段：title/description/servings/preparationTime/source/ingredients/directions fuzzy>=0.9，favorite精确；+1行且旧行完全保留。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/049-RecipeAddSingleRecipe/attempt-1/raw-private/agent-events.jsonl`：cell6 L1683-1684；cell10 L2563-2564；cell11 L2918-2919；cell12 L3201-3202；cell13 L3415-3416；cell14 L3653-3654。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/049-RecipeAddSingleRecipe/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3700，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/recipe.py:354-384`；`android_world/android_world/task_evals/common_validators/sqlite_validators.py:149-192`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：WebElement.set_value不存在不是Runtime功能bug；没有IME trace或DB不能认定自动纠错/持久化哪层改串。
- **fix审查**：使用已支持API、保留失败前缀、最终字段readback后再Save；不凭变形文本禁IME，也不重复不可逆Save。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-052

**RecipeDeleteDuplicateRecipes3 — supported_with_strategy_limit**

- **观测 / claim**：32输入occurrences仅一真正重复对；cell13/14两个Butternut细节明确不等；34步未发出Delete。
- **根因裁定**：完整occurrence覆盖与预算分配不足为probable策略解释；未删除和耗尽confirmed；34操作内合法完全验证路线是否存在unknown。
- **第一次偏离**：匹配过一个目标内容后未完成该组其他distinct occurrence，转其他候选/搜索恢复；不是已见误删。
- **真正oracle**：只允许删除两个指定target recipeId任一，所有其他before行精确保留；并非按title分组删除；结果32->31。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/raw-private/agent-events.jsonl`：cell8 L2577-2578；cell11 L3351-3352；cell12 L3744-3745；cell13 L3823-3824；cell14 L3908-3909；cell16 L5062-5063；cell24 L7316-7319。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L7353，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/recipe.py:200-225`；`android_world/android_world/task_evals/common_validators/sqlite_validators.py:73-115,380-415`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：同名10份不是10重复；bounded repr是真的观测降级，但后续JSON-native恢复不等细节且未见错误删除，不能认定serializer是唯一根因。
- **fix审查**：完整相关signature+distinct occurrence、保留commit路径；serializer产品变更需明确契约，预算研究仅独立可比性决策而非扩预算修分。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-058

**RetroCreatePlaylist — supported_with_causal_limit**

- **观测 / claim**：三次add flow后重开仅1 Song/Dreamer's Awake；cell19/20使用宽祖先XPath，23/24步停。
- **根因裁定**：宽祖先可绑定首个菜单的解释probable；没有每次实际menu element ID，不能排除app dedup/插入层。
- **第一次偏离**：cell16开始的跨任意祖先ViewGroup菜单定位缺最近行唯一绑定；不是已记录三次同element ID。
- **真正oracle**：名称fuzzy>=0.9筛选后行数恰3；标题及query生成的0-based顺序精确匹配；非IR答案。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/raw-private/agent-events.jsonl`：cell16 L4284-4285；cell18 L4734-4735；cell19 L5021-5022；cell20 L5299-5300；cell23 L6249-6250。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L6630，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/retro_music.py:41-76,162-170`；`android_world/android_world/task_evals/common_validators/sqlite_validators.py:19-70`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：三次若实际不同正确菜单仍只1首，需转查app/DB；一个余步不证明能补全，当前不是耗尽。
- **fix审查**：目标title最近实际行内唯一菜单并核对geometry，完整顺序读回；不全局first菜单、不盲重加。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-060

**RetroPlaylistDuration — supported_with_missing_final_state**

- **观测 / claim**：Select all为14 selected；列表/详情均14 Songs 01:08:25；最后4 selected只打开Remove菜单无commit，30步封顶。
- **根因裁定**：未测贡献先全选、未完成数值纠正是已见行为错误；正式最终DB及初始化实际时长缺失，不能确认唯一失分分支或缺哪首。
- **第一次偏离**：以全选数量代替45-50分钟贡献约束；首次有效总时长在追加后才读到。
- **真正oracle**：所有INNER JOIN歌曲行playlist_name必须精确等于目标，sum(duration_ms)在[2700000,3000000]闭区间；空其他playlist不可见；不要求params成员/顺序。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/060-RetroPlaylistDuration/attempt-1/raw-private/agent-events.jsonl`：cell22 L6659-6660；cell25 L7669-7670；cell26 L8559-8560；cell29 L9578-9579；cell30 L9791-9794。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/060-RetroPlaylistDuration/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L9855，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/retro_music.py:260-293`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：15个params名字不等于实际14首，无各首时长不能重造初始化或推荐确定删除子集；漏super是可比性风险，不证本次0由之造成。
- **fix审查**：只用UI数值建立聚合计划、保存可逆纠正路径；初始化owner另查基类/存储隔离，不得泄漏hidden subset或加预算。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-076

**SimpleCalendarFirstEventAfterStartTime — supported_contract_defect_not_agent_success**

- **观测 / claim**：10月29日Grocery Shopping恰17:20-18:20；Agent向后看到10月30日08:35 Appointment for Budget Planning并提交。
- **根因裁定**：after措辞、同参数阈值事件、IDENTITY(title)参考三者分裂confirmed；次日答案是否全局最早或题目日期范围正确unknown。
- **第一次偏离**：任务生成/期待在Agent前即不一致；Agent排除等于阈值不能证明其候选完整。
- **真正oracle**：相关proto事件start_date/date与start_time/time恰同阈值；oracle只抽title，STRING_MATCH fuzzy>=0.9且基数相等，不进行strict-after/min查询。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/076-SimpleCalendarFirstEventAfterStartTime/attempt-1/raw-private/agent-events.jsonl`：cell5 L1351-1353；cell6 L1677-1678。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/076-SimpleCalendarFirstEventAfterStartTime/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L1782，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto:858-893`；`android_world/android_world/task_evals/information_retrieval/proto_utils.py:147-210`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：没有完整76事件/绝对时间清单，不能把reward0认作已证误判Agent正确答案；at-or-after或strict-after是future语义决策。
- **fix审查**：明确inclusive或拆分query threshold与严格更晚相关事件，定义跨日/并列first；不把源title喂给Agent或重算旧分。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-085

**SimpleSmsSendClipboardContent — supported_with_helper_provenance_limit**

- **观测 / claim**：最先打开Google Messages，前6步未推进目标app；clipboard getter报Settings app not running after5000ms；未确认recipient，无正文/Send。
- **根因裁定**：目标身份/页面stage策略失败confirmed；Settings helper准备失败是独立分支，为什么失败unknown。
- **第一次偏离**：cell3把Messages当Simple SMS；后续精确文本search echo误命中不是已证明app启动。
- **真正oracle**：sent provider row的规范化address精确、body fuzzy>=0.9、time delta<=5min，加前台package=com.simplemobiletools.smsmessenger；非仅final宣告。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1/raw-private/agent-events.jsonl`：cell3 L731-732；cell8 L1786-1787；cell12 L2662-2663；cell14 L3226-3227；cell15 L3428-3429；cell17 L3800-3801；cell18 L3899-3900。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/085-SimpleSmsSendClipboardContent/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3936，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/common_validators/sms_validators.py:93-152,176-180,211-276`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：raw错误不证明clipboard为空或AMKernel故障；当前helper requireRunning源码仅解释性投影，未钉历史Node包源码/服务log；动作12仍转发上游500，不是budget拒绝。
- **fix审查**：实际app/recipient/composer判据与受限commit规划；helper需历史证据再选环境修复，不擅自启动服务/新session。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-091

**SportsTrackerTotalDistanceForCategoryOverInterval — supported_with_numeric_limit**

- **观测 / claim**：已见10月9日08:00单条1.24mi，提交1996；12/20主动停，没有完整category/date集合验收。
- **根因裁定**：把单项当总计confirmed行为；第二2.80mi候选遗漏与6502m精确期望仍probable。
- **第一次偏离**：日期筛选未应用/验证后，取首个详情即reduce成total，未重新建立目标population。
- **真正oracle**：相关proto两sports_activities total_distance SUM；类别/日期用于初始化排噪；NUMBER_MATCH float且abs差严格<10，不是<=10。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/attempt-1/raw-private/agent-events.jsonl`：cell18 L2929-2930；cell19 L3197-3198；cell20 L3300-3301；cell21 L3431-3432；cell22 L3545-3546。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/091-SportsTrackerTotalDistanceForCategoryOverInterval/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L3792，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto:2932-2989`；`android_world/android_world/task_evals/information_retrieval/proto_utils.py:164-208`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：1996是1.24mi合理换算；params.distance=4000不是初始化全部答案；未捕获第二项完整类别/日期/原始米值，不能将6502标confirmed。
- **fix审查**：验证成员/日期/单位绑定后SUM；保留8步做候选核对，非增加预算或接受近似总数。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-098

**SystemBrightnessMaxVerify — supported_with_missing_final_state**

- **观测 / claim**：cell3/6 root.iter(node)返回0；截图路径仍有UI；cell7 swipe至x976；未读回semantic endpoint，3/10停。
- **根因裁定**：观察/验收缺口confirmed；drag破坏初始化255只是probable，真正evaluator整数和该次XML均未留证。
- **第一次偏离**：把shade打开要求package改变；随后将匹配0个node等同无控件，再凭sun/thumb中心认定max。
- **真正oracle**：settings get system screen_brightness解析int必须==255；不是视觉百分比、SeekBar gamma数、答语或模式布尔。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1/raw-private/agent-events.jsonl`：cell2 L658-659；cell3 L940-941；cell4 L1088-1090；cell6 L1644-1645；cell7 L2138-2140。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/098-SystemBrightnessMaxVerify/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L2238，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/system.py:41-52,74-86`；`android_world/android_world/env/adb_utils.py:971-1001`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：x976位于track内侧不证明触控有效max端点也是x1038；097的class-tag/range只能邻案解释，不能补出098源码/值。可能初始非255/异步变化/quit后变化，不能锁定drag唯一原因。
- **fix审查**：区分parse-empty/source-empty；若可见semantic已经max则不变更，否则有界endpoint动作后读semantic值；不能加自动fallback、宽松near-max oracle。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-106

**TasksCompletedTasksForDate — supported_with_unknown_membership**

- **观测 / claim**：最终合法string只有两个标题；模板固定三项相关任务；10步封顶，后续只见其他unchecked行，第三title未留证。
- **根因裁定**：长度guard可确定拒绝2对3；具体filter/scroll状态及完整缺失成员原因unknown/probable，不得强行补第三title。
- **第一次偏离**：wrong-surface/right swipe前缀与未证明completed scope，后续无效scroll/compound denial；不能由menu wording证明过滤状态。
- **真正oracle**：逗号split/strip，STRING fuzzy>=0.9；先len(answer)==len(expected)=3，再每项any匹配。due Oct16而completed Oct10，非按完成发生Oct16过滤。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/106-TasksCompletedTasksForDate/attempt-1/raw-private/agent-events.jsonl`：cell5 L1416-1417；cell6 L1744-1745；cell9 L2686-2687；cell10 L2796-2797；cell11 L3129-3130；cell17 L4781-4782；cell18 L5112-5115。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/106-TasksCompletedTasksForDate/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L5539，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto:1527-1576`；`android_world/android_world/task_evals/information_retrieval/proto_utils.py:147-180`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：latent any非一一匹配是false-positive缺陷，不是本次长度拒绝原因；params.title被without-replacement排除，不能补作第三项；DB缺失不影响内存proto长度逻辑。
- **fix审查**：原surface/filter确认与distinct occurrence覆盖，JSON-native返回；不从hidden count/title修Agent，也不放宽集合比较。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-107

**TasksDueNextWeek — supported_with_absolute_date_limit**

- **观测 / claim**：4重叠窗口合26行，cell14把Tmrw/Mon..Sat/Oct22统归next week，返回20。
- **根因裁定**：weekday未经绝对日期消歧即计入下周的Agent predicate错误confirmed；14个noise逐条绝对日期是源码/捕获事实推断而非DB直接读。
- **第一次偏离**：cell14 label集合判据，不是少翻一页或title去重导致20。
- **真正oracle**：COUNT六相关tasks_app_tasks，NUMBER float精确6、无tolerance；Monday Oct16至Sun Oct22闭区间是初始化相关日期范围。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/107-TasksDueNextWeek/attempt-1/raw-private/agent-events.jsonl`：cell7 L2436-2437；cell10 L3054-3055；cell11 L3319-3320；cell12 L3580-3581；cell13 L3838-3839；cell14 L4251-4252。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/107-TasksDueNextWeek/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L4268，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto:1398-1467`；`android_world/android_world/task_evals/information_retrieval/proto_utils.py:164-208`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：完整窗口不等于日期成员正确；若历史绝对日期把14项放在目标周，需反查初始化，而非固守源重建；无DB不冒充14条绝对日期观测。
- **fix审查**：绝对日期或经验证date filter后count；保留重复occurrence，不以title dedup修错数。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

### case-115

**VlcCreateTwoPlaylists — supported**

- **观测 / claim**：D7B0第三、footage_46第四；cell27/32同序读回。46/48，exhausted=false，agent_finished；原reward0.5。
- **根因裁定**：故意先追加易见的后位项再欠重排债confirmed；两次proxy前置拒绝与一次支持swipe无进展分开；哪份DB分项通过unknown。
- **第一次偏离**：cell14向Adventure追加D7B0第三（cell13已准备）；不是已证save丢失或budget关闭。
- **真正oracle**：两个Boolean verify_playlist平均；名称fuzzy筛选后各恰4行、filename/0-based position精确。0.5只能推出一个分项通过，不定位哪个。

- **原证据锚点**：`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/115-VlcCreateTwoPlaylists/attempt-1/raw-private/agent-events.jsonl`：cell13 L3262-3263；cell14 L3543-3544；cell15 L3842-3843；cell27 L7007-7008；cell29 L7442-7443；cell30 L7651-7652；cell32 L8367-8368。`campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/115-VlcCreateTwoPlaylists/attempt-1/result.json`的`task`、`stepBudget`、`officialReward`、`agent.termination`、`stages`；first final为原raw L8499，与`raw-private/business-submission.json`一致。

- **源码锚点**：`android_world/android_world/task_evals/single/vlc.py:33-71,144-150,224-226`；`android_world/android_world/task_evals/common_validators/sqlite_validators.py:19-70`。均纳入历史blob核查；历史installed-byte限制仍在。

- **反证 / 边界**：final自称budget closed被result反证；图示title stem不证DB全filename/position；两拒绝不消耗UI step，也不证明kernel/传输故障。
- **fix审查**：按独立goal顺序追加并做完整readback；明确单touch协议且不换策略预算；未来分项收据是诊断，不是本次修分。 全部方案保留原协议/动作和时间预算；只读复核没有执行或证明该方案可成功。该案逐fix的target完整性、风险/备选/证伪条款见JSON。

## 四项关键反证：独立核查与边界

1. **036 Moria**：原cell24的`Moria, Charlotte, Emilia`对原params的`Maria,Charlotte,Emilia`，按源码的lowercase SequenceMatcher公式为`0.9130434782608695`，阈值`>=0.9`。只证明该字符串关系不足以解释拒绝；没有运行CreateFile或检查文件存在。输出目录仍是probable原因。

2. **033 内容**：相同公式关系为`0.9763779527559056`，但原读回strip后只有3行；真正task还要求5行且中间两空行，且先验精确extensionless路径。普通fuzzy通过不能覆盖guard。

3. **115**：原result和账本反证“预算耗尽”；原两次pointer policy拒绝发生admission前，一次支持swipe后读回仍反序。两个Boolean分项平均为0.5只说明恰一个通过，不说明哪份持久playlist通过。不得改写成0或全成功。

4. **执行/提交可靠性**：alive只排除观测到的kernel死亡，不排除serializer结构降级、上游500、错误API、语义无进展；首业务final保留只排除缺final/cleanup替换这条解释，不保证业务值。状态任务无post-quit/pre-evaluator持久快照，IR则用内存proto与合法answer，二者不可混判。

额外公式事实：014两个显示note对原reference的关系分别`0.4444444444444444`、`0.6938775510204082`，低于阈值；这是条件字符串比较，不是重评分。106先基数guard再any-fuzzy，2对3必拒；非一一匹配latent false-positive缺陷并不解释这次拒绝。091容差严格`abs(diff)<10`，107无容差，060毫秒总时长边界闭区间，098必须整数255。

## 44个fix逐条审查

全部44项已有风险、备选/取舍和falsification字段；它们仍是proposal，不是“有字段即实施就绪”。26项需要更精确的位置或行为/产品/诊断边界注记，逐条如下。其余18项未发现同类定位阻塞，但仍无实施/运行验收授权。JSON为44项完整审查，保留原target、原证伪条款与review意见。

| caseId.fixIndex（0起） | 定位 / 类型补充 |
|---|---|
| 001.1 | 已指Skill文件/行，但project/section名不独立；仅adherence，不是产品缺陷。 |
| 014.1 | 缺确切file/symbol；可在测评runner.py:run_episode evaluator边界790-796落diagnostic proposal，官方validator另标。 |
| 023.0 | Skill file/notes guidance不是精确section；绑定raw cells13-18与实际files/notes acceptance段，路线dialog可行性未知。 |
| 023.1 | 仅API/wait策略名，须绑定raw cell与Skill section；不是待修改的Appium实现。 |
| 024.0 | Skill file/notes section和Agent planning未给确切section/cell；应绑定raw cells12-16，标行为policy。 |
| 024.1 | 业务final决策策略，缺project/file/section；须明确仅Agent执行policy。 |
| 030.0 | 已指loaded Skill但无精确section/行或Agent cell；不得开成产品自动删除fix。 |
| 030.1 | 只有Selenium gesture策略；须绑定raw cell14/15，不修改第三方接口。 |
| 030.2 | 短路径须规范为FSQ_AndroidWorld_eval/android_world/android_world/utils/file_utils.py；需oracle时间语义决策。 |
| 033.0 | Agent构造/验收策略须绑定raw cell8/10；Skill变更需确切section，不能写成历史task专用硬编码。 |
| 033.1 | 短路径须规范并区分模板措辞与filename generation契约。 |
| 036.0 | files-and-notes acceptance为概括指引；给出已加载原Skill行/确切heading，并区分Agent目录选择与Skill产品改动。 |
| 036.2 | 仅visual fallback策略；须标精确Skill section与raw cells8-12、21-24；非Moria根因fix。 |
| 049.2 | 是机制调查条件，不是实施fix；缺历史Appium/IME包身份与file/symbol，不应补猜。 |
| 052.1 | 已定位raw line3744，但payload规范策略不等于Runtime实现变更。 |
| 052.2 | target仍待owner identify symbol；正式wheel已有runner.py:_normalize_result/_bounded_repr及protocol.py:json_size/_json_encoded_size；仓库映射待模块owner。 |
| 058.0 | nearest-row策略明确，须补已加载Skill精确section/raw cells16-20，不声称实际element ID已证。 |
| 058.1 | Agent acceptance策略，无产品file/symbol；绑定raw cells16-24与ordered acceptance section。 |
| 060.0 | 只有aggregate example/Agent plan，缺确切Skill section/raw cell；可行性未证明。 |
| 060.1 | action ledger策略，绑定raw cells25-30，不开成预算放宽实现项。 |
| 085.0 | installed-app selection / observed-stage predicates为策略概括；补已加载原Skill具体section及raw cells3-18，不宣称缺一条Skill。 |
| 085.1 | 给出lib/client.ts:requireRunning但project/npm包版本、历史代码路径尚未钉住；环境诊断非已证产品fix。 |
| 098.1 | control/stop-if-satisfied建议缺精确section；绑定raw cell7并保留semantic max映射未知。 |
| 098.2 | runner.py evaluation boundary缺symbol；应标run_episode:790-796，且仅future diagnostic。 |
| 107.0 | cell14精确但Skill只有existing contract；若开Skill修改需具体section和仓库file。 |
| 115.0 | 仅task planning/Skill ordered-content概念；绑定raw cells13-15,27与具体section，不虚构已证Skill缺漏。 |

验收不能只看reward上升：要证实针对已证原因、保持goal/oracle/预算/原生协议/单session、失败前缀不被重放、保存/删除不重复，且能被各案counterevidence推翻。特别是052的34操作可行性、023/024的rename dialog、060可见数值获取成本均未被本次复核证明；不得用加步骤、加重试或放宽oracle代替方案。

## 与AMKernel owner的对齐

截至`2026-11-10T00:45:52.960064+00:00`，预期`../amkernel/evidence/android-eval-0.1.4-failure-analysis-20261110/module-analysis.json`和`.md`均不存在；也只读查看了兄弟项目evidence目录。**未空等，未声称已合并模块报告，尚无可列的实际意见分歧。** unavailable不是disagree。

| 待对齐主题 | 本review证据更强之处 | 还需模块owner提供 |
|---|---|---|
| tuple/结构返回 | 发布wheel SHA固定；`_normalize_result`/`_bounded_repr`明确按strict JSON走摘要，原052/106等响应确有repr；JSON-native后续能恢复部分事实 | 对应仓库file/symbol、已承诺契约、原artifact是否保留完整值；不能只以repr判实现bug |
| 原生click / pointer | 003历史截图直接证明无进展；原始响应与Harness明确policy拒绝可区分 | 有则提供历史dispatch trace、实际拒绝payload；不从HTTP200或当前源码推历史onclick |
| Skill | 历史加载内容比当前工作树/建议更能证明Agent当时已获指导 | 逐section既有不变量与proposal差异；无遵循不等于缺规则 |
| helper / brightness | 原085错误、098无numeric readback直接支持unknown边界 | 历史Node依赖hash、服务trace、实际XML/settings留证；邻097或当前dirty helper不够 |

证据优先级：历史原请求/响应/状态 > 冻结发布包及历史installed字节 > 记录revision blob > 当前未钉源码 > proposal。若模块报告后来出现，整合owner应逐claim列agree/disagree、原锚点、哪边证据更强及需补查内容；不得事后把未读模块报告写成本review执行过。

## 交回整合owner

保留主报告已正确的probable/unknown、Moria/VLC/执行/提交反证；引用本review补31-file身份；细化结构化置信；把每fix精确落到project/module/file/symbol/Skill section或原Agent cell。模块报告落盘后补实际分歧。历史状态缺口无法从现在设备补成过去事实，不要求现场补跑。

三处任务源码契约问题可立future-version语义决策；没有证据支持的AMKernel代码bug明确不立案，不为了给fix制造rootcause。


## R07 moduleAlignment 追加：正式模块报告实际对齐

追加读取快照：`2026-11-10T00:57:02.120954+00:00`。本节优先于前文“模块报告尚未出现”的历史状态；前轮20案审查与原R07记录保留，不改写为当时已读。本轮只对齐下列claims和相关fix，不重做20案全量核查、不重审主owner在途26项落点修订，也不覆盖未来版本。

### 实际读取版本

| 文件（路径相对项目根） | SHA256 |
|---|---|
| `../amkernel/evidence/android-eval-0.1.4-failure-analysis-20261110/module-analysis.json` | `052dc6d7c79d34f18d3ea3772a5907f67218345312d674343b6b57a1fa2c97d5` |
| `../amkernel/evidence/android-eval-0.1.4-failure-analysis-20261110/module-analysis.md` | `c6ff2100db3fdd54ffa72eb5b5a8f12b50be08da2400fd853b258c4f3657d20f` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/README.md` | `2a8361cf272d82ceb4d3eaacb0935d9ea37b9bfc44277221888a6095ac5d69be` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/cases.json` | `3473e67767eaa7e3dd64c1291b2ab905e364a4feb00791b8554d6f0ab9abeaa5` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/cases.md` | `c49cea3981b3fee7172f66e272c57856ca34de5915215617ed46e81c5dbfcc38` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/module-map.md` | `65721a76ac427f0ca04d6a4d67248e8c8cc76704d3e143957a5ac2ceaccd891b` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/review.json` | `dd61ed4b25bd50169c6b36d91470a048bac43c03742f5f830ce416127bb2b4ef` |
| `evidence/amkernel-0.1.4-r15-current-stack-20261109T154403Z/failure-analysis/review.md` | `7da8b2d8ecd43ff09bd8103bccaa7312fb6a54a22435287cf27b05eaa54107a8` |

模块报告锁定版为20案、37fix、7common组；内部review13项修订后accepted是其报告的收据，不是本review执行。其17个AndroidWorld installed/source digest与本review旧Git blob digest全部一致；本次没有重跑installed hash、Runner或SDK隔离探针。当前主报告已可见confidenceAssessment拆分字段与部分身份/落点修订，本节仅审核实际引用的锁定片段，不声称已审核未来修订。

### 逐claim resolution（可直接交主owner落实）

`agree`表示同一claim一致；`compatible-but-different-scope`表示可合并但对象不同；`disagree`表示原证据不能支持至少一边的具体断言。主题可含不同subclaim，完整逐项关系见JSON，不能只看主题标签。所有原始行号都指原`agent-events.jsonl`，不是临时`trace.json`序号。

#### MA01 — P2 / 跨案provenance / compatible-but-different-scope

**待裁claim**：发布/installed provenance比旧review的31-file Git blob核查多了什么。

**双方锚点**：模块`module-analysis.json#/provenance/androidWorld`、`module-analysis.json#/provenance/topLevelPythonModulesByteMatchedToCommit`、`module-analysis.json#/provenance/sdkEnvironmentDistinction`、`module-analysis.md:9-15`；主报告/旧review`review.json#/independentOfflineQueries/sourceIdentity`、`cases.json#/cases/*/sourceIdentity`。

**哪边更强**：模块报告在17文件的current retained installed比对更完整；旧review在31文件Git blob范围更广。两者互补。对方执行的hash/probe不算本次执行，当前留存installed也不自动变成正式时刻installed-byte快照。

**最终采用**：记录revision及发布wheel已钉；17文件另有模块owner留存installed-byte一致收据，且与本review旧Git blob digest相符；未覆盖的历史import/安装内容和DB状态仍不补造。Harness客户端5.3.1与Agent5.2.5属不同解释器，无版本矛盾。

**落实条目**：
- w4:p1引用17条installed收据并标执行者；保留31-file Git blob与17-file installed范围差异，不再笼统说完全未作installed对照。
- 不得将本次读取报告/比较digest写成重新执行模块owner的隔离Runner/SDK探针。

**责任**：amkernel owner：发布包/installed来源收据与仓库symbol映射；FSQ evaluation owner：历史dependency/import身份汇总。

**能改变结论的证据**：若有正式时刻完整安装字节/路径签名，可进一步关闭残余历史身份缺口；相反的历史dirty字节会限制对应源码应用。

#### MA02 — P2 / 003,014,024,052,058,085,091,098,106,115 / agree

**待裁claim**：tuple/非JSON容器实际17次有界repr涉及10案；output与result两种truncated不能混为一谈。

**双方锚点**：模块`module-analysis.json#/runtimeCrossCutting/1`、`module-analysis.json#/runtimePerCase`、`module-analysis.json#/offlineProbes/0/result/normalization`、`module-analysis.md:27-32`；主报告/旧review`module-map.md:77-83`、`review.json#/independentOfflineQueries/releasedWheel`。

**原始锚点**：003 cell4 L1028-1029；014 cell2 L438-439；014 cell7 L1392-1393；024 cell5 L1228-1229；024 cell12 L3024-3025；052 cell8 L2577-2578；052 cell12 L3744-3745；052 cell15 L4878-4879；058 cell3 L910-911；085 cell7 L1687-1688；091 cell2 L481-482；098 cell4 L1088-1090；098 cell5 L1343-1345；098 cell7 L2138-2140；106 cell9 L2686-2687；106 cell14 L3721-3722；115 cell8 L1956-1957。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：17条原response及发布runner/protocol比任何“output未截断所以没信息丢失”的概述更强。本次只对前轮已解析原响应做repr定向投影，未重审20案或运行probe。

**最终采用**：17个原response同时output.truncated=false与result.kind=repr/result.truncated=true；是整个非JSON结果被有界summary替换，不是stdout/stderr或传输流截断。结构信息损失confirmed，是否影响各次决策/失分依赖后续JSON-native恢复；不是17次Runtime crash或10案根因confirmed。

**落实条目**：
- 主报告R1补17/10及完整case/cell锚点，保留052/106为例而非宣称只有两案。
- 采用src/amkernel/runner.py:_normalize_result/_bounded_repr及protocol.py:_json_encoded_size精确位置；Skill给JSON-native投影指导，产品是否扩tuple支持另作契约/安全决策。

**责任**：amkernel Runtime owner：结果契约/有界表示；amkernel Skill owner：G-BOUNDARY；执行Agent：JSON-native payload和读result摘要。

**能改变结论的证据**：若原artifact/其他response已保留完整值，应收窄该次信息损失；要证明导致具体失分仍需未恢复的决策字段与历史动作链。

#### MA03 — P1 / 003 / disagree

**待裁claim**：模块003的“恢复Down撞底墙无移动”“原六click完成4/6”“错误迷宫/unique minimal”与原保留截图矛盾。

**双方锚点**：模块`module-analysis.json#/cases/1/nearCause/claim`、`module-analysis.json#/cases/1/rootCause/evidence/1`、`module-analysis.json#/cases/1/rootCause/excludedAlternatives/1`、`module-analysis.json#/cases/1/rootCause/missingEvidence`、`module-analysis.md:209-240`；主报告/旧review`cases.json#/cases/1/causal/proximateCause`、`cases.json#/cases/1/causal/underlyingNativeClickMechanism`。

**原始锚点**：003 cell18 L3279-3281；003 cell20 L3699-3701；003 cell21 L3777-3779；003 cell22 L3961-3962；003 cell23 L4018-4020。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：本review/主报告采用原PNG；模块的中间截图缺失只是自身投影遗漏，原raw可解码。原网格与模块文本grid不一致；(3,1)是恢复后而不是六element.click后位置。

**最终采用**：十个导航动作后，六个element.click批量结束截图仍X=(0,0)；一次Right坐标tap后X=(0,1)，随后获准三个Down后末X=(3,1)，下一个Right预算拒绝。四次恢复touch有效，不是四次撞墙；不能将四次恢复进展归给之前六click。底层dispatch/快照时序unknown。

**落实条目**：
- w3:p1更正nearCause、grid、4-of-6归属和missing-screenshot；以raw executionCount20/21/22/23及PNG为准。
- w4:p1采用主报告该行为时间线；保留20步真实封顶，但不据未执行替代路线断言所有路径可行/不可行，也不称最短路线唯一。

**责任**：amkernel module-analysis owner：机制叙述修订；执行Agent/Skill G-ROUTE：先验证控制效果；Harness/Appium/Chrome owner：仅在有历史dispatch证据时再判底层原因。

**能改变结论的证据**：若有独立原始逐动作事件证明不同状态，可改变dispatch归属；当前HTTP200不能推onclick成功，错误seed重建不能覆盖原截图。

#### MA04 — P2 / 052 / compatible-but-different-scope

**待裁claim**：052原params32/31等价类与模块“至少8个同title/description生成贡献、UI覆盖未知”并不冲突。

**双方锚点**：模块`module-analysis.json#/cases/10/rootCause`、`module-analysis.json#/parentCalibration/5`、`module-analysis.md:1080-1125`；主报告/旧review`cases.json#/cases/10/oracle/initialParamEquivalenceProbe`、`cases.json#/cases/10/causal/missingEvidence`。

**原始锚点**：052 cell12 L3744-3745；052 cell13 L3823-3824；052 cell14 L3908-3909；052 cell24 L7316-7319。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：固定实例的原result.params比生成器通用下界对这个实例更精确；模块对“真实DB/UI覆盖/身份”限制更强。二者统计对象不同。

**最终采用**：原params共32occurrences/31完整内容类、恰一个二重对；特定title出现10次不等于10个重复。生成器至少8个同title/description贡献是通用下界，不是完整UI group；42视窗观测非42独立记录。未完成Delete confirmed，完整真实DB/行身份/合法34步可行性unknown。

**落实条目**：
- 合并两种统计时显式写input multiset、generated lower bound、captured viewport、DB IDs四层；禁止用32/31证明完整UI已覆盖或按params位置删。
- 052-F1/F2/F4仅保留occurrence覆盖、完整字段、JSON-native输出；不承诺已验证34步可完成。

**责任**：FSQ owner：输入等价与oracle精确行ID谓词；amkernel Skill G-COVER/G-BOUNDARY：覆盖/签名策略；执行Agent：提交前pair与survivor验收。

**能改变结论的证据**：历史DB或稳定UI row IDs可提升实际群体/删除分支结论；没有这些时不能由源码组数推UI可达性。

#### MA05 — P2 / 036 / compatible-but-different-scope

**待裁claim**：Moria字符串关系可接受与从未得到evaluator content pass可同时为真；物理目录因果仅probable。

**双方锚点**：模块`module-analysis.json#/cases/8/nearCause`、`module-analysis.json#/cases/8/rootCause`、`module-analysis.json#/cases/8/rootCause/missingEvidence/0`、`module-analysis.md:885-918`；主报告/旧review`cases.json#/cases/8/causal/rootCause`、`cases.json#/cases/8/causal/alternativesExcluded`、`review.json#/independentOfflineQueries/stringCounterevidence/actualOutput/036`。

**原始锚点**：036 cell12 L3863-3865；036 cell14 L4574-4575；036 cell19 L5633-5634；036 cell23 L6873-6874；036 cell24 L7301-7304。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：原UI字串+真fuzzy公式支持Moria本身不足解释0；模块对“并无持久path/cat/evaluator分支”边界正确。module missingEvidence称整案无截图则被原JPEG/PNG反证。

**最终采用**：捕获UI字串按真实fuzzy规则的条件关系>=0.9，不代表文件存在或evaluator已比较/通过内容。可见创建breadcrumb为Download，oracle限定Documents/Markor；物理文件路径/短路分支未捕获，因此目录失分probable。视觉采样不足可改进，但不能以Moria为本次已证失分原因。

**落实条目**：
- w4:p1把“saved UI string passes current content helper”写成条件字符串关系，不用“evaluator content pass”。
- w3:p1将“No screenshot for this episode”改为早期部分影像elided、仍有留存完整contact sheet；保留各自可证明的内容范围。
- 036-F1只教独立source/output绑定；隐含Markor目标目录由AndroidWorld owner澄清future goal，不给Agent隐藏答案。

**责任**：FSQ AndroidWorld owner：输出路径契约/证据收据；执行Agent/Skill G-ACCEPT：目录独立验收。

**能改变结论的证据**：历史find/cat和pre/post-quit快照可确定目录/内容分支；app自动路由到Markor会反证Download物理路径推断。

#### MA06 — P1 / 060 / disagree

**待裁claim**：业务聚合错误与初始化链风险可兼容，但“唯一合法measurement”、MediaStore oracle输入和具体历史分支不能从缺per-song显示推出。

**双方锚点**：模块`module-analysis.json#/cases/12/nearCause/claim`、`module-analysis.json#/cases/12/rootCause/claim`、`module-analysis.json#/cases/12/rootCause/missingEvidence`、`module-analysis.json#/fixes (060-F1)`、`module-analysis.md:1251-1296`；主报告/旧review`cases.json#/cases/12/causal`、`cases.json#/cases/12/confidenceAssessment`、`module-map.md:54-55`。

**原始锚点**：060 cell22 L6659-6660；060 cell25 L7669-7670；060 cell26 L8559-8560；060 cell30 L9791-9794。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：原source确定评分读playlist.db的SongEntity.duration而非直接MediaStore。主报告保留skip-base-init风险更完整；模块也明确未捕获per-item值，故其only-lawful推论自相矛盾。

**最终采用**：已见Select all14首/68:25与移除未commit是业务观测。evaluator读playlist.db joined duration_ms；并无历史最终行集/分支。RetroPlaylistDuration未调用基类初始化/存储隔离是独立源码风险，影响实际集合/seed范围unknown。只知道该次投影未显示per-song数值，不知道所有合法Details/原生路线都不存在。

**落实条目**：
- w3:p1删除only lawful measurement及fix060-F1同义绝对句；改成“若没有建立合法单项读取路径，可考虑有预算约束的可逆aggregate增量，未证明可成功”。
- w4:p1保留初始化风险与Agent聚合行为双线，不把缺super认成本次唯一原因；不由params15名补出当时14首/时长。
- 更正raw7669的executionCount为25、8559为26，使用原响应而不是混合ordinal。

**责任**：FSQ AndroidWorld owner：RetroPlaylistDuration.initialize_task/_get_playlist_info_query/is_successful；执行Agent/Skill G-ORDER-AGG：数值聚合策略；Harness owner：未来诊断收据，不扩预算。

**能改变结论的证据**：历史歌曲时长/DB行、初始化阶段签名或app Details数值可分离初始化/观测/持久化；未捕获不能证明路线不可能。

#### MA07 — P2 / 076 / compatible-but-different-scope

**待裁claim**：after与等于阈值契约冲突一致；“次日provably outside named day”不是唯一已证自然语言范围。

**双方锚点**：模块`module-analysis.json#/cases/13/rootCause`、`module-analysis.json#/cases/13/rootCause/evidence/3`、`module-analysis.json#/fixes (076-F1,076-F2)`、`module-analysis.md:1338-1351`；主报告/旧review`cases.json#/cases/13/causal/distinction`、`cases.json#/cases/13/causal/outcomeConfidence`。

**原始锚点**：076 cell5 L1351-1353；076 cell6 L1677-1678。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：两份都证实契约矛盾。主报告对自然语言正确性unknown更稳；原句“after5:20pm October29”可读成timestamp阈值，也可读成限定该日，未明示only该日。

**最终采用**：源码期望Grocery Shopping恰17:20却问after，契约冲突confirmed；Agent提交次日title与原oracle不符confirmed。它是否符合strict-after、该日限定/跨日范围及全局first未知；既不认定Agent正确，也不凭解释偏好认定跨日必违规。

**落实条目**：
- w3:p1删除provably outside和076-F2强制定日的此案归因；改为“若任务明确限定某日/区间则不越界；本案范围歧义须保留”。
- oracle owner决定inclusive wording或strict-later generation并定义跨日/tie；未获decision前不教Agent用边界title迎合hidden oracle。

**责任**：FSQ AndroidWorld task owner：tasks.textproto/calendargenerator/expected-answer契约；amkernel Skill G-TIME-ANSWER：保留真实范围/边界不确定性。

**能改变结论的证据**：正式task规范明示only该日可定scope；完整事件清单可证strict-after first，但当前两页UI与固定title oracle不能完成此证明。

#### MA08 — P1 / 107 / disagree

**待裁claim**：日期谓词错误一致；模块新增“confirmed merge independently unsound/dedup/两窗口丢失”无原代码支持。

**双方锚点**：模块`module-analysis.json#/cases/18/rootCause/claim`、`module-analysis.json#/cases/18/rootCause/evidence/1`、`module-analysis.json#/fixes (107-F2)`、`module-analysis.md:1803-1837`；主报告/旧review`cases.json#/cases/18/causal`、`cases.json#/cases/18/confidenceAssessment`。

**原始锚点**：107 cell7 L2436-2437；107 cell8 L2561-2562；107 cell10 L3054-3055；107 cell11 L3319-3320；107 cell12 L3580-3581；107 cell13 L3838-3839；107 cell14 L4251-4252。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：原cell14是max suffix-prefix overlap后a+b[overlap:]，不是按key全局set去重；相同窗口1/5是冗余观测，原回包逐一相等。原代码/回包比“overlap小于窗口所以错误”的概括更强。

**最终采用**：提交20而oracleCOUNT6及采用label-membership谓词confirmed。各噪声具体绝对日期/formatter语义仅source-linked或probable。四个变化窗口拼接报告26行且保留同窗重复occurrences；被省略的窗口经原回包证为未变，不能认定丢数据或独立merge根因。稳定DB/row IDs仍缺，不据fingerprint声称任意情况下覆盖必正确。

**落实条目**：
- w3:p1撤回merge confirmed缺陷；107-F2可保留“逐窗口说明重叠/冗余依据”，不得说每个冗余窗口都必须再拼入、或overlap3本身错。
- w4:p1保留label谓词为已见错误，absolute noise-date分配/formatter因果保留probable；别将通用fingerprint碰撞风险写成此案已发生。

**责任**：执行Agent/Skill G-TIME-ANSWER：先日期成员后count；Skill G-COVER：overlap依据/occurrence保留；非已证Runtime或Harness bug。

**能改变结论的证据**：稳定行ID/不可见插入或实际非冗余窗口被遗漏的原证据可证明特定merge错误；现有相等回包与纯列表拼接不支持该断言。

#### MA09 — P1 / 098 / compatible-but-different-scope

**待裁claim**：无numeric readback不是所有合法native路线不可能；主报告“drag破坏已满足255/内侧端点”也需进一步收窄。

**双方锚点**：模块`module-analysis.json#/cases/16/rootCause`、`module-analysis.json#/cases/16/nearCause`、`module-analysis.json#/fixes (098-F2)`、`module-analysis.md:1620-1700`；主报告/旧review`cases.json#/cases/16/causal/rootCause`、`cases.json#/cases/16/causal/proximateCause`、`cases.json#/cases/16/confidenceAssessment`、`review.json#/cases/16`。

**原始锚点**：098 cell3 L940-941；098 cell5 L1343-1345；098 cell6 L1644-1645；098 cell7 L2138-2140。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：模块修订后的geometry/scalar边界比主报告叙述“内侧拖动/已满足”更准确；原截图不能分辨有效track/padding，097邻案不代替098读值。本轮targeted原PNG检查支持近/full但不定数值。

**最终采用**：已见匹配literal node为0、未做semantic/numeric验收、一次swipe候选动作和reward0。正式初始整数、实际XML标签、active geometry、是否改变数值及精确末值未独立留证。若历史实际加载的谓词成功读int，则0逻辑含义为!=255；不是独立读值。无证据排除所有授权native Settings读回路线，也无证据证明初始255被该drag破坏。

**落实条目**：
- w4:p1将already-satisfied target/“Zero-node parser hid usable semantics”收窄为初始化源码请求max与literal-node观察缺口；actual098 XML缺失，邻097仅解释性证据。
- w3:p1更正098-F2 mechanism“so goal satisfied t0”为条件；维持Verify目标，不改为从低值设置，也不宣称Taskinvalid/native不可测。
- 旧review任何“可用numeric route”字样也仅为可探索策略，不作本案路线可达证明；本条为更晚的scope约束。

**责任**：执行Agent/Skill G-ACCEPT：已独立证实目标再stop；不凭模型pixel estimate认证exact255；FSQ owner：初始化/evaluator状态收据；无已证AMKernel实现bug。

**能改变结论的证据**：原始正式settings整数/完整XML或actual active-control定义可分离候选机制；新现场读值、邻案或近满图片不能填历史缺口。

#### MA10 — P1 / 106 / disagree

**待裁claim**：2对3长度拒绝一致；模块将排序选项Completed/By completion time当实际Completed任务组/已证隐藏状态过强。

**双方锚点**：模块`module-analysis.json#/cases/17/rootCause/evidence/2`、`module-analysis.json#/cases/17/rootCause/excludedAlternatives/2`、`module-analysis.json#/cases/17/nearCause/evidence/5`、`module-analysis.json#/fixes (106-F1,106-F2)`、`module-analysis.md:1704-1739`；主报告/旧review`cases.json#/cases/17/causal`、`cases.json#/cases/17/loadedSkillEvidence`。

**原始锚点**：106 cell8 L2262-2263；106 cell9 L2686-2687；106 cell10 L2796-2797；106 cell13 L3595-3596；106 cell15 L3916-3917；106 cell16 L4299-4300；106 cell18 L5112-5115。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：原cell13点击Sort，cell15/16返回Grouping/Sorting、Move completed tasks to bottom、Completed/By completion time/Descending，属于排序配置surface，不是第三任务/真实group内容。主报告对filter未知更符合观测。

**最终采用**：固定proto三title与最终两title必长度拒绝confirmed；第三身份/在UI何处/是否可达/10步内能否完整遍历unknown。Show completed操作后两candidate离开当前viewport是观测，不由menu词/checkbox或排序配置标签证明真实group已存在/可进入，更不据此排除app/visibility问题。

**落实条目**：
- w3:p1删除“Completed group exists(c20 header)”与据此排除app fault；改为排序面板配置观测。
- 106-F1/F2保留需业务membership/覆盖证明，但将“enter group/forbid toggle off”写成若实际观察到该group/状态时的条件，不向Agent泄漏hidden count或保证可达。
- 保留latent非一一matcher缺陷与本次length失败分离，不补params.title为第三项。

**责任**：执行Agent/Skill G-COVER：真实surface/membership/覆盖；FSQ AndroidWorld owner：proto/matcher及未来证据收据；不预判Tasks app或Runtime根因。

**能改变结论的证据**：真正任务group视图、稳定完成状态、第三title或完整路线原证据可提升可达性结论；当前Sort面板不能。

#### MA11 — P1 / 115 / disagree

**待裁claim**：46/48和reward0.5一致；模块断言Adventure分项0/Ultimate过、未开行菜单、gate没closed不够精确。

**双方锚点**：模块`module-analysis.json#/cases/19/nearCause/claim`、`module-analysis.json#/cases/19/rootCause/firstCausalDivergence/reason`、`module-analysis.json#/cases/19/rootCause/excludedAlternatives`、`module-analysis.json#/cases/19/rootCause/missingEvidence/1`、`module-analysis.md:1880-1926`；主报告/旧review`cases.json#/cases/19/causal`、`cases.json#/cases/19/actionBudget`。

**原始锚点**：115 cell14 L3543-3544；115 cell15 L3842-3843；115 cell27 L7007-7008；115 cell29 L7442-7443；115 cell30 L7651-7652；115 cell31 L7889-7890；115 cell32 L8367-8368。完整raw路径、输出及截图hash在`review.json.moduleAlignment.addenda[0].resolutions`与本轮查询收据。

**哪边更强**：原scalar只证明一个Boolean分项成功，不标哪一个；原cell31确实打开D7B0行More Actions并枚举，无Move up/down。原gate.closed=true但非budget耗尽。主报告分项unknown更强。

**最终采用**：可见Adventure最后两项反序及追加顺序confirmed；持久DB与UI映射、哪份Boolean通过仍unknown/probable。原分0.5且46/48主动结束，不是budget耗尽；gate结束时closed(agent_finished)。两次policy拒绝不计UI步骤。确已打开行菜单，未发现Move up/down；不等于所有合法reorder/repair不可能。

**落实条目**：
- w3:p1移除“Ultimate passes/Adventure scores0”确定归属，换成visible order likely解释一个失败分项。
- 把“row menu never opened”换成raw7889-7890已列菜单；正确原executionCount27/31/32，不沿用错位的30/35/36。
- 115-F1/F2/F3保留goal-order和条件修复，不因这些证据保证remove/readd预算内可行；不能把swipe泛称永远scroll或clickable=false当绝不drag的判据。

**责任**：执行Agent/Skill G-ORDER-AGG：有序构造/验收；Harness owner：单touch admission契约可见性；FSQ VLC oracle owner：分项/DB证据。

**能改变结论的证据**：历史playlist join rows和分项Boolean可识别赢家；成功reorder/实际payload可定修复机制；目前final自述不能覆盖账本或缺失分项。

#### MA12 — P2 / 001,014,033,076,091,106 / compatible-but-different-scope

**待裁claim**：module root confidence6confirmed/14probable是混合对象汇总，不是6个完整历史根因已证、14个其余根因均已知。

**双方锚点**：模块`module-analysis.json#/cases/*/rootCause/confidence`、`module-analysis.md:76-99`、`module-analysis.json#/verification/independentReview`；主报告/旧review`cases.json#/cases/*/confidenceAssessment`、`review.json#/findings/3`。

**哪边更强**：主报告当前拆分sourceDefect/observedBehavior/episodeFailureCause比单列root confidence更不易误读；模块段内unknown限制必须保留，内部review13项接受不能替代本次原证据裁定。

**最终采用**：001/014/076的confirmed限源码契约；033限可见filename/content构造差异；091限单项被当总数的行为；106限2vs3必拒长度谓词。物理后缀/DB、strict-first正确性、精确合计、第三title/filter/可达性等仍unknown或probable。其余14个probable也不是已证底层因果链。

**落实条目**：
- w4:p1不要把6/14当已定位历史原因成功率；引用各案分层confidence字段并标claim对象。
- w3:p1coverage表root confidence加scope或拆source/behavior/episode；unknown链不被probable整案标签吞掉。
- Runtime已知InvalidElementStateException诊断限制为独立非causal缺陷，原391无该异常，不算本轮失败产品bug。

**责任**：两报告owner：置信语义/对外结论；amkernel Runtime owner：非causal诊断问题单列。

**能改变结论的证据**：具备对应历史evaluator输入/分支/状态可升episode归因；重新跑成功或模型自述不算历史闭环。

#### MA13 — P2 / 003,036,052,060,076,098,106,107,115 / compatible-but-different-scope

**待裁claim**：37fix/7common组可提供产品位置映射，但不能据此把主报告44fix逐条视为已实施/已证有效或重做此前26项审查。

**双方锚点**：模块`module-analysis.json#/fixes`、`module-analysis.json#/commonFixes`、`module-analysis.json#/sourceReferences`；主报告/旧review`cases.json#/cases/*/fixes`、`review.json#/fixReview`。

**哪边更强**：模块src/amkernel/skill与Runtime符号映射更精确，可被主owner用于其在途26项落点修订；修复依据的真假则以MA03/06/08/09/10/11原证据为准。

**最终采用**：G-BOUNDARY/ROUTE/ACCEPT/COVER/ORDER-AGG/TIME-ANSWER是Agent策略与Skill提案，不是缺规则已证导致失分。E-TASK-CONTRACT由AndroidWorld owner决定future version。不得以预算增加、增重试、放宽oracle或默认DOM/多pointer能力造成功。

**落实条目**：
- w4:p1仅借用明确location与cross-project owner；其后未来修订不在本轮锁定review范围。
- w3:p1同步修正060-F1唯一measurement、076-F2唯一day-scope、098-F2已证初始255、106-F1/F2配置组、107-F2冗余窗口、115-F2/F3handle/repair可行性的错误前提。
- 37fix与44fix按机制关联，不强行一一计数；验收必须能被反证且遵守原协议/预算，未经授权不实施或运行。

**责任**：amkernel Skill owner：策略文档提案；amkernel Runtime owner：仅结果/诊断契约；FSQ Harness owner：admission/收据；AndroidWorld owner：任务generator/goal/oracle。

**能改变结论的证据**：合法同预算隔离验收若另获授权且确有成功/失败证据，可检验proposal；本次未执行模块隔离探针，更未测其对LLM效果。

### 本轮实际只读查询与执行归属

- 从前轮已核验原raw的内存快照定向投影17条`result.kind=repr`：003(4)、014(2/7)、024(5/12)、052(8/12/15)、058(3)、085(7)、091(2)、098(4/5/7)、106(9/14)、115(8)，括号为executionCount。各条`output.truncated=false`、`result.truncated=true`；没有执行单元或oracle。

- 对107原回包做数组相等比较：初始两个scroll的before/after均相等，exec13末窗before/after亦相等；四个变化窗口连续边界的有序(title,description,due)一致。原cell14是suffix-prefix overlap拼接，不是set去重；相同重复occurrence仍在首窗。只做原值比较，不执行Agent代码或计分。

- 只解码003四张、098两张原PNG进行裁切观察，未采新截图、未写图像文件。003六click后原点，坐标tap后右移，末恢复到(3,1)；098两图近/full，但active track和255整数均不可由图推出。036完整JPEG存在性及hash另作字节检查，视觉结论仍归属前轮review。

- 只读对照`retro_music.py:41-58,260-293`和`tasks.textproto:858-893`；发布源码、原请求/响应优于投影丢失、模型自述和当前未钉app实现。没有测试、task/init/score重跑、Runtime/SDK探针、设备/MCP/ADB/Appium/服务操作。

### 跨项目责任与交回要求

- **FSQ_AndroidWorld_eval / AndroidWorld**：001/014/076源码契约问题；060跳基类初始化是风险，非已证历史失分；033/036输出/换行wording、106due/completed及latentmatcher分开决策。 Task语义选择由owner决定future version；不追改旧reward、不给Agentexpected answer。 精确file/symbol见JSON责任建议。

- **amkernel Skill / execution Agent policy**：G-BOUNDARY/ROUTE/ACCEPT/COVER/ORDER-AGG/TIME-ANSWER；既有规则已加载，不等于缺一条Skill导致失败。 按MA03/06/07/08/09/10/11纠正特定方案依据，再将generic策略标proposal，验证不扩预算/重试/授权面。 精确file/symbol见JSON责任建议。

- **amkernel Runtime**：strict JSON-native whole-result摘要是已证机制；是否改变设计另决策；InvalidElementStateException诊断限制为独立非causal缺陷。 不把17次repr算10案根因；不把未出现的异常诊断修正宣称本轮被测改进。 精确file/symbol见JSON责任建议。

- **FSQ_AndroidWorld_eval Harness**：native-only/single touch、pre-admission refusal vs charged upstream failure、business final及evaluator边界。 补协议可见性/未来最小分项收据是诊断提案，不自动增加动作/开放DOM或隐藏多交互。 精确file/symbol见JSON责任建议。

主owner `w4:p1`采用本节resolution整合；模块owner `w3:p1`修其残留事实/机制句；本review不改双方主报告。不把5个主题级disagree等同5个新产品bug：多为报告投影/范围/谓词归属错误；098还需收窄主报告与旧review的过强初始状态/端点表述。没有本轮证据证明AMKernel Runtime实现bug导致这些正式失分；已知诊断限制独立列出，不抹成“产品没有任何bug”。
