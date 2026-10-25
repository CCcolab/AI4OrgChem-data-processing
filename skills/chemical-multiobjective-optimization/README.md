# 双目标贝叶斯优化

实际调用BoTorch双输出GP和qLogNEHVI，在显式有限池提出一个待观测候选，记录Pareto、方向和参考点，不将合成提议当作实验改进。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-multiobjective-optimization-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

将min目标乘−1后统一max，X按bounds缩放、Y用Standardize；噪声方差为给定SD平方。实际拟合SingleTaskGP，CPU double，单次有界优化不自动重试。qLogNEHVI用Sobol蒙特卡洛估计并对有限池逐点评分；报告优化警告而不认证收敛。保存模型状态并重载复核后验。

超体积单位是两个目标单位的乘积，数值依赖尺度与参考点；不能跨不同约定直接排名。提议不是实验结果/全局最优/安全方案；不认证不确定度校准、可合成性或真实闭环改进。固定小预算不保证拟合优化收敛。

[BoTorch官方多目标教程](https://botorch.org/docs/v0.17.2/tutorials/multi_objective_bo)说明全max方向与参考点，[qLogNEHVI接口](https://botorch.readthedocs.io/en/stable/acquisition.html)说明对数采集函数；实际执行版本固定0.18.1。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-multiobjective-optimization-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 两个目标最大化 | `python runtime/examples/01_case.py --output ../chemical-multiobjective-optimization-1` | 真实BoTorch拟合与采集计算，保存单个PENDING提议；不执行实验。 退出码0。 |
| 2 第二目标明确最小化 | `python runtime/examples/02_case.py --output ../chemical-multiobjective-optimization-2` | 真实BoTorch拟合与采集计算，保存单个PENDING提议；不执行实验。 退出码0。 |
| 3 改变参考点 | `python runtime/examples/03_case.py --output ../chemical-multiobjective-optimization-3` | 真实BoTorch拟合与采集计算，保存单个PENDING提议；不执行实验。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式bounds、feature_names/feature_units、observed_ids/x/y、source_ids、candidate_ids/x、objective_units；1–3维，3–32条已有观测，1–64个候选。重复观测坐标拒绝，已观测候选不参与提议；所有来源和单位必须明确。不会把预测补成观测。严格2个目标；parameters显式seed、directions、reference_point、逐目标noise_sd、maxiter1–30、mc_samples8–64。参考点必须被至少一个已有点严格支配。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 知识要点、前提与公式

将每个最小化目标与对应参考坐标乘−1，统一为最大化。点a支配b是各目标均不差且至少一个更好；Pareto集合取不被其他点支配者。相对参考点r的超体积HV是Pareto点与r形成矩形区域的并集体积，HVI=HV(P∪新点)−HV(P)；其单位是两个目标单位的乘积，尺度或参考点变化会改变数值。

本例SingleTaskGP对两输出使用独立GP结构，并以Standardize处理目标及已给噪声方差；不声称学习目标间相关性。NEHVI对已有点潜在值/Pareto前沿的不确定性积分，qLogNEHVI使用数值稳定的对数域及平滑近似来评分，输出log_acquisition_values不能当原单位超体积。此处q=1，仅对显式有限池逐点评分；8–64个Sobol样本和有界拟合不提供收敛/全局最优保证。

## 基础阅读与来源层级

章节定位：GPML第2章Regression（正文）；Daulton等第4–5节与Ament等LogEI/对数超体积附录（作者HTML正文）。

基础阅读：[GPML](https://gaussianprocess.org/gpml/chapters/)。

原始方法/作者专论：[NEHVI](https://arxiv.org/html/2105.08195v2)、[LOGEI](https://arxiv.org/html/2310.20708v3)。

实现接口：[BOTORCHTUT](https://botorch.org/docs/v0.17.2/tutorials/multi_objective_bo)、[BOTORCHAPI](https://botorch.readthedocs.io/en/stable/acquisition.html)。

GPML为2006年专著，作者网页对应第二次印刷；第2章回归正文可访问并核对，其他章仅按已核目录定位。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。
