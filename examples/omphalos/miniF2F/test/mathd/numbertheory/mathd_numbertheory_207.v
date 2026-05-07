(* miniF2F problem: mathd_numbertheory_207
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Convert $852_9$ to base 10. Show that it is 695.

   Informal proof:
   We have that $852_9 = 8(9^2) +5(9^1)+ 2(9^0) = 8(81)+5(9)+2(1)=648 + 45 + 2 = 695$.
*)

Require Import Arith.

Theorem mathd_numbertheory_207 :
  8 * 9^2 + 5 * 9 + 2 = 695.
Proof.
Admitted.