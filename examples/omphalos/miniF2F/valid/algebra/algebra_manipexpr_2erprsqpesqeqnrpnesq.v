(* miniF2F problem: algebra_manipexpr_2erprsqpesqeqnrpnesq
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any two complex numbers e and r, $2er + e^2 + r^2 = (-r + (-e))^2$.

   Informal proof:
   Developing the square, we get $(-r + (-e))^2 = (-r)^2 + 2 (-r)(-e) + (-e)^2 = 2er +
   e^2 + r^2$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_manipexpr_2erprsqpesqeqnrpnesq
    (e r : C) :
    2 * (e * r) + (e^2 + r^2) = (-r + (-e))^2.

Proof.
Admitted.
