# 整理化学数据：Pandas清洗与统计

适用于小规模实验结果表的数值审计、重复标记、分组描述统计和元数据连接。保留原始记录，不自动去重、删异常值、插补或换单位；这里的“清洗”是把问题显式列出来。

| 文件 | 职责 |
| --- | --- |
| 本README | 知识、案例、输入输出和操作说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 处理指令、数据约定及统计边界，可下载用于自己的代理 |
| [runtime/clean_chemical_data.py](runtime/clean_chemical_data.py) | 读取Skill→校验CSV→数值分类→分组统计/受约束连接→保存完整结果 |

程序、依赖和案例都在runtime。下载[完整Python代码包](downloads/chemical-pandas-cleaning-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件页用“Download raw file”下载，不把网页另存为程序。


## 已验证运行环境与功能

**下列数据/数值功能已在本地运行成功；结论限定于列出的操作与案例。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.7 / CPU |
| 本轮实际依赖范围 | pandas 2.2.2；numpy 1.26.4 |
| 本轮已验证功能 | CSV数值审计、保留重复记录、分组描述统计、受约束元数据连接和结果保存；参数修改与已有结果保护 |
| 测试内容 | 01_replicates、02_issues、03_join、changed-parameter、existing-output-protection；结果文件、ZIP CRC与SHA-256核对 |
| 测试结果 | 5/5项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 仅描述统计与显式输入审计；无自动去重/插补/换单位，无独立重复、因果或显著性认证。 |

使用已有独立Python环境，没有在本轮重新安装依赖。通过所列小型案例不等于全部平台、输入分布或科学用途已认证。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/docs/VERIFIED_ENVIRONMENTS.md)。


## 必要知识

原始值、解析后的数字和缺失原因应分开保存。0不是缺失；文本NA不自动解释成空。重复行可能是误录，也可能是实验重复，程序只标记、不替用户决定。分组均值与样本SD描述当前记录，不证明差异显著、测量准确或因果关系。SD使用ddof=1，只有一个有效值时不定义；技术重复不能直接当独立样本。

