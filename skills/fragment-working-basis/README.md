# 片段支持与工作基复核

在同一实全局AO度量中组装用户声明的片段支持列，复核支持、数值秩、目标覆盖和可选一电子算子变换，不生成片段能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/fragment-working-basis-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


## 已验证运行环境与功能

**下列数据/数值功能已在本地运行成功；结论限定于列出的操作与案例。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | numpy 2.4.6 |
| 本轮已验证功能 | 给定片段支持、全局AO度量、工作基秩与单电子变换的一致性复核；参数修改与已有结果保护 |
| 测试内容 | default、changed-parameter、existing-output-protection；结果文件、ZIP CRC与SHA-256核对 |
| 测试结果 | 3/3项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 未认证全部双电子张量/新哈密顿量、片段物理解释或相关能计算。 |

使用已有独立Python环境，没有在本轮重新安装依赖。通过所列小型案例不等于全部平台、输入分布或科学用途已认证。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/docs/VERIFIED_ENVIRONMENTS.md)。


## 核心知识：片段候选列与规范工作基

全部片段必须使用同一实全局AO顺序和正定重叠S。片段支持是输入列在哪些AO行允许非零的声明；先拒绝支持外超过atol的系数，再合并候选B。若G=BᵀSB=UΛUᵀ，按rank_rtol保留正谱，Q=B U_r Λ_r⁻¹/²满足QᵀSQ=Λ_r⁻¹/²U_rᵀGU_rΛ_r⁻¹/²=I。这是保留空间的规范正交化，不是保证每列局域的片段算法。

与对称正交化B G⁻¹/²相比，规范形式保留独立谱方向，秩亏时允许减少列数；原片段列可能在U_r中全局混合。因此组装前支持检查通过，不能推断最终每条Q仍属于单一片段。列缩放、近线性相关与Gram阈值会影响数值秩；候选数不是独立自由度数。

目标T的投影为QQᵀST，残差R=T−QQᵀST；报告sqrt Tr(RᵀSR)并与atol比较。通过只说明所给目标被保留空间覆盖，不证明完整虚轨道空间或所有化学性质均被覆盖。给定一电子算子AO矩阵H时，新矩阵为QᵀHQ；Q为矩形时是子空间限制，不能当作保留全谱的可逆基变换。密度系数变换与算子矩阵变换约定也不能混用。

①18个原AO按O/H1/H2输入，覆盖5条保存占据轨道，不产生片段能量；②冗余3列得到秩2体现依赖方向剔除；③支持外0.1系数应拒绝。缺少算子不补能量；二电子张量变换、片段相互作用能、SCF与新量子后端均未提供。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Atomic Basis Functions/Hartree-Fock Theory配合[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§5.5、§6.4、§8.1，分别作为AO与数值子空间基础；这些章节不证明本项目片段能量方法，因为本工具并未实现该方法。

本模块所引L1与Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

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

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
