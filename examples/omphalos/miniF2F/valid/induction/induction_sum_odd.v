(* miniF2F problem: induction_sum_odd
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integer $n$, $\sum_{k=0}^{n-1} (2k + 1) = n^2$.

   Informal proof:
   We show the result by induction on $n$. The result is trivial for $n=1$. Let us
   assume it is true for $n \geq 1$.
   We have that $\sum_{k=0}^{(n+1)-1} (2k + 1) = \sum_{k=0}^{n-1} (2k + 1) + (2n + 1)$.
   The induction hypothesis tells us that $\sum_{k=0}^{n-1} (2k + 1) = n^2$. So
   $\sum_{k=0}^{(n+1)-1} (2k + 1) = n^2 + 2n +1 = (n+1)^2$ and the result is true for
   $n+1$.
   By induction, we conclude that the result is true for all positive integer $n$.
*)

Require Import Coq.Arith.Arith.

(* Helper function to compute the sum of f from 0 to n-1 *)
Fixpoint sum_n (f : nat -> nat) (n : nat) : nat :=
  match n with
  | 0 => 0
  | S m => f m + sum_n f m
  end.

Theorem induction_sum_odd : forall n : nat,
  n > 0 ->
  sum_n (fun k => 2 * k + 1) n = n * n.
Proof.
Admitted.
