# Calendar / Retro：r4 原生失败逐例离线调查

覆盖：059、060、068、069、070、071、072、074、076、078，共 10 例。本文只分析已有证据；不修改源代码、配置、SDK、既有结果，不调用设备、ADB、模拟器、模型、任务或评分器，不启动新 campaign，不安装软件，不执行测试。所有修复与验证均为未来建议。

## 阅读约定与共同边界

- `BASE` = `evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4`。下表 `RNNN` 为该例原生运行目录、`ENNN` 为 episode 目录；`RNNN/execution-result.json`、`events.jsonl`、`report.json` 及 `ENNN/raw-private/fsq-native/worker/{fsq-task-result.private.json,native-action-audit.jsonl,request.json}` 均已逐例读取。`events #N` 表示原始 `sequence`，`audit #N` 表示 action audit 的 `sequence`，`agent-…-N` 是执行步骤 ID，不可相互混用。
- 每例还读取 `ENNN/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。10 例官方 reward 均保持 **0**（原始 int/float 表述不作改分），evaluator 均正常返回、无异常，`componentResults.status=not_provided`，`logCapture.records=[]`；因此不能把某个猜想写成已由官方确认的扣分分项。worker 均 exit 0、未到 business deadline；“原生步骤失败”“主 runner 的业务 inconclusive”“官方 reward 0”是不同层次。
- 初始化参考时间均为 **2023-10-15T15:34:00+00:00，UTC**；设备截图实际显示 Sun, Oct 15 / 15:34 起的时间。2026 年 host 文件时间和执行时间不是日历检索参考日期。`request.json` 没有独立 referenceTime/timezone 字段；实际 worker 构造 Task 只用公开 goal 等字段。不能由此断言模型必然不知道日期：它看到了设备日期、月份与选择器年份。
- 月视图截图有可见日期数字和蓝色事件块，但相应保留 UI XML 只暴露顶栏和容器，未给出可用的日期数字/事件标题定位。截图与 XML 的差异已实际目视核对，不能把 XML 没有事件当成“当天无事件”。`ui_snapshot.coverage.status=partial`，仅凭它也不能证明是压缩器删掉日期；原始 Android 自绘/可访问性层与压缩层各自的贡献仍需区分。
- `report.json.agent_output`、结果中 `tool_name=agent_runtime.runner` 的 `tool_output` 是主执行报告；不是 verifier，也不是官方评分。10 例 mainAnswer 都是 `status=valid, businessStatus=inconclusive`：有效指结构与出处有效，不指业务答案正确。信息检索例提交的 summary 都是无法确定/无法核实的说明，并非“没有事件”。不得把未来 private fixture 标题直接提供给模型补答案。

### 原始证据目录别名

- `E059` = `next-stage-plan/execution/run/episodes/059-RetroPlayingQueue`
  - `R059` = `E059/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-059-20261110T194558Z-40f104`
- `E060` = `next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration`
  - `R060` = `E060/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-060-20261110T195314Z-4b9455`
- `E068` = `next-stage-plan/execution/run/episodes/068-SimpleCalendarAnyEventsOnDate`
  - `R068` = `E068/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-068-20261110T203716Z-cc47af`
- `E069` = `next-stage-plan/execution/run/episodes/069-SimpleCalendarDeleteEvents`
  - `R069` = `E069/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-069-20261110T204031Z-070a4c`
- `E070` = `next-stage-plan/execution/run/episodes/070-SimpleCalendarDeleteEventsOnRelativeDay`
  - `R070` = `E070/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-070-20261110T204453Z-796afd`
- `E071` = `next-stage-plan/execution/run/episodes/071-SimpleCalendarDeleteOneEvent`
  - `R071` = `E071/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-071-20261110T204756Z-e5e868`
- `E072` = `next-stage-plan/execution/run/episodes/072-SimpleCalendarEventOnDateAtTime`
  - `R072` = `E072/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-072-20261110T205143Z-7d9f1b`
- `E074` = `next-stage-plan/execution/run/episodes/074-SimpleCalendarEventsInTimeRange`
  - `R074` = `E074/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-074-20261110T205836Z-f11b48`
- `E076` = `next-stage-plan/execution/run/episodes/076-SimpleCalendarFirstEventAfterStartTime`
  - `R076` = `E076/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-076-20261110T210507Z-a98ce7`
- `E078` = `next-stage-plan/execution/run/episodes/078-SimpleCalendarNextEvent`
  - `R078` = `E078/raw-private/fsq-native/workspace/.fsq/runs/android/fsq-native-gpt61-r4-clock-lifecycle-20261110-run-078-20261110T210944Z-e9ef93`

### 冻结执行机制的源码锚点

源码根为 `/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent`。以下 FSQ 文件均在 parent 已逐文件校验与冻结 manifest 一致的 16 文件集合内；对应 package sha256 `5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`，不可只依据 dirty HEAD 推断执行行为。

- **S-Locator**：`drivers/android/_uiautomator2.py::tap_on` **109–116**，只等 selector 存在、click 后返回 passed；`_selector/_selector_query` **356–381**，裸 `target` 只变成 `text=…`，不会匹配 content-desc；有 xpath 则直交给设备 xpath。`More options`、`Playlists` 等“屏幕可见/有 content-desc”不等于裸 target 可点击。`launch_app` **94–100** 只调用 app_start 后返回 passed，不验证已到目标 activity；本文只记实际仍在 launcher，不推断未安装或错误包名。
- **S-Input**：同文件 `input_text` **137–151**，click → 可选 clear_text → set_text → passed，无字段回读或业务日期提交确认；passed 不能证明 NumberPicker 的值真正改变。
- **S-Observation**：同文件 `ui_snapshot` **237–275** 返回 XML、partial coverage、50 字符文字属性限制；`_compact_ui_snapshot_node/_compact_ui_snapshot_attributes` **297–339** 保留有信号节点、裁剪属性/文字，不提供自绘日期格的识别。`harnesses/_android.py::capture_artifact` **128–158** 保存截图字节与快照；`adapters/coding_agent/_harness_tools.py::_format_runner_result/_result_summary` **147–218** 返回 JSON 和 artifact refs，不应把“存在截图路径”视为主模型已理解像素。
- **S-Skill**：`resources/skills/android-harness.md` **7–10** 规定 launch/kill lifecycle，**14–18** 规定当前结构证据、locator 优先及重新观察，**23–26、78–80** 规定断言与 AI visual verdict。`resources/skills/automation-basics.md` **3–6** 优先平台工具与确定性断言。现有指导没有区分月/日选择器、NumberPicker提交回读、检索覆盖证明和重复确认的边界。
- **S-Plan**：`agent/_pre_plan.py` 模块级预规划指令 **14–46**，规定忠实提炼 goal、只一个最终目标、不增加无关约束；`agent/_core.py::_augment_goal_only_task_with_pre_plan` **145–201** 把预规划 key_actions/verification_goal 注入 task。`agent/_prompt.py::PromptModelBuilder.build_task_prompt` **65–95** 把 Task、runtime_policy 与单一 verification_goal 交给主执行。
- **S-Answer**：`models/_agent_io.py::AgentFinalOutput` **39–50** 只有泛化 `summary: str`，没有专门检索答案字段或标题列表约束。实际 producer `PN/fsq_worker.py::select_main_answer` **22–57** 只从唯一正常主 runner 的已验证 `task_run_v1.summary` 选答案，**193–197** 用公开 goal 建 Task。这里 `PN = E078/raw-private/fsq-native/worker-site/fsq_androidworld_eval`；10 例 producer 两文件逐份 SHA256 相同，`fsq_native.py=0af6d9b3802fcfd5708bc9dcdf2132bf48a9e3da01ae0401fafa6ae9ad468e13`、`fsq_worker.py=22cfac33ddf511c8b75b4d92ffe6067b3ec745f2c9b29eb93601484a005176d2`，不是当前仓库 producer 的猜测。
- **S-Budget**：`PN/fsq_native.py::NativeDispatchBudget.dispatch` **85–118** 在转发前给写 capability 计费，达到 maximum 后拒绝；`_finish/snapshot` **120–142** 记录成功/失败，已受理而目标不存在的动作仍消耗额度；观察/断言不算写额度。launch/kill 也在 **20–24** 的写 capability 中。拒绝后重试同一动作不会恢复额度，也不能把拒绝的 Delete 说成已删除。
- **S-Verify**：`agent/_verification_task.py::VerificationEvidenceBuilder.build/_agent_claims` **31–81** 把主执行结果当 claim；验证指令 **187–198** 要求不在缺证据时推定成功，也不重读 visual assertion 的像素。`agent/_core.py` **106–115** 执行独立 verification 并用其 summary 发出 run_completed。因此 run_completed.summary 不等于 mainAnswer.summary。
- **S-Runtime**：`adapters/coding_agent/_runtime.py::_ToolOutputBudgetFilter` **79–148** 将长/旧工具输出落盘并给路径；`_build_request` **885–904** 传结构输出契约和 max_turns；`agent_engine/_runner.py::run_agent` **129–174** 的 EngineError(max_turns) 是另一边界。本组 059/060 有正常主 runner 输出且无预算拒绝，不能凭反复 search/read 或 summary 中“window”措辞臆断 max_turns/时间超限。

修复归属缩写：FSQ-runtime/driver/skill 由 FSQ owner；producer 的输入/预算回执/答案传递由 harness owner 与 FSQ owner 联合设计。以下不要求加大既有额度、重试新 episode、改变 rubric，未来验证只在获授权后进行。

## 案例 059 — RetroPlayingQueue

交叉核对：已核对轨迹、有契约冲突保留。retro_music.py:79–97/203–206完整playing_queue title列表==5expected，不是suffix/delta/相对顺序；noise/重复充分失败。初始queue缺证，不坐实跨题污染。

### 目标与约束
公开 goal 要求把五首歌依次加入 **playing queue**：Through the Storm → Hidden Paths → Forever Young → Whispers of the Past → Heartbeat Away；不是建 playlist，也没授权清空既有队列。私有 fixture 中的 playlist_name 不是额外用户要求。原 reward=0，native outcome=inconclusive。

### 真实动作链与屏幕转换
1. `events #19/#23`、`agent-launch_app-1/3` 均 passed，但后图仍是 launcher；`swipe-4/6` 打开/滚动应用抽屉，`tap_on-8` 才进 Retro，`tap_on-10` 进 Songs。初次 Songs XML 有 15 首库内歌曲，尚未打开队列，不存在可靠的初始 queue 基线。
2. `events #67` / `tap_on-14` 针对 Through the Storm 的祖先 ViewGroup + 直接 menu XPath，后图实际为含 “Add to playing queue”的菜单；`#71` / `tap_on-16` 点击该项，后图出现 Through the Storm mini player，实际渲染截图还有toast **“Added 1 title to the playing queue.”**。这是首个Add执行成功的正证据，不能照搬模型“缺少首次添加证明”而忽略；但没有队列前后基线，仍不能证明该occurrence在后续动作后幸存于正确追加序列。
3. `events #81/#89` / `tap_on-20/22` 尝试 Hidden Paths menu；后图仍是 Songs 而不是菜单，且随后 mini player 显示 Whispers of the Past。不能把 passed 当成菜单已打开，也不能仅凭播放器变化推断具体误点/自动播放机制。`swipe-24/26/28` 调整列表；`#105` / `tap_on-30` 后图终于有菜单，`#109` / `tap_on-32` 点击 Add。
4. `tap_on-36/38`、`tap_on-41/43`、`tap_on-46/48` 分别完成后面三首的菜单→Add。`tap_on-50` 开播放器，`tap_on-52` 开 Now playing queue，`swipe-54` 到尾段。后图可见旧的一段 `…Hidden Paths, Through the Storm, Silent Dreams, Chasing Shadows, Beyond the Horizon, Whispering Wind`，随后才是 `Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away`。同名 Hidden Paths 出现两次，不能只按标题匹配一个旧 occurrence。
5. `events #163` / `assert_with_ai-56` 要求五首新追加歌连续，返回 failed；`#165` / `assert_with_ai-57` 改成允许插曲的相对顺序，返回 passed，指出当前可见行 3/8/9/10/11。原图目视支持这两个不同命题；后者不能推翻前者，且不证明 Through 的 observed occurrence 是本次新追加。主 runner 与独立 verifier 都保留 inconclusive，没有把相对顺序宣称为完整成功。`kill_app-58` 成功。audit 共受理 30/32 写动作，无拒绝、无 deadline。

