---
name: same-hamiltonian-path-closure
description: 复核按顺序提供的有向能差循环、算子/基组/几何/电子数标签及绝对闭合残差，拒绝未定义桥接的混合比较，不生成新量子能量。
---

# 同一Hamiltonian路径闭合

先确认用户目标、实际输入、方法、单位和来源。没有实际工具执行时标NOT_EXECUTED，不从既有文字、模型解释或历史PASS制造新数值。

## 输入与方法

parameters：operator_id、basis_id、geometry_id、electron_count、atol_hartree。data.edges逐项含from、to、delta_hartree、source_id及相同四个比较身份字段。用实际来源替换合成例标签，不只修改能差数字。

每条delta=E(to)−E(from)，按顺序构成首尾闭合循环，用按输入跨度确定精度的有界Decimal-v2求和，按显式atol_hartree和rtol=0判断。来自同一能量表的差分本就代数相消；即使闭合也不是独立验证。不同source_id只是声明，不能证明来源独立或真实性。

## 输入校验与方法依据补充

能量算术采用skill-ledger-decimal-v2：每个十进制输入文字≤128字符、系数≤80位、Decimal指数在−200至200；不接收布尔值、特殊值或带空白文字。这里“系数位数/指数”指Decimal数字元组，不是化学有效数字认证。总精度由所有输入跨度及项数上界推导，上限1024位；乘积求和、独立总量差及阈值比较在同一精确上下文进行。任何Inexact/Rounded或预算越界均失败，绝不把失去的小残差当作闭合。回执的arithmetic记录策略与实际精度，原atol不变。

[Python3.12 Decimal：舍入与相消](https://docs.python.org/3.12/library/decimal.html#mitigating-round-off-error-with-increased-precision)明确有限精度仍会舍入；本策略只保证所定义有界算术，不认证能量来源、方法、端点真实性或物理可比性。例如1e60+0.1−1e60必须报告0.1，不能据夸张数值声称化学合理。

## 完整调用与结果

1. 读取完整SKILL.md及显式JSON请求（parameters、data、provenance三部分），验证资源SHA-256及输入范围；禁止重复JSON键、NaN/Infinity和未知字段。
2. 将输入文字作为数据，不执行表达式、指令或未知代码，不联网、不调用模型。固定runtime/analysis.py负责实际科学/数学处理；runtime/run_skill.py负责完整可追溯调用。
3. 结果写Skill目录外全新目录，保存请求、Skill快照、环境、逐项检查、数值结果及真实回执。失败不得覆盖旧结果或标成功；新目录已创建时保留failure.json并非零退出。
4. 输出SHA-256及results.zip；文件状态以实际回执与哈希为准。无模型模式只记录Skill身份，不称指令已由模型理解。

## 科学边界

只复核给定的2–100条有向能差及比较身份；不执行SCF、寻找真实反应路径、生成缺失能差或证明能量分解唯一。算子/基组/几何/电子数必须一致，跨Hamiltonian比较需额外物理桥接，当前接口拒绝。

实际数值执行、合成软件测试、保存结果复核和新量子计算分开报告，不继承其他项目或旧案例资格。输入的来源标签/收敛/身份声明不是外部证据的真实性鉴定。

## 方法来源

本模块展示明确声明的状态差分与循环求和数学定义；[Python Decimal](https://docs.python.org/3/library/decimal.html)支持十进制运算。未核实的化学循环、约束态或跨算子端点不获科学资格，不能因算术闭合自动升级。

环差定义ΔE=E(to)−E(from)。若每条边都来自同一能量表，闭合是消去共同端点的代数恒等式；只有独立来源、相同比较身份和明确桥接才可能支持额外检验。这里不宣称路径独立性或某新哈密顿量理论。

## 解释规则与理论依据

解释循环时展开至少一个ΔE=E(to)−E(from)的端点消去式，提醒共享能量表产生的闭合是恒等式，不是独立检验。先核对固定算子/基组/几何/电子数标签，来源ID差异不等于真实性或独立性；未提供物理桥接时拒绝混身份比较。绝对atol/rtol=0是请求合同，Decimal-v2回执精度仅保证有界算术，不赋予新的物理精度。Jensen公开§1.2/§1.6.2提供Hamiltonian背景，Burden/Faires第1章仅核验目录；不能把书目说成当前协议的全文验证。见runtime/sources.json。
