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

## 运行与结果

表格拟合样板支持带截距的普通最小二乘线性校准、残差分析和未知样品浓度反算。已完成默认与修改参数的DeepSeek真实工具调用、Notebook保存，以及原生Notebook和结果ZIP下载验证。操作步骤见 [运行指引](docs/SKILL_RUNNING.md)，验证详情见 [在线复验记录](docs/SKILL_ONLINE_ACCEPTANCE.md)。

运行后可查看数值结果、图表和模型解释，并下载结果文件。若Chrome课末下载区域加载异常，可按运行指引通过Colab文件面板下载ZIP。

## 数据与方法来源

本例采用David Harvey教材中的咖啡因HPLC校准数据，方法说明引用NIST统计手册。数据出处、CC BY-NC-SA 4.0归属及适用范围见 [Skill说明](skills/table-fitting-residuals/README.md)；代码许可信息见 [许可说明](docs/RIGHTS_REVIEW.md)。
