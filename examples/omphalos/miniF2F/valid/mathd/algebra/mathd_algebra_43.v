(* miniF2F problem: mathd_algebra_43
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the $x$-coordinate for the $x$-intercept of the line containing the points
   $(7,4)$ and $(6,3)$? Show that it is 3.

   Informal proof:
   First we find that the slope of the line is $\frac{4 - 3}{7 - 6} = 1$.  Now, for any
   other point, $P = (x, y)$, to be on this line, the slope between $P$ and either of
   $(7, 4)$ or $(6, 3)$ must be equal to 1.  Thus $\frac{y - 3}{x - 6} = 1 \Rightarrow y
   = x - 3$.  A line crosses the $x$-axis when it has $y = 0$.  Plugging this in for our
   line we get $0 = x - 3 \Rightarrow x = 3$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_43
  (a b : R)
  (f : R -> R)
  (h0 : forall x, f x = a * x + b)
  (h1 : f 7 = 4)
  (h2 : f 6 = 3) :
  f 3 = 0.
Proof.
Admitted.