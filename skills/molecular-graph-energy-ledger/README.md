# 分子图匹配与能量账本

独立执行有界SMARTS图匹配或有来源的同态Hartree账本算术，保留原始结构、原子索引和科学身份，不从图生成量子能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/molecular-graph-energy-ledger-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


## 已验证运行环境与功能

**下列数据/数值功能已在本地运行成功；结论限定于列出的操作与案例。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | rdkit 2026.3.6 |
| 本轮已验证功能 | 有界SMARTS图匹配与已给账本入口；本轮正路径只运行图匹配，不生成量子能量；参数修改与已有结果保护 |
| 测试内容 | default、changed-parameter、existing-output-protection；结果文件、ZIP CRC与SHA-256核对 |
| 测试结果 | 3/3项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 图匹配与来源账本是两类功能；本轮未完整复验所有能量账本分支，不由图生成能量，不认证化学身份。 |

使用已有独立Python环境，没有在本轮重新安装依赖。通过所列小型案例不等于全部平台、输入分布或科学用途已认证。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/docs/VERIFIED_ENVIRONMENTS.md)。


## 知识与适用边界

图模式按query_smarts和include_chirality执行GetSubstructMatches。酸OH模式在乙酸/乙酸根/碳酸分别匹配1/0/2；不是通用羧酸分类器。账本为Σ coefficient×value_hartree，使用按输入跨度确定精度的有界Decimal-v2，与独立声明reference_hartree按显式绝对容差比较。来源标签不等于鉴定，闭合不验证物理分解。

图与账本是独立模式。图模式使用RDKit默认解析，保留原SMILES、清理/映射/立体警告及零起始匹配原子索引；SMARTS≤32原子、每分子最多1000个非截断匹配，最多50个小分子。不执行无界图枚举、通用身份认证或芳香性理论判定。账本模式只接受显式同方法、基组、几何、态与算子标签的同态Hartree线性组合；方法不同不能靠换单位解决。

[RDKit查询接口](https://www.rdkit.org/docs/source/rdkit.Chem.rdchem.html)；[Daylight SMARTS](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html)；[Python Decimal](https://docs.python.org/3/library/decimal.html)。这些资料支持语言/软件与算术，不提供本案例的分子量子能量。

## 输入校验与方法依据补充

能量算术采用skill-ledger-decimal-v2：每个十进制输入文字≤128字符、系数≤80位、Decimal指数在−200至200；不接收布尔值、特殊值或带空白文字。这里“系数位数/指数”指Decimal数字元组，不是化学有效数字认证。总精度由所有输入跨度及项数上界推导，上限1024位；乘积求和、独立总量差及阈值比较在同一精确上下文进行。任何Inexact/Rounded或预算越界均失败，绝不把失去的小残差当作闭合。回执的arithmetic记录策略与实际精度，原atol不变。

[Python3.12 Decimal：舍入与相消](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)明确有限精度仍会舍入；本策略只保证所定义有界算术，不认证能量来源、方法、端点真实性或物理可比性。例如1e60+0.1−1e60必须报告0.1，不能据夸张数值声称化学合理。

## 知识要点与经典依据

图模式输出SMARTS查询原子到解析图原子的索引映射，索引依解析后的图和查询顺序；它不是分子身份鉴定。手性是否参与由include_chirality明确控制。含OH的酸片段在乙酸/乙酸根/碳酸的1/0/2是查询语义，不是可推广到所有酸的类别判决。Gasteiger编专著II.3/II.4/II.6及VI.1提供结构、图、立体和子结构检索的经典阅读定位。[Gasteiger编《Handbook of Chemoinformatics》](https://onlinelibrary.wiley.com/doi/book/10.1002/9783527618279)，Wiley-VCH，2003；核验的是出版社/作者目录与书目，所列付费章节未作全文核验。经典结构表示背景与具体RDKit接口定义分层使用。

账本模式独立计算`Eassembled=Σc_i E_i`、`residual=Eassembled−Ereference`，当`|residual|≤atol_hartree`才满足声明的算术闭合。同方法、基组、几何、态和算子标签是当前接口比较条件；同单位并不能消除不兼容。参考源须单列，不能把本次求和结果伪装为独立证据。即使−10+2=−8，也只核实这个组合，不能从图或项名导出电子能或证明能量分解唯一。

Jensen§1.2/§1.6.2用于理解系统定义和Hamiltonian各项，而本模块具体分项由请求协议定义；专著不为任意账本提供物理背书。[Jensen《Introduction to Computational Chemistry》3版](https://catalogimages.wiley.com/images/db/pdf/9781118825990.excerpt.pdf)，Wiley，2017，实际核验出版社开放第1章节选；后述推导为本页给定模型的解析运算，不冒称读过整书。
Decimal-v2按有界输入跨度确定精度并捕获舍入，精度见回执；十进制文字可避免先丢失所需小数位，但不增加实验有效数字。[来源层次与访问限度](runtime/sources.json)。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\molecular-graph-energy-ledger-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 酸、阴离子与碳酸查询 | `python runtime/examples/01_case.py --output ../molecular-graph-energy-ledger-1` | 匹配数1、0、2，保留查询原子索引。 退出码0。 |
| 2 有手性约束的镜像结构查询 | `python runtime/examples/02_case.py --output ../molecular-graph-energy-ledger-2` | include_chirality=True时匹配数1、0；改False时两条都匹配。 退出码0。 |
| 3 有明确来源的合成账本 | `python runtime/examples/03_case.py --output ../molecular-graph-energy-ledger-3` | −10+2=−8 Hartree，残差0；这是假设数字的算术，不是新QM。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。graph参数：mode、query_smarts、include_chirality；data.molecules含id、smiles。ledger参数：mode、protocol_id、atol_hartree；data含terms、reference_hartree、reference_source、quantity_definition，项的科学身份字段见第三例JSON。不同模式不强迫同时提供图和能量。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

SMARTS部分依据RDKit的查询语义；能量分项、正负号及同态协议是用户明确提供的账本定义，不由图匹配导出。Decimal说明仅支持算术实现，不是量子能量分解的理论背书。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
