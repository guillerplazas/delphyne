#!/usr/bin/env bash
set -u
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source "$HOME/.config/omphalos/env.sh"
for coverage_arm in D E; do
  python -m experiments.coverage_experiment run --stage=validation --arm="$coverage_arm" --max_workers=24 --wait >> experiments/campaigns/coverage_20260911/validation.log 2>&1
  coverage_exit=$?
  if [ "$coverage_exit" -ne 0 ]; then
    printf '%s\n' "$coverage_exit" > experiments/campaigns/coverage_20260911/validation.exit
    exit "$coverage_exit"
  fi
done
python -m experiments.coverage_experiment report --stage=validation >> experiments/campaigns/coverage_20260911/validation.log 2>&1
coverage_exit=$?
printf '%s\n' "$coverage_exit" > experiments/campaigns/coverage_20260911/validation.exit
exit "$coverage_exit"
