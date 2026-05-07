(* miniF2F problem: mathd_numbertheory_961
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when 2003 is divided by 11? Show that it is 1.

   Informal proof:
   Dividing, we find that $11\cdot 182=2002$.  Therefore, the remainder when 2003 is
   divided by 11 is $1$.
*)

Require Import PeanoNat.

Theorem mathd_numbertheory_961 : 
  2003 mod 11 = 1.
Proof.
Admitted.