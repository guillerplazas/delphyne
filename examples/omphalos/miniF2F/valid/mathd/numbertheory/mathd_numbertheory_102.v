(* miniF2F problem: mathd_numbertheory_102
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the remainder of $2^8$ when it is divided by 5. Show that it is 1.

   Informal proof:
   $2^4 = 16 \equiv 1 \pmod{5}$, so $2^8 = 2^{2 \cdot 4} = (2^4)^2 = 16^2 \equiv 1^2
   \equiv 1 \pmod{5}$.
*)

Require Import ZArith.

Open Scope Z_scope.

Theorem mathd_numbertheory_102 :
  (2^8) mod 5 = 1.
Proof.
Admitted.