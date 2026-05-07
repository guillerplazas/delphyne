(* miniF2F problem: mathd_algebra_113
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What value of $x$ will give the minimum value for $x^2- 14x + 3$? Show that it is 7.

   Informal proof:
   We start by completing the square: \begin{align*}
   x^2-14x+3&= x^2-14x +\left(\frac{14}{2}\right)^2 - \left(\frac{14}{2}\right)^2 + 3\\
   & = x^2 -14x + 7^2 - 49 + 3\\
   &=(x-7)^2 - 46.\end{align*}Since the square of a real number is at least 0, we have
   $$(x-7)^2\ge 0,$$where $(x-7)^2 =0$ only if $x=7$.   Therefore, $(x-7)^2 - 46$ is
   minimized when $x=7.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_113 (x : R) :
  x^2 - 14 * x + 3 >= 7^2 - 14 * 7 + 3.
Proof.
Admitted.