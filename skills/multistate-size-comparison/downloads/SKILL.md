---
name: multistate-size-comparison
description: 核对已有态集合完整性、来源与固定非负归一化权重，不运行多态优化或推断统计权重。
---

# 态集合与固定权重复核

先确认用户目标、实际输入、方法、单位和来源。没有实际工具执行时标NOT_EXECUTED，不从既有文字、模型解释或历史PASS制造新数值。

## 输入与方法

parameters含protocol_id、method_id、basis_id、weight_atol、expected_states（每size对应态ID列表）及comparison_definition。data.states逐项给size、id、energy_hartree、weight、eligible、source_id、state_definition和相同方法/基组/协议身份；最多128条。

先要求实际(size,id)与声明全集严格一致，不接受缺态、重复或新增未声明态。每size的显式非负权重和须为1；分开报告固定加权能量与端点资格。权重是输入，不从能量猜Boltzmann人口，不偷偷归一化不合格权重。

## 核心知识：声明态全集、固定权重与尺寸比较

先声明每个size所需state ID全集，再要求实际(size,id)集合逐项相等；重复、缺失或未声明项均拒绝，不能仅因已提供若干低能态就称态集合完备。各条需显式非负权重、有限能量、相同protocol/method/basis身份、state_definition、source_id和资格声明；这些标签不鉴定数据真实性，也不证明全部物理态已枚举。

对每个size计算权重和W=Σiwi并检查|W−1|≤weight_atol，再报告候选量Ufixed=ΣiwiEi。代码不将不合格W偷偷归一化，也不调用numpy.average来除W；即使候选算术有值，端点资格或权重门禁失败仍不是合格比较。给定权重的线性和是显式合同，改变输入权重就改变问题，不能由能量表反推出正确人口。在精确非负且W=1时，这也是标量能量的凸组合，故min(Ei)≤Ufixed≤max(Ei)；容差允许的W偏差意味着只能近似应用该界限，当前程序未另做物理人口推断。

只有另有物理系综与概率定义时，能量平均才可解释为相应系综平均。例如正则系综人口需温度、简并度和配分函数；自由能还含熵/配分函数定义，通常不等于Ufixed。本模块不推Boltzmann权重、不计算自由能，也不把不同组成/尺寸的原始总能量相减来排名。跨尺寸比较应先给共同参考、守恒/组成及明确物理量，当前接口不自动补齐。

①完整合成small/large分别得0.75/0.95 Eh，各自独立报告；②缺态拒绝部分平均；③资格不明端点仍保存候选算术并令检查失败。新多态优化、态跟踪、量子谱完备性和真实系综证据未执行。此教学工具是集合/来源合同与固定权重账本，不是多态量子引擎。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Exact and Approximate Wave Functions、Multiconfigurational Self-Consistent Field Theory提供电子态背景，仅核验目录；不把它当作本固定权重合同或统计力学人口的证明。[O1：Boyd、Vandenberghe，Convex Optimization，Cambridge University Press，2004，§2.1.4](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)的作者授权正文已核读，支持非负归一权重的凸组合解释，不支持任意权重的物理人口意义。[NumPy average](https://numpy.org/doc/stable/reference/generated/numpy.average.html)是通用归一化算术API，不能替代系综理论。若未来加入物理人口/自由能功能，应另给并验证相应统计力学教材与协议。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/multistate-size-comparison/runtime/sources.json)。


## 科学适用性补充

比较多电子态或多尺寸体系前，先定义每个体系的组成、态身份、共同参考、所用方法/基组、预期态集合和权重含义。不同组成的总能不能未经反应式、计量系数与参考约定直接相减解释物性。

本地复核器逐尺寸核对显式期望态集合，无缺失、重复或多余；只做非负、显式固定且各尺寸和为1的权重求和 ΣwᵢEᵢ。它不是有符号反应能/LDE 组装器，不自动生成 Boltzmann 布居、激发谱或自由能。不自动重归一化用户权重，也不凭浮点算术证明状态正交、电子态连续性或后端端点资格。

要求 1至16 个尺寸标签、总计1至128项态记录，明确 energy_hartree、weight、eligible、来源与态定义；协议/方法/基组身份须匹配。合成例01是完整集合；例02缺失 large/b；例03将 small/a 资格设为 false，后两例均应拒绝。真实新计算应由用户已有各态求解器按协议生成，失败/待验态不得填零或以旧 PASS 顶替。

## 配套程序已验证运行环境

正式prepare/review/import及结果保存已在Windows 11、Python 3.12.14、CPU环境运行成功。数组复核使用NumPy 2.4.6，prepare仅用标准库。 三个正式案例、参数修改、预期错误与输出保护共8/8项本地检查通过，GitHub下载复验同为8/8项符合预期。完整依赖与操作见README。

该结论只对应所列正式功能和已测环境，不把输入准备说成外部实算，也不自动推广到其它软件版本或开发预览。

## 正式交付与完整调用

正式功能是准备输入、复核给定数据、导入已有结果JSON。三种模式prepare、review、import均不运行外部求解器，不导入用户选择的.py代码。调用链为读取完整SKILL.md并保存身份 → 显式parameters/data/provenance → 输入检查 → 本文件限定数学复核 → 回执、文件与SHA-256。调用名`multistate-size-comparison`保持不变。

```python
receipt = bridge.run_skill(mode="review", request_file="my-input.json", output_dir="new-results")
```

配套完整模板是runtime/run_skill.py；01_prepare.py、02_review.py和03_import_result.py对应准备、复核和文件导入。import请求的parameters恰含result_file（绝对常规JSON路径≤2MB），data为空，provenance明确来源。导入数据仍须符合上文科学schema，不自动转换算子、单位、态身份或数组顺序。

prepare只需Python标准库；本项数组复核需要NumPy，已验版本见runtime/requirements.txt。 当前正式程序不需要本项目Runtime、Docker、模型账号、PySCF或其它量子化学软件。包内数据不可原地修改后重写清单掩盖变化；复制用户输入到包外另行修改。完整命令与对应输出见README。

写新结果目录，保存输入、Skill、方法参数、逐项检查及实际产物；数值检查不合格退出1，输入/调用异常退出2并在已经建立的合法目录保留失败产物。参数解析或输出路径拒绝可以在建立目录前发生。不自动重试，不覆盖旧结果。来源声明或程序完成不能单独证明科学端点与物理解释成立。

## 真实计算对接：开发预览

只有用户明确选择开发预览时才讨论调用其已有求解程序。完整入口、信任边界、依赖与协议要求见[runtime/development_preview/README.md](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/multistate-size-comparison/runtime/development_preview/README.md)。这部分未完成新真实后端实算验收，不属于正式prepare/review/import的可用资格；不得把历史实算、人工数据、文件导入或本地程序检查当作新后端已通过。

预览不安装软件、不创建Docker/WSL或替用户选择环境。任意Python适配器与用户同权限运行，不是安全沙箱，不提供操作系统硬资源限额；需要真实原生日志、独立能量/导数记录、实际收敛与端点资格。缺少后端、协议或关键证据时仅准备或复核已有结果，不补造数值。
