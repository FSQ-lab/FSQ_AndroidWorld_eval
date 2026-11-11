# FSQ 修复独立复核：第一批 task contracts

时间：2026-11-10T10:57:06+08:00。范围：001 / 014 / 076；**contract 代码复核完成，无需修正的源码 finding（P0/P1/P2 均为0）**。这不是安装验收或未来测评开跑许可。两个 **P1 级未来运行门槛**列在下方，不伪装成新发现的源码 bug。

只读复核；仅写本文件与 `review.json`。未改源码/测试/配置/文档/AGENTS，未操作设备、服务、发布、Git 写操作或原 campaign。`FSQRepairHourly01a1c098` 未停止、未重配。第三批 runner 私有评分留证尚未交付，**本次未读取其半成品**。

## 指令与证据边界

已读取会话自动加载的 `/Users/qunmi/Documents/FSQ_LAB/AGENTS.md`；其总管协调角色仅适用于根目录会话，不将该角色强加给本子项目复核。遵守本次用户限定的两个证据文件写入范围。

依据最终 `failure-analysis/module-map.md:41–49,68–94`、`review-resolution.md:9,23,29,34,44–55`，并投影读取 `cases.json` 的001/014/076原参数、oracle、来源与unknown。历史源码契约矛盾confirmed，不升级成历史attempt必然通过；历史物理文件、最终expense DB、完整strict-first成员集仍unknown。当前修复是用户后来明确选定的新契约，不把分析阶段的decision-needed误写成实施授权。

## 逐项实现与真实消费者

所有下列 `android_world/android_world/...` 路径均相对父项目。

### 001 — 完整文件名原样检查：通过静态复核

- `task_evals/single/audio_recorder.py:85–123,125–159`：generator仍生成带 `.m4a` 的完整名；goal插入同一个 `file_name`；`is_successful` 不再二次追加后缀。
- `utils/file_utils.py:228–258`：实际 helper 从ADB返回的路径集合做完整 `base/target` 精确成员检查。没有stem、额外后缀或猜测别名分支；double suffix仅在请求本身就是double suffix时成立。
- `task_evals/utils/user_data_generation.py:108–131`：修饰词插在extension之前，不会把完整名变成stem。
- `audio_recorder_test.py:76–122`：检查exact、额外后缀、stem、无关名、缺失、显式double suffix和extensionless请求。只替换ADB transport，保留真实查找函数，不是把成功Boolean原样mock回去。**本次只读，未执行。**

最小修正：无。预存边界保留：helper接受文件或目录，未检查非空音频/时长/codec；这不是本次suffix修复新增问题，也不把存在性检查吹成音频质量验收。

### 014 — 独立yes/no列与原note持久比较：通过静态复核

- `single/expense.py:324–372`：真实 `csv.writer` 写pipe分隔CSV，独立 `reimbursable` 字段；target=yes、noise=no。原note不追加/剥离 `Reimbursable.`，也不修改params参考行。goal明确只选yes、排除no、原note逐字复制。
- `expense.py:247–281,331–332`：仅Markor覆写 `_free_form_fields=['name']`。`common_validators/sqlite_validators.py:149–163` 因而对note/整数amount/category走exact，name仍走原fuzzy。普通及Gallery expense任务保留原name/note fuzzy策略；共享阈值/比较helper未改。
- **不止display：** `sqlite_validators.py:280–310` 从 `list_rows` 的实际after行调用同一比较器；`task_evals/utils/sqlite_utils.py:27–103` 从pull出的SQLite文件执行查询并构造行对象。exact-note策略到达真实持久行比较，不是CSV展示自洽或mock echo。原before行保护与新增数量检查仍在 `sqlite_validators.py:165–192`。
- `expense_test.py:168–349` 覆盖pipe/quote/LF多行、yes/no独立筛选、相同原note分别出现在target/noise、长note污染/剥离、错金额/类别，以及普通expense旧策略。其 `_persisted_expenses` 实际是**合成行对象**，不冒称已经证明Android持久化。
- 新增一次隔离标准库边界检查：当前项目Python **3.11.16** 对仅含bare CR的原note `Receipt\rKeep original` 仍加CSV引号，`DictReader(newline='')` 读回一行且note相同。没有项目import/设备/测试套件；此前纯静态CR风险猜测被此输出反证，**不保留为finding或修正请求**。

