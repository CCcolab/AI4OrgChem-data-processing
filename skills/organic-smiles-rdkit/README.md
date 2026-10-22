# SMILES 与 RDKit

分类：**有机分子结构与身份识别** · Skill：`organic-smiles-rdkit`

从有机分子的SMILES出发，调用Skill完成结构解析、描述符、SMARTS匹配和Morgan相似度分析。先了解本Skill涉及的知识点和数据，再查看调用示例；页面下部提供Notebook运行与下载入口。

## 知识与数据来源


### 学习目标

| 层次 | 本页练习 |
| --- | --- |
| 跟随操作 | 读入SMILES教学样本，解析和保留异常记录，绘制结构，计算描述符与指纹相似度 |
| 独立解释 | 区分不同写法与不同分子；说明酸/酸根、盐、立体及同位素信息为何保留；解释指纹参数如何影响相似度 |

需要基本有机结构、官能团、电荷和立体化学知识。

### 本页学什么

用乙醇、乙酸/乙酸根、苯、苯酚、苯甲酸、阿司匹林及明确的立体/盐/同位素教学结构，完成解析、规范表示、描述符、羧酸查询、Morgan指纹和相似度分析。样本含14条记录，其中2条故意无效；它们必须留在错误表，不能静默删除。结构图用RDKit真实绘制，不用生成式图片。

本例不做结构编辑、去盐、中和、互变异构归一或PubChem查询；这些仍属于通用Skill的其他任务范围，不能继承本页验收。

### 必要知识与参考资料

| 知识点 | 在有机化学中的用法 | 具体出处 |
| --- | --- | --- |
| SMILES连接、芳香性、电荷与组分 | 区分苯环、官能团、离子和盐，保留原始结构 | [Daylight SMILES §3.1–3.2](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html) |
| 同位素与局部立体编码 | 不凭@/@@直接命名R/S；不为未指定中心补构型 | [Daylight §3.3.1–3.3.3](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html) |
| canonical isomeric SMILES | 同一版本下比较规范表示；不自动合并酸碱、盐和互变异构体 | [RDKit Reading and Writing Molecules](https://www.rdkit.org/docs/GettingStartedInPython.html) |
| SMARTS查询 | 本例`[CX3](=O)[OX2H1]`查找含OH的羧酸片段，不把乙酸根合并为乙酸 | [Daylight SMARTS §4.1–4.3](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html)；RDKit Substructure Searching |
| 描述符 | MolWt为平均分子量数值（g/mol）；MolLogP是模型估计；TPSA按拓扑规则计算（Å²） | [RDKit Descriptors](https://www.rdkit.org/docs/source/rdkit.Chem.Descriptors.html)；[Crippen MolLogP](https://www.rdkit.org/docs/source/rdkit.Chem.Crippen.html) |
| Morgan bit指纹与Tanimoto | 参数一致时比较结构特征；位碰撞和参数选择影响相似度 | [RDKit Morgan Fingerprints](https://www.rdkit.org/docs/GettingStartedInPython.html#morgan-fingerprints-circular-fingerprints)；[生成器API](https://www.rdkit.org/docs/source/rdkit.Chem.rdFingerprintGenerator.html) |
| Murcko骨架 | 提取算法定义的环系及连接部分；无环分子的空骨架单独标记 | RDKit Getting Started — Murcko Decomposition |

对本页非空位集合，Tanimoto为：

$$T(A,B)=\frac{|A\cap B|}{|A\cup B|}$$

程序同时用RDKit接口和Python位集合独立核算；空并集约定1。该分数不是活性相同概率，也不是严格可计量的“共同化学特征百分比”。

### 数据从哪里来

`molecules.csv`为本项目编写的教学结构集：课程中出现的简单结构，加上用于检验表示、电荷、手性、同位素和错误处理的记录。不是实验数据、临床数据或数据库批量下载。009/010仅标记相反局部手性，不凭符号指定R/S；011/012为故意无效输入。逐记录说明、来源和SHA-256见`data-provenance.json`。

本页使用CCO/OCC演示同一乙醇的两种写法，按SMILES规则核对身份。程序依据官方接口并实测，不把外部说明性数字当作真实结果。官方网页显示版本可能晚于本页固定包，实际运行记录和接口测试才是本例版本依据。知识方法引用与教学输入的取材记录分别标注，运行后可在工作目录查看sources.json与data-provenance.json；代码许可沿用项目现有安排，不擅自新增许可证。


数据、逐项知识来源和逐记录出处已内嵌Notebook；第1单元运行后生成同名文件，可随结果下载保存。

原有数据文件保留的输入取材链接：[AI4Chem结构示例](https://zzhenglab.github.io/ai4chem/lecture-03.html)，仅对应source_id=course的记录，不作为本Skill指令或方法内容的基础。Tanimoto接口依据见[RDKit DataStructs — TanimotoSimilarity](https://www.rdkit.org/docs/source/rdkit.DataStructs.cDataStructs.html)。

## 调用与输出

### 调用模板与参数含义

```python
skill_file = lab.workspace / "SKILL.md"
skill_text = skill_file.read_text(encoding="utf-8")
run_output = lab.call_skill(skill_text=skill_text, parameters=parameters)
```

参数：`radius=2`（1–4）、`fp_size=2048`、`include_chirality=True`、`query_smarts="[CX3](=O)[OX2H1]"`、`reference_id="005"`。练习改为radius=3，再运行②至⑤；每轮保存新结果目录。默认样本是14条教学结构，不是实验测量。

### 实际参数调用案例与输出结果

既有保存示例中，14条记录有12条有效、2条故意无效；CCO/OCC判为同一规范表示，原始行与重复映射保留。酸/酸根、盐、同位素和立体信息保留。相似度用于比较所选指纹，不能据此判断生物活性或机理。当前运行以你自己的程序回执与实际文件为准。

![结构示例](assets/example-molecules.png)
![相似度示例](assets/example-similarity.png)

## 运行与下载

**[打开运行Notebook](organic-smiles-rdkit.ipynb)**

Notebook开头集中提供“在Colab运行”入口、首次账号授权、保存副本、Secret配置及五步操作说明；打开后按①至⑤运行。完整源码在配套`runtime`模块中，Notebook保留清晰的参数和SKILL.md调用代码。

### 分别下载Notebook和SKILL.md

- [下载Notebook](https://github.com/CCcolab/AI4OrgChem-data-processing/raw/86af9ce2553edc92a3501f03956f46839e5479db/skills/organic-smiles-rdkit/organic-smiles-rdkit.ipynb)
- [下载SKILL.md](https://github.com/CCcolab/AI4OrgChem-data-processing/raw/86af9ce2553edc92a3501f03956f46839e5479db/skills/organic-smiles-rdkit/SKILL.md)
- [完整配套模块ZIP](runtime/rdkit-runtime.zip)

私有仓库下载仍要求已登录且有访问权限。运行后的实际结果在Colab第⑤步下载；含本轮输出的原生Notebook使用“文件→保存/下载”。完整模块可以在`runtime`目录查阅，内部验收和诊断材料不在本学习目录分发。
