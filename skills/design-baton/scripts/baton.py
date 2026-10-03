#!/usr/bin/env python3
"""Design Baton mechanical toolkit. Python 3.10+, standard library only."""
import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile
import zlib

SKILL = Path(__file__).resolve().parents[1]
FORMAT = '0.1.0'
REPOSITORY = 'https://github.com/jimzord12/design-baton'
ENTRY = 'skills/design-baton/SKILL.md'
CORE = ('README.md', 'baton.json', 'PROJECT_STATE.md', 'context/briefing.md',
        'context/decisions.md', 'context/glossary.md')
COMPONENTS = {'session-lifecycle', 'decisions-tree', 'snapshots', 'upgrades',
              'workspace-format', 'toolkit', 'skill-improvement'}
EXCLUDED = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules',
            'dist', 'build', 'exports', 'output', '.superpowers'}
MAX_MEMBERS = 2000
MAX_FILE = 50 * 1024 * 1024
MAX_TOTAL = 200 * 1024 * 1024
SEMVER = r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'
ID = r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}'


class BatonError(ValueError):
    """A useful user-facing contract failure."""


def require(condition, message):
    if not condition:
        raise BatonError(message)


def text_field(value, label):
    require(isinstance(value, str) and bool(value.strip()) and '\x00' not in value,
            f'{label} must be nonempty text')
    return value


def object_field(value, label):
    require(isinstance(value, dict), f'{label} must be an object')
    return value


def date_field(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value),
            'prepared_on/date must be YYYY-MM-DD')
    try:
        date = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise BatonError(f'invalid date: {value}') from exc
    require(1980 <= date.year <= 2107, 'ZIP date year must be between 1980 and 2107')
    return date


def safe_path(value):
    text_field(value, 'path')
    require('\\' not in value and not value.startswith('/'), f'unsafe path: {value}')
    parts = value.split('/')
    for part in parts:
        require(part not in ('', '.', '..') and not part.endswith((' ', '.')),
                f'unsafe path segment: {value}')
        require(not any(ord(c) < 32 or c in ':<>"|?*' for c in part), f'unsafe filename: {value}')
        require(not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', part.split('.')[0]),
                f'reserved filename: {value}')
    return PurePosixPath(value)


def parse_json(raw, label):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, f'{label}: duplicate JSON key {key}')
            out[key] = value
        return out
    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as exc:
        raise BatonError(f'{label}: invalid JSON: {exc}') from exc


def check_case_path(value, prefixes):
    """Detect spelling collisions at directory prefixes as well as full filenames."""
    parts = safe_path(value).parts
    for index in range(1, len(parts) + 1):
        prefix = '/'.join(parts[:index])
        key = prefix.casefold()
        require(key not in prefixes or prefixes[key] == prefix, f'case collision: {prefix}')
        prefixes[key] = prefix


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.baton-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def collect(root):
    """Collect a bounded complete workspace, omitting documented generated content."""
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), f'workspace directory missing or symlink: {root}')
    files = {}
    names = set()
    prefixes = {}
    total = 0
    for directory, dirs, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        relative = base.relative_to(root).parts
        in_sources = bool(relative and relative[0] == 'sources')
        kept = []
        for name in dirs:
            path = base / name
            if name in EXCLUDED and not in_sources:
                continue
            require(not path.is_symlink(), f'symlink directory rejected: {path}')
            check_case_path(path.relative_to(root).as_posix(), prefixes)
            kept.append(name)
        dirs[:] = sorted(kept)
        for name in sorted(filenames):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if not in_sources and (name.endswith(('.zip', '.pyc', '.tmp')) or name.startswith('.baton-')):
                continue
            check_case_path(rel, prefixes)
            require(not path.is_symlink() and path.is_file(), f'nonregular file rejected: {rel}')
            require(rel.casefold() not in names, f'case collision: {rel}')
            names.add(rel.casefold())
            size = path.stat().st_size
            total += size
            require(size <= MAX_FILE and total <= MAX_TOTAL, 'workspace size limit exceeded')
            require(len(files) < MAX_MEMBERS, 'workspace member limit exceeded')
            files[rel] = path.read_bytes()
    return files


