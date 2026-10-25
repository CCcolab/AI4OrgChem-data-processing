# 闭壳层 RHF 单点

**真实后端待验 · PARTIAL_BACKEND_PENDING**：便携输入/用户后端/实AO复核可用；历史固定水结果保留，新便携PySCF任务未实算。 本页便携模板和本地复核不继承历史后端PASS。

此 Skill 的指令可独立用于用户自己的环境；不强制使用本项目 Runtime、Docker、安装登记或模型账号。顶层两个文件各有职责：本页介绍知识、输入/输出和操作，SKILL.md 提供完整任务指令；runtime 放调用程序、依赖与案例。

[查看完整 SKILL.md 代码](SKILL.md?plain=1) · [下载完整指令](downloads/rhf-single-point-skill.zip) · [Python代码包下载目录](downloads/) · [源文件SHA-256](runtime/SHA256SUMS.txt)

下载目录中选择 `rhf-single-point-python.zip`，下载后按同目录 SHA256SUMS.txt 核对压缩包。已经解压代码包的用户无需再次下载，直接执行下面步骤；包内源文件哈希见 runtime/SHA256SUMS.txt。

## 知识点与科学边界

闭壳层限制性 Hartree–Fock 使用成对占据的空间轨道。实 AO 约定下 CᵀSC=I、D=C diag(n) Cᵀ，n 为 0/2；N=Tr(DS)，不能在非正交 AO 中改用 Tr(D)。

普通全电子 RHF 账本为 E=Tr(Dh)+½Tr(DVHF)+Enuc；F=h+VHF。程序还检查 DSD=2D 和 FDS−SDF 的残差。输入的 AO 顺序、核几何、单位、电荷、自旋和基组必须来自同一计算。数值一致、SCF 收敛不证明波函数稳定或物理基态，不提供相关能、UHF、DFT 或周期计算的通用认证。

本地复核器接受实 AO、正定 S（最小本征值>1e−10、条件数≤1e10）、各维≤128、正偶数电子和明确 0/2 占据。matrix_atol 与 energy_atol_hartree 均需显式给定（1e−14至1e−4）。案例01来自已保存水分子 RHF/6-31G(d) 数组，案例02为二 AO 人工工程数据，案例03故意破坏电子数以验证拒绝。历史数组重算不是新 SCF。

教材依据、推导及实现来源见 [完整 Skill](SKILL.md?plain=1) 与 [来源说明](runtime/sources.json)。经典教材用于理论背景，官方软件文档用于 API；不将 API 文档称为教材级物理证明。本轮只验收便携接口及数学复核，真实量子后端资格按独立记录判断。

## 下载、依赖与首次操作

1. 下载 Python 代码包，在 Windows 解压到短路径（例如 `C:\s`），进入解出的 `rhf-single-point` 文件夹；其它系统同样先进入该目录。所有命令均从该目录运行。无需下载整个仓库。
2. 已有 Python 3.10+。`prepare` 只用标准库，不安装任何软件。数组复核需要 NumPy；纯 Decimal 账本不需要 NumPy。依赖清单给出本次已验版本，当前平台可用性另行确认。本文已在 Python 3.12.14/NumPy 2.4.6 下复验，未宣称覆盖所有 Python/操作系统。
3. 可以选择自己的现有虚拟环境；只有缺依赖且你要安装时才手动执行 `python -m pip install -r runtime/requirements.txt`。程序不会自动安装、联网或切换环境。安装后仍使用同一环境的 `python`。
4. 结果目录必须是包外全新路径。下面 `C:/s/out/...` 是 Windows 示例；其它系统换成自己的绝对短路径。保留上一次目录，下一次更换名称。

## 三个对应案例

| 程序 | 实际输入与行为 | 预期产物/状态 |
| --- | --- | --- |
| 01_prepare.py | 读取 01.json 和完整 Skill，不调用科学后端 | PREPARED_NOT_EXECUTED、输入快照、调用计划 |
| 02_review.py | 对 01.json 的已有数组/人工账本做本页限定的数值复核 | COMPLETE_DEFINED_SCOPE、逐项 result.json |
| 03_user_backend.py | 明确调用 file_backend.py 读取同一用户结果文件，记录文件哈希，再复核 | backend_calls=1、USER_SUPPLIED_RESULT_FILE_REVIEW；新量子调用0 |

```powershell
python runtime/examples/01_prepare.py --output C:/s/out/rhf-single-point-prep01
python runtime/examples/02_review.py --output C:/s/out/rhf-single-point-review01
python runtime/examples/03_user_backend.py --output C:/s/out/rhf-single-point-file01
```

`01.json`、`02.json` 是两个具体的复核输入，`03.json` 是故意不合格的反例（非零退出是预期）。每份 provenance 描述其人工/历史来源，不能把教学数据输出当作真实新计算。另有 `demo_backend.py` 演示桥接函数调用，只返回人工数据，execution.kind 明确标注 SYNTHETIC_ENGINEERING_DEMO。

