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

## 参考资料说明

各Skill页面按“知识点—出处—使用位置”组织参考资料。化学概念参考相应领域教材；公式和算法参考方法论文、专业手册或软件官方文档；示例数据注明教材题目、论文附件、公开数据集或真实计算记录；Skill功能和参数以对应的指令及实际程序为依据。

资料通过作者、大学、出版社和官方文档网站提供的合法开放原文，或合法获取的图书馆与正版资料核对。引用注明作者、书名或论文题名、版本、章节／页码／公式号和可访问链接。教材内容与模型生成的解释分别标识；转载文字、图片和数据时，按相应许可注明归属与改动。

### 当前表格拟合案例的参考资料

| 用途 | 参考资料与定位 | 本页采用的内容 |
| --- | --- | --- |
| 教材与示例数据 | David Harvey，《Analytical Chemistry 2.1》，第12.5节，Exercise 12.5.2：[作者与教材介绍](https://sites.google.com/depauw.edu/dth/analytical-curriculum-projects/analytical-chemistry-2-1) · [教材题目与数据表](https://chem.libretexts.org/Courses/BethuneCookman_University/B-CU%3A_CH-345_Quantitative_Analysis/Book%3A_Analytical_Chemistry_2.1_%28Harvey%29/12%3A_Chromatographic_and_Electrophoretic_Methods/12.05%3A_High-Performance_Liquid_Chromatography) | 本科分析化学开放教材中的咖啡因HPLC外标校准练习；逐项转录4组浓度—峰面积及待测峰面积424195，教材参考答案94.4 mg/L |
| 线性拟合方法 | NIST/SEMATECH统计手册，[§4.4.3.1 Least Squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm) | 最小二乘准则、带截距直线模型和系数计算 |
| 残差与结果判读 | NIST/SEMATECH统计手册，[§4.4.4 How can I tell if a model fits my data?](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm) | 观测减预测的残差定义、残差图及结合多项证据判断拟合质量 |
| Skill功能与调用 | [table-fitting-residuals指令](skills/table-fitting-residuals/SKILL.md) · [功能及参数说明](skills/table-fitting-residuals/README.md) | 表格检查、拟合任务和结果解释的调用约定；本页实现带截距的普通最小二乘校准 |

教材将该题数据归于Kusch与Knupp发表于 *Chem. Educator*（2003，8，201–205）的研究。本例的直接数据依据是上述教材题目，引用链与转录记录见 [数据来源记录](skills/table-fitting-residuals/data-provenance.json) 和 [参考资料清单](skills/table-fitting-residuals/sources.json)。Harvey教材相关内容按CC BY-NC-SA 4.0注明归属；代码许可信息见 [许可说明](docs/RIGHTS_REVIEW.md)。
