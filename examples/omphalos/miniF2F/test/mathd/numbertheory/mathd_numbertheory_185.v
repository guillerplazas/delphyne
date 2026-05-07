(* miniF2F problem: mathd_numbertheory_185
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   When a number is divided by 5, the remainder is 3. What is the remainder when twice
   the number is divided by 5? Show that it is 1.

   Informal proof:
   If our number is $n$, then $n\equiv 3\pmod5$.  This tells us that  \[2n=n+n\equiv
   3+3\equiv1\pmod5.\] The remainder is $1$ when the number is divided by 5.
*)

Require Import Nat.

Theorem mathd_numbertheory_185:
  forall n : nat,
  n mod 5 = 3 ->
  (2 * n) mod 5 = 1.
Proof.
Admitted.