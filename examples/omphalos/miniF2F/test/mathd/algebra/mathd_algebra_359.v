(* miniF2F problem: mathd_algebra_359
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of $y$ in the arithmetic sequence $y + 6$, $12$, $y$? Show that it
   is 9.

   Informal proof:
   The difference between the second and first term is $12 - (y + 6) = 6 - y$, and the
   difference between the third and second term is $y - 12$.  These must be equal, so $6
   - y = y - 12$.  Solving for $y$, we find $y = 9$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_359 : forall y : R,
  y + 6 + y = 2 * 12 -> 
  y = 9.
Proof.
Admitted.