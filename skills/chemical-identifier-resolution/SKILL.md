---
name: chemical-identifier-resolution
description: 对用户显式指定的化学名称、CAS、PubChem CID、InChIKey或SMILES准备并执行有来源的标识符解析，保留候选、歧义和失败，区别数据库结构与化学身份认证。
---

# 化学结构标识符：PubChem 与 CIR

先确认标识符类型、目的和是否允许发送查询到第三方。名称不是结构本身；不得凭常识为歧义名称指定唯一结构。默认只进行本地SMILES解析；联网需用户显式同意，不需要模型服务或账号密钥。

## 输入与范围

- UTF-8 CSV三列：id、query_type、query。ID唯一且保留前导零；类型显式为local_smiles、name、cas、cid或inchikey，不靠外观自动推断。1–10条、文件≤32000字节、查询≤256字符，本地结构≤128原子，不接受虚拟原子或CXSMILES。
- CAS正则及校验位通过只表示字符串满足编号规则，不证明注册存在、所有权或结构匹配。InChIKey是查询键，不能从哈希逆推出结构。CID必须是正整数。
- 本版不接受未知URL、任意API地址或隐式上传SMILES。需要数据库结构检索时另行设计和确认传输范围。

## 完整流程

1. 读取本SKILL.md及输入，保留原始字节；验证列、类型、ID及范围。网络关闭时遇远程标识符即拒绝，不发送查询。
2. local_smiles调用RDKit默认解析与canonical isomeric SMILES输出。解析包含默认清理，不另行脱盐、中和或生成未指定构型。
3. PubChem先查询CID列表，再按CID取SMILES、ConnectivitySMILES、InChIKey和分子式。最多10候选，验证CID与属性逐一对齐；多候选全部保留，不选择第一个。缺少带立体SMILES时失败，不用ConnectivitySMILES冒充替代。
4. CIR以显式名称、CAS或InChIKey查询SMILES；该接口可能按优先级选一个解释，并可能丢失名称中的立体信息。返回一个结果不代表没有歧义，也不代表已穷尽候选。
5. 分开保留服务来源和原返回结构，RDKit规范表示仅用于复核；不把PubChem、CIR和RDKit规范写法的字符串差异直接判为化学矛盾，不跨服务自动合并结构。
6. 网络请求逐次限速至≤2.5次/秒，单次20秒超时；429/503最多再试一次。记录HTTP状态、时间、请求URL、原响应及SHA-256。失败保留对应输入行，禁止把空结果补成结构。
7. 保存候选CSV、输入、Skill快照、请求日志、环境、回执、SHA-256和结果ZIP。说明哪些是本地解析、实际网络查询、失败或待专业确认；数值和文件状态以回执及文件为准。

## 解释边界

PubChem有自己的结构标准化，CIR采用其解析器及名称库；服务结果不是原始样品、盐型、质子化状态、同位素或立体纯度的认证。名称可能不唯一；未指定构型不等于无手性或外消旋。二维连通性SMILES不能代替带立体结构。精确化学身份需结合原始结构文件、供应商/实验记录及专家复核。本模块不预测活性、反应、物性或开展批量数据库镜像。

## 程序与来源

`runtime/resolve_identifiers.py`中的run_skill读取完整SKILL.md，调用固定本地/网络工具，不将自然语言指令当作Python执行；无模型模式只保存指令身份，不声称模型理解了Skill。

- [PubChem PUG-REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest)：命名空间、CID和属性协议。
- [PubChem服务论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030920/)：程序接口及限速原则。
- [NCI CIR官方说明](https://cactus.nci.nih.gov/chemical/structure_documentation)：解析优先级、InChIKey查询及名称立体信息局限。
- [RDKit解析与清理](https://www.rdkit.org/docs/RDKit_Book.html#molecular-sanitization)：本地图的约定。

软件运行通过不等于所有名称均被正确解析；报告具体来源、候选数和失败，不能笼统写“身份认证通过”。

## 输入校验与方法依据补充

CSV必须有且仅有唯一的id、query_type、query三列表头（顺序可变），逐记录严格核对字段数和引号；重复表头、空行、缺项或多项均拒绝，不覆盖或拼接查询。仅完整读取且在大小预算内的失败输入会随failure.json、Skill快照及results.zip保存。远程查询仍须显式许可；解析或校验失败不发送请求。

[Python CSV语法](https://docs.python.org/3.12/library/csv.html)说明记录与引号处理；[pandas2.2读取约定](https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.read_csv.html)提示畸形行的索引推断风险。输入合同由本模块明确限定，不能仅靠库默认值保证字段对应。 返回候选不是CAS登记或立体身份鉴定。

