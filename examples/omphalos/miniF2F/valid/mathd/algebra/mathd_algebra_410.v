(* miniF2F problem: mathd_algebra_410
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the minimum possible value for $y$ in the equation $y = x^2 - 6x + 13$? Show
   that it is 4.

   Informal proof:
   Write $x^2-6x$ as $(x-3)^2-9$ to obtain  \[
   y=(x-3)^2+4.
   \]Since $(x-3)^2\geq0$, we have $y\geq4$.  The value $y=4$ is obtained when $x=3$.
   (Note: this method of rewriting a quadratic expression is called ``completing the
   square'').
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_410 :
  forall x y : R,
    y = x^2 - 6 * x + 13 -> 4 <= y.
Proof.
Admitted.