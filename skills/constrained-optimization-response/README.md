# 约束结构响应与端点复核

**后端待验 · PARTIAL_BACKEND_PENDING**：仅验证线性约束端点、给定梯度与Hessian；新量子约束优化未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

对提供的实坐标、梯度、Hessian和线性约束复核可行性、切向驻点与曲率，解释约束内端点，明确不提供新几何优化或量子梯度引擎。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/constrained-optimization-response-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

对满行秩A用SVD取得切空间Z，检查||A x−b||、||Zᵀg||、明确收敛声明及ZᵀHZ的严格正最小特征值。位置/梯度/Hessian门槛有各自单位，不能混称一个无量纲阈值。完整梯度非零可以与约束内驻点相容。

这里是给定端点的数值复核器，不是几何优化器。未运行新优化、SCF或梯度后端。仅线性约束，非线性约束需要额外Lagrangian曲率和协议，不由当前Hessian代替。切空间正曲率只支持声明约束内的局部候选，不证明无约束/全局极小值、分子稳定性或态连续性。

切空间投影及驻点规则在本页明示；[NumPy SVD](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)和[eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持数值处理，不能认证外部量子梯度。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\constrained-optimization-response-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 线性约束内驻点 | `python runtime/examples/01_case.py --output ../constrained-optimization-response-1` | 完整梯度范数2，切向梯度0，切向曲率3；合成受约束二次函数，不是优化所得分子。 退出码0。 |
| 2 不可行端点 | `python runtime/examples/02_case.py --output ../constrained-optimization-response-2` | A x−b=0.1超过位置门槛，不获资格，退出1。 退出码1。 |
| 3 切向负曲率 | `python runtime/examples/03_case.py --output ../constrained-optimization-response-3` | 切向最小特征值−1，拒绝极小点资格，退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters含coordinate_unit、position_atol、gradient_atol、hessian_atol、curvature_min、rank_rtol。data含coordinates、gradient、hessian、constraint_matrix、constraint_target、converged、source_definition。所有坐标共用bohr或angstrom，最多60维，线性约束A x=b且保留至少1个自由度。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
