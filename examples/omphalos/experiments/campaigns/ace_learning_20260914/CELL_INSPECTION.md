# Every matched proof cell

Descriptions below are terminal observations from actual logs, not causal diagnoses of book effects. Each trace contains all model outputs and verifier computations, including the complete submitted scripts. Admission stops can occur below $.10 when the next request's conservative estimate exceeds the remaining budget.

## training / mathd_algebra_206 / seed 0: shared_success

v2: solved, $0.00069166, 1 model requests. Candidate B: solved, $0.00267226, 3 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_206_0.json](analysis/traces/training_v2_mathd_algebra_206_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:5019`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_206_0.json](analysis/traces/training_B_mathd_algebra_206_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2775`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / algebra_amgm_sum1toneqn_prod1tonleq1 / seed 0: shared_failure

v2: admission:price, $0.03904390, 22 model requests. Candidate B: admission:price, $0.03854766, 23 model requests.

**v2 evidence:** [analysis/traces/training_v2_algebra_amgm_sum1toneqn_prod1tonleq1_0.json](analysis/traces/training_v2_algebra_amgm_sum1toneqn_prod1tonleq1_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
assert (Hsum' : sum_n a (S n) = INR (S n)) by cbn in Hsum; rewrite <- plus_assoc in Hsum; exact Hsum.
```

```text
(-32003, 'Coq: Proof is not complete.')
```

Accepted prefix: 7 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6670`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_algebra_amgm_sum1toneqn_prod1tonleq1_0.json](analysis/traces/training_B_algebra_amgm_sum1toneqn_prod1tonleq1_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
unsafe command
```

```text
Proof obligations may not be bypassed.
```

Accepted prefix: 0 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5107`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12_2000_p6 / seed 0: candidate_loss

v2: solved, $0.01775186, 14 model requests. Candidate B: admission:price, $0.03886256, 32 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12_2000_p6_0.json](analysis/traces/training_v2_amc12_2000_p6_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'open_obligations': 1, 'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 1, 'tactic_does_not_close_goal': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:4604`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12_2000_p6_0.json](analysis/traces/training_B_amc12_2000_p6_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
apply Hr.
```

```text
(-32003, 'Coq: In environment\np, q : Z\nHp : 0 < p\nHq : 0 < q\nHpp : prime p\nHpq : prime q\nHpb : 4 <= p <= 18\nHqb : 4 <= q <= 18\nHeq : p * q - (p + q) = 194\nr : Z\nHpr : prime r\nHrl : 4 <= r\nHru : r <= 18\nHr : Z.even r = false\nHrmod : r mod 2 = 0\nUnable to unify "Z.even r = false" with "False".')
```

Accepted prefix: 23 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5346`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / aime_1988_p8 / seed 0: shared_success

v2: solved, $0.01013010, 5 model requests. Candidate B: solved, $0.00594718, 4 model requests.

**v2 evidence:** [analysis/traces/training_v2_aime_1988_p8_0.json](analysis/traces/training_v2_aime_1988_p8_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'type_or_rewrite_shape': 1, 'syntax_or_pattern': 2, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7391`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_aime_1988_p8_0.json](analysis/traces/training_B_aime_1988_p8_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3217`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2017_p7 / seed 0: shared_success

v2: solved, $0.01210180, 8 model requests. Candidate B: solved, $0.01194472, 10 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2017_p7_0.json](analysis/traces/training_v2_amc12a_2017_p7_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 3, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:3375`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2017_p7_0.json](analysis/traces/training_B_amc12a_2017_p7_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 2, 'missing_name_or_hypothesis': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3478`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12b_2002_p11 / seed 0: shared_failure

v2: admission:price, $0.03811260, 24 model requests. Candidate B: admission:price, $0.03617302, 26 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12b_2002_p11_0.json](analysis/traces/training_v2_amc12b_2002_p11_0.json).
Last verifier symptom: focus; tactic:

```rocq
- assert (Eab : Z.even (a + b) = false).
```

```text
(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet -- is not finished.')
```

Accepted prefix: 96 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6422`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12b_2002_p11_0.json](analysis/traces/training_B_amc12b_2002_p11_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
omega.
```

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Accepted prefix: 23 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5199`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / imo_1963_p5 / seed 0: candidate_win

v2: admission:price, $0.03734150, 15 model requests. Candidate B: solved, $0.01565666, 10 model requests.

**v2 evidence:** [analysis/traces/training_v2_imo_1963_p5_0.json](analysis/traces/training_v2_imo_1963_p5_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
- assert (Hp : 0 < PI) by exact PI_pos.
```

```text
(-32003, 'Coq: The variable PI_pos was not found in the current environment.')
```

Accepted prefix: 43 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7307`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_imo_1963_p5_0.json](analysis/traces/training_B_imo_1963_p5_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'missing_name_or_hypothesis': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3959`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / induction_pord1p1on2powklt5on2 / seed 0: shared_success

v2: solved, $0.02949530, 14 model requests. Candidate B: solved, $0.02845670, 13 model requests.

**v2 evidence:** [analysis/traces/training_v2_induction_pord1p1on2powklt5on2_0.json](analysis/traces/training_v2_induction_pord1p1on2powklt5on2_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 3, 'syntax_or_pattern': 2, 'focus': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:5881`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_induction_pord1p1on2powklt5on2_0.json](analysis/traces/training_B_induction_pord1p1on2powklt5on2_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 2, 'focus': 2, 'type_or_rewrite_shape': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:4750`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_224 / seed 0: shared_failure

v2: admission:price, $0.03716328, 19 model requests. Candidate B: admission:price, $0.03378328, 18 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_224_0.json](analysis/traces/training_v2_mathd_algebra_224_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
omega.
```

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Accepted prefix: 54 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:5672`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_224_0.json](analysis/traces/training_B_mathd_algebra_224_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
repeat inversion H.
```

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 56 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5365`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2016_p2 / seed 0: candidate_win

v2: admission:price, $0.02960274, 17 model requests. Candidate B: solved, $0.00263004, 3 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2016_p2_0.json](analysis/traces/training_v2_amc12a_2016_p2_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite <- (Nat.pow_mul_r 10 3 5) in H.
```

```text
(-32003, 'Coq: Found no subterm matching "(10 ^ 3) ^ 5" in H.')
```

Accepted prefix: 5 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6431`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2016_p2_0.json](analysis/traces/training_B_amc12a_2016_p2_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2800`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_301 / seed 0: shared_success

v2: solved, $0.00083466, 1 model requests. Candidate B: solved, $0.00387914, 5 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_301_0.json](analysis/traces/training_v2_mathd_numbertheory_301_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7020`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_301_0.json](analysis/traces/training_B_mathd_numbertheory_301_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'open_obligations': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2914`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_185 / seed 0: shared_failure

v2: admission:price, $0.03528046, 24 model requests. Candidate B: admission:price, $0.03556490, 19 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_185_0.json](analysis/traces/training_v2_mathd_algebra_185_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
all: intro H; repeat (unfold Add in H; inversion H).
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 4 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8322`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_185_0.json](analysis/traces/training_B_mathd_algebra_185_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
all: intro H; repeat inversion H.
```

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 22 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5401`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / imo_1967_p3 / seed 0: shared_failure

v2: admission:price, $0.03771022, 21 model requests. Candidate B: admission:price, $0.04219574, 22 model requests.

**v2 evidence:** [analysis/traces/training_v2_imo_1967_p3_0.json](analysis/traces/training_v2_imo_1967_p3_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nia.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 10 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7494`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_imo_1967_p3_0.json](analysis/traces/training_B_imo_1967_p3_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite Hfactor.
```

```text
(-32003, 'Coq: Found no subterm matching\n"c (S n) * c (S (S n)) * (c (k + S n) - c k) * (c (k + S (S n)) - c k)"\nin the current goal.')
```

Accepted prefix: 26 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5212`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12b_2004_p3 / seed 0: shared_success

v2: solved, $0.01750772, 11 model requests. Candidate B: solved, $0.03174476, 16 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12b_2004_p3_0.json](analysis/traces/training_v2_amc12b_2004_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1, 'syntax_or_pattern': 2, 'resource': 3}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7900`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12b_2004_p3_0.json](analysis/traces/training_B_amc12b_2004_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 4, 'tactic_does_not_close_goal': 2, 'resource': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5398`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_323 / seed 0: shared_success

v2: solved, $0.00249632, 2 model requests. Candidate B: solved, $0.00947590, 5 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_323_0.json](analysis/traces/training_v2_mathd_algebra_323_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2192`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_323_0.json](analysis/traces/training_B_mathd_algebra_323_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 1, 'tactic_does_not_close_goal': 1, 'type_or_rewrite_shape': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3765`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_221 / seed 0: shared_success

v2: solved, $0.00055726, 1 model requests. Candidate B: solved, $0.00057806, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_221_0.json](analysis/traces/training_v2_mathd_numbertheory_221_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2154`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_221_0.json](analysis/traces/training_B_mathd_numbertheory_221_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2760`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_28 / seed 0: shared_success

v2: solved, $0.00164332, 2 model requests. Candidate B: solved, $0.00339048, 4 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_28_0.json](analysis/traces/training_v2_mathd_algebra_28_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:1845`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_28_0.json](analysis/traces/training_B_mathd_algebra_28_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'type_or_rewrite_shape': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2806`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2003_p1 / seed 0: shared_success

v2: solved, $0.00391710, 4 model requests. Candidate B: solved, $0.00328650, 4 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2003_p1_0.json](analysis/traces/training_v2_amc12a_2003_p1_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1, 'tactic_does_not_close_goal': 1, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7908`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2003_p1_0.json](analysis/traces/training_B_amc12a_2003_p1_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1, 'focus': 1, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:4169`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_247 / seed 0: shared_success

v2: solved, $0.00334286, 5 model requests. Candidate B: solved, $0.00359864, 4 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_247_0.json](analysis/traces/training_v2_mathd_algebra_247_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2247`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_247_0.json](analysis/traces/training_B_mathd_algebra_247_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'tactic_does_not_close_goal': 2, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2828`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_458 / seed 0: shared_success

v2: solved, $0.00277632, 4 model requests. Candidate B: solved, $0.00253006, 4 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_458_0.json](analysis/traces/training_v2_mathd_numbertheory_458_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2014`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_458_0.json](analysis/traces/training_B_mathd_numbertheory_458_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2606`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / imo_1977_p6 / seed 0: shared_failure

v2: admission:price, $0.04043882, 12 model requests. Candidate B: admission:price, $0.03928356, 14 model requests.

**v2 evidence:** [analysis/traces/training_v2_imo_1977_p6_0.json](analysis/traces/training_v2_imo_1977_p6_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
lia.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 8 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8533`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_imo_1977_p6_0.json](analysis/traces/training_B_imo_1977_p6_0.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof imo_1977_p6): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 30 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5362`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_326 / seed 0: shared_success

v2: solved, $0.00048566, 1 model requests. Candidate B: solved, $0.00052686, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_326_0.json](analysis/traces/training_v2_mathd_numbertheory_326_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6801`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_326_0.json](analysis/traces/training_B_mathd_numbertheory_326_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2246`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_35 / seed 0: shared_success

v2: solved, $0.00046886, 1 model requests. Candidate B: solved, $0.00048486, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_35_0.json](analysis/traces/training_v2_mathd_numbertheory_35_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:3043`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_35_0.json](analysis/traces/training_B_mathd_numbertheory_35_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2203`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2013_p7 / seed 0: shared_success

v2: solved, $0.00088246, 1 model requests. Candidate B: solved, $0.00078686, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2013_p7_0.json](analysis/traces/training_v2_amc12a_2013_p7_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:3691`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2013_p7_0.json](analysis/traces/training_B_amc12a_2013_p7_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2293`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_48 / seed 0: shared_success

v2: solved, $0.00907386, 8 model requests. Candidate B: solved, $0.00680078, 7 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_48_0.json](analysis/traces/training_v2_mathd_numbertheory_48_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 2, 'syntax_or_pattern': 2, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:4179`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_48_0.json](analysis/traces/training_B_mathd_numbertheory_48_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 2, 'focus': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3579`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_629 / seed 0: shared_failure

v2: admission:price, $0.03751654, 15 model requests. Candidate B: admission:price, $0.03695304, 22 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_629_0.json](analysis/traces/training_v2_mathd_numbertheory_629_0.json).
Last verifier symptom: focus; tactic:

```rocq
* destruct Hm_cases as [-> | Hm_cases].
```

```text
(-32003, 'Coq: [Focus] Wrong bullet *: Current bullet * is not finished.')
```

Accepted prefix: 14 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8357`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_629_0.json](analysis/traces/training_B_mathd_numbertheory_629_0.json).
Last verifier symptom: syntax_or_pattern; tactic:

```rocq
all: try change 1728 = 144 in Heq.
```

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Accepted prefix: 30 tactics; remaining focused goals: 17.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5359`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / imo_1968_p5_1 / seed 0: candidate_win

v2: admission:price, $0.03947068, 18 model requests. Candidate B: solved, $0.02992550, 14 model requests.

**v2 evidence:** [analysis/traces/training_v2_imo_1968_p5_1_0.json](analysis/traces/training_v2_imo_1968_p5_1_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
- field.
```

```text
(-32003, 'Coq: Tactic failure: Goal is not an equation (of expected equality) eq.')
```

Accepted prefix: 25 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:5123`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_imo_1968_p5_1_0.json](analysis/traces/training_B_imo_1968_p5_1_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 3, 'other_verifier_failure': 1, 'type_or_rewrite_shape': 2, 'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 1, 'focus': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:4595`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / aime_1990_p4 / seed 0: shared_success

v2: solved, $0.01145844, 11 model requests. Candidate B: solved, $0.00601216, 6 model requests.

**v2 evidence:** [analysis/traces/training_v2_aime_1990_p4_0.json](analysis/traces/training_v2_aime_1990_p4_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'other_verifier_failure': 1, 'tactic_does_not_close_goal': 1, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:3495`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_aime_1990_p4_0.json](analysis/traces/training_B_aime_1990_p4_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3631`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_37 / seed 0: shared_success

v2: solved, $0.00134160, 1 model requests. Candidate B: solved, $0.00049606, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_37_0.json](analysis/traces/training_v2_mathd_algebra_37_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:1508`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_37_0.json](analysis/traces/training_B_mathd_algebra_37_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:2932`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2002_p13 / seed 0: shared_success

v2: solved, $0.00843798, 4 model requests. Candidate B: solved, $0.03040048, 11 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2002_p13_0.json](analysis/traces/training_v2_amc12a_2002_p13_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6423`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2002_p13_0.json](analysis/traces/training_B_amc12a_2002_p13_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 2, 'missing_name_or_hypothesis': 5}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:4937`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_410 / seed 0: shared_success

v2: solved, $0.00261504, 5 model requests. Candidate B: solved, $0.00118972, 2 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_410_0.json](analysis/traces/training_v2_mathd_algebra_410_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2906`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_410_0.json](analysis/traces/training_B_mathd_algebra_410_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3006`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / aime_1988_p3 / seed 0: shared_success

v2: solved, $0.03582632, 17 model requests. Candidate B: solved, $0.03591732, 13 model requests.

**v2 evidence:** [analysis/traces/training_v2_aime_1988_p3_0.json](analysis/traces/training_v2_aime_1988_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 2, 'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 2, 'missing_name_or_hypothesis': 1, 'focus': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8222`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_aime_1988_p3_0.json](analysis/traces/training_B_aime_1988_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1, 'type_or_rewrite_shape': 3, 'focus': 2, 'tactic_does_not_close_goal': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5040`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / imo_1983_p6 / seed 0: shared_success

v2: solved, $0.02414154, 11 model requests. Candidate B: solved, $0.01542686, 6 model requests.

**v2 evidence:** [analysis/traces/training_v2_imo_1983_p6_0.json](analysis/traces/training_v2_imo_1983_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'tactic_does_not_close_goal': 5, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:5132`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_imo_1983_p6_0.json](analysis/traces/training_B_imo_1983_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 3, 'tactic_does_not_close_goal': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:4546`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12b_2003_p17 / seed 0: shared_success

v2: solved, $0.00631428, 7 model requests. Candidate B: solved, $0.00402436, 8 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12b_2003_p17_0.json](analysis/traces/training_v2_amc12b_2003_p17_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2787`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12b_2003_p17_0.json](analysis/traces/training_B_amc12b_2003_p17_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3614`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12a_2020_p13 / seed 0: shared_failure

v2: admission:price, $0.03614856, 19 model requests. Candidate B: admission:price, $0.04052028, 19 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12a_2020_p13_0.json](analysis/traces/training_v2_amc12a_2020_p13_0.json).
Last verifier symptom: focus; tactic:

```rocq
}
```

```text
(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')
```

Accepted prefix: 23 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:7916`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12a_2020_p13_0.json](analysis/traces/training_B_amc12a_2020_p13_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
{ apply le_INR.
```

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nHc0 : 0 < INR c\nHb0 : 0 < INR b\nHa0 : 0 < INR a\nHpc : 0 < Rpower n (/ INR c)\nHpb : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHpa : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)\nHlogn : ln n <> 0\nHlog : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHfrac : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHane : INR a <> 0\nHbne : INR b <> 0\nHcne : INR c <> 0\nHia : 0 < / INR a\nHib : 0 < / INR b\nHic : 0 < / INR c\nUnable to unify "INR ?M1902 < INR ?M1903 \\/ INR ?M1902 = INR ?M1903" with\n "2 < INR a \\/ 2 = INR a".')
```

Accepted prefix: 38 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5343`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / aime_1984_p1 / seed 0: candidate_loss

v2: solved, $0.03303952, 13 model requests. Candidate B: admission:price, $0.03877996, 15 model requests.

**v2 evidence:** [analysis/traces/training_v2_aime_1984_p1_0.json](analysis/traces/training_v2_aime_1984_p1_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 6, 'type_or_rewrite_shape': 2, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:6143`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_aime_1984_p1_0.json](analysis/traces/training_B_aime_1984_p1_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
ring.
```

```text
(-32003, 'Coq: Tactic failure: not a valid ring equation.')
```

Accepted prefix: 46 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5260`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_403 / seed 0: shared_success

v2: solved, $0.00059586, 1 model requests. Candidate B: solved, $0.00054226, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_403_0.json](analysis/traces/training_v2_mathd_numbertheory_403_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:2100`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_403_0.json](analysis/traces/training_B_mathd_numbertheory_403_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3366`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / amc12_2000_p1 / seed 0: candidate_win

v2: admission:price, $0.03866630, 19 model requests. Candidate B: solved, $0.01482438, 6 model requests.

**v2 evidence:** [analysis/traces/training_v2_amc12_2000_p1_0.json](analysis/traces/training_v2_amc12_2000_p1_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
* apply Hcore with (a := i) (b := o) (c := m); nia.
```

```text
(-32003, 'Coq: In environment\ni, m, o : nat\nHim : i <> m\nHmo : m <> o\nHoi : o <> i\nHprod : i * m * o = 2001\nHcore :\n  forall a b c : nat, a < b -> b < c -> a * b * c = 2001 -> a + b + c <= 671\nHim\' : i <= m\nHom : m > o\nHio\' : i <= o\nUnable to unify "i + o + m <= 671" with "i + m + o <= 671".')
```

Accepted prefix: 60 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8480`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_amc12_2000_p1_0.json](analysis/traces/training_B_amc12_2000_p1_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 2, 'type_or_rewrite_shape': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5161`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_algebra_43 / seed 0: shared_success

v2: solved, $0.00050046, 1 model requests. Candidate B: solved, $0.00053566, 1 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_algebra_43_0.json](analysis/traces/training_v2_mathd_algebra_43_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:1509`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_algebra_43_0.json](analysis/traces/training_B_mathd_algebra_43_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3617`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## training / mathd_numbertheory_42 / seed 0: shared_success

v2: solved, $0.00101360, 2 model requests. Candidate B: solved, $0.00111220, 2 model requests.

**v2 evidence:** [analysis/traces/training_v2_mathd_numbertheory_42_0.json](analysis/traces/training_v2_mathd_numbertheory_42_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:1757`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/training_B_mathd_numbertheory_42_0.json](analysis/traces/training_B_mathd_numbertheory_42_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:3785`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_234 / seed 0: shared_success

v2: solved, $0.00052246, 1 model requests. Candidate B: solved, $0.00091166, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_234_0.json](analysis/traces/validation_v2_mathd_algebra_234_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:19043`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_234_0.json](analysis/traces/validation_B_mathd_algebra_234_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5685`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1969_p2 / seed 0: shared_failure

v2: admission:price, $0.03981614, 20 model requests. Candidate B: admission:price, $0.02952896, 39 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1969_p2_0.json](analysis/traces/validation_v2_imo_1969_p2_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
- simpl. nra.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 15 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:12939`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1969_p2_0.json](analysis/traces/validation_B_imo_1969_p2_0.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 1 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10038`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_190 / seed 0: shared_success

v2: solved, $0.00024748, 1 model requests. Candidate B: solved, $0.00057146, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_190_0.json](analysis/traces/validation_v2_mathd_algebra_190_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:12881`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_190_0.json](analysis/traces/validation_B_mathd_algebra_190_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5557`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_393 / seed 1: shared_success

v2: solved, $0.00959564, 7 model requests. Candidate B: solved, $0.00491774, 5 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_393_1.json](analysis/traces/validation_v2_mathd_algebra_393_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'type_or_rewrite_shape': 4}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:12932`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_393_1.json](analysis/traces/validation_B_mathd_algebra_393_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'type_or_rewrite_shape': 2, 'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6310`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1991_p9 / seed 1: shared_failure

v2: admission:price, $0.03782722, 18 model requests. Candidate B: admission:price, $0.04155970, 17 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1991_p9_1.json](analysis/traces/validation_v2_aime_1991_p9_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
- lia.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 42 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:25897`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1991_p9_1.json](analysis/traces/validation_B_aime_1991_p9_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
replace (((22 * cos x - 7) / 7)²) with (((22 * cos x - 7) / 7) * ((22 * cos x - 7) / 7)) in Htrig by ring.
```

```text
(-32003, 'Coq: Tactic failure: not a valid ring equation.')
```

Accepted prefix: 16 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10013`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1964_p2 / seed 1: candidate_loss

v2: solved, $0.02544376, 14 model requests. Candidate B: admission:price, $0.03845920, 16 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1964_p2_1.json](analysis/traces/validation_v2_imo_1964_p2_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'tactic_does_not_close_goal': 6, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17378`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1964_p2_1.json](analysis/traces/validation_B_imo_1964_p2_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nra.
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 45 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9929`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2020_p21 / seed 0: shared_failure

v2: admission:price, $0.03238960, 19 model requests. Candidate B: admission:price, $0.03742322, 22 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2020_p21_0.json](analysis/traces/validation_v2_amc12a_2020_p21_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
- repeat constructor; simpl; intuition congruence.
```

```text
(-32003, 'Coq: Unable to unify "NoDup (?M8909 :: ?M8910)" with "NoDup nil".')
```

Accepted prefix: 2 tactics; remaining focused goals: 4.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:16500`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2020_p21_0.json](analysis/traces/validation_B_amc12a_2020_p21_0.json).
Last verifier symptom: resource; tactic:

```rocq
- vm_compute.
```

```text
(-32003, 'Coq: Stack overflow.')
```

Accepted prefix: 2 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13657`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2013_p8 / seed 1: shared_success

v2: solved, $0.00883022, 8 model requests. Candidate B: solved, $0.01258304, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2013_p8_1.json](analysis/traces/validation_v2_amc12a_2013_p8_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 1, 'focus': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21662`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2013_p8_1.json](analysis/traces/validation_B_amc12a_2013_p8_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 2, 'other_verifier_failure': 1, 'type_or_rewrite_shape': 1, 'focus': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:7870`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2019_p21 / seed 1: shared_failure

v2: admission:price, $0.04207448, 24 model requests. Candidate B: admission:price, $0.04087004, 28 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2019_p21_1.json](analysis/traces/validation_v2_amc12a_2019_p21_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
apply pair_equal.
```

```text
(-32003, 'Coq: The variable pair_equal was not found in the current environment.')
```

Accepted prefix: 9 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:20050`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2019_p21_1.json](analysis/traces/validation_B_amc12a_2019_p21_1.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite <- H1.
```

```text
(-32003, 'Coq: Found no subterm matching "(sqrt 2 * sqrt 2)%R" in the current goal.')
```

Accepted prefix: 13 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10525`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2020_p21 / seed 1: shared_failure

v2: admission:price, $0.03335106, 17 model requests. Candidate B: admission:price, $0.02883374, 14 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2020_p21_1.json](analysis/traces/validation_v2_amc12a_2020_p21_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
+ simpl; intuition; lia.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 3 tactics; remaining focused goals: 49.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:23386`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2020_p21_1.json](analysis/traces/validation_B_amc12a_2020_p21_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
all: (intro H; intuition; discriminate).
```

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 4 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:11230`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / induction_prod1p1onk3le3m1onn / seed 0: shared_failure

v2: admission:price, $0.03808346, 21 model requests. Candidate B: admission:price, $0.03863418, 16 model requests.

**v2 evidence:** [analysis/traces/validation_v2_induction_prod1p1onk3le3m1onn_0.json](analysis/traces/validation_v2_induction_prod1p1onk3le3m1onn_0.json).
Last verifier symptom: focus; tactic:

```rocq
+++ lra.
```

```text
(-32003, 'Coq: [Focus] Wrong bullet +++: Current bullet *** is not finished.')
```

Accepted prefix: 41 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:25696`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_induction_prod1p1onk3le3m1onn_0.json](analysis/traces/validation_B_induction_prod1p1onk3le3m1onn_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
apply (Rmult_le_reg_r ((INR n + 1) * (INR n + 2) ^ 3) Hp).
```

```text
(-32003, 'Coq: In environment\nn : nat\nIH :\n  (S n > 0)%nat ->\n  prod_1_to_n (fun k : nat => 1 + / INR k ^ 3) (S n) <= 3 - / INR (S n)\nHn : (S (S n) > 0)%nat\nHpos : (0 < S n)%nat\nHIH : prod_1_to_n (fun k : nat => 1 + / INR k ^ 3) (S n) <= 3 - / INR (S n)\nHcast : 0 < INR (S (S n))\nHd : 0 < INR (S (S n)) ^ 3\nHfactor : 0 <= 1 + / INR (S (S n)) ^ 3\nHnonneg : 0 <= INR n\nHn1 : INR n + 1 <> 0\nHn2 : INR n + 2 <> 0\nHp : 0 < (INR n + 1) * (INR n + 2) ^ 3\nThe term "Hp" has type "0 < (INR n + 1) * (INR n + 2) ^ 3"\nwhile it is expected to have type "R".')
```

Accepted prefix: 61 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9313`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_284 / seed 0: shared_success

v2: solved, $0.00049266, 1 model requests. Candidate B: solved, $0.00046906, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_284_0.json](analysis/traces/validation_v2_mathd_numbertheory_284_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8856`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_284_0.json](analysis/traces/validation_B_mathd_numbertheory_284_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5533`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1991_p6 / seed 1: shared_failure

v2: admission:price, $0.04160134, 17 model requests. Candidate B: admission:price, $0.03307902, 11 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1991_p6_1.json](analysis/traces/validation_v2_aime_1991_p6_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
{ lia. }
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 38 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21964`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1991_p6_1.json](analysis/traces/validation_B_aime_1991_p6_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
assert (H20 : (Int_part (r + 19 / 100) <= Int_part (r + 20 / 100))%Z) by (pose proof (H19 _ _ ltac:(lra)) as H; lia).
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 27 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9974`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_327 / seed 1: shared_success

v2: solved, $0.00168244, 3 model requests. Candidate B: solved, $0.00178220, 4 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_327_1.json](analysis/traces/validation_v2_mathd_algebra_327_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:11018`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_327_1.json](analysis/traces/validation_B_mathd_algebra_327_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5977`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2020_p5 / seed 1: shared_success

v2: solved, $0.00056006, 1 model requests. Candidate B: solved, $0.00037314, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2020_p5_1.json](analysis/traces/validation_v2_amc12b_2020_p5_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:13048`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2020_p5_1.json](analysis/traces/validation_B_amc12b_2020_p5_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5593`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_433 / seed 1: shared_success

v2: solved, $0.00187676, 3 model requests. Candidate B: solved, $0.00213450, 3 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_433_1.json](analysis/traces/validation_v2_mathd_algebra_433_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:11206`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_433_1.json](analysis/traces/validation_B_mathd_algebra_433_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5811`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2013_p8 / seed 0: shared_success

v2: solved, $0.00802514, 8 model requests. Candidate B: solved, $0.00387326, 6 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2013_p8_0.json](analysis/traces/validation_v2_amc12a_2013_p8_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:19735`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2013_p8_0.json](analysis/traces/validation_B_amc12a_2013_p8_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6379`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1991_p9 / seed 0: shared_failure

v2: admission:price, $0.04270830, 24 model requests. Candidate B: admission:price, $0.03487266, 21 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1991_p9_0.json](analysis/traces/validation_v2_aime_1991_p9_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nra.
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 30 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:13047`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1991_p9_0.json](analysis/traces/validation_B_aime_1991_p9_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
- rewrite Rmult_0.
```

```text
(-32003, 'Coq: The variable Rmult_0 was not found in the current environment.')
```

Accepted prefix: 25 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9826`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12_2001_p21 / seed 1: candidate_loss

v2: solved, $0.03158988, 26 model requests. Candidate B: admission:price, $0.04340486, 21 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12_2001_p21_1.json](analysis/traces/validation_v2_amc12_2001_p21_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'tactic_does_not_close_goal': 2, 'syntax_or_pattern': 1, 'other_verifier_failure': 1, 'missing_name_or_hypothesis': 2}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26140`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12_2001_p21_1.json](analysis/traces/validation_B_amc12_2001_p21_1.json).
Last verifier symptom: syntax_or_pattern; tactic:

```rocq
destruct (le_gt_dec b 10); all: try lia.
```

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Accepted prefix: 3 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14380`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_461 / seed 0: shared_success

v2: solved, $0.00066406, 1 model requests. Candidate B: solved, $0.00056846, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_461_0.json](analysis/traces/validation_v2_mathd_numbertheory_461_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8706`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_461_0.json](analysis/traces/validation_B_mathd_numbertheory_461_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5547`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1960_p2 / seed 0: shared_success

v2: solved, $0.00184170, 2 model requests. Candidate B: solved, $0.02355740, 17 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1960_p2_0.json](analysis/traces/validation_v2_imo_1960_p2_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:13780`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1960_p2_0.json](analysis/traces/validation_B_imo_1960_p2_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 3, 'tactic_does_not_close_goal': 1, 'other_verifier_failure': 1, 'missing_name_or_hypothesis': 1, 'open_obligations': 5}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8764`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_282 / seed 0: shared_failure

v2: admission:price, $0.03117184, 38 model requests. Candidate B: admission:price, $0.03078340, 34 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_282_0.json](analysis/traces/validation_v2_mathd_algebra_282_0.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21428`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_282_0.json](analysis/traces/validation_B_mathd_algebra_282_0.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10770`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_251 / seed 1: shared_success

v2: solved, $0.00089066, 1 model requests. Candidate B: solved, $0.00128706, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_251_1.json](analysis/traces/validation_v2_mathd_algebra_251_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:16872`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_251_1.json](analysis/traces/validation_B_mathd_algebra_251_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5790`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2020_p5 / seed 0: shared_success

v2: solved, $0.00027434, 1 model requests. Candidate B: solved, $0.00054366, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2020_p5_0.json](analysis/traces/validation_v2_amc12b_2020_p5_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21609`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2020_p5_0.json](analysis/traces/validation_B_amc12b_2020_p5_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5524`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1981_p6 / seed 0: shared_success

v2: solved, $0.00816620, 5 model requests. Candidate B: solved, $0.00558136, 7 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1981_p6_0.json](analysis/traces/validation_v2_imo_1981_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 2, 'tactic_does_not_close_goal': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:13692`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1981_p6_0.json](analysis/traces/validation_B_imo_1981_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6585`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_214 / seed 0: shared_success

v2: solved, $0.00031480, 1 model requests. Candidate B: solved, $0.00063266, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_214_0.json](analysis/traces/validation_v2_mathd_algebra_214_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:19926`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_214_0.json](analysis/traces/validation_B_mathd_algebra_214_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5805`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12_2000_p12 / seed 0: shared_success

v2: solved, $0.03479026, 21 model requests. Candidate B: solved, $0.01779782, 9 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12_2000_p12_0.json](analysis/traces/validation_v2_amc12_2000_p12_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 3, 'missing_name_or_hypothesis': 5, 'tactic_does_not_close_goal': 2, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17604`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12_2000_p12_0.json](analysis/traces/validation_B_amc12_2000_p12_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 3, 'missing_name_or_hypothesis': 1, 'focus': 1, 'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:12991`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / induction_prod1p1onk3le3m1onn / seed 1: shared_failure

v2: admission:price, $0.03830328, 19 model requests. Candidate B: admission:price, $0.03886102, 15 model requests.

**v2 evidence:** [analysis/traces/validation_v2_induction_prod1p1onk3le3m1onn_1.json](analysis/traces/validation_v2_induction_prod1p1onk3le3m1onn_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
field_simplify [Hkz].
```

```text
(-32003, 'Coq: No matching clauses for match.')
```

Accepted prefix: 36 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:20041`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_induction_prod1p1onk3le3m1onn_1.json](analysis/traces/validation_B_induction_prod1p1onk3le3m1onn_1.json).
Last verifier symptom: focus; tactic:

```rocq
- exact Hpos.
```

```text
(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet + is not finished.')
```

Accepted prefix: 41 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9204`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / algebra_others_exirrpowirrrat / seed 1: shared_failure

v2: admission:price, $0.04037872, 26 model requests. Candidate B: admission:price, $0.03466118, 30 model requests.

**v2 evidence:** [analysis/traces/validation_v2_algebra_others_exirrpowirrrat_1.json](analysis/traces/validation_v2_algebra_others_exirrpowirrrat_1.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
- exact Htmp.
```

```text
(-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nHs2 : (sqrt 2)²%R = 2%R\nHtmp : (sqrt 2 * IZR q)%R = (IZR p / IZR q * IZR q)%R\nThe term "Htmp" has type "(sqrt 2 * IZR q)%R = (IZR p / IZR q * IZR q)%R"\nwhile it is expected to have type\n "(IZR p * IZR q)%R = (sqrt 2 * IZR q * IZR q)%R".')
```

Accepted prefix: 14 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:14455`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_algebra_others_exirrpowirrrat_1.json](analysis/traces/validation_B_algebra_others_exirrpowirrrat_1.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
exact Hs.
```

```text
(-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nHs : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\nThe term "Hs" has type "(IZR p ^ 2 / IZR q ^ 2)%R = 2%R"\nwhile it is expected to have type\n "(IZR p * IZR p)%R = (2 * (IZR q * IZR q))%R".')
```

Accepted prefix: 13 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10520`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_64 / seed 1: shared_success

v2: solved, $0.00467240, 5 model requests. Candidate B: solved, $0.00718014, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_64_1.json](analysis/traces/validation_v2_mathd_numbertheory_64_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'focus': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:22301`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_64_1.json](analysis/traces/validation_B_mathd_numbertheory_64_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'focus': 1, 'tactic_does_not_close_goal': 1, 'missing_name_or_hypothesis': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:7018`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1989_p8 / seed 0: shared_success

v2: solved, $0.00030802, 1 model requests. Candidate B: solved, $0.00061286, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1989_p8_0.json](analysis/traces/validation_v2_aime_1989_p8_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8903`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1989_p8_0.json](analysis/traces/validation_B_aime_1989_p8_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:5997`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_234 / seed 1: shared_success

v2: solved, $0.00036418, 1 model requests. Candidate B: solved, $0.00043178, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_234_1.json](analysis/traces/validation_v2_mathd_algebra_234_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:23246`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_234_1.json](analysis/traces/validation_B_mathd_algebra_234_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6056`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2002_p6 / seed 0: shared_success

v2: solved, $0.00032786, 1 model requests. Candidate B: solved, $0.00050766, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2002_p6_0.json](analysis/traces/validation_v2_amc12a_2002_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:14580`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2002_p6_0.json](analysis/traces/validation_B_amc12a_2002_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6016`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_33 / seed 0: shared_success

v2: solved, $0.00074786, 1 model requests. Candidate B: solved, $0.00095282, 2 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_33_0.json](analysis/traces/validation_v2_mathd_numbertheory_33_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8748`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_33_0.json](analysis/traces/validation_B_mathd_numbertheory_33_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6349`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2016_p3 / seed 0: shared_success

v2: solved, $0.00547166, 4 model requests. Candidate B: solved, $0.02371606, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2016_p3_0.json](analysis/traces/validation_v2_amc12a_2016_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:9448`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2016_p3_0.json](analysis/traces/validation_B_amc12a_2016_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 2, 'type_or_rewrite_shape': 1, 'syntax_or_pattern': 2, 'tactic_does_not_close_goal': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8416`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1960_p2 / seed 1: shared_success

v2: solved, $0.00576988, 5 model requests. Candidate B: solved, $0.00790054, 9 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1960_p2_1.json](analysis/traces/validation_v2_imo_1960_p2_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 2}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:18480`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1960_p2_1.json](analysis/traces/validation_B_imo_1960_p2_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'tactic_does_not_close_goal': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:7667`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_251 / seed 0: shared_success

v2: solved, $0.00191194, 2 model requests. Candidate B: solved, $0.00063228, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_251_0.json](analysis/traces/validation_v2_mathd_algebra_251_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'focus': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:18515`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_251_0.json](analysis/traces/validation_B_mathd_algebra_251_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6376`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_421 / seed 0: shared_success

v2: solved, $0.00216480, 3 model requests. Candidate B: solved, $0.00278670, 3 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_421_0.json](analysis/traces/validation_v2_mathd_algebra_421_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:10461`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_421_0.json](analysis/traces/validation_B_mathd_algebra_421_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:7045`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1964_p2 / seed 0: shared_success

v2: solved, $0.03109670, 13 model requests. Candidate B: solved, $0.02317124, 9 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1964_p2_0.json](analysis/traces/validation_v2_imo_1964_p2_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 3, 'missing_name_or_hypothesis': 1, 'type_or_rewrite_shape': 2, 'tactic_does_not_close_goal': 3}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:20901`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1964_p2_0.json](analysis/traces/validation_B_imo_1964_p2_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 1, 'type_or_rewrite_shape': 1, 'tactic_does_not_close_goal': 5, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9865`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_303 / seed 1: shared_failure

v2: admission:price, $0.03678682, 21 model requests. Candidate B: admission:price, $0.03631528, 24 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_303_1.json](analysis/traces/validation_v2_mathd_numbertheory_303_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
{ apply Nat.mul_le_mul_r.
```

```text
(-32003, 'Coq: The reference Nat.mul_le_mul_r was not found in the current environment.')
```

Accepted prefix: 22 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:25691`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_303_1.json](analysis/traces/validation_B_mathd_numbertheory_303_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
{ apply PeanoNat.Nat.mod_lt; lia. }
```

```text
(-32003, 'Coq: The reference PeanoNat.Nat.mod_lt was not found in the current environment.')
```

Accepted prefix: 8 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:12329`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_190 / seed 1: shared_success

v2: solved, $0.00052906, 1 model requests. Candidate B: solved, $0.00032708, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_190_1.json](analysis/traces/validation_v2_mathd_algebra_190_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8670`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_190_1.json](analysis/traces/validation_B_mathd_algebra_190_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:6571`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_37 / seed 0: shared_failure

v2: admission:rocq_seconds, $0.03623244, 25 model requests. Candidate B: admission:rocq_seconds, $0.02404314, 22 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_37_0.json](analysis/traces/validation_v2_mathd_numbertheory_37_0.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof mathd_numbertheory_37): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 23 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26349`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_37_0.json](analysis/traces/validation_B_mathd_numbertheory_37_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
{ ring.
```

```text
(-32003, 'Coq: Tactic failure: not a valid ring equation.')
```

Accepted prefix: 9 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14202`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_303 / seed 0: shared_failure

v2: admission:price, $0.03832704, 33 model requests. Candidate B: admission:price, $0.03720136, 30 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_303_0.json](analysis/traces/validation_v2_mathd_numbertheory_303_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
do 172 (destruct n as [|n]).
```

```text
(-32003, 'Coq: The variable n was not found in the current environment.')
```

Accepted prefix: 5 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26221`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_303_0.json](analysis/traces/validation_B_mathd_numbertheory_303_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
destruct (le_gt_dec n 13) as [Hs | Hl].
```

```text
(-32003, 'Coq: The variable le_gt_dec was not found in the current environment.')
```

Accepted prefix: 10 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13355`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2002_p3 / seed 1: shared_success

v2: solved, $0.01407108, 8 model requests. Candidate B: solved, $0.01670930, 23 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2002_p3_1.json](analysis/traces/validation_v2_amc12b_2002_p3_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:10156`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2002_p3_1.json](analysis/traces/validation_B_amc12b_2002_p3_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1, 'focus': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9636`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2019_p21 / seed 0: shared_failure

v2: admission:price, $0.02479886, 38 model requests. Candidate B: admission:price, $0.04038580, 29 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2019_p21_0.json](analysis/traces/validation_v2_amc12a_2019_p21_0.json).
No failed verifier receipt: inspect the final model output and terminal admission event in the linked cell record.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:18887`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2019_p21_0.json](analysis/traces/validation_B_amc12a_2019_p21_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
+ change (2 / (sqrt 2 * sqrt 2) = 1)%R.
```

```text
(-32003, 'Coq: Not convertible.')
```

Accepted prefix: 14 tactics; remaining focused goals: 3.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13714`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_433 / seed 0: shared_success

v2: solved, $0.00235882, 5 model requests. Candidate B: solved, $0.00297174, 4 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_433_0.json](analysis/traces/validation_v2_mathd_algebra_433_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:24744`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_433_0.json](analysis/traces/validation_B_mathd_algebra_433_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8131`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_405 / seed 1: candidate_win

v2: admission:price, $0.03778502, 11 model requests. Candidate B: solved, $0.03478932, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_405_1.json](analysis/traces/validation_v2_mathd_numbertheory_405_1.json).
Last verifier symptom: focus; tactic:

```rocq
}
```

```text
(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')
```

Accepted prefix: 40 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:25120`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_405_1.json](analysis/traces/validation_B_mathd_numbertheory_405_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1, 'type_or_rewrite_shape': 3, 'tactic_does_not_close_goal': 1, 'missing_name_or_hypothesis': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13023`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_284 / seed 1: shared_success

v2: solved, $0.00028296, 1 model requests. Candidate B: solved, $0.00025816, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_284_1.json](analysis/traces/validation_v2_mathd_numbertheory_284_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:20973`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_284_1.json](analysis/traces/validation_B_mathd_numbertheory_284_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8264`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_327 / seed 0: shared_success

v2: solved, $0.00148550, 3 model requests. Candidate B: solved, $0.00138964, 4 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_327_0.json](analysis/traces/validation_v2_mathd_algebra_327_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:18784`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_327_0.json](analysis/traces/validation_B_mathd_algebra_327_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8696`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / algebra_others_exirrpowirrrat / seed 0: shared_failure

v2: admission:price, $0.03675184, 31 model requests. Candidate B: admission:price, $0.03852468, 28 model requests.

**v2 evidence:** [analysis/traces/validation_v2_algebra_others_exirrpowirrrat_0.json](analysis/traces/validation_v2_algebra_others_exirrpowirrrat_0.json).
Last verifier symptom: focus; tactic:

```rocq
}
```

```text
(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')
```

Accepted prefix: 3 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:14552`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_algebra_others_exirrpowirrrat_0.json](analysis/traces/validation_B_algebra_others_exirrpowirrrat_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
field_simplify [HqR] in Hsqr.
```

```text
(-32003, 'Coq: No matching clauses for match.')
```

Accepted prefix: 13 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:12860`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1984_p6 / seed 0: shared_failure

v2: admission:price, $0.04111188, 23 model requests. Candidate B: admission:price, $0.04200458, 16 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1984_p6_0.json](analysis/traces/validation_v2_imo_1984_p6_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nia.
```

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Accepted prefix: 22 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26374`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1984_p6_0.json](analysis/traces/validation_B_imo_1984_p6_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
{ rewrite Hpow.
```

```text
(-32003, 'Coq: Found no subterm matching "2 ^ k" in the current goal.')
```

Accepted prefix: 40 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14423`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_214 / seed 1: shared_success

v2: solved, $0.00059986, 1 model requests. Candidate B: solved, $0.00032360, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_214_1.json](analysis/traces/validation_v2_mathd_algebra_214_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8671`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_214_1.json](analysis/traces/validation_B_mathd_algebra_214_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:8997`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1984_p6 / seed 1: shared_failure

v2: admission:price, $0.03690224, 22 model requests. Candidate B: admission:rocq_seconds, $0.01137172, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1984_p6_1.json](analysis/traces/validation_v2_imo_1984_p6_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
- change (2 * oa + 1 + (2 * od + 1) = 2 ^ k * 2) in H4.
```

```text
(-32003, 'Coq: Not convertible.')
```

Accepted prefix: 15 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17084`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1984_p6_1.json](analysis/traces/validation_B_imo_1984_p6_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
nia.
```

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 7 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14262`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_37 / seed 1: shared_failure

v2: admission:rocq_seconds, $0.02089896, 18 model requests. Candidate B: admission:rocq_seconds, $0.02488848, 25 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_37_1.json](analysis/traces/validation_v2_mathd_numbertheory_37_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
reflexivity.
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 9 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26490`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_37_1.json](analysis/traces/validation_B_mathd_numbertheory_37_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
native_compute.
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 9 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14420`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_421 / seed 1: shared_success

v2: solved, $0.00123568, 3 model requests. Candidate B: solved, $0.00093348, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_421_1.json](analysis/traces/validation_v2_mathd_algebra_421_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17996`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_421_1.json](analysis/traces/validation_B_mathd_algebra_421_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:9706`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_405 / seed 0: shared_failure

v2: admission:price, $0.04031842, 14 model requests. Candidate B: admission:price, $0.03663122, 12 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_405_0.json](analysis/traces/validation_v2_mathd_numbertheory_405_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite (Hpat a), (Hpat b), (Hpat c).
```

```text
(-32003, 'Coq: Found no subterm matching "t a mod 7" in the current goal.')
```

Accepted prefix: 52 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:12630`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_405_0.json](analysis/traces/validation_B_mathd_numbertheory_405_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite T17, T16, h1.
```

```text
(-32003, 'Coq: Found no subterm matching "t 16" in the current goal.')
```

Accepted prefix: 54 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13463`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_43 / seed 0: shared_failure

v2: admission:price, $0.03728252, 24 model requests. Candidate B: admission:rocq_seconds, $0.02030272, 24 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_43_0.json](analysis/traces/validation_v2_mathd_numbertheory_43_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
reflexivity.
```

```text
(-32003, 'Coq: In environment\nn, d : nat\nUnable to unify "(fact n mod d + n * (fact n mod d)) mod d" with\n "(fact n mod d + (n mod d * (fact n mod d)) mod d) mod d".')
```

Accepted prefix: 6 tactics; remaining focused goals: 3.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17164`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_43_0.json](analysis/traces/validation_B_mathd_numbertheory_43_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
apply (proj2 (Nat.Div0.div_exact (fact 942) (15 ^ 233))).
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 3 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14445`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_282 / seed 1: shared_failure

v2: admission:price, $0.03021478, 39 model requests. Candidate B: admission:price, $0.02789924, 37 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_282_1.json](analysis/traces/validation_v2_mathd_algebra_282_1.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:25218`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_282_1.json](analysis/traces/validation_B_mathd_algebra_282_1.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13255`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_algebra_393 / seed 0: shared_success

v2: solved, $0.01220644, 12 model requests. Candidate B: solved, $0.00498752, 5 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_algebra_393_0.json](analysis/traces/validation_v2_mathd_algebra_393_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 4, 'syntax_or_pattern': 3}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:22192`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_algebra_393_0.json](analysis/traces/validation_B_mathd_algebra_393_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'type_or_rewrite_shape': 2}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:10632`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_64 / seed 0: shared_success

v2: solved, $0.00394300, 7 model requests. Candidate B: solved, $0.01151334, 13 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_64_0.json](analysis/traces/validation_v2_mathd_numbertheory_64_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'focus': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:24331`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_64_0.json](analysis/traces/validation_B_mathd_numbertheory_64_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'focus': 1, 'tactic_does_not_close_goal': 1, 'missing_name_or_hypothesis': 2, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:11296`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2008_p4 / seed 0: candidate_loss

v2: solved, $0.01759068, 14 model requests. Candidate B: admission:price, $0.02423306, 44 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2008_p4_0.json](analysis/traces/validation_v2_amc12a_2008_p4_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'open_obligations': 1, 'type_or_rewrite_shape': 3, 'tactic_does_not_close_goal': 2, 'other_verifier_failure': 2, 'focus': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21509`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2008_p4_0.json](analysis/traces/validation_B_amc12a_2008_p4_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
fail 1 "The theorem is false as stated: Rprod 501 includes the k = 0 factor 4 / 0 = 0, so the product is 0, not 502.".
```

```text
(-32003, 'Coq: Tactic failure: The theorem is false as stated: Rprod 501 includes the k = 0 factor 4 / 0 = 0, so the product is 0, not 502. (level 1).')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13305`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2002_p3 / seed 0: shared_success

v2: solved, $0.00810260, 9 model requests. Candidate B: solved, $0.00929192, 10 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2002_p3_0.json](analysis/traces/validation_v2_amc12b_2002_p3_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:23479`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2002_p3_0.json](analysis/traces/validation_B_amc12b_2002_p3_0.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'syntax_or_pattern': 3}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:11195`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_43 / seed 1: shared_failure

v2: admission:rocq_seconds, $0.03985986, 22 model requests. Candidate B: admission:rocq_seconds, $0.02644408, 28 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_43_1.json](analysis/traces/validation_v2_mathd_numbertheory_43_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
{ rewrite <- (Hmf 942 (15 ^ 233)).
```

```text
(-32003, 'Coq: The variable Hmf was not found in the current environment.')
```

Accepted prefix: 3 tactics; remaining focused goals: 2.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26562`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_43_1.json](analysis/traces/validation_B_mathd_numbertheory_43_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
apply (proj2 (Nat.div_exact (fact 942) (15 ^ 233) (Nat.pow_nonzero 15 233 ltac:(lia)))).
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 4 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14519`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_530 / seed 1: shared_failure

v2: admission:price, $0.03970360, 23 model requests. Candidate B: admission:price, $0.03686152, 25 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_530_1.json](analysis/traces/validation_v2_mathd_numbertheory_530_1.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nra.
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 37 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:23368`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_530_1.json](analysis/traces/validation_B_mathd_numbertheory_530_1.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite E.
```

```text
(-32003, 'Coq: Found no subterm matching "INR (5 * k)" in the current goal.')
```

Accepted prefix: 19 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13693`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_530 / seed 0: shared_failure

v2: admission:price, $0.03751260, 25 model requests. Candidate B: admission:price, $0.04059172, 33 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_530_0.json](analysis/traces/validation_v2_mathd_numbertheory_530_0.json).
Last verifier symptom: syntax_or_pattern; tactic:

```rocq
change INR n / INR k < 6 in Hlt.
```

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Accepted prefix: 40 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:18028`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_530_0.json](analysis/traces/validation_B_mathd_numbertheory_530_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
nra.
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 32 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13888`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1984_p7 / seed 1: shared_failure

v2: admission:price, $0.04108986, 20 model requests. Candidate B: admission:price, $0.03183038, 22 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1984_p7_1.json](analysis/traces/validation_v2_aime_1984_p7_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
assert (h1000 : f 1000 = 997).
```

```text
(-32003, 'Coq: The variable f was not found in the current environment.')
```

Accepted prefix: 0 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:16015`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1984_p7_1.json](analysis/traces/validation_B_aime_1984_p7_1.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
assert (h1000 : f 1000 = 997) by rewrite (Hhi 1000 ltac:(lia)); reflexivity.
```

```text
(-32003, 'Coq: Proof is not complete.')
```

Accepted prefix: 1 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13787`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2008_p4 / seed 1: candidate_win

v2: admission:price, $0.03933488, 21 model requests. Candidate B: solved, $0.01085006, 9 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2008_p4_1.json](analysis/traces/validation_v2_amc12a_2008_p4_1.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
exact Hd.
```

```text
(-32003, 'Coq: The variable Hd was not found in the current environment.')
```

Accepted prefix: 20 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:17028`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2008_p4_1.json](analysis/traces/validation_B_amc12a_2008_p4_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'type_or_rewrite_shape': 1, 'missing_name_or_hypothesis': 1, 'other_verifier_failure': 1, 'focus': 1, 'syntax_or_pattern': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:12158`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1969_p2 / seed 1: shared_failure

v2: admission:price, $0.03288070, 37 model requests. Candidate B: admission:price, $0.03652732, 21 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1969_p2_1.json](analysis/traces/validation_v2_imo_1969_p2_1.json).
Last verifier symptom: open_obligations; tactic:

```rocq
Qed.
```

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Accepted prefix: 1 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:23022`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1969_p2_1.json](analysis/traces/validation_B_imo_1969_p2_1.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
apply Hneq.
```

```text
(-32003, 'Coq: In environment\nm, n : R\nk : nat\na : nat -> R\ny : R -> R\nHk : (0 < k)%nat\nHy :\n  forall x : R,\n  y x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm : y m = 0\nHn : y n = 0\nHneq : m <> n\nq : R\nHq : sin_in (m - n)² q\nUnable to unify "m <> n" with "q = 0".')
```

Accepted prefix: 9 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13842`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / imo_1981_p6 / seed 1: shared_success

v2: solved, $0.01314770, 8 model requests. Candidate B: solved, $0.00588016, 8 model requests.

**v2 evidence:** [analysis/traces/validation_v2_imo_1981_p6_1.json](analysis/traces/validation_v2_imo_1981_p6_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1, 'tactic_does_not_close_goal': 1, 'syntax_or_pattern': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:13824`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_imo_1981_p6_1.json](analysis/traces/validation_B_imo_1981_p6_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:12139`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2002_p6 / seed 1: shared_success

v2: solved, $0.00107932, 2 model requests. Candidate B: solved, $0.00035346, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2002_p6_1.json](analysis/traces/validation_v2_amc12a_2002_p6_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:9221`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2002_p6_1.json](analysis/traces/validation_B_amc12a_2002_p6_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:11536`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1991_p6 / seed 0: shared_failure

v2: admission:price, $0.04010680, 19 model requests. Candidate B: admission:price, $0.03600614, 17 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1991_p6_0.json](analysis/traces/validation_v2_aime_1991_p6_0.json).
Last verifier symptom: missing_name_or_hypothesis; tactic:

```rocq
- eapply le_trans.
```

```text
(-32003, 'Coq: The variable le_trans was not found in the current environment.')
```

Accepted prefix: 15 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:26247`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1991_p6_0.json](analysis/traces/validation_B_aime_1991_p6_0.json).
Last verifier symptom: tactic_does_not_close_goal; tactic:

