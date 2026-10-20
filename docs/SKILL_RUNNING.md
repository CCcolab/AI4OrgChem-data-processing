# Skill运行与下载

仓库保持私有。用已授权GitHub账号阅读Notebook，点击文件页Download raw file下载.ipynb，再到Colab“文件→上传笔记本”。Google登录及Secret配置由使用者本人操作。新Notebook需单独确认Secret访问权限；无需公开仓库或填写GitHub令牌。

准备单元自带Skill与数据、核对哈希并创建独立venv。参数默认为4个标准、未知峰面积424195、带截距true。将include_highest_standard改为false是明确使用前三个标准的敏感性练习，不认定最高点错误。来源样板的反算浓度为94.37792857876974与94.11215895100756 mg/L，实际新结果以本次程序输出为准。

先运行环境、参数、凭据、调用、显示和下载单元，再按表单修改参数并重跑参数至下载。凭据每次读取到内存，子进程运行后清除所选变量；不显示或写入Notebook输出。缺配置、未授权、HTTP错误及超时会停止，不算通过，不自动重试。

核对PASS_REAL_MODEL_AND_TOOL_CALL、COLAB位置、实际模型名及tool_calls=1。核对数值结果、单位与残差，不能把R²高或正的截距当作物理因果证据。结果ZIP通过课末链接下载，外层.ipynb通过“文件→下载→下载.ipynb”保存，两者分别核验。

保存的示例图只用于GitHub阅读，不代表你已执行。Notebook当前分发版本的真实在线验收见SKILL_STATUS.md。新RHF未验收；试学、专家解释评定及其它Skill不在本页验收范围。
