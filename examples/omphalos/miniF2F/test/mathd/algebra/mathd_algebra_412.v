(* miniF2F problem: mathd_algebra_412
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of two numbers is 25 and their difference is 11. What is the larger of the
   two numbers? Show that it is 18.

   Informal proof:
   Let $x,y$ be the two numbers, $x>y$. Then $x+y=25$ and $x-y=11$, thus:

   $x=\frac{1}{2}\left((x+y)+(x-y)\right)=\frac{1}{2}(25+11)=18$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_412:
  forall (x y : R),
  (x + y = 25) ->
  (x - y = 11) ->
  x = 18.
Proof.
Admitted.