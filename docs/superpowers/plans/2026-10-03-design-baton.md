# Design Baton v0.1.0 Implementation Plan

> **For agentic workers:** Use executing-plans for inline execution and requesting-code-review for independent review. Steps use checkbox syntax for tracking.

**Goal:** Publish the portable Design Baton skill, deterministic toolkit, and synthetic continuation example.

**Architecture:** A small skill router delegates to four playbooks. One standard-library Python CLI owns mechanical file validation and reproducible packaging; agents and owners own semantic decisions.

**Tech Stack:** Python 3.10+, unittest, Markdown, JSON, GitHub Actions.

**Spec:** Owner-supplied local implementation handoff, intentionally excluded from publication. Public contracts are maintained in the workspace format and playbooks.

## Global Constraints

- Bundle and initial component versions: 0.1.0; skill slug: design-baton; MIT.
- Discovery is offered at each new slice, performed only with authorization, and persisted across resumes.
- At most 15 flat decision branches; no invented leaf limit.
- Exact full-commit pins; no substitution of main; no skill installation implied by publication.
- Standard library runtime; source bytes preserved; no private operational material published.

### Task 1: Workspace and map contracts

Files: `tests/test_baton.py`, `skills/design-baton/scripts/baton.py`, `skills/design-baton/assets/workspace/`, `skills/design-baton/references/workspace-format.md`.

Interfaces: `init_workspace(root, slug, title, date, commit, fixture=False)`, `validate_workspace(root, allow_fixture=False)`, `BatonError`.

- [x] Write black-box CLI tests for initialization, missing core, invalid metadata, broken links, and map authority/completion boundaries.
- [x] Run `python -m unittest discover -s tests -v`; confirm missing CLI fails.
- [x] Implement typed metadata checks, portable path checks, local link resolution, decision IDs and flat maps.
- [x] Run the same tests; correct failures; inspect the diff.

### Task 2: Archives and snapshot transactions

Files: toolkit and tests from Task 1; snapshots playbook.

Interfaces: CLI `snapshot ROOT --date DATE --output-dir DIR [--initial|--retry]`, `inspect-archive ZIP [--allow-fixture]`.

- [x] Write tests proving stable roots, reproducibility, failure recovery, repeat retry identity, hostile archive rejection and source fidelity.
- [x] Run tests and confirm absent commands fail.
- [x] Implement deterministic sorted ZIPs, bounded inspection before extraction, staged metadata and atomic output.
- [x] Run tests; inspect metadata before and after simulated output failure.

### Task 3: Procedure and bundle packaging

Files: `SKILL.md`, `agents/openai.yaml`, `versions.json`, four playbooks, bundle validation/package CLI, repository documentation and CI.

Interfaces: `validate-bundle`, `package-skill --output-dir DIR --date DATE`; optional exact local pin verification during workspace validation.

- [x] Write tests for broken manifest/router paths, curated package content and deterministic checksum.
- [x] Run tests and confirm missing package command fails.
- [x] Author routing, discovery, snapshots, upgrades, precise schema and CLI examples.
- [x] Implement manifest and template validation, explicit curated file set, SHA-256 output.
- [x] Run authoring validator, full unittest suite and CLI smoke checks.

### Task 4: Examples, review and publication

Files: `examples/`, `docs/validation.md`, changelog and release notes. Release artifacts stay outside versioned workspace.

- [x] Generate explicitly labeled fixture examples in application and community domains, each with distinct authority labels.
- [x] Independently walk through new/resumed/declined discovery, required decisions, retrieval failure and upgrades; review code against the handoff.
- [x] Resolve findings, run final tests, bundle validation, and public file/privacy review.
- [ ] Commit tested tree; push; annotate `v0.1.0`; record exact commit in release notes.
- [ ] Generate real pinned sample after commit, package skill and checksum, publish release, and verify remote tag and assets.

## Execution record

The owner explicitly authorized implementation, commits, pushes, and public release. Work uses the fresh repository checkout; no unrelated local work exists. No history rewriting or cleanup is needed.
