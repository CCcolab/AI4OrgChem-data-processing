# 轨道旋转、局域化与密度复核

**后端待验 · PARTIAL_BACKEND_PENDING**：已验证给定旋转与密度不变性；实际Boys/Pipek局域化优化后端未执行。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

复核用户提供的实AO轨道旋转、度量正交性、占据兼容与密度/固定矩阵能量不变性，不把任意旋转称为已完成Boys或Pipek局域化。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/orbital-localization-density-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：等占据旋转为何保持密度

前提为同一有限实AO顺序、正定S、S正交轨道列C与实正交旋转U。本模块只接受所声明容差内的RHF占据0/2，不处理复轨道、分数占据或自旋分块的一般情形。令n=diag(occupations)，C′=CU，则D′−D=C(UnUᵀ−n)Cᵀ。因为C满列秩，密度保持当且仅当UnUᵀ=n；这要求U保留等占据子空间。

两条占据同为2时任意正交混合有U(2I)Uᵀ=2I；占据2与0的二轨道若各混合45°，原n=diag(2,0)变成含非零交叉项的UnUᵀ，密度通常改变。N=Tr(DS)与轨道系数逐元素是否相同无关。占据空间旋转可改变单轨道外观而保持同一密度；不能据外观自动命名σ/π、孤对或成键轨道。

固定h与Vhf时E=Tr(Dh)+½Tr(DVhf)+Enuc，因此D相同会使此账本相同；本程序不重建Vhf[D]、不求新SCF或稳定性。Boys最小化轨道空间展宽，Pipek–Mezey使用原子人口相关目标，选择目标并实际优化后才能称执行了相应局域化；任意U检查通过不满足这一步。

①保存水的占据内旋转只重算旧数组；②非单位度量的两条等占据轨道旋转保持D，但缺能量矩阵便将能量检查记未执行；③占据/虚空间混合应失败。读结果须同时看CᵀSC、UᵀU、占据兼容、相对密度误差与Tr(DS)，不能只看程序退出或固定能量差。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Orbital Rotations、Hartree-Fock Theory对应旋转与密度理论。具体局域化目标另见[PySCF局域轨道](https://pyscf.org/user/lo.html)，软件说明与经典教材分开标识。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

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
