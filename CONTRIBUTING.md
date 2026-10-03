# Contributing

Use Python 3.10+ and standard-library runtime modules. Keep judgments and owner
agreement in the playbooks; scripts handle deterministic mechanics. Do not impose
a domain taxonomy or turn a proposal into an agreement. Keep the router small.

Before sending a change, run:

```sh
python -m unittest discover -s tests -v
python skills/design-baton/scripts/baton.py validate-bundle
python skills/design-baton/scripts/baton.py validate-workspace examples/sample-project --allow-fixture
python skills/design-baton/scripts/baton.py validate-workspace examples/community-workshop --allow-fixture
```

Add behavior tests for changed boundaries/failure recovery. Exercise conversational
rules with realistic walkthroughs; text-matching tests cannot prove an agent asked
correctly. Use isolated temporary synthetic data, never private project material.

## Version changes

`skills/design-baton/versions.json` is the only authoritative version manifest.
Bump each affected meaningful component and the containing bundle when releasing.
Do not version every Markdown file or repeat version authority in prose. A changed
component may retain its new version on main until a bundle release includes it.
Existing released bundles remain unchanged. If the workspace/map contract changes,
update schema/toolkit/templates/examples together and document compatibility.

During 0.x, minor bumps signal potentially incompatible behavior and require
explicit notes; patches are compatible fixes. At 1.0, major/minor/patch mean
breaking changes, compatible capabilities and compatible fixes. Compatibility
covers readable data, decision/discovery authority, session guarantees and CLI.

## Release checklist

1. Update manifest/changelog and test supported formats, pins and conversational
   guarantees. Review the public file set; no private handoffs or real sources.
2. Commit the tested tree, then create an annotated `vX.Y.Z` tag at that commit.
   Never move or reuse a published tag or force-push release history.
3. Package with `package-skill --date YYYY-MM-DD --output-dir` outside the skill.
   The curated ZIP includes the license; the auto source archive is distinct.
4. Record the full tested commit in release notes after the commit exists; it
   cannot be embedded as its own SHA inside that commit's manifest.
5. Create a fictional continuation with a real release pin and explicit deferral
   after the release commit is known. It need not be committed into its own pin.
6. Publish bundle notes listing component versions and compatibility, curated ZIP,
   SHA-256 checksum, and optional real pinned continuation example.
7. Verify remote peeled tag target, downloadable asset hashes, repository visibility
   and CI. Skill installation is a separate explicitly requested operation.

For long notes use `gh release create ... --notes-file <UTF-8 file>`.
Only bundle GitHub Releases are needed; no per-protocol release pipeline.
