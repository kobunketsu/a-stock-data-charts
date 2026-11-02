# 2343参考池迁移器：离线预备，尚无新结果

只替换5554股冻结查询的历史参考语料。输入必须是query_all_a_up80的single_stock和lookback_patch，不读取新抓供应商近期28条差异，也不重建查询原始数据。

## 严格不变
查询名册5554、节点ID/股东源/价格/日历/日期/基价/所有5N先前变化/行列分组全部不变，不再运行分箱。除empty_reference_cell外拒绝原因不得解除。只更新参考事件数/股票数/小样本、该空格资格、参考版本/SHA、参考池名单标识与衍生覆盖数。原空格有新样本可变合格；但future_notice等其他拒绝仍存在则不可变合格。新空格反之失去匹配。统计日起点的事后信息等原警告保留。

## 真实输入契约
--pool指向2343名单CSV；五份all曲线必须已经独立审计完成、每份162条曲线（两起点各81格），9行9列。matrix_manifest必须由最终真实冻结结果生成，不允许以旧1494改标签充当新数据。格式：

```json
{"status":"AUDITED_COMPLETE","reference_pool_count":2343,"pool_sha256":"真实名单文件SHA256","matrices":{"10":{"path":"实际10日全历史曲线相对路径","sha256":"真实文件SHA256"},"20":{"path":"...","sha256":"..."},"30":{"path":"...","sha256":"..."},"60":{"path":"...","sha256":"..."},"120":{"path":"...","sha256":"..."}}}
```

相对path按manifest所在目录解析。缺矩阵、SHA不符、股票池不含于5554或输出已有文件立即失败。默认不执行、不生成输出；--execute才运行。默认新输出shareholder_model_2343/query_all_a，不覆盖旧。

```sh
python3 shareholder_model_2343/query_migration/test_contract.py
python3 shareholder_model_2343/query_migration/migrate_reference.py \
 --base query_all_a_up80/single_stock --patch query_all_a_up80/lookback_patch \
 --pool shareholder_pool_screening_multiyear/analysis_all/pool_from_2015-10-01.csv \
 --matrix-manifest shareholder_model_2343/lookbacks/QUERY_REFERENCE_MANIFEST.json
# 最终矩阵独立通过后，才在同命令添加 --execute
```

## 验证计划
当前仅语法和4个合成契约单测通过，无真实新矩阵、无新查询结果。正式运行逐锚断言允许修改字段以外全部相同；base60与patch60字段对齐、源文件SHA复验；输出11108份原始JSON及gzip、两个索引、MIGRATION_QA和每股合格数。随后独立代理需遍历所有节点核验不可变字段，重数新空格/脱离空格、逐曲线counts及版本SHA，确认5554不缩/2343会员恰好/旧源SHA无变。不要将内部断言等同独立审计或发布许可。
