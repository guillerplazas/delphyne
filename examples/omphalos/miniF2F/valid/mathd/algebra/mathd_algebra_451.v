(* miniF2F problem: mathd_algebra_451
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $g(x)=f^{-1}(x)$. If $g(-15)=0$, $g(0)=3$, $g(3)=9$ and $g(9)=20$, what
   is $f(f(9))$? Show that it is 0.

   Informal proof:
   Since $f$ and $g$ are inverses and $g(3) = 9$, we have $f(9) = 3$, so $f(f(9)) =
   f(3)$. Similarly, $g(0) = 3$, so $f(3) = 0$.
*)

Require Import Reals.

Definition bijective {A B} (f : A -> B) :=
  (forall y, exists x, f x = y) /\
  (forall x1 x2, f x1 = f x2 -> x1 = x2).

Theorem mathd_algebra_451 :
  forall (σ : R -> R) (σ_inv : R -> R),
    bijective σ ->
    σ_inv (- 15)%R = 0%R ->
    σ_inv 0%R = 3%R ->
    σ_inv 3%R = 9%R ->
    σ_inv 9%R = 20%R ->
    (forall x, σ (σ_inv x) = x) ->
    (forall x, σ_inv (σ x) = x) ->
    σ (σ 9%R) = 0%R.

Proof.
Admitted.
