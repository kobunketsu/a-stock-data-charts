"""Event-level 9x9 matrix and stability; no network. Frozen templates are schema/provenance, never tail returns."""
from pathlib import Path
import argparse,json,copy,hashlib
from metadata_policy import finalize_metadata
import numpy as np,pandas as pd
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,required=True);P.add_argument('--lookback',type=int,required=True);P.add_argument('--baseline',type=Path,default=Path('positive80_audit/baseline'));P.add_argument('--expansion-guard',type=Path);P.add_argument('--pool-method',type=Path);P.add_argument('--baseline60',type=Path,default=Path('positive80_audit/baseline60'));a=P.parse_args();B=a.root;N=a.lookback;TOL=1e-12;H=[20,60,120,250];KEYS=['mean','median','positive_fraction','p10','p90'];ANCH=['public_nextopen','stat_close']
guard=json.load(open(a.expansion_guard)) if a.expansion_guard else None
if guard is not None:assert guard['status']=='PASS' and guard['scope']=='old1494_canonical_and_paths_preserved'
poolmethod=json.load(open(a.pool_method)) if a.pool_method else None
POOL_COUNT=poolmethod['pool_count'] if poolmethod else 1494
T=a.baseline60 if N==60 else a.baseline/'prior'/str(N);templates={k:json.load(open(T/f'{k}.json')) for k in ['all','recent','stability']}
p=pd.read_csv(B/'statdate_only/event_panel_statdate.csv',dtype={'code':str});f=pd.read_csv(B/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv');m=pd.read_csv(B/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv');z=np.load(B/'statdate_only/daily_paths_statdate.npz');assert np.array_equal(p.event_id,z['event_id']);assert np.array_equal(p.event_id,f.event_id);R={'public_nextopen':z['public_nextopen_returns'],'stat_close':z['stat_returns']};M={'public_nextopen':f.mom60.to_numpy(),'stat_close':f.stat_mom60.to_numpy()};hd=p.holder_delta.to_numpy();code=p.code.to_numpy();dates=p.notice.str[:10];ids=p.event_id.to_numpy()
broad=np.isfinite(hd)&np.isfinite(M['public_nextopen'])&np.isfinite(M['stat_close'])
if 'prior_stock_index' in p:broad &= p.prior_stock_index.to_numpy()>=N
for r in R.values():broad &= np.isfinite(r).all(axis=1)
base=p.event_id.isin(m.event_id).to_numpy();assert int(base.sum())==len(m);assert np.array_equal(base,broad&(hd!=0)), 'Membership must use ni>=N, dual finite features, dual complete251, nonzero holder'
def snap(x,edges):
 out=np.abs(x).copy()
 for edge in edges:out[np.abs(out-edge)<=TOL]=edge
 return out
ha=snap(hd,[0,.05,.15,.3,1]);hb=np.where(ha==0,-1,np.where(ha<.05,0,np.where(ha<.15,1,np.where(ha<=.3,2,np.where((hd>0)&(ha>1),4,3)))))
rows=copy.deepcopy(templates['all']['rows']);cols=copy.deepcopy(templates['all']['columns'])+[{'id':'up_4','direction':'up','bin':4,'label':f'此前{N}个交易日股价上涨80%及以上'}]
PB={anchor:np.where(snap(v,[0,.1,.2,.4,.8])==0,-1,np.searchsorted([.1,.2,.4,.8],snap(v,[0,.1,.2,.4,.8]),side='right')) for anchor,v in M.items()}
def cnt(mask):return {'count_events':int(mask.sum()),'count_stocks':int(p.loc[mask,'code'].nunique())}
def bounds(mask):return (str(dates[mask].min()),str(dates[mask].max())) if mask.any() else (None,None)
def hm(row):return (hb==row['bin'])&((hd<0) if row['direction']=='decline' else (hd>0))
def cm(anchor,col):return (PB[anchor]==col['bin'])&((M[anchor]<-TOL) if col['direction']=='down' else (M[anchor]>TOL))
def encode(x):
 if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
 if isinstance(x,list):return [encode(v) for v in x]
 if isinstance(x,np.integer):return int(x)
 if isinstance(x,np.bool_):return bool(x)
 if isinstance(x,(float,np.floating)) and not np.isfinite(x):return None
 return x
