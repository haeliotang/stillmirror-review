---
name: stillmirror-review:ledger
description: Generate an Allocation Ledger from local Claude Code traces and git commits.
---

# StillMirror Allocation Ledger

Use this skill when the user asks where recent attention or agent budget has
actually been allocated.

Run the bundled helper, resolved through the plugin root:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" ledger --since 30d
```

If you are working from a checkout of this repository instead of an installed
plugin, run `plugins/stillmirror-review/bin/stillmirror-review ledger --since 30d`
instead.

The ledger must classify each allocation with one or more rubric labels:

- `core_problem`
- `support_infrastructure`
- `evaluation`
- `packaging_distribution`
- `maintenance_debugging`
- `exploration`
- `noise`

The output is evidence for user review, not a diagnosis.
