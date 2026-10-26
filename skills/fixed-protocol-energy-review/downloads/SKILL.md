---
name: fixed-protocol-energy-review
description: 按用户明确的固定协议核对已有普通态与条件态能量账本，不生成条件态算子或新量子能量。
---

# 固定协议能量账本复核

先确认用户目标、实际输入、方法、单位和来源。没有实际工具执行时标NOT_EXECUTED，不从既有文字、模型解释或历史PASS制造新数值。

## 输入与方法

parameters显式protocol_id、protocol_version、method_id、basis_id、geometry_id、atol_hartree。data含comparison_definition和ordinary/conditional两条states，每态含算子/占据定义、收敛及端点资格、带source_id的功能式项与另报总能量。具体完整schema见案例JSON，不可省略或靠标签补算。

逐项按声明的coefficient×value_hartree按skill-ledger-decimal-v2有界自适应精确上下文求和，与reported_total_hartree按显式绝对容差比较；同方法/基组/几何/协议身份必须匹配。只有两端声明可用且账本通过才报告conditional−ordinary，否则比较量为null。来源与资格标记仍须外部实证复核。

## 核心知识：显式能量协议、精确账本与物理资格

先给定protocol_id/version、method/basis、同一geometry身份，再逐态明确operator_definition、occupation_definition、功能式项、来源以及收敛/端点资格声明。相同方法/几何标签不足以证明普通态与条件态共享同一Hamiltonian；改变算子、占据限制或功能式通常定义了不同问题。这个模块接受的是用户明示的比较协议，不从教材推导新的通用条件态理论。

每态账本L=Σk ak Ek，与另报总量Ereported比较|L−Ereported|≤atol_hartree。来源标签和endpoint_qualified/converged只是输入声明，实际资格需真实输出支持；只有两端账本和声明均通过才给Lconditional−Lordinary。算术闭合检查能发现错项/符号/数值不一致，不能证明输入能量真实、分解唯一或两端物理可比。

采用skill-ledger-decimal-v2的有界自适应精确上下文，精度由输入十进制跨度和项数推导，不预先固定精度。字面量≤128字符、系数数字≤80位、指数−200至200，所需精度≤1024位；Inexact/Rounded等触发即失败。例如1e60+0.1−1e60的解析值为0.1，不能因有限精度相消变0而声称闭合。Decimal位数并不认证化学有效数字或测量不确定度。

①合成功能差0.2 Eh只是合同算术；②几何身份不同拒绝；③资格声明false保留账本但比较差null。固定条件功能差不自动是物理键能、激发能、自由能或实验可观测量。新普通/条件SCF及真正端点证据仍NOT_EXECUTED；经典HF变分理论只作标准基础，不能给任何新定义的条件量背书。

### 经典教材、实现来源及支持范围

[Q1：Helgaker、Jørgensen、Olsen，Molecular Electronic-Structure Theory，Wiley，2000，ISBN 9780471967552](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)的Orbital Rotations/Hartree-Fock Theory供普通态与变分概念学习；所选条件态的物理意义必须另有明确研究协议与证据，当前合成账本不能替代。保留[Decimal舍入与相消说明](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)作算术来源。

本模块所引Q1的作者、版次、年份和相关章节名称已对照出版社目录核验；未读取其全书正文，不声称已逐式或按页核验。上文推导由本模块明确给出，API文档仅支持实现接口。完整来源类型、访问范围和输入/保存数据身份见[runtime/sources.json](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/fixed-protocol-energy-review/runtime/sources.json)。

## 输入校验与方法依据补充

能量算术采用skill-ledger-decimal-v2：每个十进制输入文字≤128字符、系数≤80位、Decimal指数在−200至200；不接收布尔值、特殊值或带空白文字。这里“系数位数/指数”指Decimal数字元组，不是化学有效数字认证。总精度由所有输入跨度及项数上界推导，上限1024位；乘积求和、独立总量差及阈值比较在同一精确上下文进行。任何Inexact/Rounded或预算越界均失败，绝不把失去的小残差当作闭合。回执的arithmetic记录策略与实际精度，原atol不变。

[Python3.12 Decimal：舍入与相消](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)明确有限精度仍会舍入；本策略只保证所定义有界算术，不认证能量来源、方法、端点真实性或物理可比性。例如1e60+0.1−1e60必须报告0.1，不能据夸张数值声称化学合理。


## 科学适用性补充

普通态与条件态只有在具体协议明确了算子、占据、核几何、基组、方法和能量泛函后才可比较。“条件态”没有可由 Skill 自动推导的通用量子化学算子。

本地复核器要求一个 ordinary 和一个 conditional 端点，协议 ID/版本、方法/基组/几何身份一致。按显式带符号系数装配每态 1至32 项账本，再与独立报告的总能比较；只有两个端点的账本、收敛及资格声明通过后才给 conditional−ordinary。十进制精度受有界输入控制，单位为 Hartree。资格布尔值、source_id 和算术闭合并不认证外部证据的独立性。

差值不自动等于键能、激发能、相互作用能或实验观测；不同泛函不能仅靠改名变得兼容。三个随包账本都是人工教学数据，第三个故意把条件态资格声明设为 false。用户已有程序应提供真实独立分项、总能及资格依据，不能仅将总能反填为单一账本项并称完成独立验收。

## 正式交付与完整调用

正式功能是准备输入、复核给定数据、导入已有结果JSON。三种模式prepare、review、import均不运行外部求解器，不导入用户选择的.py代码。调用链为读取完整SKILL.md并保存身份 → 显式parameters/data/provenance → 输入检查 → 本文件限定数学复核 → 回执、文件与SHA-256。调用名`fixed-protocol-energy-review`保持不变。

```python
receipt = bridge.run_skill(mode="review", request_file="my-input.json", output_dir="new-results")
```

配套完整模板是runtime/run_skill.py；01_prepare.py、02_review.py和03_import_result.py对应准备、复核和文件导入。import请求的parameters恰含result_file（绝对常规JSON路径≤2MB），data为空，provenance明确来源。导入数据仍须符合上文科学schema，不自动转换算子、单位、态身份或数组顺序。

prepare只需Python标准库；本项Decimal账本复核也只用标准库。 当前正式程序不需要本项目Runtime、Docker、模型账号、PySCF或其它量子化学软件。包内数据不可原地修改后重写清单掩盖变化；复制用户输入到包外另行修改。完整命令与对应输出见README。

写新结果目录，保存输入、Skill、方法参数、逐项检查及实际产物；数值检查不合格退出1，输入/调用异常退出2并在已经建立的合法目录保留失败产物。参数解析或输出路径拒绝可以在建立目录前发生。不自动重试，不覆盖旧结果。来源声明或程序完成不能单独证明科学端点与物理解释成立。

## 真实计算对接：开发预览

只有用户明确选择开发预览时才讨论调用其已有求解程序。完整入口、信任边界、依赖与协议要求见[runtime/development_preview/README.md](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/skills/fixed-protocol-energy-review/runtime/development_preview/README.md)。这部分未完成新真实后端实算验收，不属于正式prepare/review/import的可用资格；不得把历史实算、人工数据、文件导入或本地程序检查当作新后端已通过。

预览不安装软件、不创建Docker/WSL或替用户选择环境。任意Python适配器与用户同权限运行，不是安全沙箱，不提供操作系统硬资源限额；需要真实原生日志、独立能量/导数记录、实际收敛与端点资格。缺少后端、协议或关键证据时仅准备或复核已有结果，不补造数值。