def writejson(path,v):path.write_text(json.dumps(encode(v),ensure_ascii=False,separators=(',',':'),allow_nan=False))
def curve(anchor,row,col,mask):
 cc=cnt(mask);n=cc['count_events'];c={'anchor':anchor,'row_id':row['id'],'column_id':col['id'],**cc,'small_sample':n<50 or cc['count_stocks']<10,'empty':not n};q=R[anchor][mask].astype(float)
 vals=[q.mean(0),np.median(q,axis=0),(q>0).mean(0),np.quantile(q,.1,axis=0),np.quantile(q,.9,axis=0)] if n else [[None]*251 for _ in KEYS]
 c.update({k:v.tolist() if hasattr(v,'tolist') else v for k,v in zip(KEYS,vals)});
 if n:assert c['mean'][0]==c['median'][0]==0
 return c
checks=[]
def verify_curves(payload,old,label):
 if guard is not None:
  checks.append({'part':label,'status':'NOT_APPLICABLE_EXPANDED_COHORT','note':'Expanded totals are new estimates; preserved old-pool subcohort is separately reaggregated and compared'})
  return True
 olds={(x['anchor'],x['row_id'],x['column_id']):x for x in old['curves']};errors=[]
 for c in payload['curves']:
  if c['column_id']=='up_4':continue
  key=c['anchor'],c['row_id'],c['column_id'];o=olds[key]
  for k in ['count_events','count_stocks','small_sample','empty']:
   if c[k]!=o[k]:errors.append([list(key),k,c[k],o[k]])
  for k in KEYS:
   # Same old UI rounding (7 decimals) must be retained exactly.
   vals=[round(x,7) if x is not None else None for x in c[k]]
   if vals!=o[k]:errors.append([list(key),k,'rounded curve mismatch'])
 checks.append({'part':label,'status':'PASS' if not errors else 'FAIL','errors':errors[:30],'error_count':len(errors)})
 return not errors
