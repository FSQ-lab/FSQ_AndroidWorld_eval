# 原r12v2 033 MarkorMergeNotes：离线调查

## 结论与边界

**已证实原Agent保存/重开观察与现有任务契约有两处差异：完整文件名带了默认 `.md`，正文只有单LF分隔的三行而非含两个空行的五行。** 这是本项原UI及原请求直接证据，不是拿其他任务或模型final替代。

实际安装scorer不容忍给目标名补 `.md`/`.txt`，并在模糊内容校验之后再严格检查空行。原UI三行字符串可通过原fuzzy，却不能通过后一个结构谓词。**原文件系统find/cat返回未留存，原日志没有本项scorer分支文本，因此不能把某个具体首return分支写成已经观察到，更不能宣称扩展名是唯一历史零分原因。**

本项离线诊断的可达证据已经取全；不需要、不授权为此新跑。没有修改AMKernel、技能、安装依赖、任务renderer/evaluator/参数、预算、重试或原成绩。不把查明差异称作已fix；不推进下一项。

## 原身份与来源核对

原attempt：`campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/033-MarkorMergeNotes/attempt-1/`。

Goal：

> Merge the contents of Markor notes tough_frog_2023_08_05.txt, proud_cat_edited.txt and 2023_08_21_friendly_koala.md (in the same order) into a new Markor note named mIObBbo4 and save it. Add a new line between the content of each note.

- manifest index33；complexity7.8；seed2594989658；paramsTransport为JSON；params SHA256 `83d348ecd71eee0838de42e16ede8c5725cd63bf2b70490f4149eaf41fce8868`。实际manifest参数与原result逐对象相同。
- 原17/78业务动作、18个reference steps；18个Python调用，17 completed、1 failed，全部Kernel alive，无timed_out；Agent正常完成、无预算耗尽。原officialReward为0.0，error/invalidReason均null；原task teardown和environment close已完成，原session quit成功并核实absent。
- 原result SHA256 `e563c89d457aa19ce08b8c4bd0473c8a3e8f0e20317fa427dcb253f7b5bd7ca0`；normalized `a695eab6128571af8ed0d37612b3337f9e00167f5f3bdd7839dfeb81a1736512`；raw `2d62d4adb8a73459945dba97a5cc8db14b6eac61127eb0ac516d759ccd56db4b`。
- 已从原raw独立提取18对完整code/response；18份code的SHA逐项匹配原result的codeSha256。父另有独立提取，未由本作者覆盖。完整数据见 `owner-original-calls.json` 与 `owner-raw-field-proof.json`。

## 实际安装的任务、文件与判分契约

实际导入路径均为本项目 `.venv/lib/python3.11/site-packages/android_world/`；7个直接相关源码均已核对SHA与安装distribution RECORD一致。原result版本为AndroidWorld0.1.0、revision55ddaf5edc6f6c25673aed343907d5b9dca66f84；当前文件/RECORD核对不是未留存历史安装树的逐字节证明。

- 具体scorer是 **`MarkorMergeNotes.is_successful`**（`task_evals/single/markor.py:603`），不是基类空白成功值；它先调用委托 **`CreateFile.is_successful`**（`common_validators/file_validators.py:199`）。基类TaskEval.is_successful只检查initialized。
- `markor.py:542–560`把 `new_file_name` 原样交给CreateFile，未补扩展名；reference正文是三段原参数按 **双LF** 拼接并加末尾LF。
- `env/device_constants.py:32`给出 `MARKOR_DATA=/storage/emulated/0/Documents/Markor`。本项期待的完整目标路径是 `/storage/emulated/0/Documents/Markor/mIObBbo4`，不含扩展名。
- `markor.py:562–582`先清理Markor任务目录，再初始化CreateFile，随后创建三份原输入文件。`file_utils.py:134–169`使用echo写入，所以原单行参数会带末尾LF；这与原UI读值相符。初始化没有创建合并目标。
- `file_validators.py:203–209`先调用 `file_utils.check_file_or_folder_exists`；不存在即0，尚不读取正文。
- `file_utils.py:228–258`取得原base_path下递归find结果，然后检查 `convert_to_posix_path(base_path,target)` 是否在完整路径集合中。**不是stem/basename匹配，不自动接受 `.md`/`.txt`，也不把同名子目录中的不同完整路径当成根目录目标。**
- 若存在，`file_validators.py:212–226`对同一个无扩展名目标cat，去CR、strip，再用原fuzzy比较内容；不匹配即0。
- CreateFile通过后，`markor.py:612–638`再次cat同一个无扩展名目标，去CR、strip，split("\n")后要求恰好5行且index1/index3均为空。原三段内容各20个字母数字，适用此结构检查。没有最终归一化为任意单LF分隔的逻辑。

