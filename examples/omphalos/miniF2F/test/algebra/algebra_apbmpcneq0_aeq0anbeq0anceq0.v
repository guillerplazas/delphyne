(* miniF2F problem: algebra_apbmpcneq0_aeq0anbeq0anceq0
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Assume that $m$ and $n$ are both positive reals, $m^3 = 2$, $n^3 = 4$, and $a + bm +
   cn = 0$ for rational numbers $a$, $b$, and $c$.
   Show that $a = b = c = 0$.

   Informal proof:
   We have that $m = 2^{1/3}$ and $n=2^{2/3}=m^2$ so $a+bm+cm^2=0$.

   Let us suppose that $ab \ne 0$ and $c=0$. Then $a+bm=0$ so $m$ is rational and there
   exists $p, q \in \mathbb{Z}$ with $q \neq 0$ and $m=\frac{p}{q}$ and $gcd(p, q)=1$.
   So $m^3=2=\frac{p^3}{q^3}$ and $2q^3=p^3$. So $2 \mid p$. Since $2 \mid p$, $8 \mid
   p^3 = 2q^3$ and $4 \mid q^3$. Necessarily, $q \mid 2$ which is absurd because $gcd(p,
   q)=1$, so $m$ is irrational and if $ab \ne 0$, then $c \ne 0$.

   So if $ab \ne 0$, then $c \ne 0$. Dividing $a+bm+cm^2=0$ by $c$ we can assume that
   $c=1$ without loss of generality, so $m^2+bm+c=0$.
   Multiplying by $m$, we get $2+bm^2+2m=0$, but $m^2=-c-bm$ so $2+b(-c-bm)+2m=0$ and
   $2-bc-b^2m+2m=(2-bc)+m(2-b^2)=0$. So either $2-bc=2-b^2=0$ or $m$ is rational. As
   seen above, $m$ is irrational so $b^2=2$, but $\sqrt{2}$ is irrational which is
   absurd, so $ab=0$.

   Since $ab=0$, and using the fact that $m$ is irrational, we have that necessarily
   $a=b=c=0$.
*)

Require Import Reals.Reals.
Require Import QArith.QArith.
From Stdlib Require Import Qreals.

Theorem algebra_apbmpcneq0_aeq0anbeq0anceq0:
  forall (a b c: Q) (m n: R),
    (0 < m /\ 0 < n)%R ->
    (Rpower m 3 = 2)%R ->
    (Rpower n 3 = 4)%R ->
    (Q2R a + Q2R b * m + Q2R c * n = 0)%R ->
    (a == 0)%Q /\ (b == 0)%Q /\ (c == 0)%Q.

Proof.
Admitted.
