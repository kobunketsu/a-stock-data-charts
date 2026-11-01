import json,collections,datetime as dt,statistics,csv,pathlib
root=pathlib.Path('historical-capture/shareholder_frequency');a=json.load(open(root/'raw.json'));lo=dt.date(2026,8,1);hi=dt.date(2026,10,31)
def date(s): return dt.date.fromisoformat(s[:10])
def ashare(c): return c.startswith(('0','3','6','8','92','43'))
latest=json.load(open(root/'latest.json'));listed={r['SECURITY_CODE'] for r in latest if '退' not in r['SECURITY_NAME_ABBR']};groups=collections.defaultdict(list)
for x in a:
 if ashare(x['SECURITY_CODE']) and x['SECURITY_CODE'] in listed:groups[x['SECURITY_CODE']].append(x)
results=[]
for c,rs in groups.items():
 # earliest available disclosure for each endpoint, then keep only advancing endpoints
 first={}
 for x in rs:
  e=date(x['END_DATE']);n=date(x['HOLD_NOTICE_DATE'])
  if e not in first or n<first[e]:first[e]=n
 by_notice=collections.defaultdict(list)
 for e,n in first.items():by_notice[n].append(e)
 events=[];highest=dt.date.min
 for n,es in sorted(by_notice.items()):
  e=max(es)
  if e>highest:events.append((n,e));highest=e
 ds=[x[0] for x in events];ends=[x[1] for x in events];gaps=[(y-x).days for x,y in zip(ds,ds[1:])];egaps=[(y-x).days for x,y in zip(ends,ends[1:])]
 row=dict(code=c,name=rs[0]['SECURITY_NAME_ABBR'],raw_records=len(rs),events=len(events),first=str(ds[0]),last=str(ds[-1]),span=(ds[-1]-ds[0]).days,first_gap=(ds[0]-lo).days,last_gap=(hi-ds[-1]).days,median_gap=statistics.median(gaps) if gaps else None,mean_gap=statistics.mean(gaps) if gaps else None,max_gap=max(gaps) if gaps else None,last_endpoint=str(ends[-1]),median_endpoint_gap=statistics.median(egaps) if egaps else None,event_dates=';'.join(str(x) for x in ds),endpoint_dates=';'.join(str(x) for x in ends))
 results.append(row)
base=[r for r in results if r['events']>=6 and r['span']>=60]
metrics={'raw_count':len(a),'unique_raw_rows':len({json.dumps(x,sort_keys=True) for x in a}),'all_codes':len({x['SECURITY_CODE'] for x in a}),'excluded_codes':sorted({x['SECURITY_CODE'] for x in a if not ashare(x['SECURITY_CODE'])}),'latest_table_codes':len(latest),'latest_non_retired_name_codes':len(listed),'ashare_codes':len(groups),'qualifying_base_6events_60days':len(base),'strict_internal_max_lt14':len([r for r in base if r['max_gap']<14]),'strict_edges_lt14':len([r for r in base if max(r['max_gap'],r['first_gap'],r['last_gap'])<14]),'median_lt14':len([r for r in base if r['median_gap']<14]),'mean_lt14':len([r for r in base if r['mean_gap']<14]),'mean_lt14_recent':len([r for r in base if r['mean_gap']<14 and r['last_gap']<14]),'mean_le14_recent':len([r for r in base if r['mean_gap']<=14 and r['last_gap']<=14]),'strict_edges_le14':len([r for r in base if max(r['max_gap'],r['first_gap'],r['last_gap'])<=14]),'median_endpoint_lt14':len([r for r in base if r['median_endpoint_gap']<14]),'any_event_pair_lt14':sum(any((date(y)-date(x)).days<14 for x,y in zip(r['event_dates'].split(';'),r['event_dates'].split(';')[1:])) for r in results)}
(root/'summary.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
with open(root/'per_stock.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(sorted(results,key=lambda r:r['code']))
(root/'strict.json').write_text(json.dumps([r for r in base if max(r['max_gap'],r['first_gap'],r['last_gap'])<14],ensure_ascii=False,indent=2))
print(json.dumps(metrics,ensure_ascii=False,indent=2));print('examples',json.dumps(sorted(base,key=lambda r:(r['max_gap'],r['mean_gap']))[:8],ensure_ascii=False,indent=2))