单位参数是标签，不换算。混合单位、检测限值、百分号后缀或千位逗号需先确认规则。本版不做结构解析、实验真实性认证、置信区间、SEM或假设检验。[read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)、[to_numeric](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html)、[Python statistics](https://docs.python.org/3.12/library/statistics.html)和[merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)给出实际软件约定。

## 知识要点与经典依据

把每行代表的实验单位说清楚，才能解释统计量。对组内n个有效观测，`mean=Σy_i/n`，样本SD为`s=sqrt(Σ(y_i−mean)²/(n−1))`，SD与y同单位。重复记录若是误录会改变描述统计，若是技术重复又不能自动当独立实验；所以程序保留并标记，不代替研究者决定删行。0与空缺是反例：删掉0或把空缺补0都会改变均值。右表同键多行会制造伪重复，因此连接要求many_to_one。

描述统计不要求把数据先宣称为正态；若将样本方差推广为总体方差估计或生成SEM/CI，则需相应抽样、独立性及分布条件。本模块不进行这些推断。[Harvey《Analytical Chemistry2.1》§4.1](https://chem.libretexts.org/Bookshelves/Analytical_Chemistry/Analytical_Chemistry_2.1_by_David_Harvey/Analytical_Chemistry_2.1_(Harvey)/04:_Evaluating_Analytical_Data/4.01:_Characterizing_Measurements_and_Results)的Mean/Standard Deviation给出定义，§4.4讨论样本、总体和均值不确定度；这里核验开放章节正文。既引NIST离散程度页是方法手册，pandas文档是表格接口依据，两者职责不同。

汇总用Python3.12标准库`statistics.mean/stdev`，其整数比累积路径避免先把大和/平方和写成浮点；保留最后结果的浮点精度。有限输入仍可能使真实结果超出输出范围，或使非零均值/SD下溢为0。均值输出为0时，额外用Fraction.from_float精确和区分严格相消零；SD为0而有效值不全相同时，也明确拒绝下溢结果。范围失败保存input/audit、statistics-failure.json、failure.json和结果包，不写成功回执。`sample_sd_status=UNDEFINED_N_LT_2`仅用于n<2；n≥2成功为DEFINED，计算失败单列。单位改变与有限性不能证明数据化学合理，极大/极小值测试只检数值边界。[定义与实现来源](runtime/sources.json)。

## 安装、默认运行与保存

Windows解压到有写入权限的短路径，如`D:\Chem\clean`，进入README和runtime所在目录。Python 3.12，使用独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\clean_chemical_data.py --output ..\clean-default
```

结果目录必须在Skill之外且不存在；再次运行换成`..\clean-default-2`。保留该目录或复制其中results.zip即可保存。audit.csv包含所有原列及派生状态；issues.csv只列问题行，group-summary.csv列每组总数、有效数、排除数、均值、样本SD、最小/最大值及单位。回执、输入、实际参数、Skill快照、SHA-256和结果ZIP同时保存。文件级失败返回非零并保留已取得输入及failure.json。

## 三个案例：调用与结果对应

以下均为项目编写的**合成教学数据**，不是实验测量或化学方法学验证。

| 案例 | 调用代码 | 对应结果 |
| --- | --- | --- |
| ①重复记录与SD | `python runtime/examples/01_replicates.py --output ../clean-replicates` | A组50、70、50全保留，均值56.6667，样本SD11.5470；B组80、90均值85，SD7.0711。重复行及ID001两行均标记，不自动删除 |
| ②缺失、坏数字和范围 | `python runtime/examples/02_issues.py --output ../clean-issues` | 显式0–100范围；0、75有效，空/bad/105/inf分别为MISSING/INVALID_NUMERIC/OUT_OF_DECLARED_RANGE/NONFINITE。6行保留，4行排除统计；NA仍是字面组名，单值SD留空 |
| ③元数据连接 | `python runtime/examples/03_join.py --output ../clean-join` | 用batch连接A→ethanol、B→water；右键唯一，5行输入仍为5行且顺序不变。未知键不丢行，重复右键拒绝 |

Windows将表中python替换为`.\.venv\Scripts\python.exe`。完整程序：[①](runtime/examples/01_replicates.py)、[②](runtime/examples/02_issues.py)、[③](runtime/examples/03_join.py)。

## 用户CSV与参数修改

输入为UTF-8 CSV、≤2 MB、1–10000行，原字段全部按文本读取。默认列id、batch、yield_pct；列名可显式修改。保留前导零：

```csv
sample,condition,conversion
001,A,25
002,A,35
003,B,
```

在Skill目录外保存为`..\my-data.csv`：

```powershell
.\.venv\Scripts\python.exe runtime\clean_chemical_data.py --input ..\my-data.csv --id-column sample --group-column condition --value-column conversion --unit % --minimum 0 --maximum 100 --output ..\my-clean-results
```

去掉minimum/maximum表示没有这项范围规则，不能因此称数值化学上合理。更换规则必须保存到另一个新目录。右表连接用`--lookup ..\metadata.csv --lookup-key condition`，右表键非空且唯一，非键列不得和原表重名。程序不会执行任意表达式或自动推断分组含义。

## 完整Skill调用模板

完整可运行模板在[call_skill_template.py](runtime/examples/call_skill_template.py)，核心为：

```python
from clean_chemical_data import run_skill

receipt = run_skill(
    input_csv="../my-data.csv", output_dir="../my-clean-results-2",
    id_column="sample", value_column="conversion", group_column="condition",
    unit="%", minimum=0, maximum=100,
)
print(receipt)
```

调用时runtime须在Python模块路径中，完整模板已处理路径。run_skill实际读取并保存顶层SKILL.md及哈希，运行固定Pandas工具；未调用语言模型，不声称模型理解了指令。原始CSV需以文本方式导入电子表格，避免软件自动改变ID或把字段作为公式执行。

代码包完整性见[SHA-256](downloads/SHA256SUMS.txt)。内部验收日志不进入用户包。

## 输入校验与方法依据补充

CSV先按严格引号语法读取，要求所有表头非空且唯一、每条记录恰好与表头同宽；空行、多余字段或缺少字段均拒绝。核对后直接用字符串字段构造DataFrame，不猜索引、不丢字段、不把NA或001改写。失败时保留预算内原始字节与failure.json/结果ZIP；查表输入也在解析前保存。

[Python CSV语法](https://docs.python.org/3.12/library/csv.html)说明记录与引号处理；[pandas2.2读取约定](https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.read_csv.html)提示畸形行的索引推断风险。输入合同由本模块明确限定，不能仅靠库默认值保证字段对应。 分组均值和样本SD只作描述；[NIST离散程度说明](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm)不提供实验独立性、置信区间或因果资格。
