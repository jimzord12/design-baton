# Session lifecycle

Component: `session-lifecycle`. Version authority: [manifest](../../versions.json).

## Entry and resume

1. Inspect an attached ZIP before extraction. Resolve and verify the procedure
   pin in README and baton.json; see the [format](../workspace-format.md).
   Obtain the exact pinned router and relevant resources. If retrieval fails,
   request the matching release asset and summarize local records meanwhile.
   Do not use latest or claim a validated procedural resume.
2. Read README, briefing, decisions, PROJECT_STATE, then the selected subject
   and its map if one exists. Consult glossary for unfamiliar project terms.
   These records must stand alone without prior conversations.
3. State the project purpose and recommend one bounded slice with an explicit
   target, briefly. Honor current owner redirection over the old next step.
   Continue an already selected slice when appropriate; do not create a new
   slice merely because a conversation restarted.
4. For a new selected slice, set a stable ID, subject path and target in
   baton.json. Set discovery to `not-offered`, offer discovery, and record
   `pending` while waiting. Do not perform discovery before the answer.
   An explicit request for discovery already authorizes it: record `accepted`
   and proceed without redundant approval. Discussing the slice alone does not.
5. On resume, accepted stays accepted and declined stays declined for that
   slice. Pending remains pending; continue useful focused work without
   discovery. An answer changing discovery state is recorded with provenance
   in decisions or subject notes. Do not repeatedly prompt a declined owner.

## Active discussion

Distinguish owner decisions, agent defaults made under delegation, proposals,
assumptions and open questions. Record durable outcomes in decisions with stable
IDs, rationale, status, authority and source. Supersession is explicit; retain
the old decision and link the replacement. Repetition does not establish agreement.

Keep the target visible. Use concrete cases to expose boundaries, such as what
happens when a workshop participant arrives late or an application user submits
incomplete data. Ask high-impact questions only when unresolved and relevant.
Do routine work under existing delegation. When discovery is authorized, use
the [Decisions Tree Protocol](decisions-tree.md); otherwise continue focused design.

Update subject design when its substance changes. Record implications for other
subjects as links or concise notes rather than independently redesigning them.
Remove resolved continuation notes after moving durable facts to their owner.
Do not append a retrospective after every response or create unnecessary ZIPs.

## Scope change and completion

When the owner redirects, state the revised scope and target. Decide whether it
is the same slice with a clarification or a genuinely new bounded slice. Preserve
existing outcomes and deferred leaves; if it is new, assign a new ID and offer
discovery independently. Old authorization does not authorize a different slice.
Archived maps retain their discovery authorization and stable IDs.

Judge completion against the target, not the existence of a ZIP or a checked
box. A slice may complete with explicit nonessential deferrals. Required open or
deferred decisions prevent completion. Check for omitted necessary decisions too.
Announce completion and the recommended next slice; selection and discovery
authorization remain separate. Established decisions provide context unless the
owner intentionally reopens one.

## Pause and close

On an explicit pause, close or export, use [Snapshots](snapshots.md). Reconcile
the current documents, state blockers and next action, validate, and produce the
complete continuation ZIP. If packaging or retrieval fails, report the precise
failure and recovery action rather than a successful handoff. Do not claim that
public repository publication installed the procedure into a cloud environment.
