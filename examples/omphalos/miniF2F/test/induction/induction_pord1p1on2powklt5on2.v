(* miniF2F problem: induction_pord1p1on2powklt5on2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integer $n$, $(\prod_{k=1}^{n} (1 + 1/2^k)) < 5/2$.

   Informal proof:
   For $n=1$ or $n=2$, the statement is trivially true.
   For $n\geq 3$, we prove a stronger statement $(\prod_{k=1}^{n} (1 + 1/2^k)) < 5/2 *
   (1 - \frac{1}{2^n})$.
   This can be proved by induction: starting with $n=3$, the base case is $(1+1/2) *
   (1+1/4) * (1+1/8) = 135/64 < 5/2 * (1 - 1/8) = 35/16$, which holds true.
   For the inductive case, the inductive hypothesis is $(\prod_{k=1}^{n_0} (1 + 1/2^k))
   < 5/2 * (1 - \frac{1}{2^n_0})$. We then have $(\prod_{k=1}^{n_0+1} (1 + 1/2^k)) =
   \prod_{k=1}^{n_0} (1 + 1/2^k)) * (1+1/2^{n_0+1}) < 5/2 * (1 - \frac{1}{2^n_0}) *
   (1+\frac{1}{2^{n_0+1}}) = 5/2 * (1 - \frac{1}{2^n_0} + \frac{1}{2^{n_0+1}} -
   \frac{1}{2^n_0 * 2^{n_0+1}}) = 5/2 * (1-\frac{1}{2^{n_0+1}} - \frac{1}{2^n_0 *
   2^{n_0+1}}) < 5/2 * (1-\frac{1}{2^{n_0+1}})$. Hence the inductive case holds true.
*)



Require Import Coq.Reals.Reals.
Open Scope R_scope.

Fixpoint prod_1_to_n (n : nat) : R :=
  match n with
  | 0 => 1
  | S k => prod_1_to_n k * (1 + / (2 ^ (S k)))
  end.

Theorem induction_pord1p1on2powklt5on2 :
  forall n : nat,
    (0 < n)%nat ->
    prod_1_to_n n < 5 / 2.

Proof.
Admitted.
