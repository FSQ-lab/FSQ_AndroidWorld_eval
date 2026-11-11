# 033 MarkorMergeNotes：父复核

## 本项结论

最明确的问题是模型的完成验收漏项：它验证了自己计算的单换行内容与不含扩展名的显示标题，没有核对完整保存名称及源换行保留。原UI已证两处相对实际判分契约的差异；不是已发现AMKernel执行故障，也不是已证明的014式展示数据/reference改写不一致。任务措辞对扩展名及new line/blank line有歧义，不能把这种歧义自动等同于任务无解或评分器实现错误。

本项没有修改生产、技能、任务、evaluator、依赖或冻结成绩。离线诊断不触发新跑、设备查询或下一项。原reward仍为0.0。

## 来源

证据目录：`evidence/markor-merge-diagnosis-20261109T090714Z/`。原来源为r12 v2 `033-MarkorMergeNotes/attempt-1`，seed `2594989658`，params SHA256 `83d348ecd71eee0838de42e16ede8c5725cd63bf2b70490f4149eaf41fce8868`。

- result SHA256：`e563c89d457aa19ce08b8c4bd0473c8a3e8f0e20317fa427dcb253f7b5bd7ca0`
- raw SHA256：`2d62d4adb8a73459945dba97a5cc8db14b6eac61127eb0ac516d759ccd56db4b`
- normalized SHA256：`a695eab6128571af8ed0d37612b3337f9e00167f5f3bdd7839dfeb81a1736512`

父逐原raw提取18对code/response，另见本目录 `original-python-executions.json` 与 `original-source-identity.json`。原17/78业务动作、18个reference steps；18次Python调用中17 completed、1 failed，全部kernel alive，无timed_out。

## 最早可证偏离及完成误判

1. exec11/12（raw2086/2087、2275/2276）：从三个指定原文件读取的source1/2/3都以LF结尾，内容与原params一致。
2. exec13（raw2561/2562）：创建对话框有独立name、ext控件，ext默认`.md`，type为Markdown。
3. exec14（raw2875/2876）：原调用代码含非法换行字符串，编译报SyntaxError line9，尚未执行动作。父离线直接parse该原请求亦失败；exec15代码可parse并恢复，不是未恢复的官方0分原因。
4. exec15（raw3338/3339）：只修改name为`mIObBbo4`，未修改ext；主动rstrip每份源末尾CR/LF后，以单LF拼接三份内容，保存并读回。
5. exec17（raw3807/3808）：实际按`File mIObBbo4.md`定位并重开；列表完整描述确认`.md`。正文恰3行、0空行，与三个原params以单LF拼接完全相同。
6. exec17的`matches=True`只比较base title为`mIObBbo4`及正文等于自己的`merged`，不能证明满足完整文件名称及官方格式要求。没有证据表明模型直接键入`.md`；它保留了默认扩展名。

## 实际判分契约与已运行验证

父亲读实际安装 `markor.py:535–638`、`file_validators.py:166–226` 及所有者 `owner-scorer-source-proof.json`。

- constructor将无扩展名`mIObBbo4`传入CreateFile，期望三段以双LF分隔。
- CreateFile先要求精确完整路径存在，无`.md`/`.txt`别名容忍；不存在即返回0。若存在才cat同一路径并fuzzy匹配。
- Merge仅在CreateFile通过后再检查正文，去CR、strip后必须5行，索引1和3为空行。
- 父实际运行安装中的fuzzy函数，并从实际Merge方法AST提取最后三句纯layout块执行原exec17正文：fuzzy=True，但layout=0.0；受控constructor双LF参考候选layout=1.0。未调用完整is_successful、未构造环境或伪造文件系统。
- 独立方另行运行实际纯函数/原AST表达式：原UI正文fuzzy ratio约0.97638、strict=False；双LF参考strict=True；受控仅`.md`路径集精确存在性False、受控无ext目标路径集True。这些候选不是历史find或新reward。

对应收据：`parent-original-field-evidence.json`、`parent-installed-pure-predicate-smoke.json`、`parent-original-code-parse-smoke.json`、`independent-033-contract-smoke.json`。

## 不能越过的边界

原 `v2-ready-run-full.log:583–601` 是18steps后done；所有者按前34项原reference步数序列归属该段。父亲读该段，未见具体existence/fuzzy/layout失败消息。CreateFile失败使用INFO日志，原log未保留目标名称或原find/cat返回，原attempt也没有note文件dump。

因此：

- 不能声称已直接观察原次首个返回分支，或把后置layout检查说成原次实际已执行。
- 不能把原UI正文当作无扩展名目标文件的历史cat内容，或假定原find只含`.md`文件。
- 未验证当前UI可保存无扩展名；不能把“清空ext即可通过”当已实测修法。
- 本项不证明任务无解、残留污染、AMKernel改写内容或评分器代码错误。

## 修复与操作范围

现有技能 `amkernel-appium.md:130–133` 已要求核验真实请求结果而不是成功点击。本项证据指向模型具体完成验收未覆盖完整身份/内容约束，未证明新增AMKernel机制或技能补丁是必要修复；不添加benchmark答案特例。

本slice设备、Appium动作、新session、环境/任务初始化、回放、服务操作、安装升级、生产/技能修改均为0，无新增外部资源需要清理。不恢复或替换原失败，不启动下一项。
