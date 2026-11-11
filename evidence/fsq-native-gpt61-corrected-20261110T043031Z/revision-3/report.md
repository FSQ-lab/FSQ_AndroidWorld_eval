# Canonical swipe consumer：真实失败与最小修复闭包

## 结论

这是 adapter 的 capability canonicalization predicate 错误，不是已有证据表明 Agent 给了无效格式；不据 worker exit0 或 native success 判定官方成功。已仅修复 consumer，完成离线证明；旧102保留 `invalid_agent/native_evidence_invalid`、reward=null、evaluatorCalls=0，不重试、不补评分、不修改原终态。

新 revision3 candidate：`d9f3237c0d6d26f512bfdd3870fd4563519fc24f6cae160beb93a015a597a057`。
新 evaluator source tree：`69158f28eadbcd1921bd58a4dd9207b7dcbc10d5fd2756507604313d163bf99c`。
独立 review 尚未批准；限定变更交接见 `review-handoff.json`。此报告不是执行许可。

## 原阶段事实，原件全部保留

原 run：`revision-2/resource-admission-20261110/fsq-envprepare-r1-5554-20261110T065520Z/`。

- 新授权真实签发 2026-11-10T12:33:41.126340Z，90分钟，至14:03:41.126340Z；candidate94a33fc、review5a941e、model58d968。具体 effects 以真实用户新表单明确批准为准，不自扩权限。
- 唯一地图准备成功；8条 target-specific ADB 命令均rc0，complete=true / restored_and_verified。7241271字节固定地图写后SHA `57a1955c6f517a114999fa50480ecc1402ed9b524db602540ac1c08f57ff140e` 匹配既有pin。目标本已root，`guestAdbdRootRequested=false`，未执行adb root；bootId仍`0f36e370-012a-4423-a1f9-959beae8f90d`。原receipt保留每条stdout/stderr/rc；只保留真实目录/地图/mode/context改变，未做回滚/unroot。
- 唯一新资格通过，outer27.98s；7 checks全true，恢复22个原既有快照，实际8项baseData全present=true。没有触发DBgate，也没有造库、重装或替换快照。readiness SHA `54bde965af9ffa68d88d6b20056ba21bfacf22f8488f71ecc6f6f6bfcd77f8fc`；environment closed。此资格只归revision2，不能转给修后revision3。
- 唯一102 smoke入场前实测剩余授权5231秒，覆盖原完整1330秒。入口shell exit1 /110.44s；outer单spawn exit0、forced=false；worker单spawn exit0 /87.51s、businessDeadlineReached=false。没有超时、强杀、自动重试。classification为原`invalid_agent/native_evidence_invalid`，EvidenceError，evaluatorCalls0，reward=null。
- 真实cleanup：taskTearDown completed；official environment closed；owned worker leader reaped，process group disappearance observed，members/runningPids均空；无signals/kill，cleanupFailure=false。native Harness close 明确不提供设备状态恢复，不能升级为guest已恢复、Wi-Fi当前状态已知或全局session为零。

原始入口/worker日志及process receipts在该run的 `execution/qualify/`、`execution/smoke-102-SystemWifiTurnOff/` 和 `execution/smoke-102-SystemWifiTurnOff.outer/`。外层日志的ffmpeg warning和一次a11y retry是保留事实，不将它们改称本次EvidenceError根因。原资格device probe/controller未持久化的内部返回文本不能补造；保留的是实际发出的process.log及已有结构收据。

## 精确失败 predicate：静态定位，没有重跑原check

Producer `fsq_native.py`：

```python
WRITE_CAPABILITIES["swipe"] == "swipe"
WRITE_ALIASES = {alias: name for name, alias in WRITE_CAPABILITIES.items()}
# 因而 WRITE_ALIASES["swipe"] == "swipe"
```

真实 `worker/native-action-audit.jsonl`：sequence1-4为launch_app/ui_snapshot，sequence5是
`capability="swipe", event="attempted", countedWrite=true, ticket=3`，sequence6对应成功completion。这是原生FSQ和计数producer已经支持的canonical名称；snake/camel恰好同名。

旧consumer `fsq_evidence.py` 的审计循环却要求：

```python
isinstance(capability, str) and bool(capability) and capability not in WRITE_ALIASES
```

该条件会把合法自映射 `swipe` 当成非canonical alias拒绝。这是保留producer字段与源码predicate的直接冲突；原failure.json按隐私策略只记录异常类型，未保留原异常message，因此不声称从原日志恢复出message/stack。没有重跑原validator来确认报错，也未对旧native root补/改证据。

`fsq_runner.py` 在validate_native_evidence通过后才归档native并调用official evaluator；因此本次停在取证，native root未归档但仍保留，worker process receipt独立保留。SDK内部status/verification success不是官方reward。

