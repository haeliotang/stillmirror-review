# Maintainer Review (the wedge)

A capture-free review of a repository's recent work, for open-source
maintainers. It answers one recurring question — *is this project advancing its
core, or drowning in maintenance?* — from `git` alone. No plugin install, no hook
capture: run it on any repo you have cloned.

It is the **wedge**: a parallel adoption channel, decoupled from the
capture-based spine. Its distribution is designed in — the output is a **badge**
you commit to your README, so every repo visitor sees it.

## Run it

```sh
stillmirror-review maintainer-review --since 90d
# scope to a branch (PR-time):
stillmirror-review maintainer-review --base origin/main
# write the committable artifacts somewhere tracked by git:
stillmirror-review maintainer-review --out-dir docs/maintenance
```

It writes three artifacts to `--out-dir` (default `.stillmirror/reviews`, which
is git-ignored — point `--out-dir` at a committed directory to publish the
badge):

- `<date>-maintainer-review.md` — the human report.
- `maintainer-badge.json` — a [shields.io endpoint](https://shields.io/endpoint)
  badge (so the badge updates when you regenerate and commit it).
- `maintainer-review.json` — a machine sidecar with per-commit labels,
  `maintainer_counts`, and **`canonical_counts`** (stable across projects).

## The badge

The badge answers the maintainer's one question in a glance — advancing the core
vs upkeep — as a neutral split (`other` is excluded, not folded into upkeep). The
command prints a paste-ready static badge, e.g.:

```markdown
![StillMirror](https://img.shields.io/badge/work-feature_40%25_%C2%B7_upkeep_45%25-blue)
```

For a live badge that updates from a committed `maintainer-badge.json`:

```markdown
![StillMirror](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPO/main/docs/maintenance/maintainer-badge.json)
```

The badge color is **fixed-neutral by design** — it shows the mix, never a grade.

### Two channels: a human glance, a machine endpoint

Distribution is not bet on human eyeballs alone. Each run also writes a
**`maintainer-summary.json`** — an aggregate, **name-free** evidence summary
(counts, authorship tiers, coverage; no per-commit authors or subjects). The
GitHub Action publishes it next to the badge, so a reviewer — human *or* a
review-AI — can fetch a stable endpoint:

```text
https://raw.githubusercontent.com/OWNER/REPO/stillmirror-badges/maintainer-summary.json
```

The **badge is the human glance**; the **summary is the machine-discoverable
endpoint**. The full `maintainer-review.json` (with per-commit detail) stays
local.

## Labels (a profile over the canonical rubric)

The surface speaks the maintainer's vocabulary; each label maps to a canonical
StillMirror class underneath (so a future anonymized aggregate report is
possible):

| maintainer label | canonical |
|---|---|
| `feature` | `core_problem` |
| `bug_fixing` | `maintenance_debugging` |
| `release_packaging` | `packaging_distribution` |
| `infra` | `support_infrastructure` |
| `docs` | `packaging_distribution` |
| `triage_responding` | `evaluation` |
| `other` | `exploration` |

Classification prefers, in order: the conventional-commit prefix (`feat:`,
`fix:`, `chore:`, `docs:`, …); then the **changed file paths** — what actually
changed, which is more truthful than the subject's claim and agnostic to whoever
(human or agent) wrote the message (e.g. a commit touching only `docs/` → docs,
only `.github/` → infra); then, for commits that span categories, the **bulk of
the diff** by changed lines (e.g. 1 line of code + 200 of docs → docs). Diffs are
read *to classify* — the line counts are used and discarded, **never reported as
a metric** (no LOC). Genuinely ambiguous commits (a code change with a vague
subject) stay `other` rather than being force-fit.

## Authorship & accountability

As agents make contributions cheap and abundant, the scarce signal is no longer
*how much* was produced but *how much carries a human's explicit accountability*.
The report and sidecar split commits into three tiers:

| tier | meaning |
|---|---|
| `bot` | authored by a bot (`*[bot]`, Dependabot, CI bots, …) — unaccountable by default |
| `attested` | a human who left an explicit marker: a `Signed-off-by` trailer or a signature |
| `human` | a human author with only implicit attestation |

This is shown as **composition, not a contributor ranking** — no leaderboard, no
per-person score. Signatures are *detected*, not cryptographically verified here
(there are no public keys). The point is the same one StillMirror makes
everywhere: in a flood of automatable output, a named human standing behind a
change is the signal that keeps its value — so a StillMirror **alignment record**
is itself a named human attestation (`alignment record --attested-by "<name>"`)
and must never be ghost-written by an agent.

## Optional: PR/issue enrichment

`triage_responding` is undercounted because it lives in pull-request and issue
threads, not commits. Opt in to fill part of that blind spot via the `gh` CLI:

```sh
stillmirror-review maintainer-review --since 90d --with-pr-issues
```

It adds merged-PR and closed-issue counts for the window. It **degrades
gracefully** — if `gh` is missing, unauthenticated, or the repo is not on GitHub,
the wedge stays git-only and the report says so. The badge stays commit-based;
PR/issue counts are reported as separate evidence, never folded into the
distribution.

## Aggregate across repos (anonymized)

Run `maintainer-review` on several repos, then aggregate the sidecars into an
**anonymized** "State of OSS Maintenance" report — distributions only, naming no
project and no contributor:

```sh
stillmirror-review aggregate path/to/sidecars/ another/sidecar.json --out-dir agg
```

It reports medians (feature/upkeep, bot/human-attested) and totals across repos.
This is the only honest way to make a flood of repos legible without ranking or
exposing anyone — the demand-gen artifact that names no one.

## What it does not do (values boundary)

- **Evidence, not verdict.** No score, no grade, no "you're drowning" language.
- **Maintainer-pull only.** It reads the local/cloned repo; it never fetches or
  comments on a repo unsolicited.
- **Honest about its blind spot.** It reads commit *subjects* only — it cannot
  see pull-request / issue triage, review discussion, or the effort behind a
  commit. `triage_responding` is undercounted; the report says so.
- Any future cross-project aggregate report must be anonymized.

## Automate it (GitHub Action)

A composite Action keeps the badge live with no manual work — the loop that makes
the badge actually self-propagating. Add one workflow to your repo:

```yaml
# .github/workflows/stillmirror-badge.yml
name: StillMirror badge
on:
  schedule: [{ cron: "0 9 * * 1" }]   # weekly
  workflow_dispatch: {}
permissions:
  contents: write                      # only to write the badge branch
jobs:
  badge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }       # full history for the review window
      - uses: haeliotang/stillmirror-review/.github/actions/maintainer-review@stillmirror-review--v0.9.1
        with:
          since: "90d"
          publish-badge: "true"
```

The Action writes `maintainer-badge.json` to a dedicated **orphan branch**
(`stillmirror-badges` by default) using the built-in `GITHUB_TOKEN` — your `main`
history stays clean, and an unchanged badge produces no commit. Then point your
README at the live endpoint badge:

```markdown
![StillMirror](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPO/stillmirror-badges/maintainer-badge.json)
```

**Inputs:** `since` (default `90d`), `base` (scope to a branch for PR runs),
`badge-branch` (default `stillmirror-badges`), `publish-badge` (`true`/`false`),
`out-dir`.

For a PR-scoped review, run the Action with `base: origin/${{ github.base_ref }}`
and `publish-badge: "false"` — it writes a **job summary only**, never a comment
on the contributor's PR. (A published GitHub Marketplace listing is on the
roadmap; see [VISION.md](VISION.md).)
