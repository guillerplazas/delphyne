# ACE revision rebenchmark — 2026-09-13

The complete fresh proof benchmark is recorded in [RESULTS.md](RESULTS.md).
[FINDINGS.md](FINDINGS.md) explains the platform changes, learning yield,
uncertainty and recommendation; [ARTIFACTS.md](ARTIFACTS.md) distinguishes
the lean evidence export from the preserved local raw archive.

Guille explicitly authorized a new experiment budget starting at zero,
with the existing $40 ceiling, and required platform correctness before
paid dispatch. `authorization.json` preserves that instruction and the
earlier campaign's charges and unresolved liability. The old interrupted
validation is not resumed or used for tuning.

The [platform revision](../../../docs/ace_role_revision.md) preserves local
drafts and checked partial products, reviews novelty separately, supports
targeted corrections and evidence-only examples, bounds prompt growth,
checkpoints work at budget stops, and cooperatively pauses new requests.
The query demonstrations and role tests use real Rocq with scripted model
responses. The campaign integration test also exercises the full adaptation
driver, book audit/freeze, both paired panels and reporting with HTTP blocked.
Its synthetic proof results live only in pytest temporary directories.

## Frozen comparison

The control is X3, book SHA
`1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067`.
The candidate starts from X3 and adapts through the v2 reflector, curator
and reducer. Forty previously paid trainX trajectories provide its sources;
there are no fresh source generators or embeddings. The generator retains
Luna-medium, core tools, bounded/focused proof control and the $0.10,
64-request, 300-verifier-second limits. Its Responses output allowance is
32768 tokens. Only the learned book differs between arms.

The pause adapter is common to both proof arms. An offline test compares
its dispatched request to the flagship policy's request. Both proof arms
use fresh config directories; earlier answers are not replayed as controls.
The candidate book is frozen and its receipts rechecked before training.
Training is diagnostic, with no effect-size expansion gate. Validation
requires the frozen book to have reached training requests.

| Stage | Maximum jobs | Allocation |
| --- | ---: | ---: |
| Adaptation: 40 reflectors, up to 40 curators, up to 10 reducers | 90 | $12 |
| trainX: 40 problems × two arms | 80 | $8 |
| validationX: 40 problems × two seeds × two arms | 160 | $16 |
| Unused contingency; no extra arms, seeds or automatic retries | — | $4 |
| Total | 330 | $40 |

The reservation ledger caps aggregate liability, including unknown charges.
A nominal per-problem stop alone is not a hard billing ceiling. Costs are
recomputed from dated token prices, including cached-input discounts and
failed attempts. Report adaptation cost separately from inference, plus
cost per qualified solve, all-in preparation cost and descriptive
amortization. The ceiling is a limit, not a spending target.

Final practical interest is at least two additional qualified solves out
of 80 at at most 1.25 times inference cost, or at least 10% inference savings
with at most two fewer solves. Statistical support uses family-clustered
two-sided p<0.10 and 90% intervals. Seeds are repeated measurements, not
independent theorems. Missing or administratively censored cells prevent a
verdict; platform failures remain in the denominator. No default is changed
automatically. validationX remains reused development data; testX and the
protected challenge remain closed.

## Both-harness commands

Run from `examples/omphalos` on i34-gpu01, using the shared environment.
The new experiment module uses the standard supervised launcher, one
attempt, 24 workers and 32 Rocq slots. Long runs belong in tmux.

```bash
source ~/.config/omphalos/env.sh
python -m experiments.ace_revision_experiment prepare
# Run the scoped tests and persist preflight.json before sealing.
python -m experiments.ace_revision_experiment seal
python -m experiments.ace_revision_experiment all
```

`all` runs adaptation, a real-Rocq receipt audit, training, validation,
HTTP-forbidden exact replay, and reporting. Each stage records immutable
inputs, manifests and batch completions. A changed, audited book is required
for proof runs. There are no hidden retries or fallback candidate books.
The source seal prevents editing the measured treatment in place.

To pause admission without interrupting in-flight HTTP settlement:

```bash
python -m runtime.campaign_pause experiments/campaigns/ace_revision_20260913/PAUSED --reason "requested pause"
```

Let the supervisor drain. The flag is shared by roles and proof workers;
already admitted operations may still finish. Do not kill only the wrapper
and leave its attempt running. Cancellation is administrative censoring,
not an ordinary failed proof.

Scope guards differ between earlier campaigns and intentionally cannot be
uninstalled within a process. Run these regression groups separately:

```bash
pytest -q tests/test_ace_roles.py tests/test_ace_role_revision.py tests/test_ace_roles_reporting.py
pytest -q tests/test_ace_revision_campaign.py
pytest -q tests/test_writer_receipts.py tests/test_terminal_evidence.py
pytest -q tests/test_writer_drafts.py
```

The source seal, preflight evidence, per-role checkpoints, complete revision
records, ledger, raw transport snapshots and result caches distinguish
local execution, reviewed novelty, retention, prompt exposure and final
coverage. Scripted preflight is not a model-performance measurement.
