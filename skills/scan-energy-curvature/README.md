# 几何扫描与能量曲率

对明确态、方法、坐标定义与单位的已取得能量扫描执行局部三点一/二阶差分及可用的步长对照，拒绝已知态切换和未收敛点，不生成新能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/scan-energy-curvature-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

能量单位限定Hartree，坐标显式angstrom、bohr、degree或radian，不自动换算。以中心附近三点局部二次插值求一/二阶导数，支持非均匀步长；有额外两侧邻点时另取更粗三点对照。差值只是敏感性诊断，不是误差界或收敛证书；没有足够邻点写NOT_EXECUTED。

输入是已经取得的能量扫描，不启动量子后端。方法/态/收敛标签必须一致，仍需专业核对实际波函数连续性；标签相同本身不是证明。局部曲率不是完整振动Hessian、反应机理或无约束极小点资格。

[NumPy差分说明](https://numpy.org/doc/stable/reference/generated/numpy.gradient.html)给出非均匀三点公式及有限差分语境；本程序显式解权重并另算二阶导数，不声称调用gradient就完成二阶或科学验证。

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
