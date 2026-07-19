# Basis Change Impact frozen fixture

`fixture.json` is the pre-implementation conformance case for the first Basis
Change Impact vertical slice. Tests validate its internal references and its
frozen expected impact set.

The fixture is synthetic and redacted. It contains no prompts, transcripts,
local paths, private excerpts, or raw tool payloads.

Changing the expected affected or unaffected file sets requires an explicit
product-contract review; they must not be adjusted to fit implementation output.

## Author dogfood

`run_dogfood.py` replays three actual agent-generated milestone commits from the
Basis Change Impact implementation branch. For each commit it compares:

- the file names visible to ordinary Git diff;
- the allocation ledger's lack of claim-level formation chains;
- global and branch-scoped Basis Change Impact results.

Run it from a branch that contains the three milestone commits:

```sh
python3 examples/basis-change-impact/run_dogfood.py
```

`dogfood-results.json` is the verified output. In all three cases the formation
graph recovers one declared descendant absent from the ordinary diff while the
branch-scoped view contains exactly the changed linked files.

This is retrospective author dogfood, not external-user evidence. It validates
the mechanism and incremental information over diff/ledger; it does not validate
market demand, prospective capture quality, or external-person usability.
