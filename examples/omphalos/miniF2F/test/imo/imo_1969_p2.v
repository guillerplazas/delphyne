(* miniF2F problem: imo_1969_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a_1, a_2,\cdots, a_n$ be real constants, $x$ a real variable, and
   $f(x)=\cos(a_1+x)+\frac{1}{2}\cos(a_2+x)+\frac{1}{4}\cos(a_3+x)+\cdots+\frac{1}{2^{n-1}}\cos(a_n+x).$
   Given that $f(x_1)=f(x_2)=0,$ prove that $x_2-x_1=m\pi$ for some integer $m.$

   Informal proof:
   Because the period of $\cos(x)$ is $2\pi$, the period of $f(x)$ is also $2\pi$.
   $f(x_1)=f(x_2)=f(x_1+x_2-x_1)$
   We can get $x_2-x_1 = 2k\pi$ for $k\in N^*$. Thus, $x_2-x_1=m\pi$ for some integer
   $m.$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import Rdefinitions.
Require Import Rbasic_fun.
From Coq Require Import Reals.
From Coq Require Import Lia.
From Coq Require Import Lra.

Theorem imo_1969_p2 :
  forall (m n : R) (k : nat) (a : nat -> R) (y : R -> R),
    (0 < k)%nat ->
    (forall x : R, y x = sum_f_R0 (fun i => (cos (a i + x) / (2^i))) (pred k)) ->
    y m = 0 ->
    y n = 0 ->
    exists t : Z, m - n = (IZR t) * PI.

Proof.
Admitted.
