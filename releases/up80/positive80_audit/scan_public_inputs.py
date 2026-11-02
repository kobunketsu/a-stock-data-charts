from pathlib import Path
import zipfile,re,json,gzip
R=Path('./up80_complete_package');patterns={'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','aws_access':rb'AKIA[0-9A-Z]{16}','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{25,})','openai_key':rb'sk-(?:proj-)?[A-Za-z0-9_-]{35,}','bearer_token':rb'Bearer [A-Za-z0-9_.-]{30,}'};hits=[];checked=0;paths=[]
for p in sorted(R.glob('*.zip')):
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if any(x in {'.git','.openai','.aws','.codex'} for x in Path(name).parts):paths.append(name)
   if Path(name).suffix.lower() not in {'.json','.jsonl','.txt','.md','.py','.js','.html','.csv','.gz'}:continue
   raw=z.read(name)
   if Path(name).suffix.lower()=='.gz':raw=gzip.decompress(raw)
   checked+=1
   for label,pat in patterns.items():
    if re.search(pat,raw):hits.append({'file':name,'pattern':label})
assert not hits and not paths,(hits,paths)
out={'status':'PASS_PATTERN_SCAN','text_members_scanned':checked,'credential_pattern_hits':hits,'private_deployment_directory_hits':paths,'limits':'Pattern scan is a safety check, not a proof that every possible secret format is absent. No raw credential matches printed.'};(R/'INDEPENDENT_PUBLIC_SCAN.json').write_text(json.dumps(out,indent=2));print(out)
