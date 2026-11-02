# 新增849股股东历史合并（仅离线程序，尚未运行）

等待Mac返回所有18组完整CAPTURE_COMPLETE及原页；缺组、缺页、SHA不符均禁止合并。

从任意目录运行，参数均为真实本地路径：

```bash
python3 /path/to/shareholder_model_2343/pipeline/merge_added_holders.py \
  --old-root /path/to/up80_recovery/research \
  --capture-root /path/to/shareholder_model_2343/capture_handoff/holders \
  --output-root /path/to/shareholder_model_2343
```

输出holders/events_raw.csv、holders_baseline_2009/events_raw.csv、HOLDER_MERGE_AUDIT.json、HOLDER_RECOVERY_AUDIT.json和holder_merge_audit下的逐项证据。不会覆盖已存在的主CSV。旧1494的名册、主表、基线先对FROZEN1494_INPUT_SHA.json精确校验，原CSV整个字节串作为输出前缀保留，追加849新记录；不使用新筛选快照替换旧1494的任何记录，包括曾有差异的28条。

1. 复用849的69054条2015Oct–2026Oct DET元数据，核gzip与解压数据双SHA。
2. 增加2009–2015Sep DET；增加F102009–2026原始捕获用于补缺。18组manifest、每页SHA/条数/页序及末probeSHA必核。
3. 按(code,统计日)优先全部DET；F10只补缺端点。相同端点人数或公布日期冲突保留DET，逐条写冲突证据，不静默修订。
4. F10只用HOLDER_A_NUM；缺失/非正A隔离，绝不用HOLDER_TOTAL_NUM回填。无法解析日期或统计日晚于公布日隔离。所有原F10仍留捕获文件。
5. 复用5列DET和F10的TOTAL_A_SHARES未知留空，不由平均持股数反推。已有旧1494所有原字段与来源不改变。
6. 新行保留SOURCE_TABLE/SOURCE_NOTICE_FIELD/SOURCE_HOLDER_FIELD/SOURCE_NOTICE_VERIFICATION；供应商公布日不是逐条核验首次公开时间。

当前只有标准库语法检查；未运行实际合并，更未运行模型或网络。完整数据返回后由独立审计核2343输入、冻结1494字节前缀、差异和隔离，再允许模型计算。本脚本与已经冻结的采集目录分开，未修改首发Mac采集包。

HOLDER_RECOVERY_AUDIT的complete仅表示完整holder输入合并完成，independent_audit_status仍pending；价格/日历完整性不在该字段中，不输出或伪填INPUT_COMPLETENESS。
