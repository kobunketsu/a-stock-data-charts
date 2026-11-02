"""Offline completeness gate. A terminal verified absence is distinct from incomplete capture."""
from pathlib import Path
import json,hashlib
import pandas as pd

def check_inputs(root):
 root=Path(root);plan=json.load(open(root/'PREDECLARED_PLAN.json'));pool=set(pd.read_csv(root/'qualified_pool.csv',dtype={'code':str}).code.str.zfill(6));old=set(pd.read_csv(root/'frozen_old1494.csv',dtype={'code':str}).code.str.zfill(6));assert len(pool)==plan['pool']==2343 and len(old)==1494 and old<=pool
 p=root/'INPUT_COMPLETENESS.json'
 if not p.exists():raise RuntimeError('PENDING_INPUTS: INPUT_COMPLETENESS.json absent; do not build partial/empty research results')
 manifest=json.load(open(p));assert manifest['status']=='complete'
 assert not manifest.get('stop_on_refusal') and not manifest.get('refusal'), 'Refusal requires parent decision, never convert it to empty coverage'
 rows=manifest['prices'];assert len(rows)==len(pool);lookup={str(r['code']).zfill(6):r for r in rows};assert set(lookup)==pool
 for code,r in lookup.items():
  assert r['status'] in ['ok','reused','empty_no_price'],f'Unresolved price status {code}'
  f=root/'prices'/f'{code}.csv'
  if r['status']=='empty_no_price':assert not f.exists(),f'Conflicting empty manifest and price CSV {code}'
  else:
   assert f.exists(),f'Missing confirmed price {code}'
   assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],f'Price hash mismatch {code}'
 for rel in ['holders/events_raw.csv','holders_baseline_2009/events_raw.csv','absolute_only/trading_calendar.csv']:
  f=root/rel;assert f.exists(),f'Missing frozen input {rel}'
  assert hashlib.sha256(f.read_bytes()).hexdigest()==manifest['input_sha256'][rel],f'Input hash mismatch {rel}'
 assert set(manifest['holder_codes_accounted'])==pool
 assert set(manifest['frozen_old1494_codes'])==old
 return manifest
