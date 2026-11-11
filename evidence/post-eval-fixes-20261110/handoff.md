# 测评后修复交接：三批实施/验证/scoped review协调结束，部署另行授权

**三批实施/实际验证/独立scoped review的协调收尾已完成，FSQportionComplete=true。** 第一批15passed与第三批32passed/D01-D03 closure已完成；第二批revision2补证两次实际attempt最终accepted-with-limits。此完成仅是本批范围，不表示已部署、17历史案修好或新FSQadapter完成。总管决定广泛Skillcandidate只留档、不默认合入/发布；G1/G2与newmanifest/freshqualification仍open。

## 三批状态与证据

| 批次 | 当前实际状态 | 证据及边界 |
|---|---|---|
| 第一批 001 / 014 / 076 | 实施完成；独立 contract review 完成，无 actionable 源码 finding（P0/P1/P2 均为 0） | [review.md](review.md)、[review.json](review.json)。实施者 15 passed / 离线 consumer smoke 证据见 [README](../../README.md)；reviewer 未重跑，本次也未重跑。两个未来运行 P1 门槛仍开放。 |
| 第二批 外部AMKernel候选 | 原六场与revision2两次实际补证均已交付；最终独立review accepted-with-limits，协调完成 | [report](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/report.md)、[review-handoff](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/review-handoff.json)、[finalOutcomeReview](../../../amkernel/evidence/post-eval-skill-review-20261110/review.json#/finalOutcomeReview)。actualAttempts=2；广泛candidate只留档，不默认合入/发布；无成功率或整体成本收益证明。 |
| 第三批 evaluator私有留证 | 源码完成；D01/D02/D03独立closure均resolved | [verification.json#/corrections/0](../evaluator-private-diagnostics-20261110/verification.json#/corrections/0)：32passed（旧26+6）及定向smoke；[review.json#/diagnosticsClosure](review.json#/diagnosticsClosure)为最新独立结论。部署identity/installed/manifest/qualification仍open。 |

## 第一批 review 与两个 P1 未来运行门槛

第一批只修完整文件名、独立报销筛选元数据/原 note、显式同日 strict-after 契约；并非历史 attempt 必然应通过的证明。review 未发现需修改的源码问题。

- **G1 / P1_before_future_evaluation：身份未闭环。** review 记录子模块 8 个 tracked 文件 dirty；HEAD 和父 gitlink 同为 `55ddaf5edc6f6c25673aed343907d5b9dca66f84`，父 README 实为 untracked。当前 commit/gitlink 无法重建新定义。仅在后续授权下纳入预期子模块改动、推进父 gitlink、纳入 README；不能扫入用户无关/生成文件。本次不执行 Git 写操作。
- **G2 / P1_before_future_evaluation：安装与新资格。** review 记录当前非 editable 的 installed 实现/textproto/metadata 均与新 source 不同。`PYTHONPATH` source 自测不是 installed consumer 验收，也未证明每种消费者的实际 import。后续须另行授权 package/install 被接受身份，核对实际 import/task-data bytes，用新 manifest/task identity 和 fresh qualification。旧 `time` 不能 shim 成新 `hour`；不得改写 frozen manifest。

以上来自 review 时刻观察，本次未重跑 Git/import/installed 校验，也未消除任一门槛。review source-set SHA256 `995e8378ec4ca435a7f739356e64089597a97c7c76a8870efe75e6a44925286d` 是当时 working-tree byte identity，不是 commit/install identity；本次 README 整合改变 README bytes，不能冒称原九文件 digest 仍是新总体身份。两份原 review 保持原样。

## 第二批：最终补证accepted-with-limits，candidate只留档

Owner：amkernel owner。原配对结果与候选已交付，独立记录于原amkernel evidence，未在本项目应用或合入原树。[candidate.patch](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate.patch)、[candidate-manifest.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate-manifest.json)保留交付；最终review的13receipt锚点记录patch SHA256为`297410142516e60ce95edfbed2006f2872cb398bd11b039ed4d51aad22f670a1`，本轮不重新散列或应用。旧handoff此前引用的patch hash已在JSON historicalDeliverySnapshot留档。以下原交接字段索引保留，不代表所有历史SDK/环境/prompt身份都已证明：

- **`candidateIdentity`**：Candidate/change paths, source commit if any, dirty-source digest if applicable, package/Skill versions and artifact provenance/hash; distinguish unpublished candidate from released artifact.
- **`runtimeAndAgentIdentity`**：Actual AMKernel/Skill/OMP/model identities and execution entry point/MCP route used by the real Agent; relevant runtime/config evidence and differences from the comparator, if used.
- **`scenarioAndTaskBinding`**：Actual scenario/task IDs and target behavior, definition/instance identity, goal/params provenance or hash, fixture versus real-device boundary; no preselected IDs or invented manifest.
- **`executionProtocol`**：Actual commands, run/attempt IDs, timestamps, seeds if used, attempt count, step/time/action budgets; comparator controls/differences or explicit statement that no comparison was run.
- **`actualRealAgentEvidence`**：Real-Agent trajectory/tool/session logs, output paths and hashes, observed end state versus acceptance criteria, reward only if actually evaluated; distinguish measured results from inference or offline fixtures.
- **`resourceAndCleanup`**：Authorized resource window/target and session identities, conflicts, actual cleanup/restoration evidence and any unknown/failed cleanup; do not infer cleanup from idle state.
- **`outcomeAndLimits`**：Actual outcomes, failures and limitations, unverified scope, evidence-backed causal claims and requested next decision; publication/installation/qualification require separate authorization.

总体JSON的`batch2.delivery`现已填写外部证据引用与原配对事实，不再标成未交付。原12个slot全部完成，无丢弃/未启动；是native Copilot CLI上的合成loopback W3C UI，不是物理Android或formal OMP。

| 原配对指标 | OLD | NEW |
|---|---:|---:|
| Business通过 | 6/6 | 6/6 |
| Python calls | 37 | 34 |
| Actions | 49 | 51 |
| Elapsed seconds | 293.626 | 349.422 |

无成功率改善或整体成本收益结论；不能假定更少calls抵消更多actions/耗时。tokens、金额、实际provider模型身份和完整历史SDK/env/prompt仍未知。只保留候选，不写已改善或历史17case已修。

独立补证 `structured-recovery-supplement-20261110T031940Z` 的 **revision2已完成OLD→NEW各一次，actualAttempts=2**；最终独立解释为 **accepted-with-limits**，无剩余证据 blocker。权威最新结论是 [finalOutcomeReview](../../../amkernel/evidence/post-eval-skill-review-20261110/review.json#/finalOutcomeReview) 与 [review.md §8](../../../amkernel/evidence/post-eval-skill-review-20261110/review.md#8-finaloutcomereviewaccepted-with-limits)，时间 `2026-11-10T04:29:34.999254+00:00`。原外部pending/attempt0或“待最终解释”字段是历史cutoff，由最终review覆盖当前状态；本轮不回写任何原始/历史收据。

两臂均实际覆盖tuple-summary hazard，并在首个依赖字段mutation之前合法读取、实际交付完整值；保存状态独立验收通过，原非目标字段保留。不是由最终业务碰巧正确、外层transport成功或Agent自述推定恢复。固定hazard/recovery/business/protocol/qualified均成立；原六场仍不追认structured recovery资格。

| 本补证实际观察 | OLD | NEW |
|---|---:|---:|
| 实际attempt | 1 | 1 |
| Hazard covered / recovery qualified | true / true | true / true |
| Business / protocol / qualified | true / true / true | true / true / true |
| Mutation actions / budget | 5 / 10 | 5 / 10 |
| Python calls | 7 | 7 |
| Native HTTP requests | 100 | 69 |
| Process elapsed seconds | 56.568 | 55.813 |
| Failed cells | 1 | 1 |
| 成功session create / delete | 1 / 1 | 1 / 1 |
| 实际snapshot activeSession | false | false |

生命周期来自fixture journal成功请求、counter与snapshot，不来自Agent done。OLD在DELETE seq99后再次POST/session seq100，HTTP400拒绝，cell7 failed/alive `SessionNotCreatedException`；因此不是“只尝试创建一次”。NEW在save seq60后查旧页面seq61，HTTP404，cell4 failed/alive `NoSuchElementException`；“stale”指页面已改变，不冒称 `StaleElementReferenceException`。两臂失败cell及OLD既有post-save404全部保留，fixed protocol true不表示无错误，不按新偏好追改评分。

**总管最终采纳决定：广泛Skillcandidate只留档，不默认合入原树、不发布。** 原六场与补证OLD/NEW均通过，没有成功率收益或整体成本收益证明；HTTP100→69、elapsed56.568→55.813仅是单pair描述，不建立因果Skill效果、普遍可靠性、token/计费收益。实际provider/model未获native events证实；闭源vendor system prompt/embedded SDK不可见，usage=[]表示tokens/费用未知而非零。宿主为Copilot CLI1.0.105 synthetic loopback，不是formal OMP或真实Android，也不证明17历史案已修。

### 最终review的13条receipt锚点（引用快照，不新散列）

以下以原 `amkernel/evidence/skill-boundary-ab-20261110T024711Z/` 为基准；精确已记录SHA256见 [最终review §8.5](../../../amkernel/evidence/post-eval-skill-review-20261110/review.md#85-锁定实际-evidence) 和 `handoff.json#/finalBatchClosure/skillFinalReview/receiptSha256AsRecordedByFinalReview`。这些是finalOutcomeReview当时锁定的13项，不声称随后行政收尾改过的report/handoff/index仍有同一current hash；没有开展新hash全审。

- [review-handoff.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/review-handoff.json)
- [report.md](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/report.md)
- [receipt-index.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/receipt-index.json)
- [candidate-manifest.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate-manifest.json)
- [candidate.patch](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/candidate.patch)
- [structured-recovery-supplement-20261110T031940Z/criterion-review-package.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/criterion-review-package.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/execution-authorization.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/execution-authorization.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/manifest.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/manifest.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/summary.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/summary.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/structured-recovery-boundary-old.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/structured-recovery-boundary-old.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/structured-recovery-boundary-new.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/actual-pair/structured-recovery-boundary-new.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/actual-outcome-interpretation.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/actual-outcome-interpretation.json)
- [structured-recovery-supplement-20261110T031940Z/revision-2/workspace-safety-after-actual.json](../../../amkernel/evidence/skill-boundary-ab-20261110T024711Z/structured-recovery-supplement-20261110T031940Z/revision-2/workspace-safety-after-actual.json)

## 第三批：实际留证内容与边界

交付路径：`src/fsq_androidworld_eval/runner.py`、新`evaluator_diagnostics.py`、`tests/test_evaluator_diagnostics.py`。本轮只整合文档，不改已验证源码或重跑检查。最新三项source SHA256见总体JSON的`batch3.sourceSha256AsReported`及README corrected-source表，均引用`review.json#/diagnosticsClosure/sourceIdentity`与`verification.json#/corrections/0/sourceSha256`。既有Harness glob包含helper的identity消费者链已复核；不等于已锁完整新runtime/installed身份或已获准入。

### 捕获的是既有日志/异常，不是新增评分或 DB 调查

新身份 attempt 默认产生 `raw-private/evaluator-diagnostics.json`。观察评分线程到达原 root/absl filter 点的既有记录，保留原 message template 与有界 literal 参数投影，**不是重新渲染的完整 message 文本**。异常记录类型、有界原参数、最多 16 帧且无 locals；同时记录原 reward、task name/params hash、phase 和评分开始/结束时间。不遍历私有 task 属性、不补查 DB、不重调 evaluator。

起点在业务Agent退出、step adapter finish/session cleanup、协议核对、提交读取及必要`interaction_cache`设置之后；只包围原来唯一一次`task.is_successful(env)`。返回/异常即结束；移除filters后写盘，仍在task teardown之前。不捕获初始化、Agent、恢复或teardown日志。原logger level/handler/propagation不变；其他线程/未到达入口的logger、stdout/stderr/native输出和被抑制INFO/DEBUG可能不可见。独立源码复核已完成，但原有sinks仍可能输出隐藏值，不宣称所有native输出独占raw-private或OS保密性已验证。

### 私有 sidecar 与 public 引用

实施契约：私有目录0700，sidecar/临时文件0600，原子replace。单文件≤65,536bytes；日志49,152bytes/256条；单次literal/type-name共享投影预算2,048字符/64节点，深度3、容器前8项，类型名编码前最多128字符；异常最多16帧且无locals。固定schema labels与分别有cap的source/frame字段不混计共享预算。省略/截断/丢弃/采集错误明确记录，written不表示完整状态可见。

公开`evaluator.diagnostics`仅含持久引用`{path,sha256,status,bytes}`；状态`written|truncated|capture_error`，truncated也涵盖不安全参数省略。失败为`{status:write_failed,errorType}`，无虚假有效path/hash。evaluator公开error只保留hook-free且≤128字符的type；原生参数/帧留私有，写盘失败不回退public详情。仅受信任维护者离线读取，禁止进入Agent prompt/工具回包/Skill/归一化事件/public索引。此边界已有scoped源码复核，不是所有既有sink或真实sandbox/OS隔离认证；业务答案/既有日志目的地也不能因此假定可公开。

### scalar、未知状态与 IO 成本

`componentResults` 明示 `not_provided / scalar_return_interface`，不从 scalar 或日志解析推造子分数/Boolean；VLC 0.5 仍不能定位哪份 playlist 分项通过。没有日志的失败、遗漏对象字段、完整异常链、最终 DB/device snapshot 与历史 unknown 均未解决，特别不据此关闭 060/098/106 证据缺口。历史 attempt 不补写。

新增有界投影/编码 CPU 与本地写盘 IO；`evaluator.durationSeconds` 不含 sidecar 落盘，而 stage 总时长包含留证。字节上限不是存储延迟上限，写盘在评分结束后、teardown 前可能延迟后续阶段。**不声称零 IO、零 wall-clock 扰动或性能等价。** 原 reward/异常/终态/cleanup 保留只引用实施者覆盖的离线路径；真实设备/运行时耗时未验证。

### 既有实施验证与已完成独立closure（本轮均不重跑）

实际报告命令：

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_evaluator_diagnostics.py tests/test_runner.py
```

原交付是26passed/2warnings/0.44s，首次7failed/19passed因OfflineProxy fixture缺wait_for_idle，补fixture后通过、未改生产cleanup；保留为历史。D01-D03全部修正后，同一窄命令一次得到**32passed/2warnings/0.51s（旧26+新6）**。新增case覆盖root/absl退出竞态、长type-name编码前预算，以及恶意metadata的return/native-exception/write-failure三条runner边界；warnings仍为pydub audioop/ffmpeg发现问题。

原5个离线scenario（reject/pass/raise/silent/write_failure）保留，纠正smoke没有重跑它们。新增定向smoke见`verification.json#/corrections/0/directedSmoke`：
- D01 root/absl：A/B记录不串不丢，foreign filters/sink保持。
- D02：10k类型/异常名在编码前裁到128并计预算，sidecar2208bytes/truncated。
- D03：正常返回/原生异常的offline runner均zero metadata hooks、一次evaluator，原reward/terminal/cleanup保持，持久引用hash匹配。
这些是实施者真实运行的离线证据，不是本轮或reviewer重跑；外部设备/OMP/环境仍是fixture，不能推出真实设备/Agent/sandbox/IO时延或新campaign资格。

最新独立结论为[review.json#/diagnosticsClosure](review.json#/diagnosticsClosure)，时间2026-11-10T11:23:37+08:00：D01/D02/D03全部resolved，unresolvedOriginalFindings=[]，无新增定向finding，无需再改这三项。旧finding及旧hash原样保留；原实施文档/corrections里的pending标签由后续closure覆盖，不回写原收据。
closure记录verification.json文件SHA256为`7e44cb90737500675277b7a837e0d7e2254a7bc1ece64cea749c1721e1ddf8bf`、implementation.md为`edb76403177d42154554ccb242a3d941c913385a658f32cc1f73b3790768b50a`；三源码hash在总体JSON/README精确引用，不在本轮重算。这是review快照，不是完整新部署identity。

## 可采纳源码与下一次启用前的步骤

第一批实际改动在子模块：`android_world/task_evals/single/audio_recorder.py`及`audio_recorder_test.py`，`single/expense.py`及`expense_test.py`，`information_retrieval/proto/tasks.textproto`与`proto_utils_test.py`，以及`android_world/task_metadata.json`、`docs/tasks_guide.md`（均以子模块根为基准，前述single/IR路径位于android_world/task_evals下）。行为为完整文件名精确匹配、独立报销筛选列与原note、同日strict-after新参数契约。第三批父仓库文件为runner/helper/窄测试，新增既有日志/异常有界sidecar与公开错误收窄；D01稳定filter快照、D02编码前类型名cap/共享预算、D03避免metadata用户hook。完整路径清单见JSON，不覆盖其他用户hunks。

1. Obtain explicit deployment/resource authorization; choose accepted task definitions and protocol. Preserve historical manifests/results/83.1897%; scope completion alone is not launch permission.
2. Under separate Git authorization, review intended changes, commit the AndroidWorld submodule and advance the parent gitlink; include intended parent source/docs without sweeping unrelated/generated files. Capture actual commits and source hashes.
3. Build/install the accepted package identity separately; verify actual consumer imports and implementation/textproto/metadata bytes. Do not equate source PYTHONPATH proof with installed acceptance.
4. Capture the complete Harness/runtime/target/artifact identity, including corrected runner/helper. Check evaluator revision and migration admission policy; the old current_stack allowlist is not blanket approval of new AndroidWorld definitions. Any needed policy change requires separate authorization.
5. Prepare a distinct new manifest with approved definition/instance/protocol/runtime identities and fresh readiness/qualification in the authorized exclusive resource window; never rewrite or borrow old frozen evidence.
6. Run fresh non-scoring rehearsal and calibration required by the approved protocol, inspect actual identity/cleanup/evidence gates, and only then separately authorize a new campaign/output directory. No step is performed by this handoff.

本节是未来另行授权的具体闭环顺序，不是本次执行。当前完整runtimeIdentity/新submodule commit/gitlink/installed/new manifest/readiness均不填假值；旧固定revision/迁移规则是否接纳新定义也须真实解决，不能只替换hash冒充可运行。

## 历史边界与后续接续

原 formal `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` 的 **83.1897%** 与全部原 manifest/params/results/raw/analysis 证据不变；本次不重算、不回写历史 pass、不做全历史 immutability 新审计。030/060/latent matcher 不顺手修复；第三批观测增量不改变这些已知未知项。

**本批三批实施/验证/scoped review协调已结束**，不再把外部review或补证attempt0当当前等待；原pending收据不回写。仍须另行授权的是G1/G2 commit-gitlink/installed、完整新身份/newmanifest/readiness/freshqualification，不是未解决的源码P2。独立源review快照保留，不能声称current whole project被review。新FSQadapter是新总管w6:p2指挥w4:p1的独立在途接入任务，不在本批完成范围，不中断它。本轮不publish/commit/push/stage/install/build，不改独立review或任何实现/原始结果/日志；唯一随后获准的服务动作是停止本会话创建的FSQRepairHourly01a1c098，不触碰其他timer/Appium/模拟器/agent。

本轮只修改并必要读回handoff.md/json，读取已交付收据，不改README、新adapter源/文档或两份独立review，不运行模型/测试/设备/新hash全审。JSON的priorDocumentationVerification保留前轮文档校验历史，不冒充本轮新校验或原收据至今未变化的断言。文档读回后停止唯一owned repair timer，停止回执单独向总管报告。
