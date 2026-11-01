import csv,json,datetime,pathlib,collections,hashlib
R=pathlib.Path(__file__).resolve().parent
rows=json.loads((R/'all_raw.json').read_text());pool=json.loads((R/'pool_codes.json').read_text())
def date(v):return datetime.date.fromisoformat(v[:10]) if v else None
def dump(name,data):
 if not data:return
 with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
by=collections.defaultdict(list);year=collections.Counter();negative=[];laglong=[];missing=[];exact=collections.Counter();keys=collections.Counter();nulls=collections.Counter();shares=0
for r in rows:
 by[r['SECURITY_CODE']].append(r);n=date(r.get('HOLD_NOTICE_DATE'));e=date(r.get('END_DATE'))
 if n:year[n.year]+=1
 for k in ['SECURITY_CODE','HOLD_NOTICE_DATE','END_DATE','HOLDER_NUM']:
  if r.get(k) is None:nulls[k]+=1
 if n and e:
  if e>n:negative.append(r)
  if (n-e).days>30:laglong.append(r)
 if r.get('CHANGE_SHARES'):shares+=1
 exact[json.dumps(r,sort_keys=True,ensure_ascii=False)]+=1
 keys[(r.get('SECURITY_CODE'),r.get('END_DATE'),r.get('HOLD_NOTICE_DATE'))]+=1
coverage=[]
for c in pool:
 a=by[c]
 if not a:missing.append(c);continue
 nd=sorted(date(r['HOLD_NOTICE_DATE']) for r in a if r.get('HOLD_NOTICE_DATE')); ed=sorted(date(r['END_DATE']) for r in a if r.get('END_DATE'))
 coverage.append(dict(SECURITY_CODE=c,SECURITY_NAME_ABBR=a[-1]['SECURITY_NAME_ABBR'],rows=len(a),first_announcement_date=str(nd[0]),last_announcement_date=str(nd[-1]),first_endpoint=str(ed[0]),last_endpoint=str(ed[-1]),span_days=(nd[-1]-nd[0]).days,has_2020_announcement=any(x.year==2020 for x in nd),five_year_observed_span=(nd[-1]-nd[0]).days>=1826,listing_date_verified=False))
dump('coverage_by_stock.csv',coverage);dump('invalid_negative_lag.csv',negative)
qa=dict(rows=len(rows),stocks=len(set(r['SECURITY_CODE'] for r in rows)),missing_codes=missing,announcement_year_rows=dict(year),null_critical_fields=dict(nulls),negative_lag_count=len(negative),lag_over_30_days=len(laglong),share_change_rows=shares,exact_duplicate_excess=sum(v-1 for v in exact.values()),code_endpoint_announcement_duplicate_excess=sum(v-1 for v in keys.values()),stocks_with_five_year_observed_span=sum(r['five_year_observed_span'] for r in coverage),stocks_with_2020_announcement=sum(r['has_2020_announcement'] for r in coverage),min_announcement=min(r['HOLD_NOTICE_DATE'] for r in rows),max_announcement=max(r['HOLD_NOTICE_DATE'] for r in rows),announcement_first_public_timestamp_verified=False,listing_date_verified=False,warning='Observed data span does not establish listing date; raw rows retained including anomalous dates. Model must filter anomalies and reconstruct PIT previous count from prior known announcements.')
(R/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False,indent=2))
