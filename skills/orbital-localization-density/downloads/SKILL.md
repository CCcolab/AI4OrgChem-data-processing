---
name: orbital-localization-density
description: 为用户已有局域化程序准备输入与调用，复核实AO旋转、占据兼容、密度及固定矩阵能量，区分优化收敛与不变性。
---

# 轨道旋转、局域化与密度复核

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

下载指令的来源链接使用公开仓库明确地址；完整Python代码包内的来源文件位于`runtime/sources.json`。顶层维护源与下载导出字节一致。
