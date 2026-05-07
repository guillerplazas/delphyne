(* miniF2F problem: mathd_algebra_332
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Real numbers $x$ and $y$ have an arithmetic mean of 7 and a geometric mean of
   $\sqrt{19}$. Find $x^2+y^2$. Show that it is 158.

   Informal proof:
   The givens tell us that $\frac{x+y}{2}=7$ and $\sqrt{xy}=\sqrt{19}$, or $x+y=14$ and
   $xy=19$. $(x+y)^2=x^2+2xy+y^2$, so  \[
   x^2+y^2=(x+y)^2-2xy=14^2-2\cdot19=196-38=158
   \]
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_332 :
  forall (x y : R),
    (x + y) / 2 = 7 ->
    sqrt (x * y) = sqrt 19 ->
    x^2 + y^2 = 158.
Proof.
Admitted.