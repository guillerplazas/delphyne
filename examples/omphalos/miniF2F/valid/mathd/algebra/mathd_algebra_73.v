(* miniF2F problem: mathd_algebra_73
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $p$, $q$, and $r$ be constants. One solution to the equation $(x-p)(x-q) =
   (r-p)(r-q)$ is $x=r$. Find the other solution in terms of $p$, $q$, and $r$. Show
   that it is p+q-r.

   Informal proof:
   If we expand the left side, we have  \begin{align*}
   (x-p)(x-q) &=x(x-q) -p(x-q)\\
   & = x^2 - qx - px +pq \\
   &= x^2 -(p+q)x + pq.
   \end{align*} The other side of the equation is a constant, since there isn't an $x$
   term. So, if we view the equation as a quadratic in $x$, the sum of the roots is
   $-[-(p+q)] = p+q$.  We know that one of the roots is $r$, so if the other is $s$, we
   have $r+s = p+q$, so $s = p+q-r$.
*)

Require Import Coquelicot.Coquelicot.
Open Scope C_scope.

Theorem mathd_algebra_73:
  forall (p q r x: C),
    (x - p) * (x - q) = (r - p) * (r - q) ->
    x <> r ->
    x = p + q - r.

Proof.
Admitted.
