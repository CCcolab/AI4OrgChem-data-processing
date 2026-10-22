## 配置模型凭据

**本地**：配置文件位置由你自己选择；在参数ENV_FILE指定已有`.env`。只读取其中`DEEPSEEK_API_KEY`，不修改文件，不在代码、命令行或结果里填写密钥值。

**Colab**：左侧钥匙“Secret”中使用同名`DEEPSEEK_API_KEY`并开启当前Notebook访问权限。不要上传整份.env、不要把密钥粘贴到代码。此配置按Google账号及Notebook授权生效；缺失、空值、未授权或API失败会明确停止。新Notebook首次授权需你本人完成。

执行只将内存凭据传给子进程，结束后清除临时变量；调用轨迹不保存Authorization或密钥。只发送本页公开教学结构、Skill指令和本次参数给DeepSeek，不发送个人文件或环境变量集合。
