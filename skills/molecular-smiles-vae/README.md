# 受限SMILES序列VAE教学

实际训练只接受无分支C/N/O链的微型GRU-VAE，逐条保留解码和无效结果，演示重参数化与KL项，不冒称通用分子生成器。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/molecular-smiles-vae-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


## 已验证运行环境与功能

**当前版本的输入与失败处理已在下列环境运行成功；完整学习流程仅有固定历史版本的运行记录。**

| 项目 | 已验证内容 |
| --- | --- |
| 操作系统 | Windows 11 |
| Python / 设备 | 3.12.14 / CPU |
| 本轮实际依赖范围 | Python标准库（仅输入层测试，未导入数值/模型后端） |
| 本轮已验证功能 | JSON根类型/必需结构/非有限值拒绝、输入与Skill快照、failure.json、ZIP/SHA-256保存、已有结果保护；未进入analysis或模型后端 |
| 测试内容 | 三种早期输入反例（数组根、缺必需结构、NaN）均退出2并保留失败证据；已有输出被拒绝且原字节不变 |
| 测试结果 | 4/4项符合预期；含输入拒绝/旧结果保护，不表示所有命令退出0 |
| 历史运行记录 | 历史固定bb629ee版（2026-10-25）在Linux / Python 3.12.14 / CPU完成默认入口；不等于本修订版完整运行复验 |
| 验证日期 / 程序基线 | 2026-10-26 / 67aaaaa；本次只改说明与分发，不改计算程序 |
| 未覆盖范围 | 本轮未执行完整拟合、训练、预测、采样/策略学习或模型权重重载；默认入口完整运行仅有固定历史版本记录。完整Torch运行未复验，GPU及其它依赖版本也未验证。不认证真实化学预测泛化、实验改进或最优性。 |

完整运行的依赖仍需按runtime/requirements.txt单独配置；本轮未重新安装或核验整套模型依赖，不能把安装清单当作本轮已运行环境。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/docs/VERIFIED_ENVIRONMENTS.md)。


## 知识与适用边界

GRU编码器输出对角高斯mu/logvar，重参数化采样；GRU解码器teacher forcing训练，损失为非PAD词元平均交叉熵+beta×样本平均KL。保存重载编码器结果，从标准正态潜变量逐词元采样，分别记录是否EOS结束、可解析、长度合规。

不是通用SMILES tokenizer。空、无效、未结束或超长输出全部保存，不隐藏失败；新颖性仅相对于本次实际训练集的规范字符串，不代表数据库/专利新颖性、可合成性或性质改善。没有留出生成质量/泛化认证；固定预算不认证收敛。

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

## 知识要点、前提与公式

编码器给出q(z|s)=N(μ,diag(exp(logvar)))，通过z=μ+exp(logvar/2)⊙ε、ε∼N(0,I)把随机性与可微参数分开。与标准正态先验的KL为½Σ(μ²+exp(logvar)−1−logvar)。GRU解码器用teacher forcing预测下一词元；采样时从标准正态潜变量逐词元解码。

标准按序列的负ELBO包含每条序列的重建负对数似然之和与KL。本实现明确使用全批非PAD词元平均CE加beta×样本平均KL；两项归一尺度不同，beta=1不应直接称为未经缩放的标准序列ELBO，改变长度分布会改变相对权重。这里只接受无分支大写C/N/O链，不是通用SMILES语法。可解析、EOS结束与长度合规分别记录，空/无效/未结束样本保留；新颖性仅对实际训练规范字符串集合。

## 基础阅读与来源层级

章节定位：Deep Learning第10章Sequence Modeling与第20章Deep Generative Models（目录）；AEVB §2.4重参数化及第3节VAE（作者HTML正文）。

基础阅读：[DL](https://www.deeplearningbook.org/)。

原始方法/作者专论：[AEVB](https://arxiv.org/html/1312.6114v11)。

Deep Learning为MIT Press2016版；核对作者公开目录中的相应章节，章节正文抓取超限，不据此声称已读全书。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。

