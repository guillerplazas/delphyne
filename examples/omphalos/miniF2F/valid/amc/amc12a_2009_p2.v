(* miniF2F problem: amc12a_2009_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Which of the following is equal to $1 + \frac {1}{1 + \frac {1}{1 + 1}}$?

   $\textbf{(A)}\ \frac {5}{4} \qquad \textbf{(B)}\ \frac {3}{2} \qquad \textbf{(C)}\
   \frac {5}{3} \qquad \textbf{(D)}\ 2 \qquad \textbf{(E)}\ 3$ Show that it is \text{C}.

   Informal proof:
   We compute:

   $
   \begin{align*}
   1 + \frac {1}{1 + \frac {1}{1 + 1}}
   &=
   1 + \frac {1}{1 + \frac {1}{1 + 1}}
   \\
   &=
   1 + \frac {1}{1 + \frac 12}
   \\
   &=
   1 + \frac {1}{\frac 32}
   \\
   &=
   1 + \frac 23
   \\
   &=
   \frac 53
   \end{align*}
   $

   This is choice $\text{C}$.

   Interesting sidenote: The continued fraction $1 + \frac {1}{1 + \frac {1}{1 +
   1....}}$ is equal to the golden ratio, or $\frac{1+\sqrt{5}}{2}$.
*)

Require Import QArith.
Require Import QArith_base.

Theorem amc12a_2009_p2 :
  1 + (1 / (1 + (1 / (1 + 1)))) = (5 # 3)%Q.
Proof.
Admitted.
