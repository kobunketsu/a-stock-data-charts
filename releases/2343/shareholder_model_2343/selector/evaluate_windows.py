"""Compare frozen-universe rolling-quarter disclosure pools; no outcome input, no network."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np,pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--sources',nargs='+',required=True,help='Complete row arrays, mutually exclusive notice intervals');ap.add_argument('--earliest',required=True);a=ap.parse_args();R=Path(__file__).resolve().parent
assert pd.Timestamp(a.earliest).day==1, 'Earliest must be a calendar-month start'
plan={x['id']:x for x in json.loads((R/'SEGMENT_PLAN.json').read_text())}
coverage=[]
for source in map(Path,a.sources):
 wm=json.loads((source.parent/'MANIFEST.json').read_text());assert wm['status']=='complete'
 assert hashlib.sha256(source.read_bytes()).hexdigest()==wm['sha256']
 for part in wm['sources']:
  sp=plan[part['segment']];folder=R/'segments'/part['segment']/'raw_capture'
  cm=json.loads((folder/'CAPTURE_MANIFEST.json').read_text())
  assert cm['status']=='complete' and not cm['errors'] and cm['closing_probe_count_pages_and_first_page_equal']
  segment=(folder/'all_raw.json').read_bytes();assert hashlib.sha256(segment).hexdigest()==part['sha256']==cm['all_raw_sha256']
  sr=json.loads(segment);assert len(sr)==part['rows']==cm['count']
  assert all(sp['start']<=x['HOLD_NOTICE_DATE'][:10]<=sp['end'] for x in sr)
  coverage.append((pd.Timestamp(sp['start']),pd.Timestamp(sp['end'])))
coverage.sort();assert coverage[0][0]==pd.Timestamp(a.earliest) and coverage[-1][1]==pd.Timestamp('2026-10-31')
assert all(a1+pd.Timedelta(days=1)==b0 for (_,a1),(b0,_) in zip(coverage,coverage[1:])), 'Incomplete/overlapping source intervals'
raw=pd.concat([pd.DataFrame(json.loads(Path(f).read_text())) for f in a.sources],ignore_index=True)
required=['SECURITY_CODE','SECURITY_NAME_ABBR','END_DATE','HOLD_NOTICE_DATE','HOLDER_NUM'];assert set(required)<=set(raw.columns)
raw.SECURITY_CODE=raw.SECURITY_CODE.astype(str).str.zfill(6)
for c in ['END_DATE','HOLD_NOTICE_DATE']:raw[c]=pd.to_datetime(raw[c]).dt.normalize()
registry=pd.DataFrame(json.loads((R/'frozen_registry_5577.json').read_text()));reg=registry[~registry.SECURITY_NAME_ABBR.str.contains('退',na=False)];listed=set(reg.SECURITY_CODE);names=dict(zip(reg.SECURITY_CODE,reg.SECURITY_NAME_ABBR));old=set(pd.read_csv(R/'old_1494.csv',dtype={'code':str}).code)
assert len(listed)==5554
assert not raw.duplicated(['SECURITY_CODE','END_DATE','HOLD_NOTICE_DATE']).any(), 'Duplicated source keys: inspect source overlap; do not silently deduplicate repeated ranges'
valid=raw[raw.SECURITY_CODE.isin(listed)&raw.SECURITY_CODE.str.startswith(('0','3','6','8','92','43'))&(raw.END_DATE<=raw.HOLD_NOTICE_DATE)].copy()
last=pd.Timestamp('2026-10-31');windows=[];metrics=[];passing={}
for end in pd.date_range(pd.Timestamp(a.earliest)+pd.offsets.MonthEnd(3),last,freq='ME'):
 start=(end-pd.DateOffset(months=2)).replace(day=1)
 d=valid[valid.HOLD_NOTICE_DATE.between(start,end)].copy()
 d=d.sort_values(['SECURITY_CODE','END_DATE','HOLD_NOTICE_DATE']).drop_duplicates(['SECURITY_CODE','END_DATE'])
 d=d.sort_values(['SECURITY_CODE','HOLD_NOTICE_DATE','END_DATE']).groupby(['SECURITY_CODE','HOLD_NOTICE_DATE'],sort=False).tail(1).sort_values(['SECURITY_CODE','HOLD_NOTICE_DATE'])
 frontier=d.groupby('SECURITY_CODE').END_DATE.cummax().groupby(d.SECURITY_CODE).shift()
 d=d[d.END_DATE>frontier.fillna(pd.Timestamp('1900-01-01'))]
 g=d.groupby('SECURITY_CODE').HOLD_NOTICE_DATE.agg(events='size',first='min',last='max')
 g['span']=(g['last']-g['first']).dt.days;g['mean_gap']=g.span/(g.events-1);g['last_gap']=(end-g['last']).dt.days;g['first_gap']=(g['first']-start).dt.days
 gaps=d.groupby('SECURITY_CODE').HOLD_NOTICE_DATE.diff().dt.days;g['max_gap']=gaps.groupby(d.SECURITY_CODE).max()
 g['qualifies']=(g.events>=3)&(g.span>=60)&(g.mean_gap<=30)&(g.last_gap<=30)
 label=str(end.date());passing[label]=set(g.index[g.qualifies]);g=g.reset_index().rename(columns={'SECURITY_CODE':'code'});g['window_start']=str(start.date());g['window_end']=label;metrics.append(g)
 windows.append({'window_start':str(start.date()),'window_end':label,'qualifying_stocks':len(passing[label])})
M=pd.concat(metrics,ignore_index=True);M.to_csv(R/f'window_metrics_from_{a.earliest}.csv',index=False)
summary={'status':'calculated_wait_independent_audit','coverage_intervals_verified':[[str(a.date()),str(b.date())] for a,b in coverage],'source_first':str(raw.HOLD_NOTICE_DATE.min().date()),'source_last':str(raw.HOLD_NOTICE_DATE.max().date()),'source_rows':len(raw),'source_stocks':int(raw.SECURITY_CODE.nunique()),'negative_lag_rows':int((raw.END_DATE>raw.HOLD_NOTICE_DATE).sum()),'frozen_registry':5554,'source_rows_outside_frozen_registry':int((~raw.SECURITY_CODE.isin(listed)).sum()),'source_codes_outside_frozen_registry':sorted(set(raw.SECURITY_CODE)-listed),'snapshots':[{'file':str(Path(f).resolve()),'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()} for f in a.sources],'windows':windows,'alternatives':[]}
for start in ['2024-10-01','2023-10-01','2020-10-01','2015-10-01']:
 if start<a.earliest:continue
 first=(pd.Timestamp(start)+pd.offsets.MonthEnd(3)).strftime('%Y-%m-%d');keys=[k for k in passing if k>=first];pool=set().union(*(passing[k] for k in keys));p=pd.DataFrame([{'code':c,'name':names[c],'qualifying_windows':sum(c in passing[k] for k in keys),'first_qualified_window':next(k for k in keys if c in passing[k]),'last_qualified_window':next(k for k in reversed(keys) if c in passing[k]),'in_old1494':c in old} for c in sorted(pool)])
 p.to_csv(R/f'pool_from_{start}.csv',index=False)
 item={'start':start,'end':'2026-10-31','calendar_months':(2026-pd.Timestamp(start).year)*12+10-pd.Timestamp(start).month+1,'complete_windows':len(keys),'pool':len(pool),'retained_old1494':len(pool&old),'added_to_old1494':len(pool-old),'missing_old1494':sorted(old-pool),'exactly_one_window':int((p.qualifying_windows==1).sum()),'last_window_pass':len(passing['2026-10-31']),'code_set_sha256':hashlib.sha256('\n'.join(sorted(pool)).encode()).hexdigest()}
 added=p[~p.in_old1494]
 item['added_exactly_one_window']=int((added.qualifying_windows==1).sum())
 item['added_last_qualified_before2020']=int((added.last_qualified_window<'2020-01-01').sum())
 item['added_last_qualified_before2023']=int((added.last_qualified_window<'2023-01-01').sum())
 item['qualifying_window_count_distribution']={str(k):int(v) for k,v in p.qualifying_windows.value_counts().sort_index().items()}
 if start=='2024-10-01':item['legacy_B23_exact_set_match']=pool==old;item['legacy_B23_source_rows']=int((raw.HOLD_NOTICE_DATE>=start).sum());item['legacy_B23_expected_rows']=111472
 summary['alternatives'].append(item)
(R/f'COMPARISON_FROM_{a.earliest}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k not in ['windows','snapshots']},ensure_ascii=False,indent=2),flush=True)
