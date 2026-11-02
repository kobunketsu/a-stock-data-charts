"""Usage: python compare_published_8cols.py new_delivery_manifest.json
Manifest files entries: lookback_market_days,type(all/recent/stability),path.
No event-level preservation claim: old1494 event arrays are unavailable.
"""
from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parent;manifest=json.load(open(sys.argv[1]));errors=[];error_count=0;checked=0;maxdiff=0.;tails=[]
def err(value):
 global error_count
 error_count+=1
 if len(errors)<5000:errors.append(value)
def eq(a,b,context,tol=0):
 global maxdiff
 if isinstance(a,list):
  if len(a)!=len(b):err([context,'length',len(a),len(b)]);return
  for i,(x,y) in enumerate(zip(a,b)):eq(x,y,context+f'[{i}]',tol)
 elif a is None or b is None or isinstance(a,(str,bool)):
  if a!=b:err([context,'value',a,b])
 else:
  d=abs(float(a)-float(b));maxdiff=max(maxdiff,d)
  if d>tol:err([context,'numeric',a,b,d])
for entry in manifest['files']:
 n=entry['lookback_market_days'];typ=entry['type'];new=json.load(open(entry['path']));old=json.load(open(R/(f'baseline60/{typ}.json' if n==60 else f'baseline/prior/{n}/{typ}.json')))
 if typ in ['all','recent']:
  cm={(c['anchor'],c['row_id'],c['column_id']):c for c in new['curves']};assert len(cm)==162 and len(new['columns'])==9
  for o in old['curves']:
   key=(o['anchor'],o['row_id'],o['column_id']);v=cm[key]
   for k in ['count_events','count_stocks','small_sample','empty','mean','median','p10','p90','positive_fraction']:eq(o[k],v[k],str((n,typ,key,k)))
   checked+=1
  for o in old['special_price_counts']:
   if o['category']!='price_up_at_least_80pct':continue
   v=cm[o['anchor'],o['row_id'],'up_4'];eq(o['count_events'],v['count_events'],str((n,typ,o['anchor'],o['row_id'],'tail_events')));eq(o['count_stocks'],v['count_stocks'],str((n,typ,o['anchor'],o['row_id'],'tail_stocks')));tails.append(v['count_events'])
 else:
  keys=['sample_mode','period','anchor','row_id','column_id'];cm={tuple(c[k] for k in keys):c for c in new['series']};assert len(cm)==1296
  for o in old['series']:
   key=tuple(o[k] for k in keys);v=cm[key]
   for k in ['count_events','count_stocks','small_sample','horizons','first_notice','last_notice','mean','median','equal_stock_mean']:eq(o[k],v[k],str((n,typ,key,k)),1e-12 if k in ['mean','median','equal_stock_mean'] else 0)
   checked+=1
out={'status':'PASS' if not error_count else 'FAIL','legacy_matrix_cells_and_stability_series_checked':checked,'max_numeric_difference':maxdiff,'difference_count':error_count,'first_5000_differences':errors,'tail_count_checks':len(tails),'limitation':'Frozen1494 full member IDs unavailable; compares published old8 stats/counts and saved positive-tail counts, not individual event membership.'};(R/'legacy8_regression.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print({k:v for k,v in out.items() if k!='first_5000_differences'});sys.exit(bool(error_count))
