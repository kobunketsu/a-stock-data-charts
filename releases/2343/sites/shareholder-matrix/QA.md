# 验证记录
- 数据版本 holder3-price4-20261101T172350Z；最终 6×8×2，96 条聚合曲线。
- `node verify.cjs` 通过：251 日长度、有限数值、0 日基准、分位排序、小样本标记、主矩阵与排除项总数。
- `node --check dist/app.js` 通过。
- 通过 Sites managed preview + cua_repl 实测：48 个格子；起点、均值/中位数、250 日、37 日自选、点格选择、小样本提示、分位分布显示、加入/清空对照。
- 同一时长和统计量切换起点，色阶文本完全相同。
- 完整桌面截图人工检查：标题、矩阵、曲线、统计与限制排版正常。
- 移动端使用680px响应式单列控制与横向矩阵滚动；本次浏览器未提供视口调整能力，未声称真实手机/独立Mac设备实测。
- 控制台所见错误均来自浏览器扩展 content-script.bundle.js，非本页面脚本。
- Site get_site 已核验仅owner Wenjie，custom，无其他人或组，0外部访客。
- 静态、无外部CDN、无后端、无原始个股明细；仅冻结聚合数据。

## 48格走势图更新
- 默认视图改为48个内嵌SVG，0–250日完整曲线，不需点击。
- 默认全格统一纵轴，由两个起点全部251日所选统计量决定；均值与中位数分别实测切换起点刻度完全相同。
- 浏览器实测：48 SVG；第0日48格均为0.00%；第250日、均值/中位数、双起点、独立刻度警示、色块视图切换和点格放大均通过。
- 样本不足曲线灰色虚线，仍显示真实收益和计数；不隐去极值。
- 全页截图显示8列全部可见，行列标签完整；手机仍为横向滚动。

## 64格精简更新
- 最终数据 holder4-price4-20261101T174310Z，128条曲线，两起点各64格；原96曲线保持不变（数据方审计）。
- 顺序已浏览器核验：减少>30%、减少15%-30%、减少5%-15%、减少0%-5%、增加0%-5%、增加5%-15%、增加15%-30%、增加>30%。
- 简化表头和单格重复文本；0个小图SVG文字节点，坐标统一在表上说明，保留无记录和小样本标识。
- 每起点63个真实曲线SVG+1个无记录空格；空格null不变成0。0日其余63格0.00%；250日、均值/中位数、双起点、色块/曲线、空格点开均正常，0个NaN路径。
- 均值共同纵轴在起点切换前后文字完全一致；移除独立刻度入口，避免无格内标度时误读。
- 大于30%两行纳入，人数不变602条仍排除；主矩阵32398/32375，数值校验及排除项合计通过。
- 全页截图排版通过。权限再次确认仍仅owner、custom。

### 最终覆盖：用户要求各格撑满并标真实高低
- 默认改为各格独立自动撑满，保留统一刻度开关；全局警告只能直接比较形状。
- 每格高/低为所选统计量整条0–250日曲线实际极值，不是加留白的纵轴端点。
- 实测首格均值高15.03%、低-17.36%，与数据精确值15.03479%/-17.36413%一致；统计日起点增加>30%/上涨40%-80%中位数高0.12%、低-15.94%，与精确值0.11855%/-15.94045%一致。
- 空格没有极值文字或SVG；0和250日、统计量、起点及两种刻度切换通过，路径无NaN。
- 表头有符号简写，负区间使用明确分隔符“−30%～−15%”；完整含义保留全局说明、aria及title。

## 红涨绿跌更新
- 相对起点正收益红、负收益绿、0灰，过零位置线性插值精确分段，无clipPath ID冲突。
- 连续同号路径保持连接，均值实线与中位数虚线可分辨；低样本仍灰色虚线，计数和风险提示保留。
- 选中收益与实际高低数字按数值符号着色，非曲线斜率或高低排名。色块使用双起点共同对称色界，低样本与空格灰色。
- `verify-colors.cjs`通过：正负、过零、全0、空值、低样本。浏览器0日64个值中性色；正常曲线红绿段可见，低样本彩色曲线段为0。
- 均值/中位数、起点、时长、两种刻度和色块切换正常，实际极值数值未改变。
- 默认详情恢复decline_0/down_0（4,285条、390只），排序仍从decline_over30开始。
- 完整截图和详细曲线虚线截图已检查，字体与配色对比清晰。

