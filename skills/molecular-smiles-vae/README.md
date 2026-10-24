# 受限SMILES序列VAE教学

实际训练只接受无分支C/N/O链的微型GRU-VAE，逐条保留解码和无效结果，演示重参数化与KL项，不冒称通用分子生成器。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/molecular-smiles-vae-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

GRU编码器输出对角高斯mu/logvar，重参数化采样；GRU解码器teacher forcing训练，损失为非PAD词元平均交叉熵+beta×样本平均KL。保存重载编码器结果，从标准正态潜变量逐词元采样，分别记录是否EOS结束、可解析、长度合规。

不是通用SMILES tokenizer。空、无效、未结束或超长输出全部保存，不隐藏失败；新颖性仅相对于本次20条训练规范字符串，不代表数据库/专利新颖性、可合成性或性质改善。没有留出生成质量/泛化认证；固定预算不认证收敛。

[Kingma与Welling原论文](https://arxiv.org/abs/1312.6114)支持重参数化及变分目标，不能赋予本教学模型分子生成质量。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\molecular-smiles-vae-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

20条项目编写的C/N/O无分支链；没有性质标签、实验数据或预训练模型。实际CPU训练与解码不证明生成质量或化学可用性。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 beta=.05、潜变量2维 | `python runtime/examples/01_case.py --output ../molecular-smiles-vae-1` | 实际训练25步并保留8次解码全部结果；有效率按实际输出计算，不预设全有效。 退出码0。 |
| 2 beta=.5对照 | `python runtime/examples/02_case.py --output ../molecular-smiles-vae-2` | 实际训练25步并保留8次解码全部结果；有效率按实际输出计算，不预设全有效。 退出码0。 |
| 3 beta=1、潜变量4维 | `python runtime/examples/03_case.py --output ../molecular-smiles-vae-3` | 实际训练25步并保留8次解码全部结果；有效率按实际输出计算，不预设全有效。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data为唯一ids与5–64条仅由大写C/N/O构成的无分支SMILES；parameters显式seed、epochs1–100、learning_rate、latent_dim2–8、beta0–2、samples1–16、max_length1–12。其他SMILES语法明确拒绝。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
