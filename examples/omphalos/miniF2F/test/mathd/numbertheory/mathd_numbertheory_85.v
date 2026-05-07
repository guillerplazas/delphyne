(* miniF2F problem: mathd_numbertheory_85
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   My father's age is $1222_{3}$, in base three to represent his three lower limbs --
   two legs and a cane.  How old is he in base ten? Show that it is 53.

   Informal proof:
   $1222_{3} = 2\cdot3^{0}+2\cdot3^{1}+2\cdot3^{2}+1\cdot3^{3} = 2+6+18+27 = 53$.
*)

Require Import Arith.

Theorem mathd_numbertheory_85 :
  1 * 3^3 + 2 * 3^2 + 2 * 3 + 2 = 53.
Proof.
Admitted.