## 默认20日与小样本同色
- 仅后续默认观察日改为20：初始状态、选择器、滑杆、摘要、各格选中值及详细曲线标记一致。此前价格分类仍为60市场交易日；完整0–250日曲线不变，60日选项保留。
- 小样本与普通样本同样红正绿负及相同色深规则；去掉灰底/灰线/灰斜纹覆盖，保留记录数、小样本标记及虚线。
- 浏览器默认常见组20日均值+1.74%、中位数+0.53%，与数据0.0173749/0.0052632一致。
- 小样本19段红/13段绿、灰色曲线段0；小样本详情红绿均正确，空格仍“无记录”。0日64个数值中性，20/250日切换通过。
- JSON SHA256与冻结源完全相同：c26951520a2621a04e1db4580430287c2525291e5343288fdcdd778d593b2a0b。

## 横向股价有符号升序
- UI列顺序固定为down_3,down_2,down_1,down_0,up_0,up_1,up_2,up_3。
- 浏览器核验：−80%～−40%、−40%～−20%、−20%～−10%、−10%～0%、0%-10%、10%-20%、20%-40%、40%-80%；曲线/色块及双起点切换后顺序一致。
- 数据仍按row_id/column_id匹配，无位置索引错配；64格、空格、默认20日常见组1.74%/0.53%保持。
- 这是原453只股票池快照的展示排序更新，尚未替换扩大的股票池数据。

## 月频972候选池接入
- 数据版本monthly972-holder4-price4-20261101，SHA256 3ae5cdd9a23f101a122d121815594d7c5494a80ce0616f25bf948b5d2f0fb0d4。
- 独立审计全量128格×251日5统计量通过，parent及data agent明确放行后发布。
- 首页清楚显示：972候选池→971股/89957事件→两起点共同完整250日且人数非零61074条/907股；不将候选池规模当作实际样本股数。
- 方法显示2026-08-01至10-31、平均间隔≤30天、至少3次、跨度≥60天、最新≤30天；说明平均间隔并非每次间隔、日期有效记录、回溯选池选择偏差。
- 浏览器核验两起点主矩阵60075/60019，各64格、14低样本含1空格；排除数之和与61074基底相符。相同分组在两个起点成员可能变化已提示。
- 默认20日常见组7570条/793股，均值1.87%、中位数0.72%。0/250日、均值/中位数、起点、空格、列排序均通过，0个NaN路径。
- 全页截图确认候选池方法、样本漏斗、矩阵及统计均正常。

## 2026-11-02 单格增加中位数双线
- 所有非空小图同时显示平均收益实线、中位数虚线，两线红正绿负。低样本只保留文字计数，不再将均值改虚线。
- 每格自适应范围与全局统一范围均由mean+median共同确定；高/低为两条完整曲线合计实际极值。选择器明确仅控制格子数字、圆点、色块，不隐藏线。
- verify-dual.cjs检查63,252个有限值均包含在本格及全局范围；合成全零、全空、两线差异大样例通过。
- 浏览器两起点各63个均值组+63个中位数组；空格无曲线；低样本均值虚线路径0。切换统计量前后两条曲线路径完全相同；统一刻度跨起点相同；0/250/20日、空格详情通过，NaN路径0。
- 默认仍20日，常见格7570条793股、均值1.87%中位数0.72%；月频972数据SHA保持3ae5cdd9a23f101a122d121815594d7c5494a80ce0616f25bf948b5d2f0fb0d4。
- 完整截图检查双线与统一图例可读。未修改GitHub仓库，主代理另行同步。

## 2026-11-02 正向尾部拆分72格及标题互换
- 接入事件级重聚合并独立审计放行的monthly972-holder9rows-price8cols-20261102，SHA7b40b69524dfcad59fb199705876d760785b9a53fa920cfba8cfd3b51099ce1d。
- 正向>30拆为(30,100]与>100，30归原15–30，100归30–100，完整说明与aria保留；9行8列，下降4行不变。
- 左上角上方此前股价→、下方股东人数↓；仅互换文本上下位置，没有转置数据。
- 每起点72格；公开70对双线+2空格/23低样本，统计69对双线+3空格/22低样本。固定61074、907股未改变。
- 新行点击、详情、对照、起点、均值/中位数选择、统一/自适应、0/20/250日通过，NaN路径0；极值合并两线范围检查69778有限值通过。
- >100低样本保留提示、计数与红绿；空格无伪零。全页截图检查9行及顶部双线图例正常。