最小修正：无。Markor实际显示、人工输入至Pro Expense的持久效果未由本次执行验证。

### 076 — 严格>、显式同日期与真实IR链：通过静态复核

- `information_retrieval/proto/tasks.textproto:857–963`：goal限定named date、00:00–23:59的**start**，阈值 `{hour}:00`，target `{hour}:30`。同日期 `EQUAL_TO start_date` 加 `GREATER_THAN start_time` 排除随机竞争项；保留现有 IDENTITY(title) 规则。
- 全部声明域已静态核对：15个日期（2023-10-15至29）、10个非空无逗号title、13个hour（06,07,09,10,11,12,13,15,16,17,18,20,21）、16种duration（5分钟至3小时的现有h/m格式）。target start范围06:30–21:30，阈值与start无跨日。21:30+3h的**end**可以次日；start-only契约允许，不是误把次日事件当答案。
- registry `information_retrieval_registry.py:51–60,90–112` 实际解析textproto并从声明域抽参数；`proto_utils.py:297–325` 格式化relevant state与exclusion；`information_retrieval.py:82–119` 把它们送入calendar初始化并使用真实answer comparator。
- `calendar_utils.py:192–331` 与 `proto_utils.py:409–430` 的真实 `>` 比较排除所有同日起始晚于阈值的noise：阈值到target之间的竞争、target-time tie、较晚/跨午夜结束的事件都不能抢答案。因此恰一个relevant target的bound title就是唯一最早合法title，不需要偷偷更改oracle为另一套argmin算法。
- equality不是答案。共享helper也检查endpoints，可能保守排除正时长的equality/更早或前日重叠noise；helper未改，文档明确该边界。新增equality fixture用zero-duration point event隔离start边界，**不拿它证明正时长equality事件必保留**。
- `calendar_utils.py:35–73,158–189`、`utils/datetime_utils.py:215–234`、IR `datetime_utils.py:24–25,89–113`：所有声明duration都有明确解析；随机datetime返回具体值；parser无成功路径null；noise重试耗尽显式raise而非返回空事件。未发现本修复新增跨日/空值随机缺陷；这不是已运行所有seed的证明。
- `proto_utils.py:147–251` 仍用relevant title和原string matcher。shared多答案匹配不消费occurrence的弱点是既存问题；当前singleton任务不新增该问题。random target ties被排除；未生成/测试多个relevant tied targets，不声称已实现通用tie reducer。
- 参数仅声明 `hour`，未提供旧 `time` shim。对task名的限定搜索只见definition、regression、metadata和guide；动态registry从声明生成。**旧manifest中的time参数保留为历史，不能迁到新定义冒充兼容。**

`proto_utils_test.py:1049–1156` 读真实textproto并调用真实format/exclusion/answer函数；遍历全部date×hour及代表性equal/between/tie/later/前后日fixture，不是wording测试。title/duration组合未在新tests中穷举，也未由本次重新执行；仅静态检查其域和parser相容。

最小修正：无。

## 元数据、共享行为和未来运行门槛

`task_metadata.json:10–11,113–114,617–618` 与实际001/014/076 goal同步；`docs/tasks_guide.md:207–223`、父 `README.md:186–223` 记录新契约、无旧time shim、历史不变和安装/资格门槛。实际submodule diff仅8个指定tracked文件，未见共享calendar/proto/SQLite/file helper的patch。未泛化为其他任务的全量正确性认证。

| 严重性／门槛 | 精确位置与证据 | 消费者风险／最小动作 |
|---|---|---|
| **P1：未来运行前身份闭环**（已知门槛，不是源码finding） | `README.md:198–200`；submodule HEAD与父gitlink仍为 `55ddaf5edc6f6c25673aed343907d5b9dca66f84`，但8个tracked文件dirty；父 `README.md` 实为untracked | 旧commit/gitlink不能重建新定义。另行授权后只提交审查通过的submodule变更、推进父gitlink并纳入预期README；不能扫入用户无关/生成文件。本次不执行。 |
| **P1：安装、新manifest与资格**（已知门槛，不是源码finding） | `pyproject.toml:24–25`；`android_world/setup.py:64–93`；installed `direct_url.json:1` 为local-path **editable=false**；3个installed实现/textproto与metadata哈希全异于新source | 源码 `PYTHONPATH` 通过不等于已安装消费者通过。另行授权package/install reviewed identity，检查实际import/task-data bytes，新manifest/task identity并fresh qualification。不得回写旧manifest、给旧time加shim或假定当前安装已更新。 |

