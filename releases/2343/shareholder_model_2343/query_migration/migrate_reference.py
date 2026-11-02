"""Replace reference corpus only; all frozen query features and bins immutable. Requires real audited 2343 matrices."""
from pathlib import Path
import argparse,json,gzip,hashlib,copy,math,csv
from collections import Counter
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--patch',type=Path,required=True);p.add_argument('--pool',type=Path,required=True);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent/'query_all_a');p.add_argument('--matrix-manifest',type=Path,required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();a.count_only=False;O=a.output.resolve()
assert O not in [a.base.resolve(),a.patch.resolve()] and not any(x in O.parents for x in [a.base.resolve(),a.patch.resolve()]),'Do not overwrite or nest inside frozen query source'
assert not (O.exists() and any(O.iterdir())),'Output must be new/empty; no overwrite'
pool={r['code'] for r in csv.DictReader(a.pool.open(encoding='utf-8-sig'))};assert len(pool)==2343
if not a.execute:
 print(json.dumps({'status':'PLAN_ONLY_NO_OUTPUT','reference_pool':len(pool),'query_scope_expected':5554,'requires_real_audited_matrices':True}));raise SystemExit()
NS=[10,20,30,60,120];TOL=1e-12;NEG='price_decline_magnitude_at_least80'
def sh(b):return hashlib.sha256(b).hexdigest()
def load(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def pos(x):return x is not None and math.isfinite(x) and x>0 and (x>=.8 or abs(x-.8)<=TOL)
def neg(x):return x is not None and math.isfinite(x) and x<0 and (abs(x)>=.8 or abs(abs(x)-.8)<=TOL)
bi=load(a.base/'index.json');pi=load(a.patch/'index.json');assert {x['code'] for x in bi['stocks']}=={x['code'] for x in pi['stocks']};bd={x['code']:x for x in bi['stocks']};pd={x['code']:x for x in pi['stocks']}
refs={};versions={};hashes={}
manifest=load(a.matrix_manifest);assert manifest['status']=='AUDITED_COMPLETE' and manifest['reference_pool_count']==2343
assert manifest['pool_sha256']==sh(a.pool.read_bytes());assert set(manifest['matrices'])==set(map(str,NS))
for n,item in manifest['matrices'].items():
 path=Path(item['path']);path=path if path.is_absolute() else a.matrix_manifest.parent/path
 raw=path.read_bytes();assert sh(raw)==item['sha256'];j=json.loads(raw)
 assert len(j['rows'])==9 and len(j['columns'])==9 and len(j['curves'])==162
 assert len({(c['anchor'],c['row_id'],c['column_id']) for c in j['curves']})==162
 for c in j['curves']:
  assert c['count_events']>=0 and 0<=c['count_stocks']<=c['count_events']
  assert c['small_sample']==(c['count_events']<50 or c['count_stocks']<10)
 refs[int(n)]={(c['anchor'],c['row_id'],c['column_id']):c for c in j['curves']};versions[n]=j['metadata']['version'];hashes[n]=sh(raw)
assert len(bd)==5554 and pool<=set(bd)
O.mkdir(parents=True,exist_ok=True)
counts={str(n):Counter() for n in NS};bycode={};unchanged=Counter();source_hashes={str(a.base/'index.json'):sh((a.base/'index.json').read_bytes()),str(a.patch/'index.json'):sh((a.patch/'index.json').read_bytes())};outbase=[];outpatch=[]
ALLOWED={'reasons','eligible','reference_count_events','reference_count_stocks','reference_small_sample'}
def update(z,n,anchor):
 old=copy.deepcopy(z);ct=counts[str(n)];ct['anchors']+=1;ct['old_eligible']+=int(z['eligible'])
 why=[r for r in z['reasons'] if r!='empty_reference_cell']
 r=refs[n].get((anchor,z.get('row_id'),z.get('column_id')))
 if z.get('row_id') is not None and z.get('column_id') is not None:assert r is not None,'Missing declared matrix cell'
 if r is not None:
  if r['count_events']==0:why.append('empty_reference_cell')
  z.update(reference_count_events=r['count_events'],reference_count_stocks=r['count_stocks'],reference_small_sample=r['small_sample'])
 else:
  # Invalid bins keep rejection: lack of a matching group cannot be repaired by a larger reference pool.
  assert not old['eligible']
  if 'empty_reference_cell' in old['reasons']:why.append('empty_reference_cell')
 z.update(reasons=list(dict.fromkeys(why)),eligible=not why and r is not None and r['count_events']>0)
 assert {k:v for k,v in z.items() if k not in ALLOWED}=={k:v for k,v in old.items() if k not in ALLOWED}
 assert [x for x in z['reasons'] if x!='empty_reference_cell']==[x for x in old['reasons'] if x!='empty_reference_cell']
 ct['new_eligible']+=int(z['eligible']);ct['newly_eligible']+=int(z['eligible'] and not old['eligible']);ct['newly_ineligible']+=int(old['eligible'] and not z['eligible'])
 return z
def meta(m,patch=False):
 m.update(reference_pool_stocks=2343,reference_pool_count=2343,reference_dataset_version=versions['60'],reference_dataset_versions=versions,reference_sha256=hashes,reference_pool_sha256=manifest['pool_sha256'],reference_update='Only reference corpus changed; all query features/bins/prices/dates and nonempty-reference rejection reasons frozen')
 if 'reference_pool' in m:m['reference_pool'].update(stocks=2343,unchanged=False)
 if 'legacy60_update' in m:m['legacy60_update']='Reference corpus updated to2343; legacy60 price/features preserved'
 return m
def emit(root,j,item,patch=False):
 root.mkdir(parents=True,exist_ok=True);(root/'stocks').mkdir(exist_ok=True);raw=json.dumps(j,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();gz=gzip.compress(raw,mtime=0);code=j['code'];(root/'stocks'/f'{code}.json').write_bytes(raw);(root/'stocks'/f'{code}.json.gz').write_bytes(gz);r=copy.deepcopy(item);r.update(file=f'stocks/{code}.json.gz',bytes=len(raw),sha256=sh(raw),gzip_sha256=sh(gz),reference_pool_member=code in pool)
 if patch:r['gzip_bytes']=len(gz)
 else:r.update(compressed_bytes=len(gz),transport='gzip')
 return r
for i,code in enumerate(sorted(bd)):
 bp=a.base/bd[code]['file'];pp=a.patch/pd[code]['file'];source_hashes[str(bp)]=sh(bp.read_bytes());source_hashes[str(pp)]=sh(pp.read_bytes());b=load(bp);q=load(pp);original_b=copy.deepcopy(b);original_q=copy.deepcopy(q);assert {n['id'] for n in b['nodes']}==set(q['nodes']);local={}
 for obj in [b,q]:
  if 'reference_pool_member' in obj:obj['reference_pool_member']=code in pool
 # Count 5N patch only; base60 migration separately must match corresponding patch60.
 for nid,v in q['nodes'].items():
  for n in NS:
   for anchor,z in v['anchors_by_lookback'][str(n)].items():update(z,n,anchor)
 for n in NS:local[str(n)]={an:sum(int(v['anchors_by_lookback'][str(n)][an]['eligible']) for v in q['nodes'].values()) for an in ['public_nextopen','stat_close']}
 if not a.count_only:
  saved=counts['60'].copy()
  for node in b['nodes']:
   for an,z in node['anchors'].items():
    update(z,60,an);t=q['nodes'][node['id']]['anchors_by_lookback']['60'][an]
    for k in ['base_price','prior60_change','row_id','column_id','eligible','reasons','reference_count_events','reference_count_stocks','reference_small_sample']:assert z[k]==t[k],(code,node['id'],an,k)
  counts['60']=saved
  assert {k:v for k,v in q.items() if k not in ['metadata','nodes','reference_pool_member']}=={k:v for k,v in original_q.items() if k not in ['metadata','nodes','reference_pool_member']}
  for nid in q['nodes']:assert {k:v for k,v in q['nodes'][nid].items() if k!='anchors_by_lookback'}=={k:v for k,v in original_q['nodes'][nid].items() if k!='anchors_by_lookback'}
  assert b['calendar']==original_b['calendar'] and b['prices']==original_b['prices'];assert q['calendar']==original_q['calendar'] and q['prices']==original_q['prices']
  for old,node in zip(original_b['nodes'],b['nodes']):assert {k:v for k,v in old.items() if k!='anchors'}=={k:v for k,v in node.items() if k!='anchors'}
  b['metadata']=meta(b['metadata']);baseitem=emit(O/'single_stock',b,bd[code]);baseitem['feature_eligibility']=local['60'];baseitem['feature_eligibility_by_lookback']=local;outbase.append(baseitem)
  q['metadata']=meta(q['metadata'],True);q['metadata']['legacy_stock_sha256']=baseitem['sha256'];outpatch.append(emit(O/'lookback_patch',q,pd[code],True))
 bycode[code]=local
 if (i+1)%500==0:print('processed',i+1,flush=True)
report={'status':'count_only' if a.count_only else 'generated_internal_audit_pass','stocks':len(bd),'lookback_anchor_counts':counts,'anchor_immutable_fields_verified':True,'non_reference_rejection_reasons_preserved':True}
if not a.count_only:
 for path,h in source_hashes.items():assert sh(Path(path).read_bytes())==h
 coverage=copy.deepcopy(bi['metadata'].get('coverage',{}));coverage['reference_pool_count']=2343;coverage['stocks_with_comparable_nodes_by_lookback']={str(n):sum(any(v[str(n)].values()) for v in bycode.values()) for n in NS};coverage['stocks_with_comparable_nodes_by_lookback_and_anchor']={str(n):{an:sum(v[str(n)][an]>0 for v in bycode.values()) for an in ['public_nextopen','stat_close']} for n in NS};coverage['eligible_anchors_by_lookback']={str(n):counts[str(n)]['new_eligible'] for n in NS};report['coverage']=coverage
 for root,index,stocks,patch in [('single_stock',bi,outbase,False),('lookback_patch',pi,outpatch,True)]:
  index['stocks']=stocks;index['metadata']['coverage']=coverage;index['metadata']=meta(index['metadata'],patch);index['metadata']['version']='all-a5554-reference2343-v1';(O/root/'index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')))
 (O/'SOURCE_SHA256.json').write_text(json.dumps(source_hashes,indent=2));report['source_files_unchanged']=len(source_hashes);report['base_index_sha256']=sh((O/'single_stock/index.json').read_bytes());report['patch_index_sha256']=sh((O/'lookback_patch/index.json').read_bytes());(O/'per_stock_eligibility.json').write_text(json.dumps(bycode,separators=(',',':')))
(O/('AFFECTED_COUNTS.json' if a.count_only else 'MIGRATION_QA.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report))
