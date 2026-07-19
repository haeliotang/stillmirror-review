---
name: stillmirror-review:review
description: Generate a Project Alignment Review markdown file for user alignment review.
---

# StillMirror Project Alignment Review

Use this skill when the user asks for a StillMirror review of the current
project. The review joins two spines — the goals the user accepted (what they
authorized) and the allocation evidence (what the agent did) — and surfaces them
for human alignment review.

Run the bundled helper, resolved through the plugin root:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" review --since 30d
```

If you are working from a checkout of this repository instead of an installed
plugin, run `plugins/stillmirror-review/bin/stillmirror-review review --since 30d`
instead.

The review must include:

- Coverage & Blind Spots (what StillMirror could not see);
- Mainline Hypothesis;
- Goal Provenance (each goal's lifecycle state and how many allocations
  reinforced it);
- Basis Change Impact (goal → explicit claim → file chains with stale basis,
  scoped to branch-changed files when `--base` is used);
- Triage — what's worth the user's attention (clusters by goal, by session, and
  by agent — real subagent identity, a session is not an agent — plus surfaced
  exceptions like unlinked work);
- Allocation Ledger summary;
- Observed Divergence;
- questions for Alignment Review.

The Triage section is where to point the user when there is a flood of
multi-agent work: it surfaces exceptions for review, never ranks agents or
asserts trends. Surfaced ≠ judged wrong; not surfaced ≠ approved.

To check whether a review is even due (e.g. before nudging the user), run
`"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" review-due`; it reports new
allocations, new goal events, how many top-level sessions ran, and how many
distinct subagents (`agents_touched`) ran since the last review.

Do not output drift scores, productivity scores, objective-capture diagnoses, or
advice about what the user should pursue.

## Basis Change Impact — declared receipts, item-level human decisions

Formation receipts must be recorded at a real decision boundary, when the claim
and affected files are explicit. Do not reconstruct them from hidden reasoning
or invent them retrospectively during review. A worker can record one atomically:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" formation record \
  --claim "<explicit decision claim>" \
  --basis-goal "<active accepted goal>" \
  --artifact "<repository file>" \
  --declared-by "<named human or agent>" --tier agent
```

When the review surfaces `needs_revalidation`, explain that the recorded basis
changed; do not call the artifact wrong. Ask the user separately about each
impact item. Only after the user decides, record their item-level decision:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" impact revalidate <impact-id> \
  --decision retained|updated|retired --attested-by "<the user's name>"
```

Never revalidate on the user's behalf. A project-wide `alignment record` or
proposal ratification does not clear pending impact items.

## Assisted attestation — you draft, the human ratifies

The seven alignment labels (`necessary_support`, `intentional_pivot`,
`operational_drift`, `exploration`, `noise`, `misclassification`,
`insufficient_evidence`) are a **machine vocabulary**. **Do not make the user
operate them** — for a human, choosing from a taxonomy and composing a reason is
exactly the friction that makes them abdicate. Instead:

**1. Draft a proposal.** Read the review evidence and map it to labels + a short
plain-language note, then record it as a *draft* (it is NOT an attestation — the
judgment seat stays empty until the user ratifies):

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment propose \
  --label necessary_support --label exploration \
  --note "<your plain-language read of the period>" \
  --drafted-by "assistant"
```

**2. Ask the user in plain terms — never show them the label list.** Give them a
one-line read and exactly three options:

> "This period looks like *<your one-line plain read>*. Does that look right, is
> something off, or can't you tell?"

**3. Ratify with their decision** — this is the irreducible human act; only the
user decides, and you must never ratify on their behalf:

```sh
# "looks right" →
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment ratify \
  --decision accept --attested-by "<the user's name>"

# "something's off: it was actually …" → re-map their words to labels, then:
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment ratify \
  --decision amend --label operational_drift \
  --note "<the user's correction, in their words>" --attested-by "<the user's name>"

# "no, that read is wrong / I won't endorse it" →
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment ratify \
  --decision reject --attested-by "<the user's name>"
```

`accept`/`amend` record a real attestation carrying both `proposed_by` (you) and
`attested_by` (the user). `reject` leaves the seat empty — abdication stays
visible; do not retry it as an accept. **Silence is not assent:** if the user
does not answer, leave the draft pending; never accept on their behalf.

If a *classifier* label on a specific allocation is wrong (not the overall
judgment), correct that entry instead — an accountable act, named, not fabricated:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" correct \
  --event <event_id> --label evaluation \
  --attested-by "<who is accountable>" --note "User reclassified this entry."
```

A user who prefers to author their own attestation directly can still use
`alignment record --label … --attested-by "<their name>"` — but default to the
draft-and-ratify flow above; it is what keeps the human act cheap without forging
it.
