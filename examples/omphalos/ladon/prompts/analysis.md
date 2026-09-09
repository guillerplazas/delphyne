# Ladon analysis session — hint $hint_n (class A, offline), night $date

## The hint

$hint_context

## The plan entry

$plan_entry

## Your task

This hint is answerable offline: from archived cells, caches and the
existing tools (`tools/reports/ace_cap_report.py`, `tools/analysis/budget_ablation.py`,
`tools/analysis/replay_with_budget.py`, `tools/analysis/failure_analysis.py`,
`tools/analysis/decision_audit.py`, `tools/analysis/cell_records.py`) — no API spend, no
Rocq launch. Do the analysis, write the artifact, and stop.

1. Run the relevant tools (read their module docstrings first). Write
   any new script you need under `$hint_dir/` (never under `tools/`).
2. Write `$analysis` (markdown): the question, the exact commands and
   inputs, the numbers (paired per cell where applicable, never pooled
   sums alone), the answer, and a **recommendation**: what arm, if any,
   should be built from this, and what it would cost.
3. Write `$notes` with a `## New hints` section (`- [tag] Title — body`
   per idea, or `- none`).
4. Write `$arm_yaml`:

```yaml
hint: $hint_n
class: A
title: "<short title>"
summary: "<one sentence answer>"
analysis: $analysis
touched: [<files you created or modified, relative to examples/omphalos>]
ready: false
```

You have at most $max_turns turns. Write a first version of
`$analysis` as soon as you have any numbers and refine it as you go —
a session that runs out of turns with nothing written counts as no
result. Keep the last ten turns for `$notes` and `$arm_yaml`. Do not
modify product code.
