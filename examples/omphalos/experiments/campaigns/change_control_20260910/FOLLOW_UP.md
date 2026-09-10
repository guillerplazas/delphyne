# Checked change control: completed local screen

All 24 registered trainX local episodes completed for **$0.15247908**:
41 settled requests, zero platform failures, retries, censoring, teacher
calls or unresolved charges. The $3 ceiling was not a spending target.
No full train or validation problems were run. The retained bounded
money+focused reference remains recommended.

## Primary comparison

| Luna medium arm | Correct applicability | Useful transitions | API cost | Cost/useful |
| --- | ---: | ---: | ---: | ---: |
| Fixed demonstrations (F) | 3/6 | 1/6 | $0.02441020 | $0.02441020 |
| Checked control (C) | 6/6 | 2/6 | $0.01390688 | $0.00695344 |

The practical local gate passed: C resolved all four convertible and two
nonconvertible decisions, enabled verified induction and IMO 1983 progress,
lost no F useful transition, and saved 43.03% total cost and 71.51%
cost/useful. Cost ratio 0.570, descriptive family-bootstrap 90% interval
[0.462, 0.694], family-clustered two-sided p=0.03125. Useful-progress
difference +1/6 has p=1 and descriptive 90% interval [0, 0.5]. Six inspected
families at one seed cannot establish a coverage guarantee or transfer.

F used 18 requests versus C's 11. The six removed applicability requests
cost $0.00695244, accounting for 66.19% of the total saving. The remainder
compares 12 F ordinary requests with 11 C ordinary requests. This is evidence
for verification/control and a narrower decision process, not better model
reasoning or ACE. Checking the known canonical candidate replaces a query;
it does not add a preflight followed by duplicate verification.

The useful induction and IMO 1983 continuations finish from saved prefixes.
These are not qualified full-problem solves. The Rsqr exact-H witness also
works before change and therefore is not evidence of enabling progress.
Generic statistics fields named solved_a/solved_b refer to the endpoint
being compared: useful local progress here, decision correctness below.

## Terra and effort diagnostic

All three settings used the same fixed-demo applicability phase. Each made
one request per state and none used the available inspection tools.

| Setting | Correct decisions | Applicability-phase cost |
| --- | ---: | ---: |
| Luna medium (reused F phase) | 3/6 | $0.00695244 |
| Terra low | 4/6 | $0.05430900 |
| Terra medium | 4/6 | $0.05985300 |

Terra low corrected all four positive cases but abstained on neither
negative. Medium correctly abstained on the INR-3 negative but falsely
abstained on the convertible Rsqr case; it still attempted the nonconvertible
real-power correction. Both Terra settings corrected IMO 1983, missed by
Luna. Medium cost 10.21% more than low without improving the aggregate count.

Against Luna, low/medium cost ratios are 7.81/8.61, with descriptive 90%
intervals [6.67, 8.82]/[6.77, 10.27]. Both cost comparisons have raw p=0.03125
and Holm-adjusted p=0.09375. All three correctness contrasts have raw and
adjusted p=1. Medium-versus-low cost p=0.25. These tiny-panel observations
do not select a stronger model or effort level. Terra episodes deliberately
have no ordinary continuation: their reported useful=0 is not a solve result.

## Response-contract limitation

The inherited exact-full-script-prefix contract rejected seven ordinary
responses before kernel checking (F: three; C: four). The offline
prefix_audit.json records their first mismatches; none retained a
token-equivalent complete required prefix. Two C responses returned only a
suffix, including the locally known valid exact-H answer; others changed
earlier proof steps. Rejection does not establish mathematical invalidity.
Official scores remain unchanged. A suffix interface would be a separate
common engineering correction, requiring a new version and freeze rather
than retrospective rescoring or an ACE claim.

## Decision and authorization boundary

No adaptive arm or further model/effort sweep is supported. Existing Rocq
checks suffice for the narrow conversion decision. The next research
question is transfer and full runtime cost of controlled continuation.
The conditional 18-cell full train comparison (six problems, seed 0,
C/F/retained reference; proposed $2 ceiling) requires separate approval.
Eventual fresh paired validation is 160 cells and requires another freeze
and approval. Full X caps remain $0.10; reset episodes and Terra's local
reservation allowance are not full-problem budgets. Deployment still requires
at least 15% lower total cost and cost per qualified solve with no observed
coverage loss. This local screen cannot establish that target.

Further ACE research needs a concrete adaptation mechanism that improves
over these same fixed demonstrations and checks. Current evidence instead
supports examining representations and controlled search, particularly the
full-prefix response contract. Do not broaden into unrelated missing-reference
or normalization categories based on this result.

## Validation and provenance

Omphalos make test (including new pure and live Rocq tests), local Pyright
1.1.409, touched-file pinned 1.1.406 checks, Ruff, applicability demos and
post-run repricing passed. Root make pyright passes core and then reports
the recorded 17 unrelated why3py.simple errors; none were changed. All 41
receipts reprice exactly. Frozen sources have zero drift.

See registration.json and sealed.json for the immutable protocol;
report_primary.json, report_terra.json and final_report.json for measurements;
receipts_primary.csv and receipts_terra.csv for charges; checks.json for
verification. Previous paid campaigns remain unchanged. Work is staged and
uncommitted, preserving pre-existing changes and .vscode/settings.json.
