# mathd_numbertheory_303

All registered attempts, including failures. Costs include cache writes.

| Panel | Replicate | Solved | Cost | Requests | Last checked failure |
|---|---:|---:|---:|---:|---|
| historical_none | 0 | 0 | $0.040509 | 23 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| historical_x3_seed0 | 0 | 0 | $0.044208 | 23 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| historical_x3_seed1 | 1 | 0 | $0.044912 | 24 | (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).') |
| previous_ace_selected | 0 | 0 | $0.063555 | 24 | (-32003, 'Coq: Expects a disjunctive pattern with 2 branches.') |
| previous_nonace_matched | 0 | 0 | $0.069748 | 20 | (-32003, 'Coq: In environment\nx, y, z : nat\nH :\n  forall n : nat,\n  In n [x; y; z] <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHnd : NoDup [x; y; z]\nK :\n  f |
| previous_nonace_ordinary | 0 | 0 | $0.042069 | 27 | (-32003, 'Coq: The reference interval_cases was not found in the current environment.') |
| previous_ace_historical | 0 | 0 | $0.071882 | 25 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| previous_ace_historical | 1 | 0 | $0.070155 | 30 | (-32003, 'Coq: Unable to find an instance for the variable n.') |
| previous_nonace_ordinary | 1 | 0 | $0.037075 | 23 | (-32003, 'Coq: The variable n was not found in the current environment.') |
| previous_nonace_matched | 1 | 0 | $0.070302 | 27 | (-32003, 'Coq: In environment\nl : list nat\nH :\n  forall n : nat,\n  In n l <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHnd : NoDup l\nn : nat\nHn2 : 2 <= n\nHe |
| previous_ace_selected | 1 | 0 | $0.067302 | 40 | (-32003, 'Coq: This proof is focused, but cannot be unfocused this way') |
| x3_32768 | 0 | 0 | $0.044485 | 20 | (-32003, 'Coq: The variable y was not found in the current environment.') |
| none_8192 | 0 | 0 | $0.060673 | 20 | (-32003, 'Coq: The reference interval_cases was not found in the current environment.') |
| x3_8192 | 0 | 0 | $0.074778 | 38 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| none_32768 | 0 | 0 | $0.045757 | 18 | Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a sm |
| none_32768 | 1 | 0 | $0.041429 | 32 | (-32003, 'Coq: The variable Hclass was not found in the current environment.') |
| x3_8192 | 1 | 0 | $0.072651 | 26 | (-32003, 'Coq: In environment\nl : list nat\nH :\n  forall n : nat,\n  In n l <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHl : NoDup l\nHclass :\n  forall x : nat |
| none_8192 | 1 | 0 | $0.068151 | 46 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |
| x3_32768 | 1 | 0 | $0.037273 | 21 | (-32003, 'Coq: Tactic failure:  Cannot find witness.') |

Full checks, failing tactics, accepted prefixes, returned proofs, request hashes, usage and source paths are in the [compressed JSON dossier](mathd_numbertheory_303.json.gz). Controller stops are recorded separately in `../termination.json` (compressed in the review export when large).
