#!/usr/bin/env bash
set -u
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source "$HOME/.config/omphalos/env.sh"
python -m experiments.coverage_experiment run --stage=author --arm=author --max_workers=4 --wait > experiments/campaigns/coverage_20260911/author.log 2>&1
coverage_exit=$?
printf '%s\n' "$coverage_exit" > experiments/campaigns/coverage_20260911/author.exit
exit "$coverage_exit"
