(* miniF2F problem: mathd_algebra_247
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $t=2s-s^2$ and $s=n^2 - 2^n+1$. What is the value of $t$ when $n=3$? Show that it
   is 0.

   Informal proof:
   First substitute $n=3$ into the expression for $s$ to find $s=3^2 - 2^3 + 1 =
   9-8+1=2$.  Then substitute $s=2$ into the expression for $t$ to find $t=2(2) - 2^2
   =0$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_247 :
  forall (t s : R) (n : nat),
  t = 2 * s - s ^ 2 ->
  s = INR(n*n) - 2^(n) + 1 ->
  n = 3%nat ->
  t = 0.

Proof.
Admitted.
