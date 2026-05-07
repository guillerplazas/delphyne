(* miniF2F problem: amc12a_2009_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $P = 2^m$ and $Q = 3^n$. Which of the following is equal to $12^{mn}$
   for every pair of integers $(m,n)$?

   $\textbf{(A)}\ P^2Q \qquad \textbf{(B)}\ P^nQ^m \qquad \textbf{(C)}\ P^nQ^{2m} \qquad
   \textbf{(D)}\ P^{2m}Q^n \qquad \textbf{(E)}\ P^{2n}Q^m$ Show that it is \bold{E)}
   P^{2n} Q^m.

   Informal proof:
   We have $12^{mn} = (2\cdot 2\cdot 3)^{mn} = 2^{2mn} \cdot 3^{mn} = (2^m)^{2n} \cdot
   (3^n)^m = \bold{E)} P^{2n} Q^m$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem amc12a_2009_p6
  (m n p q : R)
  (h₀ : p = Rpower 2 m)
  (h₁ : q = Rpower 3 n) :
  Rpower p (2 * n) * Rpower q m = Rpower 12 (m * n).

Proof.
Admitted.
