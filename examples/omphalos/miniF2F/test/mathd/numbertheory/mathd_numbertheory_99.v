(* miniF2F problem: mathd_numbertheory_99
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve the congruence $2n \equiv 15 \pmod{47}$, as a residue modulo 47.  (Give an
   answer between 0 and 46.) Show that it is 31.

   Informal proof:
   Note that $15 \equiv 62 \pmod{47}$, so we can write the given congruence as $2n
   \equiv 62 \pmod{47}$.  Since 2 is relatively prime to 47, we can divide both sides by
   2, to get $n \equiv 31 \pmod{47}$.
*)

Require Import Nat.
Require Import ZArith.

Theorem mathd_numbertheory_99:
  forall n : nat,
  (2 * n) mod 47 = 15 ->
  n mod 47 = 31.
Proof.
Admitted.