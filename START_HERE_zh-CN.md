# AI4OrgChem · 有机化学数据处理Skill目录

<!-- Canonical entry: https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md -->

当前Python学习版。按七个专业分类和一个共用支持分类，共33项；点击名称进入README学习，完整SKILL.md可单独下载，Python程序、依赖和案例位于runtime。各页提供代码包，不需要云端交互账号。每个Skill使用自己的独立Python环境，不将不兼容的依赖混装。

**五项便携后端：** RHF、局域化、固定协议能量、约束响应及多态比较支持独立输入准备、已有结果复核和用户已有后端调用，不强制本项目Runtime、Docker或安装登记。五项新便携真实后端继续待验；原固定协议的历史结果保留，不能据本地程序通过自动提升资格。

**验收范围：** 本地数值计算、旧结果后处理、合成模拟、本地机器学习训练和新量子后端执行分别记录。合成数据高分不证明化学预测能力。下列五项标“后端待验”的项目不能宣称新后端计算已完成；[查看五项状态及适用范围](docs/BACKEND_STATUS.md)。

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

- [RHF 单点计算助手](skills/rhf-single-point/README.md)（便携Python；真实后端待验）
- [轨道局域化与密度不变性验证](skills/orbital-localization-density/README.md)（便携Python；真实后端待验）
- [非正交子空间投影与泄漏分析](skills/nonorthogonal-subspace/README.md)
- [片段工作基组装与一致性审计](skills/fragment-working-basis/README.md)
- [镜面对称轨道适配与奇偶性分析](skills/reflection-parity/README.md)
- [矩阵分区掩码与正定性检查](skills/partition-mask-audit/README.md)
- [固定协议条件态与能量复核](skills/fixed-protocol-energy-review/README.md)（便携Python；真实后端待验）

## 分子结构优化与多态比较

- [约束优化与结构响应](skills/constrained-optimization-response/README.md)（便携Python；真实后端待验）
- [多态与尺寸比较](skills/multistate-size-comparison/README.md)（便携Python；真实后端待验）

## 化学信息学与分子设计

- [可视化化学空间｜PCA、t-SNE 与 UMAP](skills/chemical-space-embedding/README.md)
- [聚类化学分子｜KMeans、层次聚类与 DBSCAN](skills/chemical-molecule-clustering/README.md)
- [构建化学预测模型｜回归与分类](skills/chemical-regression-classification/README.md)
- [验证化学预测模型｜交叉验证与解释](skills/chemical-model-validation/README.md)
- [构建化学树模型｜决策树与随机森林](skills/chemical-tree-forest-models/README.md)
- [构建化学神经网络｜MLP 回归与分类](skills/chemical-mlp-models/README.md)
- [构建分子图神经网络｜GNN 与 MPNN](skills/molecular-gnn-mpnn/README.md)
- [预测分子性质与反应活性｜Chemprop](skills/chemical-chemprop-prediction/README.md)
- [预训练分子表示｜对比学习与掩码学习](skills/molecular-self-supervised-pretraining/README.md)
- [生成候选分子｜SMILES VAE 与潜空间采样](skills/molecular-smiles-vae/README.md)

## 化学实验设计与优化

- [优化化学实验｜贝叶斯优化与条件推荐](skills/chemical-bayesian-optimization/README.md)
- [权衡化学目标｜多目标贝叶斯优化](skills/chemical-multiobjective-optimization/README.md)
- [筛选实验方案｜多臂老虎机与探索利用](skills/chemical-multiarmed-bandit/README.md)
- [学习序贯策略｜Q-learning 与化学模拟环境](skills/chemical-q-learning-simulation/README.md)

## 共用运行支持

- [Runtime 使用助手](skills/runtime-usage-assistant/README.md)

## 使用与科学范围

先读知识、输入/单位、三个案例及对应输出，再按页面短路径安装。用户数据修改时需同步参数、列名和来源，不自动删错行或把模型解释当作程序回执。数值、文件及SHA-256以本轮真实输出为准。

[Python使用说明](docs/PYTHON_USAGE.md) · [方法与来源说明](docs/RIGHTS_REVIEW.md)