def markdown_links(files, skip_prefixes=()):
    """Check relative inline/image and reference links, including normalized parent links."""
    for name, raw in files.items():
        if not name.endswith('.md') or any(name.startswith(prefix) for prefix in skip_prefixes):
            continue
        try:
            content = raw.decode('utf-8')
        except UnicodeError as exc:
            raise BatonError(f'{name} must be UTF-8') from exc
        content = re.sub(r'```.*?```', '', content, flags=re.S)
        targets = re.findall(r'\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)', content)
        targets += re.findall(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)', content, flags=re.M)
        for target in targets:
            target = target.strip('<>')
            url = urlsplit(target)
            if url.scheme or url.netloc or target.startswith('#'):
                continue
            path = unquote(url.path)
            if not path:
                continue
            require('\\' not in path and not path.startswith('/'), f'{name}: unsafe link {target}')
            parts = list(PurePosixPath(name).parent.parts)
            for part in path.split('/'):
                if part == '..':
                    require(bool(parts), f'{name}: link escapes root: {target}')
                    parts.pop()
                elif part not in ('', '.'):
                    parts.append(part)
            resolved = '/'.join(parts)
            safe_path(resolved)
            require(resolved in files or any(n.startswith(resolved + '/') for n in files),
                    f'{name}: broken local link: {target}')


def decision_ids(files):
    content = files['context/decisions.md'].decode('utf-8')
    ids = re.findall(r'^## (D-[a-zA-Z0-9_-]+)\s*$', content, re.M)
    require(len(ids) == len(set(ids)), 'duplicate decision IDs')
    return set(ids)


def validate_map(data, decisions, active=None):
    object_field(data, 'map')
    require(data.get('map_format') == FORMAT, 'unsupported map_format')
    require(re.fullmatch(ID, text_field(data.get('slice_id'), 'slice_id')), 'invalid slice_id')
    text_field(data.get('target'), 'map target')
    require(type(data.get('complete')) is bool, 'map complete must be boolean')
    if active:
        require(active['discovery'] == 'accepted', 'map requires accepted discovery')
        require(data['slice_id'] == active['id'] and data['target'] == active['target'],
                'map slice/target contradicts active_slice')
    branches = data.get('branches')
    require(isinstance(branches, list) and 1 <= len(branches) <= 15, 'map needs 1–15 branches')
    ids = set()
    def identifier(item):
        value = text_field(item.get('id'), 'map ID')
        require(re.fullmatch(ID, value) and value not in ids, f'invalid or duplicate map ID: {value}')
        ids.add(value)
    for branch in branches:
        object_field(branch, 'branch')
        require(set(branch) <= {'id', 'title', 'leaves'}, 'branches contain leaves only; no nested branches')
        identifier(branch)
        text_field(branch.get('title'), 'branch title')
        leaves = branch.get('leaves')
        require(isinstance(leaves, list) and bool(leaves), 'branch needs concrete leaves')
        for leaf in leaves:
            object_field(leaf, 'leaf')
            require(set(leaf) <= {'id', 'question', 'required', 'status', 'decisions', 'rationale', 'future_branch'},
                    'unknown leaf fields or nested hierarchy')
            identifier(leaf)
            text_field(leaf.get('question'), 'leaf question')
            require(type(leaf.get('required')) is bool and type(leaf.get('future_branch')) is bool,
                    'required/future_branch must be boolean')
            status = leaf.get('status')
            require(status in ('open', 'resolved', 'deferred'), 'invalid leaf status')
            refs = leaf.get('decisions', [])
            require(isinstance(refs, list) and all(isinstance(v, str) for v in refs), 'decisions must be IDs')
            require(len(refs) == len(set(refs)) and all(v in decisions for v in refs), 'broken/duplicate decision references')
            if status == 'resolved':
                require(bool(refs), 'resolved leaf needs decision references')
            else:
                require(not refs, 'unresolved leaf cannot claim resolving decisions')
            if status == 'deferred':
                text_field(leaf.get('rationale'), 'deferral rationale')
            require(not (data['complete'] and leaf['required'] and status != 'resolved'),
                    'complete map contains unresolved required leaves')


