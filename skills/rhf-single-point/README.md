# RHF输入准备与结果复核

为已有闭壳层RHF结果准备复核请求，复核已有实AO密度、电子数及能量账本，不执行新SCF。 正式入口提供准备、已有数据复核和结果JSON导入。输入准备不会运行科学求解器；数值复核仅证明输入通过所列检查。

[完整SKILL.md代码](SKILL.md?plain=1) · [下载完整指令](downloads/rhf-single-point-skill.zip) · [Python代码包](downloads/rhf-single-point-python.zip) · [源文件SHA-256](runtime/SHA256SUMS.txt)

## 知识点与科学边界

闭壳层限制性 Hartree–Fock 使用成对占据的空间轨道。实 AO 约定下 CᵀSC=I、D=C diag(n) Cᵀ，n 为 0/2；N=Tr(DS)，不能在非正交 AO 中改用 Tr(D)。

普通全电子 RHF 账本为 E=Tr(Dh)+½Tr(DVHF)+Enuc；F=h+VHF。程序还检查 DSD=2D 和 FDS−SDF 的残差。输入的 AO 顺序、核几何、单位、电荷、自旋和基组必须来自同一计算。数值一致、SCF 收敛不证明波函数稳定或物理基态，不提供相关能、UHF、DFT 或周期计算的通用认证。

本地复核器接受实 AO、正定 S（最小本征值>1e−10、条件数≤1e10）、各维≤128、正偶数电子和明确 0/2 占据。matrix_atol 与 energy_atol_hartree 均需显式给定（1e−14至1e−4）。案例01来自已保存水分子 RHF/6-31G(d) 数组，案例02为二 AO 人工工程数据，案例03故意破坏电子数以验证拒绝。历史数组重算不是新 SCF。

教材依据、推导及实现来源见 [完整 Skill](SKILL.md?plain=1) 与 [来源说明](runtime/sources.json)。经典教材用于理论背景，官方软件文档用于 API；不将 API 文档称为教材级物理证明。本轮只验收便携接口及数学复核，真实量子后端资格按独立记录判断。

## 依赖与首次操作

下载代码包并在有权限的短路径解压，例如Windows的 `C:/s/rhf-single-point`，进入该目录执行下列命令。使用自己的Python环境，不依赖本项目Runtime、Docker、安装登记或模型账号。

本次验证Python3.12.14。准备模式仅用标准库；数组复核及结果导入后的复核需要NumPy2.4.6。 仅缺依赖时由用户自行执行 `python -m pip install -r runtime/requirements.txt`；程序不安装软件、不联网、不切换环境。正式三个案例不需要PySCF或其它量子化学软件。

## 三个对应案例

| 程序 | 操作 | 输出 |
| --- | --- | --- |
| 01_prepare.py | 读取完整Skill和01.json，保存输入计划 | PREPARED_NOT_EXECUTED；不生成新数值 |
| 02_review.py | 复核01.json中的既有数组或人工账本 | COMPLETE_DEFINED_SCOPE及逐项检查 |
| 03_import_result.py | 将01.json作为已有结果文件读取并复核 | result_file_imports=1，backend_calls=0及原文件SHA-256 |

```powershell
python runtime/examples/01_prepare.py --output C:/s/out/rhf-single-point-prepare01
python runtime/examples/02_review.py --output C:/s/out/rhf-single-point-review01
python runtime/examples/03_import_result.py --output C:/s/out/rhf-single-point-import01
```

01.json与02.json是明确来源的两份复核输入；03.json是故意不合格反例，非零退出是预期。数据来源看各自provenance；保存的历史计算数组与人工示例均不代表本次进行了新实算。

## 修改参数与结果对应

先复制 `runtime/examples/02.json` 到包外（如 `C:/s/my-input.json`），在编辑器将 `parameters.matrix_atol` 改为 `2e-8` 后另存，再运行：

```powershell
python runtime/run_skill.py --mode review --input C:/s/my-input.json --output C:/s/out/rhf-single-point-changed01
```

该修改的对应结果：仍为二 AO 人工数据；重建能量 −1.3 Hartree，电子数2。只改变工程容差。

不要直接修改受哈希保护的包内程序/实例再自动重算清单掩盖变化。输入必须是 parameters、data、provenance 三部分；字段、数组与单位参照完整 SKILL.md、[复核源码](runtime/analysis.py) 和 [输入实例](runtime/examples/02.json)。参数容差不是物理误差条，放宽它不能修正错误方法。

## 使用用户已有结果

用户已有程序导出的JSON须符合本Skill的parameters/data/provenance字段、单位和数组顺序，详见[完整Skill](SKILL.md?plain=1)、[复核程序](runtime/analysis.py)及[实例](runtime/examples/02.json)。在包外建立导入请求，例如：

```json
{"parameters": {"result_file": "C:/s/my-exported-result.json"}, "data": {},
 "provenance": {"kind": "USER_RESULT", "description": "说明软件、方法、几何、单位与原生日志来源"}}
```

```powershell
python runtime/run_skill.py --mode import --input C:/s/import-request.json --output C:/s/out/rhf-single-point-user01
```

result_file须为绝对路径的常规JSON文件且不超过2MB；不把文件文字当代码执行。保存原文件字节与SHA-256后执行同样的数学复核。来源标签和converged只作为输入声明，不能独立认证其真实性。

## 完整调用模板

```python
from pathlib import Path
import importlib.util

page = Path("C:/s/rhf-single-point").resolve()
spec = importlib.util.spec_from_file_location("skill_review", page / "runtime/run_skill.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
receipt = bridge.run_skill(mode="review", request_file="C:/s/my-input.json", output_dir="C:/s/out/review-new")
```

程序实际读取并保存SKILL.md身份，再验证输入、复核及写结果。没有调用语言模型，不称模型已理解指令。正式入口不接受--backend或--execute。

## 结果保存与失败处理

写包外全新目录，禁止覆盖。准备模式另保存input-plan.json（复核输入计划，不是新计算软件输入）。保存request.json、SKILL.used.md、run-receipt.json；复核时另有review-request.json、result.json。导入时另存source-result.original.json和import-return.json。SHA256SUMS.txt、results.zip及其侧SHA用于保存和复核。

数值检查失败退出1；输入/解析等异常退出2。合法新目录已经创建时保存failure.json、实际回执和已有产物；参数解析、已有输出、危险或超限输入可在写入前拒绝。结果以程序回执、检查项和实际文件为准，不把失败结果或旧PASS当作新合格端点。输入准备只做结构及来源声明检查，不验收科学端点。

## 开发预览

需调用用户现有程序产生新计算结果时，先读[独立开发预览](runtime/development_preview/README.md)。任意Python适配器、原生请求及可选PySCF模板已从正式入口移至该目录；新真实后端完整实算没有完成验收。预览需用户明确选择，并不属于上述三个已验证的常规功能。没有自动安装或启动环境，不以目录重命名提升科学资格。
