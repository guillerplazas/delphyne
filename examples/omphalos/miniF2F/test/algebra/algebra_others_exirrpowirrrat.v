(* miniF2F problem: algebra_others_exirrpowirrrat
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that there exist real numbers $a$ and $b$ such that $a$ is irrational, $b$ is
   irrational, and $a^b$ is rational.

   Informal proof:
   We know that $\sqrt{2}$ is an irrational number.
   If $\sqrt{2}^{\sqrt{2}}$ is rational, we found a solution.
   Otherwise, we consider $a=\sqrt{2}^{\sqrt{2}}$ and $b=\sqrt{2}$.
   Then, we have
   $a^b=(\sqrt{2}^{\sqrt{2}})^{\sqrt{2}}=\sqrt{2}^{\sqrt{2}\times\sqrt{2}}=\sqrt{2}^2=2$
   so $a^b$ is rational, and we found a solution.
*)

Require Import Reals.
Require Import Psatz.
Require Import Classical.

Definition irrational (x : R) := 
  ~ exists (p q : Z), q <> 0%Z /\ x = (IZR p / IZR q)%R.

Theorem algebra_others_exirrpowirrrat :
  exists a b : R, 
    irrational a /\ irrational b /\ ~ irrational (Rpower a b).

Proof.
Admitted.
