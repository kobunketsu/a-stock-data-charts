# a-stock-data-charts
A stock data charts project

## 972股研究系统

本仓库保存已交付的 **972股最新版完整项目**：离线网页、分析源码、冻结计算输入、统计结果和原始抓取证据。版本为 `monthly972-holder4-price4-20261101`，不与旧453股交付包混用。

### 查看网页

克隆仓库或从 GitHub 的 Code → Download ZIP 下载并解压，打开 [`shareholder_system_972_web/打开系统.html`](../../shareholder_system_972_web/打开系统.html)。请保留整个网页目录。若浏览器限制本地文件脚本，可在仓库根目录运行：

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory shareholder_system_972_web/dist
```

然后打开 <http://127.0.0.1:8000>。网页无需Python依赖或网络数据接口。

界面提供两种起点、各64格，股东人数和此前股价均按有符号变化从小到大排列；默认后续第20个交易日，曲线覆盖0–250日。红色为正收益、绿色为负收益，低样本仍着色并保留提醒；默认各小图独立纵轴并标注实际极值。

### 项目结构

| 路径 | 内容 |
| --- | --- |
| `shareholder_system_972_web/` | 可独立打开的网页、内嵌数据、界面自检、网页SHA清单 |
| `shareholder_system_972/` | 分析脚本、方法、字段字典、统计与审计结果 |
| `shareholder_system_972/prices/` | 972只股票冻结复权日行情 |
| `shareholder_system_972/holders/`、`holders_baseline_2019/` | 主期及2019基线的合并原始股东记录 |
| `shareholder_system_972/absolute_only/trading_calendar.csv` | 仅日期的市场交易日历 |
| `shareholder_system_972/holder_matrix_4bins/` | 双起点矩阵、完整精度统计、成员、构建和独立审计脚本 |
| `shareholder_system_972/source_provenance/` | 原始接口快照、行情与复权因子、选池证据、历史来源脚本 |
| `PUBLICATION_NOTES.json` | 公开副本路径脱敏记录；数据与矩阵算法未变 |
| `VALIDATION.json` | 本次同步前的本地验证结果 |

原9个普通ZIP已合并为3,325个可直接维护的文件；仓库无需再次合包，也不重复保存ZIP。项目约473MB，克隆时需要下载公开研究数据。

### 从冻结输入完整重算

需要Python 3.11或更高版本（建议3.12）、至少4GB可用内存及2GB空闲磁盘。在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r shareholder_system_972/requirements.txt
python shareholder_system_972/rebuild_system.py --check-inputs
python shareholder_system_972/rebuild_system.py
```

入口先验证977个冻结输入、4个计算脚本和配套元数据SHA，再执行原始股东CSV清洗、双起点事件路径、矩阵计算及128格独立审计。四个发布输出必须逐字节匹配 `release_reference.json`，结果写入 `rebuild_result.json`。派生事件面板和NPZ可再生，已通过 `.gitignore` 排除。

本次在macOS ARM64、Python 3.13.1上完整重算并通过128格独立审计。160,640个曲线统计值中仅1个均值与原Python 3.12发布结果相差约8.7×10⁻¹⁹：网页JSON和成员文件SHA完全一致，完整精度JSON与CSV因该末位差异未通过严格SHA。入口按设计停止，未更新网页。仓库保留原版统计文件，详细证据见 `VALIDATION.json`；不同运行环境不保证完整精度文件逐字节一致。

重算后如需更新本地网页的数据：

```bash
python shareholder_system_972/rebuild_system.py --web-dir shareholder_system_972_web/dist
```

只有发布SHA全部一致才会更新本地网页数据。此操作不修改在线站点。

使用Node.js运行随包网页自检：

```bash
cd shareholder_system_972_web
node --check dist/app.js
node --check dist/data.js
node verify.cjs
node verify-colors.cjs
```

详细说明见[研究系统README](../../shareholder_system_972/README_972_ZH.md)、[选池方法](../../shareholder_system_972/METHOD_MONTHLY972_ZH.md)和[字段字典](../../shareholder_system_972/DATA_DICTIONARY_ZH.md)。历史抓取脚本仅供来源审阅，其旧路径已替换为通用 `historical-capture/` 占位目录，不是默认重算入口，运行前需自行配置目录和检查外部接口。

### 数据口径与限制

- 股票池按2026-08-01至2026-10-31有效披露筛选：先排除负披露滞后，再要求至少3次、首末跨度至少60自然日、平均间隔不超过30天、最近披露距窗口末不超过30天。平均频率不代表每次间隔都在30天内。
- 最终池972只＝旧池保留452只＋新增520只；有效事件覆盖971只/89,957条。共同完整250日且股东变化非零样本907只/61,074条；含不变为908只/62,221条。两起点主格分别60,075与60,019条，每图14个低样本格（含1个空格）。
- 公布后模式使用数据商记载公布日之后首个市场交易日开盘；统计日模式使用统计日收盘，属于事后观察，当时股东人数通常未公布，不能作可交易信号。
- 股价前置窗口为60个市场交易日，收益为相对起点的绝对收益，不扣大盘指数。每次披露等权，同股可重复且观察期重叠，不是组合净值。
- 近期选池回溯和完整250日筛选存在选择偏差；未计费用、滑点及成交限制。796只行情跨度至少5年，另176只不足5年，未验证均为新上市。旧回归预测器未重新训练。
- 数据是冻结快照，无实时行情、自动刷新或交易功能；默认重算不联网重新抓取。外部接口及历史修订可能导致重新下载不一致。

### 来源、许可与公开范围

保留原数据来源清单、解码器归属和[AKShare许可证](../../shareholder_system_972/AKSHARE_LICENSE.txt)。第三方行情与股东数据的权利归其权利人；本仓库没有为这些数据新增开源许可或商业转售授权。历史来源脚本和证据中保留候选982/新增529等采集批次名，以最终 `qualified_972.csv` 和 `POOL_METHOD.json` 为准。

本次同步仅含交付项目和公开股票市场数据，不含凭据、账户部署配置或个人持仓。离线网页不继承在线站点的登录保护。本仓库同步不启用GitHub Pages，也不修改原在线网站。
