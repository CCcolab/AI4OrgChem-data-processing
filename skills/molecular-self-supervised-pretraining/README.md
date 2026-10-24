# 分子图自监督预训练

实际执行小型原子遮蔽或图特征对比预训练，并可冻结编码器做教学探针；保留训练范围和权重，不宣称预训练提升化学预测。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/molecular-self-supervised-pretraining-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

原子遮蔽将选中原子序数输入置零，真实类别单独保留作交叉熵目标；图对比用两种独立张量特征遮蔽、归一化嵌入及成对InfoNCE。只在训练图预训练；可选冻结编码器探针50步，训练内缩放目标，并检查编码器未改。

当前自编图特征只有原子序数、度、电荷、芳香标志及键级，未编码手性、同位素或3D；涉及这些信息时记录提示，不能用于对应性质区分或身份认证。只演示小型训练，不提供通用药效/产率预测、外推或适用域认证。保存文件为本次自生成权重，不读取不可信checkpoint。 特征遮蔽不被声明为化学合理的新分子；负例可能化学近似。没有匹配的从头训练基线与独立数据，不声称预训练提高性能。

[MPNN](https://proceedings.mlr.press/v70/gilmer17a.html)；[SimCLR原论文](https://proceedings.mlr.press/v119/chen20j.html)用于对比目标的数学参考，其视觉增强不自动成为分子语义不变量。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\molecular-self-supervised-pretraining-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条项目编写的简单SMILES；回归标签为1+.2MolWt−1.5TPSA+.5MolLogP加seed17小扰动，分类标签为MolWt>70，人为组不是化学骨架组。这是实际本地CPU训练、保存和重载；标签不是实验值，小预算不认证优化收敛、预测泛化或化学用途。没有语言模型服务调用或预训练权重下载。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 遮蔽原子序数 | `python runtime/examples/01_case.py --output ../molecular-self-supervised-pretraining-1` | 实际预训练并保存嵌入/权重；探针仅作软件演示。 退出码0。 |
| 2 双视图特征对比 | `python runtime/examples/02_case.py --output ../molecular-self-supervised-pretraining-2` | 实际预训练并保存嵌入/权重；探针仅作软件演示。 退出码0。 |
| 3 遮蔽后冻结探针 | `python runtime/examples/03_case.py --output ../molecular-self-supervised-pretraining-3` | 实际预训练并保存嵌入/权重；探针仅作软件演示。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data含5–64条唯一ids、单组分SMILES及监督任务target/target_unit，可声明groups；parameters含seed与零起始test_indices。相同忽略手性/同位素/映射的图不得跨划分，声明组别也不得跨划分。仅≤64原子有机元素图，无金属/多组分。完整参数见JSON；原SMILES保留。无监督任务不接受属性标签；mask_then_probe显式提供监督标签。另给mode、hidden_units、depth、epochs1–50、learning_rate、batch_size和temperature。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

`runtime/run_from_csv.py`明确选择id、smiles及可选target/groups列，以--template保留参数并完全替换示例data；监督任务必须提供--target-unit。结果保留原CSV。更换行数时须同步修改零起始test_indices，重复图和声明组别不得跨训练/测试。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\03.json --input runtime\examples\molecules.csv --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\graph-csv-results
```

[SimCLR原始论文](https://proceedings.mlr.press/v119/chen20j.html)研究视觉增强与对比目标，不能直接背书本例的分子特征掩码为化学等价变换。张量loss/encoder重放只证明该实现执行；化学表示优劣须在独立真实数据与匹配从零训练对照下评价。
