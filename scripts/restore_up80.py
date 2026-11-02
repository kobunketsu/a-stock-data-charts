#!/usr/bin/env python3
"""Restore frozen UP80 inputs offline, checking archives and every file SHA256."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, stat, tempfile, zipfile

REPO = Path(__file__).resolve().parents[1]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def relative(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError(f'Unsafe archive path: {name}')
    return p

def target(root, name):
    p = root / str(relative(name))
    if p.is_symlink() or not p.resolve().is_relative_to(root):
        raise ValueError(f'Path escapes destination or is a symlink: {name}')
    return p

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, default=REPO / 'datasets/up80/inputs')
    parser.add_argument('--metadata', type=Path, default=REPO / 'releases/up80')
    parser.add_argument('--destination', type=Path, default=REPO / 'releases/up80')
    parser.add_argument('--check-only', action='store_true', help='Check archive hashes and inventory without restoring')
    parser.add_argument('--verify-restored', action='store_true', help='Check every existing input file; do not write')
    args = parser.parse_args()
    root = args.destination.resolve()
    rows = [json.loads(x) for x in (args.metadata / 'FILE_MANIFEST.jsonl').read_text().splitlines()]
    entries = {r['file']: r for r in rows}
    if len(entries) != len(rows):
        raise ValueError('Duplicate manifest paths')
    parts = json.loads((args.metadata / 'PARTS.json').read_text())['data_parts']
    names = [r['file'] for r in parts]
    if len(set(names)) != len(names) or set(r['part'] for r in rows) != set(names):
        raise ValueError('Part manifest mismatch')
    # Validate all archives, paths and existing files before writing anything.
    for part in parts:
        archive = args.archives / str(relative(part['file']))
        if archive.stat().st_size != part['bytes'] or sha(archive) != part['sha256']:
            raise ValueError(f'Archive SHA/size mismatch: {part["file"]}')
        with zipfile.ZipFile(archive) as z:
            expected = {r['file'] for r in rows if r['part'] == part['file']}
            if len(z.infolist()) != part['entries'] or len(z.infolist()) != len(expected) or set(z.namelist()) != expected:
                raise ValueError(f'Archive inventory mismatch: {part["file"]}')
            for info in z.infolist():
                dest = target(root, info.filename)
                if info.is_dir() or stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK or info.flag_bits & 1:
                    raise ValueError(f'Unsupported entry: {info.filename}')
                record = entries[info.filename]
                if info.file_size != record['bytes']:
                    raise ValueError(f'Entry size mismatch: {info.filename}')
                if dest.exists() and (not dest.is_file() or dest.stat().st_size != record['bytes'] or sha(dest) != record['sha256']):
                    raise ValueError(f'Existing file differs; refusing overwrite: {info.filename}')
                if args.verify_restored and not dest.is_file():
                    raise ValueError(f'Missing restored input: {info.filename}')
    if args.check_only or args.verify_restored:
        print(json.dumps({'status': 'PASS', 'archives': len(parts), 'files': len(rows), 'restored_files_verified': args.verify_restored, 'writes': 0}))
        return
    restored = skipped = 0
    for part in parts:
        with zipfile.ZipFile(args.archives / part['file']) as z:
            for info in z.infolist():
                dest = target(root, info.filename)
                if dest.exists():
                    skipped += 1
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                fd, temporary = tempfile.mkstemp(prefix='.up80-', dir=dest.parent)
                tmp = Path(temporary)
                try:
                    h = hashlib.sha256()
                    with os.fdopen(fd, 'wb') as output, z.open(info) as source:
                        for block in iter(lambda: source.read(1024 * 1024), b''):
                            output.write(block)
                            h.update(block)
                    if h.hexdigest() != entries[info.filename]['sha256']:
                        raise ValueError(f'File SHA mismatch: {info.filename}')
                    # Exclusive installation: never replace a file created concurrently.
                    os.link(tmp, dest)
                    restored += 1
                finally:
                    tmp.unlink(missing_ok=True)
    print(json.dumps({'status': 'PASS', 'files_restored': restored, 'existing_exact_files_kept': skipped, 'network_used': False}))

if __name__ == '__main__':
    main()
