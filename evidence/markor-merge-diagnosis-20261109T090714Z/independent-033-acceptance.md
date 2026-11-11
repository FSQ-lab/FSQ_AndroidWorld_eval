# 033 MarkorMergeNotes：独立离线验收

署名：**w4:p2 独立离线契约验收助手**。签署时间：**2026-11-09T09:15:14Z**。

目录：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/markor-merge-diagnosis-20261109T090714Z`。

## 裁定

**Owner最终五文件独立验收通过，仅限本项离线契约/完成验证诊断；不是fix验收。** 已亲读 `offline-report.md`、`summary.json`、`minimal-contract.json`、`immutability.json`、`zero-operations.json`。实际五件字节SHA均与 `owner-final-delivery.json` 最终版本一致，完整签署版本见本JSON的 `ownerFinalDeliveryAcceptance`。

已证原完成验证层有两处遗漏：保留创建对话框默认扩展名，未验证完整目标文件名；主动剥掉源末换行后按单LF合并，未验证空行结构。原模型没有直接键入`.md`；其成功输入只改basename。任务措辞有解释空间，但这不是已证实的014式renderer/reference矛盾。

**原实际首个返回0的分支缺证；严格空行检查不保证原调用到达。** 不把文件名当作唯一历史原因，不证明当前UI可保存无扩展名文件或任务不可完成，不把纯候选当原find/cat。现有证据足以离线收口，不做设备查询、回放、清空扩展名能力验证或下一项。

## 原身份与独立重验

原r12v2 manifest index33，seed `2594989658`，paramsTransport **json**，params SHA256 `83d348ecd71eee0838de42e16ede8c5725cd63bf2b70490f4149eaf41fce8868`。实际原result与manifest参数一致。目标为无扩展名 `mIObBbo4`，三源依次为 `tough_frog_2023_08_05.txt`、`proud_cat_edited.txt`、`2023_08_21_friendly_koala.md`。

原result/normalized/raw的SHA均独立重算，与父字段证据和已登记原件一致；完整hash见 `independent-033-original-evidence.json`。**全部18段code与18个response逐对象比对原raw，均与父提取一致**。17 completed、1 failed，全部alive；原17/78业务动作、18 reference steps、reward0。未沿用014或其他任务验收。

实际scorer身份为 `MarkorMergeNotes.is_successful`，委托 `CreateFile.is_successful`；不是基类的成功返回值。七个相关已安装源码由本作者独立对distribution RECORD核对一致。原版本字段记录AndroidWorld0.1.0 / revision55ddaf5edc6f6c25673aed343907d5b9dca66f84，不把当前RECORD核对冒称历史安装全树证明。

## 原UI/请求的确切因果位置

- exec11/12（raw2086–2087、2275–2276）：三源UI字符串均以LF结尾，与初始化echo行为一致。
- exec13（raw2561–2562）：创建前name=`my_note`，独立extension编辑框=`.md`，type=`Markdown`。这是实际默认值，不是模型输入后缀。
- exec14（raw2875–2876）：原请求本身含非法引号换行。独立`ast.parse`在line9失败；exec15可解析。SyntaxError在编译前发生，不能称前半cell动作已执行；它已恢复，不是未恢复的官方0阻断。
- exec15（raw3338–3339）：只把name改为`mIObBbo4`，未修改ext；对每份源执行`rstrip(CR+LF)`，再单LF join并保存。丢失源末LF发生在原模型请求代码，不是已证实的AMKernel传输改写。
- exec17（raw3807–3808）：实际按`File mIObBbo4.md`定位并重开；listed带`.md`，显示title隐藏后缀，正文恰3行、0空行、无末LF。`matches=true`只比较base title和自算单LF字符串，不是完整文件名/空行判据。它比final prose更强，但仍不是原官方find/cat输入。

## 实际契约及必要纯smoke

源码前缀：`.venv/lib/python3.11/site-packages/android_world/`。

- `task_evals/single/markor.py:542–560`把原名原样传CreateFile；reference是三段内容双LF join并附末LF。`562–582`创建三源，未预创建输出目标。
- `utils/file_utils.py:134–169`用echo写源文件；`228–258`用find结果的完整路径集合做精确membership，不是stem匹配，也没有`.md`/`.txt`别名。
- `common_validators/file_validators.py:199–226`先检查 `/storage/emulated/0/Documents/Markor/mIObBbo4` 是否存在，再cat同一字面路径，去CR/strip后fuzzy；不存在或fuzzy不匹配均可返回0。
- `markor.py:603–638`仅在CreateFile通过后再cat同一字面路径，去CR/strip并split，严格要求5行、索引1/3为空。

| 本作者实际离线核对 | 结果 | 证据边界 |
|---|---|---|
| 原exec17 UI三行字符串对reference的实际fuzzy | true，ratio0.9763779527559056 | 不是原cat内容，也不说明原existence通过 |
| 同一UI字符串执行原AST严格结构表达式 | false，3行 | 不证明历史实际到达该分支 |
| constructor双LF reference的受控候选 | 严格结构true | 不是新官方reward |
| 原existence表达式：受控路径集合只有`.md` | false | 不是历史find结果 |
| 同表达式：受控集合含精确无扩展名目标 | true | 不证明当前UI能创建该文件 |

以上仅调用实际纯helper、未初始化的本地constructor及实际源码AST纯表达式；**未调用initialize_task或is_successful**。父、owner的独立pure receipts已亲读，与本作者结果相符；本作者receipt不由其替代。

## 原首分支与语义边界

已亲读原run-full.log580–606；owner以manifest前34段step序列定位本项583–601，18steps后done。该归属是顺序证据，不是带任务名的分支trace。整份留存日志未找到本项文件名/三段内容，未保留原find/cat或目标not-found/mismatch INFO。**没有INFO不能反推某门已通过。**

因此只可条件性说明：若只有`.md`而没有精确目标，则existence先0、后续未达；若精确目标存在且内容同原UI三行，则fuzzy通过、严格结构0。没有原文件系统输入，不能选其中一个冒充实际首分支，也不能声称纠正其中一处即可保证1。

Owner限定检索未发现留存的目标note，原teardown已清理；本作者未查当前设备。新运行不能恢复历史原输入，这个缺口不作待执行行动。

源原文本本已带LF，保留其内容再额外插入一LF可得双LF，与reference相容；原成功请求则主动去掉源末LF。故结论落在**模型构造/完成验证层偏差**，不直接裁为任务内部矛盾。goal的“note named”与默认后缀、以及“new line”与保留源终止符，存在需要明示的表达空间；本轮不改任务语义，不新增别名、放宽空行或注入参考答案。

## Owner最终交付与只读收据

五文件实际SHA已逐件匹配最终交付manifest；summary最终SHA为 `87a1943f8d75640a84a27b003a333921c6a796d6fe30b5d9a7b660772c164995`。其中身份、原0分、两处差异、首分支未知、无fix/新reward、无待执行现场与下一项均一致。

Owner的2186历史/152技能/7源码收据已审阅相符；本作者不冒称重新执行其全量hash扫描，也不把零操作自报当作全主机命令审计。本作者独立范围是原033三件hash、18原始调用对及七源码RECORD，见 `independent-033-readonly-receipt.json`。

本作者零设备/ADB/Appium/session/env/init/is_successful/DB读取/回放/服务/build/lint/test suite/formatter/生产/依赖/技能改动；未覆盖owner、父或历史文件。只在本目录写本人署名证据。

产物：`independent-033-acceptance.md/json`、`independent-033-original-evidence.json`、`independent-033-contract-smoke.json`、`independent-033-readonly-receipt.json`。**本项独立离线验收完成，供父复核后交付；不推进下一项。**
