#!/usr/bin/env python3
"""Rebuild the frozen 972-stock matrix release, with input and output SHA checks."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--check-inputs',action='store_true',help='Only validate complete release inputs and source hashes')
 p.add_argument('--web-dir',type=Path,help='Optional separate website directory containing index.html')
 a=p.parse_args()
 if sys.version_info<(3,11):raise SystemExit('需要 Python 3.11 或更高版本，建议 3.12。')
 refpath=ROOT/'release_reference.json'
 if not refpath.is_file():raise SystemExit('缺少 release_reference.json；请完整合并代码与输入分包。')
 ref=json.loads(refpath.read_text(encoding='utf-8'))
 errors=[]
 for rel,expected in {**ref['inputs'],**ref['scripts'],**ref.get('supporting_metadata',{})}.items():
  path=ROOT/rel
  if not path.is_file():errors.append(f'MISSING: {rel}')
  elif sha(path)!=expected:errors.append(f'SHA MISMATCH: {rel}')
 if errors:
  print('\n'.join(errors[:30]));raise SystemExit(f'输入或脚本检查失败，共 {len(errors)} 项。未运行计算。')
 with (ROOT/'qualified_972.csv').open(encoding='utf-8-sig') as f:codes=[r['code'] for r in csv.DictReader(f)]
 if len(codes)!=972 or len(set(codes))!=972:raise SystemExit('股票池必须是最终 972 只不重复股票。')
 if any(f'prices/{c}.csv' not in ref['inputs'] for c in codes):raise SystemExit('发行清单未完整包含 972 股行情。')
 if a.web_dir and not (a.web_dir.resolve()/'index.html').is_file():raise SystemExit('--web-dir 必须指向包含 index.html 的网页目录。')
 print(f'PASS: {len(ref["inputs"])} 个冻结输入、{len(ref["scripts"])} 个计算脚本及配套元数据 SHA 完全一致。',flush=True)
 if a.check_inputs:return
 for rel in ['build_event_panel.py','holder_matrix_4bins/build_matrix.py','holder_matrix_4bins/audit_matrix.py']:
  print('Running',rel,flush=True);subprocess.run([sys.executable,str(ROOT/rel)],cwd=ROOT,check=True)
 checks={}
 for rel,expected in ref['outputs'].items():
  actual=sha(ROOT/rel);checks[rel]={'expected_sha256':expected,'rebuilt_sha256':actual,'exact_match':actual==expected}
 report={'status':'PASS' if all(x['exact_match'] for x in checks.values()) else 'MISMATCH','scope':'merged raw holder CSVs + frozen 972-stock pool + adjusted stock prices + date calendar -> cleaning -> event paths -> matrix','checks':checks}
 (ROOT/'rebuild_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 if report['status']!='PASS':raise SystemExit('重算结果与发布版不完全一致；查看 rebuild_result.json。未更新网页。')
 if a.web_dir:
  web=a.web_dir.resolve();src=ROOT/'holder_matrix_4bins/curves_ui.json';shutil.copy2(src,web/'curves_ui.json')
  (web/'data.js').write_text('window.RESEARCH_DATA='+src.read_text(encoding='utf-8')+';\n',encoding='utf-8')
 print('PASS: 发布版统计结果 SHA 完全一致；独立审计通过。未进行网络抓取或网站发布。')
if __name__=='__main__':main()
