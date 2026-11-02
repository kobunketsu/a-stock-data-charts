from pathlib import Path
import json,gzip,pandas as pd,numpy as np,hashlib,sys
O=Path(__file__).resolve().parent;R=O.parent;ARC=R/'archive972/shareholder_system_972';BASE=Path('./positive80_audit/baseline/single_stock_patch/stocks');pool=pd.read_csv(R/'qualified_1494.csv',dtype={'code':str});out=[];errors=[];oldcount=0
partial='--partial' in sys.argv
if partial:pool=pool[pool.code.map(lambda c:(O/'prices'/f'{c}.csv').exists())]
for q in pool.itertuples():
 c=q.code;path=O/'prices'/f'{c}.csv'
 if not path.exists():raise SystemExit('Price missing; refusing partial audit: '+c)
 d=pd.read_csv(path).set_index('date');assert d.index.is_monotonic_increasing and not d.index.duplicated().any();assert np.isfinite(d.select_dtypes('number')).all().all();assert (d[['open','high','low','close','adjustment_factor']]>0).all().all()
 for k in ['open','high','low','close']:assert np.allclose(d[k],d['raw_'+k]*d.adjustment_factor,rtol=1e-12,atol=1e-10)
 frozen=ARC/'prices'/f'{c}.csv'
 if frozen.exists():
  original=frozen.read_bytes().split(b'\n',1)[1];restored=b''.join(line for line in path.read_bytes().splitlines(keepends=True)[1:] if line[:10]>=b'2019-01-01');assert restored==original;oldcount+=1
 bp=BASE/f'{c}.json.gz'
 if not bp.exists():errors.append({'code':c,'error':'baseline_gz_missing'});continue
 j=json.loads(gzip.decompress(bp.read_bytes()));norm=float(j['metadata']['normalization_factor']);current=float(d.loc[j['metadata']['latest_available_price_date'],'adjustment_factor']);maxerr=0.;maxmom=0.;nprice=0;nmom=0;nb=0;issues=[]
 for x in j['prices']:
  date=x['date'];r=d.loc[date] if date in d.index else None;valid=r is not None and np.isfinite(r.volume) and r.volume>0
  for field in ['open','close']:
   actual=float(r[field])/norm if valid else None;expect=x[field]
   if actual is None or expect is None:
    if actual is not None or expect is not None:issues.append({'kind':'price_null_disagreement','date':date,'field':field,'baseline':expect,'new':actual})
   else:
    delta=abs(actual-expect);maxerr=max(maxerr,delta);nprice+=1
    if delta>1e-9:issues.append({'kind':'normalized_price_difference','date':date,'field':field,'baseline':expect,'new':actual,'absolute_error':delta})
  if x.get('volume') is not None and r is not None and float(r.volume)!=float(x['volume']):issues.append({'kind':'volume_difference','date':date,'baseline':x['volume'],'new':float(r.volume)})
 for nid,record in j['nodes'].items():
  for lookback,anchors in record['anchors_by_lookback'].items():
   for anchor,a in anchors.items():
    date=a.get('date');bp=a.get('base_price')
    if date and bp is not None and date in d.index:
     actual=float(d.loc[date,'open' if anchor=='public_nextopen' else 'close'])/norm;delta=abs(actual-bp);maxerr=max(maxerr,delta);nb+=1
     if delta>1e-9:issues.append({'kind':'base_price_difference','node':nid+':'+lookback,'anchor':anchor,'absolute_error':delta})
    start=a.get('prior_start',a.get('prior'+lookback+'_start'));end=a.get('prior_end',a.get('prior'+lookback+'_end'));expect=a.get('prior_change',a.get('prior'+lookback+'_change'))
    if expect is not None and start in d.index and end in d.index:
     actual=float(d.loc[end,'close'])/float(d.loc[start,'close'])-1;delta=abs(actual-expect);maxmom=max(maxmom,delta);nmom+=1
     if delta>1e-10:issues.append({'kind':'priorN_difference','node':nid+':'+lookback,'anchor':anchor,'absolute_error':delta})
 if abs(current-norm)>1e-9:issues.append({'kind':'normalization_factor_difference','baseline':norm,'new':current})
 if issues:errors.append({'code':c,'issues':issues})
 out.append({'code':c,'rows':len(d),'first':d.index.min(),'last':d.index.max(),'baseline_price_values_checked':nprice,'anchor_base_values_checked':nb,'priorN_values_checked':nmom,'max_price_abs_error':maxerr,'max_priorN_abs_error':maxmom,'factor_abs_error':abs(current-norm),'issue_count':len(issues),'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
pd.DataFrame(out).to_csv(O/('restored_price_coverage_partial.csv' if partial else 'restored_price_coverage.csv'),index=False);report={'status':('PASS_PARTIAL' if partial else 'PASS') if not errors else 'FAIL','stocks':len(out),'old972_2019plus_byte_identical':oldcount==972,'total_price_rows':sum(x['rows'] for x in out),'baseline_price_values_checked':sum(x['baseline_price_values_checked'] for x in out),'anchor_base_values_checked':sum(x['anchor_base_values_checked'] for x in out),'priorN_values_checked':sum(x['priorN_values_checked'] for x in out),'max_factor_abs_error':max(x['factor_abs_error'] for x in out),'max_price_abs_error':max(x['max_price_abs_error'] for x in out),'max_priorN_abs_error':max(x['max_priorN_abs_error'] for x in out),'errors':errors,'scope':'Saved120day-warmup baseline normalized open/close, volumes, anchorbase, all5N=10/20/30/60/120 prior changes and latest factor checked. Does not by itself prove all pre-window refetched522 history identical; historical main8column regression remains required.'};(O/('RESTORED_PRICE_QA_PARTIAL.json' if partial else 'RESTORED_PRICE_QA.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