当前installed metadata SHA256 `fd3cf23ebb26e461a961dd60ff3f011d7e6ec78c992c10babbbdb86f9dd591e1` 与原manifest pin相同，新source metadata是 `17b65f385c353491044ba639b625a87af8d18e9c2f4dd26b73dc31c5baafd14c`。这证明当前保留的安装副本不同；**未执行项目import，不能据此假定每一种消费者的实际sys.path，也不能把current installed bytes倒推成完整正式时刻安装快照。**

## 精确review source identity

父HEAD观察值：`977020aa4306bc7f5628ec69f65ea998af3013a1`。reviewed source-set SHA256：

`995e8378ec4ca435a7f739356e64089597a97c7c76a8870efe75e6a44925286d`

算法：以下9个文件按相对路径排序，每项拼接 `path + TAB + SHA256 + LF`，UTF-8后SHA256。这是working-tree byte identity，不是commit或安装身份。

| 实际审阅的改动文件 | SHA256 |
|---|---|
| `README.md` | `8f2ff828646796e75c6854f446021f129d267995846373d021d05faf79a8568b` |
| `android_world/android_world/task_evals/single/audio_recorder.py` | `f9a3a0143f711c9f111a372ce8ed27db93fe5d5788322f4f1425106ea529357f` |
| `android_world/android_world/task_evals/single/audio_recorder_test.py` | `d13a7d093646fb4b03f94d5d84b92306c93c7cfd0ab46a5aa6e2da38d1f82b93` |
| `android_world/android_world/task_evals/single/expense.py` | `2068db47b2e4681a6bf3adfaa639db431acf6a60c8b0523101f8eb6b7efabba9` |
| `android_world/android_world/task_evals/single/expense_test.py` | `8f67e35a2bdd4cd6eef12a0af6b2326a8bbf7e4f69e6828311290f7abdd463db` |
| `android_world/android_world/task_evals/information_retrieval/proto/tasks.textproto` | `9442158ac415199aa6b6511e65626491c6dd325e601f572f9aa5012aa6ec15e4` |
| `android_world/android_world/task_evals/information_retrieval/proto_utils_test.py` | `563a951e04852c84fe58d4883a34406d892fc7cde27ef9928de9bbbe39ced7bb` |
| `android_world/android_world/task_metadata.json` | `17b65f385c353491044ba639b625a87af8d18e9c2f4dd26b73dc31c5baafd14c` |
| `android_world/docs/tasks_guide.md` | `b047752d906639f2d1d841e9d77e99e3669ae323d126b6733b071d3ac27c630b` |

实际范围还含最终分析的相关段落/JSON投影、上述生产helper的相关函数、package配置及当前installed来源/hash。完整dependency、analysis、manifest和installed逐文件hash见 `review.json#/sourceIdentity`。未把全文件digest伪装成全文件逐行审查。

原manifest SHA256：`b63bb9973bc78729da8ab058d0087c87cb06456479f40737c84e1eeb7a7721b8`。历史分析记录116终态、96.5 reward sum、83.1897%；**本次未重算成绩、未重评、未改变原始campaign**。未执行整套历史raw immutability审计，不额外声称已证明所有历史文件和某个基线逐字一致。

## 执行与未执行

- **实际执行：** 限定范围Git只读diff/status/HEAD/gitlink、源码/测试/文档/分析/manifest阅读、SHA256、当前installed来源/hash核对；新isolated stdlib-only bare-CR CSV probe（eval及项目Python3.11.16），输出一条完整record且note保持CR。
- **仅阅读owner证据：** `README.md:202–213` 所录15 passed/2 warnings及离线consumer smoke。没有重跑，也不计作本review独立运行结果。
- **未执行：** 任何项目测试套件、已有smoke、实际registry/IR生成或评分、设备/UI/实际SQLite持久化、安装/build/qualification/发布/commit、第三批runner复核。LSP报告无已配置server，采用限定read/grep导航。
- 014和076另由两个read-only reviewer切片核对；他们没有执行tests/probes或写文件。CR最初静态猜测已被当前解释器输出反证并撤回。

