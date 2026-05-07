(* miniF2F problem: mathd_algebra_270
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x) = \dfrac{1}{x + 2},$ what is $f(f(1))$? Show that it is \dfrac{3}{7}.

   Informal proof:
   We see that $f(1) = \dfrac{1}{1 + 2} = \dfrac{1}{3}.$ Therefore, $f(f(1)) =
   f\left(\dfrac{1}{3}\right) = \dfrac{1}{\frac{1}{3} + 2} = \dfrac{1}{\frac{7}{3}} =
   \dfrac{3}{7}.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_270
  (f : R -> R)
  (h₀ : forall x : R, x <> -2 -> f x = 1 / (x + 2)) :
  f (f 1) = 3 / 7.
Proof.
Admitted.
