# AI4OrgChem-data-processing · Agent Skills

**在线了解我们创建的Agent Skill，下载Notebook，在Colab或本地实际调用。** 每个Skill使用一页说明与一份可运行.ipynb，提供功能、知识和数据出处、运行环境、调用模板、参数、结果解释及下载。

本仓库保持**私有**，需要已授权的GitHub账号访问。GitHub页面用于阅读；Colab提供Python运行环境。模型实际调用由你的DeepSeek凭据授权，数值由白名单程序计算；不使用OpenAI API或SDK。

## 当前Skill样板

| Skill | 在线介绍与图表 | Notebook | 参数与任务 |
| --- | --- | --- | --- |
| 表格拟合与残差分析 | [功能、来源与用法](skills/table-fitting-residuals/README.md) | [在线预览并下载.ipynb](skills/table-fitting-residuals/table-fitting-residuals.ipynb) | [参数](skills/table-fitting-residuals/parameters.json) · [任务模板](skills/table-fitting-residuals/task-template.txt) |

以David Harvey教材中咖啡因HPLC外标校准表为例，实际调用table-fitting-residuals Skill，拟合带截距直线、检查残差并反算浓度。数据是教材转录，不是AI编造或本项目新实验。本例属于有机物分析数据处理，不把它称为有机反应机理课程。

## 如何在线运行

1. 打开上表Notebook，在GitHub文件页面点击 **Download raw file（下载原始文件）**，得到.ipynb。
2. 打开 [Google Colab](https://colab.research.google.com/)，选择“文件→上传笔记本”，上传刚下载的文件。私有仓库不能依靠匿名Colab链接自动读取，不需要把GitHub令牌填入Notebook。
3. 在Colab左侧Secret保存DEEPSEEK_API_KEY并授权当前Notebook。不要修改代码中的变量名，不上传整份.env。
4. 从头运行，修改参数后再运行相关单元，核对真实回执及图表，最后下载结果ZIP及执行后的Notebook。

本地Jupyter读取你设置的.env路径。详情见 [配置说明](skills/table-fitting-residuals/CONFIGURATION_zh-CN.md) 和 [运行指引](docs/SKILL_RUNNING.md)。无需本机Web服务或Docker；依赖安装和模型调用需要网络。

## 完成与未验收范围

本次GitHub分发副本已完成独立环境安装、默认/修改参数的DeepSeek真实工具调用、保存、原生Notebook和两轮结果ZIP实际下载复验。详见 [当前Skill状态](docs/SKILL_STATUS.md) 与 [在线复验记录](docs/SKILL_ONLINE_ACCEPTANCE.md)。Chrome课末HTML下载存在输出加载限制，已验证的替代下载步骤见运行指引；模型解释未经专家独立审核。

本页完整实现的是未加权、带截距线性OLS样板。其余14项Skill及18项通用候选仍按后续计划接入，不代表已开放33个服务。模型解释、教学试学与程序运行分别评价。**新RHF继续未验收。**

旧五课入口作为 [历史原型说明](LEGACY_FIVE_LESSONS.md) 保留，不再作为当前平台教学组织依据。

数据出处、方法依据与适用范围详见Skill页面。保留Harvey教材CC BY-NC-SA 4.0归属及NIST方法引用；项目级代码许可仍按 [既有许可说明](docs/RIGHTS_REVIEW.md) 执行，本次不新增许可证。当前仓库不含.env、密钥、私有数据库、本机部署或原始私有验收附件。
