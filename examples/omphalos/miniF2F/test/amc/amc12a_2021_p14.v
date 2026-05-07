(* miniF2F problem: amc12a_2021_p14
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of $\left(\sum_{k=1}^{20} \log_{5^k}
   3^{k^2}\right)\cdot\left(\sum_{k=1}^{100} \log_{9^k} 25^k\right)?$

   $\textbf{(A) }21 \qquad \textbf{(B) }100\log_5 3 \qquad \textbf{(C) }200\log_3 5
   \qquad \textbf{(D) }2{,}200\qquad \textbf{(E) }21{,}000$ Show that it is \textbf{(E)
   }21{,}000.

   Informal proof:
   We will apply the following logarithmic identity:
   $\log_{p^n}{q^n}=\log_{p}{q},$
   which can be proven by the Change of Base Formula:
   $\log_{p^n}{q^n}=\frac{\log_{p}{q^n}}{\log_{p}{p^n}}=\frac{n\log_{p}{q}}{n}=\log_{p}{q}.$
   Now, we simplify the expressions inside the summations:
   $\begin{align*}
   \log_{5^k}{{3^k}^2}&=\log_{5^k}{(3^k)^k} \\
   &=k\log_{5^k}{3^k} \\
   &=k\log_{5}{3},
   \end{align*}$
   and 
   $\begin{align*}
   \log_{9^k}{25^k}&=\log_{3^{2k}}{5^{2k}} \\
   &=\log_{3}{5}.
   \end{align*}$
   Using these results, we evaluate the original expression:
   $\begin{align*}
   \left(\sum_{k=1}^{20} \log_{5^k} 3^{k^2}\right)\cdot\left(\sum_{k=1}^{100} \log_{9^k}
   25^k\right)&=\left(\sum_{k=1}^{20} k\log_{5}{3}\right)\cdot\left(\sum_{k=1}^{100}
   \log_{3}{5}\right) \\
   &= \left(\log_{5}{3}\cdot\sum_{k=1}^{20}
   k\right)\cdot\left(\log_{3}{5}\cdot\sum_{k=1}^{100} 1\right) \\
   &= \left(\sum_{k=1}^{20} k\right)\cdot\left(\sum_{k=1}^{100} 1\right) \\
   &= \frac{21\cdot20}{2}\cdot100 \\
   &= \textbf{(E) }21{,}000.
   \end{align*}$
   ~MRENTHUSIASM (Solution)

   ~JHawk0224 (Proposal)
*)

Require Import Coq.Reals.Reals.
Require Import Coq.Init.Nat.
Require Import Coq.micromega.Lra.

Open Scope R_scope.



Theorem amc12a_2021_p14 :
  ( (sum_f_R0 (fun i => ln (3 ^ ((i+1)*(i+1))) / ln (5 ^ (i+1))) 19)
    * (sum_f_R0 (fun i => ln (25 ^ (i+1)) / ln (9 ^ (i+1))) 99)
  ) = 21000.

Proof.
Admitted.
