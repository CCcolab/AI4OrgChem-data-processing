# 多态与体系尺寸比较复核

**后端待验 · PARTIAL_BACKEND_PENDING**：仅验证集合完整性及固定权重算术；新多态量子计算未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

按显式态集合、来源、协议和固定权重检查多态/尺寸表的完整性与可比条件，分尺寸给加权账本，不自动生成态或把总能差升级为物理结论。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/multistate-size-comparison-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

先要求实际(size,id)与声明全集严格一致，不接受缺态、重复或新增未声明态。每size的显式非负权重和须为1；分开报告固定加权能量与端点资格。权重是输入，不从能量猜Boltzmann人口，不偷偷归一化不合格权重。

没有新多态优化、态连续性跟踪或所有物理态完备性证明。资格/source标签只作输入声明，需对应真实输出复核。固定加权平均不是自由能，不自动减去不同组成/尺寸的总能来排名；任何这类比较需要额外物理定义。真实高成本后端本轮未运行，合成表仅软件验证。

固定加权求和与完整集合规则在本页显式定义；[NumPy average](https://numpy.org/doc/stable/reference/generated/numpy.average.html)说明一般加权平均，不提供统计力学人口或量子端点资格。

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
