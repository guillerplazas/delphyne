(* miniF2F problem: algebra_sqineq_at2malt1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real number $a$, $a(2-a)\leq 1$.

   Informal proof:
   We have that for any real number $a$, $(a - 1)^2 \geq 0$. So, $a^2 - 2a + 1 \geq 0$.
   As a result, $a(2-a) = 2a - a^2 \leq 1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_at2malt1 (a : R) : a * (2 - a) <= 1.
Proof.
Admitted.