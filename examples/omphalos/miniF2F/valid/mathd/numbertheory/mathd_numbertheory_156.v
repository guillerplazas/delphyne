(* miniF2F problem: mathd_numbertheory_156
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $n$ be a positive integer.  What is the greatest possible value of $\gcd(n + 7,
   2n + 1)$? Show that it is 13.

   Informal proof:
   Let $d = \gcd(n + 7, 2n + 1)$, so $d$ divides both $n + 7$ and $2n + 1$.  Then $d$
   divides $2(n + 7) - (2n + 1) = 13$, so $d$ is at most 13.

   If $n = 6$, then $\gcd(n + 7, 2n + 1) = \gcd(13,13) = 13$, which shows that the value
   of 13 is attainable.  Therefore, the greatest possible value of $\gcd(n + 7, 2n + 1)$
   is $13$.
*)

Require Import Nat.
Require Import Arith.

Theorem mathd_numbertheory_156 :
  forall n : nat,
  n > 0 ->
  gcd (n + 7) (2 * n + 1) <= 13.
Proof.
Admitted.