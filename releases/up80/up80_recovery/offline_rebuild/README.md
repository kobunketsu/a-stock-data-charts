# 离线重建入口（云端完整复建已验证）

本入口只编排本地文件，不抓取网络、不启动浏览器、不部署、不推送 GitHub。本入口已在新的独立空目录完整执行，研究重建及5,554股查询迁移均完成，并与正式数据逐值比较通过。本测试证明当前云端环境可复建，不代替研究独立审计或发布授权。

## 使用

当前云端环境：Python 3.12.14、numpy 2.3.5、pandas 2.2.3。依赖锁定见 requirements.txt。Mac Python 3.13 / ARM 尚未验证，不应称为已测试支持环境。不要在运行时自动联网安装依赖。

```bash
# 默认仅检查基本输入并打印命令，不生成模型
python up80_recovery/offline_rebuild/run_offline.py \
  --package-root /path/to/package --work-root /path/to/new-empty-rebuild
# 完成最终审计和资源检查后，显式启动本地计算
python up80_recovery/offline_rebuild/run_offline.py \
  --package-root /path/to/package --work-root /path/to/new-empty-rebuild --execute
```

`--package-root` 默认根据入口脚本所在位置推导，不依赖旧 shared 或个人工作区绝对路径。工作目录必须为空；原包不写入。`--baseline`、`--baseline60`、`--query-base`、`--query-patch` 可明确指定其他只读输入位置。聚合器虽然带旧路径默认值，入口始终显式传入两个 baseline 参数，不使用旧默认。

## 必要输入布局

保留以下相对结构；最终交付必须提供完整输入哈希清单，不可仅打包脚本或曲线均值。

- `up80_recovery/qualified_1494.csv`：冻结训练名单。
- `up80_recovery/archive972/shareholder_system_972/`：`qualified_972.csv`、`holders/events_raw.csv`、`holders_baseline_2019/events_raw.csv`。原归档含候选982记录，合并时按972名单过滤。
- `up80_recovery/research/holder_capture/`：完整343个源页、`CAPTURE_MANIFEST.json`、全部合并原始JSON、`RESUME_FROZEN_PAGES.json`、`RESUME_COMPLETE_QA.json`、`CAPTURE_CHECKPOINT.json` 和校验脚本。旧 incomplete checkpoint 是历史证据；不能代替新 complete manifest。
- `up80_recovery/research/prices/`：全部1494股原价CSV，不能用972股或部分价格代替。
- `up80_recovery/research/absolute_only/trading_calendar.csv`：冻结市场交易日历，非指数收益。
- `up80_recovery/research/qualified_pool.csv` 及 `ARCHIVE_EXTRA_CODES.csv`、`ARCHIVE_EXTRA_CODES_COMPARISON.csv`。
- `positive80_audit/baseline/prior/{10,20,30,120}/{all,recent,stability}.json` 和 `positive80_audit/baseline60/{all,recent,stability}.json`：旧15份冻结统计及schema，**不作为新增尾部收益来源**。
- `positive80_audit/baseline/single_stock/` 与 `single_stock_patch/`：各5,554股完整index和每股原始JSON/gzip。不可用只有代码名单的占位文件替代。

## 源码和阶段

1. `holder_capture/verify_resume_complete.py`：逐页SHA、完整页序、原216页字节不变。
2. `merge_recovered_holders.py`：只接受完整manifest。冻结旧972的2019+原值；DET端点优先，F10只补缺端点且只用A人数，缺A不回填TOTAL。
3. `audit_holder_merge_local.py`：旧972全部原字段精确核对，F10无冲突、无TOTAL回填。
4. `build_superset.py` + `clean_holders.py`：重建全部合法观测、完整双起点251日路径，保留独立的新鲜度准入。
5. `lookback_pipeline/prepare_lookback_panels.py`：重建10/20/30/60/120市场日特征，各自零基行情序号>=N，不能用旧60成员充当其他窗口。
6. `lookback_pipeline/aggregate.py`：逐窗口实际事件重聚合81格、全历史/2020后/分期/股票等权/非重叠，旧8列回归须PASS。入口显式循环五次，不依赖带环境默认值的`run_aggregate_all.py`；该原脚本保留作来源参考。
7. `shareholder_query_up80/migrate_up80.py`：读取新矩阵引用，迁移冻结5,554股查询节点；不重算原价格、日期、户数或已有此前收益；训练池仍1494股。

输出 `prior/{N}/{all,recent,stability}.json`、`query_output/`、`logs/` 和 `OFFLINE_RUN.json`。阶段失败立即退出。即使内部回归通过，状态仍为 `pending_independent_audit`，不是可发布许可。

## 核验与限制

已恢复holder主表241,976行、2009基线1,465行；冻结972原值137,345行。原全1494逐事件档未保留，恢复后计数一致不等于逐成员已证明相同，须通过旧15份曲线回归及独立审计评估。股东公布日期仍是供应商字段，不应宣称逐条核验首次公开时间。统计日起点含事后信息，不可冒称可交易信号。

此版本不创建大ZIP。最终冻结后，另生成源代码、必要输入、15矩阵、查询输出及独立审计报告的相对路径SHA清单，再由主代理统一决定归档或发布。

## 重建能力的边界

1494股研究：从本包冻结股东记录、实际价格和交易日历重新计算观测、特征与未来路径，再逐事件聚合。

5554股查询：本轮仅从冻结已发布的 base 查询数据和五窗口补丁迁移新增>=80%引用；并非从5554股原始供应商响应重新生成。旧4060新增查询股票的全部原供应商响应不在此次恢复输入中，因此不能声称具备全5554股原始源端到端复造能力。原实际价格/户数/日期/特征均由冻结查询快照保留。

## 本次完整实测结果

2026-11-02 云端 Python 3.12.14：完整重建耗时530.56秒（约8分51秒，含迁移；后续独立逐值比较约半分钟）。工作目录每10秒采样的占用峰值4,952,297,472字节（约4.61 GiB），不含原输入包，不声称瞬时全系统磁盘峰值。预留更多空间用于输入包、解压和临时文件。

15份矩阵JSON、15份panel/feature/membership CSV均与正式版本字节一致；5组NPZ的15个数组精确一致（NaN位置一致）；两套各5554股gzip全部字节一致，索引所有字段及逐股资格结果一致。没有忽略metadata、路径或SHA差异。关键暂存输入1839文件全部字节一致。详细结果见 `VALIDATED_REBUILD.json`，完整测试报告由交付清单引用。

首次计时命令因系统无 `/usr/bin/time` 在运行入口前退出；改用Python测量器后一次完整复建成功，无重建算法修补，无网络调用。Mac Python3.13/ARM仍未测试。
