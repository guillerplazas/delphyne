(* miniF2F problem: mathd_algebra_547
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the positive value of the expression $\sqrt{x^3 - 2^y}$ when $x = 5$ and $y =
   2$? Show that it is 11.

   Informal proof:
   Plugging in, the desired expression is just $\sqrt{5^3 - 2^2} = \sqrt{125 - 4} =
   \sqrt{121} = 11$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_547 :
  forall (x y : R),
  x = 5 ->
  y = 2 ->
  sqrt (x^3 - Rpower 2 y) = 11.


Proof.
Admitted.
