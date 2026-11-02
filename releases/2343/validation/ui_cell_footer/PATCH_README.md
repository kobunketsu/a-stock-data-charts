# 单元格同高与竖线分位数修复

这是基于 MANIFEST.json 中 base_commit 的最终修复，只包含正确竖线 h 版本。

在网页源码根（包含 dist/app.js）先核对基础文件 SHA256，然后执行：

```sh
git apply --check /path/to/marker_hover.patch
git apply /path/to/marker_hover.patch
node verify-cell-footer.cjs
```

亦可使用 files/ 中的精确文件覆盖同名文件。应用后逐文件 SHA256 必须与 manifest final_sha256 相同。验证脚本需要既有 fixtures 与 dist/prior 数据；数据不在本增量包中，保持原版。

公开仓库采用 QA_CURRENT.md 即可；不复制私站累计内部 QA.md。该文档替代是有意的，三个代码/测试文件与已部署版本逐字节一致。不包含托管配置、账号、令牌、数据资产或 Git 元数据。
