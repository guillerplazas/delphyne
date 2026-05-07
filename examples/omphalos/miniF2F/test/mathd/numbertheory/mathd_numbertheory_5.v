(* miniF2F problem: mathd_numbertheory_5
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the smallest integer greater than 10 that is both a perfect square and a
   perfect cube? Show that it is 64.

   Informal proof:
   A number is both a perfect square and a perfect cube if and only if it is a sixth
   power. The smallest sixth power greater than 10 is $2^6= 64$.
*)

Require Import PeanoNat.

Theorem mathd_numbertheory_5:
  forall n : nat,
  10 <= n ->
  (exists x, x^2 = n) ->
  (exists t, t^3 = n) ->
  64 <= n.
Proof.
Admitted.