# ACE investigation — short report

September 21, 2026. **All 2,044 planned solver attempts are finished. There are no pending paid experiments.** Luna remained the solver throughout; stronger models were used only to prepare playbooks. Only trainX and validationX were used.

## What we achieved

The strongest version is **O1: let the agent use and improve its playbook during training, then freeze the final playbook for solving**. Its authors are Sol-medium; its solver is Luna.

Each comparison below covers forty problems, each attempted twice. Costs include unsuccessful attempts and exclude the one-time preparation fee.

| Comparison | Ordinary baseline | O1 | Cost reduction |
|---|---:|---:|---:|
| trainX, both at $0.10 allowance | 63 solves; $1.71480 | 64 solves; $1.49240 | **12.97%** |
| validationX, both at $0.10 | 56 solves; $1.75434 | 56 solves; $1.67464 | **4.54%** |
| validationX, baseline $0.10 / O1 $0.05 | 56 solves; $1.75434 | 55 solves; $1.47902 | **15.69%** |

**We reached the practical 10% serving-cost target on trainX at the same budget.** We also reached it on validationX by combining ACE with a lower stopping allowance, losing just one solve out of eighty attempts—within your accepted trade-off.

The attribution matters: lowering the ordinary baseline's allowance alone saves **11.86%** on validationX. O1 adds **4.35% savings against that lower-budget baseline**, at equal coverage. The full 15.69% is therefore a joint ACE-and-budget result. At equal $0.10 allowance, the measured validation ACE effect remains 4.54%.

TrainX tests reuse of familiar problems. ValidationX tests transfer within a repeatedly used development set. These are useful measured results, with uncertainty: O1's same-budget train saving has a 90% interval of −1.53% to +26.11%. Neither partition establishes a universal 10% improvement on untouched problems.

## Why previous results were disappointing

**Savings on successful proofs were being erased by expensive failures.** With the full fixed-source Sol book, shared successful validation attempts become cheaper, but large error messages and lost solves make the overall bill 9.13% higher. Even O1 still spends 71% of its validation bill on failures.

**Some learned advice was incorrect, even with strong authors.** Executable checks found wrong tactic ordering and unsupported explanations. Correcting three rules produced R1: 10.60% less cost and four extra train solves at a matched $0.09 allowance. That useful result includes manual repair and cannot be presented as fully autonomous ACE.

**Small pilots and mismatched controls gave misleading impressions.** The short Sol book initially saved 57.41%. On new attempts of those same twelve problems, it instead cost 48.63% more and solved five fewer. Historical controller and output-cap changes also explained some apparently large ACE advantages. All these unfavorable results remain in the report.

## Which direction has the strongest evidence

Keep **O1's adaptive training and frozen serving**, and focus learning on expensive failures with **compiler-checked repair examples**. We already demonstrated short valid repairs for the costly LCM theorem, an induction ruined by expansion, and a missing proof dependency. Two shared-failure regressions account for more than the remaining $0.0957 needed to reach a same-budget 10% validation saving. That identifies a concrete target; it does not claim those dollars have already been recovered automatically.

Combine that work with the tested stopping-budget choice and shared parser/feedback repairs. Larger authors alone are insufficient: the full Luna-authored book is competitive with the full Sol-authored book, while costing 91.70% less to prepare.

## Cost and confidence in the evidence

O1 preparation costs **$23.46**, so these are serving savings, not 10% total savings on an eighty-attempt deployment. Under the observed train averages, preparation breaks even after about **8,440 attempts**. The complete research bill is **$317.41–$317.63**; the small interval retains one unknown timeout invoice.

Verification includes **2,040 exact replays**, four separate terminal-failure checks, **1,215 distinct compiled proofs** covering all 1,537 solved outcomes, and **4,560 budget-replay scenarios**. A final statistical review corrected floating-point tie handling without changing any cost, solve count or practical conclusion. No failed outcome was replaced and testX remained closed.

[Full report](long_report.md) · [Evidence and reproduction index](artifact_index.md)
