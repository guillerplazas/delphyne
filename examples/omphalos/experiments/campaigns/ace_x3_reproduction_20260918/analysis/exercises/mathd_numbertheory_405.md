# mathd_numbertheory_405

All registered attempts, including failures. Costs include cache writes.

| Panel | Replicate | Solved | Cost | Requests | Last checked failure |
|---|---:|---:|---:|---:|---|
| historical_none | 0 | 0 | $0.041184 | 13 | (-32003, 'Coq: Found no subterm matching "t (n + 17) mod 7" in the current goal.') |
| historical_x3_seed0 | 0 | 0 | $0.045031 | 10 | (-32003, 'Coq: Found no subterm matching "t 13" in the current goal.') |
| historical_x3_seed1 | 1 | 0 | $0.038810 | 10 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| previous_nonace_matched | 0 | 0 | $0.074270 | 16 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| previous_nonace_ordinary | 0 | 0 | $0.039037 | 13 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| previous_ace_historical | 0 | 1 | $0.043383 | 12 | — |
| previous_ace_selected | 0 | 0 | $0.065928 | 13 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| previous_ace_selected | 1 | 1 | $0.063882 | 13 | — |
| previous_ace_historical | 1 | 1 | $0.052425 | 10 | — |
| previous_nonace_ordinary | 1 | 0 | $0.046498 | 13 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| previous_nonace_matched | 1 | 0 | $0.078532 | 16 | (-32003, 'Coq: Found no subterm matching "t a mod 7" in the current goal.') |
| none_8192 | 0 | 0 | $0.075329 | 22 | (-32003, 'Coq: The variable x was not found in the current environment.') |
| x3_8192 | 0 | 0 | $0.069325 | 13 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| none_32768 | 0 | 0 | $0.046006 | 12 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| x3_32768 | 0 | 0 | $0.037511 | 10 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| x3_32768 | 1 | 0 | $0.043959 | 10 | (-32003, 'Coq: In environment\na, b, c : nat\nt : nat -> nat\nh0 : t 0 = 0\nh1 : t 1 = 1\nh2 : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3 : a mod 16 = 5\nh4 : b mod 1 |
| none_32768 | 1 | 0 | $0.046563 | 15 | (-32003, 'Coq: Found no subterm matching "t 0" in the current goal.') |
| x3_8192 | 1 | 0 | $0.071587 | 13 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| none_8192 | 1 | 1 | $0.056785 | 14 | — |

Full checks, failing tactics, accepted prefixes, returned proofs, request hashes, usage and source paths are in the [compressed JSON dossier](mathd_numbertheory_405.json.gz). Controller stops are recorded separately in `../termination.json` (compressed in the review export when large).
