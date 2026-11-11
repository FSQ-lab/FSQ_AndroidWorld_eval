# 主runner契约异常与阶段停止偏差

## 结论与责任

四项原错误均为 `Agent exceeded the configured turn limit.`，不是business timeout、写额度耗尽或笼统异常。013/049官方通过1分；014/048官方失败0分。`exact_main_summary`标记主输出生产契约失败，不把已有官方分改成invalid。

**调度存在真实指令/实现偏差。** 之前助手承诺“遇任何invalid立即failclosed停止”，而冻结驱动只对cleanup/forced/evidence/global drift的列举条件停；`invalid_evaluator`和`exact_main_summary`没有进入halt谓词。应明确承认，而不是以最终qualified=false冒充当时已经停止。

源码已按candidate manifest绑定：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/src/fsq_androidworld_eval/fsq_campaign.py`，SHA256 `fe0b3280562b2801b3faca509e34b4a98db79c247ebfe41bbaaba5bab57e3210`。本调查没有改该代码。

## 四例（唯一案例不重复计数）

| index | 原官方身份 | 原生错误与动作额度 | 真实业务差距与循环 |
|---|---|---|---|
| 013 | passed / 1.0 | max_turns；46/60，denied=0，非deadline | 已录三笔并被官方判1；业务完成后没有主summary；read_artifact_slice=23 |
| 014 | failed / 0.0 | max_turns；12/60，denied=0，非deadline | 无任何新增；局部no→全覆盖无证；反复search未推进；search_artifact=55 |
| 048 | failed / 0.0 | max_turns；9/60，denied=0，非deadline | 首artifact已有合格完整候选但没有打开Broccoli录入；反复slice；read_artifact_slice=81 |
| 049 | passed / 1.0 | max_turns；18/24，denied=0，非deadline | 菜谱保存并逐字段验证、官方1；后反复读已过断言；read_artifact_slice=66 |

计数口径：13/49同时属于passed与main异常，14/48原已在failed集合；59唯一案例不是把4例再加一次。主runner错误和verifier的独立success/failed/inconclusive不可互换。

## 机制、边界及未来修改点

- FSQ `agent_engine/_runner.py:141–174` 达100turn直接EngineError；`adapters/coding_agent/_runtime.py:343–375`保留失败而不产出AgentFinalOutput；这是既存错误路径，不应伪造完成。
- FSQ `tools/_tool_artifacts.py:23–45,51–95`按转义原文切片/搜索；`_ToolOutputBudgetFilter:93–115`历史大输出淘汰与缺失稳定候选/断言账本共同诱发循环是强推断。未保存完整wire prompt，不能写成唯一已证内部根因。
- **FSQ P1**：短结构化投影及字段定位、带artifact身份与cursor的进度记忆、区分局部无匹配/全覆盖、在既有100turn内预留合法终结机会。必要重读不能被一刀切拒绝；不能加预算、自动重跑、异常转成功、verifier冒充main。
- **Harness P0**：把“停止条件”与operational validation对齐。先把用户已要求的任何invalid及exact-main契约破坏明确定义为阶段停止；在写入原episode record、等待owned cleanup证明后记录stage_halted，禁止下一spawn。普通业务failed0/partial继续，不篡改原分类/评分。
- **Harness P0**：若需要人工题间停止，提供独立显式stop请求，不靠改授权/manifest制造漂移或杀不明进程。停止是控制事件，不是假装identity错误。只列未来方案，本轮没有新增控制功能。

## 原停止条件与实际后果

- `fsq_campaign.py:204–220`只看cleanup、worker/outer forced、evidenceFailure及四种global invalid；不含invalid_evaluator。
- `:276–283`识别mainAnswer非valid，加入exact_main_summary；`:867–880`计算operationalErrors并保存attempt，但halt只调用halt_reason(record)，没有使用errors。
- `:834–846`题间静态检查只发现真实identity/authorization/租约问题，不是通用正常cancel接口。
- `:882–891`最终qualified会因operationalErrors为false，exit2；这只是结尾失格，不能抹去中间继续消费后题的事实。
- 原101 invalid_evaluator后102..115继续；四项main异常也未暂停。若严格将main契约失败列为invalid，则最早应在013后停止，不能只说101之后多跑了14题。

## 未执行的未来验证矩阵

| 输入边界 | 要求的可观测行为 |
|---|---|
| 普通failed/0或partial/0.5且所有操作契约有效、cleanup已证 | 仍允许下一题；不把低分误当invalid |
| 013型main失败/无exact summary，official1 | 保留passed/1及main失败；完成本题cleanup后stage_halted，禁止下一attempt_started |
| 014/048型main失败且official0 | 保留failed/0并同样停止，不用独立verifier补summary |
| 101型official调用抛错/null，业务trace合法 | invalid_evaluator/null原封保留，官方只调用一次，cleanup后停止，不把null当0 |
| 任何invalid_*（即使cleanup成功） | 按预先明确的阶段failclosed规则停止；缺setup/evaluator/agent证据分层保留 |
| worker或outer forced、cleanup unknown/failed | 停止，不能用后续任务恢复证明前题曾clean；无新worker |
| episode边界source/manifest/authorization/readiness drift | 在下一attempt_started之前拒绝，记录漂移身份，不碰设备/不篡改授权造停止 |
| 用户或总管在题间明确请求停止 | 走独立正常stop请求通道，当前owned cleanup收束后不启动下一题；不能靠改授权hash或kill不明进程 |
| turn循环与重复读 | 使用同hash/同范围/同结果重读且无候选或状态进展作为有界信号，必要重读不一刀切；原100turn内留模型合法终结机会，错误仍保留错误 |

未来可先用原record的副本/合成record做纯离线谓词与controller状态测试；真正新campaign须另外批准、绑定新代码身份/新资源授权。当前没有跑测试、设备、评分或任务，也没有修改原result/report。

## 原证据入口

- [FSQ逐例核心调查](fsq-case-notes/core-contract-browser.md)：013/014/048/049各自goal、events、截图、结果路径及具体未来方案。
- [原四类异常harness抽取](harness-evidence/013.json)、[014](harness-evidence/014.json)、[048](harness-evidence/048.json)、[049](harness-evidence/049.json)。
- [原正式阶段报告](../next-stage-plan/execution/run/report.json)，含attempt operationalErrors与最终haltReason/qualified。
- [原最终交付记录](../final-handoff/report.json)：保留原分数、唯一异常集合及原协议偏差说明。
