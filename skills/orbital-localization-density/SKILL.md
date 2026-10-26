---
name: orbital-localization-density
description: 复核给定轨道旋转、等占据空间的密度与电子数，不运行Boys或PM优化器。
---

# 轨道旋转与密度复核

先确认用户目标、实际输入、方法、单位和来源。没有实际工具执行时标NOT_EXECUTED，不从既有文字、模型解释或历史PASS制造新数值。

## 输入与方法

parameters为atol、density_semantics=SPIN_SUMMED_REAL_AO_RHF；data必需overlap、coefficients、occupations、rotation。可选hcore、veff、nuclear_hartree必须成组提供；不默补能量。实数组每维≤128，S正定且条件数≤1e10，占据仅0/2。

C′=CU，D=C diag(n) Cᵀ；核对CᵀSC=I、UᵀU=I、U diag(n) Uᵀ=diag(n)、相对密度差及Tr(DS)。只有等占据混合才保持密度；占据/虚空间互混不获不变性。能量对照只在固定hcore/veff下计算，不代表新自洽端点。

## 核心知识：等占据旋转为何保持密度

前提为同一有限实AO顺序、正定S、S正交轨道列C与实正交旋转U。本模块只接受所声明容差内的RHF占据0/2，不处理复轨道、分数占据或自旋分块的一般情形。令n=diag(occupations)，C′=CU，则D′−D=C(UnUᵀ−n)Cᵀ。因为C满列秩，密度保持当且仅当UnUᵀ=n；这要求U保留等占据子空间。

两条占据同为2时任意正交混合有U(2I)Uᵀ=2I；占据2与0的二轨道若各混合45°，原n=diag(2,0)变成含非零交叉项的UnUᵀ，密度通常改变。N=Tr(DS)与轨道系数逐元素是否相同无关。占据空间旋转可改变单轨道外观而保持同一密度；不能据外观自动命名σ/π、孤对或成键轨道。

固定h与Vhf时E=Tr(Dh)+½Tr(DVhf)+Enuc，因此D相同会使此账本相同；本程序不重建Vhf[D]、不求新SCF或稳定性。Boys最小化轨道空间展宽，Pipek–Mezey使用原子人口相关目标，选择目标并实际优化后才能称执行了相应局域化；任意U检查通过不满足这一步。

①保存水的占据内旋转只重算旧数组；②非单位度量的两条等占据轨道旋转保持D，但缺能量矩阵便将能量检查记未执行；③占据/虚空间混合应失败。读结果须同时看CᵀSC、UᵀU、占据兼容、相对密度误差与Tr(DS)，不能只看程序退出或固定能量差。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Orbital Rotations、Hartree-Fock Theory对应旋转与密度理论。具体局域化目标另见[PySCF局域轨道](https://pyscf.org/user/lo.html)，软件说明与经典教材分开标识。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/orbital-localization-density/runtime/sources.json)。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。


## 科学适用性补充

同一有限实 AO 度量下 C′=CU，D′−D=C[U diag(n)Uᵀ−diag(n)]Cᵀ。等占据子空间内的正交旋转保持密度与 Tr(DS)；占据/虚轨道互混通常不保持密度。局域轨道逐元素不同不代表波函数改变。

Boys 目标与轨道空间展宽有关；Pipek–Mezey 目标依赖所选原子人口定义，两者不能由任意旋转代替。密度不变、优化器收敛与化学轨道命名是三件事。局域极值不证明全局最佳，也不自动给出 σ/π 或孤对分类。可选 PySCF 模板分别保存迭代目标、梯度和最终端点梯度；PM 固定明确的 meta_lowdin 人口方法。

本地复核器只接受实 AO、0/2 占据、S 正定且条件数≤1e10、各维≤128。输入为 overlap、coefficients、occupations、rotation；atol 与 density_semantics 显式给定。可选 hcore、veff、nuclear_hartree 必须成组提供，所得能量仅比较固定矩阵，不是新 SCF。案例01复核保存的水轨道旋转，02为非单位度量人工数据，03为应失败的占据/虚空间混合。

## 配套程序已验证运行环境

正式prepare/review/import及结果保存已在Windows 11、Python 3.12.14、CPU环境运行成功。数组复核使用NumPy 2.4.6，prepare仅用标准库。 三个正式案例、参数修改、预期错误与输出保护共8/8项本地检查通过，GitHub下载复验同为8/8项符合预期。完整依赖与操作见README。

该结论只对应所列正式功能和已测环境，不把输入准备说成外部实算，也不自动推广到其它软件版本或开发预览。

## 正式交付与完整调用

正式功能是准备输入、复核给定数据、导入已有结果JSON。三种模式prepare、review、import均不运行外部求解器，不导入用户选择的.py代码。调用链为读取完整SKILL.md并保存身份 → 显式parameters/data/provenance → 输入检查 → 本文件限定数学复核 → 回执、文件与SHA-256。调用名`orbital-localization-density`保持不变。

```python
receipt = bridge.run_skill(mode="review", request_file="my-input.json", output_dir="new-results")
```

配套完整模板是runtime/run_skill.py；01_prepare.py、02_review.py和03_import_result.py对应准备、复核和文件导入。import请求的parameters恰含result_file（绝对常规JSON路径≤2MB），data为空，provenance明确来源。导入数据仍须符合上文科学schema，不自动转换算子、单位、态身份或数组顺序。

prepare只需Python标准库；本项数组复核需要NumPy，已验版本见runtime/requirements.txt。 当前正式程序不需要本项目Runtime、Docker、模型账号、PySCF或其它量子化学软件。包内数据不可原地修改后重写清单掩盖变化；复制用户输入到包外另行修改。完整命令与对应输出见README。

写新结果目录，保存输入、Skill、方法参数、逐项检查及实际产物；数值检查不合格退出1，输入/调用异常退出2并在已经建立的合法目录保留失败产物。参数解析或输出路径拒绝可以在建立目录前发生。不自动重试，不覆盖旧结果。来源声明或程序完成不能单独证明科学端点与物理解释成立。

## 真实计算对接：开发预览

只有用户明确选择开发预览时才讨论调用其已有求解程序。完整入口、信任边界、依赖与协议要求见[runtime/development_preview/README.md](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/orbital-localization-density/runtime/development_preview/README.md)。这部分未完成新真实后端实算验收，不属于正式prepare/review/import的可用资格；不得把历史实算、人工数据、文件导入或本地程序检查当作新后端已通过。

预览不安装软件、不创建Docker/WSL或替用户选择环境。任意Python适配器与用户同权限运行，不是安全沙箱，不提供操作系统硬资源限额；需要真实原生日志、独立能量/导数记录、实际收敛与端点资格。缺少后端、协议或关键证据时仅准备或复核已有结果，不补造数值。
