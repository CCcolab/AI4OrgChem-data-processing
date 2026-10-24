# 镜面反射与子空间奇偶

复核显式提供的实AO反射、度量酉性、二次反射恒等与子空间闭合，只有通过后才给指定空间的奇偶适配，不从矩阵标签猜几何镜面。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/reflection-parity-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

检查R²=I、RᵀSR=S、BᵀSB=I以及RB−B(BᵀSRB)的平方S范数。仅闭合时对限制反射对角化，谱须为±1才输出适配列；不闭合时不贴奇偶标签。

代数通过不证明输入R确实对应所说几何镜面；还需坐标、原子/壳层映射和AO约定。奇偶在指定空间内定义，不能直接认证轨道化学类型、能量或密度不变性；占据兼容需单独检查。

反射、度量和闭合公式在本页显式给出；[NumPy eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)支持限制算子的实对称分解。

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
