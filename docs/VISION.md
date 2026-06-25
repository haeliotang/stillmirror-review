# StillMirror Review — Vision & Roadmap

> A provenance tool should make its own direction visible. This is that record.

## What StillMirror is

StillMirror Review is **the review layer for agentic work**. As agents get
better at *doing*, the scarce thing becomes the human's ability to review *what
they actually authorized to happen*. StillMirror does not help an agent do more;
it helps a person review what they let happen.

It tracks three things and joins them for human review:

- **what goals were accepted** (authorization provenance),
- **where work was allocated** (evidence),
- **where human alignment review is needed** (the join).

```text
Problem is a hypothesis.
Allocation is evidence.
Alignment is user review, not a system verdict.
```

## The reframe: provenance, not analytics

The truthful core is the **join of two spines**:

- **Goal events** — what you meant (introduced / reinforced / replaced / retired).
- **Allocation evidence** — what the agent did (hook events + git, classified).

"What I authorized to happen" ≠ "where tool-events landed." Allocation is
*evidence*, demoted from the headline; the product noun is **alignment /
authorization provenance**. The allocation classifier is a lossy proxy — it sees
tool names, file basenames, command tokens, and commit subjects, never intent,
effort, or impact. So StillMirror's job is not to *measure* allocation but to
give the human an honest, auditable, correctable prompt for review.

This is why the core mechanics are:

- **Evidence receipts** — every entry says *why* it got its label.
- **Correction loop** — the human relabels; the ledger honors it thereafter.
- **Coverage / blind spots** — the artifact advertises what it could not see.
- **Goal-event log** — low-noise provenance of *decisions*, which anchors the
  `core_problem` classification the ledger cannot do alone.

A still mirror reflects faithfully — but only what is in front of it. StillMirror
names its own blind spots so no one mistakes a partial reflection for the whole.

## Naming

The product is **StillMirror Review**; the generated artifact is the **Project
Alignment Review** (not "Drift Review"). "Drift" presupposes a true course you
departed from — a judgment the product explicitly refuses to make. The word
survives where it belongs: `operational_drift` is one *user-selectable*
alignment label, a conclusion the human may reach, never the system's frame.

## Shape: one spine + one wedge

- **Spine** — capture → allocation-evidence ledger (with receipts + correction)
  ⋈ goal-event log → honest periodic alignment review.
- **Wedge** — open-source maintainer review, running on public git/PR/issue with
  no capture needed; a concrete audience and feedback loop for adoption.

Everything else is a *view* on the spine or a later adapter, never a new pillar.
Resist roadmap-as-menu.

## Roadmap (depth before breadth)

- **v0.2 — The Trustworthy Spine** *(current)*: evidence receipts, correction
  loop, coverage / blind-spot honesty, goal-event log, reinforcement join, and
  wiring the mainline-hypothesis. Reframe + artifact rename.
- **v0.3 — Review ritual & triggers**: *when and where review happens* (PR-time,
  weekly cron, end-of-session "review due" signal). A review layer is worthless
  if review never happens — this is the highest-leverage unsolved problem.
- **v0.4 — Evidence breadth**: commit / diff / PR / issue ingestion;
  session-to-session comparison.
- **Parallel — Open-source Maintainer Review (wedge)**: no capture required;
  start anytime, decoupled from the spine.
- **v0.5 — Claude Desktop MCPB review adapter**: read `.stillmirror/` for
  reflective, non-coding review sessions.
- **v0.6 — Multi-agent budget *view***: a view on the same spine, not a pillar.
- **v1.0 — Objective provenance-lite for agentic projects.**
- **Deferred** — research / writing drift review.

## What StillMirror will not do

No personality analysis. No productivity score. No AI strategy advisor. No
full-chat mirror. No "what you should do" planner. No 3D visualization as a core
selling point.

**Named gravity.** Two roadmap steps pull toward this line and need active design
effort to resist:

- Longitudinal aggregation (v0.3+) manufactures verdict-feel even when no score
  is computed — periodic reviews must *show uncertainty and require correction*,
  never assert trends.
- Multi-agent views (v0.6) drift toward cost / efficiency reports — keep the
  question "which problems did my agent budget serve?", not "what did it cost?".