**交接：contract部分已完成，无源码修正请求；保留上述未来运行门槛。第三批runner切片等待owner交付后另派复核。定时服务不受此次复核影响。**

---

# 第二部分：第三批 evaluator 私有留证独立复核

记录时间：2026-11-10T11:05:50+08:00。此前第一批contract段落保持原文；其中“第三批未开始”的交接是第一部分当时状态，本附录更新该切片状态，**不改变001/014/076结论或G1/G2未来身份/安装/资格门槛**。

**结论：需修正，3项P2（D01–D03）；无P0/P1源码finding。** 未发现新helper漏出既有Harness源码identity集合；未观察到历史成绩改变或新增公开expected-value泄漏。新实现的真实设备、sandbox、耗时和future qualification仍未验证。未改实现、原始结果/日志，未操作设备/服务/发布/commit/push；定时服务 `FSQRepairHourly01a1c098` 未停止或重配。

## 源码与实施收据锁定

实际逐段读取：`src/fsq_androidworld_eval/runner.py` evaluator/异常/cleanup/Agent输入边界及本批diff；完整 `evaluator_diagnostics.py`；完整319行 `tests/test_evaluator_diagnostics.py`。另读取现有campaign、readiness、continuation、runtime migration、scorer相关identity与error消费者。没有将整个依赖文件的hash当成全文件逐行审查。

| 本切片文件 | 实际SHA256（均与owner verification.json一致） |
|---|---|
| `src/fsq_androidworld_eval/runner.py` | `a1d14605496f4778b99d5f89a30eb69571990dfe419ffdaa0c18a5d04ba3b7de` |
| `src/fsq_androidworld_eval/evaluator_diagnostics.py` | `bb1d37ea7c62df2d7457a704f7f333df244e850fb2b2b4b3fd6e7130eca359e6` |
| `tests/test_evaluator_diagnostics.py` | `ca39f13fef7baf325bb3d59a439c59b611bfe8f6c02453fe1d01302619908a75` |

实施收据实际读取：
- `evidence/evaluator-private-diagnostics-20261110/implementation.md`，SHA256 `1a83817df4a887e8c062b8f61cf06cf30534dee8edd844ad21e4c987bb0b1d57`。
- 同目录 `verification.json`，SHA256 `5f4a95cf73b86e44240931d40606229a8270a52c7a6195a3f004617bc7b6f21a`。

owner的 **26 passed / 2 warnings、5个offline scenarios** 仅作为其证据阅读；未重跑，不冒称本review执行。各consumer源码hash另见 `review.json#/diagnosticsReview/sourceIdentity/consumerFiles`。

## Findings（severity、证据与最小修正）

### D01 / P2 — 并发移除filter可使另一attempt静默漏记

**位置：** `src/fsq_androidworld_eval/evaluator_diagnostics.py`，`EvaluatorDiagnostics.__enter__:130–134`、`__exit__:139–146`，主要是 **142–144** 的原地 `logger.removeFilter(self)`。

Python3.11 `logging.Filterer.filter` 直接迭代共享 `filters` 列表，`removeFilter` 原地删除。列表为 `[A,B]` 时，B线程刚调用完A的thread-mismatch filter、尚未迭代下一项；A线程退出并删除A，B向下标0移动，B线程迭代器继续下标1即结束。B的in-scope记录跳过自己的capture，正常sink仍收到，却没有对应dropped/error计数，sidecar可以标成 `written`。

**新增、实际执行的最小证据：** 仅用隔离stdlib `Logger`，阻塞A.filter→移除A→恢复dispatch；输出 `thread_finished=True, B_still_registered=True, B_observed_records=[]`。没有root/absl改动、文件写入或运行owner测试；它验证的是helper所用stdlib primitive的竞态，而非声称已在真实runner attempt看到丢失。

现有 `tests/test_evaluator_diagnostics.py:291–319` 在两线程日志之后、detach之前又做barrier（303），恰好排除了该交错，不能证明detach/dispatch安全。

**消费者风险：** concurrent receipts的原生拒绝证据可无提示消失；不据此声称已有历史attempt丢日志或评分值变化。

