from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
bad=[];count=0
for line in (root/'FILE_MANIFEST.jsonl').read_text().splitlines():
 r=json.loads(line);p=root/r['file'];count+=1
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['file'])
print({'checked':count,'mismatches':bad,'status':'PASS' if not bad else 'FAIL'})
raise SystemExit(1 if bad else 0)
