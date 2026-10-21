# 表格拟合与残差分析：运行与下载

**分类：有机分析与实验数据处理** · Skill调用名：`table-fitting-residuals`

[教学与来源](TEACHING.md) · [获取Notebook程序](NOTEBOOK.md) · [返回首页](../../START_HERE_zh-CN.md)

本页只说明准备环境、配置凭据、填写参数、提交调用、保存和下载。知识点、数据出处和化学解释见“教学与来源”。

## 1. 准备Notebook与环境

**[▶ 在 Colab 运行](https://colab.research.google.com/github/CCcolab/AI4OrgChem-data-processing/blob/72a69915b6ea0250c99bf2fe6c498a212852c03a/skills/table-fitting-residuals/table-fitting-residuals.ipynb)**

直接打开仓库中的 Notebook，登录自己的 Google 账号后保存副本，再从第一单元开始运行。私有仓库首次需在 Colab“文件 → 打开笔记本 → GitHub”勾选“包括私有代码库”，由你本人核对并授权 `repo`（公私仓库读写）与 `gist` 权限。账号需已获本仓库访问权；代码不填写 GitHub Token。

下载副本仅作备用：从[Notebook程序入口](NOTEBOOK.md)下载ZIP并解压，在 Colab 选择 **文件 → 上传笔记本**，或在本地 Jupyter 打开。

Python 3.12及以上，固定NumPy 2.4.6、Matplotlib 3.11.2。准备单元在会话中建立独立venv并核验内嵌源码和样本哈希，CPU即可，无需Docker或GPU。

最多4轮模型请求、每轮1400输出tokens、每请求60秒，不自动重试；只允许一次数值工具调用。调用使用自己的DeepSeek账户与额度。

## 2. 配置凭据

- Colab：左侧钥匙 **Secret** 中保存 `DEEPSEEK_API_KEY`，为当前Notebook开启访问权限，再运行凭据单元。不同副本分别核对授权。
- 本地Jupyter：凭据单元从自己选择的.env读取同名变量，Colab不能读取本机磁盘上的.env。
- 不将密钥粘贴进代码、参数或聊天，不上传整份.env。程序只显示安全提示，不显示密钥值。[完整配置与报错说明](CONFIGURATION_zh-CN.md)。

两页都使用DeepSeek与已经审阅的白名单数值工具；模型提供工具调用，计算由实际程序执行。没有真实工具调用不能当作执行通过。

## 3. 参数与调用模板

[下载参数JSON](parameters.json) · [自然语言调用模板](task-template.txt) · [Skill指令](SKILL.md)

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

## 4. 从头运行与修改参数

1. 依次运行准备、参数、凭据、调用、结果显示单元。准备失败时先解决依赖或输入错误。
2. 核对模型工具调用成功与程序数值检查；先看数值和图表，再看Agent文字。
3. 默认`include_highest_standard=true`；改为`false`后依次重跑参数、凭据、调用和显示单元。每次生成新目录。
4. 比较4点与3点的系数、RSS、残差和反算浓度；数值检查采用独立Decimal公式，模型文字不代替科学解释。

## 5. 保存Notebook与下载结果

| 需要保存什么 | 操作 |
| --- | --- |
| 自己的云端副本 | Colab“文件 → 在云端硬盘中保存副本”或“保存” |
| 含本次输出的原生Notebook | “文件 → 下载 → 下载.ipynb”，这是完整执行Notebook |
| 本次数值与图表 | 运行课末下载单元，单独保存本轮结果ZIP |

本轮文件名为`skill-results.zip`。若输出区下载控件加载失败，打开Colab左侧 **文件** 面板，展开准备单元显示的工作目录及本轮run目录，在ZIP的右侧菜单选择 **下载**。无需关闭标签页或更改浏览器安全设置。

结果包含输入、参数、系数、残差CSV、图表、独立数值检查、环境、解释和逐文件清单。下载后核对参数、是否使用最高标准点及SHA-256；只收到模型文字或超时/拒绝不等于完成计算。

## 6. 本页材料下载

- [仅含Notebook的ZIP](table-fitting-residuals-notebook.zip)
- [原始数据CSV](caffeine-calibration.csv) · [默认参数](parameters.json) · [调用模板](task-template.txt)
- [保存的数值示例](example-result.json) · [校准和残差图](example-calibration-and-residuals.png)
- [逐项知识来源](sources.json) · [数据来源](data-provenance.json)

结果判读回到[教学与来源](TEACHING.md)；文件身份见[全仓SHA-256清单](../../SHA256SUMS.txt)。
