# 表格Q-learning有限环境模拟

在用户完整给出的有限教学MDP中实际执行表格Q-learning及冻结策略评价，区分终止和截断，不模拟未知化学反应或控制实验设备。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-q-learning-simulation-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

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
