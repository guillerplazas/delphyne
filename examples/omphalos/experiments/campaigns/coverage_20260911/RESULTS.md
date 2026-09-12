# Fixed-book coverage results — 2026-09-11

Completed all 240 planned cells. D solved **31/40 testX versus 30/40** for the
fresh flagship, with no losses, at **9.1% higher total cost** and 5.5% higher
cost per solve. Preserve this observed +1 signal, but its extra solve received
no new example: it does not establish demonstration-driven improvement.
Validation was 26/40 D, 25/40 E, versus historical flagship 27/40.
Keep both implementations opt-in and retain the flagship default. This is an
attribution/reach limitation, not a rejection based on a significance gate.
No further runs were purchased.

## Complete-panel results

| Partition | Arm | Solved / 40 | Total API $ | $ / solve |
|---|---|---:|---:|---:|
| trainX | D: demos | 26 | 0.703147 | 0.027044 |
| trainX | E: exploration | 26 | 0.696616 | 0.026793 |
| trainX | Flagship (historical) | 28 | 0.689223 | 0.024615 |
| validationX | D: demos | 26 | 0.629711 | 0.024220 |
| validationX | E: exploration | 25 | 0.675583 | 0.027023 |
| validationX | Flagship (historical) | 27 | 0.667228 | 0.024712 |
| testX | D: demos | 31 | 0.521671 | 0.016828 |
| testX | Flagship (fresh) | 30 | 0.478305 | 0.015944 |

Experiment total **$3.70503274**, 2,503 settled requests, all 240 fresh cells,
zero retries, platform failures, censored cells or unresolved charges.
Separate authoring: **$0.493695**, six settled requests. Combined cash spend
**$4.19872774**. Historical control costs above are not new campaign spend.

Test D gained `imo_1965_p2` and lost nothing. That gain had no example selection.
Only `mathd_algebra_31` selected a new example (sqrt, four selection events);
both arms left it unsolved. Its final failure was a type mismatch involving
`R` versus `AbsRing`, illustrating why generic sqrt overlap is not enough.
Among nine unsolved D test problems, cached syntax errors affected six, unknown
references four, and no-witness/subproof-incomplete errors three each.
These test observations are descriptive and supplied no edits or examples.

Test paired coverage difference is +2.5 percentage points; the descriptive
family bootstrap 90% interval is [0, +7.5] points, based on just one discordant
family (two-sided exact p=1). This sparse interval is not a generalization
guarantee. Total-cost ratio is 1.091, descriptive 90% interval [0.942, 1.280].
Validation D difference was -2.5 points, interval [-10, +5], cost ratio .944,
interval [.844, 1.063]. These uncertainties qualify the estimates rather
than automatically discarding useful ideas.

The next useful work is training-only selector relevance and trigger/tool-turn
calibration, using the recorded failures before another full benchmark. The
verified demo bank and Delphyne exploration implementation remain available.
Do not train on the held-out test gain or its failures.

## What changed

The incumbent is ACE bounded **money + focused**, Luna medium, the fixed X3
playbook (`ace_x3_offline.yaml`, SHA-256
`1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067`),
$.10, 64 requests and 300 verifier seconds per problem. Admission and restart
arms stay disabled. This campaign changes no ACE learning or playbook content.

**D — focused demonstrations (#10).** Six verified training examples for
representation bridges and structural reasoning, selected by matching symbols
and query type, at most one example, with source-family exclusion. Four are
complete proofs; two are explicitly partial. Unmatched queries retain the
legacy selector. New examples are visible only to D.

**E — bounded exploration (#35).** At the first repeated-state stall (k=4),
try a short suffix branch then an alternate opener using Delphyne strategies,
`nofail`, and shared nested budgets: $.025, six requests, 120 verifier seconds;
three requests per branch. Ordinary generation retains its original output
limit; exploration uses 4096 tokens. Resume only from a kernel-checked usable
state. Failed exploration cannot reset the outer deployment budget.

Executable demos cover successful handoff and exhausted fallback. Existing
read-skill/search/inspection tools are reused. The new prompts receive the
unchanged incumbent playbook. Sol-medium supplied six author drafts for
$0.493695 separately from experiments. Four required small offline repairs
(normal forms, explicit lemma arguments, or Lean syntax); exact theorem-wrapper
stripping and all original drafts/checks are preserved. No paid repair reruns.

## Protocol and evidence

Exactly six new runs of 40 cells each, seed 0: D/E trainX, D/E validationX,
then validation-selected D and a fresh flagship testX control. The 80 compatible
historical train/validation control cells are reused, not newly purchased.
Both variants received validation without significance or minimum-effect gates.
D advanced by validation coverage, then cost. No combined arm, pilot, extra seed,
or test-informed edit. Production code/demos were frozen before the first
benchmark request; test statements and selection were frozen before test calls.
The one demo-navigation syntax correction occurred before any benchmark spend
and is explicitly preserved in registration history.

One seed and historical development controls limit causal attribution. Provider
output varies despite the same seed label. Gains and losses without example
exposure must not be attributed to D. Intervals/p-values are descriptive, not
promotion or follow-up gates. Cost curves in each report are retrospective
final-cost qualification, **not measured runs at smaller admission budgets**.

## Mechanism and failure observations

Training D selected new examples on eight problems, all with unchanged solve
status. Its two gains and four losses occurred without selection. Broad INR/nat
matching repeatedly chose a long recurrence proof for unrelated algebra/AM-GM
states. Verified demonstrations exist, but relevant transfer remains unproven.
Training E never dispatched exploration: visible paid histories reached at most
three repeats. I should have checked trigger reach under the bounded runtime
before buying the full run. This does not establish that nested search is
ineffective. The frozen validation run then reached exploration on one problem,
mathd_algebra_282: all six responses requested searches (8/8/1/3/5/1 tool calls),
with no submitted proof or usable return. Both incumbent and E left it unsolved.
Mixed script-plus-tool responses were handled as tool requests; an unused draft
contained admits and was never checked or accepted. Low reach and tool-only
exhaustion are distinct issues to address in future training-only work.

For the 14 unsolved training cells in each arm, cached syntax errors affected
10 problems in both arms; unknown references affected 9 D / 8 E; type mismatch
7 D and unification failure 8 E. Terminal-only counts miss earlier failures.
Validation's most widespread cached failures were syntax (8 D / 7 E), unknown
references (5 D / 6 E), and incomplete proofs (5 each). Verifier error labels
such as prover-crash are proof-check feedback, not launcher/platform failures.
All development cells completed without platform or structured-parser failures.
Per-problem gains/losses, terminal and any-cached failure counts, selected
examples, and actual dispatch diagnosis are in the stage audit JSON files.
No validation/test observation was used to repair these candidates.

## Validation

Omphalos `make test`, 23 focused tests, pinned Pyright 1.1.406 on changed Python
files, Ruff checks/format, live demos and `make reprice` passed. Root
`make pyright` passes core Delphyne, then reports 17 pre-existing errors in
`examples/find_invariants/why3_utils.py` following an unresolved
`why3py.simple` import; the out-of-scope code is unchanged.
