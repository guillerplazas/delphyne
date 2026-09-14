# ACE roles with checked handoffs

**Current status:** the v1 campaign was interrupted during validation when
Guille redirected work to platform improvements. It has no validation
verdict. The separately tested and benchmarked successor is documented in
[ACE role revision](ace_role_revision.md); this page describes the sealed v1.

The opt-in strategies in `prove_ace_roles.py` give curators and reducers a
small decision interface and give reflectors access to recorded execution
evidence. The measured campaign is
[`ace_roles_20260913`](../experiments/campaigns/ace_roles_20260913/README.md).
Its results decide whether the resulting book is useful; valid tool calls
alone do not establish an improvement. The flagship configuration is intact.

## Interfaces

`WriteACEChoices` presents local `c1` context, `d1` draft and `r1` receipt
references. The model decides whether to retain or drop each draft. Python
resolves references, validates complete coverage, derives the retained and
unretained receipt sets, and compiles the existing `CurationDelta` format.
Long immutable source and receipt hashes remain in persisted evidence.

`CheckAdviceSnippet` uses the existing unassisted Rocq Compute operation in
the selected training context. The writer gets at most three new checks,
four model turns and 180 verifier seconds; individual operations have
60-second, 512-RPC and 8192-byte view limits. Identical checks reuse their
receipts. Changed code must receive its own check. A valid open fragment is
not a complete proof. Successful local fragments can supply successor
contexts without becoming global lemmas.

The reducer receives the actual curator products and receipts. Original
drafts also survive unsuccessful curator jobs, so an empty operation list
does not discard the only repair opportunity. Inherited receipts require
their exact source contexts. Source-family-excluded demonstrations show the
curator and reducer protocols with real Rocq outcomes.

`ReflectACEEvidence` receives the authoritative terminal record, a compact
event index and the training trajectory. `ReadTrainingEvidence(e1)` looks up
an existing event; it does not run another generator or search a benchmark.
The final answer binds one proposed draft to one event or explicitly
abstains. The terminal record distinguishes submitted text, accepted text,
assistance and unsuccessful execution. A draft remains unverified until a
writer checks it.

The role instructions are ordinary project data in
`prompts/ace/role_skills/`. They are loaded by Delphyne queries, so they work
from both Codex and Claude Code without installing a harness-specific
plugin. Generator tools are held fixed in this experiment: the prior
snippet and resource-completion campaigns did not justify repeating those
treatments.

## Architecture and reproduction

Strategies own the evidence/decision contracts and tool limits; policies
own model selection, prompting, search and financial admission. Rocq work
uses Compute, and demonstrations are executable specifications. This
follows the separation described in the
[Delphyne paper](https://arxiv.org/abs/2502.05310). The explicit
generator/reflector/curator handoff tests an implementation mechanism of
[ACE](https://arxiv.org/abs/2510.04618), not the proposition that any larger
context or additional tool necessarily improves results.

From `examples/omphalos`, either harness can run:

```bash
source ~/.config/omphalos/env.sh
pytest -q tests/test_ace_roles.py tests/test_ace_roles_reporting.py
```

The recorded 36-cell pilot replay and 120-cell receipt audit remain valid.
Full-campaign audit/replay/report commands currently refuse unresolved
billing and incomplete validation; do not reset the ledger to bypass that.

Audit and replay run only on terminal campaign stages. Audit performs exact
real-Rocq rechecks of retained receipts; replay forbids HTTP and checks
transport state, results and budgets against the paid measurements. Their
jobs are different: cached replay does not re-execute the verifier.
The campaign's seal prevents changing measured code or prompts in place.

Known measured limitation: a reflector that supplies both a proposed
snippet and an abstention reason receives the generic message “A proposed
draft needs exactly one supplied event.” In one pilot, that feedback failed
to identify the actual conflicting fields, wasting the remaining turns.
The original failed job is preserved. A future version should use an
explicit proposal/abstention discriminant and field-specific feedback;
that revision is implemented separately in v2 and is not included in this
campaign's measurements.

The strict development guard excludes testX, protected challenge data,
mixed reports and unrelated archives before experiment imports. Do not
replace these commands with aggregate partition, repricing or Ladon CLI
commands while that closure applies.
