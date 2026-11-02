from pathlib import Path
import subprocess,sys,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent
assert (R/'lookbacks/PREPARED_ALL.json').exists(), 'Wait for full five-N prepared panels'
for name in ['DELIVERY_MANIFEST.json','matrix_manifest.json']:
 path=R/'lookbacks'/name
 if path.exists():path.unlink()
files=[]
for n in [10,20,30,60,120]:
 root=R/'lookbacks'/f'lookback_{n}'
 with open(root/'aggregate.log','w') as log:subprocess.run([sys.executable,str(O/'aggregate.py'),'--root',str(root),'--lookback',str(n)],stdout=log,stderr=subprocess.STDOUT,check=True)
 qa=json.load(open(root/'OLD8_REGRESSION.json'));assert qa['status']=='PASS'
 for kind,rel in [('all','holder_matrix_9rows/curves_ui.json'),('recent','holder_matrix_9rows_2020plus/curves_ui.json'),('stability','stability/stability_ui.json')]:
  p=root/rel;files.append({'lookback_market_days':n,'type':kind,'path':str(p),'source_path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print('completed',n,flush=True)
manifest={'status':'computed_old8_internal_regression_pass_wait_independent_audit','files':files};(R/'lookbacks/DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2));(R/'lookbacks/matrix_manifest.json').write_text(json.dumps({str(x['lookback_market_days']):x['path'] for x in files if x['type']=='all'},indent=2));print('All five lookbacks ready for independent audit',flush=True)
