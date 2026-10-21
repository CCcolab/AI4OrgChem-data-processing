# 分析有机分子｜SMILES与RDKit

学习如何把有机结构表示转成可复核的分子分析结果，并实际使用`organic-smiles-rdkit` Agent Skill。面向已有基本有机结构知识的学习者；跟随操作为基础，独立解释需要掌握官能团、电荷和立体化学。无需8765、Docker或OpenAI API。

## 本页学什么

用乙醇、乙酸/乙酸根、苯、苯酚、苯甲酸、阿司匹林及明确的立体/盐/同位素教学结构，完成解析、规范表示、描述符、羧酸查询、Morgan指纹和相似度分析。样本含14条记录，其中2条故意无效；它们必须留在错误表，不能静默删除。结构图用RDKit真实绘制，不用生成式图片。

本例不做结构编辑、去盐、中和、互变异构归一或PubChem查询；这些仍属于通用Skill的其他任务范围，不能继承本页验收。

## 必要知识与参考资料

| 知识点 | 在有机化学中的用法 | 具体出处 |
| --- | --- | --- |
| SMILES连接、芳香性、电荷与组分 | 区分苯环、官能团、离子和盐，保留原始结构 | [Daylight SMILES §3.1–3.2](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html)；[AI4Chem Lecture 3 §1](https://zzhenglab.github.io/ai4chem/lecture-03.html) |
| 同位素与局部立体编码 | 不凭@/@@直接命名R/S；不为未指定中心补构型 | [Daylight §3.3.1–3.3.3](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html) |
| canonical isomeric SMILES | 同一版本下比较规范表示；不自动合并酸碱、盐和互变异构体 | [RDKit Reading and Writing Molecules](https://www.rdkit.org/docs/GettingStartedInPython.html) |
| SMARTS查询 | 本例`[CX3](=O)[OX2H1]`查找含OH的羧酸片段，不把乙酸根合并为乙酸 | [Daylight SMARTS §4.1–4.3](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html)；RDKit Substructure Searching |
| 描述符 | MolWt为平均分子量数值（g/mol）；MolLogP是模型估计；TPSA按拓扑规则计算（Å²） | [RDKit Descriptors](https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html)；[Crippen MolLogP](https://www.rdkit.org/docs/source/rdkit.Chem.Crippen.html) |
| Morgan bit指纹与Tanimoto | 参数一致时比较结构特征；位碰撞和参数选择影响相似度 | [RDKit Morgan Fingerprints](https://www.rdkit.org/docs/GettingStartedInPython.html#morgan-fingerprints-circular-fingerprints)；[生成器API](https://www.rdkit.org/docs/source/rdkit.Chem.rdFingerprintGenerator.html) |
| Murcko骨架 | 提取算法定义的环系及连接部分；无环分子的空骨架单独标记 | RDKit Getting Started — Murcko Decomposition |

对本页非空位集合，Tanimoto为：

$$T(A,B)=\frac{|A\cap B|}{|A\cup B|}$$

程序同时用RDKit接口和Python位集合独立核算；空并集约定1。该分数不是活性相同概率，也不是严格可计量的“共同化学特征百分比”。

## 数据从哪里来

`molecules.csv`为本项目编写的教学结构集：课程中出现的简单结构，加上用于检验表示、电荷、手性、同位素和错误处理的记录。不是实验数据、临床数据或数据库批量下载。009/010仅标记相反局部手性，不凭符号指定R/S；011/012为故意无效输入。逐记录说明、来源和SHA-256见`data-provenance.json`。

课程§1.3把两个不同结构写成“same structure”的示例不照搬，本页使用CCO/OCC演示同一乙醇的两种写法。程序依据官方接口并实测，不复制课程示意数值或图片。官方网页显示版本可能晚于本页固定包，实际运行记录和接口测试才是本例版本依据。引用开放可读资料不代表取得整篇再分发许可；保留链接与归属，代码许可沿用项目现有安排，不擅自新增许可证。

## 运行与参数

在线阅读本Notebook；交互运行时将此.ipynb上传Colab并在自己的账号保存副本。当前仓库私有，不提供未经验证的匿名GitHub下载链接。依赖安装到本次会话独立venv：Python 3.12/3.13兼容、RDKit 2026.3.6、NumPy 2.4.6、Matplotlib 3.11.2；安装失败会停止，记录实际版本。CPU即可，无需GPU。每次最多50条，API最多3轮，每轮60秒，不自动重试；外层230秒停止，终止进程和保存回执另留15秒，不增加科学计算预算。

| 参数 | 默认 | 范围/意义 |
| --- | --- | --- |
| radius | 2 | 1–4整数；修改为3比较局部邻域扩展 |
| fp_size | 2048 | 1024/2048/4096，固定长度bit指纹 |
| include_chirality | true | 指纹和匹配是否使用手性；规范身份始终保留立体信息 |
| query_smarts | `[CX3](=O)[OX2H1]` | 合法且非空的SMARTS；本例查羧酸 |
| reference_id | 005 | 必须是有效记录ID；默认苯 |

调用模板见`task-template.txt`；参数模板见`parameters.json`。Skill原文默认交付代码，本Notebook由用户明确提交执行，使用已审阅的白名单适配器，不执行模型任意生成代码。密钥配置见下方说明及`CONFIGURATION_zh-CN.md`。

## 怎样解释结果

核对analysis.csv的原始字符串、规范表示、分子式、电荷与状态；errors.csv保留无效/空输入，duplicates.csv报告001/002重复映射但不删行。酸与酸根、两种已指定立体结构和13C记录应分别保留。结构图标出ID；相似度图以005为参照。radius=2改3时分子身份、分子式和描述符应不变，相似度可能改变；不要用相似度判定同一性。

结果中的MolLogP、HBD/HBA、TPSA是RDKit方法输出，不是本页测得的溶解度、活性或安全性。SMARTS匹配依赖查询约束，不等于普遍唯一的官能团计数。模型解释单独显示，数值以工具结果为准；模型文字未经专家独立认证。

## 保存与下载材料

本页提供原生Notebook、调用/参数模板、样本、精简源码及运行结果ZIP。运行结果包括输入、参数、环境、CSV、图表、科学检查和脱敏调用回执；下载后以清单复核SHA-256。先运行再保存自己的执行Notebook，未运行的模板没有执行输出。
