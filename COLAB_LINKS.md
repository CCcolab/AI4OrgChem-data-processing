# Colab入口尚待配置

目标owner、repository与固定ref未确认；当前不生成不存在的GitHub/Colab运行链接。可以下载colab目录中的适配Notebook上传Colab做候选验收。

维护者在批准的目标身份确定后运行`python tools/configure_links.py --owner OWNER --repo REPOSITORY --ref COMMIT_SHA`，只生成本地链接，不创建仓库、不推送、不提升远程验收状态。正式发布后必须用真实链接复验五课。
