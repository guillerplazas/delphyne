(* miniF2F problem: mathd_numbertheory_22
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The two-digit number $``B6,''$ where $B$ is the tens digit, is the square of a
   positive integer. How many distinct possible values are there for $B$? Show that it
   is 2.

   Informal proof:
   Of the two-digit perfect squares, only $4^2=16$ and $6^2=36$ end in $6$. Thus, there
   are $2$ distinct possible values for $B$.
*)

Require Import Arith.
Require Import Nat.

Theorem mathd_numbertheory_22 :
  forall b : nat,
  b < 10 ->
  exists a : nat, (10 * b + 6) = a * a ->
  (b = 3 \/ b = 1).
Proof.
Admitted.