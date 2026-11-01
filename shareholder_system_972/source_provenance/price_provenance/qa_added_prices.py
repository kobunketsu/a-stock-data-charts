import pandas as pd,numpy as np,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;B=Path('historical-capture/shareholder_model_v2'); pool=pd.read_csv(O/'qualified_982.csv',dtype={'code':str});old=pd.read_csv(B/'qualified_453.csv',dtype={'code':str});out=[]
for row in pool.itertuples():
 c=row.code;p=O/'prices'/f'{c}.csv'
 if not p.exists():out.append({'code':c,'status':'missing'});continue
 d=pd.read_csv(p);vals=d[['open','high','low','close','volume','adjustment_factor']].to_numpy();problems=[]
 if not np.isfinite(vals).all():problems.append('nonfinite')
 if (d[['open','high','low','close','adjustment_factor']]<=0).any().any():problems.append('nonpositive')
 if d.date.duplicated().any() or not d.date.is_monotonic_increasing:problems.append('date_order')
 if (d.high+1e-7<d[['open','close','low']].max(axis=1)).any() or (d.low-1e-7>d[['open','close','high']].min(axis=1)).any():problems.append('OHLC_order')
 for field in ['open','high','low','close']:
  if not np.allclose(d[field],d['raw_'+field]*d.adjustment_factor):problems.append('adjustment_'+field)
 reused=c in set(old.code)
 if reused and hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256((B/'prices'/p.name).read_bytes()).digest():problems.append('old_changed')
 out.append({'code':c,'name':row.name,'status':'ok' if not problems else 'qa_error','problems':';'.join(problems),'rows':len(d),'first':d.date.min(),'last':d.date.max(),'history_5y':(pd.Timestamp(d.date.max())-pd.Timestamp(d.date.min())).days>=1826,'reused_old':reused,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
r=pd.DataFrame(out);r.to_csv(O/'price_coverage.csv',index=False);report={'pool':len(pool),'statuses':r.status.value_counts().to_dict(),'total_rows':int(r.rows.fillna(0).sum()),'missing_codes':r.loc[r.status=='missing','code'].tolist(),'qa_errors':r.loc[r.status=='qa_error'].to_dict('records'),'all_original453_byte_identical':bool(len(r[(r.reused_old==True)&(r.status=='ok')])==453)};(O/'price_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if (O/'qualified_972.csv').exists():
 main=pd.read_csv(O/'qualified_972.csv',dtype={'code':str}); rr=r[r.code.isin(main.code)].copy();rr.to_csv(O/'price_coverage_972.csv',index=False)
 summary={'pool':len(main),'statuses':rr.status.value_counts().to_dict(),'rows':int(rr.rows.fillna(0).sum()),'stocks_history_at_least_5years':int(rr.history_5y.fillna(False).sum()),'missing_codes':rr.loc[rr.status=='missing','code'].tolist(),'qa_errors':rr.loc[rr.status=='qa_error'].to_dict('records'),'candidate_pool_count':982,'explanation':'972 is cleaned main pool; full982 price fetch preserved as candidate acquisition record.'}
 (O/'price_qa_972.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('MAIN972',json.dumps(summary,ensure_ascii=False))
