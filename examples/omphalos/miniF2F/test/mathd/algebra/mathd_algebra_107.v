(* miniF2F problem: mathd_algebra_107
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the radius of the circle with equation $x^2 + 8x + y^2 - 6y = 0$. Show that it
   is 5.

   Informal proof:
   Completing the square gives us $(x +4)^2 + (y -3)^2 -25 = 0$. Rearranging terms, we
   have $(x +4)^2 + (y -3)^2 = 25$. It follows that the square of the radius is 25, so
   the radius must be $5$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_107:
  forall (x y : R),
    (x^2 + 8 * x + y^2 - 6 * y = 0) ->
    (x + 4)^2 + (y - 3)^2 = 5^2.
Proof.
Admitted.