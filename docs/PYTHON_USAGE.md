# Python使用方式

从[目录](../START_HERE_zh-CN.md)进入Skill README，先看科学范围和案例数据来源，再下载完整Python包。在Windows有写入权限的短路径解压，每个Skill创建单独Python3.12环境，按runtime/requirements.txt安装。机器学习模块会在本机训练小模型，不调用大语言模型服务，也不下载未知预训练权重。

顶层README解释知识、参数与案例；完整SKILL.md提供可下载指令；runtime中的.py实际读取SKILL.md、校验输入、执行工具及保存结果。无语言模型模式只读取/保存Skill身份，不声称模型理解了指令。输入、参数、环境、结果和回执对应同一轮，写Skill外全新目录；复制结果文件夹或results.zip保存。

用户CSV只在明确支持的入口使用，不猜列名、单位或标签。量子模块当前区分准备、旧数组复核和真实后端运行；已有结果及软件PASS不自动继承为新计算通过。Docker未启动时不改设置、不偷偷改用其他后端。
