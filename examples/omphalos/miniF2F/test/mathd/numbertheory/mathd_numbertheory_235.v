(* miniF2F problem: mathd_numbertheory_235
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the units digit of $29 \cdot 79 + 31 \cdot 81$. Show that it is 2.

   Informal proof:
   $9 \cdot 9 + 1 \cdot 1 = 81 + 1 = 82$, so the units digit is $2$.
*)

Require Import Coq.Arith.PeanoNat.

Theorem mathd_numbertheory_235 : 
  (29 * 79 + 31 * 81) mod 10 = 2.
Proof.
Admitted.