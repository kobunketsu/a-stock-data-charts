"""Expanded pool, original event eligibility and frozen trading calendar; no index returns."""
from pathlib import Path
import pandas as pd,numpy as np,json,shutil,sys,clean_holders
from clean_holders import holders
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent;clean_holders.ROOT=ROOT;H=[1,3,5,10,20,40,60,120,250]
# This restored model must never silently run from a partial checkpoint.
pool_codes=set(pd.read_csv(ROOT/'qualified_pool.csv',dtype={'code':str}).code)
assert len(pool_codes)==1494, 'Expected frozen1494 reference pool'
missing=[c for c in sorted(pool_codes) if not (ROOT/'prices'/f'{c}.csv').exists()]
assert not missing, f'Incomplete recovered prices: {len(missing)} missing; do not publish partial model'
assert (ROOT/'HOLDER_RECOVERY_AUDIT.json').exists(), 'Holder merge not complete'
assert json.loads((ROOT/'HOLDER_RECOVERY_AUDIT.json').read_text())['status']=='complete'
for d in ['model','absolute_only','statdate_only','threshold_curves/ranges_uniform60']:(ROOT/d).mkdir(parents=True,exist_ok=True)
if not (ROOT/'absolute_only/trading_calendar.csv').exists():raise FileNotFoundError('Frozen trading calendar missing from this package')
cal=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(ROOT/'absolute_only/trading_calendar.csv').date));N=len(cal)
e,pub,hqa=holders(ROOT/'holders/events_raw.csv');e.to_csv(ROOT/'model/events_clean.csv',index=False);pub.to_csv(ROOT/'model/public_holder_observations.csv',index=False)
frames=[];paths_public=[];paths_stat=[];qa={'missing_price':0,'missing_entry':0,'missing_history':0};offset=np.arange(251)
for code,g in e.groupby('code',sort=True):
 path=ROOT/'prices'/f'{code}.csv'
 if not path.exists():qa['missing_price']+=len(g);continue
 d=pd.read_csv(path,parse_dates=['date']).drop_duplicates('date').sort_values('date').set_index('date');d=d[(d.close>0)&(d.open>0)]
 v=d.reindex(cal);ac=v.close.to_numpy().copy();ao=v.open.to_numpy();av=v.volume.to_numpy();ac[(av<=0)|~np.isfinite(av)]=np.nan
 ei=cal.searchsorted(g.notice,side='right');ni=d.index.searchsorted(g.notice,side='right')-1
 within=ei<N;entryok=np.zeros(len(g),bool);entryok[within]=np.isfinite(ao[ei[within]])&np.isfinite(av[ei[within]])&(av[ei[within]]>0)
 qa['missing_entry']+=int((~entryok).sum())
 histok=ni>=0;histok&=(g.notice.to_numpy()-d.index[np.maximum(ni,0)].to_numpy())/np.timedelta64(1,'D')<=7
 qa['missing_history']+=int((entryok&~histok).sum());keep=entryok&histok
 q=g.loc[keep].copy();ei=ei[keep];ni=ni[keep]
 if not len(q):continue
 sk=cal.searchsorted(q.endpoint,side='right')-1;ck=cal.searchsorted(q.notice,side='right')-1
 q['prior_stock_index']=ni;q['entry_date']=cal[ei];q['entry_index']=ei;q['entry_open']=ao[ei];q['stat_index']=sk;q['stat_date']=cal[sk];q['stat_close']=ac[sk];q['price_first_date']=d.index.min();q['price_last_date']=d.index.max();q['price_history_5y']=bool(d.index.min()+pd.DateOffset(years=5)<=d.index.max())
 q['public_feature_start_date']=[cal[k-60] if k>=60 else pd.NaT for k in ck];q['public_feature_end_date']=cal[ck]
 q['mom60']=np.where(ck>=60,ac[ck]/ac[np.maximum(ck-60,0)]-1,np.nan);q['stat_mom60']=np.where(sk>=60,ac[sk]/ac[np.maximum(sk-60,0)]-1,np.nan)
 q['legacy_mom60']=d.close.pct_change(60).iloc[ni].to_numpy()
 ix=ei[:,None]+offset;valid=ix<N;P=np.where(valid,ac[np.minimum(ix,N-1)]/ao[ei,None]-1,np.nan).astype('float32');q['public_entry_day_close_return']=P[:,0];P[:,0]=0
 ix=sk[:,None]+offset;valid=ix<N;S=np.where(valid,ac[np.minimum(ix,N-1)]/ac[sk,None]-1,np.nan).astype('float32')
 q['balanced250']=np.isfinite(P).all(axis=1);q['stat_balanced250']=np.isfinite(S).all(axis=1);q['matched_balanced250']=q.balanced250&q.stat_balanced250;q['holder_sign']=np.where(q.holder_delta<0,'decline',np.where(q.holder_delta>0,'rise','unchanged'))
 for h in H:q[f'returns_{h}']=P[:,h];q[f'stat_return_{h}']=S[:,h]
 frames.append(q);paths_public.append(P);paths_stat.append(S)
 if len(frames)%50==0:print('built stocks',len(frames),'events',sum(len(x) for x in frames),flush=True)
p=pd.concat(frames,ignore_index=True);p.insert(0,'event_id',np.arange(len(p)));P=np.concatenate(paths_public);S=np.concatenate(paths_stat)
p.to_csv(ROOT/'statdate_only/event_panel_statdate.csv',index=False);p.to_csv(ROOT/'model/event_panel.csv',index=False)
np.savez_compressed(ROOT/'statdate_only/daily_paths_statdate.npz',event_id=p.event_id.to_numpy(),public_nextopen_returns=P,stat_returns=S)
fcols=['event_id','code','notice','public_feature_start_date','public_feature_end_date','legacy_mom60','mom60','stat_mom60'];p[fcols].to_csv(ROOT/'threshold_curves/ranges_uniform60/lookback_feature_audit.csv',index=False)
base=p.matched_balanced250.to_numpy()&np.isfinite(p.mom60)&np.isfinite(p.stat_mom60)&(p.holder_delta!=0)
cols=['event_id','code','notice','endpoint','entry_date','stat_date','holder_delta','mom60','stat_mom60','legacy_mom60','public_feature_start_date','public_feature_end_date'];p.loc[base,cols].to_csv(ROOT/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv',index=False)
summary={'holders':hqa,'prices':qa,'event_panel_records':len(p),'event_panel_stocks':int(p.code.nunique()),'event_panel_stocks_with_5year_price_span':int(p.loc[p.price_history_5y,'code'].nunique()),'selected_pool':1494,'valid_main_pool':1494,'pool_codes_without_panel':sorted(set(pd.read_csv(ROOT/'qualified_pool.csv',dtype={'code':str}).code)-set(p.code)),'interim_membership_not_final_N60':True,'matched_nonzero_complete250':int(base.sum()),'matched_nonzero_stocks':int(p.loc[base,'code'].nunique()),'notice_min':str(p.loc[base,'notice'].min()),'notice_max':str(p.loc[base,'notice'].max()),'source_calendar':'frozen original market calendar dates only, no index return read'}
(ROOT/'model/panel_qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
