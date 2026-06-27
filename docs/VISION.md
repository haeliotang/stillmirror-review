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

(The v0.9 entry below refines this: the evidence substrate is *consumer-agnostic*
— a human today, a reviewer-AI tomorrow may do the reading — but the terminus
stays a **named human attestation**, and an empty judgment seat is surfaced, not
filled.)

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
- **v0.3 — Review ritual & triggers** *(shipped)*: review-due state; a
  human-boundary SessionStart nudge (opt-in) and a PR-time `--base` review;
  triage aggregation (by goal, by agent thread, surfaced exceptions) in the
  review. See [TRIGGERS.md](TRIGGERS.md).
- **v0.4 — Evidence breadth** *(shipped)*: **diff ingestion** (changed lines
  read *to classify* mixed commits by the bulk of the change — never reported as
  LOC), opt-in **PR/issue ingestion** via `gh` (merged/closed + open backlog,
  project-level), and **Review Debt** — agent work authorized but not yet stood
  behind, measured against the last human-attested review (the edge-era "budget"
  is human attention). **Non-goals, refused on principle (not deferred):** LOC /
  change-volume as a *reported metric*; PR/issue *thread content* and
  *per-responder* breakdowns (ranking risk); and session-to-session **trend /
  score deltas** — the only safe "since last review" delta is Review Debt
  (evidence counts, no trend line, no better/worse).
- **Parallel — Open-source Maintainer Review (wedge)** *(v0 shipped)*: the
  `maintainer-review` command — capture-free, git-only, landing as a committable
  **badge + report** with a canonical sidecar — plus a **composite GitHub Action**
  that auto-refreshes the badge on a dedicated orphan branch (the self-propagating
  loop), and an **authorship & accountability** view (bot / human-attested /
  human) that surfaces how much of a flood carries explicit human accountability,
  as composition, never a ranking. Distribution is designed in across **two
  channels** — a **badge** for the human glance and a name-free
  **`maintainer-summary.json`** machine endpoint a reviewer (human or AI) can
  fetch, published next to the badge — so reach is not bet on human eyeballs
  alone; opt-in **PR/issue enrichment** (via `gh`, git-only stays the default); and
  an **anonymized aggregate** (`aggregate`) — a "State of OSS Maintenance" report
  that names no project or contributor. See
  [MAINTAINER-REVIEW.md](MAINTAINER-REVIEW.md). *Deferred:* a Marketplace listing
  and per-PR comments.
- **v0.5 — Claude Desktop MCPB review adapter** *(shipped)*: a stdlib MCP server
  (`bin/stillmirror-mcp`, a thin adapter over the CLI) + an MCPB `manifest.json`,
  bringing reflective review into Claude Desktop. Three tools — `review_due`,
  `review` (evidence), `record_alignment` (the named human act). The accountability
  floor is enforced at the tool boundary: it surfaces evidence and records the
  user's own attestation, and refuses to attest on the human's behalf. See
  [MCP-ADAPTER.md](MCP-ADAPTER.md).
- **v0.6 — Multi-agent budget *view*** *(shipped)*: budget reframed from *cost
  spent* to **attention owed**. The Review Debt section maps the fleet's
  unreviewed allocation **by problem** and surfaces the threads with the most
  unattended output (where to look, not a ranking). A view on the spine, not a
  pillar. **Non-goals (refused):** token / cost capture, and any per-agent
  efficiency, quality, or "best/worst" ranking.
- **v0.7 — Consolidation & hardening** *(shipped)*: not new capability. The
  project ran StillMirror on itself; the evidence (feature ~12% vs upkeep ~82% by
  the wedge; a sprawling ~17-command surface) and Hao's attestation pointed to
  *tighten, don't expand*. So: one coherent "how it fits together" story (intent
  provenance ⋈ allocation evidence ⋈ human attestation), dead code trimmed
  (unused `init` dirs, a dead profile field), and our own attestation dogfooded
  (signed-off commits + a recorded alignment). The discipline applied to itself.
- **v0.8 — Root out the classifier: declare, don't guess** *(shipped)*. The
  weakest link since day one — keyword inference over impoverished metadata
  (61% of work "unlinked"). Pressure-tested against the multi-agent future (most
  people will hand decisions to AI or a reviewer-AI), the fix is not a *smarter
  guesser* but a move from inference to **declaration**: `focus` lets the worker
  (a human, or an agent) declare which goal the current work serves, so
  allocation becomes ground-truth (`supports_mainline: declared`), overriding the
  keyword guess. The rule classifier stays as the transparent fallback for
  *undeclared* work, and coverage reports the **declared-vs-inferred** split
  honestly. StillMirror is thereby positioned as the **auditable evidence
  substrate** — consumable by a human today or a reviewer-AI tomorrow, with the
  accountable attestation as terminus. **Non-goals:** an opaque LLM that renders
  the verdict. **Deferred:** per-agent/per-session focus (v0.8 is a global
  time-window; concurrent-agent attribution is the multi-agent extension).
