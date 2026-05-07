(* miniF2F problem: mathd_algebra_114
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a = 8$, what is the value of $\left(16\sqrt[3]{a^2}\right)^{\frac 13}$? Show that
   it is 4.

   Informal proof:
   Note that $a^2 = 64$ and $\sqrt[3]{64} = 4$. Therefore,
   $$\left(16\sqrt[3]{a^2}\right)^{\frac {1}{3}} = \left(16 \times
   4\right)^{\frac{1}{3}} = 64^\frac{1}{3} = 4.$$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Open Scope R_scope.

Theorem mathd_algebra_114 (a : R)
  (H : a = 8) :
  Rpower (16 * Rpower (a ^ 2) (1/3)) (1/3) = 4.

Proof.
Admitted.