for mode in ['all','recent']:
 dateok=np.ones(len(p),bool) if mode=='all' else (dates>='2020-01-01').to_numpy();ba=base&dateok;br=broad&dateok;out=B/('holder_matrix_9rows' if mode=='all' else 'holder_matrix_9rows_2020plus');out.mkdir(parents=True,exist_ok=True);meta=copy.deepcopy(templates[mode]['metadata']);meta.update(lookback_market_days=N,version=f'recovered-up80-lookback{N}-{POOL_COUNT}-20261102-{mode}',cohort=cnt(ba),broader_eligible_cohort_including_unchanged=cnt(br),notice_min=bounds(ba)[0],notice_max=bounds(ba)[1],price_bins='signed (0,10%),[10%,20%),[20%,40%),[40%,80%); positive [80%,infinity) included; exact zero and negative magnitude>=80% outside grid',event_ids_sha256=hashlib.sha256(ids[ba].tobytes()).hexdigest(),recovery_note='Recomputed from recovered individual events/prices; archived metadata provenance retained separately; old8 numerical regression required before publication')
 if poolmethod is not None:
  meta['pool']=poolmethod;meta['stock_pool_screening_dates']=poolmethod['screening_dates']
 meta['archived_provenance']={k:copy.deepcopy(meta[k]) for k in ['panel_coverage','price_coverage','sample_funnel','history_extension'] if k in meta}
 meta['archived_provenance_note']='Historical published source snapshot, not current recovered-source measurement; reused and newly fetched sources are distinguished by the recovery manifests.'
 meta['panel_coverage']={'event_panel_records':int(dateok.sum()),'event_panel_stocks':int(p.loc[dateok,'code'].nunique()),'lookback_market_days':N,'scope':'current per-N prior_stock_index-filtered event panel within selected notice-date range'}
 meta['price_coverage']={'status':'see_recovery_price_audit','note':'Archived source coverage is under archived_provenance; current raw-price coverage is audited separately, not inferred from matrix event counts.'}
 meta['sample_funnel']={'valid_pool_stocks':POOL_COUNT,'event_panel_stocks':int(p.loc[dateok,'code'].nunique()),'event_panel_records':int(dateok.sum()),'common_complete250_nonzero_records':int(ba.sum()),'common_complete250_nonzero_stocks':int(p.loc[ba,'code'].nunique())}
 meta['history_extension']={'collection_target_start':'2010-01-01','actual_complete_sample_notice_min':bounds(ba)[0],'source_snapshot':'recovered inputs, with frozen reuse and missing-source recapture documented in recovery audit'}
 meta['warnings']=[w.replace('2024年10月至2026年10月','2015年10月至2026年10月') if poolmethod is not None else w for w in meta.get('warnings',[])]+['本轮使用恢复的事件级输入；部分缺失来源重新采集，来源版本不等同于旧快照，发布前须通过旧8列数值回归。']
 meta['holder_unchanged']=cnt(br&(hb==-1));meta['holder_groups']=[{**row,**cnt(ba&hm(row))} for row in rows];meta['holder_tail_groups_included']={d:cnt(ba&(hb>=3)&((hd<0) if d=='decline' else (hd>0))) for d in ['decline','rise']};meta['sample_funnel']=dict(meta.get('sample_funnel',{}),common_complete250_nonzero_records=int(ba.sum()),common_complete250_nonzero_stocks=int(p.loc[ba,'code'].nunique()))
 curves=[];extras=[];members=[]
 for anchor in ANCH:
  for row in rows:
   hh=ba&hm(row)
   for kind,sel in [('price_unchanged',PB[anchor]==-1),('price_down_at_least_80pct',(PB[anchor]==4)&(M[anchor]<-TOL))]:extras.append({'anchor':anchor,'row_id':row['id'],'category':kind,**cnt(hh&sel)})
   for col in cols:
    mask=hh&cm(anchor,col);curves.append(curve(anchor,row,col,mask));members.extend({'anchor':anchor,'row_id':row['id'],'column_id':col['id'],'event_id':int(i)} for i in ids[mask])
  cc=[c for c in curves if c['anchor']==anchor];zero=sum(x['count_events'] for x in extras if x['anchor']==anchor and x['category']=='price_unchanged');down=sum(x['count_events'] for x in extras if x['anchor']==anchor and x['category']=='price_down_at_least_80pct');grid=sum(c['count_events'] for c in cc);assert grid+zero+down==int(ba.sum());meta[anchor]={'main_holder_count':cnt(ba),'main_grid_events':grid,'cells':81,'empty_cells':sum(c['empty'] for c in cc),'below50_events':sum(c['count_events']<50 for c in cc),'below10_stocks':sum(c['count_stocks']<10 for c in cc),'small_cells':sum(c['small_sample'] for c in cc),'accounting':{'broader_eligible':int(br.sum()),'holder_unchanged_excluded':int((br&(hb==-1)).sum()),'nonzero_holder_included':int(ba.sum()),'price_unchanged_excluded':zero,'price_down_at_least80_excluded':down,'absolute_price_at_least80_excluded':down,'main_grid_events':grid}}
 if guard is not None:finalize_metadata(meta,B.parents[1])
 payload={'metadata':meta,'rows':rows,'columns':cols,'curves':curves,'special_price_counts':extras};verify_curves(payload,templates[mode],mode);writejson(out/'curves.json',payload);ui=copy.deepcopy(payload)
 for c in ui['curves']:
  for k in KEYS:c[k]=[round(v,7) if v is not None else None for v in c[k]]
 writejson(out/'curves_ui.json',ui);writejson(out/'metadata.json',meta);pd.DataFrame(members).to_csv(out/'event_membership.csv',index=False);pd.DataFrame(extras).to_csv(out/'price_special_counts.csv',index=False);pd.DataFrame([{k:c[k] for k in ['anchor','row_id','column_id','count_events','count_stocks','small_sample','empty']} for c in curves]).to_csv(out/'cell_counts.csv',index=False)
 daily=[{k:c[k] for k in ['anchor','row_id','column_id','count_events','count_stocks','small_sample']}|{'h':h,**{k:c[k][h] for k in KEYS}} for c in curves for h in range(251)];D=pd.DataFrame(daily);D.to_csv(out/'daily.csv',index=False);D[D.h.isin(meta['selected_horizons'])].to_csv(out/'selected_horizons.csv',index=False)
 print('matrix',N,mode,meta['cohort'],flush=True)
# Non-overlap selection is global per stock before era/cell slicing. Strictly >250 at both anchors.
non=np.zeros(len(p),bool)
for _,g in p.loc[base].sort_values(['code','entry_index','notice','event_id']).groupby('code',sort=True):
 lastpub=laststat=-10**9
 for i,r in g.iterrows():
  if r.entry_index-lastpub>250 and r.stat_index-laststat>250:non[i]=True;lastpub=r.entry_index;laststat=r.stat_index
