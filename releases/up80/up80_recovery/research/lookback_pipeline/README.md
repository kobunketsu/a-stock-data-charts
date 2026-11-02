# Recovered event-level lookback pipeline

1. Parent `build_superset.py` rebuilds canonical historical event panel and two complete251-path arrays from recovered raw holders/prices, with strict capture completeness guards.
2. Parent `prepare_lookback_panels.py` computes actual market-date N endpoints and selects zero-based prior-stock-index>=N. No N60 finite-feature mask is applied to other N.
3. `run_aggregate_all.py` runs `aggregate.py` for10/20/30/60/120. Inputs are per-N panel/feature/membership/NPZ; NPZ.event_id must equal panel.event_id positionally. All return extraction uses row boolean masks, never assumes event_id equals array position.

Outputs: two9x9 matrices perN, all/recent(2020+) curves, full precision CSV/JSON, UI7decimal arrays; stability four eras and annual coverage, event mean/median and equal-stock means at20/60/120/250; global per-stock nonoverlapping selection using strictly>250 market days at **both** anchors.

Nonoverlap sort is independently confirmed original algorithm: code,entry_index,notice,event_id; selection precedes era and cell grouping. Input float32 returns are converted to float64 before statistics. Each stock's within-cell mean is averaged equally across stocks.

Only positive prior-price>=80% is newly included asup_4. Exact80% included after1e-12 boundary snapping; negative magnitude>=80% and exact zero remain outside matrix. No summary-derived new returns are used.

Regression is a release gate: recomputed original8 columns must exactly reproduce frozen UI7decimal statistics and all counts; old stability must reproduce counts/dates and values within1e-12. Failure writes BLOCKED_OLD8_REGRESSION and terminates runner; no manifest for publication is produced. Do not loosen tolerances or substitute frozen summaries for failed event-level reconstruction.

Metadata schema/provenance is seeded from frozen published snapshots. Cohorts, group counts, accounting and dates are recomputed. Yearly stability output is explicitly period-source coverage, not a freshly computed raw-cleaning funnel; oldraw provenance must not be mistaken for a new measurement. Synthetic smoke fixtures live outside production under/tmp and are deliberately blocked by baseline regression.