**最小修正：** 对管理中的root/absl注册采用序列化更新的immutable/copy-on-write filter快照，或等价的稳定dispatcher，保留外部filters/sinks/level。仅锁 `removeFilter` 或filter函数无效，因为stdlib迭代器不取该锁。补确定性交错的consumer回归，未由本review实施/运行。

### D02 / P2 — 未支持对象的类型名绕过投影字符上限

**位置：** `evaluator_diagnostics.py`，`EvaluatorDiagnostics._value` **58、83**；序列化发生在 `filter:113`、`__exit__:173`，均在byte-limit判断之前。

两个省略分支直接保存完整 `kind.__name__`，不按metadata长度或剩余字符预算裁剪/扣减；节点耗尽分支也如此。异常参数中的超长类型名不能被后续仅删log/frame的envelope缩减循环裁掉。

**新增、实际执行的最小证据：** 在内存执行本helper的 `_value(type('T'*10000,(),{})())`，未进入context、未注册logger、未写文件。结果：`MAX_VALUE_CHARS=2048`，`omittedType` **10000字符**，JSON投影 **10066 bytes**。

**消费者风险：** 声称的单投影字符上限不成立，临时JSON分配/CPU可随任意type-name长度增长，发生于byte检查之前。**这不证明成功落盘文件超过64KiB**；最终写入仍被长度检查限制或成为 `write_failed`。未证明当前native task会触发，也未证明隐私外泄。

**最小修正：** 任何省略分支（含node-limit）都应在copy/encode前应用小metadata cap和剩余共享字符预算并扣减；预算耗尽不能退回完整类型名。不需要类型名时用固定literal省略标签更简单。应补长类型名/异常参数的有界consumer回归，不只检查最终文件大小；本review未修改/运行。

### D03 / P2 — 类型判断调用用户metaclass hook，可由观测本身中断评分

**位置：** `evaluator_diagnostics.py`，`EvaluatorDiagnostics._value` **73** 的 `kind in (tuple,list,dict)`；`filter:121` 仅捕获 `Exception`。相关的58/83及 `_exception:95` 的普通类型名属性访问也可能派发metaclass hook（此部分为静态分析）。

membership会比较类型相等而非只做identity，因而可调用对象所属metaclass的 `__eq__`。

**新增、实际执行的最小证据：** 内存调用本helper的真实 `filter`，输入标准 `LogRecord(funcName='probe')`，args含一个自定义metaclass对象；该metaclass保留 `type.__hash__`，`__eq__` 抛 `SystemExit`。输出：`events=['metaclass_eq']`、`escaped_exception_type='SystemExit'`、`captureErrors=0`；未调用 `str/repr`，无context/root/absl/文件操作。初始合成fixture需补hash与非空funcName才能到达目标分支；报告结论来自修正后的有效record，不把fixture构造错误算产品失败。

**消费者风险：** 即使原sink不format该对象，诊断观察也能额外执行其代码，使本可返回的evaluator在logging调用处abort；`runner.py:817` 的 `except Exception` 同样不会包含这个 `SystemExit`。**runner的finally通常仍会执行cleanup**，不声称该例必然绕过cleanup，也未声称真实native task曾触发。已有native异常在exit时被替换属于进一步静态风险，本次未证明。

**最小修正：** 改成 `kind is tuple or kind is list or kind is dict`。同时去除普通type-name访问的用户hook表面：可取 `type.__dict__['__name__']` 的builtin descriptor，再用builtin str操作做D02所需裁剪；仅 `type.__getattribute__` 仍可能解析metaclass自定义descriptor。或者使用固定标签。**不要仅扩大BaseException捕获来掩盖问题**，那仍会执行/阻塞在用户hook里。需行为回归证明observer不触发该hook且不改变evaluator结果，本review未实施。

## 其余验收结论与边界

### 唯一评分、分类、超时与cleanup

`runner.py:791–808` 只有一次 `task.is_successful(env)`，直接赋原reward，无coercion、二次评分或组件猜测。metadata在原调用的finally记录；helper普通IO异常在 `__exit__:197–202`转为诊断失败reference，普通native evaluator异常继续传播到 `invalid_evaluator`；`runner.py:829–887`原分类/cleanup/exit路线保留。**D03是额外的observer outcome风险，不能据普通路径通过而忽略。**

