# 本地Git评测记录归档（部分覆盖，不是全部证据备份）

## 保存范围

仅授权本地add/commit，不push、不创建远端、不安装LFS。原始记录字节、成绩、代码、配置和其他人的工作树修改均不改动。原index为空；通过精确文件列表纳入被ignore的记录，保留原`.gitignore`。

本次选择 **1296份既存文档，78,713,269字节**，另加本目录5份归档元数据。包含本次FSQ完整调查84份文档（report/cases/双方记录/独立笔记/验收）、正式阶段report、final-handoff报告/任务索引、冻结身份manifest，以及可安全纳入的既往amkernel与harness汇报/验收记录。逐文件选入路径和SHA256见 [selected-files.json](selected-files.json)。

## 整个evidence的扫描快照

| 范围 | 文件数 | 逻辑字节数 |
|---|---:|---:|
| 本次FSQ目录 | 15548 | 2,477,983,996 |
| 既往amkernel/共享harness及其他目录 | 18225 | 6,664,835,456 |

清单初始总计33,773文件、9,142,819,452逻辑字节，全部ignored（tracked=0、untracked-nonignored=0）。逻辑大小不是磁盘已分配块数或Git压缩体积。历史中只有名称明确含amkernel的目录单独标为historical-amkernel-named，不能据此把其余harness目录说成没有amkernel任务；精确顶层统计见manifest。

## 明确未保存的材料

本次 **32,477份既存文件、9,064,106,183字节未由此提交保存**。包括raw-private、模拟器COW、安装包/构建缓存、日志/二进制、历史深层过程记录、超过5MiB的文档、53个未跟随symlink，以及24份保守排除的敏感/私有候选文档。

完整可读逐文件状态见 [coverage.tsv](coverage.tsv)；其中git_state_at_inventory是扫描时状态，不是提交后的状态；selected_for_local_git_commit表示此次精确选入集合，实际是否提交以交付SHA的tree核验为准。字节统计是该次扫描快照；仍在写入的未选日志不宣称被冻结。

7个单文件超过100MiB，最大为约3.40GB的模拟器qcow2；全量新增超过1GiB，因此未强塞普通Git。详细路径/大小在manifest的filesOver100MiB。现有仓库无evidence归档提交或.gitattributes；全局虽配置LFS filter，本机git-lfs不可用，不擅自安装或自建LFS服务。

## 敏感信息边界

对1324份候选文档的82,631,137字节做了内容筛查，并补查1300份通过初筛文档中的明文凭据赋值；24份因潜在凭据/cookie字段、private命名路径或资源授权记录而整份排除。见 [risk-findings.json](risk-findings.json)，仅列类别/路径/大小，不含匹配内容。匹配是保守风险标记，不声称每项都是实际有效凭据。

未对排除的raw-private、二进制、压缩包和大文件给出“无凭据”结论；它们可能含会话/认证/设备或个人信息。已选报告也包含评测fixture数据和本地路径，本次仅获本地保存授权，**未通过公开发布审查，不得据此push或上传private材料**。

## 外部冻结材料与下一步

仅保留现有identity/candidate manifest中的外部路径/hash引用；未复制或搬动其他仓库、外部安装的FSQ/AndroidWorld、依赖wheel、evidence之外的campaigns。此Git提交不覆盖这些外部原件。

后续可在另获授权后选择：①对未保存raw资料做凭据/隐私清理审查并另建加密、校验和完备的离线归档；②在用户已有且明确授权的存储中保存大文件；③若确有需求，讨论受控LFS方案和容量后再安装配置。不能把仅有引用/清单说成原材料已备份。本次不执行这些后续选择。

## 核验

[manifest.json](manifest.json)记录选入/未覆盖边界。提交后只核验精确提交树、blob与当前目标文件、选中文档SHA及未夹带原工作树/index改动；不重扫此前649原artifact，不运行测试/设备/模型/重评。实际commit SHA、分支和tree核验结果由本次交付提供。

目录symlink核验补充：原Git ignored列表中的SDK `platforms`目录symlink也已按lstat加入未覆盖清单；未遍历、复制或移动其外部目标。