- **v0.9 — Reframe for the no-human-in-the-loop future** *(shipped)*. A route
  review under the premise that most people will *not* review (abdication, or a
  reviewer-AI) found a clean split: the **substrate** (ledger, receipts,
  coverage, provenance, attestation, MCP, `focus`) is consumer-agnostic and
  AI-ready; several **interface** choices assumed a human consumer and deviated.
  v0.9 corrects by reframe, not rebuild:
  - the SessionStart nudge is now a **consumer-agnostic signal** — addressed to
    whatever attends (a human *or* a review process), with the same state
    queryable as JSON via `review-due` for automation;
  - **abdication is made visible** — an empty judgment seat (work accumulating
    with no attestation ever) is surfaced as a finding (`review-due.ever_attested`
    and a prominent Review Debt callout), not papered over;
  - the **revised mainline hypothesis**: not "keep a *human* in the judgment
    seat" but **"ensure an accountable reviewer (a human now, possibly an
    accountable AI past the moral-agent threshold) sits on auditable evidence,
    with a named human attestation as terminus — and make abdication visible
    rather than fill the empty seat."** The human narrows to the irreducible
    accountability terminus; the moment-to-moment reviewing may be a human or an
    AI consuming the same auditable substrate.
  - **v0.9.1** turns two of these from narrative into mechanism: `correct` takes
    a named `--attested-by` attester (a relabel is itself an accountable act, not
    a silent edit), and the wedge ships the machine-discoverable
    `maintainer-summary.json` endpoint alongside the badge.
- **v0.9.2 — Per-agent attribution: capture the seam we were dropping**
  *(shipped)*. An investigation (real traces + the verified hook schema) caught
  an **overclaim**: entries grouped by `session_id_hash`, but every subagent
  event folds into its parent session — "by agent thread" was really "by
  session." The fix was in capture, not concept: Claude Code exposes per-subagent
  `agent_id`/`agent_type` on subagent `PostToolUse`, and the normalizer was
  discarding them. v0.9.2 preserves that identity (`agent_id` hashed like the
  session id; `agent_type` kept as a label), carries an `agent` dimension on every
  ledger entry, and makes Review Debt and Triage **truly per-agent** (by problem,
  by session, by agent — a session is not an agent), with `agents_touched` beside
  `sessions_touched` and a **named blind spot** (same-type agents share a label;
  agent-teams `TaskCreated/Completed` carry no `agent_id`; pre-0.9.2 events have
  none). **Foundation-first by design:** the per-agent *focus declaration* half is
  **deferred** until there is real concurrent-agent capture to validate against —
  but the data model carries both `agent_type` (the declarable, stable key) and
  `agent_id` (per-invocation precision) so a future `active_focus_at(…,
  agent_type, agent_id)` resolves most-specific-first without a rebuild.
  **Non-goal:** inferring agent identity where the hook gives none — declare it or
  name the blind spot, never guess. This is the same discipline that caught the
  TaskCreated regression, applied to our own overclaim.
- **v0.9.3 — Provenance accountability: extend the floor to the root**
  *(shipped)*. The opening question: in the multi-agent era the *generative*
  setting of intent (`goals add`, eventually `problem set`) will be done by AI
  too. The accountability floor must not be removed at the root — but the answer
  is **not** a human/AI toggle that treats the two as equivalent (that erases the
  seam the tool exists to keep, and builds the "AI sets the goal → AI works → AI
  reviews → all green" ramp). Instead, lift the primitive the project already
  invented twice — the `--attested-by` attester (v0.9.1) and the wedge's
  bot/attested/human tiers — **up the authorization tree to its root**: `problem
  set` and `goals add/replace` now stamp a **named setter + accountability tier**
  (`human` / `agent`-under-a-named-principal / `autonomous`). An `autonomous`
  setting is **never an equivalent silent value**: it is `accountable: false`,
  and the review surfaces a **root empty-seat finding** (analogous to v0.9's empty
  judgment seat) — *the project's purpose has no one behind it*. Goals gain
  **propose ≠ authorize**: an autonomous `goals add` lands as `proposed` (excluded
  from `core_problem` matching), and `goals accept --attested-by` is the
  accountable promotion. **Backward compatible:** a pre-0.9.3 record with no block
  is *unmarked*, not an empty seat. **Boundary:** not a toggle; never auto-fills
  the seat; the question is always "is anyone accountable," recorded, never
  erased. The floor, walked up the tree: leaf (v0.8 `focus`), worker (v0.9.2
  `agent_id`), now **root**.
- **v0.9.4 — Assisted attestation: hide the taxonomy, keep the verdict human**
  *(shipped)*. Dogfooding the loop by hand surfaced the real adoption blocker:
  for a human, **operating a 7-label taxonomy + composing a reason is too much
  friction** — and the project's own premise (attention is scarce) means that
  friction *guarantees* the empty seat. The fix is not to automate the human away
  (that forges the floor) but to **separate the act from its articulation**: the
  labels + reasoning are clerical, machine-facing, and can be **drafted by an AI**;
  the act (a named human standing behind it) stays irreducible but becomes
  near-zero-effort — **accept / amend / reject** a draft, in plain terms, with the
  7 labels **never shown to the human** by default. Mechanism: `alignment propose
  --drafted-by` writes a *draft* (kept in a separate `proposals.jsonl`, it does
  **not** reset Review Debt or set `ever_attested`); `alignment ratify --decision
  accept|amend|reject --attested-by` is the human act — accept/amend write a real
  attestation carrying **both** `proposed_by` (the AI) and `attested_by` (the
  human), reject leaves the seat empty. StillMirror has **no LLM** and stays that
  way: the draft is authored by the *AI consumer* (the review skill, the MCP
  client — two new tools `propose_alignment`/`ratify_alignment`), never by the
  CLI. This is `propose ≠ authorize` a fourth time, now at the **terminus**.
  **Named limit:** no tool can force a human to *look* before accepting — v0.9.4
  makes draft-vs-ratified visible, reject cheap, and silence ≠ assent (a pending
  draft is an empty seat), but accept-without-looking stays possible. That residue
  is stated, not engineered away.
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
