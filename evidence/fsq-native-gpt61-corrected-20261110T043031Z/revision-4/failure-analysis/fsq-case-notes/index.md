# r4：FSQ侧59例原生轨迹调查与修复计划

## 范围与证据等级

本记录是FSQ侧独立调查，不代替harness侧官方判据调查或最终联合报告。仅分析既有r4存量：逐例公开goal、main runner与独立verifier、events、execution、write审计、初始化、官方diagnostics、实际保留截图；结合与冻结manifest匹配的FSQ源码及harness owner逐例核对的冻结oracle。未操作设备、运行模型、安装、重评、改项目或改旧结果。所有修复与验证均是未来计划，非已实施。

- **事实**：原始动作/参数/回执、实际已查看像素、已匹配源码可直接支持。
- **强推断**：已知证据一致但没有评分瞬间状态、持久实体ID、完整wire prompt或反事实；不写成实测。
- **未知**：现存材料没有提供；保留到逐例，不用统一标签掩盖。
- **已核对**：双方逐例比对过的事实/判据及限定，不等于所有根因已证。各例正文中的核对状态和理由为准，不因slice已交付或agent idle自动升级。

原始分类仍为56例failed、2例passed（013/049）、1例invalid_evaluator（101）；failed中027/113原reward各0.5，不能抹成0。013/014/048/049的exact_main_summary问题只说明主输出契约异常：013/049原official1、014/048原official0全部保留，不重标invalid_agent。101原null/invalid_evaluator不改0。main runner、独立verifier、官方oracle三条结果线始终分开。

冻结FSQ package/source SHA256：`5ae6f139056ce10164f47fa2f91ec068fbdcdfe0235b2fcea821ad9ddc2c648d`。机制调查16个文件逐文件hash全部匹配，见[证据索引](../fsq-evidence-index.json)的`source_identity.mechanism_files`。额外tool artifact文件亦单独匹配。uiautomator2本地版本匹配但无冻结逐字节绑定，不把其推测当当次执行事实。

## 六份逐例正文

每例均给出目标约束、原动作/event/audit锚点、已查看画面、首偏离/直接失败/根机制分层、源码锚点、可实施修复、owner/优先级、边界/风险、未来验证和剩余未知。不是仅按应用/表象聚类。

| 正文 | 案例 | 数量 |
|---|---|---:|
| [核心契约、浏览器、剪贴板](core-contract-browser.md) | 002、003、004、013、014、048、049、101 | 8 |
| [媒体、联系人、Markor](media-contacts-markor.md) | 001、007、008、009、010、011、023、024、027、029、030、032、033、036 | 14 |
| [费用与配方](expense-recipes.md) | 015、016、017、019、046、047、050、052 | 8 |
| [Retro与Calendar](calendar-retro.md) | 059、060、068、069、070、071、072、074、076、078 | 10 |
| [短信、系统、导航](sms-system-navigation.md) | 040、041、044、081、082、084、085、086、097、098、113 | 11 |
| [运动与Tasks](sports-tasks.md) | 087、090、091、092、106、107、108、110 | 8 |

最终离线核对：六文件59个案例标题与原目标清单完全相等，逐组亦相等，无漏项或重复；59例均有双侧逐例正式回执，pending=0。七份Markdown中61个本地链接存在，590个原始输入引用存在；16个冻结机制文件hash匹配。仅验证调查产物与既有证据，不运行测试/设备/模型/评分。原case路径、预算和main状态见[case-inventory](../case-inventory.json)及[FSQ证据索引](../fsq-evidence-index.json)；缺评分瞬间值仍按各例永久unknown，不把已核对等同根因全证。

## 跨例修复顺序（必须以各例机制为前提）

