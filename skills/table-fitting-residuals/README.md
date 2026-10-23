# 表格拟合与残差分析

分类：**有机分析与实验数据处理** · Skill：`table-fitting-residuals`

通过Python程序复核有明确来源的咖啡因HPLC校准表。

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


[逐项知识来源与章节](runtime/sources.json) · [数据转录与许可说明](runtime/data-provenance.json) · [原始浓度/峰面积CSV](runtime/caffeine-calibration.csv)

## 保存的示例图表

以下是来源样板真实四点运行的保存输出，供在线阅读；不代表刚打开网页就已完成新的模型调用。

![咖啡因外标校准与残差](assets/example-calibration-and-residuals.png)

反算浓度94.37792857876974 mg/L。正的拟合截距本身不能确立基线或系统误差的物理成因。示例参数见[结果JSON](assets/example-result.json)，当前数值以本地运行输出为准。


## 怎样解释结果

默认使用4个标准点，样品峰面积为424195，反算浓度接近教材答案94.4 mg/L；具体数值以实际运行输出为准。斜率单位为峰面积单位/(mg/L)，截距单位为峰面积单位，残差采用观测减预测。

改用前三个点是样本范围敏感性练习，不能据此断定最高标准点错误。4个点且没有重复测量，不能单凭高R²认定方差恒定或给出机理结论；模型解释与数值检查分别阅读。

## 自测

1. 为什么本例保留拟合截距？正截距能否单独证明基线偏差？
2. 去掉最高标准点后，应该比较哪些结果？能否据此直接删去该点？
3. 题设没有给出额外稀释倍数时，能否自行添加？

## 调用、参数与对应输出

默认：`python table-fitting-residuals.py --output ../fit-default`。参数模板见[runtime/parameters.json](runtime/parameters.json)。

| 参数 | 含义 | 对应输出 |
| --- | --- | --- |
| include_highest_standard=true | 4个标准；改为false明确选择前三点 | numerical-result.json中的n与used_ids、拟合系数与反算浓度、残差图 |
| unknown_peak_area=424195.0 | 峰面积，任意单位；有限非负数 | sample_concentration_mg_L；默认约94.37793 mg/L |
| fit_intercept=true | 拟合截距，不支持强制过原点 | intercept、slope、RSS、R²与残差 |

这是未加权、带截距的限定线性OLS样板，不扩展声称加权/非线性、自动删点或实验不确定度验证。原始表格见[runtime/caffeine-calibration.csv](runtime/caffeine-calibration.csv)，数据出处及许可见[数据来源](runtime/data-provenance.json)，方法和章节见[知识来源](runtime/sources.json)。

结果中的`fitted-and-residuals.csv`逐行对应标准ID；`numerical-result.json`包含45位Decimal独立公式复核；`calibration-and-residuals.png`显示校准与观测减预测残差。选择前三点是范围敏感性分析，不是认定最高点错误。数值模式不会生成模型解释或真实Agent调用回执。

## 运行与下载

### 1. 下载并在Windows短路径解压

下载[完整Python代码包](downloads/table-fitting-residuals-python.zip?raw=1)；私有仓库下载需要已有访问权限。程序入口为`table-fitting-residuals.py`，必须与`runtime`目录保持同级，不能只下载入口文件。

**Windows请使用有写入权限的短目录，避免在多层长目录中安装依赖。** 例如把ZIP“全部解压”到`D:\Chem\t`，解压后进入`D:\Chem\t\table-fitting-residuals`。没有D盘时使用自己可写入的其它短目录，并替换下面示例路径。两个Skill分别解压到独立目录。

如果安装NumPy时出现`No such file or directory`，且路径很长或提示`Windows Long Path support`，请保留原目录，在更短的新目录重新解压并重新建立环境；无需修改系统长路径设置。

在含`README.md`、`requirements.txt`和`.py`的Skill文件夹打开PowerShell，或先执行：

```powershell
Set-Location -LiteralPath 'D:\Chem\t\table-fitting-residuals'
```

