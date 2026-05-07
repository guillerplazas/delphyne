(* miniF2F problem: amc12a_2010_p10
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The first four terms of an arithmetic sequence are $p$, $9$, $3p-q$, and $3p+q$. What
   is the $2010^\text{th}$ term of this sequence?

   $\textbf{(A)}\ 8041 \qquad \textbf{(B)}\ 8043 \qquad \textbf{(C)}\ 8045 \qquad
   \textbf{(D)}\ 8047 \qquad \textbf{(E)}\ 8049$ Show that it is \textbf{(A) }8041.

   Informal proof:
   $3p-q$ and $3p+q$ are consecutive terms, so the common difference is $(3p+q)-(3p-q) =
   2q$.

   $\begin{align*}p+2q &= 9\\
   9+2q &= 3p-q\\
   q&=2\\
   p&=5\end{align*}$

   The common difference is $4$. The first term is $5$ and the $2010^\text{th}$ term is

   $5+4(2009) = \textbf{(A) }8041$
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem amc12a_2010_p10:
  forall (p q : R) (a : nat -> R),
    (forall n, a (n + 2)%nat - a (n + 1)%nat = a (n + 1)%nat - a n) ->
    a 1%nat = p ->
    a 2%nat = 9 ->
    a 3%nat = 3 * p - q ->
    a 4%nat = 3 * p + q ->
    a 2010%nat = 8041.

Proof.
Admitted.
