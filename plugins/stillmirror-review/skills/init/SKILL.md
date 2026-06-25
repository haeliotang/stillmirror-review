---
name: stillmirror-review:init
description: Initialize StillMirror Review local project state.
---

# StillMirror Review Init

Use this skill when the user asks to initialize StillMirror Review in the
current project.

Run the bundled helper, resolved through the plugin root:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" init
```

If you are working from a checkout of this repository instead of an installed
plugin, run `plugins/stillmirror-review/bin/stillmirror-review init` instead.

This creates `.stillmirror/` with local-only traces, accepted goals, allocation
rubric, evidence, snapshots, and review folders. Do not upload or transmit any
project traces.
