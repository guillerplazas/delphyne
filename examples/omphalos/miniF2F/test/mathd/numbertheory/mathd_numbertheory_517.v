(* miniF2F problem: mathd_numbertheory_517
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the modulo 4 residue of $121 \cdot 122 \cdot 123$. Show that it is 2.

   Informal proof:
   $121 \cdot 122 \cdot 123 \equiv 1 \cdot 2 \cdot 3 \equiv 6 \equiv 2 \pmod{4}$.
*)

Require Import PeanoNat.

Theorem mathd_numbertheory_517 :
  (121 * 122 * 123) mod 4 = 2.
Proof.
Admitted.