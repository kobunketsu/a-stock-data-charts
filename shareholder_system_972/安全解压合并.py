#!/usr/bin/env python3
"""Safely merge this release's ordinary ZIPs. No network; never overwrite different files."""
import argparse,hashlib,re,stat,zipfile
from pathlib import Path,PurePosixPath
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--zip-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
patterns=['01_*972*.zip','02_*972*.zip','03_972股计算输入_part*.zip','04_972股原始抓取证据_part*.zip']
files=sorted({f for pattern in patterns for f in a.zip_dir.expanduser().glob(pattern)})
if not files:raise SystemExit('未找到本次972版本ZIP；请用 --zip-dir 指定存放下载文件的文件夹。')
out=a.output.expanduser().resolve();plans={};allowed={'shareholder_system_972','shareholder_system_972_web'}
for f in files:
 with zipfile.ZipFile(f) as z:
  if z.testzip() is not None:raise SystemExit('ZIP校验失败：'+f.name)
  for info in z.infolist():
   path=PurePosixPath(info.filename)
   if path.is_absolute() or '..' in path.parts or '\\' in info.filename or not path.parts or path.parts[0] not in allowed:raise SystemExit('拒绝不安全或非本版本路径：'+info.filename)
   if stat.S_ISLNK(info.external_attr>>16):raise SystemExit('拒绝压缩包符号链接：'+info.filename)
   target=out.joinpath(*path.parts)
   if out not in target.resolve().parents:raise SystemExit('拒绝越界路径')
   if info.is_dir():continue
   h=hashlib.sha256(z.read(info)).hexdigest()
   if str(path) in plans and plans[str(path)][2]!=h:raise SystemExit('不同ZIP包含冲突版本：'+str(path))
   if target.exists() and (not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=h):raise SystemExit('已有文件内容不同，未覆盖。请换一个空的 --output 文件夹：'+str(target))
   plans[str(path)]=(f,info.filename,h)
# Every path/conflict was checked before writing.
for name,(f,member,h) in plans.items():
 target=out.joinpath(*PurePosixPath(name).parts)
 if target.is_file():continue
 target.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(f) as z:target.write_bytes(z.read(member))
print('完成：',len(files),'个ZIP，',len(plans),'个文件，目录：',out)
required=['02_']+[f'03_972股计算输入_part{i:02d}of04.zip' for i in range(1,5)]
missing=[x for x in required if not any(f.name.startswith(x) if x=='02_' else f.name==x for f in files)]
if missing:print('提示：重新计算所需分包还未收齐；只看网页不受影响。缺少：',', '.join(missing))
else:print('重算包已收齐。进入 shareholder_system_972，阅读 README_972_ZH.md。')
