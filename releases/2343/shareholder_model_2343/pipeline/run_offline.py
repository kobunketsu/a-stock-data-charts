"""Offline2343 rebuild entry. All source acquisition/merge remains parent-controlled."""
from pathlib import Path
import argparse,json,subprocess,sys,hashlib
import numpy as np,pandas as pd
from guard_inputs import check_inputs
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);P.add_argument('--old-root',type=Path,required=True);P.add_argument('--check-inputs',action='store_true');a=P.parse_args();B=a.root.resolve();a.old_root=a.old_root.resolve();C=Path(__file__).resolve().parent
check_inputs(B)
if a.check_inputs:print('INPUTS_VERIFIED_NO_MODEL_EXECUTION');raise SystemExit
(B/'logs').mkdir(exist_ok=True)
def run(name,args):
 with open(B/'logs'/f'{name}.log','w') as log:subprocess.run([sys.executable,*map(str,args)],stdout=log,stderr=subprocess.STDOUT,check=True)
run('superset',[C/'build_superset.py',B]);run('prepare',[C/'prepare_lookback_panels.py',B]);run('old_preservation',[C/'audit_preservation.py','--root',B,'--old-root',a.old_root])
# Reaggregate the actual new-input old1494 subcohort, then compare all81 cells including up4.
for n in [10,20,30,60,120]:
 V=B/'old1494_validation'/f'lookback_{n}';run(f'old1494_aggregate_{n}',[C/'aggregate.py','--root',V,'--lookback',n]);old=a.old_root/'lookbacks'/f'lookback_{n}'
 for rel in ['holder_matrix_9rows/curves_ui.json','holder_matrix_9rows_2020plus/curves_ui.json','stability/stability_ui.json']:
  u=json.load(open(old/rel));v=json.load(open(V/rel));field='series' if 'stability' in rel else 'curves';assert len(u[field])==len(v[field])
  for x,y in zip(u[field],v[field]):
   for k,val in x.items():
    if isinstance(val,list) and k in ['mean','median','positive_fraction','p10','p90','equal_stock_mean']:
     if field=='curves':assert val==y[k],(n,rel,k,'7-decimal UI must exactly match')
     else:assert np.allclose(np.array(val,dtype=float),np.array(y[k],dtype=float),rtol=0,atol=1e-12,equal_nan=True),(n,rel,k)
    else:assert y[k]==val,(n,rel,k)
(B/'OLD1494_FULL_GRID_REGRESSION.json').write_text(json.dumps({'status':'PASS','all_5N_81_cells_and_stability_preserved':True},indent=2))
files=[]
for n in [10,20,30,60,120]:
 root=B/'lookbacks'/f'lookback_{n}';run(f'expanded_aggregate_{n}',[C/'aggregate.py','--root',root,'--lookback',n,'--expansion-guard',B/'OLD1494_PRESERVATION.json','--pool-method',B/'POOL_METHOD.json'])
 for kind,rel in [('all','holder_matrix_9rows/curves_ui.json'),('recent','holder_matrix_9rows_2020plus/curves_ui.json'),('stability','stability/stability_ui.json')]:
  p=root/rel;files.append({'lookback_market_days':n,'type':kind,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
non_checks=[]
oldcodes=set(pd.read_csv(B/'frozen_old1494.csv',dtype={'code':str}).code)
for n in [10,20,30,60,120]:
 old=pd.read_csv(a.old_root/'lookbacks'/f'lookback_{n}/stability/nonoverlapping_membership.csv',dtype={'code':str});new=pd.read_csv(B/'lookbacks'/f'lookback_{n}/stability/nonoverlapping_membership.csv',dtype={'code':str});new=new[new.code.isin(oldcodes)];keys=['code','notice','endpoint'];assert not old.duplicated(keys).any() and not new.duplicated(keys).any();u=old.sort_values(keys).reset_index(drop=True);v=new.sort_values(keys).reset_index(drop=True)
 for key in keys+['entry_index','stat_index']:assert u[key].equals(v[key]),(n,key,'Old nonoverlap members changed')
 non_checks.append({'lookback_market_days':n,'preserved_old1494_nonoverlapping_events':len(old),'status':'PASS'})
(B/'OLD1494_NONOVERLAP.json').write_text(json.dumps({'status':'PASS','canonical_checks':non_checks},indent=2))
run('comparison',[C/'compare_stability.py','--root',B,'--old-root',a.old_root]);(B/'DELIVERY_MANIFEST.json').write_text(json.dumps({'status':'computed_wait_independent_audit_no_publication','files':files},indent=2));run('metadata_finalize',[C/'metadata_finalize.py','--root',B,'--apply']);print('OFFLINE2343_COMPUTED_WAIT_INDEPENDENT_AUDIT')
