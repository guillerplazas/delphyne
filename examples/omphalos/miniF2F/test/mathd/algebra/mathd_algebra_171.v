(* miniF2F problem: mathd_algebra_171
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Consider the function $f(x)=5x+4$.  What is $f(1)$? Show that it is 9.

   Informal proof:
   We have $f(1) = 5\cdot 1+4 =5+4=9$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_171 (f : R -> R) :
  (forall x, f x = 5 * x + 4) -> f 1 = 9.
Proof.
Admitted.
