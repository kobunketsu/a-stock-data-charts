#!/usr/bin/env python3
"""Compare an independent UP80 rebuild with frozen published assets; never modify them."""
from pathlib import Path
import argparse, csv, gzip, hashlib, json, math

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package-root', type=Path, required=True)
    p.add_argument('--work-root', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    expected = a.package_root / 'up80_recovery/research/lookbacks'
    actual = a.work_root / 'research/lookbacks'
    report = {'absolute_tolerance': 1e-12, 'relative_tolerance': 0, 'maximum_absolute_float_difference': 0.0, 'float_differences': 0, 'exact_byte_files': 0, 'different_byte_files': [], 'failures': [], 'failure_count': 0, 'matrix_json_files': 0, 'csv_files': 0, 'query_gzip_files': 0, 'metadata_ignored': False}

    def failure(path):
        report['failure_count'] += 1
        if len(report['failures']) < 100: report['failures'].append(path)

    def compare(x, y, path):
        if type(x) is not type(y): failure(path + ': type'); return
        if isinstance(x, dict):
            if set(x) != set(y): failure(path + ': keys')
            for k in x.keys() & y.keys(): compare(x[k], y[k], path + '.' + k)
        elif isinstance(x, list):
            if len(x) != len(y): failure(path + ': length')
            for i, (u, v) in enumerate(zip(x, y)): compare(u, v, path + f'[{i}]')
        elif isinstance(x, float) and x != y:
            delta = abs(x - y)
            if not math.isfinite(delta): failure(path + ': nonfinite'); return
            report['float_differences'] += 1
            report['maximum_absolute_float_difference'] = max(report['maximum_absolute_float_difference'], delta)
            if delta > 1e-12: failure(path + ': float exceeds tolerance')
        elif x != y: failure(path + ': exact value')

    def bytes_equal(x, y, label):
        if sha(x) == sha(y): report['exact_byte_files'] += 1; return True
        report['different_byte_files'].append(label)
        return False

    for n in [10, 20, 30, 60, 120]:
        er = expected / f'lookback_{n}'; ar = actual / f'lookback_{n}'
        for rel in ['holder_matrix_9rows/curves_ui.json', 'holder_matrix_9rows_2020plus/curves_ui.json', 'stability/stability_ui.json']:
            x, y = er / rel, ar / rel; label = f'N{n}/{rel}'
            report['matrix_json_files'] += 1
            bytes_equal(x, y, label)
            compare(json.loads(x.read_text()), json.loads(y.read_text()), label)
        for x in sorted(er.rglob('*.csv')):
            rel = x.relative_to(er); y = ar / rel; label = f'N{n}/{rel}'
            report['csv_files'] += 1
            if bytes_equal(x, y, label): continue
            with x.open(newline='', encoding='utf-8-sig') as xf, y.open(newline='', encoding='utf-8-sig') as yf:
                xr, yr = list(csv.reader(xf)), list(csv.reader(yf))
            if len(xr) != len(yr): failure(label + ': row count')
            if xr[0] != yr[0]: failure(label + ': header')
            for i, (xs, ys) in enumerate(zip(xr[1:], yr[1:]), 1):
                if len(xs) != len(ys): failure(label + ': columns')
                for k, (u, v) in enumerate(zip(xs, ys)):
                    if u == v: continue
                    path = label + f': row{i}, column{k}'
                    # Identifiers, dates and integer counts must match exactly.
                    if xr[0][k] in ['code', 'event_id'] or not any(c in u + v for c in '.eE'):
                        failure(path + ': exact field'); continue
                    try: compare(float(u), float(v), path)
                    except ValueError: failure(path + ': nonnumeric')
    web = a.package_root / 'sites/shareholder-matrix/dist'
    for published, rebuilt in [('single_stock', 'single_stock'), ('single_stock_patch', 'lookback_patch')]:
        er = web / published; ar = a.work_root / 'query_output' / rebuilt
        ei, ai = er / 'index.json', ar / 'index.json'
        bytes_equal(ei, ai, published + '/index.json')
        ej, aj = json.loads(ei.read_text()), json.loads(ai.read_text())
        compare(ej, aj, published + '/index.json')
        if len(ej['stocks']) != 5554: failure(published + ': expected5554')
        for item in ej['stocks']:
            x, y = er / item['file'], ar / item['file']; label = published + '/' + item['file']
            report['query_gzip_files'] += 1
            if not bytes_equal(x, y, label): compare(json.loads(gzip.decompress(x.read_bytes())), json.loads(gzip.decompress(y.read_bytes())), label)
    report['status'] = 'FAIL' if report['failures'] else ('PASS_EXACT' if not report['different_byte_files'] else 'PASS_NUMERIC_WITH_BYTE_DIFFERENCES')
    report['array_scope'] = 'Native paths regenerated. Cloud reference NPZ arrays are not included in the frozen distribution, so no native-versus-cloud NPZ array equality is asserted here.'
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['different_byte_files', 'failures']}, ensure_ascii=False))
    raise SystemExit(1 if report['failures'] else 0)

if __name__ == '__main__':
    main()
