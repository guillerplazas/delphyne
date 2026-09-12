# Fixed-book coverage campaign — 2026-09-11

Guille approved implementation of the revised plan. The experimental ceiling
is $25; the separate demo-development ceiling is internally limited to $3.
The ceiling is not a target. Every benchmark run is 40 problems, seed 0.

D adds six kernel-checked focused query examples with source-family exclusion.
E adds one nested exploration at seenstate(k=4): suffix then alternate opener,
at most three requests each, six total, $.025 and 120 verifier seconds,
inside the original $.10/64-request/300-second allowance. The incumbent
ACE playbook, model effort, and normal proof/output budgets remain fixed.
No combined arm, paid local pilot, extra seed or automatic default change.

Two trainX runs, two validationX runs, then one validation-selected testX
contender plus the flagship: six runs / 240 fresh cells. Reuse 80 historical
train/validation control cells. A metadata-only inventory found no bounded
testX control, so the test comparator is fresh. Both technically sound
variants receive validation; p-values and small train differences are not
expansion gates. Choose test contender by validation qualified solves, cost,
then arm name; freeze before test. Validation is development data.

All experimental calls and retries use ledger.sqlite3 ($24 benchmark + $1
infrastructure reserve). Demo authoring uses author.sqlite3, six Sol-medium
requests, one per training draft; it is not a prover comparison. No paid
reruns or repair evaluations can be charged to development. Unknown charges
remain liabilities. Missing/censored cells prevent a comparative verdict.
The launcher has one attempt; additional infrastructure retries require an
identified manifest, at most four, with charges preserved.

## Demonstration development

Six Sol drafts cost $0.493695. All included a redundant theorem declaration;
preparation removes it only when it exactly matches the source statement
modulo whitespace. Two drafts then passed. Four revealed incorrect rewrite
normal forms, explicit-argument mistakes, or Lean `norm_num` syntax. Small
training-only developer corrections produced four complete proofs and two
executable partial proofs. Each was checked against the original theorem.
Partial proofs are never represented as full solves. Draft admission reports
are preserved; final evidence is demo_checks.json and developer_repairs.json.
No more model calls were purchased to repair these drafts.

## Shared commands

From examples/omphalos, source ~/.config/omphalos/env.sh. Both harnesses use:

```bash
python -m experiments.coverage_experiment prepare-author
python -m experiments.coverage_experiment run --stage=author --arm=author --max_workers=4 --wait
python -m experiments.coverage_experiment build-demos
python -m tools.data.materialize_demo demos/coverage.demo.yaml
python -m experiments.coverage_experiment seal
python -m experiments.coverage_experiment run --stage=training --arm=D --max_workers=24 --wait
python -m experiments.coverage_experiment run --stage=training --arm=E --max_workers=24 --wait
python -m experiments.coverage_experiment report --stage=training
python -m tools.reports.coverage_audit --stage=training
```

Repeat run/report for validation, then `freeze-test`; use selection.json for
the test arm and run reference separately. Long runs use tmux and the standard
supervised launcher. Completed stages refuse additional runs. Preparation and
reports use immutable names: do not overwrite completed campaign artifacts.

Final reporting includes paired family uncertainty, gains/losses, common
failure classes, invocation counts, costs including failures, and retrospective
cost-qualified curves (not measured lower-budget policies). Training supplies
detailed diagnosis; validation/test observations cannot supply candidate edits.

Completed: 240 benchmark cells / $3.70503274, separate authoring $0.493695.
D testX 31/40 versus fresh flagship 30/40 at 9.1% more total cost; the extra
solve had no new-example exposure. See [RESULTS.md](RESULTS.md) for the full
comparison and failure observations. No further runs; defaults unchanged.
