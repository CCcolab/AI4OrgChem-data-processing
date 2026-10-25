---
name: chemical-experimental-plotting
description: 用明确变量、单位、分组和不确定度含义的实验CSV绘制散点、用户提供的对称误差线或重复观测均值与样本SD，保存实际绘图值、图和来源，不自动拟合或作显著性结论。
---

# 科研图表：实验数据与误差表达

先确认每行、横纵轴、单位、分组及重复层次。图只是数据表达，不能从曲线形状自动推断化学机理、因果或显著性。不从截图猜原始观测，不为视觉效果删点、平滑或缩窄误差线。

## 输入与范围

UTF-8 CSV，≤128000字节、1–1000条，id,x,y,group四列必需；ID唯一且非空，重复观测使用不同ID，组名由用户明确提供。x/y必须有限。用户显式声明单位，程序不换算。仅支持连续数值横轴和三种模式：scatter、supplied-error、replicate-sd。名称、结构、来源真实性不在本程序中认证。

## 完整处理

1. 读取完整SKILL.md和CSV，确认模式、单位及误差定义，保存原输入和设置到Skill外全新目录；已有目录拒绝。
2. scatter绘制所有原始点，不连线、不拟合，也不生成未提供的误差。supplied-error还需yerr列，非负且有限，必须声明SD、SEM或CI_HALF_WIDTH；不在这些概念间自动换算。
3. replicate-sd按声明group与数值x汇总，保留所有观测，输出n、均值、样本SD（ddof=1）。n=1时SD未定义，留空并只画点，不能把缺失SD写0。组内记录不自动被认定为独立样本，不能据此生成SEM或置信区间。
4. 标明坐标单位、分组、模式及误差含义。未提供CI置信水平时明确未推断，不能将输入半宽称为经过验证的95%CI。不画截断/对数轴，不插值、不平滑、不添加显著性星号。
5. 保存实际plotted-values.csv、PNG、SVG、原始CSV、参数、Skill快照、环境、真实回执、SHA-256及结果ZIP。任何数值或绘图失败保留本次输入、设置及failure.json，非零退出，不返回成功图链。

## 解释与权威

SD描述样本散布，SEM和置信区间涉及估计对象及独立性等假设，不能混用。图能呈现模式，但不能单独证明差异显著、反应机理、测量准确度或预测性能。未知重复层次需研究者补充；示例均为项目编写的合成软件教学输入，不是新实验结果。

实际程序是runtime/plot_experiment.py，run_skill读取并记录本指令身份，运行固定NumPy/Matplotlib工具；不联网、不调用模型，不宣称模型理解了指令。

- [Matplotlib errorbar](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html)：误差数组及非负条件，绘图接口不认证其统计意义。
- [NumPy std](https://numpy.org/doc/stable/reference/generated/numpy.std.html)：ddof及样本SD约定。
- [NIST graphical residual analysis](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm)：图形诊断与单一数值指标的局限；本Skill不产生拟合残差。

## 解释规则与理论依据

先解释误差条对应观测散布还是估计不确定度。replicate-sd使用s²=Σ(y−mean)²/(n−1)，不能未经用户请求换成s/√n；后者解释还需独立性等条件。n=1只画点，不称零误差。用均值12/SD2/SEM2÷√3的例子区分对象，不由SD条重叠与否下显著性结论。supplied-error只复现已声明半宽，CI_HALF_WIDTH不认证置信水平。Harvey§4.1/§4.4是已核验开放教材正文，Matplotlib/NumPy为绘图/算法接口；本模块不新增区间或假设检验。见runtime/sources.json。
