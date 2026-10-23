# SMILES 与 RDKit

分类：**有机分子结构与身份识别** · Skill：`organic-smiles-rdkit`

先学习结构表示、参数含义和输出判读，再运行本页下部的Python程序。

## 知识与数据来源

### 学习目标

需要基本的有机结构、官能团、电荷与立体化学知识。通过本例，辨别“同一结构的不同写法”与“不同化学身份”，读懂输入、参数和输出文件之间的关系。

### 本页学什么

SMILES描述结构，SMARTS描述查询模式；规范SMILES用于同版本下比较表示；描述符给出算法计算值，Morgan指纹与Tanimoto衡量所选表示的相似度。本例保留盐、电荷、立体与同位素信息，不做结构标准化或活性/机理推断。

### 必要知识与参考资料

**以下主体是语言规范说明和软件官方文档，并非“经典有机化学教材”。** 它们分别回答“符号怎样解释”和“程序怎样计算”。方法论文另列为延伸阅读；不把未核对的教材章节或未读全文列为已核验依据。

| 知识点 | 本例中的含义 | 资料类型与具体章节 |
| --- | --- | --- |
| SMILES的连接、芳香性、电荷、组分 | 保留苯环、离子、盐的结构身份 | 语言规范说明：[Daylight §3.2.1–3.2.5](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html) |
| 同位素与局部手性 | 不凭@/@@直接命名R/S，不补写未指定构型 | 语言规范说明：[Daylight §3.3.1、§3.3.3](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html) |
| 规范表示与结构解析 | CCO/OCC都表示乙醇；按本例RDKit版本核对 | 官方教程：[Reading single molecules、Writing molecules](https://www.rdkit.org/docs/GettingStartedInPython.html)；Daylight §3.1 |
| SMARTS子结构查询 | `[CX3](=O)[OX2H1]`查含OH的羧酸片段 | 语言规范说明：[Daylight §4.1原子、§4.2键、§4.3逻辑](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html) |
| 平均分子量、MolLogP、TPSA | g/mol、模型估计值、Å²；不当作实验测量 | 官方API：[MolWt](https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html)、[Crippen MolLogP](https://www.rdkit.org/docs/source/rdkit.Chem.Crippen.html)、[CalcTPSA](https://www.rdkit.org/docs/source/rdkit.Chem.rdMolDescriptors.html#rdkit.Chem.rdMolDescriptors.CalcTPSA) |
| Morgan指纹与Tanimoto | 半径、位数及手性设置影响比较结果 | 官方API：[GetMorganGenerator](https://www.rdkit.org/docs/source/rdkit.Chem.rdFingerprintGenerator.html)；[Fingerprints and Molecular Similarity](https://www.rdkit.org/docs/GettingStartedInPython.html#fingerprints-and-molecular-similarity) |
| Murcko骨架 | 提取环系及连接部分，无环分子另标为空骨架 | 官方教程：[Murcko Decomposition](https://www.rdkit.org/docs/GettingStartedInPython.html#murcko-decomposition) |

对本例位集合，$T(A,B)=|A\cap B|/|A\cup B|$，空并集约定1；程序用位集合独立复算。相似度1不能证明化学身份或生物活性相同。

延伸阅读：Weininger（1988）的[SMILES方法论文](https://doi.org/10.1021/ci00057a005)，28(1):31–36；Rogers与Hahn（2010）的[圆形指纹方法论文书目与摘要](https://pubmed.ncbi.nlm.nih.gov/20426451/)，50(5):742–754，DOI:10.1021/ci100050t。前者核对出版社书目，后者核对书目与索引摘要；不声称本次取得并核对两篇全文。

### 数据从哪里来

`molecules.csv`是本项目组织和核对的14条通用结构教学输入，包含重复写法、酸/酸根、芳香结构、手性、盐、同位素及两条故意无效记录；不是实验数据或外部课程数据文件。`source_id=project`是本例输入构造/核对标签，不是数据库下载标识。逐记录说明和文件哈希在`data-provenance.json`，方法依据在`sources.json`。

### 数据和模板文件

[runtime/molecules.csv](runtime/molecules.csv)为14条教学结构；[parameters.json](runtime/parameters.json)为五个参数模板；[数据来源](runtime/data-provenance.json)及[知识来源](runtime/sources.json)分别记录其出处。读取CSV时保留字符串ID；编辑参数副本后用`--params`传入，输入与参数保存在结果包中。

## 调用、参数与对应输出

默认：`python organic-smiles-rdkit.py --output ../results-radius2`；将参数模板中的radius改为3后，用`--params`传入并保存到另一新目录。

| 模板字段 | 本例值/范围 | 对应输出与应观察的变化 |
| --- | --- | --- |
| radius | 2；1–4整数 | 改为radius=3后，比较similarity.csv的tanimoto及analysis.csv的fingerprint_on_bits；分子式/描述符不应因此改变 |
| fp_size | 2048；1024/2048/4096 | Morgan位向量长度；改变会影响指纹碰撞和相似度 |
| include_chirality | True；布尔值 | 指纹及查询是否使用手性；不能据此删除原始SMILES中的立体信息 |
| query_smarts | `[CX3](=O)[OX2H1]` | analysis.csv的query_match_count；003、007、008各1，004乙酸根为0 |
| reference_id | "005"；有效输入ID | similarity.csv的reference_id均为005；苯与自身相似度为1 |

### 本页工具的输入与执行边界

本轮边界约定为`rdkit-bounded-teaching-v2`；五个分析参数及内置14条结构保持一致。

Python程序使用内置的14条教学输入，本页命令行不接受任意CSV输入。配套工具用于本地开发复核时要求：UTF-8、五列完整、ID唯一且为1–64位字母/数字/点/下划线/连字符（字母或数字开头）；1–50行，CSV不超过128000字节，SMILES不超过512字符、每个分子不超过128个原子。字段不接受控制字符或电子表格公式前缀。名称请放label列；结构列只接收SMILES，不接受名称后缀、CXSMILES或虚拟原子。无效结构按行保留，参照ID必须有效。

SMARTS不超过120字符、32个查询原子；匹配超过1000项时明确拒绝统计，防止将截断数当成完整结果。解析后原子索引从0开始，指向本轮RDKit分子，不是原始字符串的字符位置。接口依据：[RDKit名称与CXSMILES解析说明](https://www.rdkit.org/docs/RDKit_Book.html#reading-molecule-names)、[GetSubstructMatches与maxMatches](https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html#rdkit.Chem.rdchem.Mol.GetSubstructMatches)；本页固定版本另以实际接口和反例复核。

调用前复核全部运行资源，并在发送模型请求前检查输入格式和参照结构；模型只能使用一次限定工具，最多3轮请求、每轮60秒，不自动重试，不跟随API重定向。模型响应上限1MB；分析子进程230秒，超时后终止，清理最多15秒。失败不生成成功验收回执。每次运行生成独立结果ZIP，核对文件清单、CRC和SHA-256。以上是单用户教学任务边界，不是多用户服务的负载能力保证。

### 实际参数调用案例与输出结果

下面是**同一输入、同一固定程序**在本地重算的两组保存结果，不是模型编写的数值。默认组严格采用上面的全部参数；对照组只把`radius`从2改为3，其余四项不变。两组均14条记录、12有效、2拒绝，16项程序检查通过。001/002规范表示相同但两行都保留；011/012进入errors.csv。

| ID | 分子式 | MolWt (g/mol) | 羧酸查询匹配数 | Tanimoto：radius=2 | Tanimoto：radius=3 |
| --- | --- | --- | --- | --- | --- |
| 001 | C2H6O | 46.069 | 0 | 0.000000 | 0.000000 |
| 002 | C2H6O | 46.069 | 0 | 0.000000 | 0.000000 |
| 003 | C2H4O2 | 60.052 | 1 | 0.111111 | 0.100000 |
| 004 | C2H3O2- | 59.044 | 0 | 0.000000 | 0.000000 |
| 005 | C6H6 | 78.114 | 0 | 1.000000 | 1.000000 |
| 006 | C6H6O | 94.113 | 0 | 0.272727 | 0.214286 |
| 007 | C7H6O2 | 122.123 | 1 | 0.214286 | 0.166667 |
| 008 | C9H8O4 | 180.159 | 1 | 0.125000 | 0.093750 |
| 009 | C4H10O | 74.123 | 0 | 0.000000 | 0.000000 |
| 010 | C4H10O | 74.123 | 0 | 0.000000 | 0.000000 |
| 011 | — | — | — | 拒绝 | 拒绝 |
| 012 | — | — | — | 拒绝 | 拒绝 |
| 013 | C3H10ClN | 95.573 | 0 | 0.000000 | 0.000000 |
| 014 | C2H6O | 47.061 | 0 | 0.000000 | 0.000000 |

数值在表中按显示精度舍入，CSV保留程序精度；“—/拒绝”不是0或缺失值填零。程序生成的图对应**默认组radius=2**：

![默认参数下的结构与ID](assets/example-molecules.png)
![默认参数下相对于005苯的Morgan相似度](assets/example-similarity.png)

| 输出文件 | 与本次调用的对应关系 | 阅读方法 |
| --- | --- | --- |
| parameters.json | 保存实际使用的五个参数 | 先核对与本次参数文件完全一致 |
| analysis.csv | 14条输入的逐行结果，含解析状态、原结构、分子式、描述符及匹配数 | 按id对齐；拒绝行不当作零结果 |
| errors.csv / duplicates.csv | 分别保留011/012及002→001映射 | 错误/重复只报告，不静默删除 |
| similarity.csv | 有效记录与reference_id的指纹相似度，含独立位集合核算 | 比较同一id在两组参数下的值 |
| numerical-result.json | 记录数量、参数、方法环境和16项检查 | 确认参数与checks；不把模型文字替代它 |
| molecules.png / similarity.png | 本次结构图和相似度图 | 用ID与输入及CSV对应 |

真实Agent运行后，还会得到`run-receipt.json`、`agent-trace.json`和`agent-explanation.md`；上面的**本地数值样例没有伪造模型调用回执或解释**。实际执行和文件下载状态以本轮程序回执及实际下载文件为准。

## 运行与下载

推荐下载[完整Python代码包](downloads/organic-smiles-rdkit-python.zip)，解压并进入该Skill目录。程序入口为[organic-smiles-rdkit.py](organic-smiles-rdkit.py)，同级保留`runtime`目录。单独下载入口文件不能代替完整代码包。

Windows PowerShell示例；先安装Python 3.12或3.13：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe organic-smiles-rdkit.py --output ..\results-default
```

macOS/Linux使用`.venv/bin/python`执行同样的安装和运行命令。默认模式只做本地数值计算，无需模型账号、API密钥或联网请求；依赖首次安装需要获取对应软件包。

完成后双击结果目录的`report.html`查看回执、参数和图表；保留`results.zip`及`results.zip.sha256`。报告为自包含HTML，没有外部脚本、输出框架或本地Web服务。代码输出`PASS_LOCAL_NUMERICAL`，明确表示没有调用模型。

### 修改参数再运行

复制[runtime/parameters.json](runtime/parameters.json)为自己的参数文件，按上表修改后运行到新目录：

```powershell
.\.venv\Scripts\python.exe organic-smiles-rdkit.py --params my-parameters.json --output ..\results-modified
.\.venv\Scripts\python.exe organic-smiles-rdkit.py --verify ..\results-modified
```

已有结果目录拒绝覆盖；`--verify`只核对文件和ZIP的SHA-256，不重复计算。

### 可选：让Agent读取SKILL.md并解释结果

`SKILL.md`是给AI助手的技能指令；`.py`是执行数值计算的程序。默认数值模式读取并记录Skill身份，不能把它称为真实Agent调用。确需模型解释时，再显式开启：

```powershell
.\.venv\Scripts\python.exe organic-smiles-rdkit.py --agent --env-file .env --output ..\results-agent
```

`.env`是自己已有的本地配置文件，程序只读其中`DEEPSEEK_API_KEY`，不把值写进代码、命令行、日志或结果包；不自动读取其它配置。该模式使用自己的DeepSeek账号和额度，不使用OpenAI服务。不配置`--agent`就不会读取密钥或调用模型。真实模式必须有实际工具调用回执，模型文字不能替代程序文件检查；本次迁移只做离线模拟验证，没有新增真实模型调用。

### 下载文件

- [完整Python代码包](downloads/organic-smiles-rdkit-python.zip)：入口、Skill、依赖清单及配套源码与数据。
- [查看Python入口源码](organic-smiles-rdkit.py) · [查看SKILL.md源码](SKILL.md?plain=1) · [依赖清单](requirements.txt)。

仓库为私有；取得完整代码包后，日常运行只需要本地Python环境。33项Skill按专业分类组织，本页仅承诺上述已实现的限定任务。
