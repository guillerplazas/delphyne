(* miniF2F problem: algebra_sqineq_36azm9asqle36zsq
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For real numbers a and z, show that $36az - 9a^2 \leq 36z^2$.

   Informal proof:
   We can rewrite the inequality as $2.(3a).(6z) - (3.a)^2 \leq (6.z)^2$, then
   $2.(3a).(6z) \leq (3.a)^2 + (6.z)^2$ . Then use that for all real numbers $x,y$,
   $x^2+y^2 \geq 2xy$, with $x=3a$ and $y=6z$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_36azm9asqle36zsq (z a : R) :
  36 * (a * z) - 9 * a^2 <= 36 * z^2.
Proof.
Admitted.