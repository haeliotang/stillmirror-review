# Triggers & cadence

A review layer is worthless if review never happens. StillMirror triggers review
at the boundaries of **human attention** and **work products** — never at the
boundaries of agents or tasks (those do not scale: you cannot field one ping per
agent). One human return surfaces one digest, no matter how many agents ran.

## Is a review due?

`review-due` derives, with no persisted state, what has accumulated since your
last recorded alignment review:

```sh
stillmirror-review review-due
```

```json
{
  "due": true,
  "threshold": 20,
  "last_reviewed_at": "2026-06-20T10:00:00Z",
  "new_allocations": 42,
  "new_goal_events": 1,
  "sessions_touched": 7,
  "ever_attested": true
}
```

`sessions_touched` is the multi-agent number: how many distinct agent threads ran
since you last looked. The clock resets when you `alignment record`.
`ever_attested` is `false` when **no one has stood behind this work yet** — an
empty judgment seat, surfaced rather than papered over (a v0.9 abdication signal).

## SessionStart nudge (re-engagement boundary)

A second SessionStart hook can emit a single quiet line when a review is due. It
is **off by default** and silent unless both conditions hold: you opted in, and a
review is actually due.

```sh
export STILLMIRROR_SESSION_NUDGE=1        # opt in (otherwise silent)
export STILLMIRROR_NUDGE_THRESHOLD=20     # new allocations before nudging (default 20)
```

When due, the hook adds one line of `additionalContext` at session start. The
message is **consumer-agnostic** — addressed to whatever attends, a human *or* a
review process, never assuming a human is in the loop:

```text
StillMirror: 42 allocation(s) across 7 thread(s) and 1 goal event(s) are
unattested since the last attestation. No one has stood behind this work yet. A
reviewer — you or a review process — should attend; nothing is settled until
someone accountable stands behind it. Run /stillmirror-review:review.
```

This keeps the v0.2 principle that hooks stay silent by default; the nudge never
interrupts work mid-flight. The same state is queryable as JSON via `review-due`
for automation.

## PR-time review (work-product boundary)

A pull request is a natural "authorize this to leave the building" checkpoint, and
in a multi-agent world it aggregates many agents' work into one reviewable
product. Scope a review to a branch's work with `--base`:

```sh
stillmirror-review review --base origin/main
```

### Recipe: pre-push git hook

`.git/hooks/pre-push` (make it executable):

```sh
#!/usr/bin/env sh
stillmirror-review review --base origin/main >/dev/null
echo "StillMirror alignment review written to .stillmirror/reviews/"
```

### Recipe: GitHub Actions

```yaml
- name: StillMirror alignment review
  run: |
    python3 plugins/stillmirror-review/bin/stillmirror-review review --base origin/${{ github.base_ref }}
    cat .stillmirror/reviews/*-project-alignment-review.md >> "$GITHUB_STEP_SUMMARY"
```

## Periodic cadence (recipe, not a daemon)

StillMirror ships no scheduler. Wire a weekly review with cron or the Claude Code
schedule mechanism:

```cron
0 9 * * 1  cd /path/to/project && stillmirror-review review --since 7d
```

Periodic reviews must show uncertainty and invite correction, never assert a
trend — see the Coverage & Triage sections of the generated review.
