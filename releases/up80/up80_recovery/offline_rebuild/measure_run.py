from pathlib import Path
import subprocess,time,json,sys,platform,importlib.metadata,os
root=Path(__file__).resolve().parents[2];start=time.time();work=root/'up80_offline_test';peak=0;samples=[]
cmd=[sys.executable,str(root/'up80_recovery/offline_rebuild/run_offline.py'),'--package-root',str(root),'--work-root',str(work),'--execute']
with (root/'up80_offline_run.log').open('w') as log:
 proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=root)
 while proc.poll() is None:
  size=int(subprocess.check_output(['du','-s','-B1',str(work)],stderr=subprocess.DEVNULL).split()[0]) if work.exists() else 0
  peak=max(peak,size);samples.append({'elapsed_seconds':round(time.time()-start,2),'allocated_bytes':size});time.sleep(10)
end=time.time();size=int(subprocess.check_output(['du','-s','-B1',str(work)]).split()[0]) if work.exists() else 0;peak=max(peak,size)
out={'command':cmd,'exit_code':proc.returncode,'elapsed_seconds':end-start,'started_unix':start,'ended_unix':end,'peak_allocated_work_bytes_sampled':peak,'disk_sampling_interval_seconds':10,'final_allocated_work_bytes':size,'python':platform.python_version(),'dependencies':{n:importlib.metadata.version(n) for n in ['numpy','pandas']},'samples':samples,'measurement_note':'Observed peak work-directory allocation sampled every10s, not a guaranteed instantaneous global filesystem peak; /usr/bin/time unavailable'}
(root/'up80_offline_measurements.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));sys.exit(proc.returncode)
