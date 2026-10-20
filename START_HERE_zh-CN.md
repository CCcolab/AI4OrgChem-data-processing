# AI4OrgChem-data-processing统一使用入口

**固定入口：** [开始使用](https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md)。请从本页进入当前已发布的Skill页面。

GitHub用于阅读与下载，运行使用自己的Google Colab或本地Jupyter。每项Skill一页，提供功能、知识与数据来源、环境、调用模板、参数、结果解释及下载；不需要本机Web平台账号或登录令牌。

## 当前已发布的Skill

| Skill | 介绍与来源 | Notebook | 输入模板 |
| --- | --- | --- | --- |
| 表格拟合与残差分析 | [功能、知识与数据来源](skills/table-fitting-residuals/README.md) | [预览与下载](skills/table-fitting-residuals/table-fitting-residuals.ipynb) | [参数](skills/table-fitting-residuals/parameters.json) · [调用模板](skills/table-fitting-residuals/task-template.txt) |

本页仅列实际已同步的页面。完整33项按7个专业应用分类和1个共用支持分类组织，本地建设目录与验收队列由项目维护；本地准备情况不等于GitHub已发布内容。

## 开始运行

1. 打开Notebook文件，选择Download raw file下载.ipynb。
2. 在[Colab](https://colab.research.google.com/)选择“文件→上传笔记本”，保存自己的副本。私有仓库使用已授权GitHub账号读取，不向Notebook填写GitHub令牌。
3. 按[配置说明](skills/table-fitting-residuals/CONFIGURATION_zh-CN.md)在Colab Secret配置DEEPSEEK_API_KEY及本页访问权限；本地读取自己选择的.env。代码中不填密钥值。
4. 从头运行、修改参数、核对数值与图表，保存执行Notebook并下载结果ZIP。[运行与下载说明](docs/SKILL_RUNNING.md)。

参考资料与原始方法见各Skill页及[项目首页](README.md)；跟随操作与独立解释分别评价，适用范围以已验样板记录为准。

维护者参阅[自动防回流检查](docs/PLATFORM_BOUNDARY_GUARD_zh-CN.md)。当前入口由PLATFORM_ENTRY.json定义，旧历史页面不作为当前平台使用说明。
