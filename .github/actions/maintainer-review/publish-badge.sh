#!/usr/bin/env bash
# Publish a single badge JSON to a dedicated orphan branch, idempotently, without
# ever touching the caller's working tree. Generated artifacts (the badge) are
# kept separate from authored history; an unchanged badge produces no commit.
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

# Resolve the remote URL from the caller's repo (token-authed in CI; a local
# path in tests), then work in a throwaway clone so the caller's tree is safe.
REMOTE_URL="$(git remote get-url "$REMOTE" 2>/dev/null || echo "$REMOTE")"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git clone --quiet "$REMOTE_URL" "$WORK"
cd "$WORK"
git config user.email "actions@users.noreply.github.com"
git config user.name "StillMirror Action"

if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  git checkout --quiet "$BRANCH"
else
  git checkout --quiet --orphan "$BRANCH"
  git rm -rfq . 2>/dev/null || true
fi

cp "$BADGE_FILE" "$BADGE_NAME"
git add "$BADGE_NAME"
if git diff --cached --quiet; then
  echo "publish-badge: badge unchanged; nothing to publish"
  exit 0
fi

git commit -q -m "Update maintainer badge"
git push --quiet origin "$BRANCH"
echo "publish-badge: published to $BRANCH"
