---
name: rhf-single-point
description: 为用户已有量子化学后端准备闭壳层RHF单点输入并复核真实结果，检查实AO密度、电子数和能量账本，区分收敛与稳定性。
---

# 闭壳层 RHF 单点

为实际用户的问题准备完整、可复现、可审计的闭壳层 RHF 输入、调用与结果复核。按用户已有软件生成代码或输入，缺软件时只准备文件，不擅自安装或启动其它环境。

## 专业定义与程序适用范围

闭壳层限制性 Hartree–Fock 使用成对占据的空间轨道。实 AO 约定下 CᵀSC=I、D=C diag(n) Cᵀ，n 为 0/2；N=Tr(DS)，不能在非正交 AO 中改用 Tr(D)。

普通全电子 RHF 账本为 E=Tr(Dh)+½Tr(DVHF)+Enuc；F=h+VHF。程序还检查 DSD=2D 和 FDS−SDF 的残差。输入的 AO 顺序、核几何、单位、电荷、自旋和基组必须来自同一计算。数值一致、SCF 收敛不证明波函数稳定或物理基态，不提供相关能、UHF、DFT 或周期计算的通用认证。

本地复核器接受实 AO、正定 S（最小本征值>1e−10、条件数≤1e10）、各维≤128、正偶数电子和明确 0/2 占据。matrix_atol 与 energy_atol_hartree 均需显式给定（1e−14至1e−4）。案例01来自已保存水分子 RHF/6-31G(d) 数组，案例02为二 AO 人工工程数据，案例03故意破坏电子数以验证拒绝。历史数组重算不是新 SCF。

复核参数恰为 method=RHF、basis、geometry_id、ao_order、electron_count、density_semantics=SPIN_SUMMED_REAL_AO_RHF、matrix_atol、energy_atol_hartree。data 恰为 overlap、coefficients、occupations、density、hcore、veff、fock、nuclear_hartree、reported_total_hartree、scf_converged。能量单位 Hartree，维数/原始数值逐项检查；布尔值不得冒充数值。任何不合格检查均非零退出，但保存所有可用产物。

## 理论与实现来源

[Helgaker、Jørgensen、Olsen：Molecular Electronic-Structure Theory（Wiley，2000）](https://www.wiley-vch.de/en/areas-interest/natural-sciences/molecular-electronic-structure-theory-978-0-471-96755-2)提供 HF、轨道与密度理论背景。书目信息/目录核验不等于已通读全书或逐页认证本实现。[PySCF SCF 官方指南](https://pyscf.org/user/scf.html)支持可选 API 使用，不代替教材或物理基态资格。明确推导和实际数值检查分别呈现，来源细节见 runtime/sources.json。

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

## 可选现有 PySCF 后端

runtime/backends/pyscf_backend.py 为实际库调用模板，使用 native-request.json。RHF 只执行一次 kernel；局域化使用已有占据轨道，单次 Boys 或 PM，不再执行 SCF。需要保存原生日志、数组、迭代回调与端点梯度，缺回调字段则失败，不伪造收敛。

PySCF 官方不原生支持 Windows；本模板只供已有受支持 Python/PySCF 环境的用户选择。Windows 用户可导入其其它现有软件的结果，不必创建 Docker/WSL。该可选模板本次只做语法、前置校验和缺依赖路径验证，真实新 PySCF 任务未执行。
