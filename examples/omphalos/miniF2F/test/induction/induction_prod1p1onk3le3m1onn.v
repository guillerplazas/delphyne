(* miniF2F problem: induction_prod1p1onk3le3m1onn
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any positive integer $n$, we have $\prod_{k=1}^n (1 + 1/k^3) \leq 3 -
   1/n$.

   Informal proof:
   We can prove this by induction on n. For the base case, $n=1$, the statement is
   trivial.
   For the inductive case, we assume $\prod_{k=1}^{n_0} (1 + 1/k^3) \leq 3 - 1/n_0$.
   Therefore, we have $\prod_{k=1}^{n_0+1} (1 + 1/k^3) \leq (3-1/n_0) (1 + 1/(n_0+1)^3)
   = 3 + \frac{3}{(n_0+1)^3}-\frac{1}{n_0}-\frac{1}{n_0 (n_0+1)^3}$.
   It hence suffices to show that $\frac{3}{(n_0+1)^3}+\frac{1}{n_0+1} \leq
   \frac{1}{n_0} + \frac{1}{n_0 (n_0+1)^3}$, which is equivalent to
   $3n_0 + n_0 (n_0+1)^2 \leq (n_0+1)^3 + 1$. Simplifying, we get
   $n_0^2 - n_0 + 2 \geq 0$. This is obviously true for $n\geq 1$.
*)

Require Import Coq.Reals.Reals.

Open Scope R_scope.



Fixpoint prod_1_to_n (f : nat -> R) (n : nat) : R :=
  match n with
  | O => 1
  | S p => prod_1_to_n f p * f (S p)
  end.



Theorem induction_prod1p1onk3le3m1onn :
  forall (n : nat),
    (n > 0)%nat ->
    prod_1_to_n (fun k => 1 + / (INR k ^ 3)) n <= 3 - / INR n.

Proof.
Admitted.
