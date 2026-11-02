from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parent
def holders(path):
 d=pd.read_csv(path,dtype={'SECURITY_CODE':str});main_rows=len(d)
 baseline=ROOT/'holders_baseline_2009/events_raw.csv'
 if baseline.exists():d=pd.concat([pd.read_csv(baseline,dtype={'SECURITY_CODE':str}),d],ignore_index=True)
 raw=len(d)
 d.SECURITY_CODE=d.SECURITY_CODE.str.zfill(6)
 for c in ['END_DATE','HOLD_NOTICE_DATE']:d[c]=pd.to_datetime(d[c]).dt.normalize()
 for c in ['HOLDER_NUM','TOTAL_A_SHARES']:d[c]=pd.to_numeric(d[c],errors='coerce')
 candidate_raw_rows=raw;candidate_main_rows=main_rows;candidate_negative_lag=int((d.END_DATE>d.HOLD_NOTICE_DATE).sum())
 pool=set(pd.read_csv(ROOT/'qualified_pool.csv',dtype={'code':str}).code)
 main_source=d.iloc[-candidate_main_rows:];main_negative_lag=int(((main_source.END_DATE>main_source.HOLD_NOTICE_DATE)&main_source.SECURITY_CODE.isin(pool)).sum())
 main_rows=int(main_source.SECURITY_CODE.isin(pool).sum());d=d[d.SECURITY_CODE.isin(pool)];raw=len(d)
 bad=int((d.END_DATE>d.HOLD_NOTICE_DATE).sum());d=d[(d.END_DATE<=d.HOLD_NOTICE_DATE)&(d.HOLDER_NUM>0)]
 pool=set(pd.read_csv(ROOT/'qualified_pool.csv',dtype={'code':str}).code);d=d[d.SECURITY_CODE.isin(pool)]
 d=d.sort_values(['SECURITY_CODE','END_DATE','HOLD_NOTICE_DATE']).drop_duplicates(['SECURITY_CODE','END_DATE'])
 rows=[];public=[];back=0
 for code,g in d.groupby('SECURITY_CODE'):
  history=[]
  for notice,s in g.groupby('HOLD_NOTICE_DATE',sort=True):
   r=s.sort_values('END_DATE').iloc[-1]
   if history and r.END_DATE<=history[-1].END_DATE:back+=1;continue
   public.append({'code':code,'notice':notice,'endpoint':r.END_DATE,'holder_num':r.HOLDER_NUM})
   if history:
    p=history[-1];gap=(r.END_DATE-p.END_DATE).days;lag=(notice-r.END_DATE).days
    if 1<=gap<=45 and lag<=30 and notice>=pd.Timestamp('2010-01-01'):
     delta=r.HOLDER_NUM/p.HOLDER_NUM-1
     rows.append(dict(code=code,notice=notice,endpoint=r.END_DATE,previous_endpoint=p.END_DATE,previous_notice=p.HOLD_NOTICE_DATE,holder_num=r.HOLDER_NUM,previous_holder_num=p.HOLDER_NUM,holder_delta=delta,holder_delta_10d=delta*10/gap,holder_trend3=r.HOLDER_NUM/history[-3].HOLDER_NUM-1 if len(history)>=3 else np.nan,trend3_start_notice=history[-3].HOLD_NOTICE_DATE if len(history)>=3 else pd.NaT,trend3_span_days=(notice-history[-3].HOLD_NOTICE_DATE).days if len(history)>=3 else np.nan,trend3_endpoint_span=(r.END_DATE-history[-3].END_DATE).days if len(history)>=3 else np.nan,trend3_max_gap=max((b.END_DATE-a.END_DATE).days for a,b in zip(history[-3:],[*history[-2:],r])) if len(history)>=3 else np.nan,three_declines=bool(len(history)>=3 and history[-3].HOLDER_NUM>history[-2].HOLDER_NUM>history[-1].HOLDER_NUM>r.HOLDER_NUM),three_rises=bool(len(history)>=3 and history[-3].HOLDER_NUM<history[-2].HOLDER_NUM<history[-1].HOLDER_NUM<r.HOLDER_NUM),endpoint_gap=gap,lag_days=lag,shares_change=r.TOTAL_A_SHARES/p.TOTAL_A_SHARES-1 if p.TOTAL_A_SHARES>0 else np.nan))
   history.append(r)
 events=pd.DataFrame(rows);pub=pd.DataFrame(public)
 return events,pub,dict(raw_rows=raw,candidate_raw_rows=candidate_raw_rows,candidate_main_2010plus_rows=candidate_main_rows,candidate_negative_lag_rows=candidate_negative_lag,main_2010plus_raw_rows=main_rows,baseline2009_raw_rows=raw-main_rows,negative_lag_excluded=bad,main_negative_lag_excluded=main_negative_lag,baseline_negative_lag_excluded=bad-main_negative_lag,backward_removed=back,public_advancing_records=len(pub),eligible_events=len(events))
