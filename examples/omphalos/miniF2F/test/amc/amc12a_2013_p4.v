(* miniF2F problem: amc12a_2013_p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of $\frac{2^{2014}+2^{2012}}{2^{2014}-2^{2012}}?$

   $ \textbf{(A)}\ -1\qquad\textbf{(B)}\ 1\qquad\textbf{(C)}\
   \frac{5}{3}\qquad\textbf{(D)}\ 2013\qquad\textbf{(E)}\ 2^{4024} $ Show that it is
   \textbf{(C)} \frac{5}{3}.

   Informal proof:
   $\frac{2^{2014}+2^{2012}}{2^{2014}-2^{2012}}$

   We can factor a ${2^{2012}}$ out of the numerator and denominator to obtain

   $\frac{2^{2012}*(2^2+1)}{2^{2012}*(2^2-1)}$

   The ${2^{2012}}$ cancels, so we get 

   $\frac{(2^2+1)}{(2^2-1)}=\frac{5}{3}$, which is $C$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2013_p4 :
  (2^2014 + 2^2012) / (2^2014 - 2^2012) = (5 / 3)%R.
Proof.
Admitted.