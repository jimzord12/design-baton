# Snapshots

Component: `snapshots`. Version authority: [manifest](../../versions.json).

## Reconcile first

On requested pause, close or export, prepare a complete current workspace. Do
not export after every reply. A snapshot is neither a transcript nor a diff.

Ownership: README owns procedure reference and reading order; baton.json owns
machine pin, snapshot lineage and discovery authorization; briefing owns purpose,
scope and constraints; decisions owns durable outcomes, authority and provenance;
glossary owns shared terms; PROJECT_STATE owns semantic progress, blockers and next
action; subjects own design; maps own authorized questions; sources own unchanged
original reference material. See the [format](../workspace-format.md).

Reconcile each owning document before validation. Keep continuation notes short
and actionable. Remove resolved notes after preserving durable material. Preserve
sources byte-for-byte. Generate only useful subject documents and maps; do not
create empty folders or copy generic machinery into a normal project ZIP.

Manual checks before packaging:

- Owner agreements have supporting provenance; proposals, defaults and assumptions
  retain their labels. Supersession is explicit.
- Every decision necessary for the slice target is settled before claiming completion.
  Optional deferrals are reasoned, and no necessary decision was omitted from the map.
- Human state agrees with map outcomes and machine discovery authorization.
- Original supplied sources match their original bytes; local links resolve.
- Continuation notes describe current blockers and one useful next action, without
  stale resolved tasks or reliance on old conversations.

## Identity and packaging

Use one stable extracted root `<project-slug>/`. Initial workspace identity is 1,
predecessor null. Export it with `--initial`. Subsequent snapshots are sequential,
with predecessor N-1; filenames are `NN-<project-slug>.zip`, at least two digits
and naturally larger after 99. The explicit ISO date is part of the identity.

After a successful export, an ordinary snapshot command prepares the next identity.
For an already prepared identity, including a failed output attempt, the ordinary
command exports that identity. `--retry` explicitly exports the current identity
without incrementing it. Use its existing prepared date. A changed archive with
the same filename is refused; select a separate output directory for a revised
prepared export and identify the revision honestly. Do not treat competing copies
as authoritative solely because one has a higher number.

The toolkit persists `export_status: prepared` before writing output. It builds
the candidate archive with `export_status: exported`, validates, and writes it
atomically outside the root; only then persists exported status locally. Output
failure leaves a recoverable prepared identity and returns failure. If final
metadata persistence fails, the existing archive may be present; retry verifies
identical bytes and finishes the metadata update. A retry does not advance identity.
Commands are single-writer: do not run concurrent snapshots against the same root.

Sorted members, normalized midnight timestamps, regular-file permissions and fixed
compression make identical inputs/date/identity produce identical bytes in the
same Python/zlib environment. Cross-zlib byte identity is not promised.
All current project files and original sources are included, subject to the
documented generated-content exclusions and archive limits. Review the file set
for private or unrelated files before sharing; filenames alone cannot identify them.

## Verify and deliver

Validate workspace, export outside its root, then inspect the resulting archive
before extraction or delivery. State the filename, identity and remaining blockers.
Package success validates mechanics, not truth of prose or semantic completion.
On failure say what is prepared, which output (if any) exists, and the exact retry
command. Do not announce a successful export without a valid resulting archive.

For parallel continuations, identify their common predecessor, compare changes
and reconcile agreements and scope explicitly. Higher numbering is not proof of
authority. Full branch/merge automation is outside this starter's scope.
