#!/usr/bin/env bash
# Publish a single badge JSON to a dedicated orphan branch, idempotently, without
# touching the caller's working tree. Generated artifacts (the badge) are kept
# separate from authored history; an unchanged badge produces no commit.
#
# Uses a git worktree of the *current* repo (not a fresh clone) so it inherits
# whatever auth the repo already has — e.g. the token actions/checkout injects as
# an http.extraheader, which a fresh clone would not carry.
#
# Usage: publish-badge.sh <badge-file> [branch] [remote]
set -euo pipefail

BADGE_FILE="${1:?usage: publish-badge.sh <badge-file> [branch] [remote]}"
BRANCH="${2:-stillmirror-badges}"
REMOTE="${3:-origin}"
BADGE_NAME="maintainer-badge.json"

if [ ! -f "$BADGE_FILE" ]; then
  echo "publish-badge: badge file not found: $BADGE_FILE" >&2
  exit 1
fi
# Resolve to an absolute path before we work inside the worktree.
ABS_BADGE="$(cd "$(dirname "$BADGE_FILE")" && pwd)/$(basename "$BADGE_FILE")"

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
if git -C "$WORK" diff --cached --quiet; then
  echo "publish-badge: badge unchanged; nothing to publish"
  exit 0
fi

git -C "$WORK" \
  -c user.email="actions@users.noreply.github.com" \
  -c user.name="StillMirror Action" \
  commit -q -m "Update maintainer badge"
git -C "$WORK" push --quiet "$REMOTE" "HEAD:$BRANCH"
echo "publish-badge: published to $BRANCH"
