from pathlib import Path
import json,pandas as pd,numpy as np,hashlib,collections,re
R=Path('./up80_recovery/research');A=R.parent/'archive972/shareholder_system_972';H=R/'holder_capture';cap=json.load(open(H/'CAPTURE_MANIFEST.json'));assert cap['status']=='complete' and not cap['errors'] and not cap['stop_on_refusal'];files=cap['files'];assert len(files)==343;pagegroups=collections.defaultdict(list)
for f in files:
 raw=(H/f['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];j=json.loads(raw);assert j['success'] and j['result'] is not None;prefix,num=re.match(r'(.+)_page(\d+)\.json',f['file']).groups();pagegroups[prefix].append((int(num),j['result']))
for g,seq in pagegroups.items():
 seq.sort();assert [x[0] for x in seq]==list(range(1,seq[0][1]['pages']+1));assert sum(len(x[1]['data']) for x in seq)==seq[0][1]['count']
oldpages=json.load(open(H/'CAPTURE_CHECKPOINT.json'))['pages'];assert len(oldpages)==216
for f in oldpages:assert hashlib.sha256((H/f['file']).read_bytes()).hexdigest()==f['sha256']
pool=set(pd.read_csv(R/'qualified_pool.csv',dtype={'code':str}).code);m=pd.read_csv(R/'holders/events_raw.csv',dtype=str,keep_default_na=False);base=pd.read_csv(R/'holders_baseline_2009/events_raw.csv',dtype=str,keep_default_na=False);assert len(m)==241976 and set(m.SECURITY_CODE)==pool and len(pool)==1494;assert len(base)==1465 and base.SECURITY_CODE.nunique()==377;key=['SECURITY_CODE','END_DATE','HOLD_NOTICE_DATE'];assert not m.duplicated(key).any();assert not base.duplicated(key).any()
oldpool=set(pd.read_csv(A/'qualified_972.csv',dtype={'code':str}).code);old=pd.concat([pd.read_csv(A/'holders/events_raw.csv',dtype=str,keep_default_na=False),pd.read_csv(A/'holders_baseline_2019/events_raw.csv',dtype=str,keep_default_na=False)],ignore_index=True);old=old[old.SECURITY_CODE.isin(oldpool)];assert len(old)==137345;assert not old.duplicated(key).any();both=old.merge(m,on=key,how='left',suffixes=('_old','_new'),validate='one_to_one',indicator=True);assert (both['_merge']=='both').all();fields=[]
for k in old.columns:
 if k in key:continue
 a=both[k+'_old'];b=both[k+'_new'];an=pd.to_numeric(a,errors='coerce');bn=pd.to_numeric(b,errors='coerce');ok=(a==b)|(an.notna()&bn.notna()&(an==bn));assert ok.all(),(k,both.loc[~ok,key+[k+'_old',k+'_new']].head().to_dict('records'));fields.append(k)
neg=(pd.to_datetime(m.HOLD_NOTICE_DATE)<pd.to_datetime(m.END_DATE)).sum();out={'status':'PASS_SOURCE_RECOVERY_ONLY','main_rows':len(m),'stocks':len(pool),'baseline_rows':len(base),'pages_hash_and_sequences_verified':len(files),'old216_pages_unchanged':True,'old972_frozen_rows':len(old),'old_fields_verified':fields,'negative_lag_raw':int(neg),'limitation':'Does not establish unavailable old1494 full individual-event membership; published old8 regression still required.'};Path(__file__).with_name('recovered_holders_independent.json').write_text(json.dumps(out,indent=2));print(out)
