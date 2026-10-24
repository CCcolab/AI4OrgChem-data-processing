# 同一Hamiltonian路径闭合

复核按顺序提供的有向能差循环、算子/基组/几何/电子数标签及绝对闭合残差，拒绝未定义桥接的混合比较，不生成新量子能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/same-hamiltonian-path-closure-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

每条delta=E(to)−E(from)，按顺序构成首尾闭合循环，用50位Decimal求和，按显式atol_hartree和rtol=0判断。来自同一能量表的差分本就代数相消；即使闭合也不是独立验证。不同source_id只是声明，不能证明来源独立或真实性。

只复核给定的2–100条有向能差及比较身份；不执行SCF、寻找真实反应路径、生成缺失能差或证明能量分解唯一。算子/基组/几何/电子数必须一致，跨Hamiltonian比较需额外物理桥接，当前接口拒绝。

本模块展示明确声明的状态差分与循环求和数学定义；[Python Decimal](https://docs.python.org/3/library/decimal.html)支持十进制运算。未核实的化学循环、约束态或跨算子端点不获科学资格，不能因算术闭合自动升级。

## 输入校验与方法依据补充

能量算术采用skill-ledger-decimal-v2：每个十进制输入文字≤128字符、系数≤80位、Decimal指数在−200至200；不接收布尔值、特殊值或带空白文字。这里“系数位数/指数”指Decimal数字元组，不是化学有效数字认证。总精度由所有输入跨度及项数上界推导，上限1024位；乘积求和、独立总量差及阈值比较在同一精确上下文进行。任何Inexact/Rounded或预算越界均失败，绝不把失去的小残差当作闭合。回执的arithmetic记录策略与实际精度，原atol不变。

[Python3.12 Decimal：舍入与相消](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)明确有限精度仍会舍入；本策略只保证所定义有界算术，不认证能量来源、方法、端点真实性或物理可比性。例如1e60+0.1−1e60必须报告0.1，不能据夸张数值声称化学合理。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\same-hamiltonian-path-closure-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 闭合的合成有向循环 | `python runtime/examples/01_case.py --output ../same-hamiltonian-path-closure-1` | 0.1+0.2−0.3=0；只是合成算术验证。 退出码0。 |
| 2 故意不闭合的反例 | `python runtime/examples/02_case.py --output ../same-hamiltonian-path-closure-2` | 残差0.01 Hartree，保存结果并退出1，不能返回全流程成功。 退出码1。 |
| 3 不同算子的拒绝反例 | `python runtime/examples/03_case.py --output ../same-hamiltonian-path-closure-3` | 比较身份不一致，保留输入和failure.json，退出2。 退出码2。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters：operator_id、basis_id、geometry_id、electron_count、atol_hartree。data.edges逐项含from、to、delta_hartree、source_id及相同四个比较身份字段。用实际来源替换合成例标签，不只修改能差数字。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

环差定义ΔE=E(to)−E(from)。若每条边都来自同一能量表，闭合是消去共同端点的代数恒等式；只有独立来源、相同比较身份和明确桥接才可能支持额外检验。这里不宣称路径独立性或某新哈密顿量理论。
