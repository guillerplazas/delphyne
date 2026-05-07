(* miniF2F problem: mathd_algebra_140
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The expression $24x^2-19x-35$ can be written as $(Ax-5)(2Bx+C)$, where $A$, $B$, and
   $C$ are positive numbers. Find $AB-3C$. Show that it is -9.

   Informal proof:
   The expression $24x^2-19x-35$ can be factored as $(3x-5)(8x+7)$. Therefore,
   $(Ax-5)=(3x-5)$ and $(2Bx+C)=(8x+7)$. From that, $A=3$, $B=4$, and $C=7$.
   \begin{align*}
   AB-3C&=3\cdot4-3\cdot7\\
   &=12-21\\
   &=-9
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_140 :
  forall a b c : R,
  (0 < a) -> (0 < b) -> (0 < c) ->
  (forall x : R, 24 * x^2 - 19 * x - 35 = (a * x - 5) * (2 * (b * x) + c)) ->
  a * b - 3 * c = -9.
Proof.
Admitted.