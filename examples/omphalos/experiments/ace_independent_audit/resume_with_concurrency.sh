#!/usr/bin/env bash
# Both harnesses: finish the current batch and switch only its successor.
set +x
set -euo pipefail
source "$HOME/.config/omphalos/env.sh"
source "$HOME/.secrets/openai.env"
test -n "${OPENAI_API_KEY:-}"
export OPENAI_API_KEY
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
python -u -m experiments.ace_independent_audit.concurrent_handoff \
    >> experiments/campaigns/ace_independent_audit/logs/concurrent-resumption-20260920.log 2>&1
