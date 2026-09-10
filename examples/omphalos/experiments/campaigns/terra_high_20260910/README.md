# Terra high-effort extension

The user requested a small check of higher Terra effort on 2026-09-10.
This is a separate six-episode trainX diagnostic, not reuse of the previous
campaign's unused spending authorization. Ceiling $1.20, allocated entirely
to high effort; no retries, teacher calls, additional seeds, full problems,
validation or automatic expansion. The executable module's docstring and
registration.json were frozen before launch.

The six saved states, seed 0, canonical order, fixed five-demo bank,
model gpt-5.6-terra, tools, Responses API, temperature unset, 32768 output
limit, four-request limit, verifier limits and $1 local reservation allowance
are unchanged from the previous diagnostic. Only medium becomes high.
Full X problem caps remain $0.10. These are local reset episodes, not full
problems with remaining runtime budgets. All states were previously inspected.

Primary endpoint: correct applicability versus the six archived Terra medium
cells. A practical signal requires at least one additional correct decision
and no loss of a previously correct state. Terra low is a secondary comparator.
Report all-cell cost and cost/correct separately. Family-clustered two-sided
p<0.10, Holm over two contrasts per endpoint, descriptive 90% intervals.
Keep platform failures and unsuccessful attempts in the six-cell denominator;
missing/censored outcomes prohibit ranking. Unknown is not a refutation.
No solve/coverage or deployment claim follows from applicability correctness.
Historical controls are economical but leave run-to-run and timing confounds.

Implementation reuses ChangeConfig and the frozen change_episode strategy;
there is no policy, prompt, tool or budgeting redesign. Local configuration
checks established that all six configurations differ only in arm label and
effort, retain diagnostic_only=True, and keep four requests. Local stdlib and
Omphalos model schemas expose high effort. The supervised launcher runs one
worker in tmux with the campaign ledger, using the same commands from Codex
or Claude Code. launch.json records the command. Old campaigns are read-only.

The local practical signal is exploratory. The savings-first deployment
criterion remains >=15% lower full total cost and cost/qualified solve with
no observed coverage loss. No model promotion or full-problem runs are
covered by this check. Further effort levels are not automatically launched.
