(* miniF2F problem: mathd_numbertheory_559
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A positive integer $X$ is 2 more than a multiple of 3. Its units digit is the same as
   the units digit of a number that is 4 more than a multiple of 5. What is the smallest
   possible value of $X$? Show that it is 14.

   Informal proof:
   If a positive integer is 4 more than a multiple of 5, then its units digit must be 4
   or 9.  We check positive integers ending in 4 or 9 until we find one which is 2 more
   than a multiple of 3: 4 is 1 more than a multiple of 3, 9 is a multiple of 3, and
   $14$ is 2 more than a multiple of 3.
*)

Require Import PeanoNat.

Theorem mathd_numbertheory_559:
  forall x y : nat,
  (x mod 3 = 2) ->
  (y mod 5 = 4) ->
  (x mod 10 = y mod 10) ->
  (14 <= x).
Proof.
Admitted.