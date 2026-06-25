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

Goals have a lifecycle, recorded as an append-only provenance log in
`.stillmirror/goals/goal-events.jsonl` (introduced / reinforced / replaced /
retired). Use the lifecycle commands so the log stays truthful:

```sh
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" goals retire "<goal id or statement>"
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" goals replace "<old goal>" --with "<new goal>"
"${CLAUDE_PLUGIN_ROOT}/bin/stillmirror-review" goals events
```

If you are working from a checkout of this repository instead of an installed
plugin, use `plugins/stillmirror-review/bin/stillmirror-review` as the command
prefix instead.

AcceptedGoal only means the user has reviewed or accepted a goal in this
project context. It is not a statement about the user's true value function.
StillMirror records *when* a goal entered, was reinforced, replaced, or retired;
it never judges whether the goal itself is good.
