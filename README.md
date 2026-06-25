# StillMirror Review

Project Drift Review for agentic work.

StillMirror Review is a Claude Code plugin that makes allocation trails visible
for user alignment review. It helps answer:

- what problem seems to be driving the project;
- where attention and agent work are actually allocated;
- whether recent allocations still match the goals the user has reviewed or accepted.

It does not decide what the goal should be.

```text
Problem is a hypothesis.
Allocation is evidence.
Alignment is user review, not a system verdict.
```

## Install from marketplace

Add this repository as a Claude Code plugin marketplace:

```sh
claude plugin marketplace add haeliotang/stillmirror-review --scope user
claude plugin install stillmirror-review@stillmirror --scope user
```

Verify the installed plugin:

```sh
claude plugin details stillmirror-review
```

Expected shape:

```text
stillmirror-review 0.1.0
  Project Drift Review for agentic work. Makes allocation trails visible for
  user review.
  Source: stillmirror-review@stillmirror

Component inventory
  Skills (4)  goals, init, ledger, review
  Hooks (6)  SessionStart, UserPromptSubmit, PostToolUse, SubagentStop,
             Stop, SessionEnd
  MCP servers (0)
```

Then run a project-level smoke test in a target repository:

```sh
cd /path/to/your/project
claude
```

Inside Claude Code, invoke the skills:

```text
/stillmirror-review:init
/stillmirror-review:goals
/stillmirror-review:ledger
/stillmirror-review:review
```

After the smoke test, the target repository should contain local review state:

```text
.stillmirror/goals/accepted-goals.json
.stillmirror/allocations/allocation-ledger.json
.stillmirror/reviews/*-project-drift-review.md
```

Make sure `.stillmirror/` is ignored by the target repository:

```sh
grep -n "^\\.stillmirror/" .gitignore
```

If you want to inspect the generated local state from the shell, use normal
filesystem checks. Do not depend on Claude's internal plugin cache paths; they
are implementation details and can change.

For local testing from a checkout:

```sh
claude --plugin-dir ./plugins/stillmirror-review
```

Then use the included skills:

```text
/stillmirror-review:init
/stillmirror-review:ledger
/stillmirror-review:review
/stillmirror-review:goals
```

## Direct CLI usage

You can also run the bundled helper directly:

```sh
plugins/stillmirror-review/bin/stillmirror-review init
plugins/stillmirror-review/bin/stillmirror-review goals add "Maintain hook reliability"
plugins/stillmirror-review/bin/stillmirror-review ledger --since 30d
plugins/stillmirror-review/bin/stillmirror-review review --since 30d
plugins/stillmirror-review/bin/stillmirror-review alignment record --label necessary_support
```

## What gets written

StillMirror Review writes local project state under:

```text
.stillmirror/
  traces/
  goals/
  allocations/
  alignment/
  reviews/
```

The default hook capture stores sanitized event summaries, hashes, resource
types, tool names, file paths, and timestamps. It does not store raw prompts by
default. Raw local traces also record the absolute working-directory path; they
stay under `.stillmirror/` and are git-ignored, never transmitted.

## Allocation rubric

Each `AllocationEntry` can use one or more labels:

- `core_problem`
- `support_infrastructure`
- `evaluation`
- `packaging_distribution`
- `maintenance_debugging`
- `exploration`
- `noise` (session lifecycle/control events with no allocation signal)

## Boundaries

StillMirror Review does not output drift scores, productivity scores,
objective-capture diagnoses, personality judgments, or recommendations about
what your goals should be.

## Development

Validate the plugin and marketplace:

```sh
claude plugin validate ./plugins/stillmirror-review --strict
claude plugin validate ./.claude-plugin/marketplace.json --strict
python3 -m unittest discover -s tests -v
```

## License

Apache-2.0.
