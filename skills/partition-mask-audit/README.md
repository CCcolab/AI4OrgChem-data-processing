# 分区掩码、对称性与谱

按完整互斥索引分区及显式耦合规则审计实对称矩阵掩码与谱，按矩阵角色决定是否要求正定，不把修改算子冒充等价表示或新自洽结果。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/partition-mask-audit-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

生成对称布尔掩码，禁止块置0，报告移除的Frobenius范数、修改前后特征谱及对称残差。overlap角色要求原/新最小特征值严格大于atol；hamiltonian允许不定，不应用一概正定门槛。

掩码改变矩阵，通常改变问题，不等同于基变换。AO Hamiltonian的普通Euclidean特征值不自动等于广义本征问题的轨道能。正定与否取决于矩阵用途；不生成新条件态、SCF或能量解释。

[NumPy eigvalsh/eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持对称矩阵谱；本页显式给出掩码和角色规则。软件谱检查不认证物理算子。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\partition-mask-audit-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

第一例数值数组来自有来源的旧PySCF水分子结果，来源/原始数组SHA-256见runtime/sources.json；本次只重算后处理，没有新SCF。其余反例为项目编写的合成数学输入。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 真实水分子S的分块掩码 | `python runtime/examples/01_case.py --output ../partition-mask-audit-1` | 按O/H1/H2保留对角块，原/新S均正定；这是修改后的矩阵，不是原分子的等价度量。 退出码0。 |
| 2 不定Hamiltonian角色 | `python runtime/examples/02_case.py --output ../partition-mask-audit-2` | −1特征值允许，不因非正定拒绝Hamiltonian。 退出码0。 |
| 3 同矩阵改作overlap反例 | `python runtime/examples/03_case.py --output ../partition-mask-audit-3` | 负特征值不适合作overlap，正定检查失败、退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters为atol、matrix_role（overlap/hamiltonian）、allowed_pairs；data为matrix及partitions（id、indices）。索引从0起始，必须完整互斥；允许对为无序耦合对，若要保留对角块也须显式列出。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

对称掩码只保证显式保留/删除的耦合与对称性，不一般保持正定性。Hamiltonian允许负本征值，overlap须另过正定门槛；这两个role是输入协议，不是可互换的物理解释。eigh接口不把普通特征值自动变成非正交AO广义本征能量。
