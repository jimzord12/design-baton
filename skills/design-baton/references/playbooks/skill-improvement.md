# Skill improvement

Component: `skill-improvement`. Version authority: [manifest](../../versions.json).

## Review before slice closure

Before closing a slice, review the use of Design Baton during that slice for
observed friction, problems, and worthwhile enhancements. Keep the review brief
and proportional; do not manufacture a finding or reopen the project's target.
When a slice remains active across a session pause, preserve pending feedback
without requiring another review after every response or resumed session.

Use concrete session evidence: a confusing instruction, failed operation,
missing step, repeated manual work, or an unnecessary interaction. Distinguish
an observation from its interpretation and a proposed remedy. Do not invent
measurements. A possible enhancement can be useful without proving a defect;
label its expected benefit and uncertainty.

Separate skill-wide feedback from domain-specific project design. Record a
project problem in its owning project document. Consider reusable procedure
changes here only when the observed behavior or benefit belongs to Design Baton.
Report no meaningful skill feedback briefly when that is the actual result.

## Filter and discuss

Read existing relevant open and closed issues in the procedure's repository
before proposing a new issue. Compare the underlying behavior, affected version,
and evidence, not only similar titles. If issue lookup is unavailable, state
that deduplication is unverified; do not block slice completion.

Present consequential findings with evidence, impact, and a recommendation.
Discuss briefly with the owner. Prioritize worthwhile improvements rather than
filing every inconvenience. An existing matching issue can be referenced locally;
adding a comment or reopening it is a separate action requiring owner approval.

For a proposed new issue, show the complete title and body using the
[issue template](../../assets/skill-improvement-issue.md). Include the pinned
bundle and affected component versions, actual versus expected behavior,
reproduction or a concrete example, impact, a proposed improvement or open
remedy, and acceptance criteria. Distinguish verified facts from assumptions.
Do not claim a repeat count or checked release version without evidence.

## Obtain approval for the exact issue

Create a GitHub issue only after the owner approves the displayed issue draft
and its destination. Approval to use the skill, review feedback, close a slice,
or implement this protocol is not approval to file a particular issue. No answer
is pending, not approval. An explicit instruction to file a fully supplied issue
already authorizes that content and needs no redundant confirmation.

Before displaying the final draft, remove private project details and use a
sanitized example. Include only public-safe links and evidence. If a sensitive
detail is essential, explain the gap and obtain suitable public-safe wording;
do not publish it merely because an issue is useful. Changed scope or material
content requires approval of the revised draft. Minor formatting changes that
preserve the approved content do not.

Issue approval authorizes filing only. It does not authorize implementation,
change the active project's procedure pin, or expand project permissions.
Development and release of a fix are separate authorized work.

## File and preserve the result

Use supported GitHub tools with the approved repository, title, and body. Create
no issue while approval is absent or declined. If a duplicate is discovered
after approval, explain it and propose updating the existing issue rather than
silently posting a different action. Respect that action's approval separately.

Record the returned issue URL, approved draft, and disposition. On a timeout or
uncertain write result, first check whether the issue was actually created
before retrying, to prevent duplicates. On failure, preserve the approved draft,
the attempted destination, approval provenance, and a concrete retry action.
Never claim an issue exists without a confirmed result.

Use `context/skill-feedback.md` only when feedback needs durable retention. It
may contain a concise local ID, slice ID, pinned versions, evidence, disposition
(`draft`, `pending`, `approved`, `declined`, `filed`, or `blocked`), approval
provenance, the public-safe draft, and issue URL when confirmed. This is optional
human-readable project material, not a second decision log or machine lock.
Do not create an empty feedback file. Reconcile continuation notes to point at
the owning record rather than duplicating full drafts. Do not repeatedly ask
about declined feedback or refile an already filed finding on resume.

## Keep closure independent

Review the project's completion target honestly, then perform this brief review
before the final closure message. Pending approval, declined feedback, GitHub
unavailability, or a failed issue write do not prevent an otherwise complete
slice from closing. Preserve unfinished feedback for an appropriate later
response or continuation, then use the normal snapshot route when requested.
Feedback review does not make an incomplete project slice complete.
