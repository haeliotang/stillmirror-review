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

## Multi-agent principle (the v0.3 reframe)

As agents multiply, humans cannot face N agents or read every subtask. That
reframes StillMirror from "a mirror you look into" to **an attention allocator
for human oversight** — it decides *where scarce human attention should go* among
a flood of agent work. That is one step from the avoid-list ("deciding what
matters" = a verdict), so the governing principle is:

> Trigger at the boundaries of human attention and work products — never at the
> boundaries of agents or tasks. Aggregate to navigate, never to judge.

**Two kinds of aggregation.** In a multi-agent world aggregation is not optional
vanity; it is the only way a human can engage at all. The line that keeps it
honest:

- *Verdict aggregation* (forbidden) collapses events into a score / grade /
  trend, destroying the evidence.
- *Triage aggregation* (necessary) collapses events into navigable clusters +
  surfaced exceptions, **always decomposable back to v0.2 receipts**. It says
  "this cluster has no goal link — you may want to look; evidence here", never
  "this cluster is bad". v0.2's receipts/coverage/correction are the precondition
  that makes safe aggregation possible.

## Roadmap (depth before breadth)

- **v0.2 — The Trustworthy Spine**: evidence receipts, correction loop, coverage
  / blind-spot honesty, goal-event log, reinforcement join, and wiring the
  mainline-hypothesis. Reframe + artifact rename.
- **v0.3 — Review ritual & triggers** *(current)*: review-due state; a
  human-boundary SessionStart nudge (opt-in) and a PR-time `--base` review;
  triage aggregation (by goal, by agent thread, surfaced exceptions) in the
  review. See [TRIGGERS.md](TRIGGERS.md).
- **v0.4 — Evidence breadth**: commit / diff / PR / issue ingestion;
  session-to-session comparison and deltas (kept out of v0.3 to avoid trend /
  verdict creep).
- **Parallel — Open-source Maintainer Review (wedge)** *(v0 shipped)*: the
  `maintainer-review` command — capture-free, git-only, landing as a committable
  **badge + report** with a canonical sidecar — plus a **composite GitHub Action**
  that auto-refreshes the badge on a dedicated orphan branch (the self-propagating
  loop), and an **authorship & accountability** view (bot / human-attested /
  human) that surfaces how much of a flood carries explicit human accountability,
  as composition, never a ranking. Distribution is designed in (the badge is the
  ad). See [MAINTAINER-REVIEW.md](MAINTAINER-REVIEW.md). *Deferred:* a Marketplace
  listing, per-PR comments, PR/issue enrichment (a flood to be triaged, not
  dumped), and an **anonymized** "State of OSS Maintenance" aggregate report.
- **v0.5 — Claude Desktop MCPB review adapter**: read `.stillmirror/` for
  reflective, non-coding review sessions.
- **v0.6 — Multi-agent budget *view***: a view on the same spine, not a pillar.
- **v1.0 — Objective provenance-lite for agentic projects.**
- **Deferred** — research / writing drift review.

## The accountability floor

Push the scarcity chain to its end. Cloud metering made tokens scarce;
multi-agent made human attention scarce; abundant on-device AI makes even
*review* automatable. At each step the scarce resource migrates toward the human
— and it bottoms out at something that is not a resource at all: **accountability,
a named human consequentially standing behind an authorization.** You cannot make
it abundant, because it is a *relation*, not a quantity; "scaling" it by
automating judgment does not scale it, it *deletes* it — leaving oversight theater
(scores, badges, auto-approvals) over an absence of responsibility.

So StillMirror's deepest discipline is to **refuse to become the reviewer** — to
stay the instrument that makes a human review faster, never the substitute that
reviews for them. The human-act gates (`alignment record`, `correct`) are the
whole point; they are named human attestations and must never be ghost-written by
an agent. As everything else becomes automatable, **human-attested provenance**
is the signal that keeps its value — the hand-signature among infinite forgeries.
This is also why the avoid-list holds: a score is the on-ramp to automated,
unaccountable judgment, so refusing scores is refusing to build that ramp.

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
