# 当前完成与未验收范围

日期：2026-10-19；核心0.1.0。

五课已完成真实Colab默认/修改参数共10轮运行、私有依赖安装、手工参数修改、结果重载及Drive另存副本。五份原生下载的Notebook已核验；其内嵌结果ZIP均与云端结果逐字节一致。单独点击ZIP链接下载仍未验；新RHF仍未验收（NOT_EXECUTED）。

本次仅更新公开导航和状态文字，不改变科学代码、样本、内置wheel及运行器。保存的科学输出和Colab内置原课中的旧状态文字属于历史快照，以本页说明及docs/STATUS.md为准；FAIL、DIAGNOSTIC及NOT_ASSESSED边界不变。

GitHub只显示静态内容；交互计算使用独立Colab适配。公开页面/固定ref入口首次同步后单独核对；Binder、其它账号/环境、试学与独立解释能力未验收。

## 数值与证据

- B03：Y_SHIFT=0.5时截距1.5、斜率2、RSS14；残差不变。
- F01：漏项时程序SUCCEEDED，科学检查FAIL，残差-0.5 Eh；不会自动补项或改参考。
- F02：自旋求和、原AO顺序、非正交AO密度的电子数用Tr(DS)=10，不能用Tr(D)。轨道变号时核对密度与能量不变量；坏度量FAIL，全MO检查DIAGNOSTIC，科学资格NOT_ASSESSED。
- 10轮结果共8幅PNG、260条课程清单通过校验。五份外层Notebook包含修改参数回执与结果附件，原生Notebook下载已核对，独立ZIP按钮下载仍未验。

公开摘要见[VALIDATION_SUMMARY.json](VALIDATION_SUMMARY.json)，仅记录课程与文件哈希，不包含私人Drive链接、账号、主机路径或原始浏览器日志。
