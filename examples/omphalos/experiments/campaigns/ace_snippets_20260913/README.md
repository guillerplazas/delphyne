# Rocq snippet tool: authorized implementation and comparison

Guille authorized this plan on September 13, 2026. Both Codex and Claude Code
use the same Python entry points from `examples/omphalos`. No testX or
protected challenge evidence is permitted. Install `runtime.snippet_scope`
before experiment imports; mixed memory/history remains closed.

## Implementation

`CheckRocqSnippet(context_id, snippet)` uses a context-bound, unassisted Rocq
Compute check. The complete raw snippet reaches Rocq, including malformed
tails. Receipts distinguish rejection, executed fragments with open goals,
complete Qed-accepted proofs, resource exhaustion and unavailable evidence.
Complete checks return the accepted proof immediately. Contexts bind source
file hashes, imports and exact verified prefixes. The model cannot choose
arbitrary files. There are at most four probes per theorem, within the
incumbent request and verifier allowances.

Versioned writer queries give reflector, curator and reducer the same tool,
at most three probes and four model requests. The final request has no tools.
Executable advice is rendered deterministically from retained receipt IDs;
rewriting code requires another check. Every available checked receipt is
retained or explicitly dropped. Plain explanatory prose is not certified.
The existing terminal receipt reaches reflection and now also recognizes
proofs completed by this new tool. Historical defaults and books stay intact.

Delphyne queries, strategies, Compute, demonstrations and budget streams own
the workflow. Every individual Rocq operation exposes its actual elapsed
cost to `grounded_search`; no composite operation hides multiple checks.
The existing supervised launcher and cumulative ledger handle paid execution.

## Registered comparison

- Reference: current bounded/focused Luna-medium flagship, frozen X3 book.
- A: reference with the snippet tool, versioned instructions and two train-only
  executable query demonstrations. Source theorem families are excluded.
- B: exactly A's prover, with a targeted checked update to the frozen book.

Proof cells retain $0.10, 64 model requests, 300 Rocq seconds and 32768 output
tokens. Operations retain 60 seconds, 512 RPCs and 8192 view bytes. Other
interventions remain off. Writing uses 8192 output tokens and 180 Rocq seconds
per job; reflector/curator caps are $0.10, reducer caps $0.20.

Eight existing training trajectories, listed in protocol.json, form two
batches of four. Each batch runs four reflections, four curations and one
reduction, starting from its batch-start book. Deterministic merging admits
at most three additions per batch under the existing 4000-token book guard.
There are no fresh source generators, embeddings or paid diagnostics.

The training panel contains the 17 historical flagship trainX syntax-error
problems plus mathd_algebra_323, amc12b_2002_p11 and mathd_numbertheory_42.
Run 20 problems per arm at seed0, then 40 validationX problems per eligible
arm at seed0. B requires A's full validation panel as its contemporary
control. One selected contender may receive all 40 validationX problems at
seed1 plus 40 fresh incumbent controls. Reuse 60 compatible historical
seed0 controls; replay their observed requests offline before dispatch.

## Gates, inference and accounting

A requires a real training snippet check with a meaningful Rocq verdict.
B requires completed writing, a changed checked book and actual dispatched
training requests carrying it. Missing required writer output blocks a B
verdict; it does not silently substitute an incomplete book. B's comparison
may require A as a control even if A's standalone exposure gate fails.

Against the incumbent, expansion requires >=1 additional qualified solve at
all-in cost ratio <=1.25, or <=1 lost solve at ratio <=0.90. Include B's
one-time writing expense. Rank coverage, all-in cost per solve, total cost,
then A. After repeat, scale the gate to two solves over 80 observations;
fresh seed1 must not be worse in both coverage and cost. Count preparation
once across the combined panel. No incumbent promotion is automatic, and no
runs are added to cross a significance threshold.

Report qualified solves, inference cost, preparation cost, total campaign
spending and cost per qualified solve together. All failed attempts remain
in denominators. Missing/admin-censored required cells and unknown billing
prohibit verdicts. Use the existing family-clustered paired evaluator,
two-sided p<.10 and 90% intervals; Holm adjusts A/reference, B/A and B/reference.
Historical controls, repeated validation selection, cache fractions, tariffs
and controller/runtime differences limit causal/generalization claims.

The existing $30 ledger already contains $3.61359998. The remaining
$26.38640002 is allocated as: writing $2, training $4, validation $8, optional
repeat/fresh control $8, contingency $4.38640002. The old training allocation
transfers $0.25248468 to contingency; contingency transfers $1.86608466 to
validation. The same ledger retains its $30 hard ceiling and prior receipts.
All new cells use a snippets-v1 namespace. Prior exports remain snapshots.

SDK and launcher automatic retries are disabled. Unknown charges retain
their liabilities and halt dispatch. At most four explicitly recorded,
reconciled infrastructure retries are allowed, one per logical cell, retaining
the cell cap and counting paid prefixes once. The reserve is not a target.
Codex-session costs are separate and unavailable through this ledger.

## Commands and review

Free setup/checks:

```sh
python -m tools.data.snippet_demos
python -m experiments.snippet_experiment prepare
python -m pytest -q tests/test_snippet_tool.py
python -m experiments.snippet_experiment preflight
```

The offline-check receipt and source seal must pass before the authorized
campaign command can dispatch. `campaign` uses `OmphalosExperiment`, not a
direct API loop. New measurements and transport snapshots live in this
campaign and its corresponding output directory. Run only scoped checks;
global tests, partition checks, repricing and Ladon status are excluded.

Implementation remains inside Omphalos, staged and uncommitted. Durable
milestones live here and in a permitted memory entry; the mixed index is not
opened. Ladon night metadata was inspected directly before recording work;
all inspected nights were done.
