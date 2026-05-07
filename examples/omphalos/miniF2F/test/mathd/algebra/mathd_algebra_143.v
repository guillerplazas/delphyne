(* miniF2F problem: mathd_algebra_143
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x) = x + 1$ and $g(x) = x^2 + 3$, what is the value of $f(g(2))$? Show that it
   is 8.

   Informal proof:
   We are asked to apply the function $f$ to the number $g(2)$.  First, we need to find
   $g(2)$.  We substitute $x=2$ into the expression given for $g$ to find that
   $g(2)=2^2+3=7$.  Then we substitute $x=7$ into the expression for $f$ to find
   $f(7)=7+1=8$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_143 :
  forall (f g : R -> R),
  (forall x, f x = x + 1) ->
  (forall x, g x = x^2 + 3) ->
  f (g 2) = 8.
Proof.
Admitted.