## 2026-11-02 Mac zoom / accessible fallback
- No keyboard, wheel or pinch handlers; no preventDefault; viewport has no user-scalable or maximum-scale restrictions. Browser-native shortcuts remain browser-owned, avoiding custom double zoom.
- Added accessible, separately labelled button-only page scale 50–200%, 100% default/reset. Toolbar remains unscaled. Percentage explicitly excludes browser-native scale.
- Browser QA: 125%, 200%, 50%, reset100%; endpoints disabled; 72 cells/70 nonempty paired SVG unchanged. 200% matrix remains overflow-x:auto, 1080px content /505px viewport, arrow scrolling moves scrollLeft; enlarged vector lines remain sharp in screenshot.
- Sent Meta+=, Meta+Shift+=, Meta+-, Meta+0 while horizon select focused: page scale and day20 unchanged, no duplicate custom action. Cloud Linux automation does NOT verify macOS browser chrome or ChatGPT host shortcut forwarding. Site cannot control keys intercepted by host; on-page controls are available fallback.
- verify-zoom.cjs checks bounded callbacks/reset plus absence of shortcut interception/viewport lock. Existing three data/dual-curve/color suites PASS; aggregate JSON unchanged.

## 2026-11-02 additional two smaller steps
- Minimum changed 50% → 40% → 30%; default/reset remain100%, maximum200%. Browser-native zoom remains untouched.
- Browser six minus clicks from100 reach30%, further minus disabled;72 cells/10 rows intact, matrix/table both1353 CSS px so no horizontal clipping. Reset returns100%; day20 unchanged.
- Screenshot: vector geometry retained; at30% text is naturally very small—use for overview and enlarge to read. Not claiming readable fine text at all display densities or changing host-native minimum.
- verify-zoom/data/dual suites PASS.

## 2026-11-02 audited historical expansion and stability panel
- Default full available history (actual2012 onward), optional exact frozen2020+ dataset. Data switches synchronously from bundled aggregate-only data.js (~4MB); no async race/stale fetch, comparison selections cleared on switch, current grid selection retained.
- Audited main JSON hashes: full935742def51a9f6f33fbded33751b651cd25e9e863e029f12246fce996d576b1;2020+7b40b69524dfcad59fb199705876d760785b9a53fa920cfba8cfd3b51099ce1d. Original aggregate JSON fixtures outside served dist, avoiding duplicate payloads. No event-level data.
- Full cohort75490/926; public grid74348/stat74299. Old61074/907 cohort and common7570-record cell20-day +1.87% mean/+0.72% median reproduced.
- Added current-cell four-period panel with event mean, event median, equal-stock mean;20/60/120/250 horizons; all_events or nonoverlapping250. Clearly independent of main history selector; period sample baselines and actual first/last dates shown. Includes annual raw/price-feature/final cohort coverage.
-2010/11 final0 and early194 events(193 April/1 May) warning explicit; more history does not guarantee stability; noCI/prediction.
- All five node suites PASS. verify-history checks both bundled objects vs audited fixtures (JSON numeric equivalence includes -0=0),1152 unique series, four horizons, null/small flags and counts.
- Browser: default72cells/fourperiod rows; full/recent switch counts/text/versions correct; compare cleared. stat_close/empty cell -> no data both detail and period, noNaN/undefined. Mean/median,sharedaxis,horizon0(all70 nonempty numeric0)/20/250, period20/60/120/250, nonoverlap switching passed. Positive/negative and low-sample values retain sign colors.30% zoom persists across both datasets and anchors;reset100%. Panel screenshot reviewed; wide table horizontal scroll. Mac native shortcut limitation unchanged.

## 2026-11-02 B23 final1494 expansion
- Owner-only access rechecked (sole Wenjie owner, zero external visitors/groups/editors).
- Replaced all/recent/stability with independently released final1494 aggregates; exact3 SHA verified by verify-history. Never deployed1294 intermediate. All972 retained+522; historical972 old data replaced, explanatory comparison retained.
- Screening dates2024-10-01..2026-10-31 (25months,23whole3month windows, union any passing window) explicitly separate from actual sample dates. Not continuous/current monthly qualification. Default actual2012..2025 cohort102238/1395;2020+82036/1370.
- Browser main public100667/stat100602;72cells,19small/1empty each. Early default publicdecline_0/down_0 has54events/51stocks and no false small badge. Early warning updated272(270April/2May), removed obsolete allcells-small claim.
- Browser range/anchor/sharedaxis/stat/horizon0(71validzeros)/250,emptydetail/nonoverlap250panel,smalltailcoloredlines,30%zoom+dataswitch/reset passed. NoNaN/undefined, counts/versions current, screenshot verified clear screening vs sample period. Existing dual/color/zoom/data tests and1152series integrity suite PASS.
- Coverage and dispersion improved but cross-period stability has no consistent improvement. No independence/CI/prediction claim. All served data aggregate-only.

