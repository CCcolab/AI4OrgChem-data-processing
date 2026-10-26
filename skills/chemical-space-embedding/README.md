# 化学描述符空间可视化

对用户明确给定的数值描述符执行实际PCA、t-SNE或UMAP，保存拟合/查询坐标及可用变换，不把二维图的距离或分组当作物性与活性证据。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-space-embedding-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


## 已验证运行环境与功能

**当前版本的输入与失败处理已在下列环境运行成功；完整学习流程仅有固定历史版本的运行记录。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | Python标准库（仅输入层测试，未导入数值/模型后端） |
| 本轮已验证功能 | JSON根类型/必需结构/非有限值拒绝、输入与Skill快照、failure.json、ZIP/SHA-256保存、已有结果保护；未进入analysis或模型后端 |
| 测试内容 | 三种早期输入反例（数组根、缺必需结构、NaN）均退出2并保留失败证据；已有输出被拒绝且原字节不变 |
| 测试结果 | 4/4项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 本轮未执行完整拟合、训练、预测、采样/策略学习或模型权重重载；默认入口完整运行仅有固定历史版本记录。没有以输入层通过替代完整算法运行结论。不认证真实化学预测泛化、实验改进或最优性。 |

完整运行的依赖仍需按runtime/requirements.txt单独配置；本轮未重新安装或核验整套模型依赖，不能把安装清单当作本轮已运行环境。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](../../docs/VERIFIED_ENVIRONMENTS.md)。


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

## 知识要点、前提与公式

PCA把参考数据中心化后，用正交方向保留尽可能多的样本方差；等价于在给定秩下最小化平方重建误差。若中心矩阵为X=UΣVᵀ，前r个右奇异向量给出投影，解释方差比例为σᵢ²/Σⱼσⱼ²。本例先按scale选择是否用参考行StandardScaler；标准化会改变各描述符对Euclidean几何的相对权重，不能视为无影响的单位换算。

t-SNE的核心目标是邻域概率分布间的KL(P∥Q)，perplexity调节有效邻域尺度；本实现联合拟合全部输入，不提供新点transform。UMAP从邻域结构构造低维表示，本例只用Euclidean度量，查询点由已拟合参考表示近似变换。局部邻域可视化不要求二维全局距离、面积、簇大小或坐标轴具有物理意义；trustworthiness只是输入/输出邻域保持程度，不是活性预测验证。

## 基础阅读与来源层级

章节定位：ESL第2版第14章Unsupervised Learning（目录主题定位）；t-SNE/UMAP用所列原论文补充现代方法。

基础阅读：[ESL2](https://link.springer.com/book/10.1007/978-0-387-84858-7)。

原始方法/作者专论：[TSNE](https://jmlr.org/papers/v9/vandermaaten08a.html)、[UMAP](https://arxiv.org/abs/1802.03426)。

实现接口：[SKPCA](https://scikit-learn.org/stable/modules/decomposition.html#pca)、[SKTSNE](https://scikit-learn.org/stable/modules/manifold.html#t-sne)、[UMAPAPI](https://umap-learn.readthedocs.io/en/latest/transform.html)。

ESL为2009年第2版；本次核对出版社目录中的相关主题，未声称读取受限章节正文。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。

单位标签要求：feature_units的每项在去除首尾空白后必须非空；无量纲显式写dimensionless或1。保留用户单位原文，不自动换算，不将空格解释为无量纲。target_unit同样不得为空白。
