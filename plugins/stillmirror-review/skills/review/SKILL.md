---
name: stillmirror-review:review
description: Generate a Project Drift Review markdown file for user alignment review.
---

# StillMirror Project Drift Review

Use this skill when the user asks for a StillMirror review of the current
project.

Run:

```sh
plugins/stillmirror-review/bin/stillmirror-review review --since 30d
```

The review must include:

- Mainline Hypothesis;
- Accepted Goals;
- Allocation Ledger summary;
- Observed Divergence;
- questions for Alignment Review.

Do not output drift scores, productivity scores, objective-capture diagnoses,
or advice about what the user should pursue.

After the user chooses an alignment label, write it back with:

```sh
plugins/stillmirror-review/bin/stillmirror-review alignment record \
  --label necessary_support \
  --note "User confirmed these allocations support the accepted goal."
```
