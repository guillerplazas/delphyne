(* miniF2F problem: mathd_algebra_109
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The point $(a, b)$ lies on the line with the equation $3x + 2y = 12.$ When $a = 4$,
   what is the value of $b$? Show that it is 0.

   Informal proof:
   We plug in $x = 4$: \begin{align*}
   3(4) + 2y &= 12\\
   12 + 2y &= 12\\
   y &= 0.
   \end{align*}

   Therefore, $b = 0$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_109 (a b : R) :
  3 * a + 2 * b = 12 ->
  a = 4 ->
  b = 0.
Proof.
Admitted.
