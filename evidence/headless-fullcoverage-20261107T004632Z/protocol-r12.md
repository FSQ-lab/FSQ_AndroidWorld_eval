# r12.full_coverage_after_verified_recovery.v1

本轮由交接prompt明确授权改变campaign级fail-stop策略。旧r11目录与结果不改写，不续跑、不拼接、不冒充旧协议正式分数。

## 冻结契约

指定原manifest文件与完整任务规格摘要必须匹配已锁定值。新`prepare --inherit-manifest`不调用suite参数生成；116项规格与参数保持相同，12项校准仅选取原任务规格并重排连续索引。原模型、Agent工具/动作策略、步数/时间预算、MCP120000ms、单任务重试限制与官方reward语义不变。冻结Runtime只允许Harness源摘要因本次改动发生变化；原AMKernel、OMP、依赖与官方任务源码身份仍须匹配。实际无窗口/渲染环境证据绑定至manifest.target并进入readiness身份。

## 调度与证据

新run拒绝已有执行证据。每次runner启动前写入`attempt_started`，结束写入`attempt_terminal`及原result摘要。单项失败或invalid不自动重跑；只有原有pre-Agent invalid_infrastructure允许原预算中的一次重试，两个attempt均留存。其他invalid，包括episode局部工具违规，保留原分类与reward/null。

每个异常终态要求新的全局manifest/Runtime身份验证、readiness attestation、Appium会话缺席与真实核心服务健康检查。检查包含ADB、activity/package/settings/window、system_server/SurfaceFlinger PID、boot ID、Appium与Emulator gRPC实调用。追加恢复证据绑定原result、分类与cleanup，不能改写原始结果，也不能将Harness回收伪装成Agent成功quit。

清理仍未知、全局身份改变或环境不可用时写入pause原因及未启动索引，返回2，不盲目启动下一项。此实现不自动冷重启或resume中断campaign；不得把暂停结果报告成116项完成。

## 资格与计分

资格重建只使用现有已安装冻结应用；缺应用时失败，不重装。正常官方setup在只读临时层重建应用状态与快照。新协议要求新资格、完整116项无Agent预演、新12项校准，再新建116项run。

独立`continuation_audit`核对实际启动/终态、source规格、Runtime/目标、readiness、result来源、checkpoint顺序、预算与恢复证据。116条结果不等于116项有效结果。新协议full的`officialScore`始终为null；只有完整有效来源、全部有效终态、原Agent清理和校准门禁成立时，才可产生独立的`fullValidScore`。有效覆盖率、诊断分数、invalid/null与原cleanup异常另行保留。旧r11离线重算语义不变。

## 已执行验证

- 全套回归426 passed；2个既有警告保留，未为消除警告改依赖。
- 真实`_load_manifest`继承清单验证与`_core_service_health`路径已执行，核心服务与gRPC返回qualified。
- 已实际生成116项预演清单和12项校准清单，并逐项核对与指定源规格相等。

完整门禁及正式campaign状态由后续实际产物证明，本协议文档本身不是资格或正式分数证据。


## 本轮资格修正边界

第一次资格报告虽返回qualified，但独立检查发现VLC快照缺少`app_onboarding_done`。已通过冻结AMKernel的PythonExec与官方Appium Client完成真实首启、核对权限、成功quit并独立查询session404后保存官方快照。资格与live attestation现在要求这项真实启动证据；原报告不覆盖。

修正后的首轮116项无Agent预演全部通过。随后12项校准全部启动并结束，但来源审计拒绝两个记录：官方IR初始化把日期改写为UI表达，Runner原先在初始化后保存params，而参数摘要在初始化前计算。已把参数记录移到初始化前，保持输入内容与摘要一致；官方活任务的日期改写、目标、evaluator、reward与预算不变。旧校准结果与审计错误保留，不改写或拼接。此次Runner源码身份变化使原门禁失效，必须重新建立完整资格、116项预演与12项校准。

参数记录修正后相关266项回归通过；真实无Agent参数记录smoke与新轮门禁由独立产物记录，不把旧门禁重贴为通过。

## v2 实际恢复边界

`r12.full_coverage_after_verified_recovery.v2` 保留 v1 的模型、输入、预算、重试和 reward 语义。恢复前先将原终态及新鲜探测写入独立文件、fsync 并绑定 checkpoint，再允许调用官方 `datetime_utils.setup_datetime`。仅限 UTC 时区单项漂移、已知清理、全局无会话和核心服务健康；只恢复官方时间设置，不冻结日期。恢复后重新验证身份、readiness、会话缺席及核心服务；boot ID、system_server 或 SurfaceFlinger PID 改变必须暂停，不能以一次健康返回替代重启协调。

Agent 异常且从未创建 session 时，仅在进程确实退出、有整数 exitCode、代理错误为空、所有创建/删除/活动/待处理/未知创建计数均明确为零且会话摘要列表为空时，允许恢复检查后继续。保留原 invalid 分类与 null reward，不将环境恢复升级为 Agent 成功清理。缺失计数、未知创建或仍在执行均不放行。

原 v1 暂停轮与先前门禁保持原身份；v2 必须按最终源码重新生成资格、116项无Agent预演及12项校准，从第1项新建完整轮次。实际结果以独立审计产物为准。


## 最终执行证据

最终源码回归484 passed；新资格、116项真实无Agent预演和新12项校准均通过。独立新full实际启动并终结116项，116项有效：80成功、36失败、0 invalid、0 null reward、0原始清理门禁异常；新协议`fullValidScore=80/116`，旧协议`officialScore=null`。40次恢复验证包含3次真实UTC恢复；本轮恢复边界无boot/core PID变化，没有增加单项重试或改写结果。

正常系统UI已恢复VLC原有效拒绝权限，恢复session成功quit且全部相关身份404；原Appium与同一无窗口AVD保持运行。完整证据、创建异常协调附记与新旧计分边界见`report.md`、`v2-ready-final-summary.json`及两路独立audit文件。

