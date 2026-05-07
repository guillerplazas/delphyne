(* miniF2F problem: mathd_algebra_245
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify $\left( \frac{4}{x} \right)^{-1} \left( \frac{3x^3}{x} \right)^2 \left(
   \frac{1}{2x} \right)^{-3}$. Show that it is 18x^8.

   Informal proof:
   $\left( \frac{4}{x} \right)^{-1} \left( \frac{3x^3}{x} \right)^2 \left( \frac{1}{2x}
   \right)^{-3} = \frac{x}{4} \cdot (3x^2)^2 \cdot (2x)^3 = \frac{x}{4} \cdot 9x^4 \cdot
   8x^3 = 18x^8$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_245 :
  forall x : R,
  x <> 0 ->
  (/ (4 / x)) * (((3 * x^3) / x)^2) * ((/ (1 / (2 * x)))^3) = 18 * x^8.

Proof.
Admitted.
