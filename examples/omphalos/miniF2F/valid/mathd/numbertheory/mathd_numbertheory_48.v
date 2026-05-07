(* miniF2F problem: mathd_numbertheory_48
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $321_{b}$ is equal to the base 10 integer 57, find $b$ given that $b>0$. Show that
   it is 4.

   Informal proof:
   Converting $321_{b}$ to base 10 and setting it equal to 57, we find that 
   \begin{align*} 3(b^2)+2(b^1)+1(b^0)&=57
   \\ 3b^2+2b+1&=57
   \\\Rightarrow\qquad 3b^2+2b-56&=0
   \\\Rightarrow\qquad (3b+14)(b-4)&=0
   \end{align*}This tells us that $b$ is either $-\frac{14}{3}$ or $4$. We know that
   $b>0$, so $b=4$.
*)

Require Import Arith.

Theorem mathd_numbertheory_48:
  forall b : nat,
  0 < b ->
  3 * b^2 + 2 * b + 1 = 57 -> 
  b = 4.
Proof.
Admitted.