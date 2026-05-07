(* miniF2F problem: amc12a_2013_p7
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sequence $S_1, S_2, S_3, \cdots, S_{10}$ has the property that every term
   beginning with the third is the sum of the previous two.  That is, $ S_n = S_{n-2} +
   S_{n-1} \text{ for } n \ge 3. $ Suppose that $S_9 = 110$ and $S_7 = 42$.  What is
   $S_4$?

   $ \textbf{(A)}\ 4\qquad\textbf{(B)}\ 6\qquad\textbf{(C)}\ 10\qquad\textbf{(D)}\
   12\qquad\textbf{(E)}\ 16\qquad $ Show that it is \textbf{(C) }{10}.

   Informal proof:
   $S_9 = 110$, $S_7 = 42$

   $S_8 = S_9 - S_ 7 = 110 - 42 = 68$

   $S_6 = S_8 - S_7 = 68 - 42 = 26$

   $S_5 = S_7 - S_6 = 42 - 26 = 16$

   $S_4 = S_6 - S_5 = 26 - 16 = 10$

   Therefore, the answer is $\textbf{(C) }{10}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2013_p7 
  (s : nat -> R)
  (h0 : forall n : nat, s (S (S n)) = s (S n) + s n)
  (h1 : s 9%nat = 110)
  (h2 : s 7%nat = 42) :
  s 4%nat = 10.

Proof.
Admitted.
