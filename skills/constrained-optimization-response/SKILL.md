---
name: constrained-optimization-response
description: 复核给定线性约束下的梯度、Hessian和候选端点，不执行几何优化或产生新导数。
---

# 线性约束导数与端点复核

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

## 配套程序已验证运行环境

正式prepare/review/import及结果保存已在Windows 11、Python 3.12.14、CPU环境运行成功。数组复核使用NumPy 2.4.6，prepare仅用标准库。 三个正式案例、参数修改、预期错误与输出保护共8/8项本地检查通过，GitHub下载复验同为8/8项符合预期。完整依赖与操作见README。

该结论只对应所列正式功能和已测环境，不把输入准备说成外部实算，也不自动推广到其它软件版本或开发预览。

## 正式交付与完整调用

正式功能是准备输入、复核给定数据、导入已有结果JSON。三种模式prepare、review、import均不运行外部求解器，不导入用户选择的.py代码。调用链为读取完整SKILL.md并保存身份 → 显式parameters/data/provenance → 输入检查 → 本文件限定数学复核 → 回执、文件与SHA-256。调用名`constrained-optimization-response`保持不变。

```python
receipt = bridge.run_skill(mode="review", request_file="my-input.json", output_dir="new-results")
```

配套完整模板是runtime/run_skill.py；01_prepare.py、02_review.py和03_import_result.py对应准备、复核和文件导入。import请求的parameters恰含result_file（绝对常规JSON路径≤2MB），data为空，provenance明确来源。导入数据仍须符合上文科学schema，不自动转换算子、单位、态身份或数组顺序。

prepare只需Python标准库；本项数组复核需要NumPy，已验版本见runtime/requirements.txt。 当前正式程序不需要本项目Runtime、Docker、模型账号、PySCF或其它量子化学软件。包内数据不可原地修改后重写清单掩盖变化；复制用户输入到包外另行修改。完整命令与对应输出见README。

写新结果目录，保存输入、Skill、方法参数、逐项检查及实际产物；数值检查不合格退出1，输入/调用异常退出2并在已经建立的合法目录保留失败产物。参数解析或输出路径拒绝可以在建立目录前发生。不自动重试，不覆盖旧结果。来源声明或程序完成不能单独证明科学端点与物理解释成立。

## 真实计算对接：开发预览

只有用户明确选择开发预览时才讨论调用其已有求解程序。完整入口、信任边界、依赖与协议要求见[runtime/development_preview/README.md](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/constrained-optimization-response/runtime/development_preview/README.md)。这部分未完成新真实后端实算验收，不属于正式prepare/review/import的可用资格；不得把历史实算、人工数据、文件导入或本地程序检查当作新后端已通过。

预览不安装软件、不创建Docker/WSL或替用户选择环境。任意Python适配器与用户同权限运行，不是安全沙箱，不提供操作系统硬资源限额；需要真实原生日志、独立能量/导数记录、实际收敛与端点资格。缺少后端、协议或关键证据时仅准备或复核已有结果，不补造数值。
