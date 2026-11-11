# 原r12v2 060 RetroPlaylistDuration：离线独立复核

## 终端结论

**实际评分是RetroPlaylistDuration自己的duration scorer，不是父类verify_playlist。** 它读取所有非空playlist的JOIN行；任一行playlist_name不等于目标名就返回False，然后累计返回行的duration_ms，检查45–50分钟闭区间。没有固定10/12首、标题/顺序、files/noise成员检查，也不是先过滤目标列表后只计目标时长。

原UI确实读到目标列表`12 Songs • 01:01:13`，超过50分钟673秒；但12首本身不构成失败条件。原10/12首决策有未测时长的估算，不能从数量推断当时总时长，尤其不能认定cell20的10首已经越界。

旧review有明确错误：cell19只截图，没有返回页面；cell27是首次**非空**总时长回读，此前已有空表0 Songs/00:00；原raw最终incomplete是cleanup阶段声明，normalized.finalText仍为null、agentCompleted=false。它没有假称成功，但不能把cleanup prose写成业务final已被Harness采纳；本任务判分不使用final文本，因此null也不是直接零分解释。

本轮仅离线诊断与通用建议；未改父review/proposal、正式skill、Runtime或安装，未启动设备/服务/会话、未读DB、未初始化/重跑。没有新官方分数，不推进下一项。

## 原身份与来源

