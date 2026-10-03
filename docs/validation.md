# v0.1.0 validation record

## Automated acceptance

The standard-library unittest suite exercises observable CLI behavior in isolated
temporary directories with synthetic pins and inputs. It covers:

- Fresh offline core generation and validation, complete nonzero commit pins,
  no accidental workspace overwrite, missing core and broken local file links.
- Invalid formats, types, dates, lineage, pin/README inconsistencies and explicitly
  opt-in fixture pins.
- Small authorized complete maps and optional explicit deferrals; rejection of
  16 branches, nested hierarchy, duplicate IDs, broken decision links, wrong boolean
  types and unresolved required leaves marked complete.
- Persisted declined discovery, complete stable-root exports, original source bytes,
  reproducible retry ZIPs, no repeated identity advance and sequential lineage.
- Real output-path failure plus simulated atomic replacement failure: prepared
  identity remains recoverable, no partial archive is reported as successful.
- Unsafe traversal/absolute/backslash/reserved paths, archive symlinks, duplicate
  names, case collisions including directory prefixes, multi-root archives,
  corruption, oversize files and member-count limits.
- Highly compressible source preservation without producing a ZIP that fails its
  own inspection. Existing different archives are not overwritten.
- Curated skill content, deterministic packaging and SHA-256, dangling router
  links and missing component paths.
- Synthetic Git release history: exact pin succeeds, later main does not change
  the old component manifest, wrong tag/commit is rejected, and content hidden
  with assume-unchanged still fails actual pinned-blob verification.

Run `python -m unittest discover -s tests -v`. CI executes the same suite and
bundle/example validation on Linux and Windows with Python 3.10 and 3.13.
Local execution uses Python 3.11. The installed authoring tool's quick_validate.py
also passed frontmatter/name/scaffold checks; UI metadata follows its local schema.
No authoring tool is a runtime dependency.

## Conversational walkthroughs

An independent read-only reviewer checked the handoff against the playbooks and
walked through these scenarios:

| Scenario | Expected behavior found in the procedure |
| --- | --- |
| New slice approved for discussion, discovery unanswered | Record pending; focused useful work continues without discovery |
| Resume declined slice | Preserve refusal; no repeated offer or hidden map |
| Resume accepted slice | Continue map without needlessly reauthorizing |
| Required decision still open or deferred | No slice completion claim |
| Exact shared procedure retrieval fails | Request matching release asset; summarize local records meanwhile; never substitute latest |
| Main changes Decisions Tree version | Existing full-commit pin retains released component versions |
| Owner redirects old next-step recommendation | Follow current direction; select new slice/target before a new discovery offer |

The application fixture distinguishes owner agreement, agent-default and proposal,
with a nonessential reminder deferral. The community workshop fixture distinguishes
agreement and assumption, retains declined discovery and an unresolved required
arrival decision. Neither requires a predefined subject taxonomy.

These are document/scenario walkthroughs, not a claim that arbitrary future agents
will obey every instruction. The toolkit cannot determine whether prose is true,
whether a proposal gained genuine agreement, or whether a map omitted a necessary
decision. Those remain manual checks in the snapshot playbook.

## Review findings and release checks

Independent review found three boundary defects before publication: path-prefix
case ambiguity, compressor/inspection ratio mismatch, and Git-status-only pin
verification. Each was reproduced in a failing regression test and corrected.
The scoped re-review checks the corresponding fixes before release.

The release process verifies the public repository, fully committed tested tree,
annotated tag target, actual sample pin and downloaded asset checksums after the
commit exists. Exact release SHA and final remote results belong in GitHub release
notes; embedding a commit's own SHA in its manifest is impossible.

Limitations: formats other than 0.1.0 are unsupported; no arbitrary migrations,
automatic cloud installation, semantic decision-making, or concurrent snapshot
writers. Local structural checks do not verify external URLs. Anchor fragments
are not validated. ZIP byte identity across different zlib versions is not promised.
