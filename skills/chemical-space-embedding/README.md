# 化学描述符空间可视化

对用户明确给定的数值描述符执行实际PCA、t-SNE或UMAP，保存拟合/查询坐标及可用变换，不把二维图的距离或分组当作物性与活性证据。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-space-embedding-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

StandardScaler只拟合指定参考行；PCA用全SVD，t-SNE固定500迭代、exact和显式perplexity，UMAP固定100epochs/单线程及显式邻居数。保存坐标CSV、标注参考/查询的embedding.png和自生成joblib，报告解释方差或局部几何诊断；不训练监督标签。

仅Euclidean数值描述符。t-SNE/UMAP的全局距离、簇大小和轴方向不是物理量，不认证化学空间完整性或预测性能。随机种子不保证跨版本/平台逐比特一致；参数不同不直接比较二维坐标。未实现Tanimoto指纹嵌入或UMAP监督学习。

[scikit-learn PCA](https://scikit-learn.org/stable/modules/decomposition.html#pca)、[t-SNE](https://scikit-learn.org/stable/modules/manifold.html#t-sne)、[UMAP新点变换](https://umap-learn.readthedocs.io/en/latest/transform.html)。在线文档滚动更新，实际依赖固定并记录版本。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-space-embedding-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条SMILES由项目编写，X为本地RDKit实际计算的4种描述符；回归标签是声明的合成线性函数加微小随机扰动，分类标签是MolWt>70的合成规则，组别也是人为教学分组。它们不是实验活性、产率或经过验证的化学预测数据。 每次是实际本地拟合/训练，但软件执行通过不能认证化学泛化；不调用大语言模型服务或下载预训练模型。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 PCA参考与查询 | `python runtime/examples/01_case.py --output ../chemical-space-embedding-1` | 前24行拟合、后8行变换，保存32行坐标及解释方差；不使用标签。 退出码0。 |
| 2 t-SNE全表描述 | `python runtime/examples/02_case.py --output ../chemical-space-embedding-2` | 32行联合嵌入，perplexity=5；没有新样本transform承诺。 退出码0。 |
| 3 UMAP参考与查询 | `python runtime/examples/03_case.py --output ../chemical-space-embedding-3` | 前24行拟合、8行transform，显式邻居/种子；只作描述性几何。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式ids、features二维有限实数矩阵、feature_names及逐列feature_units；5–200行、1–32列。不是二进制指纹/Tanimoto接口。parameters显式algorithm、seed、n_components、fit_rows、scale、perplexity、n_neighbors。PCA/UMAP仅在前fit_rows拟合，再变换其余查询；t-SNE必须全表拟合且不支持新点transform。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

配套runtime/run_from_csv.py读取CSV并生成同样的显式请求，不猜测列名；使用--template指定本页案例JSON、--input指定自己的CSV、--features列出数值列、--feature-units逐列给单位，--id-column指定ID；监督学习还需--target及--target-unit，声明分组时加--groups。模板的parameters保留，data由CSV完全替换，不挪用示例标签。原CSV文本保存在实际请求内；结果仍写全新--output目录。参数含zero-based test_indices，换数据必须核对索引及分组，不自动拆分。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecular-descriptors.csv --features mol_wt_g_mol tpsa_A2 mol_logp_model heavy_atoms --feature-units g/mol angstrom2 dimensionless count --output ..\embedding-csv
```