### 首个偏离、直接失败、机制层级
- **事实**：第一处可直接证明的导航分叉是 `tap_on-20` 未到期待的歌曲操作菜单；其成功回执没有业务页面后置条件。播放器由首次Add后的暂停态变为播放态、随后换成另一歌，与后来整库般队列同时出现，**支持“误进入播放/队列被重建”的竞争解释但未证明**；不能把所有错误归在第一个Add。更早 `tap_on-16` 的首次 Add 对空/已有队列具体语义无法由现有图证明，不能提前定性为错歌。
- **事实**：最终尾段只有四首请求歌曲连续可见；没有基线可严格称整个尾段都是新增加，但这些四次后续Add有动作证据。Through 的首次Add有toast正证据，其最终occurrence来源/位置则未闭环。首次视觉断言失败后只改断言命题、未修复队列，业务动作并未因此完成。相对顺序是必要证据之一，不是“追加五首”的充分条件。
- **强推断**：主策略没有把“每次 Add 必须产生目标 queue delta”当不变量，也没有在菜单未打开时阻止推进；这使旧队列同名歌可被误当本次追加的证据。S-Locator 的 click-only passed 和 S-Skill 的泛化断言规则允许这一证据空洞。
- **官方已闭合/未知**：完整playing_queue title列表严格==5expected；当前noise/重复充分0，不再留后缀判据未知。initialize:147–160只清storage/playlist，:100–107未清queue，不据此坐实跨题污染。原初始queue、哪次点击改变播放/重建仍未知；XPath pre-state只有一个直接menu，不支持必因多重匹配错点；无max_turns/预算耗尽。

### 修复建议与未来验证
- **CR-59 / P1 / FSQ-skill+runtime**：在 `resources/skills/android-harness.md` 的操作后验证规则增加有序集合编辑约束：先读取现有队列基线/尾部，进入目标行菜单后才允许 Add；每个真正不确定的 Add 后核对新增 occurrence 和相对位置，而非最终全局 `contains`。主执行维护“已确认追加到哪一首”的游标，菜单没打开就不推进，不通过放宽断言替代修复。对应机制锚点 **S-Locator（tap_on 109–116、_selector 356–381）、S-Skill（14–26）、S-Verify（187–198）**。
- **边界/冲突**：非空原队列仅追加五首可符合公开add语义，但不保证通过完整列表oracle；不可擅清用户queue凑分，需独立任务/fixture语义冲突处理，保留初始queue缺证。
- **未来验证（未执行）**：分别覆盖空/非空/同名队列，区分公开追加delta与官方完整列表；先澄清合同，不承诺追加方案通过现oracle，不增预算或盲重复Add。
- **剩余未知**：原初始queue与播放状态变化来源；完整列表评分边界已闭合。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R059/sources/000-goal.txt`；原生链路：`R059/execution-result.json::steps[*].step_id/phase_reports`、`R059/events.jsonl::sequence/tool_arguments`；主结论：`R059/report.json::agent_output`、`E059/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E059/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E059/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-92223036cc8a.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-ed41fa720c79.json`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-392c18aa8689.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-4584a57f2809.json`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-6317df9ee6d5.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-4524d988acff.json`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-ada040777868.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-20-finalize-after-action-1-d92305ae2279.json`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-tap-on-52-finalize-after-action-1-6428d8008fa4.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-52-finalize-after-action-1-e0a0b5417c43.json`。
- 实际目视PNG：`R059/artifacts/screenshots/screenshot-agent-swipe-54-finalize-after-action-1-2f9a74c8ad24.png`；相同阶段结构快照：`R059/artifacts/ui-snapshots/ui_snapshot-agent-swipe-54-finalize-after-action-1-4bda1cddaadd.json`。

## 案例 060 — RetroPlaylistDuration

交叉核对：已核对。只读noise一首04:44，零Add，0Songs/00:00与根assert空串分开；25/30零拒绝正常停非硬timeout。retro_music.py:41–76/286–293按指定playlist JOIN实际duration_ms总和45–50min，空总0充分失败。

### 目标与约束
公开 goal：在 Retro Music 创建名为 **Reggae Rhythms 51** 的 playlist，使用提供歌曲，总时长 **45–50 分钟**。名称、成员和总时长共同成立才完成；不是把播放队列时长或正在播放歌曲时长当 playlist 时长。原 reward=0.0，native outcome=failed。

### 真实动作链与屏幕转换
1. `launch_app-1/3` 后仍 launcher；`swipe-4/6 → tap_on-8` 从抽屉进入 Retro；`tap_on-10` 开 Songs。`events #51` / `tap_on-12` 点 Beyond the Horizon **歌曲本体**，出现 mini player，`tap_on-14` 开播放器，看到单曲 `04:44`；这是单曲信息，不是所需的组合求和。
2. `press_key-16/18` 返回；`tap_on-20` 再进 Songs，`long_press_on-22` 显示 1 selected，但 `press_key-24` 退出选择。`events #91/#95` / `tap_on-26/28` 通过首行 menu → Details，后图明确 `Beyond the Horizon.mp3 / Length: 04:44`。整个 trace 只实际读到这一首时长，未记录完整 duration 表、子集选择或秒数求和。
3. `tap_on-30` 关 Details，`press_key-31` 返回首页；`tap_on-33` 裸 target “Playlists” target missing，`tap_on-35` 改 action_playlist 成功；`tap_on-37` 裸 “More options” target missing，`tap_on-39` 改 accessibilityId 成功。`tap_on-41` New playlist → `input_text-43` 名称 → `tap_on-44` Create。
4. 创建后 `events #133` 对应快照显示完整标题及 **0 Songs • 00:00**；实际渲染图同样是空 playlist 卡片。`assert_state-46` 没有 element，仅 text.contains，返回 `Text assertion failed` / invoke `harness_output.text=""`；这不是空卡片不存在，而是断言没有正确限定文本元素。`assert_visible-47` 只证明标题存在。随后 `kill_app-48`；没有任何 Add to playlist 动作。
5. audit 25/30 写动作、denied=0、deadlineExceeded=false；主 runner **正常 success 返回**结构化业务 inconclusive，耗时309757ms，无 EngineError(max_turns)。其“navigation…consumed the execution window”仅是模型叙述，不能替代边界记录。verifier 依据实际卡片判 failed；官方0.0与其一致，但非从 verifier 产生。

