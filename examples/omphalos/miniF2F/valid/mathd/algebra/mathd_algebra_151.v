(* miniF2F problem: mathd_algebra_151
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Evaluate $\left\lceil\sqrt{27}\right\rceil - \left\lfloor\sqrt{26}\right\rfloor$.
   Show that it is 1.

   Informal proof:
   Because $\sqrt{25}<\sqrt{26}<\sqrt{27}<\sqrt{36}$, we have
   $\left\lceil\sqrt{27}\right\rceil=6$ and $\left\lfloor\sqrt{26}\right\rfloor=5$.  The
   expression thus evaluates to $6-5=1$.
*)

Require Import Reals.
Require Import Rfunctions.
Require Import ZArith.

Open Scope R_scope.

Theorem mathd_algebra_151:
  Z.sub (up (sqrt 27)) (up (sqrt 26) - 1) = 1%Z.

Proof.
Admitted.
