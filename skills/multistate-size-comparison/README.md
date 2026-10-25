# 多态与尺寸比较

**真实后端待验 · PARTIAL_BACKEND_PENDING**：用户态集合接口与固定非负归一化权重复核可用；真实多态集合与专用有符号公式仍待验。 本页便携模板和本地复核不继承历史后端PASS。

此 Skill 的指令可独立用于用户自己的环境；不强制使用本项目 Runtime、Docker、安装登记或模型账号。顶层两个文件各有职责：本页介绍知识、输入/输出和操作，SKILL.md 提供完整任务指令；runtime 放调用程序、依赖与案例。

[查看完整 SKILL.md 代码](SKILL.md?plain=1) · [下载完整指令](downloads/multistate-size-comparison-skill.zip) · [Python代码包下载目录](downloads/) · [源文件SHA-256](runtime/SHA256SUMS.txt)

下载目录中选择 `multistate-size-comparison-python.zip`，下载后按同目录 SHA256SUMS.txt 核对压缩包。已经解压代码包的用户无需再次下载，直接执行下面步骤；包内源文件哈希见 runtime/SHA256SUMS.txt。

## 知识点与科学边界

比较多电子态或多尺寸体系前，先定义每个体系的组成、态身份、共同参考、所用方法/基组、预期态集合和权重含义。不同组成的总能不能未经反应式、计量系数与参考约定直接相减解释物性。

本地复核器逐尺寸核对显式期望态集合，无缺失、重复或多余；只做非负、显式固定且各尺寸和为1的权重求和 ΣwᵢEᵢ。它不是有符号反应能/LDE 组装器，不自动生成 Boltzmann 布居、激发谱或自由能。不自动重归一化用户权重，也不凭浮点算术证明状态正交、电子态连续性或后端端点资格。

要求 1至16 个尺寸标签、总计1至128项态记录，明确 energy_hartree、weight、eligible、来源与态定义；协议/方法/基组身份须匹配。合成例01是完整集合；例02缺失 large/b；例03将 small/a 资格设为 false，后两例均应拒绝。真实新计算应由用户已有各态求解器按协议生成，失败/待验态不得填零或以旧 PASS 顶替。

教材依据、推导及实现来源见 [完整 Skill](SKILL.md?plain=1) 与 [来源说明](runtime/sources.json)。经典教材用于理论背景，官方软件文档用于 API；不将 API 文档称为教材级物理证明。本轮只验收便携接口及数学复核，真实量子后端资格按独立记录判断。

## 下载、依赖与首次操作

1. 下载 Python 代码包，在 Windows 解压到短路径（例如 `C:\s`），进入解出的 `multistate-size-comparison` 文件夹；其它系统同样先进入该目录。所有命令均从该目录运行。无需下载整个私有仓库。
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
python runtime/examples/01_prepare.py --output C:/s/out/multistate-size-comparison-prep01
python runtime/examples/02_review.py --output C:/s/out/multistate-size-comparison-review01
python runtime/examples/03_user_backend.py --output C:/s/out/multistate-size-comparison-file01
```

`01.json`、`02.json` 是两个具体的复核输入，`03.json` 是故意不合格的反例（非零退出是预期）。每份 provenance 描述其人工/历史来源，不能把教学数据输出当作真实新计算。另有 `demo_backend.py` 演示桥接函数调用，只返回人工数据，execution.kind 明确标注 SYNTHETIC_ENGINEERING_DEMO。

## 修改参数与使用自己的结果

先复制 `runtime/examples/01.json` 到包外（如 `C:/s/my-input.json`），在编辑器将 `parameters.weight_atol` 改为 `2e-10` 后另存，再运行：

```powershell
python runtime/run_skill.py --mode review --input C:/s/my-input.json --output C:/s/out/multistate-size-comparison-changed01
```

该修改的对应结果：完整人工态集合仍通过；也可将同一尺寸两态权重一并改为0.5/0.5，不能仅改单态破坏归一化。

不要直接修改受哈希保护的包内程序/实例再自动重算清单掩盖变化。输入必须是 parameters、data、provenance 三部分；字段、数组与单位参照完整 SKILL.md、[复核源码](runtime/analysis.py) 和 [输入实例](runtime/examples/01.json)。参数容差不是物理误差条，放宽它不能修正错误方法。

用户已有软件可导出同一结果 schema。在包外新建下面 JSON，将路径改成实际**绝对路径**（JSON 用 `/` 或 `\\`，不要写未转义的 `\`）：

```json
{"parameters": {"backend_result_file": "C:/s/my-exported-result.json"}, "data": {},
 "provenance": {"kind": "USER_RESULT", "description": "说明软件/方法/几何/单位及原生日志位置"}}
```

```powershell
python runtime/run_skill.py --mode backend --input C:/s/file-request.json --backend runtime/backends/file_backend.py --execute --output C:/s/out/multistate-size-comparison-user01
```

file_backend 仅导入文件，不会执行文件中的文本命令；需新计算时选择自己信任的 .py 适配器。调用用户程序是在当前 Python 进程、以当前用户权限执行，不能把它视作不可信代码沙箱。

`backend_calls` 是桥接函数进入次数；科学核函数调用次数、资源和外部行为还需原生日志核对。桥接器不独立监控任意外部 Python 程序的模型/网络调用，也不会将其声明当作已验证事实。

## 完整调用模板

完整程序在 [runtime/run_skill.py](runtime/run_skill.py)。下面代码可在包外保存；把 skill_dir 和输入输出路径替换为实际绝对路径：

```python
from pathlib import Path
import importlib.util
skill_dir = Path("C:/s/multistate-size-comparison")
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

本项没有通用量子求解器。“用户已有后端”可以是用户已有 Python 库或软件导出的结果；配套 file_backend.py 真实读取并记录文件哈希，不启动新求解。需要新计算时，由用户将其可信程序的输出转换为这里明确的复核 schema；专用物理方法与端点资格不能由桥接器自动生成。

## 结果保存与失败处理

结果目录包含 request.json、SKILL.used.md、run-receipt.json、result.json（已执行复核时）、SHA256SUMS.txt、results.zip 及其独立哈希。backend 模式另保存后端源码快照、原始返回、来源文件或原生中间产物。准备模式没有数值结果。

检查失败用 FAILED_NUMERICAL_CHECKS；异常用 FAILED_PARTIAL_OUTPUT_RETAINED，保留已经写出的产物、failure.json 与结果 ZIP。失败不等于合格端点。结果状态以实际回执及文件为准，外部来源声明仍需用户核对。成功输出也只证明所列检查。旧目录不会覆盖，无自动重试。

本地工程验收、历史结果复核、真实后端验收分开记录。可选 PySCF 模板本轮没有运行新量子任务；也没有调用模型、安装依赖或上传内部材料。
