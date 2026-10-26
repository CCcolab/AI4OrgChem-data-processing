# 各Skill运行环境、测试结果与未覆盖范围

本页为公开的脱敏功能验证摘要。32项采用同一披露栏目，具体依赖、案例、测试结果和限制在各自README/SKILL.md中。环境和通过状态限定于实际记录，不宣称跨平台、任意输入或全部科学用途已经验收。

## 当前版本的验证范围

本轮补齐27项：13项执行数据/数值正路径、参数修改及结果保存；14项学习模块只执行模型后端之前的输入拒绝、失败保存及旧结果保护。已有五项准备/复核/文件导入的运行环境说明保持原样。没有模型服务、训练/预测、Docker或新量子计算。

| Skill | 本地环境 | 已测范围 | 结果（含预期拒绝） |
| --- | --- | --- | --- |
| [SMILES 与 RDKit](../skills/organic-smiles-rdkit/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 7/7项符合预期 |
| [解析化学结构标识符｜PubChem 与 CIR](../skills/chemical-identifier-resolution/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [整理化学数据｜Pandas 清洗与统计](../skills/chemical-pandas-cleaning/README.md) | Windows 11 / Python 3.12.7 / CPU | 所列正式数据/复核功能 | 5/5项符合预期 |
| [表格拟合与残差分析](../skills/table-fitting-residuals/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 4/4项符合预期 |
| [绘制科研图表｜实验数据与误差分析](../skills/chemical-experimental-plotting/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 5/5项符合预期 |
| [分子图匹配与能量账本复核](../skills/molecular-graph-energy-ledger/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [同哈密顿量路径闭合核对](../skills/same-hamiltonian-path-closure/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [几何扫描能量分解与曲率分析](../skills/scan-energy-curvature/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [核排斥能与几何响应分析](../skills/nuclear-repulsion-response/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [RHF输入准备与结果复核](../skills/rhf-single-point/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 8/8项符合预期 |
| [轨道旋转与密度复核](../skills/orbital-localization-density/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 8/8项符合预期 |
| [非正交子空间投影与泄漏分析](../skills/nonorthogonal-subspace/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [片段工作基组装与一致性审计](../skills/fragment-working-basis/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [镜面对称轨道适配与奇偶性分析](../skills/reflection-parity/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [矩阵分区掩码与正定性检查](../skills/partition-mask-audit/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 3/3项符合预期 |
| [固定协议能量账本复核](../skills/fixed-protocol-energy-review/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 9/9项符合预期 |
| [线性约束导数与端点复核](../skills/constrained-optimization-response/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 8/8项符合预期 |
| [态集合与固定权重复核](../skills/multistate-size-comparison/README.md) | Windows 11 / Python 3.12.14 / CPU | 所列正式数据/复核功能 | 8/8项符合预期 |
| [可视化化学空间｜PCA、t-SNE 与 UMAP](../skills/chemical-space-embedding/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [聚类化学分子｜KMeans、层次聚类与 DBSCAN](../skills/chemical-molecule-clustering/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [构建化学预测模型｜回归与分类](../skills/chemical-regression-classification/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [验证化学预测模型｜交叉验证与解释](../skills/chemical-model-validation/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [构建化学树模型｜决策树与随机森林](../skills/chemical-tree-forest-models/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [构建化学神经网络｜MLP 回归与分类](../skills/chemical-mlp-models/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [构建分子图神经网络｜GNN 与 MPNN](../skills/molecular-gnn-mpnn/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [Chemprop分子属性回归教学](../skills/chemical-chemprop-prediction/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [预训练分子表示｜对比学习与掩码学习](../skills/molecular-self-supervised-pretraining/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [生成候选分子｜SMILES VAE 与潜空间采样](../skills/molecular-smiles-vae/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [优化化学实验｜贝叶斯优化与条件推荐](../skills/chemical-bayesian-optimization/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [权衡化学目标｜多目标贝叶斯优化](../skills/chemical-multiobjective-optimization/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [筛选实验方案｜多臂老虎机与探索利用](../skills/chemical-multiarmed-bandit/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |
| [学习序贯策略｜Q-learning 与化学模拟环境](../skills/chemical-q-learning-simulation/README.md) | Windows 11 / Python 3.12.14 / CPU | 输入/失败保存，仅此范围 | 4/4项符合预期 |

各项计数是软件检查，不是科学预测准确率；输入反例应被拒绝，不能将全部检查通过理解为所有命令均成功计算。没有在本轮重新创建依赖环境；Python3.12.7与3.12.14、NumPy1.26.4与2.4.6的记录不可混用。

## 历史成功运行与当前修订分开

第三方在固定[bb629ee版](https://github.com/CCcolab/AI4OrgChem-data-processing/commit/bb629ee486c221c8fe979918e9121a03cd2c5dcb)的Linux / Python3.12.14 / CPU环境执行32项默认/准备/复核入口，首轮37次命令，并有20次精确依赖追加复验。这是该固定版本的记录，不是当前main的完整模型流程重验。后续F01–F07的关闭属于各自定点范围；单独的正常回归对照也不能替代全部模块重跑。

当前14项学习模块完整流程本轮均未执行：六项表格表示/建模、五项Torch相关模块，以及单目标GP、老虎机与Q-learning。用户可按各自README准备环境自行运行；公开材料区分代码提供的功能、历史成功运行与本次实际测试。

## Torch依赖与五项计算预览

完整Torch运行未复验：GNN/MPNN、自监督预训练、SMILES VAE、Chemprop，以及通过BoTorch/GPyTorch调用Torch的双目标贝叶斯优化。GPU、完整训练/推理、权重重载未因本轮说明修订获得新资格。

单目标贝叶斯优化使用scikit-learn GaussianProcessRegressor，不依赖Torch；纠正旧清单把它归入Torch的文案，但其GP拟合/提议流程本轮同样没有重跑。

RHF、轨道旋转、固定协议账本、线性约束导数和态集合五项正式prepare/review/import已按各自环境验证；任意用户后端新实算仍单列[开发预览](DEVELOPMENT_PREVIEW.md)，不因此提升真实计算验收资格。

## 通用未覆盖项

未统一验收Windows以外的当前修订版、Python3.13、GPU、全新依赖安装、任意用户输入分布、实时数据库可用性、真实模型服务、实验安全性或化学预测泛化。教材定位、程序返回0、数值自检、教学训练与科学结论是不同证据层次。具体模块中明确的数据单位、来源、体系、矩阵角色、划分和方法假设仍然有效。
