(* miniF2F problem: amc12a_2008_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the [[reciprocal]] of $\frac{1}{2}+\frac{2}{3}$?

   $\mathrm{(A)}\ \frac{6}{7}\qquad\mathrm{(B)}\ \frac{7}{6}\qquad\mathrm{(C)}\
   \frac{5}{3}\qquad\mathrm{(D)}\ 3\qquad\mathrm{(E)}\ \frac{7}{2}$ Show that it is
   \frac{6}{7}.

   Informal proof:
   Here's a cheapshot: 
   Obviously, $\frac{1}{2}+\frac{2}{3}$ is greater than $1$. Therefore, its reciprocal
   is less than $1$, and the answer must be $\frac{6}{7}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2008_p2 :
  forall x : R,
  (x * (1 / 2 + 2 / 3) = 1) -> x = 6 / 7.
Proof.
Admitted.