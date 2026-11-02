from pathlib import Path
import pandas as pd,urllib.request,urllib.parse,urllib.error,json,time,hashlib,threading,concurrent.futures,datetime
O=Path(__file__).resolve().parent;ROOT=O.parents[1];ARC=ROOT/'archive972/shareholder_system_972';old=sorted(pd.read_csv(ARC/'qualified_972.csv',dtype={'code':str}).code);allcodes=sorted(pd.read_csv(ROOT/'qualified_1494.csv',dtype={'code':str}).code);new=sorted(set(allcodes)-set(old));assert len(old)==972 and len(new)==522
stop=threading.Event();lock=threading.Lock();manifest=[];errors=[];jobs=[]
for name,codes,report,end in [('det_added',new,'RPT_HOLDERNUM_DET','2026-10-31'),('det_old_early',old,'RPT_HOLDERNUM_DET','2018-12-31'),('f10_all',allcodes,'RPT_F10_EH_HOLDERNUM','2019-12-31')]:
 for start in range(0,len(codes),100):jobs.append((f'{name}_{start//100:02d}',codes[start:start+100],report,end))
def log(*x):print(datetime.datetime.now(datetime.timezone.utc).isoformat(),*x,flush=True)
def fetch(name,codes,report,end,page):
 field='NOTICE_DATE' if report=='RPT_F10_EH_HOLDERNUM' else 'HOLD_NOTICE_DATE';fil='(SECURITY_CODE in ('+','.join('"'+c+'"' for c in codes)+'))'+f"({field}>='2009-01-01')({field}<='{end}')";p=dict(reportName=report,columns='ALL',pageSize=500,pageNumber=page,filter=fil,sortColumns=f'SECURITY_CODE,{field},END_DATE',sortTypes='1,1,1',source='WEB',client='WEB');url='https://datacenter-web.eastmoney.com/api/data/v1/get?'+urllib.parse.urlencode(p);fn=O/f'{name}_page{page:04d}.json'
 if fn.exists():b=fn.read_bytes()
 else:
  for attempt in range(2):
   if stop.is_set():raise RuntimeError('All-host collection stopped after refusal')
   try:
    with urllib.request.urlopen(url,timeout=45) as r:b=r.read()
    fn.write_bytes(b);break
   except urllib.error.HTTPError as e:
    if e.code in [401,403,429]:stop.set();log('REFUSAL_STOP',e.code,url);raise
    if e.code<500 or attempt:raise
    time.sleep(2)
   except urllib.error.URLError as e:
    msg=str(e).lower()
    if any(x in msg for x in ['403','401','429','forbidden','denied','unauthorized']):stop.set();log('REFUSAL_STOP_URLERROR',repr(e),url);raise
    if attempt:raise
    time.sleep(2)
   except TimeoutError:
    if attempt:raise
    time.sleep(2)
 d=json.loads(b)
 if not d.get('success') and d.get('code')!=9201:raise ValueError(str(d))
 rr=d.get('result') or {};rows=rr.get('data') or []
 with lock:manifest.append({'file':fn.name,'url':url,'sha256':hashlib.sha256(b).hexdigest(),'rows':len(rows),'count':rr.get('count',0),'pages':rr.get('pages',0),'report':report,'name':name,'page':page});(O/'manifest_progress.json').write_text(json.dumps(manifest,indent=2))
 return d,rows
def job(spec):
 if stop.is_set():raise RuntimeError('Stopped; no next group')
 name,codes,report,end=spec;d,rows=fetch(name,codes,report,end,1);r=d.get('result') or {};total=r.get('count',0);pages=r.get('pages',0);log('COUNT',name,len(codes),total,pages)
 for page in range(2,pages+1):rows.extend(fetch(name,codes,report,end,page)[1])
 assert len(rows)==total;(O/(name+'_all.json')).write_text(json.dumps(rows,ensure_ascii=False));log('DONE',name,len(rows));return name,rows
allrows={'det_added':[],'det_old_early':[],'f10_all':[]}
with concurrent.futures.ThreadPoolExecutor(2) as ex:
 fs={ex.submit(job,spec):spec[0] for spec in jobs}
 for f in concurrent.futures.as_completed(fs):
  name=fs[f]
  try:
   name,rows=f.result();kind=next(k for k in allrows if name.startswith(k+'_'));allrows[kind].extend(rows)
  except Exception as e:errors.append({'job':name,'error':repr(e)});log('ERROR',name,repr(e))
for k,v in allrows.items():(O/(k+'_all_raw.json')).write_text(json.dumps(v,ensure_ascii=False))
summary={'status':'complete' if not errors else 'incomplete','counts':{k:{'rows':len(v),'stocks':len({r['SECURITY_CODE'] for r in v})} for k,v in allrows.items()},'errors':errors,'stop_on_refusal':stop.is_set(),'files':manifest,'frozen_old2019plus':'archive972/shareholder_system_972','newcodes':new};(O/'CAPTURE_MANIFEST.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));log('FINISH',summary['counts'],errors)
