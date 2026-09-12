# Per-problem ACE attribution appendix

Every failure and discordant solve is included. Full responses and
verified-state histories are in complete_diagnostics.json; this view
summarizes the first error, terminal state and resource evidence.

## training

### imo_1967_p3

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04154 | 23 | no-witness | focus-error |
| luna-ace | 0 | $0.03181 | 21 | no-witness | no-witness |
| terra-none | 0 | $0.44232 | 37 | incomplete-proof | other |
| terra-ace | 0 | $0.39478 | 30 | other | already-used |

**luna-none.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: [Focus] Wrong bullet *: Current bullet * is not finished.')

```rocq
* exists 0.
```

Remaining allowance: $0.05846, 41 requests, 297.74 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
nia.
```

Remaining allowance: $0.06819, 43 requests, 298.21 verifier seconds. Cited advice: rocq-00003, rocq-00005, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: (in proof imo_1967_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: Proof obligations may not be bypassed.

```rocq
unsafe command
```

Remaining allowance: $0.55768, 27 requests, 292.93 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: Proof obligations may not be bypassed.

Last: (-32003, 'Coq: Hkm is already used.')

```rocq
- assert (Hkm : k <= m) by lia.
```

Remaining allowance: $0.60522, 34 requests, 298.31 verifier seconds. Cited advice: rocq-00002, rocq-00003. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### aime_1988_p3

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03892 | 19 | unknown-reference | no-matching-clause |
| luna-ace | 1 | $0.03947 | 14 | unify-failure | accepted |
| terra-none | 1 | $0.32144 | 30 | subproof-incomplete | accepted |
| terra-ace | 1 | $0.26171 | 23 | type-mismatch | accepted |

**luna-none.** First: (-32003, 'Coq: The reference norm_num was not found in the current environment.')

Last: (-32003, 'Coq: No matching clauses for match.')

```rocq
field_simplify [Hl2ne] in Heq.
```

Remaining allowance: $0.06108, 45 requests, 297.73 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### induction_pord1p1on2powklt5on2

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03967 | 17 | syntax-error | focus-error |
| luna-ace | 1 | $0.04184 | 15 | syntax-error | accepted |
| terra-none | 1 | $0.18536 | 22 | syntax-error | accepted |
| terra-ace | 1 | $0.13330 | 15 | no-witness | accepted |

**luna-none.** First: (-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")

Last: (-32003, 'Coq: [Focus] Wrong bullet -: Current bullet -- is not finished.')

```rocq
- exact Hmul.
```

Remaining allowance: $0.06033, 47 requests, 298.24 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### algebra_amgm_sum1toneqn_prod1tonleq1

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03768 | 22 | type-mismatch | other |
| luna-ace | 0 | $0.04008 | 30 | other | unify-failure |
| terra-none | 0 | $0.34174 | 37 | incomplete-proof | no-applicable-tactic |
| terra-ace | 1 | $0.36099 | 32 | type-mismatch | accepted |

**luna-none.** First: (-32003, 'Coq: In environment\nn : nat\na : nat -> R\nHa : forall i : nat, (i < S n)%nat -> 0 <= a i\nHsum : sum_n a n + a n = match n with\n | 0%nat => 1\n | S _ => INR n + 1\n end\nIH :\n (forall i : nat, (i < n)%nat -> 0 <= a i) ->\n sum_n a n = INR n -> prod_n a n <= 1\ni : nat\nThe term "a i" has type "R" while it is expected to have type\n "(i < n)%nat -> 0 <= a i".')

Last: (-32003, 'Coq: No such assumption.')

```rocq
{ apply IH; assumption. }
```

Remaining allowance: $0.06232, 42 requests, 297.18 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: Proof obligations may not be bypassed.

Last: (-32003, 'Coq: In environment\nn : nat\na : nat -> R\nHnonneg : forall i : nat, (i < S (S n))%nat -> 0 <= a i\nHsum : sum_n a (S n) + a (S n) = INR (S n) + 1\nIH : sum_n a (S n) = INR (S n) -> prod_n a (S n) <= 1\nHnonneg\' : forall i : nat, (i < S n)%nat -> 0 <= a i\nUnable to unify "prod_n a (S n) <= 1" with "prod_n a (S n) * a (S n) <= 1".')

```rocq
apply IH.
```

Remaining allowance: $0.05992, 34 requests, 297.05 verifier seconds. Cited advice: rocq-00009, rocq-00010, rocq-00011, rocq-00015. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: (in proof algebra_amgm_sum1toneqn_prod1tonleq1): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
nra.
```

Remaining allowance: $0.65826, 27 requests, 296.97 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_algebra_185

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 1 | $0.03905 | 18 | syntax-error | accepted |
| luna-ace | 0 | $0.03593 | 26 | focus-error | other |
| terra-none | 0 | $0.35205 | 35 | syntax-error | prover-crash |
| terra-ace | 0 | $0.34471 | 27 | unknown-reference | no-witness |

**luna-ace.** First: (-32003, 'Coq: [Focus] Wrong bullet -: Expecting +.')

Last: (-32003, 'Coq: Not an inductive goal with 1 constructor.')

```rocq
+ split.
```

Remaining allowance: $0.06407, 38 requests, 294.60 verifier seconds. Cited advice: rocq-00021, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
{ apply Union_is_finite. exact F0. intro h. unfold t0 in h. unfold Add in h. repeat inversion h; lia. }
```

Remaining allowance: $0.64795, 29 requests, 116.80 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: The reference Add was not found in the current environment.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
pose proof (Union_is_finite Z _ F0 (-11) ltac:(intro H; destruct H as [H|H]; [inversion H|]; destruct H; lia)) as F1.
```

