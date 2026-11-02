"""Offline-only added849 merge. Frozen1494 CSV bytes preserved as prefix; no fetching."""
from pathlib import Path
import argparse,csv,json,gzip,hashlib,io,math,datetime,collections
p=argparse.ArgumentParser();p.add_argument('--capture-root',type=Path,required=True);p.add_argument('--old-root',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();C=a.capture_root.resolve();OLD=a.old_root.resolve();OUT=a.output_root.resolve();assert OUT!=OLD and OLD not in OUT.parents,'Choose separate output root, not frozen old research tree';OUT.mkdir(parents=True,exist_ok=True)
def sh(b):return hashlib.sha256(b).hexdigest()
frozen=json.loads((Path(__file__).resolve().parent/'FROZEN1494_INPUT_SHA.json').read_text())
for rel,digest in frozen.items():assert sh((OLD/rel).read_bytes())==digest,f'Frozen1494 input mismatch: {rel}'
def number(v):
 try:
  x=float(v);return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
def day(v):
 try:return datetime.date.fromisoformat(str(v)[:10]).isoformat()
 except (ValueError,TypeError):return None
def key(x):return x['SECURITY_CODE'],day(x.get('END_DATE'))
added={x['code'] for x in csv.DictReader((C/'added_849.csv').open())};assert len(added)==849
reuseqa=json.loads((C/'REUSE_QA.json').read_text());reusegzip=(C/'reused_added849_DET_metadata.json.gz').read_bytes();assert sh(reusegzip)==reuseqa['reuse_gzip_sha256'];reusebytes=gzip.decompress(reusegzip);assert sh(reusebytes)==reuseqa['reused_added849_sha256'];det=json.loads(reusebytes);assert len(det)==69054 and {x['SECURITY_CODE'] for x in det}==added
cap=json.loads((C/'CAPTURE_COMPLETE.json').read_text());assert cap['status']=='complete' and not cap['errors'] and len(cap['results'])==18
expected_jobs={j['id']:j for j in json.loads((C/'REQUEST_PLAN.json').read_text())['jobs']};assert len(expected_jobs)==18 and {j['job']['id'] for j in cap['results']}==set(expected_jobs)
for j in cap['results']:assert j['job']==expected_jobs[j['job']['id']],'Capture job differs from frozen request plan'
f10=[];provenance=[]
for result in cap['results']:
 j=result['job'];folder=C/'captured'/j['id'];assert result['status']=='complete';raw=(folder/'all_raw.json').read_bytes();assert sh(raw)==result['sha256'];rs=json.loads(raw);assert len(rs)==result['rows'];assert {x['SECURITY_CODE'] for x in rs}<=added
 page_items=json.loads((folder/'page_manifest.json').read_text());assert sorted(x['page'] for x in page_items)==list(range(1,max(1,result['pages'])+1));assert sum(x['rows'] for x in page_items)==result['rows']
 for item in page_items:
  b=(folder/item['file']).read_bytes();assert sh(b)==item['sha256'];d=json.loads(b).get('result') or {'count':0,'pages':0,'data':[]};assert d['count']==result['rows'] and d['pages']==result['pages'];assert len(d.get('data') or [])==item['rows']
 assert sh((folder/'closing_probe.json').read_bytes())==result['closing_probe']['sha256']
 if j['table']=='RPT_HOLDERNUM_DET':
  assert j['end']=='2015-09-30';assert all('2009-01-01'<=day(x['HOLD_NOTICE_DATE'])<='2015-09-30' for x in rs);det.extend(rs)
 else:
  assert j['table']=='RPT_F10_EH_HOLDERNUM' and j['end']=='2026-10-31';f10.extend(rs)
 provenance.append({'job':j['id'],'table':j['table'],'rows':len(rs),'sha256':sh(raw)})
assert {x['SECURITY_CODE'] for x in det}==added
byendpoint=collections.defaultdict(list)
for x in det:byendpoint[key(x)].append(x)
auditdir=OUT/'holder_merge_audit';auditdir.mkdir(exist_ok=True);overlap=[];missingA=[];invaliddate=[];supplement=[];duplicate_f10=[];seen=set()
for x in f10:
 k=key(x);num=number(x.get('HOLDER_A_NUM'));notice=day(x.get('NOTICE_DATE'));endpoint=day(x.get('END_DATE'));matches=byendpoint.get(k,[])
 if matches:
  overlap.append({'code':x['SECURITY_CODE'],'endpoint':endpoint,'F10_notice':notice,'F10_A':x.get('HOLDER_A_NUM'),'F10_TOTAL':x.get('HOLDER_TOTAL_NUM'),'F10_B':x.get('HOLDER_B_NUM'),'F10_H':x.get('HOLDER_H_NUM'),'DET_record_count':len(matches),'A_matches_any_DET':any(number(d.get('HOLDER_NUM'))==num for d in matches),'notice_matches_any_DET':any(day(d.get('HOLD_NOTICE_DATE'))==notice for d in matches),'joint_matches_any_DET':any(number(d.get('HOLDER_NUM'))==num and day(d.get('HOLD_NOTICE_DATE'))==notice for d in matches),'DET_records':[{'notice':d.get('HOLD_NOTICE_DATE'),'HOLDER_NUM':d.get('HOLDER_NUM')} for d in matches]})
 if num is None or num<=0:missingA.append(x);continue
 if notice is None or endpoint is None or endpoint>notice:invaliddate.append(x);continue
 if matches:continue
 # Multiple valid F10 disclosures at an endpoint are retained as raw observations, exact duplicates only removed with audit.
 identity=(x['SECURITY_CODE'],notice,endpoint,num)
 if identity in seen:duplicate_f10.append(x);continue
 seen.add(identity);z=dict(x);z['HOLDER_NUM']=x['HOLDER_A_NUM'];z['HOLD_NOTICE_DATE']=x['NOTICE_DATE'];z['TOTAL_A_SHARES']=None;z['SOURCE_TABLE']='RPT_F10_EH_HOLDERNUM';z['SOURCE_NOTICE_FIELD']='NOTICE_DATE';z['SOURCE_HOLDER_FIELD']='HOLDER_A_NUM';z['SOURCE_NOTICE_VERIFICATION']='provider_date_not_full_primary_notice_verification';supplement.append(z)
for x in det:
 x['TOTAL_A_SHARES']=x.get('TOTAL_A_SHARES');x['SOURCE_TABLE']='RPT_HOLDERNUM_DET';x['SOURCE_NOTICE_FIELD']='HOLD_NOTICE_DATE';x['SOURCE_HOLDER_FIELD']='HOLDER_NUM';x['SOURCE_NOTICE_VERIFICATION']='provider_date_not_full_primary_notice_verification'
for name,rows in [('F10_DET_overlap',overlap),('F10_DET_conflicts_keep_DET',[x for x in overlap if not x['joint_matches_any_DET']]),('F10_missing_nonpositive_A',missingA),('F10_invalid_dates',invaliddate),('F10_exact_duplicate_records',duplicate_f10)]:
 (auditdir/f'{name}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
new=det+supplement;assert {x['SECURITY_CODE'] for x in new}==added
oldcodes={x['code'] for x in csv.DictReader((OLD/'qualified_pool.csv').open(encoding='utf-8-sig'))};assert len(oldcodes)==1494 and not(oldcodes&added)
manifest=[]
for folder,lower,upper in [('holders','2010-01-01','2026-10-31'),('holders_baseline_2009','2009-01-01','2009-12-31')]:
 old=OLD/folder/'events_raw.csv';oldbytes=old.read_bytes();assert oldbytes.endswith(b'\n');oldrows=list(csv.DictReader(io.StringIO(oldbytes.decode('utf-8-sig'))));columns=list(oldrows[0]);assert {x['SECURITY_CODE'] for x in oldrows}<=oldcodes
 rows=[x for x in new if lower<=str(x['HOLD_NOTICE_DATE'])[:10]<=upper];rows.sort(key=lambda x:(x['SECURITY_CODE'],x['HOLD_NOTICE_DATE'],x['END_DATE']))
 text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=columns,extrasaction='ignore');w.writerows({c:x.get(c) for c in columns} for x in rows)
 target=OUT/folder/'events_raw.csv';target.parent.mkdir(exist_ok=True);assert not target.exists(),'Never overwrite an existing merged artifact';target.write_bytes(oldbytes+text.getvalue().encode());assert target.read_bytes()[:len(oldbytes)]==oldbytes
 allrows=list(csv.DictReader(io.StringIO(target.read_text(encoding='utf-8-sig'))));assert allrows[:len(oldrows)]==oldrows and len(allrows)==len(oldrows)+len(rows)
 if folder=='holders':assert {x['SECURITY_CODE'] for x in allrows}==oldcodes|added
 manifest.append({'file':str(target.relative_to(OUT)),'old_rows':len(oldrows),'added_rows':len(rows),'total_rows':len(allrows),'old_bytes_exact_prefix':True,'old_sha256':sh(oldbytes),'merged_sha256':sh(target.read_bytes())})
qa={'status':'merged_pending_independent_audit','frozen1494':1494,'added849':849,'total_pool':2343,'reused_DET_rows':69054,'new_early_DET_rows':len(det)-69054,'F10_raw_rows':len(f10),'F10_added_endpoint_missing_DET_rows':len(supplement),'F10_overlap_rows':len(overlap),'overlap_joint_conflicts':sum(not x['joint_matches_any_DET'] for x in overlap),'F10_missing_nonpositive_A':len(missingA),'F10_invalid_dates':len(invaliddate),'F10_exact_duplicates_removed':len(duplicate_f10),'DET_source_precedence':True,'TOTAL_A_SHARES_unknown_not_inferred':True,'frozen1494_never_refetched':True,'input_captures':provenance,'outputs':manifest,'limits':['No source notice dates inferred from statistical endpoints','Provider dates not universally verified first-public dates','2015+ DET reused from completed metadata snapshot; missing endpoints supplemented only by valid F10 A records','Overlap conflicts retain DET and remain separately auditable']};(OUT/'HOLDER_MERGE_AUDIT.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False,indent=2))

recovery={**qa,'status':'complete','independent_audit_status':'pending','merge_status':qa['status'],'main_rows':manifest[0]['total_rows'],'main_stocks':2343,'baseline2009_rows':manifest[1]['total_rows'],'holder_codes_accounted':sorted(oldcodes|added),'frozen_old1494_codes':sorted(oldcodes),'frozen_old_input_sha256':frozen}
(OUT/'HOLDER_RECOVERY_AUDIT.json').write_text(json.dumps(recovery,ensure_ascii=False,indent=2))
