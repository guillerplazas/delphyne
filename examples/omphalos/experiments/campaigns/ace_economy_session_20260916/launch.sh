#!/usr/bin/env bash
# Both harnesses run this from examples/omphalos in tmux.
set -u
source "$HOME/.config/omphalos/env.sh"
python -m experiments.ace_economy_session_experiment validation > experiments/campaigns/ace_economy_session_20260916/validation.log 2>&1
status=$?
printf '%s\n' "$status" > experiments/campaigns/ace_economy_session_20260916/validation.exit
exit "$status"
