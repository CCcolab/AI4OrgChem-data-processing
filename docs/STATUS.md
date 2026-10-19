# 当前完成与未验收范围

核心0.1.0。

五课已完成从GitHub首页进入新版Colab、私有依赖安装、默认/修改参数共10轮从头运行、手工参数修改、结果重载及Drive保存复开。五份原生Notebook和五份独立结果ZIP下载均已验收；Notebook内嵌ZIP、独立下载ZIP与本次云端附件逐字节一致，SHA-256及结果清单核对通过。环境准备长代码默认折叠，课程标题无括号日期。新RHF继续未验收（NOT_EXECUTED）。

本次只同步完成状态、导航和验收摘要，科学代码、样本、内置wheel、运行器及保存输出不变。内置原课和科学输出中的旧状态文字是历史快照，最新完成范围以本说明及docs/STATUS.md为准；FAIL、DIAGNOSTIC与NOT_ASSESSED边界不变。

GitHub用于在线阅读，Colab用于交互运行。Binder、其它账号或环境、试学及学习者独立解释能力仍未验收。旧Drive副本不自动更新，请从课程首页打开新版入口。

## 数值与证据

- B03：Y_SHIFT=0.5时截距1.5、斜率2、RSS14，残差不变。
- F01：漏项时程序SUCCEEDED、科学检查FAIL，残差−0.5 Eh。
- F02：自旋求和非正交AO密度在原AO顺序及重叠矩阵下采用Tr(DS)=10；轨道变号比较密度与能量，不要求系数逐元素相同。坏度量FAIL，全MO检查DIAGNOSTIC，科学资格NOT_ASSESSED。
- 10轮结果共8个PNG及260条课程清单完成核对。五份原生Notebook、五份内嵌结果ZIP及五份独立下载ZIP均已核验。

[验收摘要](ACCEPTANCE.md) · [机器摘要](VALIDATION_SUMMARY.json)。公开摘要不含私人Drive链接、账号、主机路径和原始日志。