## 2026-11-02 default p10–p90 distribution band
- Only functional edit: existing #band checkbox now checked by default. No localStorage/cached preferences exist. Explicit user toggle preserved through in-page anchor/history switches; reload uses new default.
- Browser first load checked=true/area1; reload +stat_close +recent checked=true/area1/noNaN; manual uncheck area0; reload restores checked=true/area1.
- Label still explicitly tenth–ninetieth percentile outcome distribution, not confidence interval or prediction probability. Aggregate data hashes unchanged; history/data integrity suites PASS.

## 2026-11-02 miniature hover p10–p90 band
- Mouse enter or keyboard-visible focus replaces only this cell SVG with neutral gray p10–p90 band behind mean solid/median dashed; domain includes both curves+p10+p90+zero with padding. Hover labels explicitly区间高/区间低 (actual combined extrema), aria says temporary local distribution axis.
- Mouseleave/blur restore original auto/shared SVG; single active overlay enforced across keyboard and pointer; rendering/dataset/anchor changes clear it. No mutation to selection/comparison on hover. Empty cells skipped.
- Browser actual pointer:enter low-sample8event cell→one gray band, move within child labels staysone, crosscell→one innewcell, outside→zero. Shared mode focusedcell temporary-24.18..71.14 while neighbor remains shared-54.12..73.62; history+anchor switch clearsall. Detail defaultband remainsenabled.
- Browser30%keyboard focus rendersband;72cells intact. First desktop coordinate attempt after focus/scroll did not hit intended cell, so no claim of verified30%coordinate targeting; locator-basedclick tested separately. Default72cells unchanged,redgreen dual lines legible overgray in screenshot.
- verify-hover bounds all142568finite values across144cells,empty handling,neutral fill/behindlines; five previous suitesPASS. All audited JSON hashes unchanged.

## 2026-11-02 single-stock historical reference view
- New separate单股走势tab; original matrix/hover/grayband/30–200%zoom preserved. Code/name lookup supports leading0 and SH/SZ/BJ prefix; unsupported code clear message. Lazy directory and one selected stock fetch with request generation guard.
- Frozen1494-stock source independently audited:36824nodes/73648anchors, latest prices2026-10-30, window2025-10-30..2026-10-30; immature nodes retained. gzip1494files ~16.25MiB total, max16.5KB each. Header-detect decompression supports already HTTP-decompressed bytes. Index SHA384d543263cb29da1f6fd653f55c9a5bc379f6190890aaf9b8a7d031bebd2f84. Full data not fetched on matrix view.
- Full-sample1494 reference fixed independent of matrix2020+ toggle; includes future information/targetstock and explicitly NOT historically available prediction/backtest. Source notice dates not separately verified first disclosure timestamps. No asof control. Actualclose and anchor(open orclose) use same latest-factor-normalized CNYscale.
- Stock true-price missing values breakSVG path. Both reference mean/median =base*(1+r),h0base; known dates use stockcalendar_index+h, beyondcutoff relative trading days only. Non-tradingdate node markers show actual node dates, nearestnext-market visual location explained; actual anchor date separately labeled. Same-day nodes availabledropdown. Nullholder shown无数据 not0. Reference rejection reasons translatedChinese.
- Browser actual gzip000008; recent2026node overlaid despite immaturefuture. Public2025-11-04 anchor2025-11-05 OPEN2.91 vsactualCLOSE2.96 verified. Independent expected values for3nodes×2statistics×5horizons=30SVGpoints maximumerror0.006793pixels (2decimalcoordinate rounding); bothanchors tested.
- Real node click000008stat2026-01-31 selects actualanchor2026-01-30; jump correspondingmatrix preserves72cells/defaultdetailband. 000021notice10/30 publicno-next-day refused butstatvalid. 000008notice10/31 rejected evenstatnode inwindow. 3011617record7stockgroup warnsbutdraws. 600053emptyreference notdrawn. 300561actualnullpath has2Msegments matching source. Invalid999999 rejected; Chinese name search loaded000009. NoNaN/undefined.
- verify-stock:all1494gzip/36824nodes; controlled delayed mock returns newerstockfirst thenolder, old cannot overwrite title/data; missingprices/emptynodes friendlyfallback. Exact audited matrixfixtures unaffected. Old tests/data/hover checksPASS. Cloudbrowser only; owner-auth production gate limitation remains, native successfuldeploy confirmspublication.

