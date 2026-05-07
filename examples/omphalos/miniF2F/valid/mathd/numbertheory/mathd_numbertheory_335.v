(* miniF2F problem: mathd_numbertheory_335
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   When Rachel divides her favorite number by 7, she gets a remainder of 5. What will
   the remainder be if she multiplies her favorite number by 5 and then divides by 7?
   Show that it is 4.

   Informal proof:
   Let $n$ be Rachel's favorite number.  Then $n \equiv 5 \pmod{7}$, so $5n \equiv 5
   \cdot 5 \equiv 25 \equiv 4 \pmod{7}$.
*)

Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_335 :
  forall n : nat,
  n mod 7 = 5 -> (5 * n) mod 7 = 4.
Proof.
Admitted.