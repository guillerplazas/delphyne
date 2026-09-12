#!/usr/bin/env bash
# Shared by Codex and Claude Code; run inside tmux on i34-gpu01.
set -uo pipefail
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source /home/guille/.config/omphalos/env.sh
python -m experiments.ace.ace_capacity_experiment campaign > experiments/campaigns/ace_capacity_20260912/campaign.log 2>&1
capacity_exit=$?
printf '%s\n' "$capacity_exit" > experiments/campaigns/ace_capacity_20260912/campaign.exit
exit "$capacity_exit"
