(* miniF2F problem: mathd_algebra_296
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A $3491$ by $3491$ square has its length decreased by $60$ and its width increased by
   $60$.  By how much does its area change? Show that it is 3600.

   Informal proof:
   The new length is $3491-60$, and the new width is $3491+60$.  Thus, the new area is

   $$(3491-60)(3491+60)=3491^2-60^2$$$3491^2$ is the area of the original square.  So
   the change in area is $60^2=3600$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_algebra_296 :
  Z.abs (((3491 - 60) * (3491 + 60) - 3491^2)) = 3600.
Proof.
Admitted.