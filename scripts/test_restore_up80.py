"""Safety checks for the offline restorer; only temporary directories are used."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile, unittest, zipfile

SCRIPT = Path(__file__).with_name('restore_up80.py')

class RestoreSafety(unittest.TestCase):
    def fixture(self, root, name='data/sample.txt'):
        archives = root / 'archives'; archives.mkdir()
        metadata = root / 'metadata'; metadata.mkdir()
        data = b'frozen\r\nbytes\n'; archive = archives / 'part.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            z.writestr(name, data)
        row = {'file': name, 'part': archive.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        (metadata / 'FILE_MANIFEST.jsonl').write_text(json.dumps(row) + '\n')
        part = {'file': archive.name, 'bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'entries': 1}
        (metadata / 'PARTS.json').write_text(json.dumps({'data_parts': [part]}))
        return archives, metadata, root / 'destination', data

    def run_restore(self, fixture, *flags):
        archives, metadata, dest, _ = fixture
        return subprocess.run([sys.executable, str(SCRIPT), '--archives', str(archives), '--metadata', str(metadata), '--destination', str(dest), *flags], capture_output=True, text=True)

    def test_restore_preserves_bytes_and_exact_existing_files(self):
        with tempfile.TemporaryDirectory() as d:
            f = self.fixture(Path(d))
            self.assertEqual(self.run_restore(f, '--check-only').returncode, 0)
            self.assertFalse(f[2].exists())
            self.assertEqual(self.run_restore(f).returncode, 0)
            self.assertEqual((f[2] / 'data/sample.txt').read_bytes(), f[3])
            self.assertEqual(self.run_restore(f, '--verify-restored').returncode, 0)
            self.assertEqual(json.loads(self.run_restore(f).stdout)['existing_exact_files_kept'], 1)

    def test_conflicting_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            f = self.fixture(Path(d)); target = f[2] / 'data/sample.txt'
            target.parent.mkdir(parents=True); target.write_bytes(b'user content')
            self.assertNotEqual(self.run_restore(f).returncode, 0)
            self.assertEqual(target.read_bytes(), b'user content')

    def test_traversal_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            f = self.fixture(Path(d), '../escape.txt')
            self.assertNotEqual(self.run_restore(f).returncode, 0)
            self.assertFalse((Path(d) / 'escape.txt').exists())
            self.assertFalse(f[2].exists())

    def test_corrupt_archive_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            f = self.fixture(Path(d)); archive = f[0] / 'part.zip'
            with archive.open('ab') as stream: stream.write(b'changed')
            self.assertNotEqual(self.run_restore(f).returncode, 0)
            self.assertFalse(f[2].exists())

if __name__ == '__main__':
    unittest.main()
