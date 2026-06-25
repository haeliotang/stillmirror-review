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
- `ledger` produces multi-label `AllocationEntry` records.
- `goals add/list` records reviewed or accepted goals.
- `review` emits a Markdown Project Drift Review without drift scores.
- `alignment record/list` writes user review records.
- redacted sample contains no private paths, raw prompts, or transcript payloads.

Boundary:

- Problem is a hypothesis.
- Allocation is evidence.
- Alignment is user review, not a system verdict.
