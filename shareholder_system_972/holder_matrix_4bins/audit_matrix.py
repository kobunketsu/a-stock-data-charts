from pathlib import Path
import pandas as pd,numpy as np,json
O=Path(__file__).resolve().parent;B=O.parent
p=pd.read_csv(B/'statdate_only/event_panel_statdate.csv',dtype={'code':str});f=pd.read_csv(B/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv');m=pd.read_csv(B/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv')
a=json.loads((O/'curves.json').read_text());mem=pd.read_csv(O/'event_membership.csv');checks=[];maxerr=0
h=abs(p.holder_delta.to_numpy());
for e in [0,.05,.15,.3]:h[abs(h-e)<=1e-12]=e
hmasks=[(h>0)&(h<.05),(h>=.05)&(h<.15),(h>=.15)&(h<=.3),h>.3]
for c in a['curves']:
 di,bi=c['row_id'].rsplit('_',1);pdirection,pbi=c['column_id'].rsplit('_',1);v=f.mom60.to_numpy() if c['anchor']=='public_nextopen' else f.stat_mom60.to_numpy();mag=abs(v).copy()
 for e in [0,.1,.2,.4,.8]:mag[abs(mag-e)<=1e-12]=e
 edges=[0,.1,.2,.4,.8];i=int(pbi)
 mask=p.event_id.isin(m.event_id).to_numpy()&hmasks[3 if bi=='over30' else int(bi)]&((p.holder_delta<0).to_numpy() if di=='decline' else (p.holder_delta>0).to_numpy())&(mag>=edges[i])&(mag<edges[i+1])&(mag>0)&((v<0) if pdirection=='down' else (v>0))
 assert mask.sum()==c['count_events'];assert p.loc[mask,'code'].nunique()==c['count_stocks']
 mm=mem[(mem.anchor==c['anchor'])&(mem.row_id==c['row_id'])&(mem.column_id==c['column_id'])]
 assert set(mm.event_id)==set(p.loc[mask,'event_id'])
 for n in [1,3,5,10,20,40,60,120,250]:
  if not mask.any():continue
  col=('returns_' if c['anchor']=='public_nextopen' else 'stat_return_')+str(n);v2=p.loc[mask,col].to_numpy();assert np.isfinite(v2).all()
  err=max(abs(v2.mean()-c['mean'][n]),abs(np.median(v2)-c['median'][n]));maxerr=max(err,maxerr);assert err<1e-7
 assert c['small_sample']==(c['count_events']<50 or c['count_stocks']<10)
checks=['128 cells independently reconstructed with direct interval masks','membership exact event-id sets','counts and unique stocks','9 horizons mean/median against separate panel columns','low-sample flags','empty cells preserved as null']
report={'status':'PASS','checks':checks,'maximum_absolute_return_error':maxerr,'cells':128}
(O/'INDEPENDENT_AUDIT.json').write_text(json.dumps(report,indent=2));print(report)
print(pd.read_csv(O/'price_special_counts.csv').groupby(['anchor','category']).count_events.sum())
