(* miniF2F problem: mathd_algebra_329
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   In a rectangular coordinate system, the line $3y = x$ intersects the line $2x + 5y =
   11$ at point $A$. What is the sum of the coordinates of point $A$? Show that it is 4.

   Informal proof:
   If the coordinates of point $A$ are $(x,y)$ then $x$ and $y$ must satisfy the
   equations of both lines (as $A$ is on both lines). Substituting the first equation
   into the second gives: \begin{align*}
   2x+5y &=11\\
   6y+5y&= 11\\
   11y&= 11\\
   y &= 1.
   \end{align*}So now $x = 3y = 3$, and so the coordinates of point $A$ are $(3,1)$. The
   sum of these is $3+1 = 4$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_329 :
  forall x y : R,
  (3 * y = x) ->
  (2 * x + 5 * y = 11) ->
  (x + y = 4).
Proof.
Admitted.
