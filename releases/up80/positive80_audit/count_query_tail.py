from pathlib import Path
import json,gzip,collections,math
R=Path(__file__).resolve().parent;B=R/'baseline/single_stock_patch';ix=json.load(open(B/'index.json'));counts={n:collections.Counter() for n in [10,20,30,60,120]};examples=[]
for item in ix['stocks']:
 j=json.loads(gzip.decompress((B/item['file']).read_bytes()))
 for nid,node in j['nodes'].items():
  for n in counts:
   for a,z in node['anchors_by_lookback'][str(n)].items():
    x=z['prior_change'];v=abs(x) if x is not None else float('nan')
    if abs(v-.8)<=1e-12:v=.8
    if not math.isfinite(v) or v<.8:continue
    side='positive' if x>0 else 'negative';counts[n][side]+=1
    if side=='positive':
     other=[r for r in z['reasons'] if r not in ['price_magnitude_at_least80','empty_reference_cell']];okay=not other and z['row_id'] is not None;counts[n]['other_conditions_pass']+=int(okay)
     if okay and sum(e['n']==n for e in examples)<3:examples.append({'code':item['code'],'id':nid,'n':n,'anchor':a,'change':x,'base_price':z['base_price'],'row_id':z['row_id'],'other_reasons':other})
out={'status':'PASS_FROZEN_SOURCE_COUNT_ONLY','counts':{str(n):dict(x) for n,x in counts.items()},'examples':examples};(R/'query_tail_independent.json').write_text(json.dumps(out,indent=2));print(out['counts'])
