# AI4OrgChem-data-processing统一使用入口

**[统一使用入口](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md)**

从具体化学问题选择Skill，阅读知识与数据来源，在Notebook中修改参数并实际调用工具，核对结果后下载。页面同时提供教学说明和可运行.ipynb。

导航采用7个专业应用分类和1个共用支持分类；本页按分类显示已经可以使用的页面，空分类不生成栏目或占位链接。[分类与页面索引](NAVIGATION.json)。

## 有机分子结构与身份识别

| Skill | 教学与来源 | Notebook | 运行与下载 |
| --- | --- | --- | --- |
| 分析有机分子｜SMILES与RDKit | [介绍](skills/organic-smiles-rdkit/README.md) | [阅读及下载](skills/organic-smiles-rdkit/organic-smiles-rdkit.ipynb) | [操作指南](skills/organic-smiles-rdkit/DOWNLOADS.md) |

## 有机分析与实验数据处理

| Skill | 教学与来源 | Notebook | 运行与下载 |
| --- | --- | --- | --- |
| 表格拟合与残差分析 | [介绍](skills/table-fitting-residuals/README.md) | [阅读及下载](skills/table-fitting-residuals/table-fitting-residuals.ipynb) | [操作指南](docs/SKILL_RUNNING.md) |

## 如何运行

仓库保持私有，使用已授权GitHub账号阅读和下载。点击Notebook文件页Download raw file，再到[Google Colab](https://colab.research.google.com/)选择“文件→上传笔记本”，保存自己的副本。按各页配置同名Colab Secret或本地.env，代码中不填写密钥值。GitHub提供阅读和下载；Colab或本地Jupyter执行程序。

原生Notebook通过文件菜单下载；结果ZIP按对应运行指南下载。保存的数值和图表供阅读，新结果以你本次真实运行和复核为准。[运行与下载说明](docs/SKILL_RUNNING.md)。

## 参考资料说明

| 页面 | 知识和数据依据 |
| --- | --- |
| SMILES与RDKit | [Daylight SMILES](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html)、[SMARTS](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html)、[RDKit官方文档](https://www.rdkit.org/docs/GettingStartedInPython.html)；课程Lecture 3作背景，样本为自主组织的教学结构，详见[逐项来源](skills/organic-smiles-rdkit/sources.json)及[数据说明](skills/organic-smiles-rdkit/data-provenance.json) |
| 表格拟合 | David Harvey《Analytical Chemistry 2.1》12.5节Exercise 12.5.2的咖啡因HPLC校准表；方法引用NIST统计手册，详见[知识来源](skills/table-fitting-residuals/sources.json)及[数据说明](skills/table-fitting-residuals/data-provenance.json) |

每页区分文献知识、教学样本和程序结果，引用具体章节和链接。跟随操作与独立解释分别评价，结果适用范围见各页。[来源与许可说明](docs/RIGHTS_REVIEW.md)。
