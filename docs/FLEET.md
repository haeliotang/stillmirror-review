# Fleet view — where your attention is owed, across producers

One human will start many projects and launch countless agents. The scarce thing
is not review *within* one project but knowing, **across all of them, which one
needs you next**. `fleet` answers that.

```sh
stillmirror-review fleet ~/projects/*
stillmirror-review fleet ~/code/stillmirror-review ~/code/wutai --json
```

## What it unifies on — the empty seat, not a debt count

Projects carry **different-resolution evidence**: a Claude Code project has the
full capture spine (tool-call level); a project built elsewhere has only its git
history (commit level). Forcing those into one "debt" number would be a lie. So
`fleet` unifies on the one signal every project can answer regardless of who or
what produced the work:

> **Is anyone accountable for the recent work, and how stale is that?**

Empty seats (no one has stood behind recent work) sort first, then the stalest
attestations, then the most owed. It is **navigation, never a ranking** — no
scores, no best/worst, no cross-project total that manufactures a verdict.

## Producer-agnostic by design

Each project is read by whatever evidence it has:

| the project… | `fleet` reads it as | the detail it shows |
|---|---|---|
| was built in Claude Code (has `.stillmirror` capture) | **capture** | unreviewed allocations since the last attestation |
| was built elsewhere (e.g. **OpenAI Codex**) — git repo, no capture | **git-only (wedge)** | commits since the last attestation (or recent window) |
| has an attestation either way | both | who stood behind it, and how long ago |
| is neither | — | "not yet under StillMirror" |

This is the wedge's whole point at fleet scale: StillMirror reviews agentic work
from **any** producer, not just Claude Code. A Codex-built project sits in the
same map as a Claude Code one — both answering the same accountability question.

## Boundaries

- **Navigation, not a ranking.** Empty-seat-first is "where to look", never
  "which project is best/worst".
- **No uniform score.** The two evidence resolutions differ; only the empty-seat
  signal is universal.
- **Local only.** It names *your own* projects (naming is the point) and is never
  transmitted. Run it on paths you control.
- **N is the caveat.** A fleet of two validates the mechanism and the
  producer-agnostic claim — not the at-scale thesis, which needs many more.
