"""Offline raw-input -> panel -> matrix rebuild; does not fetch network data."""
from pathlib import Path
import subprocess,sys,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parent
pool=pd.read_csv(ROOT/'qualified_972.csv',dtype={'code':str});assert len(pool)==972 and pool.code.is_unique
required=[ROOT/'qualified_972.csv',ROOT/'POOL_METHOD.json',ROOT/'absolute_only/trading_calendar.csv',ROOT/'holders/events_raw.csv',ROOT/'holders_baseline_2019/events_raw.csv']+[ROOT/'prices'/f'{c}.csv' for c in pool.code]
missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
if missing:raise SystemExit('Missing required inputs; refusing partial-pool computation: '+repr(missing))
for script in ['build_event_panel.py','holder_matrix_4bins/build_matrix.py','holder_matrix_4bins/audit_matrix.py']:
 subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
outputs=['holder_matrix_4bins/curves_ui.json','holder_matrix_4bins/curves.json','holder_matrix_4bins/daily.csv','holder_matrix_4bins/event_membership.csv']
audit=json.loads((ROOT/'holder_matrix_4bins/INDEPENDENT_AUDIT.json').read_text());assert audit['status']=='PASS'
report={'status':'complete','main_pool':972,'raw_candidate_pool':982,'version':'monthly972-holder4-price4-20261101','outputs_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in outputs},'audit':audit}
(ROOT/'COMPLETE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
