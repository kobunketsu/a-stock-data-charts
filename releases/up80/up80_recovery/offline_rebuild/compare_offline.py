from pathlib import Path
import json,hashlib,gzip,collections,time
import numpy as np,pandas as pd
root=Path(__file__).resolve().parents[2];w=root/'up80_offline_test';official=root/'up80_recovery/research';report={'status':'PASS','json_files':[],'table_files':[],'array_files':[],'query':{},'differences':[]};diffcounts=collections.Counter()
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(a,b,path):
 if type(a)!=type(b):record(path,a,b);return
 if isinstance(a,dict):
  if set(a)!=set(b):record(path+'.keys',sorted(a),sorted(b))
  for k in a.keys()&b.keys():compare(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):record(path+'.length',len(a),len(b))
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
 elif a!=b:record(path,a,b)
def record(path,a,b):
 report['status']='FAIL';diffcounts['metadata' if '.metadata.' in path else 'nonmetadata']+=1
 if len(report['differences'])<100:report['differences'].append({'path':path,'official':a,'rebuilt':b})
for n in [10,20,30,60,120]:
 aroot=official/'lookbacks'/f'lookback_{n}';broot=w/'research/lookbacks'/f'lookback_{n}'
 for kind,rel in [('all','holder_matrix_9rows/curves_ui.json'),('recent','holder_matrix_9rows_2020plus/curves_ui.json'),('stability','stability/stability_ui.json')]:
  a=aroot/rel;b=broot/rel;before=sum(diffcounts.values());compare(json.loads(a.read_text()),json.loads(b.read_text()),f'N{n}.{kind}');report['json_files'].append({'lookback':n,'kind':kind,'exact_bytes_equal':sh(a)==sh(b),'official_sha256':sh(a),'rebuilt_sha256':sh(b),'all_values_equal':before==sum(diffcounts.values())})
 for rel in ['model/event_panel.csv','threshold_curves/ranges_uniform60/lookback_feature_audit.csv','threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv']:
  a=aroot/rel;b=broot/rel
  same=sh(a)==sh(b)
  if not same:
   try:pd.testing.assert_frame_equal(pd.read_csv(a,dtype={'code':str}),pd.read_csv(b,dtype={'code':str}),check_exact=True)
   except AssertionError as e:record(f'N{n}.{rel}',str(e)[:1200],'different')
  report['table_files'].append({'lookback':n,'file':rel,'bytes_equal':same})
 a=np.load(aroot/'statdate_only/daily_paths_statdate.npz');b=np.load(broot/'statdate_only/daily_paths_statdate.npz');assert set(a.files)==set(b.files)
 for k in a.files:
  same=np.array_equal(a[k],b[k],equal_nan=True);report['array_files'].append({'lookback':n,'array':k,'exact_equal_nan':same,'shape':list(a[k].shape)})
  if not same:record(f'N{n}.paths.{k}','official array','rebuilt array differs')
for bundle in ['single_stock','lookback_patch']:
 ar=root/'query_all_a_up80'/bundle;br=w/'query_output'/bundle
 ai=json.loads((ar/'index.json').read_text());bi=json.loads((br/'index.json').read_text());compare(ai,bi,f'query.{bundle}.index');assert len(ai['stocks'])==len(bi['stocks'])==5554
 counts=collections.Counter()
 for item in ai['stocks']:
  code=item['code'];a=ar/item['file'];b=br/item['file'];counts['stocks']+=1
  if sh(a)==sh(b):counts['gzip_bytes_equal']+=1;continue
  counts['gzip_bytes_differ']+=1;before=sum(diffcounts.values());compare(json.loads(gzip.decompress(a.read_bytes())),json.loads(gzip.decompress(b.read_bytes())),f'query.{bundle}.{code}');counts['same_json_values']+=int(before==sum(diffcounts.values()))
 report['query'][bundle]=dict(counts)
compare(json.loads((root/'query_all_a_up80/per_stock_eligibility.json').read_text()),json.loads((w/'query_output/per_stock_eligibility.json').read_text()),'query.per_stock_eligibility')
report['difference_counts']=dict(diffcounts);report['metadata_policy']='No metadata ignored; all value differences fail and are classified separately. Paths/provenance report files are separately documented, not mistaken for model data.'
(w/'OFFLINE_COMPARISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['json_files','table_files','array_files']},ensure_ascii=False,indent=2))
