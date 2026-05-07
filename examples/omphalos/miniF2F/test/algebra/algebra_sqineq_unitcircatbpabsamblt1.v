(* miniF2F problem: algebra_sqineq_unitcircatbpabsamblt1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be real numbers such that $a^2+b^2=1$. Show that $ab+\lvert a-b\rvert
   \leq 1$.

   Informal proof:
   We have that $0 \leq (a-b+1)^2 = a^2+b^2+1-2ab+2a-2b$. Since $a^2+b^2=1$, the
   inequality becomes $0 \leq 2-2ab+2a-2b$, so $0 \leq 1-ab+a-b$.
   Similarly, by expanding $0 \leq (b-a+1)^2$ we have that $0 \leq 1-ba+b-a$.
   Combining these two inequalities, we have that $ab+\lvert a-b\rvert \leq 1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_unitcircatbpabsamblt1:
  forall (a b : R), (a^2 + b^2 = 1) -> (a * b + Rabs (a - b) <= 1).
Proof.
Admitted.