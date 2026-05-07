(* miniF2F problem: imo_1985_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For every real number $x_1$, construct the sequence $x_1,x_2,\ldots$ by setting
   $x_{n+1}=x_n \left(x_n + \frac{1}{n}\right)$ for each $n \geq 1$.  Prove that there
   exists exactly one value of $x_1$ for which $0<x_n<x_{n+1}<1$ for every $n$.

   Informal proof:
   By recursive substitution, one can write $x_n=P_n(x_1)$ , where $P_n$ is a polynomial
   with non-negative coefficients and zero constant term. Thus, $P_n(0)=0$, $P_n$ is
   strictly increasing in $[0,+\infty)$ , and $\displaystyle \lim_{x_1 \rightarrow +
   \infty} P_n(x_1)=+\infty$. We can therefore define the inverse $P_n^{-1}$ of $P_n$ on
   $[0,+\infty)$. It follows that $x_1=P_n^{-1}(x_n)$, $P_n^{-1}(0)=0$, $P_n^{-1}$ is
   strictly increasing in $[0,+\infty)$, and $\displaystyle \lim_{x_1 \rightarrow +
   \infty} P_n^{-1}(x_1) =+\infty$.

   Denote by $\displaystyle a_n=P_n^{-1}(1-\frac{1}{n})$ and $b_n=P_n^{-1}(1)$. By the
   monotonicity of $P_n^{-1}$ we have $a_n<b_n$ for each $n$. Note that:

   (a) $\displaystyle x_n<x_{n+1} \Leftrightarrow x_n>1-\frac{1}{n} \Leftrightarrow
   P_n^{-1}(x_n)>P_n^{-1}(1-\frac{1}{n}) \Leftrightarrow x_1>a_n$;
   (b) $\displaystyle x_n<1 \Leftrightarrow P_n^{-1}(x_n)<P_n^{-1}(1) \Leftrightarrow
   x_1<b_n$.

   Thus, $0<x_n<x_{n+1}<1,\forall n$ holds if and only if $a_n<x_1<b_n,\forall n$, or
   $\displaystyle x_1 \in \bigcap_{n=1}^{+\infty}(a_n,b_n)$. We need to show that
   $\displaystyle \bigcap_{n=1}^{+\infty}(a_n,b_n)$ is a singleton. We have:

   (c) if $x_1=a_n$, then $x_n=1-\frac{1}{n}$, which implies that
   $x_{n+1}=1-\frac{1}{n}<1-\frac{1}{n+1}=P_{n+1}(a_{n+1})$, and $x_1<a_{n+1}$. It
   follows that $a_n<a_{n+1},\forall n$; and
   (d) if $x_1=b_n$, then $x_n=1$, which implies that
   $x_{n+1}=1+\frac{1}{n}>1=P_{n+1}(b_{n+1})$, and $x_1>b_{n+1}$. It follows that
   $b_n>b_{n+1},\forall n$; and

   Thus, $a_n<a_{n+1}<b_{n+1}<b_n, \forall n$. Therefore, the two sequences
   $\{a_n\}_{n=1}^{+\infty}$ and $\{b_n\}_{n=1}^{+\infty}$ converge, and their limits
   $a$ and $b$ satisfy $a \leq b$. Hence, $\displaystyle
   \bigcap_{n=1}^{+\infty}(a_n,b_n)=[a,b]$ is non-empty, which demonstrates the
   existence of $x_1$.

   Now, suppose that $a \leq x_1 \leq x_1' \leq b$. We have $x_{n+1}'-x_{n+1} =
   (x_n'-x_n)(x_n'+x_n+\frac{1}{n}) \geq (x_n'-x_n)(2-\frac{1}{n}) \geq (x_n'-x_n)$ for
   each $n$, so that $x_n'-x_n \geq x_1'-x_1$ for each $n$. However, $1-\frac{1}{n}<x_n
   \leq x_n'<1$, so that $0 \leq x_n'-x_n<\frac{1}{n}$, which implies that
   $\displaystyle \lim_{n \rightarrow +\infty}(x_n'-x_n)=0$. Therefore, $x_1' \leq x_1$,
   proving unicity.

   This solution was posted and copyrighted by DAFR. The original thread for this
   problem can be found here: [https://aops.com/community/p2751173]
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1985_p6 :
  forall (f : nat -> R -> R),
  (forall x : R, f 1%nat x = x) ->
  (forall (x : R) (n : nat), f (S n) x = f n x * (f n x + /INR n)) ->
  exists! a : R, forall n : nat,
    (0 < INR n)%R ->
    0 < f n a /\ f n a < f (S n) a /\ f (S n) a < 1.

Proof.
Admitted.
