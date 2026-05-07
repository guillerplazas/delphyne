(* miniF2F problem: induction_divisibility_3divnto3m2n
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any natural number $n \in \mathbb{N}$, $3 \mid n^3 + 2n$ .

   Informal proof:
   We show the result by induction on $n$. The result is trivial for $n=0$. Let us
   assume it is true for $n \geq 0$.
   We have $(n+1)^3+2(n+1) = (n^3+3n^2+3n+1) + (2n+2) = n^3+2n + 3n^2+3n+3$. From the
   induction hypothesis, we know that $3$ divides $n^3+2n$. Since $3$ also divides
   $3n^2+3n+3$, the result is also true in $n+1$ and we have by induction that the
   result is true for all $n$.
*)

Require Import Nat.
Require Import Arith.

Theorem induction_divisibility_3divnto3m2n :
  forall n : nat, exists k : nat, n^3 + 2*n = 3*k.
Proof.
Admitted.