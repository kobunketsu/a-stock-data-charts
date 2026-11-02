from pathlib import Path
import sys,json,pandas as pd,numpy as np
R=Path(sys.argv[1]);N=int(sys.argv[2]);p=pd.read_csv(R/'statdate_only/event_panel_statdate.csv',dtype={'code':str});f=pd.read_csv(R/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv');z=dict(np.load(R/'statdate_only/daily_paths_statdate.npz'));assert np.array_equal(z['event_id'],p.event_id) and np.array_equal(f.event_id,p.event_id);assert not p.event_id.duplicated().any();base=(p.prior_stock_index>=N).to_numpy()&(p.holder_delta!=0).to_numpy()&np.isfinite(f[['mom60','stat_mom60']]).all(axis=1).to_numpy()
for key in ['public_nextopen_returns','stat_returns']:base &=np.isfinite(z[key]).all(axis=1)
member=pd.read_csv(R/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv');assert set(member.event_id)==set(p.loc[base,'event_id']);h=p.holder_delta.to_numpy();ha=abs(h).copy()
for e in [0,.05,.15,.3,1]:ha[abs(ha-e)<=1e-12]=e
hm={'decline_over30':(h<0)&(ha>.3),'rise_30to100':(h>0)&(ha>.3)&(ha<=1),'rise_over100':(h>0)&(ha>1)}
for sg in ['decline','rise']:
 sign=h<0 if sg=='decline' else h>0
 for b,lo,hi in [(0,0,.05),(1,.05,.15),(2,.15,.3)]:hm[f'{sg}_{b}']=sign&(ha>0)&(ha>=lo)&((ha<=hi) if b==2 else(ha<hi))
err=0.;cells=0;counts={}
for typ,folder in [('all','holder_matrix_9rows'),('recent','holder_matrix_9rows_2020plus')]:
 j=json.load(open(R/folder/'curves.json'));mm=pd.read_csv(R/folder/'event_membership.csv');assert len(j['curves'])==162;ba=base&(np.ones(len(p),bool) if typ=='all' else p.notice.ge('2020-01-01').to_numpy());counts[typ]=int(ba.sum())
 for c in j['curves']:
  anchor=c['anchor'];v=f['mom60' if anchor=='public_nextopen' else 'stat_mom60'].to_numpy();va=abs(v).copy()
  for e in [0,.1,.2,.4,.8]:va[abs(va-e)<=1e-12]=e
  direction,binstr=c['column_id'].split('_');b=int(binstr);edges=[0,.1,.2,.4,.8,np.inf];assert b<4 or direction=='up';mask=ba&hm[c['row_id']]&(va>0)&(va>=edges[b])&(va<edges[b+1])&((v<0) if direction=='down' else(v>0));n=int(mask.sum());ns=p.loc[mask,'code'].nunique();assert c['count_events']==n and c['count_stocks']==ns and c['small_sample']==(n<50 or ns<10) and c['empty']==(n==0);got=mm[(mm.anchor==anchor)&(mm.row_id==c['row_id'])&(mm.column_id==c['column_id'])];assert len(got)==n and set(got.event_id)==set(p.loc[mask,'event_id']);a=z['public_nextopen_returns' if anchor=='public_nextopen' else 'stat_returns'][mask].astype(float)
  funcs={'mean':lambda:a.mean(0),'median':lambda:np.median(a,axis=0),'positive_fraction':lambda:(a>0).mean(0),'p10':lambda:np.quantile(a,.1,axis=0),'p90':lambda:np.quantile(a,.9,axis=0)}
  for k,fn in funcs.items():
   assert len(c[k])==251
   if not n:assert all(x is None for x in c[k]);continue
   d=float(np.max(abs(fn()-c[k])));err=max(err,d);assert d<1e-12
  cells+=1
out={'status':'PASS','n':N,'cells':cells,'horizons':251,'stats':5,'max_error':err,'cohorts':counts,'id_to_row_not_assumed':True};(Path(__file__).parent/f'matrix162_N{N}.json').write_text(json.dumps(out,indent=2));print(out)
