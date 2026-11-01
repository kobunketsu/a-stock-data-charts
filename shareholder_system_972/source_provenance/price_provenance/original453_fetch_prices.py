import subprocess, shutil, hashlib
import urllib.request,urllib.parse,urllib.error,json,csv,pathlib,datetime,time,concurrent.futures,threading,bisect,traceback
ROOT=pathlib.Path('historical-capture/shareholder_model_v2'); P=ROOT/'prices'; RAW=ROOT/'raw_prices'; P.mkdir(exist_ok=True);RAW.mkdir(exist_ok=True)
stop=threading.Event();lock=threading.Lock(); results=[]
def get(url):
 for attempt in range(2):
  if stop.is_set():raise RuntimeError('stopped after rate-limit/access refusal')
  try:
   with urllib.request.urlopen(url,timeout=25) as r:return r.read().decode('utf-8')
  except urllib.error.HTTPError as e:
   if e.code in (401,403,429):stop.set();raise
   if e.code>=500 and attempt==0:time.sleep(1);continue
   raise
  except (TimeoutError,OSError) as e:
   if attempt==0:time.sleep(1);continue
   raise

def symbol(c):return ('sh' if c.startswith('6') else 'bj' if c.startswith(('8','4','92')) else 'sz')+c

def fetch(item):
 code,name,sym,index=item
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 u='https://finance.sina.com.cn/realstock/company/'+sym+'/hisdata/klc_kl.js'
 fu='https://finance.sina.com.cn/realstock/company/'+sym+'/hfq.js'
 out={'code':code,'name':name,'symbol':sym,'is_index':index,'price_url':u,'factor_url':None if index else fu,'retrieved_at_utc':started}
 try:
  rp=RAW/(code+'_full.js')
  if rp.exists():s=rp.read_text()
  else:s=get(u);rp.write_text(s)
  decoded=subprocess.check_output(['node',str(ROOT/'sina_decoder.js'),str(rp)],timeout=25)
  a=json.loads(decoded); out['raw_sha256']=hashlib.sha256(s.encode()).hexdigest()
  out['full_first_date']=a[0]['date'][:10];out['full_last_date']=a[-1]['date'][:10];out['full_rows']=len(a)
  if not isinstance(a,list) or not a:raise ValueError('empty/nonlist OHLCV')
  fac=[]
  if not index:
   cached=pathlib.Path('historical-capture/shareholder_model/raw_prices')/(code+'_hfq.txt')
   fs=cached.read_text() if cached.exists() else get(fu);(RAW/(code+'_hfq.txt')).write_text(fs)
   out['factor_reused_v1']=cached.exists();out['factor_sha256']=hashlib.sha256(fs.encode()).hexdigest()
   obj=json.JSONDecoder().raw_decode(fs[fs.index('{'):])[0]
   if not isinstance(obj.get('data'),list):raise ValueError('no factor data')
   fac=sorted((r['d'],float(r['f'])) for r in obj['data'])
   if not fac and obj.get('total') not in (0,'0'):raise ValueError('missing factors')
  fdates=[r[0] for r in fac]; rows=[]
  for r in a:
   d=r['date'][:10]
   if d<'2019-01-01' or d>'2026-10-30':continue
   j=bisect.bisect_right(fdates,d)-1
   f=fac[j][1] if j>=0 else 1.0
   if not index and fac and j<0:raise ValueError('date before earliest factor')
   row={'date':d,'open':float(r['open'])*f,'high':float(r['high'])*f,'low':float(r['low'])*f,'close':float(r['close'])*f,'volume':float(r['volume']),'adjustment_factor':f,'raw_open':float(r['open']),'raw_high':float(r['high']),'raw_low':float(r['low']),'raw_close':float(r['close'])}
   if min(row[k] for k in ['open','high','low','close'])<=0:continue
   rows.append(row)
  rows.sort(key=lambda r:r['date'])
  if len({r['date'] for r in rows})!=len(rows):raise ValueError('duplicate price dates')
  if not rows:raise ValueError('no dates in target window')
  tmp=P/(code+'.tmp')
  with tmp.open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  tmp.replace(P/(code+'.csv'))
  out.update(status='ok',rows=len(rows),first_date=rows[0]['date'],last_date=rows[-1]['date'],adjustment='unadjusted index' if index else 'Sina hfq: each raw OHLC multiplied by cumulative factor effective at price date',factor_events=len(fac))
 except Exception as e:out.update(status='error',error=f'{type(e).__name__}: {e}')
 with lock:
  results.append(out)
  (ROOT/'price_manifest.json').write_text(json.dumps({'source':'Sina public full-history compressed KLC_KL and historical adjustment factors','target_start':'2019-01-01','target_end':'2026-10-30','concurrency':4,'completed':len(results),'stop_on_refusal':stop.is_set(),'results':results},ensure_ascii=False,indent=2))
  if len(results)%20==0 or out['status']!='ok' or index:print(json.dumps({'completed':len(results),'code':code,'status':out['status'],'rows':out.get('rows'),'last':out.get('last_date'),'error':out.get('error')},ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 stocks=list(csv.DictReader(open('historical-capture/shareholder_frequency/qualified_453.csv',encoding='utf-8-sig')))
 items=[('index_000300','沪深300','sh000300',True),('index_000001','上证指数','sh000001',True),('index_000905','中证500','sh000905',True),('index_000852','中证1000','sh000852',True)]+[(r['code'],r['name'],symbol(r['code']),False) for r in stocks]
 with concurrent.futures.ThreadPoolExecutor(4) as pool:
  for r in pool.map(fetch,items):pass
 print('DONE',len(results),sum(r['status']=='ok' for r in results),flush=True)
