(* miniF2F problem: mathd_algebra_48
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify $(9-4i)-(-3-4i)$. Show that it is 12.

   Informal proof:
   $(9-4i)- (-3-4i) = 9-4i +3 +4i = (9+3) + (-4i+4i) = 12$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_48 :
  (9 - 4 * Ci) - ( -3 - 4 * Ci) = 12.
Proof.
Admitted.
