# Design Baton

Carry AI-assisted project design across conversations without reconstructing
context. A small skill router supplies consistent mechanics; your project files
carry domain knowledge, decisions and progress.

The usual continuation entry is: **“Unzip this bundle and read README.md.”**

Design Baton guides bounded slices, offers decision-branch discovery with explicit
authorization, records durable outcomes, and exports complete continuation ZIPs
when you ask to pause or close. It works for application design, workshop planning
and other domains without imposing a fixed subject taxonomy.

## First release

[v0.1.0 release and downloadable assets](https://github.com/jimzord12/design-baton/releases/tag/v0.1.0)
contains the installable `design-baton-v0.1.0.zip`, SHA-256 checksum, and a separate
fictional sample continuation ZIP pinned to the exact released commit.

The source repository and GitHub's automatic source archive include maintainer
material. The curated skill asset contains only the complete installable skill
folder and license. Publication does not install it into a cloud or personal skill
environment. Extract the skill asset, verify its checksum, and follow your agent
environment's supported installation workflow if you choose to install it.

Read [SKILL.md](skills/design-baton/SKILL.md) for routing and the
[workspace format](skills/design-baton/references/workspace-format.md) for contracts.
The four playbooks cover session lifecycle, the **Decisions Tree Protocol**,
snapshots, and explicit upgrades. [versions.json](skills/design-baton/versions.json)
is the authoritative bundle/component manifest.

## Try it locally

Python 3.10+ is the only runtime requirement. No package installation or network is
needed for workspace operations after the exact skill has been obtained.
From a Git checkout at the release (PowerShell):

```powershell
$pin = git rev-parse 'v0.1.0^{commit}'
python skills/design-baton/scripts/baton.py init ../my-project --slug my-project --title 'My project' --date 2026-10-03 --commit $pin
python skills/design-baton/scripts/baton.py validate-workspace ../my-project --procedure-root .
python skills/design-baton/scripts/baton.py snapshot ../my-project --initial --date 2026-10-03 --output-dir ../baton-exports
python skills/design-baton/scripts/baton.py inspect-archive ../baton-exports/01-my-project.zip
```

Fill the briefing before design starts. Select a slice and target, then offer
discovery; do not generate a map automatically. A declined answer persists across
resumes. Explicit discovery authorization is not requested again for that slice.
Maps are flat with at most 15 branches; there is no hard numerical leaf cap.

Snapshot commands reconcile mechanics only. The agent checks decision authority,
necessary unresolved work, source fidelity and semantic progress before export.
On a prepared-output failure, rerun with the same date and a working output
directory. Use `--retry` to export the same identity after success. Existing
different archives are refused. Details are in the snapshots playbook.

## Examples and validation

[Synthetic examples](examples/README.md) cover a volunteer application and a
community workshop. Their repository pins are explicitly fixtures, not real
released procedures. The release's downloadable sample uses the actual commit.

```sh
python -m unittest discover -s tests -v
python skills/design-baton/scripts/baton.py validate-bundle
python skills/design-baton/scripts/baton.py validate-workspace examples/sample-project --allow-fixture
python skills/design-baton/scripts/baton.py validate-workspace examples/community-workshop --allow-fixture
python skills/design-baton/scripts/baton.py package-skill --date 2026-10-03 --output-dir ../baton-release
```

[Validation record](docs/validation.md) distinguishes automated checks from
conversational walkthroughs. CI runs tests and bundle/example validation on
Linux and Windows. Runtime ZIP inspection never extracts unsafe members.

## Versioning and boundaries

Projects pin a bundle tag and exact full commit. They use the component versions
included at that commit even if main develops further. Upgrades are explicit;
tags are not described as cryptographically immutable. During 0.x, potentially
incompatible changes get a minor bump and explicit notes; compatible fixes get
patches. Only bundle releases are published initially.

This starter has no web app, orchestration framework, automatic semantic decisions,
legacy migration system or automatic cloud installation. ZIP byte reproducibility
holds for identical inputs/date in the same Python/zlib environment. No semantic
claim follows from packaging success.

MIT licensed. See [contributing and release instructions](CONTRIBUTING.md).
