# mathd_numbertheory_530

All registered attempts, including failures. Costs include cache writes.

| Panel | Replicate | Solved | Cost | Requests | Last checked failure |
|---|---:|---:|---:|---:|---|
| historical_none | 0 | 0 | $0.046831 | 24 | (-32003, 'Coq: The reference Nat.mod_eq_zero_of_dvd was not found in the current\nenvironment.') |
| historical_x3_seed0 | 0 | 0 | $0.040589 | 20 | (-32003, 'Coq: The reference exact_mod_cast was not found in the current environment.') |
| historical_x3_seed1 | 1 | 0 | $0.046989 | 22 | (-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : IZR (Z.of_nat n) / IZR (Z.of_nat k) < 6\nHgt : 5 < IZR (Z.of_nat n) / IZR (Z.of_nat k)\nHkr : 0 |
| previous_nonace_ordinary | 0 | 0 | $0.044767 | 31 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| previous_ace_historical | 0 | 0 | $0.069269 | 25 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| previous_ace_selected | 0 | 0 | $0.068282 | 25 | (-32003, 'Coq: Found no subterm matching "INR (?M1940 * ?M1941)" in the current goal.') |
| previous_nonace_matched | 0 | 0 | $0.069992 | 35 | (-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : IZR (Z.of_nat n) / IZR (Z.of_nat k) < 6\nd, x, y : nat\nHgt :\n  5 <\n  IZR (Z.of_nat x) * IZR  |
| previous_nonace_matched | 1 | 0 | $0.077565 | 36 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| previous_ace_selected | 1 | 0 | $0.067339 | 26 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| previous_ace_historical | 1 | 0 | $0.076838 | 25 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| previous_nonace_ordinary | 1 | 0 | $0.041208 | 25 | (-32003, 'Coq: No matching clauses for match.') |
| x3_8192 | 0 | 0 | $0.078350 | 27 | (-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : INR n / IZR (Z.of_nat k) < 6\nHgt : 5 < INR n / IZR (Z.of_nat k)\nHd : Nat.gcd n k <> 0%nat\np  |
| none_32768 | 0 | 0 | $0.046282 | 23 | (-32003, 'Coq: Found no subterm matching "IZR (Z.of_nat ?M1882)" in the current goal.') |
| x3_32768 | 0 | 0 | $0.042451 | 19 | (-32003, 'Coq: Unable to find an instance for the variable r.') |
| none_8192 | 0 | 0 | $0.078326 | 29 | (-32003, 'Coq: Found no subterm matching "INR ?M1932" in HlowR.') |
| none_8192 | 1 | 0 | $0.076550 | 39 | (-32003, 'Coq: Found no subterm matching "(?M2003 * ?M2004 / ?M2004)%nat"\nin the current goal.') |
| x3_32768 | 1 | 0 | $0.045678 | 24 | (-32003, 'Coq: No applicable tactic.') |
| none_32768 | 1 | 0 | $0.044972 | 30 | (-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : IZR (Z.of_nat n) / IZR (Z.of_nat k) < 6\nHgt : 5 < IZR (Z.of_nat n) / IZR (Z.of_nat k)\nd := Na |
| x3_8192 | 1 | 0 | $0.076548 | 24 | (-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : INR n / INR k < 6\nHgt : 5 < INR n / INR k\nHg0 : Nat.gcd n k <> 0%nat\nHgpos : (0 < Nat.gcd n  |

Full checks, failing tactics, accepted prefixes, returned proofs, request hashes, usage and source paths are in the [compressed JSON dossier](mathd_numbertheory_530.json.gz). Controller stops are recorded separately in `../termination.json` (compressed in the review export when large).
