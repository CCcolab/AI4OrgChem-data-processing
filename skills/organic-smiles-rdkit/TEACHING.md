# SMILES 与 RDKit

**分类：有机分子结构与身份识别** · Skill：`organic-smiles-rdkit`

[获取Notebook程序](NOTEBOOK.md) · [Colab运行与结果下载](RUNNING.md) · [返回首页](../../START_HERE_zh-CN.md)

本页介绍要学的知识、样本出处与结果解释。运行环境、参数填写、调用和下载操作集中在运行指南。

## 学习目标

| 层次 | 本页练习 |
| --- | --- |
| 跟随操作 | 读入SMILES教学样本，解析和保留异常记录，绘制结构，计算描述符与指纹相似度 |
| 独立解释 | 区分不同写法与不同分子；说明酸/酸根、盐、立体及同位素信息为何保留；解释指纹参数如何影响相似度 |

需要基本有机结构、官能团、电荷和立体化学知识。

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


[逐项知识来源与章节](sources.json) · [逐记录数据来源与哈希](data-provenance.json) · [14条原始教学记录](molecules.csv)

## 保存的示例图表

![有效分子结构及记录ID](example-molecules.png)

![相对于记录005的Morgan指纹相似度](example-similarity.png)

图表由已验收Notebook的RDKit和Matplotlib真实生成。两条错误输入保留在错误表，不画作有效分子；结构图仍保留盐、电荷、同位素与立体表示。

## 怎样解释结果

核对analysis.csv的原始字符串、规范表示、分子式、电荷与状态；errors.csv保留无效/空输入，duplicates.csv报告001/002重复映射但不删行。酸与酸根、两种已指定立体结构和13C记录应分别保留。结构图标出ID；相似度图以005为参照。radius=2改3时分子身份、分子式和描述符应不变，相似度可能改变；不要用相似度判定同一性。

结果中的MolLogP、HBD/HBA、TPSA是RDKit方法输出，不是本页测得的溶解度、活性或安全性。SMARTS匹配依赖查询约束，不等于普遍唯一的官能团计数。模型解释单独显示，数值以工具结果为准；模型文字未经专家独立认证。


## 自测

1. CCO和OCC为什么可以表示同一乙醇，而乙酸和乙酸根应分开？
2. @/@@为什么不能直接当作R/S命名？
3. radius从2改成3后，分子式与相似度分别应如何比较？

继续使用：[获取Notebook程序](NOTEBOOK.md) → [运行、修改参数和结果下载](RUNNING.md)。
