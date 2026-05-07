(* miniF2F problem: mathd_algebra_159
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x)=3x^4-7x^3+2x^2-bx+1$. For what value of $b$ is $f(1)=1$? Show that it is
   -2.

   Informal proof:
   Evaluating, we get $f(1) = 3-7+2-b+1 = -b-1 = 1.$ Solving for $b,$ we find that $b =
   -2.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_159:
  forall (b : R) (f : R -> R),
    (forall x, f x = 3 * (x^4) - 7 * (x^3) + 2 * (x^2) - b * x + 1) ->
    f 1 = 1 ->
    b = -2.
Proof.
Admitted.