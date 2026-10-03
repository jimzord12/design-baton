---
name: design-baton
description: Guide AI-assisted project design across conversations with bounded decision slices, durable agreements, and versioned continuation bundles. Use to start or resume design, authorize decision discovery, pause or export a project, or explicitly upgrade its procedure.
---

# Design Baton

Design Baton supplies shared session mechanics. Project records supply purpose,
domain knowledge, constraints, preferences, decisions and progress.
It is a design procedure, not a subsystem of the project or an autonomous
development framework. Follow the owner's chosen scope.

## Choose the route

| Request | Read | Result |
| --- | --- | --- |
| Start or resume design | [Session lifecycle](references/playbooks/session-lifecycle.md) | Briefed agent, selected slice, visible completion target |
| Explicit discovery authorization or working an existing map | [Decisions Tree Protocol](references/playbooks/decisions-tree.md) | Bounded map and recorded leaf outcomes |
| Pause, close or export | [Snapshots](references/playbooks/snapshots.md) | Reconciled workspace and complete continuation ZIP |
| Explicit procedure version change | [Upgrades](references/playbooks/upgrades.md) | Reviewed compatibility and intentional pin change |

Read only the needed playbooks. Also read the [workspace format](references/workspace-format.md)
when generating, validating or changing persisted files.
Reading order does not authorize expanding the project scope.
Component identities and versions come from [versions.json](versions.json).

## Establish the procedure first

For a continuation bundle, inspect archive safety before extracting it.
Read its README and `baton.json` to identify the exact bundle pin.
Use an installed matching skill or an exact verified local copy when available.
Otherwise retrieve `skills/design-baton/SKILL.md` and its referenced resources
from the full pinned commit, then follow the session-entry route.

Verify release tag, full commit and bundle manifest agree. An installed skill
with the same name is insufficient evidence that its version matches.
Do not substitute main, latest, or a nearby version.
Local structural validation alone does not verify external release identity.
The toolkit's `--procedure-root` option can verify a clean local Git checkout.

If retrieval fails, name the missing pinned procedure and request the matching
release asset. Meanwhile read and summarize the local project records using the
README's reading order. Do not invent missing playbook rules or claim a validated
procedural resume. No earlier conversation or private storage should be needed.

## Preserve authority

Distinguish owner decisions, delegated agent defaults, proposals, assumptions
and open questions. Record rationale and provenance for durable decisions.
Supported owner agreement is necessary to label an entry an owner decision.
Do not reopen established agreements silently.

Current owner redirection takes precedence over old continuation suggestions.
Ask only unresolved questions that materially affect scope, constraints,
completion or costly rework. Resolve routine choices under existing delegation.
Record cross-subject implications without redesigning every affected subject.

Scripts validate structure and package files. They do not make agreements,
judge whether prose is true, authorize discovery, or establish semantic completion.

## Keep slices bounded

A slice is a bounded part of a subject with an explicit completion target.
A decision branch is a consequential unresolved area within that slice.
A leaf is a concrete question underneath a branch.

At each new slice, propose/select the slice and target first. Then offer to
initialize branch discovery and wait for the owner's answer.
Approval to discuss the slice is not discovery authorization.
An explicit instruction to perform discovery is authorization; do not ask again.

Persist discovery as `not-offered`, `pending`, `accepted` or `declined` in
`baton.json`. Resume honors that state and supporting provenance.
If declined, continue focused work without repeating the offer in that slice.
If pending, do useful work that does not perform discovery.

When accepted, aim for 8–10 consequential branches; fewer are fine.
The hard maximum is 15 branches per slice. Do not pad.
Branches contain leaves only, without child branches or recursive hierarchy.
Present branches with a small initial set of concrete leaves; there is no
agreed hard numerical leaf limit. Flag future branch potential without expanding it.

Work through a manageable subset of leaves and test boundaries with concrete cases.
Resolved leaves link to durable decision IDs. Optional decisions may be deferred
with reasons. Any unresolved decision necessary for the slice target prevents
completion, including necessary decisions omitted from the map.

## Maintain the project workspace

Required core: README, `baton.json`, PROJECT_STATE, briefing, decisions and glossary.
Create project-specific subjects, maps and source directories only when needed.
No universal subject taxonomy is imposed.

`baton.json` owns machine identity, lineage and discovery authorization.
PROJECT_STATE owns current semantic progress and actionable continuation notes.
Briefing owns project context; decisions owns durable agreements and provenance.
Original supplied sources remain byte-for-byte intact.

Reconcile documents before packaging. On a requested pause or close, produce
a complete validated continuation ZIP with a stable project root.
Do not create a ZIP after every reply. A snapshot is neither an incremental diff
nor a conversation transcript. Do not put generic playbooks or runtime scripts
in normal project ZIPs; pin their released version instead.

## Mechanical tools

Use [scripts/baton.py](scripts/baton.py) with Python 3.10+; no runtime dependencies.
Its CLI creates workspaces, validates files, exports snapshots, inspects archives,
and validates/packages this skill. Run `python scripts/baton.py --help` from the
skill folder. Concrete commands and contract details are in the workspace format.

An unfinished export is a failure, even if a recoverable prepared identity exists.
Report what succeeded, the exact recovery action, and what remains unverified.
Checksums establish asset integrity, not owner agreement or procedural authority.

## Explicit upgrades only

Existing projects use precisely their pinned bundle's component versions.
Default-branch development never changes that pin.
Use the upgrades route only when the owner explicitly requests a version change.
Review affected behavior, formats and compatibility before changing the lock.
Record an upgrade and any actual migration. Reject unsupported formats clearly.
