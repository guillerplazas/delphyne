(* miniF2F problem: amc12a_2017_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of two nonzero real numbers is 4 times their product. What is the sum of the
   reciprocals of the two numbers?

   $\textbf{(A)}\ 1\qquad\textbf{(B)}\ 2\qquad\textbf{(C)}\ 4\qquad\textbf{(D)}\
   8\qquad\textbf{(E)}\ 12$ Show that it is \textbf{C}.

   Informal proof:
   Let $x, y$ be our two numbers. Then $x+y = 4xy$. Thus, 

   $ \frac{1}{x} + \frac{1}{y} = \frac{x+y}{xy} = 4$. 

   $\textbf{C}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2017_p2:
  forall (x y : R),
  x <> 0 ->
  y <> 0 ->
  x + y = 4 * (x * y) ->
  (1 / x) + (1 / y) = 4.
Proof.
Admitted.