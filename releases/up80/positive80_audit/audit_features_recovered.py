from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
R=Path('./up80_recovery/research');A=Path(__file__).parent;p=pd.read_csv(R/'model/event_panel.csv',dtype={'code':str});cal=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(R/'absolute_only/trading_calendar.csv').date));ns=[10,20,30,60,120];ff={n:np.full((len(p),2),np.nan) for n in ns};keys=['code','notice','endpoint'];assert not p.duplicated(keys).any()
for code,g in p.groupby('code'):
 d=pd.read_csv(R/f'prices/{code}.csv',parse_dates=['date']).set_index('date').reindex(cal);c=d.close.to_numpy().copy();c[(d.volume<=0)|d.volume.isna()]=np.nan
 for j,col in enumerate(['notice','endpoint']):
  k=cal.searchsorted(pd.to_datetime(g[col]),side='right')-1
  for n in ns:
   good=k>=n;ff[n][g.index[good],j]=c[k[good]]/c[k[good]-n]-1
out=[]
for n in ns:
 q=pd.read_csv(R/f'lookbacks/lookback_{n}/model/event_panel.csv',dtype={'code':str});m=pd.read_csv(R/f'lookbacks/lookback_{n}/threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv',dtype={'code':str});expected=p[p.prior_stock_index>=n][keys].copy();expected['pub']=ff[n][p.prior_stock_index>=n,0];expected['stat']=ff[n][p.prior_stock_index>=n,1];v=expected.merge(q,on=keys,validate='one_to_one');assert len(v)==len(expected)==len(q);assert np.allclose(v.pub,v.mom60,rtol=0,atol=1e-12,equal_nan=True) and np.allclose(v.stat,v.stat_mom60,rtol=0,atol=1e-12,equal_nan=True);base=(p.prior_stock_index>=n)&p.matched_balanced250&(p.holder_delta!=0)&np.isfinite(ff[n]).all(1);assert set(map(tuple,p.loc[base,keys].values))==set(map(tuple,m[keys].values));old=json.load(open(A/(f'baseline60/all.json' if n==60 else f'baseline/prior/{n}/all.json')));h=hashlib.sha256(m.event_id.to_numpy().tobytes()).hexdigest();assert h==old['metadata']['event_ids_sha256'];out.append({'n':n,'panel':len(q),'base':len(m),'stocks':m.code.nunique(),'recent':int((m.notice>='2020-01-01').sum()),'published_event_id_hash_matches':True})
r={'status':'PASS','all_perN_features_and_member_keys_rebuilt':True,'results':out,'limitation':'ID hash is an extra check, not unavailable old1494 canonical-member archive comparison'};(A/'features_recovered_independent.json').write_text(json.dumps(r,indent=2));print(r)
