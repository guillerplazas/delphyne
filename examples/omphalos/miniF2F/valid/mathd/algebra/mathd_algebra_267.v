(* miniF2F problem: mathd_algebra_267
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve for $x$: $\frac{x+1}{x-1} = \frac{x-2}{x+2}$ Show that it is 0.

   Informal proof:
   Cross-multiplying (which is the same as multiplying both sides by $x-1$ and by $x+2$)
   gives \[(x+1)(x+2) = (x-2)(x-1).\] Expanding the products on both sides gives  \[x^2
   + 3x + 2 = x^2 -3x +2.\] Subtracting $x^2$ and 2 from both sides gives  $3x=-3x$, so
   $6x=0$ and $x=0$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_267:
  forall (x : R),
  x <> 1 -> x <> -2 -> (x + 1) / (x - 1) = (x - 2) / (x + 2) -> x = 0.
Proof.
Admitted.