| 优先级 | 修改落点与责任 | 针对的已见问题 | 边界与将来证明 |
|---|---|---|---|
| P0 | FSQ Android Skill/runner/verification；harness核对交接 | 浏览器002/003、Clock007/008/009、041、四SMS082/084/085/086及113实际kill所需应用，冲突于官方当前前台条件；kill致0/半分仍按主强推断 | 分离资源close与app_stop，保留末态；不能提前评分或kill后重开补分。未来验证完整native返回后的原判据，非kill前图 |
| P0/P1 | FSQ driver启动后置条件；producer+runtime公开预算交界 | launch passed而后图仍launcher；重复启动/图标恢复、菜单往返挤掉Save/Delete/确认 | 查清真实启动语义并报告ready状态；公开最大/剩余write及不可恢复拒绝，不增加预算、免费化动作或盲重试 |
| P1 | FSQ input_text工具契约、Skill、主策略 | 023/032把clear+set的replace-all当cursor插入；恢复耗费写额度 | 明确替换语义；完整合法原文+前缀一次写，或经设计的插入能力。长于50字的快照不可当完整原文，未来验证原文尾部不丢 |
| P0/P1 | FSQ主策略、preplan、历史证据工作表 | 多记录只做一条、漏掉曾见Pet Supplies、过滤/计数/去重未闭合全集、跨屏证据误当当前帧 | 保存候选身份、字段、来源、位置、覆盖边界和提交回执；保留exact-match安全标准，不title批删、不注入私有fixture答案 |
| P1 | FSQ tool artifacts、history budget filter、engine合法终结 | 013/014/048/049反复search/slice旧工件直至100turn EngineError，无主summary；并非write预算/外层deadline | 原生短结构化结果、已确认事实与cursor保留、同预算内有界进展与合法收尾；不能异常强转成功或verifier冒充main |
| P1 | FSQ preplan/verification | 003自造X持续可见条件，004只验输入框未Submit，027/113多目标压成最后子目标，097外观满替代exact max | 保留公开goal的状态转换、提交语义、合取和精确数值；不新增条件或降低判据，不泛化未经授权的支付/发送提交 |
| P0生命周期/诊断、P1证据 | FSQ与harness各守边界 | 四SMS发送UI已证，sent AND foreground+actual kill使前台冲突成为主强推断；001完整filename和101Clipper异常属独立链 | 原role/sentrow/activity/录音路径未留永久unknown，不补probe；不盲重发、不猜权限、不把UI ack当官方通过，101保持invalid/null |
| P1 | FSQ检索计划、主summary契约；producer共同端到端 | 日历/Tasks/Sports未交业务数值/标题，完成证明与局部exists混淆 | 全集/日期/类别/精度证据充分后summary输出用户要求的值；不从verifier/evidence/私有答案事后补交，不因format有效就判业务正确 |

## 必须保留的逐例差异与纠正

- **007实质修正**：冻结clock.py明确清data后初始化paused00。00/Start是合法设计，不是precondition mismatch或预检破坏证据。Start→Pause是不必要往返、不是0的充分原因；007/008/009官方均检查当前DeskClock UI，不读原会话、service或内部timer实例。actual Clock kill已核对，评分瞬间UI未留存。
- **003**：路线已经到Success；FSQ新增网格/X必须持续可见导致自身否决，official0与后续Chrome kill是另一条链。
- **014/048**：014局部no不能证明全文件no；048至少一条完整10mins正例早已在artifact中，不可写全部看不清。
- **019/033/044/046/047/052/059/060/036**：无预算拒绝/硬deadline迫停者不能因模型execution window/time limit自述归成超时；分别保留漏项、空合并文件、未保存路线、只录一条、未解析候选、队列完整列表、空playlist和媒体时序机制。
- **050/052**：050已完整比较两副本但未删除；052正确保留三条不同Avocado，却没继续其它候选。安全不误删与任务未完成并存。
- **097/098**：097近max不能证明exact max；098初态已max却被无必要写入拖低。UI0..65535与system0..255不可直接混同或猜换算。
- **106/108/110**：106完成日不等due日，未实际执行出错过滤；108年份核对有价值，跨屏完整XML与当前帧裁切并存，不写AI误判；110By priority是真实有效步骤，不应禁sort。
- **090/091/092**：MAX/SUM计算未执行，不虚构算错；两位mi精度是未来未闭合约束，一条30min不能充全周总和，也不是30秒。
- **059正式冲突**：oracle完整playing_queue title列表==5expected，并非suffix/delta；原noise/重复充分失败。非空用户队列只追加可符合公开add语义但不保证该oracle通过，不能擅清queue凑分，init未清亦不坐实跨题污染。
- **030/033/036**：030官方ls -ll -au时间列不等UI Last modified/ctime、候选最新未知；033严格完整路径、默认.md及两个空行形成5行是独立缺口；036不同capture的05s/7.9s不拼同帧或主失败。
- **070/071/076/078**：Monday=Oct16已确认；071目标23:00–23:30不跨日且input被拒；076目标事件21:30至次日00:30不违开始日范围；078 text15:35/content-desc23:35并存，模型取何来源未知。
- **082/084/085/086**：发送链各自已证，actual kill目标SMS且oracle sent AND foreground；前台冲突为主强推断。recency/Oscar来源绑定只属业务/main-verifier层，非额外评分谓词；47.604/34.374/50.869/40.386s排执行>5min，不代provider.date/device now。

## 未决证据与责任边界

评分瞬间activity/forest、最终provider/SQLite行、录音完整路径、Markor自动保存字节、同名新旧recipe持久ID、完整wire prompt、未覆盖列表尾部等缺口分别保留在对应案例；没有留存就不声称取得。官方既有判据由harness owner负责确认，FSQ负责原生动作与证据生产/主决策/Skill/验证语义；跨项目输入预算、参考时间与终态清理契约由双方共同定义。所有未来实现仍需用户授权的项目开发流程，本轮只有调查记录。