Remaining allowance: $0.65529, 37 requests, 298.51 verifier seconds. Cited advice: rocq-00019, rocq-00025. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### aime_1984_p1

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 1 | $0.03786 | 13 | no-applicable-tactic | accepted |
| luna-ace | 0 | $0.03278 | 15 | type-mismatch | no-applicable-tactic |
| terra-none | 0 | $0.33814 | 33 | type-mismatch | prover-crash |
| terra-ace | 1 | $0.17376 | 11 | type-mismatch | accepted |

**luna-ace.** First: (-32003, 'Coq: In environment\nu : nat -> R\nHrec : forall n : nat, u (n + 1)%nat = u n + 1\nHsum : sum_f_R0 (fun k : nat => u (k + 1)%nat) 97 = 137\nn : nat\nThe term "0" has type "R" while it is expected to have type "nat".')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
nra.
```

Remaining allowance: $0.06722, 49 requests, 225.74 verifier seconds. Cited advice: rocq-00002, rocq-00020. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: In environment\nu : nat -> R\nHu : forall n : nat, u (n + 1)%nat = u n + 1\nHsum : sum_f_R0 (fun k : nat => u (k + 1)%nat) 97 = 137\nn : nat\nThe term "0" has type "R" while it is expected to have type "nat".')

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
rewrite !Huform in Hsum |-.
```

Remaining allowance: $0.66186, 31 requests, 113.41 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### imo_1968_p5_1

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 1 | $0.03642 | 15 | unknown-reference | accepted |
| luna-ace | 0 | $0.03879 | 18 | no-applicable-tactic | ring-failure |
| terra-none | 1 | $0.06243 | 5 | no-applicable-tactic | accepted |
| terra-ace | 1 | $0.09114 | 9 | unify-failure | accepted |

**luna-ace.** First: (-32003, 'Coq: No applicable tactic.')

Last: (-32003, 'Coq: Tactic failure: not a valid ring equation.')

```rocq
{ assert (Hex : (1 / 2 + sqrt (f x - (f x) ^ 2)) ^ 2 = 1 / 4 + (sqrt (f x - (f x) ^ 2)) ^ 2 + sqrt (f x - (f x) ^ 2)) by ring.
```

Remaining allowance: $0.06121, 46 requests, 298.16 verifier seconds. Cited advice: rocq-00012, rocq-00016. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_algebra_224

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03757 | 20 | type-mismatch | no-applicable-tactic |
| luna-ace | 0 | $0.03900 | 18 | type-mismatch | unify-failure |
| terra-none | 0 | $0.40005 | 17 | type-mismatch | no-witness |
| terra-ace | 0 | $0.38074 | 19 | subproof-incomplete | other |

**luna-none.** First: (-32003, 'Coq: The term "5" has type "R" while it is expected to have type "nat".')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
lra. }
```

Remaining allowance: $0.06243, 44 requests, 298.01 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: In environment\nk : nat\nHk1 : (5 <= k)%nat\nHk2 : (k <= 12)%nat\nH :\n 1 + 1 + 1 + 1 <\n (fix INR (n : nat) : R :=\n match n with\n | 0%nat => 0\n | 1%nat => 1\n | S (S _ as n0) => INR n0 + 1\n end)\n k\nThe term "H" has type\n "1 + 1 + 1 + 1 <\n (fix INR (n : nat) : R :=\n match n with\n | 0%nat => 0\n | 1%nat => 1\n | S (S _ as n0) => INR n0 + 1\n end)\n k"\nwhile it is expected to have type "4 < INR k".')

Last: (-32003, 'Coq: In environment\nk : nat\nHk1 : (5 <= k)%nat\nHk2 : (k <= 12)%nat\nHlow : (4 : R) < INR k\nHup : INR k <= (12 : R)\nUnable to unify "INR ?M2125 < INR ?M2126 \\/ INR ?M2125 = INR ?M2126" with\n "0 < INR k \\/ 0 = INR k".')

```rocq
apply le_INR.
```

Remaining allowance: $0.06100, 46 requests, 298.40 verifier seconds. Cited advice: rocq-00021, rocq-00025, rocq-00027. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: The term "5" has type "R" while it is expected to have type "nat".')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
lia.
```

Remaining allowance: $0.59995, 47 requests, 298.38 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: Proof is not complete.')

Last: (-32003, 'Coq: Cannot coerce Empty_set to an evaluable reference.')

```rocq
unfold A, Add, In, Empty_set.
```

Remaining allowance: $0.61926, 45 requests, 298.40 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### imo_1977_p6

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03941 | 11 | already-used | other |
| luna-ace | 0 | $0.03942 | 14 | type-mismatch | no-witness |
| terra-none | 1 | $0.26774 | 15 | other | accepted |
| terra-ace | 0 | $0.36854 | 11 | already-used | no-witness |

**luna-none.** First: (-32003, 'Coq: f is already used.')

Last: Proof obligations may not be bypassed.

```rocq
unsafe command
```

Remaining allowance: $0.06059, 53 requests, 294.31 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: In environment\nf : nat -> nat\nh₀ : forall n : nat, 0 < f n\nh₁ : forall n : nat, 0 < n -> f (f n) < f (S n)\nn : nat\nHn : 0 < S n\nH : forall m : nat, m < S n -> 0 < m -> f m = m\nHpos : 0 < S n\nThe term "Hpos" has type "0 < S n" while it is expected to have type "0 < n".')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
+ lia.
```

Remaining allowance: $0.06058, 50 requests, 298.43 verifier seconds. Cited advice: rocq-00003, rocq-00019, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: k is already used.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
+ assert (Ht1 : 0 < t - 1) by lia.
```

Remaining allowance: $0.63146, 53 requests, 284.99 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### imo_1983_p6

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 1 | $0.01677 | 8 | no-applicable-tactic | accepted |
| luna-ace | 1 | $0.02401 | 11 | no-applicable-tactic | accepted |
| terra-none | 1 | $0.36120 | 12 | syntax-error | accepted |
| terra-ace | 0 | $0.43182 | 8 | ring-failure | unknown-reference |

