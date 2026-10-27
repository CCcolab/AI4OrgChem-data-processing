# AI4OrgChem · 有机化学数据处理 Skill 目录

**版本：[v0.1.0](docs/RELEASE_v0.1.0_zh-CN.md) · 2026-10-26**

<!-- Canonical entry: https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md -->

面向有机化学学习与科研数据分析的 Skill 学习与工具集，按 7 个专业分类提供 32 项 Skill，涵盖分子结构、实验数据、能量与电子结构分析，以及化学机器学习与实验设计。

**如何使用：** 点击目录中的名称，先读各项 README 的知识点、科学边界与案例；完整 SKILL.md 可单独下载，配套 Python 程序、依赖和案例位于 runtime，各页提供完整代码包。

**运行环境：** 各项在用户自己的独立 Python 环境中运行，不需要统一平台账号，不强制使用 AI4OrgChem-Runtime 或 Docker。依赖库、可选服务及已有计算后端按对应页面配置，避免混装不兼容的依赖。见[环境与后端说明](docs/RUNTIME_INDEPENDENCE.md)。

**已验证范围：** 各项的运行环境、已测功能、测试结果与未覆盖内容见[32项运行验证对照](docs/VERIFIED_ENVIRONMENTS.md)，历史固定版本运行与当前修订测试分别列示。五项计算对接的正式功能为输入准备、已有结果复核等；新真实求解器调用列入[开发预览](docs/DEVELOPMENT_PREVIEW.md)。完整 Torch 训练、推理、权重重载及 GPU 流程仍未复验，不能由输入检查或下载一致性推断其通过，详见[功能与验证范围](docs/BACKEND_STATUS.md)。

## 有机分子结构与身份识别

- [SMILES 与 RDKit](skills/organic-smiles-rdkit/README.md)
- [解析化学结构标识符｜PubChem 与 CIR](skills/chemical-identifier-resolution/README.md)

## 有机分析与实验数据处理

- [整理化学数据｜Pandas 清洗与统计](skills/chemical-pandas-cleaning/README.md)
- [表格拟合与残差分析](skills/table-fitting-residuals/README.md)
- [绘制科研图表｜实验数据与误差分析](skills/chemical-experimental-plotting/README.md)

## 物理有机与能量分析

- [分子图匹配与能量账本复核](skills/molecular-graph-energy-ledger/README.md)
- [同哈密顿量路径闭合核对](skills/same-hamiltonian-path-closure/README.md)
- [几何扫描能量分解与曲率分析](skills/scan-energy-curvature/README.md)
- [核排斥能与几何响应分析](skills/nuclear-repulsion-response/README.md)

## 计算有机化学与电子结构

- [RHF输入准备与结果复核](skills/rhf-single-point/README.md)
- [轨道旋转与密度复核](skills/orbital-localization-density/README.md)
- [非正交子空间投影与泄漏分析](skills/nonorthogonal-subspace/README.md)
- [片段工作基组装与一致性审计](skills/fragment-working-basis/README.md)
- [镜面对称轨道适配与奇偶性分析](skills/reflection-parity/README.md)
- [矩阵分区掩码与正定性检查](skills/partition-mask-audit/README.md)
- [固定协议能量账本复核](skills/fixed-protocol-energy-review/README.md)

## 分子结构优化与多态比较

- [线性约束导数与端点复核](skills/constrained-optimization-response/README.md)
- [态集合与固定权重复核](skills/multistate-size-comparison/README.md)

## 化学信息学与分子设计

- [可视化化学空间｜PCA、t-SNE 与 UMAP](skills/chemical-space-embedding/README.md)
- [聚类化学分子｜KMeans、层次聚类与 DBSCAN](skills/chemical-molecule-clustering/README.md)
- [构建化学预测模型｜回归与分类](skills/chemical-regression-classification/README.md)
- [验证化学预测模型｜交叉验证与解释](skills/chemical-model-validation/README.md)
- [构建化学树模型｜决策树与随机森林](skills/chemical-tree-forest-models/README.md)
- [构建化学神经网络｜MLP 回归与分类](skills/chemical-mlp-models/README.md)
- [构建分子图神经网络｜GNN 与 MPNN](skills/molecular-gnn-mpnn/README.md)
- [Chemprop分子属性回归教学](skills/chemical-chemprop-prediction/README.md)
- [预训练分子表示｜对比学习与掩码学习](skills/molecular-self-supervised-pretraining/README.md)
- [生成候选分子｜SMILES VAE 与潜空间采样](skills/molecular-smiles-vae/README.md)

## 化学实验设计与优化

- [优化化学实验｜贝叶斯优化与条件推荐](skills/chemical-bayesian-optimization/README.md)
- [权衡化学目标｜多目标贝叶斯优化](skills/chemical-multiobjective-optimization/README.md)
- [筛选实验方案｜多臂老虎机与探索利用](skills/chemical-multiarmed-bandit/README.md)
- [学习序贯策略｜Q-learning 与化学模拟环境](skills/chemical-q-learning-simulation/README.md)

## 使用与科学范围

先读知识、输入/单位、配套案例及对应输出，再按页面短路径安装。用户数据修改时需同步参数、列名和来源，不自动删错行或把模型解释当作程序回执。数值、文件及SHA-256以本轮真实输出为准。

[Python使用说明](docs/PYTHON_USAGE.md) · [方法与来源说明](docs/RIGHTS_REVIEW.md)