以上源码锚点、实际scorer身份、具体源码hash和原日志窗口均在 `owner-scorer-source-proof.json`。

## 原UI/请求的逐时点证据

| 原exec / raw code、response行 | 实际观察或行为 | 能证明的范围 |
|---|---|---|
| 8 / 1530、1531 | Files列表含三份任务源note；父目录项显示 `/storage/emulated/0/Documents` | 当前任务文件列表，不是文件系统dump |
| 11 / 2086、2087 | 前两源UI文本分别为 `m4kMyOGWaENoPj6FqLjd\n`、`fxHXZsqrmnwYjXvte9pg\n` | 各自原UI读值带末LF |
| 12 / 2275、2276 | 第三源为 `f42GOjFWb2aKHogAFQSY\n` | 原第三源UI读值带末LF |
| 13 / 2561、2562 | 创建对话框name=`my_note`，独立extension输入框=`.md`，Type=`Markdown` | 本次创建前实际UI默认扩展名；不是模型已输入 `.md` |
| 14 / 2875、2876 | 原请求的code中引号内被实际换行截断，SyntaxError at line9 | 编译失败，整个cell未执行；不是前半UI动作已经落地 |
| 15 / 3338、3339 | 恢复后只改name为 `mIObBbo4`，未修改extension；把每份源末尾CR/LF rstrip，再用一个LF join，输入并点击Save | 名称/正文的真实构造请求及编辑器回读 |
| 16 / 3446、3447 | 标题为base名，编辑器仍回读三行正文 | 保存后当前编辑器观察，不是原判分cat |
| 17 / 3807、3808 | 返回Files，按 `File mIObBbo4.md`定位；实际listed为 `File mIObBbo4.md 10/15/2023, 15:34`；重开文本仍为三行；matches=true | 实际重开了带扩展名条目，且三行正文稳定可读 |
| 18 / 3867、3868 | quit返回成功 | 原会话清理，不是当前新操作 |

原重开正文是：

```text
m4kMyOGWaENoPj6FqLjd
fxHXZsqrmnwYjXvte9pg
f42GOjFWb2aKHogAFQSY
```

三段顺序和每段字符均正确；中间没有空白行。原Agent的matches只比较**隐藏扩展名的base title**和**它自己构造的单LF merged字符串**，没有验证完整目标名或空白行要求。因此“reopenedAndMatched=true”与官方0并不矛盾；该自检不是官方成功判据。

最早可定位的Agent行为差异在成功exec15：保留创建对话框默认扩展名，并主动去掉源末LF后按单LF拼接。不能把默认 `.md` 写成模型直接键入 `.md`，也不能从本轮未尝试清空extension推断无扩展名文件无法创建。

## 纯函数验证与两条条件失败机制

本作者仅构造未初始化的本地任务对象以读取委托params，调用实际安装的纯path/fuzzy函数，并对已知原UI字符串计算源码中的纯结构表达式；没有env/controller、initialize_task、is_successful、ADB或设备操作。见 `owner-pure-contract-smoke.json`。独立作者另有 `independent-033-contract-smoke.json`，两者不冒充原filesystem。

结果：

