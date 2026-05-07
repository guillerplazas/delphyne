(* miniF2F problem: mathd_algebra_288
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A point $(x,y)$ on the coordinate plane with both coordinates negative is a distance
   of 6 units from the $x$-axis. It is a distance of 15 units from the point $(8,3)$. It
   is a distance $\sqrt{n}$ from the origin. What is $n$? Show that it is 52.

   Informal proof:
   We know that $y=-6$ from the given information. By the distance formula, we have the
   equation $\sqrt{(x-8)^2+(-6-3)^2}=15$. Solving, we have \begin{align*}
   \sqrt{(x-8)^2+(-6-3)^2}&=15 \\
   x^2-16x+64+81&=225 \\
   x^2-16x-80&=0 \\
   (x-20)(x+4)&=0
   \end{align*}Thus, $x+4=0$ or $x-20=0$, so $x=-4$ or $x=20$. $x=-4$ by the given
   conditions. Thus, our point is $(-4,-6)$ and is a distance of
   $\sqrt{(-4)^2+(-6)^2}=\sqrt{52}$ units from the origin. $n=52$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_288:
  forall (x y n : R),
  x < 0 /\ y < 0 ->
  Rabs y = 6 ->
  sqrt ((x - 8)^2 + (y - 3)^2) = 15 ->
  sqrt (x^2 + y^2) = sqrt n ->
  n = 52.
Proof.
Admitted.