**terra-ace.** First: (-32003, 'Coq: Tactic failure: not a valid ring equation.')

Last: (-32003, 'Coq: The variable Rmult_le_0 was not found in the current environment.')

```rocq
assert (Hpq : 0 <= p * q) by (apply Rmult_le_0; assumption).
```

Remaining allowance: $0.56818, 56 requests, 298.06 verifier seconds. Cited advice: rocq-00001, rocq-00015. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12a_2020_p13

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04114 | 21 | unify-failure | type-mismatch |
| luna-ace | 0 | $0.03666 | 19 | rewrite-no-match | syntax-error |
| terra-none | 0 | $0.40811 | 32 | subproof-incomplete | unknown-reference |
| terra-ace | 0 | $0.27366 | 25 | none | no submission |

**luna-none.** First: (-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n Rpower n (25 / 36)\nUnable to unify "INR ?M1825 < INR ?M1826" with "0 < INR c".')

Last: (-32003, 'Coq: In environment\na, b, c : nat\nn : R\nHn : 0 < n\nHn1 : n <> 1\nHa : (1 < a)%nat\nHb : (1 < b)%nat\nHc : (1 < c)%nat\nHeq :\n Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) =\n Rpower n (25 / 36)\nHcpos : 0 < INR c\nHbpos : 0 < INR b\nHapos : 0 < INR a\nHrp1 : 0 < Rpower n (/ INR c)\nHbase1 : 0 < n * Rpower n (/ INR c)\nHrp2 : 0 < Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHbase2 : 0 < n * Rpower (n * Rpower n (/ INR c)) (/ INR b)\nHlogn : ln n <> 0\nHlog :\n (ln n * INR b * INR c + ln n * INR c + ln n) / (INR a * INR b * INR c) =\n 25 * ln n / 36\nThe term "Hlog" has type\n "(ln n * INR b * INR c + ln n * INR c + ln n) / (INR a * INR b * INR c) =\n 25 * ln n / 36"\nwhile it is expected to have type\n "36 * ln n * INR b * INR c + 36 * ln n * INR c + 36 * ln n =\n 25 * ln n * INR b * INR c * INR a".')

```rocq
exact Hlog.
```

Remaining allowance: $0.05886, 43 requests, 269.93 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Found no subterm matching "ln (n * Rpower n (/ INR c))" in Hlog.')

Last: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

```rocq
- nra [Hlog].
```

Remaining allowance: $0.06334, 45 requests, 261.94 verifier seconds. Cited advice: rocq-00006, rocq-00023. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Proof is not complete.')

Last: (-32003, 'Coq: The reference by_contra was not found in the current environment.')

```rocq
{ by_contra H.
```

Remaining allowance: $0.59189, 32 requests, 286.96 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: No submitted proof received a failing verifier verdict.

Last: No final verifier check.

Remaining allowance: $0.72634, 39 requests, 298.19 verifier seconds. Cited advice: rocq-00014, rocq-00023. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12b_2002_p11

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04105 | 23 | unknown-reference | no-witness |
| luna-ace | 0 | $0.03523 | 19 | unknown-reference | no-witness |
| terra-none | 1 | $0.41553 | 28 | subproof-incomplete | accepted |
| terra-ace | 0 | $0.34997 | 26 | syntax-error | incomplete-proof |

**luna-none.** First: (-32003, 'Coq: The reference omega was not found in the current environment.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
lia.
```

Remaining allowance: $0.05895, 41 requests, 281.99 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: The reference omega was not found in the current environment.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
{ apply Zdivide_intro with (q := ka - kb); lia. }
```

Remaining allowance: $0.06477, 45 requests, 285.18 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, "Coq: Syntax error: ')' expected after [lconstr] (in [simple_tactic]).")

Last: (-32003, 'Coq: (in proof amc12b_2002_p11): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.65003, 38 requests, 277.82 verifier seconds. Cited advice: rocq-00002. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_42

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03662 | 17 | rewrite-no-match | rewrite-no-match |
| luna-ace | 1 | $0.00100 | 2 | none | accepted |
| terra-none | 1 | $0.07312 | 9 | unknown-reference | accepted |
| terra-ace | 1 | $0.07469 | 6 | unknown-reference | accepted |

**luna-none.** First: (-32003, 'Coq: Found no subterm matching "(27 * u) mod 40" in the current goal.')

Last: (-32003, 'Coq: Found no subterm matching "(v - 40) mod 40" in Hv\'.')

```rocq
rewrite (Nat.mod_small (v - 40) 40 Hsub) in Hv'.
```

Remaining allowance: $0.06338, 47 requests, 296.74 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12b_2004_p3

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03863 | 16 | type-mismatch | other |
| luna-ace | 0 | $0.03944 | 19 | unify-failure | unify-failure |
| terra-none | 1 | $0.19472 | 14 | unknown-reference | accepted |
| terra-ace | 1 | $0.05346 | 7 | unknown-reference | accepted |

**luna-none.** First: (-32003, 'Coq: In environment\nx, y : nat\nH : 2 ^ x * 3 ^ y = 1296\nThe term "Nat.pow_nonzero 3 y" has type "3 <> 0 -> 3 ^ y <> 0"\nwhile it is expected to have type "3 ^ y <> 0" (cannot unify \n"3 ^ y = 0" and "3 <> 0").')

Last: (-32003, 'Coq: Cannot find any non-recursive equality over y.')

```rocq
all: subst x; subst y; simpl in H |- *; try discriminate; reflexivity.
```

Remaining allowance: $0.06137, 48 requests, 109.69 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: In environment\nx, y : nat\nH : 2 ^ x * 3 ^ y = 1296\nUnable to unify "?M1835 <= ?M1835 * ?M1836" with "2 ^ x <= 2 ^ x".')

Last: (-32003, 'Coq: In environment\ny : nat\nH : 2 ^ 0 * 3 ^ S (S (S (S (S (S y))))) = 1296\nHx : 0 < 11\nHy : S (S (S (S (S (S y))))) < 7\nUnable to unify "8" with "0 + S (S (S (S (S (S y)))))".')

```rocq
all: reflexivity.
```

Remaining allowance: $0.06056, 45 requests, 59.22 verifier seconds. Cited advice: rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12_2000_p1

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 1 | $0.03390 | 9 | unknown-reference | accepted |
| luna-ace | 0 | $0.03850 | 15 | no-witness | type-mismatch |
| terra-none | 1 | $0.24320 | 9 | no-witness | accepted |
| terra-ace | 1 | $0.41042 | 33 | no-witness | accepted |

**luna-ace.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: In environment\ni, m, o : nat\nHim : i <> m\nHmo : m <> o\nHoi : o <> i\nHprod : i * m * o = 2001\nHsorted :\n forall x y z : nat,\n x <= y ->\n y <= z -> x <> y -> y <> z -> x * y * z = 2001 -> x + y + z <= 671\nHmil : i > m\nHiole : i <= o\nHmole : m <= o\nThe term "Him" has type "i <> m" while it is expected to have type \n"m <> i" (cannot unify "m = i" and "i = m").')

```rocq
- exact Him.
```

Remaining allowance: $0.06150, 49 requests, 273.13 verifier seconds. Cited advice: rocq-00003, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_629

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03751 | 16 | prover-crash | prover-crash |
| luna-ace | 0 | $0.04151 | 20 | prover-crash | no-witness |
| terra-none | 0 | $0.40870 | 40 | prover-crash | type-mismatch |
| terra-ace | 0 | $0.35455 | 30 | prover-crash | unknown-reference |

**luna-none.** First: (-32003, 'Coq: Stack overflow.')

Last: (-32003, 'Coq: Stack overflow.')

```rocq
{ cbn. discriminate. }
```

Remaining allowance: $0.06249, 48 requests, 237.57 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Stack overflow.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
nia. }
```

Remaining allowance: $0.05849, 44 requests, 261.43 verifier seconds. Cited advice: rocq-00018, rocq-00019. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Stack overflow.')

Last: (-32003, 'Coq: In environment\nHp : 3 > 0\nHe : 12 ^ 3 = (3 * 12) ^ 2\nHlt : 3 < 18\nHcube : forall x q : nat, x <> 0 -> x ^ 3 = (q * x) ^ 2 -> x = q * q\nThe term "He" has type "12 ^ 3 = (3 * 12) ^ 2"\nwhile it is expected to have type "12 ^ 3 = (2 * 12) ^ 2".')

```rocq
2: pose proof (Hcube 12 2 ltac:(lia) He); lia.
```

Remaining allowance: $0.59130, 24 requests, 248.33 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: Stack overflow.')

Last: (-32003, 'Coq: The reference Nat.pow_succ was not found in the current environment.')

```rocq
1: rewrite (Nat.pow_succ 16 2) in Heq.
```

Remaining allowance: $0.64545, 34 requests, 227.44 verifier seconds. Cited advice: rocq-00018, rocq-00025. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12a_2002_p13

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03711 | 15 | unify-failure | unknown-reference |
| luna-ace | 1 | $0.02623 | 12 | no-matching-clause | accepted |
| terra-none | 1 | $0.10887 | 8 | syntax-error | accepted |
| terra-ace | 1 | $0.09234 | 6 | subproof-incomplete | accepted |

**luna-none.** First: (-32003, 'Coq: In environment\na, b : R\nHa : 0 < a\nHb : 0 < b\nHab : a <> b\nHaa : Rabs (a - 1 / a) = 1\nHbb : Rabs (b - 1 / b) = 1\nHa0 : a <> 0\nHb0 : b <> 0\nUnable to unify "?M1831² = ?M1832²" with "(a - 1 / a) ^ 2 = 1".')

Last: (-32003, 'Coq: The reference norm_num was not found in the current environment.')

```rocq
norm_num.
```

Remaining allowance: $0.06289, 49 requests, 297.48 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

## validation

### imo_1960_p2

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03919 | 24 | no-applicable-tactic | incomplete-proof |
| luna-ace | 1 | $0.00632 | 6 | no-matching-clause | accepted |
| terra-none | 1 | $0.24141 | 24 | subproof-incomplete | accepted |
| terra-ace | 1 | $0.19023 | 11 | subproof-incomplete | accepted |

**luna-none.** First: (-32003, 'Coq: No applicable tactic.')

Last: (-32003, 'Coq: (in proof imo_1960_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.06081, 40 requests, 298.06 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### aime_1991_p6

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03157 | 11 | incomplete-proof | unknown-reference |
| luna-ace | 0 | $0.03469 | 13 | other | no-applicable-tactic |
| terra-none | 0 | $0.42626 | 20 | no-applicable-tactic | syntax-error |
| terra-ace | 0 | $0.36239 | 25 | prover-crash | syntax-error |

**luna-none.** First: (-32003, 'Coq: (in proof aime_1991_p6): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: The reference omega was not found in the current environment.')

```rocq
assert (Hz : (Int_part y + 1 <= Int_part x)%Z) by omega.
```

Remaining allowance: $0.06843, 53 requests, 268.53 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: Proof obligations may not be bypassed.

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
lra.
```

Remaining allowance: $0.06531, 51 requests, 263.68 verifier seconds. Cited advice: rocq-00004, rocq-00018, rocq-00025. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: No applicable tactic.')

Last: (-32003, "Coq: Syntax error: 'end' expected after [match_list] (in [ltac_expr]).")

```rocq
let rec early_upper k fuel := lazymatch fuel with | 0 => idtac | S ?fuel' => let A := fresh "A" in assert (A : (Int_part (r + IZR (Z.of_nat k) / 100) <= Int_part (r + 57 / 100))%Z).
```

Remaining allowance: $0.57374, 44 requests, 249.08 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

Last: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

```rocq
norm_num in Hc.
```

Remaining allowance: $0.63761, 39 requests, 139.53 verifier seconds. Cited advice: rocq-00003. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### algebra_others_exirrpowirrrat

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03804 | 24 | other | no-matching-clause |
| luna-ace | 0 | $0.03667 | 32 | type-mismatch | no-witness |
| terra-none | 0 | $0.40246 | 39 | other | no-witness |
| terra-ace | 0 | $0.32913 | 30 | type-mismatch | type-mismatch |

**luna-none.** First: (-32003, 'Coq: Unknown interpretation for notation "_ ²".')

Last: (-32003, 'Coq: No matching clauses for match.')

```rocq
field_simplify [HqR] in Hsq.
```

Remaining allowance: $0.06196, 40 requests, 296.29 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHeq : sqrt 2 = (IZR p / IZR q)%R\nThe term "0" has type "nat" while it is expected to have type "R".')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
nia.
```

Remaining allowance: $0.06333, 32 requests, 296.81 verifier seconds. Cited advice: rocq-00016, rocq-00025. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Not the right number of missing arguments (expected 1).')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
nia.
```

Remaining allowance: $0.59754, 25 requests, 297.35 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHpq : sqrt 2 = (IZR p / IZR q)%R\nThe term "0" has type "nat" while it is expected to have type "R".')

Last: (-32003, 'Coq: In environment\np, q : Z\nHq : q <> 0%Z\nHpq : sqrt 2 = (IZR p / IZR q)%R\nHqR : IZR q <> 0%R\nThe term "sqrt 2" has type "R" while it is expected to have type "nat".')

```rocq
assert (Hs : (sqrt 2) ^ 2 = 2) by apply Rsqr_sqrt; lra.
```

Remaining allowance: $0.67087, 34 requests, 296.94 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_303

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03663 | 23 | no-product | no-witness |
| luna-ace | 0 | $0.04003 | 23 | already-used | focus-error |
| terra-none | 1 | $0.23660 | 31 | focus-error | accepted |
| terra-ace | 0 | $0.32961 | 29 | no-witness | subproof-incomplete |

**luna-none.** First: (-32003, 'Coq: No product even after head-reduction.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
{ lia. }
```

Remaining allowance: $0.06337, 41 requests, 270.97 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: l is already used.')

Last: (-32003, 'Coq: This proof is focused, but cannot be unfocused this way')

```rocq
}
```

Remaining allowance: $0.05997, 41 requests, 223.41 verifier seconds. Cited advice: rocq-00007, rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: Proof is not complete.')

```rocq
assert (Hr : 80 mod n < n) by apply PeanoNat.Nat.mod_upper_bound; lia.
```

Remaining allowance: $0.67039, 35 requests, 289.60 verifier seconds. Cited advice: rocq-00004, rocq-00005. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### imo_1969_p2

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04147 | 21 | incomplete-proof | unknown-reference |
| luna-ace | 0 | $0.03866 | 19 | incomplete-proof | focus-error |
| terra-none | 0 | $0.42109 | 15 | type-mismatch | unknown-reference |
| terra-ace | 0 | $0.39029 | 23 | incomplete-proof | no-witness |

**luna-none.** First: (-32003, 'Coq: (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: The reference norm_num was not found in the current environment.')

```rocq
norm_num.
```

Remaining allowance: $0.05853, 43 requests, 296.76 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: This proof is focused, but cannot be unfocused this way')

```rocq
}
```

Remaining allowance: $0.06134, 45 requests, 296.60 verifier seconds. Cited advice: rocq-00022. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: In environment\nm, n : R\nk : nat\na : nat -> R\ny : R -> R\nHk : (0 < k)%nat\nHy :\n forall x : R,\n y x = sum_f_R0 (fun i : nat => cos (a i + x) / 2 ^ i) (Init.Nat.pred k)\nHym : y m = 0\nHyn : y n = 0\nN : nat\nThe term "0" has type "R" while it is expected to have type "nat".')

Last: (-32003, 'Coq: The variable pow_succ was not found in the current environment.')

```rocq
- rewrite pow_succ.
```

Remaining allowance: $0.57891, 49 requests, 297.43 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: (in proof imo_1969_p2): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
lra.
```

