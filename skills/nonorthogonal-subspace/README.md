# 非正交子空间与泄漏复核

用明确正定实度量复核用户子空间与向量，报告Gram数值秩、S正交投影、残差平方范数及有定义的相对泄漏，不把系数平方和或投影误差当能量。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/nonorthogonal-subspace-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。

## 核心知识：S度量投影、截断与泄漏的含义

前提是有限实正定S、同一AO顺序的基列B和按列的目标v。内积为⟨u,v⟩S=uᵀSv，平方范数为vᵀSv；它与普通系数平方和不同。G=BᵀSB=UΛUᵀ，仅保留λ>rank_rtol λmax的方向r，定义Q=B U_r Λ_r⁻¹/²。直接代入得QᵀSQ=I，故P=QQᵀS=B G_r⁺ BᵀS，P²=P、PᵀS=SP。

令r=v−Pv，则QᵀSr=0，vᵀSv=(Pv)ᵀS(Pv)+rᵀSr。因此泄漏比例为rᵀSr/(vᵀSv)，分母为零或近零时无定义并写null；本工具只报告数值残差比例，不赋予物理概率、电子数或能量含义；归一化物理态及相应测量投影协议未在本工具中给定。谱被截断时投向的是保留子空间，不能要求残差与被丢弃的全部B方向也正交。记号G_r⁺表示按本阈值截断的逆，并不隐含所有非零数学本征值都保留。

可令S=WᵀW，把WB置于欧式空间理解上述投影，再还原到原AO表示。形成Gram会把WB的奇异值平方，故Gram的相对特征值阈值对应奇异值相对阈值的平方；列缩放也可能改变有限精度的保留秩。rank_rtol与atol是数值合同，不是物理误差条。本实现不静默截断环境S，也不处理复、奇异或不定度量。

①保存占据轨道目标泄漏约0，S正交虚轨道约1，均是旧数据后处理；②相关列只保留秩1而不重复计空间；③零向量投影/绝对泄漏0但相对值null。覆盖结论只关于用户实际提供的目标和保留空间，AO身份仍须独立核实。

### 经典教材、实现来源及支持范围

[L1：Golub、Van Loan，Matrix Computations，第4版，JHU Press，2013，ISBN 9781421407944](https://www.press.jhu.edu/books/title/10678/matrix-computations)的§4.2、§5.5、§6.4是正定度量、秩亏与子空间的经典入口。原有[Strang投影课程](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/resources/lecture-16-projection-matrices-and-least-squares/)是大学课程页，支持欧式直观，不伪装成已读加权AO投影教材正文。

本模块所引L1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

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