### 首个偏离、直接失败、机制层级
- **事实**：计划要求先检查时长并选组合；`tap_on-12` 先进入播放，之后围绕同一歌曲反复退回/选择/Details，但没有形成完整候选集合。首次严格可证的最终不满足是 `tap_on-44` 后空卡片，加上之后没有添加动作且直接结束。
- **事实**：直接失败是成员为0、总时长00:00，不是45–50分钟。失败的无元素文本断言与空 playlist 是两件事；即使修好断言仍不会添加歌曲。名称成功不是局部替代验收。
- **强推断**：主策略把“建出容器”当作可交付进度，在算术/成员计划失败后仍提交结束；缺少 duration/selection/saved-total 的业务闭环。S-Locator 中 text-only target 造成的两次 target missing 是成本放大因素，非唯一根因。
- **未知**：可用歌曲组合在本 seed 中各时长的完整表、是否存在展示全曲时长更省动作的 UI；不能用私有 files/noise_files 名单反推未来模型应选的组合。没有证据支持“时长加法算错”“提供歌曲不足”“官方rubric错误”或硬预算不足。

### 修复建议与未来验证
- **CR-60 / P1 / FSQ-skill+主策略**：为明确时长约束任务在 S-Skill 增加现有 UI 可见歌曲的 `(title, duration_seconds, selected)` 台账，`m:ss → 60m+s` 后总和比较45×60与50×60，先选有效组合再创建/添加，保存后以对应 playlist 卡片/详情的聚合时长独立核对。没有成员变更证据时不得把“标题存在”列为时长目标完成。来源 **S-Plan（预规划14–46及注入145–201）、S-Locator（356–381）、S-Input（137–151）**；本例预规划本来就忠实，主要修复主执行履约而非改 goal。
- **CR-60-assert / P2 / FSQ-driver+skill**：在 `assert_state` 用稳定 playlist 卡片/时长元素的 locator 限定范围，禁止把无 element 的根节点空文本误当页面全文；S-Locator `_selector` **366–369** 的空 selector 与本例 invoke.text="" 是证据。提示修正调用，不得抑制断言异常或把 failed 改 passed。
- **边界/风险**：不把 queue 的01:xx或单曲04:44加到 playlist；不直接用fixture的隐藏列表；不得靠重复同一歌曲凑时长，除非公开用户约束明确允许。
- **未来验证计划（未执行）**：授权后用公开 UI 建完整候选时长表，验证边界45:00/50:00及中间秒数、无可行子集时诚实结论、保存成员/总时长一致；保持30写动作上限和真实媒体元数据，不给模型标准答案。
- **已闭合/未知**：指定playlist实际duration_ms总和为判据，空0充分失败；2850000仅初始化理论组合，不是本轮已读曲长。合法UI完整时长表未知，不取私有最佳组合补模型。native与runner总时长范围不同不算矛盾。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R060/sources/000-goal.txt`；原生链路：`R060/execution-result.json::steps[*].step_id/phase_reports`、`R060/events.jsonl::sequence/tool_arguments`；主结论：`R060/report.json::agent_output`、`E060/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E060/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E060/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R060/artifacts/screenshots/screenshot-agent-tap-on-10-finalize-after-action-1-45aac531f41b.png`；相同阶段结构快照：`R060/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-10-finalize-after-action-1-3552491dd676.json`。
- 实际目视PNG：`R060/artifacts/screenshots/screenshot-agent-tap-on-28-finalize-after-action-1-27cd9fbb6726.png`；相同阶段结构快照：`R060/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-28-finalize-after-action-1-6cebd207fdae.json`。
- 实际目视PNG：`R060/artifacts/screenshots/screenshot-agent-tap-on-44-finalize-after-action-1-52adf856eb46.png`；相同阶段结构快照：`R060/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-44-finalize-after-action-1-e4528c8ee794.json`。

## 案例 068 — SimpleCalendarAnyEventsOnDate

交叉核对：已核对。grid无数字text、picker仅月年；Oct28三title withoutreplacement，完整生成标题缺证，未到目标集合非已转录错。

### 目标与约束
公开 goal 问 **October 28** 有哪些事件，**仅标题**，多项逗号分隔；公开文本未写年份，不能把隐藏 title 参数当答案。设备/初始化上下文是2023-10-15 UTC，月年选择器实际显示Oct/2023。原 reward=0.0，native failed；mainAnswer有效但业务 inconclusive。

### 真实动作链与屏幕转换
1. `events #19/#23` / `launch_app-1/3` 后都仍是 launcher；`#25` / `tap_on-4` 点 Predicted app: Calendar 后进入 October 月视图。实际截图可见许多蓝色事件块（含月末区域），但本次 XML 无可点击的文本“28”。
2. `#33` / `tap_on-6` 点 top_value，打开的滚轮只有 **月份和年份**（Sep/Oct/Nov；2022/2023/2024），没有日字段；`#37` / `tap_on-8` 直接OK回同一 October月视图。
3. `#41` / `tap_on-10` 用 text=28，返回 Target was not found；这是本例首个明确失败导航动作。`tap_on-12/14`、`tap_on-16/18` 又两次打开/确认同一月年对话框，未改变日期选择路径、未切 Daily view，也未读取任何目标日标题。
4. `#73` / `tap_on-21` 再点 top_value 时 audit **#41 denied/action_budget**；`kill_app-22` audit #42 同样拒绝。累计写10/10、其中一次 target missing 仍计费；无截止超时。最终屏仍 October 月视图。主 summary：`Unable to verify the complete October 28 event titles before the harness action budget was exhausted.`；不是“当天没有事件”。verifier failed依据答案非标题而非断言日历空。

### 首个偏离、直接失败、机制层级
- **事实**：在已经是Oct/2023时反复确认月年对话框不提供日级检索；首次可证偏离是 `tap_on-10` 将截图中的自绘日期假定为 XML text 元素。后续三组月年选择器没有产生新覆盖。
- **事实**：直接失败是没有取得28日完整列表、summary未给出标题。没有 no-result 页面，更没有可证明“无事件”的覆盖证据。
- **强推断**：主策略未按控件实际能力识别“月级选择器≠日级选择器”，S-Observation 的partial结构被反复当作完整导航空间；S-Skill没有让策略在一个不可寻址日期失败后切换到能暴露day字段的日视图。额度耗尽是这个循环的后果，而非解释所有导航错误的根因。
- **未知**：28日实际完整事件集合、年份省略的官方消歧规则（本地证据支持2023上下文，但不能以隐藏参数新增规则）；原始自绘/可访问性和XML压缩分别造成多少缺失。不得把数据未出现在XML写成fixture没初始化。

