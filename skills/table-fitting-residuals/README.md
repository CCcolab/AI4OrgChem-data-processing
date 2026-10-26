# 表格拟合与残差分析

分类：**有机分析与实验数据处理** · Skill：`table-fitting-residuals`

通过Python程序复核有明确来源的咖啡因HPLC校准表。


## 已验证运行环境与功能

**下列数据/数值功能已在本地运行成功；结论限定于列出的操作与案例。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | numpy 2.4.6；matplotlib 3.11.2 |
| 本轮已验证功能 | 给定CSV的有界线性/二次最小二乘、加权拟合、残差/图表及结果保存；参数修改与已有结果保护 |
| 测试内容 | 02_linear、03_weighted、changed-degree、existing-output-protection；结果文件、ZIP CRC与SHA-256核对 |
| 测试结果 | 4/4项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 只验证给定小样本和有界次数；不认证实验误差模型、外推、因果或通用预测能力。 |

使用已有独立Python环境，没有在本轮重新安装依赖。通过所列小型案例不等于全部平台、输入分布或科学用途已认证。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](../../docs/VERIFIED_ENVIRONMENTS.md)。


## 学习目标

| 层次 | 本页练习 |
| --- | --- |
| 跟随操作 | 用标准液浓度与峰面积拟合直线，绘图，反算待测浓度，改变标准点范围后比较结果 |
| 独立解释 | 解释斜率、截距、残差、RSS与R²的意义，区分数值拟合、仪器误差原因和实验测量 |

需要读表、单位、简单代数与基本分析化学知识。

## 这项Skill能帮你做什么

它指导Agent检查表格、单位和拟合目的，选择明确模型，调用数值工具，解释残差和局限。**固定咖啡因入口**仅做未加权、带截距一次OLS校准；**用户CSV入口**支持带截距一次/二次最小二乘及显式sigma的WLS。二次式对系数仍是线性模型；任意非线性、因果分析及完整统计推断未实现。

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

默认：`python runtime/table-fitting-residuals.py --output ../fit-default`。参数模板见[runtime/parameters.json](runtime/parameters.json)。

| 参数 | 含义 | 对应输出 |
| --- | --- | --- |
| include_highest_standard=true | 4个标准；改为false明确选择前三点 | numerical-result.json中的n与used_ids、拟合系数与反算浓度、残差图 |
| unknown_peak_area=424195.0 | 峰面积，任意单位；有限非负数 | sample_concentration_mg_L；默认约94.37793 mg/L |
| fit_intercept=true | 拟合截距，不支持强制过原点 | intercept、slope、RSS、R²与残差 |

这是未加权、带截距的限定线性OLS样板，不扩展声称加权/非线性、自动删点或实验不确定度验证。原始表格见[runtime/caffeine-calibration.csv](runtime/caffeine-calibration.csv)，数据出处及许可见[数据来源](runtime/data-provenance.json)，方法和章节见[知识来源](runtime/sources.json)。

结果中的`fitted-and-residuals.csv`逐行对应标准ID；`numerical-result.json`包含45位Decimal独立公式复核；`calibration-and-residuals.png`显示校准与观测减预测残差。选择前三点是范围敏感性分析，不是认定最高点错误。数值模式不会生成模型解释或真实Agent调用回执。

## 运行与下载

### 1. 下载并在Windows短路径解压

下载[完整Python代码包](downloads/table-fitting-residuals-python.zip)；公开文件可直接下载。程序入口与全部依赖均在runtime，顶层只有README.md和SKILL.md；必须解压完整代码包。

**Windows请使用有写入权限的短目录，避免在多层长目录中安装依赖。** 例如把ZIP“全部解压”到`D:\Chem\t`，解压后进入`D:\Chem\t\table-fitting-residuals`。没有D盘时使用自己可写入的其它短目录，并替换下面示例路径。两个Skill分别解压到独立目录。

如果安装NumPy时出现`No such file or directory`，且路径很长或提示`Windows Long Path support`，请保留原目录，在更短的新目录重新解压并重新建立环境；无需修改系统长路径设置。

在含`README.md`、`SKILL.md`和`runtime`的Skill文件夹打开PowerShell，或先执行：

```powershell
Set-Location -LiteralPath 'D:\Chem\t\table-fitting-residuals'
```

### 2. 建立环境并完成默认运行

