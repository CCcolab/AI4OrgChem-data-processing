# 表格拟合与残差分析

**分类：有机分析与实验数据处理** · Skill：`table-fitting-residuals`

[获取Notebook程序](NOTEBOOK.md) · [Colab运行与结果下载](RUNNING.md) · [返回首页](../../START_HERE_zh-CN.md)

本页围绕有出处的咖啡因HPLC标准液数据学习线性校准与残差解释。运行环境、参数填写、调用和下载操作集中在运行指南。

## 学习目标

| 层次 | 本页练习 |
| --- | --- |
| 跟随操作 | 用标准液浓度与峰面积拟合直线，绘图，反算待测浓度，改变标准点范围后比较结果 |
| 独立解释 | 解释斜率、截距、残差、RSS与R²的意义，区分数值拟合、仪器误差原因和实验测量 |

需要读表、单位、简单代数与基本分析化学知识。

## 这项Skill能帮你做什么

它指导Agent检查表格、单位和拟合目的，选择明确模型，调用数值工具，解释残差和局限。原文允许多种分析任务；**本页实现仅限未加权、带截距线性OLS校准**，不声称覆盖加权、非线性、因果分析或完整Skill测试。

示例问题：已知咖啡因标准液浓度及HPLC峰面积，怎样得到校准关系？峰面积424195对应多少mg/L？拟合残差告诉我们什么？只用前三个标准时结论如何变化？

## 知识与数据有何来源

数据逐项转录自 David Harvey《Analytical Chemistry 2.1》12.5节 **Exercise 12.5.2**，不是模型生成数据，也不是本项目实测。该题列出咖啡因反相HPLC标准液表和待测峰面积，给出的浓度答案约94.4 mg/L。[教材原页](https://chem.libretexts.org/Bookshelves/Analytical_Chemistry/Analytical_Chemistry_2.1_by_David_Harvey/Analytical_Chemistry_2.1_(Harvey)/12:_Chromatographic_and_Electrophoretic_Methods/12.05:_High-Performance_Liquid_Chromatography)

| 咖啡因浓度 mg/L | 峰面积，任意单位 |
| --- | --- |
| 50.0 | 226724 |
| 100.0 | 453762 |
| 125.0 | 559443 |
| 250.0 | 1093637 |

数据语境为同一题设条件下10 µL进样。这里使用已提供的数据，不操作仪器、不产生新的实验记录。教材追溯引用Kusch与Knupp，*Chem. Educator*，2003，8，201–205；本轮核对的是教材转录页，没有声称直接复核原论文原始实验数据。

教材页面标注作者David Harvey、CC BY-NC-SA 4.0。数据表和这一教材语境说明注明该来源及其许可，不为项目既有代码新增许可证，不复制原教材图。本站校准和残差图由本例数据重新计算生成。

最小二乘方法依据 [NIST统计手册：Least Squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm)。本例设浓度为x、峰面积为y，拟合：

$$\hat y=a+bx,\qquad RSS=\sum_i(y_i-\hat y_i)^2.$$

残差约定为观测减预测，反求浓度使用同一个校准模型：

$$e_i=y_i-\hat y_i,\qquad x_{sample}=(y_{sample}-a)/b.$$

残差检查与“高R²不充分”的说明依据 [NIST：How can I tell if a model fits my data?](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm)。本题只有4点且无重复；残差图是诊断起点，不能据此证明模型充分或方差恒定。本页不提供未经验证的置信区间、检出限或反应机理结论。


[逐项知识来源与章节](sources.json) · [数据转录与许可说明](data-provenance.json) · [原始浓度/峰面积CSV](caffeine-calibration.csv)

## 保存的示例图表

以下是来源样板真实四点运行的保存输出，供在线阅读；不代表刚打开网页就已完成新的模型调用。

![咖啡因外标校准与残差](example-calibration-and-residuals.png)

反算浓度94.37792857876974 mg/L。正的拟合截距本身不能确立基线或系统误差的物理成因。来源与PNG哈希见 [保存输出说明](saved-output-provenance.json)。


## 怎样解释结果

默认使用4个标准点，样品峰面积为424195，反算浓度接近教材答案94.4 mg/L；具体数值以实际运行输出为准。斜率单位为峰面积单位/(mg/L)，截距单位为峰面积单位，残差采用观测减预测。

改用前三个点是样本范围敏感性练习，不能据此断定最高标准点错误。4个点且没有重复测量，不能单凭高R²认定方差恒定或给出机理结论；模型解释与数值检查分别阅读。

## 自测

1. 为什么本例保留拟合截距？正截距能否单独证明基线偏差？
2. 去掉最高标准点后，应该比较哪些结果？能否据此直接删去该点？
3. 题设没有给出额外稀释倍数时，能否自行添加？

继续使用：[获取Notebook程序](NOTEBOOK.md) → [运行、修改参数和结果下载](RUNNING.md)。
