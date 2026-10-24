# 单目标贝叶斯优化提议

用已取得的显式观测拟合固定核GP，在有限候选池计算EI并提出一个待观测点，不生成实验反馈或冒称真实化学最优。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/chemical-bayesian-optimization-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

X按声明bounds缩放，Y仅按已有观测均值/总体SD缩放。固定振幅1和RBF长度尺度，不自动拟合核超参数；显式观测噪声进入alpha。EI=max方向使用mu−best−xi，min方向取负值等价变换，保存后验均值/潜函数SD及EI。只提出一个未观测候选。

噪声/核/平滑先验必须有研究依据；小样本后验SD不是经过校准的物理误差。不能自动保障安全、合成可行性或全局最优。当前只做一个有限池提议，不执行实验、不插入预测观测，不构成闭环实验验收。

[scikit-learn GaussianProcessRegressor](https://scikit-learn.org/stable/modules/gaussian_process.html)支持GP及alpha噪声约定；EI公式在本页显式给定。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\chemical-bayesian-optimization-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 最大化 | `python runtime/examples/01_case.py --output ../chemical-bayesian-optimization-1` | 真实GP拟合/EI，保存待观测提议；观测数量保持4。 退出码0。 |
| 2 显式改为最小化 | `python runtime/examples/02_case.py --output ../chemical-bayesian-optimization-2` | 真实GP拟合/EI，保存待观测提议；观测数量保持4。 退出码0。 |
| 3 改变探索xi | `python runtime/examples/03_case.py --output ../chemical-bayesian-optimization-3` | 真实GP拟合/EI，保存待观测提议；观测数量保持4。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。data显式bounds、feature_names/feature_units、observed_ids/x/y、source_ids、candidate_ids/x、objective_units；1–3维，3–32条已有观测，1–64个候选。重复观测坐标拒绝，已观测候选不参与提议；所有来源和单位必须明确。不会把预测补成观测。参数seed、direction=maximize/minimize、noise_sd、length_scale、xi（目标原单位）。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用大语言模型服务；本地训练、预测或提议计算如实记录。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
