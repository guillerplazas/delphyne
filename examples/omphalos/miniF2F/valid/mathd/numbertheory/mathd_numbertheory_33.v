(* miniF2F problem: mathd_numbertheory_33
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find an integer $n$ such that $0\leq n<398$ and $n$ is a multiplicative inverse to 7
   modulo 398. Show that it is 57.

   Informal proof:
   We notice that 399 is a multiple of 7: \[399=57\cdot7.\]Considering this equation
   modulo 398 gives \[1\equiv57\cdot7\pmod{398}\]so the answer is $57$.
*)

Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_33:
  forall (n : nat),
  (n < 398) ->
  (n * 7 mod 398 = 1) ->
  n = 57.
Proof.
Admitted.