# 五项后端待验状态

33项均提供学习页面、完整SKILL.md与Python代码包。下面五项的**新后端计算仍未验收**，状态保持PARTIAL_BACKEND_PENDING；其他本地案例通过也只覆盖各页的明确范围，不代表真实化学应用、预测泛化或新量子方法获认证。

| 模块 | 当前范围与缺口 |
| --- | --- |
| [rhf-single-point](../skills/rhf-single-point/README.md) | 新固定水RHF计算未执行；已验证输入准备及旧AO数组复核，不能替代新SCF。 |
| [orbital-localization-density](../skills/orbital-localization-density/README.md) | 已验证给定旋转与密度不变性；实际Boys/Pipek局域化优化后端未执行。 |
| [fixed-protocol-energy-review](../skills/fixed-protocol-energy-review/README.md) | 仅验证账本闭合与显式资格标签；新条件态量子计算未执行。 |
| [constrained-optimization-response](../skills/constrained-optimization-response/README.md) | 仅验证线性约束端点、给定梯度与Hessian；新量子约束优化未执行。 |
| [multistate-size-comparison](../skills/multistate-size-comparison/README.md) | 仅验证集合完整性及固定权重算术；新多态量子计算未执行。 |

本版没有执行新的量子计算。现有程序中可执行的准备、给定数组/账本后处理、局部数学检查，与新SCF/局域化优化/条件态/几何优化/多态后端资格分开。来源或converged标签不能代替独立波函数、科学执行、数值门槛和清理回执。

后端启动、安装登记、方法或预算改变需要单独核实；下载代码或看到数值程序PASS，不意味着后端已就绪或获准自动启动。没有用历史输出冒充新的计算，没有为展示结果调用语言模型。
