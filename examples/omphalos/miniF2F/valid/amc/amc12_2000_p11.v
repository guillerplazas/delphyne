(* miniF2F problem: amc12_2000_p11
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   $\textbf{(A)} \ - 2 \qquad \textbf{(B)} \ \frac { -1 }{2} \qquad \textbf{(C)} \ \frac
   {1}{3} \qquad \textbf{(D)} \ \frac {1}{2} \qquad \textbf{(E)} \ 2$ Show that it is
   $\text{E}$.

   Informal proof:
   $\frac {a}{b} + \frac {b}{a} - ab = \frac{a^2 + b^2}{ab} - (a - b) = \frac{a^2 +
   b^2}{a-b} - \frac{(a-b)^2}{(a-b)} = \frac{2ab}{a-b} = \frac{2(a-b)}{a-b} =2
   \Rightarrow \text{E}$. 

   Another way is to solve the equation for $b,$ giving $b = \frac{a}{a+1};$ then
   substituting this into the expression and simplifying gives the answer of $2.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12_2000_p11 :
  forall a b : R,
  a <> 0 -> b <> 0 ->
  a * b = a - b ->
  a / b + b / a - a * b = 2.
Proof.
Admitted.