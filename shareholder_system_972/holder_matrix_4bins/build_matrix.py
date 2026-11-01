from pathlib import Path
import numpy as np,pandas as pd,json,hashlib
O=Path(__file__).resolve().parent; B=O.parent; tol=1e-12
p=pd.read_csv(B/'statdate_only/event_panel_statdate.csv',dtype={'code':str})
f=pd.read_csv(B/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv')
m=pd.read_csv(B/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv')
z=np.load(B/'statdate_only/daily_paths_statdate.npz'); assert np.array_equal(z['event_id'],p.event_id); assert np.array_equal(f.event_id,p.event_id)
R={'public_nextopen':z['public_nextopen_returns'],'stat_close':z['stat_returns']}
M={'public_nextopen':f.mom60.to_numpy(),'stat_close':f.stat_mom60.to_numpy()}
broad=np.isfinite(M['public_nextopen'])&np.isfinite(M['stat_close'])&p.matched_balanced250.to_numpy()&np.isfinite(p.holder_delta.to_numpy())
for r in R.values():broad &= np.isfinite(r).all(axis=1)
base=p.event_id.isin(m.event_id).to_numpy();assert sum(base)==len(m)
hd=p.holder_delta.to_numpy(); ha=abs(hd).copy()
for e in [0,.05,.15,.3]:ha[abs(ha-e)<=tol]=e
hb=np.where(ha==0,-1,np.where(ha<.05,0,np.where(ha<.15,1,np.where(ha<=.3,2,3))))
assert np.array_equal(base,broad&(hd!=0))
rows=[{'id':f'{di}_{bi}' if bi<3 else f'{di}_over30','direction':di,'bin':bi,'label':f'股东人数{cn}{lab}'} for di,cn in [('decline','减少'),('rise','增加')] for bi,lab in enumerate(['不到5%','5%—不到15%','15%—30%','超过30%'])]
rows=sorted(rows,key=lambda r: (-1 if r['direction']=='decline' else 1)*(r['bin']+1))
cols=[{'id':f'{di}_{bi}','direction':di,'bin':bi,'label':f'此前60个交易日股价{cn}{lab}'} for di,cn in [('down','下跌'),('up','上涨')] for bi,lab in enumerate(['不到10%','10%—不到20%','20%—不到40%','40%—不到80%'])]
cols=sorted(cols,key=lambda c:(-1 if c['direction']=='down' else 1)*(c['bin']+1))
def cnt(mask):return {'count_events':int(mask.sum()),'count_stocks':int(p.loc[mask,'code'].nunique())}
def pbucket(v):
 a=abs(v).copy()
 for e in [0,.1,.2,.4,.8]:a[abs(a-e)<=tol]=e
 return np.where(a==0,-1,np.searchsorted([.1,.2,.4,.8],a,side='right'))
meta={'units':'decimal fractions; multiply by 100 for percent','horizons':list(range(251)),'selected_horizons':[0,1,3,5,10,20,40,60,120,250], 'cohort':cnt(base),'broader_eligible_cohort_including_unchanged':cnt(broad),'notice_min':p.loc[base,'notice'].min(),'notice_max':p.loc[base,'notice'].max(),'holder_bins':'(0,5%),[5%,15%),[15%,30%],(30%,infinity); signed directions separate; exact zero outside grid; boundary snap tolerance1e-12','price_bins':'signed (0,10%),[10%,20%),[20%,40%),[40%,80%); exact zero and >=80% in either direction separate','warnings':['统计日起点是事后观察，股东人数当时通常尚未公布。','公布后起点为下个市场交易日开盘，并非已计费用或成交约束的策略回测。','此前股价为固定60个市场交易日，股东变化为相邻两期统计，时间区间不同。','每条披露记录等权；同股可重复且观察期重叠，不是组合净值。','股票池按近期披露频率筛选，且保留完整250日观察，存在选择偏差。','低于50条记录或10只股票标为样本不足；不能由此证明庄家行为。'],'event_ids_sha256':hashlib.sha256(p.loc[base,'event_id'].to_numpy().tobytes()).hexdigest()}
meta['pool']=json.loads((B/'POOL_METHOD.json').read_text())
meta['panel_coverage']=json.loads((B/'model/panel_qa.json').read_text())
meta['price_coverage']=json.loads((B/'price_qa_972.json').read_text())
meta['sample_funnel']={'raw_candidate_stocks':982,'negative_lag_removed_stocks':10,'valid_pool_stocks':972,'event_panel_stocks':int(p.code.nunique()),'event_panel_records':len(p),'common_complete250_nonzero_records':int(base.sum()),'common_complete250_nonzero_stocks':int(p.loc[base,'code'].nunique())}
meta['holder_unchanged']=cnt(broad&(hb==-1));meta['holder_tail_groups_included']={d:cnt(base&(hb==3)&((hd<0) if d=='decline' else (hd>0))) for d in ['decline','rise']}
meta['holder_groups']=[{**r,**cnt(base&(hb==r['bin'])&((hd<0) if r['direction']=='decline' else (hd>0)))} for r in rows]
curves=[];daily=[];extras=[];members=[]
for anchor,v in M.items():
 pb=pbucket(v);mainholder=base&(hb>=0)&(hb<=3)
 for row in rows:
  hm=base&(hb==row['bin'])&((hd<0) if row['direction']=='decline' else (hd>0))
  for kind,em in [('price_unchanged',pb==-1),('price_up_at_least_80pct',(pb==4)&(v>tol)),('price_down_at_least_80pct',(pb==4)&(v < -tol))]:extras.append({'anchor':anchor,'row_id':row['id'],'category':kind,**cnt(hm&em)})
  for col in cols:
   mask=hm&(pb==col['bin'])&((v < -tol) if col['direction']=='down' else (v>tol));a=R[anchor][mask].astype(float);cc=cnt(mask);n=cc['count_events'];small=n<50 or cc['count_stocks']<10
   c={'anchor':anchor,'row_id':row['id'],'column_id':col['id'],**cc,'small_sample':small,'empty':not n}
   if n:
    for key,val in [('mean',a.mean(0)),('median',np.median(a,axis=0)),('positive_fraction',(a>0).mean(0)),('p10',np.quantile(a,.1,axis=0)),('p90',np.quantile(a,.9,axis=0))]:c[key]=val.tolist()
    assert c['mean'][0]==c['median'][0]==0
   else:
    for key in ['mean','median','positive_fraction','p10','p90']:c[key]=[None]*251
   curves.append(c)
   for h in range(251):daily.append({k:c[k] for k in ['anchor','row_id','column_id','count_events','count_stocks','small_sample']}|{'h':h,**{k:c[k][h] for k in ['mean','median','positive_fraction','p10','p90']}})
   for eid in p.loc[mask,'event_id']:members.append({'anchor':anchor,'row_id':row['id'],'column_id':col['id'],'event_id':int(eid)})
 ds=[c for c in curves if c['anchor']==anchor]
 meta[anchor]={'main_holder_count':cnt(mainholder),'main_grid_events':sum(c['count_events'] for c in ds),'cells':len(ds),'empty_cells':sum(c['empty'] for c in ds),'below50_events':sum(c['count_events']<50 for c in ds),'below10_stocks':sum(c['count_stocks']<10 for c in ds),'small_cells':sum(c['small_sample'] for c in ds)}
 assert sum(c['count_events'] for c in ds)+sum(x['count_events'] for x in extras if x['anchor']==anchor)==int(mainholder.sum())
D=pd.DataFrame(daily);D.to_csv(O/'daily.csv',index=False);D[D.h.isin(meta['selected_horizons'])].to_csv(O/'selected_horizons.csv',index=False)
pd.DataFrame([{k:c[k] for k in ['anchor','row_id','column_id','count_events','count_stocks','small_sample','empty']} for c in curves]).to_csv(O/'cell_counts.csv',index=False)
pd.DataFrame(extras).to_csv(O/'price_special_counts.csv',index=False);pd.DataFrame(members).to_csv(O/'event_membership.csv',index=False)
meta['version']='monthly972-holder4-price4-20261101'
meta['holder_tail_groups_are_excluded']=False
for anchor in R:
 meta[anchor]['accounting']={'broader_eligible':int(broad.sum()),'holder_unchanged_excluded':int((broad&(hb==-1)).sum()),'nonzero_holder_included':int(base.sum()),'price_unchanged_excluded':sum(x['count_events'] for x in extras if x['anchor']==anchor and x['category']=='price_unchanged'),'absolute_price_at_least80_excluded':sum(x['count_events'] for x in extras if x['anchor']==anchor and '80pct' in x['category']),'main_grid_events':meta[anchor]['main_grid_events']}
payload={'metadata':meta,'rows':rows,'columns':cols,'curves':curves,'special_price_counts':extras}
(O/'curves.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False))
(O/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2,allow_nan=False))
print(json.dumps(meta,ensure_ascii=False,indent=2))
print('EXAMPLE MOST POPULOUS')
for anchor in R:
 c=max((c for c in curves if c['anchor']==anchor),key=lambda c:c['count_events']);print(anchor,c['row_id'],c['column_id'],c['count_events'],c['count_stocks'],{h:(c['mean'][h],c['median'][h]) for h in [20,60,250]})

ui=json.loads(json.dumps(payload))
for c in ui['curves']:
 for key in ['mean','median','positive_fraction','p10','p90']: c[key]=[round(v,7) if v is not None else None for v in c[key]]
ui['metadata']['display_rounding']='UI JSON returns rounded to 7 decimal places; CSV and curves.json full precision'
(O/'curves_ui.json').write_text(json.dumps(ui,ensure_ascii=False,separators=(',',':'),allow_nan=False))
