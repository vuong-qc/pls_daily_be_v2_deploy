#!/usr/bin/env bash
set -euo pipefail

SOURCE_REPO="${SOURCE_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"
SOURCE_REPO_NAME="$(basename "${SOURCE_REPO}")"
DEFAULT_DEPLOY_REPO="$(cd "$(dirname "${SOURCE_REPO}")" && pwd)/${SOURCE_REPO_NAME}_deploy"
DEPLOY_REPO="${1:-${DEPLOY_REPO:-${DEFAULT_DEPLOY_REPO}}}"

if [[ ! -d "${SOURCE_REPO}/.git" ]]; then
  echo "Source repo not found: ${SOURCE_REPO}" >&2
  exit 1
fi

if [[ ! -d "${DEPLOY_REPO}/.git" ]]; then
  echo "Deploy repo not found: ${DEPLOY_REPO}" >&2
  echo "Pass the deploy repo path as the first argument if needed." >&2
  exit 1
fi

echo "Syncing source repo:"
echo "  ${SOURCE_REPO}"
echo "to deploy repo:"
echo "  ${DEPLOY_REPO}"

if command -v rsync >/dev/null 2>&1; then
  echo "Using rsync (macOS/Linux)..."

  rsync -a --delete \
    --exclude '.git/' \
    --exclude '.github/workflows/' \
    --exclude '.env' \
    --exclude '.env.*' \
    --exclude '*_SSH_PRIVATE_KEY*' \
    --exclude '.venv/' \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '.mypy_cache/' \
    --exclude '.coverage' \
    --exclude '.coverage.*' \
    --exclude '.DS_Store' \
    --exclude 'htmlcov/' \
    --exclude 'credentials.json' \
    --exclude '*deploy_key*' \
    --exclude 'production_deploy_key*' \
    --exclude 'backend_production_deploy_key*' \
    --exclude 'ops/production-deploy-repo-template/' \
    --exclude 'README.md' \
    "${SOURCE_REPO}/" "${DEPLOY_REPO}/"
    
elif command -v robocopy.exe >/dev/null 2>&1; then
  echo "Using robocopy (Windows)..."

  set +e

  MSYS_NO_PATHCONV=1 robocopy.exe \
    "$(cygpath -w "${SOURCE_REPO}")" \
    "$(cygpath -w "${DEPLOY_REPO}")" \
    /MIR \
    /XD ".git" ".github\workflows" ".venv" "venv" "__pycache__" ".pytest_cache" ".mypy_cache" "htmlcov" "ops\production-deploy-repo-template" \
    /XF ".env" ".env.*" ".coverage" ".coverage.*" ".DS_Store" "credentials.json" "*_SSH_PRIVATE_KEY*" "*deploy_key*" "production_deploy_key*" "backend_production_deploy_key*" "README.md"

  RC=$?
  set -e

  if [ "$RC" -ge 8 ]; then
    echo "Robocopy failed with exit code $RC" >&2
    exit "$RC"
  fi

else
  echo "Neither rsync nor robocopy is available." >&2
  exit 1
fi

find "${DEPLOY_REPO}" -maxdepth 1 -type f \
  \( -name '*_SSH_PRIVATE_KEY*' -o -name '*deploy_key*' \) \
  -delete

mkdir -p "${DEPLOY_REPO}/.github/workflows"
rm -f "${DEPLOY_REPO}/.github/workflows/"*.yml

cp \
  "${SOURCE_REPO}/ops/production-deploy-repo-template/.github/workflows/deploy-production.yml" \
  "${DEPLOY_REPO}/.github/workflows/deploy-production.yml"

cp \
  "${SOURCE_REPO}/ops/production-deploy-repo-template/README.md" \
  "${DEPLOY_REPO}/README.md"

echo
echo "Sync complete."
echo "Next steps:"
echo "  cd \"${DEPLOY_REPO}\""
echo "  git status"
echo "  git add ."
echo "  git commit -m \"Sync source for production release\""
echo "  git push origin main"
