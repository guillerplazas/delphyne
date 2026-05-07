(* miniF2F problem: induction_divisibility_3div2tooddnp1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For a natural number $n$, show that $3 \mid (2^{2n+1}+1)$.

   Informal proof:
   By induction, the base case for $n=0$ is true since $3 \mid 2+ 1 = 3$.
   Assuming the property holds at $n$, let $k$ be the positive integer such that
   $3k=2^{2n+1}+1$
   Then,  $2^{2(n+1)+1}+1=4.2^{2n+1} + 1 = 4(3k-1)+1=3(4k-1)$.
   Since 4k-1 > 0, we have showed the property at $n+1$.
*)

Require Import Nat.
Require Import ZArith.
Require Import Znumtheory.

Theorem induction_divisibility_3div2tooddnp1:
  forall n : nat,
  (exists k, 2^(2 * n + 1) + 1 = 3 * k)%nat.
Proof.
Admitted.