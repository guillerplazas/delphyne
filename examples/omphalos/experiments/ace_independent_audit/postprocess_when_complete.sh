#!/usr/bin/env bash
# Offline numerical finalization after the registered paid queue finishes.
# Both agent harnesses may use this entry point; it makes no paid calls.
set +x
set -euo pipefail
source "$HOME/.config/omphalos/env.sh"
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
python -u -m experiments.ace_independent_audit.postprocess run \
    >> experiments/campaigns/ace_independent_audit/logs/postprocess-20260920.log 2>&1
