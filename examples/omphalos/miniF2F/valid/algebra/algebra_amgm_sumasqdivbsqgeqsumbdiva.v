(* miniF2F problem: algebra_amgm_sumasqdivbsqgeqsumbdiva
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For any three positive real numbers a, b, and c, show that $a^2/b^2 + b^2/c^2 +
   c^2/a^2 \geq b/a + c/b + a/c$.

   Informal proof:
   Let $\alpha=a/b$ , $\beta=b/c$ and $\gamma=c/a$. Then we have
   $\frac{1}{2}(\alpha^2+\beta^2)\geq\alpha\beta$ by AM-GM. 
   Adding these inequalities cyclicly over the three variables, we obtain $\alpha^2 +
   \beta^2 + \gamma^2 \geq \alpha\beta + \beta\gamma+\alpha\gamma$. Replacing $\alpha$,
   $\beta$ and $\gamma$ by $a/b$, $b/c$ and $c/a$ gives the result.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_amgm_sumasqdivbsqgeqsumbdiva
  (a b c : R)
  (h₀ : 0 < a /\ 0 < b /\ 0 < c) :
  a^2 / b^2 + b^2 / c^2 + c^2 / a^2 >= b / a + c / b + a / c.
Proof.
Admitted.