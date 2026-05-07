(* miniF2F problem: mathd_algebra_433
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = 3\sqrt{2x - 7} - 8$.  Find $f(8)$. Show that it is 1.

   Informal proof:
   $f(8) = 3\sqrt{2\cdot 8 - 7} - 8 = 3\sqrt{9} - 8 =1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_433
  (f : R -> R)
  (h0 : forall x, f x = 3 * sqrt (2 * x - 7) - 8) :
  f 8 = 1.
Proof.
Admitted.