# 固定协议普通态与条件态账本复核

**后端待验 · PARTIAL_BACKEND_PENDING**：仅验证账本闭合与显式资格标签；新条件态量子计算未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

按明确定义的固定协议、算子和占据声明，复核普通/条件账本及端点资格标签，区分算术、输入证据和新量子计算，不开放用户任意条件态Compute。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/fixed-protocol-energy-review-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

逐项按声明的coefficient×value_hartree用50位Decimal求和，与reported_total_hartree按显式绝对容差比较；同方法/基组/几何/协议身份必须匹配。只有两端声明可用且账本通过才报告conditional−ordinary，否则比较量为null。来源与资格标记仍须外部实证复核。

本模块仅复核已给定数字及定义，不运行普通/条件SCF，不推导通用条件功能式。修改功能式所得差值不自动等于物理键能、激发能或实验观测。实际条件量子后端本轮未运行，不能用合成例通过代替；既有服务没有合格端点时继续关闭。

[Python Decimal](https://docs.python.org/3/library/decimal.html)支持十进制算术；科学协议、算子、占据、端点来源需由对应真实研究协议提供，不能由软件库文档代替。

## 输入校验与方法依据补充

能量算术采用skill-ledger-decimal-v2：每个十进制输入文字≤128字符、系数≤80位、Decimal指数在−200至200；不接收布尔值、特殊值或带空白文字。这里“系数位数/指数”指Decimal数字元组，不是化学有效数字认证。总精度由所有输入跨度及项数上界推导，上限1024位；乘积求和、独立总量差及阈值比较在同一精确上下文进行。任何Inexact/Rounded或预算越界均失败，绝不把失去的小残差当作闭合。回执的arithmetic记录策略与实际精度，原atol不变。

[Python3.12 Decimal：舍入与相消](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)明确有限精度仍会舍入；本策略只保证所定义有界算术，不认证能量来源、方法、端点真实性或物理可比性。例如1e60+0.1−1e60必须报告0.1，不能据夸张数值声称化学合理。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\fixed-protocol-energy-review-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 明确定义的合成账本 | `python runtime/examples/01_case.py --output ../fixed-protocol-energy-review-1` | 两账本闭合，合成功能差0.2 Hartree；仅算术验证，不是新条件态。 退出码0。 |
| 2 几何不一致 | `python runtime/examples/02_case.py --output ../fixed-protocol-energy-review-2` | 拒绝同几何比较并保存失败，退出2。 退出码2。 |
| 3 端点资格未通过 | `python runtime/examples/03_case.py --output ../fixed-protocol-energy-review-3` | 保存账本、比较差为null，检查失败退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters显式protocol_id、protocol_version、method_id、basis_id、geometry_id、atol_hartree。data含comparison_definition和ordinary/conditional两条states，每态含算子/占据定义、收敛及端点资格、带source_id的功能式项与另报总能量。具体完整schema见案例JSON，不可省略或靠标签补算。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

普通态与条件态的算子、占据、几何和泛函组成必须由实际协议及来源给定。本程序只核对该协议的账本和显式资格；缺少真实新后端证据时继续PARTIAL_BACKEND_PENDING，不以算术闭合命名物理键能、激发或可观测量。
