"""Add positive >=80% column to frozen single-stock assets. Offline, no price recomputation."""
from pathlib import Path
import argparse,json,gzip,hashlib,copy,math
from collections import Counter
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--patch',type=Path,required=True);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--matrix-manifest',type=Path);p.add_argument('--count-only',action='store_true');a=p.parse_args();O=a.output;O.mkdir(parents=True,exist_ok=True)
NS=[10,20,30,60,120];TOL=1e-12;NEG='price_decline_magnitude_at_least80'
def sh(b):return hashlib.sha256(b).hexdigest()
def load(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def pos(x):return x is not None and math.isfinite(x) and x>0 and (x>=.8 or abs(x-.8)<=TOL)
def neg(x):return x is not None and math.isfinite(x) and x<0 and (abs(x)>=.8 or abs(abs(x)-.8)<=TOL)
bi=load(a.base/'index.json');pi=load(a.patch/'index.json');assert {x['code'] for x in bi['stocks']}=={x['code'] for x in pi['stocks']};bd={x['code']:x for x in bi['stocks']};pd={x['code']:x for x in pi['stocks']}
refs={};versions={};hashes={}
if not a.count_only:
 assert a.matrix_manifest,'Require final matrix manifest'
 for n,path in json.load(open(a.matrix_manifest)).items():
  raw=Path(path).read_bytes();j=json.loads(raw);refs[int(n)]={(c['anchor'],c['row_id'],c['column_id']):c for c in j['curves']};versions[n]=j['metadata']['version'];hashes[n]=sh(raw);assert len(j['columns'])==9
counts={str(n):Counter() for n in NS};bycode={};unchanged=Counter();source_hashes={str(a.base/'index.json'):sh((a.base/'index.json').read_bytes()),str(a.patch/'index.json'):sh((a.patch/'index.json').read_bytes())};outbase=[];outpatch=[]
def update(z,n,anchor):
 old=copy.deepcopy(z);x=z.get(f'prior{n}_change',z.get('prior_change'));ct=counts[str(n)];ct['anchors']+=1;ct['old_eligible']+=int(z['eligible'])
 if pos(x):
  ct['positive_ge80']+=1
  if a.count_only:
   ct['potentially_eligible_pending_reference']+=int(z['row_id'] is not None and not [r for r in z['reasons'] if r not in ['price_magnitude_at_least80','empty_reference_cell']])
   return z
  assert z['column_id'] is None,(n,z)
  z['column_id']='up_4';why=[r for r in z['reasons'] if r not in ['price_magnitude_at_least80','empty_reference_cell']];r=refs[n].get((anchor,z['row_id'],'up_4'))
  if r is not None and r['count_events']==0:why.append('empty_reference_cell')
  z.update(reasons=list(dict.fromkeys(why)),eligible=not why and z['row_id'] is not None and r is not None and r['count_events']>0,reference_count_events=r['count_events'] if r else 0,reference_count_stocks=r['count_stocks'] if r else 0,reference_small_sample=r['small_sample'] if r else True)
  ct['newly_eligible']+=int(z['eligible'] and not old['eligible'])
 elif not a.count_only:
  if neg(x):z['reasons']=[NEG if r=='price_magnitude_at_least80' else r for r in z['reasons']]
  else:
   assert z==old
   if z['column_id'] is not None and z['row_id'] is not None:
    r=refs[n][anchor,z['row_id'],z['column_id']];assert z['reference_count_events']==r['count_events'];assert z['reference_count_stocks']==r['count_stocks'];assert z['reference_small_sample']==r['small_sample'];unchanged[str(n)]+=1
 if not a.count_only:
  for k in ['date','calendar_index','global_calendar_index','base_price',f'prior{n}_change',f'prior{n}_start',f'prior{n}_end','row_id']:
   if k in old:assert z[k]==old[k]
  ct['new_eligible']+=int(z['eligible'])
 return z
def meta(m,patch=False):
 m.update(price_positive_overflow_policy='positive change >=80% included as up_4; negative magnitude >=80% excluded',reference_dataset_version=versions['60'],query_price_bins_version='up80-v1')
 if patch:m.update(reference_dataset_versions=versions,reference_sha256=hashes,legacy60_frozen=False,legacy60_update='Only positive >=80% column and reference metadata changed; prior8 columns unchanged')
 return m
def emit(root,j,item,patch=False):
 root.mkdir(parents=True,exist_ok=True);(root/'stocks').mkdir(exist_ok=True);raw=json.dumps(j,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();gz=gzip.compress(raw,mtime=0);code=j['code'];(root/'stocks'/f'{code}.json').write_bytes(raw);(root/'stocks'/f'{code}.json.gz').write_bytes(gz);r=copy.deepcopy(item);r.update(file=f'stocks/{code}.json.gz',bytes=len(raw),sha256=sh(raw),gzip_sha256=sh(gz))
 if patch:r['gzip_bytes']=len(gz)
 else:r.update(compressed_bytes=len(gz),transport='gzip')
 return r
for i,code in enumerate(sorted(bd)):
 bp=a.base/bd[code]['file'];pp=a.patch/pd[code]['file'];source_hashes[str(bp)]=sh(bp.read_bytes());source_hashes[str(pp)]=sh(pp.read_bytes());b=load(bp);q=load(pp);original_b=copy.deepcopy(b);original_q=copy.deepcopy(q);assert {n['id'] for n in b['nodes']}==set(q['nodes']);local={}
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
  assert b['calendar']==original_b['calendar'] and b['prices']==original_b['prices'];assert q['calendar']==original_q['calendar'] and q['prices']==original_q['prices']
  for old,node in zip(original_b['nodes'],b['nodes']):assert {k:v for k,v in old.items() if k!='anchors'}=={k:v for k,v in node.items() if k!='anchors'}
  b['metadata']=meta(b['metadata']);baseitem=emit(O/'single_stock',b,bd[code]);baseitem['feature_eligibility']=local['60'];baseitem['feature_eligibility_by_lookback']=local;outbase.append(baseitem)
  q['metadata']=meta(q['metadata'],True);q['metadata']['legacy_stock_sha256']=baseitem['sha256'];outpatch.append(emit(O/'lookback_patch',q,pd[code],True))
 bycode[code]=local
 if (i+1)%500==0:print('processed',i+1,flush=True)
report={'status':'count_only' if a.count_only else 'generated_internal_audit_pass','stocks':len(bd),'lookback_anchor_counts':counts,'unchanged_prior8_reference_checks':unchanged}
if not a.count_only:
 for path,h in source_hashes.items():assert sh(Path(path).read_bytes())==h
 coverage=copy.deepcopy(bi['metadata'].get('coverage',{}));coverage['stocks_with_comparable_nodes_by_lookback']={str(n):sum(any(v[str(n)].values()) for v in bycode.values()) for n in NS};coverage['stocks_with_comparable_nodes_by_lookback_and_anchor']={str(n):{an:sum(v[str(n)][an]>0 for v in bycode.values()) for an in ['public_nextopen','stat_close']} for n in NS};coverage['eligible_anchors_by_lookback']={str(n):counts[str(n)]['new_eligible'] for n in NS};report['coverage']=coverage
 for root,index,stocks,patch in [('single_stock',bi,outbase,False),('lookback_patch',pi,outpatch,True)]:
  index['stocks']=stocks;index['metadata']['coverage']=coverage;index['metadata']=meta(index['metadata'],patch);index['metadata']['version']='all-a5554-query-up80-v1';index['reasons'][NEG]='所选回看期股价跌幅达到80%，不在当前矩阵内';index['reasons'].pop('price_magnitude_at_least80',None);(O/root/'index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')))
 (O/'SOURCE_SHA256.json').write_text(json.dumps(source_hashes,indent=2));report['source_files_unchanged']=len(source_hashes);report['base_index_sha256']=sh((O/'single_stock/index.json').read_bytes());report['patch_index_sha256']=sh((O/'lookback_patch/index.json').read_bytes());(O/'per_stock_eligibility.json').write_text(json.dumps(bycode,separators=(',',':')))
(O/('AFFECTED_COUNTS.json' if a.count_only else 'MIGRATION_QA.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report))
