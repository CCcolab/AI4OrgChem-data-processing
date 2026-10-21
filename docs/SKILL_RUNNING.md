# Skill运行与下载

[统一入口](../START_HERE_zh-CN.md)

| 页面 | 参数修改与操作指南 |
| --- | --- |
| [SMILES与RDKit](../skills/organic-smiles-rdkit/README.md) | [Notebook及材料下载、Colab上传、radius=2改3](../skills/organic-smiles-rdkit/DOWNLOADS.md) |
| [表格拟合](../skills/table-fitting-residuals/README.md) | [Notebook](../skills/table-fitting-residuals/table-fitting-residuals.ipynb)；include_highest_standard从true改false，按[配置说明](../skills/table-fitting-residuals/CONFIGURATION_zh-CN.md)运行 |

私有仓库使用已授权GitHub账号。先从Notebook文件页Download raw file下载.ipynb，再在[Colab](https://colab.research.google.com/)选择“文件→上传笔记本”，保存自己的副本。不要把GitHub令牌或DeepSeek密钥写进代码。Colab Secret为DEEPSEEK_API_KEY并单独授权当前Notebook；本地使用自己的.env。

依次运行环境、参数、凭据、调用、结果和下载单元；依赖安装和模型调用需要网络及自己的额度，按页面说明控制预算。模型选择白名单工具，程序完成真实数值计算；保存的示例不是新运行。修改参数后使用新输出目录，不覆盖旧结果。

用“文件→下载→下载.ipynb”保存原生Notebook，结果ZIP单独保存。若Chrome富输出JavaScript加载异常，无需关闭标签页或降低安全设置；从Colab左侧文件面板找到本次工作目录和run目录下载ZIP。表格页文件为skill-results.zip；RDKit页为organic-smiles-rdkit-results.zip，合并文件organic-smiles-rdkit-all-runs.zip位于工作目录。

下载后核对参数、清单及SHA。模型解释与数值检查分别阅读；具体适用范围、来源和结果判读见各页。