### 修复建议与未来验证
- **CR-68 / P1 / FSQ-skill+主策略**：在 `resources/skills/android-harness.md` 当前观察/locator规则 **14–18** 增加控件能力分流：在月视图找不到目标日结构节点且top_value只给月/年时，保留已经确认的月/年，切现有 Change view → Daily view，再用有日字段的picker或有界日导航定位28日；每次提交回读top_value，目标日未确认前不收集“答案”。引用 **S-Observation（ui_snapshot 237–275）、S-Locator（356–381）、S-Budget（85–118）**。
- **P2 / FSQ-runtime+producer**：从实际动作回执暴露剩余写额度供执行策略使用，状态不变时停止相同月年OK循环，保留纯观察用于整理已知证据；不修改计费上限。
- **边界/风险**：不得直接把截图的小字月份事件块当完整标题；不得把无法确定转为无事件；省略年份必须使用用户可见日期上下文而非host时间。
- **未来验证计划（未执行）**：获授权后覆盖月视图日期不可访问、日视图滚轮、月末/跨年及同日多标题；目标日头/所有列表页均覆盖后才允许输出标题或可证无结果；仍用10写动作。
- **给 harness owner 的逐例问题**：请确认省略年份的相对参考语义和28日既存UI数据，不把标量0反推为标题转录错误。本例根本未到转录阶段。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R068/sources/000-goal.txt`；原生链路：`R068/execution-result.json::steps[*].step_id/phase_reports`、`R068/events.jsonl::sequence/tool_arguments`；主结论：`R068/report.json::agent_output`、`E068/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E068/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E068/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R068/artifacts/screenshots/screenshot-agent-tap-on-4-finalize-after-action-1-8a7df39d557c.png`；相同阶段结构快照：`R068/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-4-finalize-after-action-1-9079ec56e058.json`。
- 实际目视PNG：`R068/artifacts/screenshots/screenshot-agent-tap-on-6-finalize-after-action-1-2deea0790d6b.png`；相同阶段结构快照：`R068/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-6-finalize-after-action-1-9e11e9289dfc.json`。
- 实际目视PNG：`R068/artifacts/screenshots/screenshot-agent-tap-on-18-finalize-after-action-1-25b358978a75.png`；相同阶段结构快照：`R068/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-18-finalize-after-action-1-2205ac46592d.json`。

## 案例 069 — SimpleCalendarDeleteEvents

交叉核对：已核对。无Delete且循环；冻结3target/20noise可确认，afterDB未知，不假称读到终态。

### 目标与约束
公开 goal：**删除2023-10-27当天全部日历事件**。破坏性动作范围是这个日期，不是本月所有事件。原reward=0.0，native及主报告inconclusive；不能据此改成passed或“删错事件”。

### 真实动作链与屏幕转换
1. `launch_app-1` 后launcher；`tap_on-3` 进October月视图；`events #31/#35` / `tap_on-5/7` 从accessibilityId=More options → Go to date。对话框图/XML只有Oct和2023滚轮，没有“27日”；`tap_on-9` OK仅回October月视图。
2. `events #43` / `tap_on-11` 裸target=27失败；`#47` / `tap_on-12` 裸target=More options也失败（实际只有content-desc）。两次失败仍是已受理写操作。新快照仍月视图。
3. `tap_on-15/17/19` 用正确的More options locator重新Go to date→OK；`tap_on-21` text=27再次Target was not found。随后 `tap_on-24/26/28` 第三次重复月年对话框→OK；整个过程中没有切day、打开event、Delete或确认删除。
4. `events #97` / `tap_on-30` More options被audit **#59 denied/action_budget**；`kill_app-31` #60同拒绝。14/14写动作全用在launch、入口、月年导航与失败locator；原生最后还是October月视图。主summary：`Could not complete event deletion or verify that October 27, 2023 is empty. The harness action budget was exhausted during navigation.`

### 首个偏离、直接失败、机制层级
- **事实**：`tap_on-7` 暴露月级picker后直接OK没有选择目标日，`tap_on-11` 对不存在的text=27开始明确失败；之后重复同一策略。不是目标日为空，也不是删除时出了错。
- **事实**：所有原生动作和audit中都没有Delete调用。直接失败是请求的破坏性事务没有发生，亦没有目标日“剩余事件=0”的后状态证据；主/独立验证保留未知最终状态是正确的证据边界。
- **强推断**：主策略缺少“先确认目标日期及完整集合→再允许删除→确认剩余集合”的事务门；日期控件误用 + text/content-desc混淆消耗额度，并未进入删除事务本身。S-Locator **356–381** 能直接解释裸More options失败，不能解释成系统菜单故障。
- **未知**：官方数据库在agent前后具体集合；月视图蓝色块只能证明有展示内容，不可据小截图补全27日标题或精确对象。没有已发生误删/删错日期的证据。

### 修复建议与未来验证
- **CR-69 / P1 / FSQ-skill+主策略**：对“按天全部删除”在 `resources/skills/android-harness.md` **14–26** 增加明确事务边界：进入Daily view，定位并回读 **2023-10-27**，收集该日完整事件集合，允许公开UI多选或逐项删除，每次确认后重新读本日剩余列表，最终以本日头+无剩余事件断言结束。月年picker OK不是目标日确认；发生target missing后禁止原样重放同一轮Go to date。引用 **S-Plan（145–201）、S-Locator（109–116、356–381）、S-Budget（85–142）**。
- **边界/风险**：只删目标日期项；跨日/循环事件若UI询问单次或整系列须按公开任务意图约束，不得默认整系列；不能为省额度绕过确认或改数据库。不要增加预算掩盖月级导航循环。
- **未来验证计划（未执行）**：授权后验证目标日0/1/多项、异日同名项保留、删除后重新进入该日依旧为空、循环事件确认边界；保持14写动作，观察不计费的既有合同不变。
- **给 harness owner 的逐例问题**：请依据既存fixture/官方后状态确认没有Delete是否足以解释0，以及跨日/循环事件日期归属；这里不预设oracle的具体删除集合。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R069/sources/000-goal.txt`；原生链路：`R069/execution-result.json::steps[*].step_id/phase_reports`、`R069/events.jsonl::sequence/tool_arguments`；主结论：`R069/report.json::agent_output`、`E069/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E069/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E069/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R069/artifacts/screenshots/screenshot-agent-tap-on-3-finalize-after-action-1-01386c605b22.png`；相同阶段结构快照：`R069/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-3-finalize-after-action-1-d6d02cd6fa64.json`。
- 实际目视PNG：`R069/artifacts/screenshots/screenshot-agent-tap-on-7-finalize-after-action-1-d748ae334a03.png`；相同阶段结构快照：`R069/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-7-finalize-after-action-1-3a46e09f72c6.json`。
- 实际目视PNG：`R069/artifacts/screenshots/screenshot-agent-tap-on-28-finalize-after-action-1-0ea189d7731b.png`；相同阶段结构快照：`R069/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-28-finalize-after-action-1-84d085eeb0bf.json`。

## 案例 070 — SimpleCalendarDeleteEventsOnRelativeDay

交叉核对：已核对。本fixture Monday=Oct16已确认且已到；两Delete未forward，不再留Monday日期未知，后续确认成本未知。

### 目标与约束
公开goal删除this Monday全部事件；参考2023-10-15 Sunday UTC，本fixture已确认指Oct16，实际也到Oct16。原reward0、native failed；失败在Delete未forward，不是已选错Monday。

### 真实动作链与屏幕转换
1. `launch_app-1/3` 后仍launcher；`tap_on-4`进Calendar；`tap_on-6/8` Change view → Daily view，日头实际October15(Sun)。`events #39` / `tap_on-10` 裸More options失败，`tap_on-12`改accessibilityId才打开菜单；`tap_on-14` Go to date得到 **Oct / 15 / 2023** 三列滚轮。
2. `events #51` / `tap_on-16` 点visible text“16”（位于当前15的相邻滚轮项），动作passed但后图中选中日仍15；`tap_on-17` OK后的日头也仍October15(Sun)。这证明点击相邻文字不等于选择值提交。
3. `events #57` / `tap_on-19` 用top_right_arrow终于到October16(Mon)。图/XML列出两个事件：Review session for Budget Planning **00:00–01:00**、Review session for Project X **10:00–10:30**。这些标题仅是原trace公开UI观察，不是未来oracle答案。
4. `events #61` / `tap_on-21` 打开前一项；编辑页再次显示October16、00:00–01:00、该标题。此时已用完12次写额度；`#65/#67` / `tap_on-23/24` 两次Delete均在转发前被拒绝（audit **#45/#46**），`kill_app-25` audit#47也拒绝。编辑页保持原样，没有Delete确认框或列表移除。主summary称不能完成；verifier依据两个原有项+Delete未转发判failed。

