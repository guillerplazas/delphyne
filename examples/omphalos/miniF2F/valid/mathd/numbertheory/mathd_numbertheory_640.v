(* miniF2F problem: mathd_numbertheory_640
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the remainder when $91145 + 91146 + 91147 + 91148$ is divided by 4. Show that it
   is 2.

   Informal proof:
   For any four consecutive integers, their residues modulo 4 are 0, 1, 2, and 3 in some
   order, so their sum modulo 4 is $0 + 1 + 2 + 3 = 6 \equiv 2 \pmod{4}$.
*)

Require Import Nat.

Theorem mathd_numbertheory_640 :
  (91145 + 91146 + 91147 + 91148) mod 4 = 2.
Proof.
Admitted.