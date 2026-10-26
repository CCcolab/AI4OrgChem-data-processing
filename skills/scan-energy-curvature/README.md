# 几何扫描与能量曲率

对明确态、方法、坐标定义与单位的已取得能量扫描执行局部三点一/二阶差分及可用的步长对照，拒绝已知态切换和未收敛点，不生成新能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/scan-energy-curvature-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


## 已验证运行环境与功能

**下列数据/数值功能已在本地运行成功；结论限定于列出的操作与案例。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | numpy 2.4.6 |
| 本轮已验证功能 | 已有扫描表的局部有限差分导数与曲率；本轮使用明确的合成标量函数；参数修改与已有结果保护 |
| 测试内容 | default、changed-parameter、existing-output-protection；结果文件、ZIP CRC与SHA-256核对 |
| 测试结果 | 3/3项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 未运行新几何扫描或确认电子态连续性；有限差分检查不认证物理反应曲率。 |

使用已有独立Python环境，没有在本轮重新安装依赖。通过所列小型案例不等于全部平台、输入分布或科学用途已认证。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](../../docs/VERIFIED_ENVIRONMENTS.md)。


## 知识与适用边界

能量单位限定Hartree，坐标显式angstrom、bohr、degree或radian，不自动换算。以中心附近三点局部二次插值求一/二阶导数，支持非均匀步长；有额外两侧邻点时另取更粗三点对照。差值只是敏感性诊断，不是误差界或收敛证书；没有足够邻点写NOT_EXECUTED。

输入是已经取得的能量扫描，不启动量子后端。方法/态/收敛标签必须一致，仍需专业核对实际波函数连续性；标签相同本身不是证明。局部曲率不是完整振动Hessian、反应机理或无约束极小点资格。

[NumPy差分说明](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)给出非均匀三点公式及有限差分语境；本程序显式解权重并另算二阶导数，不声称调用gradient就完成二阶或科学验证。

## 知识要点与经典依据

三点差分近似的是给定扫描坐标q上的导数，不是自动求出了完整分子Hessian。设左/右步长hm、hp>0，d−=E(q−hm)−E(q)，d+=E(q+hp)−E(q)。局部二次插值给出

`E′≈(−hp·d−/hm+hm·d+/hp)/(hm+hp)`，

`E″≈2(d−/hm+d+/hp)/(hm+hp)`。

hm=hp=h时退化为通常中心公式；二次函数可精确复核。一般光滑函数的非均匀二阶公式含与hp−hm有关的三阶项，不能不加条件就称二阶收敛。E=q³在q=0、hm≠hp时会产生`2(hp−hm)`的曲率反例。能量噪声可被1/h或1/h²放大，步长越小并非总越好；粗细差只是敏感性诊断，不能单独给误差上界。

E单位为Hartree时，导数分别为Hartree/q单位与Hartree/q单位²；degree与radian的数值不能直接比较。标签/收敛一致只是准入，真实态连续仍需波函数等证据。沿受限路径的正曲率不证明无约束极小点，也不直接给振动频率。

经典数值定位为Burden/Faires第3章插值与第4章数值微分。[Burden与Faires《Numerical Analysis》9版](https://www.cengage.co.in/book-list/print/numerical-analysis-c2)第1/3/4章分别涉及误差、插值与数值微分；本次核验出版社目录，未取得这些章节全文，不借目录声称已核对误差定理。
Jensen公开§1.6.2/§1.9说明几何参数与势能面背景。[Jensen《Introduction to Computational Chemistry》3版](https://catalogimages.wiley.com/images/db/pdf/9781118825990.excerpt.pdf)，Wiley，2017，实际核验出版社开放第1章节选；后述推导为本页给定模型的解析运算，不冒称读过整书。
NumPy gradient的公开推导支持非均匀一阶语境，上述二阶式来自本页局部插值推导；[runtime/sources.json](runtime/sources.json)分开记录两者。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\scan-energy-curvature-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 解析二次函数均匀扫描 | `python runtime/examples/01_case.py --output ../scan-energy-curvature-1` | 中心一阶0、二阶1 Hartree/Å²；粗细步长对照相同。合成函数不等于电子能。 退出码0。 |
| 2 非均匀三点 | `python runtime/examples/02_case.py --output ../scan-energy-curvature-2` | E=1+2q+3q²，q=0处一阶2、二阶6；无粗步长邻点明确未执行。 退出码0。 |
| 3 显式态切换 | `python runtime/examples/03_case.py --output ../scan-energy-curvature-3` | 拒绝求导，不用跨态点拼出曲率，保留失败记录，退出2。 退出码2。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters：coordinate_unit、energy_unit、center_index（零起始内部点）、state_id、method_id、geometry_definition。data.points含coordinate、energy_hartree、state_id、method_id、converged、source_id；严格递增坐标，3–1000点。不能凭输出自动断言扫描跟随同一个物理态。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

[NumPy非均匀差分推导](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html#notes)支持三点一阶公式的光滑性前提；本程序二阶量来自同一局部二次插值，二次函数可精确核算不等于对真实势能面给出误差上界。来源/收敛标签不能自动证明电子态连续，非均匀步长和单位须随结果保留。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
