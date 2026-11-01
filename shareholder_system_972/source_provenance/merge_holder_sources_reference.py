from pathlib import Path
import json,csv,hashlib,collections,datetime
R=Path(__file__).resolve().parent;OLD=R.parent/'shareholder_model_v2'
new=json.loads((R/'holders_added/all_raw.json').read_text()); assert not json.loads((R/'holders_added/manifest.json').read_text())['errors'], 'new collection incomplete'
pool=list(csv.DictReader((R/'qualified_982.csv').open()));codes={r['code'] for r in pool}
sourcepaths=[OLD/'holders/all_raw.json',OLD/'holders_baseline_2019/all_raw.json',R/'holders_added/all_raw.json']
allrows=[]
for p in sourcepaths:allrows.extend(json.loads(p.read_text()))
unique={json.dumps(x,sort_keys=True,ensure_ascii=False):x for x in allrows};allrows=list(unique.values())
assert {x['SECURITY_CODE'] for x in allrows}<=codes
for dirname,start,end in [('holders','2020-01-01','2026-10-31'),('holders_baseline_2019','2019-01-01','2019-12-31')]:
 o=R/dirname;o.mkdir(exist_ok=True);rows=[x for x in allrows if start<=x['HOLD_NOTICE_DATE'][:10]<=end];rows.sort(key=lambda x:(x['SECURITY_CODE'],x['HOLD_NOTICE_DATE'],x['END_DATE']))
 (o/'all_raw.json').write_text(json.dumps(rows,ensure_ascii=False))
 with (o/'events_raw.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (o/'pool_codes.json').write_text(json.dumps(sorted(codes)))
 by=collections.defaultdict(list)
 for x in rows:by[x['SECURITY_CODE']].append(x)
 coverage=[]
 for c in sorted(codes):
  rs=by.get(c,[]);ds=sorted(x['HOLD_NOTICE_DATE'][:10] for x in rs)
  coverage.append({'code':c,'rows':len(rs),'first':ds[0] if ds else None,'last':ds[-1] if ds else None,'observed_span_days':(datetime.date.fromisoformat(ds[-1])-datetime.date.fromisoformat(ds[0])).days if ds else None})
 with (o/'coverage_by_stock.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
 neg=[x for x in rows if x['END_DATE'][:10]>x['HOLD_NOTICE_DATE'][:10]]
 qa={'rows':len(rows),'stocks':len(by),'missing_codes':sorted(codes-set(by)),'negative_lag_count':len(neg),'year_counts':dict(collections.Counter(x['HOLD_NOTICE_DATE'][:4] for x in rows)),'first_announcement':min(x['HOLD_NOTICE_DATE'] for x in rows),'last_announcement':max(x['HOLD_NOTICE_DATE'] for x in rows),'observed_five_year_stock_count':sum(x['observed_span_days'] is not None and x['observed_span_days']>=1826 for x in coverage),'exact_duplicate_excess':0,'warning':'Raw anomalous future endpoint dates retained for downstream exclusion; observed history does not verify listing age; source announcement date not verified first public timestamp.'}
 (o/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));(o/'COMPLETE.json').write_text(json.dumps({'status':'complete',**qa},ensure_ascii=False,indent=2));print(dirname,json.dumps(qa,ensure_ascii=False))
manifest={'status':'complete','pool':982,'new_stocks_requested':529,'new_stocks_received':len({r['SECURITY_CODE'] for r in new}),'new_raw_rows':len(new),'premerge_rows':sum(len(json.loads(p.read_text())) for p in sourcepaths),'post_exact_dedup_rows':len(allrows),'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sourcepaths],'method':'Reuse original453 frozen snapshots; acquire529 new2019-2026 histories; exact-row dedup and split at notice2020-01-01; retained raw anomalies for downstream filtering'}
(R/'holder_merge_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(manifest,ensure_ascii=False))
