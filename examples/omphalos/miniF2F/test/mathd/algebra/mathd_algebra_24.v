(* miniF2F problem: mathd_algebra_24
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If a snack-size tin of peaches has $40$ calories and is $2\%$ of a person's daily
   caloric requirement, how many calories fulfill a person's daily caloric requirement?
   Show that it is 2000.

   Informal proof:
   If 40 calories is equal to $2\%=\frac{2}{100}=\frac{1}{50}$ of a person's daily
   requirement, then a person's daily caloric requirement is: $$40\cdot 50=2000$$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_24 :
  forall x : R,
  (x / 50 = 40) ->
  x = 2000.
Proof.
Admitted.