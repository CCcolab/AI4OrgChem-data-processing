# 约束结构响应与端点复核

**后端待验 · PARTIAL_BACKEND_PENDING**：仅验证线性约束端点、给定梯度与Hessian；新量子约束优化未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

对提供的实坐标、梯度、Hessian和线性约束复核可行性、切向驻点与曲率，解释约束内端点，明确不提供新几何优化或量子梯度引擎。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/constrained-optimization-response-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：线性约束的切空间、驻点与局部曲率

前提为同一长度单位的有限实坐标x、目标函数在端点附近二次连续可微、给定梯度g/Hessian H来自同一函数与坐标约定；A满行秩、Ax=b且至少一个自由度。本工具不验证导数来源真实性，也不优化几何。由SVD取正交零空间基Z，AZ=0、ZᵀZ=I，可行点写成x=x0+Zz。

约化函数f(z)=E(x0+Zz)的梯度为Zᵀg、Hessian为ZᵀHZ。因而精确可行驻点满足Zᵀg=0，即g可处于Aᵀ的列空间，完整梯度未必为0。若约化Hessian严格正定，结合上述光滑性才有约束内严格局部极小的充分条件；容差内数据只获候选资格，不能推全局/无约束极小、分子稳定性或电子态连续性。非线性约束需约束曲率与Lagrangian Hessian，不能直接沿用当前H。

本合同按||Ax−b||比较position_atol，按||Zᵀg||比较gradient_atol，H/曲率用Eh/length²；A行的缩放和各量单位必须明确。||Ax−b||是方程残差，通常不是到可行集的几何距离：x=0.1、约束x=0，A=1残差0.1，而等价A=1e−8残差1e−9。相同数值position_atol会改变门禁。因此调用者须固定约束行尺度或配套变换阈值，本实现保留原容差和算法，不暗自转为几何距离。

①E=2x+0.5x²+1.5(y−1)²在(0,1)、x=0下g=(2,0)、切向曲率3；②同一函数在(0.1,1)应给g=(2.1,0)，仍因不可行失败；③另取E=2x+0.5x²−0.5(y−1)²，在(0,1)的Hyy=−1，因切向负曲率失败。这是两种明确不同的合成解析函数，均不是分子优化或量子梯度。

### 经典教材、实现来源及支持范围

[O1：Boyd、Vandenberghe，Convex Optimization，Cambridge University Press，2004，§4.1.3、§10.1](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)的[作者授权下载说明](https://web.stanford.edu/~boyd/cvxbook/)和上述零空间/KKT正文已核读；原有[作者讲义](https://web.stanford.edu/~boyd/cvxbook/bv_cvxslides.pdf#page=329)仍标为讲义。书中凸问题的全局结论不移用于任意分子势能面。[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§6.4仅核对了出版社目录，不称已读正文。

O1上述章节已读授权正文；L1仅核对书目和目录，不声称逐式读全书。完整来源分类和支持边界见[runtime/sources.json](runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

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
