# 公开功能与真实计算预览范围

32项Skill按用户能执行的功能介绍。以下五项的正式prepare/review/import已在各自列明的本地环境运行成功，并完成下载复验；任意新求解器调用单独列入开发预览；保留原内部真实后端待验事实，单独计算预览的科学资格没有提升。

| 正式功能 | 已成功运行的环境与结果 | 范围 | 新计算对接 |
| --- | --- | --- | --- |
| [RHF输入准备与结果复核](../skills/rhf-single-point/README.md) | Windows11 / Python3.12.14 / CPU / NumPy2.4.6；本地及下载复验各8/8通过 | 为已有闭壳层RHF结果准备复核请求，复核已有实AO密度、电子数及能量账本，不执行新SCF。 | [开发预览](../skills/rhf-single-point/runtime/development_preview/README.md) |
| [轨道旋转与密度复核](../skills/orbital-localization-density/README.md) | Windows11 / Python3.12.14 / CPU / NumPy2.4.6；本地及下载复验各8/8通过 | 复核给定轨道旋转、等占据空间的密度与电子数，不运行Boys或PM优化器。 | [开发预览](../skills/orbital-localization-density/runtime/development_preview/README.md) |
| [固定协议能量账本复核](../skills/fixed-protocol-energy-review/README.md) | Windows11 / Python3.12.14 / CPU / 标准库Decimal；本地及下载复验各9/9通过 | 按用户明确的固定协议核对已有普通态与条件态能量账本，不生成条件态算子或新量子能量。 | [开发预览](../skills/fixed-protocol-energy-review/runtime/development_preview/README.md) |
| [线性约束导数与端点复核](../skills/constrained-optimization-response/README.md) | Windows11 / Python3.12.14 / CPU / NumPy2.4.6；本地及下载复验各8/8通过 | 复核给定线性约束下的梯度、Hessian和候选端点，不执行几何优化或产生新导数。 | [开发预览](../skills/constrained-optimization-response/runtime/development_preview/README.md) |
| [态集合与固定权重复核](../skills/multistate-size-comparison/README.md) | Windows11 / Python3.12.14 / CPU / NumPy2.4.6；本地及下载复验各8/8通过 | 核对已有态集合完整性、来源与固定非负归一化权重，不运行多态优化或推断统计权重。 | [开发预览](../skills/multistate-size-comparison/runtime/development_preview/README.md) |

新真实后端继续PARTIAL_BACKEND_PENDING。旧水分子RHF、乙烯局域化及固定协议历史证据各有原范围，本次只做程序和已有数据复核，不执行新SCF、Boys/PM、条件态、约束优化或态集合求解。对用户已有软件结果的导入不等于后端运行；来源和收敛声明仍需独立证据。

## 学习模块的当前复验范围

完整Torch运行未复验，不能标为完整流程已通过。本轮仅验证输入和失败保存，详见[32项运行验证对照](VERIFIED_ENVIRONMENTS.md)。Torch相关模块包括：

- [chemical-chemprop-prediction](../skills/chemical-chemprop-prediction/README.md)：完整Torch/BoTorch流程本轮未复验。
- [chemical-multiobjective-optimization](../skills/chemical-multiobjective-optimization/README.md)：完整Torch/BoTorch流程本轮未复验。
- [molecular-gnn-mpnn](../skills/molecular-gnn-mpnn/README.md)：完整Torch/BoTorch流程本轮未复验。
- [molecular-self-supervised-pretraining](../skills/molecular-self-supervised-pretraining/README.md)：完整Torch/BoTorch流程本轮未复验。
- [molecular-smiles-vae](../skills/molecular-smiles-vae/README.md)：完整Torch/BoTorch流程本轮未复验。

单目标贝叶斯优化仅用scikit-learn GP，不属于Torch模块；其完整GP拟合/提议本轮未重跑。其余学习模块同样区分固定历史版本的成功记录与本轮输入检查，不执行新模型调用。五项计算预览的原待验记录保持，内部原始记录不公开上传。
