(* miniF2F problem: induction_sumkexp3eqsumksq
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for all natural numbers $n$, we have $\sum_{k=0}^{n-1}k^3 =
   \left(\sum_{k=0}^{n-1}k\right)^2$.

   Informal proof:
   We show the result by induction on $n$. The result is trivial for $n=1$. Let us
   assume it is true for $n \geq 1$.
   We have that $\left(\sum_{k=0}^{(n+1)-1}k\right)^2 =
   \left(\left(\sum_{k=0}^{n-1}k\right) + n\right)^2 = \left(\sum_{k=0}^{n-1}k\right)^2
   + n^2 + 2n\left(\sum_{k=0}^{n-1}k\right)$. Using the induction hypothesis, we have:
   $\left(\sum_{k=0}^{(n+1)-1}k\right)^2 = \sum_{k=0}^{n-1}k^3 + n^2 +
   2n\left(\sum_{k=0}^{n-1}k\right)$.
   However, $\left(\sum_{k=0}^{n-1}k\right) = \frac{n(n-1)}{2}$ so $n^2 +
   2n\left(\sum_{k=0}^{n-1}k\right) = n^2 + (n^3 - n^2) = n^3$ and
   $\left(\sum_{k=0}^{(n+1)-1}k\right)^2 = \sum_{k=0}^{(n+1)-1}k^3$, proving the result
   in $n+1$.
   By induction, we have that the result is true for any natural number $n$.
*)

Require Import Coq.Arith.Arith.


Fixpoint sum_to (f : nat -> nat) (n : nat) :=
  match n with
  | 0 => 0
  | S p => sum_to f p + f p
  end.


Notation "∑ k < n , f" :=
  (sum_to (fun k => f) n)
  (at level 60, k ident, n at level 60, f at level 60).

Theorem induction_sumkexp3eqsumksq :
  forall n : nat,
    (∑ k < n, k^3) = (∑ k < n, k)^2.

Proof.
Admitted.
