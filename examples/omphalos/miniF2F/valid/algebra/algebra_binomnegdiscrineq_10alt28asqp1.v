(* miniF2F problem: algebra_binomnegdiscrineq_10alt28asqp1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For any real number a, show that $10a \leq 28a^2 + 1$.

   Informal proof:
   It suffices to show $0\leq 28a^2 - 10a + 1$.
   First, consider completing the square for $28a^2 - 10a$ and observe that $(a -
   \frac{5}{28})^2 = a^2 - \frac{10}{28}a + (5/28)^2$.
   Since $0\leq (a - \frac{5}{28})^2$, we have $0\leq a^2 - \frac{10}{28}a + (5/28)^2$.
   Multiplying by 28 and simplifying terms gives $0\leq 28*a^2 - 10*a + (25/28)$.
   Since $25/28 < 1$, the result follows.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_binomnegdiscrineq_10alt28asqp1:
  forall a : R, 10 * a <= 28 * a^2 + 1.
Proof.
Admitted.