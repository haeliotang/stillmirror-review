# StillMirror Review

Project Drift Review for agentic work.

StillMirror Review observes:

- what problem seems to be driving the project;
- where attention and agent budget are actually allocated;
- whether recent allocations still match the goals the user has reviewed or accepted.

It does not decide what the goal should be.

```text
Problem 是假设，Allocation 是证据，Alignment 是用户审查，不是系统判决。
```

## Install

From the public marketplace:

```sh
claude plugin marketplace add haeliotang/stillmirror-review --scope user
claude plugin install stillmirror-review@stillmirror --scope user
```

For local development from this repository root:

```sh
claude --plugin-dir ./plugins/stillmirror-review
/reload-plugins
```

Then use the included skills:

```text
/stillmirror-review:init
/stillmirror-review:ledger
/stillmirror-review:review
/stillmirror-review:goals
```

You can also run the bundled scripts directly:

```sh
plugins/stillmirror-review/bin/stillmirror-review init
plugins/stillmirror-review/bin/stillmirror-review goals add "Maintain hook reliability"
plugins/stillmirror-review/bin/stillmirror-review goals list
plugins/stillmirror-review/bin/stillmirror-review ledger --since 30d
plugins/stillmirror-review/bin/stillmirror-review review --since 30d
plugins/stillmirror-review/bin/stillmirror-review alignment record --label necessary_support
plugins/stillmirror-review/bin/stillmirror-review alignment list
```

## What gets written

The plugin writes only inside the current project:

```text
.stillmirror/
  traces/
  runs/
  problems/
  goals/
  allocations/
  alignment/
  evidence/
  snapshots/
  reviews/
```

The default hook capture stores sanitized event summaries, hashes, resource
types, tool names, file paths, and timestamps. It does not store raw prompts by
default. To opt in to short prompt previews, set:

```sh
export STILLMIRROR_CAPTURE_PROMPT_TEXT=1
```

## AllocationEntry rubric

Every allocation entry uses one or more of these six classes:

- `core_problem`
- `support_infrastructure`
- `evaluation`
- `packaging_distribution`
- `maintenance_debugging`
- `exploration`

Example:

```json
{
  "allocated_to": ["support_infrastructure", "maintenance_debugging"],
  "related_goal": "hook reliability",
  "supports_mainline": "unknown",
  "confidence": 0.68
}
```

## Boundaries

StillMirror Review does not output drift scores, productivity scores,
objective-capture diagnoses, personality judgments, or recommendations about
what your goals should be.