## 修改参数与使用自己的结果

先复制 `runtime/examples/02.json` 到包外（如 `C:/s/my-input.json`），在编辑器将 `parameters.matrix_atol` 改为 `2e-8` 后另存，再运行：

```powershell
python runtime/run_skill.py --mode review --input C:/s/my-input.json --output C:/s/out/rhf-single-point-changed01
```

该修改的对应结果：仍为二 AO 人工数据；重建能量 −1.3 Hartree，电子数2。只改变工程容差。

不要直接修改受哈希保护的包内程序/实例再自动重算清单掩盖变化。输入必须是 parameters、data、provenance 三部分；字段、数组与单位参照完整 SKILL.md、[复核源码](runtime/analysis.py) 和 [输入实例](runtime/examples/02.json)。参数容差不是物理误差条，放宽它不能修正错误方法。

用户已有软件可导出同一结果 schema。在包外新建下面 JSON，将路径改成实际**绝对路径**（JSON 用 `/` 或 `\\`，不要写未转义的 `\`）：

```json
{"parameters": {"backend_result_file": "C:/s/my-exported-result.json"}, "data": {},
 "provenance": {"kind": "USER_RESULT", "description": "说明软件/方法/几何/单位及原生日志位置"}}
```

```powershell
python runtime/run_skill.py --mode backend --input C:/s/file-request.json --backend runtime/backends/file_backend.py --execute --output C:/s/out/rhf-single-point-user01
```

file_backend 仅导入文件，不会执行文件中的文本命令；需新计算时选择自己信任的 .py 适配器。调用用户程序是在当前 Python 进程、以当前用户权限执行，不能把它视作不可信代码沙箱。

`backend_calls` 是桥接函数进入次数；科学核函数调用次数、资源和外部行为还需原生日志核对。桥接器不独立监控任意外部 Python 程序的模型/网络调用，也不会将其声明当作已验证事实。

## 完整调用模板

完整程序在 [runtime/run_skill.py](runtime/run_skill.py)。下面代码可在包外保存；把 skill_dir 和输入输出路径替换为实际绝对路径：

```python
from pathlib import Path
import importlib.util
skill_dir = Path("C:/s/rhf-single-point")
skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("bridge", skill_dir / "runtime/run_skill.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
receipt = bridge.run_skill(
    mode="backend", request_file="C:/s/file-request.json",
    output_dir="C:/s/out/new-call01",
    backend_file=skill_dir / "runtime/backends/file_backend.py", execute=True,
)
print(receipt["status"])
```

实际调用链：读取并固定完整 SKILL.md → 显式参数与数据 → 用户选定后端（可选）→ 保存原始返回 → 科学范围内复核 → 回执、文件、哈希。无模型模式记录 Skill 身份，不宣称 Markdown 已由模型理解。

## 后端与资源选择

可选 `pyscf_backend.py` 调用已有 PySCF；它不是普通 Python 安装后就必然可用。PySCF [官方安装说明](https://pyscf.org/user/install.html)明确不原生支持 Windows。没有该环境时使用其它已有后端的结果文件即可，本项目不会替用户创建 Docker/WSL。

仅在已有受支持的 PySCF 环境、检查协议和预算并确定要新计算时使用下面命令。它会发起一次真实后端任务，本次本地验收没有执行：

```powershell
python runtime/run_skill.py --mode backend --input runtime/examples/native-request.json --backend runtime/backends/pyscf_backend.py --execute --output C:/s/out/native01
```

默认 RHF 为固定水分子全电子 RHF/6-31G(d)；局域化请求复用保存的水占据轨道，默认 Boys，修改 localization="pm" 选择明确的 meta_lowdin PM。两项都不是通用态/基组认证。本模板没有操作系统硬限，只提供线程设置、内存建议及回调软时间检查。真实 PySCF 数值运行标记为**本次未执行**。


## 结果保存与失败处理

结果目录包含 request.json、SKILL.used.md、run-receipt.json、result.json（已执行复核时）、SHA256SUMS.txt、results.zip 及其独立哈希。backend 模式另保存后端源码快照、原始返回、来源文件或原生中间产物。准备模式没有数值结果。

检查失败用 FAILED_NUMERICAL_CHECKS；异常用 FAILED_PARTIAL_OUTPUT_RETAINED，保留已经写出的产物、failure.json 与结果 ZIP。失败不等于合格端点。结果状态以实际回执及文件为准，外部来源声明仍需用户核对。成功输出也只证明所列检查。旧目录不会覆盖，无自动重试。

本地工程验收、历史结果复核、真实后端验收分开记录。可选 PySCF 模板本轮没有运行新量子任务；也没有调用模型、安装依赖或上传内部材料。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
