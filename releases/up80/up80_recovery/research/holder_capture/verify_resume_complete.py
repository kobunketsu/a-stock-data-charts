from pathlib import Path
import json,hashlib,collections,datetime
p=Path(__file__).resolve().parent
m=json.loads((p/'CAPTURE_MANIFEST.json').read_text());assert m['status']=='complete' and not m['errors'] and not m['stop_on_refusal']
frozen=json.loads((p/'RESUME_FROZEN_PAGES.json').read_text());assert len(frozen['files'])==216
for x in frozen['files']:assert hashlib.sha256((p/x['file']).read_bytes()).hexdigest()==x['sha256']
groups=collections.defaultdict(list)
for x in m['files']:
 b=(p/x['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==x['sha256'];r=json.loads(b)['result'];assert len(r['data'])==x['rows'];groups[x['name']].append(x)
for name,fs in groups.items():
 assert len({x['count'] for x in fs})==1
 assert len({x['pages'] for x in fs})==1
 assert sorted(x['page'] for x in fs)==list(range(1,fs[0]['pages']+1))
 assert sum(x['rows'] for x in fs)==fs[0]['count']
qa={'status':'complete','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_216_pages_bytes_unchanged':True,'pages':len(m['files']),'groups':len(groups),'all_page_hashes_and_counts_verified':True,'all_group_page_sequences_complete':True,'counts':m['counts'],'capture_manifest_sha256':hashlib.sha256((p/'CAPTURE_MANIFEST.json').read_bytes()).hexdigest(),'original_checkpoint_sha256':hashlib.sha256((p/'CAPTURE_CHECKPOINT.json').read_bytes()).hexdigest()}
(p/'RESUME_COMPLETE_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
