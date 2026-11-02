"""Paired common-sufficient-cell comparisons, coverage and concentration; descriptive, not significance."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,required=True);P.add_argument('--old-root',type=Path,required=True);a=P.parse_args();B=a.root;OLD=a.old_root;O=B/'comparison';O.mkdir(exist_ok=True)
keys=['sample_mode','granularity','period','anchor','row_id','column_id','horizon'];metrics=['mean','median','equal_stock_mean'];tables=[];concentration=[]
for n in [10,20,30,60,120]:
 old=pd.read_csv(OLD/'lookbacks'/f'lookback_{n}/stability/stability_statistics.csv');new=pd.read_csv(B/'lookbacks'/f'lookback_{n}/stability/stability_statistics.csv');q=old.merge(new,on=keys,suffixes=('_old','_new'),how='outer',indicator=True);q.insert(0,'lookback_market_days',n);q['both_sufficient']=(q['_merge']=='both')&(q.count_events_old>=50)&(q.count_stocks_old>=10)&(q.count_events_new>=50)&(q.count_stocks_new>=10);q['newly_sufficient']=(q.count_events_new>=50)&(q.count_stocks_new>=10)&~((q.count_events_old>=50)&(q.count_stocks_old>=10))
 for m in metrics:q[m+'_change']=q[m+'_new']-q[m+'_old'];q[m+'_sign_changed']=(np.sign(q[m+'_new'])!=np.sign(q[m+'_old']))&q[m+'_new'].notna()&q[m+'_old'].notna()
 tables.append(q)
 for label,root in [('old1494',OLD),('new2343',B)]:
  r=root/'lookbacks'/f'lookback_{n}';p=pd.read_csv(r/'statdate_only/event_panel_statdate.csv',dtype={'code':str});members=pd.read_csv(r/'holder_matrix_9rows/event_membership.csv');mm=members.merge(p[['event_id','code','notice']],on='event_id',validate='many_to_one');mm['period']=pd.cut(pd.to_datetime(mm.notice).dt.year,[2009,2014,2019,2022,2100],labels=['2010–2014','2015–2019','2020–2022','2023起成熟样本']).astype(str);non=set(pd.read_csv(r/'stability/nonoverlapping_membership.csv').event_id)
  base=pd.read_csv(r/'threshold_curves/ranges_uniform60/matched_all_years_event_membership.csv',dtype={'code':str});base['period']=pd.cut(pd.to_datetime(base.notice).dt.year,[2009,2014,2019,2022,2100],labels=['2010–2014','2015–2019','2020–2022','2023起成熟样本']).astype(str)
  for mode,g0 in [('all_events',base),('nonoverlapping250',base[base.event_id.isin(non)])]:
   for era,g in [('ALL',g0),*list(g0.groupby('period'))]:
    if not len(g):continue
    c=g.code.value_counts();w=c/len(g);concentration.append({'lookback_market_days':n,'pool':label,'sample_mode':mode,'scope':'common_complete_base','anchor':'both_common_base','row_id':'ALL','column_id':'ALL','period':era,'count_events':len(g),'count_stocks':len(c),'largest_stock_share':float(w.max()),'top10_stock_share':float(w.iloc[:10].sum()),'inverse_hhi_equivalent_stocks':float(1/(w*w).sum())})
  for mode,s in [('all_events',mm),('nonoverlapping250',mm[mm.event_id.isin(non)])]:
   for (anchor,row,col,era),g in s.groupby(['anchor','row_id','column_id','period']):
    c=g.code.value_counts();w=c/len(g);concentration.append({'lookback_market_days':n,'pool':label,'sample_mode':mode,'scope':'cell','anchor':anchor,'row_id':row,'column_id':col,'period':era,'count_events':len(g),'count_stocks':len(c),'largest_stock_share':float(w.max()),'top10_stock_share':float(w.iloc[:10].sum()),'inverse_hhi_equivalent_stocks':float(1/(w*w).sum())})
D=pd.concat(tables,ignore_index=True);D.to_csv(O/'paired_cell_period_statistics.csv',index=False);D[D.both_sufficient].to_csv(O/'common_sufficient_cell_period_statistics.csv',index=False);pd.DataFrame(concentration).to_csv(O/'stock_concentration.csv',index=False)
# Stability ranges/sign reversals only over exactly the same sufficiently sampled eras, never different denominators.
out=[];eras=D[(D.granularity=='era')&D.both_sufficient]
for key,g in eras.groupby(['lookback_market_days','sample_mode','anchor','row_id','column_id','horizon']):
 if len(g)<2:continue
 for metric in metrics:
  v={}
  for suffix in ['old','new']:
   x=g[f'{metric}_{suffix}'].dropna().to_numpy();v[suffix+'_era_range']=float(x.max()-x.min()) if len(x) else None;v[suffix+'_has_positive_and_negative']=bool((x>0).any() and (x<0).any())
  out.append(dict(zip(['lookback_market_days','sample_mode','anchor','row_id','column_id','horizon'],key))|{'metric':metric,'shared_sufficient_era_count':len(g),'shared_eras':'|'.join(sorted(g.period)),**v})
pd.DataFrame(out).to_csv(O/'paired_era_stability.csv',index=False)
summary={'status':'computed_descriptive_comparison','paired_rows':len(D),'common_sufficient_rows':int(D.both_sufficient.sum()),'newly_sufficient_rows':int(D.newly_sufficient.sum()),'warning':'More coverage or lower concentration does not establish temporal independence, statistical significance, causation, or improved predictive stability. InverseHHI denotes equivalent stock concentration, not independent observations.'};(O/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(summary)
