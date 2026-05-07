(* miniF2F problem: mathd_algebra_398
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   On planet Larky, 7 ligs = 4 lags, and 9 lags = 20 lugs. How many ligs are equivalent
   to 80 lugs? Show that it is 63.

   Informal proof:
   Multiply the second equation by 4 to find that 36 lags are equivalent to 80 lugs. 
   Then multiply the first equation by 9 to find that 36 lags are equivalent to 63 ligs.
   Since each is equivalent to 36 lags, 80 lugs and $63$ ligs are equivalent.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_398:
  forall (a b c : R),
    0 < a /\ 0 < b /\ 0 < c ->
    9 * b = 20 * c ->
    7 * a = 4 * b ->
    63 * a = 80 * c.
Proof.
Admitted.