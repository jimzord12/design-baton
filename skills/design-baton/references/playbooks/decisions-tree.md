# Decisions Tree Protocol

Component: `decisions-tree`. Version authority: [manifest](../../versions.json).

## Authorization and scope

A slice is a bounded part of a subject with an explicit completion target.
A decision branch is a high-impact unresolved decision area within the slice.
A leaf is a concrete question or decision beneath a branch.

Select the slice and target first. Offer to initialize decision-branch discovery
and wait for an answer. Approval to discuss a slice does not authorize discovery.
An explicit instruction to perform discovery does: do not ask again when already
authorized. Persist state in baton.json and its provenance in project records.

- `not-offered`: make the offer after slice selection.
- `pending`: no answer yet; do useful focused work without discovery.
- `accepted`: discover or resume the map without reauthorization.
- `declined`: continue focused design; do not repeatedly offer within this slice.

Do not generate a hidden map while waiting. Discovery means identifying the
branch set as a procedure step, not merely asking a relevant focused question.
A genuinely new slice needs its own discovery state.

## Discover and present

Rank unresolved areas by consequence, uncertainty, dependencies and likely cost
of rework. Use judgment, without a complicated scoring system. Agreements already
made are context, not unresolved branches to silently reopen.

Aim for 8–10 branches when the slice warrants them; use fewer when sufficient.
The hard maximum is 15 per slice. Do not pad a small slice to hit a target.
If more than 15 areas are consequential, bound or split the slice with the owner.
Each branch has leaves only. No child branches or recursive hierarchy.

Present the branches and a small initial set of consequential, concrete leaf
questions together. No numerical leaf cap has been agreed. Add useful leaves as
discussion exposes them; avoid turning every possibility into an immediate question.
Flag `future_branch` on a leaf with future branch potential without expanding it.

## Work the map

Use JSON as the authoritative map; see [workspace format](../workspace-format.md).
A readable Markdown rendering is optional and derived, never independently edited.
Stable IDs survive reordering. Work a manageable subset of leaves at a time, in
dependency order where useful. Test answers with concrete boundary cases.

Record outcomes in the decisions document with authority, rationale and provenance.
Resolved leaves reference those decision IDs instead of duplicating statements.
Do not resolve a leaf with an unsupported proposal, assumption or mere repetition.
Agent defaults can resolve routine questions when delegated, and remain labeled.
Deferrals state why postponement does not prevent the current completion target.

## Finish or defer

A map explicitly marked complete requires every required leaf to be resolved.
Optional leaves may remain open or be explicitly deferred; prefer an explanation
of remaining work in the state. A slice may finish with explicit deferrals when
all decisions necessary for its target are settled. Required deferrals prevent
completion, even if packaging succeeds.

The validator enforces declared fields, references and limits. The agent still
judges whether the target implies a necessary decision missing from the map and
whether cited outcomes actually settle each question. Do not equate validation
with design adequacy. Preserve supersession links if an agreement changes later.
