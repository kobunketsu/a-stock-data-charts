# 2343研究与全A查询：增量离线重建

本增量包提供最终研究源码、131窗选池复现脚本、名单与方法、15份冻结研究JSON、查询最终哈希、独立审计以及便携入口。其数据依赖明确为三类，不重复携带历史输入或巨大可再生NPZ：

1. 冻结UP80旧1494：原19包；固定代码/结果Git基线为27b66ee。首次使用先按旧包入口重建，取得含canonical、五窗口面板/251日NPZ的old-root。只有Git代码而缺原输入不能凭空重造这些数据。
2. 新增849：14份完整capture ZIP，逐文件SHA由CAPTURE_EXPORT_MANIFEST核验。
3. 全市场选池元数据：SHAREHOLDER_MULTYEAR_MAC_COMPLETE_201510_202610.zip（27160835字节，SHA27f8a49a497a25a90bc29704b201c584b5116876c0167804d6d2bc5cf0f30783），14段839页416286行，完整131个滚动三月窗。不提供此源只能验证固定名单模型，不能宣称全选池复现。

完整逐包SHA/大小见repro_bundle/INPUT_DEPENDENCIES.json。此包以分别已交付的冻结依赖为前提，原19包、新14包和筛选原ZIP一字不改。

## 命令

进入任意工作目录执行；work必须新空目录。无网络请求，三inputroots保持只读。默认只显示计划，--execute才计算。

```sh
python3 /path/to/incremental/shareholder_model_2343/repro_bundle/rebuild_incremental.py \
 --bundle-root /path/to/incremental/shareholder_model_2343 \
 --old-root /path/to/rebuilt-up80/research \
 --capture-export-root /path/to/extracted849 \
 --screening-root /path/to/full-screening/shareholder_pool_screening_multiyear \
 --baseline /path/to/up80-package/positive80_audit/baseline \
 --baseline60 /path/to/up80-package/positive80_audit/baseline60 \
 --old-query-base /path/to/up80-query/single_stock \
 --old-query-patch /path/to/up80-query/lookback_patch \
 --work-root /path/to/new-empty-work --execute
```

入口先重现131窗2343集合，再merge→assemble→完整模型→旧1494canonical/双251路径/全部81格/分期/非重叠保全→15研究文件精确SHA→新5554查询引用迁移→11108gzip、2索引、逐股资格哈希比较。查询基础5554快照不等于全部5554原始供应商响应已恢复。

分阶段执行可用--research-only；该阶段成功后以同一参数和--resume-query-only继续既有work。这不是允许跳过研究回归；必须已有回归证据且15结果仍精确匹配独立审计的冻结结果。

仅工作副本会参数化baseline路径，源码前后SHA及改动原因均记录；不更改原pipeline和输入。附带的源码净化与阶段入口文案改动另有SHA说明，不冒称与原始源码完全相同。

云端环境Python3.12.14/numpy2.3.5/pandas2.2.3；本次跨目录实际重建证据随后作为独立侧包交付。Mac ARM/Python3.13完整研究计算尚未验证。长期筛选、更多股票或历史不保证统计关系稳定，也不提供因果或投资收益保证。

配套UI源码/静态站快照另分UI_DATA/UI_META ZIP，commit702b6a8c47f714eb2bb67f079d313f4c02f7fb51。新增六档显示长度仅裁剪展示；不改研究数据/样本。静态站需本地HTTP服务打开，不能将部署私有链接/平台配置当作运行依赖。
