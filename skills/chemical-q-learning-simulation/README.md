# 表格Q-learning有限环境模拟

在用户完整给出的有限教学MDP中实际执行表格Q-learning及冻结策略评价，区分终止和截断，不模拟未知化学反应或控制实验设备。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-q-learning-simulation-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。公开GitHub文件可直接查看和下载，文件页用“Download raw file”保存，不把网页另存为.py。


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
| 未覆盖范围 | 本轮未执行完整拟合、训练、预测、采样/策略学习或模型权重重载；默认入口完整运行仅有固定历史版本记录。没有以输入层通过替代完整算法运行结论。不认证真实化学预测泛化、实验改进或最优性。 |

完整运行的依赖仍需按runtime/requirements.txt单独配置；本轮未重新安装或核验整套模型依赖，不能把安装清单当作本轮已运行环境。 输入准备、数值复核、模型训练与化学用途验证分别报告；全平台对照见[运行环境与验证范围](../../docs/VERIFIED_ENVIRONMENTS.md)。


## 知识与适用边界

Q(s,a)←Q+alpha[r+gamma maxQ(s′,·)−Q]，仅真正terminal时bootstrap项为0。外部max_steps截断仍bootstrap；有限任务内生时间限制需把剩余时间纳入状态，本模块不替用户构造。训练后冻结Q运行greedy评价并检查不更新，保存原始轨迹和q-values.npy。

环境、概率、奖励全部是显式教学假设，不是反应动力学/能量或实验结果。固定alpha/epsilon/预算不保证渐近收敛或最优性；不连接实验设备，不提供真实化学环境。

[Sutton与Barto作者教材](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf)Q-learning；[Farama终止与截断说明](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)支持bootstrap区分。

## 输入校验与方法依据补充

数值数组在NumPy类型提升前逐项校验：JSON布尔值true/false、null、字符串或与数值混合的这些值均拒绝，不把标志列自动转换为0/1测量、目标、度量或概率。整数0/1仍可用于已声明的数值/二分类接口；缺失值须先按研究协议处理。数组结构遍历预算为100000项，另保留各模块原有形状、有限性和数据规模限制。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-q-learning-simulation-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 默认有限MDP | `python runtime/examples/01_case.py --output ../chemical-q-learning-simulation-1` | 实际训练、保存轨迹/Q及冻结评价；截断不伪装终止。 退出码0。 |
| 2 改变折扣因子 | `python runtime/examples/02_case.py --output ../chemical-q-learning-simulation-2` | 实际训练、保存轨迹/Q及冻结评价；截断不伪装终止。 退出码0。 |
| 3 一步上限截断反例 | `python runtime/examples/03_case.py --output ../chemical-q-learning-simulation-3` | 实际训练、保存轨迹/Q及冻结评价；截断不伪装终止。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters显式seed、episodes1–200、max_steps1–20、alpha、gamma<1、epsilon、evaluation_episodes1–20。data含states/actions、initial_state/terminal_states、三维transition_probability/reward及reward_unit。终态必须吸收且后续奖励0。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。

## 知识要点、前提与公式

有限MDP需要完整状态、动作、转移概率及奖励语义；本例学习折扣回报E[Σ_t γᵗr_t]的表格动作价值。一步Q-learning为Q(s,a)←Q(s,a)+α[r+γ max_b Q(s′,b)−Q(s,a)]；真正终态的后续价值为零。外部max_steps只是采样截断，不能抹去尚未终止环境的bootstrap；若时间上限属于任务本身，剩余时间必须纳入状态以保持Markov性。

训练后冻结Q进行greedy评价；轨迹字段undiscounted_return明确求未折扣奖励和，用于描述所采样有限轨迹，区别于Q所估计的折扣动作价值。固定alpha、epsilon及有限预算未满足渐近收敛定理的全部条件，不能因评价收益较高就声称最优策略。所有概率与奖励是教学输入，不是反应动力学、电子能或实验反馈。

## 基础阅读与来源层级

章节定位：Sutton/Barto §6.5 Q-learning（出版社目录）；Watkins/Dayan第2节方法及收敛定理假设（作者PDF正文）。

基础阅读：[SUTTON](https://mitpress.mit.edu/9780262039246/reinforcement-learning/)。

原始方法/作者专论：[WATKINS](https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf)。

实现接口：[FARAMA](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。

Sutton/Barto为2018年第2版，出版社目录确认§2.7 UCB与§6.5 Q-learning；作者整书链接本次超时，未声称重读全书。 各条原论文/软件文档的具体访问范围及版本记录见[runtime/sources.json](runtime/sources.json)；滚动API页面与固定运行依赖分开记录。经典书目补充基础，现代算法仍保留其原始论文，API文档继续用于接口约定。

## 失败产物与输出保护

对安全读取的限长常规输入，在合法全新输出目录中保存原输入、Skill及适用设置；JSON解析、缺字段、重复ID、非有限数值及CSV前处理失败均保存failure.json、SHA256SUMS.txt和results.zip，并失败退出。CSV入口同时保留原始CSV、模板和列/单位选择。输出已存在、位于源码内或为符号链接时不写入；超限或符号链接输入不复制。命令行缺少必需选项等尚未形成有效调用的错误由参数解析器拒绝，不创建结果。失败回执不代表数值或模型已执行。
