# 模型验证与数据泄漏复核

用显式组别、时间顺序或IID假设执行真实折内Pipeline验证，保存每折索引、模型和误差，不把单次交叉验证称为完整嵌套或外部化学验证。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-model-validation-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

各折重新拟合StandardScaler与Ridge，不在全表上预处理。group用GroupKFold；time用TimeSeriesSplit并要求已声明组别不跨折；shuffle仅作用户明确选择的IID演示。保存各折训练/测试索引、预测及MAE，均值为各折MAE等权平均，不冒称全样本池化误差。

组别和时间顺序需要研究设计支持，标签相同不证明独立性；随机打乱可能泄漏化学近邻或重复。未实施超参数搜索、嵌套选择、外部验证、置信区间或预测适用域认证。

[scikit-learn交叉验证](https://scikit-learn.org/stable/modules/cross_validation.html)、[Pipeline数据泄漏](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-model-validation-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条SMILES由项目编写，X为本地RDKit实际计算的4种描述符；回归标签是声明的合成线性函数加微小随机扰动，分类标签是MolWt>70的合成规则，组别也是人为教学分组。它们不是实验活性、产率或经过验证的化学预测数据。 每次是实际本地拟合/训练，但软件执行通过不能认证化学泛化；不调用大语言模型服务或下载预训练模型。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 按人为教学组分折 | `python runtime/examples/01_case.py --output ../chemical-model-validation-1` | 三折组别不交叉，逐折训练缩放；人为组不自动是化学独立组。 退出码0。 |
| 2 按输入顺序向前验证 | `python runtime/examples/02_case.py --output ../chemical-model-validation-2` | 三折仅使用过去行，分组不跨边界；原表顺序必须有真实时间含义才适用于时间预测。 退出码0。 |
| 3 显式IID打乱对照 | `python runtime/examples/03_case.py --output ../chemical-model-validation-3` | 三折shuffle仅软件对照，不保证化学组独立；不能因分数更好就替代组验证。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式ids、features二维有限实数矩阵、feature_names及逐列feature_units；5–200行、1–32列。不是二进制指纹/Tanimoto接口。监督数据必须给target、target_unit和groups。parameters只包含scheme、seed、folds、alpha，scheme仅group/time/shuffle，不接受algorithm或test_indices。group/time检查每折声明组别不跨训练/测试；shuffle是显式IID对照，允许组别交叉并披露局限。time使用输入顺序，不自动猜时间列。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

配套runtime/run_from_csv.py读取CSV并生成同样的显式请求，不猜测列名；使用--template指定本页案例JSON、--input指定自己的CSV、--features列出数值列、--feature-units逐列给单位，--id-column指定ID；监督学习还需--target及--target-unit，声明分组时加--groups。模板的parameters保留，data由CSV完全替换，不挪用示例标签。原CSV文本保存在实际请求内；结果仍写全新--output目录。本页由scheme及folds生成划分，CSV行顺序和groups含义必须重新核对，不使用test_indices。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecular-descriptors.csv --features mol_wt_g_mol tpsa_A2 mol_logp_model heavy_atoms --feature-units g/mol angstrom2 dimensionless count --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\cv-csv
```

## 知识要点、前提与公式

交叉验证评价一个明确训练流程对指定划分机制下新数据的误差；划分机制应对应使用场景。GroupKFold隔离用户声明的组，不能由组名本身证明化学骨架或实验批次独立。TimeSeriesSplit仅按输入先后扩展训练，要求真实时间含义，并在本接口检查声明组别不跨训练/测试边界。shuffle是明确选择的IID对照，故允许组别交叉，不能冒称组外化学验证。

每折独立拟合StandardScaler和固定alpha的Ridge。第k折MAEₖ=Σ_{i∈testₖ}|yᵢ−ŷᵢ|/nₖ；本例报告(1/K)ΣₖMAEₖ，各折等权，区别于按nₖ加权的池化误差。这里不搜索超参数，也不提供嵌套选择；如果用这些分数挑模型，外层评估需另行设计。

## 基础阅读与来源层级

章节定位：ESL第2版第7章Model Assessment and Selection（目录主题定位）。

基础阅读：[ESL2](https://link.springer.com/book/10.1007/978-0-387-84858-7)。

实现接口：[SKCV](https://scikit-learn.org/stable/modules/cross_validation.html)、[SKLEAK](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

ESL为2009年第2版；本次核对出版社目录中的相关主题，未声称读取受限章节正文。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。