### 2. 建立环境并完成默认运行

先安装Python 3.12或3.13，并确认`python --version`显示所选版本。以下命令逐行执行；安装报错时先停止，查看错误再继续。无需激活虚拟环境，所有安装和运行都显式使用它的Python：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe table-fitting-residuals.py --output ..\fit-default
```

首次安装依赖需要联网；默认数值计算不需要模型账号、API密钥或`.env`，不会调用模型。看到`PASS_LOCAL_NUMERICAL`后，在Skill目录的上一层找到`fit-default`结果文件夹。

### 3. 复制参数、修改后再运行

保留原模板，先复制：

```powershell
Copy-Item -LiteralPath runtime\parameters.json -Destination my-parameters.json
```

用记事本等文本编辑器打开`my-parameters.json`，只把`include_highest_standard`从`true`改为`false`，明确使用前三个标准点；不表示最高点有误。将内容改为下面的JSON并保存。JSON布尔值写小写`true`/`false`，字符串保留双引号；不要修改`runtime`中的原模板。

```json
{
  "include_highest_standard": false,
  "unknown_peak_area": 424195.0,
  "fit_intercept": true
}
```

回到同一个PowerShell窗口，运行到另一新目录并校验：

```powershell
.\.venv\Scripts\python.exe table-fitting-residuals.py --params my-parameters.json --output ..\fit-three-points
.\.venv\Scripts\python.exe table-fitting-residuals.py --verify ..\fit-three-points
```

默认使用4点，反算浓度约94.37792858 mg/L；修改后使用3点，查看拟合系数、残差和反算浓度的变化。每轮实际参数在结果的`parameters.json`和程序回执中保存；`--verify`只核对已有文件和ZIP的SHA-256，不重复计算。

### 4. 查看结果并另存一份

双击`..\fit-default\report.html`或`..\fit-three-points\report.html`，查看程序回执、实际参数和图表。报告自包含图片，无需启动Web服务。CSV、JSON和PNG也可在同一结果目录单独查看；文件状态以实际程序回执、文件清单和ZIP为准。

要保存默认结果的完整副本，先选择一个尚不存在的目标文件夹，再执行：

```powershell
Copy-Item -LiteralPath ..\fit-default -Destination ..\fit-default-saved -Recurse
.\.venv\Scripts\python.exe table-fitting-residuals.py --verify ..\fit-default-saved
Get-FileHash -LiteralPath ..\fit-default-saved\results.zip -Algorithm SHA256
```

保留整个结果文件夹，其中`results.zip`为可携带结果包，`results.zip.sha256`为ZIP哈希，`SHA256SUMS.txt`为逐文件清单。最后一条命令显示的哈希应与`results.zip.sha256`中的值相同。修改参数的结果可用同样方法另存到新的目录。

**已有结果目录不会覆盖。** 若提示“结果目录已存在”，为`--output`换一个新目录名；不要删除原始数据或旧结果。macOS/Linux在本机终端用`.venv/bin/python`替换上述Python路径，并使用相应的文件复制命令。

### 可选：让Agent读取SKILL.md并解释结果

`SKILL.md`是给AI助手的技能指令；`.py`是执行数值计算的程序。默认数值模式记录Skill身份，不能称为真实Agent调用。确需模型解释时才显式开启：

```powershell
.\.venv\Scripts\python.exe table-fitting-residuals.py --agent --env-file .env --output ..\results-agent
```

该可选模式只从自己已有的本地`.env`读取`DEEPSEEK_API_KEY`，使用自己的DeepSeek账号和额度；不把密钥值写入代码、命令行、日志或结果包。本轮README复验只运行默认数值模式，没有调用模型。

### 下载文件

- [完整Python代码包](downloads/table-fitting-residuals-python.zip?raw=1)：README、入口、SKILL.md、依赖清单、源码及数据。
- [Python入口源码](table-fitting-residuals.py) · [SKILL.md源码](SKILL.md?plain=1) · [依赖清单](requirements.txt)。
