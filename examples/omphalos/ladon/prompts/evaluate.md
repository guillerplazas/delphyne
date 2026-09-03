# Ladon evaluation session — hint $hint_n ($title), night $date

Ladon measured the arm and decided **$outcome** by rule `$rule`:
$reason. You write the record. You do not re-decide, and you do not
compute statistics: every number below is authoritative.

## Numbers (ladonX, paired per cell against `experiments/output/x_ladon_agentic`)

$numbers

## What the implement session did (`notes.md`)

$notes

## Diff stat

$diffstat

## House style — two real PROGRESS.md bullets

$progress_examples

## House style — two real HINTS.md entries

$hints_examples

## Return JSON with these fields

- `progress_bullet`: one PROGRESS.md bullet in the house style,
  starting with `- **Hint $hint_n — <title>** (` followed by the output
  directory name and `, class $hint_class):`; 4–10 sentences: what was
  changed and why, the numbers, the verdict and what it means, the
  discordant cells worth naming, the cost. One paragraph, no line
  breaks — Ladon wraps it.
- `hints_marker`: the numbers phrase for the HINTS.md status marker,
  at most 120 characters, no square brackets, e.g. `57 vs 54 (4–1,
  p=0.38), cost ×0.93 — underpowered`.
- `new_hints`: the notes' "New hints" plus anything the result itself
  suggests, each `{tag, title, body}` (tags: prompt, tool, policy,
  experiment, demo, upstream, process, method); `[]` if none.
- `commit_body`: three short paragraphs headed `Idea:`,
  `Implementation:`, `Result:` (used verbatim in the commit on KEEP).
- `human_note`: one or two sentences for the morning report — what to
  look at and what to decide; for INSPECT, what a Fable session should
  try next.
