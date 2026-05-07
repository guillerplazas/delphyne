(* miniF2F problem: mathd_algebra_181
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $\displaystyle\frac{n+5}{n-3} = 2$ what is the value of $n$? Show that it is 11.

   Informal proof:
   Multiplying both sides by $n-3$, we have $n+5 = 2(n-3)$.  Expanding gives $n+5 = 2n -
   6$, and solving this equation gives $n=11$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_181 : 
  forall n : R,
  n <> 3 ->
  (n + 5) / (n - 3) = 2 ->
  n = 11.
Proof.
Admitted.