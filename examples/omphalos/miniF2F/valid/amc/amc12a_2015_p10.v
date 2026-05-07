(* miniF2F problem: amc12a_2015_p10
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Integers $x$ and $y$ with $x>y>0$ satisfy $x+y+xy=80$. What is $x$?

   $ \textbf{(A)}\ 8 \qquad\textbf{(B)}\ 10 \qquad\textbf{(C)}\ 15 \qquad\textbf{(D)}\
   18 \qquad\textbf{(E)}\ 26$ Show that it is \textbf{(E)}\ 26.

   Informal proof:
   Use [[SFFT]] to get $(x+1)(y+1)=81$. The terms $(x+1)$ and $(y+1)$ must be factors of
   $81$, which include $1, 3, 9, 27, 81$. Because $x > y$, $x+1$ is equal to $27$ or
   $81$. But if $x+1=81$, then $y=0$ and so $x=\textbf{(E)}\ 26$.
*)

Require Import Nat.

Theorem amc12a_2015_p10
  (x y : nat)
  (h0 : (0 < y)%nat)
  (h1 : (y < x)%nat)
  (h2 : (x + y + x * y = 80)%nat) :
  x = 26%nat.

Proof.
Admitted.
