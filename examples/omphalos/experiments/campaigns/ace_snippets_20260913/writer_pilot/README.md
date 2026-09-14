# Curator and reducer tool-use pilot

Authorized by Guille's request to test the reducer, curator, or other ACE
components most likely to benefit. This follow-up preserves the completed
snippet campaign. Its first stage is twenty fresh writer jobs: eight curator
sources and two reducer batches, each crossed with current prompt and one
opt-in draft-aware contender. Both get identical historical drafts and X3 book.
The roles are tested independently; this does not measure a chained adaptation.

The intervention preserves typed unverified drafts, separates role instructions,
adds explicit per-draft decisions and selects an applicable writer demonstration.
All retained executable code still comes from exact bounded Rocq receipts.
`reduction_input` preserves drafts and receipts between these writer roles;
its actual curator-to-reducer path is covered by a scripted real-Rocq test.

Each cell permits four requests, three probes and $0.20. Seed0 costs at most
$4, including $2 of fresh controls. Only a registered useful-edit advantage can
open an identical seed1 stage costing at most another $4. The original ledger
contains $5.12989540 before this follow-up, so the worst cumulative total is
$13.12989540 under the original $30 ceiling. The $4.38640002 contingency
allocation is untouched. There are no extra source generators, embeddings,
proof panels, diagnostics or automatic retries. Unknown charges stop progress.
Codex-session cost is unavailable from the experimental ledger.

Primary outcome is useful checked source corrections surviving the existing
merge, with failures retained in the denominator. The utility rubric was
written before outcomes. Report role/source coverage, spending, cost per useful
correction, exact-check outcomes, and all relevant tool dispatches. More calls
alone cannot pass. These two reused source batches cannot establish general
coverage gains or justify default promotion; related families and repeated
seeds remain clustered. See the driver docstring and protocol.json for gates.

Both Codex and Claude Code run the same commands from examples/omphalos:

```sh
python -m experiments.writer_draft_experiment prepare
python -m pytest -q tests/test_writer_drafts.py
python -m experiments.writer_draft_experiment seal
python -m experiments.writer_draft_experiment campaign 0
python -m tools.reports.writer_draft_results audit 0
# Record utility_review_seed0.json against the frozen rubric, then:
python -m tools.reports.writer_draft_results finish 0
# campaign 1 is authorized only if gate_seed0.json expands.
```

Only the campaign/run-batch commands dispatch API requests. Use the supplied
supervised launcher inside tmux on i34-gpu01, sourcing
`~/.config/omphalos/env.sh` in that tmux shell. Never rerun preparation after
payment. All experiment imports install the development-only guard first.
Keep testX, protected evidence, mixed history and memory index closed.
