(* miniF2F problem: mathd_algebra_432
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Expand $(x+3)(2x-6)$. Show that it is 2x^2-18.

   Informal proof:
   Factoring a $2$ out of the second term gives $2(x+3)(x-3)=2(x^2-3^2)=2x^2-18$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem mathd_algebra_432 (x : R) : (x + 3) * (2 * x - 6) = 2 * x^2 - 18.
Proof.
Admitted.