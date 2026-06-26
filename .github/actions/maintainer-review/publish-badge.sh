#!/usr/bin/env bash
# Publish the badge (and any extra artifacts, e.g. a machine evidence summary) to
# a dedicated orphan branch, idempotently, without touching the caller's working
# tree. Generated artifacts are kept separate from authored history; unchanged
# content produces no commit.
#
# Uses a git worktree of the *current* repo (not a fresh clone) so it inherits
# whatever auth the repo already has — e.g. the token actions/checkout injects as
# an http.extraheader, which a fresh clone would not carry.
#
# Usage: publish-badge.sh <badge-file> [branch] [remote] [extra-file...]
set -euo pipefail

BADGE_FILE="${1:?usage: publish-badge.sh <badge-file> [branch] [remote] [extra-file...]}"
BRANCH="${2:-stillmirror-badges}"
REMOTE="${3:-origin}"
EXTRA=("${@:4}")
# The badge always lands under this canonical name (the shields endpoint URL
# depends on it); extra artifacts keep their own basename.
BADGE_NAME="maintainer-badge.json"

abspath() { (cd "$(dirname "$1")" && printf '%s/%s\n' "$(pwd)" "$(basename "$1")"); }

if [ ! -f "$BADGE_FILE" ]; then
  echo "publish-badge: badge file not found: $BADGE_FILE" >&2
  exit 1
fi
ABS_BADGE="$(abspath "$BADGE_FILE")"
EXTRA_ABS=()
for extra in ${EXTRA[@]+"${EXTRA[@]}"}; do
  if [ -f "$extra" ]; then
    EXTRA_ABS+=("$(abspath "$extra")")
  else
    echo "publish-badge: skipping missing $extra" >&2
  fi
done

TMP="$(mktemp -d)"
WORK="$TMP/wt"
cleanup() { git worktree remove --force "$WORK" 2>/dev/null || true; rm -rf "$TMP"; }
trap cleanup EXIT

if git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  git fetch --quiet "$REMOTE" "$BRANCH"
  git worktree add --quiet --detach "$WORK" FETCH_HEAD
else
  git worktree add --quiet --detach "$WORK"
  git -C "$WORK" checkout --quiet --orphan "$BRANCH"
  git -C "$WORK" rm -rfq . 2>/dev/null || true
fi

cp "$ABS_BADGE" "$WORK/$BADGE_NAME"
git -C "$WORK" add "$BADGE_NAME"
for extra in ${EXTRA_ABS[@]+"${EXTRA_ABS[@]}"}; do
  cp "$extra" "$WORK/$(basename "$extra")"
  git -C "$WORK" add "$(basename "$extra")"
done
if git -C "$WORK" diff --cached --quiet; then
  echo "publish-badge: unchanged; nothing to publish"
  exit 0
fi

git -C "$WORK" \
  -c user.email="actions@users.noreply.github.com" \
  -c user.name="StillMirror Action" \
  commit -q -m "Update maintainer badge + evidence summary"
git -C "$WORK" push --quiet "$REMOTE" "HEAD:$BRANCH"
echo "publish-badge: published $((1 + ${#EXTRA_ABS[@]})) artifact(s) to $BRANCH"