def validate_files(files, allow_fixture=False):
    for name in CORE:
        require(name in files, f'missing core file: {name}')
    data = object_field(parse_json(files['baton.json'], 'baton.json'), 'baton.json')
    require(data.get('workspace_format') == FORMAT, 'unsupported workspace_format')
    project = object_field(data.get('project'), 'project')
    slug = text_field(project.get('slug'), 'project.slug')
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) and len(slug) <= 64, 'unsafe project slug')
    safe_path(slug)
    title = text_field(project.get('title'), 'project.title')
    require('\n' not in title and '\r' not in title, 'title must be one line')
    procedure = object_field(data.get('procedure'), 'procedure')
    require(procedure.get('repository') == REPOSITORY, 'unsupported procedure repository')
    version = procedure.get('bundle_version')
    require(isinstance(version, str) and re.fullmatch(SEMVER, version), 'invalid bundle_version')
    require(version == manifest()['bundle_version'], 'workspace bundle differs from this toolkit; use the pinned toolkit')
    require(procedure.get('release_tag') == f'v{version}', 'release tag/bundle mismatch')
    commit = procedure.get('commit')
    require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit) and commit != '0' * 40,
            'complete nonzero lowercase commit pin required')
    require(procedure.get('entry_path') == ENTRY, 'unsupported procedure entry_path')
    fixture = procedure.get('fixture', False)
    require(type(fixture) is bool, 'fixture must be boolean')
    require(not fixture or allow_fixture, 'fixture pin rejected; pass --allow-fixture for synthetic examples')
    readme = files['README.md'].decode('utf-8')
    require(f'{REPOSITORY}/blob/{commit}/{ENTRY}' in readme and
            f'{REPOSITORY}/releases/tag/v{version}' in readme and f'Design Baton {version}' in readme,
            'README procedure version/URLs contradict pin')
    require(not fixture or 'FIXTURE' in readme, 'fixture must be labeled in README')
    snap = object_field(data.get('snapshot'), 'snapshot')
    number = snap.get('number')
    require(type(number) is int and number >= 1, 'snapshot number must be positive integer')
    predecessor = snap.get('predecessor')
    require((number == 1 and predecessor is None) or
            (number > 1 and type(predecessor) is int and predecessor == number - 1), 'invalid snapshot lineage')
    date_field(snap.get('prepared_on'))
    require(snap.get('export_status') in ('prepared', 'exported'), 'snapshot export_status must be prepared/exported')
    active = data.get('active_slice')
    require('active_slice' in data, 'active_slice required')
    if active is not None:
        object_field(active, 'active_slice')
        require(re.fullmatch(ID, text_field(active.get('id'), 'slice id')), 'invalid slice id')
        text_field(active.get('target'), 'slice target')
        subject = active.get('subject')
        safe_path(subject)
        require(subject in files and subject.endswith('.md'), 'active subject missing or not Markdown')
        require(active.get('discovery') in ('not-offered', 'pending', 'accepted', 'declined'), 'invalid discovery state')
        if active.get('map') is not None:
            safe_path(active['map'])
            require(active['map'] in files and active['map'].startswith('maps/') and active['map'].endswith('.json'),
                    'active map missing or outside maps/')
            validate_map(parse_json(files[active['map']], active['map']), decision_ids(files), active)
    decisions = decision_ids(files)
    for name, raw in files.items():
        if name.startswith('maps/') and name.endswith('.json') and (not active or name != active.get('map')):
            historical = parse_json(raw, name)
            require(historical.get('discovery') == 'accepted', f'{name}: archived map needs discovery authorization')
            validate_map(historical, decisions)
    markdown_links(files)
    return data


def validate_workspace(root, allow_fixture=False):
    return validate_files(collect(root), allow_fixture)


def manifest():
    return object_field(parse_json((SKILL / 'versions.json').read_bytes(), 'versions.json'), 'manifest')


def init_workspace(root, slug, title, date, commit, fixture=False):
    root = Path(root)
    require(not root.exists(), f'refusing overwrite of existing workspace: {root}')
    date_field(date)
    data = parse_json((SKILL / 'assets/workspace/baton.json').read_bytes(), 'template baton.json')
    data['project'] = {'slug': slug, 'title': title}
    data['procedure'].update(bundle_version=manifest()['bundle_version'],
                             release_tag='v' + manifest()['bundle_version'], commit=commit)
    if fixture:
        data['procedure']['fixture'] = True
    data['snapshot']['prepared_on'] = date
    values = {'TITLE': title, 'SLUG': slug, 'VERSION': data['procedure']['bundle_version'],
              'COMMIT': commit, 'REPOSITORY': REPOSITORY,
              'FIXTURE_NOTICE': '**FIXTURE: synthetic pin, not a live release; do not use for procedural resume.**\n' if fixture else ''}
    files = {}
    for name in CORE:
        if name == 'baton.json':
            files[name] = json_bytes(data)
        else:
            content = (SKILL / 'assets/workspace' / name).read_text(encoding='utf-8')
            for key, value in values.items():
                content = content.replace('{{' + key + '}}', value)
            files[name] = content.encode('utf-8')
    validate_files(files, fixture)
    root.parent.mkdir(parents=True, exist_ok=True)
    # Stage a complete directory before renaming; never overlay existing work.
    with tempfile.TemporaryDirectory(prefix='.baton-init-', dir=root.parent) as temp:
        stage = Path(temp) / slug
        stage.mkdir()
        for name, raw in files.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        require(not root.exists(), f'workspace appeared during initialization: {root}')
        stage.rename(root)
    return data


