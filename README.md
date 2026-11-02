# a-stock-data-charts

A股股东人数与股价研究系统。最新版本 **UP80：1494股研究池、5554股单股查询、5个前置观察期、双起点各81格**。数据截止2026-10-30，为冻结历史研究，非实时行情。

## 查看完整网页

克隆仓库或下载GitHub项目ZIP后，在仓库根目录运行：

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory releases/up80/sites/shareholder-matrix/dist
```

打开 <http://127.0.0.1:8000>。网页按需读取单股gzip文件，请通过本机HTTP服务使用。5个前置市场交易日观察期为10、20、30、60、120；两种起点均提供81格、均值和中位数双曲线、分位带、单股查询及键盘导航。横纵区间从有符号负值到正值排列，新增此前股价上涨≥80%列；默认后续20个交易日。颜色为红正绿负，低样本保留提示。

## 源码与数据目录

| 路径 | 内容 |
| --- | --- |
| `releases/up80/sites/shareholder-matrix/` | 可编辑网页脚本、样式、静态查询数据、测试与fixtures |
| `releases/up80/up80_recovery/research/` | 研究源码、15份矩阵JSON、特征与成员CSV、审计结果 |
| `releases/up80/up80_recovery/offline_rebuild/` | 离线编排入口、依赖版本和复现说明 |
| `releases/up80/shareholder_query_up80/` | 5554股查询快照迁移源码及数据合同 |
| `releases/up80/positive80_audit/` | 独立审计源码、旧8列回归与新增区间审计 |
| `datasets/up80/inputs/` | 原12份输入ZIP：冻结原始输入与历史发布快照，约453.3MiB |
| `scripts/restore_up80.py` | 离线安全还原、包及逐文件SHA校验；拒绝覆盖不同文件 |
| `releases/up80/*MANIFEST.jsonl`、`*PARTS.json` | 原交付SHA、源SHA、包结构及净化记录 |
| `shareholder_system_972/`、`shareholder_system_972_web/` | 保留的旧972版项目，勿与UP80混用 |

源码、网页和结果以普通文件保存，冻结研究输入及作为迁移依据的历史快照保持分包。临时NPZ与重复事件面板由重建生成，不提交Git。Git保留原始行尾字节，以保护冻结SHA。

## 还原与离线重建

需要Python及NumPy 2.3.5、Pandas 2.2.3。云端已验证环境为Python 3.12.14/x86_64；本机Mac ARM/Python 3.13.1完整运行在10日窗口旧8列回归处停止：第36日正收益占比有2个值超出既有容忍，最大差约0.000114758，不能称该环境已完整复现。详见[Mac验证记录](releases/up80/validation/MAC_REBUILD_COMPARISON.json)。正式发布结果未改；完整复建已验证环境为云端Python 3.12.14/x86_64。依赖已存在时，以下过程全部离线，无运行时自动安装：

```bash
# 仅核对输入分包SHA和清单，不写文件
python3 scripts/restore_up80.py --check-only
# 在releases/up80还原全部冻结输入；保留已存在且SHA一致的文件
python3 scripts/restore_up80.py
# 再核对17,329个已还原输入的精确SHA
python3 scripts/restore_up80.py --verify-restored
# 检查输入并显示重建计划，不执行计算
python3 releases/up80/up80_recovery/offline_rebuild/run_offline.py --package-root releases/up80 --work-root work/up80_rebuild
# 工作目录必须全新或为空；显式执行完整重建
python3 releases/up80/up80_recovery/offline_rebuild/run_offline.py --package-root releases/up80 --work-root work/up80_rebuild --execute
```

如需安装依赖，可自行创建虚拟环境并安装 `releases/up80/up80_recovery/offline_rebuild/requirements.txt`。安装与冻结输入的离线重建为两步，脚本不自动联网。重建只写独立工作目录，不覆盖发布数据、不交易或部署。运行前预留ZIP、约1.99GB解压输入与结果、独立重建目录及系统余量；云端每10秒采样的工作目录峰值约4.95GB，不能当作其他机器瞬时峰值保证。

还原工具允许通过 `--destination` 指定独立目录；若修改目的地，请同时将最终源码与结果目录结构置于该包根目录，再给重建入口传入对应 `--package-root`。不要把输入包还原到旧972目录。

[详细重建说明](releases/up80/up80_recovery/offline_rebuild/README.md) · [输入说明](releases/up80/README_完整输入存档.md) · [源码与结果说明](releases/up80/README_代码结果与离线使用.md) · [旧972版说明](docs/archive/README_972.md)

## 真实复现范围与读图口径

- **1494股研究**：可从冻结的全历史股东记录、真实行情和市场交易日历重建观测、前置特征及0–250日未来路径，再逐事件重聚合。5个前置观察期各自按实际窗口准入，新增上涨≥80%列来自真实聚合。
- **5554股查询**：从冻结的已发布base查询和5N补丁迁移新增区间及参考统计；旧4060只池外查询股的全部原供应商响应未保留，不能宣称从全部5554股原始抓取源端到端重生。查询股票池大于研究池，不代表这些股票都参与训练统计。
- 公布后模式使用公布后首个市场交易日开盘；统计日模式含事后信息，当时股东人数通常尚未公布，不是可交易信号。供应商公布日未逐条对照首次公开原文核验。
- 全样本参考是历史研究关系，不是严格逐时点的样本外预测。同股可重复且观察期重叠，不是组合净值；选池、存续与完整观察期筛选存在偏差。未计费用、滑点和成交限制，不保证预测或未来收益，不据此推断特定资金意图。
- 输入SHA、成员、日期、分组、计数及缺失位置须精确一致；聚合浮点既有比较标准为绝对误差1e-12、相对0。文件SHA差异单独记录，不以数值容忍冒充逐字节一致。原全1494旧逐事件档不可得，旧15曲线回归通过不等于已逐成员证明旧1494完全相同。

## 来源、许可与发布记录

[第三方来源与权利说明](releases/up80/up80_recovery/SOURCES_AND_RIGHTS_ZH.md)和原AKShare许可证保留。行情及股东数据权利归其权利人；本仓库没有为第三方数据新增开源许可或商业转售授权。

输入和结果使用各自独立SHA清单；路径净化前源SHA与包内SHA分别记录，源码冻结清单保留历史验收对应版本。历史中断/拒绝记录属于来源证据，不表示当前仍缺输入，也不改写其发生经过。

本公开仓库不包含凭据、个人笔记、持仓或部署身份。网页不包含线上站点的访问控制。同步不启用GitHub Pages，不创建自动刷新或交易任务。UP80最终验收及本机结果见版本目录的验收记录；原交付文档中的已验证环境与范围应结合对应记录阅读。
