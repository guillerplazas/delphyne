(* miniF2F problem: mathd_algebra_182
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Expand the following expression: $7(3y+2)$ Show that it is 21y+14.

   Informal proof:
   We apply the distributive property to get\begin{align*}
   7(3y+2) &= 7\cdot 3y+7\cdot 2\\
   &= 21y+14.
   \end{align*}
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_182
  (y : C) :
  7 * (3 * y + 2) = 21 * y + 14.

Proof.
Admitted.
