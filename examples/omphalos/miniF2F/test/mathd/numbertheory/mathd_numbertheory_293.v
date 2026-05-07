(* miniF2F problem: mathd_numbertheory_293
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What digit must be placed in the blank to make the four-digit integer $20\_7$ a
   multiple of 11? Show that it is 5.

   Informal proof:
   A number will be divisible by 11 if you get a multiple of 11 by alternately adding
   and then subtracting its digits.  If we name the blank integer $A$, then the
   alternating sum is $2 - 0 + A - 7 = A -5$.  This value can only be equal to 0 (as 11,
   22, etc all yield $A$ that are too large), so $A = 5$ is the only digit that will
   work.
*)

Require Import Nat.
Require Import ZArith.
From Coq Require Import Znumtheory.

Open Scope Z_scope.

Theorem mathd_numbertheory_293 :
  forall n : Z,
  (0 <= n <= 9)%Z ->
  exists k : Z, (20 * 100 + 10 * n + 7 = 11 * k)%Z ->
  n = 5.

Proof.
Admitted.
