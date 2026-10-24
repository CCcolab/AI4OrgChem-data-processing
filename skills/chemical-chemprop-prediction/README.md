# Chemprop分子属性预测流程

使用实际Chemprop2.3.1有向键消息网络在本地CPU训练小型回归案例，保存留出预测与自生成权重；不提供预训练药效模型或化学泛化声明。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-chemprop-prediction-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

实际Chemprop BondMessagePassing、MeanAggregation、RegressionFFN，关闭batch normalization；每划分一批，num_workers=0，用Torch Adam训练MSE。目标均值和尺度仅取训练集；保存权重并重建同架构重载复核。未使用Lightning自动训练/调参或预训练下载。

Chemprop自带特征与自编MPNN不同，不能逐数比较。小规模合成标签不证明任何实验性质预测、最佳超参数或优化收敛；没有外部测试/适用域/概率校准。输入限定同本页图范围，但软件可解析不等于物性适用。

[Chemprop2.3.1 MPNN组成文档](https://chemprop.readthedocs.io/en/latest/tutorial/python/models/basic_mpnn_model.html)；实际版本和架构写入结果。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-chemprop-prediction-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条项目编写的简单SMILES；回归标签为1+.2MolWt−1.5TPSA+.5MolLogP加seed17小扰动，分类标签为MolWt>70，人为组不是化学骨架组。这是实际本地CPU训练、保存和重载；标签不是实验值，小预算不认证优化收敛、预测泛化或化学用途。没有语言模型服务调用或预训练权重下载。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 深度2回归 | `python runtime/examples/01_case.py --output ../chemical-chemprop-prediction-1` | 真实Chemprop本地训练和留出推断，权重重载一致；无实验性能认证。 退出码0。 |
| 2 改变深度为3 | `python runtime/examples/02_case.py --output ../chemical-chemprop-prediction-2` | 真实Chemprop本地训练和留出推断，权重重载一致；无实验性能认证。 退出码0。 |
| 3 改变隐藏宽度为16 | `python runtime/examples/03_case.py --output ../chemical-chemprop-prediction-3` | 真实Chemprop本地训练和留出推断，权重重载一致；无实验性能认证。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data含5–64条唯一ids、单组分SMILES及监督任务target/target_unit，可声明groups；parameters含seed与零起始test_indices。相同忽略手性/同位素/映射的图不得跨划分，声明组别也不得跨划分。仅≤64原子有机元素图，无金属/多组分。完整参数见JSON；原SMILES保留。仅回归；hidden_units8–32、depth2–3、epochs1–100、learning_rate1e-5–.02。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

`runtime/run_from_csv.py`明确选择id、smiles及可选target/groups列，以--template保留参数并完全替换示例data；监督任务必须提供--target-unit。结果保留原CSV。更换行数时须同步修改零起始test_indices，重复图和声明组别不得跨训练/测试。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecules.csv --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\graph-csv-results
```
