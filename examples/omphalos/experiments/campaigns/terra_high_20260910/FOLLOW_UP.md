# Terra high: no additional applicability gain

Six of six episodes completed with six settled requests for **$0.057621**.
No platform failures, retries, missing/censored cells or unresolved charges.
No full problems, qualified full solves, validation or teacher calls.

| Terra effort | Correct applicability | Total API cost | Cost/correct | Reasoning tokens |
| --- | ---: | ---: | ---: | ---: |
| Low (archived) | 4/6 | $0.054309 | $0.01357725 | 569 |
| Medium (archived) | 4/6 | $0.059853 | $0.01496325 | 980 |
| High (new) | 4/6 | $0.057621 | $0.01440525 | 797 |

High made exactly the same correct/incorrect decisions as medium. It falsely
abstained on amc12a_2002_p13-35 (convertible Rsqr/multiplication) and proposed
a correction on imo_1968_p5_1-19 (nonconvertible real power). It correctly
abstained on the INR-3 case and repaired the other three positive cases.
It did not use any inspection tools. Its explanations asserted the wrong
convertibility facts on the same two cases instead of checking them.

The preregistered practical signal (at least one additional correct decision
without losing an existing correct state) failed. Correctness contrasts
against medium and low both have family-clustered two-sided p=1, also after
Holm adjustment. Against medium all six paired correctness differences are
zero: the descriptive bootstrap interval [0, 0] is degenerate and does not
establish equivalence or precision beyond these six observations. Against
low, the descriptive 90% effect interval is [-1/3, 1/3].

High cost 3.73% less than medium, ratio 0.963, descriptive 90% interval
[0.880, 1.072], adjusted p=0.6875. Versus low, high cost 6.10% more, ratio
1.061, interval [1.029, 1.093], raw p=0.0625 and adjusted p=0.125. These
cost contrasts do not meet the registered p<0.10 after multiplicity control.
The small bootstrap intervals and exact tests need not agree.

The actual cached requests match medium byte-for-structure except the
reasoning_effort option on all six cells (request_audit.json). Input tokens
and cached tokens are identical, 34941 and 15265. High generated 1268 output
tokens including 797 reasoning tokens, versus medium's 1454/980. Increasing
an effort setting did not monotonically increase measured tokens or cost
in this sample. Historical controls, one seed and a diagnostic panel limit
inference; no model selection, equivalence, general Terra limitation or
end-to-end result is established.

Stop here: no xhigh/max sweep or full-problem expansion was launched.
For this precise applicability decision, the observed next step remains
using the existing Rocq check explicitly. The earlier checked-control result
is verification/control evidence, not ACE. Further effort exploration needs
a concrete question beyond repeating this six-state null. The savings-first
full-problem target and separate approval requirements remain unchanged.

Omphalos make test, local Pyright, touched-file pinned Pyright 1.1.406 and
Ruff passed. Root make pyright retains the known 17 unrelated why3py.simple
errors. Every new receipt reprices exactly, and frozen sources have zero
drift. See report.json for outcomes, receipts.csv for accounting, checks.json
for validation, and registration.json/sealed.json for the frozen protocol.
