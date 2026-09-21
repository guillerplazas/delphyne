#!/usr/bin/env bash
# The registered September 20 continuation; usable from either agent CLI.
# Run in detached tmux. Credentials stay in the environment, never in logs.
set +x
set -euo pipefail

source "$HOME/.config/omphalos/env.sh"
source "$HOME/.secrets/openai.env"
test -n "${OPENAI_API_KEY:-}"
export OPENAI_API_KEY

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
ace_run_dir=experiments/campaigns/ace_independent_audit

python -u -m experiments.ace_independent_audit.quota_recovery resume \
    --account-ready-message 'I updated the key. Continue the wonderful job' \
    >> "$ace_run_dir/logs/quota-continuation-20260920.log" 2>&1

python -u -m experiments.ace_independent_audit.resumption \
    >> "$ace_run_dir/resumed-frozen-20260920.log" 2>&1

python -u -m experiments.ace_independent_audit.adaptive_frozen run \
    >> "$ace_run_dir/resumed-adaptive-frozen-20260920.log" 2>&1

python -m experiments.ace_independent_audit.status \
    >> "$ace_run_dir/logs/queue-complete-20260920.log" 2>&1
