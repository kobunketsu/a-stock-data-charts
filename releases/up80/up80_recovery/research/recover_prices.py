from pathlib import Path
import json,csv,subprocess,urllib.request,urllib.error,socket,threading,concurrent.futures,datetime,time,bisect,hashlib,math,argparse
O=Path(__file__).resolve().parent;REC=O.parent;ARC=REC/'archive972/shareholder_system_972';AR=ARC/'source_provenance/price_captures/raw_prices';parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['missing','archived'],required=True);args=parser.parse_args();stop=threading.Event();lock=threading.Lock();results=[];started=time.monotonic()
def get(u):
 for attempt in range(2):
  if stop.is_set():raise RuntimeError('not_attempted_after_refusal')
  try:
   with urllib.request.urlopen(u,timeout=25) as r:return r.read().decode()
  except urllib.error.HTTPError as e:
   if e.code in [401,403,429]:stop.set();raise
   if 500<=e.code<600 and attempt==0:time.sleep(1);continue
   raise
  except (TimeoutError,socket.timeout):
   if attempt==0:time.sleep(1);continue
   raise
  except urllib.error.URLError as e:
   if any(x in str(e.reason) for x in ['403','401','429']):stop.set();raise
   if isinstance(e.reason,(TimeoutError,socket.timeout)) and attempt==0:time.sleep(1);continue
   raise

def fetch(t):
 c=t['code'];sym=('sh' if c.startswith('6') else 'bj' if c.startswith(('8','4','92')) else 'sz')+c;u=f'https://finance.sina.com.cn/realstock/company/{sym}/hisdata/klc_kl.js';fu=f'https://finance.sina.com.cn/realstock/company/{sym}/hfq.js';out={'code':c,'name':t.get('name'),'mode':args.mode,'price_url':u,'factor_url':fu,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  if args.mode=='archived':rp=AR/(c+'_full.js');fp=AR/(c+'_hfq.txt');out['source']='frozen_archive_raw'
  else:
   rp=O/'raw_prices'/(c+'_full.js');fp=O/'raw_prices'/(c+'_hfq.txt')
   if not rp.exists():rp.write_text(get(u))
   if not fp.exists():fp.write_text(get(fu))
   out['source']='network_or_current_checkpoint'
  a=json.loads(subprocess.check_output(['node',str(O/'sina_decoder.js'),str(rp)],stderr=subprocess.PIPE,timeout=30));s=fp.read_text();obj=json.JSONDecoder().raw_decode(s[s.index('{'):])[0];assert isinstance(obj.get('data'),list),'missing_factors';fac=sorted((r['d'],float(r['f'])) for r in obj['data']);assert fac or obj.get('total') in [0,'0'],'missing_factors';fd=[x[0] for x in fac];rows=[]
  for r in a:
   date=r['date'][:10]
   if not '2009-01-01'<=date<='2026-10-30':continue
   j=bisect.bisect_right(fd,date)-1
   if fac and j<0:raise ValueError('factor_unavailable_at_'+date)
   f=fac[j][1] if j>=0 else 1.;v={k:float(r[k]) for k in ['open','high','low','close','volume']};assert all(math.isfinite(x) for x in v.values()) and math.isfinite(f) and f>0
   if min(v[k] for k in ['open','high','low','close'])<=0:continue
   rows.append({'date':date,**{k:v[k]*f for k in ['open','high','low','close']},'volume':v['volume'],'adjustment_factor':f,**{'raw_'+k:v[k] for k in ['open','high','low','close']}})
  rows.sort(key=lambda x:x['date']);assert rows and len({r['date'] for r in rows})==len(rows)
  tmp=O/'prices'/(c+'.tmp')
  with tmp.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  if args.mode=='archived':
   old=(ARC/'prices'/f'{c}.csv').read_bytes();h,body=old.split(b'\n',1);prefix=b''.join(x for x in tmp.read_bytes().splitlines(keepends=True)[1:] if x[:10]<b'2019-01-01');tmp.write_bytes(h+b'\n'+prefix+body);assert b''.join(x for x in tmp.read_bytes().splitlines(keepends=True)[1:] if x[:10]>=b'2019-01-01')==body;out['old_2019plus_rows_byte_identical']=True
  tmp.replace(O/'prices'/f'{c}.csv');out.update(status='ok',rows=len(rows),first_date=rows[0]['date'],last_date=rows[-1]['date'],pre2019_rows=sum(r['date']<'2019-01-01' for r in rows),raw_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),factor_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),csv_sha256=hashlib.sha256((O/'prices'/f'{c}.csv').read_bytes()).hexdigest())
 except Exception as e:out.update(status='error',error=type(e).__name__+':'+str(e))
 with lock:
  results.append(out)
  with (O/f'{args.mode}_results.jsonl').open('a') as f:f.write(json.dumps(out,ensure_ascii=False)+'\n')
  if len(results)%25==0 or out['status']!='ok':print(json.dumps({'completed':len(results),'code':c,'status':out['status'],'error':out.get('error'),'elapsed_minutes':(time.monotonic()-started)/60},ensure_ascii=False),flush=True)
 return out
if args.mode=='missing':stocks=list(csv.DictReader((REC/'price_missing_codes.csv').open(encoding='utf-8-sig')))
else:stocks=list(csv.DictReader((ARC/'qualified_972.csv').open(encoding='utf-8-sig')))
if (O/f'{args.mode}_results.jsonl').exists():
 results=[json.loads(x) for x in (O/f'{args.mode}_results.jsonl').read_text().splitlines() if x.strip()]
 if any(any(k in r.get('error','') for k in ['403','401','429','refusal']) for r in results):raise SystemExit('Prior refusal: no automated resume')
 done={r['code'] for r in results};stocks=[r for r in stocks if r['code'] not in done]
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 for _ in ex.map(fetch,stocks):pass
(O/f'{args.mode}_manifest.json').write_text(json.dumps({'mode':args.mode,'stop_on_refusal':stop.is_set(),'results':results,'total':len(results)},ensure_ascii=False,indent=2));print('DONE',len(results),sum(r['status']=='ok' for r in results),flush=True)
