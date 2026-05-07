(* miniF2F problem: induction_divisibility_9div10tonm1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that 9 divides $10^n - 1$ for any natural number n.

   Informal proof:
   We use induction. The base case for $n=0$  is true since $9 \mid 0$.
   Assume the result is true for some $n \geq 0$. Then $9\mid 10^n - 1$, and there
   exists $k$ such that $10^n - 1$ = 9k.
   Finally, rewriting $10^{n+1}-1 = 10*(10^n - 1) + 9=9 * (10*k+1)$, which implies the
   result for $n+1$.
*)

Require Import Coq.Numbers.Natural.Abstract.NDiv.
Require Import Coq.Arith.PeanoNat.

Theorem induction_divisibility_9div10tonm1 :
  forall n : nat, 0 < n -> Nat.divide 9 (10^n - 1).

Proof.
Admitted.
