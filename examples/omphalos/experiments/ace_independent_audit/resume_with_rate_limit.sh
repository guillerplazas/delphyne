#!/usr/bin/env bash
# Continue the original study under the replacement account's TPM limit.
# Both harnesses use this script; credentials are never logged.
set +x
set -euo pipefail
source "$HOME/.config/omphalos/env.sh"
source "$HOME/.secrets/openai.env"
test -n "${OPENAI_API_KEY:-}"
export OPENAI_API_KEY
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
python -u -m experiments.ace_independent_audit.rate_recovery run \
    >> experiments/campaigns/ace_independent_audit/logs/rate-resumption-20260920.log 2>&1
