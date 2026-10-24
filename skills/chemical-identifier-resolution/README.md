# 化学结构标识符：PubChem 与 CIR

把“字符串是什么”与“是哪一个化合物”分开处理。适用于小规模名称、CAS、CID、InChIKey解析，以及已有SMILES的本地图复核。不要求数据库账号，不调用大语言模型。

| 文件 | 职责 |
| --- | --- |
| 本README | 必要知识、三个案例、输入输出与操作说明 |
| [完整SKILL.md源码](SKILL.md?plain=1) | 任务指令、方法、工具流程和解释边界，可保存后接入自己的代理 |
| [runtime/resolve_identifiers.py](runtime/resolve_identifiers.py) | 完整Python流程；读取Skill→检查CSV→本地/联网工具→保留候选和失败→保存结果 |

顶层只有README.md和SKILL.md；程序、依赖、配置及案例在runtime。下载[完整Python代码包](downloads/chemical-identifier-resolution-python.zip)或[SKILL单文件ZIP](downloads/SKILL-md.zip)。私有GitHub需先登录有权限的账号；链接打开文件页后使用“Download raw file”，不要把网页另存为.py。

## 先理解这些边界

- CAS校验位正确只代表编号形式正确；本程序不认证其注册状态。InChIKey不能逆向还原结构，必须查询数据库。
- 名称可以有歧义，数据库可能采用不同的盐型、质子化与标准化规则。PubChem多候选全部保留；CIR单一返回也可能只是按优先级选定的结果。
- 保留服务原SMILES及RDKit规范写法。规范字符串不同不必然表示不同化合物；相同也不能认证实物样品、纯度或构型。未指定立体信息不等于外消旋。
- 本地模式不联网。远程查询必须显式加`--allow-network`，会把CSV中的名称、CAS、CID或InChIKey发送给所选公共服务；本版不上传用户SMILES。

来源是[PubChem官方接口](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest)、[PubChem服务论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030920/)、[NCI CIR官方说明](https://cactus.nci.nih.gov/chemical/structure_documentation)和[RDKit解析约定](https://www.rdkit.org/docs/RDKit_Book.html#molecular-sanitization)，并非经典教材的替代。CIR官方明确提示名称解析可能遗漏立体信息；结果须结合原始结构专业核对。

## 安装与结果保存

Windows在有写入权限的短路径解压，例如`D:\Chem\ids`，进入包含README.md和runtime的目录。使用Python 3.12，在独立虚拟环境中安装，后续命令不需要激活环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r runtime\requirements.txt
.\.venv\Scripts\python.exe runtime\resolve_identifiers.py --output ..\ids-default
```

结果必须在Skill目录外的**全新目录**；已有目录拒绝覆盖。每次运行换名字，例如`..\ids-default-2`。输入、Skill快照、candidates.csv、requests.json、原响应、run-receipt.json、SHA256SUMS.txt及results.zip都保存在指定目录。复制该目录或results.zip即可保存；没有浏览器运行步骤。

## 三个案例：问题、调用与对应结果

案例数据是本项目编写的公开小分子教学输入。网络返回内容可能随数据库更新变化；下面是2026-10-24实际接口调用结果，不能把它当永久注册保证。

| 案例 | 如何运行 | 对应输出及判读 |
| --- | --- | --- |
| ①本地结构：CCO、OCC及指定构型乳酸 | `python runtime/examples/01_local.py --output ../ids-local` | 两种乙醇写法均为CCO；乳酸保留有效指定构型。3条LOCAL_GRAPH_PARSED、网络0次；不声称名称或样品已认证 |
| ②PubChem：ethanol、CID 2519、64-17-5 | `python runtime/examples/02_pubchem.py --allow-network --output ../ids-pubchem` | 乙醇名称和CAS得到候选CID 702、C2H6O；CID 2519得到咖啡因C8H10N4O2。3候选行、4次请求；状态CANDIDATE_REQUIRES_REVIEW |
| ③CIR：ethanol、64-17-5 | `python runtime/examples/03_cir.py --allow-network --output ../ids-cir` | 两条均返回CCO，2次请求；状态SERVICE_SELECTED_STRUCTURE_REQUIRES_REVIEW，不表示穷尽歧义 |

表中`python`替换为Windows的`.\.venv\Scripts\python.exe`；程序链接：[①](runtime/examples/01_local.py)、[②](runtime/examples/02_pubchem.py)、[③](runtime/examples/03_cir.py)。每个案例均有完整可读源码和CSV，而非封装的不可见代码。

## 用户CSV和参数修改

UTF-8 CSV必须有且只有三列，ID保留前导零且唯一。最多10条，单查询≤256字符。显式选择类型，不把名称当SMILES猜测：

```csv
id,query_type,query
001,name,ethanol
002,cas,64-17-5
003,cid,2519
004,inchikey,LFQSCWFLJHTTHZ-UHFFFAOYSA-N
```

保存为Skill目录外的`..\my-identifiers.csv`后：

```powershell
.\.venv\Scripts\python.exe runtime\resolve_identifiers.py --input ..\my-identifiers.csv --service pubchem --allow-network --output ..\my-identifiers-results
```

将`--service pubchem`改为`cir`比较服务，或`both`分开保存两种来源。CIR案例仅支持name、cas、inchikey；对cid会保存明确失败行，而不会把CID当作名称。输入全部为local_smiles时无需网络开关。网络关闭而CSV包含远程查询时会在发送前拒绝。

## 完整SKILL调用模板

从[call_skill_template.py](runtime/examples/call_skill_template.py)复用命令行模板，核心流程是：

```python
from resolve_identifiers import run_skill

receipt = run_skill(
    input_csv="../my-identifiers.csv",
    output_dir="../my-identifiers-results-2",
    service="pubchem",
    allow_network=True,
)
# run_skill内部读取顶层完整SKILL.md，保存SKILL.used.md及其SHA-256。
# 然后依次校验CSV、调用固定工具、保留候选/失败并保存真实产物。
print(receipt)
```

导入时将本Skill的runtime加入Python模块路径，或直接使用完整模板。这里没有模型理解指令；Skill内容作为流程规范和运行身份保存。要接入自己的模型代理，须另行设计工具白名单及凭据，不能将文本当作Python执行。

## 出错时怎么看

网络不可达、404、限速、响应格式变化、结构无法解析均保留为FAILED_RETAINED行；命令退出码1表示含失败，2表示输入/文件级错误，0只表示本次候选查询流程无失败。查看requests.json中的HTTP状态、时间及原响应。429/503最多再试一次，超时20秒；不要无限重试或据此猜测化合物不存在。联网测试通过也不能等价为化学身份认证。

下载包完整性见[SHA-256](downloads/SHA256SUMS.txt)。内部验收日志独立保存在项目内，不进入用户代码包。

## 输入校验与方法依据补充

CSV必须有且仅有唯一的id、query_type、query三列表头（顺序可变），逐记录严格核对字段数和引号；重复表头、空行、缺项或多项均拒绝，不覆盖或拼接查询。仅完整读取且在大小预算内的失败输入会随failure.json、Skill快照及results.zip保存。远程查询仍须显式许可；解析或校验失败不发送请求。

[Python CSV语法](https://docs.python.org/3.12/library/csv.html)说明记录与引号处理；[pandas2.2读取约定](https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.read_csv.html)提示畸形行的索引推断风险。输入合同由本模块明确限定，不能仅靠库默认值保证字段对应。 返回候选不是CAS登记或立体身份鉴定。

