# {{TITLE}}

{{FIXTURE_NOTICE}}
This workspace uses Design Baton {{VERSION}}, pinned to commit `{{COMMIT}}`.
Read the [pinned SKILL.md]({{REPOSITORY}}/blob/{{COMMIT}}/skills/design-baton/SKILL.md)
and follow its session-entry route. Obtain shared playbooks from this exact commit;
do not automatically substitute a newer bundle. [Matching release]({{REPOSITORY}}/releases/tag/v{{VERSION}}).

Unzip this bundle and read README.md. The project records carry all necessary
project context; earlier conversations and previous snapshots are not needed.
Verify the pin, then read in this order:

1. [Briefing](context/briefing.md)
2. [Durable decisions](context/decisions.md)
3. [Current state](PROJECT_STATE.md)
4. The active subject and map referenced in [baton.json](baton.json), if any.

[Glossary](context/glossary.md) defines project terms. Machine identity, snapshot
lineage and discovery authorization belong in baton.json; prose owns progress.
If exact procedure retrieval fails, summarize these local records while asking
the owner to attach the matching skill release asset. Do not claim a validated
procedural resume or improvise the missing rules.
