# 片段支持与工作基复核

在同一实全局AO度量中组装用户声明的片段支持列，复核支持、数值秩、目标覆盖和可选一电子算子变换，不生成片段能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/fragment-working-basis-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

先拒绝片段列在声明支持外超过atol的元素，再合并B。按Gram保留方向构造Q=B U/√λ，检查QᵀSQ=I及目标残差平方S范数的平方根。可选一电子算子按QᵀHQ变换；没有算子时不制造能量。

全局正交化可能混合片段，输出工作列不保证各自保持原片段支持。保留候选映射、秩和残差，不能把组装成功称为片段能量分解、完整轨道覆盖或新电子结构。二电子张量变换、自洽与量子后端本实现未提供。

本页显式给出Gram正交化与一电子变换公式；[NumPy eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持实对称分解。AO度量和片段映射真实性需另核对。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\fragment-working-basis-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

第一例数值数组来自有来源的旧PySCF水分子结果，来源/原始数组SHA-256见runtime/sources.json；本次只重算后处理，没有新SCF。其余反例为项目编写的合成数学输入。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 真实水分子全局AO组装 | `python runtime/examples/01_case.py --output ../fragment-working-basis-1` | 18个原AO分到O/H1/H2，构造秩18工作空间并覆盖5条占据轨道；可选hcore变换，不生成片段能量。 退出码0。 |
| 2 冗余列降秩 | `python runtime/examples/02_case.py --output ../fragment-working-basis-2` | 3候选列得到秩2，覆盖指定目标。 退出码0。 |
| 3 支持外系数反例 | `python runtime/examples/03_case.py --output ../fragment-working-basis-3` | 声明支持之外存在0.1系数，输入拒绝并保存failure.json。 退出码2。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters为atol、rank_rtol；data含overlap、fragments、target_vectors，可选operator。每个fragment有唯一id、零起始ao_indices和全AO行数的coefficients；≤16片段、总候选列≤128。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
