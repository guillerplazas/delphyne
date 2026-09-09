# Omphalos

Omphalos studies reliable Rocq proof search on miniF2F using Delphyne.
The thesis focuses on **control and budgeting**: how strategies, search
policies, verified feedback and demonstrations affect cost and coverage.

## Start here

From this directory, with the project Python/Rocq environment active:

```sh
make test-unit            # deterministic Python checks, no model calls
make test-rocq            # local Rocq transport checks
make test-luna            # cached canonical example
make test                 # complete local suite and cached examples
make reprice              # audit recorded costs from token counts
```

On i34-gpu01, `~/.config/omphalos/env.sh` configures the environment.
See [usage and evaluation](docs/usage.md) for setup, experiment commands,
cache semantics, partition restrictions and verification.

## Strategies and current references

| Strategy | Purpose |
|---|---|
| [prove_standard.py](prove_standard.py) | Propose a whole proof, verify, revise from feedback |
| [prove_agentic.py](prove_agentic.py) | Add Rocq exploration tools and assisted verification |
| [prove_ace.py](prove_ace.py) | Learn and apply playbook advice through typed query roles |
| [prove_stall.py](prove_stall.py) | Stop repeated failed states under a policy cutoff |
| [prove_grounded.py](prove_grounded.py) | Compose verified advice, focused decisions and bounded tool operations |

The canonical cached baseline is Luna, `core`, reasoning `medium`,
Responses API and a $0.05 per-problem stopping budget. X experiments use
$0.10. Historical Terra configurations keep their original defaults so
existing archives retain their identities.

The bounded money+focused configuration is also retained as a budgeting
reference: 25/40 qualified solves at $0.6780 versus X3's 28/40 at $1.5238.
Guille accepted this cost/coverage trade-off; the original no-fewer-solves
experimental gate still failed. See the [ACE findings](docs/ace_review.md)
and [recorded acceptance](experiments/campaigns/ace_bounded_20260908/acceptance.json).

## Layout

| Directory | Contents |
|---|---|
| `ace/` | Playbooks, evidence, triggers, repair mining, storage and deduplication |
| `runtime/` | Rocq bridge, model/pricing registry, skills, budgets and shared paths |
| `prompts/` | Baseline, ACE and grounded templates grouped by query role |
| `demos/`, `commands/` | Executable demonstrations and cached command examples |
| `experiments/` | Baselines, ablations, ACE, Ladon, smoke entrypoints and shared configuration |
| `tools/` | Offline analysis, reports, data preparation and maintenance utilities |
| `tests/` | Deterministic unit and Rocq tests with their fixtures |
| `docs/`, `report/` | Usage/research documents and presentation reports |
| `benchmarks/`, `miniF2F/` | Partition definitions and the categorized Rocq benchmark |
| `ladon/` | Overnight orchestration, its instructions and historical night records |
| `memory/`, `papers/` | Local shared agent memory and reference papers |

`experiments/output/`, `experiments/previous/` and frozen playbook/campaign
artifacts are paid research evidence. Their paths and contents are preserved.
Scripts run as packages from this directory, for example
`python -m tools.analysis.decision_audit`; Make targets remain stable.

## Reading and development

- [Usage](docs/usage.md): current commands and evaluation conventions.
- [ACE findings](docs/ace_review.md): the completed review and bounded study.
- [Thesis proposal](docs/thesis_proposal.md): the dated original research plan.
- Local-only [PROGRESS](PROGRESS.md): curated milestones and outcomes.
- Local-only [thesis decisions](docs/thesis_decisions.md): design alternatives,
  evidence, trade-offs and corrected interpretations for writing.
- Local-only [HINTS](HINTS.md): unresolved improvements only;
  [closed hints](docs/CLOSED_HINTS.md) preserve their outcomes and IDs.
- Local-only [LINKS](docs/LINKS.md): references still needing study.

Both Claude Code and Codex use the canonical `AGENTS.md` instructions and
shared `memory/` index. `CLAUDE.md` is a symlink, never a second copy.
`make codex-setup` installs the existing profile; `make agents-check`
checks the shared setup. Ladon nights remain Claude-only; both harnesses
can inspect their records and run deterministic tests.

## Provenance

The 488 categorized problems derive from
[LLM4Rocq/miniF2F-rocq](https://github.com/LLM4Rocq/miniF2F-rocq).
The standing architectural reference is the
[Delphyne paper](https://arxiv.org/abs/2502.05310).
Benchmark statements and vendored Rocq reference material are not edited
as part of ordinary Omphalos development.
