#!/usr/bin/env bash
set -euo pipefail
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source /home/guille/.config/omphalos/env.sh
campaign=experiments/campaigns/ace_mechanisms_20260910
trap 'code=$?; echo "$code" > "$campaign/campaign.exit"' EXIT
python -m experiments.ace.ace_mechanisms_experiment run --stage=local --max_workers=4 --wait
python -m experiments.ace.ace_mechanisms_experiment report --stage=local
python -m experiments.ace.ace_mechanisms_experiment run --stage=training --max_workers=24 --wait
python -m experiments.ace.ace_mechanisms_experiment report --stage=training
if python -c 'from experiments.ace.ace_mechanisms_experiment import read; import sys; sys.exit(0 if read("selection.json")["arm"] else 1)'; then
    python -m experiments.ace.ace_mechanisms_experiment run --stage=validation --max_workers=24 --wait
    python -m experiments.ace.ace_mechanisms_experiment report --stage=validation
fi
