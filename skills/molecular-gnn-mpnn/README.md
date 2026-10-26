# 分子图GNN与MPNN入门

用显式有界分子图和固定留出实际训练小型消息传递网络，保存预测、权重与置换检查，不把合成标签示范当作化学预测验证。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/molecular-gnn-mpnn-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


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

原子投影后按键级加权汇聚邻居消息、残差ReLU、图sum pooling和线性输出；不是某篇论文的完整基准复现。回归目标仅训练内缩放，分类用BCEWithLogits。Adam全批训练固定预算，检查有限梯度、节点重编号不变性及自生成权重重载。

当前自编图特征只有原子序数、度、电荷、芳香标志及键级，未编码手性、同位素或3D；涉及这些信息时记录提示，不能用于对应性质区分或身份认证。只演示小型训练，不提供通用药效/产率预测、外推或适用域认证。保存文件为本次自生成权重，不读取不可信checkpoint。

[Gilmer等MPNN原论文](https://proceedings.mlr.press/v70/gilmer17a.html)定义消息传递框架；此处是明确简化的教学网络，不继承原论文性能。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\molecular-gnn-mpnn-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

32条项目编写的简单SMILES；回归标签为1+.2MolWt−1.5TPSA+.5MolLogP加seed17小扰动，分类标签为MolWt>70，人为组不是化学骨架组。这是实际本地CPU训练、保存和重载；标签不是实验值，小预算不认证优化收敛、预测泛化或化学用途。没有语言模型服务调用或预训练权重下载。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 回归图网络 | `python runtime/examples/01_case.py --output ../molecular-gnn-mpnn-1` | 实际训练并保存留出预测/权重；固定预算不是收敛认证。 退出码0。 |
| 2 二分类图网络 | `python runtime/examples/02_case.py --output ../molecular-gnn-mpnn-2` | 实际训练并保存留出预测/权重；固定预算不是收敛认证。 退出码0。 |
| 3 改变深度与宽度 | `python runtime/examples/03_case.py --output ../molecular-gnn-mpnn-3` | 实际训练并保存留出预测/权重；固定预算不是收敛认证。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data含5–64条唯一ids、单组分SMILES及监督任务target/target_unit，可声明groups；parameters含seed与零起始test_indices。相同忽略手性/同位素/映射的图不得跨划分，声明组别也不得跨划分。仅≤64原子有机元素图，无金属/多组分。完整参数见JSON；原SMILES保留。另给task、hidden_units4–32、depth1–3、epochs1–100及learning_rate1e-5–.05。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 用户CSV

`runtime/run_from_csv.py`明确选择id、smiles及可选target/groups列，以--template保留参数并完全替换示例data；监督任务必须提供--target-unit。结果保留原CSV。更换行数时须同步修改零起始test_indices，重复图和声明组别不得跨训练/测试。

```powershell
.\.venv\Scripts\python.exe runtime\run_from_csv.py --template runtime\examples\01.json --input runtime\examples\molecules.csv --target synthetic_response --target-unit arbitrary_synthetic_response --groups group --output ..\graph-csv-results
```

## 知识要点、前提与公式

本教学网络用h_v⁰=ReLU(Linear(x_v))，h_v^{l+1}=ReLU(h_vˡ+Σ_{u→v}b_uv Linear_l(h_uˡ))传播消息，其中b_uv为键级/3；最后对节点向量求和再线性输出。共享消息规则及sum pooling使图级函数对节点编号置换不变，而节点表示随编号等变。一次反序检查是软件诊断，不是对所有图或化学对称性的穷尽证明。

原子输入为原子序数/100、度/4、形式电荷/2及芳香标志，键只用键级；这不是唯一或完备的分子表示。手性、同位素和3D未编码，不能区分依赖这些信息的性质。重复图按忽略手性/同位素/映射的规范图标识隔离训练与测试，是保守的重复保护，并不自动隔离化学近邻或证明所有图可区分。

## 基础阅读与来源层级

章节定位：Hamilton作者第5章草稿，§5.1消息传递与式5.2–5.3的置换性质（可访问正文）。

基础阅读：[HAMILTON](https://www.cs.mcgill.ca/~wlh/grl_book/)。

原始方法/作者专论：[GILMER](https://proceedings.mlr.press/v70/gilmer17a.html)。

Hamilton引用作者2020年9月第5章预出版草稿，核对消息传递与置换性质；不冒称最终出版社修订版全文。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 自由基表示边界

本自编四维原子特征不编码自由基电子数；解析后任一原子的GetNumRadicalElectrons不为0即拒绝，在创建张量前报告错误。因此C（甲烷）可用，而[CH3]等自由基不进入训练/测试。立体化学与同位素仍按原提示处理，表示等价图不跨划分。不把该限制推广为Chemprop自身特征器的结论。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。

目标单位target_unit不能由空格、制表或换行组成；无量纲需显式声明。该要求同时用于JSON和CSV，不自动推断单位或改变输入标签。

