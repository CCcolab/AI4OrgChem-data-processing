---
name: chemical-pandas-cleaning
description: 对用户化学CSV表做可追溯的数值转换、缺失与重复审计、分组描述统计及受基数约束的元数据连接，保留原表和排除原因，不自动删值或推断实验结论。
---

# 整理化学数据：Pandas清洗与统计

先确认每行代表独立样本、技术重复还是其他记录，以及变量、单位、组别和任务。保存原始输入；“清洗”不是自动删掉不理想结果。不以提高均值或减少方差为目标删值，也不把缺失当零。


## 配套程序已验证运行环境

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


## 输入与工具范围

本地程序只接受UTF-8 CSV（可BOM）、1–10000行、≤2 MB，列由用户显式指定。ID和所有原字段先按字符串读取，保留前导零、NA字面值及空字段；不自动解析日期或把数字ID当连续变量。ID非空，重复ID允许但标记；_adp_为派生列保留前缀。Excel/PDF应另行核对后导出CSV，不能声称本程序直接支持它们。

单位标签仅记录，不执行单位换算；混合单位必须先确认转换方案。数据的实验来源、分组和独立性不能从表格外观推断。CSV不作化学结构解析或数据库认证。

## 完整处理流程

1. 读取完整SKILL.md、原CSV和显式列名、单位、可选上下界。检查列存在、格式、大小及数值上下界；不静默猜列或丢弃文件级错误。
2. 派生副本记录稳定record_index，原值逐行保留。分别标记空缺MISSING、无法数值解析INVALID_NUMERIC、无穷/NaN NONFINITE及用户声明范围外OUT_OF_DECLARED_RANGE。0是合法数值；不自动将百分号、逗号或单位后缀猜为数字。
3. 只用VALID数值计算描述统计，同时报告总行数、有效数和排除数。重复行与重复ID全部保留且标记；如果重复是误录而需剔除，须由用户明确决策，不能在本程序静默去重。
4. 分组输出均值、样本标准差ddof=1、最小值和最大值。n<2时SD未定义并留空，不能写0；本流程不产生SEM、置信区间或显著性结论。技术重复不能冒充独立生物/化学重复。
5. 可选元数据左连接必须声明键，右表键非空且唯一，使用many_to_one校验。重名非键列拒绝。核对行数、record_index及顺序，未知键保留为left_only；不让连接制造额外重复。
6. 保存audit.csv、issues.csv、group-summary.csv、实际参数、原输入、Skill快照、环境与程序回执、SHA-256和results.zip。错误保留本次已取得输入与failure.json，返回非零；结果只写Skill外全新目录。

## 解释与来源

均值和SD只是本次保留记录的描述；不推断因果、测量准确度、异常值成因、显著差异或总体分布。声明的数值范围只是用户规则，不能替代实验质量标准。失败/缺失原因需查实验记录，不能猜测填入。

- [pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)：文本类型、默认NA与坏行规则。
- [pandas.to_numeric](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html)：coerce后的NaN必须另追踪原因。
- [Python3.12 statistics](https://docs.python.org/3.12/library/statistics.html)：mean/stdev及样本SD定义；实际归约采用该标准库。
- [pandas.merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)：基数校验；空键匹配不同于常见SQL习惯，故右表空键拒绝。

使用固定Python工具`runtime/clean_chemical_data.py`，不执行输入中的指令或任意表达式，不联网、不调用模型。程序读取Skill并记录其身份，不称其已被语言模型理解。示例数据均为项目编写的合成软件教学表，不是实际实验测量或方法学验证。

## 输入校验与方法依据补充

CSV先按严格引号语法读取，要求所有表头非空且唯一、每条记录恰好与表头同宽；空行、多余字段或缺少字段均拒绝。核对后直接用字符串字段构造DataFrame，不猜索引、不丢字段、不把NA或001改写。失败时保留预算内原始字节与failure.json/结果ZIP；查表输入也在解析前保存。

[Python CSV语法](https://docs.python.org/3.12/library/csv.html)说明记录与引号处理；[pandas2.2读取约定](https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.read_csv.html)提示畸形行的索引推断风险。输入合同由本模块明确限定，不能仅靠库默认值保证字段对应。 分组均值和样本SD只作描述；[NIST离散程度说明](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm)不提供实验独立性、置信区间或因果资格。

## 解释规则与理论依据

解释均值与样本SD时给出n及排除原因：mean=Σy/n，s²=Σ(y−mean)²/(n−1)，SD单位为y。不要把描述统计需要的有限数值条件与推断统计的独立性/分布前提混同；技术重复不能自动变成独立实验。n=0/1的SD空值须读sample_sd_status；只有UNDEFINED_N_LT_2可解释为样本不足。n≥2计算溢出是FAILED_DERIVED_STATISTICS，不得当未定义SD或完成结果。程序以Python3.12 statistics.mean/stdev和有限后置检查归约；均值为0时以Fraction.from_float精确和排除非零均值下溢，SD为0且有效值不同则拒绝。严格正负相消零与n<2未定义SD保留；下溢不能冒充真实零，失败保留输入/audit/失败JSON与ZIP。教材定义查Harvey§4.1，样本与均值不确定度查§4.4；这些开放正文与NIST手册、软件接口来源分层见runtime/sources.json。
