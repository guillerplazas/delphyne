(* miniF2F problem: amc12b_2021_p3
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose$2+\frac{1}{1+\frac{1}{2+\frac{2}{3+x}}}=\frac{144}{53}.$What is the value of
   $x?$

   $\textbf{(A) }\frac34 \qquad \textbf{(B) }\frac78 \qquad \textbf{(C) }\frac{14}{15}
   \qquad \textbf{(D) }\frac{37}{38} \qquad \textbf{(E) }\frac{52}{53}$ Show that it is
   \text{A}.

   Informal proof:
   Subtracting $2$ from both sides and taking reciprocals gives
   $1+\frac{1}{2+\frac{2}{3+x}}=\frac{53}{38}$. Subtracting $1$ from both sides and
   taking reciprocals again gives $2+\frac{2}{3+x}=\frac{38}{15}$. Subtracting $2$ from
   both sides and taking reciprocals for the final time gives
   $\frac{x+3}{2}=\frac{15}{8}$ or $x=\frac{3}{4} \implies \text{A}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2021_p3:
  forall x : R,
  2 + 1 / (1 + 1 / (2 + 2 / (3 + x))) = 144 / 53 -> 
  x = 3 / 4.
Proof.
Admitted.