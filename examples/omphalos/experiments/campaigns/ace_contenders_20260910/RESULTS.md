# ACE contender benchmark results — 2026-09-10

**The xhigh-reflector contender is the stronger of the two tested combinations.**
Against the flagship it offers lower cost with some loss of coverage. The
medium-reflector contender is worse on both coverage and cost. These findings
come from all 160 authorized new cells; no pilot gate stopped this comparison.

## Configurations and measured outcomes

Both contenders use Luna-xhigh proof generation, Luna-medium curation/reduction,
audit off, and their previously frozen playbooks. They differ in reflector
effort. The historical flagship uses its original book and Luna-medium prover.
Money+focused and all proof limits are held fixed. One seed (0) per problem.

| Partition | Arm | Qualified solves | Inference cost | Cost/solve |
|---|---|---:|---:|---:|
| trainX | reference | 28/40 | $0.689223 | $0.024615 |
| trainX | reflector-medium | 26/40 | $0.693521 | $0.026674 |
| trainX | reflector-xhigh | 27/40 | $0.581698 | $0.021544 |
| validationX | reference | 27/40 | $0.667228 | $0.024712 |
| validationX | reflector-medium | 19/40 | $0.740325 | $0.038964 |
| validationX | reflector-xhigh | 24/40 | $0.586013 | $0.024417 |

The xhigh-reflector contender saves **15.60%** on trainX, losing one solve,
and **12.17%** on validationX, losing three solves. Cost/solve falls by
12.47% and 1.19%, respectively. That is a measured cost/coverage trade-off,
not increased coverage. It may be useful where lower spend matters more
than preserving every solve; it is not a coverage upgrade over the flagship.

Across the two partitions descriptively: flagship **55/80, $1.356452**;
medium-reflector **45/80, $1.433846**; xhigh-reflector **51/80, $1.167711**.
The latter saves **13.91%** overall and **7.16% per solve**, with four fewer
solves. Do not treat the pooled number as independent confirmation.

The xhigh reflector beats the medium reflector on both partitions: +1 and
+5 solves, at 16.12% and 20.84% less inference cost. On validation it has
five unique wins and no losses versus medium reflection (descriptive paired
p=.0625). Thus assembling the isolated eight-problem role-screen winners
would have missed the stronger combination. Downstream interaction testing
was useful even though the original pilot selection gate was not met.

## Uncertainty and historical controls

| Comparison versus flagship | Coverage difference | Descriptive 90% interval | Coverage p | Cost ratio (90% interval) |
|---|---:|---:|---:|---:|
| trainX, reflector-medium | -5.0 pp | -15.0 to +5.0 pp | 0.6875 | 1.006 (0.858–1.221) |
| trainX, reflector-xhigh | -2.5 pp | -12.5 to +7.5 pp | 1.0000 | 0.844 (0.750–0.968) |
| validationX, reflector-medium | -20.0 pp | -30.0 to -10.0 pp | 0.0156 | 1.110 (0.958–1.317) |
| validationX, reflector-xhigh | -7.5 pp | -17.5 to +0.0 pp | 0.3750 | 0.878 (0.771–1.017) |

Validation p-values above apply Holm correction to the two planned comparisons
against flagship; training p-values are descriptive. The medium-reflector
validation deficit has statistical support (adjusted p=.015625). The xhigh
deficit remains uncertain (adjusted p=.375). TrainX xhigh cost savings have
descriptive paired p=.0598; validation cost p=.1554. Statistical uncertainty
does not erase the observed trade-off, and absence of significance is not
evidence of equal coverage.

References were selected before new calls: all forty model-suite incumbent
trainX cells and forty seed-0 polish-campaign validation reference cells.
Their effective strategy/policy arguments and receipt costs were checked.
The latter archive has a different inactive claims artifact; neither admission
nor polished is enabled, so those claims are never consumed. Hash-pinned
references.json preserves provenance. Controls are historical, not concurrent
randomization. trainX and repeatedly used validationX are development data.

## Spend, preparation and implementation

New spend **$2.60155656**, 1,861 settled requests, 160/160 new cells, zero
platform failures, retries or unknown charges. Together with the original
suite: **$11.31879656**, within the original $30 authorization. No new
reference runs, second seeds, role adaptation, max sweep or protected outcomes.

Previously paid preparation is reused, not charged again: medium-reflector
$0.203013 and xhigh-reflector $0.249932 including common source trajectories.
At the measured validation inference means, incremental preparation amortized
over 100/1,000 uses yields medium $0.020538/$0.018711 and xhigh
$0.017150/$0.014900 per problem. These projections do not restore lost coverage.

The shared guidance now distinguishes pilot promise, practical trade-offs,
statistical evidence and default promotion. Missed small-panel gates are not
blanket vetoes on authorized follow-up, and requested cell counts are respected.
The historical model-suite verdict is preserved. Default configuration was
not automatically changed.

Omphalos make test, three new scope/attribution regressions, Ruff and pinned
new-code Pyright pass. Root Pyright retains seventeen existing errors.
Changes are staged and uncommitted.

[Protocol](README.md), [machine-readable results](final_report.json),
[per-cell data](cells.csv), [receipts](receipts.csv),
[completion audit](completion_audit.json), [references](references.json).
