---
name: fixed-protocol-energy-review
description: 按用户明确定义的协议调用已有普通态与条件态后端，复核算子、占据、独立能量分项及端点资格，不自动推导通用条件泛函。
---

# 固定协议普通态与条件态账本复核

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
