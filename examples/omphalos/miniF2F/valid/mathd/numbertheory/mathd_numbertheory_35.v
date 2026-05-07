(* miniF2F problem: mathd_numbertheory_35
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of the four positive factors of the positive integer value of
   $\sqrt{196}$? Show that it is 24.

   Informal proof:
   Calculate $\sqrt{196}=\sqrt{2^2\cdot7^2}=2\cdot7$. The sum of the four positive
   factors is $1+2+7+14=24$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Lists.List.
Import ListNotations.

Theorem mathd_numbertheory_35 : 
  (1 + 2 + 7 + 14) = 24. 
Proof.
Admitted.