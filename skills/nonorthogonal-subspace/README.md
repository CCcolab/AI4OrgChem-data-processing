# 非正交子空间与泄漏复核

用明确正定实度量复核用户子空间与向量，报告Gram数值秩、S正交投影、残差平方范数及有定义的相对泄漏，不把系数平方和或投影误差当能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/nonorthogonal-subspace-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

G=BᵀSB，按λ>rank_rtol×λmax保留Gram方向；P=B G⁺ BᵀS。分别报告vᵀSv、rᵀSr及比值；零/近零原范数的比值写null。检查P²=P、PᵀS=SP和保留范围对残差的S正交性。阈值及数值秩是工程约定，不是物理概率解释。

只处理有限实正定度量；不支持复杂、奇异或不定度量。泄漏是指定向量与指定子空间的平方S范数差，不自动等于电子数、能量损失或化学局域性。输入AO身份和度量来源必须由研究者核对。

投影公式在此显式给定；[NumPy eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持对称Gram矩阵分解。软件分解不认证AO物理身份。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\nonorthogonal-subspace-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

第一例数值数组来自有来源的旧PySCF水分子结果，来源/原始数组SHA-256见runtime/sources.json；本次只重算后处理，没有新SCF。其余反例为项目编写的合成数学输入。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 真实保存轨道投影 | `python runtime/examples/01_case.py --output ../nonorthogonal-subspace-1` | 占据轨道落在占据空间、虚轨道S正交；泄漏比例分别约0和1。只重算旧数组。 退出码0。 |
| 2 相关列与数值秩 | `python runtime/examples/02_case.py --output ../nonorthogonal-subspace-2` | 两个相关基列保留秩1；两个目标平方S范数分别2和1，泄漏0和1。 退出码0。 |
| 3 零向量反例 | `python runtime/examples/03_case.py --output ../nonorthogonal-subspace-3` | 投影与绝对泄漏为0，原范数为0，相对泄漏必须null。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters为atol、rank_rtol（1e-12至1e-4）；data为overlap、basis、vectors，均实数组，vectors按列。S正定，最小特征值>1e-10、条件数≤1e10；不静默截断环境度量S。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
