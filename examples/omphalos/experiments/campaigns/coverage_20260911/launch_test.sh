#!/usr/bin/env bash
set -u
cd /home/guille/anaconda3/envs/guille/delphyne/examples/omphalos
source "$HOME/.config/omphalos/env.sh"
python -m experiments.coverage_experiment freeze-test >> experiments/campaigns/coverage_20260911/test.log 2>&1 || exit $?
python - <<'PY' >> experiments/campaigns/coverage_20260911/test.log 2>&1
from experiments import coverage_experiment as c
c.verify()
paths=[c.CAMPAIGN/n for n in ('selection.json','test_manifest.json','validation_report.json')]
paths += [c.ROOT/r['problem_file'] for r in c.read('test_manifest.json')]
c.save('test_freeze.json',dict(dependencies={str(p.relative_to(c.ROOT)):c.digest(p) for p in paths},rule='One frozen seed-0 test comparison; no candidate edits from test outcomes'))
print('Test selection and all 40 statements sealed before first test request.')
PY
coverage_exit=$?
if [ "$coverage_exit" -ne 0 ]; then exit "$coverage_exit"; fi
coverage_selected=$(python - <<'PY'
from experiments.coverage_experiment import read
arm=read('selection.json')['arm']
assert arm in ('D','E')
print(arm)
PY
)
for coverage_arm in "$coverage_selected" reference; do
  python - <<'PY' >> experiments/campaigns/coverage_20260911/test.log 2>&1
from experiments import coverage_experiment as c
c.verify()
c.old.verify_hashes(c.read('test_freeze.json')['dependencies'])
PY
  coverage_exit=$?
  if [ "$coverage_exit" -ne 0 ]; then exit "$coverage_exit"; fi
  python -m experiments.coverage_experiment run --stage=test --arm="$coverage_arm" --max_workers=24 --wait >> experiments/campaigns/coverage_20260911/test.log 2>&1
  coverage_exit=$?
  if [ "$coverage_exit" -ne 0 ]; then
    printf '%s\n' "$coverage_exit" > experiments/campaigns/coverage_20260911/test.exit
    exit "$coverage_exit"
  fi
done
python -m experiments.coverage_experiment report --stage=test >> experiments/campaigns/coverage_20260911/test.log 2>&1
coverage_exit=$?
printf '%s\n' "$coverage_exit" > experiments/campaigns/coverage_20260911/test.exit
exit "$coverage_exit"
