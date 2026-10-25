---
name: rhf-single-point
description: 准备固定教学水分子的RHF/6-31G(d)输入、独立复核保存AO数组，或调用既有登记Runtime做一次真实单点计算，分开报告输入、旧数组复核、新SCF和科学资格。
---

# RHF单点：固定教学水分子与真实后端

先确认用户要准备输入、复核旧数组还是新计算。RHF仅适合已确认的闭壳层单行列式近似；偶数电子及单重态声明不是适用性的充分证明。不得把收敛当作波函数稳定性、物理基态或实验准确度认证。

## 当前实现边界

本模块只接收随包固定水分子XYZ和RHF/6-31G(d)、charge=0、multiplicity=1的登记请求，不开放任意分子、离子、开壳层、DFT、优化或条件态。固定水几何和profile与项目原冻结输入逐字节相同，适配器合同为skill-rhf-fixed-water-runtime-adapter-v1；不修改冻结核心、Runtime源、安装登记或镜像。

## 完整调用

1. 读取完整SKILL.md并核对资源SHA-256。prepare仅复制确定的request.json和molecule.xyz，状态PREPARED_NOT_EXECUTED；不得称已获得新能量。
2. review读取随包有来源的保存水分子AO数组，要求有限实矩阵、18AO、正确密度语义及可用正定度量。独立计算Tr(DS)、占据/密度重建、占据轨道CᵀSC、矩阵对称、F=hcore+veff及能量Tr(Dh)+0.5Tr(DVhf)+核项闭合。绝对门槛见源码，不默认使用相对容差。不逐元素比较轨道系数。
3. compute必须显式提供既有runtime_root、installation_record、其预期SHA-256及实际共享lock_root。核对登记服务/任务/模式、host文件和固定输入，不自动重新登记或建立镜像。检查Docker Linux engine，无法连接立即保留失败并停止，不能用旧结果回填。
4. 只调用原登记run-installed-runtime.py一次，使用它自己的生命周期、资源守卫和固定profile：1线程、1GiB、100秒软边界、120秒硬科学期限、最多100次SCF迭代/1次kernel，无重试。启动、准入及清理独立记录，不让外层任意kill遗弃容器，也不声称max_memory是独立硬配额。
5. 保留原启动器stdout/stderr、运行目录、清理与执行回执。原进程退出0仍只标RUNTIME_RETURNED_ZERO_REQUIRES_SCIENTIFIC_RECEIPT_REVIEW；必须读取本次Runtime数值门禁和数组后才判断科学范围，不能由程序返回0直接称验收通过。
6. 新输出目录必须在Skill外，已有目录拒绝。保存请求、Skill快照、输入/身份、结果或failure.json及能取得日志。成功准备/复核输出SHA-256和ZIP，失败不伪装成功包；本次已保存的后端记录不得清理或覆盖。

## 核心知识：从非正交AO到固定水分子RHF复核

AO基函数χμ的重叠为Sμν=∫χμχν dr；本实现仅取有限实数组、可用正定S和原始AO顺序。轨道φi=ΣμχμCμi满足CᵀSC=I。自旋求和占据ni为0/2时，D=C diag(n)Cᵀ，电子密度ρ(r)=ΣμνDμνχμ(r)χν(r)，所以积分电子数N=ΣμνDμνSνμ=Tr(DS)=Σini。Tr(D)只在相应正交表示中才可直接计数；例如S=diag(2,1)、C第一列=(1/√2,0)ᵀ、占据2时，Tr(D)=1而Tr(DS)=2。

固定RHF约定Vhf=J[D]−K[D]/2、F=h+Vhf，能量E=Tr(Dh)+½Tr(DVhf)+Enuc。相互作用按电子对计算，直接对每个电子的平均场求和会把同一对计两次，故有½；不能将它误用于任意标为veff的DFT势或不同密度约定。本复核只比较给定h/V与账本，不重新从双电子积分构造J/K。

RHF是α/β共享空间轨道的闭壳层单行列式近似；偶数电子、单重态及SCF收敛均不足以证明强相关体系适用性、波函数稳定性或真实基态。广义驻点式FC=SCε与正曲率稳定性是不同条件。①只复制固定请求；②保存水分子以10电子和约−76.0090991086 Eh核对七项恒等式；③仍需登记后端及本次科学回执。旧数组通过不变成新SCF，HOMO–LUMO差不直接是激发能。

解释或运行前应核对AO顺序、spin-summed约定、固定几何和方法、单位及来源；一项缺失不能由18×18形状补定。完整虚轨道残差、波函数稳定性、新SCF和实验准确性不在保存数组复核资格内。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Atomic Basis Functions、Orbital Rotations、Hartree-Fock Theory适合作为上述标准理论的教材入口。保留[PySCF SCF](https://pyscf.org/user/scf.html)及[密度/能量源码](https://pyscf.org/_modules/pyscf/scf/hf.html)作实现依据；教材不证明本次后端已运行。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](runtime/sources.json)。

## 解释范围与来源

保存数组复核不是新SCF；新SCF不是独立引擎认证；完整虚轨道资格、波函数稳定性与真实基态认证本模块未完成。AO密度不是实验密度，HOMO–LUMO差不是激发能。真实模型服务不需要也不调用。

- [PySCF SCF说明](https://pyscf.org/user/scf.html)：RHF/密度及方法实现语境。
- Runtime自身molecular-service profile、安装登记和来源清单决定真实能力与预算，不以通用Skill描述扩大服务。
- 保存水分子来源见runtime/saved-water/origin.json；它记录旧执行身份，不冒充本次新计算。