Remaining allowance: $0.60971, 41 requests, 297.13 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### aime_1991_p9

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04211 | 26 | no-witness | ring-failure |
| luna-ace | 1 | $0.03565 | 23 | unify-failure | accepted |
| terra-none | 1 | $0.19395 | 31 | no-witness | accepted |
| terra-ace | 1 | $0.21125 | 15 | no-matching-clause | accepted |

**luna-none.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: Tactic failure: not a valid ring equation.')

```rocq
replace ((22 / 7 * cos x - 1)²) with ((22 / 7 * cos x - 1) * (22 / 7 * cos x - 1)) in Htrig by ring.
```

Remaining allowance: $0.05789, 38 requests, 297.58 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12a_2019_p21

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03951 | 26 | unknown-reference | prover-crash |
| luna-ace | 0 | $0.04092 | 27 | incomplete-proof | no-applicable-tactic |
| terra-none | 0 | $0.26685 | 34 | none | no submission |
| terra-ace | 0 | $0.33867 | 38 | no-applicable-tactic | no-applicable-tactic |

**luna-none.** First: (-32003, 'Coq: The reference ring_nf was not found in the current environment.')

Last: ConnectionLost: (-33002, 'the Rocq server closed the connection')

Remaining allowance: $0.06049, 38 requests, 167.04 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: (in proof amc12a_2019_p21): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
lra.
```

Remaining allowance: $0.05908, 37 requests, 287.75 verifier seconds. Cited advice: rocq-00004, rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: No submitted proof received a failing verifier verdict.

Last: No final verifier check.

Remaining allowance: $0.73315, 30 requests, 297.60 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: No applicable tactic.')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
f_equal; field_simplify; nra.
```

