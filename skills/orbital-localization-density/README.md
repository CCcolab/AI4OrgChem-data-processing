# 轨道旋转、局域化与密度复核

**后端待验 · PARTIAL_BACKEND_PENDING**：已验证给定旋转与密度不变性；实际Boys/Pipek局域化优化后端未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

复核用户提供的实AO轨道旋转、度量正交性、占据兼容与密度/固定矩阵能量不变性，不把任意旋转称为已完成Boys或Pipek局域化。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/orbital-localization-density-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

C′=CU，D=C diag(n) Cᵀ；核对CᵀSC=I、UᵀU=I、U diag(n) Uᵀ=diag(n)、相对密度差及Tr(DS)。只有等占据混合才保持密度；占据/虚空间互混不获不变性。能量对照只在固定hcore/veff下计算，不代表新自洽端点。

本程序是旋转/局域化输出的复核器，没有优化Boys或Pipek–Mezey目标。没有真实局域化程序输出时不能说已经得到化学局域轨道；也不自动分类σ/π、成键或孤对。新局域化后端、波函数稳定性和新SCF本轮未执行。

[PySCF局域轨道说明](https://pyscf.org/user/lo.html)区分不同局域化目标及酉旋转；[PySCF SCF](https://pyscf.org/user/scf.html)给出密度实现语境。当前工具仅执行明确列出的矩阵复核。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\orbital-localization-density-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

第一例数值数组来自有来源的旧PySCF水分子结果，来源/原始数组SHA-256见runtime/sources.json；本次只重算后处理，没有新SCF。其余反例为项目编写的合成数学输入。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 真实保存AO数组的占据内旋转 | `python runtime/examples/01_case.py --output ../orbital-localization-density-1` | 密度、电子数和固定矩阵能量保持；数据来自已有RHF，不是新SCF或新局域化。 退出码0。 |
| 2 非单位度量的等占据旋转 | `python runtime/examples/02_case.py --output ../orbital-localization-density-2` | 两条占据均2，交换/变相后D和Tr(DS)保持；能量证据缺少，能量检查明确未执行。 退出码0。 |
| 3 占据与虚轨道混合反例 | `python runtime/examples/03_case.py --output ../orbital-localization-density-3` | 占据兼容/密度不变性检查失败，保存差异并退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters为atol、density_semantics=SPIN_SUMMED_REAL_AO_RHF；data必需overlap、coefficients、occupations、rotation。可选hcore、veff、nuclear_hartree必须成组提供；不默补能量。实数组每维≤128，S正定且条件数≤1e10，占据仅0/2。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