ERAS=[('2010–2014','2010-01-01','2014-12-31'),('2015–2019','2015-01-01','2019-12-31'),('2020–2022','2020-01-01','2022-12-31'),('2023起成熟样本','2023-01-01','2100-12-31')];series=[];periods=[];yearly=[];statrows=[]
for sample,sel in [('all_events',base),('nonoverlapping250',non)]:
 for gran,period,start,end in [('era',*e) for e in ERAS]+[('year',str(y),f'{y}-01-01',f'{y}-12-31') for y in range(2010,2027)]:
  mask=sel&(dates>=start).to_numpy()&(dates<=end).to_numpy();cc=cnt(mask);lo,hi=bounds(mask);rec={'sample_mode':sample,'granularity':gran,'period':period,'start_rule':start,'end_rule':end,'source_events':cc['count_events'],'source_stocks':cc['count_stocks'],'first_notice':lo,'last_notice':hi};
  if gran=='year' and period=='2026' and not mask.any():rec['maturity_note']='No complete250-trading-day mature observations at frozen price cutoff; not evidence of zero raw disclosures'
  (periods if gran=='era' else yearly).append(rec)
  for anchor in ANCH:
   for row in rows:
    for col in cols:
     mm=mask&hm(row)&cm(anchor,col);cc=cnt(mm);size=cc['count_events'];lo,hi=bounds(mm);q=R[anchor][mm][:,H].astype(float)
     if size:
      avg=q.mean(0).tolist();med=np.median(q,axis=0).tolist();eq=pd.DataFrame(q).assign(code=code[mm]).groupby('code').mean().mean(axis=0).tolist()
     else:avg=med=eq=[None]*4
     c={'sample_mode':sample,'period':period,'anchor':anchor,'row_id':row['id'],'column_id':col['id'],**cc,'small_sample':size<50 or cc['count_stocks']<10,'horizons':H,'first_notice':lo,'last_notice':hi,'mean':avg,'median':med,'equal_stock_mean':eq}
     if gran=='era':series.append(c)
     statrows.extend({k:c[k] for k in ['sample_mode','period','anchor','row_id','column_id','count_events','count_stocks','small_sample','first_notice','last_notice']}|{'granularity':gran,'horizon':h,'mean':avg[t],'median':med[t],'equal_stock_mean':eq[t]} for t,h in enumerate(H))
oldseries={(s['sample_mode'],s['period'],s['anchor'],s['row_id'],s['column_id']):s for s in templates['stability']['series']};errs=[]
for s in series:
 if guard is not None:continue
 if s['column_id']=='up_4':continue
 k=tuple(s[x] for x in ['sample_mode','period','anchor','row_id','column_id']);old=oldseries[k]
 for field in ['count_events','count_stocks','small_sample','first_notice','last_notice']:
  if s[field]!=old[field]:errs.append([list(k),field,s[field],old[field]])
 for field in ['mean','median','equal_stock_mean']:
  if not np.allclose(np.array(s[field],dtype=float),np.array(old[field],dtype=float),rtol=0,atol=1e-12,equal_nan=True):errs.append([list(k),field,'difference>1e-12'])
checks.append({'part':'stability','status':('NOT_APPLICABLE_EXPANDED_COHORT' if guard is not None else 'PASS') if not errs else 'FAIL','error_count':len(errs),'errors':errs[:30]});out=B/'stability';out.mkdir(exist_ok=True);meta=copy.deepcopy(templates['stability']['metadata']);meta.update(version=f'recovered-up80-lookback{N}-{POOL_COUNT}-stability-20261102',lookback_market_days=N,yearly_coverage_schema='period_source_coverage_by_sample_mode; not raw-clean funnel');early=base&(dates<'2015-01-01').to_numpy();meta['early_period_month_counts']=dates[early].str[5:7].value_counts().sort_index().to_dict();
if poolmethod is not None:
 meta['stock_pool_screening_dates']=poolmethod['screening_dates'];meta['warnings']=[w.replace('2024年10月至2026年10月','2015年10月至2026年10月') for w in meta.get('warnings',[])]
if guard is not None:finalize_metadata(meta,B.parents[1],periods=periods)
payload={'metadata':meta,'periods':periods,'yearly_coverage':yearly,'rows':rows,'columns':cols,'series':series};writejson(out/'stability_ui.json',payload);pd.DataFrame(statrows).to_csv(out/'stability_statistics.csv',index=False);pd.DataFrame(periods).to_csv(out/'period_coverage.csv',index=False);pd.DataFrame(yearly).to_csv(out/'yearly_coverage.csv',index=False);p.loc[non,['event_id','code','notice','endpoint','entry_index','stat_index']].to_csv(out/'nonoverlapping_membership.csv',index=False)
qa={'lookback_market_days':N,'status':'PASS' if all(c['status'] in ['PASS','NOT_APPLICABLE_EXPANDED_COHORT'] for c in checks) else 'BLOCKED_OLD8_REGRESSION','checks':checks,'base':cnt(base),'broader':cnt(broad),'nonoverlap':cnt(non)};qa['old_pool_preservation_guard']=guard;writejson(B/('AGGREGATION_QA.json' if guard is not None else 'OLD8_REGRESSION.json'),qa);print(json.dumps(qa,ensure_ascii=False),flush=True)
if qa['status']!='PASS':raise SystemExit('BLOCKED: recovered old8 regression differs; no publish')
