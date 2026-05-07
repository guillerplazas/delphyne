(* miniF2F problem: amc12a_2021_p25
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $d(n)$ denote the number of positive integers that divide $n$, including $1$ and
   $n$. For example, $d(1)=1,d(2)=2,$ and $d(12)=6$. (This function is known as the
   divisor function.) Let$f(n)=\frac{d(n)}{\sqrt [3]n}.$There is a unique positive
   integer $N$ such that $f(N)>f(n)$ for all positive integers $n\ne N$. What is the sum
   of the digits of $N?$

   $\textbf{(A) }5 \qquad \textbf{(B) }6 \qquad \textbf{(C) }7 \qquad \textbf{(D)
   }8\qquad \textbf{(E) }9$ Show that it is \textbf{(E) }9.

   Informal proof:
   We consider the prime factorization of $n:$ $n=\prod_{i=1}^{k}p_i^{e_i}.$ By the
   Multiplication Principle, we have $d(n)=\prod_{i=1}^{k}(e_i+1).$ Now, we rewrite
   $f(n)$ as $f(n)=\frac{d(n)}{\sqrt
   [3]n}=\frac{\prod_{i=1}^{k}(e_i+1)}{\prod_{i=1}^{k}p_i^{e_i/3}}=\prod_{i=1}^{k}\frac{e_i+1}{p_i^{{e_i}/3}}.$
   As $f(n)>0$ for all positive integers $n,$ note that $f(a)>f(b)$ if and only if
   $f(a)^3>f(b)^3$ for all positive integers $a$ and $b.$ So, $f(n)$ is maximized if and
   only if $f(n)^3=\prod_{i=1}^{k}\frac{(e_i+1)^3}{p_i^{{e_i}}}$ is maximized.

   For each independent factor $\frac{(e_i+1)^3}{p_i^{e_i}}$ with a fixed prime $p_i,$
   where $1\leq i\leq k,$ the denominator grows faster than the numerator, as
   exponential functions always grow faster than polynomial functions. Therefore, for
   each prime $p_i$ with
   $\left(p_1,p_2,p_3,p_4,\ldots\right)=\left(2,3,5,7,\ldots\right),$ we look for the
   nonnegative integer $e_i$ such that $\frac{(e_i+1)^3}{p_i^{e_i}}$ is a relative
   maximum:
   $\begin{array}{c|c|c|c|c} 
   & & & & \\ [-2.25ex]
   \boldsymbol{i} & \boldsymbol{p_i} & \boldsymbol{e_i} &
   \boldsymbol{\dfrac{(e_i+1)^3}{p_i^{e_i}}} & \textbf{Max?} \\ [2.5ex]
   \hline\hline 
   & & & & \\ [-2ex]
   1 & 2 & 0 & 1 & \\     
   & & 1 & 4 & \\    
   & & 2 & 27/4 &\\    
   & & 3 & 8 & \checkmark\\    
   & & 4 & 125/16 & \\ [0.5ex]
   \hline  
   & & & & \\ [-2ex]
   2 & 3 & 0 & 1 &\\    
   & & 1 & 8/3 & \\    
   & & 2 & 3 &  \checkmark\\    
   & & 3 & 64/27 &  \\ [0.5ex]
   \hline  
   & & & & \\ [-2ex]
   3 & 5 & 0 & 1 &  \\    
   & & 1 & 8/5 &  \checkmark\\    
   & & 2 & 27/25 & \\ [0.5ex]
   \hline  
   & & & & \\ [-2ex]
   4 & 7 & 0 & 1 &  \\    
   & & 1 & 8/7 &  \checkmark\\    
   & & 2 & 27/49 & \\ [0.5ex]
   \hline  
   & & & & \\ [-2ex]
   \geq5 & \geq11 & 0 & 1 & \checkmark \\    
   & & \geq1 & \leq8/11 &   \\ [0.5ex]
   \end{array}$
   Finally, the positive integer we seek is $N=2^3\cdot3^2\cdot5^1\cdot7^1=2520.$ The
   sum of its digits is $2+5+2+0=\textbf{(E) }9.$

   Alternatively, once we notice that $3^2$ is a factor of $N,$ we can conclude that the
   sum of the digits of $N$ must be a multiple of $9.$ Only choice $\textbf{(E)}$ is
   possible.
*)

Require Import Arith.
Require Import List.
Require Import Reals.

Open Scope R_scope.

Definition divisors (n : nat) : list nat :=
  filter (fun d => n mod d =? 0) (seq 1 n).

Fixpoint fueled_sum_digits (fuel n : nat) : nat :=
  match fuel with
  | 0 => 0
  | S fuel' =>
    if n mod 10 =? n then n else n mod 10 + fueled_sum_digits fuel' (n / 10)
  end.

Definition sum_digits n := fueled_sum_digits (S n) n.

Theorem amc12a_2021_p25 :
  forall (N : nat) (f : nat -> R),
  (forall n, (0 < n)%nat ->
    f n = INR (length (divisors n)) / Rpower (INR n) (1 / 3)) ->
  (forall n, n <> N -> f n < f N) ->
  (sum_digits N = 9)%nat.
Proof.
Admitted.
