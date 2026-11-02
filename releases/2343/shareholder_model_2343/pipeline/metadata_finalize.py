"""Finalize only metadata after run_offline ends; update15-file SHA manifest without changing statistics."""
from pathlib import Path
import argparse,json,hashlib
from metadata_policy import finalize_metadata
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);P.add_argument('--apply',action='store_true');a=P.parse_args();B=a.root.resolve();manifest=B/'DELIVERY_MANIFEST.json'
assert manifest.exists() and (B/'comparison/SUMMARY.json').exists(),'Wait for completed offline run; never rewrite files while aggregators are writing'
assert json.load(open(B/'OLD1494_NONOVERLAP.json'))['status']=='PASS';delivery=json.load(open(manifest));assert len(delivery['files'])==15 and delivery['status']=='computed_wait_independent_audit_no_publication'
def dump(j):return json.dumps(j,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
changes=[]
for n in [10,20,30,60,120]:
 R=B/'lookbacks'/f'lookback_{n}'
 for kind in ['holder_matrix_9rows','holder_matrix_9rows_2020plus','stability']:
  files=[R/kind/'stability_ui.json'] if kind=='stability' else [R/kind/'curves_ui.json',R/kind/'curves.json',R/kind/'metadata.json']
  for p in files:
   raw=p.read_bytes();j=json.loads(raw);meta=j if p.name=='metadata.json' else j['metadata'];before=dump({k:v for k,v in j.items() if k!='metadata'}) if p.name!='metadata.json' else None
   finalize_metadata(meta,B,periods=j.get('periods') if kind=='stability' else None)
   if before is not None:assert dump({k:v for k,v in j.items() if k!='metadata'})==before,'Nonmetadata changed'
   cooked=dump(j);changes.append({'file':str(p.relative_to(B)),'before_sha256':sha(raw),'after_sha256':sha(cooked),'non_metadata_unchanged':True,'non_metadata_payload_sha256_before':sha(before) if before is not None else None,'non_metadata_payload_sha256_after':sha(dump({k:v for k,v in j.items() if k!='metadata'})) if before is not None else None})
   if a.apply:p.write_bytes(cooked)
if a.apply:
 for f in delivery['files']:
  p=Path(f['path']);f['sha256']=sha(p.read_bytes())
 delivery['metadata_finalization']='expanded2343-frozen1494-added849-v1';manifest.write_text(json.dumps(delivery,indent=2));(B/'METADATA_FINALIZE_AUDIT.json').write_text(json.dumps({'status':'PASS_METADATA_ONLY','files':changes,'all_statistics_membership_and_prices_unchanged':True},indent=2))
print(json.dumps({'mode':'APPLIED' if a.apply else 'DRY_RUN','files':len(changes),'metadata_only':True}))
