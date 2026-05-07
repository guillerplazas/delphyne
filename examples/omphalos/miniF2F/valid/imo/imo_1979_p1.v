(* miniF2F problem: imo_1979_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $p$ and $q$ are natural numbers so that$
   \frac{p}{q}=1-\frac{1}{2}+\frac{1}{3}-\frac{1}{4}+ \ldots
   -\frac{1}{1318}+\frac{1}{1319}, $prove that $p$ is divisible with $1979$.

   Informal proof:
   We first write
   $\begin{align*}
   \frac{p}{q}
   &=1-\frac{1}{2}+\frac{1}{3}-\frac{1}{4}+\cdots-\frac{1}{1318}+\frac{1}{1319}\\
   &=1+\frac{1}{2}+\cdots+\frac{1}{1319}-2\cdot\left(\frac{1}{2}+\frac{1}{4}+\cdots+\frac{1}{1318}\right)\\
   &=1+\frac{1}{2}+\cdots+\frac{1}{1319}-\left(1+\frac{1}{2}+\cdots+\frac{1}{659}\right)\\
   &=\frac{1}{660}+\frac{1}{661}+\cdots+\frac{1}{1319}
   \end{align*}$Now, observe that
   $\begin{align*}
   \frac{1}{660}+\frac{1}{1319}=\frac{660+1319}{660\cdot 1319}=\frac{1979}{660\cdot
   1319}
   \end{align*}$and similarly $\frac{1}{661}+\frac{1}{1318}=\frac{1979}{661\cdot 1318}$
   and $\frac{1}{662}+\frac{1}{1317}=\frac{1979}{662\cdot 1317}$, and so on. We see that
   the original equation becomes
   $\begin{align*}
   \frac{p}{q}
   =\frac{1979}{660\cdot 1319}+\frac{1979}{661\cdot 1318}+\cdots+\frac{1979}{989\cdot
   990}=1979\cdot\frac{r}{s}
   \end{align*}$where $s=660\cdot 661\cdots 1319$ and $r=\frac{s}{660\cdot
   1319}+\frac{s}{661\cdot 1318}+\cdots+\frac{s}{989\cdot 990}$ are two integers.
   Finally consider $p=1979\cdot\frac{qr}{s}$, and observe that $s\nmid 1979$ because
   $1979$ is a prime, it follows that $\frac{qr}{s}\in\mathbb{Z}$. Hence we deduce that
   $p$ is divisible with $1979$.

   The above solution was posted and copyrighted by Solumilkyu. The original thread for
   this problem can be found here: [https://aops.com/community/p6171228]
*)

Require Import Nat.
Require Import Reals.
Require Import Lia.
Require Import Rdefinitions.
Require Import Rbasic_fun.
Require Import FunctionalExtensionality.
From mathcomp Require Import all_ssreflect.

Theorem imo_1979_p1 (p q : nat) :
  0 < q ->
  (sum_f_R0 (fun k => (-1)^(S k+1) * /INR (S k))%R 1318)%R = (INR p / INR q)%R ->
  exists k, p = k * 1979.

Proof.
Admitted.
