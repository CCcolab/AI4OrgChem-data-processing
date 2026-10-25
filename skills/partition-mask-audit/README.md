# 分区掩码、对称性与谱

按完整互斥索引分区及显式耦合规则审计实对称矩阵掩码与谱，按矩阵角色决定是否要求正定，不把修改算子冒充等价表示或新自洽结果。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/partition-mask-audit-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：矩阵掩码与基变换的区别

前提是有限实对称矩阵、每个索引恰好出现一次的分区，以及显式允许的无序耦合对。用对称0/1矩阵M构造H′=M∘H（逐元素相乘），所以H′仍对称；但删除元素通常改变算子或度量。它与可逆基变换Hnew=TᵀHT、Snew=TᵀST不同，不能据形状相同称等价表示。

对overlap，uᵀSu应对所有非零u为正；本实现以原/新最小特征值均严格大于atol作数值门槛。只保留全部对角块时，各块是原SPD矩阵的主子矩阵，块直和仍SPD；任意其他对称删耦合则无此保证。例如3×3矩阵对角1、非对角0.9原最小谱0.1，单独删a–c耦合而留a–b/b–c后最小谱约−0.2727922061。

Hamiltonian的负本征值本身不构成错误，能量零点可变，不能套用overlap正定门槛。在非正交AO中轨道方程是Hc=Scε；普通eig(H)只描述输入矩阵的欧式谱，不自动是广义能谱。若同时使用改后的S/H，需要重新定义科学问题、约束及求解协议，本工具不代做。

①保存水S按O/H1/H2留对角块可以通过正定检查，但不代表原分子的等价度量；②不定矩阵在hamiltonian角色可通过；③相同矩阵作overlap应失败。移除Frobenius范数只是矩阵差指标，不是相互作用能、能量误差或新条件态结果。

### 经典教材、实现来源及支持范围

[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§4.2、§8.1、§8.7与[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Atomic Basis Functions/Hartree-Fock Theory分别提供数值与AO背景；正定检查不认证输入的物理算子身份。

本模块所引L1与Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

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
