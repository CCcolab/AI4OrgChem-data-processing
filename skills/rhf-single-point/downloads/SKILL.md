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

## 解释范围与来源

保存数组复核不是新SCF；新SCF不是独立引擎认证；完整虚轨道资格、波函数稳定性与真实基态认证本模块未完成。AO密度不是实验密度，HOMO–LUMO差不是激发能。真实模型服务不需要也不调用。

- [PySCF SCF说明](https://pyscf.org/user/scf.html)：RHF/密度及方法实现语境。
- Runtime自身molecular-service profile、安装登记和来源清单决定真实能力与预算，不以通用Skill描述扩大服务。
- 保存水分子来源见runtime/saved-water/origin.json；它记录旧执行身份，不冒充本次新计算。
