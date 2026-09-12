#!/usr/bin/env bash
# Both harnesses: run in tmux on i34-gpu01. Preserve the first-run log.
set -u
source "$HOME/.config/omphalos/env.sh"
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos || exit 1
python -m experiments.ace.ace_attribution_experiment campaign >> experiments/campaigns/ace_attribution_20260912/campaign.log 2>&1
attribution_exit=$?
echo "$attribution_exit" > experiments/campaigns/ace_attribution_20260912/campaign.resume_01.exit
exit "$attribution_exit"
