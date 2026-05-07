(* miniF2F problem: mathd_algebra_327
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve for $a$: $\frac15|9+2a|<1$.  Express your answer in interval notation. Show
   that it is (-7, -2).

   Informal proof:
   Multiplying by 5 gives $|9+2a|<5$, so we must have  $$-5 < 9+2a < 5.$$Subtracting 9
   from all three parts of this inequality chain gives  $$-14 < 2a < -4,$$and dividing
   by 2 gives $-7 < a < -2,$ or $a \in (-7, -2)$ in interval notation.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_327 : forall a : R,
  (1 / 5 * Rabs (9 + 2 * a) < 1) ->
  -7 < a /\ a < -2.

Proof.
Admitted.