### 首个偏离、直接失败、机制层级
- **事实**：`tap_on-10`首次target missing是无效locator成本；最关键的导航偏离是 `tap_on-16` passed后选中日未变却仍OK。之后已通过arrow正确到所选Monday，所以不能将整例简单归为“日期选错”。
- **事实**：直接失败是删除0项。两次Delete没有到native driver，不能写成“点了Delete但没有确认”；action_budget是紧邻失败边界，12次受理额度此前都消耗在入口、视图、重复导航和打开事件。
- **强推断**：在当前日Sun15、目标相邻Mon16的情况下，先切Daily后直接一个右箭头即可完成已观察到的日期转换；实际却加入失败More options和无效picker路径。主策略没有把剩余操作与完整删除事务所需动作联合规划，并在永久额度拒绝后重复尝试。
- **规划边界事实**：预规划最终目标写成“selected Monday's day view”，没有把this Monday的参考日期固化；本例尚无选错Monday证据，但未来验证必须同时验证日期身份与清空，而不是任一Monday为空即通过。
- **剩余未知**：Delete若获准后的确认/系列选项和终DB；Monday=Oct16已闭合，不能声称12写必无解或必要增加预算。

### 修复建议与未来验证
- **CR-70 / P1 / FSQ-skill+producer**：由当前UI日头和可信参考日期解析相对目标，明确记录绝对目标日及来源；在现有daily相邻日情形使用top_right_arrow、立即回读日头，避免进入不必要滚轮。依据 **S-Skill（14–18）、S-Locator（109–116）、S-Budget（85–142）**，对“passed但选中值不变”不推进，对永久action_budget拒绝不再重试。
- **P1 / FSQ主策略**：到目标日后以完整列表为事务对象，选择合适UI多选/逐项Delete并确认，保留有界余量给最终校验；不能只保证能打开第一个事件。用 `PN/fsq_worker.py` **193–197** 的Task构造与 `PromptModelBuilder.build_task_prompt` **65–95** 明确参考时间是任务上下文，不是标题oracle；若引入输入字段需双方端到端一致，不默改本轮结果。
- **边界/风险**：周起始/“this”语义不确定时不能擅删上一周Monday；不能把动作预算拒绝当可重试的设备卡顿；不得弱化破坏性确认。
- **未来验证计划（未执行）**：授权后覆盖参考日在周日/周一、UTC跨日及local展示变化、Monday含午夜/全天/多项、同名异日项，确认只删已解析目标日且所有项清空；保持12写动作。
- **已核对**：目标Monday=Oct16、所见两项未删除；后续确认成本/未留终DB不补测。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R070/sources/000-goal.txt`；原生链路：`R070/execution-result.json::steps[*].step_id/phase_reports`、`R070/events.jsonl::sequence/tool_arguments`；主结论：`R070/report.json::agent_output`、`E070/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E070/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E070/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R070/artifacts/screenshots/screenshot-agent-tap-on-14-finalize-after-action-1-b59da6b6b350.png`；相同阶段结构快照：`R070/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-14-finalize-after-action-1-f40c34350f2c.json`。
- 实际目视PNG：`R070/artifacts/screenshots/screenshot-agent-tap-on-19-finalize-after-action-1-dca836e35463.png`；相同阶段结构快照：`R070/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-19-finalize-after-action-1-1cce06b474af.json`。
- 实际目视PNG：`R070/artifacts/screenshots/screenshot-agent-tap-on-23-finalize-after-action-1-3363bd6ccba7.png`；相同阶段结构快照：`R070/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-23-finalize-after-action-1-99d6249bbed7.json`。

## 案例 071 — SimpleCalendarDeleteOneEvent

交叉核对：已核对。input25在forward前预算拒绝，不套074输入passed但值无效；fixture目标23:00–23:30不跨日，失败仍在导航/未删。

### 目标与约束
公开 goal 精确限定 **2023-10-24、23:00、Workshop on Project X** 三元组，只删除这个匹配事件；不是任意同名事件，也不是该日全部事件。原reward=0.0，native inconclusive。

### 真实动作链与屏幕转换
1. `launch_app-1 → tap_on-3` 进October月视图；`events #31/#35/#39` / `tap_on-5/7/9` 正确More options→Go to date→OK，但图/XML显示只有月/年picker，回到原月视图。`events #49` / `tap_on-11` target=24失败，后图无目标日事件列表。
2. `tap_on-13/15/17` 又一次More options→Go to date→OK，还是同一月份；之后 `events #77/#81` / `tap_on-19/21` 才 Change view→Daily view，日头为 **October15(Sun)**，列表是另一天的Catch up on Project X 07:00–07:45，不能因包含Project X就删除。
3. `events #85` / `tap_on-23` 点日头，终于打开三列picker **Oct / 15 / 2023**。`#89` / `input_text-25` 对 `//android.widget.EditText[@text='15']` 试图设24，但audit **#49 denied/action_budget**，没有调用到底层set_text；后图仍15。`kill_app-26` audit#50同拒绝。12/12写动作已在进入此picker前耗尽。
4. 全部动作中无event详情匹配、Delete或删除确认，最终是Oct15的日期picker；主summary=`Deletion was not completed or verified because the harness action budget was exhausted during date navigation.` verifier保留目标项是否不再出现的inconclusive。

### 首个偏离、直接失败、机制层级
- **事实**：首次明确偏离是 `tap_on-11` 在月视图用不存在的text=24；更早月年OK没选择日已暴露路线不足。正确日级picker被发现过晚。直接失败是没有执行删除且没有目标三元组前后状态。
- **事实**：本例 `input_text-25` 是**被拒绝、未执行**；与074“input_text passed但值不变”完全不同。不得用本例证明set_text坏，也不得说试写24后日期被错误重置15。
- **强推断**：月级和日级picker能力未建模造成重复路线，错误消耗写额度后才找到可行入口；主策略直到目标日已确认前仍不能开始破坏性动作。无同名错删证据，反而不应为了绕过失败去删当前Oct15的Project X事件。
- **已闭合/未知**：目标23:00–23:30不跨日；未到时间读取/删除，不猜23h换算错。终DB未知，不再保留本目标跨日候选。

### 修复建议与未来验证
- **CR-71 / P1 / FSQ-skill+主策略**：明确“精确删除”先从月视图切日视图，日picker修改目标值并回读 **Oct24/2023**，再打开候选详情同时验证title/date/start_time，三者全匹配才Delete；不使用标题模糊包含，也不使用month grid text猜点。来源 **S-Locator（109–116、356–381）、S-Skill（14–26）、S-Plan（预规划14–46）**；本例预规划三元组保留正确，修改应针对执行路径，不是放宽规格。
- **P2 / FSQ-runtime+producer**：在动作回执中传递剩余可写额度，策略对受理失败及时改用有日字段视图，拒绝后只整理既有证据，不重试Delete/teardown来消耗无用回合。来源 **S-Budget（85–142）**。
- **边界/风险**：23:00按目标显示时区解读，不替换为host时区；循环事件只删任务所指实例，不能删整系列；final absence必须在目标日/时间覆盖，而不是在Oct15看不到标题。
- **未来验证计划（未执行）**：获授权后覆盖同标题异日/异时、23:00跨午夜结束、月/日picker差异、剩余额度临界；确认只删除匹配对象并保留其它事件，保持12写动作。
- **给 harness owner 的逐例问题**：请确认原fixture三元组与官方后状态，区分“未执行删除”与“执行但识别错目标”。本例没有后者证据。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R071/sources/000-goal.txt`；原生链路：`R071/execution-result.json::steps[*].step_id/phase_reports`、`R071/events.jsonl::sequence/tool_arguments`；主结论：`R071/report.json::agent_output`、`E071/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E071/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E071/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R071/artifacts/screenshots/screenshot-agent-tap-on-3-finalize-after-action-1-ec8cce18716f.png`；相同阶段结构快照：`R071/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-3-finalize-after-action-1-b9d290b3bb48.json`。
- 实际目视PNG：`R071/artifacts/screenshots/screenshot-agent-tap-on-7-finalize-after-action-1-ed2ec33e772a.png`；相同阶段结构快照：`R071/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-7-finalize-after-action-1-d14773098e4f.json`。
- 实际目视PNG：`R071/artifacts/screenshots/screenshot-agent-tap-on-23-finalize-after-action-1-f150833008d9.png`；相同阶段结构快照：`R071/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-23-finalize-after-action-1-a8f5f9aa0d5f.json`。

## 案例 072 — SimpleCalendarEventOnDateAtTime

交叉核对：已核对。未到目标日；oracle预定相关时刻覆盖/端点title，并非动态读UI筛选，不将未执行at谓词当本轮算法错误。

### 目标与约束
公开 goal 问 **October27 2023 at 8:00pm**，只返回标题、多项逗号分隔；8:00pm应按设备日历时区转成20:00。公开文字“at”未自行规定严格start等于还是覆盖该时刻，不能在调查中用隐藏rubric补定义。原reward=0.0，native failed。

### 真实动作链与屏幕转换
1. `launch_app-1/3` 后launcher；`tap_on-4`进入October月视图，图上有密集蓝色事件块，XML没有日格或事件标题。`events #31/#35` / `tap_on-6/8` More options→Go to date，后图只有 **Oct/2023** 月年选择；`tap_on-10` OK没有任何27日或20:00确认。
2. `events #45/#49/#53` / `tap_on-12/14/16` 再次完整重复More options→Go to date→OK，仍同月视图；没有day字段、没有TimePicker、没有单项event详情。
3. `events #59` / `tap_on-18` 裸target=More options返回Target was not found；刷新结构后 `#65` / `tap_on-20` 用正确accessibilityId，但audit **#39 denied/action_budget**；`kill_app-21` audit#40同拒绝。10/10写额度耗尽，最后仍October月视图。
4. 主summary=`Unable to determine the event titles from the available calendar evidence.`，无标题输出；verifier failed是“提交说明而非titles-only”，不是发现20:00实际无事件。无model API异常、无deadline。

