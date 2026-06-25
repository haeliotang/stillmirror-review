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

The command prints a paste-ready static badge, e.g.:

```markdown
![StillMirror](https://img.shields.io/badge/work-feature_40%25_%C2%B7_fixes_30%25-blue)
```

For a live badge that updates from a committed `maintainer-badge.json`:

```markdown
![StillMirror](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPO/main/docs/maintenance/maintainer-badge.json)
```

The badge color is **fixed-neutral by design** — it shows the mix, never a grade.

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

Classification uses the conventional-commit prefix (`feat:`, `fix:`, `chore:`,
`docs:`, …) when present, else whole-word keywords on the commit subject.

## What it does not do (values boundary)

- **Evidence, not verdict.** No score, no grade, no "you're drowning" language.
- **Maintainer-pull only.** It reads the local/cloned repo; it never fetches or
  comments on a repo unsolicited.
- **Honest about its blind spot.** It reads commit *subjects* only — it cannot
  see pull-request / issue triage, review discussion, or the effort behind a
  commit. `triage_responding` is undercounted; the report says so.
- Any future cross-project aggregate report must be anonymized.

## Recipes

A `pre-push` hook or GitHub Action can regenerate the badge — see
[TRIGGERS.md](TRIGGERS.md) for the same `--base` pattern. A dedicated GitHub
Action wrapper is on the roadmap (see [VISION.md](VISION.md)).
