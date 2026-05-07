(* miniF2F problem: amc12a_2009_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   One dimension of a cube is increased by $1$, another is decreased by $1$, and the
   third is left unchanged. The volume of the new rectangular solid is $5$ less than
   that of the cube. What was the volume of the cube?

   $\textbf{(A)}\ 8 \qquad \textbf{(B)}\ 27 \qquad \textbf{(C)}\ 64 \qquad \textbf{(D)}\
   125 \qquad \textbf{(E)}\ 216$ Show that it is \text{(D)}.

   Informal proof:
   Let the original cube have edge length $a$. Then its volume is $a^3$.
   The new box has dimensions $a-1$, $a$, and $a+1$, hence its volume is $(a-1)a(a+1) =
   a^3-a$. 
   The difference between the two volumes is $a$. As we are given that the difference is
   $5$, we have $a=5$, and the volume of the original cube was $5^3 =
   125\Rightarrow\text{(D)}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2009_p5 :
  forall x : R,
  (x^3 - (x + 1) * (x - 1) * x = 5) -> 
  x^3 = 125.
Proof.
Admitted.