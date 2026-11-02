"""Offline rebuild orchestrator. Default: validate and print plan. Never fetches or publishes."""
from pathlib import Path
import argparse,json,sys,shutil,subprocess,hashlib
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--work-root',type=Path,required=True,help='New empty directory; never the source package')
p.add_argument('--baseline',type=Path)
p.add_argument('--baseline60',type=Path)
p.add_argument('--query-base',type=Path)
p.add_argument('--query-patch',type=Path)
p.add_argument('--execute',action='store_true',help='Without this flag only validate/print plan')
a=p.parse_args();src=a.package_root.resolve();work=a.work_root.resolve();rr=src/'up80_recovery/research';archive=src/'up80_recovery/archive972/shareholder_system_972';b=(a.baseline or src/'positive80_audit/baseline').resolve();b60=(a.baseline60 or src/'positive80_audit/baseline60').resolve();qb=(a.query_base or b/'single_stock').resolve();qp=(a.query_patch or b/'single_stock_patch').resolve()
assert work!=src and not(work.exists() and any(work.iterdir())), 'Use a NEW empty work root; never overwrite frozen or active output'
required=[rr/'holder_capture/CAPTURE_MANIFEST.json',rr/'holder_capture/RESUME_FROZEN_PAGES.json',rr/'holder_capture/RESUME_COMPLETE_QA.json',rr/'absolute_only/trading_calendar.csv',rr/'qualified_pool.csv',archive/'qualified_972.csv',archive/'holders/events_raw.csv',archive/'holders_baseline_2019/events_raw.csv',src/'up80_recovery/qualified_1494.csv',qb/'index.json',qp/'index.json',src/'shareholder_query_up80/migrate_up80.py']
required += [b/'prior'/str(n)/f'{kind}.json' for n in [10,20,30,120] for kind in ['all','recent','stability']]+[b60/f'{kind}.json' for kind in ['all','recent','stability']]
for f in required:assert f.is_file(), f'Missing input: {f}'
manifest=json.loads((rr/'holder_capture/CAPTURE_MANIFEST.json').read_text());assert manifest['status']=='complete' and not manifest['errors']
assert len(list((rr/'prices').glob('*.csv')))>=1494,'Incomplete prices'
R=work/'research';py=sys.executable
commands=[[py,str(R/'holder_capture/verify_resume_complete.py')],[py,str(R/'merge_recovered_holders.py')],[py,str(R/'audit_holder_merge_local.py')],[py,str(R/'build_superset.py'),str(R)],[py,str(R/'lookback_pipeline/prepare_lookback_panels.py')]]
commands += [[py,str(R/'lookback_pipeline/aggregate.py'),'--root',str(R/'lookbacks'/f'lookback_{n}'),'--lookback',str(n),'--baseline',str(b),'--baseline60',str(b60)] for n in [10,20,30,60,120]]
querycmd=[py,str(work/'query_migrate.py'),'--base',str(qb),'--patch',str(qp),'--output',str(work/'query_output'),'--matrix-manifest',str(R/'lookbacks/matrix_manifest.json')]
print(json.dumps({'status':'DRAFT_PENDING_FINAL_INDEPENDENT_AUDIT','offline_only':True,'execute':a.execute,'stages':commands+[querycmd]},ensure_ascii=False,indent=2))
if not a.execute:sys.exit(0)
work.mkdir(parents=True,exist_ok=True)
def copyfile(s,d):d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d)
for rel in ['qualified_972.csv','holders/events_raw.csv','holders_baseline_2019/events_raw.csv']:copyfile(archive/rel,work/'archive972/shareholder_system_972'/rel)
copyfile(src/'up80_recovery/qualified_1494.csv',work/'qualified_1494.csv')
for rel in ['qualified_pool.csv','merge_recovered_holders.py','audit_holder_merge_local.py','build_superset.py','clean_holders.py','ARCHIVE_EXTRA_CODES.csv','ARCHIVE_EXTRA_CODES_COMPARISON.csv','absolute_only/trading_calendar.csv']:copyfile(rr/rel,R/rel)
for folder in ['holder_capture','prices','lookback_pipeline']:shutil.copytree(rr/folder,R/folder,ignore=shutil.ignore_patterns('__pycache__','*.log'))
copyfile(src/'shareholder_query_up80/migrate_up80.py',work/'query_migrate.py')
logs=work/'logs';logs.mkdir()
for i,cmd in enumerate(commands):
 with (logs/f'{i:02d}.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,cwd=work)
for n in [10,20,30,60,120]:assert json.loads((R/'lookbacks'/f'lookback_{n}'/'OLD8_REGRESSION.json').read_text())['status']=='PASS'
mat={str(n):str(R/'lookbacks'/f'lookback_{n}'/'holder_matrix_9rows/curves_ui.json') for n in [10,20,30,60,120]};(R/'lookbacks/matrix_manifest.json').write_text(json.dumps(mat,indent=2))
files=[]
for n in [10,20,30,60,120]:
 for name,rel in [('all','holder_matrix_9rows/curves_ui.json'),('recent','holder_matrix_9rows_2020plus/curves_ui.json'),('stability','stability/stability_ui.json')]:
  dest=work/'prior'/str(n)/f'{name}.json';copyfile(R/'lookbacks'/f'lookback_{n}'/rel,dest);files.append({'file':str(dest.relative_to(work)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
with (logs/'query.log').open('w') as f:subprocess.run(querycmd,stdout=f,stderr=subprocess.STDOUT,check=True,cwd=work)
(work/'OFFLINE_RUN.json').write_text(json.dumps({'status':'internal_checks_completed_pending_independent_audit','network_used':False,'publication_performed':False,'files':files},indent=2))