### 首个偏离、直接失败、机制层级
- **事实**：在第一次picker显示仅月/年之后，`tap_on-10` 直接OK没有日期级进展；第二组重复选择器是首个可证的无进展循环。没有尝试过8pm，故不能归咎12/24小时计算或时区。
- **事实**：直接失败是缺少目标日/时刻候选集合及标题答案；月视图XML缺标题不构成no-result，最终summary也没有声称无结果。
- **强推断**：主策略停留在月级控件并把正确的年份/月确认反复当作导航任务，缺少 `date confirmed → time coverage → exact titles → summary` 的检索证据链。S-Locator裸More options误用又消耗一次额度；预算拒绝是最后边界，不是第一因。
- **已闭合/未知**：官方用预定相关时刻覆盖/端点title集合，不在评分时动态读UI过滤。本例未到候选阶段，无谓词错误证据；模型可观察全集仍未覆盖，不把私有集合补交。

### 修复建议与未来验证
- **CR-72 / P1 / FSQ-skill+主策略**：在当前月级picker没有day时立刻使用Daily view的日字段路线，日头确认Oct27/2023后读取有时间范围的日列表，按公开goal的时刻语义找候选，必要时开详情保留起止时间、时区和完整title；覆盖不足时不宣称无结果。定位规则引用 **S-Observation（237–275）、S-Locator（356–381）、S-Skill（14–26）**。
- **CR-72-answer / P1 / FSQ-runtime+producer**：`PromptModelBuilder.build_task_prompt` **65–95** 与 `AgentFinalOutput` **39–50** 明确检索任务summary是用户答案载体，操作说明/evidence放其它已有字段；producer `select_main_answer` **22–57** 保持唯一主runner选择，不从verifier或私有fixture补答案。只有证据充分时输出titles-only，不能为格式强塞猜测标题。
- **边界/风险**：候选可能开始于20:00之前但仍在进行，不能在未明确语义时偷偷改成start==20:00；午夜/UTC本地日边界也要与屏幕一致。本例这些是未来验收边界，不是已确认根因。
- **未来验证计划（未执行）**：授权后覆盖20:00开始、覆盖20:00、相邻边界、同刻多项和空集，验证完整标题/逗号格式与summary提交，不加大10写动作。
- **给 harness owner 的逐例问题**：请确认“at”的既有官方定义和保留的UI/fixture时区；不得把本例未检索的集合当成未来答案告知模型。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R072/sources/000-goal.txt`；原生链路：`R072/execution-result.json::steps[*].step_id/phase_reports`、`R072/events.jsonl::sequence/tool_arguments`；主结论：`R072/report.json::agent_output`、`E072/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E072/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E072/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R072/artifacts/screenshots/screenshot-agent-tap-on-4-finalize-after-action-1-72047e06dec8.png`；相同阶段结构快照：`R072/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-4-finalize-after-action-1-964947dd032b.json`。
- 实际目视PNG：`R072/artifacts/screenshots/screenshot-agent-tap-on-8-finalize-after-action-1-511795471c68.png`；相同阶段结构快照：`R072/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-8-finalize-after-action-1-05dddd307dd8.json`。
- 实际目视PNG：`R072/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-a0e939274c2a.png`；相同阶段结构快照：`R072/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-a13579812236.json`。

## 案例 074 — SimpleCalendarEventsInTimeRange

交叉核对：已核对。input20 passed→after仍15→OK仍15→只走到18；底层提交分支未知，非overlap算法错。

### 目标与约束
公开 goal：**Friday 4:15pm–8pm** 的事件，标题-only、逗号分隔。参考为2023-10-15 Sunday UTC；本次策略试设 **20日**，与其后Friday一致，但最终实际只到Oct18 Wednesday。预规划把between解释为 **overlapping**；这比公开文字更具体，需记录而不预判官方等价。原reward=0.0，native failed。

### 真实动作链与屏幕转换
1. `launch_app-1 → tap_on-3` 进月视图；`events #31/#35` / `tap_on-5/7` 切Daily view。日头 **October15(Sun)**，当天列表有从凌晨到傍晚的若干项目；这不是目标Friday，不能用其中时间相似项回答。
2. `events #39` / `tap_on-9` 点top_value开三列 **Oct / 15 / 2023** picker。`#43` / `input_text-11` 用xpath `//android.widget.EditText[@text='15']` 输入20，**execution_status=passed**、audit **#21 attempted / #22 succeeded**。但before/after XML day字段均text=15，后截图居中值也仍 **15**；`#45` / `tap_on-12` OK后日头仍October15(Sun)。这是明确的动作回执/业务值不一致，不是被预算拒绝。
3. `events #49/#51/#53` / `tap_on-14/15/16` 连点top_right_arrow，各自后图依次 **October16(Mon) → October17(Tue) → October18(Wed)**。说明日导航正常，但策略从真实15开始逐日补救，未在入手时取得Friday。
4. 下一次 `events #57/#59` / `tap_on-18/19` 被audit **#35/#36 denied/action_budget**，`kill_app-20` #37同拒绝；10/10写动作已用完，最后仍Oct18。主summary无法确定，不是no events。没有执行16:15–20:00的候选筛选、没有目标Friday全日覆盖。

### 首个偏离、直接失败、机制层级
- **事实**：首个可证明的核心偏离为 `input_text-11` passed但NumberPicker值没变；按“工具passed”继续OK没有取得语义后置条件。S-Input **137–151** 正是write-only、不读回的实现。
- **强推断**：主策略至少通过后续箭头观察知道日期仍15，但选择了代价高的逐日追赶；未结合剩余额度改用已确认可用控件，也没有把NumberPicker编辑与提交确认作为一体。精确底层原因（uiautomator2 XPath set_text、控件焦点/校验、NumberPicker提交规则）**未知**，不能仅凭原生passed断言文字成功写入后被应用“重置”。
- **事实**：直接失败是没到Friday、未提供标题；action_budget是后果。日期早三天，时区/4:15转16:15计算未进入执行，不是已证明根因。
- **未知/分歧**：预规划 `verification_goal` 与key_actions明写overlapping；公开between可能有既存业务定义，但官方标量日志没有解释。不能为迁就推定分数擅自改overlap/within/start-only，也不能用该差异解释本轮未到Friday的失败。

