# 小型MLP描述符模型

在本地CPU实际训练有界小型MLP回归或二分类，训练内缩放、披露优化收敛警告并保存重载结果，不声称合成案例证明化学泛化。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-mlp-models-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

先固定留出，再训练Pipeline；回归目标也仅在训练集缩放并还原预测单位。只使用本地随机初始化小网络，不下载权重。保存拟合/收敛警告，ConvergenceWarning使相应检查失败，不伪装优化成功；重载自己的模型核对预测。

小样本MLP很容易过拟合，随机种子不等于跨版本逐位复现。当前没有自动选网络、早停验证、外部测试、概率校准或化学适用域认证；不能用合成函数拟合分数宣传药效或产率预测。

[scikit-learn神经网络](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)、[Pipeline与泄漏](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-mlp-models-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条SMILES由项目编写，X为本地RDKit实际计算的4种描述符；回归标签是声明的合成线性函数加微小随机扰动，分类标签是MolWt>70的合成规则，组别也是人为教学分组。它们不是实验活性、产率或经过验证的化学预测数据。 每次是实际本地拟合/训练，但软件执行通过不能认证化学泛化；不调用大语言模型服务或下载预训练模型。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 6单元回归MLP | `python runtime/examples/01_case.py --output ../chemical-mlp-models-1` | 本地lbfgs训练，训练内缩放特征与目标；披露实际收敛，保存真实留出预测。 退出码0。 |
| 2 6单元二分类MLP | `python runtime/examples/02_case.py --output ../chemical-mlp-models-2` | 0/1合成任务，本地训练及模型重载；没有调用语言模型服务。 退出码0。 |
| 3 显式改12单元和正则项 | `python runtime/examples/03_case.py --output ../chemical-mlp-models-3` | 独立训练与保存；不是自动选优，留出集不能反复充当最终验证。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式ids、features二维有限实数矩阵、feature_names及逐列feature_units；5–200行、1–32列。不是二进制指纹/Tanimoto接口。监督数据另给target、target_unit及可选groups。parameters包含algorithm、seed、test_indices（零起始），算法专属参数见案例；分组一旦提供不得跨训练/测试。MLP给hidden_units（2–16）、max_iter（50–500）、alpha正则项；只有一层隐藏层，solver固定lbfgs，tol=1e-5。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

配套runtime/run_from_csv.py读取CSV并生成同样的显式请求，不猜测列名；使用--template指定本页案例JSON、--input指定自己的CSV、--features列出数值列、--feature-units逐列给单位，--id-column指定ID；监督学习还需--target及--target-unit，声明分组时加--groups。模板的parameters保留，data由CSV完全替换，不挪用示例标签。原CSV文本保存在实际请求内；结果仍写全新--output目录。参数含zero-based test_indices，换数据必须核对索引及分组，不自动拆分。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecular-descriptors.csv --features mol_wt_g_mol tpsa_A2 mol_logp_model heavy_atoms --feature-units g/mol angstrom2 dimensionless count --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\mlp-csv
```

## 知识要点、前提与公式

一隐藏层网络可写为f(z)=W₂ReLU(W₁z+b₁)+b₂；本例回归输出为实数，二分类通过logistic输出层形成类别概率。非线性隐藏单元增加表达能力，同时增加小样本过拟合风险。alpha作用于权重L2惩罚，其具体样本数归一约定依赖固定版本的scikit-learn，不与其他框架参数直接数值对照。

本例固定lbfgs优化非凸目标；达到数值停止条件不等于找到全局最优或通过化学泛化验证，ConvergenceWarning使相应检查失败。特征仅训练内缩放；回归还将训练目标标准化，并把预测还原到目标原单位。没有早停验证集或自动网络选择，改变宽度后的独立运行不能反复充当最终测试。

## 基础阅读与来源层级

章节定位：ESL第2版第11章Neural Networks；Deep Learning第6章Deep Feedforward Networks、第8章Optimization（均按目录定位）。

基础阅读：[ESL2](https://link.springer.com/book/10.1007/978-0-387-84858-7)、[DL](https://www.deeplearningbook.org/)。

实现接口：[SKMLP](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)、[SKLEAK](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。

ESL为2009年第2版；本次核对出版社目录中的相关主题，未声称读取受限章节正文。 Deep Learning为MIT Press2016版；核对作者公开目录中的相应章节，章节正文抓取超限，不据此声称已读全书。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 二分类概率证据

二分类结果新增classification-probabilities.csv：id、零起始source_index、observed_class、predicted_class、probability_class_0、probability_class_1，行顺序对应test_indices。result.json中的classification_classes及classification_probability_metadata.class_order给出predict_proba列顺序[0,1]，held_out_probabilities保存同一概率矩阵；原held-out-predictions.csv保持原字段。额外检查owned_model_save_restore_probabilities复核自生成模型重载概率与类别顺序。

概率来自同一次已拟合模型，未作概率校准，不代表已验证化学风险。local_prediction_runs=2表示原模型与重载模型两个推断阶段；local_prediction_method_calls明确记录二分类4次predict/predict_proba、回归2次predict。本次复用已有原模型预测，未增加拟合次数或二分类预测方法调用总数。save_model接口变更仅在本页及另外两份相同的回归/分类、树/森林、MLP支持库中同步。
