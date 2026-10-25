# 多态与体系尺寸比较复核

**后端待验 · PARTIAL_BACKEND_PENDING**：仅验证集合完整性及固定权重算术；新多态量子计算未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

按显式态集合、来源、协议和固定权重检查多态/尺寸表的完整性与可比条件，分尺寸给加权账本，不自动生成态或把总能差升级为物理结论。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/multistate-size-comparison-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：声明态全集、固定权重与尺寸比较

先声明每个size所需state ID全集，再要求实际(size,id)集合逐项相等；重复、缺失或未声明项均拒绝，不能仅因已提供若干低能态就称态集合完备。各条需显式非负权重、有限能量、相同protocol/method/basis身份、state_definition、source_id和资格声明；这些标签不鉴定数据真实性，也不证明全部物理态已枚举。

对每个size计算权重和W=Σiwi并检查|W−1|≤weight_atol，再报告候选量Ufixed=ΣiwiEi。代码不将不合格W偷偷归一化，也不调用numpy.average来除W；即使候选算术有值，端点资格或权重门禁失败仍不是合格比较。给定权重的线性和是显式合同，改变输入权重就改变问题，不能由能量表反推出正确人口。在精确非负且W=1时，这也是标量能量的凸组合，故min(Ei)≤Ufixed≤max(Ei)；容差允许的W偏差意味着只能近似应用该界限，当前程序未另做物理人口推断。

只有另有物理系综与概率定义时，能量平均才可解释为相应系综平均。例如正则系综人口需温度、简并度和配分函数；自由能还含熵/配分函数定义，通常不等于Ufixed。本模块不推Boltzmann权重、不计算自由能，也不把不同组成/尺寸的原始总能量相减来排名。跨尺寸比较应先给共同参考、守恒/组成及明确物理量，当前接口不自动补齐。

①完整合成small/large分别得0.75/0.95 Eh，各自独立报告；②缺态拒绝部分平均；③资格不明端点仍保存候选算术并令检查失败。新多态优化、态跟踪、量子谱完备性和真实系综证据未执行。此教学工具是集合/来源合同与固定权重账本，不是多态量子引擎。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Exact and Approximate Wave Functions、Multiconfigurational Self-Consistent Field Theory提供电子态背景，仅核验目录；不把它当作本固定权重合同或统计力学人口的证明。[O1：Boyd、Vandenberghe，Convex Optimization，Cambridge University Press，2004，§2.1.4](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)的作者授权正文已核读，支持非负归一权重的凸组合解释，不支持任意权重的物理人口意义。[NumPy average](https://numpy.org/doc/stable/reference/generated/numpy.average.html)是通用归一化算术API，不能替代系综理论。若未来加入物理人口/自由能功能，应另给并验证相应统计力学教材与协议。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\multistate-size-comparison-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 完整合成态集合 | `python runtime/examples/01_case.py --output ../multistate-size-comparison-1` | small与large分别得0.75和0.95 Hartree的合成加权值；不作跨尺寸差分或物理结论。 退出码0。 |
| 2 缺态拒绝 | `python runtime/examples/02_case.py --output ../multistate-size-comparison-2` | 实际集合不完整，拒绝部分平均，退出2。 退出码2。 |
| 3 资格不明端点 | `python runtime/examples/03_case.py --output ../multistate-size-comparison-3` | 保存候选算术但标未获资格，整体检查失败、退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters含protocol_id、method_id、basis_id、weight_atol、expected_states（每size对应态ID列表）及comparison_definition。data.states逐项给size、id、energy_hartree、weight、eligible、source_id、state_definition和相同方法/基组/协议身份；最多128条。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
