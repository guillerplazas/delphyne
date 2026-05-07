(* miniF2F problem: mathd_algebra_37
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $x+y = 7$ and $3x+y = 45,$ evaluate $x^2-y^2.$ Show that it is 217.

   Informal proof:
   217
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_37 :
  forall x y : R,
  x + y = 7 ->
  3 * x + y = 45 ->
  x^2 - y^2 = 217.
Proof.
Admitted.