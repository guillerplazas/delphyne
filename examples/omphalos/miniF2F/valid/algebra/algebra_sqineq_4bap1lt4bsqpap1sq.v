(* miniF2F problem: algebra_sqineq_4bap1lt4bsqpap1sq
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For any two real numbers a and b, show that $4b(a+1)\leq 4b^2+(a+1)^2$.

   Informal proof:
   The result comes from $x^2+y^2 \geq 2xy$ for all reals $x,y$, applied to $x=2b$ and
   $y=a+1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_4bap1lt4bsqpap1sq :
  forall a b : R,
  4 * b * (a + 1) <= 4 * (b * b) + (a + 1) * (a + 1).
Proof.
Admitted.