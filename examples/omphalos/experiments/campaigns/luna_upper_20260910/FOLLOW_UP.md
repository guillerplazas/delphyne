# Luna effort sweep: xhigh ties high; max regresses

All 12 new local trainX episodes completed for **$0.03147888**, with 17
settled model requests, no platform failures, retries, missing/censored cells
or unresolved charges. No teacher calls, full problems or qualified solves.

| Luna effort | Correct applicability | Total phase cost | Cost/correct | Reasoning tokens | Model requests | Tool calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Medium (saved) | 3/6 | $0.00695244 | $0.00231748 | 1597 | 6 | 0 |
| High (saved) | 5/6 | $0.00785130 | $0.00157026 | 2552 | 6 | 0 |
| Xhigh (new) | 5/6 | $0.00877530 | $0.00175506 | 3367 | 6 | 0 |
| Max (new) | 4/6 | $0.02270358 | $0.00567590 | 12107 | 11 | 7 |

Xhigh repairs all four positive cases and correctly abstains on real power,
but attempts the nonconvertible INR-3 change. Compared with high, it fixes
Rsqr and loses INR-3: equal count, different error. Xhigh costs 11.77% more
than high. Max correctly handles induction, large naturals and both negative
cases, but falsely abstains on convertible Rsqr and IMO 1983. It costs 2.89
times high for one fewer correct decision. Neither passes the registered
practical gate of an additional correct decision without regression vs high.

## What max's inspection actually did

Max used seven tool calls across four states (tool_audit.json):

- Induction: InspectProofState replayed the full prefix plus the canonical
  change successfully, then max proposed that correction. This is a direct
  local conversion check using an existing tool.
- INR-3: its first inspection omitted the prefix and failed because a was
  absent. Its second included the prefix and returned Not convertible;
  max correctly abstained. The first tool failure is an unsuccessful attempt,
  not a platform failure, and its request cost is retained.
- Real power: Print pow exposed the recursive definition and max correctly
  abstained. This is relevant definition inspection.
- IMO 1983: Check Rle_0_sqr exposed a square-notation statement; max then
  printed pow and tried Check change, which failed because a tactic is not
  a reference. It falsely abstained without checking the proposed local
  conversion or inspecting Rsqr. This suggests confusion between square
  representations and poorly targeted inspection, not missing capability.

The Rsqr error received no inspection. More effort did trigger existing tools,
but using a tool is not sufficient: it must resolve the relevant local fact.
Successful local inspection also does not by itself count as useful downstream
progress. This experiment has no ordinary continuation and establishes no
full-proof solves or end-to-end savings.

## Uncertainty and decision

All five accuracy contrasts have Holm-adjusted p=1. The unadjusted xhigh
versus medium accuracy p is 0.5; the other four are 1. Descriptive 90% accuracy
effect intervals: medium to xhigh [0, 2/3], medium to max [-1/3, 2/3], high to
xhigh [-1/3, 1/3], high to max [-1/2, 0], xhigh to max [-2/3, 1/3]. Six
inspected families, one seed, historical controls and sequential exploration
prevent strong ranking or equivalence claims.

Cost ratios and descriptive 90% intervals: xhigh/high 1.118 [0.955, 1.351];
max/high 2.892 [2.188, 3.782]; xhigh/medium 1.262 [1.049, 1.547]; max/medium
3.266 [2.642, 4.081]; max/xhigh 2.587 [2.132, 3.133]. Holm-adjusted cost
p values are respectively .375, .15625, .1875, .15625, .15625. None passes
the registered adjusted p<.10 screen. Raw p=.03125 for the three max cost
contrasts does not override the multiplicity rule. Practical costs and
statistical uncertainty are both retained.

High has the lowest observed cost/correct among these four settings; xhigh
has the same aggregate accuracy with a different mistake, and max adds
substantial computation without a gain on this panel. No model promotion or
further expansion follows. The more informative mechanism lead is selecting
the right check and representation: max demonstrates that the existing
inspection can test a canonical change, and also how unfocused reference
inspection can go wrong. This supports controlled verification research,
not an ACE attribution or a broad new tool project.

## Verification and provenance

The first request on all 12 cells matches the saved medium request except
effort; the model is Luna and each receipt uses its correct xhigh/max ledger
allocation. First-request identity does not imply identical later requests:
max's tool use creates extra turns. Frozen sources have zero drift. Run the
offline audit from Omphalos with
python -m experiments.campaigns.luna_upper_20260910.audit_requests.

Omphalos make test, local Pyright, touched-file pinned Pyright 1.1.406 and
Ruff passed. Root make pyright retains the same 17 unrelated why3py.simple
errors. All 17 receipts reprice exactly; historical outputs are untouched.
See report.json, receipts.csv, request_audit.json, tool_audit.json and
checks.json. Work remains staged and uncommitted.
