#!/usr/bin/env bash
# Both Codex and Claude Code run this from examples/omphalos, in tmux.
set -u
source "$HOME/.config/omphalos/env.sh"
python -m experiments.ace_economy_budget_experiment validation > experiments/campaigns/ace_economy_budget_20260916/validation.log 2>&1
status=$?
printf '%s\n' "$status" > experiments/campaigns/ace_economy_budget_20260916/validation.exit
exit "$status"
