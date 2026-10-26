# 线性约束导数与端点复核：真实计算对接开发预览

此目录的真实后端调用**尚未完成新实算验收**，不列入正式已验证功能。正常学习与已有结果处理请返回[README](../../README.md)，运行prepare、review或import即可。原内部待验记录与历史实算范围保留，不能据入口调整宣称完成。

## 依赖与进入条件

自行检查用户已有且信任的科学后端、版本、方法、输入schema和预算；本项目不会安装软件或启动Runtime/Docker/WSL。本项没有已验收的新量子/优化求解实现；须由用户定义专用物理协议并提供真实后端。 固定协议算子、约束导数和态集合资格不能由通用桥接器生成。

用户必须显式给出--enable-preview、--backend可信.py及--execute，才可能导入其Python代码。该代码与用户同权限执行；预览不是沙箱、独立网络/模型监测或硬资源限制。--enable-preview只是显式选择，不表示科学验收通过。

```powershell
python runtime/development_preview/run_backend.py --enable-preview --mode backend --input C:/s/my-native-request.json --backend C:/s/my-trusted-backend.py --execute --output C:/s/out/preview-new
```

用户后端函数run_backend(request, output_dir)返回review_request（parameters/data/provenance）和execution（至少kind）。先保存输入、后端源码与返回，再调用正式同一数学复核；不把后端自报来源或收敛当作独立认证。原schema见[backend-contract.json](backend-contract.json)。

## 保留的模板与边界

backends/demo_backend.py仅返回人工教学数据；backends/file_backend.py仅导入已有文件；examples/03_backend_contract_demo.py只演示文件适配器合同，需--enable-preview，不运行科学求解器。它们通过调用合同测试也不提供新科学资格。

真实条件态、约束优化端点及多态集合需要各自独立协议和后端验收；当前保留接口示例，不冒充已有实算功能。

相同目录外的新结果路径才可写入，失败保留已生成文件和非零回执，不自动重试。开发预览产物不能替代原始软件日志、真实资源使用、独立物理分项与端点检查。