budget/timeout数值没有重置或扩充。sidecar IO位于评分后、teardown前，在原campaign subprocess deadline内；bounded bytes不是bounded延迟。storage卡顿仍可延迟cleanup；owner已明确披露，不声称零wall-clock变化。

### 隐藏信息与公共error安全收窄

新result只带relative path/hash/status/bytes，或 `write_failed/errorType`，不带native args、log template或frames；exception frames不保存locals。Agent prompt在capture前组装，sidecar在Agent退出后产生，未找到新数据流把它送进prompt/normalized events。

**预存边界：** filters保持透传，不抑制原有sinks；native expected-row warning仍可能出现在继承stderr/日志目的地。仅“主result与Agentprompt无值”不能证明所有原生输出独占raw-private，更不等于验证了OS sandbox保密性。这不是本patch新增泄漏，也不把已有sink视为已完成安全审计。

`runner.py:820–827`仅对evaluator error收窄成type。已核对：`scorer.record_classification:209–220`先用invalidReason，再看error存在性；cleanup/provenance、campaign的异常终态处理也不依赖evaluator message/traceback。已有campaign/scorer测试fixture本就使用type-only错误；新 `tests/test_evaluator_diagnostics.py:193–213`检查 `invalid_evaluator`、公开隔离及cleanup。找到依赖message的测试是未改的preparation/rehearsal错误，不属于runner evaluator分支。**已知仓库消费者兼容这次安全收窄；外部私有脚本未审核，不能保证它们兼容。**

### Logger lifecycle、嵌套与资源

不改handlers、global/effective level、propagate或formatting；只观察direct root/absl与当前线程。propagated child logger不经过ancestor logger filter，其他线程/输出通道或已被level/filter抑制的记录不可见，文档已有该限制。

D01说明concurrent detach尚不安全。单实例reuse/reentrant保留/覆盖内部状态；同线程distinct nested captures会同时观察重叠区间，**不提供exclusive attempt ownership**。当前runner每次新建single-call context且无nested caller，不将未被当前调用方使用的形式另立源码finding，也不宣称它们已安全覆盖。普通attach/remove Exception会计数，失败移除留下inactive filter；没有测试/证明任意hostile logger或异步异常都安全。

普通literal使用exact builtin类型、字符/node/depth/items上限和Unicode slicing，填满record/log-byte预算后跳过后续projection。D02/D03是上述安全假设的例外。已有1000-record测试不覆盖type-name/metadata hook，也不是无限flood CPU、任意sink或磁盘延迟保证。

### Sidecar状态、原子性与测试质量

`helper:185–202`新建private dir0700、exclusive temp0600、close后原子replace、finally清temp；既有supervisor先创建raw-private0700。失败reference不返回虚假有效path/hash，普通IO错误不替代原evaluator错误；不宣称fsync持久性、symlink攻击或OS越权攻击已验证。silent scalar保留 `componentResults.not_provided`，`written`只代表限定观测面文件写出，不代表完整分项/所有日志。

新增测试大多使用真实runner/scorer/native row predicate并读取持久JSON/hash，只替换外部设备/进程边界，具有consumer价值而非mockecho/wording。它们未覆盖三项finding；owner26passed/5smoke不能作为这些新边界的证明。本review没有增写永久测试。

## 关键检查：沿用既有Harness identity，helper没有被漏hash

- `campaign.py:194–211`使用现有 `src/fsq_androidworld_eval/*.py` glob，加 `pyproject.toml` 后交给原 `_paths_digest:133–138`；新helper即使untracked也已在集合内。**无需新增第二套identity。**
- manifest producer：`campaign.py:419–420,520–521` 写入runtimeIdentity。live `_load_manifest:624–668` 比较当前完整identity；run入口1386–1389与qualify入口1584–1587调用该检查。
- readiness：`preparation.py:367–370`绑定包括runtimeIdentity在内的manifestSha256；`campaign._readiness_identity:820–837`重验。不是仅pin runner文件。
- inheritance/migration：`continuation.py:54–66`允许新Harness相对历史source演化；current_stack `runtime_migration.py:58–72`要求observed target与审批identity精确相等。这不等于新manifest钉住后允许helper静默漂移。
- offline scorer：`scorer.py:686–699,717–735,788–791`检查记录中的migration、manifest/readiness/checkpoint绑定；recovery `campaign.py:1251–1256`重验live manifest。离线历史审计**不拿今天checkout重新散列来否定历史**，也不冒称该路径已验证当前installed imports或新sidecar内容。

