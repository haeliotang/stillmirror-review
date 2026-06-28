# Claude Desktop review adapter (MCP / MCPB)

A small MCP server (`bin/stillmirror-mcp`) that brings StillMirror's review into
**Claude Desktop** for reflective, non-coding review. You can ask, in plain
conversation:

- *"What needs my review in this project?"*
- *"Review the last 30 days."*
- *"Record that I see this as necessary support."*

It is a **thin adapter over the CLI** — it shells out to `stillmirror-review`,
so it inherits all of its logic and its discipline. Stdlib-only JSON-RPC over
stdio; no new dependencies.

## What it exposes (6 tools)

| tool | what it does |
|---|---|
| `review_due` | read-only: unreviewed allocations, new goal events, top-level sessions and distinct subagents, and whether a drafted attestation awaits ratification, since the last human-attested review |
| `review` | returns the full Project Alignment Review (coverage, review debt, goal provenance, triage, allocation evidence) — **evidence, not a verdict** |
| `record_alignment` | records the **user's own** attestation — labels the user chose, named to the accountable human |
| `propose_alignment` | the assistant **drafts** an attestation (labels + plain note) for the user to ratify — a draft, **not** an attestation; the seat stays empty until ratified |
| `ratify_alignment` | records the user's **accept / amend / reject** of a draft — the irreducible human act; accept/amend carry both `proposed_by` (assistant) and `attested_by` (user); reject leaves the seat empty |
| `fleet` | cross-project overseer view — where attention is owed across the user's projects (empty seats, staleness); producer-agnostic, navigation not a ranking |

## Two surfaces, one server

The same server runs in two places:

- **Claude Code** — bundled by the plugin (`mcpServers` in `plugin.json`), so
  installing the plugin auto-registers it; the six tools sit alongside the
  plugin's skills + hooks. Confirm with `/mcp` or `claude plugin details
  stillmirror-review` (`MCP servers (1)`).
- **Claude Desktop** — packaged from the same `manifest.json` via `mcpb pack .`.

Same code, same discipline, two entry points.

### Assisted attestation — draft, then ask in plain terms

The friction of operating a 7-label taxonomy is what makes a human abdicate. So
the assistant **drafts** the labels + reasoning (`propose_alignment`), then asks
the user a plain-language question — *does this look right, is something off, or
can't you tell?* — **never showing the label list** — and records their decision
with `ratify_alignment`. The labels are the draft's machine vocabulary; the user's
act is the plain accept/amend/reject. A draft is not an attestation, and the
assistant must never ratify on the user's behalf.

## The values line, enforced at the tool boundary

This adapter is the place the accountability floor is most tempting to cross — a
chat assistant could just *read the evidence and pronounce the verdict*. It must
not. So:

- `review` returns evidence and its tool contract tells the assistant to present
  it as evidence, never to summarize it as a conclusion ("the project is
  drifting").
- `record_alignment` **refuses** to run without an explicit `attested_by` and the
  user's own `labels`. The assistant must not choose the judgment or attest on
  the human's behalf — it is a conduit for a named human act, not a substitute
  for it.

## Install into Claude Desktop (MCPB)

The plugin directory doubles as an MCP bundle: `manifest.json` (Desktop) lives
alongside `.claude-plugin/plugin.json` (Claude Code) — same code, two surfaces.

Package and load it with the `mcpb` tooling, then add the resulting bundle in
Claude Desktop's extensions/MCP settings:

```sh
# from plugins/stillmirror-review/
mcpb pack .         # produces a .mcpb bundle from manifest.json + bin/
```

Requires `python3` on the machine running Claude Desktop (the server is a Python
script). It operates on whatever `project_path` you name in the conversation.

> Note: the MCP protocol is exercised by this repo's tests (initialize /
> tools/list / tools/call over stdio), but **loading inside Claude Desktop is the
> one step verified by you** — confirm the bundle appears and the tools respond.
