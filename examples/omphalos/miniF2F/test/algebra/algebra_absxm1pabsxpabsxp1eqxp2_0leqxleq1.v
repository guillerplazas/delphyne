(* miniF2F problem: algebra_absxm1pabsxpabsxp1eqxp2_0leqxleq1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real number $x$, if $|x-1| + |x| + |x+1| = x + 2$, then $0 \leq x
   \leq 1$.

   Informal proof:
   If $x \leq -1$, then $|x-1| + |x| + |x+1| = -(x-1) - x - (x + 1) = -3x$. So, $-3x =
   x+2$ and $x=-\frac{1}{2}$, which is a contradiction.
   If $-1 < x < 0$, then $|x-1| + |x| + |x+1| = -(x-1) - x + (x + 1) = 2-x$. So, $2-x =
   x+2$ and $x=0$, which is a contradiction.
   If $x > 1$, then $|x-1| + |x| + |x+1| = x-1 + x + (x + 1) = 3x$. So, $3x = x+2$ and
   $x=1$, which is a contradiction.
   As a result, the only possible values for x are between 0 and 1 and 0 $\leq$ x $\leq$
   1.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_absxm1pabsxpabsxp1eqxp2_0leqxleq1 :
  forall x : R,
  Rabs (x - 1) + Rabs x + Rabs (x + 1) = x + 2 ->
  0 <= x /\ x <= 1.
Proof.
Admitted.