(* miniF2F problem: mathd_algebra_598
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that  $4^{a}=5$, $5^{b}=6$, $6^{c}=7,$ and  $7^{d}=8$. What is $a\cdot b\cdot
   c\cdot d$? Show that it is \frac{3}{2}.

   Informal proof:
   Because \[
   4^{a\cdot b\cdot c\cdot d}
   = \left(\left(\left(4^a\right)^b\right)^c\right)^d
   = \left(\left( 5^b\right)^c\right)^d
   = \left(6^c\right)^d = 7^d = 8 = 4^{3/2},
   \]we have $a\cdot b\cdot c\cdot d = \frac{3}{2}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_598:
  forall (a b c d : R),
    Rpower 4 a = 5 ->
    Rpower 5 b = 6 ->
    Rpower 6 c = 7 ->
    Rpower 7 d = 8 ->
    a * b * c * d = 3 / 2.
Proof.
Admitted.
