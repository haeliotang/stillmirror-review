---
name: stillmirror-review:review
description: Generate a Project Drift Review markdown file for user alignment review.
---

# StillMirror Project Drift Review

Use this skill when the user asks for a StillMirror review of the current
project.

Run the bundled helper, resolved through the plugin root:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" review --since 30d
```

If you are working from a checkout of this repository instead of an installed
plugin, run `plugins/stillmirror-review/bin/stillmirror-review review --since 30d`
instead.

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
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" alignment record \
  --label necessary_support \
  --note "User confirmed these allocations support the accepted goal."
```
