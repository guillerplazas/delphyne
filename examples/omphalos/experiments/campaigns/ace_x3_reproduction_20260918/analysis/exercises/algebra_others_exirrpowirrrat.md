# algebra_others_exirrpowirrrat

All registered attempts, including failures. Costs include cache writes.

| Panel | Replicate | Solved | Cost | Requests | Last checked failure |
|---|---:|---:|---:|---:|---|
| historical_none | 0 | 0 | $0.043267 | 24 | (-32003, 'Coq: No matching clauses for match.') |
| historical_x3_seed0 | 0 | 0 | $0.040260 | 32 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| historical_x3_seed1 | 1 | 0 | $0.038390 | 22 | (-32003, 'Coq: In environment\ns := sqrt 2 : R\np, q : Z\nHq : q <> 0%Z\nHeq : s = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nThe term "sqrt (2 : R)" has type "R" while it is expected  |
| previous_ace_historical | 0 | 0 | $0.067417 | 62 | (-32003, 'Coq: Unable to find an instance for the variable r.') |
| previous_ace_selected | 0 | 0 | $0.071413 | 39 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| previous_nonace_matched | 0 | 0 | $0.075891 | 30 | (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHs : (sqrt (2 : R))²%R = (2 : R)\nHqR : IZR q <> 0%R\nHpq : (IZR p * / IZR q * (IZR p * /  |
| previous_nonace_ordinary | 0 | 0 | $0.042098 | 21 | (-32003, 'Coq: In environment\nHsq : (sqrt 2)²%R = (2 : R)\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nHs : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\nThe |
| previous_nonace_ordinary | 1 | 0 | $0.037725 | 23 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| previous_nonace_matched | 1 | 0 | $0.072920 | 39 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| previous_ace_selected | 1 | 0 | $0.067419 | 30 | (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHs2 : (IZR p * / IZR q * (IZR p * / IZR q))%R = 2%R\nHqR : IZR q <> (0 : R)\nHinv : (IZR q |
| previous_ace_historical | 1 | 0 | $0.069605 | 32 | (-32003, 'Coq: The variable q was not found in the current environment.') |
| none_32768 | 0 | 0 | $0.044026 | 28 | (-32003, 'Coq: Unknown interpretation for notation "/ _".') |
| x3_32768 | 0 | 0 | $0.042212 | 26 | (-32003, 'Coq: No applicable tactic.') |
| none_8192 | 0 | 0 | $0.071592 | 41 | (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nHs : (IZR p / IZR q * (IZR p / IZR q))%R = 2%R\nHcancel : (2 * (IZR q  |
| x3_8192 | 0 | 0 | $0.070002 | 50 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| x3_8192 | 1 | 0 | $0.069025 | 40 | (-32003, 'Coq: The variable q was not found in the current environment.') |
| none_8192 | 1 | 0 | $0.074562 | 39 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| x3_32768 | 1 | 0 | $0.045272 | 32 | (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p * / IZR q)%R\nHqR : IZR q <> 0%R\nThe term "IZR q" has type "R" while it is expected to have type "nat |
| none_32768 | 1 | 0 | $0.043294 | 29 | (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHq0 : IZR q <> 0%R\nThe term "sqrt (2 : R)" has type "R" while it is expected to have type |

Full checks, failing tactics, accepted prefixes, returned proofs, request hashes, usage and source paths are in the [compressed JSON dossier](algebra_others_exirrpowirrrat.json.gz). Controller stops are recorded separately in `../termination.json` (compressed in the review export when large).
