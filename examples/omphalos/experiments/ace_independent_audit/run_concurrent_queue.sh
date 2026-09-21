#!/usr/bin/env bash
# Both harnesses: continue the certified handoff, with no repeated attempts.
set +x
set -euo pipefail
source "$HOME/.config/omphalos/env.sh"
source "$HOME/.secrets/openai.env"
test -n "${OPENAI_API_KEY:-}"
export OPENAI_API_KEY
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
python -u -m experiments.ace_independent_audit.concurrent_queue \
    >> experiments/campaigns/ace_independent_audit/logs/concurrent-queue-20260920.log 2>&1
