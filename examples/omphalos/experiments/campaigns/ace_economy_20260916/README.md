# ACE inference economics and advisor controls

**Current interpretation:** Guille's quality requirement concerns code and
implementation quality. The inferred per-replicate coverage veto is
withdrawn. [The reassessment](reassessment/README.md) supersedes the old
practical labels, while keeping measurements and uncertainty unchanged.
Both harnesses generate the current decision records offline with
`python -m tools.reports.ace_economy_reassessment`. Original report commands
below reproduce historical gate outputs, not the clarified interpretation.

**Current scope: validationX only. Guille's latest instruction is "Never
touch testX".** All test plans in the original sealed protocol are revoked.
No test experiment was launched. Before the correction, setup read the test
partition list and hashed its statement files. That access was disclosed.
The original mixed seal remains untouched and must not be opened or verified.
The main coordinator was stopped before its final mixed verification; its
validation workers finished normally. See `validation_scope.json` for the
prospective validation-only seal and the scope amendment.

Use the validation-only continuation, report and replay entry points from
`examples/omphalos`, in either Claude Code or Codex:

```sh
python -m experiments.ace_economy_validation verify
python -m tools.reports.ace_economy_validation
python -m tools.analysis.ace_economy_audit
python -m tools.reports.ace_economy_figures
python -m tools.analysis.replay_economy --campaign main --batches baseline budget session views --assemble
```

Do not invoke the historical `experiments.ace_economy_experiment` CLI. Its
source and original protocol are preserved as preregistration provenance;
its mixed-scope verifier is retired. The continuation hashes only allowed
runtime code, the fixed book, validation manifests and validation inputs.
Exact replay checks outcomes, values and budget state with HTTP blocked.

The completed main campaign has **400 validation cells**: 40 problems,
two replicates, matched ACE and empty-book agentic controls, plus three
80-cell advisor arms. Paid work used the standard supervised launcher with
24 workers, 32 machine-wide slots and one attempt. There were no automatic
paid retries. The matched-budget follow-up adds exactly 80 non-ACE cells
under the **same combined $50 authorization** and reuses 80 paid ACE cells.
There is no remaining main paid work, held-out confirmation or promotion.

The primary comparison changes only the frozen v2 book versus no book.
Budget doubles the per-problem monetary allowance from $0.10 to $0.20;
session resets context once; views halves display bytes from 8192 to 4096.
Proof checking, output allowance and demonstrations are held fixed. All
controls remain opt-in. The known v2 closed-cast advice defect is documented;
this comparison does not repair a historical book in place.

The original preregistration mistakenly added preserved proof coverage on
each replicate to the 10% inference-saving target. That extra condition no
longer determines the current interpretation. Report all-attempt cost,
coverage, cost per qualified solve, paired family-clustered 90% intervals
and two-sided p-values separately. Practical promise is not a significance
test or permission to promote a default. All evidence is
from repeatedly reused development data. Advisor p-values are exploratory
and unadjusted across three interventions.

Historical book preparation adds at least $1.36785368 before embeddings;
this sunk cost is separate from the new experiment ceiling. Inference costs
are recomputed from provider token receipts at the repository's dated Luna
rates, not from an independently retrieved account invoice. See `RESULTS.md`,
`analysis/results.json`, `cells.csv`, the receipt export and replay records.
Raw caches, transport snapshots and SQLite ledgers remain in the local
campaign/output archives; the audit inventory binds them by SHA-256.

The ACE paper's 10.6% headline concerns accuracy, not a 10% inference-cost
reduction. Its adaptation-cost comparisons use other context-learning
methods. This campaign tests the user's practical economics objective:
[ACE, ICLR 2026](https://arxiv.org/abs/2510.04618v3).

Prompt attribution uses `analysis/diagnostics.json`. It counts nested
assistant answers and tool results, correcting the frozen basic profile's
`all_message_chars` and `resent_tool_output_chars`. Money and the original
gates depend on token receipts, so that descriptive correction does not
change them.

Checks use explicit modules. Aggregate tests, partition checks and global
repricing may access the closed partition and are excluded. Pinned root
`make pyright` reaches 17 existing `why3py.simple` errors outside Omphalos;
all changed Python files pass the separate pinned check.