先安装Python 3.12或3.13，并确认`python --version`显示所选版本。以下命令逐行执行；安装报错时先停止，查看错误再继续。无需激活虚拟环境，所有安装和运行都显式使用它的Python：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe runtime\table-fitting-residuals.py --output ..\fit-default
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
.\.venv\Scripts\python.exe runtime\table-fitting-residuals.py --params my-parameters.json --output ..\fit-three-points
.\.venv\Scripts\python.exe runtime\table-fitting-residuals.py --verify ..\fit-three-points
```

默认使用4点，反算浓度约94.37792858 mg/L；修改后使用3点，查看拟合系数、残差和反算浓度的变化。每轮实际参数在结果的`parameters.json`和程序回执中保存；`--verify`只核对已有文件和ZIP的SHA-256，不重复计算。

### 4. 查看结果并另存一份

双击`..\fit-default\report.html`或`..\fit-three-points\report.html`，查看程序回执、实际参数和图表。报告自包含图片，无需启动Web服务。CSV、JSON和PNG也可在同一结果目录单独查看；文件状态以实际程序回执、文件清单和ZIP为准。

要保存默认结果的完整副本，先选择一个尚不存在的目标文件夹，再执行：

```powershell
Copy-Item -LiteralPath ..\fit-default -Destination ..\fit-default-saved -Recurse
.\.venv\Scripts\python.exe runtime\table-fitting-residuals.py --verify ..\fit-default-saved
Get-FileHash -LiteralPath ..\fit-default-saved\results.zip -Algorithm SHA256
```

保留整个结果文件夹，其中`results.zip`为可携带结果包，`results.zip.sha256`为ZIP哈希，`SHA256SUMS.txt`为逐文件清单。最后一条命令显示的哈希应与`results.zip.sha256`中的值相同。修改参数的结果可用同样方法另存到新的目录。

**已有结果目录不会覆盖。** 若提示“结果目录已存在”，为`--output`换一个新目录名；不要删除原始数据或旧结果。macOS/Linux在本机终端用`.venv/bin/python`替换上述Python路径，并使用相应的文件复制命令。

### 可选：让Agent读取SKILL.md并解释结果

`SKILL.md`是给AI助手的技能指令；`.py`是执行数值计算的程序。默认数值模式记录Skill身份，不能称为真实Agent调用。确需模型解释时才显式开启：

```powershell
.\.venv\Scripts\python.exe runtime\table-fitting-residuals.py --agent --env-file .env --output ..\results-agent
```

该可选模式只从自己已有的本地`.env`读取`DEEPSEEK_API_KEY`，使用自己的DeepSeek账号和额度；不把密钥值写入代码、命令行、日志或结果包。本轮README复验只运行默认数值模式，没有调用模型。

### 下载文件

- [完整Python代码包](downloads/table-fitting-residuals-python.zip)：README、入口、SKILL.md、依赖清单、源码及数据。
- [Python入口源码](runtime/table-fitting-residuals.py) · [SKILL.md源码](SKILL.md?plain=1) · [依赖清单](runtime/requirements.txt)。

## 三个明确的调用案例与用户CSV

顶层只保留README.md和SKILL.md，程序、依赖与案例在runtime。原咖啡因教材复算入口移为runtime/table-fitting-residuals.py，数值方法仍是原四点带截距OLS，不改变教材数据或来源许可。

| 案例 | Python调用 | 对应结果 |
| --- | --- | --- |
| ①有来源的咖啡因校准 | `python runtime/table-fitting-residuals.py --output ../fit-caffeine` | 4个标准点，原待测面积424195反算94.3779286 mg/L；只用前三点时更改参数JSON并写新目录。不是本项目新实验 |
| ②合成直线与用户CSV | `python runtime/examples/02_linear.py --output ../fit-linear` | 5点y=1+2x，系数按常数到高次顺序[1,2]；残差在浮点容差内为0；不能作为预测性能证明 |
| ③合成二次与显式SD | `python runtime/examples/03_weighted.py --output ../fit-weighted` | 5点y=1+2x+0.5x²，sigma作为y标准差，最小化Σ((y-yhat)/sigma)²；系数[1,2,0.5]，不混淆1/sigma与1/sigma² |

三个程序完整源码见[runtime入口](runtime/table-fitting-residuals.py)、[直线](runtime/examples/02_linear.py)、[加权二次](runtime/examples/03_weighted.py)；另有[完整调用模板](runtime/examples/call_skill_template.py)。第二、三例为项目编写的合成教学输入，既不是外部课程数据，也不是化学验证集。

用户CSV列为id,x,y，可加sigma；ID非空且唯一，重复观测使用不同ID。数据3–1000条（二次至少4条）、全部有限、x有变异；本程序不删除缺失或错误行，文件级失败保留input.csv、parameters.json、Skill快照和failure.json并返回非零。准备自己的CSV后：

```powershell
.\.venv\Scripts\python.exe runtime\fit_csv.py --input ..\my-fit.csv --x-unit mg/L --y-unit area_au --degree 1 --output ..\my-fit-results
```

权重调用另加`--sigma-column sigma`；sigma必须是严格正的响应标准差，不是方差、任意权重或x误差。degree只接受1/2且始终拟合截距；不执行任意字符串公式或自动提高阶数。数值在缩放x的设计矩阵中求解，再把系数换回原x单位；rcond=1e-12、缩放设计条件数上限1e10是本程序工程准入规则。拟合优度R²明确为原y上的未加权、带截距定义；常量y时为null。加权RSS另行报告，不把它称为未加权RSS。

输出为run-receipt.json、residuals.csv（y-yhat）、fit-and-residuals.png、原输入、实际参数、Skill快照、SHA-256及results.zip。图上误差线仅表示输入sigma，不是新推导的置信区间。本版不输出p值、置信区间、检出限、误差变量回归或预测泛化结论。x误差与观测相关性未建模，需研究者判断。

程序读取完整SKILL.md并调用固定数值工具；无模型执行只保存指令身份，不宣称语言模型理解了Skill。所有结果必须在Skill目录外的新目录；已有目录拒绝覆盖。`python`在Windows替换为`.\.venv\Scripts\python.exe`。

## 知识要点与经典依据

固定咖啡因入口复算Harvey§12.5习题；通用CSV入口选择带截距一次或二次式。一次式对x为直线，二次式仍对待估系数线性。OLS最小化`RSS=Σ(y_i−yhat_i)²`；sigma是响应标准差时，WLS最小化`Σ((y_i−yhat_i)/sigma_i)²`。以1/sigma缩放设计矩阵的行，对应的是1/sigma²目标权重，不能把方差作为sigma输入。

残差e=y−yhat，RMSE=sqrt(RSS/n)，常规未加权R²=1−RSS/Σ(y−mean_y)²；常量y时后者未定义。WLS的最小目标与此未加权R²不同，后者可能为负。高R²、低RSS均不证明机理、因果或外推；x误差/响应相关性不在当前模型中。描述性求最小二乘不要求先假定正态，但经典估计误差/区间需要额外条件，本模块不输出这些推断。

方法阅读用[Harvey§5.4 Linear Regression and Calibration Curves](https://chem.libretexts.org/Bookshelves/Analytical_Chemistry/Analytical_Chemistry_2.1_by_David_Harvey/Analytical_Chemistry_2.1_(Harvey)/05:_Standardizing_Analytical_Methods/5.04:_Linear_Regression_and_Calibration_Curves)的未加权、残差、Weighted Linear Regression with Errors in y及Curvilinear Regression小节；开放正文已核验。教材采用归一化的方差权重，乘同一常数不改变最小化解。Harvey§12.5是题源，NIST是方法手册，NumPy是求解接口，不能把三类证据混称。本页不以作者表尚有版本差异的Miller书目作唯一基础。

**用稳定表达回放预测。** 回执保留原字段`coefficients`作兼容导出，并新增`scaled_coefficients`。令`z=(x-scaled_x_center)/scaled_x_scale`，则`yhat=Σ scaled_coefficients[k]·z^k`；z无量纲，所有scaled系数单位为y，center/scale单位为x。可直接用`numpy.polynomial.polynomial.polyval(z,scaled_coefficients)`回放。原x很大而跨度很小时，原基系数会严重相消，内部RSS极小也不能认证该导出可用。

`original_basis_diagnostic`比较观测x上原基回放与缩放预测，采用`max|差|/max|缩放预测|≤1e−10`的无量纲工程准则；没有max(1,yScale)或固定有量纲atol，故改变y单位不会掩盖相同比例的损失。全零预测要求原基也精确回放零。失稳为REPLAY_UNSTABLE并给出ORIGINAL_BASIS_REPLAY_UNSTABLE警告，仍可使用稳定表达；通过仅适用于观测x，不认证外推或测量精度。[Burden与Faires《Numerical Analysis》9版](https://www.cengage.co.in/book-list/print/numerical-analysis-c2)第1/3/4章分别涉及误差、插值与数值微分；本次核验出版社目录，未取得这些章节全文，不借目录声称已核对误差定理。
完整章节/接口映射及访问限度见[runtime/sources.json](runtime/sources.json)。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
