(* miniF2F problem: mathd_algebra_251
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Three plus the reciprocal of a number equals 7 divided by that number.  What is the
   number? Show that it is 2.

   Informal proof:
   Let $x$ be the number.  Converting the words in the problem into an equation gives us
   $3+\dfrac{1}{x} = \dfrac{7}{x}$.  Subtracting $\dfrac{1}{x}$ from both sides gives $3
   = \dfrac{6}{x}$. Multiplying both sides of this equation by $x$ gives $3x =6$, and
   dividing both sides of this equation by 3 gives $x = 2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_251:
  forall x : R,
  x <> 0 ->
  3 + 1/x = 7/x ->
  x = 2.
Proof.
Admitted.