# a-stock-data-charts

A股股东人数与股价研究系统。最新已审版本：**2343股研究池、5554股单股查询、5个前置观察期、双起点各81格**。行情冻结至2026-10-30，选池元数据截至2026-10-31，非实时行情。

## 最短网页启动

下载完整项目或克隆后，在仓库根目录运行：

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory releases/2343/sites/shareholder-matrix/dist
```

浏览器打开 <http://127.0.0.1:8000>。需本机HTTP服务以按需读取单股gzip，不能用file方式保证完整查询。

参考研究池2343股；查询范围仍5554股。此前观察期N为10/20/30/60/120个市场交易日。新增曲线显示长度L六档10/20/30/60/120/250（默认250），同步矩阵小图、详情和单股；**L只裁剪显示，不改变样本或数据**。后续收益观察日h默认20，与L独立。保留双曲线、分位灰带、红正绿负、样本提示、键盘导航和缩放。前端基于冻结commit `702b6a8c47f714eb2bb67f079d313f4c02f7fb51`，已同步界面修复版 `4abf0fd20ca341ce9ea4bcb03eac113eb91008d8`：81格走势图统一220px高；悬停或键盘聚焦时，底部显示竖线当前收益日 h 的p90[h]/p10[h]，移出恢复样本数。缺失分位值显示“暂无区间”，低样本提示保留。该修复不改变研究或查询数据；[界面验证](releases/2343/sites/shareholder-matrix/QA_CURRENT.md)与[补丁SHA清单](releases/2343/validation/ui_cell_footer/PATCH_MANIFEST.json)可核验。

## 可维护源码和三组完整冻结依赖

| 路径 | 内容 |
| --- | --- |
| `releases/2343/shareholder_model_2343/` | 研究源码、131窗选池程序、名单、方法、15份冻结研究JSON及独立审计 |
| `releases/2343/sites/shareholder-matrix/` | 可编辑网页、11108份查询gzip、2索引、fixtures与12项自检 |
| `releases/2343/validation/acceptance/` | 实际独立解包重建和输出比较的最终验收 |
| `datasets/up80/inputs/`、`code_results/`、`acceptance/` | UP80原19份输入、代码/结果及验收ZIP，字节保留 |
| `datasets/2343/capture/` | 新增849股原始full/因子/CSV/股东页及SHA，14份完整ZIP |
| `datasets/2343/selector/` | 完整2015Oct–2026Oct选池源：14段839页416286条及131窗独立审计 |
| `datasets/2343/DEPENDENCY_LOCATIONS.json` | 全部34份只读依赖的仓库路径、大小与SHA |
| `datasets/2343/source_archives/` | 原始CORE ZIP，保留精确来源；网页和源码正常展开可编辑 |
| `scripts/restore_2343_dependencies.py` | 全离线安全还原；先校验全部ZIP/路径/已有文件，拒绝覆盖不同内容 |
| `releases/up80/`与旧972目录 | 历史版本保留，不与新版混用 |

依赖可以从本仓库完整恢复，不能只用代码或网页均值代替。原始34ZIP不可变；临时canonical面板和NPZ由重建生成，留在独立work目录，不提交Git。

## 完整离线重建

已验证云端环境为Python3.12.14/x86_64、NumPy2.3.5、pandas2.2.3；依赖见新版requirements.txt。没有自动联网安装、抓取、交易或部署。先准备匹配环境，再执行：

```bash
# 仓库根目录：仅校验34依赖包SHA与安全路径，不解压、不计算
python3 scripts/restore_2343_dependencies.py --check-only
# 还原到独立工作目录，保留源码目录与冻结ZIP
python3 scripts/restore_2343_dependencies.py --destination work/2343_inputs
# 先重建旧1494基线（已有完整只读基线可直接使用）
python3 work/2343_inputs/old_up80/up80_recovery/offline_rebuild/run_offline.py --package-root work/2343_inputs/old_up80 --work-root work/up80_reference --execute
# 再重现131窗选池、2343研究、旧1494保全与5554查询迁移
python3 releases/2343/shareholder_model_2343/repro_bundle/rebuild_incremental.py --bundle-root releases/2343/shareholder_model_2343 --old-root work/up80_reference/research --capture-export-root work/2343_inputs/new849_capture --screening-root work/2343_inputs/complete_selector/shareholder_pool_screening_multiyear --baseline work/2343_inputs/old_up80/positive80_audit/baseline --baseline60 work/2343_inputs/old_up80/positive80_audit/baseline60 --old-query-base work/up80_reference/query_output/single_stock --old-query-patch work/up80_reference/query_output/lookback_patch --work-root work/2343_rebuild --execute
```

省略新版入口的`--execute`仅检查/显示计划。工作目录必须全新或为空，原输入保持只读。可按原入口使用`--research-only`，研究通过后`--resume-query-only`继续；不能跳过回归。

云端已从实际独立ZIP解包完成研究与查询两阶段执行：131窗精确重现2343集合，15研究JSON、15CSV、15路径数组、11108查询gzip和2索引精确一致，未忽略metadata。研究约870.68秒、查询约109秒；最终工作目录约7.03GiB，不含只读输入、旧基线和临时开销，不能作为所有平台峰值保证。

**本机没有重跑新全模型。** Mac ARM/Python3.13只做语法、清单、还原小测试和UI自检；旧UP80在该环境的零收益边界差异继续保留于旧验证记录，不保证新全链逐位一致，也不放宽数学阈值。请预留显著多于工作目录数值的磁盘空间。

[原增量运行说明](releases/2343/shareholder_model_2343/README_INCREMENTAL.md) · [最终验收](releases/2343/validation/acceptance/验收说明.md) · [UP80历史说明](docs/archive/README_UP80.md)

## 研究口径与复现边界

- 2343为2015-10至2026-10的131个三自然月窗口中至少一次满足原月频规则的并集，并非始终月频。默认N60完整样本为125732条/2139股。旧1494的canonical事件、54字段及双251路径保全；新1620格×251日×5统计及136080分期统计经独立核验。
- 1494旧研究从原19包冻结输入重建；新增849完整原始行情、因子和股东来源可恢复。三组输入均参与可搬运重建，选池不能只靠最终名单冒充复现。
- 5554查询采用冻结已发布base及5N快照迁移参考统计，并非全部5554原始供应商响应端到端重生。查询覆盖大于参考研究池，不等于每股都参与训练。
- 公布后模式与统计日模式必须区分；统计日起点含事后信息，当时股东人数通常尚未公开，不作可交易信号。供应商公布日期未逐条原文核验首次公开时间。
- 近期名册、回溯选池、存续及完整250日选择存在偏差；同股重复与观察期重叠，不是组合净值。未计费用、滑点和成交限制，不保证因果、稳定性或预测收益。

## 来源、许可与发布说明

第三方原始数据权利归来源权利人，不因入库获得本项目开源或商业转售许可。旧来源说明、AKShare解码器许可证、原始请求URL/时间/SHA、停止和恢复证据均保留。私人日志不入库；来源包中需要保全的日志采用脱敏文本及双SHA。

CORE有两份仅大小写不同的静态审计文件名。为兼容Mac，仅将小写独立报告改名为`independent_old1494_preservation.json`，原内容SHA不变；原manifest、原CORE ZIP和映射记录保留，算法与数值未改。历史准备/pending文案表示当时状态，最终结论以新版validation最终PASS为准。

本轮不改变在线站点、仓库可见性、Pages、账号、网络或安全设置；仓库不含凭据或部署身份。本地静态网页不继承在线私有访问控制。
