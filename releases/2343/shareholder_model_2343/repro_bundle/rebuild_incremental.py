"""Offline incremental2343 rebuild. Frozen sources read-only. Default only prints plan."""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,sys
P=argparse.ArgumentParser();P.add_argument('--bundle-root',type=Path,default=Path(__file__).resolve().parents[1]);P.add_argument('--old-root',type=Path,required=True,help='Fully rebuilt frozen1494 research, including canonical/panels/NPZ');P.add_argument('--capture-export-root',type=Path,required=True,help='Extracted new84914ZIPs; contains CAPTURE_EXPORT_MANIFEST.json and capture_handoff');P.add_argument('--screening-root',type=Path,required=True,help='Frozen complete2015 metadata root with 14segments/windows/registry');P.add_argument('--baseline',type=Path,required=True,help='Frozen old8 templates positive80_audit/baseline');P.add_argument('--baseline60',type=Path,required=True);P.add_argument('--old-query-base',type=Path,required=True);P.add_argument('--old-query-patch',type=Path,required=True);P.add_argument('--work-root',type=Path,required=True);P.add_argument('--research-only',action='store_true');P.add_argument('--resume-query-only',action='store_true');P.add_argument('--execute',action='store_true');a=P.parse_args()
B=a.bundle_root.resolve();OLD=a.old_root.resolve();CAP=a.capture_export_root.resolve();W=a.work_root.resolve();SCREEN=a.screening_root.resolve();baseline=a.baseline.resolve();baseline60=a.baseline60.resolve();qb=a.old_query_base.resolve();qp=a.old_query_patch.resolve()
assert W!=B and W!=OLD and W!=CAP and OLD not in W.parents and CAP not in W.parents,'Use independent new work directory';assert a.resume_query_only or not(W.exists() and any(W.iterdir())),'Output work root must be new/empty'
required=[SCREEN/'windows/201510_202610/all_raw.json',SCREEN/'windows/201510_202610/MANIFEST.json',B/'selector/evaluate_windows.py',B/'pipeline/merge_added_holders.py',B/'pipeline/assemble_inputs.py',B/'pipeline/run_offline.py',B/'query_migration/migrate_reference.py',CAP/'CAPTURE_EXPORT_MANIFEST.json',OLD/'model/events_clean.csv',OLD/'statdate_only/daily_paths_statdate.npz',qb/'index.json',qp/'index.json']
for n in [10,20,30,60,120]:required.extend([OLD/'lookbacks'/f'lookback_{n}'/'statdate_only/daily_paths_statdate.npz',OLD/'lookbacks'/f'lookback_{n}'/'stability/nonoverlapping_membership.csv'])
for f in required:assert f.is_file(),f'Missing prerequisite: {f}'
plan={'status':'PLAN_ONLY' if not a.execute else 'EXECUTION_REQUESTED','network':False,'old_reference_pool':1494,'new_reference_pool':2343,'steps':['Verify incremental bundle hashes and all14source-export hashes','Copy only source code/pool method files into new work root; frozen inputroots read-only','Parameterize copied aggregate baseline paths without changing numerical logic','Merge added849holder rows with byte-prefix frozen1494','Assemble frozen1494 prices and added849 outcomes/calendar','Rebuild and strictly regress old1494 canonical/251paths/all81cells/nonoverlap','Compare final15 outputs with independently audited frozen output hashes','Only after identical audit targets: migrate frozen5554query snapshots','Compare query output/index hashes with frozen expected manifest']}
print(json.dumps(plan,ensure_ascii=False,indent=2),flush=True)
if not a.execute:raise SystemExit(0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
fm=json.loads((B/'repro_bundle/INCREMENTAL_FILE_MANIFEST.json').read_text());assert fm['status']=='FROZEN_AUDITED' or (a.research_only and fm['status']=='FROZEN_RESEARCH_AUDITED_QUERY_PENDING')
for x in fm['files']:
 p=B/x['file'];assert p.is_file() and sha(p)==x['sha256'],x['file']
cm=json.loads((CAP/'CAPTURE_EXPORT_MANIFEST.json').read_text());assert cm['status']=='capture_complete_not_model_audited'
for x in cm['files']:
 p=CAP/'capture_handoff'/x['path'];assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['path']
expected=json.loads((B/'frozen_results/EXPECTED_OUTPUTS.json').read_text());assert expected['status']=='AUDITED_COMPLETE' and expected['reference_pool_count']==2343
assert sha(B/'qualified_pool.csv')==expected['pool_sha256']
W.mkdir(parents=True,exist_ok=True);logs=W/'reproduction_logs';logs.mkdir(exist_ok=True);patches=[]
py=sys.executable
def run(stage,args):
 with (logs/(stage+'.log')).open('w') as f:subprocess.run([py,*map(str,args)],cwd=W,stdout=f,stderr=subprocess.STDOUT,check=True)
if not a.resume_query_only:
 selection=W/'selection';selection.mkdir()
 for name in ['frozen_registry_5577.json','old_1494.csv','SEGMENT_PLAN.json']:shutil.copy2(SCREEN/name,selection/name)
 shutil.copy2(B/'selector/evaluate_windows.py',selection/'evaluate_windows.py');(selection/'segments').symlink_to(SCREEN/'segments',target_is_directory=True)
 run('00_select',[selection/'evaluate_windows.py','--sources',SCREEN/'windows/201510_202610/all_raw.json','--earliest','2015-10-01'])
 import csv
 selected={x['code'] for x in csv.DictReader((selection/'pool_from_2015-10-01.csv').open())};frozen_pool={x['code'] for x in csv.DictReader((B/'qualified_pool.csv').open())};assert selected==frozen_pool and len(selected)==2343,'131-window selection differs'
 for directory in ['pipeline','query_migration']:shutil.copytree(B/directory,W/directory,ignore=shutil.ignore_patterns('__pycache__','*.log'))
 for name in ['qualified_pool.csv','frozen_old1494.csv','added_849.csv','POOL_METHOD.json','PREDECLARED_PLAN.json']:shutil.copy2(B/name,W/name)
 # Adapt only copied orchestration/default arguments. Never edit running/frozen original code.
 p=W/'pipeline/run_offline.py';before=p.read_bytes();s=before.decode();needle="P.add_argument('--check-inputs',action='store_true');";assert needle in s
 if "P.add_argument('--baseline'" not in s:s=s.replace(needle,needle+"P.add_argument('--baseline',type=Path,required=True);P.add_argument('--baseline60',type=Path,required=True);")
 s=s.replace("[C/'aggregate.py','--root',", "[C/'aggregate.py','--baseline',a.baseline,'--baseline60',a.baseline60,'--root',");p.write_text(s);patches.append({'file':'pipeline/run_offline.py','before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':sha(p),'change':'Explicit baseline CLI arguments forwarded to both old-subcohort and expanded aggregation'})
 p=W/'pipeline/aggregate.py';before=p.read_bytes();s=before.decode()
 import re
 s,n=re.subn(r"default=Path\('[^']*positive80_audit/baseline60'\)","default=Path('positive80_audit/baseline60')",s);assert n==1
 s,n=re.subn(r"default=Path\('[^']*positive80_audit/baseline'\)","default=Path('positive80_audit/baseline')",s);assert n==1
 p.write_text(s);patches.append({'file':'pipeline/aggregate.py','before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':sha(p),'change':'Only two default filesystem paths sanitized; wrapper passes both explicitly'})
 for p in list((W/'pipeline').glob('*.py'))+list((W/'query_migration').glob('*.py')):assert b'/workspace/' not in p.read_bytes() and b'/home/agent/' not in p.read_bytes(),p.name
 (W/'PORTABLE_SOURCE_ADAPTATIONS.json').write_text(json.dumps(patches,indent=2))
 run('01_merge',[W/'pipeline/merge_added_holders.py','--old-root',OLD,'--capture-root',CAP/'capture_handoff/holders','--output-root',W])
 run('02_assemble',[W/'pipeline/assemble_inputs.py','--old-root',OLD,'--price-capture',CAP/'capture_handoff/prices/price_capture','--root',W])
 run('03_research',[W/'pipeline/run_offline.py','--root',W,'--old-root',OLD,'--baseline',baseline,'--baseline60',baseline60])
else:
 patches=json.loads((W/'PORTABLE_SOURCE_ADAPTATIONS.json').read_text())
 assert (W/'OLD1494_FULL_GRID_REGRESSION.json').exists()
outputs=[];matrices={}
for x in expected['files']:
 actual=W/x['rebuilt_file'];assert sha(actual)==x['sha256'],f'Frozen audited matrix differs: {x["rebuilt_file"]}';outputs.append({'file':x['rebuilt_file'],'sha256':sha(actual),'exact_bytes_equal':True})
 if x['kind']=='all':matrices[str(x['lookback'])]={'path':str(actual),'sha256':sha(actual)}
# The audit status is inherited only through exact-byte identity with frozen independently audited matrices.
qmanifest={'status':'AUDITED_COMPLETE','reference_pool_count':2343,'pool_sha256':sha(W/'qualified_pool.csv'),'matrices':matrices,'audit_basis':'All15 local rebuilt matrices exactly match packaged independently audited frozen hashes'};(W/'REBUILT_AUDITED_MATRIX_MANIFEST.json').write_text(json.dumps(qmanifest,indent=2))
if a.research_only:
 (W/'RESEARCH_REBUILD_VALIDATION.json').write_text(json.dumps({'status':'PASS_RESEARCH_ONLY_QUERY_PENDING','matrices':outputs,'source_adaptations':patches},indent=2));print('PASS_RESEARCH_ONLY_QUERY_PENDING',flush=True);raise SystemExit(0)
run('04_query',[W/'query_migration/migrate_reference.py','--base',qb,'--patch',qp,'--pool',W/'qualified_pool.csv','--output',W/'query_all_a','--matrix-manifest',W/'REBUILT_AUDITED_MATRIX_MANIFEST.json','--execute'])
qe=json.loads((B/'frozen_results/EXPECTED_QUERY_HASHES.json').read_text());assert qe['status']=='AUDITED_COMPLETE' and qe['stocks_per_bundle']==5554
for x in qe['files']:
 p=W/'query_all_a'/x['file'];assert sha(p)==x['sha256'],f'Query output differs: {x["file"]}'
report={'status':'PASS_OFFLINE_INCREMENTAL_REBUILD','network_used':False,'matrices':outputs,'query_files_verified':len(qe['files']),'old1494_regression':json.loads((W/'OLD1494_FULL_GRID_REGRESSION.json').read_text()),'old1494_nonoverlap':json.loads((W/'OLD1494_NONOVERLAP.json').read_text()),'limits':['Uses three frozen dependencies: old1494 research, new849 capture, and complete131-window selection metadata; no raw data invented','5554query migrated from frozen published snapshots; not rebuilt from all original vendor responses','Mac platform execution not established by cloud verification'],'source_adaptations':patches};(W/'INCREMENTAL_REBUILD_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS_OFFLINE_INCREMENTAL_REBUILD',flush=True)
