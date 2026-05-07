(* miniF2F problem: mathd_algebra_427
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given the equations $3x+y=17,5y+z=14$ and $3x+5z=41$, what is the value of the sum
   $x+y+z$? Show that it is 12.

   Informal proof:
   Sum all three equations to find that $6x+6y+6z=17+14+41$, from which $x+y+z=72/6=12$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem mathd_algebra_427 :
  forall (x y z : R),
  (3 * x + y = 17) ->
  (5 * y + z = 14) ->
  (3 * x + 5 * z = 41) ->
  (x + y + z = 12).
Proof.
Admitted.