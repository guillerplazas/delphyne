(* miniF2F problem: mathd_algebra_35
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $p (x) = 2-x^2$ and $q(x) = \frac{6}{x}$, what is the value of $p (q(2))$? Show
   that it is -7.

   Informal proof:
   Since $q(2) = \frac62 = 3$, we have $p(q(2)) = p(3) = 2-3^2 = -7$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_35
  (p q : R -> R)
  (h₀ : forall x, p x = 2 - x^2)
  (h₁ : forall x, x <> 0 -> q x = 6 / x) :
  p (q 2) = -7.
Proof.
Admitted.