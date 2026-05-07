(* miniF2F problem: mathd_algebra_478
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The volume of a cone is given by the formula $V = \frac{1}{3}Bh$, where $B$ is the
   area of the base and $h$ is the height. The area of the base of a cone is 30 square
   units, and its height is 6.5 units. What is the number of cubic units in its volume?
   Show that it is 65.

   Informal proof:
   We are given that $B = 30$ and $h = 6.5$ and asked to find $\frac{1}{3}Bh$.  We find
   that \[\frac{1}{3}Bh = \frac{1}{3}(30)(6.5) = (10)(6.5) = 65.\]
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_478:
  forall (b h v : R),
  (0 < b /\ 0 < h /\ 0 < v) ->
  v = (1/3) * (b * h) ->
  b = 30 ->
  h = 13/2 ->
  v = 65.
Proof.
Admitted.