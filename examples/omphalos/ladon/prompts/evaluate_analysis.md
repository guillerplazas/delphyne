# Ladon evaluation session — hint $hint_n ($title), night $date

Ladon ran this hint as an **offline analysis** (class A): no arm, no
paired cells, no statistics. The session's artifact is below. Ladon
decided **$outcome** by rule `$rule`: $reason. You write the record;
you do not re-decide.

## The analysis artifact

$numbers

## What the session noted (`notes.md`)

$notes

## House style — two real PROGRESS.md bullets

$progress_examples

## House style — two real HINTS.md entries

$hints_examples

## Return JSON with these fields

- `progress_bullet`: one PROGRESS.md bullet in the house style,
  starting with `- **Hint $hint_n — <title>** (offline analysis, class
  A):`; 4–8 sentences: the question, the inputs, the numbers that
  decide it, the answer, and the recommendation (build an arm, or
  close the hint, and why). One paragraph, no line breaks.
- `hints_marker`: the one-sentence answer of the analysis, at most
  120 characters, no square brackets, e.g. `the $0.10 cap never binds
  on ladonX; the lossless floor is $0.06 with 3 % headroom — no change`.
- `new_hints`: the notes' "New hints" plus anything the analysis
  suggests, each `{tag, title, body}` (tags: prompt, tool, policy,
  experiment, demo, upstream, process, method); `[]` if none.
- `commit_body`: leave as the single word `n/a` (nothing is committed
  for an analysis).
- `human_note`: one or two sentences for the morning report: what the
  artifact establishes and what, if anything, Guille should decide.
