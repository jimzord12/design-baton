# Changelog

## 0.2.0 — 2026-10-03

- Add skill-improvement 0.1.0: review observed friction before slice closure,
  discuss meaningful findings, check duplicates, and file only approved exact
  public-safe issue drafts. Preserve pending/failed feedback without blocking closure.
- Update session-lifecycle and snapshots to 0.2.0 for the new close-review route.
- Toolkit 0.1.1 registers the component and packages the reusable issue template.
- Decisions-tree, upgrades, and workspace-format remain at 0.1.0.

Compatibility: workspace/map format remains 0.1.0; no data migration is needed.
The new procedural review changes closure expectations, so the bundle uses a
minor bump. Existing v0.1.0 pins stay unchanged; upgrading is explicit. Issue
approval authorizes filing, not implementing a fix.

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
