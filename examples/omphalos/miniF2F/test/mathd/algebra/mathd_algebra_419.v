(* miniF2F problem: mathd_algebra_419
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of $-a-b^2+3ab$ if $a=-1$ and $b=5$? Show that it is -39.

   Informal proof:
   Plugging in the given values yields $-a-b^2+3ab=-(-1)-5^2+3(-1)(5)=1-25-15=-39$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_419 :
  forall a b : R, 
  a = -1 -> 
  b = 5 -> 
  -a - b^2 + 3 * (a * b) = -39.
Proof.
Admitted.