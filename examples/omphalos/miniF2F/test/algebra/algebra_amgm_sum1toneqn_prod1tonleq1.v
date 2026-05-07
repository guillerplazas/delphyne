(* miniF2F problem: algebra_amgm_sum1toneqn_prod1tonleq1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For a sequence of nonnegative real numbers $a_1, a_2, \ldots, a_n$ such that
   $\sum_{i=1}^n a_i = n$, show that $\prod_{i=1}^n a_i \leq 1$.

   Informal proof:
   By the arithmetic-geometric mean inequality, we have that:
   $$\frac{\sum_{i=1}^n a_i}{n} \geq \left(\prod_{i=1}^n a_i\right)^\frac{1}{n}$$
   Since $\sum_{i=1}^n a_i = n$, the inequality becomes:
   $$1 \geq \left(\prod_{i=1}^n a_i\right)^\frac{1}{n}$$
   Exponentiating over $n$ gives the desired inequality.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.


Fixpoint sum_n (a : nat -> R) (n : nat) : R :=
  match n with
  | 0 => 0
  | S p => sum_n a p + a p
  end.


Fixpoint prod_n (a : nat -> R) (n : nat) : R :=
  match n with
  | 0 => 1
  | S p => prod_n a p * a p
  end.


Theorem algebra_amgm_sum1toneqn_prod1tonleq1:
  forall (n : nat) (a : nat -> R),
    (forall i, (i < n)%nat -> 0 <= a i) ->
    sum_n a n = INR n ->
    prod_n a n <= 1.

Proof.
Admitted.
