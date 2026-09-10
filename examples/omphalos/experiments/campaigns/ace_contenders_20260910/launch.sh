#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.config/omphalos/env.sh"
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
campaign_dir=experiments/campaigns/ace_contenders_20260910
trap 'printf "%s\n" "$?" > "$campaign_dir/campaign.exit"' EXIT
python -m experiments.ace.ace_contender_benchmark run --max_workers=24 --wait > "$campaign_dir/campaign.log" 2>&1
python -m experiments.ace.ace_contender_benchmark report >> "$campaign_dir/campaign.log" 2>&1
