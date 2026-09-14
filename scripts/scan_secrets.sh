#!/bin/sh
set -eu
command -v gitleaks >/dev/null 2>&1 || { echo 'Install the documented Gitleaks version before committing.' >&2; exit 1; }
if [ "${1:-}" = '--staged' ]; then
    git diff --cached --no-ext-diff --binary | gitleaks stdin --redact --no-banner
else
    staging=$(mktemp -d)
    trap 'rm -rf "$staging"' EXIT HUP INT TERM
    git checkout-index --all --prefix="$staging/"
    gitleaks dir "$staging" --redact --no-banner
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        gitleaks git . --redact --no-banner --log-opts='--all'
    fi
fi
