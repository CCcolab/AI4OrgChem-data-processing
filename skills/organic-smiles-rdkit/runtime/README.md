# SMILES 与 RDKit配套模块

本目录提供五步Notebook使用的完整程序和输入。molecules.csv是14条项目教学输入，parameters.json是默认参数，data-provenance.json记录构造与哈希，sources.json记录语言规范、官方文档及方法论文核对范围。四文件的阅读、参数和输出对应关系见Skill学习页面。

source_id=project是本例构造/核对标签，不把AI4Chem课程列为数据或方法来源。旧版错误归类在项目内历史记录保留，本版按Daylight开放规则与固定RDKit程序复核。

Colab①已携带并写入全部文件，无需手动上传。②表单是实际参数；修改下载的parameters.json不会自动修改云端。不要修改说明JSON绕过资源哈希。

需要Python3.12/3.13及requirements-colab.txt中的固定依赖。molecule_tool.py执行数值分析；skill_agent.py仅允许限定工具；colab_workflow.py组织五步界面。Colab密钥来自同名Secret，本地来自自己选择的.env；不要把密钥值写入源码或数据。

README中的两组数值示例为LOCAL_NUMERICAL_ONLY，不含新模型调用回执。Notebook实际运行后以本轮回执、参数和下载清单为准。
