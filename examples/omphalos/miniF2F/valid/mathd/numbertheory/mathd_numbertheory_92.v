(* miniF2F problem: mathd_numbertheory_92
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve the congruence $5n \equiv 8 \pmod{17}$, as a residue modulo 17.  (Give an
   answer between 0 and 16.) Show that it is 5.

   Informal proof:
   Note that $8 \equiv 25 \pmod{17}$, so we can write the given congruence as $5n \equiv
   25 \pmod{17}$.  Since 5 is relatively prime to 17, we can divide both sides by 5, to
   get $n \equiv 5 \pmod{17}$.
*)

Require Import Arith.

Theorem mathd_numbertheory_92:
  forall n : nat, 
  (5 * n mod 17 = 8) -> 
  (n mod 17 = 5).
Proof.
Admitted.