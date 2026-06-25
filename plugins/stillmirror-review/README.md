# StillMirror Review

The review layer for agentic work.

StillMirror Review helps you review *what you actually let happen* versus *what
you meant*, by joining two spines — accepted-goal provenance and allocation
evidence. It observes:

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
plugins/stillmirror-review/bin/stillmirror-review problem set "Validate StillMirror as a review layer"
plugins/stillmirror-review/bin/stillmirror-review goals add "Maintain hook reliability"
plugins/stillmirror-review/bin/stillmirror-review goals replace "Maintain hook reliability" --with "Ship a trustworthy review layer"
plugins/stillmirror-review/bin/stillmirror-review goals retire "<goal id or statement>"
plugins/stillmirror-review/bin/stillmirror-review goals events
plugins/stillmirror-review/bin/stillmirror-review ledger --since 30d
plugins/stillmirror-review/bin/stillmirror-review correct --event <event_id> --label evaluation
plugins/stillmirror-review/bin/stillmirror-review review-due
plugins/stillmirror-review/bin/stillmirror-review review --since 30d
plugins/stillmirror-review/bin/stillmirror-review review --base origin/main
plugins/stillmirror-review/bin/stillmirror-review maintainer-review --since 90d
plugins/stillmirror-review/bin/stillmirror-review alignment record --label necessary_support
plugins/stillmirror-review/bin/stillmirror-review alignment list
```

## Maintainer review (the wedge)

`maintainer-review` is a parallel, capture-free, git-only review for open-source
maintainers — *advancing the core, or drowning in maintenance?* It needs no
install and runs on any cloned repo; its output is a committable **badge** (the
badge is the distribution), plus a report and a machine sidecar with
cross-project `canonical_counts`. Evidence, not verdict; neutral badge color. See
[docs/MAINTAINER-REVIEW.md](https://github.com/haeliotang/stillmirror-review/blob/main/docs/MAINTAINER-REVIEW.md).

## Triggers (review when it matters)

Review is triggered at **human** and **work-product** boundaries, never per agent
or per task. `review-due` reports what accumulated since your last review
(including `sessions_touched`); an opt-in SessionStart nudge
(`STILLMIRROR_SESSION_NUDGE=1`) surfaces it as one quiet line; and
`review --base <ref>` scopes a review to a branch at PR time. The review's
**Triage** section clusters a flood of multi-agent work by goal and by agent
thread and surfaces exceptions — always decomposable to receipts, never a
ranking. See [docs/TRIGGERS.md](https://github.com/haeliotang/stillmirror-review/blob/main/docs/TRIGGERS.md).

## What gets written

The plugin writes only inside the current project:

```text
.stillmirror/
  traces/
  problems/      mainline-hypothesis.json
  goals/         accepted-goals.json, goal-events.jsonl
  allocations/   allocation-ledger.json, corrections.jsonl, rubric.json
  alignment/     alignment-reviews.jsonl
  reviews/       *-project-alignment-review.md
```

The default hook capture stores sanitized event summaries, hashes, resource
types, tool names, file paths, and timestamps. It does not store raw prompts by
default. To opt in to short prompt previews, set:

```sh
export STILLMIRROR_CAPTURE_PROMPT_TEXT=1
```

Raw local traces also record the absolute working-directory path. They stay
under `.stillmirror/` and are git-ignored, never transmitted.

## AllocationEntry rubric

Every allocation entry uses one or more of these seven classes:

- `core_problem`
- `support_infrastructure`
- `evaluation`
- `packaging_distribution`
- `maintenance_debugging`
- `exploration`
- `noise` — session lifecycle/control events that carry no allocation signal

Each entry also carries a **receipt** (the matched patterns and goal tokens
behind its label) and a `review_state`. A human `correct` overrides the
classifier on every later run:

```json
{
  "allocated_to": ["support_infrastructure", "maintenance_debugging"],
  "related_goal": "hook reliability",
  "supports_mainline": "unknown",
  "confidence": 0.65,
  "review_state": "unreviewed",
  "receipt": {
    "matched_patterns": {"support_infrastructure": ["hook"], "maintenance_debugging": ["fix"]},
    "goal_signals": [{"statement": "hook reliability", "tokens": ["hook"]}],
    "auto_labels": ["support_infrastructure", "maintenance_debugging"]
  }
}
```

## Boundaries

StillMirror Review does not output drift scores, productivity scores,
objective-capture diagnoses, personality judgments, or recommendations about
what your goals should be.
