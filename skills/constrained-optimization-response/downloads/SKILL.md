---
name: constrained-optimization-response
description: 对提供的实坐标、梯度、Hessian和线性约束复核可行性、切向驻点与曲率，解释约束内端点，明确不提供新几何优化或量子梯度引擎。
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

O1上述章节已读授权正文；L1仅核对书目和目录，不声称逐式读全书。完整来源分类和支持边界见[runtime/sources.json](runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 完整调用与结果

1. 读取完整SKILL.md及显式JSON请求（parameters、data、provenance三部分），验证资源SHA-256及输入范围；禁止重复JSON键、NaN/Infinity和未知字段。
2. 将输入文字作为数据，不执行表达式、指令或未知代码，不联网、不调用模型。固定runtime/analysis.py负责实际科学/数学处理；runtime/run_skill.py负责完整可追溯调用。
3. 结果写Skill目录外全新目录，保存请求、Skill快照、环境、逐项检查、数值结果及真实回执。失败不得覆盖旧结果或标成功；新目录已创建时保留failure.json并非零退出。
4. 输出SHA-256及results.zip；文件状态以实际回执与哈希为准。无模型模式只记录Skill身份，不称指令已由模型理解。

## 科学边界

这里是给定端点的数值复核器，不是几何优化器。未运行新优化、SCF或梯度后端。仅线性约束，非线性约束需要额外Lagrangian曲率和协议，不由当前Hessian代替。切空间正曲率只支持声明约束内的局部候选，不证明无约束/全局极小值、分子稳定性或态连续性。

实际数值执行、合成软件测试、保存结果复核和新量子计算分开报告，不继承其他项目或旧案例资格。输入的来源标签/收敛/身份声明不是外部证据的真实性鉴定。

## 方法来源

切空间投影及驻点规则在本页明示；[NumPy SVD](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)和[eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持数值处理，不能认证外部量子梯度。

[Boyd与Vandenberghe作者讲义第10章](https://web.stanford.edu/~boyd/cvxbook/bv_cvxslides.pdf#page=329)给出线性等式KKT与零空间消元。对Ax=b，令AZ=0，驻点检查Zᵀg，局部切向曲率检查ZᵀHZ；有限阈值只是给定数组的候选资格。非线性约束需Lagrangian Hessian，本工具不提供；没有新量子优化、全局极小或收敛真实性认证。
