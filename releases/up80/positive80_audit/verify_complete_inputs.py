from pathlib import Path
import json,zipfile,hashlib
R=Path('./up80_complete_package');S=R.parent;rows=[json.loads(x) for x in (R/'FILE_MANIFEST.jsonl').read_text().splitlines()];assert len({x['file'] for x in rows})==len(rows);expected={x['file']:x for x in rows};qa=json.load(open(R/'INPUT_PACKAGE_QA.json'));seen=set();total=0;baseline=0;changed=0
for p in qa['parts']:
 f=R/p['file'];assert f.stat().st_size<45*1024**2;assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256'];z=zipfile.ZipFile(f);assert z.testzip() is None
 for info in z.infolist():
  name=info.filename;assert not Path(name).is_absolute() and '..' not in Path(name).parts
  if 'DATA_' not in f.name:continue
  assert name not in seen;seen.add(name);r=expected[name];assert r['part']==f.name;raw=z.read(name);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];source=(S/name).read_bytes();assert len(source)==r['source_bytes'] and hashlib.sha256(source).hexdigest()==r['source_sha256'];assert r['changed_in_packaging']==(raw!=source);changed+=int(raw!=source);total+=len(raw)
  if name.startswith('positive80_audit/baseline/'):
   assert raw==source;baseline+=1
assert seen==set(expected)
assert qa['status']=='COMPLETE_INPUTS_OUTPUTS_PENDING'
price_members=[x for x in seen if x.startswith('up80_recovery/research/prices/') and x.endswith('.csv')];assert len(price_members)==1494
for name in seen:assert not any(part in {'.git','.openai','.aws','.codex','__pycache__'} for part in Path(name).parts)
out={'status':'PASS_COMPLETE_INPUT_ARCHIVE_ONLY','parts':len(qa['parts']),'manifest_files':len(seen),'uncompressed_bytes_verified':total,'research_price_csvs':len(price_members),'baseline_files_byte_exact':baseline,'declared_packaging_redactions':changed,'all_member_hashes_and_source_hashes_verified':True,'all_files_under45MiB':True,'no_network_calls':True,'source_code_and_final_outputs_are_separate_package':True};(R/'INDEPENDENT_INPUT_AUDIT.json').write_text(json.dumps(out,indent=2));print(out)
