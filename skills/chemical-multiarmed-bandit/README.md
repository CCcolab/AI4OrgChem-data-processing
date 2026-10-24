# 多臂老虎机决策教学

运行有界Bernoulli UCB或Thompson本地模拟，或复核明确的0/1历史并给出待执行建议，不把模拟奖励解释成化学实验产率。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-multiarmed-bandit-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

UCB先按声明顺序探索未访问臂，之后均值+exploration×sqrt(2log(t)/n)。Thompson独立Beta(1,1)先验，成功/失败更新。推荐不增加计数；保留每条奖励及模拟概率。

只支持平稳独立Bernoulli奖励，不支持连续产率、费用约束、漂移或化学实验安全。有限模拟没有最佳臂/收敛保证。历史来源标签不证明真实实验，不能把选择建议算作已完成观测。

[Sutton与Barto作者教材](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf)第2章讨论多臂老虎机及探索；本页具体UCB/Beta更新式明确列出，不继承化学适用性。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-multiarmed-bandit-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 UCB模拟 | `python runtime/examples/01_case.py --output ../chemical-multiarmed-bandit-1` | 真实本地模拟或历史计数，提议状态PENDING且不制造新观察。 退出码0。 |
| 2 Thompson模拟 | `python runtime/examples/02_case.py --output ../chemical-multiarmed-bandit-2` | 真实本地模拟或历史计数，提议状态PENDING且不制造新观察。 退出码0。 |
| 3 历史重放后建议 | `python runtime/examples/03_case.py --output ../chemical-multiarmed-bandit-3` | 真实本地模拟或历史计数，提议状态PENDING且不制造新观察。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters含mode、algorithm、seed、budget1–200、exploration；data为2–10个唯一arms，模拟给probabilities，历史模式给arm/reward/source_id。仅整数0/1奖励，历史来源ID唯一。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
