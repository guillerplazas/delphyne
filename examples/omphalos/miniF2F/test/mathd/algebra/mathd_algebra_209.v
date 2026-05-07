(* miniF2F problem: mathd_algebra_209
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $h(x)=f^{-1}(x)$. If $h(2)=10$, $h(10)=1$ and $h(1)=2$, what is
   $f(f(10))$? Show that it is 1.

   Informal proof:
   Since $f$ and $h$ are inverse functions and $h(2) = 10$, $f(10) = 2$, so $f(f(10)) =
   f(2)$.  And since $h(1) = 2$, $f(2) = 1$.
*)

Require Import Reals.
Require Import FunctionalExtensionality.

Theorem mathd_algebra_209 :
  forall (f f_inv : R -> R),
  (forall x, f (f_inv x) = x) ->
  (forall x, f_inv (f x) = x) ->
  f_inv (IZR 2) = IZR 10 ->
  f_inv (IZR 10) = IZR 1 ->
  f_inv (IZR 1) = IZR 2 ->
  f (f (IZR 10)) = IZR 1.


Proof.
Admitted.
