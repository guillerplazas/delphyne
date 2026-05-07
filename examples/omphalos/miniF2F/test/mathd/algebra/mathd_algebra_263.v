(* miniF2F problem: mathd_algebra_263
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $y$: $\sqrt{19+3y} = 7$. Show that it is 10.

   Informal proof:
   Squaring both sides of this equation, we have that $19+3y=49$. Now, we subtract $19$
   from both sides of the equation and then divide by $3$ to get that $3y = 30
   \Rightarrow y = 10$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_263 :
  forall y : R,
  (0 <= 19 + 3 * y) ->
  (sqrt (19 + 3 * y) = 7) ->
  y = 10.
Proof.
Admitted.