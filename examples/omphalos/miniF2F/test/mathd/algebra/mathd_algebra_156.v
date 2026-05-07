(* miniF2F problem: mathd_algebra_156
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The graphs of $y=x^4$ and $y=5x^2-6$ intersect at four points with $x$-coordinates
   $\pm \sqrt{m}$ and $\pm \sqrt{n}$, where $m > n$. What is $m-n$? Show that it is 1.

   Informal proof:
   At the intersection points, the $y$-coordinates of the two graphs must be equal, so
   we have the equation $x^4=y=5x^2-6$, or $x^4=5x^2-6$. Putting all the terms on one
   side, we get $x^4-5x^2+6=0$. Factoring, we get $(x^2-3)(x^2-2)=0$, so $x^2-3=0
   \Rightarrow x=\pm \sqrt{3}$ or $x^2-2=0 \Rightarrow x=\pm \sqrt{2}$. Thus, $m=3$ and
   $n=2$ and $m-n=1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_156 (x y : R) (f g : R -> R) :
  (forall t, f t = t^4) ->
  (forall t, g t = 5 * t^2 - 6) ->
  f x = g x ->
  f y = g y ->
  x^2 < y^2 ->
  y^2 - x^2 = 1.
Proof.
Admitted.
