"""Rebuild market-date lookbacks from recovered full superset; no network."""
from pathlib import Path
import json,hashlib,sys
import pandas as pd,numpy as np
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
p=pd.read_csv(R/'model/event_panel.csv',dtype={'code':str})
z=np.load(R/'statdate_only/daily_paths_statdate.npz')
assert np.array_equal(z['event_id'],p.event_id)
P=z['public_nextopen_returns'];S=z['stat_returns']
cal=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(R/'absolute_only/trading_calendar.csv').date))
features={n:np.full((len(p),2),np.nan) for n in [10,20,30,60,120]}
notice=pd.to_datetime(p.notice);endpoint=pd.to_datetime(p.endpoint)
ck=cal.searchsorted(notice,side='right')-1;sk=cal.searchsorted(endpoint,side='right')-1
for code,g in p.groupby('code',sort=False):
 d=pd.read_csv(R/'prices'/f'{code}.csv',parse_dates=['date']).drop_duplicates('date').sort_values('date').set_index('date')
 d=d[(d.close>0)&(d.open>0)].reindex(cal)
 ac=d.close.to_numpy().copy();av=d.volume.to_numpy();ac[(av<=0)|~np.isfinite(av)]=np.nan
 for n,f in features.items():
  for j,k in enumerate([ck[g.index],sk[g.index]]):
   v=np.where(k>=n,ac[k]/ac[np.maximum(k-n,0)]-1,np.nan)
   f[g.index,j]=v
out=[]
for n,f in features.items():
 # N60 original pipeline assigned IDs after ni>=60 admission; other N preserve superset IDs.
 keep=p.prior_stock_index.to_numpy()>=n
 q=p.loc[keep].copy();ff=f[keep];pp=P[keep];ss=S[keep]
 if n==60:q['event_id']=np.arange(len(q))
 q['mom60']=ff[:,0];q['stat_mom60']=ff[:,1]
 q['public_feature_start_date']=[str(cal[k-n].date()) if k>=n else None for k in ck[keep]]
 q['public_feature_end_date']=cal[ck[keep]].astype(str)
 broad=np.isfinite(pp).all(1)&np.isfinite(ss).all(1)&np.isfinite(ff).all(1)&np.isfinite(q.holder_delta)
 base=broad&(q.holder_delta.to_numpy()!=0)
 O=R/'lookbacks'/f'lookback_{n}'
 for folder in ['model','statdate_only','threshold_curves/ranges_uniform60','absolute_only']:(O/folder).mkdir(parents=True,exist_ok=True)
 q.to_csv(O/'model/event_panel.csv',index=False)
 q.to_csv(O/'statdate_only/event_panel_statdate.csv',index=False)
 np.savez_compressed(O/'statdate_only/daily_paths_statdate.npz',event_id=q.event_id.to_numpy(),public_nextopen_returns=pp,stat_returns=ss)
 cols=['event_id','code','notice','public_feature_start_date','public_feature_end_date','legacy_mom60','mom60','stat_mom60']
 q[cols].to_csv(O/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv',index=False)
 q.loc[base].to_csv(O/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv',index=False)
 meta={'lookback_market_days':n,'panel_records':len(q),'cohort_events':int(base.sum()),'cohort_stocks':int(q.loc[base,'code'].nunique()),'recent_events':int((base&(q.notice>='2020-01-01')).sum()),'event_ids_sha256':hashlib.sha256(q.loc[base,'event_id'].to_numpy().tobytes()).hexdigest(),'admission':'zero-based prior_stock_index>=N; actual two market-date close endpoints; both complete251 paths; finite two lookbacks; nonzero holder change','restored_not_yet_legacy_regression_approved':True}
 (O/'PREPARED.json').write_text(json.dumps(meta,indent=2));out.append(meta);print(meta,flush=True)
(R/'lookbacks/PREPARED_ALL.json').write_text(json.dumps(out,indent=2))
