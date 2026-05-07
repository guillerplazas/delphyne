(* miniF2F problem: algebra_sqineq_2unitcircatblt1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real numbers $a$ and $b$ such that $a^2 + b^2 = 2$, $ab \leq 1$.

   Informal proof:
   We have that $0 \leq (a-b)^2 = a^2 - 2ab + b^2$. Since $a^2 + b^2 = 2$, the
   expression becomes $0 \leq 2 - 2ab$. As a result, $ab \leq 1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_2unitcircatblt1 : 
  forall a b : R, 
  a^2 + b^2 = 2 -> 
  a * b <= 1.
Proof.
Admitted.