## 2026-11-02 keyboard previous/next node
- Current node list now date-ascending with stable id tie order; default remains most recent eligible node (or latest if none). Previous/next buttons plus live position/date. Boundaries disabled/no wrap; blocked nodes retained and reason shown.
- Unmodified←/→only in visible single-stock panel with loaded nonemptynodes. Input/textarea/select/contenteditable/textbox and meta/ctrl/alt/shift combinations ignored. No timers/held state; each repeat uses current dropdown index and redraws synchronously. Stock load nulls oldcurrent and request guard preserved.
- Actual CUA browser000008:29/29 default→Left28/29 blocked10/13 stilldisplayed→Right29/29→extraRight stays29. InputLeft and Meta+Left unchanged. FirstnodeLeft stays1/29 disabledprevious; repeatedRight to3/29. Statanchor switch thenLeft andmatrix-tabLeft preservecorrectstate; noNaN/undefined. Existingdata andgzip unchanged; fullA not claimed or included yet.

## 2026-11-02 default single-stock p10–p90 distribution band
- New checked-by-default toggle; neutral gray path below actual/mean/median, normalized base_price*(1+p10/p90). Y includes real price, mean/median andbothpercentiles. Toggle affectsdrawonly; match/count/nodeunchanged. Missingpairedpercentiles splitpolygon;empty/invalidnoband. Meaningexplicitnotactualminmax/notCI/notguaranteedbounds.
- CUA actualgzip000008 auditednodehn_a9aacd03c78735a92d657e87:publicbase2.91/statbase2.88, h0/1/20/60/250 p10/p90 total20points independently expected;maxcoordinateerrors0.005785px/0.006042px. EverybandvertexwithinY70..390. Toggleoff0band/samenode;on1band;Rightupdatesnodeandband.
- 301161small7/7 drawband+warning;600053empty→onlyactual/noband;001232newlisting8/4 insufficient60history→noband+Chinese reasons,noNaN. Switchback000008removesoldstate;30%Lefttoinvalidnodecorrectlyremovesband. Screenshotgraybehindblack/red/greenlegible;futureticksrelative交易日only. All datahashes unchanged; verify-stock-band includes syntheticnull-gap2polygons.

## Prior-price lookback controls (pending audited publication)
- Global prior-price windows 10/20/30/60/120, default60, distinct from future20 day.
- All/recent/stability load atomically by N; pending hides old research and stock overlay; latest request wins; failed window cannot silently show60. Switching clears comparisons and hover. Stock keeps node id and re-matches new window, expanded120-day calendar rebases anchor bydate.
- CUA browser:20 combinations (5N ×2history ×2anchor), all72cells, noNaN, metadata sample sizes and early coverage change correctly. New annual schemas show source_events/stocks byperiod, not fake raw funnel.
- Independent numerical fixture overlay_5n_expected.json:180 real SVG prices (9valid states ×4mean/median/p10/p90 ×5h), max rounding error0.006881px; ref counts andcalendar index equal; N30public0price node hasnooverlay.
- Full evidence shareholder_lookbacks_v1/audit/viewer_browser_qa.json. VM tests delayed window10→120 and old stock response; exact original60cache. Research/dual/color/hover/zoom/stockband regressionsPASS.

