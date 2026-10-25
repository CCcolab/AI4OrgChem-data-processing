# 统一入口与旧平台防回流检查

当前入口由根目录PLATFORM_ENTRY.json声明，统一指向GitHub的START_HERE_zh-CN.md。本地详细32项专业Skill工作目录与GitHub已发布页面分开列示；不把本地准备状态当成已同步页面。冻结的早期README和历史记录不是当前使用入口。

## 自动执行位置

- `.githooks/pre-commit`：检查Git实际索引，包含待提交文件的真实字节；不能用未暂存的干净副本掩盖已暂存旧代码。
- `.githooks/pre-push`：检查HEAD提交内容，不能靠工作区删除掩盖旧提交中的代码。
- `tools/package_checked_skill.py`：打包前检查完整候选目录，打包后再次检查ZIP；只在通过后生成正式文件和SHA-256。公开包与内部交付包使用不同资料边界。
- `tools/publish_checked_skill.py`：检查发布目录、HEAD、回归测试和目标仓库身份与PLATFORM_ENTRY声明的可见性，然后才允许普通推送；不支持强推。
- GitHub Actions `platform-boundary`：每次push、PR和手动触发运行违规样本测试、提交检查与发布目录检查。只读权限，不调用模型或科学后端。

本地安装钩子使用`git config --local core.hooksPath .githooks`，不修改全局Git配置。新克隆不会继承本地Git配置，需执行此命令；GitHub端由Actions执行同一检查。维护者可有意绕过本地钩子，因此它不是针对恶意绕过的沙箱。

## 检查规则

拒绝旧localweb/deployment模块、旧启动/停止/状态脚本、已知旧Windows部署包名称、实际旧模块导入和启动命令、serve CLI及静态8765绑定。注释和历史说明中提到8765不等于运行代码，不据此误删知识与证据。

递归检查ZIP、wheel、tar.gz、代码容器中的BUNDLE/RESOURCE Base64资源及ZIP附件。检查不执行代码、不解包到文件系统；损坏、加密、越界路径、超预算或不能检查的声明资源按失败处理。旧模块改文件名后若仍保留导入、启动或绑定行为也会被拦截；不能保证识别所有蓄意混淆的任意程序。

公开发布还拒绝内部验收目录、令牌、数据库、真实机器路径和私人Drive链接。内部完整交付允许保存原始验收材料，但仍禁止旧服务代码。源码扫描走当前目录和实际存在的受跟踪文件，不遍历虚拟环境、Git对象库及整个历史输出；staged/commit模式直接读取Git对象，发布/交付模式读取候选完整目录，不能用源码扫描代替发布检查。

## 维护命令

```powershell
# 当前源码
.\.venv\Scripts\python.exe -B tools\check_platform_boundary.py --scope source
# 实际待提交索引
.\.venv\Scripts\python.exe -B tools\check_platform_boundary.py --scope staged
# 公开候选，目录中必须有统一入口
.\.venv\Scripts\python.exe -B tools\check_platform_boundary.py --root PUBLICATION_DIRECTORY --scope release
# 使用统一受检打包器；输入和输出均在项目内，且不能覆盖旧文件
.\.venv\Scripts\python.exe -B tools\package_checked_skill.py --input PUBLICATION_DIRECTORY --output NEW_ZIP
```

历史交付构建脚本接入同一检查；新增构建脚本也须调用检查器。已封存旧包不在本轮重写，新打包必须重新检查。

## 保证范围

检查依据当前字节，不随清理记录日期自动放宽。规则和入口的更新也受测试与CI核对。此前私有阶段的分支保护接口返回403；本次按用户授权公开仓库，不自动新增或修改分支保护。当前保护以GitHub实际设置为准，CI不能被描述为不可绕过的强制门槛。本地钩子与受检发布器对正常流程执行阻断；有意禁用钩子或绕过发布器仍可能直接写入。

升级权限后应重新读取分支保护接口并设置platform-boundary为必需检查，不能照抄本轮状态。GitHub缓存旧提交的物理删除不属于检查器能力，不使用“所有历史已彻底擦除”表述。
