# 直接从竖线h版升级至修好布局的两行版

基础站点源码commit见MANIFEST。对应公开仓库已同步竖线h修复版；不要先应用中间有布局回归的两行补丁。

在网页根（含dist/app.js）核对base_sha256后执行：
```sh
git apply --check /path/to/cell_layout_fixed.patch
git apply /path/to/cell_layout_fixed.patch
node verify-cell-layout.cjs
```
或用files中的精确文件覆盖。应用后核对final_sha256。已有verify-cell-footer.cjs保持不变，包中另附副本供核查；验证需要既有fixtures/dist/prior数据，数据不重复打包。
公开说明用QA_CURRENT.md，不复制内部累计QA。包不含截图、账号、托管配置或数据资产。
