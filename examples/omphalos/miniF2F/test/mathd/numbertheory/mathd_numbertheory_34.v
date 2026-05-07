(* miniF2F problem: mathd_numbertheory_34
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $9^{-1} \pmod{100}$, as a residue modulo 100.  (Give an answer between 0 and 99,
   inclusive.) Show that it is 89.

   Informal proof:
   Note that $9 \cdot 11 \equiv 99 \equiv -1 \pmod{100}$.  Then $9 \cdot (-11) \equiv
   -99 \equiv 1 \pmod{100}$, so $9^{-1} \equiv -11 \equiv 89 \pmod{100}$.
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_34 : 
  forall x : nat, 
  (x < 100) -> 
  (x * 9 mod 100 = 1) -> 
  (x = 89).
Proof.
Admitted.