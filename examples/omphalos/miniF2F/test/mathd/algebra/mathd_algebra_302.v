(* miniF2F problem: mathd_algebra_302
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Evaluate $\left(\frac{i}{2}\right)^2$. Show that it is -\frac{1}{4}.

   Informal proof:
   $(i/2)^2 = (i^2)/(2^2) = (-1)/4 = -\frac{1}{4}$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_302 :
  (Ci / 2)^2 = - (1 / 4).

Proof.
Admitted.
