# AI4OrgChem Runtime使用助手

只读路由科学任务，并可核对用户明确指定的既有安装记录与已登记主机文件；不启动Docker、安装登记或科学计算。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、参数和使用说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 完整处理指令和解释边界，可保存用于自己的代理 |
| [runtime/run_skill.py](runtime/run_skill.py) | 读取Skill→验证输入→调用[完整工具源码](runtime/analysis.py)→保存真实结果 |

顶层文件只有README.md和SKILL.md；程序、依赖、参数和案例在runtime。下载[完整Python代码包](downloads/runtime-usage-assistant-python.zip)或[Skill单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需有权限的账号，文件页用“Download raw file”保存，不把网页另存为.py。

## 知识与适用边界

普通固定水RHF路由到molecular-service single-point；旧AO复核路由本地后处理。任意用户条件态请求明确拒绝。inspect核对v1安装记录SHA、service/task/mode/image身份及登记host_files逐字节SHA；不访问引擎，不继承ENGINEERING_VALIDATED为科学PASS。

这是路由/只读身份助手，不是通用后端或新计算程序。引擎运行状态、镜像存在、profile数值门槛都标NOT_PROBED/NOT_EXECUTED。没有安装时先说明缺失，不自动安装/注册；旧结果不充当新计算。

本项目明确的Runtime安装合同：ai4orgchem-runtime-installation-v1、molecular-service/single-point/live。匹配只覆盖此合同及本机给定的文件，不声明其他服务或新科学资格。

## 安装与默认运行

Windows在有写入权限的短路径（例如D:\Chem\s）解压，进入README和runtime所在目录，使用Python3.12的独立环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\run_skill.py --output ..\runtime-usage-assistant-default
```

默认运行第一个教学请求。结果必须在Skill外全新目录；第二次换一个名字，拒绝已有目录且不覆盖。结果包括request.json、SKILL.used.md、result.json、run-receipt.json、SHA256SUMS.txt和results.zip。复制结果目录或ZIP即可保存。输入/计算失败保留failure.json并退出2；数值检查失败保存结果和检查详情并退出1，不当作成功。

## 三个案例：参数与对应结果

下列输入和全部程序是本项目编写的教学案例；合成数字不代表实际电子能或实验测量。反例的预期失败也单独保留。

| 案例 | Python调用 | 对应结果与状态 |
| --- | --- | --- |
| 1 固定普通水任务路由 | `python runtime/examples/01_case.py --output ../runtime-usage-assistant-1` | 路由成功，科学执行NOT_EXECUTED。 退出码0。 |
| 2 任意条件态拒绝 | `python runtime/examples/02_case.py --output ../runtime-usage-assistant-2` | 拒绝未准入的计算并保存failure.json。 退出码2。 |
| 3 旧数组任务路由 | `python runtime/examples/03_case.py --output ../runtime-usage-assistant-3` | 标NO_NEW_SCF，不启动后端。 退出码0。 |

Windows将python替换为`.\.venv\Scripts\python.exe`。案例完整程序：[①](runtime/examples/01_case.py)、[②](runtime/examples/02_case.py)、[③](runtime/examples/03_case.py)，请求JSON在对应01.json、02.json、03.json中。

## 修改参数与自己的输入

复制[runtime/examples/01.json](runtime/examples/01.json)到Skill外的`..\my-request.json`，按真实数据修改parameters、data和provenance。parameters含mode=route/inspect、intent=fixed_water_rhf/saved_ao_review/conditional_user_compute。data含user_goal；inspect另给runtime_root、installation_record、expected_record_sha256，路径由用户本机提供，案例不预填私有路径。

```powershell
.\.venv\Scripts\python.exe runtime\run_skill.py --input ..\my-request.json --output ..\my-skill-results
```

只修改参数不会更改旧结果，必须写新目录。严格UTF-8 JSON≤2 MB，不接受重复键或非有限数值。不应只改科学身份标签来绕过不兼容检查，来源标签本身不证明真实性。完整可复用[调用模板](runtime/examples/call_skill_template.py)支持--skill-dir、--input和--output，程序内部实际读取顶层Skill并保存其哈希，不调用模型。

软件执行通过只覆盖声明的输入和数值范围，不代表整个理论、化学身份或新量子方法获认证。下载包[SHA-256](downloads/SHA256SUMS.txt)与内部验收记录分开，内部材料不进入用户包。
