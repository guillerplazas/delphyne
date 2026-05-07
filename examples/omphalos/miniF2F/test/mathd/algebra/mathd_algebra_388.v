(* miniF2F problem: mathd_algebra_388
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If

   \begin{align*}
   3x+4y-12z&=10,\\
   -2x-3y+9z&=-4,
   \end{align*}

   compute $x$. Show that it is 14.

   Informal proof:
   Let $w=y-3z$.  The equations become

   \begin{align*}
   3x+4w&=10,\\
   -2x-3w&=-4.
   \end{align*}

   Adding four times the second equation to three times the first equation,

   $$9x+12w-8x-12w=30-16\Rightarrow x=14.$$
*)

Require Import Reals.
Require Import Lra.

Open Scope R_scope.

Theorem mathd_algebra_388 :
  forall (x y z : R),
  3 * x + 4 * y - 12 * z = 10 ->
  -2 * x - 3 * y + 9 * z = -4 ->
  x = 14.
Proof.
Admitted.
