---
name: multistate-size-comparison
description: 为用户已有多态求解器组织协议、输入和调用，检查态集合、来源与资格；配套数值复核器仅组装显式非负归一化权重。
---

# 多态与体系尺寸比较复核

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

## 用户环境与后端选择

本 Skill 可独立下载阅读，配套 Python 不要求本项目 Runtime、安装登记、Docker 或固定磁盘路径。不自动安装/更新软件，不创建虚拟化环境，不索取模型密钥。先询问用户实际任务、已有程序/版本、输入和资源约束；优先复核已有结果；只有用户要求新计算并已选择可信程序时才执行。

1. 明确模型、体系/几何、单位、电子态、协议身份、来源与期望输出。缺必需信息则列出缺项，不能默补关键科学条件。
2. 核对用户已有后端是否实际支持该方法；不把某软件的泛用 SCF/优化器冒充专用条件态实现。不改变用户算子/占据/权重来迁就接口。
3. 生成适合用户现有环境的输入和调用；配套桥接器的 backend 模式只接受用户明确指定的可信 .py 和 execute=True。该 Python 与用户同权限运行，不是安全沙箱；不得把 CSV/JSON 文本当代码执行。准备模式不导入后端，不验证科学端点。
4. 先保存输入、Skill 快照、后端身份与资源协议；计算时保留原生日志、中间产物、实际收敛证据。后端返回 review_request（parameters/data/provenance）和 execution（至少 kind）；先保存返回，再执行明确范围的复核。
5. 严格区分准备、历史数组复核、人工数学演示、真实后端计算与模型解释。不使用语言模型也能执行这些显式程序；读取 Markdown 只记录指令文件身份，不是模型已理解/执行 Skill。
6. 写全新结果目录，禁止覆盖；数值检查失败或解释/适配失败仍保留已生成文件、失败原因与非零退出。无自动重试。不把失败产物视为合格端点。
7. 交付逐项检查、实际程序回执、文件及 SHA-256。不得从图形外观、文本解释、程序退出或旧 PASS 单独推断科学结论。

## 配套调用合同与依赖

portable-skill-backend-v1 是独立便携模板合同，不修改任何项目冻结合同。JSON 根对象恰为 parameters、data、provenance；provenance 含 kind、description。禁止重复键和非有限数。具体数学复核字段见本文件及 runtime/analysis.py；完整实例见 runtime/examples/*.json。用户可自行输出兼容 JSON，或编写调用已有 Python 库的适配器并返回相同结构。

prepare 仅 Python 3.10+ 标准库；四项数组/几何复核需要 NumPy，纯十进制账本仅标准库。requirements.txt 提供已验依赖版本。PySCF 仅可选模板需要，不能作为其它后端的强制依赖。模板不提供通用作业调度或硬资源隔离；线程参数、库内存建议和回调时间检查不等于操作系统硬限。用户有严格资源要求时使用自己已有的受控调度环境，不自动重试或放宽限制。

## 调用示例

完整 Python 模板在 runtime/run_skill.py；调用链是读取 SKILL.md → 显式请求/参数 → 用户选定适配器（可选）→ 数学复核 → 回执与文件。runtime/examples/01_prepare.py、02_review.py、03_user_backend.py 分别展示准备、复核、读取用户已有后端导出的结果；03 没有新量子计算。demo_backend.py 仅测试桥接合同，严禁当真实求解器。

```python
receipt = bridge.run_skill(
    mode="backend", request_file="my-request.json", output_dir="new-results",
    backend_file="my-trusted-backend.py", execute=True,
)
```

后端函数：run_backend(request, output_dir) 返回 {"review_request": {"parameters": ..., "data": ..., "provenance": ...}, "execution": {"kind": "明确的执行类型", ...}}。file_backend.py 是完整可运行的结果导入适配器；连接新求解器时，其物理算法、独立能量分项、端点资格和资源控制仍由真实后端及研究协议负责，不以本桥接器补造。

backend_calls 只统计桥接函数进入次数，不是科学核函数调用总数；Python 模块导入也可执行代码。后端原生任务次数与资源使用须由原生日志另外证明，不能将外部模块自报的 model_calls/network_calls 当作独立监测。桥接器本身不调用模型/网络，亦不执行后台超时强杀。

下载指令的来源链接使用公开仓库明确地址；完整Python代码包内的来源文件位于`runtime/sources.json`。顶层维护源与下载导出字节一致。
