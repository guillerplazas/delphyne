# Completed bounded ACE polish assessment

All 224 registered cells were attempted: 24 pilots (including two recorded
implementation failures), 40 frozen trainX cells and 160 fresh validationX
cells. No extra seeds, teacher calls or retries. Actual API cost/liability:
$4.24146774, 2,749 settled HTTP attempts, no unknown charges, no allocation
transfers and no $0.10 per-cell crossings. The $8 ceiling was not a target.

## Complete-panel result

| Panel | Reference solves / cost | Candidate solves / cost |
| --- | --- | --- |
| trainX, seed 0 | Not run | 26/40 / $0.76279972 |
| validationX, seed 0 | 27/40 / $0.66722836 | 26/40 / $0.80152864 |
| validationX, seed 1 | 26/40 / $0.76607986 | 27/40 / $0.71136712 |
| validationX, pooled | 53/80 / $1.43330822 | 53/80 / $1.51289576 |

Cost per qualified validation solve is $0.02704355 for the reference and
$0.02854520 for the candidate. The pooled cost ratio is 1.05553: **5.55%
more cost with equal observed coverage**. Neither preregistered utility
gate passes. Retain original bounded money+focused as the recommended
budget reference; keep the polished implementation opt-in, not promoted.

Family-clustered solve p=1.0; descriptive 90% effect interval -2.5 to +2.5
percentage points. Cost p=0.35545; descriptive 90% ratio interval
0.96041–1.16483. Median paired cost difference is -$0.0000402, mean
+$0.00099484 (90% interval -$0.00074452 to +$0.00273424). The candidate is
cheaper on 44/80 cells, but its costly tails outweigh those savings.
Seed 0 is 20.13% dearer with one fewer solve; seed 1 is 7.14% cheaper with
one additional solve. This disagreement is why both frozen seeds matter.
This is an inconclusive statistical result, not an equivalence claim.
ValidationX remains development data, not a clean holdout.

The four discordant cells are a candidate win on amc12_2001_p21 seed 0,
a loss on imo_1964_p2 seed 0, and opposite outcomes on
induction_prod1p1onk3le3m1onn across seeds. The latter cancels within its
family, leaving two discordant families. Neither unique candidate win
used an output downshift. There were no experiment-platform failures or
administratively censored cells in training or validation; prover-level
resource/unknown outcomes below are a separate measurement.

## Mechanisms and remaining failures

- **Output recovery is weakly targeted.** Nine training cells used it and
  none solved. Seventeen validation cells used it and one solved:
  aime_1984_p7 seed 0, at $0.04237026 versus the reference's successful
  $0.02100072. This is a checked continuation, not incremental coverage.
  There were no truncated API responses. The pilot arm's extra solve also
  did not use downshift. Do not attribute incidental arm wins to this
  mechanism; require a stronger progress signal before another isolated
  experiment (HINTS #123, closed implementation #118).
- **Advice coverage is still coarse.** Matching selected 20 examples
  across 12 validation cells and abstained on 772 focused queries. At most
  one example was supplied per selected query. Valid training actions do
  not automatically transfer to a different proof state. Syntax leakage
  remains: `push_cast in Hgt`, `decide`, misplaced `%R` and malformed
  assertions. An unavailable `positivity` tactic and missing local `Hta`
  also remain. Use tactic/error-shape routing and explicit abstention
  through Delphyne queries/examples, not more broad playbook text (#122,
  #94/#95). No post-validation prompt tuning was performed.
- **Arithmetic needs representation changes, not longer repetition.**
  Examples include sqrt rewrites with no matching subterm, nat/IZR casts,
  division/gcd type mismatches and nonlinear goals that `lia`/`nra` cannot
  discharge. Reuse narrowly matched, Rocq-checked normalization/bridge
  transitions (#94/#110), and the existing large-natural abstraction
  proposal (#72). A stronger teacher should author a missing transition
  only after this targeted training diagnosis, not receive validation or
  protected solutions as adaptation input.
- **Resource and unknown outcomes are not refutations.** Eleven of the
  candidate's 27 unsolved validation cells contain a cached resource or
  unknown outcome (reference: ten of 27). Candidate terminal cached
  outcomes are 16 rejected, four incomplete and seven unknown. Number
  theory 303/37/43 includes expensive `vm_compute` or large naturals and
  server restarts; imo_1984_p6 includes expensive `nia`. Five candidate
  cells explicitly exhausted the verifier allowance. Resource recovery
  stays disabled: its two pilot formatting failures invalidated that
  contrast, despite the subsequent tested formatter repair (#116).
- **Admission is now observable.** Twenty-four candidate validation cells
  have an explicit monetary refusal; refusal need not be the terminal
  event because one reduced continuation may follow. Five explicit
  verifier-exhaustion stops and no output truncations help distinguish
  budget stops from logical failure. Conservatively reserving 32K output
  can stop well below $0.10 actual spend; remaining dollars are not
  evidence that spending them would solve the theorem.

The heuristic last-error categories for candidate failures are structure
9, incomplete 4, syntax 4, resource 4, normal-form 3, type 2 and reference
1. They are not root-cause labels: for example, a closed-server error can
fall into the generic structure bucket. Prefer typed outcomes and explicit
events. Cache records are distinct cached checks, not invocation counts;
the event stream records actual invocations separately.

## Engineering and evidence limits

Typed reservation, sequential verifier preflight, shared Delphyne recovery
budget, matched worked examples, structured adaptation contracts and event
accounting are implemented and tested. The benchmark measures their frozen
bundle; it does not isolate the common typed/preflight controls. Structured
adaptation was tested offline, not evaluated in a paid role-model trial.
New structured contracts are opt-in on `adapt_grounded_transition`; the
legacy batch/iteration interfaces retain their original defaults.

All Omphalos checks pass; root Pyright stops at the existing out-of-scope
why3py.simple dependency after the core passes. Full historical bounded
cache replay has a pre-existing miss reproduced with unmodified HEAD;
only the sampled replay passed. Do not claim complete replay neutrality.
Raw paid outputs and original reports are untouched. Corrected pilot
reader drafts and post-pilot execution changes are explicitly archived.

See `final_report.json`, `failure_audit.json`, `receipts.csv`, `checks.json`
and `retention.json`. Raw caches, logs, SQLite ledger and admission JSONL
remain in the local campaign/run directories; compact evidence is tracked.
Both harnesses use the same Python entrypoints. No testX or protected
challenge problems were evaluated or mined.
