# Luna high: improved aggregate accuracy with one regression

The user's clarification was Luna, not Terra. This separate diagnostic ran
six Luna high episodes on the same trainX states, seed 0, and compared with
the saved Luna medium fixed-demo applicability phases. All six completed
with six settled requests for **$0.00785130**, no platform failures, retries,
censoring or unresolved charges. No full problems or teacher calls.

| Luna effort | Correct applicability | Total phase cost | Cost/correct | Reasoning tokens |
| --- | ---: | ---: | ---: | ---: |
| Medium (archived) | 3/6 | $0.00695244 | $0.00231748 | 1597 |
| High (new) | 5/6 | $0.00785130 | $0.00157026 | 2552 |

High gained three correct decisions: abstention on both nonconvertible
states (amc12a_2020_p13-27 and imo_1968_p5_1-19), and the repair on
imo_1983_p6-33. It lost the previously correct convertible Rsqr decision on
amc12a_2002_p13-35, falsely claiming conversion was unsupported. Induction
and the large natural-number case remained correct. None of its six requests
used inspection tools. Thus increased effort improved aggregate accuracy,
but did not remove the need to check the precise local fact.

Cost rose 12.93%, while cost/correct fell 32.24%. The preregistered practical
signal required an additional correct decision with no lost correct state;
that gate failed because of Rsqr. The accuracy gain is exploratory, not
statistically established: family-clustered two-sided p=0.625, descriptive
90% effect interval [-1/6, 5/6]. Cost ratio 1.129, descriptive 90% interval
[0.925, 1.308], cost p=0.375. Six inspected families, one seed and historical
controls leave substantial uncertainty; do not interpret a failed gate as
no aggregate improvement or the aggregate improvement as a reliable win.

The actual first requests match medium exactly except reasoning_effort on
all six states; model gpt-5.6-luna is verified in the cache. Input/cached
tokens are identical at 34941/15265. High produced 3009 output tokens,
including 2552 reasoning tokens, versus medium's 2084/1597. The comparison
uses medium's applicability phase only, excluding ordinary continuation.
No downstream continuation was run for high, so useful progress, qualified
full solves and end-to-end savings remain unmeasured. Cost/correct is not
cost per qualified solve. Generic solved_a/solved_b statistics mean correct
applicability here.

This is a more encouraging effort result than the Terra check. Keep Luna
high as a possible comparator if another independently justified mechanism
or transfer study is approved; do not promote it or automatically sweep
xhigh/max on this panel. Explicit checked control still made all six local
applicability decisions correctly in the earlier campaign. That observation
supports checking/control, not ACE, and comparisons of continuation cost
require a matched continuation experiment. The full-problem deployment
target remains >=15% lower total cost and cost per qualified solve with no
observed coverage loss; this diagnostic cannot establish it.

Omphalos make test, local Pyright, pinned touched-file Pyright 1.1.406 and
Ruff passed. Root make pyright retains the recorded 17 unrelated
why3py.simple errors. Six receipts reprice exactly and frozen sources have
zero drift. See report.json, receipts.csv, request_audit.json and checks.json.
Older campaigns remain unchanged; work is staged and uncommitted.
