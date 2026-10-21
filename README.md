# AI4OrgChem-data-processing · Agent Skills

**[统一使用入口](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md)**

按有机化学专业应用选择Skill。先读知识和数据来源，再取得Notebook，在自己的Colab或本地Jupyter实际调用工具，解释并保存结果。

导航沿用既定的**7个专业应用分类＋1个共用支持分类**，下面只列实际提供的Skill页面。分类名称与Skill调用名固定，页面简称用于阅读。

| 入口 | 包含什么 |
| --- | --- |
| 教学与来源 | 学习目标、必要知识、具体参考章节与数据出处、示例图表和结果解释 |
| Notebook程序 | 获取原生.ipynb的专用入口，提供Notebook ZIP和文件校验 |
| 运行与下载 | 运行环境、凭据配置、调用模板与参数、Colab操作、保存和结果下载 |

## 有机分子结构与身份识别

| Skill | 教学与来源 | Notebook程序 | 运行与下载 |
| --- | --- | --- | --- |
| **SMILES 与 RDKit** | [知识与示例](skills/organic-smiles-rdkit/TEACHING.md) | [获取.ipynb](skills/organic-smiles-rdkit/NOTEBOOK.md) | [Colab操作与结果下载](skills/organic-smiles-rdkit/RUNNING.md) |

## 有机分析与实验数据处理

| Skill | 教学与来源 | Notebook程序 | 运行与下载 |
| --- | --- | --- | --- |
| **表格拟合与残差分析** | [知识与示例](skills/table-fitting-residuals/TEACHING.md) | [获取.ipynb](skills/table-fitting-residuals/NOTEBOOK.md) | [Colab操作与结果下载](skills/table-fitting-residuals/RUNNING.md) |

## 开始使用

1. 进入“教学与来源”，确认问题、数据和知识出处。
2. 进入“Notebook程序”，下载ZIP并解压得到.ipynb；也可使用原生文件页的Download raw file按钮。
3. 在[Google Colab](https://colab.research.google.com/)选择“文件→上传笔记本”，保存自己的副本；按“运行与下载”配置Secret、修改参数、运行并下载结果。

仓库保持私有，阅读和下载需使用已获授权的GitHub账号。Colab登录自己的Google账号；代码中不填写密钥值。GitHub页面用于学习与材料获取，计算在Colab或自己的Jupyter中进行。

## 参考资料说明

SMILES与RDKit依据Daylight SMILES/SMARTS和RDKit官方文档，AI4Chem Lecture 3作背景，数据为自主组织的教学结构。表格拟合使用David Harvey《Analytical Chemistry 2.1》12.5节Exercise 12.5.2咖啡因HPLC校准表，方法参考NIST统计手册。具体章节、链接、归属和数据处理见各Skill“教学与来源”。[来源与许可](docs/RIGHTS_REVIEW.md)。
