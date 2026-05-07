(* miniF2F problem: mathd_algebra_190
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Write $\cfrac{\cfrac{3}{8}+\cfrac{7}{8}}{\cfrac{4}{5}}$ as a simplified fraction.
   Show that it is \cfrac{25}{16}.

   Informal proof:
   $\cfrac{3}{8}+\cfrac{7}{8}=\cfrac{10}{8}=\cfrac{5}{4}$. Therefore,
   $\cfrac{5}{4}\div\cfrac{4}{5}=\cfrac{5}{4}\cdot
   \cfrac{5}{4}=\cfrac{25}{16}$.
*)

Require Import QArith.

Theorem mathd_algebra_190 :
  ((3/8 + 7/8) / (4/5) == 25/16)%Q.
Proof.
Admitted.