### 修复建议与未来验证
- **CR-74 / P1 / FSQ-driver+skill**：`UiAutomator2AndroidDriver.input_text` **137–151** 对可安全读取且非secret的目标返回实际字段值，或由调用侧立即用现有ui_snapshot读回；NumberPicker路线显式区分滚轮当前选中值与相邻可见文字，要求确认值20及提交后日头Oct20才继续。仅修改`passed`文案无效，不能吞异常或简单重试。优先复用现有公开控件/有证据的滚动，不引入特定seed坐标。
- **CR-74-time / P1 / FSQ-预规划+主策略**：在 `agent/_pre_plan.py` **14–46** 避免将含糊between无告警地扩展为overlap，保留原始区间文字与可核对时间字段；主策略先取完整目标日列表，再应用经任务既有定义确认的区间谓词。`PromptModelBuilder.build_task_prompt` **65–95** 和 **S-Answer（39–50、select_main_answer22–57）** 将标题结果和执行说明分开，不以猜测空集应付预算终止。
- **边界/风险**：通用输入回读不要泄露密码/secret；text-based locator值变后不能用旧text=15查询判失败，应绑定原控件身份；不要自动删改事件或更改手机时间来跳Friday。
- **未来验证计划（未执行）**：授权后覆盖NumberPicker XPath输入passed却不提交、正常文本输入、手势滚轮提交、跨月Friday；时间窗口验证严格包含/相交边界及跨午夜项，先与harness确认既存语义；保持10写动作。
- **给 harness owner 的逐例问题**：请离线确认input_text后day仍15是否与底层保留日志一致；between的官方已有语义是什么？本轮不得因后者未确认而忽略前者的确定偏离。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R074/sources/000-goal.txt`；原生链路：`R074/execution-result.json::steps[*].step_id/phase_reports`、`R074/events.jsonl::sequence/tool_arguments`；主结论：`R074/report.json::agent_output`、`E074/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E074/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E074/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R074/artifacts/screenshots/screenshot-agent-tap-on-7-finalize-after-action-1-2ad61cf8e093.png`；相同阶段结构快照：`R074/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-7-finalize-after-action-1-de4f30b41651.json`。
- 实际目视PNG：`R074/artifacts/screenshots/screenshot-agent-tap-on-9-finalize-after-action-1-6c87919172ad.png`；相同阶段结构快照：`R074/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-9-finalize-after-action-1-e335f6047b0e.json`。
- 实际目视PNG：`R074/artifacts/screenshots/screenshot-agent-input-text-11-finalize-after-action-1-a25e0360dddb.png`；相同阶段结构快照：`R074/artifacts/ui-snapshots/ui_snapshot-agent-input-text-11-finalize-after-action-1-36c2641572eb.json`。
- 实际目视PNG：`R074/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-6fbfe38e2850.png`；相同阶段结构快照：`R074/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-efea53f3baa4.json`。
- 实际目视PNG：`R074/artifacts/screenshots/screenshot-agent-tap-on-16-finalize-after-action-1-6f1b09fae96e.png`；相同阶段结构快照：`R074/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-16-finalize-after-action-1-56e0f7751454.json`。

## 案例 076 — SimpleCalendarFirstEventAfterStartTime

交叉核对：已核对。修正版目标事件21:30至次日00:30已确认，开始日符合目标日，跨午夜结束不排除；失败在导航，未发生strictafter误算，不回填私有title。

### 目标与约束
公开 goal非常明确：只考虑 **2023-10-29本日00:00–23:59开始**的事件，找 **start严格大于21:00** 中最早开始时刻，并列时收全标题，titles-only逗号分隔。不得把恰好21:00的事件、21:00仍在进行但更早开始的事件、下一天凌晨事件算入。原reward=0.0，native failed。

### 真实动作链与屏幕转换
1. `launch_app-1/3` 后都launcher；`tap_on-4`进入October月视图，实际图有蓝色事件块，而XML只给顶栏/容器。`events #31` / `tap_on-6` 点top_value开仅Oct/2023的月年滚轮；`tap_on-8` OK回同月视图。
2. `events #43/#47/#51` / `tap_on-10/12/14` 又用More options→Go to date→OK，打开的仍是月年对话框，无day29。`#55` / `tap_on-16` 裸target=29，返回Target was not found；后图仍month，不是空日表。
3. `events #61` / `tap_on-18` More options打开菜单，`#65` / `tap_on-20` Go to date已被audit **#39 denied/action_budget**，`kill_app-21` #40同拒绝。10/10写动作，最后屏是overflow menu，未曾打开Oct29日列表或任何event详情。
4. 主summary=`Unable to determine the event titles from the available evidence.`；native verifier的failed指提交不是所需titles-only，未判定业务集合为空。没有21:00、23:59过滤或排序的执行证据，没有时区转换异常。

### 首个偏离、直接失败、机制层级
- **事实**：在已经确认Oct/2023后重复月年OK不选日期，`tap_on-16` 将自绘29当text节点而target missing，是第一处明确定位错误。后续菜单重入未解决日级入口。
- **事实**：直接失败是没有取得被查询日期的候选集合和答案；不是找不到严格大于21:00的事件。没有no-result画面，没有真实运算结果，不能归咎“把strictly after写成>=”或跨日21点长事件。
- **强推断**：月级/日级UI路径选择错误和不变状态反复操作耗尽预算。预规划在`report.json.task.key_actions/verification_goal`中完整保留了strictly after、当天上界、并列标题；本例不是预规划丢失数学谓词，而是主执行未抵达应用谓词的阶段。
- **未知**：本日候选/并列集合以及官方精确结果，无分项日志；不得直接把privateOutcome或fixture title当模型应答，也不能推测reward0是区间语义不一致。

### 修复建议与未来验证
- **CR-76 / P1 / FSQ-skill+主策略**：复用Daily view有day字段的picker，确认Oct29/2023后建立公开UI候选表 `(start_date, start_time, full_title)`；先按本日和 `21:00 < start <= 23:59`过滤，再取最小start，按这个最小值收齐全部并列项。缺少整日/尾段覆盖时不能返回空集或单条。引用 **S-Skill（14–26）、S-Locator（356–381）、S-Plan（14–46及145–201）**。
- **CR-76-answer / P1 / FSQ-runtime+producer**：在主执行输入/输出契约明确summary交付实际标题，其他字段记录过滤过程和证据；不把“最早”用单个`assert_visible(title)`代替。保持 **AgentFinalOutput39–50、PromptModelBuilder65–95、select_main_answer22–57** 的唯一答案出处，任何迁移需要双方共同端到端完成，不回填旧结果。
- **边界/风险**：不要按事件结束时刻排序；跨午夜结束但29日21点后开始的项是否符合看start而非end，次日开始不符合；不因排序/候选太多擅增操作额度。
- **未来验证计划（未执行）**：获授权后覆盖恰21:00、21:01、23:59、次日00:00、跨日结束、同最早时刻多项、真实空集；使用公开UI证据算集合，仍10写动作。
- **给 harness owner 的逐例问题**：请确认官方使用的当天/strict-after谓词与公开goal一致、检查原fixture是否有并列或跨日项；但不要将隐藏答案作为修复输入。本例确定失败在导航，未触及谓词。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R076/sources/000-goal.txt`；原生链路：`R076/execution-result.json::steps[*].step_id/phase_reports`、`R076/events.jsonl::sequence/tool_arguments`；主结论：`R076/report.json::agent_output`、`E076/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E076/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E076/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R076/artifacts/screenshots/screenshot-agent-tap-on-4-finalize-after-action-1-749387f35494.png`；相同阶段结构快照：`R076/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-4-finalize-after-action-1-ca4c4fd9dabe.json`。
- 实际目视PNG：`R076/artifacts/screenshots/screenshot-agent-tap-on-12-finalize-after-action-1-5ed1e69b909f.png`；相同阶段结构快照：`R076/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-12-finalize-after-action-1-9bb8dcf43bb9.json`。
- 实际目视PNG：`R076/artifacts/screenshots/screenshot-agent-tap-on-20-finalize-after-action-1-65473aa1029d.png`；相同阶段结构快照：`R076/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-20-finalize-after-action-1-0c4179caf2b1.json`。

## 案例 078 — SimpleCalendarNextEvent

交叉核对：已核对、有时钟capture保留。较充分候选已读但summary不答；clock text15:35/content-desc23:35并存，模型采用哪项未知，不把15点解释当已证唯一当前时间。

### 目标与约束
公开 goal问 **next upcoming event**，仅标题；若多项并列最早则逗号分隔。应先把“upcoming”锚定设备/fixture当前时刻，再验证所有更早候选被排除，不能把任意详情标题存在当作“下一项”。参考为2023-10-15T15:34Z，屏幕观察时钟15:34–15:37、日期Sun Oct15；不是2026 host现在。原reward=0.0，native failed。

### 真实动作链与屏幕转换
1. `launch_app-1`后launcher；`tap_on-3`开Calendar；`events #31/#35` / `tap_on-5/7` 切 **Simple event list**，是本组少有直接进入可读结构化agenda的路线。`tap_on-7`后图/树明确完整显示 **15 Sunday** 的Call with Marketing02:28、Review session for Project X04:01、Meeting with Dr.Smith08:32、Board meeting22:35–22:45、Appointment for Annual Report22:57–23:57，并已显示下一段 **16 Monday**。这些标题仅复述真实UI，非oracle提供；该页已经具有“早于当前时刻/未来候选”的强证据。
2. `events #41` / `swipe-9` 向下浏览到前一天尾部，再显示 **15 Sunday** 的同一完整序列及 **16 Monday**；这扩展了日期段覆盖。`#43` / `swipe-10` 从 `(530,1)` 向 `(530,1100)`（reference1080×2400），实际拉下 **系统通知/快捷设置**，而不是事件列表。后图可见Internet、Bluetooth、数据警告等；`press_key-12` Back才返回agenda。这一手势跨越app内容边界，消耗2个写动作（误拉+恢复）。
3. `events #65` / `tap_on-15` 打开Board meeting详情，后图/树 **Oct15、22:35→22:45、完整标题**；随后 `press_key-17`返回，再 `tap_on-19`打开**同一个**详情。`#83` / `assert_state-21`只检查event_title的resourceId+text，passed/invoke.exists=true，没有比较“是否earliest”。
4. 此时10/10写额度耗尽。`press_key-22/23`（events#85/#87，audit **#43/#44**）均action_budget拒绝；`ui_snapshot-24`仍同详情；`tap_on-25`按class ImageButton尝试返回也audit#47拒绝。`assert_state-26`再次相同title exists通过，既没有回到agenda也没有增加顺序证据；`kill_app-27`audit#50拒绝。
5. 主runner正常返回有效结构，但summary=`Could not conclusively determine the earliest upcoming event.`；其evidence只保留title存在、不足以排序的自述。独立verifier判failed理由是未交付title-only而不是“Board meeting不是下一项”。最终屏仍详情，非no-result。