Remaining allowance: $0.66133, 26 requests, 278.20 verifier seconds. Cited advice: rocq-00005, rocq-00021. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_37

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03253 | 23 | prover-crash | focus-error |
| luna-ace | 0 | $0.01893 | 23 | prover-crash | prover-crash |
| terra-none | 1 | $0.30382 | 43 | prover-crash | accepted |
| terra-ace | 1 | $0.25380 | 26 | subproof-incomplete | accepted |

**luna-none.** First: Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

Last: (-32003, 'Coq: [Focus] Wrong bullet -: Current bullet - is not finished.')

```rocq
- discriminate.
```

Remaining allowance: $0.06747, 41 requests, 44.34 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

Last: (-32003, 'Coq: Stack overflow.')

```rocq
vm_compute.
```

Remaining allowance: $0.08107, 41 requests, 54.29 verifier seconds. Cited advice: rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### imo_1984_p6

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03900 | 24 | already-used | no-witness |
| luna-ace | 0 | $0.03317 | 20 | already-used | prover-crash |
| terra-none | 0 | $0.23977 | 20 | already-used | prover-crash |
| terra-ace | 0 | $0.38332 | 21 | already-used | incomplete-proof |

**luna-none.** First: (-32003, 'Coq: a is already used.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
nia.
```

Remaining allowance: $0.06100, 40 requests, 96.10 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: a is already used.')

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 59s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
- nia.
```

Remaining allowance: $0.06683, 44 requests, 48.76 verifier seconds. Cited advice: rocq-00003, rocq-00005. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: a is already used.')

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
nia.
```

Remaining allowance: $0.76023, 44 requests, 56.29 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: a is already used.')

Last: (-32003, 'Coq: (in proof imo_1984_p6): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.61668, 43 requests, 277.85 verifier seconds. Cited advice: rocq-00016, rocq-00022. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12a_2020_p21

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04107 | 22 | syntax-error | syntax-error |
| luna-ace | 0 | $0.03637 | 21 | syntax-error | incomplete-proof |
| terra-none | 0 | $0.41970 | 19 | incomplete-proof | rewrite-no-match |
| terra-ace | 0 | $0.36706 | 20 | syntax-error | prover-crash |

**luna-none.** First: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

Last: (-32003, "Coq: Syntax error: [term level 200] expected after '(' (in [term]).")

```rocq
{ apply (proj1 ((Nat.Private_NDivProp.mod_divides n 5) (by lia))).
```

Remaining allowance: $0.05893, 42 requests, 269.18 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, "Coq: Syntax error: [term level 200] expected after '=>' (in [binder_constr]).")

Last: (-32003, 'Coq: (in proof amc12a_2020_p21): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.06363, 43 requests, 238.29 verifier seconds. Cited advice: rocq-00004, rocq-00018, rocq-00019. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: (in proof amc12a_2020_p21): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: Found no subterm matching "5 * Nat.gcd (fact 10) n" in the current goal.')

```rocq
{ rewrite <- Hlcm.
```

Remaining allowance: $0.58030, 45 requests, 186.83 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, "Coq: Syntax error: 'with' or 'in' expected (in [ltac_expr]).")

Last: (-32003, 'Coq: Stack overflow.')

```rocq
assert (F10 : fact 10 = 3628800) by native_compute.
```

Remaining allowance: $0.63294, 44 requests, 210.19 verifier seconds. Cited advice: rocq-00005, rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_algebra_282

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03125 | 30 | already-used | incomplete-proof |
| luna-ace | 0 | $0.03626 | 20 | already-used | incomplete-proof |
| terra-none | 0 | $0.30052 | 33 | incomplete-proof | incomplete-proof |
| terra-ace | 0 | $0.30663 | 34 | incomplete-proof | incomplete-proof |

**luna-none.** First: (-32003, 'Coq: f is already used.')

Last: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.06875, 34 requests, 287.70 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: f is already used.')

Last: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.06374, 44 requests, 279.11 verifier seconds. Cited advice: rocq-00006, rocq-00025. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.69948, 31 requests, 292.82 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

Last: (-32003, 'Coq: (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.69337, 30 requests, 288.82 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_405

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03686 | 13 | already-used | rewrite-no-match |
| luna-ace | 0 | $0.04054 | 10 | already-used | rewrite-no-match |
| terra-none | 0 | $0.40775 | 12 | rewrite-no-match | prover-crash |
| terra-ace | 1 | $0.31091 | 18 | rewrite-no-match | accepted |

**luna-none.** First: (-32003, 'Coq: a is already used.')

Last: (-32003, 'Coq: Found no subterm matching "t (n + 17) mod 7" in the current goal.')

```rocq
rewrite E1, E0.
```

Remaining allowance: $0.06314, 51 requests, 296.02 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: a is already used.')

Last: (-32003, 'Coq: Found no subterm matching "t 13" in the current goal.')

```rocq
rewrite (h2 13) by lia.
```

Remaining allowance: $0.05946, 54 requests, 297.69 verifier seconds. Cited advice: rocq-00005, rocq-00007. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Found no subterm matching "t 1" in the current goal.')

Last: Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
repeat rewrite Nat.add_mod by lia.
```

Remaining allowance: $0.59225, 52 requests, 265.82 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12b_2002_p3

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.03719 | 20 | unknown-reference | incomplete-proof |
| luna-ace | 1 | $0.00569 | 5 | unknown-reference | accepted |
| terra-none | 1 | $0.09884 | 11 | unknown-reference | accepted |
| terra-ace | 1 | $0.04052 | 9 | none | accepted |

**luna-none.** First: (-32003, 'Coq: The reference omega was not found in the current environment.')

Last: (-32003, 'Coq: (in proof amc12b_2002_p3): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

Remaining allowance: $0.06281, 44 requests, 298.38 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_43

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.01845 | 20 | unknown-reference | prover-crash |
| luna-ace | 0 | $0.01905 | 29 | prover-crash | prover-crash |
| terra-none | 0 | $0.40538 | 30 | no-witness | unify-failure |
| terra-ace | 0 | $0.17985 | 23 | prover-crash | prover-crash |

**luna-none.** First: (-32003, 'Coq: The reference Nat.div_mul_cancel was not found in the current environment.')

Last: Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
{ vm_compute. }
```

Remaining allowance: $0.08155, 44 requests, 35.64 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Out of memory.')

Last: ConnectionLost: (-33002, 'the Rocq server closed the connection')

Remaining allowance: $0.08095, 35 requests, 51.07 verifier seconds. Cited advice: rocq-00004, rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: Tactic failure: Cannot find witness.')

Last: (-32003, 'Coq: In environment\np := 15 ^ 233 : nat\nHp : p <> 0\nHp1 : 1 < p\nf :=\n fix f (n : nat) : nat :=\n match n with\n | 0 => 1\n | S n0 => (S n0 * f n0) mod p\n end\n : nat -> nat\nn : nat\nIH : f n = fact n mod p\nUnable to unify "(S n * fact n) mod p" with "(S n * (fact n mod p)) mod p".')

```rocq
reflexivity. }
```

Remaining allowance: $0.59462, 34 requests, 91.62 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: Out of memory.')

Last: ConnectionLost: (-33002, 'the Rocq server closed the connection')

Remaining allowance: $0.82015, 41 requests, 57.73 verifier seconds. Cited advice: rocq-00003, rocq-00018. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### mathd_numbertheory_530

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04097 | 24 | syntax-error | other |
| luna-ace | 0 | $0.03574 | 20 | subproof-incomplete | unknown-reference |
| terra-none | 0 | $0.33714 | 42 | type-mismatch | type-mismatch |
| terra-ace | 0 | $0.37150 | 25 | not-convertible | no-applicable-tactic |

**luna-none.** First: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

Last: (-32003, 'Coq: The reference Nat.mod_eq_zero_of_dvd was not found in the current\nenvironment.')

```rocq
rewrite (Nat.mod_eq_zero_of_dvd Hgn) in E.
```

Remaining allowance: $0.05903, 40 requests, 297.54 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Proof is not complete.')

Last: (-32003, 'Coq: The reference exact_mod_cast was not found in the current environment.')

```rocq
{ exact_mod_cast H5R.
```

Remaining allowance: $0.06426, 44 requests, 298.02 verifier seconds. Cited advice: rocq-00007, rocq-00018, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: In environment\nn, k : nat\nd := Nat.gcd n k : nat\nx : nat\nhn : (0 < x * d)%nat\ny : nat\nhk : (0 < y * d)%nat\nhu : INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d)) < 6\nhl : 5 < INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d))\nHx : n = (x * d)%nat\nHy : k = (y * d)%nat\nThe term "0" has type "R" while it is expected to have type "nat".')

Last: (-32003, 'Coq: In environment\nn, k : nat\nd := Nat.gcd n k : nat\nx : nat\nhn : (0 < x * d)%nat\ny : nat\nhk : (0 < y * d)%nat\nhu : INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d)) < 6\nhl : 5 < INR x * IZR (Z.of_nat d) / IZR (Z.of_nat (y * d))\nHx : n = (x * d)%nat\nHy : k = (y * d)%nat\nThe term "0" has type "R" while it is expected to have type "nat".')

```rocq
assert (hd : d <> 0) by (intro E; subst d; simpl in hn; lia).
```

Remaining allowance: $0.66286, 22 requests, 297.22 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-ace.** First: (-32003, 'Coq: Not convertible.')

Last: (-32003, 'Coq: No applicable tactic.')

```rocq
nra.
```

Remaining allowance: $0.62850, 39 requests, 297.81 verifier seconds. Cited advice: rocq-00004, rocq-00008. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

### amc12_2001_p21

| Arm | Solved | Cost | Requests | First error | Last error |
|---|---:|---:|---:|---|---|
| luna-none | 0 | $0.04462 | 22 | prover-crash | prover-crash |
| luna-ace | 0 | $0.03846 | 35 | prover-crash | no-witness |
| terra-none | 0 | $0.39721 | 20 | unknown-reference | prover-crash |
| terra-ace | 1 | $0.35166 | 28 | unknown-reference | accepted |

**luna-none.** First: Rocq transport failure ((-33000, 'no reply from the Rocq server within 57s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
repeat (first [ nia | destruct b as [|b] ]).
```

Remaining allowance: $0.05538, 42 requests, 6.22 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**luna-ace.** First: (-32003, 'Coq: Stack overflow.')

Last: (-32003, 'Coq: Tactic failure: Cannot find witness.')

```rocq
assert (Hneq : (35520 <> 40320)%nat) by nia.
```

Remaining allowance: $0.06154, 29 requests, 274.32 verifier seconds. Cited advice: rocq-00003, rocq-00024. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.

**terra-none.** First: (-32003, 'Coq: The reference interval_cases was not found in the current environment.')

Last: Rocq transport failure ((-33000, 'no reply from the Rocq server within 60s')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
repeat rewrite Nat.Div0.mul_mod in Hsevenprod.
```

Remaining allowance: $0.60279, 44 requests, 151.46 verifier seconds. Cited advice: none. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.


## Fixed book-swap and effort diagnostics

### effort/high/aime_1988_p8

Solved: True; cost: $0.07313; requests: 5; failing checks: 2.

### effort/high/amc12a_2020_p13

Solved: False; cost: $0.31954; requests: 22; failing checks: 3.

Final error: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

```rocq
{ field_simpl [Ha0, Hb0, Hc0] in Hrat.
```

### effort/high/amc12b_2002_p11

Solved: False; cost: $0.25798; requests: 26; failing checks: 0.

Final error: None

### effort/high/amc12b_2004_p3

Solved: True; cost: $0.20354; requests: 11; failing checks: 5.

### effort/high/mathd_algebra_323

Solved: True; cost: $0.01892; requests: 2; failing checks: 1.

### effort/high/mathd_algebra_43

Solved: True; cost: $0.00603; requests: 1; failing checks: 0.

### effort/high/mathd_numbertheory_326

Solved: True; cost: $0.00707; requests: 1; failing checks: 0.

### effort/high/mathd_numbertheory_629

Solved: True; cost: $0.33102; requests: 15; failing checks: 6.

### effort/low/aime_1988_p8

Solved: True; cost: $0.05120; requests: 3; failing checks: 2.

### effort/low/amc12a_2020_p13

Solved: False; cost: $0.39720; requests: 21; failing checks: 9.

Final error: (-32003, 'Coq: No applicable tactic.')

```rocq
nra.
```

### effort/low/amc12b_2002_p11

Solved: False; cost: $0.40107; requests: 20; failing checks: 6.

Final error: (-32003, 'Coq: Tactic failure:  Cannot find witness.')

```rocq
lia.
```

### effort/low/amc12b_2004_p3

Solved: False; cost: $0.20335; requests: 17; failing checks: 9.

Final error: Deadline: (-33000, 'no reply from the Rocq server within 1s')

### effort/low/mathd_algebra_323

Solved: True; cost: $0.01571; requests: 2; failing checks: 1.

### effort/low/mathd_algebra_43

Solved: True; cost: $0.00424; requests: 1; failing checks: 0.

### effort/low/mathd_numbertheory_326

Solved: True; cost: $0.00640; requests: 1; failing checks: 0.

### effort/low/mathd_numbertheory_629

Solved: True; cost: $0.17195; requests: 23; failing checks: 5.

### swaps/luna-terra-book/amc12a_2008_p4

Solved: False; cost: $0.02632; requests: 48; failing checks: 23.

Final error: (-32003, 'Coq:  (in proof amc12a_2008_p4): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

### swaps/luna-terra-book/amc12a_2019_p21

Solved: False; cost: $0.03551; requests: 38; failing checks: 6.

Final error: (-32003, 'Coq: Syntax error: [ltac_use_default] expected after [tactic] (in [tactic_command]).')

```rocq
set s := sqrt 2.
```

### swaps/luna-terra-book/imo_1981_p6

Solved: True; cost: $0.00745; requests: 6; failing checks: 2.

### swaps/luna-terra-book/induction_prod1p1onk3le3m1onn

Solved: True; cost: $0.02294; requests: 22; failing checks: 3.

### swaps/luna-terra-book/mathd_algebra_282

Solved: False; cost: $0.03786; requests: 27; failing checks: 6.

Final error: (-32003, 'Coq:  (in proof mathd_algebra_282): Attempt to save an incomplete proof\n(there are remaining open goals).')

```rocq
Qed.
```

### swaps/luna-terra-book/mathd_numbertheory_303

Solved: False; cost: $0.04015; requests: 26; failing checks: 7.

Final error: (-32003, 'Coq: The variable d was not found in the current environment.')

```rocq
- do 45 destruct d.
```

### swaps/luna-terra-book/mathd_numbertheory_33

Solved: True; cost: $0.00661; requests: 8; failing checks: 3.

### swaps/luna-terra-book/mathd_numbertheory_43

Solved: False; cost: $0.01713; requests: 20; failing checks: 12.

Final error: Rocq transport failure ((-33002, 'the Rocq server closed the connection')): the prover server was restarted and this attempt has no verdict. Try again with a cheaper tactic or a smaller proof state.

```rocq
apply (proj2 (Nat.Div0.div_exact (fact 942) (15^233))).
```

### swaps/terra-luna-book/amc12a_2008_p4

Solved: True; cost: $0.32284; requests: 11; failing checks: 5.

### swaps/terra-luna-book/amc12a_2019_p21

Solved: False; cost: $0.25228; requests: 39; failing checks: 0.

Final error: None

### swaps/terra-luna-book/imo_1981_p6

Solved: True; cost: $0.05144; requests: 7; failing checks: 0.

### swaps/terra-luna-book/induction_prod1p1onk3le3m1onn

Solved: True; cost: $0.37607; requests: 21; failing checks: 7.

### swaps/terra-luna-book/mathd_algebra_282

Solved: False; cost: $0.39551; requests: 26; failing checks: 8.

Final error: (-32003, 'Coq: Tactic failure: not a valid ring equation.')

```rocq
replace (9 / (1 + 1) : R) with (9 / 2) by ring.
```

### swaps/terra-luna-book/mathd_numbertheory_303

Solved: False; cost: $0.39750; requests: 23; failing checks: 8.

Final error: (-32003, 'Coq: Syntax error: illegal begin of vernac.')

```rocq
}.
```

### swaps/terra-luna-book/mathd_numbertheory_33

Solved: True; cost: $0.02445; requests: 3; failing checks: 1.

### swaps/terra-luna-book/mathd_numbertheory_43

Solved: False; cost: $0.21935; requests: 26; failing checks: 14.

Final error: ConnectionLost: (-33002, 'the Rocq server closed the connection')
