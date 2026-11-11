# 18案独立验收 — w4:p2

## 结论与证据

18/18 接受，保留逐案未知；不是现场资格、新 reward 或所有业务答案正确的证明。最终逐案 report/diagnosis SHA 与共享 proposal SHA 见 [独立验收清单](independent-case-acceptance.json)。

- [原调用计数及签名](independent-author-proof-count-receipts.json)：308 个 canonical Python 响应，261 completed / 47 failed，308 kernel alive。110 另有 docs 请求与内层 JSON 解析前拒绝，不混入 Python 响应数。Sports 原 proof 的 resultStatus=null 不能作为 canonical 状态；独立清单补存原 83 响应的 ID、行号、状态、kernel 与参数/代码指纹。
- [Harness 验收](independent-harness-acceptance.json)、[owner 指纹验收](independent-owner-fingerprint-acceptance.json)：12 件证据、9 件开发代码/测试/README、18 历史结果均匹配。实际 helper 18/18 是离线构造 TaskEval 公开参考时钟，不是现场初始化。安装 clipboard helper 的内存 ADB adapter smoke 只证明自身启动后 5000ms foreground 失败边界。
- focused 首轮 569 passed / 2 failed 保留；tests-only 修正后仅两项目标 2 passed。不称一次 571 全绿。独立 reviewer 未重跑任何 checks/smoke。
- [零操作及授权证据修订收据](independent-zero-operations.json)：本批无设备、ADB、session、生产 Appium、真实 env/task init、DB、evaluator、重放、新 reward 或正式 skill/Runtime 修改。仅按授权修正 Sports 五案的报告与诊断。

## 逐案接收

| 案 | 接受结论 | 主要保留边界 |
|---|---|---|
| 073 | 旧捕获丢失；两页 UI 支持候选；Sunday22 跨页有价值 | 未保留实际 initialized expected titles；晚 final 不是新 receipt |
| 074 | set_value 不支持；picker 重试未提交日期；unresolved | 输入 commit 根因未知；未读 Friday 业务数据 |
| 076 | strict-after 与恰好边界种子存在上游契约歧义 | completed 非预算耗尽；quit 先于 final，不推新协议顺序 |
| 080 | SAVE 在 18/18 后拒绝；未证文件持久化 | 无原判分文件系统快照；启动/ASI 因果未知 |
| 082 | 误开 Google Messages，目标回复未完成；与 0 一致 | 不断言历史 SMS DB 无行或唯一判分分支 |
| 084 | recipient newline 未确认；无 body/send | 正确确认控件及历史 scorer 输入未知 |
| 085 | completed/blocked，8/12，非硬预算终止 | 剪贴板未测；ASI 与搜索因果未知 |
| 086 | sender/target 分开；最后 send 因预算拒绝 | 最后 Appium 包不是实际 scorer 输入；补一点击不保证成功 |
| 087 | count1 与静态 COUNT2 不符，归 model/skill | 非 Runtime；数字类型不能倒推违反未披露的 r12 指令 |
| 089 | 2:15:00→135 与 UI/source 兼容；numeric admission 无效 | 无历史 initialized proto；不称唯一失败或新 reward |
| 090 | late raw4790 与 finalText=null；对象形状另列 | 非已观察类型拒绝分支；category/maximality 与新 receipt 未测 |
| 091 | 4.04mi→6502 候选换算兼容；object admission 无效 | 分项距离/实际 proto SUM 未保留，不能从卡片反推唯一分项 |
| 092 | 1:45:00→105=30+75 候选兼容；object admission 无效 | 活跃日期范围与实际 proto SUM 未保留 |
| 101 | native modifier 不是桌面复制证据；getter 自身启动失败 | 原 clipboard、官方 Clipper 分支、helper 启动根因未知 |
| 106 | filter 行差支持三标题候选；旧 final 捕获丢失 | 不证明全 app 默认、唯一 filter 或实际 expected 比较 |
| 107 | numeric20 与静态 COUNT6 业务错、未披露 string 门分层 | 原 final 是 number20，非 string；sort/filter 可达性未测 |
| 110 | capture loss 与 malformed inner JSON 分开 | 20 响应 + docs + 被拒 write；outer hash 不证明 inner JSON 合法 |
| 111 | by Thursday 正确，incomplete 成员资格未证 | 17vs3 是静态长度不符；不是 due-on 问题；重复实体未知 |

## Sports 实例证据边界

五案均未保留历史 initialized proto 或真实 get_expected_answer 返回。087 的 COUNT2 是静态模板数量；089/090/091/092 只接受 UI 数值与 source 变换兼容，不称历史唯一分支、正式匹配或新 reward。090 的 late final/capture loss 与 object 类型必须分层。091 先前 4007+2494 分项只是非唯一推断，算术和为 6501 而非 6502；不作为已观察期望值。

## 共享候选与后续边界

共享 proposal 新增 165–189 行已读；八组指导仅候选。保留脚本内批量观察与有条件动作，不加固定 benchmark 路线/答案、不把环境症状当根因。r15 公开 initialized_task.device_time 参考及 offset，保持 exact goal/params/预算/evaluator，不证明任一旧 0 的唯一成因。旧 r12/13/14 不追补 clock 要求；新 source/prompt/protocol 身份须重新资格、预演、校准。本批不启动正式 run。

父提供的历史 696 / 正式 skill9 无差异属于父的最终 immutable 收据；不冒领为 reviewer 重新扫描。所有保留未知明确列在逐案清单，无未解决阻断项。
