(* miniF2F problem: mathd_algebra_493
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = x^2 - 4\sqrt{x} + 1$. What is $f(f(4))$? Show that it is 70.

   Informal proof:
   First, we evaluate $f(4)$: $$f(4) = 4^2 - 4\sqrt{4} + 1 = 9.$$ Thus, $$f(f(4)) = f(9)
   = 9^2 - 4 \sqrt{9} + 1 = 70.$$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_493 (f : R -> R) (h0 : forall x, f x = x^2 - 4 * sqrt x + 1) : 
  f (f 4) = 70.
Proof.
Admitted.