(* miniF2F problem: mathd_algebra_132
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f (x) = x + 2$ and $g (x) = x^2$, then for what value of $x$ does $f(g(x)) =
   g(f(x))$? Express your answer as a common fraction. Show that it is $-\frac{1}{2}$.

   Informal proof:
   We have that $f(g(x)) = f(x^2) = x^2 + 2$ and $g(f(x)) = g(x + 2) = (x + 2)^2 = x^2 +
   4x + 4,$ so we want to solve
   \[x^2 + 2 = x^2 + 4x + 4.\]This simplifies to $4x = -2,$ so $x = -\frac{1}{2}.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_132 :
  forall (x : R) (f g : R -> R),
  (forall x, f x = x + 2) ->
  (forall x, g x = x^2) ->
  (f (g x) = g (f x)) ->
  x = -1 / 2.
Proof.
Admitted.