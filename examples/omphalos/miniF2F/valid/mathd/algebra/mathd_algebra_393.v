(* miniF2F problem: mathd_algebra_393
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x)=4x^3+1$, find $f^{-1}(33)$. Show that it is 2.

   Informal proof:
   If we substitute $f^{-1}(x)$ into our expression for $f$ we get 
   \[f(f^{-1}(x))=4(f^{-1}(x))^3+1.\]This reduces to  \[x=4(f^{-1}(x))^3+1.\]If we solve
   for $f^{-1}(x)$, we find that $f^{-1}(x)=\sqrt[3]{\frac{x-1}{4}}$. Therefore,
   $f^{-1}(33)=\sqrt[3]{\frac{33-1}{4}}=\sqrt[3]8=2$.
*)

Require Import Reals.
Require Import FunctionalExtensionality.

Definition bijective {X Y : Type} (f : X -> Y) :=
  (exists g : Y -> X, (forall x, g (f x) = x) /\ (forall y, f (g y) = y)).

Definition inverse {X Y : Type} (f : X -> Y) (g : Y -> X) :=
  (forall x, g (f x) = x) /\ (forall y, f (g y) = y).

Theorem mathd_algebra_393 :
  forall (f : R -> R),
  (forall x, f x = 4 * x * x * x + 1)%R ->
  bijective f ->
  exists g, inverse f g /\ (g 33 = 2)%R.

Proof.
Admitted.
