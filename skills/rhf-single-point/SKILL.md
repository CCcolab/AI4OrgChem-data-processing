---
name: rhf-single-point
description: 为已有闭壳层RHF结果准备复核请求，复核已有实AO密度、电子数及能量账本，不执行新SCF。
---

# RHF输入准备与结果复核

为已有闭壳层RHF结果准备复核请求，复核已有实AO密度、电子数及能量账本，不执行新SCF。 指令用于限定范围的准备与复核，不自动选择或执行外部科学程序。

## 专业定义与程序适用范围

闭壳层限制性 Hartree–Fock 使用成对占据的空间轨道。实 AO 约定下 CᵀSC=I、D=C diag(n) Cᵀ，n 为 0/2；N=Tr(DS)，不能在非正交 AO 中改用 Tr(D)。

普通全电子 RHF 账本为 E=Tr(Dh)+½Tr(DVHF)+Enuc；F=h+VHF。程序还检查 DSD=2D 和 FDS−SDF 的残差。输入的 AO 顺序、核几何、单位、电荷、自旋和基组必须来自同一计算。数值一致、SCF 收敛不证明波函数稳定或物理基态，不提供相关能、UHF、DFT 或周期计算的通用认证。

本地复核器接受实 AO、正定 S（最小本征值>1e−10、条件数≤1e10）、各维≤128、正偶数电子和明确 0/2 占据。matrix_atol 与 energy_atol_hartree 均需显式给定（1e−14至1e−4）。案例01来自已保存水分子 RHF/6-31G(d) 数组，案例02为二 AO 人工工程数据，案例03故意破坏电子数以验证拒绝。历史数组重算不是新 SCF。

复核参数恰为 method=RHF、basis、geometry_id、ao_order、electron_count、density_semantics=SPIN_SUMMED_REAL_AO_RHF、matrix_atol、energy_atol_hartree。data 恰为 overlap、coefficients、occupations、density、hcore、veff、fock、nuclear_hartree、reported_total_hartree、scf_converged。能量单位 Hartree，维数/原始数值逐项检查；布尔值不得冒充数值。任何不合格检查均非零退出，但保存所有可用产物。

## 理论与实现来源

[Helgaker、Jørgensen、Olsen：Molecular Electronic-Structure Theory（Wiley，2000）](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)提供 HF、轨道与密度理论背景。书目信息/目录核验不等于已通读全书或逐页认证本实现。[PySCF SCF 官方指南](https://pyscf.org/user/scf.html)支持可选 API 使用，不代替教材或物理基态资格。明确推导和实际数值检查分别呈现，来源细节见 runtime/sources.json。

## 正式交付与完整调用

正式功能是准备输入、复核给定数据、导入已有结果JSON。三种模式prepare、review、import均不运行外部求解器，不导入用户选择的.py代码。调用链为读取完整SKILL.md并保存身份 → 显式parameters/data/provenance → 输入检查 → 本文件限定数学复核 → 回执、文件与SHA-256。调用名`rhf-single-point`保持不变。

```python
receipt = bridge.run_skill(mode="review", request_file="my-input.json", output_dir="new-results")
```

配套完整模板是runtime/run_skill.py；01_prepare.py、02_review.py和03_import_result.py对应准备、复核和文件导入。import请求的parameters恰含result_file（绝对常规JSON路径≤2MB），data为空，provenance明确来源。导入数据仍须符合上文科学schema，不自动转换算子、单位、态身份或数组顺序。

prepare只需Python标准库；本项数组复核需要NumPy，已验版本见runtime/requirements.txt。 当前正式程序不需要本项目Runtime、Docker、模型账号、PySCF或其它量子化学软件。包内数据不可原地修改后重写清单掩盖变化；复制用户输入到包外另行修改。完整命令与对应输出见README。

写新结果目录，保存输入、Skill、方法参数、逐项检查及实际产物；数值检查不合格退出1，输入/调用异常退出2并在已经建立的合法目录保留失败产物。参数解析或输出路径拒绝可以在建立目录前发生。不自动重试，不覆盖旧结果。来源声明或程序完成不能单独证明科学端点与物理解释成立。

## 真实计算对接：开发预览

只有用户明确选择开发预览时才讨论调用其已有求解程序。完整入口、信任边界、依赖与协议要求见[runtime/development_preview/README.md](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/rhf-single-point/runtime/development_preview/README.md)。这部分未完成新真实后端实算验收，不属于正式prepare/review/import的可用资格；不得把历史实算、人工数据、文件导入或本地程序检查当作新后端已通过。

预览不安装软件、不创建Docker/WSL或替用户选择环境。任意Python适配器与用户同权限运行，不是安全沙箱，不提供操作系统硬资源限额；需要真实原生日志、独立能量/导数记录、实际收敛与端点资格。缺少后端、协议或关键证据时仅准备或复核已有结果，不补造数值。
