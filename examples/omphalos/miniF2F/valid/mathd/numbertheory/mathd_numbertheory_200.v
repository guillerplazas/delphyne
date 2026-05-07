(* miniF2F problem: mathd_numbertheory_200
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Tim is doing a cakewalk with $11$ steps. He takes his first step on step $1$ and
   takes a total of $139$ steps, walking in a circle (so that after the 11th step he
   reaches the first step again). Which step of the cakewalk does he end on? Show that
   it is 7.

   Informal proof:
   When you divide $139$ steps by $11$ steps, you get $12$ with a remainder of $7$.
   Therefore, Tim lands on step $7$.
*)

Require Import Arith.

Theorem mathd_numbertheory_200 :
  139 mod 11 = 7.
Proof.
Admitted.