(* miniF2F problem: amc12b_2003_p9
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f$ be a linear function for which $f(6) - f(2) = 12.$ What is $f(12) - f(2)?$

   $
   \text {(A) } 12 \qquad \text {(B) } 18 \qquad \text {(C) } 24 \qquad \text {(D) } 30
   \qquad \text {(E) } 36
   $ Show that it is \text {(D) } 30.

   Informal proof:
   Since $f$ is a linear function with slope $m$,

   $m = \frac{f(6) - f(2)}{\Delta x} = \frac{12}{6 - 2} = 3$

   $f(12) - f(2) = m \Delta x = 3(12 - 2) = 30 \Rightarrow \text (D)$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2003_p9 :
  forall (a b : R) (f : R -> R),
  (forall x : R, f x = a * x + b) ->
  f 6 - f 2 = 12 ->
  f 12 - f 2 = 30.
Proof.
Admitted.