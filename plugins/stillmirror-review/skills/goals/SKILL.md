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

Prefer the helper commands instead of editing JSON by hand:

```sh
plugins/stillmirror-review/bin/stillmirror-review goals add "Maintain hook reliability"
plugins/stillmirror-review/bin/stillmirror-review goals list
```

AcceptedGoal only means the user has reviewed or accepted a goal in this
project context. It is not a statement about the user's true value function.
