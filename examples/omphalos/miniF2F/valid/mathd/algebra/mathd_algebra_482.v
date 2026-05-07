(* miniF2F problem: mathd_algebra_482
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If two (positive) prime numbers are roots of the equation $x^2-12x+k=0$, what is the
   value of $k$? Show that it is 35.

   Informal proof:
   35
*)

Require Import Reals.
Require Import Arith.
Require Import Znumtheory.
Require Import Lia.

Open Scope R_scope.

Theorem mathd_algebra_482 :
  forall (m n : nat) (k : R) (f : R -> R),
    Znumtheory.prime (Z.of_nat m) ->
    Znumtheory.prime (Z.of_nat n) ->
    m <> n ->
    (forall x : R, f x = x^2 - 12 * x + k) ->
    f (INR m) = 0 ->
    f (INR n) = 0 ->
    k = 35.

Proof.
Admitted.