def zip_bytes(files, root, date):
    day = date_field(date)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(files):
            safe_path(name)
            info = zipfile.ZipInfo(f'{root}/{name}', (day.year, day.month, day.day, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
            compressed_size = len(compressor.compress(files[name]) + compressor.flush())
            # Preserve highly compressible originals without creating a ratio-limit violation.
            method = zipfile.ZIP_STORED if len(files[name]) > max(1, compressed_size) * 1000 else zipfile.ZIP_DEFLATED
            info.compress_type = method
            archive.writestr(info, files[name], compress_type=method, compresslevel=9)
    return out.getvalue()


def snapshot(root, output_dir, date, initial=False, retry=False, allow_fixture=False):
    root, output_dir = Path(root).resolve(), Path(output_dir).resolve()
    require(root != output_dir and root not in output_dir.parents, 'output directory must be outside workspace')
    files = collect(root)
    data = validate_files(files, allow_fixture)
    day = date_field(date)
    snap = data['snapshot']
    if initial:
        require(snap['number'] == 1, '--initial requires snapshot 1')
    elif retry:
        pass
    elif snap['export_status'] == 'exported':
        snap.update(number=snap['number'] + 1, predecessor=snap['number'],
                    prepared_on=date, export_status='prepared')
    require(snap['prepared_on'] == day.isoformat(), 'retry/prepared export must use its existing prepared_on date')
    # Persist the prepared identity before output. Failure leaves a recoverable identity.
    prepared = copy.deepcopy(data)
    prepared['snapshot']['export_status'] = 'prepared'
    atomic_write(root / 'baton.json', json_bytes(prepared))
    data['snapshot']['export_status'] = 'exported'
    files['baton.json'] = json_bytes(data)
    validate_files(files, allow_fixture)
    name = f"{snap['number']:02d}-{data['project']['slug']}.zip"
    output = output_dir / name
    payload = zip_bytes(files, data['project']['slug'], date)
    inspect_archive(io.BytesIO(payload), allow_fixture)
    if output.exists():
        require(output.read_bytes() == payload, f'archive exists with different contents: {output}; choose a new output directory')
    else:
        atomic_write(output, payload)
    atomic_write(root / 'baton.json', json_bytes(data))
    return output


def inspect_archive(path, allow_fixture=False):
    """Validate without extracting any member."""
    files = {}
    seen = set()
    roots = set()
    prefixes = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        require(0 < len(infos) <= MAX_MEMBERS, 'archive member limit exceeded or empty archive')
        for info in infos:
            name = info.filename
            require(info.orig_filename == name, 'NUL in archive member')
            check_case_path(name.rstrip('/'), prefixes)
            require(name.casefold().rstrip('/') not in seen, f'duplicate/case-colliding archive member: {name}')
            seen.add(name.casefold().rstrip('/'))
            parts = name.rstrip('/').split('/')
            require(len(parts) >= 2 or info.is_dir(), 'archive must have one stable root directory')
            roots.add(parts[0])
            mode = info.external_attr >> 16
            require(not stat.S_ISLNK(mode), f'archive symlink rejected: {name}')
            require(stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR), f'nonregular archive member: {name}')
            require(not info.flag_bits & 1, 'encrypted archive unsupported')
            total += info.file_size
            require(info.file_size <= MAX_FILE and total <= MAX_TOTAL, 'archive size limit exceeded')
            require(info.file_size <= max(1, info.compress_size) * 1000, 'archive compression ratio limit exceeded')
        require(len(roots) == 1, 'archive has multiple roots')
        # Reject a file which is also an ancestor of another member.
        file_names = {i.filename.casefold() for i in infos if not i.is_dir()}
        for info in infos:
            for parent in PurePosixPath(info.filename).parents:
                require(str(parent).casefold() not in file_names, 'archive file/directory collision')
        for info in infos:
            if not info.is_dir():
                files[info.filename.split('/', 1)[1]] = archive.read(info)
        data = validate_files(files, allow_fixture)
        require(next(iter(roots)) == data['project']['slug'], 'archive root/project slug mismatch')
    return data


def bundle_files():
    allowed = {'SKILL.md', 'agents/openai.yaml', 'versions.json'}
    files = {}
    for directory in ('references', 'assets', 'scripts'):
        for name, raw in collect(SKILL / directory).items():
            files[f'{directory}/{name}'] = raw
    for name in allowed:
        require((SKILL / name).is_file(), f'missing skill file: {name}')
        files[name] = (SKILL / name).read_bytes()
    # MIT notice belongs in the installed asset as well as the source repository.
    license_path = SKILL / 'LICENSE'
    if not license_path.exists():
        license_path = SKILL.parents[1] / 'LICENSE'
    require(license_path.is_file(), 'MIT license missing')
    files['LICENSE'] = license_path.read_bytes()
    return files


def validate_bundle():
    files = bundle_files()
    data = manifest()
    require(type(data.get('manifest_format')) is int and data['manifest_format'] == 1, 'unsupported manifest_format')
    require(isinstance(data.get('bundle_version'), str) and re.fullmatch(SEMVER, data['bundle_version']), 'invalid bundle version')
    components = object_field(data.get('components'), 'components')
    require(set(components) == COMPONENTS, 'manifest component IDs mismatch')
    paths = set()
    for key, component in components.items():
        object_field(component, key)
        require(isinstance(component.get('version'), str) and re.fullmatch(SEMVER, component['version']), f'{key}: invalid version')
        safe_path(component.get('path'))
        require(component['path'] in files and component['path'] not in paths, f'{key}: missing/duplicate component path')
        paths.add(component['path'])
    router = files['SKILL.md'].decode('utf-8')
    require(router.startswith('---\n') and '\n---\n' in router[4:], 'SKILL frontmatter missing')
    frontmatter = router.split('---', 2)[1]
    require(re.search(r'^name: design-baton$', frontmatter, re.M), 'invalid skill name')
    require(re.search(r'^description: .+', frontmatter, re.M), 'description missing')
    require(not any(re.search(r'\bTODO\b|\bTBD\b', raw.decode('utf-8', errors='ignore')) for raw in files.values()),
            'unfinished scaffold in skill')
    for key in COMPONENTS - {'toolkit'}:
        require(components[key]['path'] in router, f'router does not link {key}')
    yaml = files['agents/openai.yaml'].decode('utf-8')
    require('display_name: "Design Baton"' in yaml and '$design-baton' in yaml, 'UI metadata inconsistent')
    # Templates are unpublished output assets; validate after substitution, not as live pins.
    template = parse_json(files['assets/workspace/baton.json'], 'template')
    require(template['procedure']['commit'] is None, 'starter template must not contain a fake commit')
    markdown_links(files, skip_prefixes=('assets/',))
    with tempfile.TemporaryDirectory() as temp:
        init_workspace(Path(temp) / 'bundle-check', 'bundle-check', 'Bundle check', '2026-10-03', '1' * 40, True)
    return files


def package_skill(output_dir, date):
    files = validate_bundle()
    output_dir = Path(output_dir).resolve()
    require(output_dir != SKILL and SKILL not in output_dir.parents, 'skill output must be outside skill folder')
    name = f"design-baton-v{manifest()['bundle_version']}.zip"
    payload = zip_bytes(files, 'design-baton', date)
    output = output_dir / name
    if output.exists():
        require(output.read_bytes() == payload, 'existing skill package differs; choose a new output directory')
    else:
        atomic_write(output, payload)
    checksum = hashlib.sha256(payload).hexdigest()
    checksum_path = output_dir / (name + '.sha256')
    checksum_bytes = f'{checksum}  {name}\n'.encode('ascii')
    if checksum_path.exists():
        require(checksum_path.read_bytes() == checksum_bytes, 'existing checksum differs')
    else:
        atomic_write(checksum_path, checksum_bytes)
    return output


def verify_pin(data, procedure_root):
    """Verify an exact trusted local Git copy; structural validation never pretends retrieval occurred."""
    pin = data['procedure']
    require(not pin.get('fixture'), 'fixture is not a verifiable live release')
    root = Path(procedure_root)
    def git(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
        require(result.returncode == 0, f'pin verification failed: {result.stderr.strip()}')
        return result.stdout.strip()
    tag = git('rev-parse', '--verify', pin['release_tag'] + '^{commit}')
    require(tag == pin['commit'], 'release tag/commit mismatch')
    raw = git('show', pin['commit'] + ':skills/design-baton/versions.json')
    locked = parse_json(raw, 'pinned manifest')
    require(locked['bundle_version'] == pin['bundle_version'], 'pinned manifest/bundle mismatch')
    require(git('rev-parse', 'HEAD') == pin['commit'], 'local procedure checkout is not at pinned commit')
    changes = git('status', '--porcelain', '--', 'skills/design-baton')
    require(not changes, 'local procedure files differ from pinned commit')
    # Status alone trusts index flags such as assume-unchanged and skip-worktree.
    # Verify actual regular-file bytes against every tracked skill blob instead.
    tree = git('ls-tree', '-r', pin['commit'], '--', 'skills/design-baton')
    for line in tree.splitlines():
        fields, path = line.split('\t', 1)
        mode, kind, expected = fields.split()
        safe_path(path)
        local = root / path
        require(kind == 'blob' and mode in ('100644', '100755') and local.is_file() and not local.is_symlink(),
                f'pinned procedure file missing or nonregular: {path}')
        actual = git('hash-object', '--no-filters', str(local.resolve()))
        require(actual == expected, f'local procedure content differs from pinned commit: {path}')
    return locked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='create a minimal workspace; refuses existing destination')
    init.add_argument('root', type=Path)
    for name in ('slug', 'title', 'date', 'commit'):
        init.add_argument('--' + name, required=True)
    init.add_argument('--fixture', action='store_true', help='explicit synthetic fixture pin')
    val = sub.add_parser('validate-workspace', help='offline structural validation; optional local Git pin verification')
    val.add_argument('root', type=Path)
    val.add_argument('--allow-fixture', action='store_true')
    val.add_argument('--procedure-root', type=Path)
    snap = sub.add_parser('snapshot', help='prepare/export complete continuation ZIP, outside workspace')
    snap.add_argument('root', type=Path)
    snap.add_argument('--date', required=True)
    snap.add_argument('--output-dir', required=True, type=Path)
    flags = snap.add_mutually_exclusive_group()
    flags.add_argument('--initial', action='store_true')
    flags.add_argument('--retry', action='store_true')
    snap.add_argument('--allow-fixture', action='store_true')
    inspect = sub.add_parser('inspect-archive', help='bounded validation before extraction; never extracts')
    inspect.add_argument('archive', type=Path)
    inspect.add_argument('--allow-fixture', action='store_true')
    sub.add_parser('validate-bundle', help='validate manifest, router, links and rendered templates')
    package = sub.add_parser('package-skill', help='create deterministic curated ZIP and SHA-256')
    package.add_argument('--output-dir', type=Path, required=True)
    package.add_argument('--date', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            init_workspace(args.root, args.slug, args.title, args.date, args.commit, args.fixture)
            print(f'Created workspace: {args.root}')
        elif args.command == 'validate-workspace':
            data = validate_workspace(args.root, args.allow_fixture)
            if args.procedure_root:
                verify_pin(data, args.procedure_root)
            print('Workspace valid' + ('; exact local release pin verified' if args.procedure_root else '; external pin retrieval not verified'))
        elif args.command == 'snapshot':
            print(f'Exported: {snapshot(args.root, args.output_dir, args.date, args.initial, args.retry, args.allow_fixture)}')
        elif args.command == 'inspect-archive':
            data = inspect_archive(args.archive, args.allow_fixture)
            print(f"Archive valid: {data['project']['slug']} snapshot {data['snapshot']['number']}; nothing extracted")
        elif args.command == 'validate-bundle':
            print(f'Bundle valid: {len(validate_bundle())} curated files')
        elif args.command == 'package-skill':
            print(f'Packaged: {package_skill(args.output_dir, args.date)}')
        return 0
    except (BatonError, OSError, UnicodeError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
