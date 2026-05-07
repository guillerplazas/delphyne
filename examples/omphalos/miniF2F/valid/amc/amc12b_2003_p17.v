(* miniF2F problem: amc12b_2003_p17
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $\log (xy^3) = 1$ and $\log (x^2y) = 1$, what is $\log (xy)$?

   $\mathrm{(A)}\ -\frac 12 
   \qquad\mathrm{(B)}\ 0 
   \qquad\mathrm{(C)}\ \frac 12
   \qquad\mathrm{(D)}\ \frac 35 
   \qquad\mathrm{(E)}\ 1$ Show that it is \mathrm{(D)} \frac 35.

   Informal proof:
   Since 
   $\begin{align*}
   &\log(xy) +2\log y = 1  \\
   \log(xy) + \log x = 1 \quad \Longrightarrow \quad &2\log(xy) + 2\log x = 2
   \end{align*}$
   Summing gives 
   $3\log(xy) + 2\log y + 2\log x = 3 \Longrightarrow 5\log(xy) = 3$

   Hence $\log (xy) = \frac 35 \Rightarrow \mathrm{(D)}$.

   It is not difficult to find $x = 10^{\frac{2}{5}}, y = 10^{\frac{1}{5}}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2003_p17:
  forall x y : R,
  0 < x -> 0 < y ->
  ln (x * y ^ 3) = 1 ->
  ln (x ^ 2 * y) = 1 ->
  ln (x * y) = 3 / 5.
Proof.
Admitted.