- path转换保留名字：无扩展名、`.md`、`.txt`是三个不同完整路径。
- 原exec17的三行字符串对构造reference的实际fuzzy为True，ratio `0.9763779527559056`。因此**不能说三行内容必然先在fuzzy分支失败**。
- 对同一原UI字符串执行严格5行空行表达式为False；构造reference自身为True。此结构差异不会被较宽松的fuzzy成功掩盖。
- 对原exec14请求做离线ast.parse得到相同SyntaxError；exec15改用chr(10)恢复。不需要修改AMKernel来接受语法无效Python。

条件分支必须分开：

1. **若**原判分find中只有 `.md`而无完整无扩展名目标，则CreateFile在existence分支先返回0；正文fuzzy和严格空行检查均未达。
2. **若**完整无扩展名目标存在且保存的正是原UI三行文本，fuzzy可通过，但Merge最终严格空行分支返回0。
3. 原文件系统输入未保存，无法排除未观察到的其他同名文件/实际cat内容。因此以上是由原观察和实际代码支持的充分条件机制，不是伪造的原分支追踪。

## 原run-full.log与历史文件留存缺口

已读 `evidence/headless-fullcoverage-20261107T004632Z/v2-ready-run-full.log:580–605`。本项属于583–601：18个Completed step，随后done。归属通过manifest零基顺序及前34段step-count与原result逐项一致来核对；日志本身没有任务名标签。

**该日志没有 `mIObBbo4 not found`、目标内容mismatch或原find/cat返回。** CreateFile失败提示在实际源码中是logging.info，但本留存日志没有这些消息。不能把没有INFO消息当成existence/fuzzy通过；也不能拿其他任务的warning补成本项实际分支。

原attempt只留result、normalized、raw agent events与空stderr，没有note二进制、原find路径列表或官方读取内容。对本campaign/evidence递归路径中的 `mIObBbo4*` 文件名搜索无命中；此项只声明命名路径检索范围，不声称穷举所有归档成员或外部临时目录。原result的evaluator摘要只保留0.0及完成状态。

原teardown已完成；Markor基类tear_down清目录，CreateFile tear_down还调用clear_device_storage。因此事后当前设备不能当作历史判分文件系统。本轮没有查询它，也不提出靠重跑补造历史。

位置证据限定为：原操作在显示三份初始化note的同一Files目录创建/重开，没有18调用之外的已登记目录跳转。**预期**绝对路径已由源码确定，**实际**保存绝对路径与无扩展名副本是否存在未有文件系统dump；不把目录UI/标题推成实际cat字节。

## 当前可收口的结论、修复状态

1. 原official0、正常Agent终止、原18calls及文件名/换行差异已证；不存在必须先恢复的timeout/死Kernel证据。
2. 原输出内容、名称与具体scorer的两处不一致已明确，不把014的renderer/reference问题套到033。本项没有类似marker追加造成的源字段/reference改写差异；源文件echo末LF与“额外插入一个换行”可得到双LF，因此不先判goal/reference矛盾。Goal对完整文件名（含扩展名）及额外空白行有隐含要求，可以建议未来版本表述更明确，但这不等于已认定任务契约bug，更不是AMKernel故障。
3. **真实首失败return分支仍不可直接确认**；缺的是原判分find/cat输入及分支诊断，而不是本轮还未调用设备。这个历史缺口不能由一次新运行恢复。
4. 本轮未实施任何fix，不声称AMKernel/技能缺陷，不把当前证据推为任务无解；没有新reward，也不修改原0.0。
5. 仅本项离线诊断收口。若未来讨论通用终态验证，应区分完整文件名与UI base title、原业务要求与自算字符串；不得为了拿1给Agent塞入冻结reference或修改本任务判据。本轮没有这样的生产改动或后续运行计划。

最终范围与不可变性见 `minimal-contract.json`、`immutability.json`、`zero-operations.json`、`summary.json`。独立验收由p2另行署名，本报告不代其宣布通过。
