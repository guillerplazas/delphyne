(* miniF2F problem: mathd_algebra_437
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the integer that lies between $\sqrt[3]{-45}$ and $\sqrt[3]{-101}$. Show that it
   is -4.

   Informal proof:
   We have $(-3)^3 = -27$, $(-4)^3 = -64$, and $(-5)^3 = -125$.  Since $-64$ is between
   $-45$ and $-101$, we know that $\sqrt[3]{-64}$, which equals $-4$, is between
   $\sqrt[3]{-45}$ and $\sqrt[3]{-101}$.
*)

Require Import Reals.
Require Import ZArith.
Open Scope R_scope.

Theorem mathd_algebra_437 :
  forall (x y : R) (n : Z),
    x^3 = -45 ->
    y^3 = -101 ->
    x < IZR n ->
    IZR n < y ->
    n = (-4)%Z.

Proof.
Admitted.
