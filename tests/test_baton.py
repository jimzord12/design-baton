"""Behavioral acceptance tests; all projects and pins here are synthetic fixtures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch
import zipfile

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / 'skills/design-baton/scripts/baton.py'
PIN = '1' * 40


class BatonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'sample'

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)],
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn('error:', result.stderr)
        return result

    def init(self, slug='sample', title='Sample application'):
        self.root = self.base / slug
        self.run_cli('init', self.root, '--slug', slug, '--title', title,
                     '--date', '2026-10-03', '--commit', PIN, '--fixture')
        return self.root

    def metadata(self):
        return json.loads((self.root / 'baton.json').read_text())

    def save(self, data):
        (self.root / 'baton.json').write_text(json.dumps(data), encoding='utf-8')

    def validate(self, ok=True):
        return self.run_cli('validate-workspace', self.root, '--allow-fixture', ok=ok)

    def map(self):
        (self.root / 'subjects').mkdir()
        (self.root / 'subjects/design.md').write_text('# Design\n', encoding='utf-8')
        (self.root / 'maps').mkdir()
        (self.root / 'context/decisions.md').write_text(
            '# Decisions\n\n## D-001\nStatement: Use a simple form.\nAuthority: owner\n'
            'Status: accepted\nRationale: Low training cost.\nSource: synthetic owner scenario.\n', encoding='utf-8')
        data = self.metadata()
        data['active_slice'] = {'id': 'slice-1', 'subject': 'subjects/design.md',
                                'target': 'Choose intake', 'map': 'maps/intake.json',
                                'discovery': 'accepted'}
        self.save(data)
        return {'map_format': '0.1.0', 'slice_id': 'slice-1', 'target': 'Choose intake',
                'complete': True, 'branches': [{'id': 'branch-1', 'title': 'Intake', 'leaves': [
                    {'id': 'leaf-1', 'question': 'Which intake?', 'required': True,
                     'status': 'resolved', 'decisions': ['D-001'], 'future_branch': False},
                    {'id': 'leaf-2', 'question': 'Add optional reminders?', 'required': False,
                     'status': 'deferred', 'rationale': 'Later slice', 'future_branch': True}]}]}

    def save_map(self, data):
        (self.root / 'maps/intake.json').write_text(json.dumps(data), encoding='utf-8')

    def snapshot(self, *extra, ok=True):
        return self.run_cli('snapshot', self.root, '--date', '2026-10-03',
                            '--output-dir', self.base / 'exports', '--allow-fixture', *extra, ok=ok)

    def test_init_offline_core_and_no_overwrite(self):
        self.init()
        self.validate()
        self.assertEqual(self.metadata()['snapshot']['number'], 1)
        self.assertIsNone(self.metadata()['active_slice'])
        self.assertFalse((self.root / 'maps').exists())
        self.assertIn(PIN, (self.root / 'README.md').read_text())
        before = (self.root / 'README.md').read_bytes()
        self.run_cli('init', self.root, '--slug', 'sample', '--title', 'Other',
                     '--date', '2026-10-03', '--commit', PIN, ok=False)
        self.assertEqual(before, (self.root / 'README.md').read_bytes())

    def test_fixture_requires_explicit_opt_in(self):
        self.init()
        self.run_cli('validate-workspace', self.root, ok=False)

    def test_init_rejects_bad_slug_date_or_pin(self):
        for flag, value in [('--slug', '../bad'), ('--date', '2026-02-30'), ('--commit', 'main')]:
            args = {'--slug': 'sample', '--title': 'Sample', '--date': '2026-10-03', '--commit': PIN}
            args[flag] = value
            self.run_cli('init', self.root, *[item for pair in args.items() for item in pair], ok=False)
            self.assertFalse(self.root.exists())

    def test_missing_core_and_broken_links(self):
        self.init()
        (self.root / 'context/glossary.md').rename(self.root / 'context/old-glossary.md')
        self.validate(ok=False)
        (self.root / 'context/old-glossary.md').rename(self.root / 'context/glossary.md')
        with (self.root / 'PROJECT_STATE.md').open('a') as f:
            f.write('\n[missing](subjects/missing.md)\n')
        self.validate(ok=False)

    def test_invalid_metadata_and_readme_pin(self):
        self.init()
        original = self.metadata()
        for path, value in [('workspace_format', '8.0.0'), ('snapshot.number', True),
                            ('snapshot.predecessor', 0), ('procedure.release_tag', 'v9.0.0'),
                            ('procedure.commit', 'main'), ('procedure.entry_path', '../SKILL.md')]:
            data = copy.deepcopy(original)
            bits = path.split('.')
            dest = data
            for bit in bits[:-1]:
                dest = dest[bit]
            dest[bits[-1]] = value
            self.save(data)
            self.validate(ok=False)
        self.save(original)
        readme = self.root / 'README.md'
        readme.write_text(readme.read_text().replace(PIN, '2' * 40))
        self.validate(ok=False)

    def test_maps_accept_small_complete_with_optional_deferral(self):
        self.init()
        self.save_map(self.map())
        self.validate()

    def test_maps_reject_authority_shape_references_and_completion_errors(self):
        self.init()
        original = self.map()
        bad = []
        data = copy.deepcopy(original)
        data['branches'] = [dict(copy.deepcopy(data['branches'][0]), id=f'b-{i}') for i in range(16)]
        bad.append(data)
        for mutation in ('nested', 'duplicate', 'broken', 'open', 'deferred', 'wrong-type'):
            data = copy.deepcopy(original)
            branch = data['branches'][0]
            leaf = branch['leaves'][0]
            if mutation == 'nested': branch['branches'] = []
            if mutation == 'duplicate': branch['leaves'][1]['id'] = leaf['id']
            if mutation == 'broken': leaf['decisions'] = ['D-404']
            if mutation == 'open': leaf['status'] = 'open'
            if mutation == 'deferred': leaf.update(status='deferred', rationale='Later')
            if mutation == 'wrong-type': leaf['required'] = 'yes'
            bad.append(data)
        for data in bad:
            self.save_map(data)
            self.validate(ok=False)
        self.save_map(original)
        data = self.metadata()
        for discovery in ('pending', 'declined', 'not-offered'):
            data['active_slice']['discovery'] = discovery
            self.save(data)
            self.validate(ok=False)

    def test_declined_discovery_persists_without_map(self):
        self.init()
        data = self.metadata()
        data['active_slice'] = {'id': 'slice-1', 'subject': 'PROJECT_STATE.md',
                                'target': 'Choose a goal', 'discovery': 'declined'}
        self.save(data)
        self.snapshot('--initial')
        self.assertEqual(self.metadata()['active_slice']['discovery'], 'declined')

    def test_snapshot_full_root_source_bytes_reproducible_retry(self):
        self.init()
        (self.root / 'sources').mkdir()
        source = b'\x00\xff original bytes\r\n'
        (self.root / 'sources/reference.zip').write_bytes(source)
        (self.root / '.git').mkdir()
        (self.root / '.git/private').write_text('secret')
        self.snapshot('--initial')
        archive = self.base / 'exports/01-sample.zip'
        first = archive.read_bytes()
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(z.read('sample/sources/reference.zip'), source)
            self.assertTrue(all(n.startswith('sample/') for n in z.namelist()))
            self.assertFalse(any('/.git/' in n for n in z.namelist()))
        self.snapshot('--retry')
        self.assertEqual(first, archive.read_bytes())
        self.run_cli('inspect-archive', archive, '--allow-fixture')
        self.snapshot()
        self.assertEqual(self.metadata()['snapshot']['number'], 2)
        self.assertEqual(self.metadata()['snapshot']['predecessor'], 1)
        self.snapshot('--retry')
        self.assertEqual(self.metadata()['snapshot']['number'], 2)

    def test_output_failure_leaves_recoverable_identity(self):
        self.init()
        self.snapshot('--initial')
        blocker = self.base / 'blocked'
        blocker.write_text('not a directory')
        self.run_cli('snapshot', self.root, '--date', '2026-10-03', '--output-dir', blocker,
                     '--allow-fixture', ok=False)
        self.assertEqual(self.metadata()['snapshot']['number'], 2)
        self.assertEqual(self.metadata()['snapshot']['export_status'], 'prepared')
        self.snapshot()
        self.assertEqual(self.metadata()['snapshot']['number'], 2)
        self.assertEqual(self.metadata()['snapshot']['export_status'], 'exported')

    def test_archive_rejects_hostile_members_before_reading_workspace(self):
        archive = self.base / 'bad.zip'
        cases = [('sample/../escape', False), ('/absolute', False), ('C:/drive', False),
                 ('sample\\..\\escape', False), ('sample/link', True), ('sample/CON', False)]
        for name, symlink in cases:
            with zipfile.ZipFile(archive, 'w') as z:
                info = zipfile.ZipInfo(name)
                if symlink:
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(info, 'target')
            self.run_cli('inspect-archive', archive, ok=False)
        for names in [('sample/README.md', 'sample/README.md'),
                      ('sample/README.md', 'sample/readme.md'), ('sample/a', 'other/b')]:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                with zipfile.ZipFile(archive, 'w') as z:
                    for name in names: z.writestr(name, 'data')
            self.run_cli('inspect-archive', archive, ok=False)

    def test_snapshot_rejects_output_inside_workspace(self):
        self.init()
        self.run_cli('snapshot', self.root, '--date', '2026-10-03',
                     '--output-dir', self.root / 'exports', '--allow-fixture', ok=False)

    def test_bundle_reproducibility_curated_files_and_checksum(self):
        self.run_cli('validate-bundle')
        out = self.base / 'packages'
        self.run_cli('package-skill', '--output-dir', out, '--date', '2026-10-03')
        archive = out / 'design-baton-v0.1.0.zip'
        before = archive.read_bytes()
        self.run_cli('package-skill', '--output-dir', out, '--date', '2026-10-03')
        self.assertEqual(before, archive.read_bytes())
        checksum = (out / (archive.name + '.sha256')).read_text().split()[0]
        self.assertEqual(checksum, hashlib.sha256(before).hexdigest())
        with zipfile.ZipFile(archive) as z:
            self.assertIn('design-baton/SKILL.md', z.namelist())
            self.assertIn('design-baton/LICENSE', z.namelist())
            self.assertFalse(any('/tests/' in n or '__pycache__' in n for n in z.namelist()))

    def test_archive_integrity_and_documented_limits(self):
        self.init()
        self.snapshot('--initial')
        original = self.base / 'exports/01-sample.zip'
        broken = self.base / 'broken.zip'
        broken.write_bytes(original.read_bytes()[:100])
        self.run_cli('inspect-archive', broken, '--allow-fixture', ok=False)
        oversized = self.base / 'oversized.zip'
        with zipfile.ZipFile(oversized, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('sample/big.txt', b'a' * (51 * 1024 * 1024))
        self.run_cli('inspect-archive', oversized, ok=False)
        crowded = self.base / 'crowded.zip'
        with zipfile.ZipFile(crowded, 'w') as z:
            for i in range(2001): z.writestr(f'sample/{i}.txt', b'x')
        self.run_cli('inspect-archive', crowded, ok=False)

    def test_snapshot_different_existing_archive_is_not_overwritten(self):
        self.init()
        self.snapshot('--initial')
        archive = self.base / 'exports/01-sample.zip'
        original = archive.read_bytes()
        (self.root / 'subjects').mkdir()
        (self.root / 'subjects/new.md').write_text('# New design\n')
        self.snapshot('--retry', ok=False)
        self.assertEqual(original, archive.read_bytes())

    def test_bundle_rejects_missing_manifest_path_and_dangling_router_link(self):
        bundle = self.base / 'skill'
        shutil.copytree(REPO / 'skills/design-baton', bundle)
        shutil.copy2(REPO / 'LICENSE', bundle / 'LICENSE')
        cli = bundle / 'scripts/baton.py'
        data = json.loads((bundle / 'versions.json').read_text())
        data['components']['decisions-tree']['path'] = 'references/missing.md'
        (bundle / 'versions.json').write_text(json.dumps(data))
        result = subprocess.run([sys.executable, str(cli), 'validate-bundle'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing', result.stderr)
        data['components']['decisions-tree']['path'] = 'references/playbooks/decisions-tree.md'
        (bundle / 'versions.json').write_text(json.dumps(data))
        with (bundle / 'SKILL.md').open('a') as f:
            f.write('\n[missing](references/missing.md)\n')
        result = subprocess.run([sys.executable, str(cli), 'validate-bundle'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('broken local link', result.stderr)

    def test_exact_pin_tag_mismatch_and_newer_main_are_detected(self):
        # This Git history is a synthetic local repository, never a live release.
        local = self.base / 'procedure'
        local.mkdir()
        def git(*args):
            result = subprocess.run(['git', '-C', str(local), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()
        git('init')
        git('config', 'user.name', 'Fixture author')
        git('config', 'user.email', 'fixture@example.invalid')
        folder = local / 'skills/design-baton'
        folder.mkdir(parents=True)
        versions = json.loads((REPO / 'skills/design-baton/versions.json').read_text())
        (folder / 'versions.json').write_text(json.dumps(versions))
        git('add', '.')
        git('commit', '-m', 'Synthetic initial bundle')
        first = git('rev-parse', 'HEAD')
        git('tag', '-a', 'v0.1.0', '-m', 'Synthetic tag')
        self.run_cli('init', self.root, '--slug', 'sample', '--title', 'Synthetic pin check',
                     '--date', '2026-10-03', '--commit', first)
        self.run_cli('validate-workspace', self.root, '--procedure-root', local)
        git('update-index', '--assume-unchanged', 'skills/design-baton/versions.json')
        (folder / 'versions.json').write_text('{"tampered": true}')
        self.run_cli('validate-workspace', self.root, '--procedure-root', local, ok=False)
        (folder / 'versions.json').write_text(json.dumps(versions))
        git('update-index', '--no-assume-unchanged', 'skills/design-baton/versions.json')
        versions['components']['decisions-tree']['version'] = '0.2.0'
        (folder / 'versions.json').write_text(json.dumps(versions))
        git('add', '.')
        git('commit', '-m', 'Synthetic later main')
        # The locked commit still contains the old component; the newer checkout is refused.
        self.assertEqual(json.loads(git('show', first + ':skills/design-baton/versions.json'))
                         ['components']['decisions-tree']['version'], '0.1.0')
        self.run_cli('validate-workspace', self.root, '--procedure-root', local, ok=False)
        data = self.metadata()
        data['procedure']['commit'] = git('rev-parse', 'HEAD')
        self.save(data)
        readme = self.root / 'README.md'
        readme.write_text(readme.read_text().replace(first, data['procedure']['commit']))
        result = self.run_cli('validate-workspace', self.root, '--procedure-root', local, ok=False)
        self.assertIn('tag/commit mismatch', result.stderr)

    def test_atomic_output_failure_preserves_no_partial_archive(self):
        self.init()
        self.snapshot('--initial')
        spec = importlib.util.spec_from_file_location('baton_test', CLI)
        baton = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baton)
        real_replace = baton.os.replace
        def fail_output(source, dest):
            if str(dest).endswith('.zip'):
                raise OSError('simulated interrupted output')
            return real_replace(source, dest)
        with patch.object(baton.os, 'replace', side_effect=fail_output):
            with self.assertRaises(OSError):
                baton.snapshot(self.root, self.base / 'exports', '2026-10-03', allow_fixture=True)
        self.assertEqual(self.metadata()['snapshot']['number'], 2)
        self.assertEqual(self.metadata()['snapshot']['export_status'], 'prepared')
        self.assertFalse((self.base / 'exports/02-sample.zip').exists())
        self.assertFalse(list((self.base / 'exports').glob('*.tmp')))
        self.snapshot()
        self.run_cli('inspect-archive', self.base / 'exports/02-sample.zip', '--allow-fixture')

    def test_compressible_original_source_roundtrips_through_inspection(self):
        self.init()
        (self.root / 'sources').mkdir()
        (self.root / 'sources/zeros.bin').write_bytes(b'\x00' * (2 * 1024 * 1024))
        self.snapshot('--initial')
        archive = self.base / 'exports/01-sample.zip'
        self.run_cli('inspect-archive', archive, '--allow-fixture')
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(z.read('sample/sources/zeros.bin'), b'\x00' * (2 * 1024 * 1024))

    def test_archive_rejects_differently_cased_directory_prefixes(self):
        self.init()
        self.snapshot('--initial')
        original = self.base / 'exports/01-sample.zip'
        alias = self.base / 'alias.zip'
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(alias, 'w') as dest:
            for info in source.infolist(): dest.writestr(info, source.read(info))
            dest.writestr('sample/Foo/a.txt', 'a')
            dest.writestr('sample/foo/b.txt', 'b')
        self.run_cli('inspect-archive', alias, '--allow-fixture', ok=False)


if __name__ == '__main__':
    unittest.main()
