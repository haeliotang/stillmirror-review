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
- `correct` records a re-label as a named accountable act (`attested_by`,
  defaulting to git `user.name`); the next `ledger` run honors it
  (`review_state: "corrected"`).
- `maintainer-review` writes a name-free aggregate `maintainer-summary.json`
  (no per-commit entries/authors); the GitHub Action publishes it next to the
  badge as a machine-discoverable evidence endpoint.
- `ledger` emits a `coverage` object naming what was not captured.
- `goals add/list` records reviewed or accepted goals, and `add`/`retire`/
  `replace` append `goal_introduced`/`goal_retired`/`goal_replaced` events to
  `goals/goal-events.jsonl`.
- `problem set` writes `problems/mainline-hypothesis.json`.
- `problem set` and `goals add/replace` stamp an `accountability` block
  (`set_by` + `tier` + `accountable`) via `--attested-by` + `--tier
  {human,agent,autonomous}`, defaulting to `human` (git `user.name`) so existing
  use is unchanged. `--tier agent` requires a named principal; `--tier
  autonomous` is `accountable: false`.
- an `autonomous` `problem set` makes `review` surface a **root empty-seat
  finding** ("the project's root problem has no accountable party") and sets
  `coverage.root_accountable: false`; a pre-0.9.3 record with no block produces
  **no** finding (`root_accountable: null` — unmarked, not an empty seat).
- an `autonomous` `goals add` lands as `review_state: "proposed"` (logged as
  `goal_proposed`), is excluded from `core_problem` matching until accepted, and
  `goals accept <ref> --attested-by` promotes it to `accepted` (logged as
  `goal_accepted`); `accept` refuses an `autonomous` tier.
- `focus "<goal>"` declares current intent; events in the focus window get
  ground-truth linkage (`supports_mainline: "declared"`, `core_problem`,
  `receipt.reason: "declared"`) overriding the keyword guess, and `focus --clear`
  ends it. `focus` accepts only an existing active accepted goal and never
  silently creates a human-accepted goal. `ledger` coverage reports the
  declared-vs-inferred split.
- named alignment attestations carry `canonicalization_version` and a
  `subject_digest` over stable problem, goal, goal-event, ledger, and formation
  content. Volatile generation timestamps do not change the digest; actual
  captured-content changes mark the prior attestation stale and make review due.
- `formation record` atomically appends one explicit decision claim and all its
  declared goal/file edges to `formation/receipts.jsonl`. The basis must be an
  existing active accepted goal; artifacts must be files inside the current Git
  repository. Invalid input writes nothing, and repeated `--request-id` values
  are idempotent or rejected on content conflict.
- `goals retire/replace` deterministically traverses declared formation edges
  only and appends one idempotent invalidation event. Exact affected files become
  `needs_revalidation`; unlinked files and inferred edges do not.
- `impact show --base <ref>` scopes impact to linked files changed in
  `merge-base(<ref>, HEAD)..HEAD`. The Project Alignment Review includes the
  goal → explicit claim → file chain, evidence class, and coverage boundary.
- `impact revalidate <impact-id> --decision retained|updated|retired
  --attested-by <human>` records a named item-level attestation and clears only
  that item. A project-wide alignment attestation cannot clear impact debt.
- every impact surface says stale basis, not a correctness verdict; it never
  labels an affected artifact incorrect or wrong.
- `review` emits a Markdown **Project Alignment Review** with Coverage & Blind
  Spots, Goal Provenance, and **Triage** sections, and no drift scores or
  verdicts.
- `review-due` derives `new_allocations`, `new_goal_events`,
  `sessions_touched`, and `agents_touched` (distinct subagents, a separate number
  from sessions) since the last alignment record, and `due` flips on threshold.
- hook capture preserves per-subagent identity when present: `agent_id` (hashed
  to `agent_id_hash`) and `agent_type` (a clear label) from subagent
  `PostToolUse`/`SubagentStop`; main-agent events carry neither. Each ledger
  entry carries an `agent` dimension, and `coverage.agents_observed` counts
  distinct subagents with a named blind spot (same-type agents share a label;
  agent-teams task events carry no `agent_id`; pre-0.9.2 and main-agent events
  group under the top-level session — a session is not an agent).
- `review` Triage and Review Debt attribute **by problem, by session, and by
  agent** (real subagent identity where present), never labeling a session an
  agent and never ranking agents.
- the SessionStart `review-due --nudge` hook is silent unless
  `STILLMIRROR_SESSION_NUDGE=1` and a review is due; its message is
  consumer-agnostic (addressed to a human *or* a review process).
- `review-due` reports `ever_attested`, and `review` surfaces an empty judgment
  seat (work accumulating with no attestation) as a prominent finding.
- `review --base <ref>` scopes the window to a branch's commits.
- the Triage section groups by goal (with an `unlinked` bucket) and by session,
  surfaces exceptions with `event_id`s, and carries the "surfaced ≠ judged"
  disclaimer (no agent ranking, no trends).
- `alignment record/list` writes user review records, each a named human
  attestation (`attested_by` + `human_attested`), defaulting the attester to git
  `user.name`.
- assisted attestation: `alignment propose --drafted-by` writes a **draft** to a
  separate `alignment/proposals.jsonl` that is **not** an attestation — it does
  not reset Review Debt or set `ever_attested`, and `review-due.pending_proposal`
  + the review surface it as an empty seat with a draft awaiting ratification.
  `alignment ratify --decision accept|amend|reject --attested-by` is the human
  act: accept/amend write a real attestation carrying both `proposed_by` (AI) and
  `attested_by` (human) and reset the debt; reject leaves the seat empty. `ratify`
  refuses without a named human, and a draft refuses without `--drafted-by`.
- the MCP adapter exposes `propose_alignment` and `ratify_alignment` alongside
  `record_alignment`; `ratify_alignment` refuses to ratify without a named human.
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
- `fleet <path>…` produces a producer-agnostic cross-project view that unifies on
  the **empty seat** (is anyone accountable for recent work, and how stale),
  reading capture state where present and falling back to **git-only** otherwise
  (so a project built outside Claude Code still appears); it sorts empty seats
  first, names the user's own projects (local only), and is navigation — no
  scores, no ranking, no cross-project totals. `--json` carries per-project
  `source`, `accountable`, `staleness_days`, `owed`, and `pending_proposal`.
- redacted sample contains no private paths, raw prompts, or transcript payloads.
- the frozen Basis Change Impact fixture resolves to exactly three affected and
  one unaffected file. `run_dogfood.py` reproduces `dogfood-results.json` over
  three actual agent-generated milestone commits; all case gates pass, while the
  artifact explicitly names retrospective author-only and external-validity
  limits.

Boundary:

- Problem is a hypothesis.
- Allocation is evidence.
- Alignment is user review, not a system verdict.
