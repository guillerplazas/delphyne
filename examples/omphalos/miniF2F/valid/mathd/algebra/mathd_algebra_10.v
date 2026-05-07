(* miniF2F problem: mathd_algebra_10
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the positive difference between $120\%$ of 30 and $130\%$ of 20? Show that it
   is 10.

   Informal proof:
   One hundred twenty percent of 30 is $120\cdot30\cdot\frac{1}{100}=36$, and $130\%$ of
   20 is $ 130\cdot 20\cdot\frac{1}{100}=26$.  The difference between 36 and 26 is $10$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_10:
  Rabs ((120 / 100) * 30 - (130 / 100) * 20) = 10.
Proof.
Admitted.