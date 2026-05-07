(* miniF2F problem: mathd_algebra_80
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve  \[\frac{x-9}{x+1}=2\]for $x$. Show that it is -11.

   Informal proof:
   Cross-multiplication gives  \[x-9=2x+2.\]Simplifying this expression tells us 
   \[x=-11.\]
*)

From Coq Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_80:
  forall (x : R), x <> -1 -> (x - 9) / (x + 1) = 2 -> x = -11.
Proof.
Admitted.