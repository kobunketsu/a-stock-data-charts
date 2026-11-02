from pathlib import Path
import sys,json,pandas as pd,numpy as np
R=Path(sys.argv[1]);N=int(sys.argv[2]);p=pd.read_csv(R/'statdate_only/event_panel_statdate.csv',dtype={'code':str});z=dict(np.load(R/'statdate_only/daily_paths_statdate.npz'));assert np.array_equal(p.event_id,z['event_id']);m=pd.read_csv(R/'holder_matrix_9rows/event_membership.csv');base=pd.read_csv(R/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv');d=pd.read_csv(R/'stability/stability_statistics.csv');chosen=[]
for _,g in p[p.event_id.isin(base.event_id)].sort_values(['code','entry_index','notice','event_id']).groupby('code'):
 last=stat=-10000
 for i,t in g.iterrows():
  if t.entry_index-last>250 and t.stat_index-stat>250:chosen.append(int(t.event_id));last=t.entry_index;stat=t.stat_index
saved=pd.read_csv(R/'stability/nonoverlapping_membership.csv');assert set(saved.event_id)==set(chosen);members={k:set(g.event_id) for k,g in m.groupby(['anchor','row_id','column_id'])};eras={'2010–2014':(2010,2014),'2015–2019':(2015,2019),'2020–2022':(2020,2022),'2023起成熟样本':(2023,2099)};year=p.notice.str[:4].astype(int);err=0.;checked=0
for (mode,gran,period,an,row,col),g in d.groupby(['sample_mode','granularity','period','anchor','row_id','column_id']):
 ids=members.get((an,row,col),set());lo,hi=eras[period] if gran=='era' else (int(period),int(period));mask=p.event_id.isin(ids)&year.between(lo,hi)
 if mode=='nonoverlapping250':mask &=p.event_id.isin(chosen)
 count=int(mask.sum());stocks=p.loc[mask,'code'].nunique();assert (g.count_events==count).all() and (g.count_stocks==stocks).all() and (g.small_sample==(count<50 or stocks<10)).all()
 for t in g.itertuples():
  a=z['public_nextopen_returns' if an=='public_nextopen' else 'stat_returns'][mask.to_numpy(),t.horizon].astype(float)
  if count:
   eq=pd.DataFrame({'code':p.loc[mask,'code'].to_numpy(),'r':a}).groupby('code').r.mean().mean();diff=np.max(abs(np.array([a.mean(),np.median(a),eq])-np.array([t.mean,t.median,t.equal_stock_mean])));err=max(err,float(diff));assert diff<1e-12
  else:assert np.isnan(t.mean) and np.isnan(t.median) and np.isnan(t.equal_stock_mean)
  checked+=1
out={'status':'PASS','n':N,'rows':checked,'max_error':err,'dual_anchor_nonoverlap_events':len(chosen),'id_to_row_not_assumed':True};(Path(__file__).parent/f'stability162_N{N}.json').write_text(json.dumps(out,indent=2));print(out)
