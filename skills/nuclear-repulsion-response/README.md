# 核排斥能及响应

根据显式核电荷和有单位的非周期Cartesian坐标计算核间Coulomb项、原子对贡献、解析梯度/力及Hessian，不推断电子能或分子平衡结构。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/nuclear-repulsion-response-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

原子单位E=Σ(i<j)ZiZj/rij；解析Cartesian梯度、负梯度力与Hessian逐对组装，导数单位按输入坐标换算。bohr=0.529177210544 Å，来自CODATA2022；这是新模块显式约定，不修改项目冻结核心常数。检查净梯度及Hessian对称性，工程门槛均1e-9，不冒充电子结构验证。

仅有限非周期点核，2–64核，实际整数Z为1–86；不接受ECP有效电荷、电子、外部点电荷、周期边界或溶剂项。距离小于1e-6 bohr及非有限结果拒绝。核项不决定分子的总能、稳定性或平衡几何。

[NIST CODATA2022常数表](https://physics.nist.gov/cuu/pdf/wall_2022.pdf)提供bohr/Hartree约定；Coulomb点核公式及其解析导数在本页显式给定。核项不是实验分子总能。

## 知识要点与经典依据

这是固定几何下点核的Coulomb项。原子单位中`Enn=Σ(i<j)ZiZj/r_ij`；Zi为真实核电荷，r以bohr计。对r=Ri−Rj，链式求导得`g_i=−ZiZj·r/r³`、`g_j=−g_i`，力为−g。两单位核在x=0和1bohr时梯度为+1/−1、力向外，核间排斥不意味着整个分子不能成键。

单对Hessian块为`B=ZiZj(3rrᵀ/r⁵−I/r³)`；ii/jj块加B、ij/ji块减B。该组装给出平移方向零响应及对称性。核项可有横向负曲率，因此不能用其本身的特征值判定分子振动或平衡。分子总能还含电子动能、电子—核吸引和电子间相互作用，当前程序没有这些项。

若输入坐标是Å，令a0=0.529177210544Å，r_bohr=R_Å/a0，则`g_Å=g_bohr/a0`、`H_Å=H_bohr/a0²`，能量不变。核电荷为整数并不能自动验证用户没有误填ECP电荷；2–64真实非周期点核是本模块合同。阈值与近接截断是工程保护，不是理论精确性认证。

Jensen公开§1.3与§1.6.2包含Coulomb相互作用及核/电子项分离，给出模型背景；上面的导数为对此模型的显式推导。[Jensen《Introduction to Computational Chemistry》3版](https://catalogimages.wiley.com/images/db/pdf/9781118825990.excerpt.pdf)，Wiley，2017，实际核验出版社开放第1章节选；后述推导为本页给定模型的解析运算，不冒称读过整书。
CODATA2022表提供a0与Hartree常数定义，不提供分子稳定性证明。逐项职责见[runtime/sources.json](runtime/sources.json)。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\nuclear-repulsion-response-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 两单位核相距1 bohr | `python runtime/examples/01_case.py --output ../nuclear-repulsion-response-1` | 核项1 Hartree，x梯度为+1/−1，力方向相反，净力0。 退出码0。 |
| 2 同一几何的Å表达 | `python runtime/examples/02_case.py --output ../nuclear-repulsion-response-2` | 核项仍为1 Hartree；梯度按1/bohr_Å换算，不能直接比较不同单位导数的数字。 退出码0。 |
| 3 三核教学水几何 | `python runtime/examples/03_case.py --output ../nuclear-repulsion-response-3` | 实际计算三个核对贡献及9×9 Hessian；几何未经优化，也没有电子能。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters.coordinate_unit为bohr或angstrom；data.nuclei含唯一id、整数Z、三维xyz。实际核电荷与几何由用户确认，不能从文件名猜。输出energy_hartree、pairs、gradient、force、hessian及单位。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
