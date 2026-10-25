# RHF单点：固定教学水分子

**后端待验 · PARTIAL_BACKEND_PENDING**：新固定水RHF计算未执行；已验证输入准备及旧AO数组复核，不能替代新SCF。 新后端执行状态为`NOT_EXECUTED`，本地程序或旧结果检查通过不能替代后端验收。

提供输入准备、已保存AO数组复核和一次真实登记后端调用。当前仅固定水分子RHF/6-31G(d)、中性单重态；不因Skill名称而扩大到任意用户分子或条件态。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例和实际操作 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 输入、方法、身份、预算与解释边界 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill、准备输入/复核AO数组/调用原登记Runtime、保存回执 |

顶层只保留README.md和SKILL.md。程序、依赖、固定输入及案例都在runtime。下载[完整Python代码包](downloads/rhf-single-point-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。GitHub需有权限账号；使用文件页“Download raw file”，不把网页另存为.py。

## 核心知识：从非正交AO到固定水分子RHF复核

AO基函数χμ的重叠为Sμν=∫χμχν dr；本实现仅取有限实数组、可用正定S和原始AO顺序。轨道φi=ΣμχμCμi满足CᵀSC=I。自旋求和占据ni为0/2时，D=C diag(n)Cᵀ，电子密度ρ(r)=ΣμνDμνχμ(r)χν(r)，所以积分电子数N=ΣμνDμνSνμ=Tr(DS)=Σini。Tr(D)只在相应正交表示中才可直接计数；例如S=diag(2,1)、C第一列=(1/√2,0)ᵀ、占据2时，Tr(D)=1而Tr(DS)=2。

固定RHF约定Vhf=J[D]−K[D]/2、F=h+Vhf，能量E=Tr(Dh)+½Tr(DVhf)+Enuc。相互作用按电子对计算，直接对每个电子的平均场求和会把同一对计两次，故有½；不能将它误用于任意标为veff的DFT势或不同密度约定。本复核只比较给定h/V与账本，不重新从双电子积分构造J/K。

RHF是α/β共享空间轨道的闭壳层单行列式近似；偶数电子、单重态及SCF收敛均不足以证明强相关体系适用性、波函数稳定性或真实基态。广义驻点式FC=SCε与正曲率稳定性是不同条件。①只复制固定请求；②保存水分子以10电子和约−76.0090991086 Eh核对七项恒等式；③仍需登记后端及本次科学回执。旧数组通过不变成新SCF，HOMO–LUMO差不直接是激发能。

解释或运行前应核对AO顺序、spin-summed约定、固定几何和方法、单位及来源；一项缺失不能由18×18形状补定。完整虚轨道残差、波函数稳定性、新SCF和实验准确性不在保存数组复核资格内。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Atomic Basis Functions、Orbital Rotations、Hartree-Fock Theory适合作为上述标准理论的教材入口。保留[PySCF SCF](https://pyscf.org/user/scf.html)及[密度/能量源码](https://pyscf.org/_modules/pyscf/scf/hf.html)作实现依据；教材不证明本次后端已运行。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 安装与三个案例

Windows解压到有写权限的短路径，如D:\Chem\rhf，进入README和runtime所在目录。Python3.12独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --mode prepare --output ..\water-prepared
```

| 案例 | 调用 | 结果及范围 |
| --- | --- | --- |
| ①准备固定输入 | `python runtime/examples/01_prepare.py --output ../water-prepared-2` | 复制request.json/XYZ，PREPARED_NOT_EXECUTED，没有新SCF |
| ②复核有来源的旧AO数组 | `python runtime/examples/02_review.py --output ../water-reviewed` | 重算Tr(DS)约10、能量账本约−76.0090991086 Hartree等7项明确检查。不是新能量生成或新RHF验收 |
| ③新RHF | `python runtime/examples/03_compute.py`加下述身份参数及全新输出 | 使用已有登记Runtime和Linux Docker引擎；本轮目前待启动引擎，尚未完成新SCF验收，不能借用②的结果 |

Windows将python替换为`.\.venv\Scripts\python.exe`。保存数组含其来源origin.json和原执行身份；未把内部验收日志放进用户包。源码完整可读，不包含模型密钥或账号配置。

## 真实后端：先核实自己的安装

本Python代码包不包含PySCF容器、Docker或Runtime安装；准备/旧数组复核不需要它们。新计算必须使用自己已经登记且来源核实的Runtime，不在这里自动下载、安装、构建或重新登记。

设置下面四个变量为你已有安装的真实路径和预期哈希，路径中的占位词必须替换；预期哈希应来自可信安装记录，而非为了让校验通过随意更改：

```powershell
$runtimeRoot = 'D:\YOUR_EXISTING_RUNTIME'
$installationRecord = 'D:\YOUR_EXISTING_INSTALLATION\installation-record.json'
$expectedRecordSha256 = 'REPLACE_WITH_TRUSTED_64_HEX_SHA256'
$sharedLockRoot = 'D:\YOUR_EXISTING_SHARED_LOCK_ROOT'
.\.venv\Scripts\python.exe runtime\run_skill.py --mode compute --runtime-root $runtimeRoot --installation-record $installationRecord --record-sha256 $expectedRecordSha256 --lock-root $sharedLockRoot --output ..\water-new-runtime
```

占位参数本身不能运行，也不代表你的安装已就绪；已有Runtime指南负责定位和核实安装。Docker Linux engine未运行时保存failure.json及诊断后停止，不改安全设置、不用旧输出兜底。保留实际共享锁，禁止随意换锁根绕过并发限制。

科学预算由原服务落实：1线程、1GiB、100秒软边界/120秒硬科学期限、最多100次SCF迭代及1次kernel，无重试。准入、启动、科学执行与清理分开，不保证整个宿主命令正好120秒结束；适配器不独立kill原生命周期监督进程。

## 保存及判断结果

结果写Skill外全新目录，已有目录拒绝。准备/复核模式保存Skill快照、输入、回执、SHA-256和results.zip；保存整个目录或ZIP即可。compute保留原启动器stdout/stderr与runtime-run内全部数值、资源和清理回执。发生异常时保留本次已取得输入和failure.json并非零退出，不覆盖原文件。

运行进程返回0时，本适配器仍标记RUNTIME_RETURNED_ZERO_REQUIRES_SCIENTIFIC_RECEIPT_REVIEW，不能直接当科学成功。需核对本次原Runtime执行/清理状态、数值门禁、数组以及未覆盖项。代码读取完整SKILL.md并记录哈希；全流程不调用语言模型，不把Skill读取称为模型理解。

本模块属于现有冻结水分子输入的独立分发适配器，合同skill-rhf-fixed-water-runtime-adapter-v1；不修改原核心、Runtime、安装登记、镜像或旧验收。
