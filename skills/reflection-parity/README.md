# 镜面反射与子空间奇偶

复核显式提供的实AO反射、度量酉性、二次反射恒等与子空间闭合，只有通过后才给指定空间的奇偶适配，不从矩阵标签猜几何镜面。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/reflection-parity-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：闭合子空间中的反射奇偶

R在这里作用于同一实AO系数列，即变换c↦Rc；它不是随意给名的算子积分矩阵。要求正定S、R²=I、RᵀSR=S和BᵀSB=I。R⁻¹=R与度量酉性联合推出RᵀS=SR，因此限制矩阵T=BᵀSRB实对称。

只有RB落在span(B)时才有RB=BT，也即Δ=RB−BT=0。此时二次作用得B=R²B=BT²；由B满列秩推出T²=I，故限制谱只能为±1。对T作正交对角化T=UΛUᵀ，BU就是给定空间中的奇偶适配列。若不闭合，T只是投影后的反射，出现介于−1与1的数也不能贴成真实奇偶本征值。

闭合残差比较的是sqrt Tr(ΔᵀSΔ)，并非其平方。若平方量为0.0396，范数约0.1989974874，必须按后者比较相同atol。实测微小残差只支持数值阈值内闭合；输入R代表哪个几何镜面仍需坐标、原子/壳层映射及AO球谐/相位约定证明。

①保存水几何与AO标签给出明确镜面，但本次仅代数复核；②二维交换反射在完整空间有±1本征列；③只取e1时交换到e2而离开空间，应不给奇偶标签。BU的旋转没有占据信息，可能混合不等占据，因此不自动保持D；奇偶也不自动等于σ/π、成键分类、能量或新SCF资格。

### 经典教材、实现来源及支持范围

[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§7.6、§8.1提供不变子空间与谱的经典背景；±1结论的前提和推导在上文写全，不能把目录核验当作真实分子群论/AO反射表示的已读正文证明。原有Strang课程仅是投影直观的补充。

本模块所引L1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\reflection-parity-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

第一例数值数组来自有来源的旧PySCF水分子结果，来源/原始数组SHA-256见runtime/sources.json；本次只重算后处理，没有新SCF。其余反例为项目编写的合成数学输入。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 真实水分子保存AO镜面 | `python runtime/examples/01_case.py --output ../reflection-parity-1` | 几何全部x=0，按原AO标签令px/dxy/dxz为奇；占据空间通过闭合后输出±1谱。不是新SCF。 退出码0。 |
| 2 完整二维交换反射 | `python runtime/examples/02_case.py --output ../reflection-parity-2` | 得到−1/+1两个奇偶方向。合成代数案例。 退出码0。 |
| 3 非闭合子空间反例 | `python runtime/examples/03_case.py --output ../reflection-parity-3` | 一维空间被映到外部，闭合检查失败、适配列为空，退出1。 退出码1。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters为atol及mirror_definition；data为overlap、reflection、basis。S正定，B必须S正交归一，R与S同维；真实镜面、原子映射和AO变换约定由用户明确。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
