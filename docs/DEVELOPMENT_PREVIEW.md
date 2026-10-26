# 真实计算对接开发预览

下列五项的正式入口只提供输入准备、给定结果复核和已有JSON文件导入。需要新计算时，用户可以单独阅读相应预览；预览真实后端完整实算未完成验收，不能视为已完成产品功能。

- [RHF输入准备与结果复核](../skills/rhf-single-point/runtime/development_preview/README.md)
- [轨道旋转与密度复核](../skills/orbital-localization-density/runtime/development_preview/README.md)
- [固定协议能量账本复核](../skills/fixed-protocol-energy-review/runtime/development_preview/README.md)
- [线性约束导数与端点复核](../skills/constrained-optimization-response/runtime/development_preview/README.md)
- [态集合与固定权重复核](../skills/multistate-size-comparison/runtime/development_preview/README.md)

预览需要用户自行核对现有软件、协议、依赖、资源和可信Python程序，显式--enable-preview、--backend及--execute；不会自动安装、启动Docker或调用模型。该桥接不是安全沙箱或硬资源调度器。本次未执行真实后端；历史记录不改写。

[返回32项目录](../START_HERE_zh-CN.md) · [功能与验收范围](BACKEND_STATUS.md)