```rocq
lra.
```

```text
(-32003, 'Coq: No applicable tactic.')
```

Accepted prefix: 17 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14314`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12_2000_p12 / seed 1: shared_success

v2: solved, $0.00783590, 5 model requests. Candidate B: solved, $0.00461338, 6 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12_2000_p12_1.json](analysis/traces/validation_v2_amc12_2000_p12_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 2, 'other_verifier_failure': 2}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:12955`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12_2000_p12_1.json](analysis/traces/validation_B_amc12_2000_p12_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'other_verifier_failure': 3}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14203`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12_2001_p21 / seed 0: shared_failure

v2: admission:rocq_seconds, $0.02212704, 15 model requests. Candidate B: admission:rocq_seconds, $0.02867474, 15 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12_2001_p21_0.json](analysis/traces/validation_v2_amc12_2001_p21_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
assert (Had : a = d + 10) by nia.
```

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 56s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 9 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:16549`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12_2001_p21_0.json](analysis/traces/validation_B_amc12_2001_p21_0.json).
Last verifier symptom: other_verifier_failure; tactic:

```rocq
- repeat (destruct b as [|b]; [nia|]).
```

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Accepted prefix: 10 tactics; remaining focused goals: 0.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14575`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2003_p6 / seed 0: shared_success

v2: solved, $0.02987572, 21 model requests. Candidate B: solved, $0.02095940, 12 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2003_p6_0.json](analysis/traces/validation_v2_amc12b_2003_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 3, 'other_verifier_failure': 4, 'missing_name_or_hypothesis': 2, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:20056`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2003_p6_0.json](analysis/traces/validation_B_amc12b_2003_p6_0.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 2, 'missing_name_or_hypothesis': 2, 'tactic_does_not_close_goal': 2, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13801`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12a_2016_p3 / seed 1: shared_success

v2: solved, $0.04251414, 17 model requests. Candidate B: solved, $0.00536502, 5 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12a_2016_p3_1.json](analysis/traces/validation_v2_amc12a_2016_p3_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'other_verifier_failure': 3, 'syntax_or_pattern': 1, 'tactic_does_not_close_goal': 4, 'type_or_rewrite_shape': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:10901`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12a_2016_p3_1.json](analysis/traces/validation_B_amc12a_2016_p3_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'missing_name_or_hypothesis': 1, 'tactic_does_not_close_goal': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13434`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1989_p8 / seed 1: shared_success

v2: solved, $0.00062206, 1 model requests. Candidate B: solved, $0.00023522, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1989_p8_1.json](analysis/traces/validation_v2_aime_1989_p8_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8634`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1989_p8_1.json](analysis/traces/validation_B_aime_1989_p8_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13090`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_33 / seed 1: shared_success

v2: solved, $0.00110092, 2 model requests. Candidate B: solved, $0.00074812, 2 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_33_1.json](analysis/traces/validation_v2_mathd_numbertheory_33_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:16876`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_33_1.json](analysis/traces/validation_B_mathd_numbertheory_33_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13224`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / amc12b_2003_p6 / seed 1: shared_success

v2: solved, $0.01578708, 24 model requests. Candidate B: solved, $0.04105558, 18 model requests.

**v2 evidence:** [analysis/traces/validation_v2_amc12b_2003_p6_1.json](analysis/traces/validation_v2_amc12b_2003_p6_1.json).
Terminal verifier: success=True, assisted completion=False. Earlier verifier-error categories: {'syntax_or_pattern': 1, 'other_verifier_failure': 1}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:24835`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_amc12b_2003_p6_1.json](analysis/traces/validation_B_amc12b_2003_p6_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {'type_or_rewrite_shape': 4, 'syntax_or_pattern': 1, 'missing_name_or_hypothesis': 2, 'other_verifier_failure': 2, 'tactic_does_not_close_goal': 1, 'focus': 1}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14292`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / mathd_numbertheory_461 / seed 1: shared_success

v2: solved, $0.00040570, 1 model requests. Candidate B: solved, $0.00053810, 1 model requests.

**v2 evidence:** [analysis/traces/validation_v2_mathd_numbertheory_461_1.json](analysis/traces/validation_v2_mathd_numbertheory_461_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:8995`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_mathd_numbertheory_461_1.json](analysis/traces/validation_B_mathd_numbertheory_461_1.json).
Terminal verifier: success=True, assisted completion=True. Earlier verifier-error categories: {}.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:13362`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

## validation / aime_1984_p7 / seed 0: shared_failure

v2: admission:price, $0.03741778, 11 model requests. Candidate B: admission:price, $0.03894534, 12 model requests.

**v2 evidence:** [analysis/traces/validation_v2_aime_1984_p7_0.json](analysis/traces/validation_v2_aime_1984_p7_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite H1003, H1000.
```

```text
(-32003, 'Coq: Found no subterm matching "f 1003" in the current goal.')
```

Accepted prefix: 31 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_revision_20260913/events.jsonl:21388`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

**B evidence:** [analysis/traces/validation_B_aime_1984_p7_0.json](analysis/traces/validation_B_aime_1984_p7_0.json).
Last verifier symptom: type_or_rewrite_shape; tactic:

```rocq
rewrite H998.
```

```text
(-32003, 'Coq: Found no subterm matching "f 998" in the current goal.')
```

Accepted prefix: 28 tactics; remaining focused goals: 1.
Terminal event: `experiments/campaigns/ace_learning_20260914/events.jsonl:14562`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`.

