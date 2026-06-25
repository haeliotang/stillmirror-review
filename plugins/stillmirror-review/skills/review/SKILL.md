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
- Allocation Ledger summary;
- Observed Divergence;
- questions for Alignment Review.

Present the labels as a rough prompt for the user's review, never as a
measurement. Do not output drift scores, productivity scores, objective-capture
diagnoses, or advice about what the user should pursue.

If the user says a label is wrong, record the correction so future reviews honor
their judgment (the ledger applies corrections by `event_id`):

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" correct \
  --event <event_id> \
  --label evaluation \
  --note "User reclassified this entry."
```

After the user chooses an alignment label, write it back with:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment record \
  --label necessary_support \
  --note "User confirmed these allocations support the accepted goal."
```
