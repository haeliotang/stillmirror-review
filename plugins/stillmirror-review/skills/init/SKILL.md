---
name: stillmirror-review:init
description: Initialize StillMirror Review local project state.
---

# StillMirror Review Init

Use this skill when the user asks to initialize StillMirror Review in the
current project.

Run:

```sh
plugins/stillmirror-review/bin/stillmirror-review init
```

This creates `.stillmirror/` with local-only traces, accepted goals, allocation
rubric, evidence, snapshots, and review folders. Do not upload or transmit any
project traces.
