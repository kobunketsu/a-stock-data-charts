#!/usr/bin/env python3
"""Offline restore of the three frozen2343 dependency groups, without overwrites."""
from pathlib import Path, PurePosixPath
import argparse,json,hashlib,zipfile,stat,os,tempfile
REPO=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def safe(root,name):
 p=PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:raise ValueError('Unsafe archive path: '+name)
 dest=root/str(p)
 if dest.is_symlink() or not dest.resolve().is_relative_to(root):raise ValueError('Destination escapes root: '+name)
 return dest
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--catalog',type=Path,default=REPO/'datasets/2343/DEPENDENCY_LOCATIONS.json');p.add_argument('--repo-root',type=Path,default=REPO);p.add_argument('--destination',type=Path,default=REPO/'work/2343_inputs');p.add_argument('--groups',nargs='+',choices=['old_up80','new849_capture','complete_selector'],default=['old_up80','new849_capture','complete_selector']);p.add_argument('--check-only',action='store_true');a=p.parse_args()
 entries=[x for x in json.loads(a.catalog.read_text()) if x['group'] in a.groups];assert entries,'Empty dependency selection';seen={};writes=[];skipped=0
 # Preflight every archive and destination before installing any file.
 for item in entries:
  archive=a.repo_root/item['repo_path'];assert archive.stat().st_size==item['bytes'] and sha(archive)==item['sha256'],item['file']
  root=(a.destination/item['group']).resolve()
  with zipfile.ZipFile(archive) as z:
   for info in z.infolist():
    dest=safe(root,info.filename)
    if info.is_dir():continue
    assert stat.S_IFMT(info.external_attr>>16)!=stat.S_IFLNK and not info.flag_bits&1,'Unsupported ZIP entry'
    if a.check_only:continue
    h=hashlib.sha256()
    with z.open(info) as f:
     for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    digest=h.hexdigest();key=str(dest)
    if key in seen:
     assert seen[key]==digest,'Conflicting repeated archive path: '+info.filename
     continue
    seen[key]=digest
    if dest.exists():assert dest.is_file() and sha(dest)==digest,'Existing file differs: '+str(dest);skipped+=1
    else:writes.append((archive,info.filename,dest,digest))
 if not a.check_only:
  for archive,name,dest,digest in writes:
   dest.parent.mkdir(parents=True,exist_ok=True);fd,tmpname=tempfile.mkstemp(prefix='.2343-',dir=dest.parent);tmp=Path(tmpname)
   try:
    h=hashlib.sha256()
    with os.fdopen(fd,'wb') as out,zipfile.ZipFile(archive) as z,z.open(name) as src:
     for b in iter(lambda:src.read(1024*1024),b''):h.update(b);out.write(b)
    assert h.hexdigest()==digest
    os.link(tmp,dest)
   finally:tmp.unlink(missing_ok=True)
 print(json.dumps({'status':'PASS','archives':len(entries),'groups':a.groups,'check_only':a.check_only,'restored_files':len(writes) if not a.check_only else 0,'existing_exact_files_kept':skipped,'network_used':False}))
if __name__=='__main__':main()
