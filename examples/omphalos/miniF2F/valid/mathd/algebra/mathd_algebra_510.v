(* miniF2F problem: mathd_algebra_510
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $x + y = 13$ and $xy = 24$, find the distance from the point $(x, y)$ to
   the origin. Show that it is 11.

   Informal proof:
   The distance from $(x, y)$ to the origin is $\sqrt{x^2 + y^2}$. We note that $x^2 +
   y^2 = x^2 + 2xy + y^2 - 2xy = (x + y)^2 - 2xy$, so $\sqrt{x^2 + y^2} = \sqrt{13^2-48}
   = \sqrt{121} = 11$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_510:
  forall (x y : R),
  (x + y = 13) ->
  (x * y = 24) ->
  sqrt (x^2 + y^2) = 11.
Proof.
Admitted.