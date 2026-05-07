(* miniF2F problem: mathd_numbertheory_247
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve the congruence $3n \equiv 2 \pmod{11}$, as a residue modulo 11.  (Give an
   answer between 0 and 10.) Show that it is 8.

   Informal proof:
   Note that $2 \equiv -9 \pmod{11}$, so we can write the given congruence as $3n \equiv
   -9 \pmod{11}$.  Since 3 is relatively prime to 11, we can divide both sides by 3, to
   get $n \equiv -3 \equiv 8 \pmod{11}$.
*)

Require Import Arith.

Theorem mathd_numbertheory_247 : forall n : nat,
  (3 * n) mod 11 = 2 -> n mod 11 = 8.
Proof.
Admitted.
