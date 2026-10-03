# Workspace format and toolkit

Component: `workspace-format`. Version authority: [manifest](../versions.json).
Runtime: Python 3.10+, standard library. This toolkit supports workspace and map
format `0.1.0`. Unsupported formats are rejected; migrations are explicit work.

## Ownership and layout

Required files: README.md, baton.json, PROJECT_STATE.md, context/briefing.md,
context/decisions.md, context/glossary.md. Optional: subjects/, maps/, sources/.
One stable portable project root; no fixed subject taxonomy or empty directories.

| File | Authority |
| --- | --- |
| README.md | Exact procedure reference, entry wording and reading order |
| baton.json | Machine identity, pin, lineage, active slice and discovery |
| PROJECT_STATE.md | Semantic progress, blockers and next action |
| context/briefing.md | Purpose, scope, constraints and owner preferences |
| context/decisions.md | Durable decisions, rationale, authority and provenance |
| context/glossary.md | Project and procedure terms |
| subjects/ | Project-specific design |
| maps/ | Authoritative JSON branch maps; optional derived views |
| sources/ | Original supplied material, preserved byte-for-byte |

## baton.json schema

All objects use UTF-8 JSON; duplicate keys are rejected. Required fields:

- `workspace_format`: exactly `0.1.0`.
- `project`: object; `slug` matches `[a-z0-9]+(?:-[a-z0-9]+)*`, at most 64
  characters, excluding portable reserved filenames; `title` is nonempty one-line text.
- `procedure`: object; `repository` is `https://github.com/jimzord12/design-baton`;
  `bundle_version` is semantic `X.Y.Z` and matches the toolkit's bundle;
  `release_tag` is `v` plus that version; `commit` is a nonzero lowercase 40-character
  hexadecimal full Git commit; `entry_path` is `skills/design-baton/SKILL.md`.
  Optional boolean `fixture` must be true only for synthetic/offline examples;
  validation/export requires `--allow-fixture`. Such README files say **FIXTURE**
  and are not usable live pins. Templates have null commit/date and cannot resume.
- `snapshot`: object; `number` is an integer >=1 (booleans rejected);
  `predecessor` is null for 1, otherwise integer number-1; `prepared_on` is a real
  ISO `YYYY-MM-DD` date, ZIP-compatible year 1980–2107; `export_status` is `prepared`
  or `exported`. It tracks mechanical output, never semantic completion.
- `active_slice`: null, or object with `id` matching `[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}`;
  `subject` is an existing Markdown relative path; `target` is nonempty text;
  optional `map` is an existing JSON path under maps/; `discovery` is `not-offered`,
  `pending`, `accepted`, or `declined`. Active maps require accepted discovery.

README must identify Design Baton plus exact version, link to the full-commit
SKILL.md and matching release, and supply the entry paragraph and reading order.
Do not copy the snapshot number/discovery fields into competing prose locks.
Extra descriptive fields may be added to machine objects; they cannot override
these owned fields. Maps have a stricter branch/leaf shape to forbid recursion.

## Decisions and maps

Each decision uses a stable `## D-001` heading (ID starts `D-`, then letters,
digits, underscores or hyphens). Include Statement, Rationale, Status, Authority,
Source and relevant Supersedes ID. Owner decisions need supported agreement;
agent-default records delegated routine choices; proposal and assumption remain
distinct. Stable IDs are unique. The agent assesses authority and actual resolution;
structural validation checks uniqueness and existence, not truth of agreements.

Map fields: `map_format: "0.1.0"`, `slice_id`, `target`, boolean `complete`,
and `branches`, a list of 1–15 objects with `id`, `title`, `leaves` only.
Historical maps (not active) additionally record `discovery: "accepted"` so
archiving does not erase authorization. Keep supporting provenance in project prose.
Active map ID/target must match the active slice. Branches and leaves share one
unique ID namespace per map; IDs match the slice ID pattern and survive reordering.

Every leaf has `id`, nonempty `question`, boolean `required`, `status` (`open`,
`resolved`, `deferred`), boolean `future_branch`. Resolved leaves have a nonempty
`decisions` list of existing unique decision IDs. Open/deferred leaves have no
resolving decision references. Deferred leaves have a nonempty `rationale`.
No nested branches/children or unknown branch/leaf fields. No hard leaf count cap.
A complete map has no unresolved required leaves. Optional explicit deferrals
are allowed. Structural completion does not prove all necessary decisions were found.

