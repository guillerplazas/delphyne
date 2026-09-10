#!/usr/bin/env bash
# Identical launch adapter for Codex and Claude on i34-gpu01.
set -u
source "$HOME/.config/omphalos/env.sh"
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos || exit 1
python -m experiments.ace.ace_models_experiment campaign > experiments/campaigns/ace_models_20260910/campaign.log 2>&1
result=$?
echo "$result" > experiments/campaigns/ace_models_20260910/campaign.exit
exit "$result"
