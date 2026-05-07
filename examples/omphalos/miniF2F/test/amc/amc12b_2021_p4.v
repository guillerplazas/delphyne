(* miniF2F problem: amc12b_2021_p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Ms. Blackwell gives an exam to two classes. The mean of the scores of the students in
   the morning class is $84$, and the afternoon class's mean score is $70$. The ratio of
   the number of students in the morning class to the number of students in the
   afternoon class is $\frac{3}{4}$. What is the mean of the scores of all the students?

   $\textbf{(A)} ~74 \qquad\textbf{(B)} ~75 \qquad\textbf{(C)} ~76 \qquad\textbf{(D)}
   ~77 \qquad\textbf{(E)} Show that it is \textbf{(C)} ~76.

   Informal proof:
   Let there be $3x$ students in the morning class and $4x$ students in the afternoon
   class. The total number of students is $3x + 4x = 7x$. The average is
   $\frac{3x\cdot84 + 4x\cdot70}{7x}=76$. Therefore, the answer is $\textbf{(C)} ~76$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem amc12b_2021_p4 :
  forall (m a : nat),
    (0 < m)%nat ->
    (0 < a)%nat ->
    INR m / INR a = 3 / 4 ->
    (84 * INR m + 70 * INR a) / (INR m + INR a) = 76.

Proof.
Admitted.
