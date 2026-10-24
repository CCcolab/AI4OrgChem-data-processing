# 整理化学数据：Pandas清洗与统计

适用于小规模实验结果表的数值审计、重复标记、分组描述统计和元数据连接。保留原始记录，不自动去重、删异常值、插补或换单位；这里的“清洗”是把问题显式列出来。

| 文件 | 职责 |
| --- | --- |
| 本README | 知识、案例、输入输出和操作说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 处理指令、数据约定及统计边界，可下载用于自己的代理 |
| [runtime/clean_chemical_data.py](runtime/clean_chemical_data.py) | 读取Skill→校验CSV→数值分类→分组统计/受约束连接→保存完整结果 |

程序、依赖和案例都在runtime。下载[完整Python代码包](downloads/chemical-pandas-cleaning-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub文件页用“Download raw file”下载，不把网页另存为程序。

## 必要知识

原始值、解析后的数字和缺失原因应分开保存。0不是缺失；文本NA不自动解释成空。重复行可能是误录，也可能是实验重复，程序只标记、不替用户决定。分组均值与样本SD描述当前记录，不证明差异显著、测量准确或因果关系。SD使用ddof=1，只有一个有效值时不定义；技术重复不能直接当独立样本。

单位参数是标签，不换算。混合单位、检测限值、百分号后缀或千位逗号需先确认规则。本版不做结构解析、实验真实性认证、置信区间、SEM或假设检验。[read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)、[to_numeric](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html)、[GroupBy.std](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.std.html)和[merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)给出实际软件约定。

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
