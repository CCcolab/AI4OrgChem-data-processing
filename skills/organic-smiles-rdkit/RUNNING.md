# SMILES 与 RDKit：运行与下载

**分类：有机分子结构与身份识别** · Skill调用名：`organic-smiles-rdkit`

[教学与来源](TEACHING.md) · [获取Notebook程序](NOTEBOOK.md) · [返回首页](../../START_HERE_zh-CN.md)

本页只说明准备环境、配置凭据、填写参数、提交调用、保存和下载。知识点、数据出处和化学解释见“教学与来源”。

## 1. 准备Notebook与环境

从[Notebook程序入口](NOTEBOOK.md)下载ZIP并解压得到`organic-smiles-rdkit.ipynb`。打开[Google Colab](https://colab.research.google.com/)，选择 **文件 → 上传笔记本**，上传后先在自己的账号保存副本，再从第一单元开始运行。

Python 3.12/3.13兼容；固定RDKit 2026.03.6、NumPy 2.4.6、Matplotlib 3.11.2。准备单元在会话中建立独立venv并核验内嵌源码和样本哈希，CPU即可，无需Docker或GPU。

每次最多50条记录；模型请求最多3轮，每轮60秒，不自动重试；外层230秒终止，另留15秒终止进程与保存回执，不增加科学计算时间。

## 2. 配置凭据

- Colab：左侧钥匙 **Secret** 中保存 `DEEPSEEK_API_KEY`，为当前Notebook开启访问权限，再运行凭据单元。不同副本分别核对授权。
- 本地Jupyter：凭据单元从自己选择的.env读取同名变量，Colab不能读取本机磁盘上的.env。
- 不将密钥粘贴进代码、参数或聊天，不上传整份.env。程序只显示安全提示，不显示密钥值。[完整配置与报错说明](CONFIGURATION_zh-CN.md)。

两页都使用DeepSeek与已经审阅的白名单数值工具；模型提供工具调用，计算由实际程序执行。没有真实工具调用不能当作执行通过。

## 3. 参数与调用模板

[下载参数JSON](parameters.json) · [自然语言调用模板](task-template.txt) · [Skill指令](SKILL.md)

| 参数 | 默认 | 范围/意义 |
| --- | --- | --- |
| radius | 2 | 1–4整数；修改为3比较局部邻域扩展 |
| fp_size | 2048 | 1024/2048/4096，固定长度bit指纹 |
| include_chirality | true | 指纹和匹配是否使用手性；规范身份始终保留立体信息 |
| query_smarts | `[CX3](=O)[OX2H1]` | 合法且非空的SMARTS；本例查羧酸 |
| reference_id | 005 | 必须是有效记录ID；默认苯 |

## 4. 从头运行与修改参数

1. 依次运行准备、参数、凭据、调用、结果显示单元。准备失败时先解决依赖或输入错误。
2. 核对模型工具调用成功与程序数值检查；先看数值和图表，再看Agent文字。
3. 默认`radius=2`；改为`3`后依次重跑参数、凭据、调用、显示和下载单元。其余参数保持不变，每次生成新目录。
4. 核对14条记录中12条有效、2条拒绝；确认身份及描述符不变，相似度允许随指纹设置变化。不要删除错误输入或凭相似度合并化合物。

## 5. 保存Notebook与下载结果

| 需要保存什么 | 操作 |
| --- | --- |
| 自己的云端副本 | Colab“文件 → 在云端硬盘中保存副本”或“保存” |
| 含本次输出的原生Notebook | “文件 → 下载 → 下载.ipynb”，这是完整执行Notebook |
| 本次数值与图表 | 运行课末下载单元，单独保存本轮结果ZIP |

本轮ZIP为`organic-smiles-rdkit-results.zip`，全部运行合并包为`organic-smiles-rdkit-all-runs.zip`。若输出区下载控件加载失败，打开左侧 **文件** 面板，在准备单元显示的工作目录和本轮run目录找到ZIP，点击文件右侧菜单 **下载**；合并包位于工作目录。无需关闭标签页或更改浏览器安全设置。

结果包含analysis.csv、errors.csv、duplicates.csv、similarity.csv、参数、环境、结构和相似度图、数值检查及清单。下载后核对参数、记录ID和逐文件SHA-256；共享给他人前只选择必要材料并检查脱敏。

## 6. 本页材料下载

- [仅含Notebook的ZIP](organic-smiles-rdkit-notebook.zip)
- [已验源码与数据材料ZIP](organic-smiles-rdkit-materials.zip)
- [精选两轮结果示例ZIP](example-results.zip)：包含CSV、数值、PNG和参数，示例用于阅读与核对，真实新结果由自己运行产生。
- [输入CSV](molecules.csv) · [逐项知识来源](sources.json) · [数据来源](data-provenance.json)

结果判读回到[教学与来源](TEACHING.md)；文件身份见[全仓SHA-256清单](../../SHA256SUMS.txt)。
