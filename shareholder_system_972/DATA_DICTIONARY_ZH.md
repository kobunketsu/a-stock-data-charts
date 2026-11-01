# 972版矩阵数据字典

`holder_matrix_4bins/curves_ui.json` 为网页数据（收益小数保留7位）；`curves.json` 为完整精度。根对象的metadata记录版本、股票池规则、样本及方法，rows/columns是有序分类，curves共128条（两个起点各64格）。

每条曲线：
- anchor：public_nextopen＝披露后下一市场交易日开盘；stat_close＝统计日收盘、休市向前映射。
- row_id：decline_over30、decline_2、decline_1、decline_0、rise_0、rise_1、rise_2、rise_over30，按股东变化带符号从小到大。
- column_id：down_3、down_2、down_1、down_0、up_0、up_1、up_2、up_3，按此前60日价格变化带符号从小到大。0/1/2/3分别对应0—10%、10—20%、20—40%、40—80%。
- count_events / count_stocks：固定事件数 / 不重复股票数；small_sample表示事件<50或股票<10，empty表示无记录。
- mean / median：收益均值 / 中位数；positive_fraction：收益严格大于0的比例；p10/p90：事件收益的10%/90%分位数，不是置信区间。

五个数组长度均为251，下标为起点后市场交易日0—250；收益是小数，显示百分比乘100。第0日收益归零，非空格positive_fraction[0]为0。空格为null而非0。

CSV：
- daily.csv：一格一天一行，h为市场交易日，统计字段含义同JSON。
- selected_horizons.csv：0/1/3/5/10/20/40/60/120/250日摘录。
- cell_counts.csv：每格的事件/股票计数及标记。
- event_membership.csv：anchor、row_id、column_id、event_id；用event_id连接重建后的statdate_only/event_panel_statdate.csv。
- price_special_counts.csv：价格恰好不变、上涨至少80%、下跌至少80%的格外统计。

重建生成statdate_only/daily_paths_statdate.npz：event_id对应事件表行序，public_nextopen_returns和stat_returns两个数组每列对应0—250日。文件大，省略分发但可以从977个冻结输入重建。model/event_panel.csv是同一事件表的兼容副本。

股东0变化、价格0变化与绝对价格变化≥80%不归入普通格子；端点容差1e-12，股东恰好30%保留在15—30%，详细定义见metadata和方法说明。
