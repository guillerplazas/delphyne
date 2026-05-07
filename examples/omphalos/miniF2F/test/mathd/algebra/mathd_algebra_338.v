(* miniF2F problem: mathd_algebra_338
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $3a + b + c = -3, a+3b+c = 9, a+b+3c = 19$, then find $abc$. Show that it is -56.

   Informal proof:
   Summing all three equations yields that $5a + 5b + 5c = -3 + 9 + 19 = 25$. Thus, $a +
   b + c = 5$. Subtracting this from each of the given equations, we obtain that $2a =
   -8, 2b = 4, 2c = 14$. Thus, $a = -4, b = 2, c =7$, and their product is $abc = -4
   \times 2 \times 7 = -56$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_338 :
  forall a b c : R,
    (3 * a + b + c = -3) ->
    (a + 3 * b + c = 9) ->
    (a + b + 3 * c = 19) ->
    a * b * c = -56.
Proof.
Admitted.