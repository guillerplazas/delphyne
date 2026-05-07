(* miniF2F problem: mathd_algebra_282
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let \[f(x) =
   \begin{cases}
   |\lfloor{x}\rfloor| &\text{if }x\text{ is rational}, \\
   \lceil{x}\rceil^2 &\text{if }x\text{ is irrational}.
   \end{cases}
   \] Find $f(\sqrt[3]{-8})+f(-\pi)+f(\sqrt{50})+f\left(\frac{9}{2}\right)$. Show that
   it is 79.

   Informal proof:
   Since we know that $\sqrt[3]{-8}=-2$ is a rational number,
   $$f(\sqrt[3]{-8})=|\lfloor{-2}\rfloor|=2.$$Continuing from here, we know that $-\pi$
   is irrational, thus $$f(-\pi)=\lceil{-\pi}\rceil^2=(-3)^2=9.$$Because 50 is not a
   perfect square, $\sqrt{50}$ must be irrational as well, so
   $$f(\sqrt{50})=\lceil{\sqrt{50}}\rceil^2=8^2=64.$$Finally, we know that $\frac{9}{2}$
   is a rational number, so
   $$f\left(\frac{9}{2}\right)=\left|\left\lfloor{\frac92}\right\rfloor\right|=4.$$Therefore
   $$f(\sqrt[3]{-8})+f(-\pi)+f(\sqrt{50})+f\left(\frac{9}{2}\right)=2+9+64+4=79.$$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import Reals.Rfunctions.
Require Import QArith.QArith_base.
Require Import Coq.Reals.Rbasic_fun.
Open Scope R_scope.

Definition is_rational (x : R) := 
  exists (p q : Z), (q <> 0%Z) /\ x = (IZR p / IZR q)%R.

Theorem mathd_algebra_282
  (f : R -> R)
  (h0 : forall x, is_rational x -> f x = Rabs (IZR (Int_part x)))
  (h1 : forall x, ~is_rational x -> f x = (IZR (up x))^2) :
  f (Rpower 8 (1/3)) + f (-PI) + f (sqrt 50) + f (9/2) = 79.

Proof.
Admitted.
