(* miniF2F problem: amc12a_2009_p7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The first three terms of an arithmetic sequence are $2x - 3$, $5x - 11$, and $3x + 1$
   respectively. The $n$th term of the sequence is $2009$. What is $n$?

   $\textbf{(A)}\ 255 \qquad \textbf{(B)}\ 502 \qquad \textbf{(C)}\ 1004 \qquad
   \textbf{(D)}\ 1506 \qquad \textbf{(E)}\ 8037$ Show that it is 502.

   Informal proof:
   As this is an arithmetic sequence, the difference must be constant: $(5x-11) - (2x-3)
   = (3x+1) - (5x-11)$. This solves to $x=4$. The first three terms then are $5$, $9$,
   and $13$. In general, the $n$th term is $1+4n$. Solving $1+4n=2009$, we get $n=502$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2009_p7 (x : R) (n : nat) (a : nat -> R) :
  (forall m : nat, a (S m) - a m = a (S (S m)) - a (S m)) ->
  (a 1%nat = 2 * x - 3) ->
  (a 2%nat = 5 * x - 11) ->
  (a 3%nat = 3 * x + 1) ->
  (a n = 2009) ->
  n = 502%nat.

Proof.
Admitted.
