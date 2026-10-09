#!/usr/bin/env bash
# trigger_website_pob_sync.sh — after bible.cartha.com publishes a new POB
# manifest, ask for a cartha.website rebuild so the same-origin static
# /bibles/pob/* bundle is rebuilt from that exact upstream version.
#
# The rebuild is the GitHub Actions workflow zackseyun/cartha.website deploy.yml
# (Azure CI runner). It is dispatched through the AWS Lambda
# cartha-ci-website-deploy-if-changed with {"force": true}, which keeps the
# GitHub token in AWS Secrets Manager (CarthaCdkService docs/CI_MIGRATION.md).
# The retired CodePipeline cartha-website-pipeline was started here before
# October 2026.

set -euo pipefail

if [[ "${POB_SKIP_WEBSITE_SYNC:-0}" == "1" ]]; then
  echo "[website-sync] skipped because POB_SKIP_WEBSITE_SYNC=1"
  exit 0
fi

WEBSITE_DISPATCH_LAMBDA="${WEBSITE_DISPATCH_LAMBDA:-cartha-ci-website-deploy-if-changed}"
WEBSITE_DISPATCH_REGION="${WEBSITE_DISPATCH_REGION:-us-west-2}"
CDN_MANIFEST_URL="${CDN_MANIFEST_URL:-https://bible.cartha.com/manifest.json}"
MANIFEST_WAIT_ATTEMPTS="${POB_MANIFEST_WAIT_ATTEMPTS:-30}"
MANIFEST_WAIT_SECONDS="${POB_MANIFEST_WAIT_SECONDS:-10}"

say() { printf '[website-sync] %s\n' "$*"; }

manifest_contains_target() {
  local manifest_sha="$1"
  local target_sha="$2"
  if [[ -z "$manifest_sha" || -z "$target_sha" ]]; then
    return 1
  fi
  if [[ "$manifest_sha" == "$target_sha" ]]; then
    return 0
  fi
  if ! command -v git >/dev/null 2>&1; then
    return 1
  fi
  git fetch --depth=100 origin "$manifest_sha" >/dev/null 2>&1 || true
  git merge-base --is-ancestor "$target_sha" "$manifest_sha" >/dev/null 2>&1
}

resolve_target_sha() {
  if [[ -n "${TARGET_SHA:-}" ]]; then
    printf '%s\n' "$TARGET_SHA"
    return 0
  fi
  if [[ -n "${CODEBUILD_RESOLVED_SOURCE_VERSION:-}" ]]; then
    printf '%s\n' "$CODEBUILD_RESOLVED_SOURCE_VERSION"
    return 0
  fi
  if command -v git >/dev/null 2>&1; then
    git ls-remote origin refs/heads/main 2>/dev/null | awk 'NR==1 {print $1; exit}' && return 0
    git rev-parse origin/main 2>/dev/null && return 0
    git rev-parse HEAD 2>/dev/null && return 0
  fi
  return 1
}

TARGET_SHA_RESOLVED="$(resolve_target_sha || true)"
if [[ -n "$TARGET_SHA_RESOLVED" ]]; then
  say "waiting for CDN manifest to reach $TARGET_SHA_RESOLVED"
  matched=0
  for i in $(seq 1 "$MANIFEST_WAIT_ATTEMPTS"); do
    BODY="$(curl -fsSL --max-time 15 "$CDN_MANIFEST_URL" || true)"
    SHA=""
    VERSION=""
    if [[ -n "$BODY" ]]; then
      SHA="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("commit_sha") or "")' <<<"$BODY" 2>/dev/null || true)"
      VERSION="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("version") or "")' <<<"$BODY" 2>/dev/null || true)"
    fi
    say "attempt=$i manifest_sha=${SHA:-missing} version=${VERSION:-missing}"
    if manifest_contains_target "$SHA" "$TARGET_SHA_RESOLVED"; then
      matched=1
      TARGET_SHA_RESOLVED="$SHA"
      break
    fi
    sleep "$MANIFEST_WAIT_SECONDS"
  done
  if [[ "$matched" != "1" ]]; then
    echo "[website-sync] CDN manifest did not reach $TARGET_SHA_RESOLVED; refusing to trigger stale website sync" >&2
    exit 1
  fi
else
  say "target SHA unavailable; triggering website pipeline without manifest SHA gate"
fi

RESPONSE_FILE="$(mktemp)"
aws lambda invoke \
  --region "$WEBSITE_DISPATCH_REGION" \
  --function-name "$WEBSITE_DISPATCH_LAMBDA" \
  --cli-binary-format raw-in-base64-out \
  --payload "{\"force\": true, \"reason\": \"pob ${TARGET_SHA_RESOLVED:-unknown}\"}" \
  "$RESPONSE_FILE" >/dev/null
say "requested cartha.website rebuild via $WEBSITE_DISPATCH_LAMBDA: $(cat "$RESPONSE_FILE")"
grep -q '"dispatched": true' "$RESPONSE_FILE" || { echo "[website-sync] website rebuild was not dispatched" >&2; exit 1; }
rm -f "$RESPONSE_FILE"
