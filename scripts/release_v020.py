#!/usr/bin/env python3
"""Prepare/publish the owner-authorized v0.2.0 bundle; no automatic version bumps."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'skills/design-baton/scripts/baton.py'
VERSION = '0.2.0'
TAG = 'v' + VERSION


def run(*args, capture=False):
    result = subprocess.run(list(args), cwd=ROOT, check=True,
                            text=True, capture_output=capture)
    return result.stdout.strip() if capture else None


def prepare(commit, date, output):
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit) or commit == '0' * 40:
        raise ValueError('a complete nonzero lowercase commit is required')
    versions = json.loads((ROOT / 'skills/design-baton/versions.json').read_text())
    if versions['bundle_version'] != VERSION:
        raise ValueError('this publisher only supports bundle 0.2.0')
    run(sys.executable, str(CLI), 'validate-bundle')
    run(sys.executable, str(CLI), 'package-skill', '--date', date,
        '--output-dir', str(output))
    notes = (ROOT / 'releases/v0.2.0.md').read_text().replace('{{COMMIT}}', commit)
    package = output / ('design-baton-' + TAG + '.zip')
    checksum = hashlib.sha256(package.read_bytes()).hexdigest()
    notes = notes.replace('{{SHA256}}', checksum)
    if '{{' in notes:
        raise ValueError('unresolved release-note placeholder')
    notes_path = output / 'release-notes.md'
    notes_path.write_text(notes, encoding='utf-8')
    return package, notes_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist/v0.2.0')
    parser.add_argument('--prepare-only', action='store_true',
                        help='offline candidate artifacts only; no tag or release creation')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    package, notes = prepare(args.commit, args.date, output)
    if args.prepare_only:
        print('Prepared candidate artifacts only; no publication or pin verification claimed.')
        return
    if run('git', 'rev-parse', 'HEAD', capture=True) != args.commit:
        raise ValueError('checkout differs from requested release commit')
    if run('git', 'status', '--porcelain', '--untracked-files=no', capture=True):
        raise ValueError('tracked files differ from the release commit')
    remote_head = run('gh', 'api', 'repos/jimzord12/design-baton/branches/main',
                      '--jq', '.commit.sha', capture=True)
    if remote_head != args.commit:
        raise ValueError('main advanced; recheck the intended release before publishing')
    existing = subprocess.run(['gh', 'release', 'view', TAG, '--repo',
                               'jimzord12/design-baton', '--json', 'tagName'],
                              cwd=ROOT, capture_output=True, text=True)
    if existing.returncode == 0:
        raise ValueError('release already exists; never overwrite published assets')
    # Tag creation is independent of issue-filing authority and authorized here.
    tag = subprocess.run(['git', 'rev-parse', '--verify', TAG + '^{commit}'],
                         cwd=ROOT, capture_output=True, text=True)
    if tag.returncode == 0:
        if tag.stdout.strip() != args.commit:
            raise ValueError('existing tag points elsewhere; never move it')
    else:
        run('git', 'config', 'user.name', 'github-actions[bot]')
        run('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        run('git', 'tag', '-a', TAG, args.commit, '-m', 'Design Baton v0.2.0: slice-close improvement review')
    run('git', 'push', 'origin', 'refs/tags/' + TAG)
    run('gh', 'release', 'create', TAG, str(package), str(package) + '.sha256',
        '--repo', 'jimzord12/design-baton', '--verify-tag', '--target', args.commit,
        '--title', 'Design Baton v0.2.0', '--notes-file', str(notes))
    # Verify the published asset bytes, rather than comparing another compression environment.
    downloaded = output / 'downloaded'
    run('gh', 'release', 'download', TAG, '--repo', 'jimzord12/design-baton',
        '--pattern', package.name, '--pattern', package.name + '.sha256',
        '--dir', str(downloaded))
    remote = downloaded / package.name
    if remote.read_bytes() != package.read_bytes():
        raise ValueError('downloaded release asset differs from the tested package')
    if (downloaded / (package.name + '.sha256')).read_bytes() != Path(str(package) + '.sha256').read_bytes():
        raise ValueError('downloaded checksum differs')
    print('Published and verified v0.2.0 asset bytes at ' + args.commit)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print('error: ' + str(exc), file=sys.stderr)
        sys.exit(1)
