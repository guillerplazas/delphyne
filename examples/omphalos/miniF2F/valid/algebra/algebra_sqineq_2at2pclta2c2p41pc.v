(* miniF2F problem: algebra_sqineq_2at2pclta2c2p41pc
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For real numbers a and c, show that $2a(2+c)\leq a^2+c^2+4(1+c)$.

   Informal proof:
   $2a(2+c)\leq a^2+c^2+4(1+c) \iff 0\leq (a-c)^2 -4(a-c)+4$
   This right hand-side is a second degree polynomial in a-c with discriminant. It
   follows that it equals 0 in a-c=2 and is positive everywhere else
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_sqineq_2at2pclta2c2p41pc:
  forall a c : R, 2 * a * (2 + c) <= a^2 + c^2 + 4 * (1 + c).
Proof.
Admitted.