"""Idempotent metadata-only policy for the2343 expansion, never old validation."""
from pathlib import Path
from collections import Counter
import json,hashlib

def finalize_metadata(meta,root,periods=None):
 root=Path(root);inputs=json.load(open(root/'INPUT_COMPLETENESS.json'));preserve=json.load(open(root/'OLD1494_PRESERVATION.json'));grid=json.load(open(root/'OLD1494_FULL_GRID_REGRESSION.json'));assert inputs['status']=='complete' and preserve['status']==grid['status']=='PASS'
 old=set(inputs['frozen_old1494_codes']);prices=inputs['prices'];status=dict(sorted(Counter(x['status'] for x in prices).items()));added=[x for x in prices if x['code'] not in old];assert len(old)==1494 and len(prices)==2343 and len(added)==849
 meta['recovery_note']='The2343-stock expansion preserves the complete frozen1494 inputs and adds849 stocks. Actual old1494 canonical events, both251-day paths, all five-lookback81-cell matrices and stability statistics passed local preservation regression; expanded totals are new estimates. Independent release audit is separate.'
 meta['archived_provenance_note']='Archived fields describe the prior1494 published snapshot only. The old1494 inputs remain frozen; additional source acquisition concerns849 newly included stocks, not a refetch or replacement of old1494 data.'
 meta['source_provenance']={'frozen_reference_stocks':1494,'added_stocks':849,'current_pool_stocks':2343,'frozen1494_inputs_preserved':True,'old1494_canonical_and_paths_local_regression':'PASS','old1494_all_five_81cell_and_stability_local_regression':'PASS','new_total_estimates_must_equal_old_totals':False,'independent_release_audit':'separate_required_gate','input_manifest_sha256':hashlib.sha256((root/'INPUT_COMPLETENESS.json').read_bytes()).hexdigest()}
 meta['price_coverage']={'scope':'current complete input manifest; not inferred from mature model events','accounted_pool_stocks':len(prices),'price_file_stocks':sum(x['status'] in ['ok','reused'] for x in prices),'verified_empty_price_stocks':status.get('empty_no_price',0),'status_counts':status,'frozen_old_stocks':len(old),'added_stocks':len(added),'added_status_counts':dict(sorted(Counter(x['status'] for x in added).items()))}
 if 'history_extension' in meta:meta['history_extension']['source_snapshot']='Frozen old1494 historical inputs retained; added849 input sources documented in this expansion capture and merge audits.'
 selection='股票池根据2015年10月至2026年10月的历史披露记录回溯筛选：曾在至少一个完整三自然月窗口达到原月频条件；不代表全程或当前持续月频。当前名册、生存及选池偏差仍存在。'
 origin='本轮完整保留旧1494股冻结输入，另补849股数据；旧1494逐事件、双251日路径、全部5种回看期的81格及分期统计已通过本地保全回归，发布仍须独立审计。'
 warnings=[]
 for w in meta.get('warnings',[]):
  if w.startswith('本轮使用恢复的事件级输入') or w.startswith('本轮完整保留旧1494股冻结输入'):continue
  if '股票池按近期披露频率' in w or w.startswith('股票池是2015年10月') or w.startswith('股票池根据2015年10月') or w.startswith('本池代表2015年10月'):
   if selection not in warnings:warnings.append(selection)
   continue
  if periods is not None and (w.startswith('第一期') or w.startswith('2010起采集；实际可分析起点为')):continue
  warnings.append(w)
 if selection not in warnings:warnings.append(selection)
 if periods is not None:
  allperiods=[x for x in periods if x['sample_mode']=='all_events'];first=min((x['first_notice'] for x in allperiods if x.get('first_notice')),default=None)
  warnings.insert(0,f'2010起采集；本回看期实际可分析起点为{first}，各年覆盖和样本数不同。' if first else '2010起采集；本回看期暂无成熟分析样本。')
  early=next((x for x in allperiods if x['period']=='2010–2014'),None);months=meta.get('early_period_month_counts',{})
  if early:
   assert sum(months.values())==early['source_events']
   warnings.append(f"第一期{early['source_events']}条，按月份分布{months}；早期样本月份分布不均，请勿仅凭延长年份声称稳定。")
 warnings.append(origin);meta['warnings']=list(dict.fromkeys(warnings));meta['metadata_policy_version']='expanded2343-frozen1494-added849-v1';return meta
