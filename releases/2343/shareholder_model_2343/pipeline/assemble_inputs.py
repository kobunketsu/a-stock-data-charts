"""Offline input assembly. No network; never overwrite a differing frozen input."""
from pathlib import Path
import argparse,csv,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--old-root',type=Path,required=True);p.add_argument('--price-capture',type=Path,required=True);p.add_argument('--root',type=Path,required=True);a=p.parse_args();R=a.root;OLD=a.old_root;C=a.price_capture
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy_same(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert sha(src)==sha(dst),'Differing existing input: '+str(dst)
 else:shutil.copyfile(src,dst)
old={x['code'] for x in csv.DictReader((R/'frozen_old1494.csv').open())};pool={x['code'] for x in csv.DictReader((R/'qualified_pool.csv').open())};added=pool-old;assert len(old)==1494 and len(pool)==2343 and len(added)==849
m=json.loads((C/'manifest.json').read_text());assert m['planned']==849 and not m['stop_on_refusal'];result={x['code']:x for x in m['results']};assert set(result)==added
assert not (C/'STOPPED_ON_REFUSAL.json').exists() and not (C.parent.parent/'GLOBAL_STOP.json').exists(),'Refusal remains unresolved'
rows=[]
for c in sorted(old):
 src=OLD/'prices'/f'{c}.csv';assert src.is_file();copy_same(src,R/'prices'/f'{c}.csv');rows.append({'code':c,'status':'reused','sha256':sha(src),'origin':'frozen1494'})
for c in sorted(added):
 j=result[c];assert j['status'] in ['ok','empty_no_price'],f'Incomplete capture {c}: {j["status"]}'
 success=json.loads((C/'success'/f'{c}.json').read_text());assert success==j,'Manifest differs from terminal success record'
 for suffix,key in [('_full.js','raw_sha256'),('_hfq.txt','factor_sha256')]:assert sha(C/'raw_prices'/(c+suffix))==j[key]
 if j['status']=='ok':
  src=C/'prices'/f'{c}.csv';assert sha(src)==j['csv_sha256'];copy_same(src,R/'prices'/f'{c}.csv');rows.append({'code':c,'status':'ok','sha256':j['csv_sha256'],'origin':'added849_capture'})
 else:
  assert j['rows']==0 and not (C/'prices'/f'{c}.csv').exists() and not (R/'prices'/f'{c}.csv').exists();rows.append({'code':c,'status':'empty_no_price','origin':'added849_capture','reason':'source_returned_no_usable_prices_in_requested_interval','raw_sha256':j['raw_sha256'],'factor_sha256':j['factor_sha256']})
copy_same(OLD/'absolute_only/trading_calendar.csv',R/'absolute_only/trading_calendar.csv')
h=json.loads((R/'HOLDER_RECOVERY_AUDIT.json').read_text());assert h['status']=='complete','Holder merge not complete'
files=['holders/events_raw.csv','holders_baseline_2009/events_raw.csv','absolute_only/trading_calendar.csv'];hashes={f:sha(R/f) for f in files}
manifest={'status':'complete','stop_on_refusal':False,'refusal':None,'prices':rows,'holder_codes_accounted':sorted(pool),'frozen_old1494_codes':sorted(old),'input_sha256':hashes,'price_capture_manifest_sha256':sha(C/'manifest.json'),'holder_merge_audit_sha256':sha(R/'HOLDER_RECOVERY_AUDIT.json'),'note':'Capture completeness is not model eligibility or independent numerical audit.'}
p=R/'INPUT_COMPLETENESS.json';s=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
if p.exists():assert p.read_text()==s,'Existing completeness differs; review required'
else:p.write_text(s)
print(json.dumps({'status':'INPUTS_ASSEMBLED_NOT_MODEL_AUDITED','pool':2343,'price_available':sum(x['status']!='empty_no_price' for x in rows),'source_empty_prices':sum(x['status']=='empty_no_price' for x in rows)},ensure_ascii=False))
