(* miniF2F problem: mathd_algebra_22
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Evaluate $\log_{5^2}5^4$. Show that it is 2.

   Informal proof:
   Let $x=\log_{5^2}5^4$. Writing the equation in exponential form gives $(5^2)^x=5^4$.
   So, $x=2$.
*)

Require Import Coq.Reals.Reals.

Open Scope R_scope.



Definition logb (a b : R) := ln b / ln a.

Theorem mathd_algebra_22 : logb (5^2) (5^4) = 2.

Proof.
Admitted.
