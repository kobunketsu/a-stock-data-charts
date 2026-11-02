from pathlib import Path
import json,pandas as pd,numpy as np
R=Path('./up80_recovery/research');p=pd.read_csv(R/'model/event_panel.csv',dtype={'code':str});z=dict(np.load(R/'statdate_only/daily_paths_statdate.npz'));assert np.array_equal(p.event_id,z['event_id']);cal=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(R/'absolute_only/trading_calendar.csv').date));err={};n=0
for code,g in p.groupby('code'):
 raw=pd.read_csv(R/f'prices/{code}.csv',parse_dates=['date']).set_index('date');raw=raw[(raw.open>0)&(raw.close>0)];v=raw.reindex(cal);c=v.close.to_numpy().copy();c[(v.volume<=0)|v.volume.isna()]=np.nan;o=v.open.to_numpy();ni=raw.index.searchsorted(pd.to_datetime(g.notice),side='right')-1;assert np.array_equal(ni,g.prior_stock_index);assert (((pd.to_datetime(g.notice).to_numpy()-raw.index[ni].to_numpy())/np.timedelta64(1,'D'))<=7).all();ei=cal.searchsorted(pd.to_datetime(g.notice),side='right');si=cal.searchsorted(pd.to_datetime(g.endpoint),side='right')-1;assert np.array_equal(ei,g.entry_index) and np.array_equal(si,g.stat_index);assert np.allclose(o[ei],g.entry_open,equal_nan=True) and np.allclose(c[si],g.stat_close,equal_nan=True)
 for idx,bp,key in [(ei,o[ei],'public_nextopen_returns'),(si,c[si],'stat_returns')]:
  ii=idx[:,None]+np.arange(251);w=c[np.minimum(ii,len(cal)-1)]/bp[:,None]-1;w[ii>=len(cal)]=np.nan
  if key.startswith('public'):w[:,0]=0
  w=w.astype('float32');a=z[key][g.index];assert np.array_equal(np.isfinite(w),np.isfinite(a));d=float(np.nanmax(abs(w-a))) if np.isfinite(w).any() else 0;assert d==0;err[key]=max(err.get(key,0),d)
 n+=len(g)
out={'status':'PASS','superset_rows':n,'stocks':p.code.nunique(),'all251_paths_rebuilt_from_actual_price_dates':True,'prior_stock_index_and_freshness_verified':True,'float32_errors':err};Path(__file__).with_name('superset_paths_independent.json').write_text(json.dumps(out,indent=2));print(out)
