# 公开功能与真实计算预览范围

32项Skill按用户能执行的功能介绍。以下五项的正式prepare/review/import已与任意后端调用分离；保留原内部真实后端待验事实，单独计算预览的科学资格没有提升。

| 正式功能 | 范围 | 新计算对接 |
| --- | --- | --- |
| [RHF输入准备与结果复核](../skills/rhf-single-point/README.md) | 准备闭壳层RHF请求，复核已有实AO密度、电子数及能量账本，不执行新SCF。 | [开发预览](../skills/rhf-single-point/runtime/development_preview/README.md) |
| [轨道旋转与密度复核](../skills/orbital-localization-density/README.md) | 复核给定轨道旋转、等占据空间的密度与电子数，不运行Boys或PM优化器。 | [开发预览](../skills/orbital-localization-density/runtime/development_preview/README.md) |
| [固定协议能量账本复核](../skills/fixed-protocol-energy-review/README.md) | 按用户明确的固定协议核对已有普通态与条件态能量账本，不生成条件态算子或新量子能量。 | [开发预览](../skills/fixed-protocol-energy-review/runtime/development_preview/README.md) |
| [线性约束导数与端点复核](../skills/constrained-optimization-response/README.md) | 复核给定线性约束下的梯度、Hessian和候选端点，不执行几何优化或产生新导数。 | [开发预览](../skills/constrained-optimization-response/runtime/development_preview/README.md) |
| [态集合与固定权重复核](../skills/multistate-size-comparison/README.md) | 核对已有态集合完整性、来源与固定非负归一化权重，不运行多态优化或推断统计权重。 | [开发预览](../skills/multistate-size-comparison/runtime/development_preview/README.md) |

新真实后端继续PARTIAL_BACKEND_PENDING。旧水分子RHF、乙烯局域化及固定协议历史证据各有原范围，本次只做程序和已有数据复核，不执行新SCF、Boys/PM、条件态、约束优化或态集合求解。对用户已有软件结果的导入不等于后端运行；来源和收敛声明仍需独立证据。

## 第三方修订后的Torch复验范围

**完整Torch运行未复验，不能标为已通过。** 此状态单独说明，不将下列学习模块计入或替换上面的五项真实科学后端清单。

- [molecular-gnn-mpnn](../skills/molecular-gnn-mpnn/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [molecular-self-supervised-pretraining](../skills/molecular-self-supervised-pretraining/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [molecular-smiles-vae](../skills/molecular-smiles-vae/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [chemical-chemprop-prediction](../skills/chemical-chemprop-prediction/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [chemical-bayesian-optimization](../skills/chemical-bayesian-optimization/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。

本次完成定点输入、单位、失败证据、数值边界和包/来源链接检查；图输入检查用真实RDKit及原函数表达式，ndarray替身不提供真实Torch张量或模型验收。第三方既有Linux/CPU结论固定在bb629ee，不自动推广到修订版。未重新调用模型或科学后端，内部日志不公开上传。