## 实际producer证据树与格式

保留根目录：

`~/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/episodes/fsq-native-gpt61-r2-final-5554-20261110-smoke-102/`

- `worker/worker-result.json`：schemaVersion1、completed、native_execution_returned；引用TaskResult/verification/audit的路径、SHA、size、evaluator_private；mainAnswer精确指向`agent_runtime.runner.tool_output.summary`。
- `worker/fsq-task-result.private.json`：真实native TaskResult，有task_id/status/steps/verification/report/duration_ms；唯一main runner提供已解析task_run_v1，pre_plan step_id为int，status为success，criteria为字符串数组。非runner内容不作为答案。
- `worker/fsq-verification.private.json`：SDK内部校验；并非官方oracle。它记载控制UI checked=false的观察，不能据此追补官方reward或推断teardown后的状态。
- `worker/native-action-audit.jsonl`：23事件，5 admitted write，包含canonical swipe和setup/teardown，close21-22、native_return23；5写不是10个read/write tickets。无参数、目标文本或秘密。
- `worker/worker.log`：0字节，不能虚构错误栈。
- `workspace/.fsq/runs/android/<task-id>-20261110T123704Z-598054/`：实际有run.json、report.json/report.md、execution-result.json、events.jsonl、owner.json、evidence-events.jsonl、evidence-manifest.json，artifacts下tools/ui-snapshots/screenshots，以及sources/000-goal.txt。原目录不动，完整自由文本不拷入公开报告/fixture。

## 最小实现及未降低的安全边界

运行时只有 `fsq_evidence.py` 一处predicate变更：

```python
WRITE_ALIASES.get(capability, capability) == capability
```

- canonical `swipe` 自映射允许；真实非canonical `launchApp`/`tapOn` 等映射到不同名称，仍拒绝。
- swipe仍在write inventory中；不能标成read或少计一次，不改变M、B或计数unit。
- 不改path canonicalization/`..`/symlink/root containment/regular-file校验、SHA/size/private visibility。
- 不改TaskResult/episode/serial/return身份、精确main summary/businessStatus来源、无fallback要求。
- 不改事件schema/顺序/ticket/完成配对/deadline/计数/close settlement及trusted process group准入。
- 不改oracle顺序/评分、秘密和oracle文件隔离、SDK或worker。没有放宽DBgate或改预初始化生命周期。

## 离线consumer回归与实际smoke

`tests/fixtures/fsq_native_swipe.json` 来源于这次实际worker/TaskResult/verification/journal。保持真实结构、数值、事件与独立journal；自由文本替换为稳定不透明标记，一致替换task identity，去除活路径/authentication元数据。fixture原始来源摘要见`fixture-provenance.json`。测试只在自己的临时root重建fixture引用，不伪造/覆盖原native证据。

新增行为回归：
1. 完整consumer接受真实canonical swipe，核对5/5/5/0 accounting、无pending、精确summary/businessStatus和kill观察。
2. 即使重hash journal，真实非canonical launchApp仍被拒。
3. 即使同步篡改计数，不能把swipe标成uncounted read。

最终相关8组offline suite：**313 passed、1 skipped，13.54s**。跳过的是既有opt-in真实macOS sandbox/native FileOps proof，未以此声称新增运行安全证明。首次新增test错误比较了consumer不承诺保留的producer附加reason元数据，原失败日志保留；删除该incidental整体相等断言，改验证真正summary/businessStatus契约，未改运行时实现凑测试。

另在独立临时root实际调用修后consumer：rc0，answer valid，admitted/succeeded5，kill succeeded，mainFinalOrdering仍unknown；无device/model/evaluator。临时root已随上下文清理。

证据：`regression-pass.json`、完整stdout/stderr logs、`offline-consumer-smoke.json`。没有重跑原check、102业务、新资格、评分或其它live阶段。

## 新source/candidate/review闭包

- `source-closure.json`证明runtime source delta仅`fsq_evidence.py`；整个native FSQ SDK、AndroidWorld、provider/model、ADB身份不变。
- 新candidate继承原116个冻结task rows，逐值保持、没有重新生成clock-sensitive参数；target/protocol/budgets不变。
- 新candidate全部gates pending，不迁移旧review/qualification/授权/102结果。
- `review-handoff.json`绑定runtime、tests、脱敏fixture和README的当前SHA，只请求审这一真实变更及安全边界；不重开无关R01–R08，不自签独立review通过。
- 后续不同任务smoke、重新资格以及预演/校准/正式均待总管基于真实根因决定；旧102不可重试。

FSQ-first目标仍保留，不自动释放AMK。修复不需要新的外部依赖或设备动作；独立delta review及后续live范围决定是下一门槛，不是再次询问实施意愿。
