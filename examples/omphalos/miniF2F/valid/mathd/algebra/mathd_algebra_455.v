(* miniF2F problem: mathd_algebra_455
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   At each basketball practice last week, Jenny made twice as many free throws as she
   made at the previous practice.  At her fifth practice she made 48 free throws.  How
   many free throws did she make at the first practice? Show that it is 3.

   Informal proof:
   At Jenny's fourth practice she made $\frac{1}{2}(48)=24$ free throws. At her third
   practice she made 12, at her second practice she made 6, and at her first practice
   she made $3$.
*)

Require Import Arith.

Theorem mathd_algebra_455 :
  forall x : nat,
  2 * (2 * (2 * (2 * x))) = 48 ->
  x = 3.
Proof.
Admitted.
