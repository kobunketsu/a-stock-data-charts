from pathlib import Path
import json,zipfile,hashlib
R=Path('./up80_checkpoint');S=R.parent;rows=[json.loads(x) for x in (R/'FILE_MANIFEST.jsonl').read_text().splitlines()];assert len({x['file'] for x in rows})==len(rows);expected={x['file']:x for x in rows};qa=json.load(open(R/'CHECKPOINT_QA.json'));seen=set();total=0;baseline=0;changed=0
for p in qa['parts']:
 f=R/p['file'];assert f.stat().st_size<45*1024**2;assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256'];z=zipfile.ZipFile(f);assert z.testzip() is None
 for info in z.infolist():
  name=info.filename;assert not Path(name).is_absolute() and '..' not in Path(name).parts
  if 'DATA_' not in f.name:continue
  assert name not in seen;seen.add(name);r=expected[name];assert r['part']==f.name;raw=z.read(name);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];source=(S/name).read_bytes();assert len(source)==r['source_bytes'] and hashlib.sha256(source).hexdigest()==r['source_sha256'];assert r['changed_in_packaging']==(raw!=source);changed+=int(raw!=source);total+=len(raw)
  if name.startswith('positive80_audit/baseline/'):
   assert raw==source;baseline+=1
assert seen==set(expected)
readme=(R/'README_不完整恢复检查点.md').read_text();assert all(x in readme for x in ['不是已完成模型','1200','294','1605','9000','网络已停止','不可直接发布'])
missing=[json.loads(x) for x in (S/'up80_recovery/research/missing_results.jsonl').read_text().splitlines()];assert len(missing)==522 and sum(x['status']=='ok' for x in missing)==228;assert sum('403' in str(x.get('error','')) for x in missing)==294
hc=json.load(open(S/'up80_recovery/research/holder_capture/CAPTURE_CHECKPOINT.json'));assert hc['status']=='stopped_access_refusal_incomplete' and hc['categories']['det_old_early']['missing_vs_historical_expected_rows']==1605 and hc['categories']['f10_all']['rows']==9000
out={'status':'PASS_ARCHIVE_INTEGRITY_ONLY_RESEARCH_BLOCKED','parts':len(qa['parts']),'manifest_files':len(seen),'uncompressed_bytes_verified':total,'baseline_files_byte_exact':baseline,'declared_packaging_redactions':changed,'all_member_hashes_and_source_hashes_verified':True,'missing_prices':294,'missing_old_early_DET_rows':1605,'F10_partial_rows':9000,'no_network_calls':True,'publication_authorized':False};(R/'INDEPENDENT_CHECKPOINT_AUDIT.json').write_text(json.dumps(out,indent=2));print(out)
