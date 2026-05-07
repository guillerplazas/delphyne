(* miniF2F problem: mathd_numbertheory_101
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the modulo 4 residue of $17 \cdot 18$. Show that it is 2.

   Informal proof:
   $17 \cdot 18 \equiv 1 \cdot 2 \equiv 2 \pmod{4}$.
*)

Require Import Arith.

Theorem mathd_numbertheory_101 :
  (17 * 18) mod 4 = 2.
Proof.
Admitted.