# 分子描述符聚类

在声明的Euclidean数值描述符及缩放规则下实际运行KMeans、Ward或DBSCAN，保留噪声与所有ID，不把算法簇解释成化学类别或活性分组。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-molecule-clustering-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

KMeans固定n_init=10，Ward仅Euclidean，DBSCAN显式eps/min_samples，保存cluster标签CSV及自生成模型。silhouette只在去掉噪声后有至少两簇且非全单点时计算，否则null。

标签编号任意，DBSCAN的−1是噪声，不是一个新化学类。算法/尺度/参数会改变分组；当前无稳定性/bootstrap或化学标签验证，不做活性推断。Ward与DBSCAN未提供通用新点predict。

[scikit-learn聚类](https://scikit-learn.org/stable/modules/clustering.html)说明算法、距离假设及评价指标。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-molecule-clustering-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条SMILES由项目编写，X为本地RDKit实际计算的4种描述符；回归标签是声明的合成线性函数加微小随机扰动，分类标签是MolWt>70的合成规则，组别也是人为教学分组。它们不是实验活性、产率或经过验证的化学预测数据。 每次是实际本地拟合/训练，但软件执行通过不能认证化学泛化；不调用大语言模型服务或下载预训练模型。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 KMeans三簇 | `python runtime/examples/01_case.py --output ../chemical-molecule-clustering-1` | 实际拟合3簇并保留32个ID；标签不代表化学类别。 退出码0。 |
| 2 Ward层次三簇 | `python runtime/examples/02_case.py --output ../chemical-molecule-clustering-2` | Euclidean Ward输出3簇；不把Tanimoto距离套入Ward。 退出码0。 |
| 3 DBSCAN含噪声 | `python runtime/examples/03_case.py --output ../chemical-molecule-clustering-3` | eps=.8、min_samples=2，保留所有−1噪声记录及有定义时的silhouette。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式ids、features二维有限实数矩阵、feature_names及逐列feature_units；5–200行、1–32列。不是二进制指纹/Tanimoto接口。parameters包含algorithm、seed、scale、n_clusters、eps、min_samples；按所选算法使用对应参数，未用参数不会被自动优化。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

配套runtime/run_from_csv.py读取CSV并生成同样的显式请求，不猜测列名；使用--template指定本页案例JSON、--input指定自己的CSV、--features列出数值列、--feature-units逐列给单位，--id-column指定ID；监督学习还需--target及--target-unit，声明分组时加--groups。模板的parameters保留，data由CSV完全替换，不挪用示例标签。原CSV文本保存在实际请求内；结果仍写全新--output目录。参数含zero-based test_indices，换数据必须核对索引及分组，不自动拆分。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecular-descriptors.csv --features mol_wt_g_mol tpsa_A2 mol_logp_model heavy_atoms --feature-units g/mol angstrom2 dimensionless count --output ..\clusters-csv
```

## 知识要点、前提与公式

KMeans在给定簇数下近似最小化Σᵢ∥xᵢ−μ_{cᵢ}∥²，n_init=10只提供多次初始化机会，不保证全局最优。Ward每次选择使簇内平方和增加最小的合并；两个簇A/B的增加量为|A||B|/(|A|+|B|)×∥μ_A−μ_B∥²，因此本接口限定Euclidean描述符。

DBSCAN用eps邻域及min_samples识别密度连通结构，−1表示噪声。eps的意义取决于缩放后的描述符空间；未缩放时不同量纲会共同决定数值距离。本例silhouette=(b−a)/max(a,b)，a为簇内平均距离、b为最近其他簇平均距离；仅在去噪后至少两簇且不全为单点簇时计算。它不能证明分组稳定、化学类别真实或活性相同。

## 基础阅读与来源层级

章节定位：ESL第2版第14章Unsupervised Learning（目录主题定位）。

基础阅读：[ESL2](https://link.springer.com/book/10.1007/978-0-387-84858-7)。

实现接口：[SKCLUSTER](https://scikit-learn.org/stable/modules/clustering.html)。

ESL为2009年第2版；本次核对出版社目录中的相关主题，未声称读取受限章节正文。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。
