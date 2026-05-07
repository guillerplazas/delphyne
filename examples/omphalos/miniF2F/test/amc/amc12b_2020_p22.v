(* miniF2F problem: amc12b_2020_p22
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the maximum value of $\frac{(2^t-3t)t}{4^t}$ for real values of $t?$

   $\textbf{(A)}\ \frac{1}{16} \qquad\textbf{(B)}\ \frac{1}{15} \qquad\textbf{(C)}\
   \frac{1}{12} \qquad\textbf{(D)}\ \frac{1}{10} \qquad\textbf{(E)}\ \frac{1}{9}$ Show
   that it is \textbf{(C)} \frac{1}{12}.

   Informal proof:
   We proceed by using AM-GM. We get $\frac{(2^t-3t) + 3t}{2}$ $\ge
   \sqrt{(2^t-3t)(3t)}$. Thus, squaring gives us that $4^{t-1} \ge (2^t-3t)(3t)$.
   Rembering what we want to find, we divide both sides of the inequality by the
   positive amount of $\frac{1}{3\cdot4^t}$. We get the maximal values as
   $\frac{1}{12}$, and we are done.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem amc12b_2020_p22 : forall t : R,
  ((exp (t * ln 2) - 3 * t) * t) / (exp (t * ln 4)) <= 1 / 12 /\
  exists t,  ((exp (t * ln 2) - 3 * t) * t) / (exp (t * ln 4)) = 1/12.
Proof.
Admitted.
