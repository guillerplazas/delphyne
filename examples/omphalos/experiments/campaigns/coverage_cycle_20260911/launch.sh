#!/usr/bin/env bash
set -u
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source "$HOME/.config/omphalos/env.sh"
for cycle_stage in training validation; do
  for cycle_arm in D2 E2 S H; do
    python -m experiments.coverage_cycle_experiment run --stage="$cycle_stage" --arm="$cycle_arm" --max_workers=24 --wait
    cycle_exit=$?
    if [ "$cycle_exit" -ne 0 ]; then
      printf '%s\n' "$cycle_exit" > experiments/campaigns/coverage_cycle_20260911/campaign.exit
      exit "$cycle_exit"
    fi
  done
  python -m experiments.coverage_cycle_experiment report --stage="$cycle_stage"
  cycle_exit=$?
  if [ "$cycle_exit" -ne 0 ]; then
    printf '%s\n' "$cycle_exit" > experiments/campaigns/coverage_cycle_20260911/campaign.exit
    exit "$cycle_exit"
  fi
  python -m tools.reports.coverage_cycle_audit "$cycle_stage"
  cycle_exit=$?
  if [ "$cycle_exit" -ne 0 ]; then
    printf '%s\n' "$cycle_exit" > experiments/campaigns/coverage_cycle_20260911/campaign.exit
    exit "$cycle_exit"
  fi
done
printf '0\n' > experiments/campaigns/coverage_cycle_20260911/campaign.exit
