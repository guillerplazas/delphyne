# Bounded ACE polish — registered 2026-09-09

Completed: 224 cells, **$4.24146774 API**. Frozen training: 26/40 for
$0.76279972. Paired validation: **53/80 versus 53/80**, candidate $1.51289576
versus reference $1.43330822 (+5.55%). Both utility gates failed;
statistically inconclusive. Retain original bounded money+focused as the
recommended reference, keep the polished implementation opt-in. Full
results and failure interpretation: [FOLLOW_UP.md](FOLLOW_UP.md),
[final_report.json](final_report.json), [retention.json](retention.json).

Guille authorized implementation and this $8 campaign. The executable
preregistration is `experiments/ace/ace_polish_experiment.py`. There are
24 isolated trainX pilot cells, one frozen 40-cell trainX candidate panel,
and 160 paired validationX cells (candidate/reference, seeds 0 and 1).
The ledger allocations are demos $0.60, pilots $0.80, training $1.10,
validation $5.00, infrastructure retries $0.50. At most four explicitly
identified infrastructure retries; no logical-failure retries or extra seeds.
Closed-stage slack may fund later registered stages, never new cells.

Utility gates are >=15% savings with <=2/80 fewer qualified solves, or
>=4/80 additional qualified solves with <=20% extra cost (15% target).
Report family-clustered two-sided p<0.10 and descriptive 90% intervals
separately. ValidationX is development data; these are not clean holdout
claims. testX and protected challenge data are excluded from adaptation,
failure mining and evaluation. Assistant charges are not metered here.

The candidate fixes typed Compute admission and uses Delphyne preflight,
shared budget composition and query-specific example selection. Optional
mechanisms share exactly one recovery allowance: resource/stagnation suffix
repair, or one 4096-token continuation after monetary refusal with recent
verified progress. The ordinary completion cap stays 32768. No budget resets.
The preflight is sequential and zero-cost; actual Compute reserves/settles
its own time. No Rocq transport implementation was changed.

Preparation reverified 24 trainX transitions: two syntax, two type, six
normal-form, four reference, three incomplete, three structure and four
resource-associated transitions. Four resource-associated examples do not
establish logical rejection of the original timed-out action. Examples
require explicit symbol/name and failure-category matching, and at most
one is selected. No teacher/model calls were necessary. `artifact.json`
holds the raw evidence; `demos/polished.demo.yaml` includes 24 positive
navigation checks and one unsafe-action rejection with materialized results.

The retained reference uses the original money+focused recipe, with the
legacy admission behavior preserved. The surviving control-cycle source
does not reproduce its advertised implementation; its paid entrypoint is
closed. Its recorded result is 28/40 versus bounded 25/40, not a tie.
Original reports and receipts are unchanged. Full bounded cache replay has
a pre-existing miss on induction_prod1p1onk3le3m1onn, reproduced with
unmodified HEAD. A single mathd_algebra_190 replay passed. Fresh controls
avoid treating the historical measurements as contemporaneous comparisons.

Both harnesses use the same commands, after sourcing
`~/.config/omphalos/env.sh` from this directory. Runs use tmux and the
supervised launcher, 8 workers within the existing 16 machine slots:

```bash
python -m tools.reports.ace_polish_report prepare
python -m tools.reports.ace_polish_report navigation
python -m tools.data.materialize_demo demos/polished.demo.yaml
python -m tools.reports.ace_polish_report seal
python -m experiments.ace.ace_polish_experiment --phase=pilots run --max_workers=8 --wait
python -m tools.reports.ace_polish_report serialization_demos
python -m tools.reports.ace_polish_report freeze
python -m experiments.ace.ace_polish_experiment --phase=training run --max_workers=8 --wait
python -m experiments.ace.ace_polish_experiment --phase=validation run --max_workers=8 --wait
python -m tools.reports.ace_polish_report report
```

These are the historical command sequence, not a recipe to overwrite this
archive or to rerun the pilot with today's source hashes. Preparation needs
the local paid training archives; the checked artifact and demonstrations
are sufficient for frozen execution. Preparation/freeze refuse replacement.
Sealing final implementation hashes
is allowed only before payment. Do not rerun preparation in this completed
directory; status/report commands consume its registered artifacts.

## Pilot result and final freeze

All 24 cells finished: 22 results and two recorded implementation failures,
$0.53246404 across 302 settled HTTP attempts, zero retries or unknown charges.
Matched advice: 3/4 versus 3/4, $0.062172 versus $0.065704; selected.
Output downshift: 2/4 versus 1/4, $0.101593 versus $0.126489; selected.
Recovery: 1/4 versus 2/4, $0.069330 versus $0.107177; unselected because
two triggered cells failed Responses feedback translation. Its apparent
saving is not recovery evidence. Pilot differences are descriptive.

The formatter bug was repaired after the pilot: retain the immediately
preceding assistant proposal with the current feedback when clearing stale
dialogue. A real rendering/Responses-translation regression now covers this
boundary. No extra pilot cells were purchased; repaired resource recovery
remains off in the frozen benchmark candidate. Thirteen structured role
examples were also converted from existing training demonstrations without
API calls, preserving the old query buckets.

An independent reporting defect was caught before any full benchmark: the
legacy cell reader searched only the first 64KiB, while the new command's
artifact arguments put `outcome` after 131KiB. It initially reported all
pilot solves as false. The reader now anchors at the top-level outcome;
the regression includes 150KiB of arguments with a decoy success field.
The corrected solve counts leave switch selection unchanged. The erroneous
unselected drafts are preserved as `frozen_draft_reader_bug.json` and
`pilot_cells_draft_reader_bug.json`; `frozen.json` and `pilot_cells.json`
are the corrected final artifacts. No paid measurement was edited.

Pre-pilot checks: Omphalos make test, local Pyright, Ruff, repricing and
demonstration checks passed. Root make pyright passes core then stops at
the existing missing why3py.simple dependency in find_invariants (17 errors,
outside the authorized edit scope).
