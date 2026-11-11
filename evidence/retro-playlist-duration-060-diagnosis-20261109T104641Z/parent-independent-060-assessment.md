# 060：父级独立复核与通用优化候选

署名：AMKernel 父级 Agent（herdr w3:p1）。本轮只读离线诊断；不修改父级 `per-task-review/060-RetroPlaylistDuration/review.md` 或整体 proposal。不是正式技能修复、现场重跑或新评分。

## 结论

主要问题是模型用歌曲数量估算总时长，技能指导可以补强聚合约束的证据边界；没有证实 AMKernel Runtime/MCP 执行故障导致本项失败。批量操作不是问题本身，缺少的是批量决策所依赖的实际数值证据，以及仍可验证和修正的预算安排。

本项为创建指定名称、总时长 45–50 分钟的播放列表，不是查询总时长。原记录为 30/30 个 UI 动作、29 次 Python 调用、官方 reward=0、termination=step_budget。不是 r12 旧冻结协议的新成绩。

## 独立原始证据

身份：index=60，seed=217200551，paramsSha256=`dcd892c246b616e950a794dd086315709257ad98fcc14d0242fc94825464b308`。父级独立按完整 toolCallId join 了全部 29 次调用；每次代码与原 result 的 codeSha256 一致，tool_execution_end 与 message_end/toolResult 的 JSON 响应逐一相同。

|原始锚点|观察|支持的判断|
|---|---|---|
|raw1905，记录的 thinking summary|原计划先查歌曲时长，再选合适子集|Agent 起初知道应取得时长；不是任务要求完全缺失|
|raw4697，记录的 thinking summary|先设约 12 首的选择目标|最早明确的无实测时长数量假设；不是已经观察到 12 首合格|
|exec19，call4760/end4764/result4766|代码只有截图；原图是 Songs、1 selected，Beyond the Horizon 灰色选中；无单曲或选中总时长|没有返回播放列表页，也没有图像时长证据支撑后续估算|
|raw5280，记录的 thinking summary；exec20，call5279/end5282/result5284|估计 12 首约46分钟、10首约38–42分钟；随后批量加选9项，读到10 selected|把未经验证的平均时长假设用于实际选择；不能把选中数当作总时长|
|raw6225，记录的 thinking summary；exec25，call6397/end6401/result6403|猜14首约55分钟，追加两首；原图12 selected，菜单无时长|不是读到10首实际总时长后再决定追加|
|exec27，call7205/end7208/result7210|`12 Songs • 01:01:13`|首次记录到非空播放列表总时长；3673秒，比3000秒上界多673秒|
|raw7213|预算控制进入 steering 队列，liveSteered=0|不能说控制消息已经被模型接收|
|exec28，call7469/end7472/result7474；raw7478/7479|修正前的打开列表动作被拒；随后控制消息才作为 user 消息进入流|无成功修正；不能据此指控模型明知禁止还继续 mutation|
|exec29，call7553/end7556/result7558；raw7717|原会话 quit 返回；清理阶段文本明确 incomplete|诚实承认未满足任务；不是正常业务完成或 normalized finalText|

以上思考证据明确为保存的 summary=true 文本，不冒充完整内在推理。exec11 已显示空列表 `0 Songs • 00:00`，exec14 也有空列表时长；因此不能笼统写“exec27 才第一次看到任何时长”。

exec20的10首没有实测聚合值，不能说此时已经超过50分钟；exec25追加两首也不能写成“扩大已经确认的超时长状态”。已证实的是选择依据缺失，决定性的超界观察在exec27。

29 次调用为25 completed、4 failed：exec2 缺少可选 lxml、exec12 NoSuchElementException、exec21 不受支持的 duration 参数、exec28 预算拒绝。全部响应报告 kernelState=alive。UI 动作为23 click、4 actions、2 input、1 back；前三个失败发生在提交相应 UI 动作前，不能把它们算成额外消耗的 UI 配额。

原始 normalized.finalText=null、agentCompleted=false；raw7717 是预算关闭后清理阶段的 incomplete 声明。原结果还记录 owned session absent、activeSessionCount=0、taskTearDown=completed。这里陈述的是历史清理证据，不是本轮对当前共享服务/session 状态的核验。

