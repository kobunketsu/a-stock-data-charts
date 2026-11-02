from pathlib import Path
import json,gzip,hashlib,math,collections
A=Path(__file__).resolve().parent;B=A/'baseline';R=A.parent/'query_all_a_up80';mf=json.load(open(A.parent/'up80_recovery/research/lookbacks/DELIVERY_MANIFEST.json'));refs={};hashes={}
for f in mf['files']:
 if f['type']!='all':continue
 raw=Path(f['path']).read_bytes();j=json.loads(raw);refs[f['lookback_market_days']]={(c['anchor'],c['row_id'],c['column_id']):c for c in j['curves']};hashes[str(f['lookback_market_days'])]=hashlib.sha256(raw).hexdigest()
def read(root,item):
 raw=(root/item['file']).read_bytes();return json.loads(gzip.decompress(raw) if item['file'].endswith('.gz') else raw)
oldbi=json.load(open(B/'single_stock/index.json'));oldpi=json.load(open(B/'single_stock_patch/index.json'));newbi=json.load(open(R/'single_stock/index.json'));newpi=json.load(open(R/'lookback_patch/index.json'));maps=[{x['code']:x for x in i['stocks']} for i in [oldbi,oldpi,newbi,newpi]];assert all(set(m)==set(maps[0]) and len(m)==5554 for m in maps);checked=0;added=collections.Counter();eligible=collections.Counter();stockcover=collections.Counter();unchanged=0
for code in sorted(maps[0]):
 ob=read(B/'single_stock',maps[0][code]);oq=read(B/'single_stock_patch',maps[1][code]);nb=read(R/'single_stock',maps[2][code]);nq=read(R/'lookback_patch',maps[3][code]);assert ob['prices']==nb['prices'] and ob['calendar']==nb['calendar'];assert oq['prices']==nq['prices'] and oq['calendar']==nq['calendar'];assert oq['nodes'].keys()==nq['nodes'].keys();assert nq['metadata']['reference_sha256']==hashes
 for old,new in zip(ob['nodes'],nb['nodes']):assert {k:v for k,v in old.items() if k!='anchors'}=={k:v for k,v in new.items() if k!='anchors'}
 for nid,node in oq['nodes'].items():
  for n in [10,20,30,60,120]:
   for an,o in node['anchors_by_lookback'][str(n)].items():
    z=nq['nodes'][nid]['anchors_by_lookback'][str(n)][an];x=o['prior_change'];mag=abs(x) if x is not None else float('nan')
    if abs(mag-.8)<=1e-12:mag=.8
    want=dict(o)
    if math.isfinite(mag) and mag>=.8 and x>0:
     assert o['column_id'] is None and not o['eligible'];want['column_id']='up_4';why=[r for r in o['reasons'] if r not in ['price_magnitude_at_least80','empty_reference_cell']];ref=refs[n].get((an,o['row_id'],'up_4'))
     if ref is not None and ref['count_events']==0:why.append('empty_reference_cell')
     want.update(reasons=list(dict.fromkeys(why)),eligible=not why and o['row_id'] is not None and ref is not None and ref['count_events']>0,reference_count_events=ref['count_events'] if ref else 0,reference_count_stocks=ref['count_stocks'] if ref else 0,reference_small_sample=ref['small_sample'] if ref else True)
    elif math.isfinite(mag) and mag>=.8 and x<0:
     want['reasons']=['price_decline_magnitude_at_least80' if r=='price_magnitude_at_least80' else r for r in o['reasons']];assert not z['eligible'] and z['column_id'] is None
    else:unchanged+=1
    assert z==want,(code,nid,n,an);added[n]+=int(z['eligible'] and not o['eligible']);eligible[n]+=int(z['eligible']);checked+=1
 for n in [10,20,30,60,120]:
  count={an:sum(v['anchors_by_lookback'][str(n)][an]['eligible'] for v in nq['nodes'].values()) for an in ['public_nextopen','stat_close']};assert maps[2][code]['feature_eligibility_by_lookback'][str(n)]==count;stockcover[n]+=int(any(count.values()))
 for node in nb['nodes']:
  for an,z in node['anchors'].items():
   q=nq['nodes'][node['id']]['anchors_by_lookback']['60'][an]
   for k,v in z.items():
    if k!='calendar_index':assert q[k]==v,(code,node['id'],k)
 for root,item in [(R/'single_stock',maps[2][code]),(R/'lookback_patch',maps[3][code])]:
  gz=(root/item['file']).read_bytes();raw=gzip.decompress(gz);assert hashlib.sha256(gz).hexdigest()==item['gzip_sha256'];assert hashlib.sha256(raw).hexdigest()==item['sha256']
 assert nq['metadata']['legacy_stock_sha256']==maps[2][code]['sha256']
c=newbi['metadata']['coverage']
for n in [10,20,30,60,120]:assert c['stocks_with_comparable_nodes_by_lookback'][str(n)]==stockcover[n] and c['eligible_anchors_by_lookback'][str(n)]==eligible[n]
assert c['display_window_price_available_stocks']==5537 and c['source_price_rows_available_stocks']==5544 and c['stocks_with_nodes']==5527
out={'status':'PASS','stocks':5554,'anchors_checked':checked,'nonextreme_anchors_exactly_unchanged':unchanged,'new_eligible_by_N':dict(added),'eligible_anchors_by_N':dict(eligible),'comparable_stocks_by_N':dict(stockcover),'prices_calendar_holder_source_fields_unchanged':True,'negative80_still_excluded':True,'base60_patch60_consistent':True,'base_sha256':hashlib.sha256((R/'single_stock/index.json').read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256((R/'lookback_patch/index.json').read_bytes()).hexdigest()};(A/'query_migration_independent.json').write_text(json.dumps(out,indent=2));print(out)
