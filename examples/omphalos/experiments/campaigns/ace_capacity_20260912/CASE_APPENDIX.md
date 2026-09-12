# Capacity follow-up: proof-case appendix

Every diagnostic observation and every failed/discordant validation observation is listed below. Full ordered checks, model replies, errors, proof prefixes, token usage, admission events and goal views are retained in `mechanism_diagnostics_v2.json` and `crossover_diagnostics.json`. Categories describe observed verifier errors; they do not prove their root cause.

## Eight-problem outcome matrix

S = kernel-verified success; F = unsolved; P = platform failure. One seed, eight selected trainX problems.

| Model/problem | A | B | C | D | E | C money | E money | C search | E search |
|---|---|---|---|---|---|---|---|---|---|
| Luna mathd_numbertheory_48 | S | S | S | S | S | S | S | S | S |
| Luna imo_1967_p3 | F | F | F | F | F | F | P | F | P |
| Luna mathd_algebra_28 | S | S | S | S | S | S | S | S | S |
| Luna amc12b_2002_p11 | F | F | F | F | F | F | F | F | F |
| Luna amc12a_2020_p13 | F | F | F | F | F | F | F | F | F |
| Luna mathd_numbertheory_629 | F | F | S | F | F | S | F | S | F |
| Luna algebra_amgm_sum1toneqn_prod1tonleq1 | F | F | F | F | F | F | F | F | F |
| Luna aime_1988_p8 | S | S | S | S | S | S | S | S | S |
| Terra mathd_numbertheory_48 | S | S | S | S | S | S | S | S | S |
| Terra imo_1967_p3 | F | F | F | F | F | F | F | F | F |
| Terra mathd_algebra_28 | S | S | S | S | S | S | S | S | S |
| Terra amc12b_2002_p11 | F | F | S | S | F | S | S | S | S |
| Terra amc12a_2020_p13 | F | F | F | F | F | F | S | F | S |
| Terra mathd_numbertheory_629 | F | F | F | S | F | S | S | S | S |
| Terra algebra_amgm_sum1toneqn_prod1tonleq1 | F | F | F | S | F | S | S | S | S |
| Terra aime_1988_p8 | S | S | S | S | S | S | S | S | S |

## Diagnostic and continuation cells

### aime_1988_p8__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__A-level0__gpt-5.6-luna__seed0`. Solved; $0.03988716; 12 completions; 2.156 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'not-convertible': 1, 'ring-failure': 1, 'syntax-error': 7}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__A-level0__gpt-5.6-terra__seed0`. Solved; $0.05664040; 4 completions; 1.139 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__B-level0__gpt-5.6-luna__seed0`. Solved; $0.00675352; 4 completions; 9.113 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__B-level0__gpt-5.6-terra__seed0`. Solved; $0.11088940; 5 completions; 1.185 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "2" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-luna__seed0`. Solved; $0.01791378; 8 completions; 17.485 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'syntax-error': 4, 'type-mismatch': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-terra__seed0`. Solved; $0.05238220; 3 completions; 0.073 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference norm_num was not found in the current environment.')
```

### aime_1988_p8__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-luna__seed0`. Solved; $0.01791378; 8 completions; 17.485 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'syntax-error': 4, 'type-mismatch': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-terra__seed0`. Solved; $0.05238220; 3 completions; 0.073 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference norm_num was not found in the current environment.')
```

### aime_1988_p8__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-luna__seed0`. Solved; $0.01791378; 8 completions; 17.485 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'syntax-error': 4, 'type-mismatch': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__C-level0__gpt-5.6-terra__seed0`. Solved; $0.05238220; 3 completions; 0.073 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference norm_num was not found in the current environment.')
```

### aime_1988_p8__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__D-level0__gpt-5.6-luna__seed0`. Solved; $0.00819626; 5 completions; 9.276 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 3, 'type-mismatch': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")
```

### aime_1988_p8__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__D-level0__gpt-5.6-terra__seed0`. Solved; $0.05951420; 4 completions; 1.147 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00853438; 5 completions; 1.171 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-terra__seed0`. Solved; $0.07348820; 5 completions; 1.215 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00853438; 5 completions; 1.171 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-terra__seed0`. Solved; $0.07348820; 5 completions; 1.215 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00853438; 5 completions; 1.171 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### aime_1988_p8__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/aime_1988_p8__E-level0__gpt-5.6-terra__seed0`. Solved; $0.07348820; 5 completions; 1.215 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nf : nat -> nat -> R\nHdiag : forall x : nat, (x > 0)%nat -> f x x = INR x\nHsym : forall x y : nat, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x\nHrec :\n  forall x y : nat,\n  (x > 0)%nat ->\n  (y > 0)%nat -> (INR x + INR y) * f x y = INR y * f x (x + y)%nat\nThe term "14" has type "R" while it is expected to have type "nat".')
```

### algebra_amgm_sum1toneqn_prod1tonleq1__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__A-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03737514; 20 completions; 3.496 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "no-applicable-tactic",
  "elapsed": 0.09719289280474186,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < S (S n))%nat -> 0 <= a i\nHsum  : sum_n a n + a n + a (S n) =\nmatch n with\n| 0%nat => 1\n| S _ => INR n + 1\nend + 1\nIH  : (forall i : nat, (i < S n)%nat -> 0 <= a i) ->\nsum_n a n + a n = match n with\n                  | 0%nat => 1\n                  | S _ => INR n + 1\n                  end ->\nprod_n a n * a n <= 1\nH0  : 0 <= a n\nH1  : 0 <= a (S n)\nHprod  : 0 <= prod_n a n\n|-prod_n a n * a n * a (S n) <= 1"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros n a Ha Hsum.",
    "induction n as [|n IH].",
    "- simpl in *. nra.",
    "- simpl in Hsum.",
    "destruct n as [|n].",
    "+ simpl in *. nra.",
    "+ simpl in *.",
    "assert (H0 : 0 <= a n) by (apply Ha; lia).",
    "assert (H1 : 0 <= a (S n)) by (apply Ha; lia).",
    "assert (Hprod : 0 <= prod_n a n).",
    "{ assert (Haux : forall k : nat, (k <= n)%nat -> 0 <= prod_n a k).",
    "{ intros k Hk.",
    "induction k as [|k IHk].",
    "- simpl. lra.",
    "- simpl. apply Rmult_le_pos.",
    "+ apply IHk. lia.",
    "+ apply Ha. lia.",
    "}",
    "apply Haux. lia.",
    "}"
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__A-level0__gpt-5.6-terra__seed0`. Unsolved; $0.42416740; 22 completions; 3.117 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-product`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 1, 'no-product': 1, 'subproof-incomplete': 1, 'type-mismatch': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "no-product",
  "elapsed": 0.04402386303991079,
  "error": "(-32003, 'Coq: No product even after head-reduction.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHnonneg  : forall i : nat, (i < n)%nat -> 0 <= a i\nHsum  : sum_n a n = INR n\nm  : nat\nIH  : (forall i : nat, (i < m)%nat -> 0 <= a i) ->\n(exists i : nat, (i < m)%nat /\\ a i = 0) \\/\n(forall i : nat, (i < m)%nat -> 0 < a i)\nH  : forall i : nat, (i < S m)%nat -> 0 <= a i\nHp  : forall i : nat, (i < m)%nat -> 0 < a i\n|-0 = a m"
  ],
  "success": false,
  "tactic": "intros i Hi.",
  "verified_prefix": [
    "intros n a Hnonneg Hsum.",
    "assert (Hcases : (exists i, (i < n)%nat /\\ a i = 0) \\/ (forall i, (i < n)%nat -> 0 < a i)).",
    "{ assert (Haux : forall m, (forall i, (i < m)%nat -> 0 <= a i) -> (exists i, (i < m)%nat /\\ a i = 0) \\/ (forall i, (i < m)%nat -> 0 < a i)).",
    "{ intro m.",
    "induction m as [|m IH].",
    "- intro H.",
    "right.",
    "intros i Hi.",
    "lia.",
    "- intro H.",
    "destruct (IH (fun i Hi => H i ltac:(lia))) as [Hz | Hp].",
    "+ left.",
    "destruct Hz as [i [Hi Hai]].",
    "exists i.",
    "split.",
    "* lia.",
    "* exact Hai.",
    "+ destruct (Rle_lt_or_eq_dec 0 (a m)) as [Hlt | Heq].",
    "* right."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__B-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03347370; 17 completions; 1.665 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `other`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 2, 'other': 2}`.

First error:

```text
Proof obligations may not be bypassed.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 17,
  "category": "other",
  "elapsed": 0,
  "error": "Proof obligations may not be bypassed.",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "unsafe command",
  "verified_prefix": []
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__B-level0__gpt-5.6-terra__seed0`. Unsolved; $0.41110460; 31 completions; 2.857 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'incomplete-proof': 2, 'no-applicable-tactic': 1, 'other': 3, 'unknown-reference': 2}`.

First error:

```text
Proof obligations may not be bypassed.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "unknown-reference",
  "elapsed": 0.03742004930973053,
  "error": "(-32003, 'Coq: The variable Hz was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHnonneg  : forall i : nat, (i < S n)%nat -> 0 <= a i\n|-forall i : nat, (i < n)%nat -> 0 <= a i",
    "n  : nat\na  : nat -> R\nHnonneg  : forall i : nat, (i < S n)%nat -> 0 <= a i\nHz  : prod_n a n = 0\n|-prod_n a (S n) = 0 \\/ (forall i : nat, (i < S n)%nat -> 0 < a i)",
    "n  : nat\na  : nat -> R\nHnonneg  : forall i : nat, (i < S n)%nat -> 0 <= a i\nHp  : forall i : nat, (i < n)%nat -> 0 < a i\n|-prod_n a (S n) = 0 \\/ (forall i : nat, (i < S n)%nat -> 0 < a i)"
  ],
  "success": false,
  "tactic": "+ left. simpl. rewrite Hz. ring.",
  "verified_prefix": [
    "intros n a Hnonneg Hsum.",
    "assert (Hcases : prod_n a n = 0 \\/ forall i, (i < n)%nat -> 0 < a i).",
    "{ clear Hsum.",
    "induction n as [|n IH].",
    "- right. intros i Hi. lia.",
    "- destruct IH as [Hz | Hp]."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04316856; 18 completions; 2.534 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `other`; added goal views: 0. Error counts: `{'incomplete-proof': 3, 'no-applicable-tactic': 1, 'other': 2, 'syntax-error': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "other",
  "elapsed": 0,
  "error": "Proof obligations may not be bypassed.",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "unsafe command",
  "verified_prefix": []
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level0__gpt-5.6-terra__seed0`. Unsolved; $0.38116620; 20 completions; 3.858 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 1. Error counts: `{'incomplete-proof': 2, 'no-applicable-tactic': 2, 'type-mismatch': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\na : nat -> R\nHnonneg : forall i : nat, (i < 1)%nat -> 0 <= a i\nHsum : 0 + a 0%nat = 1\nIH :\n  (forall i : nat, (i < 0)%nat -> 0 <= a i) ->\n  sum_n a 0 = INR 0 -> prod_n a 0 <= 1\nThe term "0" has type "R" while it is expected to have type "nat".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "incomplete-proof",
  "elapsed": 0.033159272745251656,
  "error": "(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHnonneg  : forall i : nat, (i < S (S n))%nat -> 0 <= a i\nHsum  : sum_n a n + a n + a (S n) =\nmatch n with\n| 0%nat => 1\n| S _ => INR n + 1\nend + 1\nIH  : (forall i : nat, (i < S n)%nat -> 0 <= a i) ->\nsum_n a (S n) = INR (S n) -> prod_n a (S n) <= 1\nHa  : 0 <= a (S n)\nHs  : 0 <= sum_n a (S n)\n|-prod_n a n * a n * a (S n) <= 1"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros n a Hnonneg Hsum.",
    "induction n as [|n IH].",
    "- simpl.",
    "lra.",
    "- destruct n as [|n].",
    "+ simpl in Hsum |- *.",
    "lra.",
    "+ simpl in Hsum |- *.",
    "assert (Ha : 0 <= a (S n)).",
    "{ apply Hnonneg. lia. }",
    "assert (Hs : 0 <= sum_n a (S n)).",
    "{ clear Hsum IH.",
    "induction n as [|n IHn].",
    "- simpl.",
    "assert (H0 : 0 <= a 0%nat).",
    "{ apply Hnonneg. lia. }",
    "lra.",
    "- simpl.",
    "assert (Hk : 0 <= a (S n)) by (apply Hnonneg; lia).",
    "assert (Hrec : 0 <= sum_n a (S n)).",
    "{ apply IHn.",
    "- intros i Hi.",
    "apply Hnonneg.",
    "lia.",
    "- exact Hk.",
    "}",
    "change (0 <= sum_n a (S n) + a (S n)).",
    "lra.",
    "}"
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level1__gpt-5.6-luna__seed0`. Unsolved; $0.09920150; 64 completions; 4.007 verifier seconds.

Terminal: `stopped`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 39, 'no-applicable-tactic': 2, 'other': 4, 'syntax-error': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 64,
  "category": "incomplete-proof",
  "elapsed": 0.005054821260273457,
  "error": "(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < n)%nat -> 0 <= a i\nHsum  : sum_n a n = INR n\n|-prod_n a n <= 1"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros n a Ha Hsum."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level1__gpt-5.6-terra__seed0`. Solved; $1.13082780; 38 completions; 12.854 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'focus-error': 2, 'incomplete-proof': 2, 'no-applicable-tactic': 6, 'no-such-goal': 1, 'rewrite-no-match': 1, 'type-mismatch': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\na : nat -> R\nHnonneg : forall i : nat, (i < 1)%nat -> 0 <= a i\nHsum : 0 + a 0%nat = 1\nIH :\n  (forall i : nat, (i < 0)%nat -> 0 <= a i) ->\n  sum_n a 0 = INR 0 -> prod_n a 0 <= 1\nThe term "0" has type "R" while it is expected to have type "nat".')
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level2__gpt-5.6-luna__seed0`. Unsolved; $0.11425808; 79 completions; 5.032 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 54, 'no-applicable-tactic': 2, 'other': 4, 'syntax-error': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 79,
  "category": "incomplete-proof",
  "elapsed": 0.005354670807719231,
  "error": "(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < n)%nat -> 0 <= a i\nHsum  : sum_n a n = INR n\n|-prod_n a n <= 1"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros n a Ha Hsum."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__C-level1__gpt-5.6-terra__seed0`. Solved; $1.13082780; 38 completions; 12.854 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'focus-error': 2, 'incomplete-proof': 2, 'no-applicable-tactic': 6, 'no-such-goal': 1, 'rewrite-no-match': 1, 'type-mismatch': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\na : nat -> R\nHnonneg : forall i : nat, (i < 1)%nat -> 0 <= a i\nHsum : 0 + a 0%nat = 1\nIH :\n  (forall i : nat, (i < 0)%nat -> 0 <= a i) ->\n  sum_n a 0 = INR 0 -> prod_n a 0 <= 1\nThe term "0" has type "R" while it is expected to have type "nat".')
```

### algebra_amgm_sum1toneqn_prod1tonleq1__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__D-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03612176; 19 completions; 2.442 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unify-failure`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'other': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "unify-failure",
  "elapsed": 0.005741717293858528,
  "error": "(-32003, 'Coq: In environment\\nn : nat\\na : nat -> R\\nHa : forall i : nat, (i < S (S n))%nat -> 0 <= a i\\nHsum : sum_n a (S n) + a (S n) = INR (S n) + 1\\nIH :\\n  (forall i : nat, (i < S n)%nat -> 0 <= a i) ->\\n  sum_n a (S n) = INR (S n) -> prod_n a (S n) <= 1\\nHnonneg : 0 <= a (S n)\\nIHn :\\n  (forall i : nat, (i < S n)%nat -> 0 <= a i) ->\\n  sum_n a n + a n = match n with\\n                    | 0%nat => 1\\n                    | S _ => INR n + 1\\n                    end ->\\n  ((forall i : nat, (i < n)%nat -> 0 <= a i) ->\\n   sum_n a n = INR n -> prod_n a n <= 1) ->\\n  0 <= a n -> 0 <= sum_n a n\\nUnable to unify\\n \"?M1842 + ?M1844 < ?M1843 + ?M1845 \\\\/ ?M1842 + ?M1844 = ?M1843 + ?M1845\"\\nwith \"0 < sum_n a n + a n \\\\/ 0 = sum_n a n + a n\".')",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "- simpl. apply Rplus_le_compat.",
  "verified_prefix": [
    "intros n a Ha Hsum.",
    "induction n as [|n IH].",
    "- simpl. lra.",
    "- simpl in Hsum |- *.",
    "assert (Hnonneg : 0 <= a n) by (apply Ha; lia).",
    "assert (Hprev : 0 <= sum_n a n).",
    "{ induction n as [|n IHn].",
    "- simpl. lra."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__D-level0__gpt-5.6-terra__seed0`. Solved; $0.21377040; 29 completions; 1.116 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03597610; 22 completions; 2.517 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 3, 'type-mismatch': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The variable a was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "no-applicable-tactic",
  "elapsed": 0.024602903984487057,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < S n)%nat -> 0 <= a i\nHsum  : sum_n a n + a n = match n with\n                  | 0%nat => 1\n                  | S _ => INR n + 1\n                  end\nIH  : sum_n a n = INR n -> prod_n a n <= 1\nHnonneg  : forall i : nat, (i < n)%nat -> 0 <= a i\n|-prod_n a (S n) <= 1"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros n a Ha Hsum.",
    "induction n as [|n IH].",
    "- simpl.",
    "reflexivity.",
    "- simpl in Hsum |-.",
    "assert (Hnonneg : forall i : nat, (i < n)%nat -> 0 <= a i).",
    "{ intros i Hi.",
    "apply Ha.",
    "lia. }",
    "specialize (IH Hnonneg)."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level0__gpt-5.6-terra__seed0`. Unsolved; $0.41504680; 26 completions; 2.215 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 1, 'rewrite-no-match': 1, 'ring-failure': 1, 'subproof-incomplete': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "type-mismatch",
  "elapsed": 0.12099751178175211,
  "error": "(-32003, 'Coq: In environment\\nHaux :\\n  forall (k : nat) (x : R), 0 <= x -> x ^ k * (INR k + 1 - INR k * x) <= 1\\nHsum_nonneg :\\n  forall (m : nat) (f : nat -> R),\\n  (forall i : nat, (i < m)%nat -> 0 <= f i) -> 0 <= sum_n f m\\nHzero :\\n  forall (m : nat) (f : nat -> R),\\n  (forall i : nat, (i < m)%nat -> 0 <= f i) ->\\n  sum_n f m = 0 -> (m > 0)%nat -> prod_n f m = 0\\nHsum_div :\\n  forall (m : nat) (f : nat -> R) (d : R),\\n  sum_n (fun i : nat => f i / d) m = sum_n f m / d\\nm : nat\\nf : nat -> R\\nd : R\\nHd : d <> 0\\nIH : prod_n (fun i : nat => f i / d) m = prod_n f m / d ^ m\\nThe term \"Hd\" has type \"d <> 0\" while it is expected to have type\\n \"d ^ m <> 0 /\\\\ d <> 0\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "Haux  : forall (k : nat) (x : R), 0 <= x -> x ^ k * (INR k + 1 - INR k * x) <= 1\nHsum_nonneg  : forall (m0 : nat) (f0 : nat -> R),\n(forall i : nat, (i < m0)%nat -> 0 <= f0 i) -> 0 <= sum_n f0 m0\nHzero  : forall (m0 : nat) (f0 : nat -> R),\n(forall i : nat, (i < m0)%nat -> 0 <= f0 i) ->\nsum_n f0 m0 = 0 -> (m0 > 0)%nat -> prod_n f0 m0 = 0\nHsum_div  : forall (m0 : nat) (f0 : nat -> R) (d0 : R),\nsum_n (fun i : nat => f0 i / d0) m0 = sum_n f0 m0 / d0\nm  : nat\nf  : nat -> R\nd  : R\nHd  : d <> 0\nIH  : prod_n (fun i : nat => f i / d) m = prod_n f m / d ^ m\n|-d ^ m <> 0 /\\ d <> 0"
  ],
  "success": false,
  "tactic": "exact Hd.",
  "verified_prefix": [
    "assert (Haux : forall k : nat, forall x : R, 0 <= x -> x ^ k * (INR k + 1 - INR k * x) <= 1).",
    "{ intros k.",
    "induction k as [|k IH].",
    "- intros x Hx.",
    "simpl.",
    "lra.",
    "- intros x Hx.",
    "rewrite <- tech_pow_Rmult, S_INR.",
    "specialize (IH x Hx).",
    "assert (Hp : 0 <= x ^ k).",
    "{ apply pow_le. exact Hx. }",
    "assert (Hs : 0 <= (1 - x) * (1 - x)).",
    "{ apply Rle_0_sqr. }",
    "assert (Hk : 0 <= INR k + 1).",
    "{ apply Rplus_le_le_0_compat. apply pos_INR. lra. }",
    "assert (Hdiff : 0 <= x ^ k * (INR k + 1) * ((1 - x) * (1 - x))).",
    "{ apply Rmult_le_pos.",
    "- apply Rmult_le_pos; assumption.",
    "- exact Hs.",
    "}",
    "nra.",
    "}",
    "assert (Hsum_nonneg : forall (m : nat) (f : nat -> R), (forall i, (i < m)%nat -> 0 <= f i) -> 0 <= sum_n f m).",
    "{ intros m f Hf.",
    "induction m as [|m IH].",
    "- simpl.",
    "lra.",
    "- simpl.",
    "assert (Hm : 0 <= f m).",
    "{ apply Hf. lia. }",
    "assert (HI : 0 <= sum_n f m).",
    "{ apply IH.",
    "intros i Hi.",
    "apply Hf.",
    "lia.",
    "}",
    "lra.",
    "}",
    "assert (Hzero : forall (m : nat) (f : nat -> R), (forall i, (i < m)%nat -> 0 <= f i) -> sum_n f m = 0 -> (m > 0)%nat -> prod_n f m = 0).",
    "{ intros m f Hf Hs Hm.",
    "destruct m as [|m].",
    "- lia.",
    "- simpl in Hs |- *.",
    "assert (Hsn : 0 <= sum_n f m).",
    "{ apply Hsum_nonneg.",
    "intros i Hi.",
    "apply Hf.",
    "lia.",
    "}",
    "assert (Hfm : 0 <= f m).",
    "{ apply Hf. lia. }",
    "assert (Hfm0 : f m = 0) by lra.",
    "rewrite Hfm0.",
    "ring.",
    "}",
    "assert (Hsum_div : forall (m : nat) (f : nat -> R) (d : R), sum_n (fun i => f i / d) m = sum_n f m / d).",
    "{ intros m f d.",
    "induction m as [|m IH].",
    "- simpl.",
    "lra.",
    "- simpl.",
    "rewrite IH.",
    "unfold Rdiv.",
    "ring.",
    "}",
    "assert (Hprod_div : forall (m : nat) (f : nat -> R) (d : R), d <> 0 -> prod_n (fun i => f i / d) m = prod_n f m / d ^ m).",
    "{ intros m f d Hd.",
    "induction m as [|m IH].",
    "- simpl.",
    "field.",
    "- simpl.",
    "rewrite IH.",
    "field."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level1__gpt-5.6-luna__seed0`. Unsolved; $0.08822794; 64 completions; 4.155 verifier seconds.

Terminal: `stopped`; limiting dimensions: `[]`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'incomplete-proof': 7, 'no-applicable-tactic': 24, 'other': 1, 'type-mismatch': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The variable a was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 63,
  "category": "no-applicable-tactic",
  "elapsed": 0.005991348065435886,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < S n)%nat -> 0 <= a i\nHsum  : sum_n a n + a n = match n with\n                  | 0%nat => 1\n                  | S _ => INR n + 1\n                  end\nIH  : sum_n a n = INR n -> prod_n a n <= 1\nHnonneg  : forall i : nat, (i < n)%nat -> 0 <= a i\n|-prod_n a (S n) <= 1"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros n a Ha Hsum.",
    "induction n as [|n IH].",
    "- simpl.",
    "reflexivity.",
    "- simpl in Hsum |-.",
    "assert (Hnonneg : forall i : nat, (i < n)%nat -> 0 <= a i).",
    "{ intros i Hi.",
    "apply Ha.",
    "lia. }",
    "specialize (IH Hnonneg)."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level1__gpt-5.6-terra__seed0`. Solved; $0.83090580; 31 completions; 17.319 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 1, 'rewrite-no-match': 3, 'ring-failure': 1, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level2__gpt-5.6-luna__seed0`. Unsolved; $0.10936666; 83 completions; 5.180 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'incomplete-proof': 12, 'no-applicable-tactic': 29, 'other': 1, 'type-mismatch': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The variable a was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 83,
  "category": "no-applicable-tactic",
  "elapsed": 0.0057360948994755745,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\na  : nat -> R\nHa  : forall i : nat, (i < S n)%nat -> 0 <= a i\nHsum  : sum_n a n + a n = match n with\n                  | 0%nat => 1\n                  | S _ => INR n + 1\n                  end\nIH  : sum_n a n = INR n -> prod_n a n <= 1\nHnonneg  : forall i : nat, (i < n)%nat -> 0 <= a i\n|-prod_n a (S n) <= 1"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros n a Ha Hsum.",
    "induction n as [|n IH].",
    "- simpl.",
    "reflexivity.",
    "- simpl in Hsum |-.",
    "assert (Hnonneg : forall i : nat, (i < n)%nat -> 0 <= a i).",
    "{ intros i Hi.",
    "apply Ha.",
    "lia. }",
    "specialize (IH Hnonneg)."
  ]
}
```

### algebra_amgm_sum1toneqn_prod1tonleq1__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/algebra_amgm_sum1toneqn_prod1tonleq1__E-level1__gpt-5.6-terra__seed0`. Solved; $0.83090580; 31 completions; 17.319 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 1, 'rewrite-no-match': 3, 'ring-failure': 1, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq:  (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

### amc12a_2020_p13__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__A-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04022694; 16 completions; 17.851 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'syntax-error': 3, 'type-mismatch': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The variable Rlt_or_gt was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 15,
  "category": "no-applicable-tactic",
  "elapsed": 4.062037953175604,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHp1  : 0 < Rpower n (/ INR c)\nHp2  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp3  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHcoef  : 1 / INR a * (1 + 1 / INR b * (1 + 1 / INR c)) = 25 / 36\nHaR  : 2 <= INR a\nHbR  : 2 <= INR b\nHcR  : 2 <= INR c\nHa0  : 0 < INR a\nHb0  : 0 < INR b\nHc0  : 0 < INR c\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "assert (HbInv2 : 1 / INR b <= 1 / 2) by nra.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Habc Heq.",
    "destruct Habc as [Ha [Hb Hc]].",
    "assert (Hp1 : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp2 : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp3 : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hlog := f_equal ln Heq).",
    "rewrite ln_Rpower in Hlog.",
    "rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hp2) in Hlog.",
    "rewrite ln_Rpower in Hlog.",
    "rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hp1) in Hlog.",
    "rewrite ln_Rpower in Hlog.",
    "rewrite ln_Rpower in Hlog.",
    "assert (Hcoef : (1 / INR a) * (1 + (1 / INR b) * (1 + 1 / INR c)) = 25 / 36).",
    "{ assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "apply (Rmult_eq_reg_r (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (HaR : 2 <= INR a).",
    "{ assert (Ha' : (2 <= a)%nat) by lia.",
    "pose proof (le_INR 2 a Ha') as H.",
    "exact H.",
    "}",
    "assert (HbR : 2 <= INR b).",
    "{ assert (Hb' : (2 <= b)%nat) by lia.",
    "pose proof (le_INR 2 b Hb') as H.",
    "exact H.",
    "}",
    "assert (HcR : 2 <= INR c).",
    "{ assert (Hc' : (2 <= c)%nat) by lia.",
    "pose proof (le_INR 2 c Hc') as H.",
    "exact H.",
    "}",
    "assert (Ha0 : 0 < INR a).",
    "{ assert (Ha0' : (0 < a)%nat) by lia.",
    "pose proof (lt_INR 0 a Ha0') as H.",
    "exact H.",
    "}",
    "assert (Hb0 : 0 < INR b).",
    "{ assert (Hb0' : (0 < b)%nat) by lia.",
    "pose proof (lt_INR 0 b Hb0') as H.",
    "exact H.",
    "}",
    "assert (Hc0 : 0 < INR c).",
    "{ assert (Hc0' : (0 < c)%nat) by lia.",
    "pose proof (lt_INR 0 c Hc0') as H.",
    "exact H.",
    "}"
  ]
}
```

### amc12a_2020_p13__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__A-level0__gpt-5.6-terra__seed0`. Unsolved; $0.34747160; 21 completions; 17.906 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'rewrite-no-match': 2, 'subproof-incomplete': 1, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "ln (?M1865 * ?M1866)" in Heq.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 12,
  "category": "no-applicable-tactic",
  "elapsed": 4.096459490247071,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHpa  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)\nHpb  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHpc  : 0 < Rpower n (/ INR c)\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHcoef  : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHa0  : INR a <> 0\nHb0  : INR b <> 0\nHc0  : INR c <> 0\nHia  : INR a * / INR a = 1\nHib  : INR b * / INR b = 1\nHic  : INR c * / INR c = 1\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "assert (Hreal : 36 * (INR b * INR c + INR c + 1) = 25 * INR a * INR b * INR c) by nra.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 [Ha [Hb Hc]] Heq.",
    "assert (Hpa : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hpb : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hpc : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hlog : (/ INR a) * (ln n + (/ INR b) * (ln n + (/ INR c) * ln n)) = (25 / 36) * ln n).",
    "{ apply (f_equal ln) in Heq.",
    "repeat rewrite ln_Rpower in Heq.",
    "rewrite ln_mult in Heq by assumption.",
    "rewrite ln_Rpower in Heq.",
    "rewrite ln_mult in Heq by assumption.",
    "rewrite ln_Rpower in Heq.",
    "exact Heq. }",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hcoef : (/ INR a) * (1 + (/ INR b) * (1 + (/ INR c))) = 25 / 36).",
    "{ apply (Rmult_eq_reg_r (ln n)).",
    "- nra.",
    "- exact Hln. }",
    "assert (Ha0 : INR a <> 0) by (apply not_0_INR; lia).",
    "assert (Hb0 : INR b <> 0) by (apply not_0_INR; lia).",
    "assert (Hc0 : INR c <> 0) by (apply not_0_INR; lia).",
    "assert (Hia : INR a * / INR a = 1) by (apply Rinv_r; exact Ha0).",
    "assert (Hib : INR b * / INR b = 1) by (apply Rinv_r; exact Hb0).",
    "assert (Hic : INR c * / INR c = 1) by (apply Rinv_r; exact Hc0)."
  ]
}
```

### amc12a_2020_p13__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__B-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03892346; 19 completions; 26.037 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'syntax-error': 1, 'type-mismatch': 2, 'unify-failure': 1, 'unknown-reference': 3}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHpow :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR a".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "syntax-error",
  "elapsed": 4.033245485275984,
  "error": "(-32003, \"Coq: Syntax error: [constr] or ']' expected (in [simple_tactic]).\")",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHaR  : 0 < INR a\nHbR  : 0 < INR b\nHcR  : 0 < INR c\nHa0  : INR a <> 0\nHb0  : INR b <> 0\nHc0  : INR c <> 0\nHbc  : 0 < n * Rpower n (/ INR c)\nHrp  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHabc  : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHcpos  : 0 < Rpower n (/ INR c)\nHln  : ln n <> 0\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "field_simplify [Ha0, Hb0, Hc0] in Hlog.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (HaR : 0 < INR a) by (apply lt_0_INR; lia).",
    "assert (HbR : 0 < INR b) by (apply lt_0_INR; lia).",
    "assert (HcR : 0 < INR c) by (apply lt_0_INR; lia).",
    "assert (Ha0 : INR a <> 0) by lra.",
    "assert (Hb0 : INR b <> 0) by lra.",
    "assert (Hc0 : INR c <> 0) by lra.",
    "assert (Hbc : 0 < n * Rpower n (/ INR c)).",
    "{ unfold Rpower.",
    "apply Rmult_lt_0_compat.",
    "exact Hn.",
    "apply exp_pos.",
    "}",
    "assert (Hrp : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower.",
    "apply exp_pos.",
    "}",
    "assert (Habc : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ apply Rmult_lt_0_compat.",
    "exact Hn.",
    "exact Hrp.",
    "}",
    "assert (Hcpos : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower.",
    "apply exp_pos.",
    "}",
    "assert (Hln : ln n <> 0).",
    "{ intro Hz.",
    "apply Hn1.",
    "pose proof (exp_ln n Hn) as He.",
    "rewrite Hz in He.",
    "rewrite exp_0 in He.",
    "symmetry.",
    "exact He.",
    "}",
    "assert (Hlog := f_equal ln Hpow).",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hrp) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hcpos) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog."
  ]
}
```

### amc12a_2020_p13__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__B-level0__gpt-5.6-terra__seed0`. Unsolved; $0.25665220; 33 completions; 0.728 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-proof-submission`; added goal views: 0. Error counts: `{}`.

### amc12a_2020_p13__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__C-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03841066; 17 completions; 38.317 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'syntax-error': 3, 'type-mismatch': 2, 'unify-failure': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHneq : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR c".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 17,
  "category": "unknown-reference",
  "elapsed": 8.390969378873706,
  "error": "(-32003, 'Coq: The reference by_contra was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHaN  : INR a <> 0\nHbN  : INR b <> 0\nHcN  : INR c <> 0\nHcoef  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\n|-a = 2%nat",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHaN  : INR a <> 0\nHbN  : INR b <> 0\nHcN  : INR c <> 0\nHcoef  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\nHa2  : a = 2%nat\n|-b = 3%nat",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHaN  : INR a <> 0\nHbN  : INR b <> 0\nHcN  : INR c <> 0\n|-INR a <> 0 /\\ INR b <> 0 /\\ INR c <> 0",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHaN  : INR a <> 0\nHbN  : INR b <> 0\nHcN  : INR c <> 0\n|-INR c <> 0 /\\ INR b <> 0 /\\ INR a <> 0"
  ],
  "success": false,
  "tactic": "{ by_contra Hna.",
  "verified_prefix": [
    "intros a b c n Hn Hneq Habc Heq.",
    "destruct Habc as [Ha [Hb Hc]].",
    "assert (Hc0 : 0 < INR c) by (apply lt_0_INR; lia).",
    "assert (Hb0 : 0 < INR b) by (apply lt_0_INR; lia).",
    "assert (Ha0 : 0 < INR a) by (apply lt_0_INR; lia).",
    "assert (Hn1 : n = Rpower n 1) by (symmetry; apply Rpower_1; exact Hn).",
    "assert (Hinner : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)).",
    "{ rewrite Hn1 at 1.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hmiddle : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) = Rpower n (1 + (1 + / INR c) / INR b)).",
    "{ rewrite Hinner.",
    "rewrite Hn1 at 1.",
    "rewrite Rpower_mult.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hnormal : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) = Rpower n ((1 + (1 + / INR c) / INR b) / INR a)).",
    "{ rewrite Hmiddle.",
    "rewrite Rpower_mult.",
    "reflexivity.",
    "}",
    "rewrite Hnormal in Heq.",
    "assert (Hlog := f_equal ln Heq).",
    "rewrite !ln_Rpower in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hcoef : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36).",
    "{ apply (Rmult_eq_reg_l (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (HaN : INR a <> 0) by lra.",
    "assert (HbN : INR b <> 0) by lra.",
    "assert (HcN : INR c <> 0) by lra.",
    "field_simplify in Hcoef.",
    "field_simplify in Hcoef.",
    "assert (Ha2 : a = 2%nat)."
  ]
}
```

### amc12a_2020_p13__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__C-level0__gpt-5.6-terra__seed0`. Unsolved; $0.28097020; 29 completions; 1.341 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-proof-submission`; added goal views: 0. Error counts: `{}`.

### amc12a_2020_p13__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12a_2020_p13__C-level1__gpt-5.6-luna__seed0`. Unsolved; $0.12268652; 29 completions; 85.299 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'syntax-error': 6, 'type-mismatch': 3, 'unify-failure': 2, 'unknown-reference': 5}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHneq : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR c".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "syntax-error",
  "elapsed": 8.280742452479899,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHcoef  : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36\nHa2  : a <> 2%nat\nHa3  : (3 <= a)%nat\n|-INR 3 <= INR a",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHcoef  : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36\nHa2  : a <> 2%nat\nHa3  : (3 <= a)%nat\nHa3R  : INR 3 <= INR a\n|-False"
  ],
  "success": false,
  "tactic": "{ change INR 3 <= INR a.",
  "verified_prefix": [
    "intros a b c n Hn Hneq Habc Heq.",
    "destruct Habc as [Ha [Hb Hc]].",
    "assert (Hc0 : 0 < INR c) by (apply lt_0_INR; lia).",
    "assert (Hb0 : 0 < INR b) by (apply lt_0_INR; lia).",
    "assert (Ha0 : 0 < INR a) by (apply lt_0_INR; lia).",
    "assert (Hn1 : n = Rpower n 1) by (symmetry; apply Rpower_1; exact Hn).",
    "assert (Hinner : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)).",
    "{ rewrite Hn1 at 1.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hmiddle : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) = Rpower n (1 + (1 + / INR c) / INR b)).",
    "{ rewrite Hinner.",
    "rewrite Hn1 at 1.",
    "rewrite Rpower_mult.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hnormal : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) = Rpower n ((1 + (1 + / INR c) / INR b) / INR a)).",
    "{ rewrite Hmiddle.",
    "rewrite Rpower_mult.",
    "reflexivity.",
    "}",
    "rewrite Hnormal in Heq.",
    "assert (Hlog := f_equal ln Heq).",
    "rewrite !ln_Rpower in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hcoef : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36).",
    "{ apply (Rmult_eq_reg_l (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (Ha2 : a = 2%nat).",
    "{ destruct (Nat.eq_dec a 2) as [Ha2|Ha2].",
    "- exact Ha2.",
    "- exfalso.",
    "assert (Ha3 : (3 <= a)%nat) by lia.",
    "assert (Ha3R : INR 3 <= INR a)."
  ]
}
```

### amc12a_2020_p13__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12a_2020_p13__C-level1__gpt-5.6-terra__seed0`. Unsolved; $1.20125500; 45 completions; 8.545 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 5, 'type-mismatch': 1, 'unify-failure': 3, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 45,
  "category": "no-applicable-tactic",
  "elapsed": 0.665463250130415,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower n ((1 + (1 + / INR c) * / INR b) * / INR a) = Rpower n (25 / 36)\nHia  : INR a <> 0\nHib  : INR b <> 0\nHic  : INR c <> 0\nHrn  : Rpower n 1 = n\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHouter  : n * Rpower n ((1 + / INR c) * / INR b) =\nRpower n (1 + (1 + / INR c) * / INR b)\nHlog  : (1 + (1 + / INR c) * / INR b) * / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHex  : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36\nHsimp  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\nHmul  : 36 * INR c * INR b + 36 * INR c + 36 = 25 * INR c * INR b * INR a\nHaR2  : (2 : R) <= INR a\nHbR2  : (2 : R) <= INR b\nHcR2  : (2 : R) <= INR c\nHc0  : 0 <= INR c\nHb0  : 0 <= INR b\nHcb0  : 0 <= INR c * INR b\n|-0 <= INR c * (INR b - INR 2)",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower n ((1 + (1 + / INR c) * / INR b) * / INR a) = Rpower n (25 / 36)\nHia  : INR a <> 0\nHib  : INR b <> 0\nHic  : INR c <> 0\nHrn  : Rpower n 1 = n\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHouter  : n * Rpower n ((1 + / INR c) * / INR b) =\nRpower n (1 + (1 + / INR c) * / INR b)\nHlog  : (1 + (1 + / INR c) * / INR b) * / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHex  : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36\nHsimp  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\nHmul  : 36 * INR c * INR b + 36 * INR c + 36 = 25 * INR c * INR b * INR a\nHaR2  : (2 : R) <= INR a\nHbR2  : (2 : R) <= INR b\nHcR2  : (2 : R) <= INR c\nHc0  : 0 <= INR c\nHb0  : 0 <= INR b\nHcb0  : 0 <= INR c * INR b\nHbcC0  : 0 <= INR c * (INR b - INR 2)\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "{ apply Rmult_le_pos; lra. }",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (Hia : INR a <> 0) by (apply not_0_INR; lia).",
    "assert (Hib : INR b <> 0) by (apply not_0_INR; lia).",
    "assert (Hic : INR c <> 0) by (apply not_0_INR; lia).",
    "assert (Hrn : Rpower n 1 = n) by (apply Rpower_1; exact Hn).",
    "assert (Hinner : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)).",
    "{ rewrite (Rpower_plus 1 (/ INR c) n).",
    "rewrite Hrn.",
    "reflexivity. }",
    "rewrite Hinner in Hpow.",
    "rewrite Rpower_mult in Hpow.",
    "assert (Houter : n * Rpower n ((1 + / INR c) * / INR b) = Rpower n (1 + (1 + / INR c) * / INR b)).",
    "{ rewrite (Rpower_plus 1 ((1 + / INR c) * / INR b) n).",
    "rewrite Hrn.",
    "reflexivity. }",
    "rewrite Houter in Hpow.",
    "rewrite Rpower_mult in Hpow.",
    "assert (Hlog := f_equal ln Hpow).",
    "repeat rewrite ln_Rpower in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hex : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36).",
    "{ apply (Rmult_eq_reg_r (ln n)); [exact Hlog | exact Hln]. }",
    "assert (Hsimp : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36).",
    "{ field_simplify in Hex; try exact Hex; repeat split; assumption. }",
    "assert (Hmul := f_equal (fun x : R => x * (36 * (INR c * INR b * INR a))) Hsimp).",
    "field_simplify in Hmul; try (repeat split; assumption).",
    "assert (HaR2 : (2 : R) <= INR a).",
    "{ change (INR 2 <= INR a).",
    "apply le_INR.",
    "lia. }",
    "assert (HbR2 : (2 : R) <= INR b).",
    "{ change (INR 2 <= INR b).",
    "apply le_INR.",
    "lia. }",
    "assert (HcR2 : (2 : R) <= INR c).",
    "{ change (INR 2 <= INR c).",
    "apply le_INR.",
    "lia. }",
    "assert (Hc0 : 0 <= INR c) by lra.",
    "assert (Hb0 : 0 <= INR b) by lra.",
    "assert (Hcb0 : 0 <= INR c * INR b).",
    "{ apply Rmult_le_pos; assumption. }",
    "assert (HbcC0 : 0 <= INR c * (INR b - INR 2))."
  ]
}
```

### amc12a_2020_p13__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/amc12a_2020_p13__C-level2__gpt-5.6-luna__seed0`. Unsolved; $0.12268652; 29 completions; 85.299 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'syntax-error': 6, 'type-mismatch': 3, 'unify-failure': 2, 'unknown-reference': 5}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHneq : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR c".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "syntax-error",
  "elapsed": 8.280742452479899,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHcoef  : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36\nHa2  : a <> 2%nat\nHa3  : (3 <= a)%nat\n|-INR 3 <= INR a",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower n ((1 + (1 + / INR c) / INR b) / INR a) = Rpower n (25 / 36)\nHc0  : 0 < INR c\nHb0  : 0 < INR b\nHa0  : 0 < INR a\nHn1  : n = Rpower n 1\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHmiddle  : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) =\nRpower n (1 + (1 + / INR c) / INR b)\nHnormal  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n ((1 + (1 + / INR c) / INR b) / INR a)\nHlog  : (1 + (1 + / INR c) / INR b) / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHcoef  : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36\nHa2  : a <> 2%nat\nHa3  : (3 <= a)%nat\nHa3R  : INR 3 <= INR a\n|-False"
  ],
  "success": false,
  "tactic": "{ change INR 3 <= INR a.",
  "verified_prefix": [
    "intros a b c n Hn Hneq Habc Heq.",
    "destruct Habc as [Ha [Hb Hc]].",
    "assert (Hc0 : 0 < INR c) by (apply lt_0_INR; lia).",
    "assert (Hb0 : 0 < INR b) by (apply lt_0_INR; lia).",
    "assert (Ha0 : 0 < INR a) by (apply lt_0_INR; lia).",
    "assert (Hn1 : n = Rpower n 1) by (symmetry; apply Rpower_1; exact Hn).",
    "assert (Hinner : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)).",
    "{ rewrite Hn1 at 1.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hmiddle : n * Rpower (n * Rpower n (/ INR c)) (/ INR b) = Rpower n (1 + (1 + / INR c) / INR b)).",
    "{ rewrite Hinner.",
    "rewrite Hn1 at 1.",
    "rewrite Rpower_mult.",
    "rewrite <- Rpower_plus.",
    "reflexivity.",
    "}",
    "assert (Hnormal : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) = Rpower n ((1 + (1 + / INR c) / INR b) / INR a)).",
    "{ rewrite Hmiddle.",
    "rewrite Rpower_mult.",
    "reflexivity.",
    "}",
    "rewrite Hnormal in Heq.",
    "assert (Hlog := f_equal ln Heq).",
    "rewrite !ln_Rpower in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hcoef : (1 + (1 + / INR c) / INR b) / INR a = 25 / 36).",
    "{ apply (Rmult_eq_reg_l (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (Ha2 : a = 2%nat).",
    "{ destruct (Nat.eq_dec a 2) as [Ha2|Ha2].",
    "- exact Ha2.",
    "- exfalso.",
    "assert (Ha3 : (3 <= a)%nat) by lia.",
    "assert (Ha3R : INR 3 <= INR a)."
  ]
}
```

### amc12a_2020_p13__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/amc12a_2020_p13__C-level2__gpt-5.6-terra__seed0`. Unsolved; $1.20125500; 45 completions; 8.545 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 5, 'type-mismatch': 1, 'unify-failure': 3, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 45,
  "category": "no-applicable-tactic",
  "elapsed": 0.665463250130415,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower n ((1 + (1 + / INR c) * / INR b) * / INR a) = Rpower n (25 / 36)\nHia  : INR a <> 0\nHib  : INR b <> 0\nHic  : INR c <> 0\nHrn  : Rpower n 1 = n\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHouter  : n * Rpower n ((1 + / INR c) * / INR b) =\nRpower n (1 + (1 + / INR c) * / INR b)\nHlog  : (1 + (1 + / INR c) * / INR b) * / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHex  : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36\nHsimp  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\nHmul  : 36 * INR c * INR b + 36 * INR c + 36 = 25 * INR c * INR b * INR a\nHaR2  : (2 : R) <= INR a\nHbR2  : (2 : R) <= INR b\nHcR2  : (2 : R) <= INR c\nHc0  : 0 <= INR c\nHb0  : 0 <= INR b\nHcb0  : 0 <= INR c * INR b\n|-0 <= INR c * (INR b - INR 2)",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower n ((1 + (1 + / INR c) * / INR b) * / INR a) = Rpower n (25 / 36)\nHia  : INR a <> 0\nHib  : INR b <> 0\nHic  : INR c <> 0\nHrn  : Rpower n 1 = n\nHinner  : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)\nHouter  : n * Rpower n ((1 + / INR c) * / INR b) =\nRpower n (1 + (1 + / INR c) * / INR b)\nHlog  : (1 + (1 + / INR c) * / INR b) * / INR a * ln n = 25 / 36 * ln n\nHln  : ln n <> 0\nHex  : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36\nHsimp  : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36\nHmul  : 36 * INR c * INR b + 36 * INR c + 36 = 25 * INR c * INR b * INR a\nHaR2  : (2 : R) <= INR a\nHbR2  : (2 : R) <= INR b\nHcR2  : (2 : R) <= INR c\nHc0  : 0 <= INR c\nHb0  : 0 <= INR b\nHcb0  : 0 <= INR c * INR b\nHbcC0  : 0 <= INR c * (INR b - INR 2)\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "{ apply Rmult_le_pos; lra. }",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (Hia : INR a <> 0) by (apply not_0_INR; lia).",
    "assert (Hib : INR b <> 0) by (apply not_0_INR; lia).",
    "assert (Hic : INR c <> 0) by (apply not_0_INR; lia).",
    "assert (Hrn : Rpower n 1 = n) by (apply Rpower_1; exact Hn).",
    "assert (Hinner : n * Rpower n (/ INR c) = Rpower n (1 + / INR c)).",
    "{ rewrite (Rpower_plus 1 (/ INR c) n).",
    "rewrite Hrn.",
    "reflexivity. }",
    "rewrite Hinner in Hpow.",
    "rewrite Rpower_mult in Hpow.",
    "assert (Houter : n * Rpower n ((1 + / INR c) * / INR b) = Rpower n (1 + (1 + / INR c) * / INR b)).",
    "{ rewrite (Rpower_plus 1 ((1 + / INR c) * / INR b) n).",
    "rewrite Hrn.",
    "reflexivity. }",
    "rewrite Houter in Hpow.",
    "rewrite Rpower_mult in Hpow.",
    "assert (Hlog := f_equal ln Hpow).",
    "repeat rewrite ln_Rpower in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hex : (1 + (1 + / INR c) * / INR b) * / INR a = 25 / 36).",
    "{ apply (Rmult_eq_reg_r (ln n)); [exact Hlog | exact Hln]. }",
    "assert (Hsimp : (INR c * INR b + INR c + 1) / (INR c * INR b * INR a) = 25 / 36).",
    "{ field_simplify in Hex; try exact Hex; repeat split; assumption. }",
    "assert (Hmul := f_equal (fun x : R => x * (36 * (INR c * INR b * INR a))) Hsimp).",
    "field_simplify in Hmul; try (repeat split; assumption).",
    "assert (HaR2 : (2 : R) <= INR a).",
    "{ change (INR 2 <= INR a).",
    "apply le_INR.",
    "lia. }",
    "assert (HbR2 : (2 : R) <= INR b).",
    "{ change (INR 2 <= INR b).",
    "apply le_INR.",
    "lia. }",
    "assert (HcR2 : (2 : R) <= INR c).",
    "{ change (INR 2 <= INR c).",
    "apply le_INR.",
    "lia. }",
    "assert (Hc0 : 0 <= INR c) by lra.",
    "assert (Hb0 : 0 <= INR b) by lra.",
    "assert (Hcb0 : 0 <= INR c * INR b).",
    "{ apply Rmult_le_pos; assumption. }",
    "assert (HbcC0 : 0 <= INR c * (INR b - INR 2))."
  ]
}
```

### amc12a_2020_p13__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__D-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04058838; 18 completions; 42.330 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unify-failure`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'type-mismatch': 1, 'unify-failure': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference positivity was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "unify-failure",
  "elapsed": 8.098601250909269,
  "error": "(-32003, 'Coq: In environment\\na, b, c : nat\\nn : R\\nHn : 0 < n\\nHn1 : n <> 1\\nHa : (1 < a)%nat\\nHb : (1 < b)%nat\\nHc : (1 < c)%nat\\nHpow :\\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\\n  Rpower n (25 / 36)\\nHapos : 0 < INR a\\nHbpos : 0 < INR b\\nHcpos : 0 < INR c\\nHra : 0 < / INR a\\nHrb : 0 < / INR b\\nHrc : 0 < / INR c\\nHrn : 0 < Rpower n (/ INR c)\\nHinner : 0 < n * Rpower n (/ INR c)\\nHrin : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\\nHprod : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\\nHlog : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\\nHln : ln n <> 0\\nHfrac : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\\nHa1 : 1 < INR a\\nHb1 : 1 < INR b\\nHc1 : 1 < INR c\\nHa2nat : (2 <= a)%nat\\nHb2nat : (2 <= b)%nat\\nHc2nat : (2 <= c)%nat\\nUnable to unify \"INR ?M1902 < INR ?M1903 \\\\/ INR ?M1902 = INR ?M1903\" with\\n \"2 < INR a \\\\/ 2 = INR a\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHapos  : 0 < INR a\nHbpos  : 0 < INR b\nHcpos  : 0 < INR c\nHra  : 0 < / INR a\nHrb  : 0 < / INR b\nHrc  : 0 < / INR c\nHrn  : 0 < Rpower n (/ INR c)\nHinner  : 0 < n * Rpower n (/ INR c)\nHrin  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHprod  : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHfrac  : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHa1  : 1 < INR a\nHb1  : 1 < INR b\nHc1  : 1 < INR c\nHa2nat  : (2 <= a)%nat\nHb2nat  : (2 <= b)%nat\nHc2nat  : (2 <= c)%nat\n|-2 <= INR a",
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHapos  : 0 < INR a\nHbpos  : 0 < INR b\nHcpos  : 0 < INR c\nHra  : 0 < / INR a\nHrb  : 0 < / INR b\nHrc  : 0 < / INR c\nHrn  : 0 < Rpower n (/ INR c)\nHinner  : 0 < n * Rpower n (/ INR c)\nHrin  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHprod  : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHfrac  : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHa1  : 1 < INR a\nHb1  : 1 < INR b\nHc1  : 1 < INR c\nHa2nat  : (2 <= a)%nat\nHb2nat  : (2 <= b)%nat\nHc2nat  : (2 <= c)%nat\nHa2  : 2 <= INR a\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "{ apply le_INR. exact Ha2nat. }",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (Hapos : 0 < INR a).",
    "{ apply lt_0_INR. lia. }",
    "assert (Hbpos : 0 < INR b).",
    "{ apply lt_0_INR. lia. }",
    "assert (Hcpos : 0 < INR c).",
    "{ apply lt_0_INR. lia. }",
    "assert (Hra : 0 < / INR a) by (apply Rinv_pos; exact Hapos).",
    "assert (Hrb : 0 < / INR b) by (apply Rinv_pos; exact Hbpos).",
    "assert (Hrc : 0 < / INR c) by (apply Rinv_pos; exact Hcpos).",
    "assert (Hrn : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hinner : 0 < n * Rpower n (/ INR c)).",
    "{ apply Rmult_lt_0_compat; assumption. }",
    "assert (Hrin : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hprod : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ apply Rmult_lt_0_compat; assumption. }",
    "pose proof (f_equal ln Hpow) as Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_mult _ _ Hn Hrin) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "rewrite (ln_mult _ _ Hn Hrn) in Hlog.",
    "rewrite (ln_Rpower _ _) in Hlog.",
    "assert (Hln : ln n <> 0).",
    "{ apply ln_neq_0; assumption. }",
    "assert (Hfrac : (/ INR a) * (1 + (/ INR b) * (1 + / INR c)) = 25 / 36).",
    "{ nra. }",
    "assert (Ha1 : 1 < INR a) by (apply lt_1_INR; exact Ha).",
    "assert (Hb1 : 1 < INR b) by (apply lt_1_INR; exact Hb).",
    "assert (Hc1 : 1 < INR c) by (apply lt_1_INR; exact Hc).",
    "assert (Ha2nat : (2 <= a)%nat) by lia.",
    "assert (Hb2nat : (2 <= b)%nat) by lia.",
    "assert (Hc2nat : (2 <= c)%nat) by lia.",
    "assert (Ha2 : 2 <= INR a)."
  ]
}
```

### amc12a_2020_p13__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__D-level0__gpt-5.6-terra__seed0`. Unsolved; $0.36304180; 24 completions; 75.172 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'prover-crash': 1, 'subproof-incomplete': 1, 'type-mismatch': 2}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "type-mismatch",
  "elapsed": 9.033590788021684,
  "error": "(-32003, 'Coq: In environment\\na, b, c : nat\\nn : R\\nHa : (1 < a)%nat\\nHb : (1 < b)%nat\\nHc : (1 < c)%nat\\nHnat : (36 * (b * c + c + 1))%nat = (25 * a * b * c)%nat\\nThe term \"2\" has type \"R\" while it is expected to have type \"nat\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHnat  : (36 * (b * c + c + 1))%nat = (25 * a * b * c)%nat\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "assert (Ha2 : a = 2).",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (Hpa : 0 < INR a) by (apply lt_0_INR; lia).",
    "assert (Hpb : 0 < INR b) by (apply lt_0_INR; lia).",
    "assert (Hpc : 0 < INR c) by (apply lt_0_INR; lia).",
    "assert (Hpnc : 0 < Rpower n (/ INR c)) by (unfold Rpower; apply exp_pos).",
    "assert (Hpnb : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)) by (unfold Rpower; apply exp_pos).",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "apply (f_equal ln) in Hpow.",
    "rewrite (ln_Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)) in Hpow.",
    "rewrite (ln_Rpower n (25 / 36)) in Hpow.",
    "rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hpnb) in Hpow.",
    "rewrite (ln_Rpower (n * Rpower n (/ INR c)) (/ INR b)) in Hpow.",
    "rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hpnc) in Hpow.",
    "rewrite (ln_Rpower n (/ INR c)) in Hpow.",
    "assert (Hex : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36) by nra.",
    "assert (Hia : / INR a * INR a = 1) by (apply Rinv_l; lra).",
    "assert (Hib : / INR b * INR b = 1) by (apply Rinv_l; lra).",
    "assert (Hic : / INR c * INR c = 1) by (apply Rinv_l; lra).",
    "assert (Hmul : (/ INR a * (1 + / INR b * (1 + / INR c))) * (36 * INR a * INR b * INR c) = (25 / 36) * (36 * INR a * INR b * INR c)).",
    "{ rewrite Hex. ring. }",
    "assert (Hleft : (/ INR a * (1 + / INR b * (1 + / INR c))) * (36 * INR a * INR b * INR c) = 36 * (INR b * INR c + INR c + 1)).",
    "{ replace ((/ INR a * (1 + / INR b * (1 + / INR c))) * (36 * INR a * INR b * INR c)) with (36 * ((/ INR a * INR a) * INR b * INR c + (/ INR a * INR a) * (/ INR b * INR b) * INR c + (/ INR a * INR a) * (/ INR b * INR b) * (/ INR c * INR c))) by ring.",
    "rewrite Hia, Hib, Hic.",
    "ring. }",
    "assert (Heq : 36 * (INR b * INR c + INR c + 1) = 25 * INR a * INR b * INR c) by nra.",
    "assert (Hnat : (36 * (b * c + c + 1) = 25 * a * b * c)%nat).",
    "{ apply INR_eq.",
    "repeat rewrite plus_INR || rewrite mult_INR.",
    "simpl.",
    "lra. }",
    "clear Hpow Hn Hn1 Hpa Hpb Hpc Hpnc Hpnb Hln Hex Hia Hib Hic Hmul Hleft Heq."
  ]
}
```

### amc12a_2020_p13__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__E-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03660462; 20 completions; 33.972 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'rewrite-no-match': 1, 'syntax-error': 2, 'unify-failure': 3}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHpow :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR a".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "syntax-error",
  "elapsed": 4.029687240719795,
  "error": "(-32003, \"Coq: Syntax error: [constr] or ']' expected (in [simple_tactic]).\")",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nH0a  : (0 < a)%nat\nH0b  : (0 < b)%nat\nH0c  : (0 < c)%nat\nHia  : 0 < INR a\nHib  : 0 < INR b\nHic  : 0 < INR c\nHp_c  : 0 < Rpower n (/ INR c)\nHp_b  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp_a  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)\nHlc  : ln (n * Rpower n (/ INR c)) = ln n + / INR c * ln n\nHlb  : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) =\nln n + / INR b * (ln n + / INR c * ln n)\nHlog  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "field_simplify [ne_of_gt Hia, ne_of_gt Hib, ne_of_gt Hic] in Hlog.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (H0a : (0 < a)%nat) by lia.",
    "assert (H0b : (0 < b)%nat) by lia.",
    "assert (H0c : (0 < c)%nat) by lia.",
    "assert (Hia : 0 < INR a) by (apply lt_0_INR; exact H0a).",
    "assert (Hib : 0 < INR b) by (apply lt_0_INR; exact H0b).",
    "assert (Hic : 0 < INR c) by (apply lt_0_INR; exact H0c).",
    "assert (Hp_c : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_b : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_a : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hlc : ln (n * Rpower n (/ INR c)) = ln n + (/ INR c) * ln n).",
    "{ rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hp_c).",
    "rewrite (ln_Rpower n (/ INR c)).",
    "reflexivity.",
    "}",
    "assert (Hlb : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) = ln n + (/ INR b) * (ln n + (/ INR c) * ln n)).",
    "{ rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hp_b).",
    "rewrite (ln_Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "rewrite Hlc.",
    "reflexivity.",
    "}",
    "assert (Hlog := f_equal ln Hpow).",
    "rewrite !ln_Rpower in Hlog.",
    "rewrite Hlb in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption)."
  ]
}
```

### amc12a_2020_p13__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12a_2020_p13__E-level0__gpt-5.6-terra__seed0`. Unsolved; $0.36775860; 30 completions; 13.694 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unify-failure`; added goal views: 0. Error counts: `{'subproof-incomplete': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference positivity was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 27,
  "category": "unify-failure",
  "elapsed": 0.009591483511030674,
  "error": "(-32003, 'Coq: In environment\\na, b, c : nat\\nn : R\\nHn : 0 < n\\nHneq : n <> 1\\nHa : (1 < a)%nat\\nHb : (1 < b)%nat\\nHc : (1 < c)%nat\\nHeq :\\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\\n  Rpower n (25 / 36)\\nHia : INR a <> 0\\nHib : INR b <> 0\\nHic : INR c <> 0\\nHp1 : 0 < Rpower n (/ INR c)\\nHp2 : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\\nHprod : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\\nHln : ln n <> 0\\nL : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\\nE : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\\nUnable to unify \"?M1899 * / ?M1899 = 1\" with \"/ INR a * INR a = 1\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nn  : R\nHn  : 0 < n\nHneq  : n <> 1\nHa  : (1 < a)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nHeq  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\nRpower n (25 / 36)\nHia  : INR a <> 0\nHib  : INR b <> 0\nHic  : INR c <> 0\nHp1  : 0 < Rpower n (/ INR c)\nHp2  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHprod  : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHln  : ln n <> 0\nL  : / INR a * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nE  : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36\n|-b = 3%nat"
  ],
  "success": false,
  "tactic": "assert (Ia : / INR a * INR a = 1) by (apply Rinv_r; exact Hia).",
  "verified_prefix": [
    "intros a b c n Hn Hneq [Ha [Hb Hc]] Heq.",
    "assert (Hia : INR a <> 0) by (apply not_0_INR; lia).",
    "assert (Hib : INR b <> 0) by (apply not_0_INR; lia).",
    "assert (Hic : INR c <> 0) by (apply not_0_INR; lia).",
    "assert (Hp1 : 0 < Rpower n (/ INR c)) by (unfold Rpower; apply exp_pos).",
    "assert (Hp2 : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)) by (unfold Rpower; apply exp_pos).",
    "assert (Hprod : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) by nra.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "pose proof (f_equal ln Heq) as L.",
    "repeat rewrite ln_Rpower in L.",
    "rewrite (ln_mult n _ Hn Hp2) in L.",
    "rewrite ln_Rpower in L.",
    "rewrite (ln_mult n _ Hn Hp1) in L.",
    "rewrite ln_Rpower in L.",
    "assert (E : (/ INR a) * (1 + (/ INR b) * (1 + / INR c)) = 25 / 36) by nra."
  ]
}
```

### amc12a_2020_p13__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12a_2020_p13__E-level1__gpt-5.6-luna__seed0`. Unsolved; $0.12662500; 36 completions; 61.402 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 5, 'rewrite-no-match': 1, 'ring-failure': 1, 'syntax-error': 4, 'unify-failure': 3, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHpow :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR a".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 35,
  "category": "no-applicable-tactic",
  "elapsed": 0.19146629516035318,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < 2)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nH0a  : (0 < 2)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2) =\nRpower n (25 / 36)\nH0b  : (0 < b)%nat\nH0c  : (0 < c)%nat\nHia  : 0 < INR 2\nHib  : 0 < INR b\nHic  : 0 < INR c\nHp_c  : 0 < Rpower n (/ INR c)\nHp_b  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp_a  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2)\nHlc  : ln (n * Rpower n (/ INR c)) = ln n + / INR c * ln n\nHlb  : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) =\nln n + / INR b * (ln n + / INR c * ln n)\nHlog  : / INR 2 * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHra  : INR 2 * / INR 2 = 1\nHrb  : INR b * / INR b = 1\nHrc  : INR c * / INR c = 1\nHcoef  : 1 / 2 * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHhalf  : / INR 2 = 1 / 2\n|-2 * (/ INR b * (1 + / INR c)) = 2 * (7 / 6)",
    "b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < 2)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nH0a  : (0 < 2)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2) =\nRpower n (25 / 36)\nH0b  : (0 < b)%nat\nH0c  : (0 < c)%nat\nHia  : 0 < INR 2\nHib  : 0 < INR b\nHic  : 0 < INR c\nHp_c  : 0 < Rpower n (/ INR c)\nHp_b  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp_a  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2)\nHlc  : ln (n * Rpower n (/ INR c)) = ln n + / INR c * ln n\nHlb  : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) =\nln n + / INR b * (ln n + / INR c * ln n)\nHlog  : / INR 2 * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHra  : INR 2 * / INR 2 = 1\nHrb  : INR b * / INR b = 1\nHrc  : INR c * / INR c = 1\nHcoef  : 1 / 2 * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHhalf  : / INR 2 = 1 / 2\n|-2 <> 0"
  ],
  "success": false,
  "tactic": "- nra.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (H0a : (0 < a)%nat) by lia.",
    "assert (H0b : (0 < b)%nat) by lia.",
    "assert (H0c : (0 < c)%nat) by lia.",
    "assert (Hia : 0 < INR a) by (apply lt_0_INR; exact H0a).",
    "assert (Hib : 0 < INR b) by (apply lt_0_INR; exact H0b).",
    "assert (Hic : 0 < INR c) by (apply lt_0_INR; exact H0c).",
    "assert (Hp_c : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_b : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_a : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hlc : ln (n * Rpower n (/ INR c)) = ln n + (/ INR c) * ln n).",
    "{ rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hp_c).",
    "rewrite (ln_Rpower n (/ INR c)).",
    "reflexivity.",
    "}",
    "assert (Hlb : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) = ln n + (/ INR b) * (ln n + (/ INR c) * ln n)).",
    "{ rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hp_b).",
    "rewrite (ln_Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "rewrite Hlc.",
    "reflexivity.",
    "}",
    "assert (Hlog := f_equal ln Hpow).",
    "rewrite !ln_Rpower in Hlog.",
    "rewrite Hlb in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hra : INR a * / INR a = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hrb : INR b * / INR b = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hrc : INR c * / INR c = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hcoef : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36).",
    "{ apply (Rmult_eq_reg_r (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (Ha_cases : a = 2%nat \\/ (3 <= a)%nat) by lia.",
    "destruct Ha_cases as [Ha2 | Ha3].",
    "- subst a.",
    "assert (Hhalf : / INR 2 = 1 / 2).",
    "{ rewrite (S_INR 1).",
    "rewrite INR_1.",
    "field.",
    "}",
    "rewrite Hhalf in Hcoef.",
    "assert (Hq : / INR b * (1 + / INR c) = 7 / 6).",
    "{ apply (Rmult_eq_reg_l 2)."
  ]
}
```

### amc12a_2020_p13__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12a_2020_p13__E-level1__gpt-5.6-terra__seed0`. Solved; $0.58947860; 36 completions; 23.237 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'subproof-incomplete': 2, 'syntax-error': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference positivity was not found in the current environment.')
```

### amc12a_2020_p13__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/amc12a_2020_p13__E-level2__gpt-5.6-luna__seed0`. Unsolved; $0.12662500; 36 completions; 61.402 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 5, 'rewrite-no-match': 1, 'ring-failure': 1, 'syntax-error': 4, 'unify-failure': 3, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHpow :\n  Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n  Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR a".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 35,
  "category": "no-applicable-tactic",
  "elapsed": 0.19146629516035318,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < 2)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nH0a  : (0 < 2)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2) =\nRpower n (25 / 36)\nH0b  : (0 < b)%nat\nH0c  : (0 < c)%nat\nHia  : 0 < INR 2\nHib  : 0 < INR b\nHic  : 0 < INR c\nHp_c  : 0 < Rpower n (/ INR c)\nHp_b  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp_a  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2)\nHlc  : ln (n * Rpower n (/ INR c)) = ln n + / INR c * ln n\nHlb  : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) =\nln n + / INR b * (ln n + / INR c * ln n)\nHlog  : / INR 2 * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHra  : INR 2 * / INR 2 = 1\nHrb  : INR b * / INR b = 1\nHrc  : INR c * / INR c = 1\nHcoef  : 1 / 2 * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHhalf  : / INR 2 = 1 / 2\n|-2 * (/ INR b * (1 + / INR c)) = 2 * (7 / 6)",
    "b, c  : nat\nn  : R\nHn  : 0 < n\nHn1  : n <> 1\nHa  : (1 < 2)%nat\nHb  : (1 < b)%nat\nHc  : (1 < c)%nat\nH0a  : (0 < 2)%nat\nHpow  : Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2) =\nRpower n (25 / 36)\nH0b  : (0 < b)%nat\nH0c  : (0 < c)%nat\nHia  : 0 < INR 2\nHib  : 0 < INR b\nHic  : 0 < INR c\nHp_c  : 0 < Rpower n (/ INR c)\nHp_b  : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHp_a  : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR 2)\nHlc  : ln (n * Rpower n (/ INR c)) = ln n + / INR c * ln n\nHlb  : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) =\nln n + / INR b * (ln n + / INR c * ln n)\nHlog  : / INR 2 * (ln n + / INR b * (ln n + / INR c * ln n)) = 25 / 36 * ln n\nHln  : ln n <> 0\nHra  : INR 2 * / INR 2 = 1\nHrb  : INR b * / INR b = 1\nHrc  : INR c * / INR c = 1\nHcoef  : 1 / 2 * (1 + / INR b * (1 + / INR c)) = 25 / 36\nHhalf  : / INR 2 = 1 / 2\n|-2 <> 0"
  ],
  "success": false,
  "tactic": "- nra.",
  "verified_prefix": [
    "intros a b c n Hn Hn1 Hab Hpow.",
    "destruct Hab as [Ha [Hb Hc]].",
    "assert (H0a : (0 < a)%nat) by lia.",
    "assert (H0b : (0 < b)%nat) by lia.",
    "assert (H0c : (0 < c)%nat) by lia.",
    "assert (Hia : 0 < INR a) by (apply lt_0_INR; exact H0a).",
    "assert (Hib : 0 < INR b) by (apply lt_0_INR; exact H0b).",
    "assert (Hic : 0 < INR c) by (apply lt_0_INR; exact H0c).",
    "assert (Hp_c : 0 < Rpower n (/ INR c)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_b : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hp_a : 0 < Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a)).",
    "{ unfold Rpower. apply exp_pos. }",
    "assert (Hlc : ln (n * Rpower n (/ INR c)) = ln n + (/ INR c) * ln n).",
    "{ rewrite (ln_mult n (Rpower n (/ INR c)) Hn Hp_c).",
    "rewrite (ln_Rpower n (/ INR c)).",
    "reflexivity.",
    "}",
    "assert (Hlb : ln (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) = ln n + (/ INR b) * (ln n + (/ INR c) * ln n)).",
    "{ rewrite (ln_mult n (Rpower (n * Rpower n (/ INR c)) (/ INR b)) Hn Hp_b).",
    "rewrite (ln_Rpower (n * Rpower n (/ INR c)) (/ INR b)).",
    "rewrite Hlc.",
    "reflexivity.",
    "}",
    "assert (Hlog := f_equal ln Hpow).",
    "rewrite !ln_Rpower in Hlog.",
    "rewrite Hlb in Hlog.",
    "assert (Hln : ln n <> 0) by (apply ln_neq_0; assumption).",
    "assert (Hra : INR a * / INR a = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hrb : INR b * / INR b = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hrc : INR c * / INR c = 1).",
    "{ apply Rinv_r. lra. }",
    "assert (Hcoef : / INR a * (1 + / INR b * (1 + / INR c)) = 25 / 36).",
    "{ apply (Rmult_eq_reg_r (ln n)).",
    "- nra.",
    "- exact Hln.",
    "}",
    "assert (Ha_cases : a = 2%nat \\/ (3 <= a)%nat) by lia.",
    "destruct Ha_cases as [Ha2 | Ha3].",
    "- subst a.",
    "assert (Hhalf : / INR 2 = 1 / 2).",
    "{ rewrite (S_INR 1).",
    "rewrite INR_1.",
    "field.",
    "}",
    "rewrite Hhalf in Hcoef.",
    "assert (Hq : / INR b * (1 + / INR c) = 7 / 6).",
    "{ apply (Rmult_eq_reg_l 2)."
  ]
}
```

### amc12a_2020_p13__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12a_2020_p13__E-level1__gpt-5.6-terra__seed0`. Solved; $0.58947860; 36 completions; 23.237 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'subproof-incomplete': 2, 'syntax-error': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference positivity was not found in the current environment.')
```

### amc12b_2002_p11__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__A-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03795372; 23 completions; 14.170 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'focus-error': 2, 'no-such-goal': 1, 'no-witness': 1, 'syntax-error': 1, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "syntax-error",
  "elapsed": 4.043759839609265,
  "error": "(-32003, \"Coq: Syntax error: '|' or ']' expected (in [or_and_intropattern]).\")",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b  : Z\nHa  : prime a\nHb  : prime b\nHab  : prime (a + b)\nHabm  : prime (a - b)\nHeven  : forall p : Z, prime p -> Zeven p -> p = 2\nHnp  : ~ prime 17\nn  : Z\nHn  : 1 <= n < 17\nH  : n = 1 \\/\nn = 2 \\/\nn = 3 \\/\nn = 4 \\/\nn = 5 \\/\nn = 6 \\/\nn = 7 \\/\nn = 8 \\/\nn = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16\n|-rel_prime n 17"
  ],
  "success": false,
  "tactic": "destruct H as [->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|->]]]]]]]]]]]]]]]].",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Heven : forall p : Z, prime p -> Zeven p -> p = 2).",
    "{ intros p Hp Hpe.",
    "apply Zeven_equiv in Hpe.",
    "destruct Hpe as [k Hk].",
    "assert (Hd : (2 | p)).",
    "{ exists k.",
    "rewrite Hk.",
    "ring.",
    "}",
    "pose proof (prime_divisors p Hp 2 Hd) as H.",
    "destruct H as [Hneg|[Hone|[Heq|Hneg]]].",
    "- exfalso.",
    "revert Hneg.",
    "discriminate.",
    "- exfalso.",
    "revert Hone.",
    "discriminate.",
    "- symmetry.",
    "exact Heq.",
    "- assert (Hp2 : 2 <= p) by (apply prime_ge_2; exact Hp).",
    "lia.",
    "}",
    "assert (Hp17 : prime 17).",
    "{ destruct (prime_dec 17) as [Hp|Hnp].",
    "- exact Hp.",
    "- exfalso.",
    "apply Hnp.",
    "apply prime_intro.",
    "+ lia.",
    "+ intros n Hn.",
    "assert (n = 1 \\/ n = 2 \\/ n = 3 \\/ n = 4 \\/ n = 5 \\/ n = 6 \\/ n = 7 \\/ n = 8 \\/ n = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16) by lia."
  ]
}
```

### amc12b_2002_p11__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__A-level0__gpt-5.6-terra__seed0`. Unsolved; $0.37285620; 25 completions; 18.361 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'syntax-error': 1, 'type-mismatch': 3, 'unknown-reference': 2}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "unknown-reference",
  "elapsed": 4.039714585989714,
  "error": "(-32003, 'Coq: The reference Z.div_mod_eq was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nHa  : prime a\nHsub  : prime (a - 2)\nHab  : prime (a + 2)\nHb  : prime 2\nHeven_prime  : forall p : Z, prime p -> Z.Even p -> p = 2\nHa_ge  : 4 <= a\nHa_odd  : Z.Odd a\nHb_even  : Z.Even 2\nHrbound  : 0 <= a mod 3 < 3\nHr  : a mod 3 = 1\n|-a + 2 = (a + 2) / 3 * 3"
  ],
  "success": false,
  "tactic": "rewrite <- Z.div_mod_eq with (a := a) (b := 3) at Hr.",
  "verified_prefix": [
    "intros a b Ha Hb Hab Hsub.",
    "assert (Heven_prime : forall p : Z, prime p -> Z.Even p -> p = 2).",
    "{ intros p Hp [k Hk].",
    "assert (Hdiv : (2 | p)).",
    "{ exists k.",
    "lia.",
    "}",
    "pose proof (prime_div_prime 2 p prime_2 Hp Hdiv) as H.",
    "lia.",
    "}",
    "assert (Ha_ge : 4 <= a).",
    "{ pose proof (prime_ge_2 b Hb).",
    "pose proof (prime_ge_2 (a - b) Hsub).",
    "lia.",
    "}",
    "assert (Ha_odd : Z.Odd a).",
    "{ destruct (Z.Even_or_Odd a) as [He | Ho].",
    "- pose proof (Heven_prime a Ha He).",
    "lia.",
    "- exact Ho.",
    "}",
    "assert (Hb_even : Z.Even b).",
    "{ destruct (Z.Even_or_Odd b) as [He | Ho].",
    "- exact He.",
    "- exfalso.",
    "destruct Ha_odd as [x Hx].",
    "destruct Ho as [y Hy].",
    "assert (H1 : Z.Even (a + b)).",
    "{ exists (x + y + 1).",
    "lia.",
    "}",
    "assert (H2 : Z.Even (a - b)).",
    "{ exists (x - y).",
    "lia.",
    "}",
    "pose proof (Heven_prime (a + b) Hab H1).",
    "pose proof (Heven_prime (a - b) Hsub H2).",
    "lia.",
    "}",
    "assert (Hb_eq : b = 2) by (apply Heven_prime; assumption).",
    "subst b.",
    "assert (Ha_eq : a = 5).",
    "{ assert (Hrbound : 0 <= a mod 3 < 3) by (apply Z.mod_pos_bound; lia).",
    "assert (Hr : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2).",
    "{ destruct (a mod 3) as [|p|p] eqn:Hm.",
    "- left.",
    "reflexivity.",
    "- destruct p as [p|p|].",
    "+ exfalso.",
    "simpl in Hrbound.",
    "pose proof (Pos2Z.is_pos p).",
    "lia.",
    "+ destruct p as [p|p|].",
    "* exfalso.",
    "simpl in Hrbound.",
    "pose proof (Pos2Z.is_pos p).",
    "lia.",
    "* exfalso.",
    "simpl in Hrbound.",
    "pose proof (Pos2Z.is_pos p).",
    "lia.",
    "* right.",
    "right.",
    "reflexivity.",
    "+ right.",
    "left.",
    "reflexivity.",
    "- exfalso.",
    "simpl in Hrbound.",
    "lia.",
    "}",
    "destruct Hr as [Hr | [Hr | Hr]].",
    "- assert (Hdiv : (3 | a)).",
    "{ apply (Z.mod_divide a 3).",
    "lia.",
    "exact Hr.",
    "}",
    "pose proof (prime_div_prime 3 a prime_3 Ha Hdiv).",
    "lia.",
    "- assert (Hdiv : (3 | a + 2)).",
    "{ exists ((a + 2) / 3)."
  ]
}
```

### amc12b_2002_p11__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__B-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03416094; 34 completions; 10.442 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The variable lia was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 30,
  "category": "type-mismatch",
  "elapsed": 4.01538550388068,
  "error": "(-32003, 'Coq: In environment\\na, b : Z\\nHa : prime a\\nHb : prime b\\nHab : prime (a + b)\\nHsub : prime (a - b)\\np, d : Z\\nHp : 1 < p\\nHprime : forall n : Z, 1 <= n < p -> rel_prime n p\\nHd : 1 < d < p\\nHdiv : (d | p)\\nHd1 : 1 <= d\\nHr1 : (1 | d)\\nHr2 : (1 | p)\\nHgreat : forall x : Z, (x | d) -> (x | p) -> (x | 1)\\nThe term \"Hdiv\" has type \"(d | p)\" while it is expected to have type\\n \"(d | d)\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b  : Z\nHa  : prime a\nHb  : prime b\nHab  : prime (a + b)\nHsub  : prime (a - b)\np, d  : Z\nHp  : 1 < p\nHprime  : forall n : Z, 1 <= n < p -> rel_prime n p\nHd  : 1 < d < p\nHdiv  : (d | p)\nHd1  : 1 <= d\nHr1  : (1 | d)\nHr2  : (1 | p)\nHgreat  : forall x : Z, (x | d) -> (x | p) -> (x | 1)\n|-False"
  ],
  "success": false,
  "tactic": "pose proof (Hgreat d Hdiv (Z.divide_refl d)) as Hdunit.",
  "verified_prefix": [
    "intros a b Ha Hb Hab Hsub.",
    "assert (Hnd : forall p d : Z, prime p -> 1 < d < p -> (d | p) -> False).",
    "{ intros p d Hp Hd Hdiv.",
    "destruct Hp as [Hp Hprime].",
    "assert (Hd1 : 1 <= d).",
    "{ apply Z.lt_le_incl.",
    "exact (proj1 Hd).",
    "}",
    "pose proof (Hprime d (conj Hd1 (proj2 Hd))) as Hr.",
    "destruct Hr as [Hr1 Hr2 Hgreat]."
  ]
}
```

### amc12b_2002_p11__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__B-level0__gpt-5.6-terra__seed0`. Unsolved; $0.37498280; 25 completions; 34.575 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 2, 'syntax-error': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "focus-error",
  "elapsed": 12.404024955816567,
  "error": "(-32003, 'Coq: [Focus] Wrong bullet +: Current bullet + is not finished.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nHa  : 1 < a\nHac  : forall n : Z, 1 <= n < a -> rel_prime n a\nHapc  : forall n : Z, 1 <= n < a - 2 -> rel_prime n (a - 2)\nHap  : 1 < a - 2\nHabc  : forall n : Z, 1 <= n < a + 2 -> rel_prime n (a + 2)\nHab  : 1 < a + 2\nHbc  : forall n : Z, 1 <= n < 2 -> rel_prime n 2\nHb  : 1 < 2\nprime_div_eq  : forall p d : Z, prime p -> 1 < d -> (d | p) -> p = d\nHa4  : 3 < a\nHma  : 0 <= a mod 2 < 2\nHmb  : 0 <= 2 mod 2 < 2\nHra  : a mod 2 = 1\nDb  : (2 | 2)\nHrb  : 2 mod 2 = 0\nHra3  : 0 <= a mod 3 < 3\nH0  : a mod 3 = 0\n|-prime (a + 2 + (a - 2 + (a + 2)))",
    "a  : Z\nHa  : 1 < a\nHac  : forall n : Z, 1 <= n < a -> rel_prime n a\nHapc  : forall n : Z, 1 <= n < a - 2 -> rel_prime n (a - 2)\nHap  : 1 < a - 2\nHabc  : forall n : Z, 1 <= n < a + 2 -> rel_prime n (a + 2)\nHab  : 1 < a + 2\nHbc  : forall n : Z, 1 <= n < 2 -> rel_prime n 2\nHb  : 1 < 2\nprime_div_eq  : forall p d : Z, prime p -> 1 < d -> (d | p) -> p = d\nHa4  : 3 < a\nHma  : 0 <= a mod 2 < 2\nHmb  : 0 <= 2 mod 2 < 2\nHra  : a mod 2 = 1\nDb  : (2 | 2)\nHrb  : 2 mod 2 = 0\nHra3  : 0 <= a mod 3 < 3\nH1  : a mod 3 = 1\n|-prime (a + 2 + (a - 2 + (a + 2)))",
    "a  : Z\nHa  : 1 < a\nHac  : forall n : Z, 1 <= n < a -> rel_prime n a\nHapc  : forall n : Z, 1 <= n < a - 2 -> rel_prime n (a - 2)\nHap  : 1 < a - 2\nHabc  : forall n : Z, 1 <= n < a + 2 -> rel_prime n (a + 2)\nHab  : 1 < a + 2\nHbc  : forall n : Z, 1 <= n < 2 -> rel_prime n 2\nHb  : 1 < 2\nprime_div_eq  : forall p d : Z, prime p -> 1 < d -> (d | p) -> p = d\nHa4  : 3 < a\nHma  : 0 <= a mod 2 < 2\nHmb  : 0 <= 2 mod 2 < 2\nHra  : a mod 2 = 1\nDb  : (2 | 2)\nHrb  : 2 mod 2 = 0\nHra3  : 0 <= a mod 3 < 3\nH2  : a mod 3 = 2\n|-prime (a + 2 + (a - 2 + (a + 2)))"
  ],
  "success": false,
  "tactic": "+ assert (Da : (3 | a)).",
  "verified_prefix": [
    "intros a b Ha Hb Hab Hap.",
    "assert (prime_div_eq : forall p d : Z, prime p -> 1 < d -> (d | p) -> p = d).",
    "{ intros p d Hp Hd Hdiv.",
    "destruct Hp as [Hp Hcop].",
    "assert (Hle : d <= p).",
    "{ apply Z.divide_pos_le.",
    "- lia.",
    "- exact Hdiv.",
    "}",
    "destruct (Z.eq_dec p d) as [Heq | Hneq].",
    "- exact Heq.",
    "- assert (Hbounds : 1 <= d < p) by lia.",
    "specialize (Hcop d Hbounds).",
    "apply rel_prime_bezout in Hcop.",
    "destruct Hcop as [u v Heq].",
    "destruct Hdiv as [q Hq].",
    "assert (Hd1 : (d | 1)).",
    "{ exists (u + v * q).",
    "nia.",
    "}",
    "pose proof (Z.divide_1_r_nonneg d ltac:(lia) Hd1) as Hd_eq.",
    "lia.",
    "}",
    "destruct Ha as [Ha Hac].",
    "destruct Hb as [Hb Hbc].",
    "destruct Hab as [Hab Habc].",
    "destruct Hap as [Hap Hapc].",
    "assert (Ha4 : 3 < a) by lia.",
    "assert (Hma : 0 <= a mod 2 < 2).",
    "{ apply Z.mod_pos_bound.",
    "lia.",
    "}",
    "assert (Hmb : 0 <= b mod 2 < 2).",
    "{ apply Z.mod_pos_bound.",
    "lia.",
    "}",
    "assert (Hra : a mod 2 = 0 \\/ a mod 2 = 1) by lia.",
    "assert (Hrb : b mod 2 = 0 \\/ b mod 2 = 1) by lia.",
    "destruct Hra as [Hra | Hra].",
    "- destruct Hrb as [Hrb | Hrb].",
    "+ assert (Hs : (a + b) mod 2 = 0).",
    "{ rewrite (Z.add_mod a b 2 ltac:(lia)).",
    "rewrite Hra, Hrb.",
    "reflexivity.",
    "}",
    "assert (Ht : (a - b) mod 2 = 0).",
    "{ rewrite (Zminus_mod a b 2).",
    "rewrite Hra, Hrb.",
    "reflexivity.",
    "}",
    "assert (Ds : (2 | a + b)).",
    "{ apply (Z.mod_divide _ _).",
    "- lia.",
    "- exact Hs.",
    "}",
    "assert (Dt : (2 | a - b)).",
    "{ apply (Z.mod_divide _ _).",
    "- lia.",
    "- exact Ht.",
    "}",
    "assert (Es : a + b = 2).",
    "{ apply prime_div_eq.",
    "- exact (prime_intro _ Hab Habc).",
    "- lia.",
    "- exact Ds.",
    "}",
    "assert (Et : a - b = 2).",
    "{ apply prime_div_eq.",
    "- exact (prime_intro _ Hap Hapc).",
    "- lia.",
    "- exact Dt.",
    "}",
    "lia.",
    "+ assert (Da : (2 | a)).",
    "{ apply (Z.mod_divide _ _).",
    "- lia.",
    "- exact Hra.",
    "}",
    "assert (Ea : a = 2).",
    "{ apply prime_div_eq.",
    "- exact (prime_intro _ Ha Hac).",
    "- lia.",
    "- exact Da.",
    "}",
    "lia.",
    "- destruct Hrb as [Hrb | Hrb].",
    "+ assert (Db : (2 | b)).",
    "{ apply (Z.mod_divide _ _).",
    "- lia.",
    "- exact Hrb.",
    "}",
    "assert (Eb : b = 2).",
    "{ apply prime_div_eq.",
    "- exact (prime_intro _ Hb Hbc).",
    "- lia.",
    "- exact Db.",
    "}",
    "subst b.",
    "assert (Hra3 : 0 <= a mod 3 < 3).",
    "{ apply Z.mod_pos_bound.",
    "lia.",
    "}",
    "assert (Hcases : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2) by lia.",
    "destruct Hcases as [H0 | [H1 | H2]]."
  ]
}
```

### amc12b_2002_p11__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__C-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03669476; 19 completions; 18.205 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'already-used': 1, 'no-witness': 1, 'other': 1, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No such bound variable p (possible names are: a and b).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 16,
  "category": "no-witness",
  "elapsed": 4.022111559286714,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b  : Z\nHa  : prime a\nHb  : prime b\nHab  : prime (a + b)\nHabm  : prime (a - b)\nHa0  : 2 <= a\nHb0  : 2 <= b\nHab0  : 2 <= a + b\nHabm0  : 2 <= a - b\nHodd  : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0\nHsum3  : 3 <= a + b\nHdiff3  : 3 <= a - b\nHsumodd  : (a + b) mod 2 <> 0\nHdiffodd  : (a - b) mod 2 <> 0\nHaodd  : a mod 2 <> 0\nHbodd  : b mod 2 <> 0\n|-(a + b) mod 2 = 0"
  ],
  "success": false,
  "tactic": "lia.",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Ha0 : 2 <= a) by (apply prime_ge_2; exact Ha).",
    "assert (Hb0 : 2 <= b) by (apply prime_ge_2; exact Hb).",
    "assert (Hab0 : 2 <= a + b) by (apply prime_ge_2; exact Hab).",
    "assert (Habm0 : 2 <= a - b) by (apply prime_ge_2; exact Habm).",
    "assert (Hodd : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0).",
    "{ intros p Hp Hp3 Hm.",
    "assert (Hd : (2 | p)) by (apply Zmod_divide; lia).",
    "destruct (prime_divisors p Hp 2 Hd) as [D|[D|[D|D]]]; lia.",
    "}",
    "assert (Hsum3 : 3 <= a + b) by lia.",
    "assert (Hdiff3 : 3 <= a - b).",
    "{ destruct (Z.eq_dec (a - b) 2) as [Heq|Heq].",
    "- assert (Hd : (2 | a + b)).",
    "{ exists (b + 1). lia. }",
    "destruct (prime_divisors (a + b) Hab 2 Hd) as [D|[D|[D|D]]]; lia.",
    "- lia.",
    "}",
    "pose proof (Hodd (a + b) Hab Hsum3) as Hsumodd.",
    "pose proof (Hodd (a - b) Habm Hdiff3) as Hdiffodd.",
    "assert (Hao : a = 2 \\/ a mod 2 <> 0).",
    "{ destruct (Z.eq_dec a 2) as [Ha2|Ha2].",
    "- left; exact Ha2.",
    "- right.",
    "exact (Hodd a Ha ltac:(lia)).",
    "}",
    "assert (Hbo : b = 2 \\/ b mod 2 <> 0).",
    "{ destruct (Z.eq_dec b 2) as [Hb2|Hb2].",
    "- left; exact Hb2.",
    "- right.",
    "exact (Hodd b Hb ltac:(lia)).",
    "}",
    "assert (Hb2 : b = 2).",
    "{ destruct Hao as [Ha2|Haodd].",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ exfalso; lia.",
    "+ exfalso.",
    "apply Hsumodd.",
    "lia.",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ exact Hb2.",
    "+ exfalso.",
    "apply Hsumodd."
  ]
}
```

### amc12b_2002_p11__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__C-level0__gpt-5.6-terra__seed0`. Solved; $0.28605600; 32 completions; 14.144 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

### amc12b_2002_p11__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12b_2002_p11__C-level1__gpt-5.6-luna__seed0`. Unsolved; $0.11954284; 31 completions; 39.961 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 8, 'incomplete-proof': 1, 'no-witness': 1, 'other': 1, 'syntax-error': 2, 'type-mismatch': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No such bound variable p (possible names are: a and b).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "focus-error",
  "elapsed": 4.053818176500499,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "Hab  : prime (5 + 2)\nHabm  : prime (5 - 2)\nHa  : prime 5\nHb  : prime 2\nHab0  : 2 <= 5 + 2\nHabm0  : 2 <= 5 - 2\nHa0  : 2 <= 5\nHb0  : 2 <= 2\nHodd  : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0\nHao  : 5 = 2 \\/ 5 mod 2 <> 0\nHsum3  : 3 <= 5 + 2\nHdiff3  : 3 <= 5 - 2\nHsumodd  : (5 + 2) mod 2 <> 0\nHdiffodd  : (5 - 2) mod 2 <> 0\nHbo  : 2 = 2 \\/ 2 mod 2 <> 0\nHd  : (3 | 5 - 2)\nHzero  : (5 - 2) mod 3 = 0\nHres  : 5 mod 3 = 2\nHmod3  : 0 <= 5 mod 3 < 3\nH  : exists x : Z,\n  (match x with\n   | Z.pos H0 =>\n       (fix Ffix (x0 : comparison) (x1 x2 : positive) {struct x2} :\n            comparison :=\n          match x1 with\n          | (H1~1)%positive =>\n              match x2 with\n              | (H2~1)%positive => Ffix x0 H1 H2\n              | (H2~0)%positive => Ffix Gt H1 H2\n              | 1%positive => Gt\n              end\n          | (H1~0)%positive =>\n              match x2 with\n              | (H2~1)%positive => Ffix Lt H1 H2\n              | (H2~0)%positive => Ffix x0 H1 H2\n              | 1%positive => Gt\n              end\n          | 1%positive => match x2 with\n                          | 1%positive => x0\n                          | _ => Lt\n                          end\n          end)\n         Eq 1%positive H0\n   | _ => Gt\n   end = Lt /\\\n   match x with\n   | 17 => Eq\n   | 0 | 15 | 11 | 7 | 13 | 9 | 5 | 3 | 14 | 10 | \n     6 | 12 | 16 | 8 | 4 | 2 | 1 | Z.neg _ => Lt\n   | _ => Gt\n   end = Lt) /\\\n  (Zis_gcd x 17 1 -> False)\n|-prime 17"
  ],
  "success": false,
  "tactic": "}",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Ha0 : 2 <= a) by (apply prime_ge_2; exact Ha).",
    "assert (Hb0 : 2 <= b) by (apply prime_ge_2; exact Hb).",
    "assert (Hab0 : 2 <= a + b) by (apply prime_ge_2; exact Hab).",
    "assert (Habm0 : 2 <= a - b) by (apply prime_ge_2; exact Habm).",
    "assert (Hodd : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0).",
    "{ intros p Hp Hp3 Hm.",
    "assert (Hd : (2 | p)) by (apply Zmod_divide; lia).",
    "destruct (prime_divisors p Hp 2 Hd) as [D|[D|[D|D]]]; lia.",
    "}",
    "assert (Hsum3 : 3 <= a + b) by lia.",
    "assert (Hdiff3 : 3 <= a - b).",
    "{ destruct (Z.eq_dec (a - b) 2) as [Heq|Heq].",
    "- assert (Hd : (2 | a + b)).",
    "{ exists (b + 1). lia. }",
    "destruct (prime_divisors (a + b) Hab 2 Hd) as [D|[D|[D|D]]]; lia.",
    "- lia.",
    "}",
    "pose proof (Hodd (a + b) Hab Hsum3) as Hsumodd.",
    "pose proof (Hodd (a - b) Habm Hdiff3) as Hdiffodd.",
    "assert (Hao : a = 2 \\/ a mod 2 <> 0).",
    "{ destruct (Z.eq_dec a 2) as [Ha2|Ha2].",
    "- left; exact Ha2.",
    "- right.",
    "exact (Hodd a Ha ltac:(lia)).",
    "}",
    "assert (Hbo : b = 2 \\/ b mod 2 <> 0).",
    "{ destruct (Z.eq_dec b 2) as [Hb2|Hb2].",
    "- left; exact Hb2.",
    "- right.",
    "exact (Hodd b Hb ltac:(lia)).",
    "}",
    "assert (Hb2 : b = 2).",
    "{ destruct Hao as [Ha2|Haodd].",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ lia.",
    "+ lia.",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ exact Hb2.",
    "+ exfalso.",
    "apply Hsumodd.",
    "assert (Ha1 : a mod 2 = 1) by (pose proof (Z.mod_pos_bound a 2 ltac:(lia)) as H; lia).",
    "assert (Hb1 : b mod 2 = 1) by (pose proof (Z.mod_pos_bound b 2 ltac:(lia)) as H; lia).",
    "rewrite Z.add_mod by lia.",
    "rewrite Ha1.",
    "rewrite Hb1.",
    "reflexivity.",
    "}",
    "subst b.",
    "assert (Hmod3 : 0 <= a mod 3 < 3).",
    "{ apply Z.mod_pos_bound.",
    "lia.",
    "}",
    "assert (Hres : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2) by lia.",
    "destruct Hres as [Hres|[Hres|Hres]].",
    "- assert (Hd : (3 | a)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hres.",
    "}",
    "destruct (prime_divisors a Ha 3 Hd) as [D|[D|[D|D]]]; lia.",
    "- assert (Hzero : (a + 2) mod 3 = 0).",
    "{ rewrite Z.add_mod by lia.",
    "rewrite Hres.",
    "vm_compute.",
    "reflexivity.",
    "}",
    "assert (Hd : (3 | a + 2)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hzero.",
    "}",
    "destruct (prime_divisors (a + 2) Hab 3 Hd) as [D|[D|[D|D]]]; lia.",
    "- assert (Hzero : (a - 2) mod 3 = 0).",
    "{ replace (a - 2) with (a + -2) by ring.",
    "rewrite Z.add_mod by lia.",
    "rewrite Hres.",
    "vm_compute.",
    "reflexivity.",
    "}",
    "assert (Hd : (3 | a - 2)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hzero.",
    "}",
    "assert (Ha5 : a = 5).",
    "{ destruct (prime_divisors (a - 2) Habm 3 Hd) as [D|[D|[D|D]]]; lia.",
    "}",
    "subst a.",
    "replace (5 + 2 + (5 - 2 + (5 + 2))) with 17 by lia.",
    "assert (H17 : prime 17).",
    "{ destruct (prime_dec_aux 17 17) as [H|H].",
    "- apply prime_intro.",
    "+ lia.",
    "+ intros n Hn.",
    "destruct (Z.eq_dec n 1) as [Hn1|Hn1].",
    "* subst n.",
    "apply rel_prime_1.",
    "* apply H.",
    "lia.",
    "- vm_compute in H."
  ]
}
```

### amc12b_2002_p11__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__C-level0__gpt-5.6-terra__seed0`. Solved; $0.28605600; 32 completions; 14.144 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

### amc12b_2002_p11__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/amc12b_2002_p11__C-level2__gpt-5.6-luna__seed0`. Unsolved; $0.11954284; 31 completions; 39.961 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 8, 'incomplete-proof': 1, 'no-witness': 1, 'other': 1, 'syntax-error': 2, 'type-mismatch': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No such bound variable p (possible names are: a and b).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "focus-error",
  "elapsed": 4.053818176500499,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "Hab  : prime (5 + 2)\nHabm  : prime (5 - 2)\nHa  : prime 5\nHb  : prime 2\nHab0  : 2 <= 5 + 2\nHabm0  : 2 <= 5 - 2\nHa0  : 2 <= 5\nHb0  : 2 <= 2\nHodd  : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0\nHao  : 5 = 2 \\/ 5 mod 2 <> 0\nHsum3  : 3 <= 5 + 2\nHdiff3  : 3 <= 5 - 2\nHsumodd  : (5 + 2) mod 2 <> 0\nHdiffodd  : (5 - 2) mod 2 <> 0\nHbo  : 2 = 2 \\/ 2 mod 2 <> 0\nHd  : (3 | 5 - 2)\nHzero  : (5 - 2) mod 3 = 0\nHres  : 5 mod 3 = 2\nHmod3  : 0 <= 5 mod 3 < 3\nH  : exists x : Z,\n  (match x with\n   | Z.pos H0 =>\n       (fix Ffix (x0 : comparison) (x1 x2 : positive) {struct x2} :\n            comparison :=\n          match x1 with\n          | (H1~1)%positive =>\n              match x2 with\n              | (H2~1)%positive => Ffix x0 H1 H2\n              | (H2~0)%positive => Ffix Gt H1 H2\n              | 1%positive => Gt\n              end\n          | (H1~0)%positive =>\n              match x2 with\n              | (H2~1)%positive => Ffix Lt H1 H2\n              | (H2~0)%positive => Ffix x0 H1 H2\n              | 1%positive => Gt\n              end\n          | 1%positive => match x2 with\n                          | 1%positive => x0\n                          | _ => Lt\n                          end\n          end)\n         Eq 1%positive H0\n   | _ => Gt\n   end = Lt /\\\n   match x with\n   | 17 => Eq\n   | 0 | 15 | 11 | 7 | 13 | 9 | 5 | 3 | 14 | 10 | \n     6 | 12 | 16 | 8 | 4 | 2 | 1 | Z.neg _ => Lt\n   | _ => Gt\n   end = Lt) /\\\n  (Zis_gcd x 17 1 -> False)\n|-prime 17"
  ],
  "success": false,
  "tactic": "}",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Ha0 : 2 <= a) by (apply prime_ge_2; exact Ha).",
    "assert (Hb0 : 2 <= b) by (apply prime_ge_2; exact Hb).",
    "assert (Hab0 : 2 <= a + b) by (apply prime_ge_2; exact Hab).",
    "assert (Habm0 : 2 <= a - b) by (apply prime_ge_2; exact Habm).",
    "assert (Hodd : forall p : Z, prime p -> 3 <= p -> p mod 2 <> 0).",
    "{ intros p Hp Hp3 Hm.",
    "assert (Hd : (2 | p)) by (apply Zmod_divide; lia).",
    "destruct (prime_divisors p Hp 2 Hd) as [D|[D|[D|D]]]; lia.",
    "}",
    "assert (Hsum3 : 3 <= a + b) by lia.",
    "assert (Hdiff3 : 3 <= a - b).",
    "{ destruct (Z.eq_dec (a - b) 2) as [Heq|Heq].",
    "- assert (Hd : (2 | a + b)).",
    "{ exists (b + 1). lia. }",
    "destruct (prime_divisors (a + b) Hab 2 Hd) as [D|[D|[D|D]]]; lia.",
    "- lia.",
    "}",
    "pose proof (Hodd (a + b) Hab Hsum3) as Hsumodd.",
    "pose proof (Hodd (a - b) Habm Hdiff3) as Hdiffodd.",
    "assert (Hao : a = 2 \\/ a mod 2 <> 0).",
    "{ destruct (Z.eq_dec a 2) as [Ha2|Ha2].",
    "- left; exact Ha2.",
    "- right.",
    "exact (Hodd a Ha ltac:(lia)).",
    "}",
    "assert (Hbo : b = 2 \\/ b mod 2 <> 0).",
    "{ destruct (Z.eq_dec b 2) as [Hb2|Hb2].",
    "- left; exact Hb2.",
    "- right.",
    "exact (Hodd b Hb ltac:(lia)).",
    "}",
    "assert (Hb2 : b = 2).",
    "{ destruct Hao as [Ha2|Haodd].",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ lia.",
    "+ lia.",
    "- destruct Hbo as [Hb2|Hbodd].",
    "+ exact Hb2.",
    "+ exfalso.",
    "apply Hsumodd.",
    "assert (Ha1 : a mod 2 = 1) by (pose proof (Z.mod_pos_bound a 2 ltac:(lia)) as H; lia).",
    "assert (Hb1 : b mod 2 = 1) by (pose proof (Z.mod_pos_bound b 2 ltac:(lia)) as H; lia).",
    "rewrite Z.add_mod by lia.",
    "rewrite Ha1.",
    "rewrite Hb1.",
    "reflexivity.",
    "}",
    "subst b.",
    "assert (Hmod3 : 0 <= a mod 3 < 3).",
    "{ apply Z.mod_pos_bound.",
    "lia.",
    "}",
    "assert (Hres : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2) by lia.",
    "destruct Hres as [Hres|[Hres|Hres]].",
    "- assert (Hd : (3 | a)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hres.",
    "}",
    "destruct (prime_divisors a Ha 3 Hd) as [D|[D|[D|D]]]; lia.",
    "- assert (Hzero : (a + 2) mod 3 = 0).",
    "{ rewrite Z.add_mod by lia.",
    "rewrite Hres.",
    "vm_compute.",
    "reflexivity.",
    "}",
    "assert (Hd : (3 | a + 2)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hzero.",
    "}",
    "destruct (prime_divisors (a + 2) Hab 3 Hd) as [D|[D|[D|D]]]; lia.",
    "- assert (Hzero : (a - 2) mod 3 = 0).",
    "{ replace (a - 2) with (a + -2) by ring.",
    "rewrite Z.add_mod by lia.",
    "rewrite Hres.",
    "vm_compute.",
    "reflexivity.",
    "}",
    "assert (Hd : (3 | a - 2)).",
    "{ apply Zmod_divide.",
    "- lia.",
    "- exact Hzero.",
    "}",
    "assert (Ha5 : a = 5).",
    "{ destruct (prime_divisors (a - 2) Habm 3 Hd) as [D|[D|[D|D]]]; lia.",
    "}",
    "subst a.",
    "replace (5 + 2 + (5 - 2 + (5 + 2))) with 17 by lia.",
    "assert (H17 : prime 17).",
    "{ destruct (prime_dec_aux 17 17) as [H|H].",
    "- apply prime_intro.",
    "+ lia.",
    "+ intros n Hn.",
    "destruct (Z.eq_dec n 1) as [Hn1|Hn1].",
    "* subst n.",
    "apply rel_prime_1.",
    "* apply H.",
    "lia.",
    "- vm_compute in H."
  ]
}
```

### amc12b_2002_p11__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__C-level0__gpt-5.6-terra__seed0`. Solved; $0.28605600; 32 completions; 14.144 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

### amc12b_2002_p11__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__D-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03851196; 21 completions; 18.139 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'no-witness': 2, 'subproof-incomplete': 1, 'type-mismatch': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "type-mismatch",
  "elapsed": 8.301986741833389,
  "error": "(-32003, 'Coq: In environment\\na : Z\\nHa : prime a\\nHabm : prime (a - 2)\\nHab : prime (a + 2)\\nHb : prime 2\\nHevenprime : forall p : Z, prime p -> Z.Even p -> p = 2\\nHap : 2 <= a\\nHamp : 2 <= a - 2\\nHbp : 2 <= 2\\nHagt : 2 < a\\nHsumgt : 2 < a + 2\\nHaodd : Z.Odd a\\nHbeven : Z.Even 2\\nHsumodd : Z.Odd (a + 2)\\nH1 : a mod 3 = 1\\nHdiv1 : (3 | a - 1)\\nHdiv3 : (3 | 3)\\nThe term \"Hdiv1\" has type \"(3 | a - 1)\" while it is expected to have type\\n \"(3 | a)\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nHa  : prime a\nHabm  : prime (a - 2)\nHab  : prime (a + 2)\nHb  : prime 2\nHevenprime  : forall p : Z, prime p -> Z.Even p -> p = 2\nHap  : 2 <= a\nHamp  : 2 <= a - 2\nHbp  : 2 <= 2\nHagt  : 2 < a\nHsumgt  : 2 < a + 2\nHaodd  : Z.Odd a\nHbeven  : Z.Even 2\nHsumodd  : Z.Odd (a + 2)\nH1  : a mod 3 = 1\nHdiv1  : (3 | a - 1)\nHdiv3  : (3 | 3)\n|-(3 | a)",
    "a  : Z\nHa  : prime a\nHabm  : prime (a - 2)\nHab  : prime (a + 2)\nHb  : prime 2\nHevenprime  : forall p : Z, prime p -> Z.Even p -> p = 2\nHap  : 2 <= a\nHamp  : 2 <= a - 2\nHbp  : 2 <= 2\nHagt  : 2 < a\nHsumgt  : 2 < a + 2\nHaodd  : Z.Odd a\nHbeven  : Z.Even 2\nHsumodd  : Z.Odd (a + 2)\nH1  : a mod 3 = 1\nHdiv1  : (3 | a - 1)\nHdiv3  : (3 | 3)\n|-(3 | 2)"
  ],
  "success": false,
  "tactic": "- exact Hdiv1.",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Hevenprime : forall p : Z, prime p -> Z.Even p -> p = 2).",
    "{ intros p Hp He.",
    "destruct He as [k Hk].",
    "assert (Hd : (2 | p)).",
    "{ exists k.",
    "lia.",
    "}",
    "assert (Hcases : 2 = -1 \\/ 2 = 1 \\/ 2 = p \\/ 2 = - p).",
    "{ exact (prime_divisors p Hp 2 Hd).",
    "}",
    "destruct Hcases as [Hneg | Hrest].",
    "- lia.",
    "- destruct Hrest as [Hone | Hrest].",
    "+ lia.",
    "+ destruct Hrest as [Hpos | Hminus].",
    "* symmetry.",
    "exact Hpos.",
    "* assert (Hp2 : 2 <= p).",
    "{ apply prime_ge_2.",
    "exact Hp.",
    "}",
    "lia.",
    "}",
    "assert (Hap : 2 <= a).",
    "{ apply prime_ge_2.",
    "exact Ha.",
    "}",
    "assert (Hbp : 2 <= b).",
    "{ apply prime_ge_2.",
    "exact Hb.",
    "}",
    "assert (Hamp : 2 <= a - b).",
    "{ apply prime_ge_2.",
    "exact Habm.",
    "}",
    "assert (Hagt : 2 < a) by lia.",
    "assert (Hsumgt : 2 < a + b) by lia.",
    "assert (Haodd : Z.Odd a).",
    "{ destruct (Z.Even_or_Odd a) as [He | Ho].",
    "- assert (Ha2 : a = 2).",
    "{ apply Hevenprime with (p := a).",
    "- exact Ha.",
    "- exact He.",
    "}",
    "lia.",
    "- exact Ho.",
    "}",
    "assert (Hsumodd : Z.Odd (a + b)).",
    "{ destruct (Z.Even_or_Odd (a + b)) as [He | Ho].",
    "- assert (Hsum2 : a + b = 2).",
    "{ apply Hevenprime with (p := a + b).",
    "- exact Hab.",
    "- exact He.",
    "}",
    "lia.",
    "- exact Ho.",
    "}",
    "assert (Hbeven : Z.Even b).",
    "{ destruct Haodd as [x Hx].",
    "destruct Hsumodd as [y Hy].",
    "exists (y - x).",
    "lia.",
    "}",
    "assert (Hb2 : b = 2).",
    "{ apply Hevenprime with (p := b).",
    "- exact Hb.",
    "- exact Hbeven.",
    "}",
    "subst b.",
    "assert (Hr : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2).",
    "{ pose proof (Z.mod_pos_bound a 3) as Hmod.",
    "lia.",
    "}",
    "assert (Ha_cases : a = 3 \\/ a - 2 = 3 \\/ a + 2 = 3).",
    "{ destruct Hr as [H0 | [H1 | H2]].",
    "- left.",
    "assert (Hdiv : (3 | a)).",
    "{ apply (Z.mod_divide a 3).",
    "- lia.",
    "- exact H0.",
    "}",
    "assert (Hcases : 3 = -1 \\/ 3 = 1 \\/ 3 = a \\/ 3 = - a).",
    "{ exact (prime_divisors a Ha 3 Hdiv).",
    "}",
    "destruct Hcases as [Hneg | Hrest].",
    "+ lia.",
    "+ destruct Hrest as [Hone | Hrest].",
    "* lia.",
    "* destruct Hrest as [Hpos | Hminus].",
    "-- symmetry.",
    "exact Hpos.",
    "-- lia.",
    "- right; right.",
    "assert (Hdiv1 : (3 | a - 1)).",
    "{ apply Zmod_divide_minus.",
    "- lia.",
    "- exact H1.",
    "}",
    "assert (Hdiv3 : (3 | 3)).",
    "{ exists 1.",
    "lia.",
    "}",
    "replace (a + 2) with ((a - 1) + 3) by lia.",
    "assert (Hdiv : (3 | a + 2)).",
    "{ apply Z.divide_add_r."
  ]
}
```

### amc12b_2002_p11__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__D-level0__gpt-5.6-terra__seed0`. Solved; $0.28586660; 16 completions; 11.597 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'other': 1, 'syntax-error': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")
```

### amc12b_2002_p11__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__E-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03508750; 22 completions; 6.089 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 3, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "no-witness",
  "elapsed": 0.007893982343375683,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b  : Z\nHa  : prime a\nHb  : prime b\nHab  : prime (a + b)\nHabm  : prime (a - b)\np  : Z\nHp  : prime p\nHe  : Zeven p\nk  : Z\nHk  : p = 2 * k\nHd  : (2 | p)\n|-p = 2"
  ],
  "success": false,
  "tactic": "destruct (prime_divisors p Hp 2 Hd) as [Hneg|[Hone|[Heq|Hopp]]]; lia.",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Hep : forall p : Z, prime p -> Zeven p -> p = 2).",
    "{ intros p Hp He.",
    "destruct (Zeven_ex p He) as [k Hk].",
    "assert (Hd : (2 | p)).",
    "{ exists k. lia. }"
  ]
}
```

### amc12b_2002_p11__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/amc12b_2002_p11__E-level0__gpt-5.6-terra__seed0`. Unsolved; $0.36619260; 30 completions; 70.568 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 1, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "focus-error",
  "elapsed": 60.0349454022944,
  "error": "(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 1 < 17\n|-rel_prime 1 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 2 < 17\n|-rel_prime 2 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 3 < 17\n|-rel_prime 3 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 4 < 17\n|-rel_prime 4 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 5 < 17\n|-rel_prime 5 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 6 < 17\n|-rel_prime 6 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 7 < 17\n|-rel_prime 7 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 8 < 17\n|-rel_prime 8 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 9 < 17\n|-rel_prime 9 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 10 < 17\n|-rel_prime 10 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 11 < 17\n|-rel_prime 11 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 12 < 17\n|-rel_prime 12 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 13 < 17\n|-rel_prime 13 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 14 < 17\n|-rel_prime 14 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 15 < 17\n|-rel_prime 15 17",
    "a  : Z\nha  : prime a\nhd  : prime (a - 2)\nhab  : prime (a + 2)\nhb  : prime 2\nha2  : 2 <= a\nhd2  : 2 <= a - 2\nhb2  : 2 <= 2\nha4  : 4 <= a\nx  : Z\nhx  : a = 2 * x + 1\ny  : Z\nhmod  : 0 <= a mod 3 < 3\nhdivmod  : a = 3 * (a / 3) + a mod 3\nh2  : a mod 3 = 2\nhdiv3  : (3 | a - 2)\nheq3  : 3 = a - 2\nhn  : 1 <= 16 < 17\n|-rel_prime 16 17"
  ],
  "success": false,
  "tactic": "- apply bezout_rel_prime.",
  "verified_prefix": [
    "intros a b ha hb hab hd.",
    "assert (ha2 : 2 <= a) by exact (prime_ge_2 a ha).",
    "assert (hb2 : 2 <= b) by exact (prime_ge_2 b hb).",
    "assert (hd2 : 2 <= a - b) by exact (prime_ge_2 (a - b) hd).",
    "assert (ha4 : 4 <= a) by lia.",
    "destruct (Z.Even_or_Odd a) as [hea|hoa].",
    "- destruct hea as [x hx].",
    "assert (hdiv : (2 | a)). { exists x. lia. }",
    "assert (heq : 2 = a) by apply (prime_div_prime 2 a prime_2 ha hdiv).",
    "lia.",
    "- destruct hoa as [x hx].",
    "destruct (Z.Even_or_Odd b) as [heb|hob].",
    "+ destruct heb as [y hy].",
    "assert (hdiv : (2 | b)). { exists y. lia. }",
    "assert (heq : 2 = b) by apply (prime_div_prime 2 b prime_2 hb hdiv).",
    "clear hy hdiv.",
    "subst b.",
    "assert (hmod : 0 <= a mod 3 < 3).",
    "{ apply Z.mod_pos_bound. lia. }",
    "assert (hdivmod : a = 3 * (a / 3) + a mod 3).",
    "{ apply Z.div_mod. lia. }",
    "assert (hcases : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2) by lia.",
    "destruct hcases as [h0|[h1|h2]].",
    "* assert (hdiv3 : (3 | a)). { exists (a / 3). lia. }",
    "assert (heq3 : 3 = a) by apply (prime_div_prime 3 a prime_3 ha hdiv3).",
    "lia.",
    "* assert (hdiv3 : (3 | a + 2)). { exists (a / 3 + 1). lia. }",
    "assert (heq3 : 3 = a + 2) by apply (prime_div_prime 3 (a + 2) prime_3 hab hdiv3).",
    "lia.",
    "* assert (hdiv3 : (3 | a - 2)). { exists (a / 3). lia. }",
    "assert (heq3 : 3 = a - 2) by apply (prime_div_prime 3 (a - 2) prime_3 hd hdiv3).",
    "assert (hp : prime 17).",
    "{ apply (prime_intro 17).",
    "- lia.",
    "- intros n hn.",
    "assert (hc : n = 1 \\/ n = 2 \\/ n = 3 \\/ n = 4 \\/ n = 5 \\/ n = 6 \\/ n = 7 \\/ n = 8 \\/ n = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16) by lia.",
    "repeat (destruct hc as [->|hc]); try subst n."
  ]
}
```

### amc12b_2002_p11__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12b_2002_p11__E-level1__gpt-5.6-luna__seed0`. Unsolved; $0.12018572; 37 completions; 52.677 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-such-goal': 1, 'no-witness': 3, 'other': 1, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'syntax-error': 2, 'type-mismatch': 3, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 37,
  "category": "syntax-error",
  "elapsed": 4.039511179551482,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nHa  : prime a\nHabm  : prime (a - 2)\nHab  : prime (a + 2)\nHb  : prime 2\nHep  : forall p : Z, prime p -> Zeven p -> p = 2\nHodd_of_not_even  : forall z : Z, Z.even z = false -> Zodd z\nHsumodd  : Zodd (a + 2)\nHaodd  : Zodd a\nHbeven  : Zeven 2\nHr0  : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2\nn  : Z\nHn  : 1 <= n < 17\nHcases  : n = 1 \\/\nn = 2 \\/\nn = 3 \\/\nn = 4 \\/\nn = 5 \\/\nn = 6 \\/\nn = 7 \\/\nn = 8 \\/\nn = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16\n|-rel_prime n 17"
  ],
  "success": false,
  "tactic": "destruct Hcases as [->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->]]]]]]]]]]]]]]]]]]]]]]]]]].",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Hep : forall p : Z, prime p -> Zeven p -> p = 2).",
    "{ intros p Hp He.",
    "destruct (Zeven_ex p He) as [k Hk].",
    "assert (Hd : (2 | p)).",
    "{ exists k. lia. }",
    "destruct (prime_divisors p Hp 2 Hd) as [Hneg|[Hone|[Heq|Hopp]]].",
    "- lia.",
    "- lia.",
    "- lia.",
    "- pose proof (prime_ge_2 p Hp) as Hp2.",
    "lia.",
    "}",
    "assert (Hodd_of_not_even : forall z : Z, Z.even z = false -> Zodd z).",
    "{ intros z Hz.",
    "apply (Zodd_bool_iff z).",
    "destruct (Z.odd z) eqn:Ho.",
    "- reflexivity.",
    "- pose proof (Zeven.Zeven_odd_bool z) as H.",
    "rewrite Hz in H.",
    "rewrite Ho in H.",
    "discriminate.",
    "}",
    "assert (Hsumodd : Zodd (a + b)).",
    "{ destruct (Z.even (a + b)) eqn:Hs.",
    "- assert (Hes : Zeven (a + b)).",
    "{ apply (Zeven_bool_iff (a + b)); exact Hs. }",
    "assert (Hsum : a + b = 2).",
    "{ exact (Hep (a + b) Hab Hes). }",
    "pose proof (prime_ge_2 (a - b) Habm) as Hdiff.",
    "pose proof (prime_ge_2 b Hb) as Hb2.",
    "exfalso.",
    "lia.",
    "- apply Hodd_of_not_even.",
    "exact Hs.",
    "}",
    "assert (Haodd : Zodd a).",
    "{ destruct (Z.even a) eqn:Haev.",
    "- assert (Hea : Zeven a).",
    "{ apply (Zeven_bool_iff a); exact Haev. }",
    "assert (Ha2 : a = 2).",
    "{ exact (Hep a Ha Hea). }",
    "pose proof (prime_ge_2 (a - b) Habm) as Hdiff.",
    "pose proof (prime_ge_2 b Hb) as Hb2.",
    "exfalso.",
    "lia.",
    "- apply Hodd_of_not_even.",
    "exact Haev.",
    "}",
    "assert (Hbeven : Zeven b).",
    "{ destruct (Zodd_ex a Haodd) as [ka Hka].",
    "destruct (Zodd_ex (a + b) Hsumodd) as [ks Hks].",
    "assert (Hbform : exists m : Z, b = 2 * m).",
    "{ exists (ks - ka).",
    "lia.",
    "}",
    "destruct Hbform as [m Hm].",
    "rewrite Hm.",
    "apply Zeven_2p.",
    "}",
    "assert (Hb2 : b = 2).",
    "{ exact (Hep b Hb Hbeven). }",
    "subst b.",
    "assert (Hr0 : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2).",
    "{ pose proof (Z_mod_lt a 3 ltac:(lia)) as Hr.",
    "destruct (Z.eq_dec (a mod 3) 0) as [H0|H0].",
    "- left; exact H0.",
    "- destruct (Z.eq_dec (a mod 3) 1) as [H1|H1].",
    "+ right; left; exact H1.",
    "+ right; right; lia.",
    "}",
    "assert (H17 : prime 17).",
    "{ apply prime_intro.",
    "- lia.",
    "- intros n Hn.",
    "assert (Hcases : n = 1 \\/ n = 2 \\/ n = 3 \\/ n = 4 \\/ n = 5 \\/ n = 6 \\/ n = 7 \\/ n = 8 \\/ n = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16) by lia."
  ]
}
```

### amc12b_2002_p11__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12b_2002_p11__E-level1__gpt-5.6-terra__seed0`. Solved; $0.43951360; 32 completions; 75.807 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 1, 'not-convertible': 1, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

### amc12b_2002_p11__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/amc12b_2002_p11__E-level2__gpt-5.6-luna__seed0`. Unsolved; $0.12018572; 37 completions; 52.677 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `syntax-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-such-goal': 1, 'no-witness': 3, 'other': 1, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'syntax-error': 2, 'type-mismatch': 3, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 37,
  "category": "syntax-error",
  "elapsed": 4.039511179551482,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "a  : Z\nHa  : prime a\nHabm  : prime (a - 2)\nHab  : prime (a + 2)\nHb  : prime 2\nHep  : forall p : Z, prime p -> Zeven p -> p = 2\nHodd_of_not_even  : forall z : Z, Z.even z = false -> Zodd z\nHsumodd  : Zodd (a + 2)\nHaodd  : Zodd a\nHbeven  : Zeven 2\nHr0  : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2\nn  : Z\nHn  : 1 <= n < 17\nHcases  : n = 1 \\/\nn = 2 \\/\nn = 3 \\/\nn = 4 \\/\nn = 5 \\/\nn = 6 \\/\nn = 7 \\/\nn = 8 \\/\nn = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16\n|-rel_prime n 17"
  ],
  "success": false,
  "tactic": "destruct Hcases as [->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->|[->]]]]]]]]]]]]]]]]]]]]]]]]]].",
  "verified_prefix": [
    "intros a b Ha Hb Hab Habm.",
    "assert (Hep : forall p : Z, prime p -> Zeven p -> p = 2).",
    "{ intros p Hp He.",
    "destruct (Zeven_ex p He) as [k Hk].",
    "assert (Hd : (2 | p)).",
    "{ exists k. lia. }",
    "destruct (prime_divisors p Hp 2 Hd) as [Hneg|[Hone|[Heq|Hopp]]].",
    "- lia.",
    "- lia.",
    "- lia.",
    "- pose proof (prime_ge_2 p Hp) as Hp2.",
    "lia.",
    "}",
    "assert (Hodd_of_not_even : forall z : Z, Z.even z = false -> Zodd z).",
    "{ intros z Hz.",
    "apply (Zodd_bool_iff z).",
    "destruct (Z.odd z) eqn:Ho.",
    "- reflexivity.",
    "- pose proof (Zeven.Zeven_odd_bool z) as H.",
    "rewrite Hz in H.",
    "rewrite Ho in H.",
    "discriminate.",
    "}",
    "assert (Hsumodd : Zodd (a + b)).",
    "{ destruct (Z.even (a + b)) eqn:Hs.",
    "- assert (Hes : Zeven (a + b)).",
    "{ apply (Zeven_bool_iff (a + b)); exact Hs. }",
    "assert (Hsum : a + b = 2).",
    "{ exact (Hep (a + b) Hab Hes). }",
    "pose proof (prime_ge_2 (a - b) Habm) as Hdiff.",
    "pose proof (prime_ge_2 b Hb) as Hb2.",
    "exfalso.",
    "lia.",
    "- apply Hodd_of_not_even.",
    "exact Hs.",
    "}",
    "assert (Haodd : Zodd a).",
    "{ destruct (Z.even a) eqn:Haev.",
    "- assert (Hea : Zeven a).",
    "{ apply (Zeven_bool_iff a); exact Haev. }",
    "assert (Ha2 : a = 2).",
    "{ exact (Hep a Ha Hea). }",
    "pose proof (prime_ge_2 (a - b) Habm) as Hdiff.",
    "pose proof (prime_ge_2 b Hb) as Hb2.",
    "exfalso.",
    "lia.",
    "- apply Hodd_of_not_even.",
    "exact Haev.",
    "}",
    "assert (Hbeven : Zeven b).",
    "{ destruct (Zodd_ex a Haodd) as [ka Hka].",
    "destruct (Zodd_ex (a + b) Hsumodd) as [ks Hks].",
    "assert (Hbform : exists m : Z, b = 2 * m).",
    "{ exists (ks - ka).",
    "lia.",
    "}",
    "destruct Hbform as [m Hm].",
    "rewrite Hm.",
    "apply Zeven_2p.",
    "}",
    "assert (Hb2 : b = 2).",
    "{ exact (Hep b Hb Hbeven). }",
    "subst b.",
    "assert (Hr0 : a mod 3 = 0 \\/ a mod 3 = 1 \\/ a mod 3 = 2).",
    "{ pose proof (Z_mod_lt a 3 ltac:(lia)) as Hr.",
    "destruct (Z.eq_dec (a mod 3) 0) as [H0|H0].",
    "- left; exact H0.",
    "- destruct (Z.eq_dec (a mod 3) 1) as [H1|H1].",
    "+ right; left; exact H1.",
    "+ right; right; lia.",
    "}",
    "assert (H17 : prime 17).",
    "{ apply prime_intro.",
    "- lia.",
    "- intros n Hn.",
    "assert (Hcases : n = 1 \\/ n = 2 \\/ n = 3 \\/ n = 4 \\/ n = 5 \\/ n = 6 \\/ n = 7 \\/ n = 8 \\/ n = 9 \\/ n = 10 \\/ n = 11 \\/ n = 12 \\/ n = 13 \\/ n = 14 \\/ n = 15 \\/ n = 16) by lia."
  ]
}
```

### amc12b_2002_p11__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/amc12b_2002_p11__E-level1__gpt-5.6-terra__seed0`. Solved; $0.43951360; 32 completions; 75.807 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 1, 'not-convertible': 1, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

### imo_1967_p3__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__A-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04151174; 24 completions; 4.070 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 4, 'rewrite-no-match': 1, 'syntax-error': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "no-witness",
  "elapsed": 0.04181581176817417,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "k, m  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < 1\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : k + m + 1 > 1 /\\\n(forall n : nat, 1 < n < k + m + 1 -> ~ (exists k0 : nat, n * k0 = k + m + 1))\nHbound  : 1 + 1 < k + m + 1\nIH  : 0 < 0 ->\n0 + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c 0 * d = prod_from_1_to (fun i : nat => c (m + i) - c k) 0\nHx  : Nat.even (m + 1 - k) = false\nHy  : Nat.even (k + m + 2) = false\n|-(false || false)%bool = true"
  ],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hbound.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime.",
    "induction n as [|n IH].",
    "- lia.",
    "- simpl.",
    "destruct n as [|n].",
    "+ rewrite !Hc.",
    "assert (Heven : Nat.Even ((m + 1 - k) * (k + m + 2))).",
    "{ apply (proj1 (Nat.even_spec _)).",
    "rewrite Nat.even_mul.",
    "destruct (Nat.even (m + 1 - k)) eqn:Hx.",
    "- simpl.",
    "reflexivity.",
    "- destruct (Nat.even (k + m + 2)) eqn:Hy.",
    "+ simpl.",
    "reflexivity.",
    "+ simpl in Hx, Hy."
  ]
}
```

### imo_1967_p3__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__A-level0__gpt-5.6-terra__seed0`. Unsolved; $0.37344400; 29 completions; 1.720 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'other': 6, 'unify-failure': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "unknown-reference",
  "elapsed": 0.11635577771812677,
  "error": "(-32003, 'Coq: The variable d was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S n\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1\nHprime  : forall n0 : nat,\n1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1)\nHlt  : S n + 1 < k + m + 1\nHkm  : k <= m\n|-0 < n",
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S n\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1\nHprime  : forall n0 : nat,\n1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1)\nHlt  : S n + 1 < k + m + 1\nHkm  : k <= m\n|-n + 1 < k + m + 1",
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S n\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1\nHprime  : forall n0 : nat,\n1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1)\nHlt  : S n + 1 < k + m + 1\nHkm  : k <= m\nd  : nat\nHd  : prod_from_1_to (fun i : nat => c (m + i) - c k) n = d * prod_from_1_to c n\n|-Nat.divide (prod_from_1_to c n * c (S n))\n  (prod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k))"
  ],
  "success": false,
  "tactic": "exists ((m + S n - k) * (m + S n + k + 1) * d).",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime.",
    "destruct Hprime as [Hp Hprime].",
    "destruct (le_gt_dec k m) as [Hkm | Hmk].",
    "- exists (prod_from_1_to (fun i => c (m + i) - c k) n / prod_from_1_to c n).",
    "assert (Hdiv : Nat.divide (prod_from_1_to c n) (prod_from_1_to (fun i => c (m + i) - c k) n)).",
    "{ induction n as [|n IH].",
    "- simpl.",
    "exists 1.",
    "reflexivity.",
    "- simpl.",
    "destruct IH as [d Hd]."
  ]
}
```

### imo_1967_p3__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__B-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03814144; 23 completions; 2.493 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `ring-failure`; added goal views: 0. Error counts: `{'no-witness': 4, 'ring-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "ring-failure",
  "elapsed": 0.16962843481451273,
  "error": "(-32003, 'Coq: Tactic failure: not a valid ring equation.')",
  "outcome": "rejected",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn0  : 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHn  : S (S n) + 1 < k + m + 1\nd  : nat\nHd  : prod_from_1_to c n * c (S n) * d =\nprod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k)\n|-prod_from_1_to c n * c (S n) * c (S (S n)) * (d * (c (m + S (S n)) - c k)) =\nprod_from_1_to c n * c (S n) * d * (c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "ring.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hp Hn.",
    "unfold is_prime in Hp.",
    "destruct Hpos as [Hk [Hm Hn0]].",
    "induction n as [|n IH].",
    "- exists 1.",
    "reflexivity.",
    "- simpl.",
    "destruct n as [|n].",
    "+ rewrite Hc.",
    "rewrite Hc.",
    "rewrite Hc.",
    "destruct (Nat.Even_or_Odd (m + 1 - k)) as [[x Hx] | [x Hx]].",
    "* exists (x * (m + k + 2)).",
    "simpl.",
    "nia.",
    "* exists ((2 * x + 1) * (k + x + 1)).",
    "simpl.",
    "nia.",
    "+ specialize (IH ltac:(lia) ltac:(lia)).",
    "destruct IH as [d Hd].",
    "exists (d * (c (m + S (S n)) - c k)).",
    "simpl in Hd |- *.",
    "rewrite <- Hd."
  ]
}
```

### imo_1967_p3__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__B-level0__gpt-5.6-terra__seed0`. Unsolved; $0.35137140; 19 completions; 2.284 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 3, 'other': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "type-mismatch",
  "elapsed": 0.08406007569283247,
  "error": "(-32003, 'Coq: In environment\\nk, m, n : nat\\nc : nat -> nat\\nHk : 0 < k\\nHm : 0 < m\\nHn : 0 < n\\nHc : forall s : nat, c s = s * (s + 1)\\nHprime :\\n  k + m + 1 > 1 /\\\\\\n  (forall n : nat,\\n   1 < n < k + m + 1 -> ~ (exists k0 : nat, n * k0 = k + m + 1))\\nHlt : n + 1 < k + m + 1\\nHmk : m < k\\nf : nat -> nat\\nHf : f 1 = 0\\nThe term \"Hf\" has type \"f 1 = 0\" while it is expected to have type\\n \"f 1 + 0 = 0\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < n\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : n + 1 < k + m + 1\nHmk  : m < k\nf  : nat -> nat\nHf  : f 1 = 0\n|-prod_from_1_to f 1 = 0",
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < n\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : n + 1 < k + m + 1\nHmk  : m < k\nf  : nat -> nat\nr  : nat\nHf  : f 1 = 0\nIHr  : prod_from_1_to f (S r) = 0\n|-prod_from_1_to f (S (S r)) = 0"
  ],
  "success": false,
  "tactic": "- simpl. exact Hf.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime.",
    "destruct (le_lt_dec k m) as [Hkm | Hmk].",
    "2: assert (Hzero : forall (f : nat -> nat) r, f 1 = 0 -> prod_from_1_to f (S r) = 0).",
    "2: { intros f r Hf.",
    "induction r as [|r IHr]."
  ]
}
```

### imo_1967_p3__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__C-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03771684; 23 completions; 1.572 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 7, 'other': 5, 'subproof-incomplete': 3, 'syntax-error': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "incomplete-proof",
  "elapsed": 0.005969629622995853,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "idtac."
  ]
}
```

### imo_1967_p3__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__C-level0__gpt-5.6-terra__seed0`. Unsolved; $0.33968340; 35 completions; 2.000 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 6, 'no-witness': 3, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 35,
  "category": "incomplete-proof",
  "elapsed": 0.006510785780847073,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : is_prime (k + m + 1)\nHlt  : S (S n) + 1 < k + m + 1\nHeven  : forall x : nat, exists q : nat, c x = 2 * q\nIH  : exists d : nat,\n  prod_from_1_to c (S n) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\n|-exists d : nat,\n  prod_from_1_to c (S n) * c (S (S n)) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n) *\n  (c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "assert (Heven : forall x : nat, exists q : nat, c x = 2 * q).",
    "{ intro x.",
    "rewrite Hc.",
    "destruct (Nat.Even_or_Odd x) as [[q Hq] | [q Hq]].",
    "- exists (q * (x + 1)).",
    "rewrite Hq.",
    "ring.",
    "- exists ((2 * q + 1) * (q + 1)).",
    "rewrite Hq.",
    "ring.",
    "}",
    "induction n as [|n IH].",
    "- simpl.",
    "exists 1.",
    "reflexivity.",
    "- simpl.",
    "destruct n as [|n].",
    "+ simpl.",
    "destruct (Heven (m + 1)) as [u Hu].",
    "destruct (Heven k) as [v Hv].",
    "exists (u - v).",
    "rewrite Hu, Hv.",
    "rewrite Hc.",
    "simpl.",
    "lia.",
    "+ specialize (IH ltac:(lia) ltac:(lia))."
  ]
}
```

### imo_1967_p3__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/imo_1967_p3__C-level1__gpt-5.6-luna__seed0`. Unsolved; $0.06435790; 64 completions; 2.773 verifier seconds.

Terminal: `stopped`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 37, 'other': 5, 'subproof-incomplete': 3, 'syntax-error': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 63,
  "category": "incomplete-proof",
  "elapsed": 0.006011396646499634,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "idtac."
  ]
}
```

### imo_1967_p3__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/imo_1967_p3__C-level1__gpt-5.6-terra__seed0`. Unsolved; $0.67478440; 64 completions; 3.290 verifier seconds.

Terminal: `stopped`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 35, 'no-witness': 3, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 64,
  "category": "incomplete-proof",
  "elapsed": 0.006671058014035225,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : is_prime (k + m + 1)\nHlt  : S (S n) + 1 < k + m + 1\nHeven  : forall x : nat, exists q : nat, c x = 2 * q\nIH  : exists d : nat,\n  prod_from_1_to c (S n) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\n|-exists d : nat,\n  prod_from_1_to c (S n) * c (S (S n)) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n) *\n  (c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "assert (Heven : forall x : nat, exists q : nat, c x = 2 * q).",
    "{ intro x.",
    "rewrite Hc.",
    "destruct (Nat.Even_or_Odd x) as [[q Hq] | [q Hq]].",
    "- exists (q * (x + 1)).",
    "rewrite Hq.",
    "ring.",
    "- exists ((2 * q + 1) * (q + 1)).",
    "rewrite Hq.",
    "ring.",
    "}",
    "induction n as [|n IH].",
    "- simpl.",
    "exists 1.",
    "reflexivity.",
    "- simpl.",
    "destruct n as [|n].",
    "+ simpl.",
    "destruct (Heven (m + 1)) as [u Hu].",
    "destruct (Heven k) as [v Hv].",
    "exists (u - v).",
    "rewrite Hu, Hv.",
    "rewrite Hc.",
    "simpl.",
    "lia.",
    "+ specialize (IH ltac:(lia) ltac:(lia))."
  ]
}
```

### imo_1967_p3__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/imo_1967_p3__C-level2__gpt-5.6-luna__seed0`. Unsolved; $0.09482730; 91 completions; 3.807 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 48, 'other': 5, 'subproof-incomplete': 3, 'syntax-error': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 89,
  "category": "incomplete-proof",
  "elapsed": 0.005287093110382557,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "idtac."
  ]
}
```

### imo_1967_p3__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/imo_1967_p3__C-level2__gpt-5.6-terra__seed0`. Unsolved; $1.03245660; 86 completions; 4.428 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 57, 'no-witness': 3, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 86,
  "category": "incomplete-proof",
  "elapsed": 0.005835654214024544,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : is_prime (k + m + 1)\nHlt  : S (S n) + 1 < k + m + 1\nHeven  : forall x : nat, exists q : nat, c x = 2 * q\nIH  : exists d : nat,\n  prod_from_1_to c (S n) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\n|-exists d : nat,\n  prod_from_1_to c (S n) * c (S (S n)) * d =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) (S n) *\n  (c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "assert (Heven : forall x : nat, exists q : nat, c x = 2 * q).",
    "{ intro x.",
    "rewrite Hc.",
    "destruct (Nat.Even_or_Odd x) as [[q Hq] | [q Hq]].",
    "- exists (q * (x + 1)).",
    "rewrite Hq.",
    "ring.",
    "- exists ((2 * q + 1) * (q + 1)).",
    "rewrite Hq.",
    "ring.",
    "}",
    "induction n as [|n IH].",
    "- simpl.",
    "exists 1.",
    "reflexivity.",
    "- simpl.",
    "destruct n as [|n].",
    "+ simpl.",
    "destruct (Heven (m + 1)) as [u Hu].",
    "destruct (Heven k) as [v Hv].",
    "exists (u - v).",
    "rewrite Hu, Hv.",
    "rewrite Hc.",
    "simpl.",
    "lia.",
    "+ specialize (IH ltac:(lia) ltac:(lia))."
  ]
}
```

### imo_1967_p3__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__D-level0__gpt-5.6-luna__seed0`. Unsolved; $0.02569222; 40 completions; 1.063 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 6, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: Syntax Error: Lexer: Unterminated comment')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 16,
  "category": "incomplete-proof",
  "elapsed": 0.005395741201937199,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": []
}
```

### imo_1967_p3__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__D-level0__gpt-5.6-terra__seed0`. Unsolved; $0.37781000; 25 completions; 1.537 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `other`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 2, 'other': 6}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "other",
  "elapsed": 0,
  "error": "Proof obligations may not be bypassed.",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "unsafe command",
  "verified_prefix": []
}
```

### imo_1967_p3__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__E-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03774490; 21 completions; 2.364 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 1, 'other': 1, 'rewrite-no-match': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "incomplete-proof",
  "elapsed": 0.14783434476703405,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHpos  : 0 < k /\\ 0 < m /\\ 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : S (S n) + 1 < k + m + 1\n|-0 < m /\\ 0 < S n",
    "k, m, n  : nat\nc  : nat -> nat\nHpos  : 0 < k /\\ 0 < m /\\ 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : S (S n) + 1 < k + m + 1\n|-S (n + 1) < k + m + 1",
    "k, m, n  : nat\nc  : nat -> nat\nHpos  : 0 < k /\\ 0 < m /\\ 0 < S (S n)\nHc  : forall s : nat, c s = s * (s + 1)\nHp  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : S (S n) + 1 < k + m + 1\nd  : nat\nHd  : prod_from_1_to c n * c (S n) * d =\nprod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k)\n|-exists d0 : nat,\n  prod_from_1_to c n * c (S n) * c (S (S n)) * d0 =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k) *\n  (c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hp Hlt.",
    "unfold is_prime in Hp.",
    "destruct n as [|n].",
    "- simpl.",
    "exists 1.",
    "simpl.",
    "lia.",
    "- induction n as [|n IH].",
    "+ simpl.",
    "rewrite (Hc 1), (Hc (m + 1)), (Hc k).",
    "assert (EA : Nat.Even ((m + 1) * (m + 2))).",
    "{ destruct (Nat.Even_Odd_dec (m + 1)) as [He | Ho].",
    "- apply Nat.Even_mul_l.",
    "exact He.",
    "- apply Nat.Even_mul_r.",
    "replace (m + 2) with (S (m + 1)) by lia.",
    "apply (Nat.Even_succ (m + 1)).",
    "exact Ho. }",
    "assert (EB : Nat.Even (k * (k + 1))).",
    "{ destruct (Nat.Even_Odd_dec k) as [He | Ho].",
    "- apply Nat.Even_mul_l.",
    "exact He.",
    "- apply Nat.Even_mul_r.",
    "replace (k + 1) with (S k) by lia.",
    "apply (Nat.Even_succ k).",
    "exact Ho. }",
    "destruct EA as [a Ha].",
    "destruct EB as [b Hb].",
    "destruct (le_gt_dec ((m + 1) * (m + 2)) (k * (k + 1))) as [Hab | Hba].",
    "* assert (Hz : (m + 1) * (m + 2) - k * (k + 1) = 0) by lia.",
    "replace (m + 1 + 1) with (m + 2) by lia.",
    "rewrite Hz.",
    "exists 0.",
    "simpl.",
    "lia.",
    "* exists (a - b).",
    "simpl.",
    "nia.",
    "+ simpl in IH |- *.",
    "destruct IH as [d Hd].",
    "eexists.",
    "nia."
  ]
}
```

### imo_1967_p3__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/imo_1967_p3__E-level0__gpt-5.6-terra__seed0`. Unsolved; $0.34299740; 24 completions; 2.056 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 3, 'other': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nk, m, n : nat\nc : nat -> nat\nHk : 0 < k\nHm : 0 < m\nHn : 0 < n\nHc : forall s : nat, c s = s * (s + 1)\nHprime : is_prime (k + m + 1)\nHlt : n + 1 < k + m + 1\nUnable to unify "?M1831 * (?M1829 / ?M1830) <= ?M1831 * ?M1829 / ?M1830" with\n "prod_from_1_to c n *\n  (prod_from_1_to (fun i : nat => c (m + i) - c k) n / prod_from_1_to c n) =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) n".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "incomplete-proof",
  "elapsed": 0.006109194830060005,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "k, m, n  : nat\nc  : nat -> nat\nHk  : 0 < k\nHm  : 0 < m\nHn  : 0 < n\nHc  : forall s : nat, c s = s * (s + 1)\nHprime  : k + m + 1 > 1 /\\\n(forall n0 : nat,\n 1 < n0 < k + m + 1 -> ~ (exists k0 : nat, n0 * k0 = k + m + 1))\nHlt  : n + 1 < k + m + 1\n|-exists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime."
  ]
}
```

### imo_1967_p3__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/imo_1967_p3__E-level1__gpt-5.6-luna__seed0`. Platform failure; $0.05478874; 31 completions; 3.496 verifier seconds.

Terminal: `platform_failure`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 6, 'no-witness': 1, 'other': 3, 'rewrite-no-match': 1, 'syntax-error': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "incomplete-proof",
  "elapsed": 0.006153806112706661,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "idtac."
  ]
}
```

Failure is retained at subsequent levels; no remote retry. See the immutable exception file and supervised-completion record.

### imo_1967_p3__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/imo_1967_p3__E-level1__gpt-5.6-terra__seed0`. Unsolved; $1.23410900; 57 completions; 15.974 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `rewrite-no-match`; added goal views: 0. Error counts: `{'incomplete-proof': 11, 'no-witness': 2, 'other': 4, 'rewrite-no-match': 1, 'type-mismatch': 3, 'unify-failure': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nk, m, n : nat\nc : nat -> nat\nHk : 0 < k\nHm : 0 < m\nHn : 0 < n\nHc : forall s : nat, c s = s * (s + 1)\nHprime : is_prime (k + m + 1)\nHlt : n + 1 < k + m + 1\nUnable to unify "?M1831 * (?M1829 / ?M1830) <= ?M1831 * ?M1829 / ?M1830" with\n "prod_from_1_to c n *\n  (prod_from_1_to (fun i : nat => c (m + i) - c k) n / prod_from_1_to c n) =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) n".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 57,
  "category": "rewrite-no-match",
  "elapsed": 9.911665670573711,
  "error": "(-32003, 'Coq: Found no subterm matching\\n\"prod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\" in the current goal.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\nc  : nat -> nat\nIH  : forall k0 m0 : nat,\n0 < k0 ->\n0 < m0 ->\n~ m0 < k0 ->\nk0 <= m0 ->\n(forall s : nat, c s = s * (s + 1)) ->\nexists d0 : nat,\n  prod_from_1_to c (S n) * d0 =\n  prod_from_1_to (fun i : nat => c (m0 + i) - c k0) (S n)\nk, m  : nat\nHk  : 0 < k\nHm  : 0 < m\nHmk  : ~ m < k\nHmk'  : k <= m\nHc  : forall s : nat, c s = s * (s + 1)\nd  : nat\nHd  : prod_from_1_to c (S n) * d =\nprod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\n|-prod_from_1_to c n * (S n * (S n + 1)) * (S (S n) * (S (S n) + 1)) *\n((m + S (S n) - k) * (m + S (S n) + k + 1) * d) =\nprod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k) *\n(c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "rewrite <- Hd.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime.",
    "assert (Hz : forall (f : nat -> nat) q, f 1 = 0 -> 0 < q -> prod_from_1_to f q = 0).",
    "{ intros f q Hf.",
    "induction q as [|q IH]; intro Hq.",
    "- lia.",
    "- destruct q as [|q].",
    "+ change (prod_from_1_to f 0 * f 1 = 0).",
    "simpl.",
    "now rewrite Hf.",
    "+ change (prod_from_1_to f (S q) * f (S (S q)) = 0).",
    "rewrite IH.",
    "* reflexivity.",
    "* lia.",
    "}",
    "destruct (lt_dec m k) as [Hmk | Hmk].",
    "- exists 0.",
    "rewrite Nat.mul_0_r.",
    "symmetry.",
    "apply Hz.",
    "+ rewrite Hc, Hc.",
    "apply Nat.sub_0_le.",
    "nia.",
    "+ exact Hn.",
    "- assert (Hmk' : k <= m) by lia.",
    "clear Hz Hprime Hlt Hn.",
    "revert k m Hk Hm Hmk Hmk' Hc.",
    "induction n as [|n IH]; intros k m Hk Hm Hmk Hmk' Hc.",
    "+ exists 1.",
    "reflexivity.",
    "+ destruct n as [|n].",
    "* assert (Heven : forall x : nat, exists t, x * (x + 1) = 2 * t).",
    "{ intro x.",
    "induction x as [|x IHx].",
    "- exists 0.",
    "reflexivity.",
    "- destruct IHx as [t Ht].",
    "exists (t + x + 1).",
    "nia.",
    "}",
    "destruct (Heven (m + 1)) as [u Hu].",
    "destruct (Heven k) as [v Hv].",
    "exists (u - v).",
    "cbn [prod_from_1_to].",
    "rewrite Hc, Hc, Hc.",
    "nia.",
    "* destruct (IH k m Hk Hm Hmk Hmk' Hc) as [d Hd].",
    "exists ((m + S (S n) - k) * (m + S (S n) + k + 1) * d).",
    "cbn [prod_from_1_to].",
    "rewrite Hc, Hc."
  ]
}
```

### imo_1967_p3__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/imo_1967_p3__E-level1__gpt-5.6-luna__seed0`. Platform failure; $0.05478874; 31 completions; 3.496 verifier seconds.

Terminal: `platform_failure`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 6, 'no-witness': 1, 'other': 3, 'rewrite-no-match': 1, 'syntax-error': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "incomplete-proof",
  "elapsed": 0.006153806112706661,
  "error": "(-32003, 'Coq:  (in proof imo_1967_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-forall (k m n : nat) (c : nat -> nat),\n0 < k /\\ 0 < m /\\ 0 < n ->\n(forall s : nat, c s = s * (s + 1)) ->\nis_prime (k + m + 1) ->\nn + 1 < k + m + 1 ->\nexists d : nat,\n  prod_from_1_to c n * d = prod_from_1_to (fun i : nat => c (m + i) - c k) n"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "idtac."
  ]
}
```

Failure is retained at subsequent levels; no remote retry. See the immutable exception file and supervised-completion record.

### imo_1967_p3__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/imo_1967_p3__E-level2__gpt-5.6-terra__seed0`. Unsolved; $1.23410900; 57 completions; 15.974 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `rewrite-no-match`; added goal views: 0. Error counts: `{'incomplete-proof': 11, 'no-witness': 2, 'other': 4, 'rewrite-no-match': 1, 'type-mismatch': 3, 'unify-failure': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nk, m, n : nat\nc : nat -> nat\nHk : 0 < k\nHm : 0 < m\nHn : 0 < n\nHc : forall s : nat, c s = s * (s + 1)\nHprime : is_prime (k + m + 1)\nHlt : n + 1 < k + m + 1\nUnable to unify "?M1831 * (?M1829 / ?M1830) <= ?M1831 * ?M1829 / ?M1830" with\n "prod_from_1_to c n *\n  (prod_from_1_to (fun i : nat => c (m + i) - c k) n / prod_from_1_to c n) =\n  prod_from_1_to (fun i : nat => c (m + i) - c k) n".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 57,
  "category": "rewrite-no-match",
  "elapsed": 9.911665670573711,
  "error": "(-32003, 'Coq: Found no subterm matching\\n\"prod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\" in the current goal.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\nc  : nat -> nat\nIH  : forall k0 m0 : nat,\n0 < k0 ->\n0 < m0 ->\n~ m0 < k0 ->\nk0 <= m0 ->\n(forall s : nat, c s = s * (s + 1)) ->\nexists d0 : nat,\n  prod_from_1_to c (S n) * d0 =\n  prod_from_1_to (fun i : nat => c (m0 + i) - c k0) (S n)\nk, m  : nat\nHk  : 0 < k\nHm  : 0 < m\nHmk  : ~ m < k\nHmk'  : k <= m\nHc  : forall s : nat, c s = s * (s + 1)\nd  : nat\nHd  : prod_from_1_to c (S n) * d =\nprod_from_1_to (fun i : nat => c (m + i) - c k) (S n)\n|-prod_from_1_to c n * (S n * (S n + 1)) * (S (S n) * (S (S n) + 1)) *\n((m + S (S n) - k) * (m + S (S n) + k + 1) * d) =\nprod_from_1_to (fun i : nat => c (m + i) - c k) n * (c (m + S n) - c k) *\n(c (m + S (S n)) - c k)"
  ],
  "success": false,
  "tactic": "rewrite <- Hd.",
  "verified_prefix": [
    "intros k m n c Hpos Hc Hprime Hlt.",
    "destruct Hpos as [Hk [Hm Hn]].",
    "unfold is_prime in Hprime.",
    "assert (Hz : forall (f : nat -> nat) q, f 1 = 0 -> 0 < q -> prod_from_1_to f q = 0).",
    "{ intros f q Hf.",
    "induction q as [|q IH]; intro Hq.",
    "- lia.",
    "- destruct q as [|q].",
    "+ change (prod_from_1_to f 0 * f 1 = 0).",
    "simpl.",
    "now rewrite Hf.",
    "+ change (prod_from_1_to f (S q) * f (S (S q)) = 0).",
    "rewrite IH.",
    "* reflexivity.",
    "* lia.",
    "}",
    "destruct (lt_dec m k) as [Hmk | Hmk].",
    "- exists 0.",
    "rewrite Nat.mul_0_r.",
    "symmetry.",
    "apply Hz.",
    "+ rewrite Hc, Hc.",
    "apply Nat.sub_0_le.",
    "nia.",
    "+ exact Hn.",
    "- assert (Hmk' : k <= m) by lia.",
    "clear Hz Hprime Hlt Hn.",
    "revert k m Hk Hm Hmk Hmk' Hc.",
    "induction n as [|n IH]; intros k m Hk Hm Hmk Hmk' Hc.",
    "+ exists 1.",
    "reflexivity.",
    "+ destruct n as [|n].",
    "* assert (Heven : forall x : nat, exists t, x * (x + 1) = 2 * t).",
    "{ intro x.",
    "induction x as [|x IHx].",
    "- exists 0.",
    "reflexivity.",
    "- destruct IHx as [t Ht].",
    "exists (t + x + 1).",
    "nia.",
    "}",
    "destruct (Heven (m + 1)) as [u Hu].",
    "destruct (Heven k) as [v Hv].",
    "exists (u - v).",
    "cbn [prod_from_1_to].",
    "rewrite Hc, Hc, Hc.",
    "nia.",
    "* destruct (IH k m Hk Hm Hmk Hmk' Hc) as [d Hd].",
    "exists ((m + S (S n) - k) * (m + S (S n) + k + 1) * d).",
    "cbn [prod_from_1_to].",
    "rewrite Hc, Hc."
  ]
}
```

### mathd_algebra_28__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__A-level0__gpt-5.6-luna__seed0`. Solved; $0.00149972; 3 completions; 1.062 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nx : R\nHf : f x = 2 * x ^ 2 + 5 * x + c\nHx : f x <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (8 * x + 10) 1%nat"\nwith "8 * x + 10".')
```

### mathd_algebra_28__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__A-level0__gpt-5.6-terra__seed0`. Solved; $0.01629180; 3 completions; 1.127 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The variable sq_nonneg was not found in the current environment.')
```

### mathd_algebra_28__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__B-level0__gpt-5.6-luna__seed0`. Solved; $0.00135360; 2 completions; 1.027 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__B-level0__gpt-5.6-terra__seed0`. Solved; $0.00546680; 1 completions; 0.606 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### mathd_algebra_28__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00548226; 6 completions; 1.125 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01436380; 3 completions; 1.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The variable sq_nonneg was not found in the current environment.')
```

### mathd_algebra_28__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00548226; 6 completions; 1.125 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01436380; 3 completions; 1.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The variable sq_nonneg was not found in the current environment.')
```

### mathd_algebra_28__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00548226; 6 completions; 1.125 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01436380; 3 completions; 1.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The variable sq_nonneg was not found in the current environment.')
```

### mathd_algebra_28__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__D-level0__gpt-5.6-luna__seed0`. Solved; $0.00331516; 4 completions; 1.033 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'syntax-error': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

### mathd_algebra_28__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__D-level0__gpt-5.6-terra__seed0`. Solved; $0.00333320; 1 completions; 0.668 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### mathd_algebra_28__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00146120; 2 completions; 0.403 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-terra__seed0`. Solved; $0.00580300; 1 completions; 0.638 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### mathd_algebra_28__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00146120; 2 completions; 0.403 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-terra__seed0`. Solved; $0.00580300; 1 completions; 0.638 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### mathd_algebra_28__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-luna__seed0`. Solved; $0.00146120; 2 completions; 0.403 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nc : R\nf : R -> R\nHf : forall x : R, f x = 2 * x ^ 2 + 5 * x + c\nx : R\nHx : 2 * x ^ 2 + 5 * x + c <= 0\nUnable to unify\n "(fix pow (r : R) (n : nat) {struct n} : R :=\n     match n with\n     | 0%nat => 1\n     | S n0 => r * pow r n0\n     end)\n    (4 * x + 5) 1%nat"\nwith "4 * x + 5".')
```

### mathd_algebra_28__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_algebra_28__E-level0__gpt-5.6-terra__seed0`. Solved; $0.00580300; 1 completions; 0.638 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### mathd_numbertheory_48__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__A-level0__gpt-5.6-luna__seed0`. Solved; $0.02098510; 22 completions; 1.692 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 4, 'subproof-incomplete': 1, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__A-level0__gpt-5.6-terra__seed0`. Solved; $0.01064100; 3 completions; 1.023 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__B-level0__gpt-5.6-luna__seed0`. Solved; $0.00564082; 7 completions; 1.135 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 4}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__B-level0__gpt-5.6-terra__seed0`. Solved; $0.05262920; 7 completions; 1.114 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00480776; 7 completions; 1.263 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01711300; 3 completions; 1.064 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00480776; 7 completions; 1.263 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01711300; 3 completions; 1.064 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-luna__seed0`. Solved; $0.00480776; 7 completions; 1.263 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__C-level0__gpt-5.6-terra__seed0`. Solved; $0.01711300; 3 completions; 1.064 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__D-level0__gpt-5.6-luna__seed0`. Solved; $0.00677902; 7 completions; 1.104 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3, 'not-convertible': 1, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__D-level0__gpt-5.6-terra__seed0`. Solved; $0.04590660; 6 completions; 0.225 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-luna__seed0`. Solved; $0.01266046; 12 completions; 1.506 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'incomplete-proof': 1, 'no-such-goal': 2, 'no-witness': 5, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-terra__seed0`. Solved; $0.04531320; 5 completions; 1.154 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-luna__seed0`. Solved; $0.01266046; 12 completions; 1.506 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'incomplete-proof': 1, 'no-such-goal': 2, 'no-witness': 5, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-terra__seed0`. Solved; $0.04531320; 5 completions; 1.154 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-luna__seed0`. Solved; $0.01266046; 12 completions; 1.506 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'incomplete-proof': 1, 'no-such-goal': 2, 'no-witness': 5, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_48__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_48__E-level0__gpt-5.6-terra__seed0`. Solved; $0.04531320; 5 completions; 1.154 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_629__A-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__A-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04193766; 19 completions; 135.361 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 1, 'not-convertible': 1, 'other': 1, 'prover-crash': 9, 'syntax-error': 2}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 4.2474344205111265,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 1\n|-18 <= m",
    "Hmlt  : 2 < 18\nHmpos  : 2 > 0\n|-1728 = 576 -> False",
    "Hmlt  : 3 < 18\nHmpos  : 3 > 0\n|-1728 = 1296 -> False",
    "Hmlt  : 4 < 18\nHmpos  : 4 > 0\n|-1728 = 2304 -> False",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 5\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 6\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 7\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 8\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 9\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 10\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 11\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 12\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 13\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 14\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 15\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 16\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHmlt  : m < 18\nHmcase  : m = 17\n|-18 <= m"
  ],
  "success": false,
  "tactic": "5: subst m; exfalso; revert Heq; compute.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ change (36 ^ 3 = 216 ^ 2).",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "assert (Hm18 : 18 <= m \\/ m < 18) by lia.",
    "destruct Hm18 as [Hm18 | Hmlt].",
    "+ exact Hm18.",
    "+ assert (Hmcase : m = 0 \\/ m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "repeat match goal with | H : _ \\/ _ |- _ => destruct H as [H | H] end.",
    "1: lia.",
    "2: subst m; exfalso; revert Heq; compute.",
    "3: subst m; exfalso; revert Heq; compute.",
    "4: subst m; exfalso; revert Heq; compute."
  ]
}
```

### mathd_numbertheory_629__A-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__A-level0__gpt-5.6-terra__seed0`. Unsolved; $0.38037080; 35 completions; 21.676 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 2, 'rewrite-no-match': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 33,
  "category": "prover-crash",
  "elapsed": 12.487286232411861,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "Ht  : 5 > 0\nHeq  : Nat.lcm 12 5 ^ 3 = (12 * 5) ^ 2\n|-18 <= 5",
    "t  : nat\nHt  : S (S (S (S (S (S t))))) > 0\nHeq  : Nat.lcm 12 (S (S (S (S (S (S t)))))) ^ 3 = (12 * S (S (S (S (S (S t)))))) ^ 2\n|-18 <= S (S (S (S (S (S t)))))"
  ],
  "success": false,
  "tactic": "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ assert (Hg : Nat.gcd 12 18 = 6) by reflexivity.",
    "assert (Hd : 18 / 6 = 3) by reflexivity.",
    "unfold Nat.lcm.",
    "rewrite Hg, Hd.",
    "assert (H1 : 12 * 3 = 6 * 6) by lia.",
    "assert (H2 : 12 * 18 = (6 * 6) * 6) by lia.",
    "rewrite H1, H2.",
    "rewrite (Nat.pow_succ_r' (6 * 6) 2).",
    "rewrite Nat.pow_2_r.",
    "rewrite Nat.pow_2_r.",
    "repeat rewrite Nat.mul_assoc.",
    "reflexivity.",
    "- intros t [Ht Heq].",
    "destruct t as [|t]; [lia|].",
    "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
    "destruct t as [|t].",
    "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
    "destruct t as [|t].",
    "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
    "destruct t as [|t].",
    "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
    "destruct t as [|t].",
    "all: try (exfalso; unfold Nat.lcm in Heq; cbn in Heq; discriminate).",
    "destruct t as [|t]."
  ]
}
```

### mathd_numbertheory_629__B-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__B-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03790338; 15 completions; 51.929 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `other`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 2, 'other': 1, 'prover-crash': 4, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 15,
  "category": "other",
  "elapsed": 13.38736329972744,
  "error": "(-32003, 'Coq: Not a discriminable equality.')",
  "outcome": "rejected",
  "remaining_goals": [
    "Hmpos  : 1 > 0\nHeq  : Nat.lcm 12 1 ^ 3 = (12 * 1) ^ 2\nHsmall  : 18 > 1\nHmle  : 1 <= 17\n|-18 <= 1",
    "Hmpos  : 2 > 0\nHeq  : Nat.lcm 12 2 ^ 3 = (12 * 2) ^ 2\nHsmall  : 18 > 2\nHmle  : 2 <= 17\n|-18 <= 2",
    "Hmpos  : 3 > 0\nHeq  : Nat.lcm 12 3 ^ 3 = (12 * 3) ^ 2\nHsmall  : 18 > 3\nHmle  : 3 <= 17\n|-18 <= 3",
    "Hmpos  : 4 > 0\nHeq  : Nat.lcm 12 4 ^ 3 = (12 * 4) ^ 2\nHsmall  : 18 > 4\nHmle  : 4 <= 17\n|-18 <= 4",
    "Hmpos  : 5 > 0\nHeq  : Nat.lcm 12 5 ^ 3 = (12 * 5) ^ 2\nHsmall  : 18 > 5\nHmle  : 5 <= 17\n|-18 <= 5",
    "Hmpos  : 6 > 0\nHeq  : Nat.lcm 12 6 ^ 3 = (12 * 6) ^ 2\nHsmall  : 18 > 6\nHmle  : 6 <= 17\n|-18 <= 6",
    "Hmpos  : 7 > 0\nHeq  : Nat.lcm 12 7 ^ 3 = (12 * 7) ^ 2\nHsmall  : 18 > 7\nHmle  : 7 <= 17\n|-18 <= 7",
    "Hmpos  : 8 > 0\nHeq  : Nat.lcm 12 8 ^ 3 = (12 * 8) ^ 2\nHsmall  : 18 > 8\nHmle  : 8 <= 17\n|-18 <= 8",
    "Hmpos  : 9 > 0\nHeq  : Nat.lcm 12 9 ^ 3 = (12 * 9) ^ 2\nHsmall  : 18 > 9\nHmle  : 9 <= 17\n|-18 <= 9",
    "Hmpos  : 10 > 0\nHeq  : Nat.lcm 12 10 ^ 3 = (12 * 10) ^ 2\nHsmall  : 18 > 10\nHmle  : 10 <= 17\n|-18 <= 10",
    "Hmpos  : 11 > 0\nHeq  : Nat.lcm 12 11 ^ 3 = (12 * 11) ^ 2\nHsmall  : 18 > 11\nHmle  : 11 <= 17\n|-18 <= 11",
    "Hmpos  : 12 > 0\nHeq  : Nat.lcm 12 12 ^ 3 = (12 * 12) ^ 2\nHsmall  : 18 > 12\nHmle  : 12 <= 17\n|-18 <= 12",
    "Hmpos  : 13 > 0\nHeq  : Nat.lcm 12 13 ^ 3 = (12 * 13) ^ 2\nHsmall  : 18 > 13\nHmle  : 13 <= 17\n|-18 <= 13",
    "Hmpos  : 14 > 0\nHeq  : Nat.lcm 12 14 ^ 3 = (12 * 14) ^ 2\nHsmall  : 18 > 14\nHmle  : 14 <= 17\n|-18 <= 14",
    "Hmpos  : 15 > 0\nHeq  : Nat.lcm 12 15 ^ 3 = (12 * 15) ^ 2\nHsmall  : 18 > 15\nHmle  : 15 <= 17\n|-18 <= 15",
    "m  : nat\nHmpos  : S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m))))))))))))))) > 0\nHeq  : Nat.lcm 12 (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m))))))))))))))))\n^ 3 =\n(12 * S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m)))))))))))))))) ^ 2\nHsmall  : 18 > S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m)))))))))))))))\nHmle  : S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m))))))))))))))) <= 17\n|-18 <= S (S (S (S (S (S (S (S (S (S (S (S (S (S (S (S m)))))))))))))))"
  ],
  "success": false,
  "tactic": "all: exfalso; discriminate Heq.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ replace (Nat.lcm 12 18) with 36 by reflexivity.",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "destruct (le_gt_dec 18 m) as [Hlarge|Hsmall].",
    "+ exact Hlarge.",
    "+ assert (Hmle : m <= 17) by lia.",
    "destruct m as [|m].",
    "* lia.",
    "* all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m].",
    "all: try destruct m as [|m]."
  ]
}
```

### mathd_numbertheory_629__B-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__B-level0__gpt-5.6-terra__seed0`. Unsolved; $0.35665980; 36 completions; 7.510 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 3, 'prover-crash': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 35,
  "category": "focus-error",
  "elapsed": 0.025817768648266792,
  "error": "(-32003, 'Coq: [Focus] Wrong bullet +: Current bullet * is not finished.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m  : nat\nHpos  : m > 0\nHeq  : 1 * 12 * (1 * 12 * (1 * 12 * 1)) =\n(m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + 0)))))))))))) *\n((m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + 0)))))))))))) *\n 1)\nHq  : Nat.lcm 12 m = 1 * 12\nHlt  : m < 18\nHmle  : m <= 17\nHm2  : m ^ 2 <= 17 ^ 2\nHqle  : 1 <= 2\n|-18 <= m",
    "m  : nat\nHpos  : m > 0\nq  : nat\nHeq  : S (S q) * 12 * (S (S q) * 12 * (S (S q) * 12 * 1)) =\n(m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + 0)))))))))))) *\n((m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + (m + 0)))))))))))) *\n 1)\nHq  : Nat.lcm 12 m = S (S q) * 12\nHlt  : m < 18\nHmle  : m <= 17\nHm2  : m ^ 2 <= 17 ^ 2\nHqle  : S (S q) <= 2\n|-18 <= m"
  ],
  "success": false,
  "tactic": "+ assert (Hm3 : m <= 3) by nia.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ replace (Nat.lcm 12 18) with (6 * Nat.lcm 2 3).",
    "2: { symmetry. exact (Nat.lcm_mul_mono_l 2 3 6). }",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hpos Heq].",
    "destruct (Nat.divide_lcm_l 12 m) as [q Hq].",
    "rewrite Hq in Heq.",
    "simpl in Heq.",
    "destruct (le_lt_dec 18 m) as [Hle | Hlt].",
    "+ exact Hle.",
    "+ assert (Hmle : m <= 17) by lia.",
    "assert (Hm2 : m ^ 2 <= 17 ^ 2) by (apply Nat.pow_le_mono_l; lia).",
    "assert (Hqle : q <= 2).",
    "{ destruct (le_lt_dec q 2) as [H | H].",
    "- exact H.",
    "- assert (Hqge : 3 <= q) by lia.",
    "assert (Hq3 : 3 ^ 3 <= q ^ 3) by (apply Nat.pow_le_mono_l; lia).",
    "nia. }",
    "destruct q as [|q].",
    "* exfalso.",
    "assert (HH : Nat.lcm 12 m = 0).",
    "{ rewrite Hq. reflexivity. }",
    "apply Nat.lcm_eq_0 in HH.",
    "lia.",
    "* destruct q as [|q]."
  ]
}
```

### mathd_numbertheory_629__C-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__C-level0__gpt-5.6-luna__seed0`. Solved; $0.03342018; 24 completions; 28.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3, 'prover-crash': 2, 'ring-failure': 1, 'syntax-error': 4, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

### mathd_numbertheory_629__C-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__C-level0__gpt-5.6-terra__seed0`. Unsolved; $0.40155120; 14 completions; 57.968 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 2, 'other': 1, 'prover-crash': 6, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 14,
  "category": "prover-crash",
  "elapsed": 1.5788684794679284,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "Hlt  : 5 < 18\nHm  : 60 * (60 * (60 * 60 ^ 0)) = 12 * 5 * (12 * 5 * (12 * 5) ^ 0)\nHmpos  : 5 > 0\n|-False"
  ],
  "success": false,
  "tactic": "simpl in Hm.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ reflexivity.",
    "- intros m [Hmpos Hm].",
    "destruct (le_lt_dec 18 m) as [Hle | Hlt].",
    "+ exact Hle.",
    "+ assert (Hcases : m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "destruct Hcases as [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | [-> | ->]]]]]]]]]]]]]]]].",
    "* exfalso.",
    "change (12 ^ 3 = (12 * 1) ^ 2) in Hm.",
    "repeat rewrite Nat.pow_succ_r' in Hm.",
    "simpl in Hm.",
    "discriminate Hm.",
    "* exfalso.",
    "change (12 ^ 3 = (12 * 2) ^ 2) in Hm.",
    "repeat rewrite Nat.pow_succ_r' in Hm.",
    "simpl in Hm.",
    "discriminate Hm.",
    "* exfalso.",
    "change (12 ^ 3 = (12 * 3) ^ 2) in Hm.",
    "repeat rewrite Nat.pow_succ_r' in Hm.",
    "simpl in Hm.",
    "discriminate Hm.",
    "* exfalso.",
    "change (12 ^ 3 = (12 * 4) ^ 2) in Hm.",
    "repeat rewrite Nat.pow_succ_r' in Hm.",
    "simpl in Hm.",
    "discriminate Hm.",
    "* exfalso.",
    "change (60 ^ 3 = (12 * 5) ^ 2) in Hm.",
    "repeat rewrite Nat.pow_succ_r' in Hm."
  ]
}
```

### mathd_numbertheory_629__C-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__C-level0__gpt-5.6-luna__seed0`. Solved; $0.03342018; 24 completions; 28.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3, 'prover-crash': 2, 'ring-failure': 1, 'syntax-error': 4, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

### mathd_numbertheory_629__C-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/mathd_numbertheory_629__C-level1__gpt-5.6-terra__seed0`. Solved; $0.52310360; 18 completions; 79.361 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 3, 'other': 1, 'prover-crash': 6, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

### mathd_numbertheory_629__C-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__C-level0__gpt-5.6-luna__seed0`. Solved; $0.03342018; 24 completions; 28.197 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 3, 'prover-crash': 2, 'ring-failure': 1, 'syntax-error': 4, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

### mathd_numbertheory_629__C-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/mathd_numbertheory_629__C-level1__gpt-5.6-terra__seed0`. Solved; $0.52310360; 18 completions; 79.361 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 3, 'other': 1, 'prover-crash': 6, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

### mathd_numbertheory_629__D-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__D-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03825402; 21 completions; 68.440 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'no-witness': 2, 'other': 1, 'prover-crash': 7, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "no-witness",
  "elapsed": 0.03934920113533735,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m  : nat\nHmpos  : m > 0\nHmeq  : (12 * (1 / Nat.gcd 12 1)) ^ 3 = (12 * 1) ^ 2\nH18  : 18 > m\nH  : m = 1\n|-False"
  ],
  "success": false,
  "tactic": "lia.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ replace (Nat.lcm 12 18) with 36.",
    "* reflexivity.",
    "* unfold Nat.lcm.",
    "reflexivity.",
    "- intros m [Hmpos Hmeq].",
    "destruct (le_gt_dec 18 m) as [H18|H18].",
    "+ exact H18.",
    "+ exfalso.",
    "assert (Hm_cases : m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "destruct Hm_cases as [H|Hm_cases].",
    "* rewrite H in Hmeq.",
    "cbv [Nat.lcm] in Hmeq."
  ]
}
```

### mathd_numbertheory_629__D-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__D-level0__gpt-5.6-terra__seed0`. Solved; $0.21294280; 27 completions; 2.390 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'prover-crash': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

### mathd_numbertheory_629__E-level0__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__E-level0__gpt-5.6-luna__seed0`. Unsolved; $0.04102496; 21 completions; 22.412 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'focus-error': 3, 'prover-crash': 9, 'syntax-error': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet +: Current bullet + is not finished.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "prover-crash",
  "elapsed": 0.1773384278640151,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [],
  "success": false,
  "tactic": "* subst m. vm_compute in Heq. discriminate.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ vm_compute.",
    "lia.",
    "+ change (36 ^ 3 = 216 ^ 2).",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "assert (Hcases : m < 18 \\/ 18 <= m) by lia.",
    "destruct Hcases as [Hlt | Hge].",
    "+ assert (Hfin : m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "destruct Hfin as [Hm1 | [Hm2 | [Hm3 | [Hm4 | [Hm5 | [Hm6 | [Hm7 | [Hm8 | [Hm9 | [Hm10 | [Hm11 | [Hm12 | [Hm13 | [Hm14 | [Hm15 | [Hm16 | Hm17]]]]]]]]]]]]]]]].",
    "* subst m. vm_compute in Heq. discriminate.",
    "* subst m. vm_compute in Heq. discriminate.",
    "* subst m. vm_compute in Heq. discriminate.",
    "* subst m. vm_compute in Heq. discriminate."
  ]
}
```

### mathd_numbertheory_629__E-level0__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/mechanisms/configs/mathd_numbertheory_629__E-level0__gpt-5.6-terra__seed0`. Unsolved; $0.35369280; 31 completions; 8.742 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-witness': 1, 'prover-crash': 2}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "prover-crash",
  "elapsed": 0.9946143291890621,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "Hmpos  : 5 > 0\nHeq  : Nat.lcm 12 5 ^ 3 = (12 * 5) ^ 2\n|-18 <= 5",
    "m  : nat\nHmpos  : S (S (S (S (S (S m))))) > 0\nHeq  : Nat.lcm 12 (S (S (S (S (S (S m)))))) ^ 3 = (12 * S (S (S (S (S (S m)))))) ^ 2\n|-18 <= S (S (S (S (S (S m)))))"
  ],
  "success": false,
  "tactic": "1: (assert (Hl : Nat.lcm 12 5 = 60) by reflexivity; rewrite Hl in Heq; change (216000 = 3600) in Heq; discriminate Heq).",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ lia.",
    "+ unfold Nat.lcm.",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "destruct m as [|m].",
    "1: lia.",
    "destruct m as [|m].",
    "1: (assert (Hl : Nat.lcm 12 1 = 12) by reflexivity; rewrite Hl in Heq; change (1728 = 144) in Heq; discriminate Heq).",
    "destruct m as [|m].",
    "1: (assert (Hl : Nat.lcm 12 2 = 12) by reflexivity; rewrite Hl in Heq; change (1728 = 576) in Heq; discriminate Heq).",
    "destruct m as [|m].",
    "1: (assert (Hl : Nat.lcm 12 3 = 12) by reflexivity; rewrite Hl in Heq; change (1728 = 1296) in Heq; discriminate Heq).",
    "destruct m as [|m].",
    "1: (assert (Hl : Nat.lcm 12 4 = 12) by reflexivity; rewrite Hl in Heq; change (1728 = 2304) in Heq; discriminate Heq).",
    "destruct m as [|m]."
  ]
}
```

### mathd_numbertheory_629__E-level1__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/mathd_numbertheory_629__E-level1__gpt-5.6-luna__seed0`. Unsolved; $0.12479016; 38 completions; 40.587 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'focus-error': 4, 'no-witness': 2, 'prover-crash': 16, 'subproof-incomplete': 1, 'syntax-error': 3, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet +: Current bullet + is not finished.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 38,
  "category": "no-witness",
  "elapsed": 2.7700053062289953,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm1  : m = 1\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm2  : m = 2\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm3  : m = 3\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm4  : m = 4\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm5  : m = 5\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm6  : m = 6\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm7  : m = 7\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm8  : m = 8\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm9  : m = 9\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm10  : m = 10\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm11  : m = 11\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm12  : m = 12\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm13  : m = 13\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm14  : m = 14\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm15  : m = 15\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm16  : m = 16\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm17  : m = 17\n|-18 <= m"
  ],
  "success": false,
  "tactic": "* subst m. lia.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ vm_compute.",
    "lia.",
    "+ change (36 ^ 3 = 216 ^ 2).",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "assert (Hcases : m < 18 \\/ 18 <= m) by lia.",
    "destruct Hcases as [Hlt | Hge].",
    "+ assert (Hfin : m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "destruct Hfin as [Hm1 | [Hm2 | [Hm3 | [Hm4 | [Hm5 | [Hm6 | [Hm7 | [Hm8 | [Hm9 | [Hm10 | [Hm11 | [Hm12 | [Hm13 | [Hm14 | [Hm15 | [Hm16 | Hm17]]]]]]]]]]]]]]]]."
  ]
}
```

### mathd_numbertheory_629__E-level1__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/mathd_numbertheory_629__E-level1__gpt-5.6-terra__seed0`. Solved; $0.71707920; 57 completions; 37.536 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'incomplete-proof': 1, 'no-witness': 1, 'prover-crash': 2, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### mathd_numbertheory_629__E-level2__gpt-5.6-luna__seed0

Source: `experiments/output/ace_capacity_20260912/headroom2/configs/mathd_numbertheory_629__E-level2__gpt-5.6-luna__seed0`. Unsolved; $0.12479016; 38 completions; 40.587 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'focus-error': 4, 'no-witness': 2, 'prover-crash': 16, 'subproof-incomplete': 1, 'syntax-error': 3, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet +: Current bullet + is not finished.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 38,
  "category": "no-witness",
  "elapsed": 2.7700053062289953,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm1  : m = 1\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm2  : m = 2\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm3  : m = 3\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm4  : m = 4\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm5  : m = 5\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm6  : m = 6\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm7  : m = 7\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm8  : m = 8\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm9  : m = 9\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm10  : m = 10\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm11  : m = 11\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm12  : m = 12\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm13  : m = 13\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm14  : m = 14\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm15  : m = 15\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm16  : m = 16\n|-18 <= m",
    "m  : nat\nHmpos  : m > 0\nHeq  : Nat.lcm 12 m ^ 3 = (12 * m) ^ 2\nHlt  : m < 18\nHm17  : m = 17\n|-18 <= m"
  ],
  "success": false,
  "tactic": "* subst m. lia.",
  "verified_prefix": [
    "unfold Least.",
    "split.",
    "- split.",
    "+ vm_compute.",
    "lia.",
    "+ change (36 ^ 3 = 216 ^ 2).",
    "reflexivity.",
    "- intros m Hm.",
    "destruct Hm as [Hmpos Heq].",
    "assert (Hcases : m < 18 \\/ 18 <= m) by lia.",
    "destruct Hcases as [Hlt | Hge].",
    "+ assert (Hfin : m = 1 \\/ m = 2 \\/ m = 3 \\/ m = 4 \\/ m = 5 \\/ m = 6 \\/ m = 7 \\/ m = 8 \\/ m = 9 \\/ m = 10 \\/ m = 11 \\/ m = 12 \\/ m = 13 \\/ m = 14 \\/ m = 15 \\/ m = 16 \\/ m = 17) by lia.",
    "destruct Hfin as [Hm1 | [Hm2 | [Hm3 | [Hm4 | [Hm5 | [Hm6 | [Hm7 | [Hm8 | [Hm9 | [Hm10 | [Hm11 | [Hm12 | [Hm13 | [Hm14 | [Hm15 | [Hm16 | Hm17]]]]]]]]]]]]]]]]."
  ]
}
```

### mathd_numbertheory_629__E-level2__gpt-5.6-terra__seed0

Source: `experiments/output/ace_capacity_20260912/headroom1/configs/mathd_numbertheory_629__E-level1__gpt-5.6-terra__seed0`. Solved; $0.71707920; 57 completions; 37.536 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 1. Error counts: `{'incomplete-proof': 1, 'no-witness': 1, 'prover-crash': 2, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```


## Validation failures and discordances

### gpt-5.6-luna/luna/aime_1984_p7

Source: `experiments/output/ace_polish_validation/configs/aime_1984_p7__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.02100072; 11 completions; 3.235 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 2, 'syntax-error': 3}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### gpt-5.6-luna/luna/aime_1991_p6

Source: `experiments/output/ace_polish_validation/configs/aime_1991_p6__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03469452; 13 completions; 36.317 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'other': 1, 'subproof-incomplete': 1, 'unknown-reference': 1}`.

First error:

```text
Proof obligations may not be bypassed.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 13,
  "category": "no-applicable-tactic",
  "elapsed": 9.471684341784567,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nHr  : (0 + Int_part (r + IZR (Z.of_nat 19) / 100) +\n Int_part (r + IZR (Z.of_nat 20) / 100) +\n Int_part (r + IZR (Z.of_nat 21) / 100) +\n Int_part (r + IZR (Z.of_nat 22) / 100) +\n Int_part (r + IZR (Z.of_nat 23) / 100) +\n Int_part (r + IZR (Z.of_nat 24) / 100) +\n Int_part (r + IZR (Z.of_nat 25) / 100) +\n Int_part (r + IZR (Z.of_nat 26) / 100) +\n Int_part (r + IZR (Z.of_nat 27) / 100) +\n Int_part (r + IZR (Z.of_nat 28) / 100) +\n Int_part (r + IZR (Z.of_nat 29) / 100) +\n Int_part (r + IZR (Z.of_nat 30) / 100) +\n Int_part (r + IZR (Z.of_nat 31) / 100) +\n Int_part (r + IZR (Z.of_nat 32) / 100) +\n Int_part (r + IZR (Z.of_nat 33) / 100) +\n Int_part (r + IZR (Z.of_nat 34) / 100) +\n Int_part (r + IZR (Z.of_nat 35) / 100) +\n Int_part (r + IZR (Z.of_nat 36) / 100) +\n Int_part (r + IZR (Z.of_nat 37) / 100) +\n Int_part (r + IZR (Z.of_nat 38) / 100) +\n Int_part (r + IZR (Z.of_nat 39) / 100) +\n Int_part (r + IZR (Z.of_nat 40) / 100) +\n Int_part (r + IZR (Z.of_nat 41) / 100) +\n Int_part (r + IZR (Z.of_nat 42) / 100) +\n Int_part (r + IZR (Z.of_nat 43) / 100) +\n Int_part (r + IZR (Z.of_nat 44) / 100) +\n Int_part (r + IZR (Z.of_nat 45) / 100) +\n Int_part (r + IZR (Z.of_nat 46) / 100) +\n Int_part (r + IZR (Z.of_nat 47) / 100) +\n Int_part (r + IZR (Z.of_nat 48) / 100) +\n Int_part (r + IZR (Z.of_nat 49) / 100) +\n Int_part (r + IZR (Z.of_nat 50) / 100) +\n Int_part (r + IZR (Z.of_nat 51) / 100) +\n Int_part (r + IZR (Z.of_nat 52) / 100) +\n Int_part (r + IZR (Z.of_nat 53) / 100) +\n Int_part (r + IZR (Z.of_nat 54) / 100) +\n Int_part (r + IZR (Z.of_nat 55) / 100) +\n Int_part (r + IZR (Z.of_nat 56) / 100) +\n Int_part (r + IZR (Z.of_nat 57) / 100) +\n Int_part (r + IZR (Z.of_nat 58) / 100) +\n Int_part (r + IZR (Z.of_nat 59) / 100) +\n Int_part (r + IZR (Z.of_nat 60) / 100) +\n Int_part (r + IZR (Z.of_nat 61) / 100) +\n Int_part (r + IZR (Z.of_nat 62) / 100) +\n Int_part (r + IZR (Z.of_nat 63) / 100) +\n Int_part (r + IZR (Z.of_nat 64) / 100) +\n Int_part (r + IZR (Z.of_nat 65) / 100) +\n Int_part (r + IZR (Z.of_nat 66) / 100) +\n Int_part (r + IZR (Z.of_nat 67) / 100) +\n Int_part (r + IZR (Z.of_nat 68) / 100) +\n Int_part (r + IZR (Z.of_nat 69) / 100) +\n Int_part (r + IZR (Z.of_nat 70) / 100) +\n Int_part (r + IZR (Z.of_nat 71) / 100) +\n Int_part (r + IZR (Z.of_nat 72) / 100) +\n Int_part (r + IZR (Z.of_nat 73) / 100) +\n Int_part (r + IZR (Z.of_nat 74) / 100) +\n Int_part (r + IZR (Z.of_nat 75) / 100) +\n Int_part (r + IZR (Z.of_nat 76) / 100) +\n Int_part (r + IZR (Z.of_nat 77) / 100) +\n Int_part (r + IZR (Z.of_nat 78) / 100) +\n Int_part (r + IZR (Z.of_nat 79) / 100) +\n Int_part (r + IZR (Z.of_nat 80) / 100) +\n Int_part (r + IZR (Z.of_nat 81) / 100) +\n Int_part (r + IZR (Z.of_nat 82) / 100) +\n Int_part (r + IZR (Z.of_nat 83) / 100) +\n Int_part (r + IZR (Z.of_nat 84) / 100) +\n Int_part (r + IZR (Z.of_nat 85) / 100) +\n Int_part (r + IZR (Z.of_nat 86) / 100) +\n Int_part (r + IZR (Z.of_nat 87) / 100) +\n Int_part (r + IZR (Z.of_nat 88) / 100) +\n Int_part (r + IZR (Z.of_nat 89) / 100) +\n Int_part (r + IZR (Z.of_nat 90) / 100) +\n Int_part (r + IZR (Z.of_nat 91) / 100))%Z =\n546%Z\nHfloor  : forall y0 : R, IZR (Int_part y0) <= y0 < IZR (Int_part y0) + 1\nx, y  : R\nHxy  : 0 <= y - x < 1\nHx0  : IZR (Int_part x) <= x\nHx1  : x < IZR (Int_part x) + 1\nHy0  : IZR (Int_part y) <= y\nHy1  : y < IZR (Int_part y) + 1\n|-IZR (Int_part x) <= IZR (Int_part y)"
  ],
  "success": false,
  "tactic": "lra.",
  "verified_prefix": [
    "intros r Hr.",
    "unfold range_sum in Hr.",
    "cbn [seq map fold_left] in Hr.",
    "assert (Hfloor : forall y : R, IZR (Int_part y) <= y /\\ y < IZR (Int_part y) + 1).",
    "{ intro y.",
    "unfold Int_part.",
    "pose proof (archimed y) as H.",
    "split.",
    "- rewrite minus_IZR.",
    "lra.",
    "- rewrite minus_IZR.",
    "lra.",
    "}",
    "assert (Hstep : forall x y : R, 0 <= y - x < 1 -> (Int_part x <= Int_part y)%Z /\\ (Int_part y <= Int_part x + 1)%Z).",
    "{ intros x y Hxy.",
    "pose proof (Hfloor x) as Hx.",
    "pose proof (Hfloor y) as Hy.",
    "destruct Hx as [Hx0 Hx1].",
    "destruct Hy as [Hy0 Hy1].",
    "split.",
    "- apply le_IZR."
  ]
}
```

### gpt-5.6-luna/luna/aime_1991_p9

Source: `experiments/output/ace_polish_validation/configs/aime_1991_p9__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.03565270; 23 completions; 1.810 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 2, 'no-applicable-tactic': 2, 'ring-failure': 1, 'unify-failure': 3, 'unknown-reference': 3}`.

First error:

```text
(-32003, 'Coq: In environment\nx : R\nHc : cos x <> 0\nHs : sin x <> 0\nH : 1 / cos x + sin x / cos x = 22 / 7\nUnable to unify "?M1823 * / ?M1823 = 1" with "cos x * (1 / cos x) = 1".')
```

### gpt-5.6-luna/luna/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_polish_validation/configs/algebra_others_exirrpowirrrat__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03667356; 32 completions; 3.189 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'no-witness': 1, 'other': 1, 'type-mismatch': 4}`.

First error:

```text
(-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nThe term "0" has type "nat" while it is expected to have type "R".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 32,
  "category": "no-witness",
  "elapsed": 0.033514388371258974,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHs  : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\n|-False",
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\n|-IZR q <> 0%R"
  ],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "assert (Hirr : irrational (sqrt (2 : R))).",
    "{ unfold irrational.",
    "intros [p [q [Hq Heq]]].",
    "assert (HqR : IZR q <> 0%R).",
    "{ intro HqR.",
    "apply Hq.",
    "apply eq_IZR.",
    "exact HqR.",
    "}",
    "assert (Hs : Rmult (sqrt (2 : R)) (sqrt (2 : R)) = (2 : R)).",
    "{ apply sqrt_sqrt.",
    "lra.",
    "}",
    "rewrite Heq in Hs.",
    "field_simplify in Hs."
  ]
}
```

### gpt-5.6-luna/luna/amc12_2001_p21

Source: `experiments/output/ace_polish_validation/configs/amc12_2001_p21__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03846148; 35 completions; 25.684 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'no-witness': 3, 'prover-crash': 2, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 35,
  "category": "no-witness",
  "elapsed": 0.9112524939700961,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "Hbc  : 20 + (20 + (20 + (20 + (20 + (20 + 0))))) + 6 + 20 = 146\nHprod  : 35520 =\nInit.Nat.of_uint\n  (Decimal.D4 (Decimal.D0 (Decimal.D3 (Decimal.D2 (Decimal.D0 Decimal.Nil)))))\nHab  : 6 * 74 + 74 + 6 = 524\nHcd  : 20 * 4 + 20 + 4 = 104\nHb6  : 6 <= 6\nHb  : 6 <= 20\n|-False"
  ],
  "success": false,
  "tactic": "assert (Hneq : (35520 <> 40320)%nat) by nia.",
  "verified_prefix": [
    "intros a b c d Hprod Hab Hbc Hcd.",
    "replace (fact 8) with 40320%nat in Hprod by reflexivity.",
    "assert (Hb : b <= 20) by nia.",
    "assert (Hb6 : 6 <= b) by nia.",
    "destruct (eq_nat_dec b 6) as [HbEq|HbNe].",
    "- subst b.",
    "simpl in Hbc, Hab, Hcd, Hprod.",
    "assert (Hc : c = 20) by nia.",
    "replace (a * 6) with (6 * a) in Hab by nia.",
    "assert (Ha : a = 74) by nia.",
    "subst c.",
    "assert (Hd : d = 4) by nia.",
    "subst d.",
    "subst a.",
    "simpl in Hprod.",
    "exfalso."
  ]
}
```

### gpt-5.6-luna/luna/amc12a_2008_p4

Source: `experiments/output/ace_polish_validation/configs/amc12a_2008_p4__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.00913230; 10 completions; 15.997 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-matching-clause': 1, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference Nat.succ_eq_add_one was not found in the current environment.')
```

### gpt-5.6-luna/luna/amc12a_2019_p21

Source: `experiments/output/ace_polish_validation/configs/amc12a_2019_p21__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.04091564; 27 completions; 12.250 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 1, 'rewrite-no-match': 2, 'subproof-incomplete': 3, 'syntax-error': 1, 'unify-failure': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof amc12a_2019_p21): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "no-applicable-tactic",
  "elapsed": 4.075453962665051,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "\n|-forall z : C,\nz = (1 + Ci) / sqrt 2 ->\nfold_left Cplus (map (fun k : nat => z ^ k ^ 2) (seq 1 12)) 0 *\nfold_left Cplus (map (fun k : nat => 1 / z ^ k ^ 2) (seq 1 12)) 0 = 36"
  ],
  "success": false,
  "tactic": "lra.",
  "verified_prefix": []
}
```

### gpt-5.6-luna/luna/amc12a_2020_p21

Source: `experiments/output/ace_polish_validation/configs/amc12a_2020_p21__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03636630; 21 completions; 61.713 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 2, 'prover-crash': 3, 'syntax-error': 4}`.

First error:

```text
(-32003, "Coq: Syntax error: [term level 200] expected after '=>' (in [binder_constr]).")
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "incomplete-proof",
  "elapsed": 0.00594177795574069,
  "error": "(-32003, 'Coq:  (in proof amc12a_2020_p21): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-exists l : list nat,\n  NoDup l /\\\n  (forall n : nat, In n l <-> satisfies_condition n) /\\ length l = 48"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": []
}
```

### gpt-5.6-luna/luna/amc12b_2002_p3

Source: `experiments/output/ace_polish_validation/configs/amc12b_2002_p3__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.00569166; 5 completions; 6.612 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

### gpt-5.6-luna/luna/imo_1960_p2

Source: `experiments/output/ace_polish_validation/configs/imo_1960_p2__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.00632444; 6 completions; 1.204 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-matching-clause': 1, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: No matching clauses for match.')
```

### gpt-5.6-luna/luna/imo_1969_p2

Source: `experiments/output/ace_polish_validation/configs/imo_1969_p2__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03866376; 19 completions; 3.402 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 1, 'ring-failure': 2, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "focus-error",
  "elapsed": 0.052126584108918905,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x0 : R,\ny x0 = sum_f_R0 (fun i : nat => cos (a i + x0) / 2 ^ i) (Init.Nat.pred k)\nHm  : y m = 0\nHn  : y n = 0\nN  : nat\nC, D  : R\nHD  : forall x0 : R,\nsum_f_R0 (fun i : nat => cos (a i + x0) / 2 ^ i) N = C * cos x0 + D * sin x0\nx  : R\n|-0 < 2 ^ S N",
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x0 : R,\ny x0 = sum_f_R0 (fun i : nat => cos (a i + x0) / 2 ^ i) (Init.Nat.pred k)\nHm  : y m = 0\nHn  : y n = 0\nN  : nat\nC, D  : R\nHD  : forall x0 : R,\nsum_f_R0 (fun i : nat => cos (a i + x0) / 2 ^ i) N = C * cos x0 + D * sin x0\nx  : R\n|-positive"
  ],
  "success": false,
  "tactic": "}",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hm Hn.",
    "assert (Hrepr : forall N : nat, exists C D : R, forall x : R, sum_f_R0 (fun i => cos (a i + x) / 2 ^ i) N = C * cos x + D * sin x).",
    "{ intro N.",
    "induction N as [|N IH].",
    "- exists (cos (a 0%nat)).",
    "exists (- sin (a 0%nat)).",
    "intro x.",
    "simpl.",
    "rewrite cos_plus.",
    "lra.",
    "- destruct IH as [C [D HD]].",
    "exists (C + cos (a (S N)) / 2 ^ (S N)).",
    "exists (D - sin (a (S N)) / 2 ^ (S N)).",
    "intro x.",
    "rewrite tech5.",
    "rewrite HD.",
    "rewrite cos_plus.",
    "assert (Hp : 2 ^ (S N) <> 0).",
    "{ assert (Hpos : 0 < (2 : R) ^ (S N)).",
    "{ apply pow_pos.",
    "lra."
  ]
}
```

### gpt-5.6-luna/luna/imo_1984_p6

Source: `experiments/output/ace_polish_validation/configs/imo_1984_p6__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03317128; 20 completions; 251.236 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'already-used': 2, 'incomplete-proof': 1, 'no-such-goal': 2, 'prover-crash': 2, 'subproof-incomplete': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 60.0919257462956,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "- nia.",
  "verified_prefix": [
    "destruct H0 as [Ha [Hb [Hc Hd]]].",
    "destruct H1 as [Oa [Ob [Oc Od]]].",
    "destruct H2 as [Hab [Hbc Hcd]].",
    "destruct Oa as [xa Hxa].",
    "destruct Ob as [xb Hxb].",
    "destruct Oc as [xc Hxc].",
    "destruct Od as [xd Hxd].",
    "destruct k as [|k].",
    "- simpl in H4.",
    "nia."
  ]
}
```

### gpt-5.6-luna/luna/mathd_algebra_282

Source: `experiments/output/ace_polish_validation/configs/mathd_algebra_282__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03626396; 20 completions; 20.888 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'already-used': 1, 'incomplete-proof': 2, 'no-applicable-tactic': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: f is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "incomplete-proof",
  "elapsed": 0.005878082942217588,
  "error": "(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R,\n(exists p q : Z, q <> 0%Z /\\ x = IZR p / IZR q) ->\nf x = Rabs (IZR (Int_part x))\nh1  : forall x : R,\n~ (exists p q : Z, q <> 0%Z /\\ x = IZR p / IZR q) -> f x = IZR (up x) ^ 2\n|-f (Rpower 8 (1 / 3)) + f (- PI) + f (sqrt 50) + f (9 / 2) = 79"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "unfold is_rational in *."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_303

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_303__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.04002686; 23 completions; 76.593 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `focus-error`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 1, 'no-witness': 1, 'type-mismatch': 1, 'unknown-reference': 3}`.

First error:

```text
(-32003, 'Coq: l is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "focus-error",
  "elapsed": 0.035021630115807056,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "l  : list nat\nH  : forall n : nat,\nIn n l <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHd  : NoDup l\nHclass  : forall n : nat,\n2 <= n ->\n171 mod n = 80 mod n -> 468 mod n = 13 mod n -> n = 7 \\/ n = 13 \\/ n = 91\nHmem  : forall n : nat, In n l -> n = 7 \\/ n = 13 \\/ n = 91\n|-2 <= 7"
  ],
  "success": false,
  "tactic": "}",
  "verified_prefix": [
    "intros Hd.",
    "assert (Hclass : forall n : nat, 2 <= n -> 171 mod n = 80 mod n -> 468 mod n = 13 mod n -> n = 7 \\/ n = 13 \\/ n = 91).",
    "{ intros n Hn H171 H468.",
    "assert (Hn0 : n <> 0).",
    "{ intro E. subst n. simpl in Hn. nia. }",
    "pose proof (PeanoNat.Nat.div_mod_eq 171 n) as D171.",
    "pose proof (PeanoNat.Nat.div_mod_eq 80 n) as D80.",
    "rewrite H171 in D171.",
    "assert (Hq : 80 / n <= 171 / n) by nia.",
    "assert (Heq : 91 = n * (171 / n - 80 / n)) by nia.",
    "assert (Hdiv : exists q, 91 = n * q).",
    "{ exists (171 / n - 80 / n). exact Heq. }",
    "destruct Hdiv as [q Hq91].",
    "assert (Hn91 : n <= 91) by nia.",
    "repeat (destruct n as [|n]; simpl in Hn91, Hq91; try (left; reflexivity); try (right; left; reflexivity); try (right; right; reflexivity); try nia).",
    "}",
    "assert (Hmem : forall n, In n l -> n = 7 \\/ n = 13 \\/ n = 91).",
    "{ intros n Hn.",
    "destruct ((proj1 (H n)) Hn) as [Hn2 [H171 H468]].",
    "apply Hclass; assumption.",
    "}",
    "assert (H7 : In 7 l).",
    "{ apply (proj2 (H 7)).",
    "repeat split; vm_compute."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_37

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_37__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.01892836; 23 completions; 245.707 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-witness': 2, 'prover-crash': 11, 'ring-failure': 1, 'subproof-incomplete': 1, 'syntax-error': 1}`.

First error:

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "prover-crash",
  "elapsed": 8.140638070181012,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "\n|-Init.Nat.of_num_uint\n  (Number.UIntDecimal\n     (Decimal.D9 (Decimal.D9 (Decimal.D9 (Decimal.D9 Decimal.Nil))))) *\nInit.Nat.of_num_uint\n  (Number.UIntDecimal\n     (Decimal.D9 (Decimal.D0 (Decimal.D9 (Decimal.D1 Decimal.Nil))))) =\nInit.Nat.of_num_uint\n  (Number.UIntDecimal\n     (Decimal.D9\n        (Decimal.D0\n           (Decimal.D9\n              (Decimal.D0\n                 (Decimal.D0\n                    (Decimal.D9 (Decimal.D0 (Decimal.D9 Decimal.Nil)))))))))"
  ],
  "success": false,
  "tactic": "vm_compute.",
  "verified_prefix": [
    "unfold Nat.lcm.",
    "change (9999 * (100001 / Nat.gcd 9999 100001) = 90900909).",
    "replace (Nat.gcd 9999 100001) with 11 by reflexivity.",
    "change (9999 * 9091 = 90900909)."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_405

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_405__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.04054184; 10 completions; 2.307 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `rewrite-no-match`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 2, 'no-witness': 1, 'rewrite-no-match': 3, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 10,
  "category": "rewrite-no-match",
  "elapsed": 0.16599891567602754,
  "error": "(-32003, 'Coq: Found no subterm matching \"t 13\" in the current goal.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nt  : nat -> nat\nh0  : t 0 = 0\nh1  : t 1 = 1\nh2  : forall n : nat, n > 1 -> t n = t (n - 2) + t (n - 1)\nh3  : a mod 16 = 5\nh4  : b mod 16 = 10\nh5  : c mod 16 = 15\n|-t (14 - 2) + t (14 - 1) + (t (15 - 2) + t (15 - 1)) = 987"
  ],
  "success": false,
  "tactic": "rewrite (h2 13) by lia.",
  "verified_prefix": [
    "assert (H16 : t 16 = 987).",
    "{ rewrite (h2 16) by lia.",
    "cbn.",
    "rewrite (h2 15) by lia.",
    "rewrite (h2 14) by lia."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_43

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_43__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.01905020; 29 completions; 248.926 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 13}`.

First error:

```text
(-32003, 'Coq: Out of memory.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 28,
  "category": "prover-crash",
  "elapsed": 12.951911890879273,
  "error": "ConnectionLost: (-33002, 'the Rocq server closed the connection')",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": null,
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15^233)."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_530

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_530__reference-r64__gpt-5.6-luna__seed0`. Unsolved; $0.03573844; 20 completions; 1.984 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'subproof-incomplete': 2, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 18,
  "category": "unknown-reference",
  "elapsed": 0.06978946505114436,
  "error": "(-32003, 'Coq: The reference exact_mod_cast was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\nHlt  : INR n / INR k < 6\nHgt  : 5 < INR n / INR k\nHkR  : 0 < INR k\nHkcast  : IZR (Z.of_nat k) = INR k\nH5R  : 5 * INR k < INR n\nH6R  : INR n < 6 * INR k\n|-(5 * k < n)%nat",
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\nHlt  : INR n / INR k < 6\nHgt  : 5 < INR n / INR k\nHkR  : 0 < INR k\nHkcast  : IZR (Z.of_nat k) = INR k\nH5R  : 5 * INR k < INR n\nH6R  : INR n < 6 * INR k\nH5  : (5 * k < n)%nat\n|-(22 <= Nat.lcm n k / Nat.gcd n k)%nat"
  ],
  "success": false,
  "tactic": "{ exact_mod_cast H5R.",
  "verified_prefix": [
    "intros n k Hn Hk Hlt Hgt.",
    "pose proof (lt_0_INR k Hk) as HkR.",
    "assert (Hkcast : IZR (Z.of_nat k) = INR k).",
    "{ symmetry.",
    "apply INR_IZR_INZ.",
    "}",
    "rewrite Hkcast in Hlt, Hgt.",
    "rewrite <- INR_IZR_INZ in Hlt, Hgt.",
    "assert (H5R : 5 * INR k < INR n).",
    "{ pose proof (Rmult_lt_compat_r (INR k) 5 (INR n / INR k) HkR Hgt) as Hmul.",
    "assert (Heq : (INR n / INR k) * INR k = INR n).",
    "{ field.",
    "lra.",
    "}",
    "rewrite Heq in Hmul.",
    "exact Hmul.",
    "}",
    "assert (H6R : INR n < 6 * INR k).",
    "{ pose proof (Rmult_lt_compat_r (INR k) (INR n / INR k) 6 HkR Hlt) as Hmul.",
    "assert (Heq : (INR n / INR k) * INR k = INR n).",
    "{ field.",
    "lra.",
    "}",
    "rewrite Heq in Hmul.",
    "exact Hmul.",
    "}",
    "assert (H5 : (5 * k < n)%nat)."
  ]
}
```

### gpt-5.6-luna/luna/mathd_numbertheory_64

Source: `experiments/output/ace_polish_validation/configs/mathd_numbertheory_64__reference-r64__gpt-5.6-luna__seed0`. Solved; $0.00614216; 11 completions; 2.328 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### gpt-5.6-luna/none/aime_1984_p7

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/aime_1984_p7__luna-none-medium__gpt-5.6-luna__seed0`. Solved; $0.03317466; 9 completions; 2.470 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 2, 'rewrite-no-match': 1, 'type-mismatch': 2, 'unify-failure': 3}`.

First error:

```text
(-32003, 'Coq: In environment\nf : Z -> Z\nHlarge : forall n : Z, 1000 <= n -> f n = n - 3\nHsmall : forall n : Z, n < 1000 -> f n = f (f (n + 5))\niter :=\n  fix go (k : nat) (x : Z) {struct k} : Z :=\n    match k with\n    | 0%nat => x\n    | S k\' => go k\' (f x)\n    end\n  : nat -> Z -> Z\nHstep :\n  forall (k : nat) (x : Z), x < 1000 -> iter (S k) x = iter (S (S k)) (x + 5)\nn : Z\nHn : n + 5 * Z.of_nat 0 < 1000\nUnable to unify "f (n + 5 * Z.of_nat 0)" with "f n".')
```

### gpt-5.6-luna/none/aime_1991_p6

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/aime_1991_p6__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03157002; 11 completions; 31.474 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'syntax-error': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof aime_1991_p6): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 11,
  "category": "unknown-reference",
  "elapsed": 8.327413802035153,
  "error": "(-32003, 'Coq: The reference omega was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nHr  : (0 + Int_part (r + IZR (Z.of_nat 19) / 100) +\n Int_part (r + IZR (Z.of_nat 20) / 100) +\n Int_part (r + IZR (Z.of_nat 21) / 100) +\n Int_part (r + IZR (Z.of_nat 22) / 100) +\n Int_part (r + IZR (Z.of_nat 23) / 100) +\n Int_part (r + IZR (Z.of_nat 24) / 100) +\n Int_part (r + IZR (Z.of_nat 25) / 100) +\n Int_part (r + IZR (Z.of_nat 26) / 100) +\n Int_part (r + IZR (Z.of_nat 27) / 100) +\n Int_part (r + IZR (Z.of_nat 28) / 100) +\n Int_part (r + IZR (Z.of_nat 29) / 100) +\n Int_part (r + IZR (Z.of_nat 30) / 100) +\n Int_part (r + IZR (Z.of_nat 31) / 100) +\n Int_part (r + IZR (Z.of_nat 32) / 100) +\n Int_part (r + IZR (Z.of_nat 33) / 100) +\n Int_part (r + IZR (Z.of_nat 34) / 100) +\n Int_part (r + IZR (Z.of_nat 35) / 100) +\n Int_part (r + IZR (Z.of_nat 36) / 100) +\n Int_part (r + IZR (Z.of_nat 37) / 100) +\n Int_part (r + IZR (Z.of_nat 38) / 100) +\n Int_part (r + IZR (Z.of_nat 39) / 100) +\n Int_part (r + IZR (Z.of_nat 40) / 100) +\n Int_part (r + IZR (Z.of_nat 41) / 100) +\n Int_part (r + IZR (Z.of_nat 42) / 100) +\n Int_part (r + IZR (Z.of_nat 43) / 100) +\n Int_part (r + IZR (Z.of_nat 44) / 100) +\n Int_part (r + IZR (Z.of_nat 45) / 100) +\n Int_part (r + IZR (Z.of_nat 46) / 100) +\n Int_part (r + IZR (Z.of_nat 47) / 100) +\n Int_part (r + IZR (Z.of_nat 48) / 100) +\n Int_part (r + IZR (Z.of_nat 49) / 100) +\n Int_part (r + IZR (Z.of_nat 50) / 100) +\n Int_part (r + IZR (Z.of_nat 51) / 100) +\n Int_part (r + IZR (Z.of_nat 52) / 100) +\n Int_part (r + IZR (Z.of_nat 53) / 100) +\n Int_part (r + IZR (Z.of_nat 54) / 100) +\n Int_part (r + IZR (Z.of_nat 55) / 100) +\n Int_part (r + IZR (Z.of_nat 56) / 100) +\n Int_part (r + IZR (Z.of_nat 57) / 100) +\n Int_part (r + IZR (Z.of_nat 58) / 100) +\n Int_part (r + IZR (Z.of_nat 59) / 100) +\n Int_part (r + IZR (Z.of_nat 60) / 100) +\n Int_part (r + IZR (Z.of_nat 61) / 100) +\n Int_part (r + IZR (Z.of_nat 62) / 100) +\n Int_part (r + IZR (Z.of_nat 63) / 100) +\n Int_part (r + IZR (Z.of_nat 64) / 100) +\n Int_part (r + IZR (Z.of_nat 65) / 100) +\n Int_part (r + IZR (Z.of_nat 66) / 100) +\n Int_part (r + IZR (Z.of_nat 67) / 100) +\n Int_part (r + IZR (Z.of_nat 68) / 100) +\n Int_part (r + IZR (Z.of_nat 69) / 100) +\n Int_part (r + IZR (Z.of_nat 70) / 100) +\n Int_part (r + IZR (Z.of_nat 71) / 100) +\n Int_part (r + IZR (Z.of_nat 72) / 100) +\n Int_part (r + IZR (Z.of_nat 73) / 100) +\n Int_part (r + IZR (Z.of_nat 74) / 100) +\n Int_part (r + IZR (Z.of_nat 75) / 100) +\n Int_part (r + IZR (Z.of_nat 76) / 100) +\n Int_part (r + IZR (Z.of_nat 77) / 100) +\n Int_part (r + IZR (Z.of_nat 78) / 100) +\n Int_part (r + IZR (Z.of_nat 79) / 100) +\n Int_part (r + IZR (Z.of_nat 80) / 100) +\n Int_part (r + IZR (Z.of_nat 81) / 100) +\n Int_part (r + IZR (Z.of_nat 82) / 100) +\n Int_part (r + IZR (Z.of_nat 83) / 100) +\n Int_part (r + IZR (Z.of_nat 84) / 100) +\n Int_part (r + IZR (Z.of_nat 85) / 100) +\n Int_part (r + IZR (Z.of_nat 86) / 100) +\n Int_part (r + IZR (Z.of_nat 87) / 100) +\n Int_part (r + IZR (Z.of_nat 88) / 100) +\n Int_part (r + IZR (Z.of_nat 89) / 100) +\n Int_part (r + IZR (Z.of_nat 90) / 100) +\n Int_part (r + IZR (Z.of_nat 91) / 100))%Z =\n546%Z\nx, y  : R\nHxy  : x <= y\nHyx  : (Int_part y < Int_part x)%Z\nHx  : IZR (Int_part x) <= x /\\ IZR (Int_part x) - x > -1\nHy  : IZR (Int_part y) <= y /\\ IZR (Int_part y) - y > -1\n|-False"
  ],
  "success": false,
  "tactic": "assert (Hz : (Int_part y + 1 <= Int_part x)%Z) by omega.",
  "verified_prefix": [
    "intros r Hr.",
    "unfold range_sum in Hr.",
    "cbn [seq map fold_left] in Hr.",
    "assert (Hmono : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z).",
    "{ intros x y Hxy.",
    "destruct (Z.le_gt_cases (Int_part x) (Int_part y)) as [Hxy'|Hyx].",
    "- exact Hxy'.",
    "- exfalso.",
    "assert (Hx := base_Int_part x).",
    "assert (Hy := base_Int_part y)."
  ]
}
```

### gpt-5.6-luna/none/aime_1991_p9

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/aime_1991_p9__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04211476; 26 completions; 2.416 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `ring-failure`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 2, 'no-matching-clause': 2, 'no-such-goal': 2, 'no-witness': 3, 'other': 1, 'ring-failure': 2, 'subproof-incomplete': 1, 'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "ring-failure",
  "elapsed": 0.010879503563046455,
  "error": "(-32003, 'Coq: Tactic failure: not a valid ring equation.')",
  "outcome": "rejected",
  "remaining_goals": [
    "x  : R\nHc  : cos x <> 0\nHs  : sin x <> 0\nHe  : (1 + sin x) / cos x = 22 / 7\nHtrig  : (22 / 7 * cos x - 1)² + (cos x)² = 1\nHe'  : 1 + sin x = 22 / 7 * cos x\nHsinrel  : sin x = 22 / 7 * cos x - 1\n|-1 / sin x + 1 / tan x = 29 / 15"
  ],
  "success": false,
  "tactic": "replace ((22 / 7 * cos x - 1)²) with ((22 / 7 * cos x - 1) * (22 / 7 * cos x - 1)) in Htrig by ring.",
  "verified_prefix": [
    "intros x Hc Hs He.",
    "exists 29%Z, 15%Z.",
    "repeat split.",
    "unfold tan in He.",
    "pose proof (sin2_cos2 x) as Htrig.",
    "rewrite <- (Rdiv_plus_distr 1 (sin x) (cos x)) in He.",
    "assert (He' : 1 + sin x = (22 / 7) * cos x).",
    "{ apply (Rdiv_eq_reg_r (cos x) (1 + sin x) ((22 / 7) * cos x)).",
    "- etransitivity.",
    "+ exact He.",
    "+ field.",
    "exact Hc.",
    "- exact Hc.",
    "}",
    "assert (Hsinrel : sin x = (22 / 7) * cos x - 1) by nra.",
    "rewrite Hsinrel in Htrig."
  ]
}
```

### gpt-5.6-luna/none/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/algebra_others_exirrpowirrrat__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03804408; 24 completions; 3.711 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-matching-clause`; added goal views: 0. Error counts: `{'no-matching-clause': 2, 'other': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: Unknown interpretation for notation "_ ²".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "no-matching-clause",
  "elapsed": 0.018581205047667027,
  "error": "(-32003, 'Coq: No matching clauses for match.')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHsq  : 2%R = (IZR p / IZR q * (IZR p / IZR q))%R\n|-False",
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHsq  : (sqrt 2)²%R = (IZR p / IZR q)²%R\n|-(0 <= 2)%R"
  ],
  "success": false,
  "tactic": "field_simplify [HqR] in Hsq.",
  "verified_prefix": [
    "assert (Hs : irrational (sqrt 2)).",
    "{ unfold irrational.",
    "intros [p [q [Hq Heq]]].",
    "assert (HqR : IZR q <> 0%R).",
    "{ intro H.",
    "apply Hq.",
    "apply eq_IZR.",
    "exact H.",
    "}",
    "assert (Hsq : Rsqr (sqrt 2) = Rsqr (IZR p / IZR q)).",
    "{ rewrite Heq.",
    "reflexivity.",
    "}",
    "rewrite (Rsqr_sqrt 2) in Hsq.",
    "unfold Rsqr in Hsq."
  ]
}
```

### gpt-5.6-luna/none/amc12_2001_p21

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/amc12_2001_p21__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04461550; 22 completions; 293.779 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-such-goal': 1, 'no-witness': 2, 'prover-crash': 11, 'syntax-error': 2, 'unknown-reference': 2}`.

First error:

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 57s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "prover-crash",
  "elapsed": 60.174668923951685,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "repeat (first [ nia | destruct b as [|b] ]).",
  "verified_prefix": [
    "intros a b c d Habcd Hab Hbc Hcd.",
    "simpl in Habcd.",
    "assert (Ha0 : 0 < a) by nia.",
    "assert (Hb0 : 0 < b) by nia.",
    "assert (Hc0 : 0 < c) by nia.",
    "assert (Hd0 : 0 < d) by nia.",
    "assert (Hb : b <= 36) by nia."
  ]
}
```

### gpt-5.6-luna/none/amc12a_2008_p4

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/amc12a_2008_p4__luna-none-medium__gpt-5.6-luna__seed0`. Solved; $0.02006062; 14 completions; 1.533 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-applicable-tactic': 2, 'rewrite-no-match': 3}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "INR (S ?M1837)" in the current goal.')
```

### gpt-5.6-luna/none/amc12a_2019_p21

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/amc12a_2019_p21__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03950654; 26 completions; 132.957 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-applicable-tactic': 1, 'not-convertible': 1, 'prover-crash': 3, 'syntax-error': 2, 'type-mismatch': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference ring_nf was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "prover-crash",
  "elapsed": 27.749330358579755,
  "error": "ConnectionLost: (-33002, 'the Rocq server closed the connection')",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": null,
  "verified_prefix": [
    "intros z Hz.",
    "subst z.",
    "cbn [seq map fold_left].",
    "assert (Hs : ((sqrt 2 : R) ^ 2)%R = 2).",
    "{ assert (H : (0 : R) <= 2) by lra.",
    "exact (pow2_sqrt 2 H).",
    "}",
    "cbv [Cpow Cdiv Cinv Cplus].",
    "repeat rewrite Hs."
  ]
}
```

### gpt-5.6-luna/none/amc12a_2020_p21

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/amc12a_2020_p21__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04106614; 22 completions; 30.816 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `syntax-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'other': 1, 'syntax-error': 3, 'type-mismatch': 2, 'unify-failure': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "syntax-error",
  "elapsed": 0.02541930042207241,
  "error": "(-32003, \"Coq: Syntax error: [term level 200] expected after '(' (in [term]).\")",
  "outcome": "rejected",
  "remaining_goals": [
    "f := fun n0 : nat =>\n((n0 mod 5 =? 0) && (Nat.lcm (fact 5) n0 =? 5 * Nat.gcd (fact 10) n0))%bool : nat -> bool\nl := filter f (seq 0 (5 * fact 10 + 1)) : list nat\nn  : nat\nHmod  : n mod 5 = 0\nHeq  : (Nat.lcm (fact 5) n =? 5 * Nat.gcd (fact 10) n) = true\nH  : true = true\n|-exists k : nat, n = 5 * k",
    "f := fun n0 : nat =>\n((n0 mod 5 =? 0) && (Nat.lcm (fact 5) n0 =? 5 * Nat.gcd (fact 10) n0))%bool : nat -> bool\nl := filter f (seq 0 (5 * fact 10 + 1)) : list nat\nn  : nat\nHmod  : n mod 5 = 0\nHeq  : (Nat.lcm (fact 5) n =? 5 * Nat.gcd (fact 10) n) = true\nH  : true = true\nHex  : exists k : nat, n = 5 * k\n|-exists k : nat, n = k * 5"
  ],
  "success": false,
  "tactic": "{ apply (proj1 ((Nat.Private_NDivProp.mod_divides n 5) (by lia))).",
  "verified_prefix": [
    "pose (f := fun n : nat => andb (n mod 5 =? 0) (Nat.lcm (fact 5) n =? 5 * Nat.gcd (fact 10) n)).",
    "pose (l := filter f (seq 0 (5 * fact 10 + 1))).",
    "exists l.",
    "split.",
    "- unfold l.",
    "apply NoDup_filter.",
    "apply seq_NoDup.",
    "- split.",
    "+ intros n.",
    "unfold l.",
    "rewrite filter_In.",
    "split.",
    "* intros [_ H].",
    "unfold f in H.",
    "destruct (n mod 5 =? 0) eqn:Hmod; destruct (Nat.lcm (fact 5) n =? 5 * Nat.gcd (fact 10) n) eqn:Heq; simpl in H.",
    "-- split.",
    "++ apply Nat.eqb_eq in Hmod.",
    "assert (Hex : exists k : nat, n = 5 * k)."
  ]
}
```

### gpt-5.6-luna/none/amc12b_2002_p3

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/amc12b_2002_p3__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03719388; 20 completions; 1.620 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 1, 'other': 2, 'syntax-error': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "incomplete-proof",
  "elapsed": 0.0027156928554177284,
  "error": "(-32003, 'Coq:  (in proof amc12b_2002_p3): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros n Hn Hp.",
    "pose proof (prime_ge_2 _ Hp) as Hlow.",
    "destruct (Z_le_gt_dec n 3) as [Hle | Hgt].",
    "- destruct (Z.lt_trichotomy n 3) as [Hlt | Heq].",
    "+ assert (Hn2 : n <= 2).",
    "{ apply Zlt_succ_le.",
    "exact Hlt.",
    "}",
    "destruct (Z.lt_trichotomy n 2) as [Hlt2 | Heq2].",
    "* assert (Hn1 : n <= 1).",
    "{ apply Zlt_succ_le.",
    "exact Hlt2.",
    "}",
    "destruct (Z.lt_trichotomy n 1) as [Hlt1 | Heq1].",
    "-- assert (Hn0 : n <= 0).",
    "{ apply Zlt_succ_le.",
    "exact Hlt1.",
    "}",
    "exfalso.",
    "apply (Z.lt_irrefl 0).",
    "eapply Z.lt_le_trans.",
    "++ exact (Z.gt_lt n 0 Hn).",
    "++ exact Hn0."
  ]
}
```

### gpt-5.6-luna/none/imo_1960_p2

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/imo_1960_p2__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03918540; 24 completions; 1.944 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 4, 'no-applicable-tactic': 5, 'other': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "incomplete-proof",
  "elapsed": 0.006645639427006245,
  "error": "(-32003, 'Coq:  (in proof imo_1960_p2): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros x Hrad Hden Hineq.",
    "assert (Hsq : sqrt (1 + 2 * x) ^ 2 = 1 + 2 * x).",
    "{ apply pow2_sqrt.",
    "exact Hrad.",
    "}",
    "assert (Hpos : 0 < (1 - sqrt (1 + 2 * x)) ^ 2).",
    "{ destruct (Rle_dec 0 (1 - sqrt (1 + 2 * x))) as [Hle|Hnle].",
    "- destruct (Rle_lt_or_eq_dec 0 (1 - sqrt (1 + 2 * x)) Hle) as [Hlt|Heq].",
    "+ nra.",
    "+ exfalso.",
    "apply Hden.",
    "nra.",
    "- assert (Hlt : 1 - sqrt (1 + 2 * x) < 0) by nra.",
    "nra.",
    "}",
    "assert (Hmul : (4 * x ^ 2 / (1 - sqrt (1 + 2 * x)) ^ 2) * (1 - sqrt (1 + 2 * x)) ^ 2 < (2 * x + 9) * (1 - sqrt (1 + 2 * x)) ^ 2).",
    "{ apply Rmult_lt_compat_r.",
    "- exact Hpos.",
    "- exact Hineq.",
    "}",
    "field_simplify in Hmul.",
    "rewrite Hsq in Hmul.",
    "assert (Hs : sqrt (1 + 2 * x) < 7 / 2) by nra.",
    "assert (Hroot : 0 <= sqrt (1 + 2 * x)) by apply sqrt_pos.",
    "constructor.",
    "- lra.",
    "- nra."
  ]
}
```

### gpt-5.6-luna/none/imo_1969_p2

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/imo_1969_p2__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04147332; 21 completions; 3.239 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 1, 'no-witness': 2, 'other': 5, 'subproof-incomplete': 1, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "unknown-reference",
  "elapsed": 0.007462428882718086,
  "error": "(-32003, 'Coq: The reference norm_num was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i0 : nat => cos (a i0 + x) / 2 ^ i0) (Init.Nat.pred k)\nHm  : sum_f_R0 (fun i0 : nat => cos (a i0 + m) / 2 ^ i0) (Init.Nat.pred k) = 0\nHn  : sum_f_R0 (fun i0 : nat => cos (a i0 + n) / 2 ^ i0) (Init.Nat.pred k) = 0\ni  : nat\nHi  : (i <= Init.Nat.pred k)%nat\n|-2 <> 0"
  ],
  "success": false,
  "tactic": "norm_num.",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hm Hn.",
    "rewrite (Hy m) in Hm.",
    "rewrite (Hy n) in Hn.",
    "remember (sum_f_R0 (fun i => cos (a i) / 2 ^ i) (Init.Nat.pred k)) as C.",
    "remember (sum_f_R0 (fun i => sin (a i) / 2 ^ i) (Init.Nat.pred k)) as S.",
    "assert (Hm' : C * cos m - S * sin m = 0).",
    "{ rewrite <- Hm.",
    "subst C.",
    "subst S.",
    "rewrite (sum_eq (fun i => cos (a i + m) / 2 ^ i) (fun i => (cos (a i) * cos m - sin (a i) * sin m) / 2 ^ i)).",
    "2: { intros i Hi.",
    "rewrite cos_plus.",
    "field.",
    "apply pow_nonzero."
  ]
}
```

### gpt-5.6-luna/none/imo_1984_p6

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/imo_1984_p6__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03900012; 24 completions; 203.903 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'already-used': 1, 'incomplete-proof': 1, 'no-witness': 3, 'prover-crash': 2, 'syntax-error': 2}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "no-witness",
  "elapsed": 0.07672233320772648,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "k, m, x  : nat\nHa  : 0 < 2 * x + 1\ny  : nat\nHb  : 0 < 2 * y + 1\nz  : nat\nHc  : 0 < 2 * z + 1\nw  : nat\nHd  : 0 < 2 * w + 1\nHbc  : 2 * y + 1 < 2 * z + 1 < 2 * w + 1\nHab  : 2 * x + 1 < 2 * y + 1\nH3  : (2 * x + 1) * (2 * w + 1) = (2 * y + 1) * (2 * z + 1)\nHxw  : x + w + 1 = 2 ^ k\nHyz  : y + z + 1 = 2 ^ m\n|-2 * x + 1 = 1"
  ],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "destruct H0 as [Ha [Hb [Hc Hd]]].",
    "destruct H1 as [Oa [Ob [Oc Od]]].",
    "destruct Oa as [x Hax].",
    "destruct Ob as [y Hby].",
    "destruct Oc as [z Hcz].",
    "destruct Od as [w Hdw].",
    "destruct H2 as [Hab Hbc Hcd].",
    "subst a.",
    "subst b.",
    "subst c.",
    "subst d.",
    "destruct k as [|k].",
    "- simpl in H4.",
    "lia.",
    "- destruct m as [|m].",
    "+ simpl in H5.",
    "lia.",
    "+ simpl in H4.",
    "simpl in H5.",
    "assert (Hxw : x + w + 1 = 2 ^ k) by lia.",
    "assert (Hyz : y + z + 1 = 2 ^ m) by lia.",
    "clear H4 H5."
  ]
}
```

### gpt-5.6-luna/none/mathd_algebra_282

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_algebra_282__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03124970; 30 completions; 12.305 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'already-used': 1, 'incomplete-proof': 17, 'other': 1}`.

First error:

```text
(-32003, 'Coq: f is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 30,
  "category": "incomplete-proof",
  "elapsed": 0.006411134265363216,
  "error": "(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R, is_rational x -> f x = Rabs (IZR (Int_part x))\nh1  : forall x : R, ~ is_rational x -> f x = IZR (up x) ^ 2\n|-f (Rpower 8 (1 / 3)) + f (- PI) + f (sqrt 50) + f (9 / 2) = 79"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "unfold is_rational."
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_303

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_303__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03663124; 23 completions; 29.025 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 2, 'no-product': 1, 'no-witness': 1, 'other': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: No product even after head-reduction.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "no-witness",
  "elapsed": 9.27588289231062,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "x  : nat\nl  : list nat\nIH  : (forall n : nat,\n In n l <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n) ->\nNoDup l -> list_sum l = 111\nH  : forall n : nat,\nIn n (x :: l) <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHnodup  : NoDup (x :: l)\nx'  : nat\nl'  : list nat\nHxnot  : ~ In x l\nHtail  : NoDup l\nH0  : x' = x\nH1  : l' = l\nHx2  : 2 <= x\nHxmod1  : 171 mod x = 80 mod x\nHxmod2  : 468 mod x = 13 mod x\n|-x = 7 \\/ x = 13 \\/ x = 91",
    "x  : nat\nl  : list nat\nIH  : (forall n : nat,\n In n l <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n) ->\nNoDup l -> list_sum l = 111\nH  : forall n : nat,\nIn n (x :: l) <-> 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n\nHnodup  : NoDup (x :: l)\nx'  : nat\nl'  : list nat\nHxnot  : ~ In x l\nHtail  : NoDup l\nH0  : x' = x\nH1  : l' = l\nHx2  : 2 <= x\nHxmod1  : 171 mod x = 80 mod x\nHxmod2  : 468 mod x = 13 mod x\nHxclass  : x = 7 \\/ x = 13 \\/ x = 91\n|-list_sum (x :: l) = 111"
  ],
  "success": false,
  "tactic": "{ lia. }",
  "verified_prefix": [
    "revert H.",
    "induction l as [|x l IH].",
    "- intros H Hnodup.",
    "exfalso.",
    "assert (H7 : In 7 nil).",
    "{ apply (proj2 (H 7)).",
    "repeat split; simpl; lia. }",
    "simpl in H7.",
    "assumption.",
    "- intros H Hnodup.",
    "inversion Hnodup as [|x' l' Hxnot Htail].",
    "assert (Hxmem : In x (x :: l)).",
    "{ simpl; auto. }",
    "apply (proj1 (H x)) in Hxmem.",
    "destruct Hxmem as [Hx2 [Hxmod1 Hxmod2]].",
    "assert (Hxclass : x = 7 \\/ x = 13 \\/ x = 91)."
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_37

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_37__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03252764; 23 completions; 255.656 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 2, 'other': 1, 'prover-crash': 8, 'rewrite-no-match': 1, 'ring-failure': 1, 'syntax-error': 1}`.

First error:

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "focus-error",
  "elapsed": 31.039616570807993,
  "error": "(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')",
  "outcome": "rejected",
  "remaining_goals": [
    "\n|-(11 * 909 *\n Init.Nat.of_num_uint\n   (Number.UIntDecimal\n      (Decimal.D9 (Decimal.D0 (Decimal.D9 (Decimal.D1 Decimal.Nil))))) =?\n Init.Nat.of_num_uint\n   (Number.UIntDecimal\n      (Decimal.D9\n         (Decimal.D0\n            (Decimal.D9\n               (Decimal.D0\n                  (Decimal.D0\n                     (Decimal.D9 (Decimal.D0 (Decimal.D9 Decimal.Nil)))))))))) =\ntrue"
  ],
  "success": false,
  "tactic": "- discriminate.",
  "verified_prefix": [
    "change (9999 * (100001 / Nat.gcd 9999 100001) = 90900909).",
    "replace 100001 with (11 + 10 * 9999) by reflexivity.",
    "rewrite Nat.gcd_add_mult_diag_r.",
    "rewrite Nat.gcd_comm.",
    "replace 9999 with (11 * 909) by reflexivity.",
    "rewrite Nat.gcd_mul_diag_l.",
    "replace (11 + 10 * (11 * 909)) with (9091 * 11) by reflexivity.",
    "rewrite Nat.div_mul.",
    "- change (11 * 909 * 9091 = 90900909).",
    "apply Nat.eqb_eq."
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_405

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_405__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03685584; 13 completions; 3.980 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `rewrite-no-match`; added goal views: 0. Error counts: `{'already-used': 1, 'incomplete-proof': 1, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'unify-failure': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 13,
  "category": "rewrite-no-match",
  "elapsed": 0.3661446003243327,
  "error": "(-32003, 'Coq: Found no subterm matching \"t (n + 17) mod 7\" in the current goal.')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nt  : nat -> nat\nh0  : t 0 = 0\nh1  : t 1 = 1\nh2  : forall n0 : nat, n0 > 1 -> t n0 = t (n0 - 2) + t (n0 - 1)\nh3  : a mod 16 = 5\nh4  : b mod 16 = 10\nh5  : c mod 16 = 15\nht2  : t 2 = 1\nht3  : t 3 = 2\nht4  : t 4 = 3\nht5  : t 5 = 5\nht6  : t 6 = 8\nht7  : t 7 = 13\nht8  : t 8 = 21\nht9  : t 9 = 34\nht10  : t 10 = 55\nht11  : t 11 = 89\nht12  : t 12 = 144\nht13  : t 13 = 233\nht14  : t 14 = 377\nht15  : t 15 = 610\nht16  : t 16 = 987\nht17  : t 17 = 1597\nn  : nat\nH  : forall m : nat, m < S (S n) -> t (m + 16) mod 7 = t m mod 7\nH1  : t (n + 18) = t (n + 16) + t (n + 17)\nH2  : t (n + 2) = t n + t (n + 1)\nE1  : t (n + 17) mod 7 = t (n + 1) mod 7\nE0  : t (n + 16) mod 7 = t n mod 7\n|-(t (n + 16) + t (n + 17)) mod 7 = (t n + t (n + 1)) mod 7"
  ],
  "success": false,
  "tactic": "rewrite E1, E0.",
  "verified_prefix": [
    "assert (ht2 : t 2 = 1).",
    "{ rewrite (h2 2).",
    "- simpl.",
    "rewrite h0, h1.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht3 : t 3 = 2).",
    "{ rewrite (h2 3).",
    "- simpl.",
    "rewrite ht2, h1.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht4 : t 4 = 3).",
    "{ rewrite (h2 4).",
    "- simpl.",
    "rewrite ht2, ht3.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht5 : t 5 = 5).",
    "{ rewrite (h2 5).",
    "- simpl.",
    "rewrite ht3, ht4.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht6 : t 6 = 8).",
    "{ rewrite (h2 6).",
    "- simpl.",
    "rewrite ht4, ht5.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht7 : t 7 = 13).",
    "{ rewrite (h2 7).",
    "- simpl.",
    "rewrite ht5, ht6.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht8 : t 8 = 21).",
    "{ rewrite (h2 8).",
    "- simpl.",
    "rewrite ht6, ht7.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht9 : t 9 = 34).",
    "{ rewrite (h2 9).",
    "- simpl.",
    "rewrite ht7, ht8.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht10 : t 10 = 55).",
    "{ rewrite (h2 10).",
    "- simpl.",
    "rewrite ht8, ht9.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht11 : t 11 = 89).",
    "{ rewrite (h2 11).",
    "- simpl.",
    "rewrite ht9, ht10.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht12 : t 12 = 144).",
    "{ rewrite (h2 12).",
    "- simpl.",
    "rewrite ht10, ht11.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht13 : t 13 = 233).",
    "{ rewrite (h2 13).",
    "- simpl.",
    "rewrite ht11, ht12.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht14 : t 14 = 377).",
    "{ rewrite (h2 14).",
    "- simpl.",
    "rewrite ht12, ht13.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht15 : t 15 = 610).",
    "{ rewrite (h2 15).",
    "- simpl.",
    "rewrite ht13, ht14.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht16 : t 16 = 987).",
    "{ rewrite (h2 16).",
    "- simpl.",
    "rewrite ht14, ht15.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (ht17 : t 17 = 1597).",
    "{ rewrite (h2 17).",
    "- simpl.",
    "rewrite ht15, ht16.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (hper : forall n, t (n + 16) mod 7 = t n mod 7).",
    "{ intro n.",
    "induction n using lt_wf_ind.",
    "destruct n as [|n].",
    "- simpl.",
    "rewrite ht16, h0.",
    "reflexivity.",
    "- destruct n as [|n].",
    "+ simpl.",
    "rewrite ht17, h1.",
    "reflexivity.",
    "+ assert (H1 : t (n + 18) = t (n + 16) + t (n + 17)).",
    "{ rewrite (h2 (n + 18)).",
    "- replace (n + 18 - 2) with (n + 16) by lia.",
    "replace (n + 18 - 1) with (n + 17) by lia.",
    "reflexivity.",
    "- lia.",
    "}",
    "assert (H2 : t (n + 2) = t n + t (n + 1)).",
    "{ rewrite (h2 (n + 2)).",
    "- replace (n + 2 - 2) with n by lia.",
    "replace (n + 2 - 1) with (n + 1) by lia.",
    "reflexivity.",
    "- lia.",
    "}",
    "replace (S (S n) + 16) with (n + 18) by lia.",
    "replace (S (S n)) with (n + 2) by lia.",
    "rewrite H1, H2.",
    "assert (E1 : t (n + 17) mod 7 = t (n + 1) mod 7).",
    "{ replace (n + 17) with (n + 1 + 16) by lia.",
    "exact (H (n + 1) ltac:(lia)).",
    "}",
    "assert (E0 : t (n + 16) mod 7 = t n mod 7).",
    "{ exact (H n ltac:(lia)).",
    "}"
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_43

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_43__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.01845168; 20 completions; 264.357 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 5, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference Nat.div_mul_cancel was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 44.332899471744895,
  "error": "Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "{ vm_compute. }",
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15^233).",
    "assert (H : fact 942 mod 15^233 = 0)."
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_530

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_530__luna-none-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04096698; 24 completions; 2.460 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `other`; added goal views: 0. Error counts: `{'not-convertible': 1, 'other': 2, 'rewrite-no-match': 1, 'syntax-error': 1, 'type-mismatch': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "other",
  "elapsed": 0.02507816255092621,
  "error": "(-32003, 'Coq: The reference Nat.mod_eq_zero_of_dvd was not found in the current\\nenvironment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\nHlt  : INR n / INR k < 6\nHgt  : 5 < INR n / INR k\ng  : nat\nHg  : g = Nat.gcd n k\nHgn  : Nat.divide g n\nHgk  : Nat.divide g k\nHg0  : g <> 0%nat\nx := (n / g)%nat : nat\ny := (k / g)%nat : nat\nE  : n = (g * (n / g) + n mod g)%nat\n|-n = (g * (n / g))%nat"
  ],
  "success": false,
  "tactic": "rewrite (Nat.mod_eq_zero_of_dvd Hgn) in E.",
  "verified_prefix": [
    "intros n k Hn Hk Hlt Hgt.",
    "rewrite <- INR_IZR_INZ in Hlt, Hgt.",
    "rewrite <- (INR_IZR_INZ k) in Hlt, Hgt.",
    "remember (Nat.gcd n k) as g eqn:Hg.",
    "assert (Hgn : Nat.divide g n).",
    "{ rewrite Hg.",
    "apply Nat.gcd_divide_l.",
    "}",
    "assert (Hgk : Nat.divide g k).",
    "{ rewrite Hg.",
    "apply Nat.gcd_divide_r.",
    "}",
    "assert (Hg0 : g <> 0%nat).",
    "{ intro Hzero.",
    "destruct Hgn as [q Hq].",
    "rewrite Hzero in Hq.",
    "simpl in Hq.",
    "lia.",
    "}",
    "set (x := Nat.div n g).",
    "set (y := Nat.div k g).",
    "assert (Hnx : n = (g * x)%nat).",
    "{ unfold x.",
    "pose proof (Nat.div_mod n g Hg0) as E."
  ]
}
```

### gpt-5.6-luna/none/mathd_numbertheory_64

Source: `experiments/output/ace_attribution_20260912/validation/luna-none/configs/mathd_numbertheory_64__luna-none-medium__gpt-5.6-luna__seed0`. Solved; $0.00915588; 9 completions; 2.132 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')
```

### gpt-5.6-luna/terra/aime_1984_p7

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1984_p7__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03804916; 13 completions; 1.361 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `other`; added goal views: 0. Error counts: `{'focus-error': 1, 'no-witness': 2, 'other': 1, 'rewrite-no-match': 2, 'subproof-incomplete': 1, 'syntax-error': 1, 'type-mismatch': 2}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 13,
  "category": "other",
  "elapsed": 0.016688192263245583,
  "error": "(-32003, 'Coq: Unable to find an instance for the variable y.')",
  "outcome": "rejected",
  "remaining_goals": [
    "f  : Z -> Z\nHhigh  : forall n : Z, 1000 <= n -> f n = n - 3\nHlow  : forall n : Z, n < 1000 -> f n = f (f (n + 5))\nit := fix g (k0 : nat) (x0 : Z) {struct k0} : Z :=\n  match k0 with\n  | 0%nat => x0\n  | S k1 => f (g k1 x0)\n  end : nat -> Z -> Z\nit_f  : forall (k0 : nat) (x0 : Z), it k0 (f x0) = f (it k0 x0)\nk  : nat\nIH  : forall x0 y0 : Z, x0 = y0 -> it k x0 = it k y0\nx, y  : Z\nHxy  : x = y\n|-f (it k x) = f (it k y)"
  ],
  "success": false,
  "tactic": "rewrite IH.",
  "verified_prefix": [
    "intros f Hhigh Hlow.",
    "pose (it := fix g (k : nat) (x : Z) {struct k} : Z := match k with | O => x | S k => f (g k x) end).",
    "assert (it_f : forall (k : nat) (x : Z), it k (f x) = f (it k x)).",
    "{ intros k.",
    "induction k as [|k IH]; intro x.",
    "- simpl. reflexivity.",
    "- simpl.",
    "rewrite IH.",
    "reflexivity.",
    "}",
    "assert (it_congr : forall (k : nat) (x y : Z), x = y -> it k x = it k y).",
    "{ intros k.",
    "induction k as [|k IH]; intros x y Hxy.",
    "- exact Hxy.",
    "- simpl."
  ]
}
```

### gpt-5.6-luna/terra/aime_1991_p6

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1991_p6__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03977490; 13 completions; 45.598 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 3, 'no-witness': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 12,
  "category": "no-applicable-tactic",
  "elapsed": 9.52570872940123,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nHr  : (Int_part (r + 19 / 100) + Int_part (r + 20 / 100) + Int_part (r + 21 / 100) +\n Int_part (r + 22 / 100) + Int_part (r + 23 / 100) + \n Int_part (r + 24 / 100) + Int_part (r + 25 / 100) + \n Int_part (r + 26 / 100) + Int_part (r + 27 / 100) + \n Int_part (r + 28 / 100) + Int_part (r + 29 / 100) + \n Int_part (r + 30 / 100) + Int_part (r + 31 / 100) + \n Int_part (r + 32 / 100) + Int_part (r + 33 / 100) + \n Int_part (r + 34 / 100) + Int_part (r + 35 / 100) + \n Int_part (r + 36 / 100) + Int_part (r + 37 / 100) + \n Int_part (r + 38 / 100) + Int_part (r + 39 / 100) + \n Int_part (r + 40 / 100) + Int_part (r + 41 / 100) + \n Int_part (r + 42 / 100) + Int_part (r + 43 / 100) + \n Int_part (r + 44 / 100) + Int_part (r + 45 / 100) + \n Int_part (r + 46 / 100) + Int_part (r + 47 / 100) + \n Int_part (r + 48 / 100) + Int_part (r + 49 / 100) + \n Int_part (r + 50 / 100) + Int_part (r + 51 / 100) + \n Int_part (r + 52 / 100) + Int_part (r + 53 / 100) + \n Int_part (r + 54 / 100) + Int_part (r + 55 / 100) + \n Int_part (r + 56 / 100) + Int_part (r + 57 / 100) + \n Int_part (r + 58 / 100) + Int_part (r + 59 / 100) + \n Int_part (r + 60 / 100) + Int_part (r + 61 / 100) + \n Int_part (r + 62 / 100) + Int_part (r + 63 / 100) + \n Int_part (r + 64 / 100) + Int_part (r + 65 / 100) + \n Int_part (r + 66 / 100) + Int_part (r + 67 / 100) + \n Int_part (r + 68 / 100) + Int_part (r + 69 / 100) + \n Int_part (r + 70 / 100) + Int_part (r + 71 / 100) + \n Int_part (r + 72 / 100) + Int_part (r + 73 / 100) + \n Int_part (r + 74 / 100) + Int_part (r + 75 / 100) + \n Int_part (r + 76 / 100) + Int_part (r + 77 / 100) + \n Int_part (r + 78 / 100) + Int_part (r + 79 / 100) + \n Int_part (r + 80 / 100) + Int_part (r + 81 / 100) + \n Int_part (r + 82 / 100) + Int_part (r + 83 / 100) + \n Int_part (r + 84 / 100) + Int_part (r + 85 / 100) + \n Int_part (r + 86 / 100) + Int_part (r + 87 / 100) + \n Int_part (r + 88 / 100) + Int_part (r + 89 / 100) + \n Int_part (r + 90 / 100) + Int_part (r + 91 / 100))%Z =\n546%Z\nx, y  : R\nHxy  : x <= y\nHxl  : IZR (Int_part x) <= x\nHxr  : IZR (Int_part x) - x > -1\nHyl  : IZR (Int_part y) <= y\nHyr  : IZR (Int_part y) - y > -1\n|-IZR (Int_part x) <= IZR (Int_part y)"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros r Hr.",
    "unfold range_sum in Hr.",
    "cbn in Hr.",
    "assert (Hmono : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z).",
    "{ intros x y Hxy.",
    "apply le_IZR.",
    "pose proof (base_Int_part x) as Hx.",
    "pose proof (base_Int_part y) as Hy.",
    "destruct Hx as [Hxl Hxr].",
    "destruct Hy as [Hyl Hyr]."
  ]
}
```

### gpt-5.6-luna/terra/aime_1991_p9

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1991_p9__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03539276; 16 completions; 2.154 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'no-matching-clause': 2, 'other': 1, 'ring-failure': 1, 'subproof-incomplete': 1, 'syntax-error': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: No matching clauses for match.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 16,
  "category": "no-applicable-tactic",
  "elapsed": 0.02893022447824478,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "x  : R\nHc  : cos x <> 0\nHs  : sin x <> 0\nH  : 1 / cos x + sin x / cos x = 22 / 7\nHsc  : (sin x)² + (cos x)² = 1\nHci  : cos x * / cos x = 1\n|-(1 * / cos x)² - (sin x / cos x)² = 1"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros x Hc Hs H.",
    "unfold tan in H.",
    "assert (Hsc : (sin x)² + (cos x)² = 1) by apply sin2_cos2.",
    "assert (Hci : cos x * / cos x = 1) by (apply Rinv_r; exact Hc).",
    "assert (Hid : (1 / cos x)² - (sin x / cos x)² = 1).",
    "{ rewrite Rdiv_def."
  ]
}
```

### gpt-5.6-luna/terra/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_capacity_20260912/cross/configs/algebra_others_exirrpowirrrat__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03821100; 31 completions; 2.880 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unify-failure`; added goal views: 0. Error counts: `{'no-matching-clause': 1, 'type-mismatch': 2, 'unify-failure': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference norm_num was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 31,
  "category": "unify-failure",
  "elapsed": 0.014641016721725464,
  "error": "(-32003, 'Coq: In environment\\np, q : Z\\nHq : q <> 0%Z\\nHeq : sqrt 2 = (IZR p / IZR q)%R\\nHqR : IZR q <> 0%R\\nHsq : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\\nUnable to unify \"?M1877 = 0%Z\" with \"(p * p)%Z = (2 * (q * q))%Z\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHsq  : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\n|-(p * p)%Z = (2 * (q * q))%Z",
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHsq  : (IZR p ^ 2 / IZR q ^ 2)%R = 2%R\nHpq  : (p * p)%Z = (2 * (q * q))%Z\n|-False",
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\n|-IZR q <> 0%R"
  ],
  "success": false,
  "tactic": "{ apply eq_IZR_R0.",
  "verified_prefix": [
    "assert (Hs : irrational (sqrt (2:R))).",
    "{ unfold irrational.",
    "intros H.",
    "destruct H as [p [q [Hq Heq]]].",
    "assert (HqR : IZR q <> 0%R).",
    "{ apply not_0_IZR.",
    "exact Hq.",
    "}",
    "assert (Hsq : (sqrt (2:R) * sqrt (2:R) = (2:R))%R).",
    "{ apply sqrt_def.",
    "lra.",
    "}",
    "rewrite Heq in Hsq.",
    "field_simplify in Hsq.",
    "assert (Hpq : (p * p = 2 * (q * q))%Z)."
  ]
}
```

### gpt-5.6-luna/terra/amc12_2001_p21

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12_2001_p21__cross-level0__gpt-5.6-luna__seed0`. Solved; $0.00529698; 6 completions; 63.510 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-luna/terra/amc12a_2008_p4

Source: `experiments/output/ace_attribution_20260912/swaps/configs/amc12a_2008_p4__luna-terra-book-medium__gpt-5.6-luna__seed0`. Unsolved; $0.02631586; 48 completions; 7.345 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 21, 'rewrite-no-match': 1, 'ring-failure': 1}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "INR (S ?M1835)" in the current goal.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 42,
  "category": "incomplete-proof",
  "elapsed": 0.01601776760071516,
  "error": "(-32003, 'Coq:  (in proof amc12a_2008_p4): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-Rprod 501 (fun k : nat => (4 * INR k + 4) / (4 * INR k)) = 502"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": []
}
```

### gpt-5.6-luna/terra/amc12a_2019_p21

Source: `experiments/output/ace_attribution_20260912/swaps/configs/amc12a_2019_p21__luna-terra-book-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03550668; 38 completions; 83.499 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `syntax-error`; added goal views: 0. Error counts: `{'prover-crash': 2, 'ring-failure': 1, 'syntax-error': 3}`.

First error:

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 38,
  "category": "syntax-error",
  "elapsed": 0.0067135039716959,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "\n|-fold_left Cplus (map (fun k : nat => ((1 + Ci) / sqrt 2) ^ k ^ 2) (seq 1 12))\n  0 *\nfold_left Cplus\n  (map (fun k : nat => 1 / ((1 + Ci) / sqrt 2) ^ k ^ 2) (seq 1 12)) 0 =\n36"
  ],
  "success": false,
  "tactic": "set s := sqrt 2.",
  "verified_prefix": [
    "intros z Hz.",
    "subst z."
  ]
}
```

### gpt-5.6-luna/terra/amc12a_2020_p21

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12a_2020_p21__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03964068; 30 completions; 138.691 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'incomplete-proof': 2, 'no-witness': 1, 'prover-crash': 4, 'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 30,
  "category": "prover-crash",
  "elapsed": 15.773473598994315,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "\n|-NoDup\n  (flat_map\n     (fun i : nat =>\n      flat_map\n        (fun j : nat =>\n         map (fun k : nat => 2 ^ i * 3 ^ j * (5 * 5 * 5) * 7 ^ k)\n           (0 :: 1 :: nil))\n        (1 :: 2 :: 3 :: 4 :: nil))\n     (3 :: 4 :: 5 :: 6 :: 7 :: 8 :: nil))",
    "\n|-(forall n : nat,\n In n\n   (flat_map\n      (fun i : nat =>\n       flat_map\n         (fun j : nat =>\n          map (fun k : nat => 2 ^ i * 3 ^ j * (5 * 5 * 5) * 7 ^ k)\n            (0 :: 1 :: nil))\n         (1 :: 2 :: 3 :: 4 :: nil))\n      (3 :: 4 :: 5 :: 6 :: 7 :: 8 :: nil)) <->\n satisfies_condition n) /\\\nlength\n  (flat_map\n     (fun i : nat =>\n      flat_map\n        (fun j : nat =>\n         map (fun k : nat => 2 ^ i * 3 ^ j * (5 * 5 * 5) * 7 ^ k)\n           (0 :: 1 :: nil))\n        (1 :: 2 :: 3 :: 4 :: nil))\n     (3 :: 4 :: 5 :: 6 :: 7 :: 8 :: nil)) =\n48"
  ],
  "success": false,
  "tactic": "- native_compute.",
  "verified_prefix": [
    "exists (flat_map (fun i => flat_map (fun j => map (fun k => 2 ^ i * 3 ^ j * (5 * 5 * 5) * 7 ^ k) (0 :: 1 :: nil)) (1 :: 2 :: 3 :: 4 :: nil)) (3 :: 4 :: 5 :: 6 :: 7 :: 8 :: nil)).",
    "split."
  ]
}
```

### gpt-5.6-luna/terra/amc12b_2002_p3

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12b_2002_p3__cross-level0__gpt-5.6-luna__seed0`. Solved; $0.01329684; 12 completions; 2.054 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'other': 1, 'syntax-error': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Unable to find an instance for the variable q.')
```

### gpt-5.6-luna/terra/imo_1960_p2

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1960_p2__cross-level0__gpt-5.6-luna__seed0`. Solved; $0.01879574; 11 completions; 1.728 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-matching-clause': 1, 'syntax-error': 2, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nx : R\nHx : 0 <= 1 + 2 * x\nHneq : (1 - sqrt (1 + 2 * x)) ^ 2 <> 0\nHineq : 4 * x ^ 2 / (1 - sqrt (1 + 2 * x)) ^ 2 < 2 * x + 9\nHsq : sqrt (1 + 2 * x) * sqrt (1 + 2 * x) = 1 + 2 * x\nHpow : (1 - sqrt (1 + 2 * x)) ^ 2 <> 0\nThe term "Hneq" has type "(1 - sqrt (1 + 2 * x)) ^ 2 <> 0"\nwhile it is expected to have type "1 - sqrt (1 + 2 * x) <> 0"\n(cannot unify "1 - sqrt (1 + 2 * x) = 0" and\n"(1 - sqrt (1 + 2 * x)) ^ 2 = 0").')
```

### gpt-5.6-luna/terra/imo_1969_p2

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1969_p2__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03802440; 21 completions; 2.850 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 1, 'ring-failure': 1, 'type-mismatch': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 21,
  "category": "unknown-reference",
  "elapsed": 0.033125425688922405,
  "error": "(-32003, 'Coq: The reference positivity was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm  : y m = 0\nHn  : y n = 0\nN  : nat\nIHN  : forall f0 : nat -> R,\nf0 0%nat = 1 ->\n(forall i : nat, -1 <= f0 i <= 1) ->\n0 < sum_f_R0 (fun i : nat => f0 i / 2 ^ i) N\nf  : nat -> R\nHf0  : f 0%nat = 1\nHfb  : forall i : nat, -1 <= f i <= 1\nHold  : 0 < sum_f_R0 (fun i : nat => f i / 2 ^ i) N\n|-0 < sum_f_R0 (fun i : nat => f i / 2 ^ i) N + f (S N) / (2 * 2 ^ N)"
  ],
  "success": false,
  "tactic": "assert (Hp : 0 < 2 ^ S N) by positivity.",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hm Hn.",
    "assert (Hpos : forall (N : nat) (f : nat -> R), f 0%nat = 1 -> (forall i : nat, -1 <= f i <= 1) -> 0 < sum_f_R0 (fun i => f i / (2 ^ i)) N).",
    "{ induction N as [|N IHN].",
    "- intros f Hf0 Hfb.",
    "simpl.",
    "rewrite Hf0.",
    "lra.",
    "- intros f Hf0 Hfb.",
    "simpl.",
    "assert (Hold : 0 < sum_f_R0 (fun i => f i / (2 ^ i)) N).",
    "{ apply IHN.",
    "exact Hf0.",
    "exact Hfb.",
    "}"
  ]
}
```

### gpt-5.6-luna/terra/imo_1984_p6

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1984_p6__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.02465744; 21 completions; 242.390 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['rocq_seconds']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'already-used': 1, 'prover-crash': 3}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "prover-crash",
  "elapsed": 60.092475386336446,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "destruct H0 as [Ha [Hb [Hc Hd]]].",
    "destruct H2 as [Hab [Hbc Hcd]].",
    "destruct H1 as [Hodd_a [Hodd_b [Hodd_c Hodd_d]]].",
    "destruct Hodd_a as [pa Hpa].",
    "destruct Hodd_b as [pb Hpb].",
    "destruct Hodd_c as [pc Hpc].",
    "destruct Hodd_d as [pd Hpd]."
  ]
}
```

### gpt-5.6-luna/terra/mathd_algebra_282

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_algebra_282__luna-terra-book-medium__gpt-5.6-luna__seed0`. Unsolved; $0.03786028; 27 completions; 17.587 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'already-used': 1, 'incomplete-proof': 2, 'other': 2, 'unknown-reference': 1}`.

First error:

```text
Proof obligations may not be bypassed.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 27,
  "category": "incomplete-proof",
  "elapsed": 0.005238434299826622,
  "error": "(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R, is_rational x -> f x = Rabs (IZR (Int_part x))\nh1  : forall x : R, ~ is_rational x -> f x = IZR (up x) ^ 2\n|-f (Rpower 8 (1 / 3)) + f (- PI) + f (sqrt 50) + f (9 / 2) = 79"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros."
  ]
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_303

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_numbertheory_303__luna-terra-book-medium__gpt-5.6-luna__seed0`. Unsolved; $0.04015400; 26 completions; 37.333 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'already-used': 1, 'no-witness': 1, 'syntax-error': 2, 'unify-failure': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: l is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "unknown-reference",
  "elapsed": 0.034216782078146935,
  "error": "(-32003, 'Coq: The variable d was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "- do 45 destruct d.",
  "verified_prefix": [
    "intros Hl.",
    "assert (classify : forall n : nat, 2 <= n -> 171 mod n = 80 mod n -> 468 mod n = 13 mod n -> n = 7 \\/ n = 13 \\/ n = 91).",
    "{ intros n hn h1 h2.",
    "assert (E171 : 171 = n * (171 / n) + 171 mod n).",
    "{ apply PeanoNat.Nat.div_mod_eq. }",
    "assert (E80 : 80 = n * (80 / n) + 80 mod n).",
    "{ apply PeanoNat.Nat.div_mod_eq. }",
    "rewrite h1 in E171.",
    "assert (Hq : 80 / n <= 171 / n) by nia.",
    "assert (Hd : 91 = n * (171 / n - 80 / n)) by nia.",
    "destruct (171 / n - 80 / n) as [|d].",
    "- simpl in Hd. nia."
  ]
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_37

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_37__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03399562; 30 completions; 216.983 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-witness': 1, 'prover-crash': 13, 'syntax-error': 3}`.

First error:

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 30,
  "category": "prover-crash",
  "elapsed": 7.237603929825127,
  "error": "Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "vm_compute.",
  "verified_prefix": []
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_405

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_405__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03875740; 16 completions; 2.651 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 1, 'other': 1, 'rewrite-no-match': 2, 'syntax-error': 5}`.

First error:

```text
(-32003, "Coq: Syntax error: ')' expected after [ltac_expr] (in [ltac_expr]).")
```

Last submitted proof checkpoint:

```json
{
  "after_request": 16,
  "category": "focus-error",
  "elapsed": 0.30353118013590574,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "a, b, c  : nat\nt  : nat -> nat\nh0  : t 0 = 0\nh1  : t 1 = 1\nh2  : forall n0 : nat, n0 > 1 -> t n0 = t (n0 - 2) + t (n0 - 1)\nh3  : a mod 16 = 5\nh4  : b mod 16 = 10\nh5  : c mod 16 = 15\nE2  : t 2 = 1\nE3  : t 3 = 2\nE4  : t 4 = 3\nE5  : t 5 = 5\nE6  : t 6 = 8\nE7  : t 7 = 13\nE8  : t 8 = 21\nE9  : t 9 = 34\nE10  : t 10 = 55\nE11  : t 11 = 89\nE12  : t 12 = 144\nE13  : t 13 = 233\nE14  : t 14 = 377\nE15  : t 15 = 610\nE16  : t 16 = 987\nE17  : t 17 = 1597\nn, k  : nat\nHk  : t (k + 16) mod 7 = t k mod 7\nHSk  : t (S k + 16) mod 7 = t (S k) mod 7\n|-7 <> 0",
    "a, b, c  : nat\nt  : nat -> nat\nh0  : t 0 = 0\nh1  : t 1 = 1\nh2  : forall n0 : nat, n0 > 1 -> t n0 = t (n0 - 2) + t (n0 - 1)\nh3  : a mod 16 = 5\nh4  : b mod 16 = 10\nh5  : c mod 16 = 15\nE2  : t 2 = 1\nE3  : t 3 = 2\nE4  : t 4 = 3\nE5  : t 5 = 5\nE6  : t 6 = 8\nE7  : t 7 = 13\nE8  : t 8 = 21\nE9  : t 9 = 34\nE10  : t 10 = 55\nE11  : t 11 = 89\nE12  : t 12 = 144\nE13  : t 13 = 233\nE14  : t 14 = 377\nE15  : t 15 = 610\nE16  : t 16 = 987\nE17  : t 17 = 1597\nn, k  : nat\nHk  : t (k + 16) mod 7 = t k mod 7\nHSk  : t (S k + 16) mod 7 = t (S k) mod 7\n|-7 <> 0"
  ],
  "success": false,
  "tactic": "}",
  "verified_prefix": [
    "intros.",
    "assert (E2 : t 2 = 1).",
    "{ rewrite (h2 2 ltac:(lia)).",
    "simpl.",
    "rewrite h0.",
    "rewrite h1.",
    "reflexivity.",
    "}",
    "assert (E3 : t 3 = 2).",
    "{ rewrite (h2 3 ltac:(lia)).",
    "simpl.",
    "rewrite h1.",
    "rewrite E2.",
    "reflexivity.",
    "}",
    "assert (E4 : t 4 = 3).",
    "{ rewrite (h2 4 ltac:(lia)).",
    "simpl.",
    "rewrite E2.",
    "rewrite E3.",
    "reflexivity.",
    "}",
    "assert (E5 : t 5 = 5).",
    "{ rewrite (h2 5 ltac:(lia)).",
    "simpl.",
    "rewrite E3.",
    "rewrite E4.",
    "reflexivity.",
    "}",
    "assert (E6 : t 6 = 8).",
    "{ rewrite (h2 6 ltac:(lia)).",
    "simpl.",
    "rewrite E4.",
    "rewrite E5.",
    "reflexivity.",
    "}",
    "assert (E7 : t 7 = 13).",
    "{ rewrite (h2 7 ltac:(lia)).",
    "simpl.",
    "rewrite E5.",
    "rewrite E6.",
    "reflexivity.",
    "}",
    "assert (E8 : t 8 = 21).",
    "{ rewrite (h2 8 ltac:(lia)).",
    "simpl.",
    "rewrite E6.",
    "rewrite E7.",
    "reflexivity.",
    "}",
    "assert (E9 : t 9 = 34).",
    "{ rewrite (h2 9 ltac:(lia)).",
    "simpl.",
    "rewrite E7.",
    "rewrite E8.",
    "reflexivity.",
    "}",
    "assert (E10 : t 10 = 55).",
    "{ rewrite (h2 10 ltac:(lia)).",
    "simpl.",
    "rewrite E8.",
    "rewrite E9.",
    "reflexivity.",
    "}",
    "assert (E11 : t 11 = 89).",
    "{ rewrite (h2 11 ltac:(lia)).",
    "simpl.",
    "rewrite E9.",
    "rewrite E10.",
    "reflexivity.",
    "}",
    "assert (E12 : t 12 = 144).",
    "{ rewrite (h2 12 ltac:(lia)).",
    "simpl.",
    "rewrite E10.",
    "rewrite E11.",
    "reflexivity.",
    "}",
    "assert (E13 : t 13 = 233).",
    "{ rewrite (h2 13 ltac:(lia)).",
    "simpl.",
    "rewrite E11.",
    "rewrite E12.",
    "reflexivity.",
    "}",
    "assert (E14 : t 14 = 377).",
    "{ rewrite (h2 14 ltac:(lia)).",
    "simpl.",
    "rewrite E12.",
    "rewrite E13.",
    "reflexivity.",
    "}",
    "assert (E15 : t 15 = 610).",
    "{ rewrite (h2 15 ltac:(lia)).",
    "simpl.",
    "rewrite E13.",
    "rewrite E14.",
    "reflexivity.",
    "}",
    "assert (E16 : t 16 = 987).",
    "{ rewrite (h2 16 ltac:(lia)).",
    "simpl.",
    "rewrite E14.",
    "rewrite E15.",
    "reflexivity.",
    "}",
    "assert (E17 : t 17 = 1597).",
    "{ rewrite (h2 17 ltac:(lia)).",
    "simpl.",
    "rewrite E15.",
    "rewrite E16.",
    "reflexivity.",
    "}",
    "assert (Hperiod : forall n, t (n + 16) mod 7 = t n mod 7).",
    "{ intro n.",
    "apply (Nat.pair_induction (fun k => t (k + 16) mod 7 = t k mod 7)).",
    "- intros x y Hxy.",
    "subst y.",
    "reflexivity.",
    "- replace (0 + 16) with 16 by lia.",
    "rewrite E16.",
    "rewrite h0.",
    "reflexivity.",
    "- replace (1 + 16) with 17 by lia.",
    "rewrite E17.",
    "rewrite h1.",
    "reflexivity.",
    "- intros k Hk HSk.",
    "replace (S (S k) + 16) with (k + 2 + 16) by lia.",
    "replace (S (S k)) with (k + 2) by lia.",
    "rewrite (h2 (k + 2 + 16) ltac:(lia)).",
    "rewrite (h2 (k + 2) ltac:(lia)).",
    "replace (k + 2 + 16 - 2) with (k + 16) by lia.",
    "replace (k + 2 + 16 - 1) with (S k + 16) by lia.",
    "replace (k + 2 - 2) with k by lia.",
    "replace (k + 2 - 1) with (S k) by lia.",
    "rewrite (Nat.add_mod (t (k + 16)) (t (S k + 16)) 7).",
    "rewrite (Nat.add_mod (t k) (t (S k)) 7).",
    "rewrite Hk.",
    "rewrite HSk.",
    "reflexivity."
  ]
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_43

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_numbertheory_43__luna-terra-book-medium__gpt-5.6-luna__seed0`. Unsolved; $0.01713406; 20 completions; 247.304 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 11, 'syntax-error': 1}`.

First error:

```text
Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 22.682473247870803,
  "error": "Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "apply (proj2 (Nat.Div0.div_exact (fact 942) (15^233))).",
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15^233).",
    "symmetry."
  ]
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_530

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_530__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03898638; 27 completions; 2.634 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'rewrite-no-match': 1, 'syntax-error': 1, 'type-mismatch': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 27,
  "category": "type-mismatch",
  "elapsed": 0.045558289624750614,
  "error": "(-32003, 'Coq: In environment\\nn, k : nat\\nHn : (0 < n)%nat\\nHk : (0 < k)%nat\\ng, x, y : nat\\nHlt : INR x / INR y < 6\\nHgt : 5 < INR x / INR y\\nHg : g = Nat.gcd n k\\nHg0 : g <> 0%nat\\nHx : n = (x * g)%nat\\nHy : k = (y * g)%nat\\nHgx : (n / g)%nat = x\\nHgy : (k / g)%nat = y\\nHcop : Nat.gcd x y = 1%nat\\nHx0 : x <> 0%nat\\nHy0 : y <> 0%nat\\nHl : Nat.lcm n k = (x * y * g)%nat\\nHgR : 0 < INR g\\nHxR : 0 < INR x\\nHyR : 0 < INR y\\nHratio : INR (x * g) / INR (y * g) = INR x / INR y\\nHcancel : INR x / INR y * INR y = INR x\\nH5R : 5 * INR y < INR x\\nH6R : INR x < 6 * INR y\\nThe term \"H5R\" has type \"5 * INR y < INR x\" while it is expected to have type\\n \"INR 5 * INR y < INR x\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\ng, x, y  : nat\nHlt  : INR x / INR y < 6\nHgt  : 5 < INR x / INR y\nHg  : g = Nat.gcd n k\nHg0  : g <> 0%nat\nHx  : n = (x * g)%nat\nHy  : k = (y * g)%nat\nHgx  : (n / g)%nat = x\nHgy  : (k / g)%nat = y\nHcop  : Nat.gcd x y = 1%nat\nHx0  : x <> 0%nat\nHy0  : y <> 0%nat\nHl  : Nat.lcm n k = (x * y * g)%nat\nHgR  : 0 < INR g\nHxR  : 0 < INR x\nHyR  : 0 < INR y\nHratio  : INR (x * g) / INR (y * g) = INR x / INR y\nHcancel  : INR x / INR y * INR y = INR x\nH5R  : 5 * INR y < INR x\nH6R  : INR x < 6 * INR y\n|-INR 5 * INR y < INR x"
  ],
  "success": false,
  "tactic": "exact H5R.",
  "verified_prefix": [
    "intros n k Hn Hk Hlt Hgt.",
    "remember (Nat.gcd n k) as g eqn:Hg.",
    "assert (Hg0 : g <> 0%nat).",
    "{ intro Hz.",
    "assert (Hzn : n = 0%nat).",
    "{ apply (Nat.gcd_eq_0_l n k).",
    "rewrite <- Hg.",
    "exact Hz.",
    "}",
    "lia.",
    "}",
    "assert (Hdn : Nat.divide g n) by (rewrite Hg; apply Nat.gcd_divide_l).",
    "assert (Hdk : Nat.divide g k) by (rewrite Hg; apply Nat.gcd_divide_r).",
    "destruct Hdn as [x Hx].",
    "destruct Hdk as [y Hy].",
    "assert (Hgx : (n / g)%nat = x).",
    "{ rewrite Hx.",
    "apply Nat.div_mul.",
    "exact Hg0.",
    "}",
    "assert (Hgy : (k / g)%nat = y).",
    "{ rewrite Hy.",
    "apply Nat.div_mul.",
    "exact Hg0.",
    "}",
    "assert (Hcop : Nat.gcd x y = 1%nat).",
    "{ rewrite <- Hgx, <- Hgy.",
    "apply Nat.gcd_div_gcd.",
    "- exact Hg0.",
    "- exact Hg.",
    "}",
    "assert (Hx0 : x <> 0%nat).",
    "{ intro Z.",
    "subst x.",
    "simpl in Hx.",
    "lia.",
    "}",
    "assert (Hy0 : y <> 0%nat).",
    "{ intro Z.",
    "subst y.",
    "simpl in Hy.",
    "lia.",
    "}",
    "assert (Hl : Nat.lcm n k = ((x * y)%nat * g)%nat).",
    "{ rewrite Hx, Hy.",
    "rewrite Nat.lcm_mul_mono_r.",
    "rewrite (proj1 (Nat.gcd_1_lcm_mul x y Hx0 Hy0) Hcop).",
    "reflexivity.",
    "}",
    "rewrite Hl.",
    "rewrite Nat.div_mul.",
    "2: exact Hg0.",
    "assert (HgR : 0 < INR g) by (apply lt_0_INR; lia).",
    "assert (HxR : 0 < INR x) by (apply lt_0_INR; lia).",
    "assert (HyR : 0 < INR y) by (apply lt_0_INR; lia).",
    "rewrite <- INR_IZR_INZ in Hlt, Hgt.",
    "rewrite Hx, Hy in Hlt, Hgt.",
    "rewrite <- (INR_IZR_INZ (y * g)) in Hlt, Hgt.",
    "assert (Hratio : INR (x * g) / INR (y * g) = INR x / INR y).",
    "{ rewrite (mult_INR x g), (mult_INR y g).",
    "field.",
    "split; lra.",
    "}",
    "rewrite Hratio in Hlt, Hgt.",
    "assert (Hcancel : (INR x / INR y) * INR y = INR x).",
    "{ field.",
    "lra.",
    "}",
    "assert (H5R : 5 * INR y < INR x).",
    "{ nra.",
    "}",
    "assert (H6R : INR x < 6 * INR y).",
    "{ nra.",
    "}",
    "assert (H5 : (5 * y < x)%nat).",
    "{ apply INR_lt.",
    "rewrite mult_INR."
  ]
}
```

### gpt-5.6-luna/terra/mathd_numbertheory_64

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_64__cross-level0__gpt-5.6-luna__seed0`. Unsolved; $0.03406324; 28 completions; 16.744 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `unify-failure`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 3, 'other': 3, 'rewrite-no-match': 1, 'unify-failure': 4, 'unknown-reference': 3}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 28,
  "category": "unify-failure",
  "elapsed": 0.43846649024635553,
  "error": "(-32003, 'Coq: In environment\\nx : nat\\nH, H1 :\\n  match\\n    (let (_, H) :=\\n       (fix Ffix (x x0 x1 x2 : nat) {struct x} : nat * nat :=\\n          match x with\\n          | 0 => (x1, x2)\\n          | S x3 =>\\n              match x2 with\\n              | 0 => Ffix x3 x0 (S x1) x0\\n              | S x4 => Ffix x3 x0 x1 x4\\n              end\\n          end)\\n         ((fix Ffix (x x0 : nat) {struct x} : nat :=\\n             match x with\\n             | 0 => x0\\n             | S x1 => S (Ffix x1 x0)\\n             end)\\n            x\\n            (S\\n               (S\\n                  (S\\n                     (S\\n                        (S\\n                           (S\\n                              (S\\n                                 (S\\n                                    (S\\n                                       (S\\n                                          (S\\n                                             (S\\n                                                (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 (S\\n                                                 ((fix Ffix\\n                                                 (x x0 : nat) {struct x} :\\n                                                 nat :=\\n                                                 match x with\\n                                                 | 0 => x0\\n                                                 | S x1 => S (Ffix x1 x0)\\n                                                 end) x 0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\\n         46 0 7 in\\n     H)\\n  with\\n  | 0 => 46\\n  | 1 => 45\\n  | 2 => 44\\n  | 3 => 43\\n  | 4 => 42\\n  | 5 => 41\\n  | 6 => 40\\n  | 7 => 39\\n  | 8 => 38\\n  | 9 => 37\\n  | 10 => 36\\n  | 11 => 35\\n  | 12 => 34\\n  | 13 => 33\\n  | 14 => 32\\n  | 15 => 31\\n  | 16 => 30\\n  | 17 => 29\\n  | 18 => 28\\n  | 19 => 27\\n  | 20 => 26\\n  | 21 => 25\\n  | 22 => 24\\n  | 23 => 23\\n  | 24 => 22\\n  | 25 => 21\\n  | 26 => 20\\n  | 27 => 19\\n  | 28 => 18\\n  | 29 => 17\\n  | 30 => 16\\n  | 31 => 15\\n  | 32 => 14\\n  | 33 => 13\\n  | 34 => 12\\n  | 35 => 11\\n  | 36 => 10\\n  | 37 => 9\\n  | 38 => 8\\n  | 39 => 7\\n  | 40 => 6\\n  | 41 => 5\\n  | 42 => 4\\n  | 43 => 3\\n  | 44 => 2\\n  | 45 => 1\\n  | S\\n    (S\\n     (S\\n      (S\\n       (S\\n        (S\\n         (S\\n          (S\\n           (S\\n            (S\\n             (S\\n              (S\\n               (S\\n                (S\\n                 (S\\n                  (S\\n                   (S\\n                    (S\\n                     (S\\n                      (S\\n                       (S\\n                        (S\\n                         (S\\n                          (S\\n                           (S\\n                            (S\\n                             (S\\n                              (S\\n                               (S\\n                                (S\\n                                 (S\\n                                  (S\\n                                   (S\\n                                    (S\\n                                     (S\\n                                      (S\\n                                       (S\\n                                        (S (S (S (S (S (S (S (S (S _))))))))))))))))))))))))))))))))))))))))))))) =>\\n      0\\n  end = 42\\nUnable to unify \"0 <= ?M5271\" with \"39 <= x\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "x  : nat\nH, H1  : match\n  (let (_, H0) :=\n     (fix Ffix (x0 x1 x2 x3 : nat) {struct x0} : nat * nat :=\n        match x0 with\n        | 0 => (x2, x3)\n        | S H0 =>\n            match x3 with\n            | 0 => Ffix H0 x1 (S x2) x1\n            | S H2 => Ffix H0 x1 x2 H2\n            end\n        end)\n       ((fix Ffix (x0 x1 : nat) {struct x0} : nat :=\n           match x0 with\n           | 0 => x1\n           | S H0 => S (Ffix H0 x1)\n           end)\n          x\n          (S\n             (S\n                (S\n                   (S\n                      (S\n                         (S\n                            (S\n                               (S\n                                  (S\n                                     (S\n                                        (S\n                                           (S\n                                              (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 (S\n                                                 ((fix Ffix\n                                                 (x0 x1 : nat) {struct x0} :\n                                                 nat :=\n                                                 match x0 with\n                                                 | 0 => x1\n                                                 | S H0 => S (Ffix H0 x1)\n                                                 end) x 0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n       46 0 7 in\n   H0)\nwith\n| 0 => 46\n| 1 => 45\n| 2 => 44\n| 3 => 43\n| 4 => 42\n| 5 => 41\n| 6 => 40\n| 7 => 39\n| 8 => 38\n| 9 => 37\n| 10 => 36\n| 11 => 35\n| 12 => 34\n| 13 => 33\n| 14 => 32\n| 15 => 31\n| 16 => 30\n| 17 => 29\n| 18 => 28\n| 19 => 27\n| 20 => 26\n| 21 => 25\n| 22 => 24\n| 23 => 23\n| 24 => 22\n| 25 => 21\n| 26 => 20\n| 27 => 19\n| 28 => 18\n| 29 => 17\n| 30 => 16\n| 31 => 15\n| 32 => 14\n| 33 => 13\n| 34 => 12\n| 35 => 11\n| 36 => 10\n| 37 => 9\n| 38 => 8\n| 39 => 7\n| 40 => 6\n| 41 => 5\n| 42 => 4\n| 43 => 3\n| 44 => 2\n| 45 => 1\n| S\n  (S\n   (S\n    (S\n     (S\n      (S\n       (S\n        (S\n         (S\n          (S\n           (S\n            (S\n             (S\n              (S\n               (S\n                (S\n                 (S\n                  (S\n                   (S\n                    (S\n                     (S\n                      (S\n                       (S\n                        (S\n                         (S\n                          (S\n                           (S\n                            (S\n                             (S\n                              (S\n                               (S\n                                (S\n                                 (S\n                                  (S\n                                   (S\n                                    (S\n                                     (S\n                                      (S (S (S (S (S (S (S (S (S _))))))))))))))))))))))))))))))))))))))))))))) =>\n    0\nend = 42\n|-39 <= x"
  ],
  "success": false,
  "tactic": "all: apply le_0_n.",
  "verified_prefix": [
    "split.",
    "- vm_compute.",
    "reflexivity.",
    "- intros x H.",
    "do 39 (try destruct x; simpl in H; try constructor).",
    "all: try (vm_compute in H; inversion H).",
    "all: repeat apply le_S."
  ]
}
```

### gpt-5.6-terra/luna/aime_1984_p7

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1984_p7__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.37697820; 14 completions; 2.928 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-matching-clause': 2, 'rewrite-no-match': 6, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "f 1000" in the current goal.')
```

### gpt-5.6-terra/luna/aime_1991_p6

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1991_p6__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.34369540; 17 completions; 48.619 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'already-used': 1, 'no-applicable-tactic': 1, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference Z.le_of_not_gt was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 17,
  "category": "type-mismatch",
  "elapsed": 11.49382543656975,
  "error": "(-32003, 'Coq: In environment\\nr : R\\nHsum :\\n  (Int_part (r + 19 / 100) + Int_part (r + 20 / 100) +\\n   Int_part (r + 21 / 100) + Int_part (r + 22 / 100) +\\n   Int_part (r + 23 / 100) + Int_part (r + 24 / 100) +\\n   Int_part (r + 25 / 100) + Int_part (r + 26 / 100) +\\n   Int_part (r + 27 / 100) + Int_part (r + 28 / 100) +\\n   Int_part (r + 29 / 100) + Int_part (r + 30 / 100) +\\n   Int_part (r + 31 / 100) + Int_part (r + 32 / 100) +\\n   Int_part (r + 33 / 100) + Int_part (r + 34 / 100) +\\n   Int_part (r + 35 / 100) + Int_part (r + 36 / 100) +\\n   Int_part (r + 37 / 100) + Int_part (r + 38 / 100) +\\n   Int_part (r + 39 / 100) + Int_part (r + 40 / 100) +\\n   Int_part (r + 41 / 100) + Int_part (r + 42 / 100) +\\n   Int_part (r + 43 / 100) + Int_part (r + 44 / 100) +\\n   Int_part (r + 45 / 100) + Int_part (r + 46 / 100) +\\n   Int_part (r + 47 / 100) + Int_part (r + 48 / 100) +\\n   Int_part (r + 49 / 100) + Int_part (r + 50 / 100) +\\n   Int_part (r + 51 / 100) + Int_part (r + 52 / 100) +\\n   Int_part (r + 53 / 100) + Int_part (r + 54 / 100) +\\n   Int_part (r + 55 / 100) + Int_part (r + 56 / 100) +\\n   Int_part (r + 57 / 100) + Int_part (r + 58 / 100) +\\n   Int_part (r + 59 / 100) + Int_part (r + 60 / 100) +\\n   Int_part (r + 61 / 100) + Int_part (r + 62 / 100) +\\n   Int_part (r + 63 / 100) + Int_part (r + 64 / 100) +\\n   Int_part (r + 65 / 100) + Int_part (r + 66 / 100) +\\n   Int_part (r + 67 / 100) + Int_part (r + 68 / 100) +\\n   Int_part (r + 69 / 100) + Int_part (r + 70 / 100) +\\n   Int_part (r + 71 / 100) + Int_part (r + 72 / 100) +\\n   Int_part (r + 73 / 100) + Int_part (r + 74 / 100) +\\n   Int_part (r + 75 / 100) + Int_part (r + 76 / 100) +\\n   Int_part (r + 77 / 100) + Int_part (r + 78 / 100) +\\n   Int_part (r + 79 / 100) + Int_part (r + 80 / 100) +\\n   Int_part (r + 81 / 100) + Int_part (r + 82 / 100) +\\n   Int_part (r + 83 / 100) + Int_part (r + 84 / 100) +\\n   Int_part (r + 85 / 100) + Int_part (r + 86 / 100) +\\n   Int_part (r + 87 / 100) + Int_part (r + 88 / 100) +\\n   Int_part (r + 89 / 100) + Int_part (r + 90 / 100) +\\n   Int_part (r + 91 / 100))%Z =\\n  546%Z\\nfloor_le : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z\\nfloor_ge_pred : forall x y : R, x < y + 1 -> (Int_part x - 1 <= Int_part y)%Z\\nfloor_le_succ : forall x y : R, y < x + 1 -> (Int_part y <= Int_part x + 1)%Z\\nH : (Int_part (r + 19 / 100) <= Int_part (r + 57 / 100))%Z\\nH0 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 19 / 100))%Z\\nH1 : (Int_part (r + 19 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH2 : (Int_part (r + 20 / 100) <= Int_part (r + 57 / 100))%Z\\nH3 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 20 / 100))%Z\\nH4 : (Int_part (r + 20 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH5 : (Int_part (r + 21 / 100) <= Int_part (r + 57 / 100))%Z\\nH6 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 21 / 100))%Z\\nH7 : (Int_part (r + 21 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH8 : (Int_part (r + 22 / 100) <= Int_part (r + 57 / 100))%Z\\nH9 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 22 / 100))%Z\\nH10 : (Int_part (r + 22 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH11 : (Int_part (r + 23 / 100) <= Int_part (r + 57 / 100))%Z\\nH12 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 23 / 100))%Z\\nH13 : (Int_part (r + 23 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH14 : (Int_part (r + 24 / 100) <= Int_part (r + 57 / 100))%Z\\nH15 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 24 / 100))%Z\\nH16 : (Int_part (r + 24 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH17 : (Int_part (r + 25 / 100) <= Int_part (r + 57 / 100))%Z\\nH18 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 25 / 100))%Z\\nH19 : (Int_part (r + 25 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH20 : (Int_part (r + 26 / 100) <= Int_part (r + 57 / 100))%Z\\nH21 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 26 / 100))%Z\\nH22 : (Int_part (r + 26 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH23 : (Int_part (r + 27 / 100) <= Int_part (r + 57 / 100))%Z\\nH24 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 27 / 100))%Z\\nH25 : (Int_part (r + 27 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH26 : (Int_part (r + 28 / 100) <= Int_part (r + 57 / 100))%Z\\nH27 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 28 / 100))%Z\\nH28 : (Int_part (r + 28 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH29 : (Int_part (r + 29 / 100) <= Int_part (r + 57 / 100))%Z\\nH30 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 29 / 100))%Z\\nH31 : (Int_part (r + 29 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH32 : (Int_part (r + 30 / 100) <= Int_part (r + 57 / 100))%Z\\nH33 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 30 / 100))%Z\\nH34 : (Int_part (r + 30 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH35 : (Int_part (r + 31 / 100) <= Int_part (r + 57 / 100))%Z\\nH36 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 31 / 100))%Z\\nH37 : (Int_part (r + 31 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH38 : (Int_part (r + 32 / 100) <= Int_part (r + 57 / 100))%Z\\nH39 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 32 / 100))%Z\\nH40 : (Int_part (r + 32 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH41 : (Int_part (r + 33 / 100) <= Int_part (r + 57 / 100))%Z\\nH42 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 33 / 100))%Z\\nH43 : (Int_part (r + 33 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH44 : (Int_part (r + 34 / 100) <= Int_part (r + 57 / 100))%Z\\nH45 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 34 / 100))%Z\\nH46 : (Int_part (r + 34 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH47 : (Int_part (r + 35 / 100) <= Int_part (r + 57 / 100))%Z\\nH48 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 35 / 100))%Z\\nH49 : (Int_part (r + 35 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH50 : (Int_part (r + 36 / 100) <= Int_part (r + 57 / 100))%Z\\nH51 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 36 / 100))%Z\\nH52 : (Int_part (r + 36 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH53 : (Int_part (r + 37 / 100) <= Int_part (r + 57 / 100))%Z\\nH54 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 37 / 100))%Z\\nH55 : (Int_part (r + 37 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH56 : (Int_part (r + 38 / 100) <= Int_part (r + 57 / 100))%Z\\nH57 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 38 / 100))%Z\\nH58 : (Int_part (r + 38 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH59 : (Int_part (r + 39 / 100) <= Int_part (r + 57 / 100))%Z\\nH60 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 39 / 100))%Z\\nH61 : (Int_part (r + 39 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH62 : (Int_part (r + 40 / 100) <= Int_part (r + 57 / 100))%Z\\nH63 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 40 / 100))%Z\\nH64 : (Int_part (r + 40 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH65 : (Int_part (r + 41 / 100) <= Int_part (r + 57 / 100))%Z\\nH66 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 41 / 100))%Z\\nH67 : (Int_part (r + 41 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH68 : (Int_part (r + 42 / 100) <= Int_part (r + 57 / 100))%Z\\nH69 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 42 / 100))%Z\\nH70 : (Int_part (r + 42 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH71 : (Int_part (r + 43 / 100) <= Int_part (r + 57 / 100))%Z\\nH72 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 43 / 100))%Z\\nH73 : (Int_part (r + 43 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH74 : (Int_part (r + 44 / 100) <= Int_part (r + 57 / 100))%Z\\nH75 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 44 / 100))%Z\\nH76 : (Int_part (r + 44 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH77 : (Int_part (r + 45 / 100) <= Int_part (r + 57 / 100))%Z\\nH78 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 45 / 100))%Z\\nH79 : (Int_part (r + 45 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH80 : (Int_part (r + 46 / 100) <= Int_part (r + 57 / 100))%Z\\nH81 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 46 / 100))%Z\\nH82 : (Int_part (r + 46 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH83 : (Int_part (r + 47 / 100) <= Int_part (r + 57 / 100))%Z\\nH84 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 47 / 100))%Z\\nH85 : (Int_part (r + 47 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH86 : (Int_part (r + 48 / 100) <= Int_part (r + 57 / 100))%Z\\nH87 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 48 / 100))%Z\\nH88 : (Int_part (r + 48 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH89 : (Int_part (r + 49 / 100) <= Int_part (r + 57 / 100))%Z\\nH90 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 49 / 100))%Z\\nH91 : (Int_part (r + 49 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH92 : (Int_part (r + 50 / 100) <= Int_part (r + 57 / 100))%Z\\nH93 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 50 / 100))%Z\\nH94 : (Int_part (r + 50 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH95 : (Int_part (r + 51 / 100) <= Int_part (r + 57 / 100))%Z\\nH96 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 51 / 100))%Z\\nH97 : (Int_part (r + 51 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH98 : (Int_part (r + 52 / 100) <= Int_part (r + 57 / 100))%Z\\nH99 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 52 / 100))%Z\\nH100 : (Int_part (r + 52 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH101 : (Int_part (r + 53 / 100) <= Int_part (r + 57 / 100))%Z\\nH102 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 53 / 100))%Z\\nH103 : (Int_part (r + 53 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH104 : (Int_part (r + 54 / 100) <= Int_part (r + 57 / 100))%Z\\nH105 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 54 / 100))%Z\\nH106 : (Int_part (r + 54 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH107 : (Int_part (r + 55 / 100) <= Int_part (r + 57 / 100))%Z\\nH108 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 55 / 100))%Z\\nH109 : (Int_part (r + 55 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH110 : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100))%Z\\nH111 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 56 / 100))%Z\\nH112 : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH113 : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100))%Z\\nH114 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 57 / 100))%Z\\nH115 : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100))%Z\\nH116 : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH117 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 58 / 100))%Z\\nH118 : (Int_part (r + 57 / 100) <= Int_part (r + 58 / 100))%Z\\nH119 : (Int_part (r + 58 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH120 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 59 / 100))%Z\\nH121 : (Int_part (r + 57 / 100) <= Int_part (r + 59 / 100))%Z\\nH122 : (Int_part (r + 59 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH123 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 60 / 100))%Z\\nH124 : (Int_part (r + 57 / 100) <= Int_part (r + 60 / 100))%Z\\nH125 : (Int_part (r + 60 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH126 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 61 / 100))%Z\\nH127 : (Int_part (r + 57 / 100) <= Int_part (r + 61 / 100))%Z\\nH128 : (Int_part (r + 61 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH129 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 62 / 100))%Z\\nH130 : (Int_part (r + 57 / 100) <= Int_part (r + 62 / 100))%Z\\nH131 : (Int_part (r + 62 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH132 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 63 / 100))%Z\\nH133 : (Int_part (r + 57 / 100) <= Int_part (r + 63 / 100))%Z\\nH134 : (Int_part (r + 63 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH135 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 64 / 100))%Z\\nH136 : (Int_part (r + 57 / 100) <= Int_part (r + 64 / 100))%Z\\nH137 : (Int_part (r + 64 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH138 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 65 / 100))%Z\\nH139 : (Int_part (r + 57 / 100) <= Int_part (r + 65 / 100))%Z\\nH140 : (Int_part (r + 65 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH141 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 66 / 100))%Z\\nH142 : (Int_part (r + 57 / 100) <= Int_part (r + 66 / 100))%Z\\nH143 : (Int_part (r + 66 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH144 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 67 / 100))%Z\\nH145 : (Int_part (r + 57 / 100) <= Int_part (r + 67 / 100))%Z\\nH146 : (Int_part (r + 67 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH147 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 68 / 100))%Z\\nH148 : (Int_part (r + 57 / 100) <= Int_part (r + 68 / 100))%Z\\nH149 : (Int_part (r + 68 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH150 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 69 / 100))%Z\\nH151 : (Int_part (r + 57 / 100) <= Int_part (r + 69 / 100))%Z\\nH152 : (Int_part (r + 69 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH153 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 70 / 100))%Z\\nH154 : (Int_part (r + 57 / 100) <= Int_part (r + 70 / 100))%Z\\nH155 : (Int_part (r + 70 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH156 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 71 / 100))%Z\\nH157 : (Int_part (r + 57 / 100) <= Int_part (r + 71 / 100))%Z\\nH158 : (Int_part (r + 71 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH159 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 72 / 100))%Z\\nH160 : (Int_part (r + 57 / 100) <= Int_part (r + 72 / 100))%Z\\nH161 : (Int_part (r + 72 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH162 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 73 / 100))%Z\\nH163 : (Int_part (r + 57 / 100) <= Int_part (r + 73 / 100))%Z\\nH164 : (Int_part (r + 73 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH165 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 74 / 100))%Z\\nH166 : (Int_part (r + 57 / 100) <= Int_part (r + 74 / 100))%Z\\nH167 : (Int_part (r + 74 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH168 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 75 / 100))%Z\\nH169 : (Int_part (r + 57 / 100) <= Int_part (r + 75 / 100))%Z\\nH170 : (Int_part (r + 75 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH171 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 76 / 100))%Z\\nH172 : (Int_part (r + 57 / 100) <= Int_part (r + 76 / 100))%Z\\nH173 : (Int_part (r + 76 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH174 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 77 / 100))%Z\\nH175 : (Int_part (r + 57 / 100) <= Int_part (r + 77 / 100))%Z\\nH176 : (Int_part (r + 77 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH177 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 78 / 100))%Z\\nH178 : (Int_part (r + 57 / 100) <= Int_part (r + 78 / 100))%Z\\nH179 : (Int_part (r + 78 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH180 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 79 / 100))%Z\\nH181 : (Int_part (r + 57 / 100) <= Int_part (r + 79 / 100))%Z\\nH182 : (Int_part (r + 79 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH183 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 80 / 100))%Z\\nH184 : (Int_part (r + 57 / 100) <= Int_part (r + 80 / 100))%Z\\nH185 : (Int_part (r + 80 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH186 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 81 / 100))%Z\\nH187 : (Int_part (r + 57 / 100) <= Int_part (r + 81 / 100))%Z\\nH188 : (Int_part (r + 81 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH189 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 82 / 100))%Z\\nH190 : (Int_part (r + 57 / 100) <= Int_part (r + 82 / 100))%Z\\nH191 : (Int_part (r + 82 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH192 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 83 / 100))%Z\\nH193 : (Int_part (r + 57 / 100) <= Int_part (r + 83 / 100))%Z\\nH194 : (Int_part (r + 83 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH195 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 84 / 100))%Z\\nH196 : (Int_part (r + 57 / 100) <= Int_part (r + 84 / 100))%Z\\nH197 : (Int_part (r + 84 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH198 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 85 / 100))%Z\\nH199 : (Int_part (r + 57 / 100) <= Int_part (r + 85 / 100))%Z\\nH200 : (Int_part (r + 85 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH201 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 86 / 100))%Z\\nH202 : (Int_part (r + 57 / 100) <= Int_part (r + 86 / 100))%Z\\nH203 : (Int_part (r + 86 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH204 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 87 / 100))%Z\\nH205 : (Int_part (r + 57 / 100) <= Int_part (r + 87 / 100))%Z\\nH206 : (Int_part (r + 87 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH207 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 88 / 100))%Z\\nH208 : (Int_part (r + 57 / 100) <= Int_part (r + 88 / 100))%Z\\nH209 : (Int_part (r + 88 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH210 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 89 / 100))%Z\\nH211 : (Int_part (r + 57 / 100) <= Int_part (r + 89 / 100))%Z\\nH212 : (Int_part (r + 89 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH213 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 90 / 100))%Z\\nH214 : (Int_part (r + 57 / 100) <= Int_part (r + 90 / 100))%Z\\nH215 : (Int_part (r + 90 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nH216 : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 91 / 100))%Z\\nH217 : (Int_part (r + 57 / 100) <= Int_part (r + 91 / 100))%Z\\nH218 : (Int_part (r + 91 / 100) <= Int_part (r + 57 / 100) + 1)%Z\\nHmid : Int_part (r + 57 / 100) = 8%Z\\nH219 : (Int_part (r + 56 / 100) <= Int_part (r + 56 / 100))%Z\\nH220 : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100))%Z\\nH221 : (Int_part (r + 56 / 100) <= Int_part (r + 58 / 100))%Z\\nH222 : (Int_part (r + 56 / 100) <= Int_part (r + 59 / 100))%Z\\nH223 : (Int_part (r + 56 / 100) <= Int_part (r + 60 / 100))%Z\\nH224 : (Int_part (r + 56 / 100) <= Int_part (r + 61 / 100))%Z\\nH225 : (Int_part (r + 56 / 100) <= Int_part (r + 62 / 100))%Z\\nH226 : (Int_part (r + 56 / 100) <= Int_part (r + 63 / 100))%Z\\nH227 : (Int_part (r + 56 / 100) <= Int_part (r + 64 / 100))%Z\\nH228 : (Int_part (r + 56 / 100) <= Int_part (r + 65 / 100))%Z\\nH229 : (Int_part (r + 56 / 100) <= Int_part (r + 66 / 100))%Z\\nH230 : (Int_part (r + 56 / 100) <= Int_part (r + 67 / 100))%Z\\nH231 : (Int_part (r + 56 / 100) <= Int_part (r + 68 / 100))%Z\\nH232 : (Int_part (r + 56 / 100) <= Int_part (r + 69 / 100))%Z\\nH233 : (Int_part (r + 56 / 100) <= Int_part (r + 70 / 100))%Z\\nH234 : (Int_part (r + 56 / 100) <= Int_part (r + 71 / 100))%Z\\nH235 : (Int_part (r + 56 / 100) <= Int_part (r + 72 / 100))%Z\\nH236 : (Int_part (r + 56 / 100) <= Int_part (r + 73 / 100))%Z\\nH237 : (Int_part (r + 56 / 100) <= Int_part (r + 74 / 100))%Z\\nH238 : (Int_part (r + 56 / 100) <= Int_part (r + 75 / 100))%Z\\nH239 : (Int_part (r + 56 / 100) <= Int_part (r + 76 / 100))%Z\\nH240 : (Int_part (r + 56 / 100) <= Int_part (r + 77 / 100))%Z\\nH241 : (Int_part (r + 56 / 100) <= Int_part (r + 78 / 100))%Z\\nH242 : (Int_part (r + 56 / 100) <= Int_part (r + 79 / 100))%Z\\nH243 : (Int_part (r + 56 / 100) <= Int_part (r + 80 / 100))%Z\\nH244 : (Int_part (r + 56 / 100) <= Int_part (r + 81 / 100))%Z\\nH245 : (Int_part (r + 56 / 100) <= Int_part (r + 82 / 100))%Z\\nH246 : (Int_part (r + 56 / 100) <= Int_part (r + 83 / 100))%Z\\nH247 : (Int_part (r + 56 / 100) <= Int_part (r + 84 / 100))%Z\\nH248 : (Int_part (r + 56 / 100) <= Int_part (r + 85 / 100))%Z\\nH249 : (Int_part (r + 56 / 100) <= Int_part (r + 86 / 100))%Z\\nH250 : (Int_part (r + 56 / 100) <= Int_part (r + 87 / 100))%Z\\nH251 : (Int_part (r + 56 / 100) <= Int_part (r + 88 / 100))%Z\\nH252 : (Int_part (r + 56 / 100) <= Int_part (r + 89 / 100))%Z\\nH253 : (Int_part (r + 56 / 100) <= Int_part (r + 90 / 100))%Z\\nH254 : (Int_part (r + 56 / 100) <= Int_part (r + 91 / 100))%Z\\nThe term \"Int_part (r + 56 / 100)\" has type \"Z\"\\nwhile it is expected to have type \"R\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nHsum  : (Int_part (r + 19 / 100) + Int_part (r + 20 / 100) + Int_part (r + 21 / 100) +\n Int_part (r + 22 / 100) + Int_part (r + 23 / 100) + \n Int_part (r + 24 / 100) + Int_part (r + 25 / 100) + \n Int_part (r + 26 / 100) + Int_part (r + 27 / 100) + \n Int_part (r + 28 / 100) + Int_part (r + 29 / 100) + \n Int_part (r + 30 / 100) + Int_part (r + 31 / 100) + \n Int_part (r + 32 / 100) + Int_part (r + 33 / 100) + \n Int_part (r + 34 / 100) + Int_part (r + 35 / 100) + \n Int_part (r + 36 / 100) + Int_part (r + 37 / 100) + \n Int_part (r + 38 / 100) + Int_part (r + 39 / 100) + \n Int_part (r + 40 / 100) + Int_part (r + 41 / 100) + \n Int_part (r + 42 / 100) + Int_part (r + 43 / 100) + \n Int_part (r + 44 / 100) + Int_part (r + 45 / 100) + \n Int_part (r + 46 / 100) + Int_part (r + 47 / 100) + \n Int_part (r + 48 / 100) + Int_part (r + 49 / 100) + \n Int_part (r + 50 / 100) + Int_part (r + 51 / 100) + \n Int_part (r + 52 / 100) + Int_part (r + 53 / 100) + \n Int_part (r + 54 / 100) + Int_part (r + 55 / 100) + \n Int_part (r + 56 / 100) + Int_part (r + 57 / 100) + \n Int_part (r + 58 / 100) + Int_part (r + 59 / 100) + \n Int_part (r + 60 / 100) + Int_part (r + 61 / 100) + \n Int_part (r + 62 / 100) + Int_part (r + 63 / 100) + \n Int_part (r + 64 / 100) + Int_part (r + 65 / 100) + \n Int_part (r + 66 / 100) + Int_part (r + 67 / 100) + \n Int_part (r + 68 / 100) + Int_part (r + 69 / 100) + \n Int_part (r + 70 / 100) + Int_part (r + 71 / 100) + \n Int_part (r + 72 / 100) + Int_part (r + 73 / 100) + \n Int_part (r + 74 / 100) + Int_part (r + 75 / 100) + \n Int_part (r + 76 / 100) + Int_part (r + 77 / 100) + \n Int_part (r + 78 / 100) + Int_part (r + 79 / 100) + \n Int_part (r + 80 / 100) + Int_part (r + 81 / 100) + \n Int_part (r + 82 / 100) + Int_part (r + 83 / 100) + \n Int_part (r + 84 / 100) + Int_part (r + 85 / 100) + \n Int_part (r + 86 / 100) + Int_part (r + 87 / 100) + \n Int_part (r + 88 / 100) + Int_part (r + 89 / 100) + \n Int_part (r + 90 / 100) + Int_part (r + 91 / 100))%Z =\n546%Z\nfloor_le  : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z\nfloor_ge_pred  : forall x y : R, x < y + 1 -> (Int_part x - 1 <= Int_part y)%Z\nfloor_le_succ  : forall x y : R, y < x + 1 -> (Int_part y <= Int_part x + 1)%Z\nH  : (Int_part (r + 19 / 100) <= Int_part (r + 57 / 100))%Z\nH0  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 19 / 100))%Z\nH1  : (Int_part (r + 19 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH2  : (Int_part (r + 20 / 100) <= Int_part (r + 57 / 100))%Z\nH3  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 20 / 100))%Z\nH4  : (Int_part (r + 20 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH5  : (Int_part (r + 21 / 100) <= Int_part (r + 57 / 100))%Z\nH6  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 21 / 100))%Z\nH7  : (Int_part (r + 21 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH8  : (Int_part (r + 22 / 100) <= Int_part (r + 57 / 100))%Z\nH9  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 22 / 100))%Z\nH10  : (Int_part (r + 22 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH11  : (Int_part (r + 23 / 100) <= Int_part (r + 57 / 100))%Z\nH12  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 23 / 100))%Z\nH13  : (Int_part (r + 23 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH14  : (Int_part (r + 24 / 100) <= Int_part (r + 57 / 100))%Z\nH15  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 24 / 100))%Z\nH16  : (Int_part (r + 24 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH17  : (Int_part (r + 25 / 100) <= Int_part (r + 57 / 100))%Z\nH18  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 25 / 100))%Z\nH19  : (Int_part (r + 25 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH20  : (Int_part (r + 26 / 100) <= Int_part (r + 57 / 100))%Z\nH21  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 26 / 100))%Z\nH22  : (Int_part (r + 26 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH23  : (Int_part (r + 27 / 100) <= Int_part (r + 57 / 100))%Z\nH24  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 27 / 100))%Z\nH25  : (Int_part (r + 27 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH26  : (Int_part (r + 28 / 100) <= Int_part (r + 57 / 100))%Z\nH27  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 28 / 100))%Z\nH28  : (Int_part (r + 28 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH29  : (Int_part (r + 29 / 100) <= Int_part (r + 57 / 100))%Z\nH30  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 29 / 100))%Z\nH31  : (Int_part (r + 29 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH32  : (Int_part (r + 30 / 100) <= Int_part (r + 57 / 100))%Z\nH33  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 30 / 100))%Z\nH34  : (Int_part (r + 30 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH35  : (Int_part (r + 31 / 100) <= Int_part (r + 57 / 100))%Z\nH36  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 31 / 100))%Z\nH37  : (Int_part (r + 31 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH38  : (Int_part (r + 32 / 100) <= Int_part (r + 57 / 100))%Z\nH39  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 32 / 100))%Z\nH40  : (Int_part (r + 32 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH41  : (Int_part (r + 33 / 100) <= Int_part (r + 57 / 100))%Z\nH42  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 33 / 100))%Z\nH43  : (Int_part (r + 33 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH44  : (Int_part (r + 34 / 100) <= Int_part (r + 57 / 100))%Z\nH45  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 34 / 100))%Z\nH46  : (Int_part (r + 34 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH47  : (Int_part (r + 35 / 100) <= Int_part (r + 57 / 100))%Z\nH48  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 35 / 100))%Z\nH49  : (Int_part (r + 35 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH50  : (Int_part (r + 36 / 100) <= Int_part (r + 57 / 100))%Z\nH51  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 36 / 100))%Z\nH52  : (Int_part (r + 36 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH53  : (Int_part (r + 37 / 100) <= Int_part (r + 57 / 100))%Z\nH54  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 37 / 100))%Z\nH55  : (Int_part (r + 37 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH56  : (Int_part (r + 38 / 100) <= Int_part (r + 57 / 100))%Z\nH57  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 38 / 100))%Z\nH58  : (Int_part (r + 38 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH59  : (Int_part (r + 39 / 100) <= Int_part (r + 57 / 100))%Z\nH60  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 39 / 100))%Z\nH61  : (Int_part (r + 39 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH62  : (Int_part (r + 40 / 100) <= Int_part (r + 57 / 100))%Z\nH63  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 40 / 100))%Z\nH64  : (Int_part (r + 40 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH65  : (Int_part (r + 41 / 100) <= Int_part (r + 57 / 100))%Z\nH66  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 41 / 100))%Z\nH67  : (Int_part (r + 41 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH68  : (Int_part (r + 42 / 100) <= Int_part (r + 57 / 100))%Z\nH69  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 42 / 100))%Z\nH70  : (Int_part (r + 42 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH71  : (Int_part (r + 43 / 100) <= Int_part (r + 57 / 100))%Z\nH72  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 43 / 100))%Z\nH73  : (Int_part (r + 43 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH74  : (Int_part (r + 44 / 100) <= Int_part (r + 57 / 100))%Z\nH75  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 44 / 100))%Z\nH76  : (Int_part (r + 44 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH77  : (Int_part (r + 45 / 100) <= Int_part (r + 57 / 100))%Z\nH78  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 45 / 100))%Z\nH79  : (Int_part (r + 45 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH80  : (Int_part (r + 46 / 100) <= Int_part (r + 57 / 100))%Z\nH81  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 46 / 100))%Z\nH82  : (Int_part (r + 46 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH83  : (Int_part (r + 47 / 100) <= Int_part (r + 57 / 100))%Z\nH84  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 47 / 100))%Z\nH85  : (Int_part (r + 47 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH86  : (Int_part (r + 48 / 100) <= Int_part (r + 57 / 100))%Z\nH87  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 48 / 100))%Z\nH88  : (Int_part (r + 48 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH89  : (Int_part (r + 49 / 100) <= Int_part (r + 57 / 100))%Z\nH90  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 49 / 100))%Z\nH91  : (Int_part (r + 49 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH92  : (Int_part (r + 50 / 100) <= Int_part (r + 57 / 100))%Z\nH93  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 50 / 100))%Z\nH94  : (Int_part (r + 50 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH95  : (Int_part (r + 51 / 100) <= Int_part (r + 57 / 100))%Z\nH96  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 51 / 100))%Z\nH97  : (Int_part (r + 51 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH98  : (Int_part (r + 52 / 100) <= Int_part (r + 57 / 100))%Z\nH99  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 52 / 100))%Z\nH100  : (Int_part (r + 52 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH101  : (Int_part (r + 53 / 100) <= Int_part (r + 57 / 100))%Z\nH102  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 53 / 100))%Z\nH103  : (Int_part (r + 53 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH104  : (Int_part (r + 54 / 100) <= Int_part (r + 57 / 100))%Z\nH105  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 54 / 100))%Z\nH106  : (Int_part (r + 54 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH107  : (Int_part (r + 55 / 100) <= Int_part (r + 57 / 100))%Z\nH108  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 55 / 100))%Z\nH109  : (Int_part (r + 55 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH110  : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100))%Z\nH111  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 56 / 100))%Z\nH112  : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH113  : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100))%Z\nH114  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 57 / 100))%Z\nH115  : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100))%Z\nH116  : (Int_part (r + 57 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH117  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 58 / 100))%Z\nH118  : (Int_part (r + 57 / 100) <= Int_part (r + 58 / 100))%Z\nH119  : (Int_part (r + 58 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH120  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 59 / 100))%Z\nH121  : (Int_part (r + 57 / 100) <= Int_part (r + 59 / 100))%Z\nH122  : (Int_part (r + 59 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH123  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 60 / 100))%Z\nH124  : (Int_part (r + 57 / 100) <= Int_part (r + 60 / 100))%Z\nH125  : (Int_part (r + 60 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH126  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 61 / 100))%Z\nH127  : (Int_part (r + 57 / 100) <= Int_part (r + 61 / 100))%Z\nH128  : (Int_part (r + 61 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH129  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 62 / 100))%Z\nH130  : (Int_part (r + 57 / 100) <= Int_part (r + 62 / 100))%Z\nH131  : (Int_part (r + 62 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH132  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 63 / 100))%Z\nH133  : (Int_part (r + 57 / 100) <= Int_part (r + 63 / 100))%Z\nH134  : (Int_part (r + 63 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH135  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 64 / 100))%Z\nH136  : (Int_part (r + 57 / 100) <= Int_part (r + 64 / 100))%Z\nH137  : (Int_part (r + 64 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH138  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 65 / 100))%Z\nH139  : (Int_part (r + 57 / 100) <= Int_part (r + 65 / 100))%Z\nH140  : (Int_part (r + 65 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH141  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 66 / 100))%Z\nH142  : (Int_part (r + 57 / 100) <= Int_part (r + 66 / 100))%Z\nH143  : (Int_part (r + 66 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH144  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 67 / 100))%Z\nH145  : (Int_part (r + 57 / 100) <= Int_part (r + 67 / 100))%Z\nH146  : (Int_part (r + 67 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH147  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 68 / 100))%Z\nH148  : (Int_part (r + 57 / 100) <= Int_part (r + 68 / 100))%Z\nH149  : (Int_part (r + 68 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH150  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 69 / 100))%Z\nH151  : (Int_part (r + 57 / 100) <= Int_part (r + 69 / 100))%Z\nH152  : (Int_part (r + 69 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH153  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 70 / 100))%Z\nH154  : (Int_part (r + 57 / 100) <= Int_part (r + 70 / 100))%Z\nH155  : (Int_part (r + 70 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH156  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 71 / 100))%Z\nH157  : (Int_part (r + 57 / 100) <= Int_part (r + 71 / 100))%Z\nH158  : (Int_part (r + 71 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH159  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 72 / 100))%Z\nH160  : (Int_part (r + 57 / 100) <= Int_part (r + 72 / 100))%Z\nH161  : (Int_part (r + 72 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH162  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 73 / 100))%Z\nH163  : (Int_part (r + 57 / 100) <= Int_part (r + 73 / 100))%Z\nH164  : (Int_part (r + 73 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH165  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 74 / 100))%Z\nH166  : (Int_part (r + 57 / 100) <= Int_part (r + 74 / 100))%Z\nH167  : (Int_part (r + 74 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH168  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 75 / 100))%Z\nH169  : (Int_part (r + 57 / 100) <= Int_part (r + 75 / 100))%Z\nH170  : (Int_part (r + 75 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH171  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 76 / 100))%Z\nH172  : (Int_part (r + 57 / 100) <= Int_part (r + 76 / 100))%Z\nH173  : (Int_part (r + 76 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH174  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 77 / 100))%Z\nH175  : (Int_part (r + 57 / 100) <= Int_part (r + 77 / 100))%Z\nH176  : (Int_part (r + 77 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH177  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 78 / 100))%Z\nH178  : (Int_part (r + 57 / 100) <= Int_part (r + 78 / 100))%Z\nH179  : (Int_part (r + 78 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH180  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 79 / 100))%Z\nH181  : (Int_part (r + 57 / 100) <= Int_part (r + 79 / 100))%Z\nH182  : (Int_part (r + 79 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH183  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 80 / 100))%Z\nH184  : (Int_part (r + 57 / 100) <= Int_part (r + 80 / 100))%Z\nH185  : (Int_part (r + 80 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH186  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 81 / 100))%Z\nH187  : (Int_part (r + 57 / 100) <= Int_part (r + 81 / 100))%Z\nH188  : (Int_part (r + 81 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH189  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 82 / 100))%Z\nH190  : (Int_part (r + 57 / 100) <= Int_part (r + 82 / 100))%Z\nH191  : (Int_part (r + 82 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH192  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 83 / 100))%Z\nH193  : (Int_part (r + 57 / 100) <= Int_part (r + 83 / 100))%Z\nH194  : (Int_part (r + 83 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH195  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 84 / 100))%Z\nH196  : (Int_part (r + 57 / 100) <= Int_part (r + 84 / 100))%Z\nH197  : (Int_part (r + 84 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH198  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 85 / 100))%Z\nH199  : (Int_part (r + 57 / 100) <= Int_part (r + 85 / 100))%Z\nH200  : (Int_part (r + 85 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH201  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 86 / 100))%Z\nH202  : (Int_part (r + 57 / 100) <= Int_part (r + 86 / 100))%Z\nH203  : (Int_part (r + 86 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH204  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 87 / 100))%Z\nH205  : (Int_part (r + 57 / 100) <= Int_part (r + 87 / 100))%Z\nH206  : (Int_part (r + 87 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH207  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 88 / 100))%Z\nH208  : (Int_part (r + 57 / 100) <= Int_part (r + 88 / 100))%Z\nH209  : (Int_part (r + 88 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH210  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 89 / 100))%Z\nH211  : (Int_part (r + 57 / 100) <= Int_part (r + 89 / 100))%Z\nH212  : (Int_part (r + 89 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH213  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 90 / 100))%Z\nH214  : (Int_part (r + 57 / 100) <= Int_part (r + 90 / 100))%Z\nH215  : (Int_part (r + 90 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nH216  : (Int_part (r + 57 / 100) - 1 <= Int_part (r + 91 / 100))%Z\nH217  : (Int_part (r + 57 / 100) <= Int_part (r + 91 / 100))%Z\nH218  : (Int_part (r + 91 / 100) <= Int_part (r + 57 / 100) + 1)%Z\nHmid  : Int_part (r + 57 / 100) = 8%Z\nH219  : (Int_part (r + 56 / 100) <= Int_part (r + 56 / 100))%Z\nH220  : (Int_part (r + 56 / 100) <= Int_part (r + 57 / 100))%Z\nH221  : (Int_part (r + 56 / 100) <= Int_part (r + 58 / 100))%Z\nH222  : (Int_part (r + 56 / 100) <= Int_part (r + 59 / 100))%Z\nH223  : (Int_part (r + 56 / 100) <= Int_part (r + 60 / 100))%Z\nH224  : (Int_part (r + 56 / 100) <= Int_part (r + 61 / 100))%Z\nH225  : (Int_part (r + 56 / 100) <= Int_part (r + 62 / 100))%Z\nH226  : (Int_part (r + 56 / 100) <= Int_part (r + 63 / 100))%Z\nH227  : (Int_part (r + 56 / 100) <= Int_part (r + 64 / 100))%Z\nH228  : (Int_part (r + 56 / 100) <= Int_part (r + 65 / 100))%Z\nH229  : (Int_part (r + 56 / 100) <= Int_part (r + 66 / 100))%Z\nH230  : (Int_part (r + 56 / 100) <= Int_part (r + 67 / 100))%Z\nH231  : (Int_part (r + 56 / 100) <= Int_part (r + 68 / 100))%Z\nH232  : (Int_part (r + 56 / 100) <= Int_part (r + 69 / 100))%Z\nH233  : (Int_part (r + 56 / 100) <= Int_part (r + 70 / 100))%Z\nH234  : (Int_part (r + 56 / 100) <= Int_part (r + 71 / 100))%Z\nH235  : (Int_part (r + 56 / 100) <= Int_part (r + 72 / 100))%Z\nH236  : (Int_part (r + 56 / 100) <= Int_part (r + 73 / 100))%Z\nH237  : (Int_part (r + 56 / 100) <= Int_part (r + 74 / 100))%Z\nH238  : (Int_part (r + 56 / 100) <= Int_part (r + 75 / 100))%Z\nH239  : (Int_part (r + 56 / 100) <= Int_part (r + 76 / 100))%Z\nH240  : (Int_part (r + 56 / 100) <= Int_part (r + 77 / 100))%Z\nH241  : (Int_part (r + 56 / 100) <= Int_part (r + 78 / 100))%Z\nH242  : (Int_part (r + 56 / 100) <= Int_part (r + 79 / 100))%Z\nH243  : (Int_part (r + 56 / 100) <= Int_part (r + 80 / 100))%Z\nH244  : (Int_part (r + 56 / 100) <= Int_part (r + 81 / 100))%Z\nH245  : (Int_part (r + 56 / 100) <= Int_part (r + 82 / 100))%Z\nH246  : (Int_part (r + 56 / 100) <= Int_part (r + 83 / 100))%Z\nH247  : (Int_part (r + 56 / 100) <= Int_part (r + 84 / 100))%Z\nH248  : (Int_part (r + 56 / 100) <= Int_part (r + 85 / 100))%Z\nH249  : (Int_part (r + 56 / 100) <= Int_part (r + 86 / 100))%Z\nH250  : (Int_part (r + 56 / 100) <= Int_part (r + 87 / 100))%Z\nH251  : (Int_part (r + 56 / 100) <= Int_part (r + 88 / 100))%Z\nH252  : (Int_part (r + 56 / 100) <= Int_part (r + 89 / 100))%Z\nH253  : (Int_part (r + 56 / 100) <= Int_part (r + 90 / 100))%Z\nH254  : (Int_part (r + 56 / 100) <= Int_part (r + 91 / 100))%Z\n|-Int_part (100 * r) = 743%Z"
  ],
  "success": false,
  "tactic": "assert (H_floor_56_le : Int_part (r + 56 / 100) <= 7%Z) by lia.",
  "verified_prefix": [
    "intros r Hsum.",
    "unfold range_sum in Hsum.",
    "cbn in Hsum.",
    "assert (floor_le : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z).",
    "{ intros x y Hxy.",
    "apply Z.le_ngt.",
    "intro H.",
    "assert (Hi : (Int_part y + 1 <= Int_part x)%Z) by lia.",
    "destruct (base_Int_part x) as [Hx1 Hx2].",
    "destruct (base_Int_part y) as [Hy1 Hy2].",
    "pose proof (IZR_le _ _ Hi) as HiR.",
    "rewrite plus_IZR in HiR.",
    "cbn in HiR.",
    "lra.",
    "}",
    "assert (floor_ge_pred : forall x y : R, x < y + 1 -> (Int_part x - 1 <= Int_part y)%Z).",
    "{ intros x y Hxy.",
    "apply Z.le_ngt.",
    "intro H.",
    "assert (Hi : (Int_part y + 1 <= Int_part x - 1)%Z) by lia.",
    "destruct (base_Int_part x) as [Hx1 Hx2].",
    "destruct (base_Int_part y) as [Hy1 Hy2].",
    "pose proof (IZR_le _ _ Hi) as HiR.",
    "rewrite plus_IZR in HiR.",
    "rewrite minus_IZR in HiR.",
    "cbn in HiR.",
    "lra.",
    "}",
    "assert (floor_le_succ : forall x y : R, y < x + 1 -> (Int_part y <= Int_part x + 1)%Z).",
    "{ intros x y Hxy.",
    "apply Z.le_ngt.",
    "intro H.",
    "assert (Hi : (Int_part x + 1 + 1 <= Int_part y)%Z) by lia.",
    "destruct (base_Int_part x) as [Hx1 Hx2].",
    "destruct (base_Int_part y) as [Hy1 Hy2].",
    "pose proof (IZR_le _ _ Hi) as HiR.",
    "rewrite plus_IZR in HiR.",
    "rewrite plus_IZR in HiR.",
    "cbn in HiR.",
    "lra.",
    "}",
    "let rec bounds t := lazymatch t with | (?a + ?b)%Z => bounds a; bounds b | Int_part ?x => first [ let H := fresh in pose proof (floor_le x (r + 57 / 100) ltac:(lra)) as H | idtac ]; first [ let H := fresh in pose proof (floor_ge_pred (r + 57 / 100) x ltac:(lra)) as H | idtac ]; first [ let H := fresh in pose proof (floor_le (r + 57 / 100) x ltac:(lra)) as H | idtac ]; first [ let H := fresh in pose proof (floor_le_succ (r + 57 / 100) x ltac:(lra)) as H | idtac ] | _ => idtac end in lazymatch type of Hsum with | ?s = _ => bounds s end.",
    "assert (Hmid : Int_part (r + 57 / 100) = 8%Z) by lia.",
    "let rec tail_bounds t := lazymatch t with | (?a + ?b)%Z => tail_bounds a; tail_bounds b | Int_part ?x => first [ let H := fresh in pose proof (floor_le (r + 56 / 100) x ltac:(lra)) as H | idtac ] | _ => idtac end in lazymatch type of Hsum with | ?s = _ => tail_bounds s end."
  ]
}
```

### gpt-5.6-terra/luna/aime_1991_p9

Source: `experiments/output/ace_capacity_20260912/cross/configs/aime_1991_p9__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.15949140; 21 completions; 1.530 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

### gpt-5.6-terra/luna/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_capacity_20260912/cross/configs/algebra_others_exirrpowirrrat__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.36389100; 26 completions; 2.138 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'subproof-incomplete': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nThe term "0" has type "nat" while it is expected to have type "R".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "no-applicable-tactic",
  "elapsed": 0.019364400766789913,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHeq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\nHtwo  : (0 <= 2)%R\nHs  : (sqrt 2 * sqrt 2)%R = 2%R\nHinv  : (IZR q * / IZR q)%R = 1%R\n|-(IZR p * / IZR q * IZR q)%R = IZR p"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "assert (Hirr : irrational (sqrt 2)).",
    "{ unfold irrational.",
    "intros [p [q [Hq Heq]]].",
    "assert (HqR : IZR q <> 0%R) by exact (not_0_IZR q Hq).",
    "assert (Htwo : (0 <= 2)%R) by lra.",
    "assert (Hs : (sqrt 2 * sqrt 2 = 2)%R) by exact (sqrt_sqrt 2 Htwo).",
    "assert (Hinv : (IZR q * / IZR q = 1)%R) by exact (Rinv_r _ HqR).",
    "assert (Hcross : (sqrt 2 * IZR q = IZR p)%R).",
    "{ rewrite Heq.",
    "unfold Rdiv."
  ]
}
```

### gpt-5.6-terra/luna/amc12_2001_p21

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12_2001_p21__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.39722740; 20 completions; 168.870 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-witness`; added goal views: 0. Error counts: `{'no-witness': 3, 'prover-crash': 6, 'syntax-error': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference interval_cases was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "no-witness",
  "elapsed": 1.5124096469953656,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "+ lia.",
  "verified_prefix": [
    "intros a b c d Habcd Hab Hbc Hcd.",
    "simpl in Habcd.",
    "assert (Ha : 0 < a) by nia.",
    "assert (Hb : 0 < b) by nia.",
    "assert (Hc : 0 < c) by nia.",
    "assert (Hd : 0 < d) by nia.",
    "assert (Hab' : (a + 1) * (b + 1) = 525) by nia.",
    "assert (Hbc' : (b + 1) * (c + 1) = 147) by nia.",
    "assert (Hcd' : (c + 1) * (d + 1) = 105) by nia.",
    "assert (Hdsmall : d <= 14) by nia.",
    "clear Hab Hbc Hcd Ha Hb Hc Hd.",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d].",
    "- assert (Hc20 : c = 20) by lia.",
    "subst c.",
    "assert (Hb6 : b = 6) by lia.",
    "subst b.",
    "assert (Ha74 : a = 74) by lia.",
    "subst a.",
    "simpl in Habcd.",
    "lia.",
    "- destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d]; [lia|].",
    "destruct d as [|d].",
    "+ assert (Hc6 : c = 6) by lia.",
    "subst c.",
    "assert (Hb20 : b = 20) by lia.",
    "subst b.",
    "assert (Ha24 : a = 24) by lia.",
    "subst a.",
    "easy."
  ]
}
```

### gpt-5.6-terra/luna/amc12a_2008_p4

Source: `experiments/output/ace_attribution_20260912/swaps/configs/amc12a_2008_p4__terra-luna-book-medium__gpt-5.6-terra__seed0`. Solved; $0.32283520; 11 completions; 98.812 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 2, 'incomplete-proof': 1, 'no-applicable-tactic': 1, 'prover-crash': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof amc12a_2008_p4): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

### gpt-5.6-terra/luna/amc12a_2019_p21

Source: `experiments/output/ace_attribution_20260912/swaps/configs/amc12a_2019_p21__terra-luna-book-medium__gpt-5.6-terra__seed0`. Unsolved; $0.25227640; 39 completions; 1.804 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-proof-submission`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-terra/luna/amc12a_2020_p21

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12a_2020_p21__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.36408720; 33 completions; 18.031 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 6, 'prover-crash': 1, 'subproof-incomplete': 1, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: Stack overflow.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 33,
  "category": "incomplete-proof",
  "elapsed": 0.006326565518975258,
  "error": "(-32003, 'Coq:  (in proof amc12a_2020_p21): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "\n|-exists l : list nat,\n  NoDup l /\\\n  (forall n : nat,\n   In n l <->\n   (exists k : nat, n = k * 5) /\\\n   Nat.lcm (5 * fact 4) n = 5 * Nat.gcd (10 * fact 9) n) /\\\n  length l = 48"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "unfold satisfies_condition.",
    "change (exists l : list nat, NoDup l /\\ (forall n : nat, In n l <-> (exists k : nat, n = k * 5) /\\ Nat.lcm (5 * fact 4) n = 5 * Nat.gcd (10 * fact 9) n) /\\ length l = 48)."
  ]
}
```

### gpt-5.6-terra/luna/amc12b_2002_p3

Source: `experiments/output/ace_capacity_20260912/cross/configs/amc12b_2002_p3__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.09997620; 10 completions; 1.670 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The reference by_contra was not found in the current environment.')
```

### gpt-5.6-terra/luna/imo_1960_p2

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1960_p2__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.10742380; 13 completions; 0.927 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-terra/luna/imo_1969_p2

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1969_p2__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.34530600; 36 completions; 2.394 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `focus-error`; added goal views: 0. Error counts: `{'focus-error': 1}`.

First error:

```text
(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "focus-error",
  "elapsed": 0.4888580171391368,
  "error": "(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm  : y m = 0\nHn  : y n = 0\n|-forall N : nat, 0 < 2 ^ N",
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm  : y m = 0\nHn  : y n = 0\nHp  : forall N : nat, 0 < (2 : R) ^ N\n|-exists t : Z, m - n = IZR t * PI"
  ],
  "success": false,
  "tactic": "{ intro N. apply pow_pos. lra. }",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hm Hn.",
    "assert (Hp : forall N : nat, 0 < (2 : R) ^ N)."
  ]
}
```

### gpt-5.6-terra/luna/imo_1984_p6

Source: `experiments/output/ace_capacity_20260912/cross/configs/imo_1984_p6__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.33570900; 30 completions; 249.456 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['rocq_seconds']`; last category: `prover-crash`; added goal views: 0. Error counts: `{'already-used': 1, 'prover-crash': 2, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "prover-crash",
  "elapsed": 60.092414184473455,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "assert (Hs : b + c < a + d) by nia.",
  "verified_prefix": [
    "destruct H0 as [Ha [Hb [Hc Hd]]].",
    "destruct H1 as [Haodd [Hbodd [Hcodd Hdodd]]].",
    "unfold Nat.Odd in Haodd, Hbodd, Hcodd, Hdodd.",
    "destruct Haodd as [pa Ea].",
    "destruct Hbodd as [pb Eb].",
    "destruct Hcodd as [pc Ec].",
    "destruct Hdodd as [pd Ed].",
    "destruct H2 as [Hab [Hbc Hcd]]."
  ]
}
```

### gpt-5.6-terra/luna/mathd_algebra_282

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_algebra_282__terra-luna-book-medium__gpt-5.6-terra__seed0`. Unsolved; $0.39551040; 26 completions; 29.552 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `ring-failure`; added goal views: 0. Error counts: `{'focus-error': 1, 'incomplete-proof': 3, 'rewrite-no-match': 1, 'ring-failure': 1, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "ring-failure",
  "elapsed": 0.007782503962516785,
  "error": "(-32003, 'Coq: Tactic failure: not a valid ring equation.')",
  "outcome": "rejected",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R, is_rational x -> f x = Rabs (IZR (Int_part x))\nh1  : forall x : R, ~ is_rational x -> f x = IZR (up x) ^ 2\nHr  : is_rational (Rpower 8 (1 / 3))\nHroot  : Rpower 8 (1 / 3) = 2\nH2  : (2 : R) = INR 2\nHq  : is_rational (9 / 2)\n|-Rabs 2 + f (- PI) + f (sqrt 50) + f (9 / (1 + 1)) = 79"
  ],
  "success": false,
  "tactic": "replace (9 / (1 + 1) : R) with (9 / 2) by ring.",
  "verified_prefix": [
    "intros.",
    "assert (Hr : is_rational (Rpower 8 (1 / 3))).",
    "{ unfold is_rational.",
    "exists 2%Z, 1%Z.",
    "split.",
    "- discriminate.",
    "- assert (H8 : Rpower 2 3 = 8).",
    "{ assert (H3 : INR 3 = (3 : R)).",
    "{ cbv [INR].",
    "ring.",
    "}",
    "rewrite <- H3.",
    "rewrite (Rpower_pow 3 2) by lra.",
    "ring.",
    "}",
    "rewrite <- H8.",
    "rewrite Rpower_mult.",
    "replace (3 * (1 / 3) : R) with 1 by field.",
    "rewrite Rpower_1 by lra.",
    "field.",
    "}",
    "rewrite (h0 _ Hr).",
    "assert (Hroot : Rpower 8 (1 / 3) = 2).",
    "{ assert (H8 : Rpower 2 3 = 8).",
    "{ assert (H3 : INR 3 = (3 : R)).",
    "{ cbv [INR].",
    "ring.",
    "}",
    "rewrite <- H3.",
    "rewrite (Rpower_pow 3 2) by lra.",
    "ring.",
    "}",
    "rewrite <- H8.",
    "rewrite Rpower_mult.",
    "replace (3 * (1 / 3) : R) with 1 by field.",
    "rewrite Rpower_1 by lra.",
    "reflexivity.",
    "}",
    "rewrite Hroot.",
    "assert (H2 : (2 : R) = INR 2).",
    "{ cbv [INR].",
    "ring.",
    "}",
    "rewrite H2.",
    "rewrite Int_part_INR.",
    "simpl.",
    "assert (Hq : is_rational (9 / 2)).",
    "{ unfold is_rational.",
    "exists 9%Z, 2%Z.",
    "split.",
    "- discriminate.",
    "- cbv [IZR].",
    "ring.",
    "}"
  ]
}
```

### gpt-5.6-terra/luna/mathd_numbertheory_303

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_numbertheory_303__terra-luna-book-medium__gpt-5.6-terra__seed0`. Unsolved; $0.39750380; 23 completions; 35.269 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `syntax-error`; added goal views: 0. Error counts: `{'already-used': 1, 'no-witness': 3, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: l is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "syntax-error",
  "elapsed": 0.23382842633873224,
  "error": "(-32003, 'Coq: Syntax error: illegal begin of vernac.')",
  "outcome": "rejected",
  "remaining_goals": [],
  "success": false,
  "tactic": "}.",
  "verified_prefix": [
    "intros Hnd.",
    "assert (HC : forall n : nat, 2 <= n /\\ 171 mod n = 80 mod n /\\ 468 mod n = 13 mod n -> n = 7 \\/ n = 13 \\/ n = 91).",
    "{ intros n [Hn [H1 H2]].",
    "assert (Hnz : n <> 0) by lia.",
    "pose proof (PeanoNat.Nat.div_mod 171 n Hnz) as E1.",
    "pose proof (PeanoNat.Nat.div_mod 80 n Hnz) as E2.",
    "assert (Hr : 171 mod n < n).",
    "{ apply PeanoNat.Nat.mod_upper_bound; exact Hnz. }",
    "assert (Hr' : 80 mod n < n).",
    "{ apply PeanoNat.Nat.mod_upper_bound; exact Hnz. }",
    "assert (Hq : 80 / n < 171 / n).",
    "{ rewrite H1 in E1. nia. }",
    "assert (Hd : PeanoNat.Nat.divide n (7 * 13)).",
    "{ unfold PeanoNat.Nat.divide.",
    "exists (171 / n - 80 / n).",
    "rewrite H1 in E1.",
    "nia.",
    "}",
    "destruct (PeanoNat.Nat.divide_mul_split n 7 13 Hnz Hd) as [q [r [En [Dq Dr]]]].",
    "unfold PeanoNat.Nat.divide in Dq, Dr.",
    "destruct Dq as [u Eu].",
    "destruct Dr as [v Ev].",
    "assert (Hqpos : 0 < q) by nia.",
    "assert (Hrpos : 0 < r) by nia.",
    "assert (Hqcase : q = 1 \\/ q = 7).",
    "{ assert (Hqle : q <= 7) by nia.",
    "destruct q as [|[|[|[|[|[|q]]]]]].",
    "all: nia.",
    "}",
    "assert (Hrcase : r = 1 \\/ r = 13).",
    "{ assert (Hrle : r <= 13) by nia.",
    "destruct r as [|[|[|[|[|[|[|[|[|[|[|[|[|r]]]]]]]]]]]]].",
    "all: nia.",
    "}",
    "destruct Hqcase as [-> | ->]; destruct Hrcase as [-> | ->]; subst n; cbn in Hn |- *; lia."
  ]
}
```

### gpt-5.6-terra/luna/mathd_numbertheory_405

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_405__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.35839420; 14 completions; 46.128 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'already-used': 2, 'focus-error': 1, 'other': 1, 'prover-crash': 1, 'rewrite-no-match': 1, 'syntax-error': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

### gpt-5.6-terra/luna/mathd_numbertheory_43

Source: `experiments/output/ace_attribution_20260912/swaps/configs/mathd_numbertheory_43__terra-luna-book-medium__gpt-5.6-terra__seed0`. Unsolved; $0.21935280; 26 completions; 241.168 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 13, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Out of memory.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "prover-crash",
  "elapsed": 12.90517654363066,
  "error": "ConnectionLost: (-33002, 'the Rocq server closed the connection')",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": null,
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15 ^ 233)."
  ]
}
```

### gpt-5.6-terra/luna/mathd_numbertheory_530

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_530__cross-level0__gpt-5.6-terra__seed0`. Unsolved; $0.37506780; 25 completions; 2.784 verifier seconds.

Terminal: `stopped`; limiting dimensions: `['price']`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'not-convertible': 1, 'syntax-error': 2, 'type-mismatch': 2}`.

First error:

```text
(-32003, 'Coq: In environment\nn, k : nat\nHn : (0 < n)%nat\nHk : (0 < k)%nat\nHlt : IZR (Z.of_nat n) / IZR (Z.of_nat k) < 6\nHgt : 5 < IZR (Z.of_nat n) / IZR (Z.of_nat k)\nd := Nat.gcd n k : nat\nHd : d <> 0%nat\nx : nat\nHx : n = (x * Nat.gcd n k)%nat\ny : nat\nHy : k = (y * Nat.gcd n k)%nat\nThe term "n" has type "nat" while it is expected to have type "R".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "no-applicable-tactic",
  "elapsed": 0.07453626580536366,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\nHlt  : INR n / INR k < 6\nHgt  : 5 < INR n / INR k\nd := Nat.gcd n k : nat\nHd  : d <> 0%nat\nx  : nat\nHx  : n = (x * Nat.gcd n k)%nat\ny  : nat\nHy  : k = (y * Nat.gcd n k)%nat\nHdp  : (0 < d)%nat\nHkr  : 0 < INR k\nHknz  : INR k <> 0\nHcancel  : INR n / INR k * INR k = INR n\nHle  : (n <= 5 * k)%nat\nHrle  : (fix INR (n0 : nat) : R :=\n   match n0 with\n   | 0%nat => 0\n   | 1%nat => 1\n   | S (S _ as n1) => INR n1 + 1\n   end)\n  n <=\n(1 + 1 + 1 + 1 + 1) *\n(fix INR (n0 : nat) : R :=\n   match n0 with\n   | 0%nat => 0\n   | 1%nat => 1\n   | S (S _ as n1) => INR n1 + 1\n   end)\n  k\nHmul  : 5 * INR k < INR n\n|-False"
  ],
  "success": false,
  "tactic": "lra.",
  "verified_prefix": [
    "intros n k Hn Hk Hlt Hgt.",
    "rewrite <- (INR_IZR_INZ n) in Hlt.",
    "rewrite <- (INR_IZR_INZ n) in Hgt.",
    "rewrite <- (INR_IZR_INZ k) in Hlt.",
    "rewrite <- (INR_IZR_INZ k) in Hgt.",
    "set (d := Nat.gcd n k).",
    "assert (Hd : d <> 0%nat).",
    "{ intro Hz.",
    "unfold d in Hz.",
    "pose proof (Nat.gcd_eq_0_l n k Hz).",
    "lia. }",
    "destruct (Nat.gcd_divide_l n k) as [x Hx].",
    "destruct (Nat.gcd_divide_r n k) as [y Hy].",
    "assert (Hdp : (0 < d)%nat) by lia.",
    "assert (Hkr : 0 < INR k).",
    "{ apply lt_0_INR.",
    "exact Hk. }",
    "assert (Hknz : INR k <> 0) by lra.",
    "assert (Hcancel : (INR n / INR k) * INR k = INR n).",
    "{ unfold Rdiv.",
    "replace (INR n * / INR k * INR k) with (INR n * (INR k * / INR k)) by ring.",
    "rewrite Rinv_r by exact Hknz.",
    "ring. }",
    "assert (Hnk : (5 * k < n)%nat).",
    "{ destruct (le_gt_dec n (5 * k)) as [Hle|Hnlt].",
    "- exfalso.",
    "assert (Hrle : INR n <= INR (5 * k)).",
    "{ apply le_INR.",
    "exact Hle. }",
    "rewrite mult_INR in Hrle.",
    "cbv [INR] in Hrle.",
    "assert (Hmul : 5 * INR k < (INR n / INR k) * INR k).",
    "{ apply Rmult_lt_compat_r.",
    "exact Hkr.",
    "exact Hgt. }",
    "rewrite Hcancel in Hmul."
  ]
}
```

### gpt-5.6-terra/luna/mathd_numbertheory_64

Source: `experiments/output/ace_capacity_20260912/cross/configs/mathd_numbertheory_64__cross-level0__gpt-5.6-terra__seed0`. Solved; $0.21826380; 16 completions; 2.081 verifier seconds.

Terminal: `solved`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-matching-clause': 2, 'other': 1, 'syntax-error': 2, 'unknown-reference': 4}`.

First error:

```text
(-32003, 'Coq: The reference omega was not found in the current environment.')
```

### gpt-5.6-terra/none/aime_1984_p7

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1984_p7__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.25273800; 14 completions; 1.651 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'incomplete-proof': 2, 'other': 1, 'rewrite-no-match': 2, 'syntax-error': 2, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof aime_1984_p7): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

### gpt-5.6-terra/none/aime_1991_p6

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1991_p6__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.42626020; 20 completions; 50.916 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `syntax-error`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'syntax-error': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "syntax-error",
  "elapsed": 8.090095710940659,
  "error": "(-32003, \"Coq: Syntax error: 'end' expected after [match_list] (in [ltac_expr]).\")",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nH  : (Int_part (r + 19 / 100) + Int_part (r + 20 / 100) + Int_part (r + 21 / 100) +\n Int_part (r + 22 / 100) + Int_part (r + 23 / 100) + \n Int_part (r + 24 / 100) + Int_part (r + 25 / 100) + \n Int_part (r + 26 / 100) + Int_part (r + 27 / 100) + \n Int_part (r + 28 / 100) + Int_part (r + 29 / 100) + \n Int_part (r + 30 / 100) + Int_part (r + 31 / 100) + \n Int_part (r + 32 / 100) + Int_part (r + 33 / 100) + \n Int_part (r + 34 / 100) + Int_part (r + 35 / 100) + \n Int_part (r + 36 / 100) + Int_part (r + 37 / 100) + \n Int_part (r + 38 / 100) + Int_part (r + 39 / 100) + \n Int_part (r + 40 / 100) + Int_part (r + 41 / 100) + \n Int_part (r + 42 / 100) + Int_part (r + 43 / 100) + \n Int_part (r + 44 / 100) + Int_part (r + 45 / 100) + \n Int_part (r + 46 / 100) + Int_part (r + 47 / 100) + \n Int_part (r + 48 / 100) + Int_part (r + 49 / 100) + \n Int_part (r + 50 / 100) + Int_part (r + 51 / 100) + \n Int_part (r + 52 / 100) + Int_part (r + 53 / 100) + \n Int_part (r + 54 / 100) + Int_part (r + 55 / 100) + \n Int_part (r + 56 / 100) + Int_part (r + 57 / 100) + \n Int_part (r + 58 / 100) + Int_part (r + 59 / 100) + \n Int_part (r + 60 / 100) + Int_part (r + 61 / 100) + \n Int_part (r + 62 / 100) + Int_part (r + 63 / 100) + \n Int_part (r + 64 / 100) + Int_part (r + 65 / 100) + \n Int_part (r + 66 / 100) + Int_part (r + 67 / 100) + \n Int_part (r + 68 / 100) + Int_part (r + 69 / 100) + \n Int_part (r + 70 / 100) + Int_part (r + 71 / 100) + \n Int_part (r + 72 / 100) + Int_part (r + 73 / 100) + \n Int_part (r + 74 / 100) + Int_part (r + 75 / 100) + \n Int_part (r + 76 / 100) + Int_part (r + 77 / 100) + \n Int_part (r + 78 / 100) + Int_part (r + 79 / 100) + \n Int_part (r + 80 / 100) + Int_part (r + 81 / 100) + \n Int_part (r + 82 / 100) + Int_part (r + 83 / 100) + \n Int_part (r + 84 / 100) + Int_part (r + 85 / 100) + \n Int_part (r + 86 / 100) + Int_part (r + 87 / 100) + \n Int_part (r + 88 / 100) + Int_part (r + 89 / 100) + \n Int_part (r + 90 / 100) + Int_part (r + 91 / 100))%Z =\n546%Z\nfloor_mono  : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z\nfloor_add_one  : forall x : R, Int_part (x + 1) = (Int_part x + 1)%Z\n|-Int_part (100 * r) = 743%Z"
  ],
  "success": false,
  "tactic": "let rec early_upper k fuel := lazymatch fuel with | 0 => idtac | S ?fuel' => let A := fresh \"A\" in assert (A : (Int_part (r + IZR (Z.of_nat k) / 100) <= Int_part (r + 57 / 100))%Z).",
  "verified_prefix": [
    "intros r H.",
    "unfold range_sum in H.",
    "cbn in H.",
    "assert (floor_mono : forall x y : R, x <= y -> (Int_part x <= Int_part y)%Z).",
    "{ intros x y Hxy.",
    "destruct (Z_le_gt_dec (Int_part x) (Int_part y)) as [Hle | Hgt].",
    "- exact Hle.",
    "- exfalso.",
    "pose proof (base_Int_part x) as Hx.",
    "pose proof (base_Int_part y) as Hy.",
    "destruct Hx as [Hx1 Hx2].",
    "destruct Hy as [Hy1 Hy2].",
    "assert (Hc : IZR (Int_part y + 1) <= IZR (Int_part x)).",
    "{ apply IZR_le.",
    "lia.",
    "}",
    "rewrite plus_IZR in Hc.",
    "simpl in Hc.",
    "lra.",
    "}",
    "assert (floor_add_one : forall x : R, Int_part (x + 1) = (Int_part x + 1)%Z).",
    "{ intros x.",
    "symmetry.",
    "apply Int_part_spec.",
    "pose proof (base_Int_part x) as Hx.",
    "destruct Hx as [Hx1 Hx2].",
    "split.",
    "- rewrite plus_IZR.",
    "simpl.",
    "lra.",
    "- rewrite plus_IZR.",
    "simpl.",
    "lra.",
    "}"
  ]
}
```

### gpt-5.6-terra/none/aime_1991_p9

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1991_p9__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.19395240; 31 completions; 1.742 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

### gpt-5.6-terra/none/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/algebra_others_exirrpowirrrat__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.40246500; 39 completions; 2.652 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'no-witness': 1, 'other': 4, 'rewrite-no-match': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: Not the right number of missing arguments (expected 1).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 39,
  "category": "no-witness",
  "elapsed": 0.1046488443389535,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHpq  : (p * p)%Z = (2 * (q * q))%Z\nn  : nat\nIH  : forall y : nat,\ny < n ->\nforall p1 q1 : Z,\nq1 <> 0%Z ->\n(p1 * p1)%Z = (2 * (q1 * q1))%Z -> Z.to_nat (Z.abs q1) = y -> False\np0, q0  : Z\nHq0  : q0 <> 0%Z\nHp0  : (p0 * p0)%Z = (2 * (q0 * q0))%Z\nHn  : Z.to_nat (Z.abs q0) = n\nHepb  : Z.even p0 = true\nr  : Z\nHr  : p0 = (2 * r)%Z\nHqq  : (q0 * q0)%Z = (2 * (r * r))%Z\nHeqb  : Z.even q0 = true\ns  : Z\nHs  : q0 = (2 * s)%Z\nHs0  : s <> 0%Z\nHrs  : (r * r)%Z = (2 * (s * s))%Z\nHpos  : (0 < Z.abs s)%Z\n|-(Z.abs s <\n match Z.abs s with\n | 0 => 0\n | Z.pos y' => Z.pos y'~0\n | Z.neg y' => Z.neg y'~0\n end)%Z"
  ],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "assert (Hno : forall p q : Z, q <> 0%Z -> (p * p)%Z = (2 * (q * q))%Z -> False).",
    "{ intros p q Hq Hpq.",
    "refine (well_founded_induction Nat.lt_wf_0 (fun n => forall p q : Z, q <> 0%Z -> (p * p)%Z = (2 * (q * q))%Z -> Z.to_nat (Z.abs q) = n -> False) _ (Z.to_nat (Z.abs q)) p q Hq Hpq eq_refl).",
    "intros n IH p0 q0 Hq0 Hp0 Hn.",
    "assert (Hepb : Z.even p0 = true).",
    "{ assert (H : Z.even (p0 * p0) = true).",
    "{ rewrite Hp0.",
    "apply Z.even_even.",
    "}",
    "rewrite Z.even_mul in H.",
    "destruct (Z.even p0); simpl in H; assumption.",
    "}",
    "assert (Hep : Z.Even p0).",
    "{ apply Z.even_spec.",
    "exact Hepb.",
    "}",
    "destruct Hep as [r Hr].",
    "assert (Hqq : (q0 * q0)%Z = (2 * (r * r))%Z).",
    "{ subst p0.",
    "nia.",
    "}",
    "assert (Heqb : Z.even q0 = true).",
    "{ assert (H : Z.even (q0 * q0) = true).",
    "{ rewrite Hqq.",
    "apply Z.even_even.",
    "}",
    "rewrite Z.even_mul in H.",
    "destruct (Z.even q0); simpl in H; assumption.",
    "}",
    "assert (Heq : Z.Even q0).",
    "{ apply Z.even_spec.",
    "exact Heqb.",
    "}",
    "destruct Heq as [s Hs].",
    "assert (Hs0 : s <> 0%Z).",
    "{ intro Hz.",
    "subst s.",
    "apply Hq0.",
    "nia.",
    "}",
    "assert (Hrs : (r * r)%Z = (2 * (s * s))%Z).",
    "{ subst q0.",
    "nia.",
    "}",
    "assert (Hltz : (Z.abs s < Z.abs (s + s))%Z).",
    "{ replace (s + s)%Z with (2 * s)%Z by ring.",
    "rewrite Z.abs_mul.",
    "simpl.",
    "assert (Hpos : (0 < Z.abs s)%Z).",
    "{ apply Z.abs_pos.",
    "exact Hs0.",
    "}"
  ]
}
```

### gpt-5.6-terra/none/amc12_2001_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12_2001_p21__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.39720660; 20 completions; 148.537 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-such-goal': 1, 'no-witness': 1, 'other': 1, 'prover-crash': 7, 'syntax-error': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference interval_cases was not found in the current environment.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "prover-crash",
  "elapsed": 60.124703851528466,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "repeat rewrite Nat.Div0.mul_mod in Hsevenprod.",
  "verified_prefix": [
    "intros a b c d Hprod Hab Hbc Hcd.",
    "assert (Hfac1 : (a + 1) * (b + 1) = 525) by (clear Hprod Hbc Hcd; nia).",
    "assert (Hfac2 : (b + 1) * (c + 1) = 147) by (clear Hprod Hab Hcd; nia).",
    "assert (Hdiv1 : Nat.divide (b + 1) 525).",
    "{ exists (a + 1). nia. }",
    "assert (Hdiv2 : Nat.divide (b + 1) 147).",
    "{ exists (c + 1). nia. }",
    "assert (Hdiv : Nat.divide (b + 1) 21).",
    "{ replace 21 with (Nat.gcd 525 147) by reflexivity.",
    "apply Nat.gcd_greatest; assumption. }",
    "assert (Hbvals : b = 6 \\/ b = 20).",
    "{ destruct Hdiv as [x Hx].",
    "clear Hprod Hab Hbc Hdiv1 Hdiv2.",
    "destruct x as [|x]; nia. }",
    "assert (Hseven : Nat.divide 7 (fact 8)).",
    "{ exists (8 * fact 6).",
    "change (8 * (7 * fact 6) = 7 * (8 * fact 6)).",
    "reflexivity. }",
    "assert (Hsevenprod : Nat.divide 7 (a * b * c * d)).",
    "{ rewrite Hprod.",
    "exact Hseven. }",
    "destruct Hbvals as [Hb|Hb].",
    "- assert (Ha : a = 74) by (clear Hprod Hsevenprod; nia).",
    "assert (Hc : c = 20) by (clear Hprod Hsevenprod; nia).",
    "assert (Hd : d = 4) by (clear Hprod Hsevenprod; nia).",
    "rewrite Ha, Hb, Hc, Hd in Hsevenprod.",
    "apply Nat.Lcm0.mod_divide in Hsevenprod."
  ]
}
```

### gpt-5.6-terra/none/amc12a_2008_p4

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2008_p4__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.08079840; 6 completions; 1.280 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'syntax-error': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')
```

### gpt-5.6-terra/none/amc12a_2019_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2019_p21__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.26684700; 34 completions; 2.395 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-proof-submission`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-terra/none/amc12a_2020_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2020_p21__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.41969640; 19 completions; 113.169 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `rewrite-no-match`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 1, 'other': 1, 'prover-crash': 5, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof amc12a_2020_p21): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "rewrite-no-match",
  "elapsed": 18.41004291921854,
  "error": "(-32003, 'Coq: Found no subterm matching \"5 * Nat.gcd (fact 10) n\" in the current goal.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n  : nat\nH5  : fact 5 = 120\nk  : nat\nHk  : n = k * 5\nHlcm  : Nat.lcm 120 n = 5 * Nat.gcd (fact 10) n\n|-Nat.divide n (5 * fact 10)",
    "n  : nat\nH5  : fact 5 = 120\nk  : nat\nHk  : n = k * 5\nHlcm  : Nat.lcm 120 n = 5 * Nat.gcd (fact 10) n\nHdiv  : Nat.divide n (5 * fact 10)\n|-n < 0 + (5 * fact 10 + 1)"
  ],
  "success": false,
  "tactic": "{ rewrite <- Hlcm.",
  "verified_prefix": [
    "unfold satisfies_condition.",
    "set (l := filter (fun m => andb (Nat.eqb (m mod 5) 0) (Nat.eqb (Nat.lcm 120 m) (5 * Nat.gcd (fact 10) m))) (seq 0 (5 * fact 10 + 1))).",
    "exists l.",
    "subst l.",
    "split.",
    "- apply NoDup_filter.",
    "apply seq_NoDup.",
    "- split.",
    "+ intro n.",
    "rewrite filter_In.",
    "assert (H5 : fact 5 = 120).",
    "{ cbv [fact]. reflexivity. }",
    "rewrite H5.",
    "split.",
    "* intros [_ H].",
    "apply Bool.andb_true_iff in H.",
    "destruct H as [Hmod Hlcm].",
    "apply Nat.eqb_eq in Hmod.",
    "apply Nat.eqb_eq in Hlcm.",
    "split.",
    "-- destruct (proj1 (Nat.mod_divide n 5 ltac:(lia)) Hmod) as [k Hk].",
    "exists k.",
    "nia.",
    "-- exact Hlcm.",
    "* intros [[k Hk] Hlcm].",
    "split.",
    "-- apply (proj2 (in_seq (5 * fact 10 + 1) 0 n)).",
    "split.",
    "++ lia.",
    "++ assert (Hdiv : Nat.divide n (5 * fact 10))."
  ]
}
```

### gpt-5.6-terra/none/amc12b_2002_p3

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12b_2002_p3__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.09883680; 11 completions; 6.437 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'ring-failure': 2, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: The reference by_contra was not found in the current environment.')
```

### gpt-5.6-terra/none/imo_1960_p2

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1960_p2__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.24140620; 24 completions; 2.084 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

### gpt-5.6-terra/none/imo_1969_p2

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1969_p2__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.42109220; 15 completions; 2.573 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unknown-reference`; added goal views: 0. Error counts: `{'no-witness': 3, 'ring-failure': 1, 'type-mismatch': 1, 'unknown-reference': 3}`.

First error:

```text
(-32003, 'Coq: In environment\nm, n : R\nk : nat\na : nat -> R\ny : R -> R\nHk : (0 < k)%nat\nHy :\n  forall x : R,\n  y x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHym : y m = 0\nHyn : y n = 0\nN : nat\nThe term "0" has type "R" while it is expected to have type "nat".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 14,
  "category": "unknown-reference",
  "elapsed": 0.019437259063124657,
  "error": "(-32003, 'Coq: The variable pow_succ was not found in the current environment.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHym  : y m = 0\nHyn  : y n = 0\nq  : nat\nIH  : 0 < 2 ^ q\n|-0 < 2 ^ S q"
  ],
  "success": false,
  "tactic": "- rewrite pow_succ.",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hym Hyn.",
    "assert (Hpowall : forall q : nat, 0 < (2 : R) ^ q).",
    "{ intro q.",
    "induction q as [|q IH].",
    "- simpl.",
    "lra."
  ]
}
```

### gpt-5.6-terra/none/imo_1984_p6

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1984_p6__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.23977280; 20 completions; 243.712 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'already-used': 1, 'prover-crash': 2, 'type-mismatch': 2, 'unify-failure': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 60.092707118950784,
  "error": "Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "nia.",
  "verified_prefix": [
    "destruct H0 as [Ha [Hb [Hc Hd]]].",
    "destruct H1 as [Haodd [Hbodd [Hcodd Hdodd]]].",
    "destruct H2 as [Hab [Hbc Hcd]].",
    "assert (Hsum : b + c < a + d) by nia.",
    "assert (Hmk : m < k).",
    "{ apply (proj2 (Nat.pow_lt_mono_r_iff 2 m k ltac:(lia))).",
    "rewrite <- H5, <- H4.",
    "exact Hsum.",
    "}",
    "destruct Haodd as [x Hax].",
    "destruct Hbodd as [y Hby].",
    "destruct Hcodd as [z Hcz].",
    "destruct Hdodd as [w Hdw]."
  ]
}
```

### gpt-5.6-terra/none/mathd_algebra_282

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_algebra_282__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.30052460; 33 completions; 7.185 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 16, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 33,
  "category": "incomplete-proof",
  "elapsed": 0.007622084580361843,
  "error": "(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R, is_rational x -> f x = Rabs (IZR (Int_part x))\nh1  : forall x : R, ~ is_rational x -> f x = IZR (up x) ^ 2\n|-f (Rpower 8 (1 / 3)) + f (- PI) + f (sqrt 50) + f (9 / 2) = 79"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros."
  ]
}
```

### gpt-5.6-terra/none/mathd_numbertheory_303

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_303__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.23660160; 31 completions; 2.667 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 1, 'other': 1}`.

First error:

```text
(-32003, 'Coq: This proof is focused, but cannot be unfocused this way')
```

### gpt-5.6-terra/none/mathd_numbertheory_405

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_405__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.40774580; 12 completions; 34.182 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'focus-error': 1, 'not-convertible': 1, 'other': 1, 'prover-crash': 1, 'rewrite-no-match': 2, 'syntax-error': 1, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "t 1" in the current goal.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 12,
  "category": "prover-crash",
  "elapsed": 30.820324684493244,
  "error": "Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": "repeat rewrite Nat.add_mod by lia.",
  "verified_prefix": [
    "assert (Hper : forall n, t (n + 16) mod 7 = t n mod 7).",
    "{ assert (Hpair : forall n, t (n + 16) mod 7 = t n mod 7 /\\ t (n + 17) mod 7 = t (n + 1) mod 7).",
    "{ intro n.",
    "induction n as [|n IH].",
    "- assert (T2 : t 2 = 1).",
    "{ rewrite (h2 2) by lia. cbn. rewrite h0, h1. reflexivity. }",
    "assert (T3 : t 3 = 2).",
    "{ rewrite (h2 3) by lia. cbn. rewrite T2, h1. reflexivity. }",
    "assert (T4 : t 4 = 3).",
    "{ rewrite (h2 4) by lia. cbn. rewrite T2, T3. reflexivity. }",
    "assert (T5 : t 5 = 5).",
    "{ rewrite (h2 5) by lia. cbn. rewrite T3, T4. reflexivity. }",
    "assert (T6 : t 6 = 8).",
    "{ rewrite (h2 6) by lia. cbn. rewrite T4, T5. reflexivity. }",
    "assert (T7 : t 7 = 13).",
    "{ rewrite (h2 7) by lia. cbn. rewrite T5, T6. reflexivity. }",
    "assert (T8 : t 8 = 21).",
    "{ rewrite (h2 8) by lia. cbn. rewrite T6, T7. reflexivity. }",
    "assert (T9 : t 9 = 34).",
    "{ rewrite (h2 9) by lia. cbn. rewrite T7, T8. reflexivity. }",
    "assert (T10 : t 10 = 55).",
    "{ rewrite (h2 10) by lia. cbn. rewrite T8, T9. reflexivity. }",
    "assert (T11 : t 11 = 89).",
    "{ rewrite (h2 11) by lia. cbn. rewrite T9, T10. reflexivity. }",
    "assert (T12 : t 12 = 144).",
    "{ rewrite (h2 12) by lia. cbn. rewrite T10, T11. reflexivity. }",
    "assert (T13 : t 13 = 233).",
    "{ rewrite (h2 13) by lia. cbn. rewrite T11, T12. reflexivity. }",
    "assert (T14 : t 14 = 377).",
    "{ rewrite (h2 14) by lia. cbn. rewrite T12, T13. reflexivity. }",
    "assert (T15 : t 15 = 610).",
    "{ rewrite (h2 15) by lia. cbn. rewrite T13, T14. reflexivity. }",
    "assert (T16 : t 16 = 987).",
    "{ rewrite (h2 16) by lia. cbn. rewrite T14, T15. reflexivity. }",
    "assert (T17 : t 17 = 1597).",
    "{ rewrite (h2 17) by lia. cbn. rewrite T15, T16. reflexivity. }",
    "cbn.",
    "rewrite T16, T17, h0, h1.",
    "split; vm_compute; reflexivity.",
    "- destruct IH as [IH0 IH1].",
    "split.",
    "+ replace (S n + 16) with (n + 17) by lia.",
    "replace (S n) with (n + 1) by lia.",
    "exact IH1.",
    "+ replace (S n + 17) with (n + 18) by lia.",
    "replace (S n + 1) with (n + 2) by lia.",
    "rewrite (h2 (n + 18)) by lia.",
    "replace (n + 18 - 2) with (n + 16) by lia.",
    "replace (n + 18 - 1) with (n + 17) by lia.",
    "rewrite (h2 (n + 2)) by lia.",
    "replace (n + 2 - 2) with n by lia.",
    "replace (n + 2 - 1) with (n + 1) by lia."
  ]
}
```

### gpt-5.6-terra/none/mathd_numbertheory_43

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_43__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.40538100; 30 completions; 208.385 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `unify-failure`; added goal views: 0. Error counts: `{'no-witness': 1, 'prover-crash': 2, 'syntax-error': 2, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 29,
  "category": "unify-failure",
  "elapsed": 16.36698925960809,
  "error": "(-32003, 'Coq: In environment\\np := 15 ^ 233 : nat\\nHp : p <> 0\\nHp1 : 1 < p\\nf :=\\n  fix f (n : nat) : nat :=\\n    match n with\\n    | 0 => 1\\n    | S n0 => (S n0 * f n0) mod p\\n    end\\n  : nat -> nat\\nn : nat\\nIH : f n = fact n mod p\\nUnable to unify \"(S n * fact n) mod p\" with \"(S n * (fact n mod p)) mod p\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "p := 15 ^ 233 : nat\nHp  : p <> 0\nHp1  : 1 < p\nf := fix f0 (n0 : nat) : nat :=\n  match n0 with\n  | 0 => 1\n  | S n1 => (S n1 * f0 n1) mod p\n  end : nat -> nat\nn  : nat\nIH  : f n = fact n mod p\n|-(S n * (fact n mod p)) mod p = (S n * fact n) mod p"
  ],
  "success": false,
  "tactic": "reflexivity. }",
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15 ^ 233).",
    "set (p := 15 ^ 233).",
    "assert (Hp : p <> 0) by (subst p; apply Nat.pow_nonzero; lia).",
    "assert (Hp1 : 1 < p).",
    "{ subst p. apply Nat.pow_gt_1; lia. }",
    "set (f := fix f (n : nat) := match n with | 0 => 1 | S n => (S n * f n) mod p end).",
    "assert (Hf : forall n, f n = fact n mod p).",
    "{ intro n; induction n as [|n IH].",
    "- change (1 = 1 mod p).",
    "rewrite Nat.mod_small by exact Hp1.",
    "reflexivity.",
    "- change ((S n * f n) mod p = (S n * fact n) mod p).",
    "rewrite IH."
  ]
}
```

### gpt-5.6-terra/none/mathd_numbertheory_530

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_530__terra-none-medium__gpt-5.6-terra__seed0`. Unsolved; $0.33714360; 42 completions; 2.776 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: In environment\nn, k : nat\nd := Nat.gcd n k : nat\nx : nat\nhn : (0 < x * d)%nat\ny : nat\nhk : (0 < y * d)%nat\nhu : INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d)) < 6\nhl : 5 < INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d))\nHx : n = (x * d)%nat\nHy : k = (y * d)%nat\nThe term "0" has type "R" while it is expected to have type "nat".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 30,
  "category": "type-mismatch",
  "elapsed": 0.46210429817438126,
  "error": "(-32003, 'Coq: In environment\\nn, k : nat\\nd := Nat.gcd n k : nat\\nx : nat\\nhn : (0 < x * d)%nat\\ny : nat\\nhk : (0 < y * d)%nat\\nhu : INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d)) < 6\\nhl : 5 < INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d))\\nHx : n = (x * d)%nat\\nHy : k = (y * d)%nat\\nThe term \"0\" has type \"R\" while it is expected to have type \"nat\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nd := Nat.gcd n k : nat\nx  : nat\nhn  : (0 < x * d)%nat\ny  : nat\nhk  : (0 < y * d)%nat\nhu  : INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d)) < 6\nhl  : 5 < INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d))\nHx  : n = (x * d)%nat\nHy  : k = (y * d)%nat\n|-(22 <= Nat.lcm n k / d)%nat"
  ],
  "success": false,
  "tactic": "assert (hd : d <> 0) by (intro E; subst d; simpl in hn; lia).",
  "verified_prefix": [
    "intros n k hn hk hu hl.",
    "set (d := Nat.gcd n k).",
    "destruct (Nat.gcd_divide_l n k) as [x Hx].",
    "destruct (Nat.gcd_divide_r n k) as [y Hy].",
    "fold d in Hx.",
    "fold d in Hy.",
    "rewrite Hx in hn, hu, hl.",
    "rewrite Hy in hk, hu, hl.",
    "rewrite Nat2Z.inj_mul, mult_IZR in hu.",
    "rewrite Nat2Z.inj_mul, mult_IZR in hl.",
    "rewrite <- INR_IZR_INZ in hu.",
    "rewrite <- INR_IZR_INZ in hl."
  ]
}
```

### gpt-5.6-terra/none/mathd_numbertheory_64

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_64__terra-none-medium__gpt-5.6-terra__seed0`. Solved; $0.01797200; 5 completions; 0.906 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-terra/terra/aime_1984_p7

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1984_p7__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.25703520; 11 completions; 2.278 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-witness': 1, 'rewrite-no-match': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "f 1004" in the current goal.')
```

### gpt-5.6-terra/terra/aime_1991_p6

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1991_p6__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.36239300; 25 completions; 160.469 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `syntax-error`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1, 'no-witness': 1, 'prover-crash': 1, 'rewrite-no-match': 1, 'syntax-error': 1, 'type-mismatch': 2}`.

First error:

```text
Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "syntax-error",
  "elapsed": 8.022146602161229,
  "error": "(-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')",
  "outcome": "rejected",
  "remaining_goals": [
    "r  : R\nf := fun k : nat => Int_part (r + IZR (Z.of_nat k) / 100) : nat -> Z\nHsum  : fold_left Z.add (map f (seq 19 73)) 0%Z = 546%Z\nfold_upper  : forall (l : list nat) (M z : Z),\n(forall k : nat, In k l -> (f k <= M)%Z) ->\n(fold_left Z.add (map f l) z <= z + Z.of_nat (length l) * M)%Z\nfold_lower  : forall (l : list nat) (M z : Z),\n(forall k : nat, In k l -> (M <= f k)%Z) ->\n(z + Z.of_nat (length l) * M <= fold_left Z.add (map f l) z)%Z\nHlt  : (Int_part (100 * r) < 743)%Z\nHa  : IZR (Int_part (100 * r)) <= 100 * r\nHb  : IZR (Int_part (100 * r)) - 100 * r > -1\nHc  : IZR (Int_part (100 * r)) < 743\n|-r < 743 / 100"
  ],
  "success": false,
  "tactic": "norm_num in Hc.",
  "verified_prefix": [
    "intros r Hsum.",
    "unfold range_sum in Hsum.",
    "set (f := fun k : nat => Int_part (r + IZR (Z.of_nat k) / 100)) in *.",
    "assert (fold_upper : forall (l : list nat) (M z : Z), (forall k, In k l -> (f k <= M)%Z) -> (fold_left Z.add (map f l) z <= z + Z.of_nat (List.length l) * M)%Z).",
    "{ intros l.",
    "induction l as [|x l IH].",
    "- intros M z Hb. simpl. lia.",
    "- intros M z Hb.",
    "cbn [List.length].",
    "rewrite Nat2Z.inj_succ.",
    "cbn [map fold_left].",
    "assert (Hx : (f x <= M)%Z) by (apply Hb; simpl; auto).",
    "assert (Hl : forall k : nat, In k l -> (f k <= M)%Z).",
    "{ intros k Hk. apply Hb. simpl. auto. }",
    "specialize (IH M ((z + f x)%Z) Hl).",
    "nia.",
    "}",
    "assert (fold_lower : forall (l : list nat) (M z : Z), (forall k, In k l -> (M <= f k)%Z) -> (z + Z.of_nat (List.length l) * M <= fold_left Z.add (map f l) z)%Z).",
    "{ intros l.",
    "induction l as [|x l IH].",
    "- intros M z Hb. simpl. lia.",
    "- intros M z Hb.",
    "cbn [List.length].",
    "rewrite Nat2Z.inj_succ.",
    "cbn [map fold_left].",
    "assert (Hx : (M <= f x)%Z) by (apply Hb; simpl; auto).",
    "assert (Hl : forall k : nat, In k l -> (M <= f k)%Z).",
    "{ intros k Hk. apply Hb. simpl. auto. }",
    "specialize (IH M ((z + f x)%Z) Hl).",
    "nia.",
    "}",
    "destruct (Z_lt_ge_dec (Int_part (100 * r)) 743%Z) as [Hlt|Hge].",
    "- assert (Hr : r < 743 / 100).",
    "{ destruct (base_Int_part (100 * r)) as [Ha Hb].",
    "pose proof (IZR_lt _ _ Hlt) as Hc."
  ]
}
```

### gpt-5.6-terra/terra/aime_1991_p9

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/aime_1991_p9__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.21125040; 15 completions; 1.639 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'no-matching-clause': 1, 'no-witness': 1, 'subproof-incomplete': 1, 'unify-failure': 2}`.

First error:

```text
(-32003, 'Coq: No matching clauses for match.')
```

### gpt-5.6-terra/terra/algebra_others_exirrpowirrrat

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/algebra_others_exirrpowirrrat__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.32913300; 30 completions; 3.059 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `type-mismatch`; added goal views: 0. Error counts: `{'type-mismatch': 2}`.

First error:

```text
(-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHpq : sqrt 2 = (IZR p / IZR q)%R\nThe term "0" has type "nat" while it is expected to have type "R".')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "type-mismatch",
  "elapsed": 0.01706604938954115,
  "error": "(-32003, 'Coq: In environment\\np, q : Z\\nHq : q <> 0%Z\\nHpq : sqrt 2 = (IZR p / IZR q)%R\\nHqR : IZR q <> 0%R\\nThe term \"sqrt 2\" has type \"R\" while it is expected to have type \"nat\".')",
  "outcome": "rejected",
  "remaining_goals": [
    "p, q  : Z\nHq  : q <> 0%Z\nHpq  : sqrt 2 = (IZR p / IZR q)%R\nHqR  : IZR q <> 0%R\n|-False"
  ],
  "success": false,
  "tactic": "assert (Hs : (sqrt 2) ^ 2 = 2) by apply Rsqr_sqrt; lra.",
  "verified_prefix": [
    "assert (Hirr : irrational (sqrt 2)).",
    "{ unfold irrational.",
    "intros [p [q [Hq Hpq]]].",
    "assert (HqR : IZR q <> 0%R).",
    "{ intro H.",
    "apply Hq.",
    "apply eq_IZR.",
    "lra.",
    "}"
  ]
}
```

### gpt-5.6-terra/terra/amc12_2001_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12_2001_p21__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.35165620; 28 completions; 78.720 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-witness': 2, 'prover-crash': 2, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: The variable b was not found in the current environment.')
```

### gpt-5.6-terra/terra/amc12a_2008_p4

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2008_p4__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.23749580; 16 completions; 7.683 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'focus-error': 2, 'other': 3, 'rewrite-no-match': 1, 'syntax-error': 1}`.

First error:

```text
(-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')
```

### gpt-5.6-terra/terra/amc12a_2019_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2019_p21__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.33867160; 38 completions; 21.803 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 1}`.

First error:

```text
(-32003, 'Coq: No applicable tactic.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 26,
  "category": "no-applicable-tactic",
  "elapsed": 0.4479047078639269,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "x := (1 + Ci) / sqrt 2 : C : C\nHs  : (sqrt 2 * sqrt 2)%R = 2\n|-(((1 + 0) * (sqrt 2 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))) -\n  (0 + 1) * (- 0 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))))%R,\n ((1 + 0) * (- 0 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))) +\n  (0 + 1) * (sqrt 2 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))))%R) *\n((((1 + 0) * (sqrt 2 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))) -\n   (0 + 1) * (- 0 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))))%R,\n  ((1 + 0) * (- 0 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))) +\n   (0 + 1) * (sqrt 2 / (sqrt 2 * (sqrt 2 * 1) + 0 * (0 * 1))))%R) *\n 1) =\n(0, 1)"
  ],
  "success": false,
  "tactic": "f_equal; field_simplify; nra.",
  "verified_prefix": [
    "intros z Hz.",
    "subst z.",
    "set (x := ((1 + Ci) / sqrt 2 : C)).",
    "assert (Hs : (sqrt 2 * sqrt 2)%R = 2) by (apply sqrt_def; lra).",
    "assert (H2 : x ^ 2 = Ci).",
    "{ unfold x, Cdiv, Cinv, Cmult, Cplus, RtoC, Ci.",
    "simpl."
  ]
}
```

### gpt-5.6-terra/terra/amc12a_2020_p21

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12a_2020_p21__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.36705880; 20 completions; 89.808 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'no-such-goal': 1, 'other': 1, 'prover-crash': 4, 'syntax-error': 1, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, "Coq: Syntax error: 'with' or 'in' expected (in [ltac_expr]).")
```

Last submitted proof checkpoint:

```json
{
  "after_request": 19,
  "category": "prover-crash",
  "elapsed": 0.46922146901488304,
  "error": "(-32003, 'Coq: Stack overflow.')",
  "outcome": "resource_exhausted",
  "remaining_goals": [
    "f := fun x : nat =>\n((x mod 5 =? 0) &&\n (Nat.lcm 120 x =?\n  5 *\n  Nat.gcd\n    (of_num_uint\n       (Number.UIntDecimal\n          (Decimal.D3\n             (Decimal.D6\n                (Decimal.D2\n                   (Decimal.D8\n                      (Decimal.D8 (Decimal.D0 (Decimal.D0 Decimal.Nil)))))))))\n    x))%bool : nat -> bool\nn  : nat\nF5  : fact 5 = 120\n|-In n\n  (filter f\n     (seq 0\n        (of_num_uint\n           (Number.UIntDecimal\n              (Decimal.D1\n                 (Decimal.D8\n                    (Decimal.D1\n                       (Decimal.D4\n                          (Decimal.D4\n                             (Decimal.D0\n                                (Decimal.D0 (Decimal.D1 Decimal.Nil)))))))))))) <->\n(exists k : nat, n = k * 5) /\\ Nat.lcm (fact 5) n = 5 * Nat.gcd (fact 10) n"
  ],
  "success": false,
  "tactic": "assert (F10 : fact 10 = 3628800) by native_compute.",
  "verified_prefix": [
    "set (f := fun x => andb (Nat.eqb (x mod 5) 0) (Nat.eqb (Nat.lcm 120 x) (5 * Nat.gcd 3628800 x))).",
    "exists (filter f (seq 0 18144001)).",
    "split.",
    "- apply NoDup_filter.",
    "apply seq_NoDup.",
    "- split.",
    "+ intro n.",
    "unfold satisfies_condition.",
    "assert (F5 : fact 5 = 120) by reflexivity."
  ]
}
```

### gpt-5.6-terra/terra/amc12b_2002_p3

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/amc12b_2002_p3__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.04051760; 9 completions; 0.960 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

### gpt-5.6-terra/terra/imo_1960_p2

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1960_p2__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.19023140; 11 completions; 1.930 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'incomplete-proof': 1, 'no-applicable-tactic': 2, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Proof is not complete.')
```

### gpt-5.6-terra/terra/imo_1969_p2

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1969_p2__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.39029460; 23 completions; 2.873 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-witness`; added goal views: 0. Error counts: `{'incomplete-proof': 3, 'no-witness': 2, 'other': 1, 'rewrite-no-match': 1, 'ring-failure': 1, 'type-mismatch': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 23,
  "category": "no-witness",
  "elapsed": 0.18059026822447777,
  "error": "(-32003, 'Coq: Tactic failure:  Cannot find witness.')",
  "outcome": "rejected",
  "remaining_goals": [
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm  : sum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) (Init.Nat.pred k) * cos m -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) (Init.Nat.pred k) * sin m = 0\nHn  : sum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) (Init.Nat.pred k) * cos n -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) (Init.Nat.pred k) * sin n = 0\nHexp  : forall (N : nat) (x : R),\nsum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) N =\nsum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) N * cos x -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) N * sin x\n|-Rabs (1 / 1 - 1) <= 1 - / 1",
    "m, n  : R\nk  : nat\na  : nat -> R\ny  : R -> R\nHk  : (0 < k)%nat\nHy  : forall x : R,\ny x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHm  : sum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) (Init.Nat.pred k) * cos m -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) (Init.Nat.pred k) * sin m = 0\nHn  : sum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) (Init.Nat.pred k) * cos n -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) (Init.Nat.pred k) * sin n = 0\nHexp  : forall (N0 : nat) (x : R),\nsum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) N0 =\nsum_f_R0 (fun i : nat => cos (a i) / 2 ^ i) N0 * cos x -\nsum_f_R0 (fun i : nat => sin (a i) / 2 ^ i) N0 * sin x\nN  : nat\nIHN  : Rabs (sum_f_R0 (fun i : nat => cos (a i - a 0%nat) / 2 ^ i) N - 1) <=\n1 - / 2 ^ N\n|-Rabs (sum_f_R0 (fun i : nat => cos (a i - a 0%nat) / 2 ^ i) (S N) - 1) <=\n1 - / 2 ^ S N"
  ],
  "success": false,
  "tactic": "lra.",
  "verified_prefix": [
    "intros m n k a y Hk Hy Hm Hn.",
    "rewrite (Hy m) in Hm.",
    "rewrite (Hy n) in Hn.",
    "apply sin_eq_0_0.",
    "assert (Hexp : forall (N : nat) (x : R), sum_f_R0 (fun i => cos (a i + x) / (2 ^ i)) N = sum_f_R0 (fun i => cos (a i) / (2 ^ i)) N * cos x - sum_f_R0 (fun i => sin (a i) / (2 ^ i)) N * sin x).",
    "{ intros N.",
    "induction N as [|N IHN].",
    "- intro x.",
    "simpl.",
    "rewrite cos_plus.",
    "lra.",
    "- intro x.",
    "rewrite tech5.",
    "rewrite IHN.",
    "rewrite tech5.",
    "rewrite tech5.",
    "rewrite cos_plus.",
    "field.",
    "apply pow_nonzero.",
    "lra.",
    "}",
    "rewrite Hexp in Hm.",
    "rewrite Hexp in Hn.",
    "assert (Hbound : forall N : nat, Rabs (sum_f_R0 (fun i => cos (a i - a 0%nat) / (2 ^ i)) N - 1) <= 1 - / (2 ^ N)).",
    "{ intro N.",
    "induction N as [|N IHN].",
    "- simpl.",
    "replace (a 0%nat - a 0%nat) with 0 by ring.",
    "rewrite cos_0."
  ]
}
```

### gpt-5.6-terra/terra/imo_1984_p6

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/imo_1984_p6__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.38331600; 21 completions; 22.146 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'already-used': 1, 'focus-error': 1, 'incomplete-proof': 2, 'subproof-incomplete': 1, 'syntax-error': 1, 'type-mismatch': 1, 'unknown-reference': 2}`.

First error:

```text
(-32003, 'Coq: a is already used.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 20,
  "category": "incomplete-proof",
  "elapsed": 2.4717219872400165,
  "error": "(-32003, 'Coq:  (in proof imo_1984_p6): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "a, b, c, d, k, m  : nat\nH0  : 0 < a /\\ 0 < b /\\ 0 < c /\\ 0 < d\nH1  : Nat.Odd a /\\ Nat.Odd b /\\ Nat.Odd c /\\ Nat.Odd d\nH2  : a < b /\\ b < c < d\nH3  : a * d = b * c\nH4  : a + d = 2 ^ k\nH5  : b + c = 2 ^ m\nHdc  : a * (d - c) = c * (b - a)\nHdiff  : b - a < d - c\nHsum  : 2 ^ m < 2 ^ k\nHkm  : m < k\nHkge  : m <= k\nHmain  : 2 ^ m * b = 2 ^ k * a + (b - a) * (a + b)\nHdiv  : Nat.divide (2 ^ m) ((b - a) * (a + b))\n|-a = 1"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "assert (Hdc : a * (d - c) = c * (b - a)) by nia.",
    "assert (Hdiff : b - a < d - c) by nia.",
    "assert (Hsum : b + c < a + d) by nia.",
    "rewrite H4, H5 in Hsum.",
    "assert (Hkm : m < k).",
    "{ apply ((Nat.pow_lt_mono_r_iff 2 m k) ltac:(lia)).",
    "exact Hsum.",
    "}",
    "assert (Hkge : m <= k) by lia.",
    "assert (Hmain : 2 ^ m * b = 2 ^ k * a + (b - a) * (a + b)) by nia.",
    "assert (Hdiv : Nat.divide (2 ^ m) ((b - a) * (a + b))).",
    "{ exists (b - 2 ^ (k - m) * a).",
    "replace k with (m + (k - m)) in Hmain by lia.",
    "rewrite Nat.pow_add_r in Hmain.",
    "nia.",
    "}"
  ]
}
```

### gpt-5.6-terra/terra/mathd_algebra_282

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_algebra_282__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.30663420; 34 completions; 11.179 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `incomplete-proof`; added goal views: 0. Error counts: `{'incomplete-proof': 22, 'other': 1}`.

First error:

```text
(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 34,
  "category": "incomplete-proof",
  "elapsed": 0.0067754099145531654,
  "error": "(-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\\n(there are remaining open goals).')",
  "outcome": "incomplete",
  "remaining_goals": [
    "f  : R -> R\nh0  : forall x : R, is_rational x -> f x = Rabs (IZR (Int_part x))\nh1  : forall x : R, ~ is_rational x -> f x = IZR (up x) ^ 2\n|-f (Rpower 8 (1 / 3)) + f (- PI) + f (sqrt 50) + f (9 / 2) = 79"
  ],
  "success": false,
  "tactic": "Qed.",
  "verified_prefix": [
    "intros."
  ]
}
```

### gpt-5.6-terra/terra/mathd_numbertheory_303

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_303__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.32960700; 29 completions; 10.404 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `subproof-incomplete`; added goal views: 0. Error counts: `{'no-witness': 1, 'subproof-incomplete': 1}`.

First error:

```text
(-32003, 'Coq: Tactic failure:  Cannot find witness.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 24,
  "category": "subproof-incomplete",
  "elapsed": 4.131379724480212,
  "error": "(-32003, 'Coq: Proof is not complete.')",
  "outcome": "rejected",
  "remaining_goals": [
    "l  : list nat\nH  : forall n0 : nat,\nIn n0 l <-> 2 <= n0 /\\ 171 mod n0 = 80 mod n0 /\\ 468 mod n0 = 13 mod n0\nHnd  : NoDup l\nH7  : In 7 l\nH13  : In 13 l\nH91  : In 91 l\nn  : nat\nHn  : 2 <= n\nH1  : 171 mod n = 80 mod n\nH2  : 468 mod n = 13 mod n\nHmn  : (80 mod n + 91 mod n) mod n = 80 mod n\nHd  : 80 mod n + 91 mod n = n * ((80 mod n + 91 mod n) / n) + 80 mod n\n|-n = 7 \\/ n = 13 \\/ n = 91"
  ],
  "success": false,
  "tactic": "assert (Hr : 80 mod n < n) by apply PeanoNat.Nat.mod_upper_bound; lia.",
  "verified_prefix": [
    "intros Hnd.",
    "assert (H7 : In 7 l).",
    "{ apply (proj2 (H 7)); vm_compute; lia. }",
    "assert (H13 : In 13 l).",
    "{ apply (proj2 (H 13)); vm_compute; lia. }",
    "assert (H91 : In 91 l).",
    "{ apply (proj2 (H 91)); vm_compute; lia. }",
    "assert (Hall : forall n, In n l -> n = 7 \\/ n = 13 \\/ n = 91).",
    "{ intros n Hmem.",
    "apply (proj1 (H n)) in Hmem.",
    "destruct Hmem as [Hn [H1 H2]].",
    "assert (Hmn : (80 mod n + 91 mod n) mod n = 80 mod n).",
    "{ replace 171 with (80 + 91) in H1 by lia.",
    "rewrite PeanoNat.Nat.Div0.add_mod in H1.",
    "exact H1. }",
    "pose proof (PeanoNat.Nat.Div0.div_mod (80 mod n + 91 mod n) n) as Hd.",
    "rewrite Hmn in Hd."
  ]
}
```

### gpt-5.6-terra/terra/mathd_numbertheory_405

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_405__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.31090560; 18 completions; 7.186 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{'rewrite-no-match': 2, 'unify-failure': 1}`.

First error:

```text
(-32003, 'Coq: Found no subterm matching "t 16" in the current goal.')
```

### gpt-5.6-terra/terra/mathd_numbertheory_43

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_43__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.17985360; 23 completions; 242.274 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `prover-crash`; added goal views: 0. Error counts: `{'prover-crash': 16}`.

First error:

```text
(-32003, 'Coq: Out of memory.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 22,
  "category": "prover-crash",
  "elapsed": 13.213178941048682,
  "error": "ConnectionLost: (-33002, 'the Rocq server closed the connection')",
  "outcome": "unknown",
  "remaining_goals": [],
  "success": false,
  "tactic": null,
  "verified_prefix": [
    "unfold is_greatest.",
    "split.",
    "- exists (fact 942 / 15 ^ 233)."
  ]
}
```

### gpt-5.6-terra/terra/mathd_numbertheory_530

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_530__terra-ace-medium__gpt-5.6-terra__seed0`. Unsolved; $0.37150060; 25 completions; 2.195 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `no-applicable-tactic`; added goal views: 0. Error counts: `{'no-applicable-tactic': 2, 'not-convertible': 1, 'rewrite-no-match': 1, 'subproof-incomplete': 1, 'type-mismatch': 1, 'unknown-reference': 1}`.

First error:

```text
(-32003, 'Coq: Not convertible.')
```

Last submitted proof checkpoint:

```json
{
  "after_request": 25,
  "category": "no-applicable-tactic",
  "elapsed": 0.03691540937870741,
  "error": "(-32003, 'Coq: No applicable tactic.')",
  "outcome": "rejected",
  "remaining_goals": [
    "n, k  : nat\nHn  : (0 < n)%nat\nHk  : (0 < k)%nat\nd, x, y  : nat\nHlt  : INR x / INR y < 6\nHgt  : 5 < INR x / INR y\nEd  : d = Nat.gcd n k\nHx  : n = (x * d)%nat\nHy  : k = (y * d)%nat\nHd  : (0 < d)%nat\nHxpos  : (0 < x)%nat\nHypos  : (0 < y)%nat\nEx  : INR n = INR x * INR d\nEy  : INR k = INR y * INR d\nHdR  : 0 < INR d\nHdR0  : INR d <> 0\nHyR  : 0 < INR y\nHcancel  : INR y * (INR x / INR y) = INR x\n|-INR 5 * INR y < INR x"
  ],
  "success": false,
  "tactic": "nra.",
  "verified_prefix": [
    "intros n k Hn Hk Hlt Hgt.",
    "repeat rewrite <- INR_IZR_INZ in Hlt, Hgt.",
    "remember (Nat.gcd n k) as d eqn: Ed.",
    "destruct (Nat.gcd_divide_l n k) as [x Hx].",
    "destruct (Nat.gcd_divide_r n k) as [y Hy].",
    "rewrite <- Ed in Hx, Hy.",
    "assert (Hd : (0 < d)%nat) by lia.",
    "assert (Hxpos : (0 < x)%nat) by nia.",
    "assert (Hypos : (0 < y)%nat) by nia.",
    "assert (Ex : INR n = INR x * INR d).",
    "{ rewrite Hx.",
    "rewrite mult_INR.",
    "reflexivity.",
    "}",
    "assert (Ey : INR k = INR y * INR d).",
    "{ rewrite Hy.",
    "rewrite mult_INR.",
    "reflexivity.",
    "}",
    "rewrite Ex, Ey in Hlt, Hgt.",
    "assert (HdR : 0 < INR d).",
    "{ apply lt_0_INR.",
    "exact Hd.",
    "}",
    "assert (HdR0 : INR d <> 0) by lra.",
    "rewrite (Rdiv_mult_r_r (INR d) (INR x) (INR y) HdR0) in Hlt, Hgt.",
    "assert (HyR : 0 < INR y).",
    "{ apply lt_0_INR.",
    "exact Hypos.",
    "}",
    "assert (Hcancel : INR y * (INR x / INR y) = INR x).",
    "{ field.",
    "lra.",
    "}",
    "assert (Hxylo : (5 * y < x)%nat).",
    "{ apply INR_lt.",
    "rewrite mult_INR."
  ]
}
```

### gpt-5.6-terra/terra/mathd_numbertheory_64

Source: `experiments/output/ace_attribution_20260912/validation/terra/configs/mathd_numbertheory_64__terra-ace-medium__gpt-5.6-terra__seed0`. Solved; $0.02580060; 4 completions; 0.995 verifier seconds.

Terminal: `historical-uninstrumented`; limiting dimensions: `[]`; last category: `accepted`; added goal views: 0. Error counts: `{}`.

