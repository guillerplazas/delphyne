(* miniF2F problem: algebra_9onxpypzleqsum2onxpy
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any three positive real numbers $x$, $y$, and $z$, $9/(x+y+z)\leq
   2/(x+y)+2/(y+z)+2/(z+x)$.

   Informal proof:
   Because $x$, $y$, and $z$ are positive, so is $x+y+z$.
   Therefore it suffices to prove $9/(x+y+z) * (2x+2y+2z) \leq (2/(x+y)+2/(y+z)+2/(z+x))
   * (2x+2y+2z)$.
   We see that the left hand side can be simplified to $18$.
   The right hand side satisfies $(2/(x+y)+2/(y+z)+2/(z+x)) * (2x+2y+2z) =
   (2/(x+y)+2/(y+z)+2/(z+x)) * ((x+y) + (y+z) + (z+x)) \ge (\sqrt{2/x+y}\sqrt{x+y} +
   \sqrt{2/y+z}\sqrt{y+z} + \sqrt{2/x+z}\sqrt{x+z})^2 = (3\sqrt{2})^2 = 18$. Hence the
   inequality holds.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_9onxpypzleqsum2onxpy:
  forall x y z : R,
  (0 < x) -> (0 < y) -> (0 < z) ->
  (9 / (x + y + z) <= 2 / (x + y) + 2 / (y + z) + 2 / (z + x)).
Proof.
Admitted.