---
name: constrained-optimization-response
description: 为用户已有优化程序准备约束输入和调用，复核坐标、导数与端点；配套数值复核器限于明确的线性约束。
---

# 约束结构响应与端点复核

先确认用户目标、实际输入、方法、单位和来源。没有实际工具执行时标NOT_EXECUTED，不从既有文字、模型解释或历史PASS制造新数值。

## 输入与方法

parameters含coordinate_unit、position_atol、gradient_atol、hessian_atol、curvature_min、rank_rtol。data含coordinates、gradient、hessian、constraint_matrix、constraint_target、converged、source_definition。所有坐标共用bohr或angstrom，最多60维，线性约束A x=b且保留至少1个自由度。

对满行秩A用SVD取得切空间Z，检查||A x−b||、||Zᵀg||、明确收敛声明及ZᵀHZ的严格正最小特征值。位置/梯度/Hessian门槛有各自单位，不能混称一个无量纲阈值。完整梯度非零可以与约束内驻点相容。

## 核心知识：线性约束的切空间、驻点与局部曲率

前提为同一长度单位的有限实坐标x、目标函数在端点附近二次连续可微、给定梯度g/Hessian H来自同一函数与坐标约定；A满行秩、Ax=b且至少一个自由度。本工具不验证导数来源真实性，也不优化几何。由SVD取正交零空间基Z，AZ=0、ZᵀZ=I，可行点写成x=x0+Zz。

约化函数f(z)=E(x0+Zz)的梯度为Zᵀg、Hessian为ZᵀHZ。因而精确可行驻点满足Zᵀg=0，即g可处于Aᵀ的列空间，完整梯度未必为0。若约化Hessian严格正定，结合上述光滑性才有约束内严格局部极小的充分条件；容差内数据只获候选资格，不能推全局/无约束极小、分子稳定性或电子态连续性。非线性约束需约束曲率与Lagrangian Hessian，不能直接沿用当前H。

本合同按||Ax−b||比较position_atol，按||Zᵀg||比较gradient_atol，H/曲率用Eh/length²；A行的缩放和各量单位必须明确。||Ax−b||是方程残差，通常不是到可行集的几何距离：x=0.1、约束x=0，A=1残差0.1，而等价A=1e−8残差1e−9。相同数值position_atol会改变门禁。因此调用者须固定约束行尺度或配套变换阈值，本实现保留原容差和算法，不暗自转为几何距离。

①E=2x+0.5x²+1.5(y−1)²在(0,1)、x=0下g=(2,0)、切向曲率3；②同一函数在(0.1,1)应给g=(2.1,0)，仍因不可行失败；③另取E=2x+0.5x²−0.5(y−1)²，在(0,1)的Hyy=−1，因切向负曲率失败。这是两种明确不同的合成解析函数，均不是分子优化或量子梯度。

### 经典教材、实现来源及支持范围

