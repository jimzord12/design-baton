# Upgrades

Component: `upgrades`. Version authority: [manifest](../../versions.json).

Do not upgrade merely because main or a newer release is available. Projects use
the exact versions included in their pinned bundle. The component manifest at
that commit is authoritative; the project needs no duplicate component lock list.

On an explicit owner request to change procedure version:

1. Identify current and requested bundle tag/full commit. Retrieve exact release
   notes and manifests; verify tag/commit and checksum before relying on assets.
   Tags alone are not cryptographically immutable. Never move a published tag.
2. Compare affected component behavior, workspace readability, decision/discovery
   authority, session guarantees and CLI interfaces. Explain material differences.
   Owner authorization to upgrade does not authorize unrelated product redesign.
3. Check format compatibility. This starter supports only its declared workspace
   and map format. It does not migrate arbitrary legacy files or future formats.
   Reject unsupported formats clearly; obtain an appropriate supported toolkit
   or an explicit migration plan before modifying the lock.
4. Preserve the current workspace as a continuation snapshot when useful and
   authorized. Perform only actual needed migrations; do not label a pin-only
   update a data migration. Preserve source bytes and durable decision provenance.
5. Deliberately update procedure bundle version, release tag, full commit and
   README pinned URLs together. Record the upgrade, rationale, authority and
   any actual migration in decisions. Validate using the destination toolkit
   and exact local release checkout where available.

If exact retrieval fails, request the matching release asset; do not silently use
latest. If a claimed tag points to a different commit, stop the upgrade and name
the mismatch. A successful structural check does not excuse an unverified pin.

Versioning rules: during 0.x, potentially incompatible changes use a minor bump
and explicit compatibility notes; patches are compatible fixes. At 1.0, major,
minor and patch mean breaking changes, compatible capabilities and compatible
fixes. Meaningful protocols and formats have component versions in the manifest;
individual Markdown files do not each need versions. Only bundle GitHub Releases
are published initially; a changed component may develop on main before a bundle
release includes it. Existing released bundles remain unchanged.
