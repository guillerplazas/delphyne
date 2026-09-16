# ACE adaptation improvements and benchmark protocol

This experiment changes adaptation while preserving the polished v2 generator.
The executable preregistration is `experiments/ace_learning_experiment.py`;
campaign inputs and decisions live in
`experiments/campaigns/ace_learning_20260914/`.

Four local treatments are evaluated independently on recorded trainX inputs:

- Action-specific structured plans forbid irrelevant fields instead of relying
  on prose to prevent malformed drop/example decisions. An explicit adapter
  preserves the existing validation and atomic book mutation contracts.
- Independent review receives original failed events, exact verified prefixes,
  and bounded before/after goal and existential observations. It separates
  local mathematical support, whole-proof completion, and semantic novelty.
- Reflection compares candidate opportunities against the current book,
  prioritizing reproducible bad recipes, prerequisites, and useful fragments
  from both accepted and unsolved histories. Four turns and three drafts remain.
- Curator examples are executable Delphyne demonstrations selected by role and
  operation/error overlap; every source theorem family is excluded from its
  own examples. Examples cover focus, references, arguments and square syntax.

The 52 paid pilot episodes use archived v2 outputs as controls: 12 final-plan
queries, all 16 review queries, 12 reflector episodes and 12 curator episodes.
Review labels are a pre-call source audit, not independent human annotation;
four semantic-relevance cases remain unresolved. Curator failure strata mean
recorded rejected checks, not necessarily wholly unsuccessful episodes.
No guessed proof is labeled verified. Local observations replay real Rocq;
unknown observations never become evidence of mathematical progress.

Candidate A uses passing schema/review treatments. B adds passing reflection
and curator treatments. Both start from the same X3 seed book, with the same
40 frozen source histories and order as v2. A reuses historical reflection.
Each book is reconstructed and its retained receipts independently rechecked.
Generator prompts, tools, controller, model, reasoning effort and budget are
unchanged; generator exposure to a learned book is measured from actual model
requests. Stored examples are not claimed to be generator demonstrations.

The new API ceiling is $30: pilots $5, adaptation $5, training $8, validation
$8 and contingency $4. No paid retries or source regeneration. Up to two
40-cell trainX panels precede selection; primary validation has 80 cells
(40 problems, seeds 0 and 1). A second eligible full panel requires a recorded
rollover leaving $2 contingency. Duplicate books are evaluated once. The 120
compatible historical v2 proof cells are reused and repriced from receipts.
The source/provider time difference and input-cache sensitivity limit causal
claims. validationX is development data; testX and challenge remain closed.

Every expected cell must exist; platform failures remain in denominators.
A qualified solve costs at most $.10 in actual ledger charges, including any
transport retry. Reports include complete-panel cost, cost/solve, marginal
preparation, all-in economics, uncached-token sensitivity, paired two-sided
p-values and 90% intervals clustered by theorem family across both seeds.
Practical validation interest is two extra cells at <=1.25 cost, or >=10%
savings with at most two fewer cells. Statistical support is separate from
practical interest; no default is promoted automatically.

Both Codex and Claude Code use the same commands, from `examples/omphalos`:

```sh
python -m experiments.ace_learning_experiment prepare
python -m experiments.ace_learning_experiment data
pytest -q tests/test_ace_learning.py
python -m experiments.ace_learning_experiment seal
python -m experiments.ace_learning_experiment pilots
# Audit analysis/pilots.json and record pilot_decisions.json before adaptation.
python -m experiments.ace_learning_experiment adapt A
python -m experiments.ace_learning_experiment audit A
python -m experiments.ace_learning_experiment training A
# Repeat for B if extra treatments pass; then freeze selection.
python -m experiments.ace_learning_experiment select
python -m experiments.ace_learning_experiment validation A
python -m experiments.ace_learning_experiment replay
python -m experiments.ace_learning_experiment report
```

Use the actual selected arm for validation. Paid phases run in tmux with the
registered supervised launcher and measured 24-worker/32-slot runtime profile.
Completed batches are resumable and immutable. Preparation and fixtures are
closed after the source seal or first receipt. Regenerable analysis is separate
from raw outputs. Aggregate tests that access closed partitions are excluded;
use the scoped coverage-cycle target and explicit role/budget suites.
