from pathlib import Path
import ast,copy,json
from collections import Counter
p=Path(__file__).with_name('migrate_reference.py');tree=ast.parse(p.read_text());ns={'copy':copy,'counts':{'60':Counter()},'refs':{60:{}},'ALLOWED':{'reasons','eligible','reference_count_events','reference_count_stocks','reference_small_sample'}}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='update'],type_ignores=[]),'update','exec'),ns)
base={'row_id':'rise_0','column_id':'up_0','reasons':['empty_reference_cell'],'eligible':False,'reference_count_events':0,'reference_count_stocks':0,'reference_small_sample':True,'prior60_change':.02,'base_price':123.4,'date':'2026-01-01','global_calendar_index':4000}
cell={'count_events':80,'count_stocks':20,'small_sample':False};ns['refs'][60][('public_nextopen','rise_0','up_0')]=cell
z=ns['update'](copy.deepcopy(base),60,'public_nextopen');assert z['eligible'] and not z['reasons']
z=copy.deepcopy(base);z['reasons']=['future_notice','empty_reference_cell'];z=ns['update'](z,60,'public_nextopen');assert not z['eligible'] and z['reasons']==['future_notice']
ns['refs'][60][('public_nextopen','rise_0','up_0')]={'count_events':0,'count_stocks':0,'small_sample':True};z=copy.deepcopy(base);z.update(reasons=[],eligible=True);z=ns['update'](z,60,'public_nextopen');assert not z['eligible'] and z['reasons']==['empty_reference_cell']
z=copy.deepcopy(base);z.update(row_id=None,reasons=['holder_unchanged'],eligible=False);z=ns['update'](z,60,'public_nextopen');assert not z['eligible'] and z['reasons']==['holder_unchanged']
print(json.dumps({'status':'PASS_SYNTHETIC_CONTRACT_ONLY','cases':4,'real_new_matrices_used':False,'new_query_outputs_generated':False}))
