# 2343像素股东研究静态站快照

固定源码commit：702b6a8c47f714eb2bb67f079d313f4c02f7fb51。

将全部UI_DATA分包和UI_META解压到同一空目录，保留sites/shareholder-matrix结构。包含完整dist静态资产、5554股双查询gzip、fixtures和11个verify脚本（含verify-display-length.cjs）。

本地查看：进入sites/shareholder-matrix/dist，运行 `python3 -m http.server 8000 --bind 127.0.0.1`，再以浏览器打开本地8000端口。不要直接以file://打开，否则浏览器可能阻止本地fetch。没有打包平台token或发布凭据；本快照不代表网站部署状态。

Node标准库测试：进入sites/shareholder-matrix，运行 `for f in verify*.cjs; do node "$f" || break; done`。云端Node24.22.1本地11项测试均通过；Mac实际浏览器环境不能由此自动视为已验证。

显示长度10/20/30/60/120/250仅裁剪显示，不改变研究样本或收益统计。

为移除内部身份路径，仅QA.md历史3条证据引用改为相对路径；原/包双SHA和文档净化说明已记录。所有dist、fixtures、verify脚本均与固定commit工作树字节一致。数据、价格及数值未改。

本快照不含.git/.openai/.sites/node_modules、DEPLOYMENT.json、template.json、终端日志、旧NPZ或原始1.6GB采集数据。
