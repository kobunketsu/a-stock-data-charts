"""Explicit key-to-row old1494 regression and per-N validation panels. No network."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,required=True);P.add_argument('--old-root',type=Path,required=True);a=P.parse_args();B=a.root;OLD=a.old_root;K=['code','notice','endpoint'];oldcodes=set(pd.read_csv(B/'frozen_old1494.csv',dtype={'code':str}).code.str.zfill(6))
def read(p):return pd.read_csv(p,dtype={'code':str})
def align(old,new):
 assert not old.duplicated(K).any() and not new.duplicated(K).any(),'Duplicate canonical event key'
 x=old[K].assign(old_row=np.arange(len(old))).merge(new[K].assign(new_row=np.arange(len(new))),on=K,how='outer',indicator=True)
 assert (x['_merge']=='both').all(),'Old stock event-set changed'
 x=x.sort_values('old_row');return x.new_row.to_numpy(dtype=int)
def compare_frames(old,new,ignore=()):
 for c in old.columns:
  if c in ignore:continue
  assert c in new,c
  u=old[c].reset_index(drop=True);v=new[c].reset_index(drop=True)
  if pd.api.types.is_numeric_dtype(u) and pd.api.types.is_numeric_dtype(v):assert np.array_equal(u.to_numpy(),v.to_numpy(),equal_nan=True),c
  else:assert u.fillna('__NA__').astype(str).equals(v.fillna('__NA__').astype(str)),c
checks=[]
oldclean=read(OLD/'model/events_clean.csv');newclean=read(B/'model/events_clean.csv');newclean=newclean[newclean.code.isin(oldcodes)].reset_index(drop=True);idx=align(oldclean,newclean);compare_frames(oldclean,newclean.iloc[idx]);checks.append({'kind':'canonical_clean','events':len(oldclean),'status':'PASS'})
for n in [None,10,20,30,60,120]:
 O=OLD if n is None else OLD/'lookbacks'/f'lookback_{n}';R=B if n is None else B/'lookbacks'/f'lookback_{n}';old=read(O/'statdate_only/event_panel_statdate.csv');full=read(R/'statdate_only/event_panel_statdate.csv');row=np.flatnonzero(full.code.isin(oldcodes));new=full.iloc[row].reset_index(drop=True);ix=align(old,new);new=new.iloc[ix].reset_index(drop=True);rows=row[ix]
 compare_frames(old,new,ignore=['event_id']);oz=np.load(O/'statdate_only/daily_paths_statdate.npz');nz=np.load(R/'statdate_only/daily_paths_statdate.npz');assert np.array_equal(oz['event_id'],old.event_id) and np.array_equal(nz['event_id'],full.event_id)
 for key in ['public_nextopen_returns','stat_returns']:
  u=oz[key];v=nz[key]
  for st in range(0,len(old),1000):assert np.array_equal(u[st:st+1000],v[rows[st:st+1000]],equal_nan=True),(n,key,st)
 if n is not None:
  of=read(O/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv');nf=read(R/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv');assert np.array_equal(of.event_id,old.event_id) and np.array_equal(nf.event_id,full.event_id);nf=nf.iloc[rows].copy();compare_frames(of,nf,ignore=['event_id'])
  om=read(O/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv');nm=read(R/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv');nm=nm[nm.code.isin(oldcodes)];align(om,nm.reset_index(drop=True))
  V=B/'old1494_validation'/f'lookback_{n}'
  for d in ['statdate_only','threshold_curves/ranges_uniform60']:(V/d).mkdir(parents=True,exist_ok=True)
  new['event_id']=old.event_id.to_numpy();nf['event_id']=old.event_id.to_numpy();new.to_csv(V/'statdate_only/event_panel_statdate.csv',index=False);nf.to_csv(V/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv',index=False);np.savez_compressed(V/'statdate_only/daily_paths_statdate.npz',event_id=old.event_id.to_numpy(),public_nextopen_returns=nz['public_nextopen_returns'][rows],stat_returns=nz['stat_returns'][rows]);new[new.event_id.isin(om.event_id)].to_csv(V/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv',index=False)
 checks.append({'kind':'superset' if n is None else f'lookback{n}','events':len(old),'status':'PASS'})
qa={'status':'PASS','scope':'old1494_canonical_and_paths_preserved','key':K,'event_id_is_not_row_index':True,'checks':checks};(B/'OLD1494_PRESERVATION.json').write_text(json.dumps(qa,indent=2));print(qa)
