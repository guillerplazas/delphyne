Require Import Reals Psatz. Open Scope R_scope.
Theorem probe: forall (f:R->R) (x:R), (forall y, f y=y*y) -> f x <= 0 -> x*x <= 0.
Proof.
intros f x Hf Hx. specialize (Hf x). nra.
Qed.
