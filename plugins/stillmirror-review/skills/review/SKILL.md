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

Present the labels as a rough prompt for the user's review, never as a
measurement. Do not output drift scores, productivity scores, objective-capture
diagnoses, or advice about what the user should pursue.

If the user says a label is wrong, record the correction so future reviews honor
their judgment (the ledger applies corrections by `event_id`):

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" correct \
  --event <event_id> \
  --label evaluation \
  --attested-by "<who is accountable for this correction>" \
  --note "User reclassified this entry."
```

A correction is an accountable act — name who made it (a human, or a named
review process); do not fabricate the reclassification yourself.

After **the user** chooses an alignment label, write it back. The alignment
record is a named human attestation — the irreducible human act this tool exists
to protect. Do not invent the label or the judgment yourself; record only what
the user decided, and name them as the attester:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment record \
  --label necessary_support \
  --attested-by "<the user's name>" \
  --note "User confirmed these allocations support the accepted goal."
```