## Path and archive safety

Paths use forward slashes, relative to the root. Reject absolute paths, empty,
dot/traversal segments, backslashes, controls, Windows reserved names and illegal
filename characters, trailing spaces/dots, symlinks and case collisions. Markdown
inline/image and reference-style local file/directory links are checked offline;
parent links may normalize inside the root. Fragments are not anchor-validated.
External URLs are not fetched by validation. External retrieval and semantic checks
remain the agent's responsibility.

Archives: maximum 2,000 members, 50 MiB per file, 200 MiB total uncompressed,
1,000:1 compression ratio. Inspection verifies member paths, CRC/read integrity,
one root matching slug, regular files, required core and map metadata without
extracting anything. Absolute/traversal/backslash paths, encrypted members, symlinks,
duplicate names, case and file/directory collisions are rejected. Extract only
an inspected archive into a fresh destination; never overlay existing work.

Workspace packaging omits `.git`, `__pycache__`, `.pytest_cache`, `.venv`,
node_modules, dist, build, exports, output and .superpowers directories; outside
sources/ it also omits ZIPs, `.pyc`, `.tmp` and `.baton-*` files. The sources tree
is original input and is not filtered by those generated-content names. Safety
and size limits still apply. Store supplied archives under sources/ to preserve them.
Review all other files before publication; exclusion rules cannot detect private data.

## Runnable commands

Run from the repository root, or replace the script path with the installed
skill's `scripts/baton.py`. Get the real released full commit first:

```sh
gh api repos/jimzord12/design-baton/git/ref/tags/v0.1.0
git rev-parse 'v0.1.0^{commit}'
```

An annotated tag API response identifies a tag object, which must be peeled to
its commit. Use the commit shown in release notes or Git's peeled result. The
following shell variable represents that verified full commit, not the tag object:

```sh
PIN=$(git rev-parse 'v0.1.0^{commit}')
python skills/design-baton/scripts/baton.py init ./my-project --slug my-project --title 'My project' --date 2026-10-03 --commit "$PIN"
python skills/design-baton/scripts/baton.py validate-workspace ./my-project
python skills/design-baton/scripts/baton.py validate-workspace ./my-project --procedure-root .
python skills/design-baton/scripts/baton.py snapshot ./my-project --initial --date 2026-10-03 --output-dir ../baton-exports
python skills/design-baton/scripts/baton.py inspect-archive ../baton-exports/01-my-project.zip
python skills/design-baton/scripts/baton.py snapshot ./my-project --retry --date 2026-10-03 --output-dir ../baton-exports
python skills/design-baton/scripts/baton.py validate-bundle
python skills/design-baton/scripts/baton.py package-skill --date 2026-10-03 --output-dir ../baton-release
```

PowerShell equivalent: `$pin = git rev-parse 'v0.1.0^{commit}'`; pass `--commit $pin`.
For tests only, `init --fixture` labels a synthetic full commit; subsequent commands
require `--allow-fixture`. It is never advertised as a released procedural pin.

`--procedure-root` requires Git, a clean skill tree at the pinned HEAD, a matching
tag commit, byte-matching tracked regular skill files, and the pinned manifest bundle version. It reads the manifest from
the commit, not from newer main files. Offline structural checks without this
option explicitly do not verify external tag identity. Agents can instead verify
the exact remotely retrieved commit/tag and release asset checksum.

Snapshot requires output outside the root. `--initial` exports identity 1;
ordinary commands after an exported identity advance once. Prepared identities
and `--retry` retain number and date. On output failure the identity stays prepared.
Retry with its date and a working output directory. Existing different output is
refused. Exported archive and final local metadata contain identical identity.
Single writer only; see [Snapshots](playbooks/snapshots.md) for recovery guarantees.

Curated skill ZIP has root design-baton/, router, UI metadata, manifest, references,
templates, toolkit and MIT license. It excludes repository tests and human docs.
SHA-256 is emitted as `<asset>.sha256`. Packaging is deterministic for identical
inputs/date in the same Python/zlib environment; published assets are checksummed.
Highly compressible files use stored members to respect inspection ratio limits.
