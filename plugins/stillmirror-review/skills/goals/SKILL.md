---
name: stillmirror-review:goals
description: Review or edit accepted project goals used by StillMirror Review.
---

# StillMirror Accepted Goals

Use this skill when the user asks to inspect, add, or update accepted goals for
StillMirror Review.

Accepted goals live in:

```text
.stillmirror/goals/accepted-goals.json
```

Prefer the helper commands instead of editing JSON by hand. Resolve the helper
through the plugin root:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" goals add "Maintain hook reliability"
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" goals list
```

If you are working from a checkout of this repository instead of an installed
plugin, use `plugins/stillmirror-review/bin/stillmirror-review` as the command
prefix instead.

AcceptedGoal only means the user has reviewed or accepted a goal in this
project context. It is not a statement about the user's true value function.