## Expanded frozen A-share query scope
- Query5554 (supplier frozen registry,23name-retired excluded), research1494 unchanged. Coverage5544prices/5527nodes, default60 comparable2226; N120 comparable2193, not5554 predictions. Render source missing-A counts distinctly, no TOTAL substitution, source gaps not disclosure absence.
- Both5554 base/patch gzip files exactfinal source bytes and decode tocorrectcode; old1494 bothgzip byte-identical; research15 JSON unchanged. IndexSHA base1472fa01202f44ad65c90a6899435d0cb963aec95e0ec49c5a7f8c6d20f5d022; patch36dd10a2803911765953e6daa780a329349dda647932b8feebcd178a0db13975.
- CUA browser400 independentexpected SVGpricepoints:000001 &920099×5N×2anchors×4stats×5h, maxerror0.006424px. Counts/nodeids/anchorindicesallmatch. Wait for patch readiness, no old60 overlay while loadingnewN.
- Real edges000017missingA,000638/603388sourcegap,000016no returned recentnodes,688796dateanomaly,000023no price,000001quarterly92day rejection,000038excluded vs999999unknown, BJ920099 normalization,000008old1494 N120+arrow regressionPASS.
- Evidence shareholder_query_all_a/audit/viewer_browser_qa.json. No matrix data changes, no GitHubpush. Owner-private existingproject.
- Final coverage clarification: source interval5544 vs display-year5537. FinalbaseindexSHA57ffe037c697c87ffaf2b9d9b699ce2f1e9450a766aff335c41502f88ee5436c supersedes1472fa. All7 earlier-only-price codes browserchecked noSVG; accurate source-last-date and no failed-fetch inference. 10source-empty distinct. Patch unchanged.
- Source Git per-push64MiB limit encountered; followed official smaller-push guidance with2source commits, no intermediate deployment. Final package contains all5554 base+patchfiles.

## Positive prior-price ≥80% column (81 cells)
- New up_4 includes exact+80%; negative≥80 magnitude andexact0 remain outside. 9rows×9columns, signed ascending, all5lookbacks/all+2020/stability/single-stock consistent.
- Full15researchSHA and5554base+patchbyte verification against frozen candidatePASS; baseindex11e58f6afe8c9c8a006762035c344bf40e42be5c48ac87ebbcdb50a511c8a481; patchf420f4e5c3eaa4ab1bc7cb0c54e2c7a954b222f225d7a1ffcb520e60f28af642. Independent old8 regression andnew aggregationPASS.
- CUA20matrixstates all81cells; up_4 low samples retainredgreen, empty10publicdecline_over30noSVG; sharedYanchorconsistent;30%81visible; future0/20/250retained.
- CUA15newlyeligible up_4nodes×mean/median/p10/p90×5h=300independentexpected SVGpoints, max0.006662px; node/count/index/labels allmatch. 300478prior60+80.51%195events/158stocks jumps correctly to rise_0/up_4.
- Evidence positive80_audit/viewer_browser_qa.json. Source pushes split below64MiB, onlyfinalcompleteversion deployed; ownerprivate preserved.

## Research pool2343 and independent display-length controls
- Screening2015-10-01..2026-10-31,133months/131rollingthree-monthwindows,2343pool(old1494+849); query5554 unchanged. Dynamic pool/reference labels, observed maturity dates andearlyperiodmonthcounts. Default60cohort125732/2139, earliest2012-04-18, early389(386April,2May,1October). No stability guarantee.
- New displaylength10/20/30/60/120/250, default250 independent of priorlookback60/futureselected20. Mini/detail/stockreference mean/median/p10p90clip0..L; shared+autoY andextrema usevisibleonly. Futureday>L clampswithnotice; expandingLdoesnotresetpriorN. Actualstockyearhistory unchanged; allresearchstillcomplete250samples; stabilitytablefixedhorizons.
- CUA30L×Nmatrixstates all81; 300new2343independent SVGpoints max0.007034px; another84clippedSVGpoints across6L max0.006167px andendXmax0.003637px. Unit476160visiblevalues insideappropriateY; latehiddenextremeexcluded. Sourceversionmismatch suppressesstaleoverlay.
- Special301161stat2026-07-20 N120 newly1event/1stock accepted withexplicitlow-samplewarning; mean/mediancoincidentasexpected, graybandandjumpdecline_over30/down_3correct. Notpresentedasreliableforecast.
- Frozenbaseindexb337211e6487ffeb45745bfeeb2e01d345f94d4886e98bbbfff507351e313500; patchaafeebc4390bf47b16cd0ad3b35b11a91908438b38bd580d097a930a90d01bf3;15researchSHA+11108gzip bytecheckPASS. Independentresearch/old1494paths/querymigrationauditPASS.
- Browser evidence expansion2343_audit/viewer_browser_qa.json. Addednextdisclosure rematchwarning; shorterdisplaydoesnotmeanreliablebeforethen.