原attempt：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/060-RetroPlaylistDuration/attempt-1/`。

- index60、seed217200551、paramsTransport=JSON；params SHA256 `dcd892c246b616e950a794dd086315709257ad98fcc14d0242fc94825464b308`；complexity3，maxSteps30。原manifest参数与result逐对象一致，未重新生成。
- goal：`Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.`
- 原result SHA `86680b468b5ad8acf7579acdde5e9f162da4215d44860789d8d3f1799c05eca9`；normalized `e0ad3a096a2861a8b64c766e3d662f824160050ea54aa39b4e30a010068bede8`；raw `ea36ded95cc560202ccb49d679d5fe79b87fa67f262fef19dd67d13e44b31314`。
- 原30/30动作、30 reference steps；29次python_exec，25 completed/4 failed（2、12、21、28），全部Kernel alive，无AMKernel timed_out。动作构成为23 click、4 actions、2 input、1 back。原reward0.0，error/invalidReason均null；termination=step_budget，cleanupRequested=true，业务时钟尚有约1584秒。
- 原quit成功并核实session absent，task teardown与environment close完成。agentFinished与agentCompleted不是同一字段；原agentCompleted=false，normalized.finalText=null。

owner独立重算三原hash，并核对父保存的29份请求code SHA与原result一致；原完整toolCallId/arguments/response join、thinking摘要与图片由p2独立复核，owner不冒领其署名。

## 实际安装身份及initialize

本轮实际导入 `.venv/lib/python3.11/site-packages/android_world/task_evals/single/retro_music.py`、`common_validators/sqlite_validators.py`、`utils/sqlite_schema_utils.py`、`utils/fuzzy_match_lib.py`；4文件SHA均与AndroidWorld0.1.0的安装distribution RECORD一致。原result记录AndroidWorld revision55ddaf5edc6f6c25673aed343907d5b9dca66f84。当前文件/RECORD核对不冒充原完整安装树快照。

实际方法身份：

- `RetroPlaylistDuration.initialize_task`，retro_music.py:260–284。
- `RetroPlaylistDuration.is_successful`，286–293。
- 父类`RetroCreatePlaylist.is_successful`，162–170，才调用`sqlite_validators.verify_playlist`；被子类覆盖，本任务不走该路径。

initialize本类没有调用super.initialize_task：先以`_clear_playlist_dbs`清PlaylistEntity/SongEntity表，再写入files组和noise_files组媒体，最后扫描Music目录并关闭应用以刷新。不能把父类147–160的统一3–5分钟生成逻辑套到子类。这个覆盖方法本身不调用父类clear_internal_storage；写入15个指定文件不等于历史全音乐库只有15首。本轮不以此额外猜测污染或零分原因。

## 10 files与5 noise的生成差异——仅离线隐藏契约分析

这两组是冻结参数和生成源码中的内部分类，**不是原Agent已知分组或答案**。原goal不披露分组、单曲时长或“该选哪十首”；不得把这里的隐藏知识交给执行Agent。

- files共有10个：`_generate_list_with_sum(2850000,10)`生成10段毫秒时长，数学和为2,850,000ms（47.5分钟）。236–243行在0..n选9个随机切点、排序、插入0/n，再取相邻差。每段非负，**并不保证单曲3–5分钟**。
- noise_files共有5个且与files不重合：每首调用random.randint，输入duration在180,000–300,000ms（3–5分钟，含端点）。五首请求值合计范围900,000–1,500,000ms。
- 本轮未用原seed重造参数或历史逐曲时长。仅用真实generator代码和一个新的独立RNG(0)作合成纯执行例；官方模块与共享RNG状态未改。该例10段和仍2850000，最小39136、最大916172ms，说明不能假设统一3–5分钟。它不是原seed217200551的分配。
- `_create_test_mp3`把请求时长交给pydub silent并export MP3；本轮没有编码、读媒体或检查MediaStore/DB。请求值、实际编码/扫描时长和UI格式化时长不混为一谈。
- “选中10首”不等于“选中隐藏files十首”；“选入noise”本身也不是Duration评分禁止的动作。实际predicate不检查成员集合。不能凭隐藏分组把原问题改造成直接选择参考列表。

详见`owner-generation-analysis.json`与`owner-installed-pure-predicate-smoke.json`。

## 官方到底检查哪些字段、哪些列表

### 本任务的duration评分

`_get_playlist_info_query:41–59`从PlaylistEntity JOIN SongEntity取：playlist_name、歌曲title、duration_ms、按playlist_name分区/song_key排序的order_in_playlist。**没有目标名WHERE条件**。innerJOIN不会返回没有歌曲的空列表；它也不返回playlist_id。

`RetroPlaylistDuration.is_successful:286–293`：

1. 读取上述所有返回行。
2. 每行playlist_name必须与params中的目标名精确相等；遇到其他名称立即False，不是跳过它。
3. 累加返回行duration_ms。
4. 仅以`2700000 <= total_ms <= 3000000`返回float结果。

因此：

- 确实检查：每行列表名精确匹配，以及总毫秒时长闭区间。
- 不检查：固定曲数、歌曲标题、顺序、必须选files全集、排除noise、final中的成功声明。
- 对象隔离不是“只验证目标而忽略其他列表”：任何返回的其他非空列表行都可导致False。其他空列表无JOIN行，不能仅凭存在一个空列表就声称它导致失败。
- query及PlaylistInfo没有playlist_id，只有同名行无法区分概念上的不同列表对象，会合计。纯行例验证了这个能力边界，**未验证应用允许同名对象、也未证明原现场存在它们**。
- 原DB/query rows未保存；不能据此把foreign-list门或同名聚合写成原实际零分原因。

### 父类的verify_playlist：对照，而非本任务判分

`sqlite_validators.py:30–70`：按fuzzy且忽略大小写的列表名统计匹配行；匹配行数必须等于candidate_files长度；每个candidate标题须精确相等且order_in_playlist等于候选索引。不比较duration_ms，非匹配名称的行被忽略。

这是另一套名称、曲数、标题、顺序契约；不能用它宣称本任务“必须10首且按隐藏files顺序”，也不能用它的对象过滤语义描述Duration。

## 无设备实际纯执行证据

只执行真实安装`verify_playlist`，以及从真实Duration scorer AST提取的无I/O核心：移除第一句DB读取，把目标名参数化，其余循环/比较/return保留。使用合成PlaylistInfo对象，不fake env，不调用完整initialize/is_successful，不读SQLite，结果不是新官方分数。

| Duration受控输入 | 纯核心返回 |
|---|---|
| 空JOIN结果 | 0.0 |
| 目标名精确，2,700,000或3,000,000ms | 1.0 |
| 比下界少1ms，或比上界多1ms | 0.0 |
| 1条任意标题/任意顺序，合计47.5分钟 | 1.0 |
| 12条合成行，合计47.5分钟 | 1.0 |
| 把原UI61:13作为同名总时长的条件行 | 0.0 |
| 合格目标行加其他列表0ms行 | False |
| 仅改变目标列表名大小写 | False |
| 两组概念上不同但同名的合成行，总47.5分钟 | 1.0 |

12行例只证明曲数不是predicate条件，不证明原音乐库存在可行12首组合。UI61:13例是条件机制，不替换原判分输入。

实际verify_playlist对照：0ms仍可通过标题/顺序校验；其他名称列表行被忽略；仅改列表名大小写仍可通过；标题大小写或顺序错误失败；匹配行数不符失败。完整行、结果与源hash见`owner-installed-pure-predicate-smoke.json`。

## 原证据与旧review说法审计

父文件`per-task-review/060-RetroPlaylistDuration/review.md`保持只读；另署名审计见`owner-old-review-claim-audit.json`。

### 1. 10/12首是估算，不是测量，也不是官方固定曲数

父/p2原raw复核指出下列为**记录的thinking摘要（summary=true）**，不冒充完整内心推理或测量：

- 1905：曾计划先查单曲时长。
- 4697：已先设约12首目标；因此旧review把5282/cell20称为最早偏离，范围过窄。
- 5280：说10首约38–42分钟、12首约46分钟，承认durations vary/needcheck，但没有观测时长支撑。
- 6225：猜14首约55分钟，追加Return/Silent两首到12。
- 7206：知道可能没有预算修正，仍期待12首合格。不能把此摘要写成它已经知道真实61:13。

3050附近还出现过“编号45–50歌曲”的误释摘要，但没有据此执行该任务语义，不能将其夸大成实际动作根因。

原cell20确实从1选中批点9个标题到10，cell25追加2首到12。**无法从当时留存的时长证据证明10首已经超过50分钟**；因此旧review第7/44/45行“错误总时长在10首时已形成/追加2首扩大已超限状态”是过强因果表述。可以确认的是未验证聚合贡献就扩大选择，以及cell27最终非空回读超范围。

### 2. cell19没有返回页面

原cell19 start4762/end4764（tool result message4766）的代码只有`display(driver.get_screenshot_as_png(), mime_type='image/png')`，没有导航mutation。p2从原base64离线解码并核对SHA的图显示Songs、1 selected、Beyond the Horizon选中，无单曲/选中总时长。旧review第39行“回到播放列表页”错误。

首个长按选中标题现在可由该图确认，不再像旧第71行那样称完全未知。**最终playlist完整标题列表仍没有逐项独立读回的DB证据**，不可把动作请求集合替代最终数据库集合。

### 3. “第一次时长”必须限定非空

- 原cell11 start2813/end2814已经回读`0 Songs • 00:00`，cell14 start3645/end3646又回读空表总时长。
- p2核对5张原图：9创建菜单；15延迟取图显示空表、无弹窗；16空表菜单；19歌曲选择1 selected；25歌曲12 selected菜单。19/25无可用单曲或选中聚合时长，状态栏15:46不是歌曲时长。
- 原cell27 start7207/end7208返回目标名和`12 Songs • 01:01:13`，是首次**非空**聚合回读。旧第7/46/55行不能无条件写成第一次任何时长观察。

该UI值为3673秒，不在2700–3000秒内，超上界673秒。这足以否定观察时的业务后置条件，但不是原官方DB毫秒值dump，不能唯一锁定历史评分分支。

### 4. 预算、原final与指令送达分层

原动作账30/30已满；cell28尝试第31次打开列表被step-budget拒绝，修正未执行。cell12在点击前定位失败，cell21在perform前TypeError，均不能解释成动作已生效或驱动不可用。原4个failed均Kernel alive；最终quit成功。

原raw7717的incomplete与超限UI一致，没有错误宣告完成；但原normalized.finalText=null、agentCompleted=false，不能称业务final已采纳。原steer记录7213、实时liveSteered=0、后续真正user入队7479/下一turn交付须分开：不因日志先有steer就断言模型在7472发请求时主观故意违反已收到指令。此处具体事件join由p2独立署名。

本任务是DB状态评分，非IR答案提交任务；业务final为空不自动产生该0分。没有原query rows/分支trace，不能把预算拒绝、final捕获或对象范围门替换成唯一历史零因。

## 泛化建议候选与统一fix边界

详见`owner-generic-suggestions.json`，仅建议，不改父proposal或正式skill：

1. **聚合目标用聚合证据控制批量。** 单曲数、selected数、空列表0不能推出加入后的总时长；需要已观测增量/可靠反馈，不能把平均值猜测当已验证输入。证据不足时缩小提交、报告不确定或停止依赖，不能只“先读当前0再大批选”。
2. **区分选择成功与业务成功，保留验证/修正余量。** 成功选中10/12不等于总时长在区间；但不能承诺某条未验证路线能在30步完成，也不增加预算或重试。
3. **以当前可见上下文验证控件/页面。** 截图动作不是导航；延迟图片不保证反映紧前的短暂弹窗；不能把状态栏时钟当媒体时长。
4. **准确描述生命周期。** raw cleanup声明、Harness business final、worker finished、任务完成是不同证据；预算拒绝与实际送达的指令也应分时点，不制造故意违规归因。
5. **测评契约审计独立于Agent策略。** Duration全JOIN名称硬门与父类verify对象过滤有差异；后续若讨论修改评测范围，须另行决定新契约，不改冻结0分，不将隐藏文件组或源码答案泄露给Agent。

不能声称“现有技能没有任何可靠方式获取时长”：本轮仅证明特定已观察页面/图片没有该值，未穷尽应用所有正常UI路线。也不声称某条新规则已证明通用收益或能保证提分。统一fix留待后续授权。

## 交付与限制

原playlist DB、actual query rows、原逐曲真实时长及原确切评分分支没有持久化证据供本slice恢复；本轮不补现场，也不把合成对象当历史。

owner五文件为本报告、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`。owner前缀文件保存源码、纯执行、生成差异、旧说法审计与建议；p2独立原raw/图片/动作账另署名，互不覆盖。最终SHA见`owner-final-delivery.json`。本轮是离线诊断与建议事实交付，不是fix验收。
