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
  Spots and Goal Provenance sections, and no drift scores or verdicts.
- `alignment record/list` writes user review records.
- redacted sample contains no private paths, raw prompts, or transcript payloads.

Boundary:

- Problem is a hypothesis.
- Allocation is evidence.
- Alignment is user review, not a system verdict.
