# ACE role campaign — September 13, 2026

**Paused and administratively censored.** Guille requested more platform
work before further experiments. Validation stopped with 55/160 result
files; partial outcomes are not a comparison verdict and were not used for
tuning. `interruption.json` records $1.98787940 confirmed charges plus
$2.12898800 unresolved liability: **$4.11686740 of the $40 ceiling**.
The old stage must not resume. The follow-up
[platform revision](../../../docs/ace_role_revision.md) was developed and
checked offline, with no additional API charges.

Guille authorized implementation of the agreed plan with a **$40 ceiling
on new experimental API charges**, trainX/validationX only, and fresh paired
flagship controls for the final comparison. The ceiling is independent of
previous campaigns. Codex-session billing is unavailable to the campaign
ledger and is not included in that experimental API total.

Read `FINDINGS.md` for interpretation and `RESULTS.md` for generated totals.
`protocol.json`, `utility_rubric.json` and `seal.json` were frozen before paid
dispatch. No defaults or historical measurements are changed.

## Registered allocation

| Stage | Maximum jobs | Per-job cap | Maximum new charge |
| --- | ---: | ---: | ---: |
| Two writer pilots: 8 curators + 2 chained reducers per arm | 20 | $0.20 | $4.00 |
| Two reflector pilots: 8 sources per arm | 16 | $0.05 | $0.80 |
| Cached-source adaptation: 40 reflectors, 40 curators, 10 reducers | 90 | $0.05 / $0.20 | $12.00 |
| Candidate training, historical flagship references | 40 | $0.10 | $4.00 |
| Candidate and fresh flagship, 40 validation problems × 2 seeds | 160 | $0.10 | $16.00 |
| Contingency, without additional arms/seeds or automatic retries | — | — | $3.20 |
| Total ceiling | 326 | — | $40.00 |

The SQLite ledger reserves worst-case request liability before dispatch
and reconciles actual token counts under the frozen dated tariff. Unknown
liability blocks further dispatch. An absent draft skips the corresponding
curator; no generator trajectories or embeddings are purchased for
adaptation. Lower actual spend does not authorize an extra sweep.

The writer must produce at least nine valid jobs, including both reducers,
retain at least as many distinct useful corrections as the control, and
improve validity, utility or cost per useful correction. Utility is reviewed
after the real chained reducer, not counted from isolated curator activity.
The reflector must increase useful faithful reviews, incur no additional
unsupported execution claims, and remain within 1.5 times the control's
cost per useful review. Specific justified abstentions count under this
rubric, but are not executable book additions.

The book gate requires a useful checked addition to survive merge and reach
training requests. Training effect size or statistical significance is not
an expansion gate. Final practical interest means two additional qualified
solves out of 80 at no more than 1.25 times inference cost, or at least 10%
inference savings with at most two fewer solves. Preparation, research
spending, costs per solve, statistical support and changing defaults are
reported separately. Family-clustered inference uses two-sided p<0.10 and
90% intervals. validationX remains repeatedly reused development data.

## Both-harness commands

Use the shared Python environment on i34-gpu01. Long paid stages belong in
tmux with `source ~/.config/omphalos/env.sh`; the launcher supervises one
attempt, pins 24 workers / 32 machine slots and preserves failed cells.
The sequence below records the original protocol; it is not an instruction
to resume this interrupted campaign:

```bash
python -m experiments.ace_roles_experiment prepare
python -m tools.data.ace_role_demos
pytest -q tests/test_ace_roles.py
python -m experiments.ace_roles_experiment seal
python -m experiments.ace_roles_experiment pilots
python -m tools.reports.ace_roles_results audit
# Review the arm-free items, then map owners into pilot_review.json.
python -m experiments.ace_roles_experiment gates
python -m experiments.ace_roles_experiment adapt
python -m tools.reports.ace_roles_results audit
# Review the frozen book and persist book_review.json.
python -m experiments.ace_roles_experiment training
python -m tools.reports.ace_roles_results report
python -m experiments.ace_roles_experiment validation
python -m experiments.ace_roles_experiment replay
python -m tools.reports.ace_roles_results report
```

Preparation and completed immutable stages are idempotent with matching
inputs. Do not reseal a changed treatment or overwrite completed artifacts.
The CLI's abbreviated module docstring lists conceptual stages; demos and
report/audit are the separate modules shown above, and preflight is the
scoped test/translation procedure recorded in `offline_checks.json`.

## Evidence map

- `sources/`: 40 cached flagship training trajectories, event contexts and
  terminal receipts; `terminal_fixture.json`: the separate accepted-tail
  pilot example. No protected data is included.
- `inputs/`, `manifests/`, `batches/`: immutable model inputs and expected
  jobs, including deterministic validation dispatch ordering.
- `transport/`, `ledger.sqlite3`, `events.jsonl`: exact local replay and
  admission evidence. Raw results live in
  `../../output/ace_roles_20260913/`; they are frozen measurements.
- `audits/`: retained snippets, real-Rocq rechecks, reviewer item labels,
  owner mapping and source-local utility sensitivity.
- `pilot_review.json`, `gates.json`: explicit agent adjudication and the
  mechanical gate result. Review is not independent human blinding.
- `book_steps/`, `skips/`, `book.yaml`, `book.json`: actual chained update,
  including unsuccessful roles and abstentions.
- `replays/`: complete offline replay inventories, with HTTP forbidden.
- `reports/`, `accounting/`, `cost_sensitivity/`, `cells.csv`, `receipts.csv`:
  denominators, repriced costs, paired inference and cache sensitivity.
- `interruption.json`, `PAUSED`: censored status and conservatively retained
  liability. The training report is a milestone, not final campaign spend.
- `platform_v2/`: preserved scripted fixtures and offline quality records,
  separate from the sealed v1 treatment and its measurements. Their query
  demonstrations were subsequently sealed into the successor campaign;
  do not regenerate the historical fixtures in place.

All analytical code installs `runtime/ace_roles_scope.py` before imports.
Mixed HINTS/history/index files and aggregate test/repricing/status commands
are excluded. Accessible development notes informed the hypotheses; this
does not claim a fresh unrestricted audit of the mixed backlog.
