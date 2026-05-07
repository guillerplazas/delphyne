(* miniF2F problem: mathd_algebra_110
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify $(2-2i)(5+5i)$, where $i^2 = -1.$ Show that it is 20.

   Informal proof:
   $(2-2i)(5+5i) = 2(5) + 2(5i) -2i(5) -2i(5i) = 10+10i-10i +10 = 20$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_110 :
  forall q e : C,
  q = 2 - 2 * Ci ->
  e = 5 + 5 * Ci ->
  q * e = 20.

Proof.
Admitted.
