# 表格拟合与残差分析

**使用 `table-fitting-residuals` Agent Skill，分析有出处的咖啡因HPLC校准表。** 本页同时介绍用途、必要知识、输入模板、Colab实际调用和结果下载。它是有机物分析数据的使用样板，不是有机反应机理课程。

[下载Colab Notebook](table-fitting-residuals.ipynb) · [下载参数模板](parameters.json) · [下载数据CSV](caffeine-calibration.csv) · [自然语言任务模板](task-template.txt) · [知识与数据来源](sources.json)

仓库保持私有，本地样板不提供假冒可访问的公开徽章。先下载Notebook，再在 [Google Colab](https://colab.research.google.com/) 选择“文件→上传笔记本”；Notebook自带本页样本、Skill原文和运行器。打开后按顺序运行，在自己的Colab密钥面板配置 `DEEPSEEK_API_KEY`。不要上传整份本机.env。

## 保存的示例图表

以下是来源样板真实四点运行的保存输出，供在线阅读；不代表刚打开网页就已完成新的模型调用。

![咖啡因外标校准与残差](example-calibration-and-residuals.png)

反算浓度94.37792857876974 mg/L。正的拟合截距本身不能确立基线或系统误差的物理成因。来源与PNG哈希见 [保存输出说明](saved-output-provenance.json)。

## 这项Skill能帮你做什么

它指导Agent检查表格、单位和拟合目的，选择明确模型，调用数值工具，解释残差和局限。原文允许多种分析任务；**本页实现仅限未加权、带截距线性OLS校准**，不声称覆盖加权、非线性、因果分析或完整Skill测试。

示例问题：已知咖啡因标准液浓度及HPLC峰面积，怎样得到校准关系？峰面积424195对应多少mg/L？拟合残差告诉我们什么？只用前三个标准时结论如何变化？

## 知识与数据有何来源

数据逐项转录自 David Harvey《Analytical Chemistry 2.1》12.5节 **Exercise 12.5.2**，不是模型生成数据，也不是本项目实测。该题列出咖啡因反相HPLC标准液表和待测峰面积，给出的浓度答案约94.4 mg/L。[教材原页](https://chem.libretexts.org/Bookshelves/Analytical_Chemistry/Analytical_Chemistry_2.1_by_David_Harvey/Analytical_Chemistry_2.1_(Harvey)/12:_Chromatographic_and_Electrophoretic_Methods/12.05:_High-Performance_Liquid_Chromatography)

| 咖啡因浓度 mg/L | 峰面积，任意单位 |
| --- | --- |
| 50.0 | 226724 |
| 100.0 | 453762 |
| 125.0 | 559443 |
| 250.0 | 1093637 |

数据语境为同一题设条件下10 µL进样。这里使用已提供的数据，不操作仪器、不产生新的实验记录。教材追溯引用Kusch与Knupp，*Chem. Educator*，2003，8，201–205；本轮核对的是教材转录页，没有声称直接复核原论文原始实验数据。

教材页面标注作者David Harvey、CC BY-NC-SA 4.0。数据表和这一教材语境说明注明该来源及其许可，不为项目既有代码新增许可证，不复制原教材图。本站校准和残差图由本例数据重新计算生成。

最小二乘方法依据 [NIST统计手册：Least Squares](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm)。本例设浓度为x、峰面积为y，拟合：

$$\hat y=a+bx,\qquad RSS=\sum_i(y_i-\hat y_i)^2.$$

残差约定为观测减预测，反求浓度使用同一个校准模型：

$$e_i=y_i-\hat y_i,\qquad x_{sample}=(y_{sample}-a)/b.$$

残差检查与“高R²不充分”的说明依据 [NIST：How can I tell if a model fits my data?](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm)。本题只有4点且无重复；残差图是诊断起点，不能据此证明模型充分或方差恒定。本页不提供未经验证的置信区间、检出限或反应机理结论。

## 环境与实际调用方式

- Python 3.12及以上；NumPy 2.4.6、Matplotlib 3.11.2。Colab准备单元建立独立venv，不替换原预装依赖。
- 使用DeepSeek官方模型 `deepseek-flash` 和官方 `/chat/completions` 接口，标准库发起HTTPS请求；不使用OpenAI模型、OpenAI API或OpenAI SDK。协议字段兼容不意味着使用OpenAI服务。
- 必须有自己的DeepSeek凭据及可用网络；本地.env只读使用所选变量，不复制其它配置。Colab没有D盘访问能力，使用Colab Secrets；凭据不写入Notebook输出或结果ZIP。
- 不需要Docker、Runtime科学容器或GPU。本例数值工具在Notebook私有Python环境中计算。
- 上限4轮模型请求，每轮输出上限1400 tokens，每请求60秒超时，不自动重试。本例允许一次数值工具调用，重复调用或更改用户参数会停止并保留失败记录。模型服务可能计费，实际用量保存在回执中。

调用流程可见且可复核：校验原Skill哈希 → 把准确Skill原文交给DeepSeek → 模型返回 `fit_caffeine_calibration` 工具调用 → 运行白名单数值函数 → 把真实工具结果返回模型解释。模型生成代码不会执行；没有真实tool_call就不判为Agent调用通过。[DeepSeek官方工具调用说明](https://api-docs.deepseek.com/guides/tool_calls/)

## 模板与参数

可以直接复制 [task-template.txt](task-template.txt)。参数示例只用于该教材数据：

```json
{
  "include_highest_standard": true,
  "unknown_peak_area": 424195.0,
  "fit_intercept": true
}
```

| 字段 | 类型与单位 | 本例用途 |
| --- | --- | --- |
| include_highest_standard | 必需，布尔值 | true使用4点；false明确选择前三点，研究样本范围敏感性，不宣称最高点是异常点 |
| unknown_peak_area | 必需，有限非负数，峰面积任意单位 | 默认取教材424195；修改后属于自己的假设输入，不能称为教材新测量 |
| fit_intercept | 必需，true | 本样板拟合截距，不提供强制过原点选项 |

本样板不接受随意换模型、加权、自动删点、插补或高次多项式；这不限制通用Skill的其它可准备任务，只界定本页已实现范围。

## 在Colab中操作

1. 上传本页Notebook，运行折叠的“环境与样本准备”。看到依赖检查通过后再继续。
2. 确认参数表单默认值；在Colab Secrets添加 `DEEPSEEK_API_KEY` 并允许此Notebook访问，运行凭据单元。不要把密钥粘贴到普通代码单元。
3. 运行“调用Skill”。完成时核对 `PASS_REAL_MODEL_AND_TOOL_CALL`、Skill哈希、实际返回模型名、API轮数及工具调用数。
4. 先看程序数值与图表，再阅读Agent解释。独立Decimal公式用于复核系数和反求浓度；Agent解释并非学术或科学资格认证。
5. 将 `include_highest_standard` 改为false，按顺序重跑参数、凭据、调用和显示单元。每次创建新输出目录，不覆盖上次。
6. 点击“下载本次结果ZIP”，并通过Colab“文件→下载→下载.ipynb”保存执行后的Notebook。

## 结果怎样解释与保存

默认4点的反求浓度应接近教材的94.4 mg/L，具体系数、RSS、R²及残差以本次真实数值输出为准。斜率单位为“峰面积任意单位/(mg/L)”，截距单位为“峰面积任意单位”。不要把较高R²解读为已排除所有误差。

结果ZIP保存输入、参数、Skill与运行器、来源记录、环境、实际模型tool_call、数值结果、残差CSV、图表、Agent解释和逐文件SHA-256。不要把只收到模型文字、未调用数值工具、超时或拒绝参数的结果当成功。科学数值检查和模型解释审阅分别报告。

自测：为什么拟合截距？去掉最高标准后比较发生了什么，能否由此断定它错误？4点无重复能否证明方差恒定？该校准值是否需要额外稀释倍数，题设没有提供时能否自行添加？

## 验收边界

来源样板已完成两轮真实Colab调用、保存和实际下载验收；本次GitHub分发副本的复验状态见仓库首页的Skill状态说明。真实本地Agent调用、Colab依赖安装、默认/修改参数执行、保存和实际下载分别依据新增验收记录。原五课的云端PASS不自动迁移到本页。新RHF继续未验收；仓库保持私有，保留历史材料。


# 凭据配置：本地.env / Colab Secret

程序只保留变量名 `DEEPSEEK_API_KEY`，不填写密钥值。本地和云端的读取位置不同。

## 本地 Jupyter

将Notebook下载到本机并打开。凭据单元中的 `ENV_FILE` 默认指向当前工作目录的 `.env`；它是本地路径设置，不是密钥。程序只读取此文件中唯一的 `DEEPSEEK_API_KEY` 项，不读取其它提供者配置，也不修改文件；不从操作系统环境变量静默覆盖该值。可保留原文件中的引号或行尾注释。

文件不存在会提示检查路径；变量缺失、重复、空值或格式错误会分别停止。无需把密钥写到Notebook、聊天或参数JSON。不上传整个.env。换电脑时仅修改本机配置路径。

## Colab

Colab运行在Google云端，无法读取本机D盘。打开左侧钥匙图标 **Secret**，点击 **添加新密钥**：

| 位置 | 填写内容 |
| --- | --- |
| 名称 | `DEEPSEEK_API_KEY`（固定变量名） |
| 值 | 你自己的DeepSeek密钥；仅在Secret面板填写 |
| 笔记本访问权限 | 为当前Notebook开启；新副本需单独核对 |

不要把值替换到 `userdata.get('DEEPSEEK_API_KEY')` 中，也不要修改此名称。若Notebook报错，先读提示：Secret不存在→检查名称与账号；未授权→开启当前Notebook访问；其它读取失败→确认登录与Secret保存状态。凭据单元只显示读取成功或安全提示，不显示值。配置完成后再运行凭据、调用、结果和下载单元。

## 调用失败与重跑

HTTP 401：密钥无效或已撤销；402：检查DeepSeek账户可用额度；429：速率限制，稍后手动重试；5xx：提供者服务异常；网络超时/连接失败：检查网络后手动重试。不自动循环请求，不把配置成功当模型调用成功。执行失败时显示安全的失败类型与HTTP状态，不回显认证头、响应正文或密钥。

若出现“保存失败：笔记本已在此会话外部更改”，这是版本冲突，与密钥是否有效无关。使用“文件→在云端硬盘中保存一份副本”保留修改，不强制覆盖其它会话。云端调用与下载仍需单独验收。

安全边界：不在代码、Notebook输出、日志或结果包保存密钥；子进程仅通过内存环境接收所选密钥。已误写入代码的旧密钥应由用户在提供者后台撤销并更换；不要把旧值放进报告。