## 评分契约分层

实际安装的 `RetroPlaylistDuration.is_successful:286–293` 覆盖父类，未调用 `verify_playlist`。它对所有 JOIN 返回行检查 playlist_name 精确等于目标，然后累计 duration_ms，使用闭区间 [2700000,3000000]。不检查歌曲标题、顺序、首数或隐藏 files/noise 成员身份。

owner 的实际源码 AST 纯核心与真实 verify_playlist 合成行证据已读：上下界均通过、±1ms 边界正确；控制总量47.5分钟时1行和12行均可通过。这只证明首数不决定评分，不证明原设备存在对应可用组合，也不是原 evaluator 运行。不能把隐藏10个files作为执行答案，更不能建议固定选10首。

对象边界另外记录：任一其他名称 JOIN 行会使本评分早返失败，而不是先筛选目标；空列表没有 JOIN 行；同名概念对象可能被累计。这与父类 verify_playlist 的过滤、标题和顺序语义不同。未恢复原评分实际输入，不能断言本次存在 foreign-name 行或同名对象问题，也不能指导 Agent 为迎合评分删除无关列表。单曲生成属性仅为隐藏评测审计，不向执行 Agent 提供曲目或答案。

## 后续通用技能候选（未实施）

1. **聚合目标按数值证据决策。** 任务要求总时长、总金额或容量区间时，区分对象数量、单项属性和聚合值；没有可靠数值证据，不能用习惯平均值替代。已知空列表总值0并不揭示任何单曲的增量，不能据此认定后续批量安全。先寻找任务允许且实际可获得的属性或建立可安全调整的聚合反馈；若当前页面不提供，明确缺口，不假定存在 API 或解析器。
2. **保留批量，但设置业务依赖边界。** 有可靠单项属性时可在一次 Python 调用内批量观察、计算候选、选择并验收；只能读取容器聚合值而增量未知时，仅在可安全调整且预算允许的条件下小批提交、读回实际增量，再决定下一批。不可逆操作不能套用试错反馈。未知值不能冒充已满足前提，不机械要求每点一下都返回模型。
3. **预算计算包括验证和必要修正。** UI 动作与 Python 调用不是同一计数。规划时计入进入详情、读取所需状态、提交和可能调整的交互成本；不要在耗尽全部变更动作后才第一次获得非空业务总值。这不是增加预算、额外重试或保证能在原预算内完成。
4. **聚合验收绑定正确对象。** 总值应来自目标容器与当前状态；选择模式数量、全页面零散文本、HTTP 200 都不能代替目标对象的聚合后置条件。错误后先核实已有结果，不为满足评分清理无关对象。
5. **不足就如实停止。** 未取得必要属性或无法安全修正时报告已完成部分与未满足条件。原执行清理阶段诚实报告 incomplete 的行为应保留，不能用措辞优化伪装成功。

这属于共享 Appium 技能中业务后置条件、批量反馈边界和预算意识的最小澄清候选，不新增播放列表专用 Runtime API、不硬编码菜单路线/曲目数/标题。尚未证明模型会遵循或成绩会提升；真实应用中的可行取时长路径及原30动作内完成能力仍未验证。

## 证据入口与边界

- [父级29调用独立join及源文件只读收据](parent-independent-raw-receipt.json)
- [owner评分源码身份与契约证据](owner-scorer-source-proof.json)
- [owner真实pure/AST合成边界证据](owner-installed-pure-predicate-smoke.json)
- [p2原始cell19截图](independent-060-cell19-original.png)、[p2原始cell25截图](independent-060-cell25-original.png)：父级已直接读图核对；图像来自历史raw，不是本轮截图。

本轮没有设备/服务/会话/DB/环境初始化/执行回放/正式技能或Runtime修改/build/tests；没有新官方结果，没有全量测评。父级060旧文档和整体proposal保持原样，错误说法在本文件另署名纠正。未来正式fix仍须独立同协议Agent现场样本、原成功样本回归和session清理证明，不能用本轮离线诊断代替。
