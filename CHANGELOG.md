# Changelog

## 0.1.0 — 2026-10-03

Initial bundle: session-lifecycle, decisions-tree, snapshots, upgrades,
workspace-format and toolkit components all at 0.1.0.

- Progressive skill router and four independently maintained playbooks.
- Explicit discovery authority persisted across resumed slices; flat maps with
  at most 15 branches and linked durable outcomes.
- Exact tag/full-commit project pins; explicit upgrade and retrieval-failure routes.
- Standard-library Python workspace initialization, validation, snapshot recovery,
  bounded archive inspection and reproducible skill packaging with SHA-256.
- Application and community-domain fixture examples, acceptance tests and CI.

Compatibility: first supported workspace/map format is 0.1.0. No older or future
format migration is implemented. Publication is separate from skill installation.
