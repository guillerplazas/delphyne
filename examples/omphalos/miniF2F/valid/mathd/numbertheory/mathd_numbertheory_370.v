(* miniF2F problem: mathd_numbertheory_370
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $n$ gives a remainder of 3 when divided by 7, then what remainder does $2n+1$ give
   when divided by 7? Show that it is 0.

   Informal proof:
   If $n$ gives a remainder of 3 when divided by 7, then $n = 7k+3$ for some integer
   $k$. Therefore, $2n+1 = 2(7k+3)+1 = 14k+6+1 = 14k+7 = 7(2k+1)$. Since $7(2k+1)$ is
   divisible by 7, the remainder when $2n+1$ is divided by 7 is $0$.
*)

Require Import Arith.
Require Import Nat.

Theorem mathd_numbertheory_370:
  forall n : nat, 
    (n mod 7 = 3) -> 
    (2 * n + 1) mod 7 = 0.
Proof.
Admitted.