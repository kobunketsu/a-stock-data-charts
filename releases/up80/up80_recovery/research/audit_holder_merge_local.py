from pathlib import Path
import pandas as pd,json,hashlib
r=Path(__file__).resolve().parent;a=r.parent/'archive972/shareholder_system_972'
old=set(pd.read_csv(a/'qualified_972.csv',dtype={'code':str}).code)
pool=set(pd.read_csv(r.parent/'qualified_1494.csv',dtype={'code':str}).code)
main=pd.read_csv(r/'holders/events_raw.csv',dtype={'SECURITY_CODE':str});base=pd.read_csv(r/'holders_baseline_2009/events_raw.csv',dtype={'SECURITY_CODE':str});rows=pd.concat([main,base],ignore_index=True)
assert set(rows.SECURITY_CODE)<=pool and set(main.SECURITY_CODE)==pool
srcs=[a/'holders/events_raw.csv',a/'holders_baseline_2019/events_raw.csv'];frozen=pd.concat([pd.read_csv(p,dtype={'SECURITY_CODE':str}) for p in srcs],ignore_index=True);frozen=frozen[frozen.SECURITY_CODE.isin(old)]
actual=main[main.SECURITY_CODE.isin(old)&(main.HOLD_NOTICE_DATE>='2019-01-01')]
k=['SECURITY_CODE','HOLD_NOTICE_DATE','END_DATE'];cols=list(frozen.columns)
pd.testing.assert_frame_equal(frozen[cols].sort_values(k).reset_index(drop=True),actual[cols].sort_values(k).reset_index(drop=True),check_dtype=False,check_exact=True)
f=rows[rows.SOURCE_TABLE=='RPT_F10_EH_HOLDERNUM'];assert (f.HOLDER_NUM>0).all() and (f.HOLD_NOTICE_DATE>=f.END_DATE).all() and f.TOTAL_A_SHARES.isna().all();assert (f.SOURCE_HOLDER_FIELD=='HOLDER_A_NUM').all()
d=rows[rows.SOURCE_TABLE!='RPT_F10_EH_HOLDERNUM'];assert not(set(map(tuple,f[['SECURITY_CODE','END_DATE']].values))&set(map(tuple,d[['SECURITY_CODE','END_DATE']].values)))
q={'status':'PASS','main_rows':len(main),'baseline_rows':len(base),'frozen_972_original_columns_exact':True,'frozen_rows':len(frozen),'f10_no_total_fallback':True,'f10_no_overlap_with_preferred_det_endpoints':True,'source_counts':rows.SOURCE_TABLE.value_counts().to_dict(),'files':[{'file':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [r/'holders/events_raw.csv',r/'holders_baseline_2009/events_raw.csv']]}
(r/'HOLDER_LOCAL_INDEPENDENT_QA.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