[O1：Boyd、Vandenberghe，Convex Optimization，Cambridge University Press，2004，§4.1.3、§10.1](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)的[作者授权下载说明](https://web.stanford.edu/~boyd/cvxbook/)和上述零空间/KKT正文已核读；原有[作者讲义](https://web.stanford.edu/~boyd/cvxbook/bv_cvxslides.pdf#page=329)仍标为讲义。书中凸问题的全局结论不移用于任意分子势能面。[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§6.4仅核对了出版社目录，不称已读正文。

O1上述章节已读授权正文；L1仅核对书目和目录，不声称逐式读全书。完整来源分类和支持边界见[runtime/sources.json](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/constrained-optimization-response/runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。


## 科学适用性补充

几何优化的力为能量梯度的负值，导入梯度时不能混用。对于线性约束 Ax=b，令 T 张成 null(A)，驻点要求 Tᵀg≈0；全梯度 g 可以非零。在满足约束的点上，TᵀHT 正定是相应光滑能量在线性切空间中的局部极小充分条件，不能推出无约束或全局极小。

本地复核器要求一致的 bohr 或 angstrom 坐标，梯度单位 Hartree/长度、Hessian 单位 Hartree/长度²；不混入角度。坐标≤60，约束必须独立且至少有一个自由度。明确位置、梯度、Hessian 容差、曲率阈值及秩阈值。非线性约束需要拉格朗日 Hessian 和约束曲率，本复核器不适用。

三个 JSON 案例是显式二次函数的线性约束导数：01正切极小、02违反 x=0 约束、03负切向曲率；后两例应拒绝。不是分子优化。用户程序需提供真实坐标、梯度、Hessian、约束及优化日志，并另核对电子态连续性、方法适用性；本模板不自带量子梯度或优化器，不将导数后处理冒充新优化。

## 用户环境与后端选择

本 Skill 可独立下载阅读，配套 Python 不要求本项目 Runtime、安装登记、Docker 或固定磁盘路径。不自动安装/更新软件，不创建虚拟化环境，不索取模型密钥。先询问用户实际任务、已有程序/版本、输入和资源约束；优先复核已有结果；只有用户要求新计算并已选择可信程序时才执行。

1. 明确模型、体系/几何、单位、电子态、协议身份、来源与期望输出。缺必需信息则列出缺项，不能默补关键科学条件。
2. 核对用户已有后端是否实际支持该方法；不把某软件的泛用 SCF/优化器冒充专用条件态实现。不改变用户算子/占据/权重来迁就接口。
3. 生成适合用户现有环境的输入和调用；配套桥接器的 backend 模式只接受用户明确指定的可信 .py 和 execute=True。该 Python 与用户同权限运行，不是安全沙箱；不得把 CSV/JSON 文本当代码执行。准备模式不导入后端，不验证科学端点。
4. 先保存输入、Skill 快照、后端身份与资源协议；计算时保留原生日志、中间产物、实际收敛证据。后端返回 review_request（parameters/data/provenance）和 execution（至少 kind）；先保存返回，再执行明确范围的复核。
5. 严格区分准备、历史数组复核、人工数学演示、真实后端计算与模型解释。不使用语言模型也能执行这些显式程序；读取 Markdown 只记录指令文件身份，不是模型已理解/执行 Skill。
6. 写全新结果目录，禁止覆盖；数值检查失败或解释/适配失败仍保留已生成文件、失败原因与非零退出。无自动重试。不把失败产物视为合格端点。
7. 交付逐项检查、实际程序回执、文件及 SHA-256。不得从图形外观、文本解释、程序退出或旧 PASS 单独推断科学结论。

## 配套调用合同与依赖

portable-skill-backend-v1 是独立便携模板合同，不修改任何项目冻结合同。JSON 根对象恰为 parameters、data、provenance；provenance 含 kind、description。禁止重复键和非有限数。具体数学复核字段见本文件及 runtime/analysis.py；完整实例见 runtime/examples/*.json。用户可自行输出兼容 JSON，或编写调用已有 Python 库的适配器并返回相同结构。

prepare 仅 Python 3.10+ 标准库；四项数组/几何复核需要 NumPy，纯十进制账本仅标准库。requirements.txt 提供已验依赖版本。PySCF 仅可选模板需要，不能作为其它后端的强制依赖。模板不提供通用作业调度或硬资源隔离；线程参数、库内存建议和回调时间检查不等于操作系统硬限。用户有严格资源要求时使用自己已有的受控调度环境，不自动重试或放宽限制。

## 调用示例

完整 Python 模板在 runtime/run_skill.py；调用链是读取 SKILL.md → 显式请求/参数 → 用户选定适配器（可选）→ 数学复核 → 回执与文件。runtime/examples/01_prepare.py、02_review.py、03_user_backend.py 分别展示准备、复核、读取用户已有后端导出的结果；03 没有新量子计算。demo_backend.py 仅测试桥接合同，严禁当真实求解器。

```python
receipt = bridge.run_skill(
    mode="backend", request_file="my-request.json", output_dir="new-results",
    backend_file="my-trusted-backend.py", execute=True,
)
```

后端函数：run_backend(request, output_dir) 返回 {"review_request": {"parameters": ..., "data": ..., "provenance": ...}, "execution": {"kind": "明确的执行类型", ...}}。file_backend.py 是完整可运行的结果导入适配器；连接新求解器时，其物理算法、独立能量分项、端点资格和资源控制仍由真实后端及研究协议负责，不以本桥接器补造。

backend_calls 只统计桥接函数进入次数，不是科学核函数调用总数；Python 模块导入也可执行代码。后端原生任务次数与资源使用须由原生日志另外证明，不能将外部模块自报的 model_calls/network_calls 当作独立监测。桥接器本身不调用模型/网络，亦不执行后台超时强杀。

下载指令的来源链接使用公开仓库明确地址；完整Python代码包内的来源文件位于`runtime/sources.json`。顶层维护源与下载导出字节一致。
