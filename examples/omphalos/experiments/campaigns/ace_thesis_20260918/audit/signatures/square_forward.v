Require Import Arith Lia.
Theorem probe: forall k b:nat, k <= b -> k*k <= b*b.
Proof.
intros k b H. rewrite Nat.square_le_mono. lia.
Qed.
