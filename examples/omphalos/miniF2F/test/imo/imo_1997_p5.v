(* miniF2F problem: imo_1997_p5
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that if $x$ and $y$ are positive integers such that $x^{y^2} = y^x$, then $(x,
   y)$ is equal to $(1, 1)$, $(16, 2)$, or $(27, 3)$.

   Informal proof:
   The answer is $(1,1),(16,2)$ and $(27,3)$.
   We assume $a, b>1$ for convenience. Let $T$ denote the set of non perfect powers
   other than $1 .$

   Claim. Every integer greater than 1 is uniquely of the form $t^n$ for some $t \in T,
   n \in \mathbb{N}$.
   Proof. Clear.
   Let $a=s^m, b=t^n$.
   $$s^{m \cdot\left(t^n\right)^2}=t^{n \cdot s^m}$$
   Hence $s=t$ and we have
   $$m \cdot t^{2 n}=n \cdot t^m \Longrightarrow t^{2 n-m}=\frac{n}{m} .$$
   Let $n=t^e m$ and $2 \cdot t^e m-m=e$, or
   $$e+m=2 t^e \cdot m$$
   We resolve this equation by casework
   - If $e>0$, then $2 t^e \cdot m>2 e \cdot m>e+m$.
   - If $e=0$ we have $m=n$ and $m=2 m$, contradiction.
   - If $e=-1$ we apparently have
   $$\frac{2}{t} \cdot m=m-1 \Longrightarrow m=\frac{t}{t-2}$$
   so $(t, m)=(3,3)$ or $(t, m)=(4,2)$.
   - If $e=-2$ we apparently have
   $$\frac{2}{t^2} \cdot m=m-2 \Longrightarrow m=\frac{2}{1-2 / t^2}=\frac{2
   t^2}{t^2-2}$$
   This gives $(t, m)=(2,2)$.
   - If $e \leq-3$ then let $k=-e \geq 3$, so the equation is
   $$m-k=\frac{2 m}{t^k} \Longleftrightarrow m=\frac{k \cdot t^k}{t^k-2}=k+\frac{2
   k}{t^k-2}$$
   However, for $k \geq 3$ and $t \geq 2$, we always have $2 k \leq t^k-2$, with
   equality only when $(t, k)=(2,3)$; this means $m=4$, which is not a new solution.
*)

Require Import Arith.
Require Import PeanoNat.

Theorem imo_1997_p5:
  forall x y : nat,
  0 < x -> 0 < y ->
  x^(y^2) = y^x ->
  (x, y) = (1, 1) \/ (x, y) = (16, 2) \/ (x, y) = (27, 3).
Proof.
Admitted.