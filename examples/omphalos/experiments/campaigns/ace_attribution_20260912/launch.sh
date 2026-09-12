#!/usr/bin/env bash
# Identical entry point for Codex and Claude Code. Run inside tmux.
set -u
source "$HOME/.config/omphalos/env.sh"
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
python -m experiments.ace.ace_attribution_experiment campaign > experiments/campaigns/ace_attribution_20260912/campaign.log 2>&1
attribution_exit=$?
printf '%s\n' "$attribution_exit" > experiments/campaigns/ace_attribution_20260912/campaign.exit
exit "$attribution_exit"
