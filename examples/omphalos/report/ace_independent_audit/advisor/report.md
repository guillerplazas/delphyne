# ACE: final results for the thesis cost objective

**Advisor brief · 21 September 2026**

- **Objective:** at least 10% lower serving cost than an equivalent ordinary agentic pipeline, allowing a small coverage trade-off.
- **Evidence:** completed campaign results plus one explicitly matched historical comparison, independently audited here. Every comparison has **80 attempts: 40 problems × two replicates**. Costs include failures; preparation is separate. No pilot results are included.
- **Models:** the solver is always **Luna-medium** (`gpt-5.6-luna`). Where indicated, **Sol-medium** (`gpt-5.6-sol`) generates the playbook; it never solves benchmark attempts.

## 1. Results above 10% with equal stopping budgets

- **O1: 12.97% lower cost on trainX; 64 versus 63 solves.**
  $1.49240 versus $1.71480; both pipelines use a $0.10 stopping allowance.
  - **Recipe:** Luna uses an evolving playbook over forty training problems; Sol reflects and curates after each attempt. The final book is frozen for evaluation.
  - **Caveats:** uses stronger authors. TrainX measures familiar-problem reuse. On validationX, the same-budget saving is **4.54%, with 56 solves on both sides**. Preparation costs **$23.46**, excluded from serving savings.

- **R1: 10.60% lower cost on trainX; 66 versus 62 solves.**
  $1.52290 versus $1.70339; both pipelines use a $0.09 stopping allowance.
  - **Caveats:** a **manual diagnostic**, correcting three rules in a Sol-authored book; not fully autonomous ACE. The $0.09 result is a controller replay of completed trajectories. It does not compare ACE against a higher-budget baseline.

- **Historical ACE with reset: 11.19% lower validationX cost; 50/80 solves on both sides.**
  $1.65575 versus $1.86442 at the study's common tariff; the same session reset is applied to both pipelines.
  - **Caveats:** Luna-only; **historical paid runs, audited rather than rerun in this campaign**. Against the ordinary baseline without reset, this configuration saves only **1.05%**, with 50 versus 47 solves. The 11.19% is specifically the matched-reset comparison.

![Equal-budget comparisons. Intervals resample theorem clusters, retaining both replicates. The historical row is explicitly distinguished from the new campaign.](same_budget.pdf){width=100%}

- **Interpretation:** these observed savings cross the practical 10% target, but the 90% intervals include zero. They do not establish a general 10% reduction on new problems.
- **Leading recipe:** O1 is the strongest autonomous result at the original matched budget. Its gains occur with the same existing verifier assistance available to both ACE and the ordinary baseline.

\newpage

## 2. Results above 10% when ACE is combined with budgeting

**All comparisons below use a $0.05 contender versus its ordinary $0.10 baseline.**

![Budgeting accounts for a substantial share of the total saving. Both bar components use the original baseline bill as denominator, so they add exactly.](budget_decomposition.pdf){width=100%}

- **O1: 23.24% lower trainX cost at equal 63/80 coverage; 15.69% lower validationX cost with 55 versus 56 solves.**
  - **Caveats:** Sol authors; joint ACE-and-budget result. Lowering the ordinary baseline's budget already saves **16.59% / 11.86%** on trainX / validationX. Against those equally reduced-budget controls, O1 saves **7.97% / 4.35%**, respectively.

- **S1: 19.43% lower trainX cost; 61 versus 63 solves.**
  - **Caveats:** **Luna in every model role**, but most savings come from budgeting: the matched-$0.05 ACE saving is **3.40%**. The corresponding joint validation saving is only **1.49%**, with 55 versus 56 solves. Preparation costs **$1.76**. S1 uses fixed training trajectories; an all-Luna version of O1's adaptive recipe was not evaluated.

## 3. Main findings and direction

- **Expensive failures remain the main cost target:** unsuccessful attempts consume **71% of O1's validation bill**. Better proof trajectories alone do not guarantee lower total spending.
- **Luna-only preparation is much cheaper:** S1 costs **$1.76** to prepare versus **$21.16** for the corresponding fixed-source Sol book: **91.70% less**. This reduces preparation overhead; it is separate from benchmark serving savings.
- **Next direction:** retain O1's adaptive training and attach compiler-checked evidence to lessons about costly failures. Report budget improvements separately from matched-budget ACE improvements.
- **Limits:** budget figures replay the actual controller with recorded responses and cache charges; they are not new model draws. TrainX is familiar data; validationX is reused development data. Cache/account timing affects comparability. Serving gains exclude preparation: O1's same-budget train estimate needs approximately **8,440 served attempts** to repay preparation. TestX remained closed.

**Evidence:** [complete serving results](../serving_results.csv), [budget results](../budget_frontier.csv), [matched historical comparison](../historical_matched_comparisons.json), and [reviewed statistics](../statistical_review.json). Figure coordinates and source hashes are supplied in [figure_data.json](figure_data.json).
