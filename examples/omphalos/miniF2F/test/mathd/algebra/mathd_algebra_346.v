(* miniF2F problem: mathd_algebra_346
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = 2x-3$ and $g(x) = x+1$. What is the value of $g(f(5)-1)$? Show that it is
   7.

   Informal proof:
   We have $f(5) = 2(5) -3 = 7$, so $g(f(5)-1) = g(7-1) = g(6) = 6+1 = 7$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_346 :
  forall f g : R -> R,
  (forall x, f x = 2 * x - 3) ->
  (forall x, g x = x + 1) ->
  g (f 5 - 1) = 7.
Proof.
Admitted.