### 首个偏离、直接失败、机制层级
- **事实**：第一处明确UI偏离是 `swipe-10`从status bar起手导致通知面板；不是设备断连/日历渲染坏。此前一次向下swipe可以理解为补足前日边界，不能一并归为无用动作。
- **事实/限定**：参考日完整agenda段与22:35详情均已读，比孤立title exists强；但clock text15:35与content-desc23:35并存，主模型采用哪项未知，不以当前15点唯一化并替其断言候选必为next。候选、时间来源冲突、覆盖边界没有组织成完成/未知判据；重复相同详情/exists不能补齐。
- **事实**：直接失败是summary没有标题答案。title存在两次通过不代表next查询成功；另一方面，预算耗尽后仍可使用既有完整观察，不要求为输出答案再强行返回列表。native verifier也没有否定候选本身。
- **剩余未知**：显示过滤/全量等价性、相冲突时钟字段的生成与主模型采用来源；未见明确时区错误但不能宣称所有时间字段一致。不把视觉候选升级为标准答案或替main补交；通用最终断言可能放大重复确认仅为推断。

### 修复建议与未来验证
- **CR-78 / P1 / FSQ-skill+主策略**：agenda检索保存按日期段的 `(date,start,title)` 候选表和覆盖边界，记录设备now及来源；目标日前后段头已覆盖、完整标题已读取、同刻并列已收齐后，使用这组已有证据完成排序并交付，不重复开同一详情/同一exists断言。手势限定到当前app列表bounds内部，禁止从status bar起点做列表滚动。对应 **S-Locator（tap_on109–116）、S-Skill（14–26）、S-Observation（237–275）、S-Budget（85–142）**。
- **CR-78-answer / P1 / FSQ-runtime+producer**：`PromptModelBuilder.build_task_prompt` **65–95** 显式说明IR summary是业务答案，不是自动化报告；`AgentFinalOutput` **39–50** 继续把计划/错误放已有其它字段，`select_main_answer` **22–57** 不改为拿verifier总结或evidence中的某个标题补答案。对证据充分的检索，不应因teardown不能成功而抹掉已知业务答案；真正覆盖不全时保持诚实，不为titles-only而猜测。
- **P1 / 联合边界**：相对时间上下文应明确出现在允许公开的Task输入/执行证据中，包含referenceTime/timezone而非私有title；next语义排序使用同一时钟，不能混用host时间。70的相对日也复用此机制。
- **边界/风险**：当前正进行中的事件与“下一次开始”不同，处理依据公开goal的既有定义；全天、循环、隐藏日历过滤与并列必须有覆盖证明，不能仅按列表第一个可见title。不要加预算让重复打开继续发生，也不要将cleanup动作拒绝当作读取结果不存在。
- **未来验证计划（未执行）**：授权后覆盖同日已过/未来、次日最早、同刻并列、当前进行中、全天/过滤设置、通知栏误手势恢复；验收summary严格title-only、候选证据可追踪，保持10写动作。
- **给 harness owner 的逐例问题**：请逐项核对已展示的15日完整候选段、参考时刻以及日历过滤是否足以证明最早性；请分开给出“候选排序对不对”和“main summary提交不对”两项意见。本例不能仅标预算耗尽，也不能把官方0解释成候选title错误。

### 本例原始证据定位（已读取/目视）
- 公开目标：`R078/sources/000-goal.txt`；原生链路：`R078/execution-result.json::steps[*].step_id/phase_reports`、`R078/events.jsonl::sequence/tool_arguments`；主结论：`R078/report.json::agent_output`、`E078/raw-private/fsq-native/worker/fsq-task-result.private.json::steps[tool_name=agent_runtime.runner].tool_output.summary`。
- 原预算：`E078/raw-private/fsq-native/worker/native-action-audit.jsonl`（本节audit序号）；初始化/评分/退出：`E078/raw-private/{task-initialization.json,evaluator-diagnostics.json,fsq-worker-outcome.json}`。
- 实际目视PNG：`R078/artifacts/screenshots/screenshot-agent-tap-on-7-finalize-after-action-1-afad34757997.png`；相同阶段结构快照：`R078/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-7-finalize-after-action-1-d034af47a797.json`。
- 实际目视PNG：`R078/artifacts/screenshots/screenshot-agent-swipe-10-finalize-after-action-1-e3451d1bc8ec.png`；相同阶段结构快照：`R078/artifacts/ui-snapshots/ui_snapshot-agent-swipe-10-finalize-after-action-1-aaf0aba80338.json`。
- 实际目视PNG：`R078/artifacts/screenshots/screenshot-agent-tap-on-19-finalize-after-action-1-57935c98dbf3.png`；相同阶段结构快照：`R078/artifacts/ui-snapshots/ui_snapshot-agent-tap-on-19-finalize-after-action-1-87ae66d96814.json`。


## 横向结论与待确认清单

1. **月视图不是空数据证据**：068/069/071/072/076均重复进入只有month/year的picker；没有一个抵达目标日事件集合。070已到所选Monday却没Delete获准，不能套用“都选错日期”。074独有 **input_text passed但day仍15**；071的同类input_text则根本被拒绝，不能混写。
2. **预算边界明确，根因不同**：068–078本组8例都在既定写额度耗尽后收到永久拒绝，观察/断言继续可用；budget的before-forward语义保留，不能靠重试或加预算掩盖无效导航。059/060无预算拒绝、无business deadline，不可归为同一类，也没有本组max_turns证据。
3. **破坏性事务没有发生**：069/071无Delete调用；070两次Delete均在forward前拒绝。本组没有已证明错删、整系列误删或丢失数据的案例；修复仍要保留日期身份/标题时间匹配与确认边界。
4. **音乐目标不同**：059是append queue及新增occurrence顺序，首个Add有toast成功正证据，后续可能意外播放导致队列改变仍属待查；不能把相对顺序断言当追加证明。060是空playlist，没形成duration候选表/求和/添加，不是“算错了45–50分钟”。
5. **IR真正交付路径**：068/072/074/076/078的main summary全是无法确定说明；出处valid≠答题正确；更不能用verifier.summary、隐藏fixture或evidence里的一首title事后替换。078已读到相对充分的日agenda和候选详情，却在重复确认/误拉通知栏后交付无法确定，必须将证据利用/完成判据与UI导航失败分开。
6. **时间/语义交叉核对**：请求/初始化/屏幕一致支持2023参考上下文，没有已证明时区漂移。070 this Monday和074 Friday的绝对日解释应由harness owner逐例核对；074预规划overlapping是可见的语义具体化，不等于已经证明错误；072 at的时刻语义、076明确strict-after/tie规则、078upcoming开始时刻的定义都必须沿用现有公开任务/评分契约，不能在报告中猜隐藏答案。
7. **源码归属清楚**：FSQ driver的click/set_text成功是低层调用成功，无日历/集合后置条件；FSQ skill/preplan/main策略负责业务不变量和停止条件；producer负责真实写额度与主summary出口；独立verifier是证据审核，不能代替修复动作或标准答案。现有冻结果不作任何回填。

十例均已收到harness owner逐例正式回执，分别记录事实一致、判据补实、契约冲突与剩余未知；正文原问题中未留存的终态/时钟/DB证据永久保留未知，不要求补测。所有图片从retained PNG离线解码目视，拼图仅驻内存；未运行build/lint/test/formatter或device/model/scoring。唯一新写入为本文。
