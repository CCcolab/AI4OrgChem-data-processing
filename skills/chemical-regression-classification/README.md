# 化学表格回归与分类基线

使用显式划分和训练内缩放实际拟合Ridge或二分类Logistic基线，保存预测、模型和重载检查，区分软件训练、合成标签和化学预测验证。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-regression-classification-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


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

先按test_indices固定留出，再在训练行拟合StandardScaler和模型。Ridge报告留出MAE/RMSE/R²，常量或单条测试R²为null；Logistic报告准确率/balanced accuracy，只有测试两类齐全才有ROC-AUC。模型保存并重载自己的文件复核预测。

不能从合成标签的高分推断化学活性、因果或外推。固定留出反复调参会污染测试，应另有未触碰外部测试集；当前不做自动选模、概率校准、置信区间或多分类。

[scikit-learn线性模型](https://scikit-learn.org/stable/modules/linear_model.html)、[常见泄漏与Pipeline](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-regression-classification-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条SMILES由项目编写，X为本地RDKit实际计算的4种描述符；回归标签是声明的合成线性函数加微小随机扰动，分类标签是MolWt>70的合成规则，组别也是人为教学分组。它们不是实验活性、产率或经过验证的化学预测数据。 每次是实际本地拟合/训练，但软件执行通过不能认证化学泛化；不调用大语言模型服务或下载预训练模型。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 Ridge回归 | `python runtime/examples/01_case.py --output ../chemical-regression-classification-1` | 24训练/8留出，训练内缩放、保存回归指标和自生成模型。标签为合成函数。 退出码0。 |
| 2 Logistic二分类 | `python runtime/examples/02_case.py --output ../chemical-regression-classification-2` | 只使用训练标签拟合，保存留出0/1预测及概率指标；不认证化学分类。 退出码0。 |
| 3 显式改变Ridge正则项 | `python runtime/examples/03_case.py --output ../chemical-regression-classification-3` | alpha从1改10，写独立结果，不按留出分数自动挑选最好模型。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式ids、features二维有限实数矩阵、feature_names及逐列feature_units；5–200行、1–32列。不是二进制指纹/Tanimoto接口。监督数据另给target、target_unit及可选groups。parameters包含algorithm、seed、test_indices（零起始），算法专属参数见案例；分组一旦提供不得跨训练/测试。Ridge给alpha，Logistic给C；分类只支持0/1且训练包含两类。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

配套runtime/run_from_csv.py读取CSV并生成同样的显式请求，不猜测列名；使用--template指定本页案例JSON、--input指定自己的CSV、--features列出数值列、--feature-units逐列给单位，--id-column指定ID；监督学习还需--target及--target-unit，声明分组时加--groups。模板的parameters保留，data由CSV完全替换，不挪用示例标签。原CSV文本保存在实际请求内；结果仍写全新--output目录。参数含zero-based test_indices，换数据必须核对索引及分组，不自动拆分。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecular-descriptors.csv --features mol_wt_g_mol tpsa_A2 mol_logp_model heavy_atoms --feature-units g/mol angstrom2 dimensionless count --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\baseline-csv
```

## 知识要点、前提与公式

Ridge拟合线性均值wᵀz+b，并以平方残差和加α∥w∥²约束系数；截距不参与该惩罚。z由训练行的均值/尺度定义，因此缩放选择会改变正则化的含义。Logistic模型使用p(y=1|z)=sigmoid(wᵀz+b)，通过带L2正则的Bernoulli对数损失拟合；C控制正则强度的倒数方向，不能与Ridge的alpha直接数值类比。

测试MAE=Σ|y−ŷ|/n，RMSE=√(Σ(y−ŷ)²/n)，R²=1−RSS/TSS；单样本或常量测试目标的R²在本例为null。ROC-AUC需要测试两类齐全，衡量分数排序而非概率校准。重复按同一留出分数改参会把测试集变成选择数据，需另留未触碰的最终测试。

## 基础阅读与来源层级

章节定位：ESL第2版第3章Linear Methods for Regression、第4章Linear Methods for Classification（目录）；Bishop第3章作者幻灯片（可访问）。

基础阅读：[ESL2](https://link.springer.com/book/10.1007/978-0-387-84858-7)、[BISHOP](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)。

实现接口：[SKLINEAR](https://scikit-learn.org/stable/modules/linear_model.html)、[SKLEAK](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

ESL为2009年第2版；本次核对出版社目录中的相关主题，未声称读取受限章节正文。 Bishop为2006年PRML；核对作者页面及第3章官方幻灯片，未声称读取工具超限的完整书稿。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 二分类概率证据

二分类结果新增classification-probabilities.csv：id、零起始source_index、observed_class、predicted_class、probability_class_0、probability_class_1，行顺序对应test_indices。result.json中的classification_classes及classification_probability_metadata.class_order给出predict_proba列顺序[0,1]，held_out_probabilities保存同一概率矩阵；原held-out-predictions.csv保持原字段。额外检查owned_model_save_restore_probabilities复核自生成模型重载概率与类别顺序。

概率来自同一次已拟合模型，未作概率校准，不代表已验证化学风险。local_prediction_runs=2表示原模型与重载模型两个推断阶段；local_prediction_method_calls明确记录二分类4次predict/predict_proba、回归2次predict。本次复用已有原模型预测，未增加拟合次数或二分类预测方法调用总数。save_model接口变更仅在本页及另外两份相同的回归/分类、树/森林、MLP支持库中同步。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。

单位标签要求：feature_units的每项在去除首尾空白后必须非空；无量纲显式写dimensionless或1。保留用户单位原文，不自动换算，不将空格解释为无量纲。target_unit同样不得为空白。