**新增只读计算证据：** AST提取并执行现有 `_paths_digest`，对当前既有glob集合计算，20个path，helper included=True：
- 包含helper：`c64470ac2a06d05ac6ecd727832bebb7f5ccfd941766336ad9225ded0dd23e7f`。
- 去掉helper：`235acb09bad34e73d1f4e0b81d469bdf4f988765715ed37ce4b8847dfcb52232`。

digest不同，证明实际集合含helper；只做内存中的成员/源码hash计算，**未执行完整 `_runtime_identity`、版本探针、manifest准备或资格检查，也未部署另一套hash机制**。完整身份仍会受第一批dirty-submodule等门槛阻止；未来修正这些findings后必须重新锁新bytes，不复用本快照当开跑许可。

## 本review实际验证与交接

实际执行：限定源码/消费者/owner收据阅读、SHA256；Python3.11.16下三个新增无文件内存边界probe（stdlib移除竞态、helper长type-name、helpermetaclass hook）及原identity函数集合计算。两个辅助reviewer只做静态核对，没有运行任何probe/tests或写文件。

未执行：owner26-test或5smoke重跑、任何项目测试套件、真实runner/evaluator/device/Agent/sandbox、安装/build/新manifest/qualification/发布、历史重评/原日志变更、服务操作/commit/push。本次不声称真实设备行为或性能已获证。

首批Markdown原文SHA256 `c222426a83b209590cf83cd8c6b5ed66cb72400b7341bd9132c1559ee77d382f`；原JSON SHA256 `d4a7b84c6b1aa90b78f992ce444943c7193c37bc04e5ff6120c491561f55a582`。附录保留原Markdown为byte prefix、原JSON全部成员值不变，只新增 `diagnosticsReview`。

**交接：第二部分review完成，请实施owner修正D01/D02/D03后再提交相应新边界证据；本review不改实现。第一批contract结论与未来identity/安装/manifest/qualification门槛原样保留。定时服务未受影响。**


---

# 第三部分：D01–D03 定向收尾复核

时间：2026-11-10T11:23:37+08:00。**D01 / D02 / D03 均 resolved；本定向范围剩余源码finding为0。** 仅核对这三项修正、关联runner边界与新增consumer测试；未扩展审计。本段更新最新disposition，前述原finding、失败证据、旧hash和首批contract结论均原样保留。

依据实施者 `evidence/evaluator-private-diagnostics-20261110/verification.json#/corrections/0` 与 `implementation.md:122–198`，核对实际修正源码和新增测试，而非仅接受“已修复”文字。**未重跑32tests、旧26tests、定向smoke或旧5场景；没有额外probe的必要，因此本次未执行运行时反证。** 下列32passed/smoke事实只归属实施者证据，不算独立复核者执行。

## 原finding逐项闭合

| Finding | 最新状态 | 实际代码与consumer边界证据 |
|---|---|---|
| D01 / P2 | **resolved** | `evaluator_diagnostics.py:34–36,153–176`：模块私有锁串行化管理更新；进入/退出都赋新filters list，旧dispatch迭代器持有旧快照；退出用identity保留foreign filters及顺序，不改handler/level/propagate。`tests/test_evaluator_diagnostics.py:328–399` 的root/absl两例暂停B于真实A.filter之后，让A完整退出再恢复B；检查两份实际receipt各自记录、零drop/error、原有与后加foreign filter/order、sink不变。覆盖原缺失交错，不是加计数器掩盖漏记。 |
| D02 / P2 | **resolved** | `evaluator_diagnostics.py:31,37–51,72–124`：builtin descriptor取名引用；编码前builtin str长度/切片限制128字符并扣共享2048预算；普通省略、node耗尽、容器标签皆使用同一路径；exception type与args共用预算，裁剪计omission。`tests:402–448` 用10k类型/异常名，覆盖node/character耗尽；在真正json.dumps之前审查metadata，再读取落盘receipt检查cap、truncated及原异常保持。不只依赖最终64KiB文件检查。 |
| D03 / P2 | **resolved** | `evaluator_diagnostics.py:80–109` 用 `kind is tuple/list/dict`；`37–51`绕开metaclass equality/name lookup/descriptor与str子类hook；普通省略、容器、异常及write-error取名均统一；`runner.py:116,820–822`的evaluator公开error也使用该helper。未扩大BaseException捕获。`tests:451–522`及fixture `32–72,145–159`让恶意equality/name/descriptor/str-repr hook可抛SystemExit，走真实offline runner返回、原生异常、写盘错误三条路径，检查zero hooks、唯一evaluator调用、原reward/分类/terminal/cleanup和真实JSON错误/私有元数据。 |

