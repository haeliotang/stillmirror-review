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

## What it exposes (3 tools)

| tool | what it does |
|---|---|
| `review_due` | read-only: unreviewed allocations, new goal events, and agent threads since the last human-attested review |
| `review` | returns the full Project Alignment Review (coverage, review debt, goal provenance, triage, allocation evidence) — **evidence, not a verdict** |
| `record_alignment` | records the **user's own** attestation — labels the user chose, named to the accountable human |

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
