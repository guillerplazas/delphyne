(* miniF2F problem: mathd_algebra_568
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify $(a-1)(a+1)(a+2) - (a-2)(a+1).$ Show that it is a^3 + a^2.

   Informal proof:
   We successively expand by multiplying binomials: \begin{align*}
   (a&-1)(a+1)(a+2) - (a-2)(a+1)\\
   &= (a^2-1)(a+2)-(a-2)(a+1)\\
   &= (a^3 + 2a^2 - a - 2) - (a^2 -a -2)\\
   &= a^3 + a^2.
   \end{align*}So our answer is just $a^3 + a^2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_568 (a : R) :
  (a - 1) * (a + 1) * (a + 2) - (a - 2) * (a + 1) = a^3 + a^2.
Proof.
Admitted.