D01保证明确限于**本helper管理的更新**；不承诺任意第三方同时原地改filters也安全，这不是原D01未闭合。D02的共享预算限定retained literal/type-name，固定schema key/reason和分别有cap的source/frame字段不混计。D03保留原非evaluator runner错误路径，不借此扩展迁移/审核范围。上述限制与实施文档一致。

新增6个parametrized consumer case分别是D01×2、D02×1、D03×3，有实际record/receipt/评分边界断言，不是wording/wiring/mockecho。实施者记录一次 **32 passed / 2 warnings / 0.51s**；定向smoke记录A/B不串/不丢、10k类型截到128且sidecar2208bytes、恶意metadata零hook且原reward/cleanup保持。**本次只读取代码和这些收据，没有再运行。**

## 修正后实际源码hash

以下三项本次独立散列，均与 `corrections[0].sourceSha256` 完全匹配。它们是本轮修正review快照，不是完整runtime/installed或新manifest的准入证明。

| 文件 | 修正后SHA256 |
|---|---|
| `src/fsq_androidworld_eval/runner.py` | `a5864ca8edd0a00af6903ea27b4df84fb73630f6759de2105a9d463cb4fb766c` |
| `src/fsq_androidworld_eval/evaluator_diagnostics.py` | `d231b78432685fc61787a49a3a3cc3b0f31e7567498d90c33fce59192f80febc` |
| `tests/test_evaluator_diagnostics.py` | `95f091f2384889430aab4f00d839933f5fcd2946851ef98a7516f62b67d31977` |

交付证据实际bytes：
- `implementation.md`：`edb76403177d42154554ccb242a3d941c913385a658f32cc1f73b3790768b50a`。
- `verification.json`：`7e44cb90737500675277b7a837e0d7e2254a7bc1ece64cea749c1721e1ddf8bf`，只读取其 `corrections[0]` 作为这次定向运行证据。

追加前完整review收据：Markdown `97e7f914073cabc445c249e10c204645a539d6d57a7abfa98ba3e283b7750877`；JSON `dcdae789b81bd2c416b14aada52fed2bfa1ae3c4b00c5a6e0276c2af1020adf0`。旧Markdown保留为byte prefix；旧JSON成员（包括旧finding和旧sourcehash）不改，仅新增 `diagnosticsClosure`。

## Scope / remaining / 交接

- **本范围：** D01–D03 resolved，unresolvedOriginalFindings=[]，无新增定向finding；无须再改这三项。
- **仍open：** G1未来完整source identity、G2 installed/import验证、new manifest与fresh qualification。这些是整合/开跑门槛，**不是未解决的代码P2**；本次未尝试关闭，也未重审既有identity消费者。
- **保留原review limits：** 既有日志sinks/coverage、磁盘延迟、没有native分项/最终DB快照、历史unknown不变。实际设备/Agent/sandbox行为未独立执行验证。
- **实际动作：** 只读修正代码、增量测试/fixture与owner收据，计算SHA256；仅追加本review.md/json。未改实现/测试/配置/实施者收据/原始结果，未安装/发布/commit/push，未操作设备、服务或定时器。
- 第一批001/014/076结论原样保留；`FSQRepairHourly01a1c098`未停止、未重配。

**交接：D01–D03独立定向收尾通过；最新机器收据为 `review.json#/diagnosticsClosure`。后续只需按另行授权推进仍open的整合/安装/manifest/qualification门槛，不把本次resolved扩大为新campaign资格。**

