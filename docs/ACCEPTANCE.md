# Acceptance

StillMirror Review is ready for initial public use when the following pass:

```sh
claude plugin validate ./plugins/stillmirror-review --strict
claude plugin validate ./.claude-plugin/marketplace.json --strict
python3 -m unittest discover -s tests -v
```

Functional gates:

- `init` creates local `.stillmirror/` state.
- hook capture is sanitized by default and does not store raw prompts.
- `ledger` produces multi-label `AllocationEntry` records, each with a `receipt`
  (the matched rubric patterns and goal tokens behind its label).
- `correct` records a human re-label; the next `ledger` run honors it
  (`review_state: "corrected"`).
- `ledger` emits a `coverage` object naming what was not captured.
- `goals add/list` records reviewed or accepted goals, and `add`/`retire`/
  `replace` append `goal_introduced`/`goal_retired`/`goal_replaced` events to
  `goals/goal-events.jsonl`.
- `problem set` writes `problems/mainline-hypothesis.json`.
- `review` emits a Markdown **Project Alignment Review** with Coverage & Blind
  Spots, Goal Provenance, and **Triage** sections, and no drift scores or
  verdicts.
- `review-due` derives `new_allocations`, `new_goal_events`, and
  `sessions_touched` since the last alignment record, and `due` flips on
  threshold.
- the SessionStart `review-due --nudge` hook is silent unless
  `STILLMIRROR_SESSION_NUDGE=1` and a review is due.
- `review --base <ref>` scopes the window to a branch's commits.
- the Triage section groups by goal (with an `unlinked` bucket) and by session,
  surfaces exceptions with `event_id`s, and carries the "surfaced ≠ judged"
  disclaimer (no agent ranking, no trends).
- `alignment record/list` writes user review records, each a named human
  attestation (`attested_by` + `human_attested`), defaulting the attester to git
  `user.name`.
- `maintainer-review` (the wedge) classifies commits git-only into a maintainer
  profile mapped to canonical classes, and writes a report, a neutral-color
  shields badge JSON, and a sidecar with `maintainer_counts` and
  `canonical_counts`; its coverage names the PR/issue/triage blind spot and it
  produces no score or verdict.
- `maintainer-review` surfaces an `authorship` split (bot / attested / human)
  with per-commit attestation tiers, as composition not a ranking, and names the
  signature-not-verified blind spot.
- `review` includes a **Review Debt** section (unreviewed allocations / goal
  events / agent threads since the last human-attested review); for multi-agent
  work it maps the unreviewed pile by problem and by thread (evidence about owed
  attention, not a ranking) and clears after a human attestation.
- `maintainer-review` reads diffs (changed lines) only to classify mixed commits
  by the bulk of the change (`reason: "diff"`); no line count / LOC is ever
  reported as a metric.
- `maintainer-review --with-pr-issues` enriches via `gh` (merged/closed + open
  backlog) and degrades gracefully to git-only when `gh` is unavailable.
- `aggregate` produces an anonymized cross-repo report that names no project or
  contributor.
- redacted sample contains no private paths, raw prompts, or transcript payloads.

Boundary:

- Problem is a hypothesis.
- Allocation is evidence.
- Alignment is user review, not a system verdict.
