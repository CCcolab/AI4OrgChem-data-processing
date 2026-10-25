# 五项便携后端与真实计算待验状态

当前目录包含32项专业Skill。下列五项已解除本项目Runtime、Docker和安装登记的强制绑定；可独立准备输入、复核已有结果或调用用户明确选择的可信Python后端。**新便携真实后端保持PARTIAL_BACKEND_PENDING**，本地数学复核不替代真实端点验收。

| Skill | 当前可用范围及待验边界 |
| --- | --- |
| [rhf-single-point](../skills/rhf-single-point/README.md) | 便携输入/用户后端/实AO复核可用；历史固定水结果保留，新便携PySCF任务未实算。 |
| [orbital-localization-density](../skills/orbital-localization-density/README.md) | 便携旋转/密度复核和用户后端接口可用；历史乙烯证据保留，新便携Boys/PM任务未实算。 |
| [fixed-protocol-energy-review](../skills/fixed-protocol-energy-review/README.md) | 独立用户协议账本与结果导入可用；真实条件态后端仍待验，原失败尝试未重试。 |
| [constrained-optimization-response](../skills/constrained-optimization-response/README.md) | 用户优化程序接口与给定线性约束导数复核可用；真实新优化端点/曲率仍待验。 |
| [multistate-size-comparison](../skills/multistate-size-comparison/README.md) | 用户态集合接口与固定非负归一化权重复核可用；真实多态集合与专用有符号公式仍待验。 |

RHF与局域化提供可选现有PySCF模板；无PySCF时只准备或导入其它已有软件结果，不自动安装或创建环境。PySCF不原生支持Windows，见[官方安装说明](https://pyscf.org/user/install.html)。其它三项的专用物理算法及端点资格必须由用户的明确协议和真实求解后端提供。

历史固定水RHF和乙烯局域化的既有验收范围保留；原条件态首次失败及修复版尚未完整重验、真实约束导数/曲率、真实多态集合等缺口不改写。五项泛用新便携后端均未在本次发布执行，不上传内部日志或旧执行身份。

准备、历史数组复核、人工数学演示、真实后端运行分别记录；converged或来源标签不是独立真实性证明。普通/条件账本不生成通用条件泛函；约束复核限线性约束；多态默认非负归一化权重不是有符号LDE或自由能。当前进程Python模板不提供安全沙箱或操作系统硬资源限额。

## 第三方修订后的Torch复验范围

**完整Torch运行未复验，不能标为已通过。** 此状态单独说明，不将下列学习模块计入或替换上面的五项真实科学后端清单。

- [molecular-gnn-mpnn](../skills/molecular-gnn-mpnn/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [molecular-self-supervised-pretraining](../skills/molecular-self-supervised-pretraining/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [molecular-smiles-vae](../skills/molecular-smiles-vae/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [chemical-chemprop-prediction](../skills/chemical-chemprop-prediction/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。
- [chemical-bayesian-optimization](../skills/chemical-bayesian-optimization/README.md)：完整Torch训练/推理、权重重载及GPU未在本次修订重新验收。

本次完成定点输入、单位、失败证据、数值边界和包/来源链接检查；图输入检查用真实RDKit及原函数表达式，ndarray替身不提供真实Torch张量或模型验收。第三方既有Linux/CPU结论固定在bb629ee，不自动推广到修订版。未重新调用模型或科学后端，内部日志不公开上传。
