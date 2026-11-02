# All-A query positive-80% extension

Input is the immutable 5,554-stock production snapshot under `sites/shareholder-matrix/dist/single_stock` and `single_stock_patch`. The original gzip files and indexes are read only; final migration writes a complete source SHA inventory and checks source bytes again.

Output preserves the existing schemas. `single_stock/{index.json,stocks/*.json,stocks/*.json.gz}` is the base60 bundle; `lookback_patch/{index.json,stocks/*.json,stocks/*.json.gz}` is the five-lookback bundle. Deterministic gzip mtime=0 is used. `calendar`, `prices`, actual/source dates, holder values, raw node identifiers, prior-return values and start/end dates are never recomputed.

Only the positive prior-return >=0.8 group is added as `up_4` (including exact80%, tolerance1e-12 as in existing bins; no upper cap). Its old magnitude exclusion is removed, its cell references come from the corresponding new N matrix, and all other source/history/price/cutoff eligibility reasons are retained. Existing empty-reference reasons are recomputed only for the newly assigned column. A missing holder row does not become eligible. Empty historical cells remain excluded; small nonempty cells remain warning-only.

Negative prior-return magnitude >=0.8 remains excluded, with explicit reason `price_decline_magnitude_at_least80`. Prior8-column anchor values, eligibility, reasons and reference counts must remain unchanged; their new-matrix counts are verified. Main60 and patch60 row/column/eligibility/references must agree, while their original differing calendar-index offsets remain unchanged.

Base index coverage and per-stock five-N eligibility are recomputed from migrated nodes. Price-coverage fields stay unchanged because no price is fetched or altered. The reference training pool stays1494; expanding query coverage must not be described as expanding the training pool.

`AFFECTED_COUNTS.json` is a pre-migration impact count, not a final qualification result: new-column historical-reference availability is still required. `MIGRATION_QA.json` and `per_stock_eligibility.json` are emitted only after final matrix input is supplied.
