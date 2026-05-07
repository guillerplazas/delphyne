(* miniF2F problem: mathd_algebra_31
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $ \sqrt{x+\!\sqrt{x+\!\sqrt{x+\!\sqrt{x+\cdots}}}}=9$, find $x$. Show that it is
   72.

   Informal proof:
   We know that $ \sqrt{x+\!\sqrt{x+\!\sqrt{x+\!\sqrt{x+\cdots}}}}=9$, so
   $\sqrt{x+9}=9$. Squaring both sides we get $x+9=81$, so $x=81-9=72$.
*)

Require Import Reals.
Require Import Lra.
Require Import Coquelicot.Coquelicot.

Theorem mathd_algebra_31 :
  forall (x : R) (u : nat -> R),
  (forall n : nat, u (S n) = sqrt (x + u n)) ->
  filterlim u eventually (locally 9) ->
  9 = sqrt (x + 9).

Proof.
Admitted.
