#!/usr/bin/env python3
"""Read-only public Eastmoney holder history; bounded concurrency/retries, raw snapshots."""
import http.client
import csv,json,urllib.request,urllib.parse,urllib.error,time,hashlib,threading,concurrent.futures,datetime,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
POOL=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'qualified_453.csv'
START='2020-01-01'; END='2026-10-31'; URL='https://datacenter-web.eastmoney.com/api/data/v1/get'
stop=threading.Event(); lock=threading.Lock(); manifest=json.loads((ROOT/'manifest_progress.json').read_text()) if (ROOT/'manifest_progress.json').exists() else []
def log(*a): print(datetime.datetime.now(datetime.timezone.utc).isoformat(),*a,flush=True)
def fetch(group,codes,page):
 filt='(SECURITY_CODE in ('+','.join('"'+c+'"' for c in codes)+'))'+f"(HOLD_NOTICE_DATE>='{START}')(HOLD_NOTICE_DATE<='{END}')"
 p=dict(reportName='RPT_HOLDERNUM_DET',columns='ALL',pageSize=500,pageNumber=page,filter=filt,sortColumns='SECURITY_CODE,HOLD_NOTICE_DATE,END_DATE',sortTypes='1,1,1',source='WEB',client='WEB')
 url=URL+'?'+urllib.parse.urlencode(p); fn=ROOT/f'group{group:02d}_page{page:04d}.json'
 if fn.exists(): return json.loads(fn.read_text())
 for attempt in range(3):
  if stop.is_set(): raise RuntimeError('Collection halted following refusal')
  try:
   r=urllib.request.urlopen(url,timeout=45); b=r.read(); d=json.loads(b)
   if not d.get('success'): raise ValueError(str(d))
   fn.write_bytes(b); fn.chmod(0o444)
   with lock:
    manifest.append(dict(file=fn.name,url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=len(d['result']['data']),count=d['result']['count'],pages=d['result']['pages']))
    (ROOT/'manifest_progress.json').write_text(json.dumps(manifest,indent=2))
   time.sleep(.3); return d
  except urllib.error.HTTPError as e:
   if e.code in (401,403,429): stop.set();raise
   if attempt==2:raise
   time.sleep(2*(attempt+1))
  except (TimeoutError,urllib.error.URLError,http.client.IncompleteRead) as e:
   if attempt==2:raise
   time.sleep(2*(attempt+1))
def group_task(g,codes):
 d=fetch(g,codes,1); result=d['result'];rows=list(result['data']);log('COUNT',g,len(codes),'stocks',result['count'],'rows',result['pages'],'pages')
 (ROOT/f'group{g:02d}_count.json').write_text(json.dumps(dict(codes=codes,count=result['count'],pages=result['pages'])))
 for p in range(2,result['pages']+1):
  rows.extend(fetch(g,codes,p)['result']['data'])
  if p%10==0: log('PROGRESS',g,p,result['pages'])
 if len(rows)!=result['count']:raise ValueError(f'row count mismatch {g}')
 (ROOT/f'group{g:02d}_all.json').write_text(json.dumps(rows,ensure_ascii=False));log('DONE',g,len(rows));return rows
pool=list(csv.DictReader(POOL.open(encoding='utf-8-sig')))
col=next((c for c in ['SECURITY_CODE','code','代码','股票代码','security_code'] if c in pool[0]),None)
if col is None: raise ValueError('Unknown code column '+repr(pool[0]))
codes=sorted(set(r[col].zfill(6) for r in pool));assert len(codes)==453,len(codes)
(ROOT/'pool_codes.json').write_text(json.dumps(codes));groups=[codes[i:i+100] for i in range(0,len(codes),100)];allrows=[];errors=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 fs={ex.submit(group_task,g,c):g for g,c in enumerate(groups)}
 for f in concurrent.futures.as_completed(fs):
  try:allrows.extend(f.result())
  except Exception as e:errors.append(dict(group=fs[f],error=repr(e)));log('ERROR',fs[f],repr(e))
(ROOT/'all_raw.json').write_text(json.dumps(allrows,ensure_ascii=False))
if allrows:
 with (ROOT/'events_raw.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
(ROOT/'manifest.json').write_text(json.dumps(dict(source=URL,report='RPT_HOLDERNUM_DET',start=START,end=END,pool_size=len(codes),original_pool=str(POOL),files=manifest,errors=errors,limitations=['HOLD_NOTICE_DATE is provider announcement date, not verified first public timestamp','Current453stock pool introduces historical selection/survivorship bias','Coverage start is not listing date']),ensure_ascii=False,indent=2))
log('FINISH',len(allrows),'rows',len(set(r['SECURITY_CODE'] for r in allrows)),'stocks',errors)
